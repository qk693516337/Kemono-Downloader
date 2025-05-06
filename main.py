import sys
import os
import time
import requests
import re
import threading
# import uvicorn # Removed uvicorn import
import queue
import hashlib  # Import hashlib for hashing
from concurrent.futures import ThreadPoolExecutor, Future, CancelledError

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QListWidget,
    QRadioButton, QButtonGroup, QCheckBox, QMainWindow
)

# Import QObject before other Qt classes that inherit from it if needed
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMutex, QMutexLocker, QObject
from urllib.parse import urlparse
# Import Image module correctly
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


# Removed try-except block for kemono_api
fastapi_app = None # Set to None directly


KNOWN_NAMES = []

# --- Helper Functions ---

def clean_folder_name(name):
    """Removes invalid characters for folder names and replaces spaces with underscores."""
    if not isinstance(name, str): name = str(name) # Ensure input is string
    # Allow spaces and common separators, remove others
    cleaned = re.sub(r'[^\w\s\-\_]', '', name)
    return cleaned.strip().replace(' ', '_')

def clean_filename(name):
     """Removes invalid characters for filenames and replaces spaces with underscores."""
     if not isinstance(name, str): name = str(name) # Ensure input is string
     # Allow dots for file extensions, and common filename characters
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
        # Check if token is not empty and not just unwanted keywords
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

        # Check if the cleaned known name is a substring of the cleaned title
        if cleaned_name_for_match in cleaned_title:
            # Ensure the match itself isn't an unwanted keyword
            if cleaned_name_for_match not in unwanted_keywords:
                 matched_cleaned_names.add(cleaned_name_for_match)

    return list(matched_cleaned_names)


def is_image(filename):
    if not filename: return False
    return filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')) # Added gif

def is_video(filename):
    if not filename: return False
    # Consider common video formats
    return filename.lower().endswith(('.mp4', '.mov', '.mkv', '.webm', '.avi', '.wmv'))

def is_zip(filename):
    if not filename: return False
    return filename.lower().endswith('.zip')

def is_rar(filename):
    if not filename: return False
    return filename.lower().endswith('.rar')


def is_post_url(url):
    if not isinstance(url, str): return False
    # Simple check for '/post/' segment in the path
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

        # Check for known domains
        is_kemono = 'kemono.su' in domain or 'kemono.party' in domain # Added kemono.party
        is_coomer = 'coomer.su' in domain or 'coomer.party' in domain # Added coomer.party
        if not (is_kemono or is_coomer):
            return None, None, None # Unknown domain

        # Pattern: /<service>/user/<user_id>
        if len(path_parts) >= 3 and path_parts[1].lower() == 'user':
            service = path_parts[0]
            user_id = path_parts[2]
            # Pattern: /<service>/user/<user_id>/post/<post_id>
            if len(path_parts) >= 5 and path_parts[3].lower() == 'post':
                post_id = path_parts[4]
            return service, user_id, post_id

        # API Pattern: /api/v1/<service>/user/<user_id>
        if len(path_parts) >= 5 and path_parts[0].lower() == 'api' and path_parts[1].lower() == 'v1' and path_parts[3].lower() == 'user':
            service = path_parts[2]
            user_id = path_parts[4]
            # API Pattern: /api/v1/<service>/user/<user_id>/post/<post_id>
            if len(path_parts) >= 7 and path_parts[5].lower() == 'post':
                 post_id = path_parts[6]
            return service, user_id, post_id

    except ValueError: # Handle potential errors during URL parsing
        print(f"Debug: ValueError parsing URL '{url_string}'")
        return None, None, None
    except Exception as e: # Catch other unexpected errors
        print(f"Debug: Exception during extract_post_info for URL '{url_string}': {e}")
        return None, None, None

    # If no pattern matched
    return None, None, None


def fetch_posts_paginated(api_url_base, headers, offset, logger):
    """Fetches a single page of posts from the creator API."""
    paginated_url = f'{api_url_base}?o={offset}'
    logger(f"   Fetching: {paginated_url}")
    try:
        response = requests.get(paginated_url, headers=headers, timeout=45) # Increased timeout
        response.raise_for_status() # Check for 4xx/5xx errors
        # Check content type before parsing JSON
        if 'application/json' not in response.headers.get('Content-Type', ''):
            raise RuntimeError(f"Unexpected content type received: {response.headers.get('Content-Type')}. Body: {response.text[:200]}")
        return response.json()
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Timeout fetching page offset {offset}")
    except requests.exceptions.RequestException as e:
        # Provide more context on request errors
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
            # Search for the target post in this batch
            matching_post = next((post for post in posts_batch if str(post.get('id')) == str(target_post_id)), None)

            if matching_post:
                logger(f"🎯 Found target post {target_post_id} on page {page}.")
                yield [matching_post] # Yield only the target post
                processed_target_post = True # Set flag to stop after this
            else:
                logger(f"   Target post {target_post_id} not found on this page.")
                # Assumption: If target_post_id is given, it should be on the first few pages.
                # For now, continue pagination until the end if target not found.
                pass
        else:
            # If not looking for a target post, yield the whole batch
            yield posts_batch

        # Increment offset only if we are not processing a target post that we just found
        if not (target_post_id and processed_target_post):
            # Determine offset increment (Kemono uses 50, but check API docs if possible)
            page_size = 50
            offset += page_size
            page += 1
            time.sleep(0.6) # Slightly increased delay between page fetches

    # Final check if target post was specified but never found
    if target_post_id and not processed_target_post:
        logger(f"❌ Target post ID {target_post_id} was not found for this creator.")



# --- Worker Object for ThreadPoolExecutor ---
class PostProcessorSignals(QObject):
    """Defines signals emitted by worker threads."""
    progress_signal = pyqtSignal(str)
    file_download_status_signal = pyqtSignal(bool) # True=start, False=end
    # No request_cancel_signal needed as workers check shared event

