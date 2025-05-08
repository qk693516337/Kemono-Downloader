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


def is_title_match_for_character(post_title, character_name_filter):
    """Checks if a post title contains a specific character name (case-insensitive, whole word)."""
    if not post_title:
        return False
    if not character_name_filter: # If no filter, it's considered a match (or handle as per broader logic)
        return True 

    # Regex to match whole word, case insensitive
    pattern = r"(?i)\b" + re.escape(character_name_filter) + r"\b"

    if re.search(pattern, post_title):
        return True
    return False


def clean_folder_name(name):
    """Cleans a string to be suitable for a folder name."""
    if not isinstance(name, str): name = str(name) # Ensure string
    # Remove invalid characters, replace spaces with underscores
    cleaned = re.sub(r'[^\w\s\-\_]', '', name) # Allow alphanumeric, whitespace, hyphen, underscore
    return cleaned.strip().replace(' ', '_')


def clean_filename(name):
    """Cleans a string to be suitable for a filename, preserving extension."""
    if not isinstance(name, str): name = str(name) # Ensure string
    # Remove invalid characters, replace spaces with underscores
    # Allow alphanumeric, whitespace, hyphen, underscore, and period (for extension)
    cleaned = re.sub(r'[^\w\s\-\_\.]', '', name)
    return cleaned.strip().replace(' ', '_')


def extract_folder_name_from_title(title, unwanted_keywords):
    """Extracts a potential folder name from a title, avoiding common unwanted keywords."""
    if not title: return 'Uncategorized'
    title_lower = title.lower()
    # Tokenize by words, prefer longer, more specific tokens if possible
    tokens = re.findall(r'\b[\w\-]+\b', title_lower) # Find alphanumeric words with hyphens
    for token in tokens:
        clean_token = clean_folder_name(token) # Clean the token itself
        if clean_token and clean_token not in unwanted_keywords:
            return clean_token # Return the first suitable token
    # If no suitable token found, use the cleaned full title (or fallback)
    cleaned_full_title = clean_folder_name(title)
    return cleaned_full_title if cleaned_full_title else 'Uncategorized'


def match_folders_from_title(title, names_to_match, unwanted_keywords):
    """Matches known names (characters/shows) in a title to suggest folder names."""
    if not title or not names_to_match: return []
    title_lower = title.lower()
    matched_cleaned_names = set()
    # Sort by length to match longer names first (e.g., "Luffy Gear 5" before "Luffy")
    sorted_names_to_match = sorted(names_to_match, key=len, reverse=True)

    for name in sorted_names_to_match:
        name_lower = name.lower()
        if not name_lower: continue # Skip empty names

        pattern = r'\b' + re.escape(name_lower) + r'\b' # Whole word match
        if re.search(pattern, title_lower):
             cleaned_name = clean_folder_name(name).lower() # Clean the original matched name
             if cleaned_name and cleaned_name not in unwanted_keywords:
                 matched_cleaned_names.add(cleaned_name)
    return sorted(list(matched_cleaned_names))


def is_image(filename):
    """Checks if a filename likely represents an image."""
    if not filename: return False
    return filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))


def is_video(filename):
    """Checks if a filename likely represents a video."""
    if not filename: return False
    return filename.lower().endswith(('.mp4', '.mov', '.mkv', '.webm', '.avi', '.wmv'))


def is_zip(filename):
    """Checks if a filename likely represents a ZIP archive."""
    if not filename: return False
    return filename.lower().endswith('.zip')


def is_rar(filename):
    """Checks if a filename likely represents a RAR archive."""
    if not filename: return False
    return filename.lower().endswith('.rar')


def is_post_url(url):
    """Checks if a URL likely points to a specific post."""
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

        if not (is_kemono or is_coomer): return None, None, None # Not a supported domain

        path_parts = [part for part in parsed_url.path.strip('/').split('/') if part]

        # Standard URL format: /<service>/user/<user_id>/post/<post_id>
        # Or creator feed: /<service>/user/<user_id>
        if len(path_parts) >= 3 and path_parts[1].lower() == 'user':
            service = path_parts[0]
            user_id = path_parts[2]
            if len(path_parts) >= 5 and path_parts[3].lower() == 'post':
                post_id = path_parts[4]
            return service, user_id, post_id

        # API URL format: /api/v1/<service>/user/<user_id>/post/<post_id>
        # Or creator feed: /api/v1/<service>/user/<user_id>
        if len(path_parts) >= 5 and path_parts[0].lower() == 'api' and \
           path_parts[1].lower() == 'v1' and path_parts[3].lower() == 'user':
            service = path_parts[2]
            user_id = path_parts[4]
            if len(path_parts) >= 7 and path_parts[5].lower() == 'post':
                post_id = path_parts[6]
            return service, user_id, post_id
            
    except Exception as e:
        # Log error if needed, but return None, None, None for graceful failure
        print(f"Debug: Exception during extract_post_info for URL '{url_string}': {e}")
    return None, None, None


def fetch_posts_paginated(api_url_base, headers, offset, logger, cancellation_event=None):
    """Fetches a single page of posts from the API. Checks cancellation_event if provided."""
    if cancellation_event and cancellation_event.is_set():
        logger("   Fetch cancelled before request.")
        raise RuntimeError("Fetch operation cancelled by user.") # Or return empty list

    paginated_url = f'{api_url_base}?o={offset}'
    logger(f"   Fetching: {paginated_url}")
    try:
        response = requests.get(paginated_url, headers=headers, timeout=(10, 60)) # connect timeout, read timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4XX or 5XX)
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
    except ValueError as e: # JSONDecodeError inherits from ValueError
        raise RuntimeError(f"Error decoding JSON from offset {offset} ({paginated_url}): {e}. Response text: {response.text[:200]}")
    except Exception as e: # Catch any other unexpected errors
        raise RuntimeError(f"Unexpected error fetching offset {offset} ({paginated_url}): {e}")


