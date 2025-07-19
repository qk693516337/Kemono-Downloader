import threading
import time
import os
import json
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from .api_client import download_from_api
from .workers import PostProcessorWorker, DownloadThread
from ..config.constants import (
    STYLE_DATE_BASED, STYLE_POST_TITLE_GLOBAL_NUMBERING,
    MAX_THREADS, POST_WORKER_BATCH_THRESHOLD, POST_WORKER_NUM_BATCHES,
    POST_WORKER_BATCH_DELAY_SECONDS
)
from ..utils.file_utils import clean_folder_name


class DownloadManager:
    """
    Manages the entire download lifecycle, acting as a bridge between the UI
    and the backend workers. It handles thread pools, task submission,
    and state management for a download session.
    """

    def __init__(self, progress_queue):
        """
        Initializes the DownloadManager.

        Args:
            progress_queue (queue.Queue): A thread-safe queue for sending
                                          status updates to the UI.
        """
        self.progress_queue = progress_queue
        self.thread_pool = None
        self.active_futures = []
        self.cancellation_event = threading.Event()
        self.pause_event = threading.Event()
        self.is_running = False
        
        self.total_posts = 0
        self.processed_posts = 0
        self.total_downloads = 0
        self.total_skips = 0
        self.all_kept_original_filenames = []

    def _log(self, message):
        """Puts a progress message into the queue for the UI."""
        self.progress_queue.put({'type': 'progress', 'payload': (message,)})

    def start_session(self, config, restore_data=None):
        """
        Starts a new download session based on the provided configuration.
        This is the main entry point called by the UI.

        Args:
            config (dict): A dictionary containing all settings from the UI.
            restore_data (dict, optional): Data from a previous, interrupted session.
        """
        if self.is_running:
            self._log("❌ Cannot start a new session: A session is already in progress.")
            return
        self.is_running = True
        self.cancellation_event.clear()
        self.pause_event.clear()
        self.active_futures.clear()
        self.total_posts = 0
        self.processed_posts = 0
        self.total_downloads = 0
        self.total_skips = 0
        self.all_kept_original_filenames = []
        is_single_post = bool(config.get('target_post_id_from_initial_url'))
        use_multithreading = config.get('use_multithreading', True)
        is_manga_sequential = config.get('manga_mode_active') and config.get('manga_filename_style') in [STYLE_DATE_BASED, STYLE_POST_TITLE_GLOBAL_NUMBERING]

        should_use_multithreading_for_posts = use_multithreading and not is_single_post and not is_manga_sequential

        if should_use_multithreading_for_posts:
            fetcher_thread = threading.Thread(
                target=self._fetch_and_queue_posts_for_pool,
                args=(config, restore_data),
                daemon=True
            )
            fetcher_thread.start()
        else:
            self._start_single_threaded_session(config)

    def _start_single_threaded_session(self, config):
        """Handles downloads that are best processed by a single worker thread."""
        self._log("ℹ️ Initializing single-threaded download process...")
        self.worker_thread = threading.Thread(
            target=self._run_single_worker,
            args=(config,),
            daemon=True
        )
        self.worker_thread.start()

    def _run_single_worker(self, config):
        """Target function for the single-worker thread."""
        try:
            worker = DownloadThread(config, self.progress_queue)
            worker.run() # This is the main blocking call for this thread
        except Exception as e:
            self._log(f"❌ CRITICAL ERROR in single-worker thread: {e}")
            self._log(traceback.format_exc())
        finally:
            self.is_running = False

    def _fetch_and_queue_posts_for_pool(self, config, restore_data):
        """
        Fetches all posts from the API and submits them as tasks to a thread pool.
        This method runs in its own dedicated thread to avoid blocking.
        """
        try:
            num_workers = min(config.get('num_threads', 4), MAX_THREADS)
            self.thread_pool = ThreadPoolExecutor(max_workers=num_workers, thread_name_prefix='PostWorker_')
            if restore_data:
                all_posts = restore_data['all_posts_data']
                processed_ids = set(restore_data['processed_post_ids'])
                posts_to_process = [p for p in all_posts if p.get('id') not in processed_ids]
                self.total_posts = len(all_posts)
                self.processed_posts = len(processed_ids)
                self._log(f"🔄 Restoring session. {len(posts_to_process)} posts remaining.")
            else:
                posts_to_process = self._get_all_posts(config)
                self.total_posts = len(posts_to_process)
                self.processed_posts = 0

            self.progress_queue.put({'type': 'overall_progress', 'payload': (self.total_posts, self.processed_posts)})
            
            if not posts_to_process:
                self._log("✅ No new posts to process.")
                return
            for post_data in posts_to_process:
                if self.cancellation_event.is_set():
                    break
                worker = PostProcessorWorker(post_data, config, self.progress_queue)
                future = self.thread_pool.submit(worker.process)
                future.add_done_callback(self._handle_future_result)
                self.active_futures.append(future)
        
        except Exception as e:
            self._log(f"❌ CRITICAL ERROR in post fetcher thread: {e}")
            self._log(traceback.format_exc())
        finally:
            if self.thread_pool:
                self.thread_pool.shutdown(wait=True)
            self.is_running = False
            self._log("🏁 All processing tasks have completed.")
            self.progress_queue.put({
                'type': 'finished',
                'payload': (self.total_downloads, self.total_skips, self.cancellation_event.is_set(), self.all_kept_original_filenames)
            })
    
    def _get_all_posts(self, config):
        """Helper to fetch all posts using the API client."""
        all_posts = []
        post_generator = download_from_api(
            api_url_input=config['api_url'],
            logger=self._log,
            start_page=config.get('start_page'),
            end_page=config.get('end_page'),
            manga_mode=config.get('manga_mode_active', False),
            cancellation_event=self.cancellation_event,
            pause_event=self.pause_event,
            use_cookie=config.get('use_cookie', False),
            cookie_text=config.get('cookie_text', ''),
            selected_cookie_file=config.get('selected_cookie_file'),
            app_base_dir=config.get('app_base_dir'),
            manga_filename_style_for_sort_check=config.get('manga_filename_style'),
            processed_post_ids=config.get('processed_post_ids', [])
        )
        for batch in post_generator:
            all_posts.extend(batch)
        return all_posts

    def _handle_future_result(self, future: Future):
        """Callback executed when a worker task completes."""
        if self.cancellation_event.is_set():
            return
            
        with threading.Lock(): # Protect shared counters
            self.processed_posts += 1
            try:
                if future.cancelled():
                    self._log("⚠️ A post processing task was cancelled.")
                    self.total_skips += 1
                else:
                    result = future.result()
                    (dl_count, skip_count, kept_originals, 
                     retryable, permanent, history) = result
                    self.total_downloads += dl_count
                    self.total_skips += skip_count
                    self.all_kept_original_filenames.extend(kept_originals)
                    if retryable:
                        self.progress_queue.put({'type': 'retryable_failure', 'payload': (retryable,)})
                    if permanent:
                        self.progress_queue.put({'type': 'permanent_failure', 'payload': (permanent,)})
                    if history:
                        self.progress_queue.put({'type': 'post_processed_history', 'payload': (history,)})

            except Exception as e:
                self._log(f"❌ Worker task resulted in an exception: {e}")
                self.total_skips += 1 # Count errored posts as skipped
            self.progress_queue.put({'type': 'overall_progress', 'payload': (self.total_posts, self.processed_posts)})

    def cancel_session(self):
        """Cancels the current running session."""
        if not self.is_running:
            return
        self._log("⚠️ Cancellation requested by user...")
        self.cancellation_event.set()
        if self.thread_pool:
            self.thread_pool.shutdown(wait=False, cancel_futures=True)
            
        self.is_running = False
