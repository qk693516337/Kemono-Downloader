import os
import time
import requests
import re
import threading
import queue
import hashlib
import http.client
import traceback
from concurrent.futures import ThreadPoolExecutor, Future, CancelledError, as_completed
import html # Import the html module for unescaping

from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMutex, QMutexLocker
from urllib.parse import urlparse
try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow library not found. Please install it: pip install Pillow")
    Image = None


from io import BytesIO


fastapi_app = None # Placeholder, not used in this script
KNOWN_NAMES = [] # Global list, populated by main.py

IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp',
    '.heic', '.heif', '.svg', '.ico', '.jfif', '.pjpeg', '.pjp', '.avif'
}
VIDEO_EXTENSIONS = {
    '.mp4', '.mov', '.mkv', '.webm', '.avi', '.wmv', '.flv', '.mpeg',
    '.mpg', '.m4v', '.3gp', '.ogv', '.ts', '.vob'
}

def is_title_match_for_character(post_title, character_name_filter):
    """Checks if a post title contains a specific character name (case-insensitive, whole word)."""
    if not post_title or not character_name_filter:
        return False
    # Ensure character_name_filter is treated as a whole word, avoid partial matches within larger words.
    # Regex: \b matches word boundary. re.escape handles special characters in filter.
    pattern = r"(?i)\b" + re.escape(character_name_filter) + r"\b"
    return bool(re.search(pattern, post_title))

def is_filename_match_for_character(filename, character_name_filter):
    """Checks if a filename contains a specific character name (case-insensitive, substring)."""
    if not filename or not character_name_filter:
        return False
    # For filenames, substring matching is often more practical.
    return character_name_filter.lower() in filename.lower()


def clean_folder_name(name):
    """Cleans a string to be suitable for a folder name."""
    if not isinstance(name, str): name = str(name)
    # Remove characters that are generally problematic in folder names across OS
    cleaned = re.sub(r'[^\w\s\-\_\.\(\)]', '', name) # Allow letters, numbers, whitespace, hyphens, underscores, periods, parentheses
    cleaned = cleaned.strip() # Remove leading/trailing whitespace
    # Replace sequences of whitespace with a single underscore
    cleaned = re.sub(r'\s+', '_', cleaned)
    return cleaned if cleaned else "untitled_folder"


def clean_filename(name):
    """Cleans a string to be suitable for a file name."""
    if not isinstance(name, str): name = str(name)
    # Remove characters that are generally problematic in file names across OS
    cleaned = re.sub(r'[^\w\s\-\_\.\(\)]', '', name) # Allow letters, numbers, whitespace, hyphens, underscores, periods, parentheses
    cleaned = cleaned.strip() # Remove leading/trailing whitespace
    # Replace sequences of whitespace with a single underscore
    cleaned = re.sub(r'\s+', '_', cleaned)
    return cleaned if cleaned else "untitled_file"


def extract_folder_name_from_title(title, unwanted_keywords):
    """Extracts a potential folder name from a title, avoiding unwanted keywords."""
    if not title: return 'Uncategorized'
    title_lower = title.lower()
    # Try to find a meaningful token not in unwanted_keywords
    tokens = re.findall(r'\b[\w\-]+\b', title_lower) # Find words
    for token in tokens:
        clean_token = clean_folder_name(token) # Clean the token itself
        if clean_token and clean_token.lower() not in unwanted_keywords: # Check against lowercased unwanted keywords
            return clean_token
    # Fallback to cleaned full title if no suitable token found
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
    # Sort names by length (descending) to match longer names first (e.g., "Spider-Man" before "Spider")
    sorted_names_to_match = sorted(names_to_match, key=len, reverse=True)

    for name in sorted_names_to_match:
        name_lower = name.lower()
        if not name_lower: continue # Skip empty names

        # Use word boundary regex to ensure whole word matching
        pattern = r'\b' + re.escape(name_lower) + r'\b'
        if re.search(pattern, title_lower):
             # Clean the original casing 'name' for folder creation, then lowercase for unwanted keyword check
             cleaned_name_for_folder = clean_folder_name(name)
             if cleaned_name_for_folder.lower() not in unwanted_keywords: # Check against lowercased unwanted keywords
                 matched_cleaned_names.add(cleaned_name_for_folder) # Add the cleaned name with original casing preserved as much as possible
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
        # Check if the domain is one of the known Kemono or Coomer domains
        is_kemono = any(d in domain for d in ['kemono.su', 'kemono.party'])
        is_coomer = any(d in domain for d in ['coomer.su', 'coomer.party'])

        if not (is_kemono or is_coomer): return None, None, None # Not a recognized service

        path_parts = [part for part in parsed_url.path.strip('/').split('/') if part]

        # Standard URL structure: /{service}/user/{user_id}/post/{post_id}
        # Or creator page: /{service}/user/{user_id}
        if len(path_parts) >= 3 and path_parts[1].lower() == 'user':
            service = path_parts[0]
            user_id = path_parts[2]
            if len(path_parts) >= 5 and path_parts[3].lower() == 'post':
                post_id = path_parts[4]
            return service, user_id, post_id

        # API URL structure: /api/v1/{service}/user/{user_id}/post/{post_id}
        # Or API creator page: /api/v1/{service}/user/{user_id}
        if len(path_parts) >= 5 and path_parts[0].lower() == 'api' and \
           path_parts[1].lower() == 'v1' and path_parts[3].lower() == 'user':
            service = path_parts[2]
            user_id = path_parts[4]
            if len(path_parts) >= 7 and path_parts[5].lower() == 'post':
                post_id = path_parts[6]
            return service, user_id, post_id

    except Exception as e:
        # Log or handle unexpected errors during URL parsing if necessary
        print(f"Debug: Exception during extract_post_info for URL '{url_string}': {e}")
    return None, None, None # Return None for all if parsing fails or structure is not matched


def fetch_posts_paginated(api_url_base, headers, offset, logger, cancellation_event=None):
    """Fetches a single page of posts from the API."""
    if cancellation_event and cancellation_event.is_set():
        logger("   Fetch cancelled before request.")
        raise RuntimeError("Fetch operation cancelled by user.") # Raise error to stop pagination

    paginated_url = f'{api_url_base}?o={offset}'
    logger(f"   Fetching: {paginated_url}")
    try:
        response = requests.get(paginated_url, headers=headers, timeout=(10, 60)) # connect_timeout, read_timeout
        response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)
        # It's good practice to check content type before parsing JSON
        if 'application/json' not in response.headers.get('Content-Type', '').lower():
            logger(f"⚠️ Unexpected content type from API: {response.headers.get('Content-Type')}. Body: {response.text[:200]}")
            return [] # Return empty list or raise error if JSON is strictly expected
        return response.json()
    except requests.exceptions.Timeout:
        # Log specific timeout and re-raise or handle as a specific error
        raise RuntimeError(f"Timeout fetching offset {offset} from {paginated_url}")
    except requests.exceptions.RequestException as e:
        # General request exception (includes HTTPError, ConnectionError, etc.)
        err_msg = f"Error fetching offset {offset} from {paginated_url}: {e}"
        if e.response is not None:
            err_msg += f" (Status: {e.response.status_code}, Body: {e.response.text[:200]})"
        raise RuntimeError(err_msg)
    except ValueError as e: # JSONDecodeError inherits from ValueError
        # Handle cases where response is not valid JSON
        raise RuntimeError(f"Error decoding JSON from offset {offset} ({paginated_url}): {e}. Response text: {response.text[:200]}")
    except Exception as e:
        # Catch any other unexpected errors
        raise RuntimeError(f"Unexpected error fetching offset {offset} ({paginated_url}): {e}")