class PostProcessorWorker:
    """Processes a single post within a ThreadPoolExecutor."""
    def __init__(self, post_data, download_root, known_names, filter_character,
                 unwanted_keywords, filter_mode, skip_zip, skip_rar,
                 use_subfolders, target_post_id_from_initial_url, custom_folder_name,
                 compress_images, download_thumbnails, service, user_id,
                 api_url_input, cancellation_event, signals,
                 downloaded_files, downloaded_file_hashes, downloaded_files_lock, downloaded_file_hashes_lock,
                 skip_words_list=None): # ADDED skip_words_list
        # Store all arguments passed
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

        # Ensure Pillow is available if compression is enabled
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
        # No need to log cancellation detection repeatedly here, parent thread handles final status.
        return is_cancelled

    def skip_file(self):
        """Sets the skip flag (not typically called directly on worker)."""
        # This method is primarily for the single-threaded QThread context.
        # Skip logic for workers relies on checking skip_current_file_flag.
        pass

    def process(self):
        """Processes the single post assigned to this worker. Returns (downloaded, skipped)."""
        if self.check_cancel(): return 0, 0

        total_downloaded_post = 0
        total_skipped_post = 0
        # Standard headers, consider customizing if needed
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': f'https://{urlparse(self.api_url_input).netloc}/'}
        url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
        # LOCAL_API_BASE = "http://127.0.0.1:8000" # Removed LOCAL_API_BASE
        LARGE_THUMBNAIL_THRESHOLD = 1 * 1024 * 1024 # 1MB

        post = self.post
        api_title = post.get('title', '') # Default to empty string
        title = api_title if api_title else 'untitled_post'
        post_id = post.get('id', 'unknown_id')
        post_file_info = post.get('file')
        attachments = post.get('attachments', [])
        post_content = post.get('content', '')
        # is_target_post used for custom folder logic primarily
        is_target_post = (self.target_post_id_from_initial_url is not None) and (str(post_id) == str(self.target_post_id_from_initial_url))

        self.logger(f"\n--- Processing Post {post_id} ('{title[:50]}...') (Thread: {threading.current_thread().name}) ---")

        # --- NEW: Skip Words Check for Post Title ---
        if self.skip_words_list:
            title_lower = title.lower()
            for skip_word in self.skip_words_list:
                if skip_word.lower() in title_lower:
                    self.logger(f"   -> Skip Post (Title): Post {post_id} title ('{title[:30]}...') contains skip word '{skip_word}'. Skipping entire post.")
                    return 0, 1 # 0 downloaded, 1 skipped (the whole post)
        # --- END NEW ---


        if not isinstance(attachments, list):
            self.logger(f"⚠️ Corrupt attachment data for post {post_id}. Skipping attachments.")
            attachments = []

        # --- Determine Download Folder(s) ---
        valid_folder_paths = []
        folder_decision_reason = ""
        api_domain = urlparse(self.api_url_input).netloc if ('kemono.su' in urlparse(self.api_url_input).netloc.lower() or 'coomer.su' in urlparse(self.api_url_input).netloc.lower() or 'kemono.party' in urlparse(self.api_url_input).netloc.lower() or 'coomer.party' in urlparse(self.api_url_input).netloc.lower()) else "kemono.su"

        # 1. Custom Folder for Single Target Post (Highest Priority if applicable)
        if is_target_post and self.custom_folder_name and self.use_subfolders:
             # custom_folder_name should already be cleaned by GUI logic
             folder_path_full = os.path.join(self.download_root, self.custom_folder_name)
             valid_folder_paths = [folder_path_full]
             folder_decision_reason = f"Using custom folder for target post: '{self.custom_folder_name}'"


        # 2. Subfolders Enabled (Character Filter or Automatic) - Only if custom wasn't used
        if not valid_folder_paths and self.use_subfolders:
            folder_names_for_post = [] # Cleaned folder names derived for this post

            # a) Character Filter Applied
            if self.filter_character:
                clean_char_filter = clean_folder_name(self.filter_character.lower())
                # Match against known names found *in this post's title*
                matched_names_in_title = match_folders_from_title(title, self.known_names, self.unwanted_keywords)

                if clean_char_filter and clean_char_filter in matched_names_in_title:
                    # Use only the filtered character's folder name
                    folder_names_for_post = [clean_char_filter]
                    folder_decision_reason = f"Character filter '{self.filter_character}' matched title. Using folder '{clean_char_filter}'."
                else:
                    # Filter specified but doesn't match this post -> SKIP POST
                    self.logger(f"   -> Filter Skip Post {post_id}: Character filter '{self.filter_character}' not found in title matches ({matched_names_in_title}).")
                    return 0, 1 # 0 downloaded, 1 skipped (the whole post)

            # b) No Character Filter -> Automatic Naming
            else:
                matched_folders = match_folders_from_title(title, self.known_names, self.unwanted_keywords)
                if matched_folders:
                    folder_names_for_post = matched_folders # Use all matched known names as folders
                    folder_decision_reason = f"Found known name(s) in title: {matched_folders}"
                else:
                    # Try extracting a generic name from title
                    extracted_folder = extract_folder_name_from_title(title, self.unwanted_keywords)
                    folder_names_for_post = [extracted_folder]
                    folder_decision_reason = f"No known names in title. Using derived folder: '{extracted_folder}'"

            # Create full paths for the determined folder names
            for folder_name in folder_names_for_post:
                folder_path_full = os.path.join(self.download_root, folder_name)
                valid_folder_paths.append(folder_path_full)


        # 3. Fallback: Subfolders disabled OR no specific folder determined above
        if not valid_folder_paths:
            valid_folder_paths = [self.download_root] # Save directly to root
            if not folder_decision_reason: # Add reason if not already set
                folder_decision_reason = "Subfolders disabled or no specific folder determined. Using root download directory."


        self.logger(f"   Folder Decision: {folder_decision_reason}")
        if not valid_folder_paths:
             self.logger(f"   ERROR: No valid folder paths determined for post {post_id}. Skipping.")
             return 0, 1 # Skip post


        # --- Link Extraction from Content ---
        if post_content:
            try:
                # More robust link finding, avoid javascript: etc.
                found_links = re.findall(r'href=["\'](https?://[^"\']+)["\']', post_content)
                if found_links:
                    self.logger(f"🔗 Links found in post content:")
                    unique_links = sorted(list(set(found_links))) # Remove duplicates
                    for link in unique_links[:10]: # Log max 10 links
                        # Basic filtering of common unwanted links
                        if not any(x in link for x in ['.css', '.js', 'javascript:']):
                             self.logger(f"   - {link}")
                    if len(unique_links) > 10:
                        self.logger(f"   - ... ({len(unique_links) - 10} more links not shown)")
            except Exception as e:
                 self.logger(f"⚠️ Error parsing content for links in post {post_id}: {e}")


        # --- Identify Files/Attachments/Thumbnails ---
        files_to_process_for_download = []
        api_domain = urlparse(self.api_url_input).netloc if ('kemono.su' in urlparse(self.api_url_input).netloc.lower() or 'coomer.su' in urlparse(self.api_url_input).netloc.lower() or 'kemono.party' in urlparse(self.api_url_input).netloc.lower() or 'coomer.party' in urlparse(self.api_url_input).netloc.lower()) else "kemono.su"

        if self.download_thumbnails:
            # Thumbnail download attempt (original logic, modified to not use local API)
            self.logger(f"   Mode: Attempting to download thumbnail...") # Modified log
            # The original code relied on a local API for thumbnails.
            # Since we removed the API, this section needs to be adapted or removed.
            # For now, we'll simulate that thumbnail download is not available without the API.
            self.logger("      Thumbnail download via API is disabled as the local API is not used.")
            # If download_thumbnails is true, and we can't get it, then we should skip the post
            # as per the original logic's intention.
            self.logger(f"   -> Skipping Post {post_id}: Thumbnail download requested but API is disabled.")
            return 0, 1 # 0 downloaded, 1 skipped post

        else: # Normal file download mode
            self.logger(f"   Mode: Downloading post file/attachments.")
            # Process main post file ('file' field)
            if post_file_info and isinstance(post_file_info, dict) and post_file_info.get('path'):
                main_file_path = post_file_info['path'].lstrip('/')
                # Use provided name or derive from path
                main_file_name = post_file_info.get('name') or os.path.basename(main_file_path)
                if main_file_name:
                     file_url = f"https://{api_domain}/data/{main_file_path}"
                     files_to_process_for_download.append({
                         'url': file_url, 'name': main_file_name,
                         '_is_thumbnail': False, '_source': 'post_file'
                     })
                else:
                     self.logger(f"   ⚠️ Skipping main post file: Missing filename (Path: {main_file_path})")

            # Process attachments
            # Use a counter for attachments within the same post for unique naming
            attachment_counter = 0
            for idx, attachment in enumerate(attachments):
                if isinstance(attachment, dict) and attachment.get('path'):
                    attach_path = attachment['path'].lstrip('/')
                    attach_name = attachment.get('name') or os.path.basename(attach_path)
                    if attach_name:
                         # Construct a unique name including post ID and attachment index
                         base, ext = os.path.splitext(clean_filename(attach_name))
                         # Ensure index is added consistently for attachments
                         final_attach_name = f"{post_id}_{attachment_counter}{ext}"
                         # Add cleaned original name for readability/lookup if needed, but base on post+index for uniqueness
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


        # --- File Download Loop ---
        post_download_count = 0
        post_skip_count = 0 # Files skipped within this post

        # Use a local set and lock for filenames *within this post's processing*
        # This is secondary to the global hash check but helps with filename conflicts within the same post
        local_processed_filenames = set()
        local_filenames_lock = threading.Lock()


        for file_info in files_to_process_for_download:
            if self.check_cancel(): break # Check cancellation before each file

            # Check skip flag (set by GUI for single-thread mode, usually not used here)
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

            # --- NEW: Skip Words Check for Filename ---
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
            # --- END NEW ---


            # --- Apply File Type Filters (if not in thumbnail mode) ---
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
            
            # --- Attempt Download to Each Valid Folder ---
            file_downloaded_or_exists = False
            for folder_path in valid_folder_paths:
                if self.check_cancel(): break # Check cancellation before each folder attempt

                # --- Ensure Directory Exists ---
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

                # --- Check if File Already Exists on Disk OR Downloaded (Filename Check) ---
                # Check size > 0 to avoid re-downloading empty files from previous failures
                with local_filenames_lock: # Use local lock for filename set within post
                    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                         self.logger(f"   -> Exists Skip: '{original_name_for_log}' in '{folder_basename}'")
                         post_skip_count += 1 # Count exists as skipped for this post's summary
                         file_downloaded_or_exists = True
                         # Add to global filename set just in case
                         with self.downloaded_files_lock:
                             self.downloaded_files.add(cleaned_save_filename)
                         break # Don't try other folders if it exists in one valid location
                    elif cleaned_save_filename in local_processed_filenames:
                         self.logger(f"   -> Local Skip: '{original_name_for_log}' in '{folder_basename}' (already processed in this post)")
                         post_skip_count += 1
                         file_downloaded_or_exists = True
                         # Add to global filename set just in case
                         with self.downloaded_files_lock:
                             self.downloaded_files.add(cleaned_save_filename)
                         break # Don't try other folders
                    # Global filename check (less critical with hash check, but for consistency)
                    with self.downloaded_files_lock:
                         if cleaned_save_filename in self.downloaded_files:
                             self.logger(f"   -> Global Filename Skip: '{original_name_for_log}' in '{folder_basename}' (filename already downloaded globally)")
                             post_skip_count += 1
                             file_downloaded_or_exists = True
                             break # Don't try other folders


                # --- Actual Download Attempt ---
                try:
                    self.logger(f"⬇️ Downloading '{original_name_for_log}' to '{folder_basename}'...")
                    self.current_download_path = save_path # Still set the potential path
                    self.is_downloading_file = True
                    self.signals.file_download_status_signal.emit(True) # Signal START

                    # Use stream=True for large files, adjust timeout
                    response = requests.get(file_url, headers=headers, timeout=(15, 300), stream=True) # (connect_timeout, read_timeout)
                    response.raise_for_status() # Check for HTTP errors

                    # --- Download Content in Chunks and Calculate Hash ---
                    file_content_bytes = BytesIO()
                    downloaded_size = 0
                    chunk_count = 0
                    md5_hash = hashlib.md5() # Initialize hash object

                    for chunk in response.iter_content(chunk_size=32 * 1024): # 32KB chunks
                        if self.check_cancel(): break # Check cancellation frequently
                        # Skip flag check (less relevant for worker, but for consistency)
                        if self.skip_current_file_flag.is_set(): break

                        if chunk: # filter out keep-alive new chunks
                            file_content_bytes.write(chunk)
                            md5_hash.update(chunk) # Update hash with chunk
                            downloaded_size += len(chunk)
                            chunk_count += 1
                            # Optional: Add progress reporting per chunk if needed

                    # Check again if loop was broken by cancellation/skip
                    if self.check_cancel() or self.skip_current_file_flag.is_set():
                        self.logger(f"   ⚠️ Download interrupted {'(cancelled)' if self.cancellation_event.is_set() else '(skipped)'} for {original_name_for_log}.")
                        # Clean up partial file - not needed here as we haven't saved yet
                        # Ensure this file is marked as skipped if interrupted by skip flag
                        if self.skip_current_file_flag.is_set():
                             post_skip_count += 1
                             self.skip_current_file_flag.clear()
                        # Need to break from the folder loop as well
                        break # Break from trying other folders


                    # --- Process Downloaded Content (Hash Check, Compression, Save) ---
                    final_save_path = save_path # May change if compressed
                    current_filename_for_log = cleaned_save_filename # May change
                    file_content_bytes.seek(0) # Rewind the BytesIO object to the beginning

                    if downloaded_size == 0 and chunk_count > 0:
                         self.logger(f"⚠️ Warning: Downloaded 0 bytes despite receiving chunks for {original_name_for_log}. Skipping save.")
                         post_skip_count += 1
                         break # Treat as failure for this folder

                    if downloaded_size > 0:
                        calculated_hash = md5_hash.hexdigest() # Get the final hash

                        # --- Content Hash Check ---
                        with self.downloaded_file_hashes_lock: # Use lock for hash set
                             if calculated_hash in self.downloaded_file_hashes:
                                self.logger(f"   -> Content Skip: '{original_name_for_log}' (Hash: {calculated_hash}) already downloaded.")
                                post_skip_count += 1
                                file_downloaded_or_exists = True # Mark as handled
                                # Add filename to global set just in case filename checks are used elsewhere
                                with self.downloaded_files_lock:
                                     self.downloaded_files.add(cleaned_save_filename)
                                # Add filename to local set as well
                                with local_filenames_lock:
                                     local_processed_filenames.add(cleaned_save_filename)
                                # No need to save or compress, break from folder loop
                                break
                             else:
                                 # Hash not found, proceed with saving and adding hash later
                                 pass


                        if not file_downloaded_or_exists: # Only proceed if not skipped by hash check
                            final_bytes_to_save = file_content_bytes

                            # --- Image Compression ---
                            # Re-check if it's an image *after* download, just in case
                            is_img_for_compress = is_image(cleaned_save_filename)
                            if is_img_for_compress and not is_thumbnail and self.compress_images and Image and downloaded_size > 1500 * 1024:
                                self.logger(f"   Compressing large image ({downloaded_size / 1024:.2f} KB)...")
                                try:
                                    # Open image from bytes
                                    with Image.open(file_content_bytes) as img:
                                        original_format = img.format
                                        # Handle palette/mode issues for saving to WebP
                                        if img.mode == 'P': img = img.convert('RGBA')
                                        elif img.mode not in ['RGB', 'RGBA', 'L']: img = img.convert('RGB')

                                        compressed_bytes = BytesIO()
                                        img.save(compressed_bytes, format='WebP', quality=75, method=4) # Adjust quality/method
                                        compressed_size = compressed_bytes.getbuffer().nbytes

                                    # Only save if significantly smaller (e.g., > 10% reduction)
                                    if compressed_size < downloaded_size * 0.90:
                                        self.logger(f"   Compression success: {compressed_size / 1024:.2f} KB (WebP Q75)")
                                        compressed_bytes.seek(0)
                                        final_bytes_to_save = compressed_bytes
                                        # Update filename and save path
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
                                 # Log reason if compression enabled but size too small
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


                            # --- Save to Disk ---
                            # Check existence again before writing (reduce race slightly), though hash check is primary now.
                            # Also check filename sets again.
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
                                        # Write in chunks to handle potentially large compressed streams
                                        while True:
                                            chunk = final_bytes_to_save.read(64 * 1024) # 64KB write chunks
                                            if not chunk: break
                                            f.write(chunk)

                                    # File saved successfully, now add hash and filename to sets
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
                                     # Attempt cleanup of potentially partial file
                                     if os.path.exists(final_save_path):
                                          try: os.remove(final_save_path)
                                          except OSError: pass
                                     # Continue to next folder? Probably not useful if save failed. Break folder loop.
                                     break
                                except Exception as save_err:
                                     self.logger(f"❌ Unexpected Save Error: '{current_filename_for_log}' in '{folder_basename}'. Error: {save_err}")
                                     post_skip_count += 1
                                     if os.path.exists(final_save_path):
                                          try: os.remove(final_save_path)
                                          except OSError: pass
                                     break # Break folder loop on unexpected error

                            # Clean up BytesIO streams
                            final_bytes_to_save.close()
                            # Only close original if it's different from the one saved
                            if file_content_bytes is not final_bytes_to_save:
                                file_content_bytes.close()

                    # If downloaded/exists/saved successfully, break from folder loop
                    if file_downloaded_or_exists:
                         break

                # --- Error Handling for Download Attempt ---
                except requests.exceptions.RequestException as e:
                    self.logger(f"❌ Download Fail: {original_name_for_log}. Error: {e}")
                    # Clean up file if it was created partially/empty - not needed with BytesIO first
                    post_skip_count += 1
                    # Break folder loop: If download failed once, it will likely fail again.
                    break
                except IOError as e:
                     # This might happen if folder becomes inaccessible between check and write
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
                    # --- Cleanup after each folder attempt ---
                    self.is_downloading_file = False
                    self.current_download_path = None
                    self.signals.file_download_status_signal.emit(False) # Signal END

            # --- End of Folder Loop ---
            if self.check_cancel(): break # Check cancellation after trying all folders

            # Reset skip flag if it was processed
            if self.skip_current_file_flag.is_set():
                 self.skip_current_file_flag.clear()

            # If the file wasn't handled (downloaded/exists/skipped) in any folder, log it.
            # The skip count should already reflect failures or explicit skips.
            if not file_downloaded_or_exists:
                 # Check if it wasn't skipped for other reasons already counted
                 # This log might be redundant if errors were already logged.
                 # self.logger(f"   -> File '{original_name_for_log}' not downloaded/found in any target folder.")
                 pass


        # --- End of File Loop for Post ---
        if self.check_cancel():
            self.logger(f"   Post {post_id} processing cancelled.")
            # Return counts accumulated *before* cancellation
            return post_download_count, post_skip_count


        self.logger(f"   Post {post_id} Summary: Downloaded={post_download_count}, Skipped={post_skip_count}")
        return post_download_count, post_skip_count



