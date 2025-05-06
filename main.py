import sys
import os
import time
import requests
import re
import threading
import queue
import hashlib  # Import hashlib for hashing
from concurrent.futures import ThreadPoolExecutor, Future, CancelledError

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QListWidget,
    QRadioButton, QButtonGroup, QCheckBox, QMainWindow
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMutex, QMutexLocker, QObject
from urllib.parse import urlparse
try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow library not found. Please install it: pip install Pillow")
    Image = None # Set to None to handle gracefully later

from PyQt5.QtGui import QIcon

app = QApplication(sys.argv)
app.setWindowIcon(QIcon("Kemono.ico"))  # Taskbar + window icon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")

from io import BytesIO
fastapi_app = None # Set to None directly


KNOWN_NAMES = []

def clean_folder_name(name):
    """Removes invalid characters for folder names and replaces spaces with underscores."""
    if not isinstance(name, str): name = str(name) # Ensure input is string
    cleaned = re.sub(r'[^\w\s\-\_]', '', name)
    return cleaned.strip().replace(' ', '_')

def clean_filename(name):
     """Removes invalid characters for filenames and replaces spaces with underscores."""
     if not isinstance(name, str): name = str(name) # Ensure input is string
     cleaned = re.sub(r'[^\w\s\-\_\.]', '', name)
     return cleaned.strip().replace(' ', '_')


def extract_folder_name_from_title(title, unwanted_keywords):
    """
    Tries to find a suitable folder name from the title's first valid token.
    Falls back to 'Uncategorized' if no suitable name is found.
    """
    if not title: return 'Uncategorized'
    title_lower = title.lower()
    tokens = title_lower.split()
    for token in tokens:
        clean_token = clean_folder_name(token)
        if clean_token and clean_token not in unwanted_keywords:
            return clean_token
    return 'Uncategorized' # Fallback if no suitable token found


def match_folders_from_title(title, known_names, unwanted_keywords):
    """
    Matches known names (phrases/keywords) within the cleaned title.
    Returns a list of *cleaned* known names found.
    """
    if not title: return []
    cleaned_title = clean_folder_name(title.lower())
    matched_cleaned_names = set()

    for name in known_names:
        cleaned_name_for_match = clean_folder_name(name.lower())
        if not cleaned_name_for_match: continue # Skip empty known names
        if cleaned_name_for_match in cleaned_title:
            if cleaned_name_for_match not in unwanted_keywords:
                 matched_cleaned_names.add(cleaned_name_for_match)

    return list(matched_cleaned_names)


def is_image(filename):
    if not filename: return False
    return filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')) # Added gif

def is_video(filename):
    if not filename: return False
    return filename.lower().endswith(('.mp4', '.mov', '.mkv', '.webm', '.avi', '.wmv'))

def is_zip(filename):
    if not filename: return False
    return filename.lower().endswith('.zip')

def is_rar(filename):
    if not filename: return False
    return filename.lower().endswith('.rar')


def is_post_url(url):
    if not isinstance(url, str): return False
    return '/post/' in urlparse(url).path

def extract_post_info(url_string):
    """
    Extracts service, user_id, and post_id from Kemono/Coomer URLs.
    Returns (service, user_id, post_id) or (None, None, None).
    """
    service, user_id, post_id = None, None, None
    if not isinstance(url_string, str) or not url_string.strip():
        return None, None, None

    try:
        parsed_url = urlparse(url_string.strip())
        domain = parsed_url.netloc.lower()
        path_parts = [part for part in parsed_url.path.strip('/').split('/') if part]
        is_kemono = 'kemono.su' in domain or 'kemono.party' in domain # Added kemono.party
        is_coomer = 'coomer.su' in domain or 'coomer.party' in domain # Added coomer.party
        if not (is_kemono or is_coomer):
            return None, None, None # Unknown domain
        if len(path_parts) >= 3 and path_parts[1].lower() == 'user':
            service = path_parts[0]
            user_id = path_parts[2]
            if len(path_parts) >= 5 and path_parts[3].lower() == 'post':
                post_id = path_parts[4]
            return service, user_id, post_id
        if len(path_parts) >= 5 and path_parts[0].lower() == 'api' and path_parts[1].lower() == 'v1' and path_parts[3].lower() == 'user':
            service = path_parts[2]
            user_id = path_parts[4]
            if len(path_parts) >= 7 and path_parts[5].lower() == 'post':
                 post_id = path_parts[6]
            return service, user_id, post_id

    except ValueError: # Handle potential errors during URL parsing
        print(f"Debug: ValueError parsing URL '{url_string}'")
        return None, None, None
    except Exception as e: # Catch other unexpected errors
        print(f"Debug: Exception during extract_post_info for URL '{url_string}': {e}")
        return None, None, None
    return None, None, None


def fetch_posts_paginated(api_url_base, headers, offset, logger):
    """Fetches a single page of posts from the creator API."""
    paginated_url = f'{api_url_base}?o={offset}'
    logger(f"   Fetching: {paginated_url}")
    try:
        response = requests.get(paginated_url, headers=headers, timeout=45) # Increased timeout
        response.raise_for_status() # Check for 4xx/5xx errors
        if 'application/json' not in response.headers.get('Content-Type', ''):
            raise RuntimeError(f"Unexpected content type received: {response.headers.get('Content-Type')}. Body: {response.text[:200]}")
        return response.json()
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Timeout fetching page offset {offset}")
    except requests.exceptions.RequestException as e:
        err_msg = f"Error fetching page offset {offset}: {e}"
        if e.response is not None:
            err_msg += f" (Status: {e.response.status_code}, Body: {e.response.text[:200]})"
        raise RuntimeError(err_msg)
    except ValueError as e: # JSONDecodeError inherits from ValueError
        raise RuntimeError(f"Error decoding JSON response for offset {offset}: {e}. Body: {response.text[:200]}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error processing page offset {offset}: {e}")


