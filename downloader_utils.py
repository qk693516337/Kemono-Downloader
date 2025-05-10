import os
import time
import requests
import re
import threading
import queue # Not directly used for link queue, but kept for historical reasons
import hashlib
import http.client
import traceback
from concurrent.futures import ThreadPoolExecutor, Future, CancelledError, as_completed
import html

from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMutex, QMutexLocker
from urllib.parse import urlparse
try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow library not found. Please install it: pip install Pillow")
    Image = None


from io import BytesIO

# Constants for filename styles, mirroring main.py for clarity if used directly here
STYLE_POST_TITLE = "post_title"
STYLE_ORIGINAL_NAME = "original_name"

# Constants for skip_words_scope, mirroring main.py
SKIP_SCOPE_FILES = "files"
SKIP_SCOPE_POSTS = "posts"
SKIP_SCOPE_BOTH = "both"

fastapi_app = None
KNOWN_NAMES = []

IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp',
    '.heic', '.heif', '.svg', '.ico', '.jfif', '.pjpeg', '.pjp', '.avif'
}
VIDEO_EXTENSIONS = {
    '.mp4', '.mov', '.mkv', '.webm', '.avi', '.wmv', '.flv', '.mpeg',
    '.mpg', '.m4v', '.3gp', '.ogv', '.ts', '.vob'
}
# ADDED: Archive Extensions
ARCHIVE_EXTENSIONS = {
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2' # Added more common archive types
}

def is_title_match_for_character(post_title, character_name_filter):
    """Checks if a post title contains a specific character name (case-insensitive, whole word)."""
    if not post_title or not character_name_filter:
        return False
    pattern = r"(?i)\b" + re.escape(character_name_filter) + r"\b"
    return bool(re.search(pattern, post_title))

def is_filename_match_for_character(filename, character_name_filter):
    """Checks if a filename contains a specific character name (case-insensitive, substring)."""
    if not filename or not character_name_filter:
        return False
    return character_name_filter.lower() in filename.lower()


def clean_folder_name(name):
    """Cleans a string to be suitable for a folder name."""
    if not isinstance(name, str): name = str(name)
    cleaned = re.sub(r'[^\w\s\-\_\.\(\)]', '', name)
    cleaned = cleaned.strip()
    cleaned = re.sub(r'\s+', '_', cleaned)
    return cleaned if cleaned else "untitled_folder"


def clean_filename(name):
    """Cleans a string to be suitable for a file name."""
    if not isinstance(name, str): name = str(name)
    cleaned = re.sub(r'[^\w\s\-\_\.\(\)]', '', name)
    cleaned = cleaned.strip()
    cleaned = re.sub(r'\s+', '_', cleaned)
    return cleaned if cleaned else "untitled_file"


def extract_folder_name_from_title(title, unwanted_keywords):
    """Extracts a potential folder name from a title, avoiding unwanted keywords."""
    if not title: return 'Uncategorized'
    title_lower = title.lower()
    tokens = re.findall(r'\b[\w\-]+\b', title_lower)
    for token in tokens:
        clean_token = clean_folder_name(token)
        if clean_token and clean_token.lower() not in unwanted_keywords:
            return clean_token
    cleaned_full_title = clean_folder_name(title)
    return cleaned_full_title if cleaned_full_title else 'Uncategorized'


def match_folders_from_title(title, names_to_match, unwanted_keywords):
    """
    Matches names from a list against a title to determine potential folder names.
    Prioritizes longer matches.
    """
    if not title or not names_to_match: return []
    title_lower = title.lower()
    matched_cleaned_names = set()
    sorted_names_to_match = sorted(names_to_match, key=len, reverse=True)

    for name in sorted_names_to_match:
        name_lower = name.lower()
        if not name_lower: continue

        pattern = r'\b' + re.escape(name_lower) + r'\b'
        if re.search(pattern, title_lower):
             cleaned_name_for_folder = clean_folder_name(name)
             if cleaned_name_for_folder.lower() not in unwanted_keywords:
                 matched_cleaned_names.add(cleaned_name_for_folder)
    return sorted(list(matched_cleaned_names))


def is_image(filename):
    """Checks if the filename has a common image extension."""
    if not filename: return False
    _, ext = os.path.splitext(filename)
    return ext.lower() in IMAGE_EXTENSIONS


def is_video(filename):
    """Checks if the filename has a common video extension."""
    if not filename: return False
    _, ext = os.path.splitext(filename)
    return ext.lower() in VIDEO_EXTENSIONS


def is_zip(filename):
    """Checks if the filename ends with .zip (case-insensitive)."""
    if not filename: return False
    return filename.lower().endswith('.zip')


def is_rar(filename):
    """Checks if the filename ends with .rar (case-insensitive)."""
    if not filename: return False
    return filename.lower().endswith('.rar')

# ADDED: Generic is_archive function
def is_archive(filename):
    """Checks if the filename has a common archive extension."""
    if not filename: return False
    _, ext = os.path.splitext(filename)
    return ext.lower() in ARCHIVE_EXTENSIONS


def is_post_url(url):
    """Checks if the URL likely points to a specific post."""
    if not isinstance(url, str): return False
    return '/post/' in urlparse(url).path


def extract_post_info(url_string):
    """Extracts service, user ID, and post ID from a Kemono/Coomer URL."""
    service, user_id, post_id = None, None, None
    if not isinstance(url_string, str) or not url_string.strip(): return None, None, None
    try:
        parsed_url = urlparse(url_string.strip())
        domain = parsed_url.netloc.lower()
        is_kemono = any(d in domain for d in ['kemono.su', 'kemono.party'])
        is_coomer = any(d in domain for d in ['coomer.su', 'coomer.party'])

        if not (is_kemono or is_coomer): return None, None, None

        path_parts = [part for part in parsed_url.path.strip('/').split('/') if part]

        if len(path_parts) >= 3 and path_parts[1].lower() == 'user':
            service = path_parts[0]
            user_id = path_parts[2]
            if len(path_parts) >= 5 and path_parts[3].lower() == 'post':
                post_id = path_parts[4]
            return service, user_id, post_id

        if len(path_parts) >= 5 and path_parts[0].lower() == 'api' and \
           path_parts[1].lower() == 'v1' and path_parts[3].lower() == 'user':
            service = path_parts[2]
            user_id = path_parts[4]
            if len(path_parts) >= 7 and path_parts[5].lower() == 'post':
                post_id = path_parts[6]
            return service, user_id, post_id

    except Exception as e:
        print(f"Debug: Exception during extract_post_info for URL '{url_string}': {e}")
    return None, None, None


def fetch_posts_paginated(api_url_base, headers, offset, logger, cancellation_event=None):
    """Fetches a single page of posts from the API."""
    if cancellation_event and cancellation_event.is_set():
        logger("   Fetch cancelled before request.")
        raise RuntimeError("Fetch operation cancelled by user.")

    paginated_url = f'{api_url_base}?o={offset}'
    logger(f"   Fetching: {paginated_url} (Page approx. {offset // 50 + 1})")
    try:
        response = requests.get(paginated_url, headers=headers, timeout=(10, 60))
        response.raise_for_status()
        if 'application/json' not in response.headers.get('Content-Type', '').lower():
            logger(f"⚠️ Unexpected content type from API: {response.headers.get('Content-Type')}. Body: {response.text[:200]}")
            return [] # Return empty list on unexpected content type
        return response.json()
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Timeout fetching offset {offset} from {paginated_url}")
    except requests.exceptions.RequestException as e:
        err_msg = f"Error fetching offset {offset} from {paginated_url}: {e}"
        if e.response is not None:
            err_msg += f" (Status: {e.response.status_code}, Body: {e.response.text[:200]})"
        raise RuntimeError(err_msg)
    except ValueError as e: # JSONDecodeError is a subclass of ValueError
        raise RuntimeError(f"Error decoding JSON from offset {offset} ({paginated_url}): {e}. Response text: {response.text[:200]}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error fetching offset {offset} ({paginated_url}): {e}")


