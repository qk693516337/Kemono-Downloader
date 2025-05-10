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
import html

from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMutex, QMutexLocker
from urllib.parse import urlparse
try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow library not found. Please install it: pip install Pillow")
    Image = None


from io import BytesIO

STYLE_POST_TITLE = "post_title"
STYLE_ORIGINAL_NAME = "original_name"

SKIP_SCOPE_FILES = "files"
SKIP_SCOPE_POSTS = "posts"
SKIP_SCOPE_BOTH = "both"

CHAR_SCOPE_TITLE = "title"
CHAR_SCOPE_FILES = "files"
CHAR_SCOPE_BOTH = "both"

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
ARCHIVE_EXTENSIONS = {
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'
}

def is_title_match_for_character(post_title, character_name_filter):
    if not post_title or not character_name_filter:
        return False
    pattern = r"(?i)\b" + re.escape(character_name_filter) + r"\b"
    return bool(re.search(pattern, post_title))

def is_filename_match_for_character(filename, character_name_filter):
    if not filename or not character_name_filter:
        return False
    return character_name_filter.lower() in filename.lower()


def clean_folder_name(name):
    if not isinstance(name, str): name = str(name)
    cleaned = re.sub(r'[^\w\s\-\_\.\(\)]', '', name)
    cleaned = cleaned.strip()
    cleaned = re.sub(r'\s+', '_', cleaned)
    return cleaned if cleaned else "untitled_folder"


def clean_filename(name):
    if not isinstance(name, str): name = str(name)
    cleaned = re.sub(r'[^\w\s\-\_\.\(\)]', '', name)
    cleaned = cleaned.strip()
    cleaned = re.sub(r'\s+', '_', cleaned)
    return cleaned if cleaned else "untitled_file"


def extract_folder_name_from_title(title, unwanted_keywords):
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
    if not filename: return False
    _, ext = os.path.splitext(filename)
    return ext.lower() in IMAGE_EXTENSIONS


def is_video(filename):
    if not filename: return False
    _, ext = os.path.splitext(filename)
    return ext.lower() in VIDEO_EXTENSIONS


def is_zip(filename):
    if not filename: return False
    return filename.lower().endswith('.zip')


def is_rar(filename):
    if not filename: return False
    return filename.lower().endswith('.rar')

def is_archive(filename):
    if not filename: return False
    _, ext = os.path.splitext(filename)
    return ext.lower() in ARCHIVE_EXTENSIONS


def is_post_url(url):
    if not isinstance(url, str): return False
    return '/post/' in urlparse(url).path


def extract_post_info(url_string):
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
            return []
        return response.json()
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Timeout fetching offset {offset} from {paginated_url}")
    except requests.exceptions.RequestException as e:
        err_msg = f"Error fetching offset {offset} from {paginated_url}: {e}"
        if e.response is not None:
            err_msg += f" (Status: {e.response.status_code}, Body: {e.response.text[:200]})"
        raise RuntimeError(err_msg)
    except ValueError as e:
        raise RuntimeError(f"Error decoding JSON from offset {offset} ({paginated_url}): {e}. Response text: {response.text[:200]}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error fetching offset {offset} ({paginated_url}): {e}")


