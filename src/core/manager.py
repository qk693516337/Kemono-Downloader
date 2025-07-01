# --- Standard Library Imports ---
import threading
import time
import os
import json
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed, Future

# --- Local Application Imports ---
# These imports reflect the new, organized project structure.
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

        # --- Session State ---
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

        # --- Reset state for the new session ---
        self.is_running = True
        self.cancellation_event.clear()
        self.pause_event.clear()
        self.active_futures.clear()
        self.total_posts = 0
        self.processed_posts = 0
        self.total_downloads = 0
        self.total_skips = 0
        self.all_kept_original_filenames = []

        # --- Decide execution strategy (multi-threaded vs. single-threaded) ---
        is_single_post = bool(config.get('target_post_id_from_initial_url'))
        use_multithreading = config.get('use_multithreading', True)
        is_manga_sequential = config.get('manga_mode_active') and config.get('manga_filename_style') in [STYLE_DATE_BASED, STYLE_POST_TITLE_GLOBAL_NUMBERING]

        should_use_multithreading_for_posts = use_multithreading and not is_single_post and not is_manga_sequential

        if should_use_multithreading_for_posts:
            # Start a separate thread to manage fetching and queuing to the thread pool
            fetcher_thread = threading.Thread(
                target=self._fetch_and_queue_posts_for_pool,
                args=(config, restore_data),
                daemon=True
            )
            fetcher_thread.start()
        else:
            # For single posts or sequential manga mode, use a single worker thread
            # which is simpler and ensures order.
            self._start_single_threaded_session(config)

    def _start_single_threaded_session(self, config):
        """Handles downloads that are best processed by a single worker thread."""
        self._log("ℹ️ Initializing single-threaded download process...")
        
        # The original DownloadThread is now a pure Python thread, not a QThread.
        # We run its `run` method in a standard Python thread.
        self.worker_thread = threading.Thread(
            target=self._run_single_worker,
            args=(config,),
            daemon=True
        )
        self.worker_thread.start()

    def _run_single_worker(self, config):
        """Target function for the single-worker thread."""
        try:
            # Pass the queue directly to the worker for it to send updates
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
            
            # Fetch posts
            # In a real implementation, this would call `api_client.download_from_api`
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

            # Submit tasks to the pool
            for post_data in posts_to_process:
                if self.cancellation_event.is_set():
                    break
                # Each PostProcessorWorker gets the queue to send its own updates
                worker = PostProcessorWorker(post_data, config, self.progress_queue)
                future = self.thread_pool.submit(worker.process)
                future.add_done_callback(self._handle_future_result)
                self.active_futures.append(future)
        
        except Exception as e:
            self._log(f"❌ CRITICAL ERROR in post fetcher thread: {e}")
            self._log(traceback.format_exc())
        finally:
            # Wait for all submitted tasks to complete before shutting down
            if self.thread_pool:
                self.thread_pool.shutdown(wait=True)
            self.is_running = False
            self._log("🏁 All processing tasks have completed.")
            # Emit final signal
            self.progress_queue.put({
                'type': 'finished',
                'payload': (self.total_downloads, self.total_skips, self.cancellation_event.is_set(), self.all_kept_original_filenames)
            })

    def _get_all_posts(self, config):
        """Helper to fetch all posts using the API client."""
        all_posts = []
        # This generator yields batches of posts
        post_generator = download_from_api(
            api_url_input=config['api_url'],
            logger=self._log,
            # ... pass other relevant config keys ...
            cancellation_event=self.cancellation_event,
            pause_event=self.pause_event
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
                    # Unpack result tuple from the worker
                    (dl_count, skip_count, kept_originals, 
                     retryable, permanent, history) = result
                    self.total_downloads += dl_count
                    self.total_skips += skip_count
                    self.all_kept_original_filenames.extend(kept_originals)
                    
                    # Queue up results for UI to handle
                    if retryable:
                        self.progress_queue.put({'type': 'retryable_failure', 'payload': (retryable,)})
                    if permanent:
                        self.progress_queue.put({'type': 'permanent_failure', 'payload': (permanent,)})
                    if history:
                        self.progress_queue.put({'type': 'post_processed_history', 'payload': (history,)})

            except Exception as e:
                self._log(f"❌ Worker task resulted in an exception: {e}")
                self.total_skips += 1 # Count errored posts as skipped

            # Update overall progress
            self.progress_queue.put({'type': 'overall_progress', 'payload': (self.total_posts, self.processed_posts)})

    def cancel_session(self):
        """Cancels the current running session."""
        if not self.is_running:
            return
        self._log("⚠️ Cancellation requested by user...")
        self.cancellation_event.set()
        
        # For single thread mode, the worker checks the event
        # For multi-thread mode, shut down the pool
        if self.thread_pool:
            # Don't wait, just cancel pending futures and let the fetcher thread exit
            self.thread_pool.shutdown(wait=False, cancel_futures=True)
            
        self.is_running = False