def download_from_api(api_url_input, logger=print, start_page=None, end_page=None, manga_mode=False, cancellation_event=None):
    """
    Generator function to fetch posts from Kemono/Coomer API.
    Handles pagination and specific post fetching.
    In manga_mode, it fetches all posts and yields them in reversed order (oldest first).
    Checks cancellation_event if provided.
    """
    headers = {'User-Agent': 'Mozilla/5.0'} # Basic user agent
    service, user_id, target_post_id = extract_post_info(api_url_input)

    if cancellation_event and cancellation_event.is_set():
        logger("   Download_from_api cancelled at start.")
        return

    if not service or not user_id:
        logger(f"❌ Invalid URL or could not extract service/user: {api_url_input}")
        return # Stop generation if URL is invalid

    if target_post_id and (start_page or end_page):
        logger("⚠️ Page range (start/end page) is ignored when a specific post URL is provided.")
        start_page = end_page = None # Reset page range for single post URL

    is_creator_feed_for_manga = manga_mode and not target_post_id

    parsed_input = urlparse(api_url_input)
    api_domain = parsed_input.netloc
    # Ensure we use a valid API domain, defaulting if necessary
    if not any(d in api_domain.lower() for d in ['kemono.su', 'kemono.party', 'coomer.su', 'coomer.party']):
        logger(f"⚠️ Unrecognized domain '{api_domain}'. Defaulting to kemono.su for API calls.")
        api_domain = "kemono.su" 

    api_base_url = f"https://{api_domain}/api/v1/{service}/user/{user_id}"
    page_size = 50 # API returns 50 posts per page

    if is_creator_feed_for_manga:
        logger("   Manga Mode: Fetching all posts to reverse order (oldest posts processed first)...")
        all_posts_for_manga_mode = []
        current_offset_manga = 0
        while True: # Loop to fetch all pages
            if cancellation_event and cancellation_event.is_set():
                logger("   Manga mode post fetching cancelled.")
                break
            try:
                posts_batch_manga = fetch_posts_paginated(api_base_url, headers, current_offset_manga, logger, cancellation_event)
                if not isinstance(posts_batch_manga, list):
                    logger(f"❌ API Error (Manga Mode): Expected list of posts, got {type(posts_batch_manga)}.")
                    break
                if not posts_batch_manga: # No more posts
                    logger("✅ Reached end of posts (Manga Mode fetch all).")
                    break
                all_posts_for_manga_mode.extend(posts_batch_manga)
                current_offset_manga += len(posts_batch_manga) 
                time.sleep(0.6) 
            except RuntimeError as e:
                if "cancelled by user" in str(e).lower(): # Check if it was our cancellation
                    logger(f"ℹ️ Manga mode pagination stopped due to cancellation: {e}")
                else:
                    logger(f"❌ {e}\n   Aborting manga mode pagination.")
                break
            except Exception as e:
                logger(f"❌ Unexpected error during manga mode fetch: {e}")
                traceback.print_exc()
                break
        
        if cancellation_event and cancellation_event.is_set(): return

        if all_posts_for_manga_mode:
            logger(f"   Manga Mode: Fetched {len(all_posts_for_manga_mode)} total posts. Reversing order...")
            all_posts_for_manga_mode.reverse() 

            for i in range(0, len(all_posts_for_manga_mode), page_size):
                if cancellation_event and cancellation_event.is_set():
                    logger("   Manga mode post yielding cancelled.")
                    break
                yield all_posts_for_manga_mode[i:i + page_size]
        else:
            logger("   Manga Mode: No posts found to process.")
        return 

    current_page_num = 1
    current_offset = 0
    processed_target_post_flag = False 

    if start_page and start_page > 1:
        current_offset = (start_page - 1) * page_size
        current_page_num = start_page
        logger(f"   Starting from page {current_page_num} (calculated offset {current_offset}).")

    while True:
        if cancellation_event and cancellation_event.is_set():
            logger("   Post fetching loop cancelled.")
            break
        if end_page and current_page_num > end_page:
            logger(f"✅ Reached specified end page ({end_page}). Stopping.")
            break
        if target_post_id and processed_target_post_flag: 
            logger(f"✅ Target post {target_post_id} has been processed.")
            break

        try:
            posts_batch = fetch_posts_paginated(api_base_url, headers, current_offset, logger, cancellation_event)
            if not isinstance(posts_batch, list):
                logger(f"❌ API Error: Expected list of posts, got {type(posts_batch)} at page {current_page_num}.")
                break
        except RuntimeError as e:
            if "cancelled by user" in str(e).lower():
                 logger(f"ℹ️ Pagination stopped due to cancellation: {e}")
            else:
                logger(f"❌ {e}\n   Aborting pagination at page {current_page_num}.")
            break
        except Exception as e:
            logger(f"❌ Unexpected error fetching page {current_page_num}: {e}")
            traceback.print_exc()
            break
        
        if not posts_batch: 
            if current_page_num == (start_page or 1) and not target_post_id : 
                logger("😕 No posts found on the first page checked.")
            elif not target_post_id: 
                logger("✅ Reached end of posts (no more content).")
            break 

        if target_post_id: 
            matching_post = next((p for p in posts_batch if str(p.get('id')) == str(target_post_id)), None)
            if matching_post:
                logger(f"🎯 Found target post {target_post_id}.")
                yield [matching_post] 
                processed_target_post_flag = True
            else:
                logger(f"❌ Target post {target_post_id} not found in the batch from offset {current_offset}. This may indicate the post URL is incorrect or the API behavior is unexpected.")
                break 
        else: 
            yield posts_batch

        if not (target_post_id and processed_target_post_flag):
            if not posts_batch : break 
            current_offset += len(posts_batch)
            current_page_num += 1
            time.sleep(0.6) 
        else:
            break 

    if target_post_id and not processed_target_post_flag and not (cancellation_event and cancellation_event.is_set()):
        logger(f"❌ Target post {target_post_id} could not be found after checking relevant pages.")