def download_from_api(api_url_input, logger=print, start_page=None, end_page=None, manga_mode=False, cancellation_event=None):
    """
    Generator function to fetch post data from Kemono/Coomer API.
    Handles pagination and yields batches of posts.
    In Manga Mode, fetches all posts first, then yields them in reverse order (oldest first).
    """
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'} # Standard headers
    service, user_id, target_post_id = extract_post_info(api_url_input)

    if cancellation_event and cancellation_event.is_set():
        logger("   Download_from_api cancelled at start.")
        return

    if not service or not user_id:
        logger(f"❌ Invalid URL or could not extract service/user: {api_url_input}")
        return

    # Page range is ignored for single post URLs
    if target_post_id and (start_page or end_page):
        logger("⚠️ Page range (start/end page) is ignored when a specific post URL is provided.")
        start_page = end_page = None

    # Manga mode is only applicable for creator feeds (not single posts)
    is_creator_feed_for_manga = manga_mode and not target_post_id

    parsed_input = urlparse(api_url_input)
    api_domain = parsed_input.netloc
    # Ensure we use a valid API domain, default to kemono.su if unrecognized
    if not any(d in api_domain.lower() for d in ['kemono.su', 'kemono.party', 'coomer.su', 'coomer.party']):
        logger(f"⚠️ Unrecognized domain '{api_domain}'. Defaulting to kemono.su for API calls.")
        api_domain = "kemono.su" # Or "coomer.party" if that's preferred default

    api_base_url = f"https://{api_domain}/api/v1/{service}/user/{user_id}"
    page_size = 50 # Kemono API typically returns 50 posts per page

    # --- Manga Mode: Fetch all posts first, then reverse ---
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
                if not isinstance(posts_batch_manga, list): # API should always return a list
                    logger(f"❌ API Error (Manga Mode): Expected list of posts, got {type(posts_batch_manga)}.")
                    break
                if not posts_batch_manga: # Empty list means no more posts
                    logger("✅ Reached end of posts (Manga Mode fetch all).")
                    break
                all_posts_for_manga_mode.extend(posts_batch_manga)
                current_offset_manga += len(posts_batch_manga) # API doesn't use page_size in offset, but number of posts
                time.sleep(0.6) # Be respectful to the API
            except RuntimeError as e: # Catch errors from fetch_posts_paginated
                if "cancelled by user" in str(e).lower():
                    logger(f"ℹ️ Manga mode pagination stopped due to cancellation: {e}")
                else:
                    logger(f"❌ {e}\n   Aborting manga mode pagination.")
                break # Stop fetching on error
            except Exception as e: # Catch any other unexpected errors
                logger(f"❌ Unexpected error during manga mode fetch: {e}")
                traceback.print_exc()
                break
        
        if cancellation_event and cancellation_event.is_set(): return # Early exit if cancelled

        if all_posts_for_manga_mode:
            logger(f"   Manga Mode: Fetched {len(all_posts_for_manga_mode)} total posts. Reversing order...")
            all_posts_for_manga_mode.reverse() # Oldest posts first

            # Yield in batches of page_size
            for i in range(0, len(all_posts_for_manga_mode), page_size):
                if cancellation_event and cancellation_event.is_set():
                    logger("   Manga mode post yielding cancelled.")
                    break
                yield all_posts_for_manga_mode[i:i + page_size]
        else:
            logger("   Manga Mode: No posts found to process.")
        return # End of Manga Mode logic

    # --- Normal Mode or Single Post Mode ---
    current_page_num = 1
    current_offset = 0
    processed_target_post_flag = False # For single post URLs

    if start_page and start_page > 1:
        current_offset = (start_page - 1) * page_size # Calculate offset for starting page
        current_page_num = start_page
        logger(f"   Starting from page {current_page_num} (calculated offset {current_offset}).")

    while True: # Pagination loop
        if cancellation_event and cancellation_event.is_set():
            logger("   Post fetching loop cancelled.")
            break
        if end_page and current_page_num > end_page:
            logger(f"✅ Reached specified end page ({end_page}). Stopping.")
            break
        if target_post_id and processed_target_post_flag: # If single post was found and processed
            logger(f"✅ Target post {target_post_id} has been processed.")
            break

        try:
            posts_batch = fetch_posts_paginated(api_base_url, headers, current_offset, logger, cancellation_event)
            if not isinstance(posts_batch, list):
                logger(f"❌ API Error: Expected list of posts, got {type(posts_batch)} at page {current_page_num}.")
                break
        except RuntimeError as e: # Catch errors from fetch_posts_paginated
            if "cancelled by user" in str(e).lower():
                 logger(f"ℹ️ Pagination stopped due to cancellation: {e}")
            else:
                logger(f"❌ {e}\n   Aborting pagination at page {current_page_num}.")
            break
        except Exception as e: # Catch any other unexpected errors
            logger(f"❌ Unexpected error fetching page {current_page_num}: {e}")
            traceback.print_exc()
            break

        if not posts_batch: # No more posts
            if current_page_num == (start_page or 1) and not target_post_id : # No posts on first page of a creator feed
                logger("😕 No posts found on the first page checked.")
            elif not target_post_id: # End of creator feed
                logger("✅ Reached end of posts (no more content).")
            break # Exit pagination loop

        if target_post_id: # Processing a single post URL
            matching_post = next((p for p in posts_batch if str(p.get('id')) == str(target_post_id)), None)
            if matching_post:
                logger(f"🎯 Found target post {target_post_id}.")
                yield [matching_post] # Yield as a list containing one item
                processed_target_post_flag = True # Mark as processed
            else:
                # This case should ideally not happen if the post ID is valid and API is consistent.
                # If the API returns posts in pages, a specific post ID might not be on the first page if offset isn't 0.
                # However, for a direct post URL, we expect it or an error.
                logger(f"❌ Target post {target_post_id} not found in the batch from offset {current_offset}. This may indicate the post URL is incorrect or the API behavior is unexpected.")
                break # Stop if target post not found where expected
        else: # Processing a creator feed (not a single post)
            yield posts_batch # Yield the batch of posts

        if not (target_post_id and processed_target_post_flag): # If not a single post that was just processed
            if not posts_batch : break # Should be redundant due to check above, but safe
            current_offset += len(posts_batch) # Kemono API uses item offset, not page offset
            current_page_num += 1
            time.sleep(0.6) # Be respectful to the API
        else: # Single post was processed, exit loop
            break
            
    # Final check if a specific target post was requested but not found
    if target_post_id and not processed_target_post_flag and not (cancellation_event and cancellation_event.is_set()):
        logger(f"❌ Target post {target_post_id} could not be found after checking relevant pages.")


def get_link_platform(url):
    """Attempts to identify the platform of an external link from its domain."""
    try:
        domain = urlparse(url).netloc.lower()
        # Specific known platforms (add more as needed)
        if 'drive.google.com' in domain: return 'google drive'
        if 'mega.nz' in domain or 'mega.io' in domain: return 'mega'
        if 'dropbox.com' in domain: return 'dropbox'
        if 'patreon.com' in domain: return 'patreon'
        if 'instagram.com' in domain: return 'instagram'
        if 'twitter.com' in domain or 'x.com' in domain: return 'twitter/x'
        if 'discord.gg' in domain or 'discord.com/invite' in domain: return 'discord invite'
        if 'pixiv.net' in domain: return 'pixiv'
        if 'kemono.su' in domain or 'kemono.party' in domain: return 'kemono' # Explicitly identify kemono
        if 'coomer.su' in domain or 'coomer.party' in domain: return 'coomer' # Explicitly identify coomer

        # Generic extraction for other domains (e.g., 'example' from 'www.example.com')
        parts = domain.split('.')
        if len(parts) >= 2:
            # Return the second-to-last part for common structures (e.g., 'google' from google.com)
            # Avoid returning generic TLDs like 'com', 'org', 'net' as the platform
            # Handle cases like 'google.co.uk' -> 'google'
            if parts[-2] not in ['com', 'org', 'net', 'gov', 'edu', 'co'] or len(parts) == 2:
                 return parts[-2]
            elif len(parts) >= 3 and parts[-3] not in ['com', 'org', 'net', 'gov', 'edu', 'co']:
                 return parts[-3]
            else: # Fallback to full domain if unsure or very short domain
                 return domain
        return 'external' # Default if domain parsing fails or is too simple (e.g., 'localhost')
    except Exception: return 'unknown' # Error case