def download_from_api(api_url_input, logger=print, start_page=None, end_page=None, manga_mode=False, cancellation_event=None):
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
        start_page = end_page = None

    is_creator_feed_for_manga = manga_mode and not target_post_id

    parsed_input = urlparse(api_url_input)
    api_domain = parsed_input.netloc
    if not any(d in api_domain.lower() for d in ['kemono.su', 'kemono.party', 'coomer.su', 'coomer.party']):
        logger(f"⚠️ Unrecognized domain '{api_domain}'. Defaulting to kemono.su for API calls.")
        api_domain = "kemono.su"

    api_base_url = f"https://{api_domain}/api/v1/{service}/user/{user_id}"
    page_size = 50

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
                current_offset_manga += len(posts_batch_manga)
                time.sleep(0.6)
            except RuntimeError as e:
                if "cancelled by user" in str(e).lower():
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

    if start_page and start_page > 1 and not target_post_id:
        current_offset = (start_page - 1) * page_size
        current_page_num = start_page
        logger(f"   Starting from page {current_page_num} (calculated offset {current_offset}).")

    while True:
        if cancellation_event and cancellation_event.is_set():
            logger("   Post fetching loop cancelled.")
            break
        
        if target_post_id and processed_target_post_flag:
            break

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
            break
        except Exception as e:
            logger(f"❌ Unexpected error fetching page {current_page_num} (offset {current_offset}): {e}")
            traceback.print_exc()
            break

        if not posts_batch:
            if target_post_id and not processed_target_post_flag:
                logger(f"❌ Target post {target_post_id} not found after checking all available pages (API returned no more posts at offset {current_offset}).")
            elif not target_post_id:
                if current_page_num == (start_page or 1):
                     logger(f"😕 No posts found on the first page checked (page {current_page_num}, offset {current_offset}).")
                else:
                     logger(f"✅ Reached end of posts (no more content from API at offset {current_offset}).")
            break

        if target_post_id and not processed_target_post_flag:
            matching_post = next((p for p in posts_batch if str(p.get('id')) == str(target_post_id)), None)
            if matching_post:
                logger(f"🎯 Found target post {target_post_id} on page {current_page_num} (offset {current_offset}).")
                yield [matching_post]
                processed_target_post_flag = True
        elif not target_post_id:
            yield posts_batch

        if processed_target_post_flag:
            break

        current_offset += len(posts_batch)
        current_page_num += 1
        time.sleep(0.6)
            
    if target_post_id and not processed_target_post_flag and not (cancellation_event and cancellation_event.is_set()):
        logger(f"❌ Target post {target_post_id} could not be found after checking all relevant pages (final check after loop).")


def get_link_platform(url):
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
    progress_signal = pyqtSignal(str)
    file_download_status_signal = pyqtSignal(bool)
    external_link_signal = pyqtSignal(str, str, str, str)
    file_progress_signal = pyqtSignal(str, int, int)