def get_link_platform(url):
    """Attempts to identify the platform of an external link."""
    try:
        domain = urlparse(url).netloc.lower()
        # Specific known platforms
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
        
        # Generic extraction for other domains
        parts = domain.split('.')
        if len(parts) >= 2:
            # Return the second-to-last part for common structures (e.g., 'google' from google.com)
            # Avoid returning generic TLDs like 'com', 'org', 'net' as the platform
            if parts[-2] not in ['com', 'org', 'net', 'gov', 'edu', 'co'] or len(parts) == 2:
                 return parts[-2] 
            elif len(parts) >= 3: # Handle cases like 'google.co.uk' -> 'google'
                 return parts[-3]
            else: # Fallback to full domain if unsure
                 return domain 
        return 'external' # Default if domain parsing fails
    except Exception: return 'unknown' # Error case


class PostProcessorSignals(QObject):
    """Defines signals used by PostProcessorWorker to communicate with the GUI thread."""
    progress_signal = pyqtSignal(str) 
    file_download_status_signal = pyqtSignal(bool) 
    # MODIFIED: Added link_text argument
    external_link_signal = pyqtSignal(str, str, str, str) # post_title, link_text, link_url, platform
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
                 extract_links_only=False, num_file_threads=4, skip_current_file_flag=None,
                 manga_mode_active=False
                 ):
        self.post = post_data
        self.download_root = download_root
        self.known_names = known_names
        self.filter_character_list = filter_character_list if filter_character_list else []
        self.unwanted_keywords = unwanted_keywords
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
        self.show_external_links = show_external_links
        self.extract_links_only = extract_links_only 
        self.num_file_threads = num_file_threads 

        self.manga_mode_active = manga_mode_active

        if self.compress_images and Image is None:
            self.logger("⚠️ Image compression disabled: Pillow library not found.")
            self.compress_images = False

    def logger(self, message):
        """Emits a log message via the progress_signal if available."""
        if self.signals and hasattr(self.signals, 'progress_signal'):
            self.signals.progress_signal.emit(message)
        else: print(f"(Worker Log - No Signal): {message}") 

    def check_cancel(self):
        """Checks if cancellation has been requested."""
        return self.cancellation_event.is_set()

    def _download_single_file(self, file_info, target_folder_path, headers, original_post_id_for_log, skip_event, post_title="", file_index_in_post=0):
        """Downloads a single file, handles retries, compression, and hash checking."""
        if self.check_cancel() or (skip_event and skip_event.is_set()): return 0, 1 

        file_url = file_info.get('url')
        api_original_filename = file_info.get('_original_name_for_log', file_info.get('name'))

        if not file_url or not api_original_filename:
            self.logger(f"⚠️ Skipping file from post {original_post_id_for_log}: Missing URL or original filename. Info: {str(file_info)[:100]}")
            return 0, 1

        # --- Check skip words on ORIGINAL filename FIRST ---
        if self.skip_words_list:
            name_to_check_lower = api_original_filename.lower() 
            # Simple check if any skip word is a substring
            # For more precise matching (e.g., whole words), adjust this logic
            if any(skip_word.lower() in name_to_check_lower for skip_word in self.skip_words_list):
                 matched_skip = next((sw for sw in self.skip_words_list if sw.lower() in name_to_check_lower), "unknown_skip_word")
                 self.logger(f"   -> Skip File (Keyword on Original Name): '{api_original_filename}' contains '{matched_skip}'.")
                 return 0, 1
        # --- End skip word check ---

        _, original_ext = os.path.splitext(api_original_filename)
        if original_ext and not original_ext.startswith('.'): original_ext = '.' + original_ext 
        elif not original_ext: 
            _, temp_ext = os.path.splitext(clean_filename(api_original_filename))
            if temp_ext and not temp_ext.startswith('.'): original_ext = '.' + temp_ext
            elif temp_ext: original_ext = temp_ext
            else: original_ext = '' 

        filename_to_save = "" 

        if self.manga_mode_active:
            if post_title and post_title.strip(): 
                cleaned_post_title_full = clean_filename(post_title.strip())
                original_filename_base, _ = os.path.splitext(api_original_filename)

                extracted_sequence_from_original = ""
                simple_end_match = re.search(r'(\d+)$', original_filename_base)
                if simple_end_match:
                    extracted_sequence_from_original = simple_end_match.group(1)
                else:
                    complex_match = re.search(r'(?:[ _.\-/]|^)(?:p|page|ch|chapter|ep|episode|v|vol|volume|no|num|number|pt|part)[ _.\-]*(\d+)', original_filename_base, re.IGNORECASE)
                    if complex_match:
                        extracted_sequence_from_original = complex_match.group(1)

                cleaned_title_base = re.sub(
                    r'[|\[\]()]*[ _.\-]*(?:page|p|ch|chapter|ep|episode|v|vol|volume|no|num|number|pt|part)s?[ _.\-]*\d+([ _.\-]+\d+)?$',
                    '',
                    cleaned_post_title_full,
                    flags=re.IGNORECASE
                ).strip()
                if not cleaned_title_base:
                    cleaned_title_base = cleaned_post_title_full
                cleaned_title_base = cleaned_title_base.rstrip(' _.-')


                if extracted_sequence_from_original:
                    filename_to_save = f"{cleaned_title_base} {extracted_sequence_from_original}{original_ext}"
                    self.logger(f"   Manga Mode (Seq from Original): Renaming '{api_original_filename}' to '{filename_to_save}'")
                else:
                    fallback_sequence = str(file_index_in_post + 1) 
                    filename_to_save = f"{cleaned_title_base} {fallback_sequence}{original_ext}"
                    self.logger(f"   Manga Mode (No Seq in Original): Using cleaned title + file index '{fallback_sequence}'. Renaming '{api_original_filename}' to '{filename_to_save}'")
                
                counter = 1
                base_name_coll, ext_coll = os.path.splitext(filename_to_save)
                temp_filename_for_collision_check = filename_to_save
                while os.path.exists(os.path.join(target_folder_path, temp_filename_for_collision_check)):
                    temp_filename_for_collision_check = f"{base_name_coll}_{counter}{ext_coll}"
                    counter += 1
                if temp_filename_for_collision_check != filename_to_save:
                    filename_to_save = temp_filename_for_collision_check
                    self.logger(f"   Manga Mode: Collision detected. Adjusted filename to '{filename_to_save}'")

            else: 
                filename_to_save = clean_filename(api_original_filename)
                self.logger(f"⚠️ Manga mode: Post title missing. Using cleaned original filename '{filename_to_save}'.")
        else: 
            filename_to_save = clean_filename(api_original_filename)

        final_filename_for_sets_and_saving = filename_to_save 

        if not self.download_thumbnails: 
            is_img_type = is_image(api_original_filename)
            is_vid_type = is_video(api_original_filename)
            is_zip_type = is_zip(api_original_filename)
            is_rar_type = is_rar(api_original_filename)
            if self.filter_mode == 'image' and not is_img_type: self.logger(f"   -> Filter Skip: '{api_original_filename}' (Not Image)"); return 0,1
            if self.filter_mode == 'video' and not is_vid_type: self.logger(f"   -> Filter Skip: '{api_original_filename}' (Not Video)"); return 0,1
            if self.skip_zip and is_zip_type: self.logger(f"   -> Pref Skip: '{api_original_filename}' (ZIP)"); return 0,1
            if self.skip_rar and is_rar_type: self.logger(f"   -> Pref Skip: '{api_original_filename}' (RAR)"); return 0,1

        target_folder_basename = os.path.basename(target_folder_path) 
        current_save_path = os.path.join(target_folder_path, final_filename_for_sets_and_saving)

        if os.path.exists(current_save_path) and os.path.getsize(current_save_path) > 0:
             self.logger(f"   -> Exists (Path): '{final_filename_for_sets_and_saving}' in '{target_folder_basename}'.")
             with self.downloaded_files_lock: self.downloaded_files.add(final_filename_for_sets_and_saving) 
             return 0, 1
        
        with self.downloaded_files_lock:
            if final_filename_for_sets_and_saving in self.downloaded_files:
                self.logger(f"   -> Global Skip (Filename): '{final_filename_for_sets_and_saving}' already recorded.")
                return 0, 1

        max_retries = 3; retry_delay = 5; downloaded_size_bytes = 0
        calculated_file_hash = None; file_content_bytes = None; total_size_bytes = 0
        download_successful_flag = False
        log_name_during_dl = f"{api_original_filename} (as {final_filename_for_sets_and_saving})"

        for attempt_num in range(max_retries + 1): 
            if self.check_cancel() or (skip_event and skip_event.is_set()): break
            try:
                if attempt_num > 0: 
                    self.logger(f"   Retrying '{log_name_during_dl}' (Attempt {attempt_num}/{max_retries})...");
                    time.sleep(retry_delay * (2**(attempt_num-1))) 

                if self.signals: self.signals.file_download_status_signal.emit(True) 

                response = requests.get(file_url, headers=headers, timeout=(15, 300), stream=True) 
                response.raise_for_status()
                total_size_bytes = int(response.headers.get('Content-Length', 0))
                file_content_bytes = BytesIO(); downloaded_size_bytes = 0; md5_hasher = hashlib.md5()
                last_progress_time = time.time()

                for chunk in response.iter_content(chunk_size=1 * 1024 * 1024): # 1MB chunks
                    if self.check_cancel() or (skip_event and skip_event.is_set()): break # Check cancellation inside loop
                    if chunk:
                        file_content_bytes.write(chunk); md5_hasher.update(chunk); downloaded_size_bytes += len(chunk)
                        if time.time() - last_progress_time > 1 and total_size_bytes > 0 and self.signals:
                            self.signals.file_progress_signal.emit(log_name_during_dl, downloaded_size_bytes, total_size_bytes)
                            last_progress_time = time.time()
                
                if self.check_cancel() or (skip_event and skip_event.is_set()): break 

                if downloaded_size_bytes > 0: 
                    calculated_file_hash = md5_hasher.hexdigest()
                    download_successful_flag = True
                    break 
                elif total_size_bytes == 0 and response.status_code == 200 : 
                    self.logger(f"   Note: '{log_name_during_dl}' is a 0-byte file according to server.")
                    calculated_file_hash = md5_hasher.hexdigest() 
                    download_successful_flag = True
                    break
            
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, http.client.IncompleteRead) as e:
                self.logger(f"   ❌ Download Error (Retryable): {log_name_during_dl}. Error: {e}")
            except requests.exceptions.RequestException as e: 
                self.logger(f"   ❌ Download Error (Non-Retryable): {log_name_during_dl}. Error: {e}"); break
            except Exception as e: 
                self.logger(f"   ❌ Unexpected Download Error: {log_name_during_dl}: {e}\n{traceback.format_exc(limit=2)}"); break
            finally:
                if self.signals: self.signals.file_download_status_signal.emit(False) 

        if self.signals and total_size_bytes > 0 :
             self.signals.file_progress_signal.emit(log_name_during_dl, downloaded_size_bytes, total_size_bytes)

        if self.check_cancel() or (skip_event and skip_event.is_set()):
            self.logger(f"   ⚠️ Download interrupted for {log_name_during_dl}.")
            if file_content_bytes: file_content_bytes.close()
            return 0, 1

        if not download_successful_flag:
            self.logger(f"❌ Download failed for '{log_name_during_dl}' after {max_retries} retries.")
            if file_content_bytes: file_content_bytes.close()
            return 0, 1

        with self.downloaded_file_hashes_lock:
             if calculated_file_hash in self.downloaded_file_hashes:
                self.logger(f"   -> Content Skip (Hash): '{log_name_during_dl}' (Hash: {calculated_file_hash[:8]}...).")
                with self.downloaded_files_lock: self.downloaded_files.add(final_filename_for_sets_and_saving) 
                if file_content_bytes: file_content_bytes.close()
                return 0, 1

        bytes_to_write = file_content_bytes; bytes_to_write.seek(0) 
        final_filename_after_processing = final_filename_for_sets_and_saving 
        current_save_path_final = current_save_path 

        is_img_for_compress_check = is_image(api_original_filename) 
        if is_img_for_compress_check and self.compress_images and Image and downloaded_size_bytes > (1.5 * 1024 * 1024): 
            self.logger(f"   Compressing '{api_original_filename}' ({downloaded_size_bytes / (1024*1024):.2f} MB)...")
            try:
                with Image.open(bytes_to_write) as img_obj:
                    if img_obj.mode == 'P': img_obj = img_obj.convert('RGBA') 
                    elif img_obj.mode not in ['RGB', 'RGBA', 'L']: img_obj = img_obj.convert('RGB') 
                    
                    compressed_bytes_io = BytesIO()
                    img_obj.save(compressed_bytes_io, format='WebP', quality=80, method=4) 
                    compressed_size = compressed_bytes_io.getbuffer().nbytes

                if compressed_size < downloaded_size_bytes * 0.9: 
                    self.logger(f"   Compression success: {compressed_size / (1024*1024):.2f} MB.")
                    bytes_to_write.close() 
                    bytes_to_write = compressed_bytes_io; bytes_to_write.seek(0) 
                    
                    base_name_orig, _ = os.path.splitext(final_filename_for_sets_and_saving)
                    final_filename_after_processing = base_name_orig + '.webp'
                    current_save_path_final = os.path.join(target_folder_path, final_filename_after_processing)
                    self.logger(f"   Updated filename (compressed): {final_filename_after_processing}")
                else:
                    self.logger(f"   Compression skipped: WebP not significantly smaller."); bytes_to_write.seek(0) 
            except Exception as comp_e:
                self.logger(f"❌ Compression failed for '{api_original_filename}': {comp_e}. Saving original."); bytes_to_write.seek(0) 

        if final_filename_after_processing != final_filename_for_sets_and_saving and \
           os.path.exists(current_save_path_final) and os.path.getsize(current_save_path_final) > 0:
            self.logger(f"   -> Exists (Path - Post-Compress): '{final_filename_after_processing}' in '{target_folder_basename}'.")
            with self.downloaded_files_lock: self.downloaded_files.add(final_filename_after_processing)
            bytes_to_write.close()
            return 0, 1

        try:
            os.makedirs(os.path.dirname(current_save_path_final), exist_ok=True) 
            with open(current_save_path_final, 'wb') as f_out:
                f_out.write(bytes_to_write.getvalue())

            with self.downloaded_file_hashes_lock: self.downloaded_file_hashes.add(calculated_file_hash)
            with self.downloaded_files_lock: self.downloaded_files.add(final_filename_after_processing)

            self.logger(f"✅ Saved: '{final_filename_after_processing}' (from '{api_original_filename}', {downloaded_size_bytes / (1024*1024):.2f} MB) in '{target_folder_basename}'")
            time.sleep(0.05) 
            return 1, 0 
        except Exception as save_err:
             self.logger(f"❌ Save Fail for '{final_filename_after_processing}': {save_err}")
             if os.path.exists(current_save_path_final): 
                  try: os.remove(current_save_path_final); 
                  except OSError: self.logger(f"  -> Failed to remove partially saved file: {current_save_path_final}")
             return 0, 1
        finally:
            if bytes_to_write: bytes_to_write.close() 


    def process(self):
        """Main processing logic for a single post."""
        if self.check_cancel(): return 0, 0 

        total_downloaded_this_post = 0
        total_skipped_this_post = 0
        parsed_api_url = urlparse(self.api_url_input)
        referer_url = f"https://{parsed_api_url.netloc}/" 
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': referer_url}
        
        # Regex to capture URL (group 1) and link text (group 2)
        link_pattern = re.compile(r"""<a\s+ # Start of anchor tag with space
                                      [^>]*? # Any characters except > (non-greedy)
                                      href=["'](https?://[^"']+)["'] # Capture href URL in group 1
                                      [^>]*? # Any characters except > (non-greedy)
                                      >      # Closing > of opening tag
                                      (.*?)  # Capture link text in group 2 (non-greedy)
                                      </a>   # Closing anchor tag
                                   """, re.IGNORECASE | re.VERBOSE | re.DOTALL)

        post_data = self.post 
        post_title = post_data.get('title', '') or 'untitled_post' 
        post_id = post_data.get('id', 'unknown_id')
        post_main_file_info = post_data.get('file') 
        post_attachments = post_data.get('attachments', []) 
        post_content_html = post_data.get('content', '') 

        is_target_post_by_id = (self.target_post_id_from_initial_url is not None) and \
                               (str(post_id) == str(self.target_post_id_from_initial_url))

        self.logger(f"\n--- Processing Post {post_id} ('{post_title[:50]}...') (Thread: {threading.current_thread().name}) ---")

        # --- Skip Check 1: Post Title ---
        if self.skip_words_list:
            title_lower = post_title.lower()
            if any(skip_word.lower() in title_lower for skip_word in self.skip_words_list):
                matched_skip = next((sw for sw in self.skip_words_list if sw.lower() in title_lower), "unknown_skip_word")
                self.logger(f"   -> Skip Post (Title Keyword): Title contains '{matched_skip}'.")
                # Estimate skipped files count (main file + attachments)
                num_potential_files = len(post_attachments) + (1 if post_main_file_info else 0)
                return 0, num_potential_files 

        # --- Skip Check 2: Character Filter (Only if subfolders enabled and not a target post) ---
        if self.filter_character_list and not is_target_post_by_id and self.use_subfolders:
            matched_by_char_filter = any(is_title_match_for_character(post_title, char_filter) for char_filter in self.filter_character_list)
            if not matched_by_char_filter:
                self.logger(f"   -> Filter Skip Post: Title ('{post_title[:50]}...') doesn't match character filters.")
                num_potential_files = len(post_attachments) + (1 if post_main_file_info else 0)
                return 0, num_potential_files 

        if not isinstance(post_attachments, list): 
            self.logger(f"⚠️ Corrupt attachment data for post {post_id} (expected list, got {type(post_attachments)}). Skipping attachments.")
            post_attachments = []

        # --- Determine Potential Save Folders ---
        base_save_folders = []
        if self.use_subfolders:
            if is_target_post_by_id and self.custom_folder_name: 
                base_save_folders = [self.custom_folder_name]
                self.logger(f"   Folder: Using custom folder for target post: '{self.custom_folder_name}'")
            elif self.filter_character_list: 
                matched_chars = [clean_folder_name(cf.lower()) for cf in self.filter_character_list if is_title_match_for_character(post_title, cf)]
                if matched_chars:
                    base_save_folders = matched_chars
                    self.logger(f"   Folder: Matched character filter(s): {', '.join(base_save_folders)}")
                else: 
                    # If character filter is active but no match, we already skipped the post above
                    # If no character filter, derive from title/known names
                    matched_from_title = match_folders_from_title(post_title, self.known_names, self.unwanted_keywords)
                    base_save_folders = matched_from_title if matched_from_title else [extract_folder_name_from_title(post_title, self.unwanted_keywords)]
                    self.logger(f"   Folder: No character filter match. Using derived: {', '.join(base_save_folders)}")
            else: # No character filter active
                matched_from_title = match_folders_from_title(post_title, self.known_names, self.unwanted_keywords)
                base_save_folders = matched_from_title if matched_from_title else [extract_folder_name_from_title(post_title, self.unwanted_keywords)]
                self.logger(f"   Folder: Using derived: {', '.join(base_save_folders)}")
        else: # Subfolders disabled
            base_save_folders = [""] 
            self.logger("   Folder: Subfolders disabled. Using root download directory.")

        if not base_save_folders: # Fallback if somehow no folders were determined
            base_save_folders = [clean_folder_name(post_title) or 'untitled_post_fallback']

        # --- Skip Check 3: Potential Folder Name(s) ---
        if self.skip_words_list and self.use_subfolders: # Only check folder names if subfolders are used
            skip_post_due_to_folder = False
            for folder_name in base_save_folders:
                if not folder_name: continue # Skip check for root folder ""
                folder_name_lower = folder_name.lower()
                if any(skip_word.lower() in folder_name_lower for skip_word in self.skip_words_list):
                    matched_skip = next((sw for sw in self.skip_words_list if sw.lower() in folder_name_lower), "unknown_skip_word")
                    self.logger(f"   -> Skip Post (Folder Keyword): Potential folder '{folder_name}' contains '{matched_skip}'.")
                    skip_post_due_to_folder = True
                    break # No need to check other folders for this post
            if skip_post_due_to_folder:
                num_potential_files = len(post_attachments) + (1 if post_main_file_info else 0)
                return 0, num_potential_files
        # --- End Folder Skip Check ---

        # --- External Link Processing (Can happen even if files are skipped later) ---
        if (self.show_external_links or self.extract_links_only) and post_content_html:
            try:
                found_links_with_text = link_pattern.findall(post_content_html)
                if found_links_with_text:
                    unique_links_data = {} 
                    for link_url, raw_link_text in found_links_with_text:
                        link_url = link_url.strip()
                        clean_link_text = re.sub(r'<.*?>', '', raw_link_text) 
                        clean_link_text = html.unescape(clean_link_text) 
                        clean_link_text = clean_link_text.strip()
                        if not any(ext in link_url.lower() for ext in ['.css', '.js', '.ico', '.xml', '.svg']) \
                           and not link_url.startswith('javascript:'):
                            if link_url not in unique_links_data and clean_link_text:
                                unique_links_data[link_url] = clean_link_text
                            elif link_url not in unique_links_data: 
                                unique_links_data[link_url] = "[Link]" 
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
        # --- End External Link Processing ---

        if self.extract_links_only: 
            self.logger(f"   Extract Links Only mode: Skipping file download for post {post_id}.")
            return 0, 0 

        # --- Determine Final Save Paths (after folder name skip check passed) ---
        final_save_paths_for_post = []
        for base_folder_name in base_save_folders:
            current_path = os.path.join(self.download_root, base_folder_name)
            if self.use_post_subfolders and self.use_subfolders: 
                cleaned_title_for_subfolder = clean_folder_name(post_title)
                post_specific_subfolder = f"{post_id}_{cleaned_title_for_subfolder}" if cleaned_title_for_subfolder else f"{post_id}_untitled"
                final_save_paths_for_post.append(os.path.join(current_path, post_specific_subfolder))
            else:
                final_save_paths_for_post.append(current_path)
        
        if not final_save_paths_for_post: 
             # This case should be less likely now with the earlier folder determination, but keep as fallback
             self.logger(f"   CRITICAL ERROR: No valid folder paths determined for post {post_id}. Skipping."); return 0, 1

        # --- Prepare File List ---
        files_to_download_info_list = []
        api_file_domain = parsed_api_url.netloc 

        if self.download_thumbnails:
            self.logger(f"   Thumbnail-only mode for Post {post_id}. (Functionality depends on API providing clear thumbnail links).")
            # Logic to find thumbnail links would go here
            if not files_to_download_info_list: 
                self.logger(f"   -> No specific thumbnail links found for post {post_id} in thumbnail-only mode.")
                return 0, 0 
        else: 
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

        # --- Download Files (Skip Check 4: Original Filename happens inside _download_single_file) ---
        with ThreadPoolExecutor(max_workers=self.num_file_threads, thread_name_prefix=f'P{post_id}File_') as file_pool:
            futures_list = []
            for idx, file_info_to_dl in enumerate(files_to_download_info_list):
                if self.check_cancel(): break
                for save_location_path in final_save_paths_for_post: 
                    if self.check_cancel(): break
                    futures_list.append(file_pool.submit(
                        self._download_single_file,
                        file_info_to_dl,
                        save_location_path,
                        headers,
                        post_id, 
                        self.skip_current_file_flag, 
                        post_title,
                        file_index_in_post=idx 
                    ))
            
            for future in as_completed(futures_list): 
                if self.check_cancel(): break 
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

        if self.check_cancel(): self.logger(f"   Post {post_id} processing cancelled.");
        else: self.logger(f"   Post {post_id} Summary: Downloaded={total_downloaded_this_post}, Skipped Files={total_skipped_this_post}")

        return total_downloaded_this_post, total_skipped_this_post