class PostProcessorSignals(QObject):
    """Defines signals used by PostProcessorWorker to communicate with the GUI thread."""
    progress_signal = pyqtSignal(str) # Generic log messages
    file_download_status_signal = pyqtSignal(bool) # True if a file download starts, False if ends/fails
    # Signal carries post_title, link_text, link_url, platform
    external_link_signal = pyqtSignal(str, str, str, str) 
    # Signal carries filename, downloaded_bytes, total_bytes for progress bar
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
                 skip_words_list=None, show_external_links=False,
                 extract_links_only=False,
                 num_file_threads=4, skip_current_file_flag=None,
                 manga_mode_active=False
                 ):
        self.post = post_data
        self.download_root = download_root
        self.known_names = known_names
        self.filter_character_list = filter_character_list if filter_character_list else []
        self.unwanted_keywords = unwanted_keywords if unwanted_keywords is not None else set()
        self.filter_mode = filter_mode # 'image', 'video', or 'all'
        self.skip_zip = skip_zip
        self.skip_rar = skip_rar
        self.use_subfolders = use_subfolders
        self.use_post_subfolders = use_post_subfolders
        self.target_post_id_from_initial_url = target_post_id_from_initial_url # ID from initial URL if it was a post URL
        self.custom_folder_name = custom_folder_name # For single post downloads
        self.compress_images = compress_images
        self.download_thumbnails = download_thumbnails
        self.service = service
        self.user_id = user_id
        self.api_url_input = api_url_input # The original URL input by the user
        self.cancellation_event = cancellation_event
        self.signals = signals # For emitting progress, logs, etc.
        self.skip_current_file_flag = skip_current_file_flag # Event to skip current file download

        # Sets and locks for tracking downloaded files/hashes across threads/workers
        self.downloaded_files = downloaded_files if downloaded_files is not None else set()
        self.downloaded_file_hashes = downloaded_file_hashes if downloaded_file_hashes is not None else set()
        self.downloaded_files_lock = downloaded_files_lock if downloaded_files_lock is not None else threading.Lock()
        self.downloaded_file_hashes_lock = downloaded_file_hashes_lock if downloaded_file_hashes_lock is not None else threading.Lock()

        self.skip_words_list = skip_words_list if skip_words_list is not None else []
        self.show_external_links = show_external_links # Whether to extract and log external links
        self.extract_links_only = extract_links_only # If true, only extracts links, no downloads
        self.num_file_threads = num_file_threads # Threads for downloading files within this post

        self.manga_mode_active = manga_mode_active # True if manga mode is on

        # Disable compression if Pillow is not available
        if self.compress_images and Image is None:
            self.logger("⚠️ Image compression disabled: Pillow library not found.")
            self.compress_images = False

    def logger(self, message):
        """Emits a log message via the progress_signal if available."""
        if self.signals and hasattr(self.signals, 'progress_signal'):
            self.signals.progress_signal.emit(message)
        else: # Fallback if signals are not connected (e.g., testing)
            print(f"(Worker Log - No Signal): {message}")

    def check_cancel(self):
        """Checks if cancellation has been requested."""
        return self.cancellation_event.is_set()

    def _download_single_file(self, file_info, target_folder_path, headers, original_post_id_for_log, skip_event,
                              post_title="", file_index_in_post=0): # Added post_title here
        """Downloads a single file, handles retries, compression, and hash checking."""
        if self.check_cancel() or (skip_event and skip_event.is_set()): return 0, 1 # Downloaded, Skipped

        file_url = file_info.get('url')
        # Use '_original_name_for_log' if available (set in process()), otherwise 'name'
        api_original_filename = file_info.get('_original_name_for_log', file_info.get('name'))

        if not file_url or not api_original_filename:
            self.logger(f"⚠️ Skipping file from post {original_post_id_for_log}: Missing URL or original filename. Info: {str(file_info)[:100]}")
            return 0, 1

        # --- Skip Check 1: Skip Words (Always based on Filename) ---
        if self.skip_words_list:
            content_to_check_for_skip_words = api_original_filename.lower() # ALWAYS use filename for skip words
            log_source_for_skip_words = f"Filename '{api_original_filename}'"
            
            for skip_word in self.skip_words_list:
                if skip_word.lower() in content_to_check_for_skip_words:
                    self.logger(f"   -> Skip File (Keyword Match): {log_source_for_skip_words} contains '{skip_word}'.")
                    return 0, 1
        
        # --- Character Filter (Global Gate) ---
        # If character filters are active, the item (post for manga, file for normal) must match.
        if self.filter_character_list:
            matches_any_character_filter = False
            if self.manga_mode_active:
                # Manga Mode: Character filter applies to POST TITLE
                if any(is_title_match_for_character(post_title, char_filter) for char_filter in self.filter_character_list):
                    matches_any_character_filter = True
                if not matches_any_character_filter:
                    # This log might be redundant if the post-level check in process() already skipped it,
                    # but it's a safeguard if a file somehow reaches here without its post title matching.
                    self.logger(f"   -> Skip File (Manga Mode - Post Title No Char Match): Title '{post_title[:30]}' doesn't match active character filters for this file.")
                    return 0, 1
            else: # Normal mode: Character filter applies to FILENAME
                if any(is_filename_match_for_character(api_original_filename, char_filter) for char_filter in self.filter_character_list):
                    matches_any_character_filter = True
                if not matches_any_character_filter:
                    self.logger(f"   -> Skip File (Normal Mode - Filename No Char Match): '{api_original_filename}' doesn't match active character filters.")
                    return 0, 1
        
        # --- Filename Generation (Manga Mode vs Normal Mode) ---
        _, original_ext = os.path.splitext(api_original_filename)
        if original_ext and not original_ext.startswith('.'): original_ext = '.' + original_ext
        elif not original_ext: # Try to derive extension if missing
            _, temp_ext = os.path.splitext(clean_filename(api_original_filename)) # Clean first
            if temp_ext and not temp_ext.startswith('.'): original_ext = '.' + temp_ext
            elif temp_ext: original_ext = temp_ext
            else: original_ext = '' # No extension found

        filename_to_save = ""
        if self.manga_mode_active:
            # Manga mode renaming logic (uses post_title and sequence)
            if post_title and post_title.strip():
                cleaned_post_title_full = clean_filename(post_title.strip()) # Clean the post title for filename use
                original_filename_base, _ = os.path.splitext(api_original_filename) # Get base of original API filename

                # Try to extract a sequence number from the original filename
                extracted_sequence_from_original = ""
                # Simple number at the end: e.g., "image_01", "pic123"
                simple_end_match = re.search(r'(\d+)$', original_filename_base)
                if simple_end_match:
                    extracted_sequence_from_original = simple_end_match.group(1).zfill(2) # Pad with zero if needed
                else:
                    # More complex patterns like "page 01", "ch-2", "ep_003"
                    complex_match = re.search(r'(?:[ _.\-/]|^)(?:p|page|ch|chapter|ep|episode|v|vol|volume|no|num|number|pt|part)[ _.\-]*(\d+)', original_filename_base, re.IGNORECASE)
                    if complex_match:
                        extracted_sequence_from_original = complex_match.group(1).zfill(2) # Pad

                # Base for new filename from post title, removing existing page/chapter numbers from title
                cleaned_title_base = re.sub(
                    r'[|\[\]()]*[ _.\-]*(?:page|p|ch|chapter|ep|episode|v|vol|volume|no|num|number|pt|part)s?[ _.\-]*\d+([ _.\-]+\d+)?([ _.\-]*(?:END|FIN))?$',
                    '',
                    cleaned_post_title_full,
                    flags=re.IGNORECASE
                ).strip()
                if not cleaned_title_base: # Fallback if regex strips everything
                    cleaned_title_base = cleaned_post_title_full 
                cleaned_title_base = cleaned_title_base.rstrip(' _.-') # Clean trailing separators

                if extracted_sequence_from_original:
                    filename_to_save = f"{cleaned_title_base} - {extracted_sequence_from_original}{original_ext}"
                else:
                    # Fallback to file index in post if no sequence found in original filename
                    fallback_sequence = str(file_index_in_post + 1).zfill(2) # Pad with zero
                    filename_to_save = f"{cleaned_title_base} - {fallback_sequence}{original_ext}"
                
                # Handle potential filename collisions by appending a counter
                counter = 1
                base_name_coll, ext_coll = os.path.splitext(filename_to_save)
                temp_filename_for_collision_check = filename_to_save
                while os.path.exists(os.path.join(target_folder_path, temp_filename_for_collision_check)):
                    temp_filename_for_collision_check = f"{base_name_coll}_{counter}{ext_coll}"
                    counter += 1
                if temp_filename_for_collision_check != filename_to_save:
                    # self.logger(f"   Manga Mode: Collision detected. Adjusted filename to '{temp_filename_for_collision_check}'")
                    filename_to_save = temp_filename_for_collision_check
            else: # Manga mode but post_title is missing (should be rare)
                filename_to_save = clean_filename(api_original_filename) # Fallback to cleaned original
                self.logger(f"⚠️ Manga mode: Post title missing for post {original_post_id_for_log}. Using cleaned original filename '{filename_to_save}'.")
        else: # Normal mode
            filename_to_save = clean_filename(api_original_filename)

        final_filename_for_sets_and_saving = filename_to_save # This is the name used for saving and duplicate checks

        # --- File Type Filtering (applies to both modes, based on original filename) ---
        if not self.download_thumbnails: # Thumbnail mode bypasses these filters
            is_img_type = is_image(api_original_filename) # Check original type
            is_vid_type = is_video(api_original_filename)
            is_zip_type = is_zip(api_original_filename)
            is_rar_type = is_rar(api_original_filename)

            if self.filter_mode == 'image' and not is_img_type:
                self.logger(f"   -> Filter Skip: '{api_original_filename}' (Not Image).")
                return 0,1
            if self.filter_mode == 'video' and not is_vid_type:
                self.logger(f"   -> Filter Skip: '{api_original_filename}' (Not Video).")
                return 0,1
            if self.skip_zip and is_zip_type:
                self.logger(f"   -> Pref Skip: '{api_original_filename}' (ZIP).")
                return 0,1
            if self.skip_rar and is_rar_type:
                self.logger(f"   -> Pref Skip: '{api_original_filename}' (RAR).")
                return 0,1

        target_folder_basename = os.path.basename(target_folder_path) # For logging
        current_save_path = os.path.join(target_folder_path, final_filename_for_sets_and_saving)

        # --- Duplicate Checks (Path, Global Filename, Hash) ---
        if os.path.exists(current_save_path) and os.path.getsize(current_save_path) > 0:
             self.logger(f"   -> Exists (Path): '{final_filename_for_sets_and_saving}' in '{target_folder_basename}'.")
             with self.downloaded_files_lock: self.downloaded_files.add(final_filename_for_sets_and_saving) # Add to global set
             return 0, 1

        with self.downloaded_files_lock:
            if final_filename_for_sets_and_saving in self.downloaded_files:
                self.logger(f"   -> Global Skip (Filename): '{final_filename_for_sets_and_saving}' already recorded as downloaded this session.")
                return 0, 1

        # --- Download Loop with Retries ---
        max_retries = 3
        retry_delay = 5 # seconds
        downloaded_size_bytes = 0 
        calculated_file_hash = None
        file_content_bytes = None # BytesIO to hold downloaded content
        total_size_bytes = 0 # From Content-Length header, set on first attempt
        download_successful_flag = False

        for attempt_num in range(max_retries + 1): # max_retries means max_retries + 1 attempts total
            if self.check_cancel() or (skip_event and skip_event.is_set()):
                break # Exit retry loop if cancelled
            try:
                if attempt_num > 0:
                    self.logger(f"   Retrying '{api_original_filename}' (Attempt {attempt_num}/{max_retries})...")
                    time.sleep(retry_delay * (2**(attempt_num - 1))) # Exponential backoff

                if self.signals and hasattr(self.signals, 'file_download_status_signal'):
                    self.signals.file_download_status_signal.emit(True) # Signal download start

                response = requests.get(file_url, headers=headers, timeout=(15, 300), stream=True) # connect_timeout, read_timeout
                response.raise_for_status() # Check for HTTP errors

                current_total_size_bytes_from_headers = int(response.headers.get('Content-Length', 0))

                if attempt_num == 0: # First attempt, log initial size
                    total_size_bytes = current_total_size_bytes_from_headers
                    size_str = f"{total_size_bytes / (1024 * 1024):.2f} MB" if total_size_bytes > 0 else "unknown size"
                    self.logger(f"⬇️ Downloading: '{api_original_filename}' (Size: {size_str}) [Saving as: '{final_filename_for_sets_and_saving}']")

                # Use the size from the current attempt for progress reporting
                current_attempt_total_size = current_total_size_bytes_from_headers
                
                file_content_buffer = BytesIO() # Buffer for this attempt's content
                current_attempt_downloaded_bytes = 0
                md5_hasher = hashlib.md5()
                last_progress_time = time.time()

                for chunk in response.iter_content(chunk_size=1 * 1024 * 1024): # 1MB chunks
                    if self.check_cancel() or (skip_event and skip_event.is_set()):
                        break # Stop reading chunks if cancelled
                    if chunk:
                        file_content_buffer.write(chunk)
                        md5_hasher.update(chunk)
                        current_attempt_downloaded_bytes += len(chunk)
                        # Emit progress signal periodically
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
                    break # Break from retry loop if cancelled during chunk iteration

                # Check if download was successful for this attempt
                if current_attempt_downloaded_bytes > 0: # Successfully downloaded some data
                    calculated_file_hash = md5_hasher.hexdigest()
                    downloaded_size_bytes = current_attempt_downloaded_bytes
                    if file_content_bytes: file_content_bytes.close() # Close previous attempt's buffer
                    file_content_bytes = file_content_buffer # Keep this attempt's content
                    file_content_bytes.seek(0) # Reset pointer for reading
                    download_successful_flag = True
                    break # Exit retry loop on success
                elif current_attempt_total_size == 0 and response.status_code == 200: # Handle 0-byte files
                    self.logger(f"   Note: '{api_original_filename}' is a 0-byte file according to server.")
                    calculated_file_hash = md5_hasher.hexdigest() # Hash of empty content
                    downloaded_size_bytes = 0
                    if file_content_bytes: file_content_bytes.close()
                    file_content_bytes = file_content_buffer # Keep empty buffer
                    file_content_bytes.seek(0)
                    download_successful_flag = True
                    break # Exit retry loop
                else: # No data or failed attempt (e.g. connection dropped before any data)
                    if file_content_buffer: file_content_buffer.close() # Discard this attempt's buffer

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, http.client.IncompleteRead) as e:
                self.logger(f"   ❌ Download Error (Retryable): {api_original_filename}. Error: {e}")
                if 'file_content_buffer' in locals() and file_content_buffer: file_content_buffer.close()
            except requests.exceptions.RequestException as e: # Non-retryable (like 404)
                self.logger(f"   ❌ Download Error (Non-Retryable): {api_original_filename}. Error: {e}")
                if 'file_content_buffer' in locals() and file_content_buffer: file_content_buffer.close()
                break # Break from retry loop
            except Exception as e: # Other unexpected errors
                self.logger(f"   ❌ Unexpected Download Error: {api_original_filename}: {e}\n{traceback.format_exc(limit=2)}")
                if 'file_content_buffer' in locals() and file_content_buffer: file_content_buffer.close()
                break # Break from retry loop
            finally:
                if self.signals and hasattr(self.signals, 'file_download_status_signal'):
                    self.signals.file_download_status_signal.emit(False) # Signal download end/attempt end
        # End of retry loop

        # Emit final progress update (e.g., 100% or 0/0 if failed)
        if self.signals and hasattr(self.signals, 'file_progress_signal'):
             # Use total_size_bytes from the first successful header read for consistency in total
             final_total_for_progress = total_size_bytes if download_successful_flag and total_size_bytes > 0 else downloaded_size_bytes
             self.signals.file_progress_signal.emit(api_original_filename, downloaded_size_bytes, final_total_for_progress)


        if self.check_cancel() or (skip_event and skip_event.is_set()):
            self.logger(f"   ⚠️ Download interrupted for {api_original_filename}.")
            if file_content_bytes: file_content_bytes.close()
            return 0, 1 # Skipped due to interruption

        if not download_successful_flag:
            self.logger(f"❌ Download failed for '{api_original_filename}' after {max_retries + 1} attempts.")
            if file_content_bytes: file_content_bytes.close() 
            return 0, 1 # Skipped due to download failure

        # --- Hash Check (post-download), Compression, Saving ---
        with self.downloaded_file_hashes_lock:
             if calculated_file_hash in self.downloaded_file_hashes:
                self.logger(f"   -> Content Skip (Hash): '{api_original_filename}' (Hash: {calculated_file_hash[:8]}...) already downloaded this session.")
                with self.downloaded_files_lock: self.downloaded_files.add(final_filename_for_sets_and_saving) # Still mark filename as "processed"
                if file_content_bytes: file_content_bytes.close()
                return 0, 1 # Skipped due to hash duplicate

        bytes_to_write = file_content_bytes # This is the BytesIO from the successful download
        final_filename_after_processing = final_filename_for_sets_and_saving # May change if compressed
        current_save_path_final = current_save_path # May change if filename changes due to compression

        is_img_for_compress_check = is_image(api_original_filename) # Check original type for compression eligibility
        if is_img_for_compress_check and self.compress_images and Image and downloaded_size_bytes > (1.5 * 1024 * 1024): # Compress if > 1.5MB
            self.logger(f"   Compressing '{api_original_filename}' ({downloaded_size_bytes / (1024*1024):.2f} MB)...")
            try:
                # Ensure bytes_to_write is at the beginning for Pillow
                bytes_to_write.seek(0)
                with Image.open(bytes_to_write) as img_obj:
                    # Handle palette mode images and convert to RGB/RGBA for WebP
                    if img_obj.mode == 'P': img_obj = img_obj.convert('RGBA') 
                    elif img_obj.mode not in ['RGB', 'RGBA', 'L']: img_obj = img_obj.convert('RGB')

                    compressed_bytes_io = BytesIO()
                    img_obj.save(compressed_bytes_io, format='WebP', quality=80, method=4) # method 4 is a good balance
                    compressed_size = compressed_bytes_io.getbuffer().nbytes

                # Only use compressed if significantly smaller (e.g., >10% reduction)
                if compressed_size < downloaded_size_bytes * 0.9: 
                    self.logger(f"   Compression success: {compressed_size / (1024*1024):.2f} MB.")
                    bytes_to_write.close() # Close original downloaded content stream
                    bytes_to_write = compressed_bytes_io # Use compressed content stream
                    bytes_to_write.seek(0) # Reset pointer for writing

                    base_name_orig, _ = os.path.splitext(final_filename_for_sets_and_saving)
                    final_filename_after_processing = base_name_orig + '.webp' # Change extension
                    current_save_path_final = os.path.join(target_folder_path, final_filename_after_processing)
                    self.logger(f"   Updated filename (compressed): {final_filename_after_processing}")
                else:
                    self.logger(f"   Compression skipped: WebP not significantly smaller."); bytes_to_write.seek(0) # Reset pointer if not using compressed
            except Exception as comp_e:
                self.logger(f"❌ Compression failed for '{api_original_filename}': {comp_e}. Saving original."); bytes_to_write.seek(0) # Reset pointer

        # Check for existence again if filename changed due to compression
        if final_filename_after_processing != final_filename_for_sets_and_saving and \
           os.path.exists(current_save_path_final) and os.path.getsize(current_save_path_final) > 0:
            self.logger(f"   -> Exists (Path - Post-Compress): '{final_filename_after_processing}' in '{target_folder_basename}'.")
            with self.downloaded_files_lock: self.downloaded_files.add(final_filename_after_processing)
            bytes_to_write.close()
            return 0, 1

        # --- Save the file ---
        try:
            os.makedirs(os.path.dirname(current_save_path_final), exist_ok=True) # Ensure directory exists
            with open(current_save_path_final, 'wb') as f_out:
                f_out.write(bytes_to_write.getvalue()) # Write content

            # Add to downloaded sets upon successful save
            with self.downloaded_file_hashes_lock: self.downloaded_file_hashes.add(calculated_file_hash)
            with self.downloaded_files_lock: self.downloaded_files.add(final_filename_after_processing)

            self.logger(f"✅ Saved: '{final_filename_after_processing}' (from '{api_original_filename}', {downloaded_size_bytes / (1024*1024):.2f} MB) in '{target_folder_basename}'")
            time.sleep(0.05) # Small delay, can be removed if not needed
            return 1, 0 # Downloaded, Skipped
        except Exception as save_err:
             self.logger(f"❌ Save Fail for '{final_filename_after_processing}': {save_err}")
             if os.path.exists(current_save_path_final): # Attempt to remove partial file
                  try: os.remove(current_save_path_final);
                  except OSError: self.logger(f"  -> Failed to remove partially saved file: {current_save_path_final}")
             return 0, 1 # Skipped due to save error
        finally:
            if bytes_to_write: bytes_to_write.close() # Ensure stream is closed


    def process(self):
        """Main processing logic for a single post."""
        if self.check_cancel(): return 0, 0 # Downloaded, Skipped

        total_downloaded_this_post = 0
        total_skipped_this_post = 0
        
        # Prepare headers for file downloads
        parsed_api_url = urlparse(self.api_url_input) # Use the original input URL for referer base
        referer_url = f"https://{parsed_api_url.netloc}/"
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': referer_url, 'Accept': '*/*'}

        # Regex for finding links in HTML content
        link_pattern = re.compile(r"""<a\s+.*?href=["'](https?://[^"']+)["'][^>]*>(.*?)</a>""",
                                  re.IGNORECASE | re.DOTALL)

        # Extract post details
        post_data = self.post
        post_title = post_data.get('title', '') or 'untitled_post'
        post_id = post_data.get('id', 'unknown_id')
        post_main_file_info = post_data.get('file') # Main file object for the post
        post_attachments = post_data.get('attachments', []) # List of attachment objects
        post_content_html = post_data.get('content', '') # HTML content of the post

        # Log post processing start
        self.logger(f"\n--- Processing Post {post_id} ('{post_title[:50]}...') (Thread: {threading.current_thread().name}) ---")

        num_potential_files = len(post_attachments or []) + (1 if post_main_file_info and post_main_file_info.get('path') else 0)

        # --- Post-Level Skip Word Check (REMOVED for Manga Mode based on Title) ---
        # Skip words are now ALWAYS checked at the file level based on FILENAME in _download_single_file.
        # The old Manga Mode post-level skip based on title is removed.

        # --- Post-Level Character Filter Check (Only for Manga Mode, based on Title) ---
        # If Manga Mode is active and character filters are set, the post title MUST match one of them.
        # This acts as a gate for processing files from this post in Manga Mode.
        if not self.extract_links_only and self.manga_mode_active and self.filter_character_list:
            if not any(is_title_match_for_character(post_title, char_name) for char_name in self.filter_character_list):
                self.logger(f"   -> Skip Post (Manga Mode - Title No Char Match): Title '{post_title[:50]}' doesn't match active character filters.")
                return 0, num_potential_files # Skip all files in this post

        # Validate attachments structure
        if not isinstance(post_attachments, list):
            self.logger(f"⚠️ Corrupt attachment data for post {post_id} (expected list, got {type(post_attachments)}). Skipping attachments.")
            post_attachments = []

        # --- Determine Base Save Folders ---
        potential_base_save_folders = [] # List of base folder names (not full paths yet)
        if not self.extract_links_only: # Folder logic only applies if not just extracting links
            if self.use_subfolders:
                if self.filter_character_list: # User specified character names for folders
                    if self.manga_mode_active:
                        # Manga Mode: Only consider character folders if post title matches that character
                        for char_filter_name in self.filter_character_list:
                            if is_title_match_for_character(post_title, char_filter_name):
                                cleaned_folder = clean_folder_name(char_filter_name)
                                if cleaned_folder: potential_base_save_folders.append(cleaned_folder)
                        # If in manga mode and title didn't match any char filter, this list will be empty.
                        # The post-level skip above should have already caught this.
                    else: # Normal Mode: Create folders for all specified character filters
                        for char_filter_name in self.filter_character_list:
                            cleaned_folder = clean_folder_name(char_filter_name)
                            if cleaned_folder: potential_base_save_folders.append(cleaned_folder)
                    
                    if potential_base_save_folders:
                        self.logger(f"   Folder Target(s) (from Character Filter list): {', '.join(potential_base_save_folders)}")
                    elif self.filter_character_list: 
                         self.logger(f"   Note: Post {post_id} title did not match character filters for folder assignment (Manga Mode) or no valid char folders.")
                
                else: # No character filter list from UI, derive folders from title using known_names
                    derived_folders = match_folders_from_title(post_title, self.known_names, self.unwanted_keywords)
                    if derived_folders:
                        potential_base_save_folders.extend(derived_folders)
                        self.logger(f"   Folder Target(s) (Derived from Title & Known Names): {', '.join(derived_folders)}")
                    else: # Fallback if no known_names match
                        fallback_folder = extract_folder_name_from_title(post_title, self.unwanted_keywords)
                        potential_base_save_folders.append(fallback_folder)
                        self.logger(f"   Folder Target (Fallback from Title): {fallback_folder}")
                
                if not potential_base_save_folders: # If still no folders, use a generic one based on post title or default
                    potential_base_save_folders.append(clean_folder_name(post_title if post_title else "untitled_creator_content"))
                    self.logger(f"   Folder Target (Final Fallback): {potential_base_save_folders[0]}")

            else: # Not using subfolders, all files go to download_root
                potential_base_save_folders = [""] # Represents the root download directory

        # --- Post-Level Skip Words in Folder Name ---
        # This applies if subfolders are used and a folder name itself contains a skip word.
        if not self.extract_links_only and self.use_subfolders and self.skip_words_list:
            for folder_name_to_check in potential_base_save_folders:
                if not folder_name_to_check: continue # Skip root ""
                if any(skip_word.lower() in folder_name_to_check.lower() for skip_word in self.skip_words_list):
                    matched_skip = next((sw for sw in self.skip_words_list if sw.lower() in folder_name_to_check.lower()), "unknown_skip_word")
                    self.logger(f"   -> Skip Post (Folder Keyword): Potential folder '{folder_name_to_check}' contains '{matched_skip}'.")
                    return 0, num_potential_files

        # --- Extract and Log External Links ---
        if (self.show_external_links or self.extract_links_only) and post_content_html:
            try:
                unique_links_data = {} # Store unique URLs and their text
                for match in link_pattern.finditer(post_content_html):
                    link_url = match.group(1).strip()
                    link_inner_text = match.group(2) # Raw inner HTML of the <a> tag

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
            return 0, 0 

        # --- Prepare List of Files to Download ---
        files_to_download_info_list = []
        api_file_domain = urlparse(self.api_url_input).netloc
        if not api_file_domain: 
            api_file_domain = "kemono.su" if "kemono" in self.service.lower() else "coomer.party"


        if self.download_thumbnails: 
            self.logger(f"   Thumbnail-only mode for Post {post_id}.")
            if post_main_file_info and isinstance(post_main_file_info, dict) and post_main_file_info.get('path'):
                if is_image(post_main_file_info.get('name')): 
                    file_path = post_main_file_info['path'].lstrip('/')
                    original_api_name = post_main_file_info.get('name') or os.path.basename(file_path)
                    if original_api_name:
                        files_to_download_info_list.append({
                            'url': f"https://{api_file_domain}{file_path}" if file_path.startswith('/') else f"https://{api_file_domain}/data/{file_path}",
                            'name': original_api_name, 
                            '_original_name_for_log': original_api_name, 
                            '_is_thumbnail': True
                        })
            for att_info in post_attachments:
                 if isinstance(att_info, dict) and att_info.get('path') and is_image(att_info.get('name')):
                    att_path = att_info['path'].lstrip('/')
                    original_api_att_name = att_info.get('name') or os.path.basename(att_path)
                    if original_api_att_name:
                        files_to_download_info_list.append({
                            'url': f"https://{api_file_domain}{att_path}" if att_path.startswith('/') else f"https://{api_file_domain}/data/{att_path}",
                            'name': original_api_att_name,
                            '_original_name_for_log': original_api_att_name,
                            '_is_thumbnail': True
                        })
            if not files_to_download_info_list:
                self.logger(f"   -> No image thumbnails found for post {post_id} in thumbnail-only mode.")
                return 0, 0
        else: # Normal download mode
            if post_main_file_info and isinstance(post_main_file_info, dict) and post_main_file_info.get('path'):
                file_path = post_main_file_info['path'].lstrip('/')
                original_api_name = post_main_file_info.get('name') or os.path.basename(file_path)
                if original_api_name:
                    files_to_download_info_list.append({
                        'url': f"https://{api_file_domain}{file_path}" if file_path.startswith('/') else f"https://{api_file_domain}/data/{file_path}",
                        'name': original_api_name,
                        '_original_name_for_log': original_api_name,
                        '_is_thumbnail': False
                    })
                else: self.logger(f"   ⚠️ Skipping main file for post {post_id}: Missing name (Path: {file_path})")
            for idx, att_info in enumerate(post_attachments):
                if isinstance(att_info, dict) and att_info.get('path'):
                    att_path = att_info['path'].lstrip('/')
                    original_api_att_name = att_info.get('name') or os.path.basename(att_path)
                    if original_api_att_name:
                        files_to_download_info_list.append({
                            'url': f"https://{api_file_domain}{att_path}" if att_path.startswith('/') else f"https://{api_file_domain}/data/{att_path}",
                            'name': original_api_att_name,
                            '_original_name_for_log': original_api_att_name,
                            '_is_thumbnail': False
                        })
                    else: self.logger(f"   ⚠️ Skipping attachment {idx+1} for post {post_id}: Missing name (Path: {att_path})")
                else: self.logger(f"   ⚠️ Skipping invalid attachment {idx+1} for post {post_id}: {str(att_info)[:100]}")

        if not files_to_download_info_list:
            self.logger(f"   No files found to download for post {post_id}.")
            return 0, 0 

        self.logger(f"   Identified {len(files_to_download_info_list)} file(s) for potential download from post {post_id}.")

        # --- File Download Loop (using ThreadPoolExecutor for individual files) ---
        with ThreadPoolExecutor(max_workers=self.num_file_threads, thread_name_prefix=f'P{post_id}File_') as file_pool:
            futures_list = []
            for file_idx, file_info_to_dl in enumerate(files_to_download_info_list):
                if self.check_cancel(): break

                actual_target_full_paths_for_this_file = [] 

                if self.use_subfolders:
                    if self.filter_character_list: 
                        for char_name_from_filter_list in self.filter_character_list:
                            assign_to_this_char_folder = False
                            if self.manga_mode_active:
                                # Manga Mode: Folder assignment is based on post_title matching char_name_from_filter_list
                                # This check is somewhat redundant if the post-level title check passed,
                                # but ensures files from this post go into the matched character's folder.
                                if is_title_match_for_character(post_title, char_name_from_filter_list):
                                    assign_to_this_char_folder = True
                            else: # Normal mode
                                if is_filename_match_for_character(file_info_to_dl.get('_original_name_for_log'), char_name_from_filter_list):
                                    assign_to_this_char_folder = True
                            
                            if assign_to_this_char_folder:
                                base_char_folder_path = os.path.join(self.download_root, clean_folder_name(char_name_from_filter_list))
                                if self.use_post_subfolders:
                                    cleaned_title_for_subfolder = clean_folder_name(post_title)
                                    post_specific_subfolder_name = f"{post_id}_{cleaned_title_for_subfolder}" if cleaned_title_for_subfolder else f"{post_id}_untitled"
                                    actual_target_full_paths_for_this_file.append(os.path.join(base_char_folder_path, post_specific_subfolder_name))
                                else:
                                    actual_target_full_paths_for_this_file.append(base_char_folder_path)
                    
                    else: 
                        for base_folder_name in potential_base_save_folders: 
                            base_folder_path = os.path.join(self.download_root, base_folder_name)
                            if self.use_post_subfolders:
                                cleaned_title_for_subfolder = clean_folder_name(post_title)
                                post_specific_subfolder_name = f"{post_id}_{cleaned_title_for_subfolder}" if cleaned_title_for_subfolder else f"{post_id}_untitled"
                                actual_target_full_paths_for_this_file.append(os.path.join(base_folder_path, post_specific_subfolder_name))
                            else:
                                actual_target_full_paths_for_this_file.append(base_folder_path)
                else: 
                    actual_target_full_paths_for_this_file = [self.download_root]
                
                if self.target_post_id_from_initial_url and self.custom_folder_name:
                    custom_full_path = os.path.join(self.download_root, self.custom_folder_name)
                    actual_target_full_paths_for_this_file = [custom_full_path]
                    # self.logger(f"   Using custom folder for single post: {custom_full_path}") # Logged once is enough


                if not actual_target_full_paths_for_this_file:
                    self.logger(f"   -> File Skip (No Target Folder): '{file_info_to_dl.get('_original_name_for_log')}' for post '{post_title[:30]}'. No character folder match or other path error.")
                    total_skipped_this_post +=1
                    continue 

                for target_path in set(actual_target_full_paths_for_this_file): 
                    if self.check_cancel(): break
                    futures_list.append(file_pool.submit(
                        self._download_single_file,
                        file_info_to_dl,
                        target_path, 
                        headers,
                        post_id, 
                        self.skip_current_file_flag, 
                        post_title, 
                        file_idx 
                    ))
                if self.check_cancel(): break 

            for future in as_completed(futures_list):
                if self.check_cancel(): 
                    for f_to_cancel in futures_list:
                        if not f_to_cancel.done():
                            f_to_cancel.cancel()
                    break 
                try:
                    dl_count, skip_count = future.result() 
                    total_downloaded_this_post += dl_count
                    total_skipped_this_post += skip_count
                except CancelledError: 
                    total_skipped_this_post += 1 
                except Exception as exc_f:
                    self.logger(f"❌ File download task for post {post_id} resulted in error: {exc_f}")
                    total_skipped_this_post += 1 
        
        if self.signals and hasattr(self.signals, 'file_progress_signal'):
            self.signals.file_progress_signal.emit("", 0, 0) 

        if self.check_cancel(): self.logger(f"   Post {post_id} processing interrupted/cancelled.");
        else: self.logger(f"   Post {post_id} Summary: Downloaded={total_downloaded_this_post}, Skipped Files={total_skipped_this_post}")

        return total_downloaded_this_post, total_skipped_this_post


class DownloadThread(QThread):
    """
    Manages the overall download process. 
    Fetches posts using download_from_api and then processes each post using PostProcessorWorker.
    This class is typically used when the GUI needs a separate thread for the entire download operation
    (e.g., when not using the multi-threaded PostFetcher model from the main app).
    """
    progress_signal = pyqtSignal(str) # For general log messages
    add_character_prompt_signal = pyqtSignal(str) # To ask user to add character to known list
    file_download_status_signal = pyqtSignal(bool) # True when a file download starts, False when it ends
    finished_signal = pyqtSignal(int, int, bool) # (total_downloaded, total_skipped, was_cancelled)
    external_link_signal = pyqtSignal(str, str, str, str) # (post_title, link_text, link_url, platform)
    file_progress_signal = pyqtSignal(str, int, int) # (filename, downloaded_bytes, total_bytes)

    def __init__(self, api_url_input, output_dir, known_names_copy,
                 cancellation_event, # threading.Event()
                 filter_character_list=None,
                 filter_mode='all', skip_zip=True, skip_rar=True,
                 use_subfolders=True, use_post_subfolders=False, custom_folder_name=None, compress_images=False,
                 download_thumbnails=False, service=None, user_id=None,
                 downloaded_files=None, downloaded_file_hashes=None, downloaded_files_lock=None, downloaded_file_hashes_lock=None,
                 skip_words_list=None,
                 show_external_links=False,
                 extract_links_only=False,
                 num_file_threads_for_worker=1, # Threads per PostProcessorWorker instance
                 skip_current_file_flag=None, # threading.Event() to skip one file
                 start_page=None, end_page=None,
                 target_post_id_from_initial_url=None, # If the input URL was a specific post
                 manga_mode_active=False,
                 unwanted_keywords=None # Set of keywords to avoid in auto-generated folder names
                 ):
        super().__init__()
        # --- Store all passed arguments as instance attributes ---
        self.api_url_input = api_url_input
        self.output_dir = output_dir
        self.known_names = list(known_names_copy) # Use a copy
        self.cancellation_event = cancellation_event
        self.skip_current_file_flag = skip_current_file_flag
        self.initial_target_post_id = target_post_id_from_initial_url
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
        # Shared sets and locks for tracking downloads across potential multiple workers (if this thread spawns them)
        self.downloaded_files = downloaded_files if downloaded_files is not None else set()
        self.downloaded_files_lock = downloaded_files_lock if downloaded_files_lock is not None else threading.Lock()
        self.downloaded_file_hashes = downloaded_file_hashes if downloaded_file_hashes is not None else set()
        self.downloaded_file_hashes_lock = downloaded_file_hashes_lock if downloaded_file_hashes_lock is not None else threading.Lock()
        
        self._add_character_response = None # For handling synchronous prompt results
        self.prompt_mutex = QMutex() # Mutex for _add_character_response
        
        self.show_external_links = show_external_links
        self.extract_links_only = extract_links_only
        self.num_file_threads_for_worker = num_file_threads_for_worker
        self.start_page = start_page
        self.end_page = end_page
        self.manga_mode_active = manga_mode_active
        self.unwanted_keywords = unwanted_keywords if unwanted_keywords is not None else \
                                 {'spicy', 'hd', 'nsfw', '4k', 'preview', 'teaser', 'clip'} # Default unwanted keywords

        # Disable compression if Pillow is not available
        if self.compress_images and Image is None:
            self.logger("⚠️ Image compression disabled: Pillow library not found (DownloadThread).")
            self.compress_images = False

    def logger(self, message):
        """Emits a log message via the progress_signal."""
        self.progress_signal.emit(str(message))

    def isInterruptionRequested(self):
        """Checks if Qt interruption or manual cancellation event is set."""
        return super().isInterruptionRequested() or self.cancellation_event.is_set()

    def skip_file(self):
        """Sets the flag to skip the currently processing file (if any)."""
        if self.isRunning() and self.skip_current_file_flag:
             self.logger("⏭️ Skip requested for current file (single-thread mode).")
             self.skip_current_file_flag.set() # Signal the PostProcessorWorker
        else: self.logger("ℹ️ Skip file: No download active or skip flag not available.")

    def run(self):
        """Main execution logic for the download thread."""
        grand_total_downloaded_files = 0
        grand_total_skipped_files = 0
        was_process_cancelled = False

        # Create a signals object for PostProcessorWorker instances
        # This allows PostProcessorWorker to emit signals that this DownloadThread can connect to.
        worker_signals_obj = PostProcessorSignals()
        try:
            # Connect signals from the worker_signals_obj to this thread's signals
            # This effectively forwards signals from PostProcessorWorker up to the GUI
            worker_signals_obj.progress_signal.connect(self.progress_signal)
            worker_signals_obj.file_download_status_signal.connect(self.file_download_status_signal)
            worker_signals_obj.file_progress_signal.connect(self.file_progress_signal)
            worker_signals_obj.external_link_signal.connect(self.external_link_signal)

            self.logger("   Starting post fetch (single-threaded download process)...")
            # Get the generator for fetching posts
            post_generator = download_from_api(
                self.api_url_input,
                logger=self.logger, # Pass this thread's logger
                start_page=self.start_page,
                end_page=self.end_page,
                manga_mode=self.manga_mode_active,
                cancellation_event=self.cancellation_event # Pass cancellation event
            )

            for posts_batch_data in post_generator: # Iterate through batches of posts
                if self.isInterruptionRequested(): was_process_cancelled = True; break
                for individual_post_data in posts_batch_data: # Iterate through posts in a batch
                    if self.isInterruptionRequested(): was_process_cancelled = True; break

                    # Create a PostProcessorWorker for each post
                    post_processing_worker = PostProcessorWorker(
                         post_data=individual_post_data,
                         download_root=self.output_dir,
                         known_names=self.known_names, # Pass copy
                         filter_character_list=self.filter_character_list,
                         unwanted_keywords=self.unwanted_keywords,
                         filter_mode=self.filter_mode,
                         skip_zip=self.skip_zip, skip_rar=self.skip_rar,
                         use_subfolders=self.use_subfolders, use_post_subfolders=self.use_post_subfolders,
                         target_post_id_from_initial_url=self.initial_target_post_id,
                         custom_folder_name=self.custom_folder_name,
                         compress_images=self.compress_images, download_thumbnails=self.download_thumbnails,
                         service=self.service, user_id=self.user_id,
                         api_url_input=self.api_url_input,
                         cancellation_event=self.cancellation_event,
                         signals=worker_signals_obj, # Pass the shared signals object
                         downloaded_files=self.downloaded_files, # Pass shared sets and locks
                         downloaded_file_hashes=self.downloaded_file_hashes,
                         downloaded_files_lock=self.downloaded_files_lock, 
                         downloaded_file_hashes_lock=self.downloaded_file_hashes_lock,
                         skip_words_list=self.skip_words_list,
                         show_external_links=self.show_external_links,
                         extract_links_only=self.extract_links_only,
                         num_file_threads=self.num_file_threads_for_worker,
                         skip_current_file_flag=self.skip_current_file_flag,
                         manga_mode_active=self.manga_mode_active
                    )
                    try:
                        # Process the post (this will block until the worker is done with this post)
                        dl_count, skip_count = post_processing_worker.process()
                        grand_total_downloaded_files += dl_count
                        grand_total_skipped_files += skip_count
                    except Exception as proc_err:
                         post_id_for_err = individual_post_data.get('id', 'N/A')
                         self.logger(f"❌ Error processing post {post_id_for_err} in DownloadThread: {proc_err}")
                         traceback.print_exc()
                         # Estimate skipped files for this post if worker failed catastrophically
                         num_potential_files_est = len(individual_post_data.get('attachments', [])) + \
                                                   (1 if individual_post_data.get('file') else 0)
                         grand_total_skipped_files += num_potential_files_est

                    # Clear the skip_current_file_flag if it was set and processed
                    if self.skip_current_file_flag and self.skip_current_file_flag.is_set():
                        self.skip_current_file_flag.clear()
                        self.logger("   Skip current file flag was processed and cleared by DownloadThread.")
                    
                    self.msleep(10) # Small delay to allow GUI to update, if needed
                if was_process_cancelled: break # Break from batch loop if cancelled

            if not was_process_cancelled: self.logger("✅ All posts processed or end of content reached.")

        except Exception as main_thread_err:
            self.logger(f"\n❌ Critical error within DownloadThread run loop: {main_thread_err}")
            traceback.print_exc()
            # Ensure was_process_cancelled reflects the state if error wasn't due to user cancellation
            if not self.isInterruptionRequested(): was_process_cancelled = False # Error, not user cancel
        finally:
            # Clean up: Disconnect signals to avoid issues if the thread is somehow reused or objects persist
            try:
                if worker_signals_obj: # Check if it was initialized
                    worker_signals_obj.progress_signal.disconnect(self.progress_signal)
                    worker_signals_obj.file_download_status_signal.disconnect(self.file_download_status_signal)
                    worker_signals_obj.external_link_signal.disconnect(self.external_link_signal)
                    worker_signals_obj.file_progress_signal.disconnect(self.file_progress_signal)
            except (TypeError, RuntimeError) as e: # Catch if signals were already disconnected or other issues
                self.logger(f"ℹ️ Note during DownloadThread signal disconnection: {e}")
            
            # Emit the finished signal with totals and cancellation status
            self.finished_signal.emit(grand_total_downloaded_files, grand_total_skipped_files, was_process_cancelled)

    def receive_add_character_result(self, result):
        """Slot to receive the result from a character add prompt shown in the main thread."""
        with QMutexLocker(self.prompt_mutex): # Ensure thread-safe access
             self._add_character_response = result
        self.logger(f"   (DownloadThread) Received character prompt response: {'Yes (added/confirmed)' if result else 'No (declined/failed)'}")
        # This response might be used by logic within the thread if it was waiting for it,
        # though typically prompts are handled by the main GUI thread.