class PostProcessorWorker:
    def __init__(self, post_data, download_root, known_names,
                 filter_character_list,
                 unwanted_keywords, filter_mode, skip_zip, skip_rar,
                 use_subfolders, use_post_subfolders, target_post_id_from_initial_url, custom_folder_name,
                 compress_images, download_thumbnails, service, user_id,
                 api_url_input, cancellation_event, signals,
                 downloaded_files, downloaded_file_hashes, downloaded_files_lock, downloaded_file_hashes_lock,
                 skip_words_list=None, 
                 skip_words_scope=SKIP_SCOPE_FILES,
                 show_external_links=False,
                 extract_links_only=False,
                 num_file_threads=4, skip_current_file_flag=None,
                 manga_mode_active=False,
                 manga_filename_style=STYLE_POST_TITLE,
                 char_filter_scope=CHAR_SCOPE_FILES
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
        self.skip_words_scope = skip_words_scope
        self.show_external_links = show_external_links
        self.extract_links_only = extract_links_only
        self.num_file_threads = num_file_threads

        self.manga_mode_active = manga_mode_active
        self.manga_filename_style = manga_filename_style
        self.char_filter_scope = char_filter_scope

        if self.compress_images and Image is None:
            self.logger("⚠️ Image compression disabled: Pillow library not found.")
            self.compress_images = False

    def logger(self, message):
        if self.signals and hasattr(self.signals, 'progress_signal'):
            self.signals.progress_signal.emit(message)
        else:
            print(f"(Worker Log - No Signal): {message}")

    def check_cancel(self):
        return self.cancellation_event.is_set()

    def _download_single_file(self, file_info, target_folder_path, headers, original_post_id_for_log, skip_event,
                              post_title="", file_index_in_post=0, num_files_in_this_post=1):
        was_original_name_kept_flag = False 
        final_filename_saved_for_return = ""


        if self.check_cancel() or (skip_event and skip_event.is_set()): return 0, 1, "", False

        file_url = file_info.get('url')
        api_original_filename = file_info.get('_original_name_for_log', file_info.get('name'))
        
        final_filename_saved_for_return = api_original_filename 

        if self.skip_words_list and (self.skip_words_scope == SKIP_SCOPE_FILES or self.skip_words_scope == SKIP_SCOPE_BOTH):
            filename_to_check_for_skip_words = api_original_filename.lower()
            for skip_word in self.skip_words_list:
                if skip_word.lower() in filename_to_check_for_skip_words:
                    self.logger(f"   -> Skip File (Keyword in Original Name '{skip_word}'): '{api_original_filename}'. Scope: {self.skip_words_scope}")
                    return 0, 1, api_original_filename, False
        
        original_filename_cleaned_base, original_ext = os.path.splitext(clean_filename(api_original_filename))
        if not original_ext.startswith('.'): original_ext = '.' + original_ext if original_ext else ''

        filename_to_save = ""
        if self.manga_mode_active:
            if self.manga_filename_style == STYLE_ORIGINAL_NAME:
                filename_to_save = clean_filename(api_original_filename)
                was_original_name_kept_flag = True
            elif self.manga_filename_style == STYLE_POST_TITLE:
                if post_title and post_title.strip():
                    cleaned_post_title_base = clean_filename(post_title.strip())
                    if num_files_in_this_post > 1:
                        if file_index_in_post == 0:
                            filename_to_save = f"{cleaned_post_title_base}{original_ext}"
                            was_original_name_kept_flag = False
                        else:
                            filename_to_save = clean_filename(api_original_filename)
                            was_original_name_kept_flag = True 
                    else:
                        filename_to_save = f"{cleaned_post_title_base}{original_ext}"
                        was_original_name_kept_flag = False
                else:
                    filename_to_save = clean_filename(api_original_filename)
                    was_original_name_kept_flag = False
                    self.logger(f"⚠️ Manga mode (Post Title Style): Post title missing for post {original_post_id_for_log}. Using cleaned original filename '{filename_to_save}'.")
            else:
                self.logger(f"⚠️ Manga mode: Unknown filename style '{self.manga_filename_style}'. Defaulting to original filename for '{api_original_filename}'.")
                filename_to_save = clean_filename(api_original_filename)
                was_original_name_kept_flag = False

            if filename_to_save:
                counter = 1
                base_name_coll, ext_coll = os.path.splitext(filename_to_save)
                temp_filename_for_collision_check = filename_to_save
                while os.path.exists(os.path.join(target_folder_path, temp_filename_for_collision_check)):
                    if self.manga_filename_style == STYLE_POST_TITLE and file_index_in_post == 0 and num_files_in_this_post > 1:
                         temp_filename_for_collision_check = f"{base_name_coll}_{counter}{ext_coll}"
                    else:
                         temp_filename_for_collision_check = f"{base_name_coll}_{counter}{ext_coll}"
                    counter += 1
                if temp_filename_for_collision_check != filename_to_save:
                    filename_to_save = temp_filename_for_collision_check
            else:
                filename_to_save = f"manga_file_{original_post_id_for_log}_{file_index_in_post + 1}{original_ext}"
                self.logger(f"⚠️ Manga mode: Generated filename was empty. Using generic fallback: '{filename_to_save}'.")
                was_original_name_kept_flag = False

        else:
            filename_to_save = clean_filename(api_original_filename)
            was_original_name_kept_flag = False
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
            is_img_type = is_image(api_original_filename)
            is_vid_type = is_video(api_original_filename)
            is_archive_type = is_archive(api_original_filename)


            if self.filter_mode == 'archive':
                if not is_archive_type:
                    self.logger(f"   -> Filter Skip (Archive Mode): '{api_original_filename}' (Not an Archive).")
                    return 0, 1, api_original_filename, False
            elif self.filter_mode == 'image':
                if not is_img_type:
                    self.logger(f"   -> Filter Skip: '{api_original_filename}' (Not Image).")
                    return 0, 1, api_original_filename, False
            elif self.filter_mode == 'video':
                if not is_vid_type:
                    self.logger(f"   -> Filter Skip: '{api_original_filename}' (Not Video).")
                    return 0, 1, api_original_filename, False

            if self.skip_zip and is_zip(api_original_filename):
                self.logger(f"   -> Pref Skip: '{api_original_filename}' (ZIP).")
                return 0, 1, api_original_filename, False
            if self.skip_rar and is_rar(api_original_filename):
                self.logger(f"   -> Pref Skip: '{api_original_filename}' (RAR).")
                return 0, 1, api_original_filename, False

        target_folder_basename = os.path.basename(target_folder_path)
        current_save_path = os.path.join(target_folder_path, final_filename_for_sets_and_saving)

        if os.path.exists(current_save_path) and os.path.getsize(current_save_path) > 0:
             self.logger(f"   -> Exists (Path): '{final_filename_for_sets_and_saving}' in '{target_folder_basename}'.")
             with self.downloaded_files_lock: self.downloaded_files.add(final_filename_for_sets_and_saving)
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
        total_size_bytes = 0
        download_successful_flag = False

        for attempt_num in range(max_retries + 1):
            if self.check_cancel() or (skip_event and skip_event.is_set()):
                break
            try:
                if attempt_num > 0:
                    self.logger(f"   Retrying '{api_original_filename}' (Attempt {attempt_num}/{max_retries})...")
                    time.sleep(retry_delay * (2**(attempt_num - 1)))

                if self.signals and hasattr(self.signals, 'file_download_status_signal'):
                    self.signals.file_download_status_signal.emit(True)

                response = requests.get(file_url, headers=headers, timeout=(15, 300), stream=True)
                response.raise_for_status()

                current_total_size_bytes_from_headers = int(response.headers.get('Content-Length', 0))

                if attempt_num == 0:
                    total_size_bytes = current_total_size_bytes_from_headers
                    size_str = f"{total_size_bytes / (1024 * 1024):.2f} MB" if total_size_bytes > 0 else "unknown size"
                    self.logger(f"⬇️ Downloading: '{api_original_filename}' (Size: {size_str}) [Saving as: '{final_filename_for_sets_and_saving}']")

                current_attempt_total_size = total_size_bytes
                
                file_content_buffer = BytesIO()
                current_attempt_downloaded_bytes = 0
                md5_hasher = hashlib.md5()
                last_progress_time = time.time()

                for chunk in response.iter_content(chunk_size=1 * 1024 * 1024):
                    if self.check_cancel() or (skip_event and skip_event.is_set()):
                        break
                    if chunk:
                        file_content_buffer.write(chunk)
                        md5_hasher.update(chunk)
                        current_attempt_downloaded_bytes += len(chunk)
                        if time.time() - last_progress_time > 1 and current_attempt_total_size > 0 and \
                           self.signals and hasattr(self.signals, 'file_progress_signal'):
                            self.signals.file_progress_signal.emit(
                                api_original_filename,
                                current_attempt_downloaded_bytes,
                                current_attempt_total_size
                            )
                            last_progress_time = time.time()
                
                if self.check_cancel() or (skip_event and skip_event.is_set()):
                    if file_content_buffer: file_content_buffer.close()
                    break
                
                if current_attempt_downloaded_bytes > 0 or (current_attempt_total_size == 0 and response.status_code == 200):
                    calculated_file_hash = md5_hasher.hexdigest()
                    downloaded_size_bytes = current_attempt_downloaded_bytes
                    if file_content_bytes: file_content_bytes.close()
                    file_content_bytes = file_content_buffer
                    file_content_bytes.seek(0)
                    download_successful_flag = True
                    break
                else:
                    if file_content_buffer: file_content_buffer.close()

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, http.client.IncompleteRead) as e:
                self.logger(f"   ❌ Download Error (Retryable): {api_original_filename}. Error: {e}")
                if 'file_content_buffer' in locals() and file_content_buffer: file_content_buffer.close()
            except requests.exceptions.RequestException as e:
                self.logger(f"   ❌ Download Error (Non-Retryable): {api_original_filename}. Error: {e}")
                if 'file_content_buffer' in locals() and file_content_buffer: file_content_buffer.close()
                break
            except Exception as e:
                self.logger(f"   ❌ Unexpected Download Error: {api_original_filename}: {e}\n{traceback.format_exc(limit=2)}")
                if 'file_content_buffer' in locals() and file_content_buffer: file_content_buffer.close()
                break
            finally:
                if self.signals and hasattr(self.signals, 'file_download_status_signal'):
                    self.signals.file_download_status_signal.emit(False)
        
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

        with self.downloaded_file_hashes_lock:
             if calculated_file_hash in self.downloaded_file_hashes:
                self.logger(f"   -> Content Skip (Hash): '{api_original_filename}' (Hash: {calculated_file_hash[:8]}...) already downloaded this session.")
                with self.downloaded_files_lock: self.downloaded_files.add(final_filename_for_sets_and_saving)
                if file_content_bytes: file_content_bytes.close()
                return 0, 1, final_filename_for_sets_and_saving, was_original_name_kept_flag

        bytes_to_write = file_content_bytes
        final_filename_after_processing = final_filename_for_sets_and_saving
        current_save_path_final = current_save_path

        is_img_for_compress_check = is_image(api_original_filename)
        if is_img_for_compress_check and self.compress_images and Image and downloaded_size_bytes > (1.5 * 1024 * 1024):
            self.logger(f"   Compressing '{api_original_filename}' ({downloaded_size_bytes / (1024*1024):.2f} MB)...")
            try:
                bytes_to_write.seek(0)
                with Image.open(bytes_to_write) as img_obj:
                    if img_obj.mode == 'P': img_obj = img_obj.convert('RGBA')
                    elif img_obj.mode not in ['RGB', 'RGBA', 'L']: img_obj = img_obj.convert('RGB')

                    compressed_bytes_io = BytesIO()
                    img_obj.save(compressed_bytes_io, format='WebP', quality=80, method=4)
                    compressed_size = compressed_bytes_io.getbuffer().nbytes

                if compressed_size < downloaded_size_bytes * 0.9:
                    self.logger(f"   Compression success: {compressed_size / (1024*1024):.2f} MB.")
                    bytes_to_write.close()
                    bytes_to_write = compressed_bytes_io
                    bytes_to_write.seek(0)

                    base_name_orig, _ = os.path.splitext(final_filename_for_sets_and_saving)
                    final_filename_after_processing = base_name_orig + '.webp'
                    current_save_path_final = os.path.join(target_folder_path, final_filename_after_processing)
                    self.logger(f"   Updated filename (compressed): {final_filename_after_processing}")
                else:
                    self.logger(f"   Compression skipped: WebP not significantly smaller."); bytes_to_write.seek(0)
            except Exception as comp_e:
                self.logger(f"❌ Compression failed for '{api_original_filename}': {comp_e}. Saving original."); bytes_to_write.seek(0)

        final_filename_saved_for_return = final_filename_after_processing

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
            with self.downloaded_files_lock: self.downloaded_files.add(final_filename_after_processing)

            self.logger(f"✅ Saved: '{final_filename_after_processing}' (from '{api_original_filename}', {downloaded_size_bytes / (1024*1024):.2f} MB) in '{target_folder_basename}'")
            time.sleep(0.05)
            return 1, 0, final_filename_after_processing, was_original_name_kept_flag
        except Exception as save_err:
             self.logger(f"❌ Save Fail for '{final_filename_after_processing}': {save_err}")
             if os.path.exists(current_save_path_final):
                  try: os.remove(current_save_path_final);
                  except OSError: self.logger(f"  -> Failed to remove partially saved file: {current_save_path_final}")
             return 0, 1, final_filename_saved_for_return, was_original_name_kept_flag
        finally:
            if bytes_to_write: bytes_to_write.close()


    def process(self):
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
        post_main_file_info = post_data.get('file')
        post_attachments = post_data.get('attachments', [])
        post_content_html = post_data.get('content', '')

        self.logger(f"\n--- Processing Post {post_id} ('{post_title[:50]}...') (Thread: {threading.current_thread().name}) ---")

        num_potential_files_in_post = len(post_attachments or []) + (1 if post_main_file_info and post_main_file_info.get('path') else 0)

        post_is_candidate_by_title_char_match = False
        char_filter_that_matched_title = None

        if self.filter_character_list and \
           (self.char_filter_scope == CHAR_SCOPE_TITLE or self.char_filter_scope == CHAR_SCOPE_BOTH):
            for char_name in self.filter_character_list:
                if is_title_match_for_character(post_title, char_name):
                    post_is_candidate_by_title_char_match = True
                    char_filter_that_matched_title = char_name
                    self.logger(f"   Post title matches char filter '{char_name}' (Scope: {self.char_filter_scope}). Post is candidate.")
                    break
        
        if self.filter_character_list and self.char_filter_scope == CHAR_SCOPE_TITLE and not post_is_candidate_by_title_char_match:
            self.logger(f"   -> Skip Post (Scope: Title - No Char Match): Title '{post_title[:50]}' does not match character filters.")
            return 0, num_potential_files_in_post, []

        if self.skip_words_list and (self.skip_words_scope == SKIP_SCOPE_POSTS or self.skip_words_scope == SKIP_SCOPE_BOTH):
            post_title_lower = post_title.lower()
            for skip_word in self.skip_words_list:
                if skip_word.lower() in post_title_lower:
                    self.logger(f"   -> Skip Post (Keyword in Title '{skip_word}'): '{post_title[:50]}...'. Scope: {self.skip_words_scope}")
                    return 0, num_potential_files_in_post, []

        if not self.extract_links_only and self.manga_mode_active and self.filter_character_list and \
           (self.char_filter_scope == CHAR_SCOPE_TITLE or self.char_filter_scope == CHAR_SCOPE_BOTH) and \
           not post_is_candidate_by_title_char_match:
            self.logger(f"   -> Skip Post (Manga Mode with Title/Both Scope - No Title Char Match): Title '{post_title[:50]}' doesn't match filters.")
            return 0, num_potential_files_in_post, []

        if not isinstance(post_attachments, list):
            self.logger(f"⚠️ Corrupt attachment data for post {post_id} (expected list, got {type(post_attachments)}). Skipping attachments.")
            post_attachments = []

        base_folder_names_for_post_content = []
        if not self.extract_links_only and self.use_subfolders:
            if post_is_candidate_by_title_char_match and char_filter_that_matched_title:
                base_folder_names_for_post_content = [clean_folder_name(char_filter_that_matched_title)]
            else:
                derived_folders = match_folders_from_title(post_title, self.known_names, self.unwanted_keywords)
                if derived_folders:
                    base_folder_names_for_post_content.extend(derived_folders)
                else:
                    base_folder_names_for_post_content.append(extract_folder_name_from_title(post_title, self.unwanted_keywords))
                if not base_folder_names_for_post_content or not base_folder_names_for_post_content[0]:
                    base_folder_names_for_post_content = [clean_folder_name(post_title if post_title else "untitled_creator_content")]
            self.logger(f"   Base folder name(s) for post content (if title matched char or generic): {', '.join(base_folder_names_for_post_content)}")

        if not self.extract_links_only and self.use_subfolders and self.skip_words_list:
            for folder_name_to_check in base_folder_names_for_post_content:
                if not folder_name_to_check: continue
                if any(skip_word.lower() in folder_name_to_check.lower() for skip_word in self.skip_words_list):
                    matched_skip = next((sw for sw in self.skip_words_list if sw.lower() in folder_name_to_check.lower()), "unknown_skip_word")
                    self.logger(f"   -> Skip Post (Folder Keyword): Potential folder '{folder_name_to_check}' contains '{matched_skip}'.")
                    return 0, num_potential_files_in_post, []

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
            return 0, 0, []

        all_files_from_post_api = []
        api_file_domain = urlparse(self.api_url_input).netloc
        if not api_file_domain or not any(d in api_file_domain.lower() for d in ['kemono.su', 'kemono.party', 'coomer.su', 'coomer.party']):
            api_file_domain = "kemono.su" if "kemono" in self.service.lower() else "coomer.party"


        if post_main_file_info and isinstance(post_main_file_info, dict) and post_main_file_info.get('path'):
            file_path = post_main_file_info['path'].lstrip('/')
            original_api_name = post_main_file_info.get('name') or os.path.basename(file_path)
            if original_api_name:
                all_files_from_post_api.append({
                    'url': f"https://{api_file_domain}{file_path}" if file_path.startswith('/') else f"https://{api_file_domain}/data/{file_path}",
                    'name': original_api_name,
                    '_original_name_for_log': original_api_name,
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

        if self.download_thumbnails:
            all_files_from_post_api = [finfo for finfo in all_files_from_post_api if finfo['_is_thumbnail']]
            if not all_files_from_post_api:
                 self.logger(f"   -> No image thumbnails found for post {post_id} in thumbnail-only mode.")
                 return 0, 0, []


        if not all_files_from_post_api:
            self.logger(f"   No files found to download for post {post_id}.")
            return 0, 0, []

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

                current_api_original_filename = file_info_to_dl.get('_original_name_for_log')
                
                file_is_candidate_by_char_filter_scope = False
                char_filter_that_matched_file = None

                if not self.filter_character_list:
                    file_is_candidate_by_char_filter_scope = True
                elif self.char_filter_scope == CHAR_SCOPE_FILES:
                    for char_name in self.filter_character_list:
                        if is_filename_match_for_character(current_api_original_filename, char_name):
                            file_is_candidate_by_char_filter_scope = True
                            char_filter_that_matched_file = char_name
                            break
                elif self.char_filter_scope == CHAR_SCOPE_TITLE:
                    if post_is_candidate_by_title_char_match:
                        file_is_candidate_by_char_filter_scope = True
                elif self.char_filter_scope == CHAR_SCOPE_BOTH:
                    if post_is_candidate_by_title_char_match:
                        file_is_candidate_by_char_filter_scope = True
                    else:
                        for char_name in self.filter_character_list:
                            if is_filename_match_for_character(current_api_original_filename, char_name):
                                file_is_candidate_by_char_filter_scope = True
                                char_filter_that_matched_file = char_name
                                break
                
                if not file_is_candidate_by_char_filter_scope:
                    self.logger(f"   -> Skip File (Char Filter Scope '{self.char_filter_scope}'): '{current_api_original_filename}' no match.")
                    total_skipped_this_post += 1
                    continue

                current_path_for_file = self.download_root

                if self.use_subfolders:
                    char_title_subfolder_name = None
                    if self.target_post_id_from_initial_url and self.custom_folder_name:
                        char_title_subfolder_name = self.custom_folder_name
                    elif char_filter_that_matched_title:
                        char_title_subfolder_name = clean_folder_name(char_filter_that_matched_title)
                    elif char_filter_that_matched_file:
                        char_title_subfolder_name = clean_folder_name(char_filter_that_matched_file)
                    elif base_folder_names_for_post_content:
                        char_title_subfolder_name = base_folder_names_for_post_content[0]
                    
                    if char_title_subfolder_name:
                        current_path_for_file = os.path.join(current_path_for_file, char_title_subfolder_name)
                
                if self.use_post_subfolders:
                    cleaned_title_for_subfolder = clean_folder_name(post_title)
                    post_specific_subfolder_name = f"{post_id}_{cleaned_title_for_subfolder}" if cleaned_title_for_subfolder else f"{post_id}_untitled"
                    current_path_for_file = os.path.join(current_path_for_file, post_specific_subfolder_name)
                
                target_folder_path_for_this_file = current_path_for_file
                
                futures_list.append(file_pool.submit(
                    self._download_single_file,
                    file_info_to_dl,
                    target_folder_path_for_this_file,
                    headers,
                    post_id,
                    self.skip_current_file_flag,
                    post_title,
                    file_idx, 
                    num_files_in_this_post_for_naming 
                ))

            for future in as_completed(futures_list):
                if self.check_cancel():
                    for f_to_cancel in futures_list:
                        if not f_to_cancel.done():
                            f_to_cancel.cancel()
                    break
                try:
                    dl_count, skip_count, actual_filename_saved, original_kept_flag = future.result()
                    total_downloaded_this_post += dl_count
                    total_skipped_this_post += skip_count
                    if original_kept_flag and dl_count > 0 and actual_filename_saved:
                        kept_original_filenames_for_log.append(actual_filename_saved)
                except CancelledError:
                    self.logger(f"   File download task for post {post_id} was cancelled.")
                    total_skipped_this_post += 1
                except Exception as exc_f:
                    self.logger(f"❌ File download task for post {post_id} resulted in error: {exc_f}")
                    total_skipped_this_post += 1
        
        if self.signals and hasattr(self.signals, 'file_progress_signal'):
            self.signals.file_progress_signal.emit("", 0, 0)

        if self.check_cancel(): self.logger(f"   Post {post_id} processing interrupted/cancelled.");
        else: self.logger(f"   Post {post_id} Summary: Downloaded={total_downloaded_this_post}, Skipped Files={total_skipped_this_post}")

        return total_downloaded_this_post, total_skipped_this_post, kept_original_filenames_for_log


class DownloadThread(QThread):
    progress_signal = pyqtSignal(str)
    add_character_prompt_signal = pyqtSignal(str)
    file_download_status_signal = pyqtSignal(bool)
    finished_signal = pyqtSignal(int, int, bool, list)
    external_link_signal = pyqtSignal(str, str, str, str)
    file_progress_signal = pyqtSignal(str, int, int)


    def __init__(self, api_url_input, output_dir, known_names_copy,
                 cancellation_event,
                 filter_character_list=None,
                 filter_mode='all', skip_zip=True, skip_rar=True,
                 use_subfolders=True, use_post_subfolders=False, custom_folder_name=None, compress_images=False,
                 download_thumbnails=False, service=None, user_id=None,
                 downloaded_files=None, downloaded_file_hashes=None, downloaded_files_lock=None, downloaded_file_hashes_lock=None,
                 skip_words_list=None,
                 skip_words_scope=SKIP_SCOPE_FILES, 
                 show_external_links=False,
                 extract_links_only=False,
                 num_file_threads_for_worker=1,
                 skip_current_file_flag=None,
                 start_page=None, end_page=None,
                 target_post_id_from_initial_url=None,
                 manga_mode_active=False,
                 unwanted_keywords=None,
                 manga_filename_style=STYLE_POST_TITLE,
                 char_filter_scope=CHAR_SCOPE_FILES
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
        self.skip_words_scope = skip_words_scope
        self.downloaded_files = downloaded_files
        self.downloaded_files_lock = downloaded_files_lock
        self.downloaded_file_hashes = downloaded_file_hashes
        self.downloaded_file_hashes_lock = downloaded_file_hashes_lock
        
        self._add_character_response = None
        self.prompt_mutex = QMutex()
        
        self.show_external_links = show_external_links
        self.extract_links_only = extract_links_only
        self.num_file_threads_for_worker = num_file_threads_for_worker
        self.start_page = start_page
        self.end_page = end_page
        self.manga_mode_active = manga_mode_active
        self.unwanted_keywords = unwanted_keywords if unwanted_keywords is not None else \
                                 {'spicy', 'hd', 'nsfw', '4k', 'preview', 'teaser', 'clip'}
        self.manga_filename_style = manga_filename_style
        self.char_filter_scope = char_filter_scope

        if self.compress_images and Image is None:
            self.logger("⚠️ Image compression disabled: Pillow library not found (DownloadThread).")
            self.compress_images = False

    def logger(self, message):
        self.progress_signal.emit(str(message))

    def isInterruptionRequested(self):
        return self.cancellation_event.is_set() or super().isInterruptionRequested()


    def skip_file(self):
        if self.isRunning() and self.skip_current_file_flag:
             self.logger("⏭️ Skip requested for current file (single-thread mode).")
             self.skip_current_file_flag.set()
        else: self.logger("ℹ️ Skip file: No download active or skip flag not available for current context.")


    def run(self):
        grand_total_downloaded_files = 0
        grand_total_skipped_files = 0
        grand_list_of_kept_original_filenames = [] 
        was_process_cancelled = False

        worker_signals_obj = PostProcessorSignals()
        try:
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
                cancellation_event=self.cancellation_event
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
                         signals=worker_signals_obj,
                         downloaded_files=self.downloaded_files,
                         downloaded_file_hashes=self.downloaded_file_hashes,
                         downloaded_files_lock=self.downloaded_files_lock,
                         downloaded_file_hashes_lock=self.downloaded_file_hashes_lock,
                         skip_words_list=self.skip_words_list,
                         skip_words_scope=self.skip_words_scope,
                         show_external_links=self.show_external_links,
                         extract_links_only=self.extract_links_only,
                         num_file_threads=self.num_file_threads_for_worker,
                         skip_current_file_flag=self.skip_current_file_flag,
                         manga_mode_active=self.manga_mode_active,
                         manga_filename_style=self.manga_filename_style,
                         char_filter_scope=self.char_filter_scope
                    )
                    try:
                        dl_count, skip_count, kept_originals_this_post = post_processing_worker.process()
                        grand_total_downloaded_files += dl_count
                        grand_total_skipped_files += skip_count
                        if kept_originals_this_post:
                            grand_list_of_kept_original_filenames.extend(kept_originals_this_post)
                    except Exception as proc_err:
                         post_id_for_err = individual_post_data.get('id', 'N/A')
                         self.logger(f"❌ Error processing post {post_id_for_err} in DownloadThread: {proc_err}")
                         traceback.print_exc()
                         num_potential_files_est = len(individual_post_data.get('attachments', [])) + \
                                                   (1 if individual_post_data.get('file') else 0)
                         grand_total_skipped_files += num_potential_files_est

                    if self.skip_current_file_flag and self.skip_current_file_flag.is_set():
                        self.skip_current_file_flag.clear()
                        self.logger("   Skip current file flag was processed and cleared by DownloadThread.")
                    
                    self.msleep(10)
                if was_process_cancelled: break

            if not was_process_cancelled and not self.isInterruptionRequested():
                 self.logger("✅ All posts processed or end of content reached by DownloadThread.")

        except Exception as main_thread_err:
            self.logger(f"\n❌ Critical error within DownloadThread run loop: {main_thread_err}")
            traceback.print_exc()
            if not self.isInterruptionRequested(): was_process_cancelled = False 
        finally:
            try:
                if worker_signals_obj:
                    worker_signals_obj.progress_signal.disconnect(self.progress_signal)
                    worker_signals_obj.file_download_status_signal.disconnect(self.file_download_status_signal)
                    worker_signals_obj.external_link_signal.disconnect(self.external_link_signal)
                    worker_signals_obj.file_progress_signal.disconnect(self.file_progress_signal)
            except (TypeError, RuntimeError) as e:
                self.logger(f"ℹ️ Note during DownloadThread signal disconnection: {e}")
            
            self.finished_signal.emit(grand_total_downloaded_files, grand_total_skipped_files, self.isInterruptionRequested(), grand_list_of_kept_original_filenames)

    def receive_add_character_result(self, result):
        with QMutexLocker(self.prompt_mutex):
             self._add_character_response = result
        self.logger(f"   (DownloadThread) Received character prompt response: {'Yes (added/confirmed)' if result else 'No (declined/failed)'}")