def download_from_api(api_url_input, logger=print):
    """
    Generator function yielding batches of posts from the API.
    Handles pagination and single post fetching.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    service, user_id, target_post_id = extract_post_info(api_url_input)

    if not service or not user_id:
        logger(f"❌ Invalid or unrecognized URL: {api_url_input}. Cannot fetch.")
        return # Stop generator

    parsed_input = urlparse(api_url_input)
    api_domain = parsed_input.netloc if ('kemono.su' in parsed_input.netloc.lower() or 'coomer.su' in parsed_input.netloc.lower() or 'kemono.party' in parsed_input.netloc.lower() or 'coomer.party' in parsed_input.netloc.lower()) else "kemono.su" # Added .party domains
    api_base_url = f"https://{api_domain}/api/v1/{service}/user/{user_id}"

    offset = 0
    page = 1
    processed_target_post = False # Flag to stop if target is found

    while True:
        if target_post_id and processed_target_post:
            logger(f"✅ Target post {target_post_id} found and processed. Stopping.")
            break

        logger(f"\n🔄 Fetching page {page} (offset {offset}) for user {user_id} on {api_domain}...")
        try:
            posts_batch = fetch_posts_paginated(api_base_url, headers, offset, logger)
            if not isinstance(posts_batch, list):
                 logger(f"❌ API Error: Expected a list of posts, got {type(posts_batch)}. Response: {str(posts_batch)[:200]}")
                 break # Stop if response format is wrong
        except RuntimeError as e:
            logger(f"❌ {e}")
            logger("   Aborting pagination due to error.")
            break
        except Exception as e:
             logger(f"❌ Unexpected error during fetch loop: {e}")
             break

        if not posts_batch: # Empty list means end of posts
            if page == 1 and not target_post_id:
                 logger("😕 No posts found for this creator.")
            elif not target_post_id:
                 logger("✅ Reached end of posts.")
            break # Stop pagination

        logger(f"📦 Found {len(posts_batch)} posts on page {page}.")

        if target_post_id:
            matching_post = next((post for post in posts_batch if str(post.get('id')) == str(target_post_id)), None)

            if matching_post:
                logger(f"🎯 Found target post {target_post_id} on page {page}.")
                yield [matching_post] # Yield only the target post
                processed_target_post = True # Set flag to stop after this
            else:
                logger(f"   Target post {target_post_id} not found on this page.")
                pass
        else:
            yield posts_batch
        if not (target_post_id and processed_target_post):
            page_size = 50
            offset += page_size
            page += 1
            time.sleep(0.6) # Slightly increased delay between page fetches
    if target_post_id and not processed_target_post:
        logger(f"❌ Target post ID {target_post_id} was not found for this creator.")
class PostProcessorSignals(QObject):
    """Defines signals emitted by worker threads."""
    progress_signal = pyqtSignal(str)
    file_download_status_signal = pyqtSignal(bool) # True=start, False=end

class PostProcessorWorker:
    """Processes a single post within a ThreadPoolExecutor."""
    def __init__(self, post_data, download_root, known_names, filter_character,
                 unwanted_keywords, filter_mode, skip_zip, skip_rar,
                 use_subfolders, target_post_id_from_initial_url, custom_folder_name,
                 compress_images, download_thumbnails, service, user_id,
                 api_url_input, cancellation_event, signals,
                 downloaded_files, downloaded_file_hashes, downloaded_files_lock, downloaded_file_hashes_lock,
                 skip_words_list=None): # ADDED skip_words_list
        self.post = post_data
        self.download_root = download_root
        self.known_names = known_names
        self.filter_character = filter_character
        self.unwanted_keywords = unwanted_keywords
        self.filter_mode = filter_mode
        self.skip_zip = skip_zip
        self.skip_rar = skip_rar
        self.use_subfolders = use_subfolders
        self.target_post_id_from_initial_url = target_post_id_from_initial_url
        self.custom_folder_name = custom_folder_name
        self.compress_images = compress_images
        self.download_thumbnails = download_thumbnails
        self.service = service
        self.user_id = user_id
        self.api_url_input = api_url_input # Needed for domain/URL construction
        self.cancellation_event = cancellation_event # Shared threading.Event
        self.signals = signals # Shared PostProcessorSignals instance
        self.skip_current_file_flag = threading.Event() # Event for skipping
        self.is_downloading_file = False
        self.current_download_path = None
        self.downloaded_files = downloaded_files # Shared set (filenames)
        self.downloaded_file_hashes = downloaded_file_hashes # Shared set (hashes) # ADDED
        self.downloaded_files_lock = downloaded_files_lock # Use passed lock
        self.downloaded_file_hashes_lock = downloaded_file_hashes_lock # Use passed lock # ADDED
        self.skip_words_list = skip_words_list if skip_words_list is not None else [] # ADDED
        if self.compress_images and Image is None:
            self.logger("⚠️ Image compression enabled, but Pillow library is not loaded. Disabling compression.")
            self.compress_images = False

    def logger(self, message):
        """Emit progress messages safely via signals."""
        if self.signals and hasattr(self.signals, 'progress_signal'):
            self.signals.progress_signal.emit(message)
        else:
            print(f"(Worker Log): {message}") # Fallback

    def check_cancel(self):
        """Checks the shared cancellation event."""
        is_cancelled = self.cancellation_event.is_set()
        return is_cancelled

    def skip_file(self):
        """Sets the skip flag (not typically called directly on worker)."""
        pass

    def process(self):
        """Processes the single post assigned to this worker. Returns (downloaded, skipped)."""
        if self.check_cancel(): return 0, 0

        total_downloaded_post = 0
        total_skipped_post = 0
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': f'https://{urlparse(self.api_url_input).netloc}/'}
        url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
        LARGE_THUMBNAIL_THRESHOLD = 1 * 1024 * 1024 # 1MB

        post = self.post
        api_title = post.get('title', '') # Default to empty string
        title = api_title if api_title else 'untitled_post'
        post_id = post.get('id', 'unknown_id')
        post_file_info = post.get('file')
        attachments = post.get('attachments', [])
        post_content = post.get('content', '')
        is_target_post = (self.target_post_id_from_initial_url is not None) and (str(post_id) == str(self.target_post_id_from_initial_url))

        self.logger(f"\n--- Processing Post {post_id} ('{title[:50]}...') (Thread: {threading.current_thread().name}) ---")
        if self.skip_words_list:
            title_lower = title.lower()
            for skip_word in self.skip_words_list:
                if skip_word.lower() in title_lower:
                    self.logger(f"   -> Skip Post (Title): Post {post_id} title ('{title[:30]}...') contains skip word '{skip_word}'. Skipping entire post.")
                    return 0, 1 # 0 downloaded, 1 skipped (the whole post)


        if not isinstance(attachments, list):
            self.logger(f"⚠️ Corrupt attachment data for post {post_id}. Skipping attachments.")
            attachments = []
        valid_folder_paths = []
        folder_decision_reason = ""
        api_domain = urlparse(self.api_url_input).netloc if ('kemono.su' in urlparse(self.api_url_input).netloc.lower() or 'coomer.su' in urlparse(self.api_url_input).netloc.lower() or 'kemono.party' in urlparse(self.api_url_input).netloc.lower() or 'coomer.party' in urlparse(self.api_url_input).netloc.lower()) else "kemono.su"
        if is_target_post and self.custom_folder_name and self.use_subfolders:
             folder_path_full = os.path.join(self.download_root, self.custom_folder_name)
             valid_folder_paths = [folder_path_full]
             folder_decision_reason = f"Using custom folder for target post: '{self.custom_folder_name}'"
        if not valid_folder_paths and self.use_subfolders:
            folder_names_for_post = [] # Cleaned folder names derived for this post
            if self.filter_character:
                clean_char_filter = clean_folder_name(self.filter_character.lower())
                matched_names_in_title = match_folders_from_title(title, self.known_names, self.unwanted_keywords)

                if clean_char_filter and clean_char_filter in matched_names_in_title:
                    folder_names_for_post = [clean_char_filter]
                    folder_decision_reason = f"Character filter '{self.filter_character}' matched title. Using folder '{clean_char_filter}'."
                else:
                    self.logger(f"   -> Filter Skip Post {post_id}: Character filter '{self.filter_character}' not found in title matches ({matched_names_in_title}).")
                    return 0, 1 # 0 downloaded, 1 skipped (the whole post)
            else:
                matched_folders = match_folders_from_title(title, self.known_names, self.unwanted_keywords)
                if matched_folders:
                    folder_names_for_post = matched_folders # Use all matched known names as folders
                    folder_decision_reason = f"Found known name(s) in title: {matched_folders}"
                else:
                    extracted_folder = extract_folder_name_from_title(title, self.unwanted_keywords)
                    folder_names_for_post = [extracted_folder]
                    folder_decision_reason = f"No known names in title. Using derived folder: '{extracted_folder}'"
            for folder_name in folder_names_for_post:
                folder_path_full = os.path.join(self.download_root, folder_name)
                valid_folder_paths.append(folder_path_full)
        if not valid_folder_paths:
            valid_folder_paths = [self.download_root] # Save directly to root
            if not folder_decision_reason: # Add reason if not already set
                folder_decision_reason = "Subfolders disabled or no specific folder determined. Using root download directory."


        self.logger(f"   Folder Decision: {folder_decision_reason}")
        if not valid_folder_paths:
             self.logger(f"   ERROR: No valid folder paths determined for post {post_id}. Skipping.")
             return 0, 1 # Skip post
        if post_content:
            try:
                found_links = re.findall(r'href=["\'](https?://[^"\']+)["\']', post_content)
                if found_links:
                    self.logger(f"🔗 Links found in post content:")
                    unique_links = sorted(list(set(found_links))) # Remove duplicates
                    for link in unique_links[:10]: # Log max 10 links
                        if not any(x in link for x in ['.css', '.js', 'javascript:']):
                             self.logger(f"   - {link}")
                    if len(unique_links) > 10:
                        self.logger(f"   - ... ({len(unique_links) - 10} more links not shown)")
            except Exception as e:
                 self.logger(f"⚠️ Error parsing content for links in post {post_id}: {e}")
        files_to_process_for_download = []
        api_domain = urlparse(self.api_url_input).netloc if ('kemono.su' in urlparse(self.api_url_input).netloc.lower() or 'coomer.su' in urlparse(self.api_url_input).netloc.lower() or 'kemono.party' in urlparse(self.api_url_input).netloc.lower() or 'coomer.party' in urlparse(self.api_url_input).netloc.lower()) else "kemono.su"

        if self.download_thumbnails:
            self.logger(f"   Mode: Attempting to download thumbnail...") # Modified log
            self.logger("      Thumbnail download via API is disabled as the local API is not used.")
            self.logger(f"   -> Skipping Post {post_id}: Thumbnail download requested but API is disabled.")
            return 0, 1 # 0 downloaded, 1 skipped post

        else: # Normal file download mode
            self.logger(f"   Mode: Downloading post file/attachments.")
            if post_file_info and isinstance(post_file_info, dict) and post_file_info.get('path'):
                main_file_path = post_file_info['path'].lstrip('/')
                main_file_name = post_file_info.get('name') or os.path.basename(main_file_path)
                if main_file_name:
                     file_url = f"https://{api_domain}/data/{main_file_path}"
                     files_to_process_for_download.append({
                         'url': file_url, 'name': main_file_name,
                         '_is_thumbnail': False, '_source': 'post_file'
                     })
                else:
                     self.logger(f"   ⚠️ Skipping main post file: Missing filename (Path: {main_file_path})")
            attachment_counter = 0
            for idx, attachment in enumerate(attachments):
                if isinstance(attachment, dict) and attachment.get('path'):
                    attach_path = attachment['path'].lstrip('/')
                    attach_name = attachment.get('name') or os.path.basename(attach_path)
                    if attach_name:
                         base, ext = os.path.splitext(clean_filename(attach_name))
                         final_attach_name = f"{post_id}_{attachment_counter}{ext}"
                         if base and base != f"{post_id}_{attachment_counter}": # Avoid doubling if base is already post_id_index
                             final_attach_name = f"{post_id}_{attachment_counter}_{base}{ext}"


                         attach_url = f"https://{api_domain}/data/{attach_path}"
                         files_to_process_for_download.append({
                             'url': attach_url, 'name': final_attach_name, # Use the unique name here
                             '_is_thumbnail': False, '_source': f'attachment_{idx+1}',
                             '_original_name_for_log': attach_name # Keep original for logging
                         })
                         attachment_counter += 1 # Increment counter

                    else:
                          self.logger(f"   ⚠️ Skipping attachment {idx+1}: Missing filename (Path: {attach_path})")
                else:
                     self.logger(f"   ⚠️ Skipping invalid attachment entry {idx+1}: {str(attachment)[:100]}")


        if not files_to_process_for_download:
            self.logger(f"   No files found to download for post {post_id}.")
            return 0, 0 # No files, no action needed, not skipped post

        self.logger(f"   Files identified for download: {len(files_to_process_for_download)}")
        post_download_count = 0
        post_skip_count = 0 # Files skipped within this post
        local_processed_filenames = set()
        local_filenames_lock = threading.Lock()


        for file_info in files_to_process_for_download:
            if self.check_cancel(): break # Check cancellation before each file
            if self.skip_current_file_flag.is_set():
                original_name_for_log = file_info.get('_original_name_for_log', file_info.get('name', 'unknown_file'))
                self.logger(f"⏭️ File skip requested: {original_name_for_log}")
                post_skip_count += 1
                self.skip_current_file_flag.clear() # Reset flag
                continue

            file_url = file_info.get('url')
            original_filename = file_info.get('name') # This is the constructed unique name if applicable
            is_thumbnail = file_info.get('_is_thumbnail', False)
            original_name_for_log = file_info.get('_original_name_for_log', original_filename) # Use original for log if available

            if not file_url or not original_filename:
                 self.logger(f"⚠️ Skipping file entry due to missing URL or name: {str(file_info)[:100]}")
                 post_skip_count += 1
                 continue

            cleaned_save_filename = clean_filename(original_filename) # Clean the potentially unique name
            if self.skip_words_list:
                filename_lower = cleaned_save_filename.lower()
                file_skipped_by_word = False
                for skip_word in self.skip_words_list:
                    if skip_word.lower() in filename_lower:
                        self.logger(f"   -> Skip File (Filename): File '{original_name_for_log}' contains skip word '{skip_word}'.")
                        post_skip_count += 1
                        file_skipped_by_word = True
                        break
                if file_skipped_by_word:
                    continue # Skip to next file in the post
            if not self.download_thumbnails: # This condition will always be true now
                file_skipped_by_filter = False
                is_img = is_image(cleaned_save_filename)
                is_vid = is_video(cleaned_save_filename) # Using updated is_video
                is_zip_file = is_zip(cleaned_save_filename)
                is_rar_file = is_rar(cleaned_save_filename)

                if self.filter_mode == 'image' and not is_img:
                    self.logger(f"   -> Filter Skip: '{original_name_for_log}' (Not image/gif)")
                    file_skipped_by_filter = True
                elif self.filter_mode == 'video' and not is_vid:
                    self.logger(f"   -> Filter Skip: '{original_name_for_log}' (Not video)")
                    file_skipped_by_filter = True
                elif self.skip_zip and is_zip_file:
                    self.logger(f"   -> Pref Skip: '{original_name_for_log}' (Zip)")
                    file_skipped_by_filter = True
                elif self.skip_rar and is_rar_file:
                    self.logger(f"   -> Pref Skip: '{original_name_for_log}' (RAR)")
                    file_skipped_by_filter = True

                if file_skipped_by_filter:
                    post_skip_count += 1
                    continue # Skip to next file
            file_downloaded_or_exists = False
            for folder_path in valid_folder_paths:
                if self.check_cancel(): break # Check cancellation before each folder attempt
                try:
                    os.makedirs(folder_path, exist_ok=True)
                except OSError as e:
                    self.logger(f"❌ Error ensuring directory exists {folder_path}: {e}. Skipping path.")
                    continue # Try next folder path if available
                except Exception as e:
                    self.logger(f"❌ Unexpected error creating dir {folder_path}: {e}. Skipping path.")
                    continue

                save_path = os.path.join(folder_path, cleaned_save_filename)
                folder_basename = os.path.basename(folder_path) # For logging
                with local_filenames_lock: # Use local lock for filename set within post
                    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                         self.logger(f"   -> Exists Skip: '{original_name_for_log}' in '{folder_basename}'")
                         post_skip_count += 1 # Count exists as skipped for this post's summary
                         file_downloaded_or_exists = True
                         with self.downloaded_files_lock:
                             self.downloaded_files.add(cleaned_save_filename)
                         break # Don't try other folders if it exists in one valid location
                    elif cleaned_save_filename in local_processed_filenames:
                         self.logger(f"   -> Local Skip: '{original_name_for_log}' in '{folder_basename}' (already processed in this post)")
                         post_skip_count += 1
                         file_downloaded_or_exists = True
                         with self.downloaded_files_lock:
                             self.downloaded_files.add(cleaned_save_filename)
                         break # Don't try other folders
                    with self.downloaded_files_lock:
                         if cleaned_save_filename in self.downloaded_files:
                             self.logger(f"   -> Global Filename Skip: '{original_name_for_log}' in '{folder_basename}' (filename already downloaded globally)")
                             post_skip_count += 1
                             file_downloaded_or_exists = True
                             break # Don't try other folders
                try:
                    self.logger(f"⬇️ Downloading '{original_name_for_log}' to '{folder_basename}'...")
                    self.current_download_path = save_path # Still set the potential path
                    self.is_downloading_file = True
                    self.signals.file_download_status_signal.emit(True) # Signal START
                    response = requests.get(file_url, headers=headers, timeout=(15, 300), stream=True) # (connect_timeout, read_timeout)
                    response.raise_for_status() # Check for HTTP errors
                    file_content_bytes = BytesIO()
                    downloaded_size = 0
                    chunk_count = 0
                    md5_hash = hashlib.md5() # Initialize hash object

                    for chunk in response.iter_content(chunk_size=32 * 1024): # 32KB chunks
                        if self.check_cancel(): break # Check cancellation frequently
                        if self.skip_current_file_flag.is_set(): break

                        if chunk: # filter out keep-alive new chunks
                            file_content_bytes.write(chunk)
                            md5_hash.update(chunk) # Update hash with chunk
                            downloaded_size += len(chunk)
                            chunk_count += 1
                    if self.check_cancel() or self.skip_current_file_flag.is_set():
                        self.logger(f"   ⚠️ Download interrupted {'(cancelled)' if self.cancellation_event.is_set() else '(skipped)'} for {original_name_for_log}.")
                        if self.skip_current_file_flag.is_set():
                             post_skip_count += 1
                             self.skip_current_file_flag.clear()
                        break # Break from trying other folders
                    final_save_path = save_path # May change if compressed
                    current_filename_for_log = cleaned_save_filename # May change
                    file_content_bytes.seek(0) # Rewind the BytesIO object to the beginning

                    if downloaded_size == 0 and chunk_count > 0:
                         self.logger(f"⚠️ Warning: Downloaded 0 bytes despite receiving chunks for {original_name_for_log}. Skipping save.")
                         post_skip_count += 1
                         break # Treat as failure for this folder

                    if downloaded_size > 0:
                        calculated_hash = md5_hash.hexdigest() # Get the final hash
                        with self.downloaded_file_hashes_lock: # Use lock for hash set
                             if calculated_hash in self.downloaded_file_hashes:
                                self.logger(f"   -> Content Skip: '{original_name_for_log}' (Hash: {calculated_hash}) already downloaded.")
                                post_skip_count += 1
                                file_downloaded_or_exists = True # Mark as handled
                                with self.downloaded_files_lock:
                                     self.downloaded_files.add(cleaned_save_filename)
                                with local_filenames_lock:
                                     local_processed_filenames.add(cleaned_save_filename)
                                break
                             else:
                                 pass


                        if not file_downloaded_or_exists: # Only proceed if not skipped by hash check
                            final_bytes_to_save = file_content_bytes
                            is_img_for_compress = is_image(cleaned_save_filename)
                            if is_img_for_compress and not is_thumbnail and self.compress_images and Image and downloaded_size > 1500 * 1024:
                                self.logger(f"   Compressing large image ({downloaded_size / 1024:.2f} KB)...")
                                try:
                                    with Image.open(file_content_bytes) as img:
                                        original_format = img.format
                                        if img.mode == 'P': img = img.convert('RGBA')
                                        elif img.mode not in ['RGB', 'RGBA', 'L']: img = img.convert('RGB')

                                        compressed_bytes = BytesIO()
                                        img.save(compressed_bytes, format='WebP', quality=75, method=4) # Adjust quality/method
                                        compressed_size = compressed_bytes.getbuffer().nbytes
                                    if compressed_size < downloaded_size * 0.90:
                                        self.logger(f"   Compression success: {compressed_size / 1024:.2f} KB (WebP Q75)")
                                        compressed_bytes.seek(0)
                                        final_bytes_to_save = compressed_bytes
                                        base, _ = os.path.splitext(cleaned_save_filename)
                                        current_filename_for_log = base + '.webp'
                                        final_save_path = os.path.join(folder_path, current_filename_for_log)
                                        self.logger(f"   Updated filename: {current_filename_for_log}")
                                    else:
                                        self.logger(f"   Compression skipped: WebP not significantly smaller ({compressed_size / 1024:.2f} KB).")
                                        file_content_bytes.seek(0) # Rewind original bytes
                                        final_bytes_to_save = file_content_bytes

                                except Exception as comp_e:
                                    self.logger(f"❌ Image compression failed for {original_name_for_log}: {comp_e}. Saving original.")
                                    file_content_bytes.seek(0) # Rewind original
                                    final_bytes_to_save = file_content_bytes
                                    final_save_path = save_path # Ensure original path

                            elif is_img_for_compress and not is_thumbnail and self.compress_images:
                                 self.logger(f"   Skipping compression: Image size ({downloaded_size / 1024:.2f} KB) below threshold.")
                                 file_content_bytes.seek(0)
                                 final_bytes_to_save = file_content_bytes

                            elif is_thumbnail and downloaded_size > LARGE_THUMBNAIL_THRESHOLD: # This is_thumbnail check is less relevant now
                                  self.logger(f"⚠️ Downloaded thumbnail '{current_filename_for_log}' ({downloaded_size / 1024:.2f} KB) is large.")
                                  file_content_bytes.seek(0)
                                  final_bytes_to_save = file_content_bytes
                            else: # Ensure stream is rewound if no compression happened
                                file_content_bytes.seek(0)
                                final_bytes_to_save = file_content_bytes
                            save_file = False
                            with self.downloaded_files_lock: # Lock for global filename set
                                 with local_filenames_lock: # Lock for local filename set
                                     if os.path.exists(final_save_path) and os.path.getsize(final_save_path) > 0:
                                          self.logger(f"   -> Exists Skip (pre-write): '{current_filename_for_log}' in '{folder_basename}'")
                                          post_skip_count += 1
                                          file_downloaded_or_exists = True
                                     elif current_filename_for_log in self.downloaded_files:
                                          self.logger(f"   -> Global Skip (pre-write): '{current_filename_for_log}' in '{folder_basename}' (already downloaded globally)")
                                          post_skip_count += 1
                                          file_downloaded_or_exists = True
                                     elif current_filename_for_log in local_processed_filenames:
                                           self.logger(f"   -> Local Skip (pre-write): '{current_filename_for_log}' in '{folder_basename}' (already processed in this post)")
                                           post_skip_count += 1
                                           file_downloaded_or_exists = True
                                     else:
                                         save_file = True # OK to save


                            if save_file:
                                try:
                                    with open(final_save_path, 'wb') as f:
                                        while True:
                                            chunk = final_bytes_to_save.read(64 * 1024) # 64KB write chunks
                                            if not chunk: break
                                            f.write(chunk)
                                    with self.downloaded_file_hashes_lock:
                                         self.downloaded_file_hashes.add(calculated_hash) # ADD HASH
                                    with self.downloaded_files_lock:
                                         self.downloaded_files.add(current_filename_for_log) # Add filename
                                    with local_filenames_lock:
                                         local_processed_filenames.add(current_filename_for_log) # Add filename locally

                                    post_download_count += 1
                                    file_downloaded_or_exists = True
                                    self.logger(f"✅ Saved: '{current_filename_for_log}' ({downloaded_size / 1024:.1f} KB, Hash: {calculated_hash[:8]}...) in '{folder_basename}'")
                                    time.sleep(0.05) # Tiny delay after successful save

                                except IOError as io_err:
                                     self.logger(f"❌ Save Fail: '{current_filename_for_log}' to '{folder_basename}'. Error: {io_err}")
                                     post_skip_count += 1 # Count save failure as skip
                                     if os.path.exists(final_save_path):
                                          try: os.remove(final_save_path)
                                          except OSError: pass
                                     break
                                except Exception as save_err:
                                     self.logger(f"❌ Unexpected Save Error: '{current_filename_for_log}' in '{folder_basename}'. Error: {save_err}")
                                     post_skip_count += 1
                                     if os.path.exists(final_save_path):
                                          try: os.remove(final_save_path)
                                          except OSError: pass
                                     break # Break folder loop on unexpected error
                            final_bytes_to_save.close()
                            if file_content_bytes is not final_bytes_to_save:
                                file_content_bytes.close()
                    if file_downloaded_or_exists:
                         break
                except requests.exceptions.RequestException as e:
                    self.logger(f"❌ Download Fail: {original_name_for_log}. Error: {e}")
                    post_skip_count += 1
                    break
                except IOError as e:
                     self.logger(f"❌ File I/O Error: {original_name_for_log} in '{folder_basename}'. Error: {e}")
                     post_skip_count += 1
                     break # Break folder loop
                except Exception as e:
                     self.logger(f"❌ Unexpected Error during download/save for {original_name_for_log}: {e}")
                     import traceback
                     self.logger(f"   Traceback: {traceback.format_exc(limit=2)}")
                     post_skip_count += 1
                     break # Break folder loop on unexpected error

                finally:
                    self.is_downloading_file = False
                    self.current_download_path = None
                    self.signals.file_download_status_signal.emit(False) # Signal END
            if self.check_cancel(): break # Check cancellation after trying all folders
            if self.skip_current_file_flag.is_set():
                 self.skip_current_file_flag.clear()
            if not file_downloaded_or_exists:
                 pass
        if self.check_cancel():
            self.logger(f"   Post {post_id} processing cancelled.")
            return post_download_count, post_skip_count


        self.logger(f"   Post {post_id} Summary: Downloaded={post_download_count}, Skipped={post_skip_count}")
        return post_download_count, post_skip_count
class DownloaderApp(QWidget):
    character_prompt_response_signal = pyqtSignal(bool)
    log_signal = pyqtSignal(str)
    add_character_prompt_signal = pyqtSignal(str)
    file_download_status_signal = pyqtSignal(bool) # Combined start/end
    overall_progress_signal = pyqtSignal(int, int) # total, processed
    finished_signal = pyqtSignal(int, int, bool) # downloaded, skipped, cancelled


    def __init__(self):
        super().__init__()
        self.config_file = "Known.txt"
        self.download_thread = None
        self.thread_pool = None
        self.cancellation_event = threading.Event()
        self.active_futures = []
        self.total_posts_to_process = 0
        self.processed_posts_count = 0
        self.download_counter = 0
        self.skip_counter = 0
        self.worker_signals = PostProcessorSignals() # Single instance for workers
        self.prompt_mutex = QMutex()
        self._add_character_response = None
        self.downloaded_files = set() # Shared set for tracking downloaded filenames (secondary check)
        self.downloaded_files_lock = threading.Lock() # Lock for filenames set
        self.downloaded_file_hashes = set() # Shared set for tracking downloaded file hashes (primary check) # ADDED
        self.downloaded_file_hashes_lock = threading.Lock() # Lock for hashes set # ADDED
        self.load_known_names() # Load KNOWN_NAMES global
        self.setWindowTitle("Kemono Downloader v2.3 (Content Dedupe & Skip)") # Updated Title
        self.setGeometry(150, 150, 1050, 820) # Adjusted size for new field
        self.setStyleSheet(self.get_dark_theme())
        self.init_ui() # Initialize UI elements
        self._connect_signals()
        self.log_signal.emit("ℹ️ Local API server functionality has been removed.")


    def _connect_signals(self):
        """Connect all signals for clarity."""
        self.worker_signals.progress_signal.connect(self.log)
        self.worker_signals.file_download_status_signal.connect(self.update_skip_button_state)
        self.log_signal.connect(self.log)
        self.add_character_prompt_signal.connect(self.prompt_add_character)
        self.character_prompt_response_signal.connect(self.receive_add_character_result)
        self.overall_progress_signal.connect(self.update_progress_display)
        self.finished_signal.connect(self.download_finished)
        self.character_search_input.textChanged.connect(self.filter_character_list) # CONNECTED
    def load_known_names(self):
        """Loads known names from the config file into the global KNOWN_NAMES list."""
        global KNOWN_NAMES
        loaded_names = []
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    raw_names = [line.strip() for line in f]
                    loaded_names = sorted(list(set(filter(None, raw_names))))
                log_msg = f"ℹ️ Loaded {len(loaded_names)} known names from {self.config_file}"
            except Exception as e:
                log_msg = f"❌ Error loading config '{self.config_file}': {e}"
                QMessageBox.warning(self, "Config Load Error", f"Could not load list from {self.config_file}:\n{e}")
                loaded_names = [] # Start empty on error
        else:
            log_msg = f"ℹ️ Config file '{self.config_file}' not found. Starting empty."
            loaded_names = []

        KNOWN_NAMES = loaded_names # Update global list
        if hasattr(self, 'log_output'):
             self.log_signal.emit(log_msg)
        else:
             print(log_msg)


    def save_known_names(self):
        """Saves the current global KNOWN_NAMES list to the config file."""
        global KNOWN_NAMES
        try:
            unique_sorted_names = sorted(list(set(filter(None, KNOWN_NAMES))))
            with open(self.config_file, 'w', encoding='utf-8') as f:
                for name in unique_sorted_names:
                    f.write(name + '\n')
            KNOWN_NAMES = unique_sorted_names
            if hasattr(self, 'log_signal'):
                 self.log_signal.emit(f"💾 Saved {len(unique_sorted_names)} known names to {self.config_file}")
            else:
                 print(f"Saved {len(unique_sorted_names)} names to {self.config_file}")

        except Exception as e:
            log_msg = f"❌ Error saving config '{self.config_file}': {e}"
            if hasattr(self, 'log_signal'):
                 self.log_signal.emit(log_msg)
            else:
                 print(log_msg)
            QMessageBox.warning(self, "Config Save Error", f"Could not save list to {self.config_file}:\n{e}")
    def closeEvent(self, event):
        """Handles application closing: saves config, checks for running downloads."""
        self.save_known_names() # Save names first
        should_exit = True
        is_downloading = (self.download_thread and self.download_thread.isRunning()) or (self.thread_pool is not None)

        if is_downloading:
             reply = QMessageBox.question(self, "Confirm Exit",
                                          "Download in progress. Are you sure you want to exit and cancel?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
             if reply == QMessageBox.Yes:
                 self.log_signal.emit("⚠️ Cancelling active download due to application exit...")
                 self.cancel_download() # Request cancellation
             else:
                 should_exit = False
                 self.log_signal.emit("ℹ️ Application exit cancelled.")
                 event.ignore() # Prevent closing
                 return

        if should_exit:
            self.log_signal.emit("ℹ️ Application closing.") # Removed "Stopping API server..."
            self.log_signal.emit("👋 Exiting application.")
            event.accept() # Allow closing
    def init_ui(self):
        """Sets up all the UI widgets and layouts."""
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("🔗 Kemono Creator/Post URL:"))
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("e.g., https://kemono.su/patreon/user/12345 or .../post/98765")
        self.link_input.textChanged.connect(self.update_custom_folder_visibility)
        left_layout.addWidget(self.link_input)

        left_layout.addWidget(QLabel("📁 Download Location:"))
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select folder where downloads will be saved")
        self.dir_button = QPushButton("Browse...")
        self.dir_button.clicked.connect(self.browse_directory)
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.dir_input, 1) # Input takes more space
        dir_layout.addWidget(self.dir_button)
        left_layout.addLayout(dir_layout)
        self.custom_folder_widget = QWidget()
        custom_folder_layout = QVBoxLayout(self.custom_folder_widget)
        custom_folder_layout.setContentsMargins(0, 5, 0, 0) # Add top margin
        self.custom_folder_label = QLabel("🗄️ Custom Folder Name (Single Post Only):")
        self.custom_folder_input = QLineEdit()
        self.custom_folder_input.setPlaceholderText("Optional: Save this post to specific folder")
        custom_folder_layout.addWidget(self.custom_folder_label)
        custom_folder_layout.addWidget(self.custom_folder_input)
        self.custom_folder_widget.setVisible(False) # Initially hidden
        left_layout.addWidget(self.custom_folder_widget)
        self.character_filter_widget = QWidget()
        character_filter_layout = QVBoxLayout(self.character_filter_widget)
        character_filter_layout.setContentsMargins(0, 5, 0, 0) # Add top margin
        self.character_label = QLabel("🎯 Filter by Show/Character Name:")
        self.character_input = QLineEdit()
        self.character_input.setPlaceholderText("Only download posts matching this known name in title")
        character_filter_layout.addWidget(self.character_label)
        character_filter_layout.addWidget(self.character_input)
        self.character_filter_widget.setVisible(True) # Initially visible, controlled by subfolder checkbox
        left_layout.addWidget(self.character_filter_widget)
        left_layout.addWidget(QLabel("🚫 Skip Posts/Files with Words (comma-separated):"))
        self.skip_words_input = QLineEdit()
        self.skip_words_input.setPlaceholderText("e.g., WM, WIP, sketch, preview")
        left_layout.addWidget(self.skip_words_input)
        options_layout_1 = QHBoxLayout()
        options_layout_1.addWidget(QLabel("Filter Files:"))
        self.radio_group = QButtonGroup(self)
        self.radio_all = QRadioButton("All")
        self.radio_images = QRadioButton("Images/GIFs")
        self.radio_videos = QRadioButton("Videos")
        self.radio_all.setChecked(True)
        self.radio_group.addButton(self.radio_all)
        self.radio_group.addButton(self.radio_images)
        self.radio_group.addButton(self.radio_videos)
        options_layout_1.addWidget(self.radio_all)
        options_layout_1.addWidget(self.radio_images)
        options_layout_1.addWidget(self.radio_videos)
        options_layout_1.addStretch(1)
        left_layout.addLayout(options_layout_1)
        options_layout_2 = QHBoxLayout()
        self.use_subfolders_checkbox = QCheckBox("Separate Folders by Name/Title")
        self.use_subfolders_checkbox.setChecked(True)
        self.use_subfolders_checkbox.toggled.connect(self.update_ui_for_subfolders)
        options_layout_2.addWidget(self.use_subfolders_checkbox)

        self.download_thumbnails_checkbox = QCheckBox("Download Thumbnails Only") # Removed (via API)
        self.download_thumbnails_checkbox.setChecked(False)
        self.download_thumbnails_checkbox.setToolTip("Thumbnail download functionality is currently limited without the API.") # Updated tooltip
        options_layout_2.addWidget(self.download_thumbnails_checkbox)
        options_layout_2.addStretch(1)
        left_layout.addLayout(options_layout_2)
        options_layout_3 = QHBoxLayout()
        self.skip_zip_checkbox = QCheckBox("Skip .zip")
        self.skip_zip_checkbox.setChecked(True)
        options_layout_3.addWidget(self.skip_zip_checkbox)
        self.skip_rar_checkbox = QCheckBox("Skip .rar")
        self.skip_rar_checkbox.setChecked(True)
        options_layout_3.addWidget(self.skip_rar_checkbox)

        self.compress_images_checkbox = QCheckBox("Compress Large Images (to WebP)")
        self.compress_images_checkbox.setChecked(False)
        self.compress_images_checkbox.setToolTip("Compress images > 1.5MB to WebP format (requires Pillow).")
        options_layout_3.addWidget(self.compress_images_checkbox)
        options_layout_3.addStretch(1)
        left_layout.addLayout(options_layout_3)
        options_layout_4 = QHBoxLayout()
        self.use_multithreading_checkbox = QCheckBox(f"Use Multithreading ({4} Threads)") # Use constant
        self.use_multithreading_checkbox.setChecked(True) # Default to on
        self.use_multithreading_checkbox.setToolTip("Speeds up downloads for full creator pages.\nSingle post URLs always use one thread.")
        options_layout_4.addWidget(self.use_multithreading_checkbox)
        options_layout_4.addStretch(1)
        left_layout.addLayout(options_layout_4)
        btn_layout = QHBoxLayout()
        self.download_btn = QPushButton("⬇️ Start Download")
        self.download_btn.setStyleSheet("padding: 8px 15px; font-weight: bold;") # Make prominent
        self.download_btn.clicked.connect(self.start_download)
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_download)
        self.skip_file_btn = QPushButton("⏭️ Skip Current File")
        self.skip_file_btn.setEnabled(False)
        self.skip_file_btn.setToolTip("Only available in single-thread mode during file download.")
        self.skip_file_btn.clicked.connect(self.skip_current_file)
        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.skip_file_btn)
        left_layout.addLayout(btn_layout)
        left_layout.addSpacing(10) # Add space before list
        known_chars_label_layout = QHBoxLayout()
        self.known_chars_label = QLabel("🎭 Known Shows/Characters (for Folder Names):")
        self.character_search_input = QLineEdit() # ADDED search bar
        self.character_search_input.setPlaceholderText("Search characters...") # ADDED placeholder
        known_chars_label_layout.addWidget(self.known_chars_label, 1) # Label takes more space
        known_chars_label_layout.addWidget(self.character_search_input) # ADDED search bar

        left_layout.addLayout(known_chars_label_layout) # Use the new layout

        self.character_list = QListWidget()
        self.character_list.addItems(KNOWN_NAMES)
        self.character_list.setSelectionMode(QListWidget.ExtendedSelection)
        left_layout.addWidget(self.character_list, 1) # Allow list to stretch vertically
        char_manage_layout = QHBoxLayout()
        self.new_char_input = QLineEdit()
        self.new_char_input.setPlaceholderText("Add new show/character name")
        self.add_char_button = QPushButton("➕ Add")
        self.delete_char_button = QPushButton("🗑️ Delete Selected")
        self.add_char_button.clicked.connect(self.add_new_character)
        self.new_char_input.returnPressed.connect(self.add_char_button.click)
        self.delete_char_button.clicked.connect(self.delete_selected_character)
        char_manage_layout.addWidget(self.new_char_input, 2) # Input wider
        char_manage_layout.addWidget(self.add_char_button, 1)
        char_manage_layout.addWidget(self.delete_char_button, 1)
        left_layout.addLayout(char_manage_layout)
        right_layout.addWidget(QLabel("📜 Progress Log:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumWidth(450) # Ensure decent width
        self.log_output.setLineWrapMode(QTextEdit.WidgetWidth) # Wrap lines
        right_layout.addWidget(self.log_output, 1) # Log area stretches
        self.progress_label = QLabel("Progress: Idle")
        self.progress_label.setStyleSheet("padding-top: 5px; font-style: italic;")
        right_layout.addWidget(self.progress_label)
        main_layout.addLayout(left_layout, 5) # Left side takes 5 parts width
        main_layout.addLayout(right_layout, 4) # Right side takes 4 parts width
        self.setLayout(main_layout)
        self.update_ui_for_subfolders(self.use_subfolders_checkbox.isChecked())
        self.update_custom_folder_visibility()


    def get_dark_theme(self):
        return """
        QWidget {
            background-color: #2E2E2E; /* Slightly lighter dark */
            color: #E0E0E0; /* Lighter text */
            font-family: Segoe UI, Arial, sans-serif;
            font-size: 10pt;
        }
        QLineEdit, QTextEdit, QListWidget {
            background-color: #3C3F41;
            border: 1px solid #5A5A5A; /* Slightly lighter border */
            padding: 5px;
            color: #F0F0F0; /* Bright text in inputs */
            border-radius: 4px; /* Slightly rounder corners */
        }
        QTextEdit {
             font-family: Consolas, Courier New, monospace; /* Monospace for log */
             font-size: 9.5pt;
        }
        QPushButton {
            background-color: #555;
            color: #F0F0F0;
            border: 1px solid #6A6A6A;
            padding: 6px 12px;
            border-radius: 4px;
            min-height: 22px; /* Ensure clickable height */
        }
        QPushButton:hover {
            background-color: #656565; /* Lighter hover */
            border: 1px solid #7A7A7A;
        }
        QPushButton:pressed {
            background-color: #4A4A4A; /* Darker pressed */
        }
        QPushButton:disabled {
            background-color: #404040; /* More distinct disabled */
            color: #888;
            border-color: #555;
        }
        QLabel {
            font-weight: bold;
            padding-top: 4px;
            padding-bottom: 2px;
            color: #C0C0C0; /* Slightly muted labels */
        }
        QRadioButton, QCheckBox {
            spacing: 5px;
            color: #E0E0E0;
            padding-top: 4px;
            padding-bottom: 4px;
        }
        QRadioButton::indicator, QCheckBox::indicator {
            width: 14px; /* Slightly larger indicators */
            height: 14px;
        }
        QListWidget {
             alternate-background-color: #353535; /* Subtle alternating color */
             border: 1px solid #5A5A5A;
        }
        QListWidget::item:selected {
            background-color: #007ACC; /* Standard blue selection */
            color: #FFFFFF;
        }
        QToolTip {
            background-color: #4A4A4A;
            color: #F0F0F0;
            border: 1px solid #6A6A6A;
            padding: 4px;
            border-radius: 3px;
        }
        """
    def browse_directory(self):
        current_dir = self.dir_input.text() if os.path.isdir(self.dir_input.text()) else ""
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", current_dir)
        if folder:
            self.dir_input.setText(folder)

    def log(self, message):
        """Safely appends messages to the log output widget (called via log_signal)."""
        try:
             safe_message = str(message).replace('\x00', '[NULL]') # Ensure string, sanitize nulls
             self.log_output.append(safe_message)
             scrollbar = self.log_output.verticalScrollBar()
             if scrollbar.value() >= scrollbar.maximum() - 30: # Threshold
                 scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
             print(f"GUI Log Error: {e}")
             print(f"Original Message: {message}")


    def get_filter_mode(self):
        if self.radio_images.isChecked():
            return 'image'
        elif self.radio_videos.isChecked():
            return 'video'
        return 'all'

    def add_new_character(self):
        """Adds anew name to the known names list and updates UI."""
        global KNOWN_NAMES
        name_to_add = self.new_char_input.text().strip()
        if not name_to_add:
             QMessageBox.warning(self, "Input Error", "Name cannot be empty.")
             return
        name_lower = name_to_add.lower()
        is_duplicate = any(existing.lower() == name_lower for existing in KNOWN_NAMES)

        if not is_duplicate:
            KNOWN_NAMES.append(name_to_add)
            KNOWN_NAMES.sort(key=str.lower)
            self.character_list.clear()
            self.character_list.addItems(KNOWN_NAMES)
            self.filter_character_list(self.character_search_input.text()) # Apply current filter # MODIFIED
            self.log_signal.emit(f"✅ Added '{name_to_add}' to known names list.")
            self.new_char_input.clear()
            self.save_known_names() # Save changes immediately
        else:
             QMessageBox.warning(self, "Duplicate Name", f"The name '{name_to_add}' (or similar) already exists in the list.")


    def delete_selected_character(self):
        """Removes selected names from the known names list."""
        global KNOWN_NAMES
        selected_items = self.character_list.selectedItems()
        if not selected_items:
             QMessageBox.warning(self, "Selection Error", "Please select one or more names to delete.")
             return

        names_to_remove = {item.text() for item in selected_items}
        confirm = QMessageBox.question(self, "Confirm Deletion",
                                       f"Are you sure you want to delete {len(names_to_remove)} selected name(s)?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirm == QMessageBox.Yes:
            original_count = len(KNOWN_NAMES)
            KNOWN_NAMES = [n for n in KNOWN_NAMES if n not in names_to_remove]
            removed_count = original_count - len(KNOWN_NAMES)

            if removed_count > 0:
                 self.log_signal.emit(f"🗑️ Removed {removed_count} name(s) from the list.")
                 self.character_list.clear()
                 KNOWN_NAMES.sort(key=str.lower) # Re-sort remaining names
                 self.character_list.addItems(KNOWN_NAMES)
                 self.filter_character_list(self.character_search_input.text()) # Apply current filter # MODIFIED
                 self.save_known_names() # Save changes
            else:
                 self.log_signal.emit("ℹ️ No names were removed (selection might have changed?).")


    def update_custom_folder_visibility(self, url_text=None):
        """Shows/hides the custom folder input based on URL and subfolder setting."""
        if url_text is None:
            url_text = self.link_input.text()

        _, _, post_id = extract_post_info(url_text.strip())
        should_show = bool(post_id) and self.use_subfolders_checkbox.isChecked()

        self.custom_folder_widget.setVisible(should_show)
        if not should_show:
             self.custom_folder_input.clear() # Clear input if hiding


    def update_ui_for_subfolders(self, checked):
         """Updates related UI elements when 'Separate Folders' checkbox changes."""
         self.character_filter_widget.setVisible(checked)
         self.update_custom_folder_visibility()
         if not checked:
              self.character_input.clear()
    def filter_character_list(self, search_text):
        """Filters the character list based on the search text."""
        search_text = search_text.lower()
        for i in range(self.character_list.count()):
            item = self.character_list.item(i)
            if search_text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)


    def update_progress_display(self, total_posts, processed_posts):
        """Updates the progress label based on processed posts."""
        if total_posts > 0:
            try:
                 percent = (processed_posts / total_posts) * 100
                 self.progress_label.setText(f"Progress: {processed_posts} / {total_posts} posts ({percent:.1f}%)")
            except ZeroDivisionError:
                 self.progress_label.setText(f"Progress: {processed_posts} / {total_posts} posts") # Handle rare case
        elif processed_posts > 0: # E.g., single post mode might not set total
             self.progress_label.setText(f"Progress: Processing post {processed_posts}...")
        else:
            self.progress_label.setText("Progress: Starting...")

    def start_download(self):
        """Validates inputs and starts the download in single or multi-threaded mode."""
        is_running = (self.download_thread and self.download_thread.isRunning()) or (self.thread_pool is not None)
        if is_running:
            self.log_signal.emit("⚠️ Download already in progress.")
            QMessageBox.warning(self, "Busy", "A download is already running.")
            return
        api_url = self.link_input.text().strip()
        output_dir = self.dir_input.text().strip()
        filter_mode = self.get_filter_mode()
        skip_zip = self.skip_zip_checkbox.isChecked()
        skip_rar = self.skip_rar_checkbox.isChecked()
        use_subfolders = self.use_subfolders_checkbox.isChecked()
        compress_images = self.compress_images_checkbox.isChecked()
        download_thumbnails = self.download_thumbnails_checkbox.isChecked()
        use_multithreading = self.use_multithreading_checkbox.isChecked()
        num_threads = 4 # Define number of threads
        raw_skip_words = self.skip_words_input.text().strip()
        skip_words_list = []
        if raw_skip_words:
            skip_words_list = [word.strip() for word in raw_skip_words.split(',') if word.strip()]
        service, user_id, post_id_from_url = extract_post_info(api_url)

        if not api_url:
            QMessageBox.critical(self, "Input Error", "Please enter a Kemono/Coomer URL.")
            return
        if not service or not user_id:
             QMessageBox.critical(self, "Input Error", "Invalid or unsupported URL format.\nPlease provide a valid creator page or post URL.")
             self.log_signal.emit(f"❌ Invalid URL detected: {api_url}")
             return
        if not output_dir:
             QMessageBox.critical(self, "Input Error", "Please select a download directory.")
             return
        if not os.path.isdir(output_dir):
             reply = QMessageBox.question(self, "Directory Not Found",
                                          f"The directory '{output_dir}' does not exist.\n\nCreate it?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
             if reply == QMessageBox.Yes:
                 try:
                     os.makedirs(output_dir)
                     self.log_signal.emit(f"ℹ️ Created download directory: {output_dir}")
                 except Exception as e:
                     QMessageBox.critical(self, "Directory Error", f"Could not create directory:\n{e}")
                     self.log_signal.emit(f"❌ Failed to create directory: {output_dir} - {e}")
                     return
             else: # User chose not to create
                 return
        if compress_images and Image is None:
             QMessageBox.warning(self, "Dependency Missing", "Image compression requires the Pillow library, but it's not installed.\nPlease run: pip install Pillow\n\nCompression will be disabled for this session.")
             self.log_signal.emit("❌ Cannot compress images: Pillow library not found.")
             compress_images = False # Disable for this run
        filter_character = None
        if use_subfolders and self.character_filter_widget.isVisible():
            filter_character = self.character_input.text().strip() or None

        custom_folder_name = None
        if use_subfolders and post_id_from_url and self.custom_folder_widget.isVisible():
            raw_custom_name = self.custom_folder_input.text().strip()
            if raw_custom_name:
                 cleaned_custom = clean_folder_name(raw_custom_name)
                 if cleaned_custom:
                     custom_folder_name = cleaned_custom
                 else:
                     QMessageBox.warning(self, "Input Warning", f"Custom folder name '{raw_custom_name}' is invalid and will be ignored.")
                     self.log_signal.emit(f"⚠️ Invalid custom folder name ignored: {raw_custom_name}")
        if use_subfolders and filter_character and not post_id_from_url: # Only validate filter if for whole creator
            clean_char_filter = clean_folder_name(filter_character.lower())
            known_names_lower = {name.lower() for name in KNOWN_NAMES}

            if not clean_char_filter:
                self.log_signal.emit(f"❌ Filter name '{filter_character}' is invalid. Aborting.")
                QMessageBox.critical(self, "Filter Error", "The provided filter name is invalid (contains only spaces or special characters).")
                return
            elif filter_character.lower() not in known_names_lower:
                 reply = QMessageBox.question(self, "Add Filter Name?",
                                          f"The filter name '{filter_character}' is not in your known names list.\n\nAdd it now and continue?",
                                          QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)

                 if reply == QMessageBox.Yes:
                     self.new_char_input.setText(filter_character) # Pre-fill input for user convenience? No, just add it.
                     self.add_new_character() # This adds, sorts, saves, updates UI
                     if filter_character.lower() not in {name.lower() for name in KNOWN_NAMES}:
                          self.log_signal.emit(f"⚠️ Failed to add '{filter_character}' automatically. Please add manually if needed.")
                     else:
                          self.log_signal.emit(f"✅ Added filter '{filter_character}' to list.")
                 elif reply == QMessageBox.No:
                     self.log_signal.emit(f"ℹ️ Proceeding without adding '{filter_character}'. Posts matching it might not be saved to a specific folder unless name is derived.")
                 else: # Cancel
                     self.log_signal.emit("❌ Download cancelled by user during filter check.")
                     return # Abort download
        self.log_output.clear()
        self.cancellation_event.clear() # Reset cancellation flag
        self.active_futures = []
        self.total_posts_to_process = 0
        self.processed_posts_count = 0
        self.download_counter = 0
        self.skip_counter = 0
        with self.downloaded_files_lock:
             self.downloaded_files.clear() # Clear downloaded files set (filenames)
        with self.downloaded_file_hashes_lock:
             self.downloaded_file_hashes.clear() # Clear downloaded file hashes set # ADDED

        self.progress_label.setText("Progress: Initializing...")
        self.log_signal.emit("="*40)
        self.log_signal.emit(f"🚀 Starting Download Task @ {time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_signal.emit(f"   URL: {api_url}")
        self.log_signal.emit(f"   Save Location: {output_dir}")
        mode = "Single Post" if post_id_from_url else "Creator Feed"
        self.log_signal.emit(f"   Mode: {mode}")
        self.log_signal.emit(f"   Subfolders: {'Enabled' if use_subfolders else 'Disabled'}")
        if use_subfolders:
             if custom_folder_name:
                  self.log_signal.emit(f"   Custom Folder (Post): '{custom_folder_name}'")
             elif filter_character:
                  self.log_signal.emit(f"   Character Filter: '{filter_character}'")
             else:
                 self.log_signal.emit(f"   Folder Naming: Automatic (Known Names > Title Extraction)")
        self.log_signal.emit(f"   File Type Filter: {filter_mode}")
        self.log_signal.emit(f"   Skip: {'.zip' if skip_zip else ''}{', ' if skip_zip and skip_rar else ''}{'.rar' if skip_rar else ''}{'None' if not (skip_zip or skip_rar) else ''}")
        if skip_words_list:
            self.log_signal.emit(f"   Skip Words (Title/Filename): {', '.join(skip_words_list)}")
        else:
            self.log_signal.emit(f"   Skip Words (Title/Filename): None")
        self.log_signal.emit(f"   Compress Images: {'Enabled' if compress_images else 'Disabled'}")
        self.log_signal.emit(f"   Thumbnails Only: {'Enabled' if download_thumbnails else 'Disabled'}")
        should_use_multithreading = use_multithreading and not post_id_from_url
        self.log_signal.emit(f"   Threading: {'Multi-threaded' if should_use_multithreading else 'Single-threaded'}")
        self.log_signal.emit("="*40)
        self.set_ui_enabled(False)
        self.cancel_btn.setEnabled(True)
        try:
            common_args = {
                'api_url': api_url,
                'output_dir': output_dir,
                'known_names_copy': list(KNOWN_NAMES), # Pass a copy
                'filter_character': filter_character,
                'filter_mode': filter_mode,
                'skip_zip': skip_zip,
                'skip_rar': skip_rar,
                'use_subfolders': use_subfolders,
                'compress_images': compress_images,
                'download_thumbnails': download_thumbnails,
                'service': service,
                'user_id': user_id,
                'downloaded_files': self.downloaded_files,
                'downloaded_files_lock': self.downloaded_files_lock,
                'downloaded_file_hashes': self.downloaded_file_hashes, # ADDED
                'downloaded_file_hashes_lock': self.downloaded_file_hashes_lock, # ADDED
                'skip_words_list': skip_words_list, # --- NEW: Pass skip words ---
            }

            if should_use_multithreading:
                self.log_signal.emit("   Initializing multi-threaded download...")
                multi_args = common_args.copy()
                multi_args['num_threads'] = num_threads
                self.start_multi_threaded_download(**multi_args)
            else:
                self.log_signal.emit("   Initializing single-threaded download...")
                single_args = common_args.copy()
                single_args['custom_folder_name'] = custom_folder_name
                single_args['single_post_id'] = post_id_from_url
                self.start_single_threaded_download(**single_args)

        except Exception as e:
             self.log_signal.emit(f"❌ CRITICAL ERROR preparing download task: {e}")
             import traceback
             self.log_signal.emit(traceback.format_exc())
             QMessageBox.critical(self, "Start Error", f"Failed to start download task:\n{e}")
             self.download_finished(0, 0, False) # Reset UI state


    def start_single_threaded_download(self, **kwargs):
        """Starts the download using the dedicated QThread."""
        try:
            self.download_thread = DownloadThread(
                 cancellation_event = self.cancellation_event, # Pass the shared event
                 **kwargs
            )

            if self.download_thread._init_failed:
                 QMessageBox.critical(self, "Thread Error", "Failed to initialize the download thread.\nCheck the log for details.")
                 self.download_finished(0, 0, False) # Reset UI
                 return
            self.download_thread.progress_signal.connect(self.log_signal) # Use log_signal slot
            self.download_thread.add_character_prompt_signal.connect(self.add_character_prompt_signal) # Forward signal
            self.download_thread.file_download_status_signal.connect(self.file_download_status_signal) # Forward signal
            self.download_thread.finished_signal.connect(self.finished_signal) # Forward signal
            self.character_prompt_response_signal.connect(self.download_thread.receive_add_character_result)

            self.download_thread.start()
            self.log_signal.emit("✅ Single download thread started.")

        except Exception as e:
             self.log_signal.emit(f"❌ CRITICAL ERROR starting single-thread task: {e}")
             import traceback
             self.log_signal.emit(traceback.format_exc())
             QMessageBox.critical(self, "Thread Start Error", f"Failed to start download thread:\n{e}")
             self.download_finished(0, 0, False) # Reset UI state



    def start_multi_threaded_download(self, **kwargs):
        """Starts download using ThreadPoolExecutor and a fetcher thread."""
        num_threads = kwargs['num_threads']
        self.thread_pool = ThreadPoolExecutor(max_workers=num_threads, thread_name_prefix='Downloader_')
        self.active_futures = []
        self.processed_posts_count = 0
        self.total_posts_to_process = 0 # Updated by fetcher
        self.download_counter = 0
        self.skip_counter = 0
        worker_args_template = kwargs.copy()
        del worker_args_template['num_threads']
        fetcher_thread = threading.Thread(
             target=self._fetch_and_queue_posts,
             args=(kwargs['api_url'], worker_args_template),
             daemon=True,
             name="PostFetcher"
        )
        fetcher_thread.start()
        self.log_signal.emit(f"✅ Post fetcher thread started. {num_threads} worker threads initializing...")


    def _fetch_and_queue_posts(self, api_url_input, worker_args_template):
        """(Runs in fetcher thread) Fetches posts and submits tasks to the pool."""
        all_posts = []
        fetch_error = False
        try:
            self.log_signal.emit("   Starting post fetch...")
            def fetcher_logger(msg):
                self.log_signal.emit(f"[Fetcher] {msg}")

            post_generator = download_from_api(api_url_input, logger=fetcher_logger)

            for posts_batch in post_generator:
                if self.cancellation_event.is_set():
                    self.log_signal.emit("⚠️ Post fetching cancelled by user.")
                    fetch_error = True # Treat cancellation during fetch as an error state for cleanup
                    break
                if isinstance(posts_batch, list):
                    all_posts.extend(posts_batch)
                    self.total_posts_to_process = len(all_posts)
                    if self.total_posts_to_process % 250 == 0: # Log every 250 posts
                        self.log_signal.emit(f"   Fetched {self.total_posts_to_process} posts...")
                else:
                     self.log_signal.emit(f"❌ API returned non-list batch: {type(posts_batch)}. Stopping fetch.")
                     fetch_error = True
                     break

            if not fetch_error:
                 self.log_signal.emit(f"✅ Finished fetching. Total posts found: {self.total_posts_to_process}")


        except Exception as e:
            self.log_signal.emit(f"❌ Unexpected Error during post fetching: {e}")
            import traceback
            self.log_signal.emit(traceback.format_exc(limit=3))
            fetch_error = True
        if self.cancellation_event.is_set() or fetch_error:
            self.finished_signal.emit(self.download_counter, self.skip_counter, self.cancellation_event.is_set())
            if self.thread_pool:
                self.thread_pool.shutdown(wait=False, cancel_futures=True)
                self.thread_pool = None
            return # Stop fetcher thread


        if self.total_posts_to_process == 0:
             self.log_signal.emit("😕 No posts found or fetched successfully.")
             self.finished_signal.emit(0, 0, False) # Signal completion with zero counts
             return
        self.log_signal.emit(f"   Submitting {self.total_posts_to_process} post tasks to worker pool...")
        self.processed_posts_count = 0 # Reset counter before submitting
        self.overall_progress_signal.emit(self.total_posts_to_process, 0) # Update progress display
        common_worker_args = {
             'download_root': worker_args_template['output_dir'], # **FIXED HERE**
             'known_names': worker_args_template['known_names_copy'],
             'filter_character': worker_args_template['filter_character'],
             'unwanted_keywords': {'spicy', 'hd', 'nsfw', '4k', 'preview'}, # Define unwanted keywords here
             'filter_mode': worker_args_template['filter_mode'],
             'skip_zip': worker_args_template['skip_zip'],
             'skip_rar': worker_args_template['skip_rar'],
             'use_subfolders': worker_args_template['use_subfolders'],
             'target_post_id_from_initial_url': worker_args_template.get('single_post_id'),
             'custom_folder_name': worker_args_template.get('custom_folder_name'),
             'compress_images': worker_args_template['compress_images'],
             'download_thumbnails': worker_args_template['download_thumbnails'],
             'service': worker_args_template['service'],
             'user_id': worker_args_template['user_id'],
             'api_url_input': worker_args_template['api_url'], # Pass original URL
             'cancellation_event': self.cancellation_event,
             'signals': self.worker_signals, # Pass the shared signals object
             'downloaded_files': self.downloaded_files,
             'downloaded_files_lock': self.downloaded_files_lock,
             'downloaded_file_hashes': self.downloaded_file_hashes, # ADDED
             'downloaded_file_hashes_lock': self.downloaded_file_hashes_lock, # ADDED
             'skip_words_list': worker_args_template['skip_words_list'], # --- NEW: Pass skip words ---
        }

        for post_data in all_posts:
            if self.cancellation_event.is_set():
                self.log_signal.emit("⚠️ Cancellation detected during task submission.")
                break # Stop submitting new tasks

            if not isinstance(post_data, dict):
                self.log_signal.emit(f"⚠️ Skipping invalid post data item (type: {type(post_data)}).")
                self.processed_posts_count += 1 # Count as processed (skipped)
                self.total_posts_to_process -=1 # Adjust total if skipping invalid data
                continue
            worker = PostProcessorWorker(post_data=post_data, **common_worker_args)
            try:
                 if self.thread_pool: # Check if pool still exists
                     future = self.thread_pool.submit(worker.process)
                     future.add_done_callback(self._handle_future_result)
                     self.active_futures.append(future)
                 else: # Pool was shut down prematurely
                     self.log_signal.emit("⚠️ Thread pool shutdown before submitting all tasks.")
                     break
            except RuntimeError as e: # Handle pool shutdown error
                 self.log_signal.emit(f"⚠️ Error submitting task (pool might be shutting down): {e}")
                 break
            except Exception as e:
                 self.log_signal.emit(f"❌ Unexpected error submitting task: {e}")
                 break
        submitted_count = len(self.active_futures)
        self.log_signal.emit(f"   {submitted_count} / {self.total_posts_to_process} tasks submitted.")



    def _handle_future_result(self, future: Future):
        """(Callback) Handles results from worker threads."""
        self.processed_posts_count += 1
        downloaded_res, skipped_res = 0, 0 # Default results

        try:
            if future.cancelled():
                 pass
            elif future.exception():
                exc = future.exception()
                self.log_signal.emit(f"❌ Error in worker thread: {exc}")
                pass
            else:
                downloaded, skipped = future.result() # Result from worker.process()
                downloaded_res = downloaded
                skipped_res = skipped

            with threading.Lock(): # Use a temporary lock for updating these counters
                 self.download_counter += downloaded_res
                 self.skip_counter += skipped_res
            self.overall_progress_signal.emit(self.total_posts_to_process, self.processed_posts_count)

        except Exception as e:
             self.log_signal.emit(f"❌ Error in result callback handling: {e}")
        if self.processed_posts_count >= self.total_posts_to_process and self.total_posts_to_process > 0:
            if self.processed_posts_count >= self.total_posts_to_process:
                 self.log_signal.emit("🏁 All submitted tasks have completed or failed.")
                 cancelled = self.cancellation_event.is_set()
                 self.finished_signal.emit(self.download_counter, self.skip_counter, cancelled)
    def set_ui_enabled(self, enabled):
        """Enable/disable UI controls based on download state."""
        self.download_btn.setEnabled(enabled)
        self.link_input.setEnabled(enabled)
        self.dir_input.setEnabled(enabled)
        self.dir_button.setEnabled(enabled)
        self.radio_all.setEnabled(enabled)
        self.radio_images.setEnabled(enabled)
        self.radio_videos.setEnabled(enabled)
        self.skip_zip_checkbox.setEnabled(enabled)
        self.skip_rar_checkbox.setEnabled(enabled)
        self.use_subfolders_checkbox.setEnabled(enabled)
        self.compress_images_checkbox.setEnabled(enabled)
        self.download_thumbnails_checkbox.setEnabled(enabled)
        self.use_multithreading_checkbox.setEnabled(enabled)
        self.skip_words_input.setEnabled(enabled) # --- NEW: Enable/disable skip words input ---
        self.character_search_input.setEnabled(enabled) # ADDED
        self.new_char_input.setEnabled(enabled)
        self.add_char_button.setEnabled(enabled)
        self.delete_char_button.setEnabled(enabled)
        subfolders_on = self.use_subfolders_checkbox.isChecked()
        self.custom_folder_widget.setEnabled(enabled and subfolders_on)
        self.character_filter_widget.setEnabled(enabled and subfolders_on)
        if enabled:
             self.update_ui_for_subfolders(subfolders_on)
             self.update_custom_folder_visibility() # Update based on current URL
        self.cancel_btn.setEnabled(not enabled)
        if enabled:
            self.skip_file_btn.setEnabled(False)
    def cancel_download(self):
        """Requests cancellation of the ongoing download (single or multi-thread)."""
        if not self.cancel_btn.isEnabled(): return # Prevent double clicks

        self.log_signal.emit("⚠️ Requesting cancellation...")
        self.cancellation_event.set() # Set the shared event
        self.cancel_btn.setEnabled(False)
        self.progress_label.setText("Progress: Cancelling...")
        if self.thread_pool and self.active_futures:
            cancelled_count = 0
            for future in self.active_futures:
                if future.cancel(): # Attempts to cancel
                    cancelled_count += 1
            if cancelled_count > 0:
                 self.log_signal.emit(f"   Attempted to cancel {cancelled_count} pending/running tasks.")


    def skip_current_file(self):
         """Signals the active download thread (if single-threaded) to skip the current file."""
         if self.download_thread and self.download_thread.isRunning():
              self.download_thread.skip_file() # Call method on the QThread instance
         elif self.thread_pool:
              self.log_signal.emit("ℹ️ Skipping individual files is not supported in multi-threaded mode.")
              QMessageBox.information(self, "Action Not Supported", "Skipping individual files is only available in single-threaded mode.")
         else:
              self.log_signal.emit("ℹ️ Skip requested,  but no download is active.")


    def update_skip_button_state(self, is_downloading_active):
         """Enables/disables the skip button based on download state."""
         can_skip = (not self.download_btn.isEnabled()) and \
                    (self.download_thread and self.download_thread.isRunning()) and \
                    is_downloading_active
         if self.thread_pool is not None:
             can_skip = False

         self.skip_file_btn.setEnabled(can_skip)


    def download_finished(self, total_downloaded, total_skipped, cancelled):
        """Cleans up resources and resets UI after download completion/cancellation."""
        self.log_signal.emit("="*40)
        status = "Cancelled" if cancelled else "Finished"
        self.log_signal.emit(f"🏁 Download {status}!")
        self.log_signal.emit(f"   Summary: Downloaded={total_downloaded}, Skipped={total_skipped}")
        self.progress_label.setText(f"{status}: {total_downloaded} downloaded, {total_skipped} skipped.")
        self.log_signal.emit("="*40)
        if self.download_thread:
            try:
                 self.character_prompt_response_signal.disconnect(self.download_thread.receive_add_character_result)
            except TypeError: pass # Ignore if not connected
            self.download_thread = None
        if self.thread_pool:
            self.log_signal.emit("   Shutting down worker thread pool...")
            self.thread_pool.shutdown(wait=False, cancel_futures=True)
            self.thread_pool = None
            self.active_futures = [] # Clear future list
        self.cancellation_event.clear()
        self.set_ui_enabled(True)
        self.cancel_btn.setEnabled(False)
        self.skip_file_btn.setEnabled(False)
    def prompt_add_character(self, character_name):

         reply = QMessageBox.question(self, "Add Filter Name?",
                                      f"The filter name '{character_name}' is not in your known list.\n\nAdd it now and continue download?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
         result = (reply == QMessageBox.Yes)

         if result:
              self.new_char_input.setText(character_name) # Pre-fill for clarity if needed? No, just add.
              if character_name.lower() not in {n.lower() for n in KNOWN_NAMES}:
                   self.add_new_character() # Add the name
                   if character_name.lower() not in {n.lower() for n in KNOWN_NAMES}:
                        self.log_signal.emit(f"⚠️ Failed to add '{character_name}' via prompt. Check for errors.")
                        result = False # Treat as failure if not added
              else:
                   self.log_signal.emit(f"ℹ️ Filter name '{character_name}' was already present or added.")
         self.character_prompt_response_signal.emit(result)
    def receive_add_character_result(self, result):
        """Slot to receive the boolean result from the GUI prompt."""
        with QMutexLocker(self.prompt_mutex):
             self._add_character_response = result
        self.log_signal.emit(f"   Received prompt response: {'Yes' if result else 'No'}")
class DownloadThread(QThread):
    progress_signal = pyqtSignal(str)
    add_character_prompt_signal = pyqtSignal(str) # Ask GUI to prompt user
    file_download_status_signal = pyqtSignal(bool) # File download start/end
    finished_signal = pyqtSignal(int, int, bool) # download_count, skip_count, cancelled_flag


    def __init__(self, api_url, output_dir, known_names_copy,
                 cancellation_event, single_post_id=None, # Use shared cancellation event
                 filter_character=None, filter_mode='all', skip_zip=True, skip_rar=True,
                 use_subfolders=True, custom_folder_name=None, compress_images=False,
                 download_thumbnails=False, service=None, user_id=None,
                 downloaded_files=None, downloaded_files_lock=None,
                 downloaded_file_hashes=None, downloaded_file_hashes_lock=None,
                 skip_words_list=None): # --- NEW: Accept skip_words_list ---
        super().__init__()
        self._init_failed = False
        self.api_url_input = api_url
        self.output_dir = output_dir
        self.known_names = list(known_names_copy)
        self.cancellation_event = cancellation_event
        self.initial_target_post_id = single_post_id
        self.filter_character = filter_character
        self.filter_mode = filter_mode
        self.skip_zip = skip_zip
        self.skip_rar = skip_rar
        self.use_subfolders = use_subfolders
        self.custom_folder_name = custom_folder_name
        self.compress_images = compress_images
        self.download_thumbnails = download_thumbnails
        self.service = service # Use passed value
        self.user_id = user_id   # Use passed value
        self.skip_words_list = skip_words_list if skip_words_list is not None else [] # --- NEW: Store skip_words_list ---
        self.downloaded_files = downloaded_files if downloaded_files is not None else set()
        self.downloaded_files_lock = downloaded_files_lock if downloaded_files_lock is not None else threading.Lock()
        self.downloaded_file_hashes = downloaded_file_hashes if downloaded_file_hashes is not None else set() # ADDED
        self.downloaded_file_hashes_lock = downloaded_file_hashes_lock if downloaded_file_hashes_lock is not None else threading.Lock() # ADDED
        self.skip_current_file_flag = threading.Event()
        self.is_downloading_file = False
        self.current_download_path = None
        self._add_character_response = None # Stores response from GUI prompt
        self.prompt_mutex = QMutex() # Protects access to _add_character_response
        if not self.service or not self.user_id:
             log_msg = f"❌ Thread Init Error: Missing service ('{self.service}') or user ID ('{self.user_id}') for URL '{api_url}'"
             print(log_msg) # Print error as signals might not be connected yet
             try: self.progress_signal.emit(log_msg)
             except RuntimeError: pass # Ignore if signal connection fails during init
             self._init_failed = True


    def run(self):
        """Main execution logic for the single-threaded download."""
        if self._init_failed:
             self.finished_signal.emit(0, 0, False) # Signal completion with zero counts
             return

        unwanted_keywords = {'spicy', 'hd', 'nsfw', '4k', 'preview'} # Example unwanted keywords
        grand_total_downloaded = 0
        grand_total_skipped = 0
        cancelled_by_user = False

        try:
            if self.use_subfolders and self.filter_character and not self.custom_folder_name:
                if not self._check_and_prompt_filter_character():
                    self.finished_signal.emit(0, 0, False) # Not cancelled, aborted by validation/user
                    return
            worker_signals_adapter = PostProcessorSignals()
            worker_signals_adapter.progress_signal.connect(self.progress_signal) # Route log messages
            worker_signals_adapter.file_download_status_signal.connect(self.file_download_status_signal) # Route file status

            post_worker = PostProcessorWorker(
                 post_data=None, # Will be set per post below
                 download_root=self.output_dir,
                 known_names=self.known_names, # Use thread's (potentially updated) list
                 filter_character=self.filter_character,
                 unwanted_keywords=unwanted_keywords,
                 filter_mode=self.filter_mode,
                 skip_zip=self.skip_zip,
                 skip_rar=self.skip_rar,
                 use_subfolders=self.use_subfolders,
                 target_post_id_from_initial_url=self.initial_target_post_id,
                 custom_folder_name=self.custom_folder_name,
                 compress_images=self.compress_images,
                 download_thumbnails=self.download_thumbnails,
                 service=self.service,
                 user_id=self.user_id,
                 api_url_input=self.api_url_input,
                 cancellation_event=self.cancellation_event, # Pass the shared event
                 signals=worker_signals_adapter, # Use the adapter signals
                 downloaded_files=self.downloaded_files,
                 downloaded_files_lock=self.downloaded_files_lock,
                 downloaded_file_hashes=self.downloaded_file_hashes, # ADDED
                 downloaded_file_hashes_lock=self.downloaded_file_hashes_lock, # ADDED
                 skip_words_list=self.skip_words_list, # --- NEW: Pass skip words to worker ---
            )
            post_worker.skip_current_file_flag = self.skip_current_file_flag
            self.progress_signal.emit("   Starting post fetch...")
            def thread_logger(msg):
                self.progress_signal.emit(msg)

            post_generator = download_from_api(self.api_url_input, logger=thread_logger)

            for posts_batch in post_generator:
                if self.isInterruptionRequested(): # Checks QThread interrupt AND cancellation_event
                    self.progress_signal.emit("⚠️ Download cancelled before processing batch.")
                    cancelled_by_user = True
                    break # Exit fetch loop

                for post in posts_batch:
                    if self.isInterruptionRequested():
                        self.progress_signal.emit("⚠️ Download cancelled during post processing.")
                        cancelled_by_user = True
                        break # Exit inner post loop
                    post_worker.post = post
                    try:
                        downloaded, skipped = post_worker.process()
                        grand_total_downloaded += downloaded
                        grand_total_skipped += skipped
                    except Exception as proc_e:
                         post_id_err = post.get('id', 'N/A') if isinstance(post, dict) else 'N/A'
                         self.progress_signal.emit(f"❌ Error processing post {post_id_err}: {proc_e}")
                         import traceback
                         self.progress_signal.emit(traceback.format_exc(limit=2))
                         grand_total_skipped += 1 # Count post as skipped on error
                    self.msleep(20) # 20 milliseconds

                if cancelled_by_user:
                    break # Exit outer batch loop as well
            if not cancelled_by_user:
                 self.progress_signal.emit("✅ Post fetching and processing complete.")


        except Exception as e:
            log_msg = f"\n❌ An critical error occurred in download thread: {e}"
            self.progress_signal.emit(log_msg)
            import traceback
            tb_str = traceback.format_exc()
            self.progress_signal.emit("--- Traceback ---")
            for line in tb_str.splitlines():
                 self.progress_signal.emit("  " + line)
            self.progress_signal.emit("--- End Traceback ---")
            cancelled_by_user = False # Not cancelled by user, but by error

        finally:
            self.finished_signal.emit(grand_total_downloaded, grand_total_skipped, cancelled_by_user)


    def _check_and_prompt_filter_character(self):
        """Validates filter character and prompts user if it's not known. Returns True if OK to proceed."""
        clean_char_filter = clean_folder_name(self.filter_character.lower())
        known_names_lower = {name.lower() for name in self.known_names}

        if not clean_char_filter:
             self.progress_signal.emit(f"❌ Filter name '{self.filter_character}' is invalid. Aborting.")
             return False # Invalid filter

        if self.filter_character.lower() not in known_names_lower:
            self.progress_signal.emit(f"❓ Filter '{self.filter_character}' not found in known list.")
            with QMutexLocker(self.prompt_mutex):
                 self._add_character_response = None
            self.add_character_prompt_signal.emit(self.filter_character)
            self.progress_signal.emit("   Waiting for user confirmation to add filter name...")
            while self._add_character_response is None:
                if self.isInterruptionRequested(): # Check cancellation
                    self.progress_signal.emit("⚠️ Cancelled while waiting for user input on filter name.")
                    return False # Abort if cancelled
                self.msleep(200) # Check every 200ms
            if self._add_character_response:
                self.progress_signal.emit(f"✅ User confirmed adding '{self.filter_character}'. Continuing.")
                if self.filter_character not in self.known_names:
                    self.known_names.append(self.filter_character)
                return True # OK to proceed
            else:
                self.progress_signal.emit(f"❌ User declined to add filter '{self.filter_character}'. Aborting download.")
                return False # User declined, abort
        return True


    def skip_file(self):
        """Sets the skip flag for the currently downloading file."""
        if self.isRunning() and self.is_downloading_file:
             self.progress_signal.emit("⏭️ Skip requested for current file.")
             self.skip_current_file_flag.set() # Signal the worker's process loop
        elif self.isRunning():
             self.progress_signal.emit("ℹ️ Skip requested, but no file download active.")


    def receive_add_character_result(self, result):
        """Slot to receive the boolean result from the GUI prompt."""
        with QMutexLocker(self.prompt_mutex):
             self._add_character_response = result
        self.progress_signal.emit(f"   Received prompt response: {'Yes' if result else 'No'}")


    def isInterruptionRequested(self):
        """Overrides QThread method to check both interruption flag and shared event."""
        return super().isInterruptionRequested() or self.cancellation_event.is_set()
if __name__ == '__main__':

    qt_app = QApplication(sys.argv)

    downloader = DownloaderApp() # Create the main application window
    downloader.show() # Show the window
    exit_code = qt_app.exec_()
    print(f"Application finished with exit code: {exit_code}")
    sys.exit(exit_code) # Exit the script with the application's exit code