def download_from_api(api_url_input, logger=print, start_page=None, end_page=None, manga_mode=False, cancellation_event=None):
    """
    Generator function to fetch post data from Kemono/Coomer API.
    Handles pagination and yields batches of posts.
    In Manga Mode, fetches all posts first, then yields them in reverse order (oldest first).
    If target_post_id is specified, it will paginate until that post is found or all pages are exhausted.
    """
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
    service, user_id, target_post_id = extract_post_info(api_url_input)

    if cancellation_event and cancellation_event.is_set():
        logger("   Download_from_api cancelled at start.")
        return

    if not service or not user_id:
        logger(f"❌ Invalid URL or could not extract service/user: {api_url_input}")
        return

    if target_post_id and (start_page or end_page):
        logger("⚠️ Page range (start/end page) is ignored when a specific post URL is provided (searching all pages for the post).")
        start_page = end_page = None # Ensure no page limits when searching for a specific post

    is_creator_feed_for_manga = manga_mode and not target_post_id

    parsed_input = urlparse(api_url_input)
    api_domain = parsed_input.netloc
    if not any(d in api_domain.lower() for d in ['kemono.su', 'kemono.party', 'coomer.su', 'coomer.party']):
        logger(f"⚠️ Unrecognized domain '{api_domain}'. Defaulting to kemono.su for API calls.")
        api_domain = "kemono.su"

    api_base_url = f"https://{api_domain}/api/v1/{service}/user/{user_id}"
    page_size = 50 # Kemono API typically returns 50 posts per page

    if is_creator_feed_for_manga:
        logger("   Manga Mode: Fetching all posts to reverse order (oldest posts processed first)...")
        all_posts_for_manga_mode = []
        current_offset_manga = 0
        while True:
            if cancellation_event and cancellation_event.is_set():
                logger("   Manga mode post fetching cancelled.")
                break
            try:
                posts_batch_manga = fetch_posts_paginated(api_base_url, headers, current_offset_manga, logger, cancellation_event)
                if not isinstance(posts_batch_manga, list):
                    logger(f"❌ API Error (Manga Mode): Expected list of posts, got {type(posts_batch_manga)}.")
                    break
                if not posts_batch_manga:
                    logger("✅ Reached end of posts (Manga Mode fetch all).")
                    break
                all_posts_for_manga_mode.extend(posts_batch_manga)
                current_offset_manga += len(posts_batch_manga) # Use actual length
                time.sleep(0.6)
            except RuntimeError as e:
                if "cancelled by user" in str(e).lower():
                    logger(f"ℹ️ Manga mode pagination stopped due to cancellation: {e}")
                else:
                    logger(f"❌ {e}\n   Aborting manga mode pagination.")
                break # Stop on runtime error
            except Exception as e: # Catch any other unexpected errors
                logger(f"❌ Unexpected error during manga mode fetch: {e}")
                traceback.print_exc()
                break # Stop on other errors
        
        if cancellation_event and cancellation_event.is_set(): return

        if all_posts_for_manga_mode:
            logger(f"   Manga Mode: Fetched {len(all_posts_for_manga_mode)} total posts. Reversing order...")
            all_posts_for_manga_mode.reverse() # Oldest first

            for i in range(0, len(all_posts_for_manga_mode), page_size):
                if cancellation_event and cancellation_event.is_set():
                    logger("   Manga mode post yielding cancelled.")
                    break
                yield all_posts_for_manga_mode[i:i + page_size]
        else:
            logger("   Manga Mode: No posts found to process.")
        return # End of manga mode logic

    # --- Regular pagination (Creator feed or Single Post search) ---
    current_page_num = 1
    current_offset = 0
    processed_target_post_flag = False

    if start_page and start_page > 1 and not target_post_id: # Only apply start_page if not searching for a specific post
        current_offset = (start_page - 1) * page_size
        current_page_num = start_page
        logger(f"   Starting from page {current_page_num} (calculated offset {current_offset}).")

    while True:
        if cancellation_event and cancellation_event.is_set():
            logger("   Post fetching loop cancelled.")
            break
        
        if target_post_id and processed_target_post_flag: # If target post was found and yielded in a previous iteration
            # logger(f"✅ Target post {target_post_id} was processed. Stopping pagination.") # Logged when found
            break

        # For creator feeds (not target_post_id mode), check end_page limit
        if not target_post_id and end_page and current_page_num > end_page:
            logger(f"✅ Reached specified end page ({end_page}) for creator feed. Stopping.")
            break

        try:
            posts_batch = fetch_posts_paginated(api_base_url, headers, current_offset, logger, cancellation_event)
            if not isinstance(posts_batch, list):
                logger(f"❌ API Error: Expected list of posts, got {type(posts_batch)} at page {current_page_num} (offset {current_offset}).")
                break
        except RuntimeError as e:
            if "cancelled by user" in str(e).lower():
                 logger(f"ℹ️ Pagination stopped due to cancellation: {e}")
            else:
                logger(f"❌ {e}\n   Aborting pagination at page {current_page_num} (offset {current_offset}).")
            break # Stop on runtime error
        except Exception as e: # Catch any other unexpected errors
            logger(f"❌ Unexpected error fetching page {current_page_num} (offset {current_offset}): {e}")
            traceback.print_exc()
            break # Stop on other errors

        if not posts_batch: # API returned an empty list, meaning no more posts
            if target_post_id and not processed_target_post_flag:
                logger(f"❌ Target post {target_post_id} not found after checking all available pages (API returned no more posts at offset {current_offset}).")
            elif not target_post_id: # Normal creator feed end
                if current_page_num == (start_page or 1): # Check if it was the first page attempted
                     logger(f"😕 No posts found on the first page checked (page {current_page_num}, offset {current_offset}).")
                else:
                     logger(f"✅ Reached end of posts (no more content from API at offset {current_offset}).")
            break # Exit while loop

        if target_post_id and not processed_target_post_flag:
            matching_post = next((p for p in posts_batch if str(p.get('id')) == str(target_post_id)), None)
            if matching_post:
                logger(f"🎯 Found target post {target_post_id} on page {current_page_num} (offset {current_offset}).")
                yield [matching_post] # Yield only the matching post as a list
                processed_target_post_flag = True
                # Loop will break at the top in the next iteration due to processed_target_post_flag
            # If not found in this batch, the loop continues to the next page.
            # Logger message for "not found in batch" is removed here to avoid spam if post is on a later page.
        elif not target_post_id: # Processing a creator feed (no specific target post)
            yield posts_batch

        if processed_target_post_flag: # If we just found and yielded the target post, stop.
            break

        # Increment page and offset for the next iteration
        current_offset += len(posts_batch) # Use actual length of batch for offset
        current_page_num += 1
        time.sleep(0.6) # Keep the delay
            
    # Final check after the loop, specifically if a target post was being searched for but not found
    if target_post_id and not processed_target_post_flag and not (cancellation_event and cancellation_event.is_set()):
        # This log might be redundant if the one inside "if not posts_batch:" already covered it,
        # but it serves as a final confirmation if the loop exited for other reasons before exhausting pages.
        logger(f"❌ Target post {target_post_id} could not be found after checking all relevant pages (final check after loop).")


def get_link_platform(url):
    """Attempts to identify the platform of an external link from its domain."""
    try:
        domain = urlparse(url).netloc.lower()
        if 'drive.google.com' in domain: return 'google drive'
        if 'mega.nz' in domain or 'mega.io' in domain: return 'mega'
        if 'dropbox.com' in domain: return 'dropbox'
        if 'patreon.com' in domain: return 'patreon'
        if 'instagram.com' in domain: return 'instagram'
        if 'twitter.com' in domain or 'x.com' in domain: return 'twitter/x'
        if 'discord.gg' in domain or 'discord.com/invite' in domain: return 'discord invite'
        if 'pixiv.net' in domain: return 'pixiv'
        if 'kemono.su' in domain or 'kemono.party' in domain: return 'kemono'
        if 'coomer.su' in domain or 'coomer.party' in domain: return 'coomer'

        parts = domain.split('.')
        if len(parts) >= 2:
            if parts[-2] not in ['com', 'org', 'net', 'gov', 'edu', 'co'] or len(parts) == 2:
                 return parts[-2]
            elif len(parts) >= 3 and parts[-3] not in ['com', 'org', 'net', 'gov', 'edu', 'co']:
                 return parts[-3]
            else:
                 return domain
        return 'external'
    except Exception: return 'unknown'