# --- Main Application Class ---
class DownloaderApp(QWidget):
    # Signals for cross-thread communication
    character_prompt_response_signal = pyqtSignal(bool)
    log_signal = pyqtSignal(str)
    add_character_prompt_signal = pyqtSignal(str)
    file_download_status_signal = pyqtSignal(bool) # Combined start/end
    overall_progress_signal = pyqtSignal(int, int) # total, processed
    finished_signal = pyqtSignal(int, int, bool) # downloaded, skipped, cancelled


    def __init__(self):
        super().__init__()
        # Initialize core attributes first
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
        # self.api_server = None # Removed api_server
        # self.api_thread = None # Removed api_thread
        self.downloaded_files = set() # Shared set for tracking downloaded filenames (secondary check)
        self.downloaded_files_lock = threading.Lock() # Lock for filenames set
        self.downloaded_file_hashes = set() # Shared set for tracking downloaded file hashes (primary check) # ADDED
        self.downloaded_file_hashes_lock = threading.Lock() # Lock for hashes set # ADDED


        # Load configuration *after* initializing essential attributes
        self.load_known_names() # Load KNOWN_NAMES global

        # Setup UI last
        self.setWindowTitle("Kemono Downloader v2.3 (Content Dedupe & Skip)") # Updated Title
        self.setGeometry(150, 150, 1050, 820) # Adjusted size for new field
        self.setStyleSheet(self.get_dark_theme())
        self.init_ui() # Initialize UI elements

        # Connect signals
        self._connect_signals()

        # Start API server if configured - Removed call to start_api_server
        # self.start_api_server()
        self.log_signal.emit("ℹ️ Local API server functionality has been removed.")


    def _connect_signals(self):
        """Connect all signals for clarity."""
        # Signals from worker helper (for multi-threading)
        self.worker_signals.progress_signal.connect(self.log)
        self.worker_signals.file_download_status_signal.connect(self.update_skip_button_state)

        # Internal signals for GUI updates and thread communication
        self.log_signal.connect(self.log)
        self.add_character_prompt_signal.connect(self.prompt_add_character)
        self.character_prompt_response_signal.connect(self.receive_add_character_result)
        self.overall_progress_signal.connect(self.update_progress_display)
        self.finished_signal.connect(self.download_finished)

        # Connect search bar signal
        self.character_search_input.textChanged.connect(self.filter_character_list) # CONNECTED


    # --- Config Loading/Saving ---
    def load_known_names(self):
        """Loads known names from the config file into the global KNOWN_NAMES list."""
        global KNOWN_NAMES
        loaded_names = []
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    # Read lines, strip whitespace, filter empty lines
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

        # Log the message (use signal if UI ready, otherwise print)
        # Check if log_output exists before emitting signal during init
        if hasattr(self, 'log_output'):
             self.log_signal.emit(log_msg)
        else:
             print(log_msg)


    def save_known_names(self):
        """Saves the current global KNOWN_NAMES list to the config file."""
        global KNOWN_NAMES
        try:
            # Ensure uniqueness and sort before saving
            unique_sorted_names = sorted(list(set(filter(None, KNOWN_NAMES))))
            with open(self.config_file, 'w', encoding='utf-8') as f:
                for name in unique_sorted_names:
                    f.write(name + '\n')

            # Update global list to cleaned version (consistency)
            KNOWN_NAMES = unique_sorted_names

            # Use log_signal safely
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

    # --- Event Handling ---
    def closeEvent(self, event):
        """Handles application closing: saves config, checks for running downloads."""
        self.save_known_names() # Save names first
        should_exit = True

        # Check if download is active (either mode)
        is_downloading = (self.download_thread and self.download_thread.isRunning()) or (self.thread_pool is not None)

        if is_downloading:
             reply = QMessageBox.question(self, "Confirm Exit",
                                          "Download in progress. Are you sure you want to exit and cancel?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
             if reply == QMessageBox.Yes:
                 self.log_signal.emit("⚠️ Cancelling active download due to application exit...")
                 self.cancel_download() # Request cancellation
                 # Allow some time for cancellation signal to propagate? Maybe not needed.
             else:
                 should_exit = False
                 self.log_signal.emit("ℹ️ Application exit cancelled.")
                 event.ignore() # Prevent closing
                 return

        if should_exit:
            self.log_signal.emit("ℹ️ Application closing.") # Removed "Stopping API server..."
            # self._shutdown_api_server() # Removed call to shutdown API server
            self.log_signal.emit("👋 Exiting application.")
            event.accept() # Allow closing

    # Removed _shutdown_api_server method
    # def _shutdown_api_server(self): ...


    # --- UI Initialization ---
    def init_ui(self):
        """Sets up all the UI widgets and layouts."""
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # --- Left Side Controls ---
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

        # Custom Folder Input (Visible only for single posts + subfolders)
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

        # Character Filter Input (Visible only with subfolders)
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

        # --- NEW: Skip Words Input Field ---
        left_layout.addWidget(QLabel("🚫 Skip Posts/Files with Words (comma-separated):"))
        self.skip_words_input = QLineEdit()
        self.skip_words_input.setPlaceholderText("e.g., WM, WIP, sketch, preview")
        left_layout.addWidget(self.skip_words_input)
        # --- END NEW ---


        # --- Options Row 1 ---
        options_layout_1 = QHBoxLayout()
        options_layout_1.addWidget(QLabel("Filter Files:"))
        self.radio_group = QButtonGroup(self)
        self.radio_all = QRadioButton("All")
        self.radio_images = QRadioButton("Images/GIFs")
        self.radio_videos = QRadioButton("Videos")
        self.radio_all.setChecked(True)
        # Add radios to group for exclusivity
        self.radio_group.addButton(self.radio_all)
        self.radio_group.addButton(self.radio_images)
        self.radio_group.addButton(self.radio_videos)
        options_layout_1.addWidget(self.radio_all)
        options_layout_1.addWidget(self.radio_images)
        options_layout_1.addWidget(self.radio_videos)
        options_layout_1.addStretch(1)
        left_layout.addLayout(options_layout_1)

        # --- Options Row 2 (Checkboxes) ---
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

        # --- Options Row 3 (Checkboxes) ---
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

        # --- Options Row 4 (Threading) ---
        options_layout_4 = QHBoxLayout()
        self.use_multithreading_checkbox = QCheckBox(f"Use Multithreading ({4} Threads)") # Use constant
        self.use_multithreading_checkbox.setChecked(True) # Default to on
        self.use_multithreading_checkbox.setToolTip("Speeds up downloads for full creator pages.\nSingle post URLs always use one thread.")
        options_layout_4.addWidget(self.use_multithreading_checkbox)
        options_layout_4.addStretch(1)
        left_layout.addLayout(options_layout_4)


        # --- Action Buttons ---
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


        # --- Known Names List with Search ---
        known_chars_label_layout = QHBoxLayout()
        self.known_chars_label = QLabel("🎭 Known Shows/Characters (for Folder Names):")
        self.character_search_input = QLineEdit() # ADDED search bar
        self.character_search_input.setPlaceholderText("Search characters...") # ADDED placeholder
        known_chars_label_layout.addWidget(self.known_chars_label, 1) # Label takes more space
        known_chars_label_layout.addWidget(self.character_search_input) # ADDED search bar

        left_layout.addLayout(known_chars_label_layout) # Use the new layout

        self.character_list = QListWidget()
        # Load names *after* list widget is created
        self.character_list.addItems(KNOWN_NAMES)
        self.character_list.setSelectionMode(QListWidget.ExtendedSelection)
        left_layout.addWidget(self.character_list, 1) # Allow list to stretch vertically

        # Add/Delete Known Names Controls
        char_manage_layout = QHBoxLayout()
        self.new_char_input = QLineEdit()
        self.new_char_input.setPlaceholderText("Add new show/character name")
        self.add_char_button = QPushButton("➕ Add")
        self.delete_char_button = QPushButton("🗑️ Delete Selected")
        self.add_char_button.clicked.connect(self.add_new_character)
        # Allow adding via Enter key
        self.new_char_input.returnPressed.connect(self.add_char_button.click)
        self.delete_char_button.clicked.connect(self.delete_selected_character)
        char_manage_layout.addWidget(self.new_char_input, 2) # Input wider
        char_manage_layout.addWidget(self.add_char_button, 1)
        char_manage_layout.addWidget(self.delete_char_button, 1)
        left_layout.addLayout(char_manage_layout)


        # --- Right Side Log & Progress ---
        right_layout.addWidget(QLabel("📜 Progress Log:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumWidth(450) # Ensure decent width
        self.log_output.setLineWrapMode(QTextEdit.WidgetWidth) # Wrap lines
        right_layout.addWidget(self.log_output, 1) # Log area stretches

        # Progress Label
        self.progress_label = QLabel("Progress: Idle")
        self.progress_label.setStyleSheet("padding-top: 5px; font-style: italic;")
        right_layout.addWidget(self.progress_label)
        # Consider adding QProgressBar if desired


        # --- Assemble Main Layout ---
        main_layout.addLayout(left_layout, 5) # Left side takes 5 parts width
        main_layout.addLayout(right_layout, 4) # Right side takes 4 parts width
        self.setLayout(main_layout)

        # Initial UI state updates based on defaults
        self.update_ui_for_subfolders(self.use_subfolders_checkbox.isChecked())
        self.update_custom_folder_visibility()


    def get_dark_theme(self):
        # Dark theme CSS (improved readability slightly)
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

    # --- UI Interaction Methods ---
    def browse_directory(self):
        # Suggest last used directory? QSettings could store this.
        current_dir = self.dir_input.text() if os.path.isdir(self.dir_input.text()) else ""
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", current_dir)
        if folder:
            self.dir_input.setText(folder)

    def log(self, message):
        """Safely appends messages to the log output widget (called via log_signal)."""
        try:
             safe_message = str(message).replace('\x00', '[NULL]') # Ensure string, sanitize nulls
             self.log_output.append(safe_message)
             # Auto-scroll only if near the bottom
             scrollbar = self.log_output.verticalScrollBar()
             if scrollbar.value() >= scrollbar.maximum() - 30: # Threshold
                 scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
             # Fallback if GUI logging fails
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

        # Check for duplicates using case-insensitive comparison
        # Store original case, but compare lower-case
        name_lower = name_to_add.lower()
        is_duplicate = any(existing.lower() == name_lower for existing in KNOWN_NAMES)

        if not is_duplicate:
            # Add the name with its original casing
            KNOWN_NAMES.append(name_to_add)
            # Sort case-insensitively for display consistency
            KNOWN_NAMES.sort(key=str.lower)
            # Update the list widget and apply current filter
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
            # Filter list, keeping names NOT in the removal set
            KNOWN_NAMES = [n for n in KNOWN_NAMES if n not in names_to_remove]
            removed_count = original_count - len(KNOWN_NAMES)

            if removed_count > 0:
                 self.log_signal.emit(f"🗑️ Removed {removed_count} name(s) from the list.")
                 # Update UI list (ensure sorted after removal)
                 self.character_list.clear()
                 KNOWN_NAMES.sort(key=str.lower) # Re-sort remaining names
                 self.character_list.addItems(KNOWN_NAMES)
                 self.filter_character_list(self.character_search_input.text()) # Apply current filter # MODIFIED
                 self.save_known_names() # Save changes
            else:
                # This shouldn't happen if items were selected, but handle just in case
                 self.log_signal.emit("ℹ️ No names were removed (selection might have changed?).")


    def update_custom_folder_visibility(self, url_text=None):
        """Shows/hides the custom folder input based on URL and subfolder setting."""
        # If called by signal without text, get it from input widget
        if url_text is None:
            url_text = self.link_input.text()

        _, _, post_id = extract_post_info(url_text.strip())
        # Show only if it's a single post URL AND subfolders are enabled
        should_show = bool(post_id) and self.use_subfolders_checkbox.isChecked()

        self.custom_folder_widget.setVisible(should_show)
        if not should_show:
             self.custom_folder_input.clear() # Clear input if hiding


    def update_ui_for_subfolders(self, checked):
         """Updates related UI elements when 'Separate Folders' checkbox changes."""
         # Show/hide the character filter input
         self.character_filter_widget.setVisible(checked)
         # Re-evaluate custom folder visibility (depends on both subfolders and URL type)
         self.update_custom_folder_visibility()
         # Clear character filter input if subfolders are disabled
         if not checked:
              self.character_input.clear()

    # ADDED method to filter the character list
    def filter_character_list(self, search_text):
        """Filters the character list based on the search text."""
        search_text = search_text.lower()
        for i in range(self.character_list.count()):
            item = self.character_list.item(i)
            # Check if the item's text contains the search text (case-insensitive)
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



    # --- Download Logic Orchestration ---

    def start_download(self):
        """Validates inputs and starts the download in single or multi-threaded mode."""
        # Check if already running
        is_running = (self.download_thread and self.download_thread.isRunning()) or (self.thread_pool is not None)
        if is_running:
            self.log_signal.emit("⚠️ Download already in progress.")
            QMessageBox.warning(self, "Busy", "A download is already running.")
            return

        # --- Gather Inputs ---
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

        # --- NEW: Get Skip Words ---
        raw_skip_words = self.skip_words_input.text().strip()
        skip_words_list = []
        if raw_skip_words:
            # Split by comma, strip whitespace from each word, and filter out empty strings
            skip_words_list = [word.strip() for word in raw_skip_words.split(',') if word.strip()]
        # --- END NEW ---


        # --- Input Validation ---
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




        # Pillow Check for Compression
        if compress_images and Image is None:
             QMessageBox.warning(self, "Dependency Missing", "Image compression requires the Pillow library, but it's not installed.\nPlease run: pip install Pillow\n\nCompression will be disabled for this session.")
             self.log_signal.emit("❌ Cannot compress images: Pillow library not found.")
             compress_images = False # Disable for this run


        # --- Gather Filters ---
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


        # --- Character Filter Pre-Validation ---
        if use_subfolders and filter_character and not post_id_from_url: # Only validate filter if for whole creator
            clean_char_filter = clean_folder_name(filter_character.lower())
            known_names_lower = {name.lower() for name in KNOWN_NAMES}

            if not clean_char_filter:
                self.log_signal.emit(f"❌ Filter name '{filter_character}' is invalid. Aborting.")
                QMessageBox.critical(self, "Filter Error", "The provided filter name is invalid (contains only spaces or special characters).")
                return
            elif filter_character.lower() not in known_names_lower:
                 # Prompt user to add the name before starting threads
                 reply = QMessageBox.question(self, "Add Filter Name?",
                                          f"The filter name '{filter_character}' is not in your known names list.\n\nAdd it now and continue?",
                                          QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)

                 if reply == QMessageBox.Yes:
                     # Add the name and save (use existing method)
                     self.new_char_input.setText(filter_character) # Pre-fill input for user convenience? No, just add it.
                     self.add_new_character() # This adds, sorts, saves, updates UI
                     # Check if adding failed (e.g., duplicate detected by add_new_character)
                     if filter_character.lower() not in {name.lower() for name in KNOWN_NAMES}:
                          self.log_signal.emit(f"⚠️ Failed to add '{filter_character}' automatically. Please add manually if needed.")
                          # Don't abort here, let download proceed without guaranteed filter match yet
                     else:
                          self.log_signal.emit(f"✅ Added filter '{filter_character}' to list.")
                 elif reply == QMessageBox.No:
                     self.log_signal.emit(f"ℹ️ Proceeding without adding '{filter_character}'. Posts matching it might not be saved to a specific folder unless name is derived.")
                     # Allow proceeding, but filter might not work as expected if name isn't known
                     # Filter logic inside worker will handle skipping if name doesn't match title
                 else: # Cancel
                     self.log_signal.emit("❌ Download cancelled by user during filter check.")
                     return # Abort download


        # --- Reset State & Log Start ---
        self.log_output.clear()
        self.cancellation_event.clear() # Reset cancellation flag
        self.active_futures = []
        self.total_posts_to_process = 0
        self.processed_posts_count = 0
        self.download_counter = 0
        self.skip_counter = 0
        # Clear both downloaded sets
        with self.downloaded_files_lock:
             self.downloaded_files.clear() # Clear downloaded files set (filenames)
        with self.downloaded_file_hashes_lock:
             self.downloaded_file_hashes.clear() # Clear downloaded file hashes set # ADDED

        self.progress_label.setText("Progress: Initializing...")

        # Log settings clearly before starting
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
        # --- NEW: Log Skip Words ---
        if skip_words_list:
            self.log_signal.emit(f"   Skip Words (Title/Filename): {', '.join(skip_words_list)}")
        else:
            self.log_signal.emit(f"   Skip Words (Title/Filename): None")
        # --- END NEW ---
        self.log_signal.emit(f"   Compress Images: {'Enabled' if compress_images else 'Disabled'}")
        self.log_signal.emit(f"   Thumbnails Only: {'Enabled' if download_thumbnails else 'Disabled'}")


        # --- Determine Execution Mode ---
        # Always single-thread for single post URLs
        should_use_multithreading = use_multithreading and not post_id_from_url
        self.log_signal.emit(f"   Threading: {'Multi-threaded' if should_use_multithreading else 'Single-threaded'}")
        self.log_signal.emit("="*40)


        # --- Disable UI & Enable Cancel ---
        self.set_ui_enabled(False)
        self.cancel_btn.setEnabled(True)

        # --- Start Execution ---
        try:
            # Collect arguments common to both modes
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
                 # Pass shared state and locks
                'downloaded_files': self.downloaded_files,
                'downloaded_files_lock': self.downloaded_files_lock,
                'downloaded_file_hashes': self.downloaded_file_hashes, # ADDED
                'downloaded_file_hashes_lock': self.downloaded_file_hashes_lock, # ADDED
                'skip_words_list': skip_words_list, # --- NEW: Pass skip words ---
            }

            if should_use_multithreading:
                self.log_signal.emit("   Initializing multi-threaded download...")
                # Add multi-threading specific args
                multi_args = common_args.copy()
                multi_args['num_threads'] = num_threads
                self.start_multi_threaded_download(**multi_args)
            else:
                # Single post or multi-threading disabled
                self.log_signal.emit("   Initializing single-threaded download...")
                # Add single-thread specific args
                single_args = common_args.copy()
                single_args['custom_folder_name'] = custom_folder_name
                single_args['single_post_id'] = post_id_from_url
                self.start_single_threaded_download(**single_args)

        except Exception as e:
             self.log_signal.emit(f"❌ CRITICAL ERROR preparing download task: {e}")
             import traceback
             self.log_signal.emit(traceback.format_exc())
             QMessageBox.critical(self, "Start Error", f"Failed to start download task:\n{e}")
             # Ensure UI is reset if start fails critically
             self.download_finished(0, 0, False) # Reset UI state


    def start_single_threaded_download(self, **kwargs):
        """Starts the download using the dedicated QThread."""
        try:
            self.download_thread = DownloadThread(
                 cancellation_event = self.cancellation_event, # Pass the shared event
                 # Pass all other relevant kwargs collected in start_download
                 **kwargs
            )

            if self.download_thread._init_failed:
                 # Error already logged by thread's init
                 QMessageBox.critical(self, "Thread Error", "Failed to initialize the download thread.\nCheck the log for details.")
                 self.download_finished(0, 0, False) # Reset UI
                 return

            # Connect signals from this specific thread instance
            # These replace the direct connections used in previous versions
            self.download_thread.progress_signal.connect(self.log_signal) # Use log_signal slot
            self.download_thread.add_character_prompt_signal.connect(self.add_character_prompt_signal) # Forward signal
            self.download_thread.file_download_status_signal.connect(self.file_download_status_signal) # Forward signal
            self.download_thread.finished_signal.connect(self.finished_signal) # Forward signal

            # Connect response signal *to* the thread instance
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

        # Prepare arguments for worker threads (PostProcessorWorker)
        # Remove args not needed by worker's init or handled differently
        worker_args_template = kwargs.copy()
        del worker_args_template['num_threads']
        # api_url is used by fetcher, but also needed by worker for domain/URL construction
        # service/user_id are passed explicitly
        # output_dir needs to be mapped to download_root
        # Pass shared state explicitly

        # Start the fetcher thread
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
            # Define logger for the generator
            def fetcher_logger(msg):
                # Add prefix to distinguish fetcher logs if needed
                self.log_signal.emit(f"[Fetcher] {msg}")

            post_generator = download_from_api(api_url_input, logger=fetcher_logger)

            for posts_batch in post_generator:
                if self.cancellation_event.is_set():
                    self.log_signal.emit("⚠️ Post fetching cancelled by user.")
                    fetch_error = True # Treat cancellation during fetch as an error state for cleanup
                    break
                # Basic validation of batch
                if isinstance(posts_batch, list):
                    all_posts.extend(posts_batch)
                    self.total_posts_to_process = len(all_posts)
                    # Emit progress less frequently to avoid flooding log
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


        # --- Handle Fetch Completion / Errors ---
        if self.cancellation_event.is_set() or fetch_error:
            # If cancelled or error during fetch, signal completion immediately
            self.finished_signal.emit(self.download_counter, self.skip_counter, self.cancellation_event.is_set())
            # Ensure pool is cleaned up if fetch fails before submitting
            if self.thread_pool:
                self.thread_pool.shutdown(wait=False, cancel_futures=True)
                self.thread_pool = None
            return # Stop fetcher thread


        if self.total_posts_to_process == 0:
             self.log_signal.emit("😕 No posts found or fetched successfully.")
             self.finished_signal.emit(0, 0, False) # Signal completion with zero counts
             return


        # --- Submit Tasks to Worker Pool ---
        self.log_signal.emit(f"   Submitting {self.total_posts_to_process} post tasks to worker pool...")
        self.processed_posts_count = 0 # Reset counter before submitting
        self.overall_progress_signal.emit(self.total_posts_to_process, 0) # Update progress display


        # Extract arguments needed explicitly for the worker
        common_worker_args = {
             'download_root': worker_args_template['output_dir'], # **FIXED HERE**
             'known_names': worker_args_template['known_names_copy'],
             'filter_character': worker_args_template['filter_character'],
             'unwanted_keywords': {'spicy', 'hd', 'nsfw', '4k', 'preview'}, # Define unwanted keywords here
             'filter_mode': worker_args_template['filter_mode'],
             'skip_zip': worker_args_template['skip_zip'],
             'skip_rar': worker_args_template['skip_rar'],
             'use_subfolders': worker_args_template['use_subfolders'],
             # target_post_id is likely None here, but pass it for consistency
             'target_post_id_from_initial_url': worker_args_template.get('single_post_id'),
             # custom_folder_name is likely None here
             'custom_folder_name': worker_args_template.get('custom_folder_name'),
             'compress_images': worker_args_template['compress_images'],
             'download_thumbnails': worker_args_template['download_thumbnails'],
             'service': worker_args_template['service'],
             'user_id': worker_args_template['user_id'],
             'api_url_input': worker_args_template['api_url'], # Pass original URL
             'cancellation_event': self.cancellation_event,
             'signals': self.worker_signals, # Pass the shared signals object
             # Pass shared state and locks
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

            # Create worker with specific post and common args
            worker = PostProcessorWorker(post_data=post_data, **common_worker_args)

            # Submit the worker's process method to the pool
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
                 # Decide whether to continue or break on submission error
                 break


        # Log after submission loop completes or breaks
        submitted_count = len(self.active_futures)
        self.log_signal.emit(f"   {submitted_count} / {self.total_posts_to_process} tasks submitted.")
        # If cancelled during submission, remaining tasks won't run.
        # Fetcher thread's job is done. Callbacks handle the rest.
        # If submission loop finished and submitted_count == total_posts_to_process, check if pool needs shutdown signal?
        # No, shutdown happens in finished_signal handler or closeEvent.



    def _handle_future_result(self, future: Future):
        """(Callback) Handles results from worker threads."""
        # This runs in one of the ThreadPoolExecutor threads, use signals for UI updates
        self.processed_posts_count += 1
        downloaded_res, skipped_res = 0, 0 # Default results

        try:
            if future.cancelled():
                # Task was cancelled before/during execution
                # Count cancelled task as skipped only if it wasn't already counted within the worker
                # The worker's process method should return counts before checking cancel state at the end.
                # Let's assume worker reports counts correctly up to cancellation point.
                 # We don't increment skipped_res here, as the worker should have handled it.
                 pass
            elif future.exception():
                exc = future.exception()
                self.log_signal.emit(f"❌ Error in worker thread: {exc}")
                # Log traceback snippet if helpful
                # import traceback
                # self.log_signal.emit(traceback.format_exc(limit=2))
                # Count errored task as skipped only if it wasn't already handled in worker.
                # Assume worker reports counts correctly up to error point.
                # We don't increment skipped_res here.
                pass
            else:
                # Task completed, get results
                downloaded, skipped = future.result() # Result from worker.process()
                downloaded_res = downloaded
                skipped_res = skipped
                # Log task completion? Might be too verbose.

            # --- Safely update shared counters (using main thread or locks if needed) ---
            # These counters are primarily for the final summary.
            # Direct update is acceptable for progress display with potential minor races.
            # A more robust way uses thread-safe counters (e.g., threading.Lock with counters)
            # Let's use locks for absolute accuracy in the final count.

            with threading.Lock(): # Use a temporary lock for updating these counters
                 self.download_counter += downloaded_res
                 self.skip_counter += skipped_res


            # --- Update Progress ---
            self.overall_progress_signal.emit(self.total_posts_to_process, self.processed_posts_count)

        except Exception as e:
             # Catch errors within the callback itself
             self.log_signal.emit(f"❌ Error in result callback handling: {e}")

        # --- Check for Overall Completion ---
        # This check is tricky due to callbacks running concurrently.
        # Rely on the processed_posts_count reaching total_posts_to_process
        # Ensure this check is race-safe if possible. Using a simple counter is okay for a check-and-signal pattern.
        if self.processed_posts_count >= self.total_posts_to_process and self.total_posts_to_process > 0:
            # Add a small delay to ensure all pending callbacks (if any) have a chance to run
            # This is heuristic and not guaranteed thread-safe completion detection.
            # A more robust solution involves tracking active futures explicitly.
            # Given the current structure, this simple counter check is the most practical.
            # time.sleep(0.1) # Short delay before final check

            # Re-check count just in case
            if self.processed_posts_count >= self.total_posts_to_process:
                 self.log_signal.emit("🏁 All submitted tasks have completed or failed.")
                 cancelled = self.cancellation_event.is_set()
                 # Use the final accumulated counters (updated under lock)
                 self.finished_signal.emit(self.download_counter, self.skip_counter, cancelled)


    # --- UI State Management ---
    def set_ui_enabled(self, enabled):
        """Enable/disable UI controls based on download state."""
        # Controls to disable during download
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
        # self.character_list.setEnabled(enabled) # Keep enabled for Browse
        self.character_search_input.setEnabled(enabled) # ADDED
        self.new_char_input.setEnabled(enabled)
        self.add_char_button.setEnabled(enabled)
        self.delete_char_button.setEnabled(enabled)


        # Enable/disable conditional controls
        subfolders_on = self.use_subfolders_checkbox.isChecked()
        self.custom_folder_widget.setEnabled(enabled and subfolders_on)
        self.character_filter_widget.setEnabled(enabled and subfolders_on)


        # Update visibility if enabling UI
        if enabled:
             self.update_ui_for_subfolders(subfolders_on)
             self.update_custom_folder_visibility() # Update based on current URL

        # Cancel button is enabled only when download is running (UI disabled)
        self.cancel_btn.setEnabled(not enabled)

        # Skip button state is handled separately, reset when UI enabled
        if enabled:
            self.skip_file_btn.setEnabled(False)


    # --- Actions ---
    def cancel_download(self):
        """Requests cancellation of the ongoing download (single or multi-thread)."""
        if not self.cancel_btn.isEnabled(): return # Prevent double clicks

        self.log_signal.emit("⚠️ Requesting cancellation...")
        self.cancellation_event.set() # Set the shared event

        # Disable cancel button immediately to prevent multiple signals
        self.cancel_btn.setEnabled(False)
        self.progress_label.setText("Progress: Cancelling...")

        # Optional: Try to actively cancel futures if using thread pool
        # This might help stop tasks quicker if they check the future status,
        # but reliance on the cancellation_event is the primary mechanism.
        if self.thread_pool and self.active_futures:
            cancelled_count = 0
            for future in self.active_futures:
                if future.cancel(): # Attempts to cancel
                    cancelled_count += 1
            if cancelled_count > 0:
                 self.log_signal.emit(f"   Attempted to cancel {cancelled_count} pending/running tasks.")


    def skip_current_file(self):
         """Signals the active download thread (if single-threaded) to skip the current file."""
         # Check if single-threaded mode is active
         if self.download_thread and self.download_thread.isRunning():
              self.download_thread.skip_file() # Call method on the QThread instance
         elif self.thread_pool:
              self.log_signal.emit("ℹ️ Skipping individual files is not supported in multi-threaded mode.")
              QMessageBox.information(self, "Action Not Supported", "Skipping individual files is only available in single-threaded mode.")
         else:
              self.log_signal.emit("ℹ️ Skip requested,  but no download is active.")


    def update_skip_button_state(self, is_downloading_active):
         """Enables/disables the skip button based on download state."""
         # Enable only if: download running (UI disabled), AND single-thread mode, AND file download active
         can_skip = (not self.download_btn.isEnabled()) and \
                    (self.download_thread and self.download_thread.isRunning()) and \
                    is_downloading_active

         # Explicitly disable if multi-threading was used for this run
         # Check if thread_pool was initialized and is not None
         if self.thread_pool is not None:
             can_skip = False

         self.skip_file_btn.setEnabled(can_skip)


    def download_finished(self, total_downloaded, total_skipped, cancelled):
        """Cleans up resources and resets UI after download completion/cancellation."""
        # Log final status
        self.log_signal.emit("="*40)
        status = "Cancelled" if cancelled else "Finished"
        self.log_signal.emit(f"🏁 Download {status}!")
        self.log_signal.emit(f"   Summary: Downloaded={total_downloaded}, Skipped={total_skipped}")
        self.progress_label.setText(f"{status}: {total_downloaded} downloaded, {total_skipped} skipped.")
        self.log_signal.emit("="*40)


        # --- Cleanup Resources ---
        # QThread cleanup
        if self.download_thread:
            # Disconnect response signal *from* the thread instance
            try:
                 self.character_prompt_response_signal.disconnect(self.download_thread.receive_add_character_result)
            except TypeError: pass # Ignore if not connected
            # QThread should exit naturally after finished signal
            self.download_thread = None


        # ThreadPoolExecutor cleanup
        if self.thread_pool:
            self.log_signal.emit("   Shutting down worker thread pool...")
            # Shutdown non-blockingly, attempt to cancel any remaining futures
            self.thread_pool.shutdown(wait=False, cancel_futures=True)
            self.thread_pool = None
            self.active_futures = [] # Clear future list


        # Reset cancellation event for the next run
        self.cancellation_event.clear()

        # --- Reset UI ---
        self.set_ui_enabled(True)
        # Ensure cancel/skip buttons are disabled
        self.cancel_btn.setEnabled(False)
        self.skip_file_btn.setEnabled(False)


    # --- Character Prompt Handling ---
    # Runs in GUI thread, triggered by signal from DownloadThread
    def prompt_add_character(self, character_name):
         # Ensure prompt mutex is available if needed, though GUI thread access is usually safe
         # with QMutexLocker(self.prompt_mutex): # Might not be strictly necessary here

         reply = QMessageBox.question(self, "Add Filter Name?",
                                      f"The filter name '{character_name}' is not in your known list.\n\nAdd it now and continue download?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
         result = (reply == QMessageBox.Yes)

         if result:
              # Use the existing add method to handle adding, UI update, save
              self.new_char_input.setText(character_name) # Pre-fill for clarity if needed? No, just add.
              # Find the item in the list to simulate adding it if Add button was used
              # Check if already added by another mechanism
              if character_name.lower() not in {n.lower() for n in KNOWN_NAMES}:
                   self.add_new_character() # Add the name
                   # Verify it was added successfully
                   if character_name.lower() not in {n.lower() for n in KNOWN_NAMES}:
                        self.log_signal.emit(f"⚠️ Failed to add '{character_name}' via prompt. Check for errors.")
                        result = False # Treat as failure if not added
              else:
                   self.log_signal.emit(f"ℹ️ Filter name '{character_name}' was already present or added.")

         # Signal the result back to the waiting DownloadThread
         self.character_prompt_response_signal.emit(result)


    # Slot to receive the result for the waiting DownloadThread
    def receive_add_character_result(self, result):
        """Slot to receive the boolean result from the GUI prompt."""
        # This runs in the thread's event loop, triggered by the signal connection
        with QMutexLocker(self.prompt_mutex):
             self._add_character_response = result
        self.log_signal.emit(f"   Received prompt response: {'Yes' if result else 'No'}")


    # Removed start_api_server method
    # def start_api_server(self): ...


# --- Modified DownloadThread for Single-Threaded Mode ---
# This class handles the entire download process when multi-threading is off or for single posts.
class DownloadThread(QThread):
    # Signals emitted by this thread back to the GUI
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


        # Shared state and locks (passed from DownloaderApp)
        self.downloaded_files = downloaded_files if downloaded_files is not None else set()
        self.downloaded_files_lock = downloaded_files_lock if downloaded_files_lock is not None else threading.Lock()
        self.downloaded_file_hashes = downloaded_file_hashes if downloaded_file_hashes is not None else set() # ADDED
        self.downloaded_file_hashes_lock = downloaded_file_hashes_lock if downloaded_file_hashes_lock is not None else threading.Lock() # ADDED


        # Internal state
        self.skip_current_file_flag = threading.Event()
        self.is_downloading_file = False
        self.current_download_path = None
        self._add_character_response = None # Stores response from GUI prompt
        self.prompt_mutex = QMutex() # Protects access to _add_character_response


        # Basic validation in init
        if not self.service or not self.user_id:
             log_msg = f"❌ Thread Init Error: Missing service ('{self.service}') or user ID ('{self.user_id}') for URL '{api_url}'"
             print(log_msg) # Print error as signals might not be connected yet
             # Try emitting signal as well, might work if called after main init
             try: self.progress_signal.emit(log_msg)
             except RuntimeError: pass # Ignore if signal connection fails during init
             self._init_failed = True


    def run(self):
        """Main execution logic for the single-threaded download."""
        if self._init_failed:
             # Error already logged in __init__
             self.finished_signal.emit(0, 0, False) # Signal completion with zero counts
             return

        unwanted_keywords = {'spicy', 'hd', 'nsfw', '4k', 'preview'} # Example unwanted keywords
        grand_total_downloaded = 0
        grand_total_skipped = 0
        cancelled_by_user = False

        try:
            # --- Character Filter Pre-Check ---
            # This check is necessary here because the thread runs independently
            if self.use_subfolders and self.filter_character and not self.custom_folder_name:
                if not self._check_and_prompt_filter_character():
                    # If check fails (invalid, or user declines adding), abort.
                    # Error/reason logged inside the check method.
                    self.finished_signal.emit(0, 0, False) # Not cancelled, aborted by validation/user
                    return


            # --- Setup Worker Instance ---
            # Use the PostProcessorWorker logic for processing each post
            # Create adapter signals object that routes back to this QThread's signals
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
                 # Pass shared state and locks
                 downloaded_files=self.downloaded_files,
                 downloaded_files_lock=self.downloaded_files_lock,
                 downloaded_file_hashes=self.downloaded_file_hashes, # ADDED
                 downloaded_file_hashes_lock=self.downloaded_file_hashes_lock, # ADDED
                 skip_words_list=self.skip_words_list, # --- NEW: Pass skip words to worker ---
            )
            # Allow worker to use this thread's skip flag directly
            post_worker.skip_current_file_flag = self.skip_current_file_flag


            # --- Fetch and Process Posts ---
            self.progress_signal.emit("   Starting post fetch...")
            # Use a local logger function that emits the progress signal
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

                    # Assign post data to the worker instance
                    post_worker.post = post
                    try:
                        # Process the post using the worker's logic
                        downloaded, skipped = post_worker.process()
                        grand_total_downloaded += downloaded
                        grand_total_skipped += skipped
                    except Exception as proc_e:
                         post_id_err = post.get('id', 'N/A') if isinstance(post, dict) else 'N/A'
                         self.progress_signal.emit(f"❌ Error processing post {post_id_err}: {proc_e}")
                         import traceback
                         self.progress_signal.emit(traceback.format_exc(limit=2))
                         grand_total_skipped += 1 # Count post as skipped on error

                    # Brief pause between posts to yield control, keep UI responsive
                    self.msleep(20) # 20 milliseconds

                if cancelled_by_user:
                    break # Exit outer batch loop as well

            # --- Finished Processing ---
            if not cancelled_by_user:
                 self.progress_signal.emit("✅ Post fetching and processing complete.")


        except Exception as e:
            # Catch unexpected errors during the main run loop
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
            # Ensure finished signal is always emitted
            self.finished_signal.emit(grand_total_downloaded, grand_total_skipped, cancelled_by_user)


    def _check_and_prompt_filter_character(self):
        """Validates filter character and prompts user if it's not known. Returns True if OK to proceed."""
        clean_char_filter = clean_folder_name(self.filter_character.lower())
        # Use current known_names list (potentially updated if added via prompt earlier)
        known_names_lower = {name.lower() for name in self.known_names}

        if not clean_char_filter:
             self.progress_signal.emit(f"❌ Filter name '{self.filter_character}' is invalid. Aborting.")
             return False # Invalid filter

        if self.filter_character.lower() not in known_names_lower:
            self.progress_signal.emit(f"❓ Filter '{self.filter_character}' not found in known list.")

            # Reset response flag and signal GUI to ask
            with QMutexLocker(self.prompt_mutex):
                 self._add_character_response = None
            self.add_character_prompt_signal.emit(self.filter_character)

            # Wait loop for response from GUI (via receive_add_character_result)
            self.progress_signal.emit("   Waiting for user confirmation to add filter name...")
            while self._add_character_response is None:
                if self.isInterruptionRequested(): # Check cancellation
                    self.progress_signal.emit("⚠️ Cancelled while waiting for user input on filter name.")
                    return False # Abort if cancelled
                self.msleep(200) # Check every 200ms

            # Process the response stored in self._add_character_response
            if self._add_character_response:
                self.progress_signal.emit(f"✅ User confirmed adding '{self.filter_character}'. Continuing.")
                # Update thread's local list if GUI added it
                if self.filter_character not in self.known_names:
                    self.known_names.append(self.filter_character)
                return True # OK to proceed
            else:
                self.progress_signal.emit(f"❌ User declined to add filter '{self.filter_character}'. Aborting download.")
                return False # User declined, abort

        # Filter character is valid and already known
        return True


    def skip_file(self):
        """Sets the skip flag for the currently downloading file."""
        # Check if a download is actually active (using worker's state)
        # Accessing worker state directly isn't ideal. Use internal flag.
        if self.isRunning() and self.is_downloading_file:
             self.progress_signal.emit("⏭️ Skip requested for current file.")
             self.skip_current_file_flag.set() # Signal the worker's process loop
        elif self.isRunning():
             self.progress_signal.emit("ℹ️ Skip requested, but no file download active.")


    def receive_add_character_result(self, result):
        """Slot to receive the boolean result from the GUI prompt."""
        # This runs in the thread's event loop, triggered by the signal connection
        with QMutexLocker(self.prompt_mutex):
             self._add_character_response = result
        self.progress_signal.emit(f"   Received prompt response: {'Yes' if result else 'No'}")


    def isInterruptionRequested(self):
        """Overrides QThread method to check both interruption flag and shared event."""
        return super().isInterruptionRequested() or self.cancellation_event.is_set()



# --- Main Execution Block ---
if __name__ == '__main__':
    # Set high DPI scaling attribute if needed (Qt 5.6+)
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    qt_app = QApplication(sys.argv)
    # Optional: Apply a style like Fusion for consistency
    # qt_app.setStyle('Fusion')

    downloader = DownloaderApp() # Create the main application window
    downloader.show() # Show the window

    # Start the Qt event loop
    exit_code = qt_app.exec_()

    # Code here runs after the application window is closed
    print(f"Application finished with exit code: {exit_code}")
    sys.exit(exit_code) # Exit the script with the application's exit code