class DownloadThread(QThread):
    """Manages the overall download process (primarily for single-threaded GUI mode)."""
    progress_signal = pyqtSignal(str)
    add_character_prompt_signal = pyqtSignal(str) 
    file_download_status_signal = pyqtSignal(bool) 
    finished_signal = pyqtSignal(int, int, bool) 
    # MODIFIED: Added link_text argument
    external_link_signal = pyqtSignal(str, str, str, str) # post_title, link_text, link_url, platform
    file_progress_signal = pyqtSignal(str, int, int) 

    def __init__(self, api_url_input, output_dir, known_names_copy,
                 cancellation_event,
                 filter_character_list=None,
                 filter_mode='all', skip_zip=True, skip_rar=True,
                 use_subfolders=True, use_post_subfolders=False, custom_folder_name=None, compress_images=False,
                 download_thumbnails=False, service=None, user_id=None,
                 downloaded_files=None, downloaded_file_hashes=None, downloaded_files_lock=None, downloaded_file_hashes_lock=None,
                 skip_words_list=None,
                 show_external_links=False,
                 num_file_threads_for_worker=1, 
                 skip_current_file_flag=None, start_page=None, end_page=None,
                 target_post_id_from_initial_url=None,
                 manga_mode_active=False,
                 unwanted_keywords=None
                 ):
        super().__init__()
        self.api_url_input = api_url_input
        self.output_dir = output_dir
        self.known_names = list(known_names_copy) 
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
        
        self.downloaded_files = downloaded_files if downloaded_files is not None else set()
        self.downloaded_files_lock = downloaded_files_lock if downloaded_files_lock is not None else threading.Lock()
        self.downloaded_file_hashes = downloaded_file_hashes if downloaded_file_hashes is not None else set()
        self.downloaded_file_hashes_lock = downloaded_file_hashes_lock if downloaded_file_hashes_lock is not None else threading.Lock()

        self._add_character_response = None 
        self.prompt_mutex = QMutex() 

        self.show_external_links = show_external_links
        self.num_file_threads_for_worker = num_file_threads_for_worker

        self.start_page = start_page
        self.end_page = end_page

        self.manga_mode_active = manga_mode_active
        self.unwanted_keywords = unwanted_keywords if unwanted_keywords is not None else {'spicy', 'hd', 'nsfw', '4k', 'preview', 'teaser', 'clip'}


        if self.compress_images and Image is None: 
            self.logger("⚠️ Image compression disabled: Pillow library not found (DownloadThread).")
            self.compress_images = False

    def logger(self, message):
        """Emits a log message via the progress_signal."""
        self.progress_signal.emit(str(message))

    def isInterruptionRequested(self):
        """Overrides QThread's interruption check to also use the cancellation_event."""
        return super().isInterruptionRequested() or self.cancellation_event.is_set()

    def skip_file(self):
        """Sets the skip_current_file_flag to skip the currently downloading file."""
        if self.isRunning() and self.skip_current_file_flag:
             self.logger("⏭️ Skip requested for current file (single-thread mode).")
             self.skip_current_file_flag.set()
        else: self.logger("ℹ️ Skip file: No download active or flag not set.")

    def run(self):
        """Main execution loop for the download thread."""
        grand_total_downloaded_files = 0
        grand_total_skipped_files = 0
        was_process_cancelled = False

        worker_signals_obj = PostProcessorSignals()
        try:
            worker_signals_obj.progress_signal.connect(self.progress_signal)
            worker_signals_obj.file_download_status_signal.connect(self.file_download_status_signal)
            worker_signals_obj.file_progress_signal.connect(self.file_progress_signal)
            # Connect the worker's external_link_signal to this thread's external_link_signal
            # This ensures links found by the worker (even in single-thread mode) are emitted by this thread
            worker_signals_obj.external_link_signal.connect(self.external_link_signal)


            self.logger("   Starting post fetch (single-threaded download process)...")
            post_generator = download_from_api(
                self.api_url_input,
                logger=self.logger, 
                start_page=self.start_page,
                end_page=self.end_page,
                manga_mode=self.manga_mode_active,
                cancellation_event=self.cancellation_event # Pass cancellation event
            )

            for posts_batch_data in post_generator: 
                if self.isInterruptionRequested(): was_process_cancelled = True; break
                for individual_post_data in posts_batch_data: 
                    if self.isInterruptionRequested(): was_process_cancelled = True; break

                    post_processing_worker = PostProcessorWorker(
                         post_data=individual_post_data,
                         download_root=self.output_dir,
                         known_names=self.known_names,
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
                         signals=worker_signals_obj, # Pass the connected signals object
                         downloaded_files=self.downloaded_files, downloaded_file_hashes=self.downloaded_file_hashes,
                         downloaded_files_lock=self.downloaded_files_lock, downloaded_file_hashes_lock=self.downloaded_file_hashes_lock,
                         skip_words_list=self.skip_words_list,
                         show_external_links=self.show_external_links,
                         extract_links_only=False, 
                         num_file_threads=self.num_file_threads_for_worker,
                         skip_current_file_flag=self.skip_current_file_flag,
                         manga_mode_active=self.manga_mode_active
                    )
                    try:
                        dl_count, skip_count = post_processing_worker.process()
                        grand_total_downloaded_files += dl_count
                        grand_total_skipped_files += skip_count
                    except Exception as proc_err:
                         post_id_for_err = individual_post_data.get('id', 'N/A')
                         self.logger(f"❌ Error processing post {post_id_for_err} in DownloadThread: {proc_err}")
                         traceback.print_exc()
                         grand_total_skipped_files += len(individual_post_data.get('attachments', [])) + (1 if individual_post_data.get('file') else 0)

                    if self.skip_current_file_flag and self.skip_current_file_flag.is_set():
                        self.skip_current_file_flag.clear() 
                        self.logger("   Skip current file flag was processed and cleared.")
                    
                    self.msleep(10) 
                if was_process_cancelled: break 

            if not was_process_cancelled: self.logger("✅ All posts processed or end of content reached.")

        except Exception as main_thread_err:
            self.logger(f"\n❌ Critical error within DownloadThread run loop: {main_thread_err}")
            traceback.print_exc()
            if not self.isInterruptionRequested(): was_process_cancelled = False 
        finally:
            try:
                if worker_signals_obj:
                    # Disconnect signals
                    worker_signals_obj.progress_signal.disconnect(self.progress_signal)
                    worker_signals_obj.file_download_status_signal.disconnect(self.file_download_status_signal)
                    worker_signals_obj.external_link_signal.disconnect(self.external_link_signal)
                    worker_signals_obj.file_progress_signal.disconnect(self.file_progress_signal)
            except (TypeError, RuntimeError) as e: self.logger(f"ℹ️ Note during signal disconnection: {e}")

            self.finished_signal.emit(grand_total_downloaded_files, grand_total_skipped_files, was_process_cancelled)

    def receive_add_character_result(self, result):
        """Handles the response from a character add prompt (if GUI signals back to this thread)."""
        with QMutexLocker(self.prompt_mutex):
             self._add_character_response = result
        self.logger(f"   (DownloadThread) Received character prompt response: {'Yes' if result else 'No'}")