class PostProcessorSignals(QObject):
    """Defines signals used by PostProcessorWorker to communicate with the GUI thread."""
    progress_signal = pyqtSignal(str)
    file_download_status_signal = pyqtSignal(bool)
    external_link_signal = pyqtSignal(str, str, str, str)
    file_progress_signal = pyqtSignal(str, int, int)


class PostProcessorWorker:
    """Processes a single post: determines save paths, downloads files, handles compression."""
    def __init__(self, post_data, download_root, known_names,
                 filter_character_list,
                 unwanted_keywords, filter_mode, skip_zip, skip_rar,
                 use_subfolders, use_post_subfolders, target_post_id_from_initial_url, custom_folder_name,
                 compress_images, download_thumbnails, service, user_id,
                 api_url_input, cancellation_event, signals,
                 downloaded_files, downloaded_file_hashes, downloaded_files_lock, downloaded_file_hashes_lock,
                 skip_words_list=None, 
                 skip_words_scope=SKIP_SCOPE_FILES, # New parameter with default
                 show_external_links=False,
                 extract_links_only=False,
                 num_file_threads=4, skip_current_file_flag=None,
                 manga_mode_active=False,
                 manga_filename_style=STYLE_POST_TITLE
                 ):
        self.post = post_data
        self.download_root = download_root
        self.known_names = known_names
        self.filter_character_list = filter_character_list if filter_character_list else []
        self.unwanted_keywords = unwanted_keywords if unwanted_keywords is not None else set()
        self.filter_mode = filter_mode
        self.skip_zip = skip_zip
        self.skip_rar = skip_rar
        self.use_subfolders = use_subfolders
        self.use_post_subfolders = use_post_subfolders
        self.target_post_id_from_initial_url = target_post_id_from_initial_url
        self.custom_folder_name = custom_folder_name
        self.compress_images = compress_images
        self.download_thumbnails = download_thumbnails
        self.service = service
        self.user_id = user_id
        self.api_url_input = api_url_input
        self.cancellation_event = cancellation_event
        self.signals = signals
        self.skip_current_file_flag = skip_current_file_flag

        self.downloaded_files = downloaded_files if downloaded_files is not None else set()
        self.downloaded_file_hashes = downloaded_file_hashes if downloaded_file_hashes is not None else set()
        self.downloaded_files_lock = downloaded_files_lock if downloaded_files_lock is not None else threading.Lock()
        self.downloaded_file_hashes_lock = downloaded_file_hashes_lock if downloaded_file_hashes_lock is not None else threading.Lock()

        self.skip_words_list = skip_words_list if skip_words_list is not None else []
        self.skip_words_scope = skip_words_scope # Store the new scope
        self.show_external_links = show_external_links
        self.extract_links_only = extract_links_only
        self.num_file_threads = num_file_threads

        self.manga_mode_active = manga_mode_active
        self.manga_filename_style = manga_filename_style

        if self.compress_images and Image is None:
            self.logger("⚠️ Image compression disabled: Pillow library not found.")
            self.compress_images = False

    def logger(self, message):
        """Emits a log message via the progress_signal if available."""
        if self.signals and hasattr(self.signals, 'progress_signal'):
            self.signals.progress_signal.emit(message)
        else:
            print(f"(Worker Log - No Signal): {message}")

    def check_cancel(self):
        """Checks if cancellation has been requested."""
        return self.cancellation_event.is_set()

    def _download_single_file(self, file_info, target_folder_path, headers, original_post_id_for_log, skip_event,
                              post_title="", file_index_in_post=0, num_files_in_this_post=1):
        """
        Downloads a single file, handles retries, compression, and hash checking.
        Returns:
            (int, int, str, bool): (downloaded_count, skipped_count, final_filename_saved, was_original_name_kept_flag)
        """
        was_original_name_kept_flag = False 
        final_filename_saved_for_return = ""


        if self.check_cancel() or (skip_event and skip_event.is_set()): return 0, 1, "", False

        file_url = file_info.get('url')
        api_original_filename = file_info.get('_original_name_for_log', file_info.get('name'))

        if not file_url or not api_original_filename:
            self.logger(f"⚠️ Skipping file from post {original_post_id_for_log}: Missing URL or original filename. Info: {str(file_info)[:100]}")
            return 0, 1, api_original_filename or "", False

        final_filename_saved_for_return = api_original_filename 

        # Apply skip_words_list based on skip_words_scope (for files)
        if self.skip_words_list and (self.skip_words_scope == SKIP_SCOPE_FILES or self.skip_words_scope == SKIP_SCOPE_BOTH):
            filename_to_check_for_skip_words = api_original_filename.lower()
            for skip_word in self.skip_words_list:
                if skip_word.lower() in filename_to_check_for_skip_words:
                    self.logger(f"   -> Skip File (Keyword in Original Name '{skip_word}'): '{api_original_filename}'. Scope: {self.skip_words_scope}")
                    return 0, 1, api_original_filename, False
        
        if self.filter_character_list:
            matches_any_character_filter = False
            if self.manga_mode_active: # In manga mode, character filter applies to post title primarily
                if any(is_title_match_for_character(post_title, char_filter) for char_filter in self.filter_character_list):
                    matches_any_character_filter = True
                # Fallback: if title doesn't match, but filename does, still consider it a match for manga mode if desired
                # For now, let's stick to title match for manga post filtering, file name match for file filtering.
                # If you want manga mode character filter to also check filenames, uncomment below:
                # if not matches_any_character_filter and any(is_filename_match_for_character(api_original_filename, char_filter) for char_filter in self.filter_character_list):
                #      matches_any_character_filter = True
            else: # Normal mode, character filter applies to filename
                if any(is_filename_match_for_character(api_original_filename, char_filter) for char_filter in self.filter_character_list):
                    matches_any_character_filter = True
            
            if not matches_any_character_filter: # If no character filter matched (based on mode)
                self.logger(f"   -> Skip File (No Char Match): '{api_original_filename}' (Post: '{post_title[:30]}...') doesn't match character filters.")
                return 0, 1, api_original_filename, False
        
        original_filename_cleaned_base, original_ext = os.path.splitext(clean_filename(api_original_filename))
        if not original_ext.startswith('.'): original_ext = '.' + original_ext if original_ext else ''

        filename_to_save = ""
        if self.manga_mode_active:
            if self.manga_filename_style == STYLE_ORIGINAL_NAME:
                filename_to_save = clean_filename(api_original_filename)
                was_original_name_kept_flag = True # Original name is kept by definition here
            elif self.manga_filename_style == STYLE_POST_TITLE:
                if post_title and post_title.strip():
                    cleaned_post_title_base = clean_filename(post_title.strip())
                    if num_files_in_this_post > 1: # Multi-file post
                        if file_index_in_post == 0: # First file of multi-file post
                            filename_to_save = f"{cleaned_post_title_base}{original_ext}"
                            was_original_name_kept_flag = False
                        else: # Subsequent files of multi-file post
                            filename_to_save = clean_filename(api_original_filename) # Keep original for subsequent
                            was_original_name_kept_flag = True 
                    else: # Single file post in manga mode
                        filename_to_save = f"{cleaned_post_title_base}{original_ext}"
                        was_original_name_kept_flag = False
                else: # Manga mode, post title style, but post_title is missing
                    filename_to_save = clean_filename(api_original_filename)
                    was_original_name_kept_flag = False # Not truly "kept original" in the spirit of the style choice
                    self.logger(f"⚠️ Manga mode (Post Title Style): Post title missing for post {original_post_id_for_log}. Using cleaned original filename '{filename_to_save}'.")
            else: # Unknown manga style
                self.logger(f"⚠️ Manga mode: Unknown filename style '{self.manga_filename_style}'. Defaulting to original filename for '{api_original_filename}'.")
                filename_to_save = clean_filename(api_original_filename)
                was_original_name_kept_flag = False # Or True, depending on interpretation. Let's say False as it's a fallback.

            # Collision handling for manga mode filenames
            if filename_to_save:
                counter = 1
                base_name_coll, ext_coll = os.path.splitext(filename_to_save)
                temp_filename_for_collision_check = filename_to_save
                # Ensure unique filename in target folder
                while os.path.exists(os.path.join(target_folder_path, temp_filename_for_collision_check)):
                    # If it's the first file of a multi-file post using post_title style, append _N
                    if self.manga_filename_style == STYLE_POST_TITLE and file_index_in_post == 0 and num_files_in_this_post > 1:
                         temp_filename_for_collision_check = f"{base_name_coll}_{counter}{ext_coll}"
                    # If it's original name style, or subsequent file, or single file post, append _N to its base
                    else:
                         temp_filename_for_collision_check = f"{base_name_coll}_{counter}{ext_coll}"
                    counter += 1
                if temp_filename_for_collision_check != filename_to_save:
                    filename_to_save = temp_filename_for_collision_check
            else: # Fallback if filename_to_save ended up empty
                filename_to_save = f"manga_file_{original_post_id_for_log}_{file_index_in_post + 1}{original_ext}"
                self.logger(f"⚠️ Manga mode: Generated filename was empty. Using generic fallback: '{filename_to_save}'.")
                was_original_name_kept_flag = False

        else: # Not Manga Mode
            filename_to_save = clean_filename(api_original_filename)
            was_original_name_kept_flag = False # Not manga mode, so this flag isn't relevant in the same way
            # Collision handling for non-manga mode
            counter = 1
            base_name_coll, ext_coll = os.path.splitext(filename_to_save)
            temp_filename_for_collision_check = filename_to_save
            while os.path.exists(os.path.join(target_folder_path, temp_filename_for_collision_check)):
                temp_filename_for_collision_check = f"{base_name_coll}_{counter}{ext_coll}"
                counter += 1
            if temp_filename_for_collision_check != filename_to_save:
                filename_to_save = temp_filename_for_collision_check

        final_filename_for_sets_and_saving = filename_to_save
        final_filename_saved_for_return = final_filename_for_sets_and_saving 

        if not self.download_thumbnails:
            # Determine file type based on the original API filename
            is_img_type = is_image(api_original_filename)
            is_vid_type = is_video(api_original_filename)
            # Use the generic is_archive function
            is_archive_type = is_archive(api_original_filename)


            # ===== MODIFICATION START =====
            if self.filter_mode == 'archive':
                if not is_archive_type: # If in 'archive' mode and the file is NOT an archive
                    self.logger(f"   -> Filter Skip (Archive Mode): '{api_original_filename}' (Not an Archive).")
                    return 0, 1, api_original_filename, False
                # If it IS an archive, it will proceed.
                # self.skip_zip and self.skip_rar are False in this mode (set in main.py), so they won't cause a skip.
            elif self.filter_mode == 'image':
                if not is_img_type:
                    self.logger(f"   -> Filter Skip: '{api_original_filename}' (Not Image).")
                    return 0, 1, api_original_filename, False
            elif self.filter_mode == 'video':
                if not is_vid_type:
                    self.logger(f"   -> Filter Skip: '{api_original_filename}' (Not Video).")
                    return 0, 1, api_original_filename, False
            # No specific 'elif self.filter_mode == 'all':' is needed here, as 'all' implies no primary type filtering.
            # The self.skip_zip / self.skip_rar checks below will handle user preference for skipping archives in 'all' mode.

            # These skip checks are now primarily for 'all' mode or if filter_mode is something else.
            # In 'archive' mode, self.skip_zip and self.skip_rar will be False.
            if self.skip_zip and is_zip(api_original_filename): # Use specific is_zip for the skip_zip flag
                self.logger(f"   -> Pref Skip: '{api_original_filename}' (ZIP).")
                return 0, 1, api_original_filename, False
            if self.skip_rar and is_rar(api_original_filename): # Use specific is_rar for the skip_rar flag
                self.logger(f"   -> Pref Skip: '{api_original_filename}' (RAR).")
                return 0, 1, api_original_filename, False
            # ===== MODIFICATION END =====

        target_folder_basename = os.path.basename(target_folder_path)
        current_save_path = os.path.join(target_folder_path, final_filename_for_sets_and_saving)

        if os.path.exists(current_save_path) and os.path.getsize(current_save_path) > 0:
             self.logger(f"   -> Exists (Path): '{final_filename_for_sets_and_saving}' in '{target_folder_basename}'.")
             with self.downloaded_files_lock: self.downloaded_files.add(final_filename_for_sets_and_saving) # Add final name
             return 0, 1, final_filename_for_sets_and_saving, was_original_name_kept_flag
        
        with self.downloaded_files_lock:
            if final_filename_for_sets_and_saving in self.downloaded_files:
                self.logger(f"   -> Global Skip (Filename): '{final_filename_for_sets_and_saving}' already recorded this session.")
                return 0, 1, final_filename_for_sets_and_saving, was_original_name_kept_flag

        max_retries = 3
        retry_delay = 5
        downloaded_size_bytes = 0
        calculated_file_hash = None
        file_content_bytes = None
        total_size_bytes = 0 # Initialize total_size_bytes for this download attempt
        download_successful_flag = False

        for attempt_num in range(max_retries + 1):
            if self.check_cancel() or (skip_event and skip_event.is_set()):
                break
            try:
                if attempt_num > 0:
                    self.logger(f"   Retrying '{api_original_filename}' (Attempt {attempt_num}/{max_retries})...")
                    time.sleep(retry_delay * (2**(attempt_num - 1))) # Exponential backoff

                if self.signals and hasattr(self.signals, 'file_download_status_signal'):
                    self.signals.file_download_status_signal.emit(True) # Indicate download attempt start

                response = requests.get(file_url, headers=headers, timeout=(15, 300), stream=True) # Generous timeout
                response.raise_for_status() # Check for HTTP errors

                current_total_size_bytes_from_headers = int(response.headers.get('Content-Length', 0))

                if attempt_num == 0: # Only set total_size_bytes on the first attempt from headers
                    total_size_bytes = current_total_size_bytes_from_headers
                    size_str = f"{total_size_bytes / (1024 * 1024):.2f} MB" if total_size_bytes > 0 else "unknown size"
                    self.logger(f"⬇️ Downloading: '{api_original_filename}' (Size: {size_str}) [Saving as: '{final_filename_for_sets_and_saving}']")

                current_attempt_total_size = total_size_bytes # Use the initial total_size for progress calculation
                
                file_content_buffer = BytesIO()
                current_attempt_downloaded_bytes = 0
                md5_hasher = hashlib.md5()
                last_progress_time = time.time()

                for chunk in response.iter_content(chunk_size=1 * 1024 * 1024): # 1MB chunks
                    if self.check_cancel() or (skip_event and skip_event.is_set()):
                        break
                    if chunk:
                        file_content_buffer.write(chunk)
                        md5_hasher.update(chunk)
                        current_attempt_downloaded_bytes += len(chunk)
                        if time.time() - last_progress_time > 1 and current_attempt_total_size > 0 and \
                           self.signals and hasattr(self.signals, 'file_progress_signal'):
                            self.signals.file_progress_signal.emit(
                                api_original_filename, # Show original name in progress
                                current_attempt_downloaded_bytes,
                                current_attempt_total_size
                            )
                            last_progress_time = time.time()
                
                if self.check_cancel() or (skip_event and skip_event.is_set()):
                    if file_content_buffer: file_content_buffer.close()
                    break # Exit retry loop if cancelled
                
                # After loop, check if download was successful for this attempt
                if current_attempt_downloaded_bytes > 0 or (current_attempt_total_size == 0 and response.status_code == 200): # Successfully downloaded something or it's a valid 0-byte file
                    calculated_file_hash = md5_hasher.hexdigest()
                    downloaded_size_bytes = current_attempt_downloaded_bytes
                    if file_content_bytes: file_content_bytes.close() # Close previous buffer if any
                    file_content_bytes = file_content_buffer # Assign the new buffer
                    file_content_bytes.seek(0) # Rewind for reading
                    download_successful_flag = True
                    break # Successful download, exit retry loop
                else: # No bytes downloaded, and not a 0-byte file case
                    if file_content_buffer: file_content_buffer.close()
                    # Continue to next retry if not max retries

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, http.client.IncompleteRead) as e:
                self.logger(f"   ❌ Download Error (Retryable): {api_original_filename}. Error: {e}")
                if 'file_content_buffer' in locals() and file_content_buffer: file_content_buffer.close()
                # Continue to next retry if not max retries
            except requests.exceptions.RequestException as e: # Non-retryable HTTP errors
                self.logger(f"   ❌ Download Error (Non-Retryable): {api_original_filename}. Error: {e}")
                if 'file_content_buffer' in locals() and file_content_buffer: file_content_buffer.close()
                break # Exit retry loop
            except Exception as e: # Other unexpected errors
                self.logger(f"   ❌ Unexpected Download Error: {api_original_filename}: {e}\n{traceback.format_exc(limit=2)}")
                if 'file_content_buffer' in locals() and file_content_buffer: file_content_buffer.close()
                break # Exit retry loop
            finally:
                if self.signals and hasattr(self.signals, 'file_download_status_signal'):
                    self.signals.file_download_status_signal.emit(False) # Indicate download attempt end
        
        # Final progress update after all retries or success
        if self.signals and hasattr(self.signals, 'file_progress_signal'):
             final_total_for_progress = total_size_bytes if download_successful_flag and total_size_bytes > 0 else downloaded_size_bytes
             self.signals.file_progress_signal.emit(api_original_filename, downloaded_size_bytes, final_total_for_progress)

        if self.check_cancel() or (skip_event and skip_event.is_set()):
            self.logger(f"   ⚠️ Download interrupted for {api_original_filename}.")
            if file_content_bytes: file_content_bytes.close()
            return 0, 1, final_filename_saved_for_return, was_original_name_kept_flag

        if not download_successful_flag:
            self.logger(f"❌ Download failed for '{api_original_filename}' after {max_retries + 1} attempts.")
            if file_content_bytes: file_content_bytes.close()
            return 0, 1, final_filename_saved_for_return, was_original_name_kept_flag

        # Check hash against already downloaded files (session-based)
        with self.downloaded_file_hashes_lock:
             if calculated_file_hash in self.downloaded_file_hashes:
                self.logger(f"   -> Content Skip (Hash): '{api_original_filename}' (Hash: {calculated_file_hash[:8]}...) already downloaded this session.")
                with self.downloaded_files_lock: self.downloaded_files.add(final_filename_for_sets_and_saving) # Add final name
                if file_content_bytes: file_content_bytes.close()
                return 0, 1, final_filename_for_sets_and_saving, was_original_name_kept_flag

        bytes_to_write = file_content_bytes # This is the BytesIO object with downloaded content
        final_filename_after_processing = final_filename_for_sets_and_saving
        current_save_path_final = current_save_path # Path with potentially collided name

        is_img_for_compress_check = is_image(api_original_filename) # Check original name for image type
        if is_img_for_compress_check and self.compress_images and Image and downloaded_size_bytes > (1.5 * 1024 * 1024): # 1.5MB threshold
            self.logger(f"   Compressing '{api_original_filename}' ({downloaded_size_bytes / (1024*1024):.2f} MB)...")
            try:
                bytes_to_write.seek(0) # Ensure buffer is at the beginning
                with Image.open(bytes_to_write) as img_obj:
                    # Handle palette mode images by converting to RGBA/RGB
                    if img_obj.mode == 'P': img_obj = img_obj.convert('RGBA')
                    elif img_obj.mode not in ['RGB', 'RGBA', 'L']: img_obj = img_obj.convert('RGB')

                    compressed_bytes_io = BytesIO()
                    img_obj.save(compressed_bytes_io, format='WebP', quality=80, method=4) # method=4 is a good balance
                    compressed_size = compressed_bytes_io.getbuffer().nbytes

                if compressed_size < downloaded_size_bytes * 0.9: # Only save if significantly smaller (e.g., 10% reduction)
                    self.logger(f"   Compression success: {compressed_size / (1024*1024):.2f} MB.")
                    bytes_to_write.close() # Close original downloaded buffer
                    bytes_to_write = compressed_bytes_io # Switch to compressed buffer
                    bytes_to_write.seek(0) # Rewind compressed buffer

                    base_name_orig, _ = os.path.splitext(final_filename_for_sets_and_saving)
                    final_filename_after_processing = base_name_orig + '.webp'
                    current_save_path_final = os.path.join(target_folder_path, final_filename_after_processing) # Update save path
                    self.logger(f"   Updated filename (compressed): {final_filename_after_processing}")
                else:
                    self.logger(f"   Compression skipped: WebP not significantly smaller."); bytes_to_write.seek(0) # Rewind original if not using compressed
            except Exception as comp_e:
                self.logger(f"❌ Compression failed for '{api_original_filename}': {comp_e}. Saving original."); bytes_to_write.seek(0) # Rewind original

        final_filename_saved_for_return = final_filename_after_processing # This is the name that will be saved

        # Final check if the (potentially new, e.g. .webp) filename already exists
        if final_filename_after_processing != final_filename_for_sets_and_saving and \
           os.path.exists(current_save_path_final) and os.path.getsize(current_save_path_final) > 0:
            self.logger(f"   -> Exists (Path - Post-Compress): '{final_filename_after_processing}' in '{target_folder_basename}'.")
            with self.downloaded_files_lock: self.downloaded_files.add(final_filename_after_processing)
            bytes_to_write.close()
            return 0, 1, final_filename_after_processing, was_original_name_kept_flag

        try:
            os.makedirs(os.path.dirname(current_save_path_final), exist_ok=True)
            with open(current_save_path_final, 'wb') as f_out:
                f_out.write(bytes_to_write.getvalue())

            with self.downloaded_file_hashes_lock: self.downloaded_file_hashes.add(calculated_file_hash)
            with self.downloaded_files_lock: self.downloaded_files.add(final_filename_after_processing) # Add final name

            self.logger(f"✅ Saved: '{final_filename_after_processing}' (from '{api_original_filename}', {downloaded_size_bytes / (1024*1024):.2f} MB) in '{target_folder_basename}'")
            time.sleep(0.05) # Small delay
            return 1, 0, final_filename_after_processing, was_original_name_kept_flag
        except Exception as save_err:
             self.logger(f"❌ Save Fail for '{final_filename_after_processing}': {save_err}")
             if os.path.exists(current_save_path_final): # Attempt to clean up partial file
                  try: os.remove(current_save_path_final);
                  except OSError: self.logger(f"  -> Failed to remove partially saved file: {current_save_path_final}")
             return 0, 1, final_filename_saved_for_return, was_original_name_kept_flag # Return the name it attempted to save as
        finally:
            if bytes_to_write: bytes_to_write.close()


    def process(self):
        """Main processing logic for a single post."""
        if self.check_cancel(): return 0, 0, [] 
        
        kept_original_filenames_for_log = [] 
        total_downloaded_this_post = 0
        total_skipped_this_post = 0
        
        parsed_api_url = urlparse(self.api_url_input)
        referer_url = f"https://{parsed_api_url.netloc}/"
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': referer_url, 'Accept': '*/*'}

        link_pattern = re.compile(r"""<a\s+.*?href=["'](https?://[^"']+)["'][^>]*>(.*?)</a>""",
                                  re.IGNORECASE | re.DOTALL)

        post_data = self.post
        post_title = post_data.get('title', '') or 'untitled_post'
        post_id = post_data.get('id', 'unknown_id')
        post_main_file_info = post_data.get('file') # This is a dict if present
        post_attachments = post_data.get('attachments', []) # This is a list of dicts
        post_content_html = post_data.get('content', '')

        self.logger(f"\n--- Processing Post {post_id} ('{post_title[:50]}...') (Thread: {threading.current_thread().name}) ---")

        num_potential_files_in_post = len(post_attachments or []) + (1 if post_main_file_info and post_main_file_info.get('path') else 0)

        # Apply skip_words_list based on skip_words_scope (for posts)
        if self.skip_words_list and (self.skip_words_scope == SKIP_SCOPE_POSTS or self.skip_words_scope == SKIP_SCOPE_BOTH):
            post_title_lower = post_title.lower()
            for skip_word in self.skip_words_list:
                if skip_word.lower() in post_title_lower:
                    self.logger(f"   -> Skip Post (Keyword in Title '{skip_word}'): '{post_title[:50]}...'. Scope: {self.skip_words_scope}")
                    return 0, num_potential_files_in_post, [] # Skip all files in this post

        # Character filter for Manga Mode (applies to post title)
        if not self.extract_links_only and self.manga_mode_active and self.filter_character_list:
            if not any(is_title_match_for_character(post_title, char_name) for char_name in self.filter_character_list):
                self.logger(f"   -> Skip Post (Manga Mode - Title No Char Match): Title '{post_title[:50]}' doesn't match active character filters.")
                return 0, num_potential_files_in_post, []

        if not isinstance(post_attachments, list): # Basic sanity check
            self.logger(f"⚠️ Corrupt attachment data for post {post_id} (expected list, got {type(post_attachments)}). Skipping attachments.")
            post_attachments = []

        potential_base_save_folders = []
        if not self.extract_links_only:
            if self.use_subfolders:
                # If character filters are active and it's manga mode, folder name comes from character filter matching post title
                if self.filter_character_list and self.manga_mode_active:
                    for char_filter_name in self.filter_character_list:
                        if is_title_match_for_character(post_title, char_filter_name):
                            cleaned_folder = clean_folder_name(char_filter_name)
                            if cleaned_folder: potential_base_save_folders.append(cleaned_folder)
                
                # If not manga mode with character filter, or if manga mode didn't find a match, try known names / title
                if not potential_base_save_folders:
                    derived_folders = match_folders_from_title(post_title, self.known_names, self.unwanted_keywords)
                    if derived_folders:
                        potential_base_save_folders.extend(derived_folders)
                        self.logger(f"   Folder Target(s) (Derived from Title & Known Names): {', '.join(derived_folders)}")
                    else: 
                        fallback_folder = extract_folder_name_from_title(post_title, self.unwanted_keywords)
                        potential_base_save_folders.append(fallback_folder)
                        self.logger(f"   Folder Target (Fallback from Title): {fallback_folder}")
                
                if not potential_base_save_folders: # Absolute fallback
                    potential_base_save_folders.append(clean_folder_name(post_title if post_title else "untitled_creator_content"))
                    self.logger(f"   Folder Target (Final Fallback): {potential_base_save_folders[0]}")
            else: # Not using subfolders, save to root
                potential_base_save_folders = [""] 

        # Skip post if folder name contains skip words (only if subfolders are used)
        if not self.extract_links_only and self.use_subfolders and self.skip_words_list:
            for folder_name_to_check in potential_base_save_folders:
                if not folder_name_to_check: continue # Skip if base folder is root
                if any(skip_word.lower() in folder_name_to_check.lower() for skip_word in self.skip_words_list):
                    matched_skip = next((sw for sw in self.skip_words_list if sw.lower() in folder_name_to_check.lower()), "unknown_skip_word")
                    self.logger(f"   -> Skip Post (Folder Keyword): Potential folder '{folder_name_to_check}' contains '{matched_skip}'.")
                    return 0, num_potential_files_in_post, []

        # External Link Extraction
        if (self.show_external_links or self.extract_links_only) and post_content_html:
            try:
                unique_links_data = {} 
                for match in link_pattern.finditer(post_content_html):
                    link_url = match.group(1).strip()
                    link_inner_text = match.group(2) 

                    if not any(ext in link_url.lower() for ext in ['.css', '.js', '.ico', '.xml', '.svg']) \
                       and not link_url.startswith('javascript:') \
                       and link_url not in unique_links_data: 

                        clean_link_text = re.sub(r'<.*?>', '', link_inner_text) 
                        clean_link_text = html.unescape(clean_link_text).strip() 

                        display_text = clean_link_text if clean_link_text else "[Link]" 
                        unique_links_data[link_url] = display_text
                
                links_emitted_count = 0
                scraped_platforms = {'kemono', 'coomer', 'patreon'} 

                for link_url, link_text in unique_links_data.items():
                     platform = get_link_platform(link_url)
                     if platform not in scraped_platforms: 
                         if self.signals and hasattr(self.signals, 'external_link_signal'):
                             self.signals.external_link_signal.emit(post_title, link_text, link_url, platform)
                             links_emitted_count +=1
                
                if links_emitted_count > 0: self.logger(f"   🔗 Found {links_emitted_count} potential external link(s) in post content.")
            except Exception as e: self.logger(f"⚠️ Error parsing post content for links: {e}\n{traceback.format_exc(limit=2)}")

        if self.extract_links_only: 
            self.logger(f"   Extract Links Only mode: Finished processing post {post_id} for links.")
            return 0, 0, [] # No files downloaded or skipped in this mode for this counter

        # --- Prepare list of files to download from this post ---
        all_files_from_post_api = []
        api_file_domain = urlparse(self.api_url_input).netloc # Use domain from input URL
        if not api_file_domain or not any(d in api_file_domain.lower() for d in ['kemono.su', 'kemono.party', 'coomer.su', 'coomer.party']):
            # Fallback if input URL isn't a direct site URL (e.g. API URL was passed, though less common for user input)
            api_file_domain = "kemono.su" if "kemono" in self.service.lower() else "coomer.party"


        if post_main_file_info and isinstance(post_main_file_info, dict) and post_main_file_info.get('path'):
            file_path = post_main_file_info['path'].lstrip('/')
            original_api_name = post_main_file_info.get('name') or os.path.basename(file_path)
            if original_api_name:
                all_files_from_post_api.append({
                    'url': f"https://{api_file_domain}{file_path}" if file_path.startswith('/') else f"https://{api_file_domain}/data/{file_path}",
                    'name': original_api_name, # This 'name' might be used for initial filtering if _original_name_for_log isn't set
                    '_original_name_for_log': original_api_name, # Store the true original for logging/type checks
                    '_is_thumbnail': self.download_thumbnails and is_image(original_api_name)
                })
            else: self.logger(f"   ⚠️ Skipping main file for post {post_id}: Missing name (Path: {file_path})")

        for idx, att_info in enumerate(post_attachments):
            if isinstance(att_info, dict) and att_info.get('path'):
                att_path = att_info['path'].lstrip('/')
                original_api_att_name = att_info.get('name') or os.path.basename(att_path)
                if original_api_att_name:
                    all_files_from_post_api.append({
                        'url': f"https://{api_file_domain}{att_path}" if att_path.startswith('/') else f"https://{api_file_domain}/data/{att_path}",
                        'name': original_api_att_name,
                        '_original_name_for_log': original_api_att_name,
                        '_is_thumbnail': self.download_thumbnails and is_image(original_api_att_name)
                    })
                else: self.logger(f"   ⚠️ Skipping attachment {idx+1} for post {post_id}: Missing name (Path: {att_path})")
            else: self.logger(f"   ⚠️ Skipping invalid attachment {idx+1} for post {post_id}: {str(att_info)[:100]}")

        if self.download_thumbnails: # Filter non-images if in thumbnail mode
            all_files_from_post_api = [finfo for finfo in all_files_from_post_api if finfo['_is_thumbnail']]
            if not all_files_from_post_api:
                 self.logger(f"   -> No image thumbnails found for post {post_id} in thumbnail-only mode.")
                 return 0, 0, []


        if not all_files_from_post_api:
            self.logger(f"   No files found to download for post {post_id}.")
            return 0, 0, []

        # --- Filter out duplicates based on original API filename WITHIN THIS POST ---
        files_to_download_info_list = []
        processed_original_filenames_in_this_post = set()
        for file_info in all_files_from_post_api:
            current_api_original_filename = file_info.get('_original_name_for_log')
            if current_api_original_filename in processed_original_filenames_in_this_post:
                self.logger(f"   -> Skip Duplicate Original Name (within post {post_id}): '{current_api_original_filename}' already processed/listed for this post.")
                total_skipped_this_post += 1
            else:
                files_to_download_info_list.append(file_info)
                if current_api_original_filename: 
                    processed_original_filenames_in_this_post.add(current_api_original_filename)
        
        if not files_to_download_info_list:
            self.logger(f"   All files for post {post_id} were duplicate original names or skipped earlier.")
            return 0, total_skipped_this_post, []


        num_files_in_this_post_for_naming = len(files_to_download_info_list)
        self.logger(f"   Identified {num_files_in_this_post_for_naming} unique original file(s) for potential download from post {post_id}.")


        with ThreadPoolExecutor(max_workers=self.num_file_threads, thread_name_prefix=f'P{post_id}File_') as file_pool:
            futures_list = []
            for file_idx, file_info_to_dl in enumerate(files_to_download_info_list):
                if self.check_cancel(): break

                actual_target_full_paths_for_this_file = []

                if self.use_subfolders:
                    # If character filters are active and NOT manga mode, folder name comes from char filter matching filename
                    if self.filter_character_list and not self.manga_mode_active:
                        for char_name_from_filter_list in self.filter_character_list:
                            if is_filename_match_for_character(file_info_to_dl.get('_original_name_for_log'), char_name_from_filter_list):
                                base_char_folder_path = os.path.join(self.download_root, clean_folder_name(char_name_from_filter_list))
                                if self.use_post_subfolders:
                                    cleaned_title_for_subfolder = clean_folder_name(post_title)
                                    post_specific_subfolder_name = f"{post_id}_{cleaned_title_for_subfolder}" if cleaned_title_for_subfolder else f"{post_id}_untitled"
                                    actual_target_full_paths_for_this_file.append(os.path.join(base_char_folder_path, post_specific_subfolder_name))
                                else:
                                    actual_target_full_paths_for_this_file.append(base_char_folder_path)
                    else: # Manga mode with char filter (already handled for potential_base_save_folders) OR no char filter OR char filter didn't match filename in normal mode
                        for base_folder_name in potential_base_save_folders: # These were determined earlier
                            base_folder_path = os.path.join(self.download_root, base_folder_name)
                            if self.use_post_subfolders:
                                cleaned_title_for_subfolder = clean_folder_name(post_title)
                                post_specific_subfolder_name = f"{post_id}_{cleaned_title_for_subfolder}" if cleaned_title_for_subfolder else f"{post_id}_untitled"
                                actual_target_full_paths_for_this_file.append(os.path.join(base_folder_path, post_specific_subfolder_name))
                            else:
                                actual_target_full_paths_for_this_file.append(base_folder_path)
                else: # Not using subfolders at all
                    actual_target_full_paths_for_this_file = [self.download_root]
                
                # Override with custom folder name if it's a single post download and custom name is provided
                if self.target_post_id_from_initial_url and self.custom_folder_name: # custom_folder_name is already cleaned
                    custom_full_path = os.path.join(self.download_root, self.custom_folder_name)
                    actual_target_full_paths_for_this_file = [custom_full_path]

                # Fallback if no specific target paths were determined (e.g. char filter normal mode no match)
                if not actual_target_full_paths_for_this_file:
                    default_target_for_non_match = self.download_root
                    if self.use_subfolders: # Should use one of the potential_base_save_folders if subfolders enabled
                        gen_folder_name = potential_base_save_folders[0] if potential_base_save_folders and potential_base_save_folders[0] else clean_folder_name(post_title)
                        default_target_for_non_match = os.path.join(self.download_root, gen_folder_name)
                        if self.use_post_subfolders:
                             cleaned_title_for_subfolder = clean_folder_name(post_title)
                             post_specific_subfolder_name = f"{post_id}_{cleaned_title_for_subfolder}" if cleaned_title_for_subfolder else f"{post_id}_untitled"
                             default_target_for_non_match = os.path.join(default_target_for_non_match, post_specific_subfolder_name)
                    actual_target_full_paths_for_this_file = [default_target_for_non_match]

                for target_path in set(actual_target_full_paths_for_this_file): # Use set to avoid duplicate downloads to same path
                    if self.check_cancel(): break
                    futures_list.append(file_pool.submit(
                        self._download_single_file,
                        file_info_to_dl,
                        target_path,
                        headers,
                        post_id,
                        self.skip_current_file_flag,
                        post_title, # Pass post_title for manga naming
                        file_idx, 
                        num_files_in_this_post_for_naming 
                    ))
                if self.check_cancel(): break

            for future in as_completed(futures_list):
                if self.check_cancel():
                    for f_to_cancel in futures_list: # Attempt to cancel pending futures
                        if not f_to_cancel.done():
                            f_to_cancel.cancel()
                    break
                try:
                    dl_count, skip_count, actual_filename_saved, original_kept_flag = future.result()
                    total_downloaded_this_post += dl_count
                    total_skipped_this_post += skip_count
                    if original_kept_flag and dl_count > 0 and actual_filename_saved: # Ensure filename is not empty
                        kept_original_filenames_for_log.append(actual_filename_saved)
                except CancelledError:
                    self.logger(f"   File download task for post {post_id} was cancelled.")
                    total_skipped_this_post += 1 # Assume one file per cancelled future
                except Exception as exc_f:
                    self.logger(f"❌ File download task for post {post_id} resulted in error: {exc_f}")
                    total_skipped_this_post += 1 # Assume one file failed
        
        # Clear file progress after all files for this post are done or cancelled
        if self.signals and hasattr(self.signals, 'file_progress_signal'):
            self.signals.file_progress_signal.emit("", 0, 0)

        if self.check_cancel(): self.logger(f"   Post {post_id} processing interrupted/cancelled.");
        else: self.logger(f"   Post {post_id} Summary: Downloaded={total_downloaded_this_post}, Skipped Files={total_skipped_this_post}")

        return total_downloaded_this_post, total_skipped_this_post, kept_original_filenames_for_log


class DownloadThread(QThread):
    """
    Manages the overall download process.
    Fetches posts using download_from_api and then processes each post using PostProcessorWorker.
    """
    progress_signal = pyqtSignal(str)
    add_character_prompt_signal = pyqtSignal(str) # For main app to show prompt
    file_download_status_signal = pyqtSignal(bool) # True when a file dl starts, False when ends/fails
    finished_signal = pyqtSignal(int, int, bool, list) # dl_count, skip_count, was_cancelled, kept_original_names
    external_link_signal = pyqtSignal(str, str, str, str) # post_title, link_text, link_url, platform
    file_progress_signal = pyqtSignal(str, int, int) # filename, downloaded_bytes, total_bytes


    def __init__(self, api_url_input, output_dir, known_names_copy,
                 cancellation_event, # This is a threading.Event from the main app
                 filter_character_list=None,
                 filter_mode='all', skip_zip=True, skip_rar=True,
                 use_subfolders=True, use_post_subfolders=False, custom_folder_name=None, compress_images=False,
                 download_thumbnails=False, service=None, user_id=None,
                 downloaded_files=None, downloaded_file_hashes=None, downloaded_files_lock=None, downloaded_file_hashes_lock=None,
                 skip_words_list=None,
                 skip_words_scope=SKIP_SCOPE_FILES, 
                 show_external_links=False,
                 extract_links_only=False,
                 num_file_threads_for_worker=1, # For PostProcessorWorker's internal pool
                 skip_current_file_flag=None, # This is a threading.Event
                 start_page=None, end_page=None,
                 target_post_id_from_initial_url=None, # The specific post ID if single post URL
                 manga_mode_active=False,
                 unwanted_keywords=None,
                 manga_filename_style=STYLE_POST_TITLE
                 ):
        super().__init__()
        self.api_url_input = api_url_input
        self.output_dir = output_dir
        self.known_names = list(known_names_copy) # Make a copy
        self.cancellation_event = cancellation_event # Use the shared event
        self.skip_current_file_flag = skip_current_file_flag # Use the shared event
        self.initial_target_post_id = target_post_id_from_initial_url # Store the original target
        self.filter_character_list = filter_character_list if filter_character_list else []
        self.filter_mode = filter_mode
        self.skip_zip = skip_zip
        self.skip_rar = skip_rar
        self.use_subfolders = use_subfolders
        self.use_post_subfolders = use_post_subfolders
        self.custom_folder_name = custom_folder_name
        self.compress_images = compress_images
        self.download_thumbnails = download_thumbnails
        self.service = service
        self.user_id = user_id
        self.skip_words_list = skip_words_list if skip_words_list is not None else []
        self.skip_words_scope = skip_words_scope
        self.downloaded_files = downloaded_files # Should be the shared set from main app
        self.downloaded_files_lock = downloaded_files_lock # Shared lock
        self.downloaded_file_hashes = downloaded_file_hashes # Shared set
        self.downloaded_file_hashes_lock = downloaded_file_hashes_lock # Shared lock
        
        self._add_character_response = None # For sync prompt result
        self.prompt_mutex = QMutex() # For sync prompt result
        
        self.show_external_links = show_external_links
        self.extract_links_only = extract_links_only
        self.num_file_threads_for_worker = num_file_threads_for_worker
        self.start_page = start_page
        self.end_page = end_page
        self.manga_mode_active = manga_mode_active
        self.unwanted_keywords = unwanted_keywords if unwanted_keywords is not None else \
                                 {'spicy', 'hd', 'nsfw', '4k', 'preview', 'teaser', 'clip'}
        self.manga_filename_style = manga_filename_style

        if self.compress_images and Image is None: # Check Pillow again
            self.logger("⚠️ Image compression disabled: Pillow library not found (DownloadThread).")
            self.compress_images = False

    def logger(self, message):
        """Emits a log message via the progress_signal."""
        self.progress_signal.emit(str(message))

    def isInterruptionRequested(self):
        """Checks if Qt interruption or manual cancellation event is set."""
        # QThread's interruption is different from threading.Event
        # We primarily use the threading.Event (self.cancellation_event)
        return self.cancellation_event.is_set() or super().isInterruptionRequested()


    def skip_file(self):
        """Sets the flag to skip the currently processing file (if any)."""
        # This method is called from the main thread via the GUI button.
        # It needs to signal the PostProcessorWorker's skip_event if one is active.
        # However, the DownloadThread itself doesn't directly manage the skip_event for individual files.
        # The skip_current_file_flag is passed to PostProcessorWorker.
        if self.isRunning() and self.skip_current_file_flag:
             self.logger("⏭️ Skip requested for current file (single-thread mode).")
             self.skip_current_file_flag.set() # Signal the event
        else: self.logger("ℹ️ Skip file: No download active or skip flag not available for current context.")


    def run(self):
        """Main execution logic for the download thread."""
        grand_total_downloaded_files = 0
        grand_total_skipped_files = 0
        grand_list_of_kept_original_filenames = [] 
        was_process_cancelled = False

        # Create a PostProcessorSignals instance for this thread's workers
        worker_signals_obj = PostProcessorSignals()
        try:
            # Connect signals from this worker_signals_obj to the DownloadThread's own signals
            worker_signals_obj.progress_signal.connect(self.progress_signal)
            worker_signals_obj.file_download_status_signal.connect(self.file_download_status_signal)
            worker_signals_obj.file_progress_signal.connect(self.file_progress_signal)
            worker_signals_obj.external_link_signal.connect(self.external_link_signal)

            self.logger("   Starting post fetch (single-threaded download process)...")
            post_generator = download_from_api(
                self.api_url_input,
                logger=self.logger,
                start_page=self.start_page,
                end_page=self.end_page,
                manga_mode=self.manga_mode_active,
                cancellation_event=self.cancellation_event # Pass the shared event
            )

            for posts_batch_data in post_generator: # download_from_api yields batches
                if self.isInterruptionRequested(): was_process_cancelled = True; break
                for individual_post_data in posts_batch_data: # Iterate through posts in the batch
                    if self.isInterruptionRequested(): was_process_cancelled = True; break

                    # Create and run PostProcessorWorker for each post
                    # The PostProcessorWorker will use its own ThreadPoolExecutor for files if num_file_threads_for_worker > 1
                    post_processing_worker = PostProcessorWorker(
                         post_data=individual_post_data,
                         download_root=self.output_dir,
                         known_names=self.known_names, # Pass the copy
                         filter_character_list=self.filter_character_list,
                         unwanted_keywords=self.unwanted_keywords,
                         filter_mode=self.filter_mode,
                         skip_zip=self.skip_zip, skip_rar=self.skip_rar,
                         use_subfolders=self.use_subfolders, use_post_subfolders=self.use_post_subfolders,
                         target_post_id_from_initial_url=self.initial_target_post_id, # Pass the original target
                         custom_folder_name=self.custom_folder_name,
                         compress_images=self.compress_images, download_thumbnails=self.download_thumbnails,
                         service=self.service, user_id=self.user_id,
                         api_url_input=self.api_url_input, # Pass the original input URL
                         cancellation_event=self.cancellation_event, # Pass the shared event
                         signals=worker_signals_obj, # Pass the signals object for this thread
                         downloaded_files=self.downloaded_files, # Pass shared set
                         downloaded_file_hashes=self.downloaded_file_hashes, # Pass shared set
                         downloaded_files_lock=self.downloaded_files_lock, # Pass shared lock
                         downloaded_file_hashes_lock=self.downloaded_file_hashes_lock, # Pass shared lock
                         skip_words_list=self.skip_words_list,
                         skip_words_scope=self.skip_words_scope,
                         show_external_links=self.show_external_links,
                         extract_links_only=self.extract_links_only,
                         num_file_threads=self.num_file_threads_for_worker, # Threads for files within this post
                         skip_current_file_flag=self.skip_current_file_flag, # Pass the shared event
                         manga_mode_active=self.manga_mode_active,
                         manga_filename_style=self.manga_filename_style
                    )
                    try:
                        # The process method of PostProcessorWorker handles its internal file downloads
                        dl_count, skip_count, kept_originals_this_post = post_processing_worker.process()
                        grand_total_downloaded_files += dl_count
                        grand_total_skipped_files += skip_count
                        if kept_originals_this_post: # This is a list
                            grand_list_of_kept_original_filenames.extend(kept_originals_this_post)
                    except Exception as proc_err:
                         post_id_for_err = individual_post_data.get('id', 'N/A')
                         self.logger(f"❌ Error processing post {post_id_for_err} in DownloadThread: {proc_err}")
                         traceback.print_exc()
                         # Estimate skipped files for this post if worker crashes
                         num_potential_files_est = len(individual_post_data.get('attachments', [])) + \
                                                   (1 if individual_post_data.get('file') else 0)
                         grand_total_skipped_files += num_potential_files_est

                    if self.skip_current_file_flag and self.skip_current_file_flag.is_set():
                        self.skip_current_file_flag.clear() # Reset for the next file/post
                        self.logger("   Skip current file flag was processed and cleared by DownloadThread.")
                    
                    self.msleep(10) # Small delay between processing posts in single-thread mode
                if was_process_cancelled: break # Break from outer loop (batches)

            if not was_process_cancelled and not self.isInterruptionRequested(): # Check again after loops
                 self.logger("✅ All posts processed or end of content reached by DownloadThread.")

        except Exception as main_thread_err:
            self.logger(f"\n❌ Critical error within DownloadThread run loop: {main_thread_err}")
            traceback.print_exc()
            # Don't assume cancelled if an unexpected error occurs, let was_process_cancelled reflect actual interruption
            if not self.isInterruptionRequested(): was_process_cancelled = False 
        finally:
            # Disconnect signals
            try:
                if worker_signals_obj: # Check if it was initialized
                    worker_signals_obj.progress_signal.disconnect(self.progress_signal)
                    worker_signals_obj.file_download_status_signal.disconnect(self.file_download_status_signal)
                    worker_signals_obj.external_link_signal.disconnect(self.external_link_signal)
                    worker_signals_obj.file_progress_signal.disconnect(self.file_progress_signal)
            except (TypeError, RuntimeError) as e: #TypeError if not connected, RuntimeError if object deleted
                self.logger(f"ℹ️ Note during DownloadThread signal disconnection: {e}")
            
            # Emit finished signal with final counts and status
            self.finished_signal.emit(grand_total_downloaded_files, grand_total_skipped_files, self.isInterruptionRequested(), grand_list_of_kept_original_filenames)

    def receive_add_character_result(self, result):
        """Slot to receive the result from a character add prompt shown in the main thread."""
        # This is called by a signal from the main thread
        with QMutexLocker(self.prompt_mutex):
             self._add_character_response = result
        self.logger(f"   (DownloadThread) Received character prompt response: {'Yes (added/confirmed)' if result else 'No (declined/failed)'}")