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

try:
    from multipart_downloader import download_file_in_parts
    MULTIPART_DOWNLOADER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: multipart_downloader.py not found or import error: {e}. Multi-part downloads will be disabled.")
    MULTIPART_DOWNLOADER_AVAILABLE = False
    def download_file_in_parts(*args, **kwargs): return False, 0, None, None # Dummy function

from io import BytesIO

STYLE_POST_TITLE = "post_title"
STYLE_ORIGINAL_NAME = "original_name"
STYLE_DATE_BASED = "date_based" # For manga date-based sequential naming
MANGA_DATE_PREFIX_DEFAULT = "" # Default for the new prefix
STYLE_POST_TITLE_GLOBAL_NUMBERING = "post_title_global_numbering" # For manga post title + global counter

SKIP_SCOPE_FILES = "files"
SKIP_SCOPE_POSTS = "posts"
SKIP_SCOPE_BOTH = "both"

CHAR_SCOPE_TITLE = "title"
CHAR_SCOPE_FILES = "files"
CHAR_SCOPE_BOTH = "both"
CHAR_SCOPE_COMMENTS = "comments"

FILE_DOWNLOAD_STATUS_SUCCESS = "success"
FILE_DOWNLOAD_STATUS_SKIPPED = "skipped"
FILE_DOWNLOAD_STATUS_FAILED_RETRYABLE_LATER = "failed_retry_later"

fastapi_app = None
KNOWN_NAMES = [] # This will now store dicts: {'name': str, 'is_group': bool, 'aliases': list[str]}

MIN_SIZE_FOR_MULTIPART_DOWNLOAD = 10 * 1024 * 1024  # 10 MB - Stays the same
MAX_PARTS_FOR_MULTIPART_DOWNLOAD = 15 # Max concurrent connections for a single file

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
def parse_cookie_string(cookie_string):
    """Parses a 'name=value; name2=value2' cookie string into a dict."""
    cookies = {}
    if cookie_string:
        for item in cookie_string.split(';'):
            parts = item.split('=', 1)
            if len(parts) == 2:
                name = parts[0].strip()
                value = parts[1].strip()
                if name: # Ensure name is not empty
                    cookies[name] = value
    return cookies if cookies else None

def load_cookies_from_netscape_file(filepath, logger_func):
    """Loads cookies from a Netscape-formatted cookies.txt file."""
    cookies = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split('\t')
                if len(parts) == 7:
                    name = parts[5]
                    value = parts[6]
                    if name: # Ensure name is not empty
                        cookies[name] = value
        logger_func(f"   🍪 Loaded {len(cookies)} cookies from '{os.path.basename(filepath)}'.")
        return cookies if cookies else None
    except FileNotFoundError:
        logger_func(f"   🍪 Cookie file '{os.path.basename(filepath)}' not found at expected location.")
        return None
    except Exception as e:
        logger_func(f"   🍪 Error parsing cookie file '{os.path.basename(filepath)}': {e}")
        return None

def is_title_match_for_character(post_title, character_name_filter):
    if not post_title or not character_name_filter:
        return False
    safe_filter = str(character_name_filter).strip()
    if not safe_filter: 
        return False
        
    pattern = r"(?i)\b" + re.escape(safe_filter) + r"\b"
    match_result = bool(re.search(pattern, post_title))
    return match_result

def is_filename_match_for_character(filename, character_name_filter):
    if not filename or not character_name_filter:
        return False
    
    safe_filter = str(character_name_filter).strip().lower()
    if not safe_filter:
        return False
        
    match_result = safe_filter in filename.lower()
    return match_result


def clean_folder_name(name):
    if not isinstance(name, str): name = str(name)
    cleaned = re.sub(r'[^\w\s\-\_\.\(\)]', '', name)
    cleaned = cleaned.strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)

    if not cleaned: # If empty after initial cleaning
        return "untitled_folder"
    temp_name = cleaned
    while len(temp_name) > 0 and (temp_name.endswith('.') or temp_name.endswith(' ')):
        temp_name = temp_name[:-1]
    return temp_name if temp_name else "untitled_folder"


def clean_filename(name):
    if not isinstance(name, str): name = str(name)
    cleaned = re.sub(r'[^\w\s\-\_\.\(\)]', '', name)
    cleaned = cleaned.strip() # Remove leading/trailing spaces first
    cleaned = re.sub(r'\s+', ' ', cleaned) # Replace multiple internal spaces with a single space
    return cleaned if cleaned else "untitled_file"

def strip_html_tags(html_text):
    if not html_text: return ""
    text = html.unescape(html_text)
    clean_pattern = re.compile('<.*?>')
    cleaned_text = re.sub(clean_pattern, '', text)
    return cleaned_text.strip()

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
    """
    Matches folder names from a title based on a list of known name objects.
    Each name object in names_to_match is expected to be a dict:
    {'name': 'PrimaryFolderName', 'aliases': ['alias1', 'alias2', ...]}
    """    
    if not title or not names_to_match: return []
    title_lower = title.lower()
    matched_cleaned_names = set()
    sorted_name_objects = sorted(names_to_match, key=lambda x: len(x.get("name", "")), reverse=True)

    for name_obj in sorted_name_objects:
        primary_folder_name = name_obj.get("name")
        aliases = name_obj.get("aliases", [])
        if not primary_folder_name or not aliases:
            continue

        for alias in aliases:
            alias_lower = alias.lower()
            if not alias_lower: continue
            pattern = r'\b' + re.escape(alias_lower) + r'\b'
            if re.search(pattern, title_lower):
                cleaned_primary_name = clean_folder_name(primary_folder_name)
                if cleaned_primary_name.lower() not in unwanted_keywords:
                    matched_cleaned_names.add(cleaned_primary_name)
                    break # Found a match for this primary name via one of its aliases
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


def prepare_cookies_for_request(use_cookie_flag, cookie_text_input, selected_cookie_file_path, app_base_dir, logger_func):
    """Prepares a cookie dictionary from text input or cookies.txt file."""
    if not use_cookie_flag:
        return None

    if cookie_text_input:
        logger_func("   🍪 Using cookies from UI text input.")
        return parse_cookie_string(cookie_text_input)
    elif selected_cookie_file_path:
        logger_func(f"   🍪 Attempting to load cookies from selected file: '{os.path.basename(selected_cookie_file_path)}'...")
        return load_cookies_from_netscape_file(selected_cookie_file_path, logger_func)
    elif app_base_dir:
        cookies_filepath = os.path.join(app_base_dir, "cookies.txt")
        logger_func(f"   🍪 No UI text or specific file selected. Attempting to load default '{os.path.basename(cookies_filepath)}' from app directory...")
        return load_cookies_from_netscape_file(cookies_filepath, logger_func)
    else:
        logger_func("   🍪 Cookie usage enabled, but no text input, specific file, or app base directory provided for cookies.txt.")
        return None

def fetch_posts_paginated(api_url_base, headers, offset, logger, cancellation_event=None, pause_event=None, cookies_dict=None):    
    if cancellation_event and cancellation_event.is_set(): # type: ignore
        logger("   Fetch cancelled before request.")
        raise RuntimeError("Fetch operation cancelled by user.")

    if pause_event and pause_event.is_set(): # type: ignore        
        logger("   Post fetching paused...")
        while pause_event.is_set():
            if cancellation_event and cancellation_event.is_set():
                logger("   Post fetching cancelled while paused.") # type: ignore
                raise RuntimeError("Fetch operation cancelled by user.")
            time.sleep(0.5)
        logger("   Post fetching resumed.")

    paginated_url = f'{api_url_base}?o={offset}'
    logger(f"   Fetching: {paginated_url} (Page approx. {offset // 50 + 1})")
    try:
        response = requests.get(paginated_url, headers=headers, timeout=(10, 60), cookies=cookies_dict)
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

def fetch_post_comments(api_domain, service, user_id, post_id, headers, logger, cancellation_event=None, pause_event=None, cookies_dict=None):
    if cancellation_event and cancellation_event.is_set():
        logger("   Comment fetch cancelled before request.")
        raise RuntimeError("Comment fetch operation cancelled by user.")

    if pause_event and pause_event.is_set(): # type: ignore
        logger("   Comment fetching paused...")
        while pause_event.is_set():
            if cancellation_event and cancellation_event.is_set():
                logger("   Comment fetching cancelled while paused.")
                raise RuntimeError("Comment fetch operation cancelled by user.")
            time.sleep(0.5)
        logger("   Comment fetching resumed.")

    comments_api_url = f"https://{api_domain}/api/v1/{service}/user/{user_id}/post/{post_id}/comments"
    logger(f"   Fetching comments: {comments_api_url}")
    try:
        response = requests.get(comments_api_url, headers=headers, timeout=(10, 30), cookies=cookies_dict)
        response.raise_for_status()
        if 'application/json' not in response.headers.get('Content-Type', '').lower():
            logger(f"⚠️ Unexpected content type from comments API: {response.headers.get('Content-Type')}. Body: {response.text[:200]}")
            return [] # Return empty list if not JSON
        return response.json()
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Timeout fetching comments for post {post_id} from {comments_api_url}")
    except requests.exceptions.RequestException as e:
        err_msg = f"Error fetching comments for post {post_id} from {comments_api_url}: {e}"
        if e.response is not None:
            err_msg += f" (Status: {e.response.status_code}, Body: {e.response.text[:200]})"
        raise RuntimeError(err_msg)
    except ValueError as e: # JSONDecodeError inherits from ValueError
        raise RuntimeError(f"Error decoding JSON from comments API for post {post_id} ({comments_api_url}): {e}. Response text: {response.text[:200]}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error fetching comments for post {post_id} ({comments_api_url}): {e}")

def download_from_api(api_url_input, logger=print, start_page=None, end_page=None, manga_mode=False,
                      cancellation_event=None, pause_event=None, use_cookie=False, cookie_text="", selected_cookie_file=None, app_base_dir=None):
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
    
    cookies_for_api = None
    if use_cookie and app_base_dir: # app_base_dir is needed for cookies.txt path
        cookies_for_api = prepare_cookies_for_request(use_cookie, cookie_text, selected_cookie_file, app_base_dir, logger)

    page_size = 50

    if is_creator_feed_for_manga:
        logger("   Manga Mode: Fetching posts to sort by date (oldest processed first)...")
        all_posts_for_manga_mode = []
        
        current_offset_manga = 0
        # Determine starting page and offset for manga mode
        if start_page and start_page > 1:
            current_offset_manga = (start_page - 1) * page_size
            logger(f"   Manga Mode: Starting fetch from page {start_page} (offset {current_offset_manga}).")
        elif start_page: # start_page is 1
            logger(f"   Manga Mode: Starting fetch from page 1 (offset 0).")
        
        if end_page:
            logger(f"   Manga Mode: Will fetch up to page {end_page}.")

        while True:
            if pause_event and pause_event.is_set():
                logger("   Manga mode post fetching paused...") # type: ignore
                while pause_event.is_set():
                    if cancellation_event and cancellation_event.is_set():
                        logger("   Manga mode post fetching cancelled while paused.") # type: ignore
                        break
                    time.sleep(0.5)
                if not (cancellation_event and cancellation_event.is_set()): logger("   Manga mode post fetching resumed.")
            if cancellation_event and cancellation_event.is_set():
                logger("   Manga mode post fetching cancelled.")
                break

            current_page_num_manga = (current_offset_manga // page_size) + 1
            if end_page and current_page_num_manga > end_page:
                logger(f"   Manga Mode: Reached specified end page ({end_page}). Stopping post fetch.")
                break
            try:
                posts_batch_manga = fetch_posts_paginated(api_base_url, headers, current_offset_manga, logger, cancellation_event, pause_event, cookies_dict=cookies_for_api)
                if not isinstance(posts_batch_manga, list):
                    logger(f"❌ API Error (Manga Mode): Expected list of posts, got {type(posts_batch_manga)}.")
                    break
                if not posts_batch_manga:
                    logger("✅ Reached end of posts (Manga Mode fetch all).")
                    if start_page and not end_page and current_page_num_manga < start_page: # Started on a page with no posts
                        logger(f"   Manga Mode: No posts found on or after specified start page {start_page}.")
                    elif end_page and current_page_num_manga <= end_page and not all_posts_for_manga_mode: # Range specified but no posts in it
                        logger(f"   Manga Mode: No posts found within the specified page range ({start_page or 1}-{end_page}).")
                    break # No more posts from API
                all_posts_for_manga_mode.extend(posts_batch_manga)
                current_offset_manga += page_size # Increment by page_size for the next API call's 'o' parameter
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
            logger(f"   Manga Mode: Fetched {len(all_posts_for_manga_mode)} total posts. Sorting by publication date (oldest first)...")
            # ... (rest of sorting and yielding logic for manga mode remains the same) ...
            def sort_key_tuple(post):
                published_date_str = post.get('published')
                added_date_str = post.get('added')
                post_id_str = post.get('id', "0")

                primary_sort_val = "0000-00-00T00:00:00" # Default for missing dates (effectively oldest)
                if published_date_str:
                    primary_sort_val = published_date_str
                elif added_date_str:
                    logger(f"    ⚠️ Post ID {post_id_str} missing 'published' date, using 'added' date '{added_date_str}' for primary sorting.")
                    primary_sort_val = added_date_str
                else:
                    logger(f"    ⚠️ Post ID {post_id_str} missing both 'published' and 'added' dates. Placing at start of sort (using default earliest date).")
                
                secondary_sort_val = 0 # Default for non-integer IDs
                try:
                    secondary_sort_val = int(post_id_str)
                except ValueError:
                    logger(f"    ⚠️ Post ID '{post_id_str}' is not a valid integer for secondary sorting, using 0.")
                
                return (primary_sort_val, secondary_sort_val)

            all_posts_for_manga_mode.sort(key=sort_key_tuple) # Sorts ascending by (date, id)

            for i in range(0, len(all_posts_for_manga_mode), page_size):
                if cancellation_event and cancellation_event.is_set():
                    logger("   Manga mode post yielding cancelled.")
                    break
                yield all_posts_for_manga_mode[i:i + page_size]
        return

    current_page_num = 1
    current_offset = 0
    processed_target_post_flag = False

    if start_page and start_page > 1 and not target_post_id:
        current_offset = (start_page - 1) * page_size
        current_page_num = start_page
        logger(f"   Starting from page {current_page_num} (calculated offset {current_offset}).")

    while True:
        if pause_event and pause_event.is_set():
            logger("   Post fetching loop paused...") # type: ignore
            while pause_event.is_set():
                if cancellation_event and cancellation_event.is_set():
                    logger("   Post fetching loop cancelled while paused.")
                    break
                time.sleep(0.5)
            if not (cancellation_event and cancellation_event.is_set()): logger("   Post fetching loop resumed.")
        if cancellation_event and cancellation_event.is_set():
            logger("   Post fetching loop cancelled.")
            break
        
        if target_post_id and processed_target_post_flag:
            break

        if not target_post_id and end_page and current_page_num > end_page:
            logger(f"✅ Reached specified end page ({end_page}) for creator feed. Stopping.")
            break

        try:
            posts_batch = fetch_posts_paginated(api_base_url, headers, current_offset, logger, cancellation_event, pause_event, cookies_dict=cookies_for_api)
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

        current_offset += page_size # Increment by page_size for the next API call's 'o' parameter
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
    file_progress_signal = pyqtSignal(str, object)
    missed_character_post_signal = pyqtSignal(str, str) # New: post_title, reason


class PostProcessorWorker:
    def __init__(self, post_data, download_root, known_names,
                 filter_character_list, emitter, # Changed signals to emitter
                 unwanted_keywords, filter_mode, skip_zip, skip_rar,
                 use_subfolders, use_post_subfolders, target_post_id_from_initial_url, custom_folder_name,
                 compress_images, download_thumbnails, service, user_id, pause_event, # Added pause_event
                 api_url_input, cancellation_event,
                 downloaded_files, downloaded_file_hashes, downloaded_files_lock, downloaded_file_hashes_lock,
                 dynamic_character_filter_holder=None, skip_words_list=None, # Added dynamic_character_filter_holder
                 skip_words_scope=SKIP_SCOPE_FILES,
                 show_external_links=False,
                 extract_links_only=False,
                 num_file_threads=4, skip_current_file_flag=None,
                 manga_mode_active=False,
                 manga_filename_style=STYLE_POST_TITLE,
                 char_filter_scope=CHAR_SCOPE_FILES,
                 remove_from_filename_words_list=None,
                 allow_multipart_download=True,
                 cookie_text="", # Added missing parameter
                 use_cookie=False, # Added missing parameter
                 selected_cookie_file=None, # Added missing parameter
                 app_base_dir=None, # New parameter for app's base directory
                 manga_date_prefix=MANGA_DATE_PREFIX_DEFAULT, # New parameter for date-based prefix
                 manga_date_file_counter_ref=None, # New parameter for date-based manga naming
                 manga_global_file_counter_ref=None, # New parameter for global numbering
                 ): # type: ignore
        self.post = post_data
        self.download_root = download_root
        self.known_names = known_names
        self.filter_character_list_objects_initial = filter_character_list if filter_character_list else [] # Store initial
        self.dynamic_filter_holder = dynamic_character_filter_holder # Store the holder
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
        self.pause_event = pause_event # Store pause_event
        self.emitter = emitter # Store the emitter
        if not self.emitter:
            raise ValueError("PostProcessorWorker requires an emitter (signals object or queue).")
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
        self.remove_from_filename_words_list = remove_from_filename_words_list if remove_from_filename_words_list is not None else []
        self.allow_multipart_download = allow_multipart_download
        self.manga_date_file_counter_ref = manga_date_file_counter_ref # Store the reference
        self.selected_cookie_file = selected_cookie_file # Store selected cookie file path       
        self.app_base_dir = app_base_dir # Store app base dir        
        self.cookie_text = cookie_text # Store cookie text
        self.manga_date_prefix = manga_date_prefix # Store the prefix
        self.manga_global_file_counter_ref = manga_global_file_counter_ref # Store global counter
        self.use_cookie = use_cookie # Store cookie setting

        if self.compress_images and Image is None:
            self.logger("⚠️ Image compression disabled: Pillow library not found.")
            self.compress_images = False

    def _emit_signal(self, signal_type_str, *payload_args):
        """Helper to emit signal either directly or via queue."""
        if isinstance(self.emitter, queue.Queue):
            self.emitter.put({'type': signal_type_str, 'payload': payload_args})
        elif self.emitter and hasattr(self.emitter, f"{signal_type_str}_signal"):
            signal_attr = getattr(self.emitter, f"{signal_type_str}_signal")
            signal_attr.emit(*payload_args)
        else:
            print(f"(Worker Log - Unrecognized Emitter for {signal_type_str}): {payload_args[0] if payload_args else ''}")

    def logger(self, message):
        self._emit_signal('progress', message)

    def check_cancel(self):
        return self.cancellation_event.is_set()

    def _check_pause(self, context_message="Operation"):
        if self.pause_event and self.pause_event.is_set():
            self.logger(f"   {context_message} paused...")
            while self.pause_event.is_set(): # Loop while pause_event is set
                if self.check_cancel():
                    self.logger(f"   {context_message} cancelled while paused.")
                    return True # Indicates cancellation occurred
                time.sleep(0.5)
            if not self.check_cancel(): self.logger(f"   {context_message} resumed.")
        return False # Not cancelled during pause

    def _download_single_file(self, file_info, target_folder_path, headers, original_post_id_for_log, skip_event, # skip_event is threading.Event
                              post_title="", file_index_in_post=0, num_files_in_this_post=1,
                              manga_date_file_counter_ref=None): # Added manga_date_file_counter_ref
        was_original_name_kept_flag = False
        manga_global_file_counter_ref = None # Placeholder, will be passed from process()
        final_filename_saved_for_return = "" 

    def _get_current_character_filters(self):
        if self.dynamic_filter_holder:
            return self.dynamic_filter_holder.get_filters()
        return self.filter_character_list_objects_initial

    def _download_single_file(self, file_info, target_folder_path, headers, original_post_id_for_log, skip_event,
                              post_title="", file_index_in_post=0, num_files_in_this_post=1, # Added manga_date_file_counter_ref
                              manga_date_file_counter_ref=None,
                              forced_filename_override=None, # New for retries
                              manga_global_file_counter_ref=None): # New for global numbering
        was_original_name_kept_flag = False 
        final_filename_saved_for_return = "" 
        retry_later_details = None # For storing info if retryable failure

        if self._check_pause(f"File download prep for '{file_info.get('name', 'unknown file')}'"): return 0, 1, "", False
        if self.check_cancel() or (skip_event and skip_event.is_set()): return 0, 1, "", False

        file_url = file_info.get('url')
        cookies_to_use_for_file = None
        if self.use_cookie: # This flag comes from the checkbox
            cookies_to_use_for_file = prepare_cookies_for_request(self.use_cookie, self.cookie_text, self.selected_cookie_file, self.app_base_dir, self.logger)
        api_original_filename = file_info.get('_original_name_for_log', file_info.get('name'))
        filename_to_save_in_main_path = "" 

        if forced_filename_override:
            filename_to_save_in_main_path = forced_filename_override
            self.logger(f"   Retrying with forced filename: '{filename_to_save_in_main_path}'")
        else:
            if self.skip_words_list and (self.skip_words_scope == SKIP_SCOPE_FILES or self.skip_words_scope == SKIP_SCOPE_BOTH):
                filename_to_check_for_skip_words = api_original_filename.lower()
                for skip_word in self.skip_words_list:
                    if skip_word.lower() in filename_to_check_for_skip_words:
                        self.logger(f"   -> Skip File (Keyword in Original Name '{skip_word}'): '{api_original_filename}'. Scope: {self.skip_words_scope}")
                        return 0, 1, api_original_filename, False, FILE_DOWNLOAD_STATUS_SKIPPED, None
            
            original_filename_cleaned_base, original_ext = os.path.splitext(clean_filename(api_original_filename))
            if not original_ext.startswith('.'): original_ext = '.' + original_ext if original_ext else ''

            if self.manga_mode_active: # Note: duplicate_file_mode is overridden to "Delete" in main.py if manga_mode is on
                if self.manga_filename_style == STYLE_ORIGINAL_NAME:
                    filename_to_save_in_main_path = clean_filename(api_original_filename)
                    # Apply prefix if provided for Original Name style
                    if self.manga_date_prefix and self.manga_date_prefix.strip():
                        cleaned_prefix = clean_filename(self.manga_date_prefix.strip())
                        if cleaned_prefix:
                            filename_to_save_in_main_path = f"{cleaned_prefix} {filename_to_save_in_main_path}"
                        else:
                            self.logger(f"⚠️ Manga Original Name Mode: Provided prefix '{self.manga_date_prefix}' was empty after cleaning. Using original name only.")

                    was_original_name_kept_flag = True
                elif self.manga_filename_style == STYLE_POST_TITLE:
                    if post_title and post_title.strip():
                        cleaned_post_title_base = clean_filename(post_title.strip())
                        if num_files_in_this_post > 1:
                            if file_index_in_post == 0:
                                filename_to_save_in_main_path = f"{cleaned_post_title_base}{original_ext}"
                            else:
                                filename_to_save_in_main_path = f"{cleaned_post_title_base}_{file_index_in_post}{original_ext}"
                                was_original_name_kept_flag = False # Name is derived, not original
                        else:
                            filename_to_save_in_main_path = f"{cleaned_post_title_base}{original_ext}"
                    else:
                        filename_to_save_in_main_path = clean_filename(api_original_filename) # Fallback to original if no title
                        self.logger(f"⚠️ Manga mode (Post Title Style): Post title missing for post {original_post_id_for_log}. Using cleaned original filename '{filename_to_save_in_main_path}'.")
                elif self.manga_filename_style == STYLE_DATE_BASED:
                    current_thread_name = threading.current_thread().name

                    if manga_date_file_counter_ref is not None and len(manga_date_file_counter_ref) == 2:
                        counter_val_for_filename = -1
                        counter_lock = manga_date_file_counter_ref[1]
                        with counter_lock:
                            counter_val_for_filename = manga_date_file_counter_ref[0]
                            manga_date_file_counter_ref[0] += 1
                        
                        base_numbered_name = f"{counter_val_for_filename:03d}"
                        if self.manga_date_prefix and self.manga_date_prefix.strip():
                            cleaned_prefix = clean_filename(self.manga_date_prefix.strip())
                            if cleaned_prefix: # Ensure prefix is not empty after cleaning
                                filename_to_save_in_main_path = f"{cleaned_prefix} {base_numbered_name}{original_ext}"
                            else: # Prefix became empty after cleaning
                                filename_to_save_in_main_path = f"{base_numbered_name}{original_ext}"; self.logger(f"⚠️ Manga Date Mode: Provided prefix '{self.manga_date_prefix}' was empty after cleaning. Using number only.")
                        else: # No prefix provided
                            filename_to_save_in_main_path = f"{base_numbered_name}{original_ext}"
                    else:
                        self.logger(f"⚠️ Manga Date Mode: Counter ref not provided or malformed for '{api_original_filename}'. Using original. Ref: {manga_date_file_counter_ref}")
                        filename_to_save_in_main_path = clean_filename(api_original_filename)
                        self.logger(f"⚠️ Manga mode (Date Based Style Fallback): Using cleaned original filename '{filename_to_save_in_main_path}' for post {original_post_id_for_log}.")
                elif self.manga_filename_style == STYLE_POST_TITLE_GLOBAL_NUMBERING:
                    if manga_global_file_counter_ref is not None and len(manga_global_file_counter_ref) == 2:
                        counter_val_for_filename = -1
                        counter_lock = manga_global_file_counter_ref[1]
                        with counter_lock:
                            counter_val_for_filename = manga_global_file_counter_ref[0]
                            manga_global_file_counter_ref[0] += 1
                        
                        cleaned_post_title_base_for_global = clean_filename(post_title.strip() if post_title and post_title.strip() else "post")
                        filename_to_save_in_main_path = f"{cleaned_post_title_base_for_global}_{counter_val_for_filename:03d}{original_ext}"
                    else:
                        self.logger(f"⚠️ Manga Title+GlobalNum Mode: Counter ref not provided or malformed for '{api_original_filename}'. Using original. Ref: {manga_global_file_counter_ref}")
                        self.logger(f"⚠️ Manga mode (Date Based Style Fallback): Using cleaned original filename '{filename_to_save_in_main_path}' for post {original_post_id_for_log}.")
                else: 
                    self.logger(f"⚠️ Manga mode: Unknown filename style '{self.manga_filename_style}'. Defaulting to original filename for '{api_original_filename}'.")
                    filename_to_save_in_main_path = clean_filename(api_original_filename)

                if not filename_to_save_in_main_path: 
                    filename_to_save_in_main_path = f"manga_file_{original_post_id_for_log}_{file_index_in_post + 1}{original_ext}"
                    self.logger(f"⚠️ Manga mode: Generated filename was empty. Using generic fallback: '{filename_to_save_in_main_path}'.")
                    was_original_name_kept_flag = False
            else: 
                filename_to_save_in_main_path = clean_filename(api_original_filename)
                was_original_name_kept_flag = False
                
            if self.remove_from_filename_words_list and filename_to_save_in_main_path:
                base_name_for_removal, ext_for_removal = os.path.splitext(filename_to_save_in_main_path)
                modified_base_name = base_name_for_removal
                for word_to_remove in self.remove_from_filename_words_list:
                    if not word_to_remove: continue
                    pattern = re.compile(re.escape(word_to_remove), re.IGNORECASE)
                    modified_base_name = pattern.sub("", modified_base_name)
                # After removals, normalize all seps (underscore, dot, multiple spaces, hyphen) to a single space, then strip.
                modified_base_name = re.sub(r'[_.\s-]+', ' ', modified_base_name) # Convert all separators to spaces
                modified_base_name = re.sub(r'\s+', ' ', modified_base_name)     # Condense multiple spaces to one
                modified_base_name = modified_base_name.strip()                  # Remove leading/trailing spaces
                if modified_base_name and modified_base_name != ext_for_removal.lstrip('.'):
                    filename_to_save_in_main_path = modified_base_name + ext_for_removal
                else: 
                    filename_to_save_in_main_path = base_name_for_removal + ext_for_removal 
        
        if not self.download_thumbnails: 
            is_img_type = is_image(api_original_filename)
            is_vid_type = is_video(api_original_filename)
            is_archive_type = is_archive(api_original_filename)

            if self.filter_mode == 'archive':
                if not is_archive_type:
                    self.logger(f"   -> Filter Skip (Archive Mode): '{api_original_filename}' (Not an Archive).")
                    return 0, 1, api_original_filename, False, FILE_DOWNLOAD_STATUS_SKIPPED, None
            elif self.filter_mode == 'image':
                if not is_img_type:
                    self.logger(f"   -> Filter Skip: '{api_original_filename}' (Not Image).")
                    return 0, 1, api_original_filename, False, FILE_DOWNLOAD_STATUS_SKIPPED, None
            elif self.filter_mode == 'video':
                if not is_vid_type:
                    self.logger(f"   -> Filter Skip: '{api_original_filename}' (Not Video).")
                    return 0, 1, api_original_filename, False, FILE_DOWNLOAD_STATUS_SKIPPED, None

            if self.skip_zip and is_zip(api_original_filename):
                self.logger(f"   -> Pref Skip: '{api_original_filename}' (ZIP).")
                return 0, 1, api_original_filename, False, FILE_DOWNLOAD_STATUS_SKIPPED, None
            if self.skip_rar and is_rar(api_original_filename):
                self.logger(f"   -> Pref Skip: '{api_original_filename}' (RAR).")
                return 0, 1, api_original_filename, False, FILE_DOWNLOAD_STATUS_SKIPPED, None
        try:
            os.makedirs(target_folder_path, exist_ok=True) # For .part file
        except OSError as e:
            self.logger(f"   ❌ Critical error creating directory '{target_folder_path}': {e}. Skipping file '{api_original_filename}'.")
            return 0, 1, api_original_filename, False, FILE_DOWNLOAD_STATUS_SKIPPED, None # Treat as skip
        max_retries = 3
        retry_delay = 5
        downloaded_size_bytes = 0
        calculated_file_hash = None
        file_content_bytes = None 
        total_size_bytes = 0 
        download_successful_flag = False 
        last_exception_for_retry_later = None
        
        for attempt_num_single_stream in range(max_retries + 1): 
            if self._check_pause(f"File download attempt for '{api_original_filename}'"): break
            if self.check_cancel() or (skip_event and skip_event.is_set()): break
            try:
                if attempt_num_single_stream > 0:
                    self.logger(f"   Retrying download for '{api_original_filename}' (Overall Attempt {attempt_num_single_stream + 1}/{max_retries + 1})...")
                    time.sleep(retry_delay * (2**(attempt_num_single_stream - 1)))

                self._emit_signal('file_download_status', True)
                
                response = requests.get(file_url, headers=headers, timeout=(15, 300), stream=True, cookies=cookies_to_use_for_file)
                response.raise_for_status()
                total_size_bytes = int(response.headers.get('Content-Length', 0))

                num_parts_for_file = min(self.num_file_threads, MAX_PARTS_FOR_MULTIPART_DOWNLOAD)
                attempt_multipart = (self.allow_multipart_download and MULTIPART_DOWNLOADER_AVAILABLE and
                                     num_parts_for_file > 1 and total_size_bytes > MIN_SIZE_FOR_MULTIPART_DOWNLOAD and
                                     'bytes' in response.headers.get('Accept-Ranges', '').lower())
                
                if self._check_pause(f"Multipart decision for '{api_original_filename}'"): break # Check pause before potentially long operation
                if attempt_multipart:
                    response.close() 
                    self._emit_signal('file_download_status', False)
                    mp_save_path_base_for_part = os.path.join(target_folder_path, filename_to_save_in_main_path)
                    mp_success, mp_bytes, mp_hash, mp_file_handle = download_file_in_parts(
                        file_url, mp_save_path_base_for_part, total_size_bytes, num_parts_for_file, headers, api_original_filename,
                        emitter_for_multipart=self.emitter, cookies_for_chunk_session=cookies_to_use_for_file, # Pass cookies
                        cancellation_event=self.cancellation_event, skip_event=skip_event, logger_func=self.logger,
                        pause_event=self.pause_event # Pass pause_event
                    )
                    if mp_success:
                        download_successful_flag = True
                        downloaded_size_bytes = mp_bytes
                        calculated_file_hash = mp_hash
                        file_content_bytes = mp_file_handle 
                        break 
                    else: 
                        if attempt_num_single_stream < max_retries:
                            self.logger(f"   Multi-part download attempt failed for '{api_original_filename}'. Retrying with single stream.")
                        else: 
                            download_successful_flag = False; break 
                
                self.logger(f"⬇️ Downloading (Single Stream): '{api_original_filename}' (Size: {total_size_bytes / (1024*1024):.2f} MB if known) [Base Name: '{filename_to_save_in_main_path}']")
                file_content_buffer = BytesIO()
                current_attempt_downloaded_bytes = 0
                md5_hasher = hashlib.md5()
                last_progress_time = time.time()

                for chunk in response.iter_content(chunk_size=1 * 1024 * 1024):
                    if self._check_pause(f"Chunk download for '{api_original_filename}'"): break
                    if self.check_cancel() or (skip_event and skip_event.is_set()): break
                    if chunk:
                        file_content_buffer.write(chunk); md5_hasher.update(chunk)
                        current_attempt_downloaded_bytes += len(chunk)
                        if time.time() - last_progress_time > 1 and total_size_bytes > 0:
                            self._emit_signal('file_progress', api_original_filename, (current_attempt_downloaded_bytes, total_size_bytes))
                            last_progress_time = time.time()
                
                if self.check_cancel() or (skip_event and skip_event.is_set()) or (self.pause_event and self.pause_event.is_set()):
                    if file_content_buffer: file_content_buffer.close(); break
                
                if current_attempt_downloaded_bytes > 0 or (total_size_bytes == 0 and response.status_code == 200):
                    calculated_file_hash = md5_hasher.hexdigest()
                    downloaded_size_bytes = current_attempt_downloaded_bytes
                    if file_content_bytes: file_content_bytes.close() 
                    file_content_bytes = file_content_buffer; file_content_bytes.seek(0)
                    download_successful_flag = True; break
                else: 
                    if file_content_buffer: file_content_buffer.close()

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, http.client.IncompleteRead) as e:
                self.logger(f"   ❌ Download Error (Retryable): {api_original_filename}. Error: {e}")
                last_exception_for_retry_later = e # Store this specific exception
                if 'file_content_buffer' in locals() and file_content_buffer: file_content_buffer.close()
            except requests.exceptions.RequestException as e: 
                self.logger(f"   ❌ Download Error (Non-Retryable): {api_original_filename}. Error: {e}")
                last_exception_for_retry_later = e # Store this too
                if 'file_content_buffer' in locals() and file_content_buffer: file_content_buffer.close(); break
            except Exception as e:
                self.logger(f"   ❌ Unexpected Download Error: {api_original_filename}: {e}\n{traceback.format_exc(limit=2)}")
                if 'file_content_buffer' in locals() and file_content_buffer: file_content_buffer.close(); break
            finally:
                self._emit_signal('file_download_status', False)
        final_total_for_progress = total_size_bytes if download_successful_flag and total_size_bytes > 0 else downloaded_size_bytes
        self._emit_signal('file_progress', api_original_filename, (downloaded_size_bytes, final_total_for_progress))

        if self.check_cancel() or (skip_event and skip_event.is_set()) or (self.pause_event and self.pause_event.is_set() and not download_successful_flag):
            self.logger(f"   ⚠️ Download process interrupted for {api_original_filename}.")
            if file_content_bytes: file_content_bytes.close()
            return 0, 1, filename_to_save_in_main_path, was_original_name_kept_flag, FILE_DOWNLOAD_STATUS_SKIPPED, None

        if not download_successful_flag:
            self.logger(f"❌ Download failed for '{api_original_filename}' after {max_retries + 1} attempts.")
            if file_content_bytes: file_content_bytes.close()
            if isinstance(last_exception_for_retry_later, http.client.IncompleteRead):
                self.logger(f"   Marking '{api_original_filename}' for potential retry later due to IncompleteRead.")
                retry_later_details = {
                    'file_info': file_info,
                    'target_folder_path': target_folder_path, # This is the base character/post folder
                    'headers': headers, # Original headers
                    'original_post_id_for_log': original_post_id_for_log,
                    'post_title': post_title,
                    'file_index_in_post': file_index_in_post,
                    'num_files_in_this_post': num_files_in_this_post,
                    'forced_filename_override': filename_to_save_in_main_path, # The name it was trying to save as
                    'manga_mode_active_for_file': self.manga_mode_active, # Store context
                    'manga_filename_style_for_file': self.manga_filename_style, # Store context
                }
                return 0, 1, filename_to_save_in_main_path, was_original_name_kept_flag, FILE_DOWNLOAD_STATUS_FAILED_RETRYABLE_LATER, retry_later_details
            return 0, 1, filename_to_save_in_main_path, was_original_name_kept_flag, FILE_DOWNLOAD_STATUS_SKIPPED, None # Generic failure

        if self._check_pause(f"Post-download hash check for '{api_original_filename}'"): return 0, 1, filename_to_save_in_main_path, was_original_name_kept_flag, FILE_DOWNLOAD_STATUS_SKIPPED, None
        with self.downloaded_file_hashes_lock:
            if calculated_file_hash in self.downloaded_file_hashes:
                self.logger(f"   -> Skip Saving Duplicate (Hash Match): '{api_original_filename}' (Hash: {calculated_file_hash[:8]}...).")
                with self.downloaded_files_lock: self.downloaded_files.add(filename_to_save_in_main_path) # Mark logical name
                if file_content_bytes: file_content_bytes.close()
                if not isinstance(file_content_bytes, BytesIO): # Indicates multipart download
                    part_file_to_remove = os.path.join(target_folder_path, filename_to_save_in_main_path + ".part")
                    if os.path.exists(part_file_to_remove):
                        try: os.remove(part_file_to_remove);
                        except OSError: self.logger(f"  -> Failed to remove .part file for hash duplicate: {part_file_to_remove}") # type: ignore
                return 0, 1, filename_to_save_in_main_path, was_original_name_kept_flag, FILE_DOWNLOAD_STATUS_SKIPPED, None
        effective_save_folder = target_folder_path  # Default: main character/post folder
        filename_after_styling_and_word_removal = filename_to_save_in_main_path
                
        try: # Ensure the chosen save folder (main or Duplicate) exists
            os.makedirs(effective_save_folder, exist_ok=True)
        except OSError as e:
            self.logger(f"   ❌ Critical error creating directory '{effective_save_folder}': {e}. Skipping file '{api_original_filename}'.")
            if file_content_bytes: file_content_bytes.close()
            if not isinstance(file_content_bytes, BytesIO):
                part_file_to_remove = os.path.join(target_folder_path, filename_to_save_in_main_path + ".part")
                if os.path.exists(part_file_to_remove): os.remove(part_file_to_remove)
            return 0, 1, api_original_filename, False, FILE_DOWNLOAD_STATUS_SKIPPED, None
        data_to_write_after_compression = file_content_bytes 
        filename_after_compression = filename_after_styling_and_word_removal

        is_img_for_compress_check = is_image(api_original_filename)
        if is_img_for_compress_check and self.compress_images and Image and downloaded_size_bytes > (1.5 * 1024 * 1024):
            self.logger(f"   Compressing '{api_original_filename}' ({downloaded_size_bytes / (1024*1024):.2f} MB)...")
            if self._check_pause(f"Image compression for '{api_original_filename}'"): return 0, 1, filename_to_save_in_main_path, was_original_name_kept_flag, FILE_DOWNLOAD_STATUS_SKIPPED, None # Allow pause before compression
            try:
                file_content_bytes.seek(0) 
                with Image.open(file_content_bytes) as img_obj: 
                    if img_obj.mode == 'P': img_obj = img_obj.convert('RGBA')
                    elif img_obj.mode not in ['RGB', 'RGBA', 'L']: img_obj = img_obj.convert('RGB')
                    compressed_bytes_io = BytesIO()
                    img_obj.save(compressed_bytes_io, format='WebP', quality=80, method=4)
                    compressed_size = compressed_bytes_io.getbuffer().nbytes

                if compressed_size < downloaded_size_bytes * 0.9:  # If significantly smaller
                    self.logger(f"   Compression success: {compressed_size / (1024*1024):.2f} MB.")
                    data_to_write_after_compression = compressed_bytes_io; data_to_write_after_compression.seek(0)
                    base_name_orig, _ = os.path.splitext(filename_after_compression) 
                    filename_after_compression = base_name_orig + '.webp'
                    self.logger(f"   Updated filename (compressed): {filename_after_compression}")
                else:
                    self.logger(f"   Compression skipped: WebP not significantly smaller."); file_content_bytes.seek(0) # Reset original stream
                    data_to_write_after_compression = file_content_bytes # Use original
            except Exception as comp_e:
                self.logger(f"❌ Compression failed for '{api_original_filename}': {comp_e}. Saving original."); file_content_bytes.seek(0)
                data_to_write_after_compression = file_content_bytes # Use original
        final_filename_on_disk = filename_after_compression # This is the name after potential compression
        if not (self.manga_mode_active and self.manga_filename_style == STYLE_DATE_BASED):
            temp_base, temp_ext = os.path.splitext(final_filename_on_disk)
            suffix_counter = 1
            while os.path.exists(os.path.join(effective_save_folder, final_filename_on_disk)):
                final_filename_on_disk = f"{temp_base}_{suffix_counter}{temp_ext}"
                suffix_counter += 1
            if final_filename_on_disk != filename_after_compression: # Log if a suffix was applied
                self.logger(f"     Applied numeric suffix in '{os.path.basename(effective_save_folder)}': '{final_filename_on_disk}' (was '{filename_after_compression}')")
        if self._check_pause(f"File saving for '{final_filename_on_disk}'"): return 0, 1, final_filename_on_disk, was_original_name_kept_flag, FILE_DOWNLOAD_STATUS_SKIPPED, None
        final_save_path = os.path.join(effective_save_folder, final_filename_on_disk)

        try:
            
            if data_to_write_after_compression is file_content_bytes and not isinstance(file_content_bytes, BytesIO):
                original_part_file_actual_path = file_content_bytes.name
                file_content_bytes.close() # Close handle first
                os.rename(original_part_file_actual_path, final_save_path)
                self.logger(f"   Renamed .part file to final: {final_save_path}")
            else: # Single stream download, or compressed multipart. Write from BytesIO.
                with open(final_save_path, 'wb') as f_out:
                    f_out.write(data_to_write_after_compression.getvalue())
                if data_to_write_after_compression is not file_content_bytes and not isinstance(file_content_bytes, BytesIO):
                    original_part_file_actual_path = file_content_bytes.name
                    file_content_bytes.close()
                    if os.path.exists(original_part_file_actual_path):
                        try: os.remove(original_part_file_actual_path)
                        except OSError as e_rem: self.logger(f"  -> Failed to remove .part after compression: {e_rem}")

            with self.downloaded_file_hashes_lock: self.downloaded_file_hashes.add(calculated_file_hash)
            with self.downloaded_files_lock: self.downloaded_files.add(filename_to_save_in_main_path) # Track by logical name
            final_filename_saved_for_return = final_filename_on_disk
            self.logger(f"✅ Saved: '{final_filename_saved_for_return}' (from '{api_original_filename}', {downloaded_size_bytes / (1024*1024):.2f} MB) in '{os.path.basename(effective_save_folder)}'")
            time.sleep(0.05) # Brief pause after successful save
            return 1, 0, final_filename_saved_for_return, was_original_name_kept_flag, FILE_DOWNLOAD_STATUS_SUCCESS, None
        except Exception as save_err:
             self.logger(f"❌ Save Fail for '{final_filename_on_disk}': {save_err}")
             if os.path.exists(final_save_path):
                  try: os.remove(final_save_path);
                  except OSError: self.logger(f"  -> Failed to remove partially saved file: {final_save_path}")
             return 0, 1, final_filename_saved_for_return, was_original_name_kept_flag, FILE_DOWNLOAD_STATUS_SKIPPED, None # Treat save fail as skip
        finally:
            if data_to_write_after_compression and hasattr(data_to_write_after_compression, 'close'):
                data_to_write_after_compression.close()
            if file_content_bytes and file_content_bytes is not data_to_write_after_compression and hasattr(file_content_bytes, 'close'):
                try:
                    if not file_content_bytes.closed: # Check if already closed
                        file_content_bytes.close()
                except Exception: pass # Ignore errors on close if already handled


    def process(self):
        if self._check_pause(f"Post processing for ID {self.post.get('id', 'N/A')}"): return 0,0,[], []
        if self.check_cancel(): return 0, 0, [], []
        current_character_filters = self._get_current_character_filters()

        kept_original_filenames_for_log = [] 
        retryable_failures_this_post = [] # New list to store retryable failure details
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
        post_is_candidate_by_comment_char_match = False
        post_is_candidate_by_file_char_match_in_comment_scope = False
        char_filter_that_matched_file_in_comment_scope = None
        char_filter_that_matched_comment = None
        
        if current_character_filters and \
           (self.char_filter_scope == CHAR_SCOPE_TITLE or self.char_filter_scope == CHAR_SCOPE_BOTH):
            if self._check_pause(f"Character title filter for post {post_id}"): return 0, num_potential_files_in_post, [], []
            for idx, filter_item_obj in enumerate(current_character_filters):
                if self.check_cancel(): break
                terms_to_check_for_title = list(filter_item_obj["aliases"])
                if filter_item_obj["is_group"]:
                    if filter_item_obj["name"] not in terms_to_check_for_title:
                        terms_to_check_for_title.append(filter_item_obj["name"])
                
                unique_terms_for_title_check = list(set(terms_to_check_for_title)) 

                for term_to_match in unique_terms_for_title_check:
                    match_found_for_term = is_title_match_for_character(post_title, term_to_match)
                    if match_found_for_term:
                        post_is_candidate_by_title_char_match = True
                        char_filter_that_matched_title = filter_item_obj 
                        self.logger(f"   Post title matches char filter term '{term_to_match}' (from group/name '{filter_item_obj['name']}', Scope: {self.char_filter_scope}). Post is candidate.")
                        break
                if post_is_candidate_by_title_char_match: break
        all_files_from_post_api_for_char_check = []
        api_file_domain_for_char_check = urlparse(self.api_url_input).netloc
        if not api_file_domain_for_char_check or not any(d in api_file_domain_for_char_check.lower() for d in ['kemono.su', 'kemono.party', 'coomer.su', 'coomer.party']):
            api_file_domain_for_char_check = "kemono.su" if "kemono" in self.service.lower() else "coomer.party"

        if post_main_file_info and isinstance(post_main_file_info, dict) and post_main_file_info.get('path'):
            original_api_name = post_main_file_info.get('name') or os.path.basename(post_main_file_info['path'].lstrip('/'))
            if original_api_name:
                all_files_from_post_api_for_char_check.append({'_original_name_for_log': original_api_name})

        for att_info in post_attachments:
            if isinstance(att_info, dict) and att_info.get('path'):
                original_api_att_name = att_info.get('name') or os.path.basename(att_info['path'].lstrip('/'))
                if original_api_att_name:
                    all_files_from_post_api_for_char_check.append({'_original_name_for_log': original_api_att_name})


        if current_character_filters and self.char_filter_scope == CHAR_SCOPE_COMMENTS:
            self.logger(f"   [Char Scope: Comments] Phase 1: Checking post files for matches before comments for post ID '{post_id}'.")
            if self._check_pause(f"File check (comments scope) for post {post_id}"): return 0, num_potential_files_in_post, [], []
            for file_info_item in all_files_from_post_api_for_char_check: # Use the pre-populated list of file names
                if self.check_cancel(): break
                current_api_original_filename_for_check = file_info_item.get('_original_name_for_log')
                if not current_api_original_filename_for_check: continue
                for filter_item_obj in current_character_filters:
                    terms_to_check = list(filter_item_obj["aliases"])
                    if filter_item_obj["is_group"] and filter_item_obj["name"] not in terms_to_check:
                        terms_to_check.append(filter_item_obj["name"])
                    
                    for term_to_match in terms_to_check:
                        if is_filename_match_for_character(current_api_original_filename_for_check, term_to_match):
                            post_is_candidate_by_file_char_match_in_comment_scope = True
                            char_filter_that_matched_file_in_comment_scope = filter_item_obj
                            self.logger(f"     Match Found (File in Comments Scope): File '{current_api_original_filename_for_check}' matches char filter term '{term_to_match}' (from group/name '{filter_item_obj['name']}'). Post is candidate.")
                            break
                    if post_is_candidate_by_file_char_match_in_comment_scope: break
                if post_is_candidate_by_file_char_match_in_comment_scope: break
            self.logger(f"   [Char Scope: Comments] Phase 1 Result: post_is_candidate_by_file_char_match_in_comment_scope = {post_is_candidate_by_file_char_match_in_comment_scope}")
        
        if current_character_filters and self.char_filter_scope == CHAR_SCOPE_COMMENTS:
            if not post_is_candidate_by_file_char_match_in_comment_scope:
                if self._check_pause(f"Comment check for post {post_id}"): return 0, num_potential_files_in_post, [], []
                self.logger(f"   [Char Scope: Comments] Phase 2: No file match found. Checking post comments for post ID '{post_id}'.")
                try:
                    parsed_input_url_for_comments = urlparse(self.api_url_input)
                    api_domain_for_comments = parsed_input_url_for_comments.netloc
                    if not any(d in api_domain_for_comments.lower() for d in ['kemono.su', 'kemono.party', 'coomer.su', 'coomer.party']):
                        self.logger(f"⚠️ Unrecognized domain '{api_domain_for_comments}' for comment API. Defaulting based on service.")
                        api_domain_for_comments = "kemono.su" if "kemono" in self.service.lower() else "coomer.party"

                    comments_data = fetch_post_comments(
                        api_domain_for_comments, self.service, self.user_id, post_id,
                        headers, self.logger, self.cancellation_event, self.pause_event, # Pass pause_event
                        cookies_dict=prepare_cookies_for_request( # Prepare cookies for this API call
                            self.use_cookie, self.cookie_text, self.selected_cookie_file, self.app_base_dir, self.logger
                        )
                    )
                    if comments_data:
                        self.logger(f"     Fetched {len(comments_data)} comments for post {post_id}.")
                        for comment_item_idx, comment_item in enumerate(comments_data):
                            if self.check_cancel(): break
                            raw_comment_content = comment_item.get('content', '')
                            if not raw_comment_content: continue
                            
                            cleaned_comment_text = strip_html_tags(raw_comment_content)
                            if not cleaned_comment_text.strip(): continue

                            for filter_item_obj in current_character_filters:
                                terms_to_check_comment = list(filter_item_obj["aliases"])
                                if filter_item_obj["is_group"] and filter_item_obj["name"] not in terms_to_check_comment:
                                    terms_to_check_comment.append(filter_item_obj["name"])
                                
                                for term_to_match_comment in terms_to_check_comment:
                                    if is_title_match_for_character(cleaned_comment_text, term_to_match_comment): # Re-use title matcher
                                        post_is_candidate_by_comment_char_match = True
                                        char_filter_that_matched_comment = filter_item_obj
                                        self.logger(f"     Match Found (Comment in Comments Scope): Comment in post {post_id} matches char filter term '{term_to_match_comment}' (from group/name '{filter_item_obj['name']}'). Post is candidate.")
                                        self.logger(f"       Matching comment (first 100 chars): '{cleaned_comment_text[:100]}...'")
                                        break 
                                if post_is_candidate_by_comment_char_match: break
                            if post_is_candidate_by_comment_char_match: break 
                    else:
                        self.logger(f"     No comments found or fetched for post {post_id} to check against character filters.")

                except RuntimeError as e_fetch_comment: 
                    self.logger(f"   ⚠️ Error fetching or processing comments for post {post_id}: {e_fetch_comment}")
                except Exception as e_generic_comment: 
                    self.logger(f"   ❌ Unexpected error during comment processing for post {post_id}: {e_generic_comment}\n{traceback.format_exc(limit=2)}")
                self.logger(f"   [Char Scope: Comments] Phase 2 Result: post_is_candidate_by_comment_char_match = {post_is_candidate_by_comment_char_match}")
            else: # post_is_candidate_by_file_char_match_in_comment_scope was True
                self.logger(f"   [Char Scope: Comments] Phase 2: Skipped comment check for post ID '{post_id}' because a file match already made it a candidate.")
        if current_character_filters: # Check if any filters are defined
            if self.char_filter_scope == CHAR_SCOPE_TITLE and not post_is_candidate_by_title_char_match:
                self.logger(f"   -> Skip Post (Scope: Title - No Char Match): Title '{post_title[:50]}' does not match character filters.")
                self._emit_signal('missed_character_post', post_title, "No title match for character filter")
                return 0, num_potential_files_in_post, [], []
            if self.char_filter_scope == CHAR_SCOPE_COMMENTS and \
               not post_is_candidate_by_file_char_match_in_comment_scope and \
               not post_is_candidate_by_comment_char_match: # MODIFIED: Check both file and comment match flags
                self.logger(f"   -> Skip Post (Scope: Comments - No Char Match in Comments): Post ID '{post_id}', Title '{post_title[:50]}...'")
                if self.emitter and hasattr(self.emitter, 'missed_character_post_signal'): # Check emitter
                    self._emit_signal('missed_character_post', post_title, "No character match in files or comments (Comments scope)")
                return 0, num_potential_files_in_post, [], []
                
        if self.skip_words_list and (self.skip_words_scope == SKIP_SCOPE_POSTS or self.skip_words_scope == SKIP_SCOPE_BOTH):
            if self._check_pause(f"Skip words (post title) for post {post_id}"): return 0, num_potential_files_in_post, [], []
            post_title_lower = post_title.lower()
            for skip_word in self.skip_words_list:
                if skip_word.lower() in post_title_lower:
                    self.logger(f"   -> Skip Post (Keyword in Title '{skip_word}'): '{post_title[:50]}...'. Scope: {self.skip_words_scope}")
                    return 0, num_potential_files_in_post, [], []
        
        if not self.extract_links_only and self.manga_mode_active and current_character_filters and \
           (self.char_filter_scope == CHAR_SCOPE_TITLE or self.char_filter_scope == CHAR_SCOPE_BOTH) and \
           not post_is_candidate_by_title_char_match:
            self.logger(f"   -> Skip Post (Manga Mode with Title/Both Scope - No Title Char Match): Title '{post_title[:50]}' doesn't match filters.")
            self._emit_signal('missed_character_post', post_title, "Manga Mode: No title match for character filter (Title/Both scope)")
            return 0, num_potential_files_in_post, [], []

        if not isinstance(post_attachments, list):
            self.logger(f"⚠️ Corrupt attachment data for post {post_id} (expected list, got {type(post_attachments)}). Skipping attachments.")
            post_attachments = []

        base_folder_names_for_post_content = []
        if not self.extract_links_only and self.use_subfolders:
            if self._check_pause(f"Subfolder determination for post {post_id}"): return 0, num_potential_files_in_post, []
            primary_char_filter_for_folder = None # type: ignore
            log_reason_for_folder = ""

            if self.char_filter_scope == CHAR_SCOPE_COMMENTS and char_filter_that_matched_comment:
                if post_is_candidate_by_file_char_match_in_comment_scope and char_filter_that_matched_file_in_comment_scope:
                    primary_char_filter_for_folder = char_filter_that_matched_file_in_comment_scope
                    log_reason_for_folder = "Matched char filter in filename (Comments scope)"
                elif post_is_candidate_by_comment_char_match and char_filter_that_matched_comment: # Fallback to comment match
                    primary_char_filter_for_folder = char_filter_that_matched_comment
                    log_reason_for_folder = "Matched char filter in comments (Comments scope, no file match)"
            elif (self.char_filter_scope == CHAR_SCOPE_TITLE or self.char_filter_scope == CHAR_SCOPE_BOTH) and char_filter_that_matched_title: # Existing logic for other scopes
                primary_char_filter_for_folder = char_filter_that_matched_title
                log_reason_for_folder = "Matched char filter in title"
            if primary_char_filter_for_folder:
                base_folder_names_for_post_content = [clean_folder_name(primary_char_filter_for_folder["name"])]
                self.logger(f"   Base folder name(s) for post content ({log_reason_for_folder}): {', '.join(base_folder_names_for_post_content)}")
            elif not current_character_filters: # No char filters defined, use generic logic
                derived_folders = match_folders_from_title(post_title, self.known_names, self.unwanted_keywords)
                if derived_folders:
                    base_folder_names_for_post_content.extend(match_folders_from_title(post_title, KNOWN_NAMES, self.unwanted_keywords))
                else:
                    base_folder_names_for_post_content.append(extract_folder_name_from_title(post_title, self.unwanted_keywords))
                if not base_folder_names_for_post_content or not base_folder_names_for_post_content[0]:
                    base_folder_names_for_post_content = [clean_folder_name(post_title if post_title else "untitled_creator_content")]
                self.logger(f"   Base folder name(s) for post content (Generic title parsing - no char filters): {', '.join(base_folder_names_for_post_content)}")
            
        if not self.extract_links_only and self.use_subfolders and self.skip_words_list:
            if self._check_pause(f"Folder keyword skip check for post {post_id}"): return 0, num_potential_files_in_post, []
            for folder_name_to_check in base_folder_names_for_post_content: # type: ignore
                if not folder_name_to_check: continue
                if any(skip_word.lower() in folder_name_to_check.lower() for skip_word in self.skip_words_list):
                    matched_skip = next((sw for sw in self.skip_words_list if sw.lower() in folder_name_to_check.lower()), "unknown_skip_word")
                    self.logger(f"   -> Skip Post (Folder Keyword): Potential folder '{folder_name_to_check}' contains '{matched_skip}'.")
                    return 0, num_potential_files_in_post, [], []

        if (self.show_external_links or self.extract_links_only) and post_content_html:
            if self._check_pause(f"External link extraction for post {post_id}"): return 0, num_potential_files_in_post, [], []
            try:
                unique_links_data = {} 
                for match in link_pattern.finditer(post_content_html):
                    link_url = match.group(1).strip()
                    link_url = html.unescape(link_url) # Decode HTML entities in the URL
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
                         self._emit_signal('external_link', post_title, link_text, link_url, platform)
                         links_emitted_count +=1
                
                if links_emitted_count > 0: self.logger(f"   🔗 Found {links_emitted_count} potential external link(s) in post content.")
            except Exception as e: self.logger(f"⚠️ Error parsing post content for links: {e}\n{traceback.format_exc(limit=2)}")

        if self.extract_links_only: 
            self.logger(f"   Extract Links Only mode: Finished processing post {post_id} for links.")
            return 0, 0, [], []

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
                 return 0, 0, [], []
        if self.manga_mode_active and self.manga_filename_style == STYLE_DATE_BASED:
            def natural_sort_key_for_files(file_api_info):
                name = file_api_info.get('_original_name_for_log', '').lower()
                return [int(text) if text.isdigit() else text for text in re.split('([0-9]+)', name)]
            
            all_files_from_post_api.sort(key=natural_sort_key_for_files)
            self.logger(f"   Manga Date Mode: Sorted {len(all_files_from_post_api)} files within post {post_id} by original name for sequential numbering.")


        if not all_files_from_post_api:
            self.logger(f"   No files found to download for post {post_id}.")
            return 0, 0, [], []

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
            return 0, total_skipped_this_post, [], []


        num_files_in_this_post_for_naming = len(files_to_download_info_list)
        self.logger(f"   Identified {num_files_in_this_post_for_naming} unique original file(s) for potential download from post {post_id}.")


        with ThreadPoolExecutor(max_workers=self.num_file_threads, thread_name_prefix=f'P{post_id}File_') as file_pool:
            futures_list = []
            for file_idx, file_info_to_dl in enumerate(files_to_download_info_list):
                if self._check_pause(f"File processing loop for post {post_id}, file {file_idx}"): break
                if self.check_cancel(): break

                current_api_original_filename = file_info_to_dl.get('_original_name_for_log')
                
                file_is_candidate_by_char_filter_scope = False
                char_filter_info_that_matched_file = None 

                if not current_character_filters: 
                    file_is_candidate_by_char_filter_scope = True
                else:
                    if self.char_filter_scope == CHAR_SCOPE_FILES:
                        for filter_item_obj in current_character_filters:
                            terms_to_check_for_file = list(filter_item_obj["aliases"])
                            if filter_item_obj["is_group"] and filter_item_obj["name"] not in terms_to_check_for_file:
                                terms_to_check_for_file.append(filter_item_obj["name"])
                            unique_terms_for_file_check = list(set(terms_to_check_for_file))

                            for term_to_match in unique_terms_for_file_check:
                                if is_filename_match_for_character(current_api_original_filename, term_to_match):
                                    file_is_candidate_by_char_filter_scope = True
                                    char_filter_info_that_matched_file = filter_item_obj
                                    self.logger(f"   File '{current_api_original_filename}' matches char filter term '{term_to_match}' (from '{filter_item_obj['name']}'). Scope: Files.")
                                    break
                            if file_is_candidate_by_char_filter_scope: break
                    elif self.char_filter_scope == CHAR_SCOPE_TITLE:
                        if post_is_candidate_by_title_char_match:
                            file_is_candidate_by_char_filter_scope = True
                            char_filter_info_that_matched_file = char_filter_that_matched_title 
                            self.logger(f"   File '{current_api_original_filename}' is candidate because post title matched. Scope: Title.")
                    elif self.char_filter_scope == CHAR_SCOPE_BOTH:
                        if post_is_candidate_by_title_char_match: 
                            file_is_candidate_by_char_filter_scope = True
                            char_filter_info_that_matched_file = char_filter_that_matched_title
                            self.logger(f"   File '{current_api_original_filename}' is candidate because post title matched. Scope: Both (Title part).")
                        else: 
                            for filter_item_obj_both_file in current_character_filters:
                                terms_to_check_for_file_both = list(filter_item_obj_both_file["aliases"])
                                if filter_item_obj_both_file["is_group"] and filter_item_obj_both_file["name"] not in terms_to_check_for_file_both:
                                    terms_to_check_for_file_both.append(filter_item_obj_both_file["name"])
                                unique_terms_for_file_both_check = list(set(terms_to_check_for_file_both)) 
                                
                                for term_to_match in unique_terms_for_file_both_check:
                                    if is_filename_match_for_character(current_api_original_filename, term_to_match):
                                        file_is_candidate_by_char_filter_scope = True
                                        char_filter_info_that_matched_file = filter_item_obj_both_file 
                                        self.logger(f"   File '{current_api_original_filename}' matches char filter term '{term_to_match}' (from '{filter_item_obj['name']}'). Scope: Both (File part).")
                                        break
                                if file_is_candidate_by_char_filter_scope: break
                    elif self.char_filter_scope == CHAR_SCOPE_COMMENTS:
                        if post_is_candidate_by_file_char_match_in_comment_scope: # Post was candidate due to a file match
                            file_is_candidate_by_char_filter_scope = True
                            char_filter_info_that_matched_file = char_filter_that_matched_file_in_comment_scope # Use the filter that matched a file in the post
                            self.logger(f"   File '{current_api_original_filename}' is candidate because a file in this post matched char filter (Overall Scope: Comments).")
                        elif post_is_candidate_by_comment_char_match: # Post was candidate due to comment match (no file match for post)
                            file_is_candidate_by_char_filter_scope = True
                            char_filter_info_that_matched_file = char_filter_that_matched_comment # Use the filter that matched comments
                            self.logger(f"   File '{current_api_original_filename}' is candidate because post comments matched char filter (Overall Scope: Comments).")
                
                if not file_is_candidate_by_char_filter_scope:
                    self.logger(f"   -> Skip File (Char Filter Scope '{self.char_filter_scope}'): '{current_api_original_filename}' no match.")
                    total_skipped_this_post += 1
                    continue

                current_path_for_file = self.download_root

                if self.use_subfolders:
                    char_title_subfolder_name = None
                    if self.target_post_id_from_initial_url and self.custom_folder_name:
                        char_title_subfolder_name = self.custom_folder_name
                    elif char_filter_info_that_matched_file: 
                        char_title_subfolder_name = clean_folder_name(char_filter_info_that_matched_file["name"])
                    elif char_filter_that_matched_title: 
                        char_title_subfolder_name = clean_folder_name(char_filter_that_matched_title["name"])
                    elif base_folder_names_for_post_content:
                        char_title_subfolder_name = base_folder_names_for_post_content[0]
                    
                    if char_title_subfolder_name:
                        current_path_for_file = os.path.join(current_path_for_file, char_title_subfolder_name)
                
                if self.use_post_subfolders:
                    cleaned_title_for_subfolder = clean_folder_name(post_title)
                    post_specific_subfolder_name = cleaned_title_for_subfolder # Use only the cleaned title
                    current_path_for_file = os.path.join(current_path_for_file, post_specific_subfolder_name)
                
                target_folder_path_for_this_file = current_path_for_file
                
                manga_date_counter_to_pass = None
                manga_global_counter_to_pass = None
                if self.manga_mode_active:
                    if self.manga_filename_style == STYLE_DATE_BASED:
                        manga_date_counter_to_pass = self.manga_date_file_counter_ref
                    elif self.manga_filename_style == STYLE_POST_TITLE_GLOBAL_NUMBERING:
                        manga_global_counter_to_pass = self.manga_global_file_counter_ref if self.manga_global_file_counter_ref is not None else self.manga_date_file_counter_ref

                futures_list.append(file_pool.submit(
                    self._download_single_file,
                    file_info_to_dl,
                    target_folder_path_for_this_file,
                    headers,
                    post_id,
                    self.skip_current_file_flag,
                    post_title=post_title,
                    manga_date_file_counter_ref=manga_date_counter_to_pass,
                    manga_global_file_counter_ref=manga_global_counter_to_pass,
                    file_index_in_post=file_idx, # Changed to keyword argument
                    num_files_in_this_post=num_files_in_this_post_for_naming # Changed to keyword argument
                ))

            for future in as_completed(futures_list):
                if self.check_cancel():
                    for f_to_cancel in futures_list:
                        if not f_to_cancel.done():
                            f_to_cancel.cancel()
                    break
                try:
                    dl_count, skip_count, actual_filename_saved, original_kept_flag, status, retry_details = future.result()
                    total_downloaded_this_post += dl_count
                    total_skipped_this_post += skip_count
                    if original_kept_flag and dl_count > 0 and actual_filename_saved:
                        kept_original_filenames_for_log.append(actual_filename_saved)
                    if status == FILE_DOWNLOAD_STATUS_FAILED_RETRYABLE_LATER and retry_details:
                        retryable_failures_this_post.append(retry_details)
                except CancelledError:
                    self.logger(f"   File download task for post {post_id} was cancelled.")
                    total_skipped_this_post += 1
                except Exception as exc_f:
                    self.logger(f"❌ File download task for post {post_id} resulted in error: {exc_f}")
                    total_skipped_this_post += 1
        self._emit_signal('file_progress', "", None)

        if self.check_cancel(): self.logger(f"   Post {post_id} processing interrupted/cancelled.");
        else: self.logger(f"   Post {post_id} Summary: Downloaded={total_downloaded_this_post}, Skipped Files={total_skipped_this_post}")

        return total_downloaded_this_post, total_skipped_this_post, kept_original_filenames_for_log, retryable_failures_this_post


class DownloadThread(QThread):
    progress_signal = pyqtSignal(str) # Already QObject, no need to change
    add_character_prompt_signal = pyqtSignal(str)
    file_download_status_signal = pyqtSignal(bool)
    finished_signal = pyqtSignal(int, int, bool, list)
    external_link_signal = pyqtSignal(str, str, str, str)
    file_progress_signal = pyqtSignal(str, object)
    retryable_file_failed_signal = pyqtSignal(list) # New: list of retry_details dicts
    missed_character_post_signal = pyqtSignal(str, str) # New: post_title, reason


    def __init__(self, api_url_input, output_dir, known_names_copy,
                 cancellation_event,
                 pause_event, filter_character_list=None, dynamic_character_filter_holder=None, # Added pause_event and holder
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
                 char_filter_scope=CHAR_SCOPE_FILES, # manga_date_file_counter_ref removed from here
                 remove_from_filename_words_list=None,
                 manga_date_prefix=MANGA_DATE_PREFIX_DEFAULT, # New parameter
                 allow_multipart_download=True,
                 selected_cookie_file=None, # New parameter for selected cookie file
                 app_base_dir=None, # New parameter
                 manga_date_file_counter_ref=None, # New parameter
                 manga_global_file_counter_ref=None, # New parameter for global numbering
                 use_cookie=False, # Added: Expected by main.py
                 cookie_text="",   # Added: Expected by main.py
                 ):
        super().__init__()
        self.api_url_input = api_url_input
        self.output_dir = output_dir
        self.known_names = list(known_names_copy)
        self.cancellation_event = cancellation_event
        self.pause_event = pause_event # Store pause_event
        self.skip_current_file_flag = skip_current_file_flag
        self.initial_target_post_id = target_post_id_from_initial_url
        self.filter_character_list_objects_initial = filter_character_list if filter_character_list else [] # Store initial
        self.dynamic_filter_holder = dynamic_character_filter_holder # Store the holder
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
        self.remove_from_filename_words_list = remove_from_filename_words_list
        self.manga_date_prefix = manga_date_prefix # Store the prefix
        self.allow_multipart_download = allow_multipart_download
        self.selected_cookie_file = selected_cookie_file # Store selected cookie file
        self.app_base_dir = app_base_dir # Store app base dir
        self.cookie_text = cookie_text # Store cookie text
        self.use_cookie = use_cookie # Store cookie setting
        self.manga_date_file_counter_ref = manga_date_file_counter_ref # Store for passing to worker by DownloadThread
        self.manga_global_file_counter_ref = manga_global_file_counter_ref # Store for global numbering
        if self.compress_images and Image is None:
            self.logger("⚠️ Image compression disabled: Pillow library not found (DownloadThread).")
            self.compress_images = False

    def logger(self, message):
        self.progress_signal.emit(str(message))

    def isInterruptionRequested(self):
        return self.cancellation_event.is_set() or super().isInterruptionRequested()

    def _check_pause_self(self, context_message="DownloadThread operation"):
        if self.pause_event and self.pause_event.is_set():
            self.logger(f"   {context_message} paused...")
            while self.pause_event.is_set():
                if self.isInterruptionRequested():
                    self.logger(f"   {context_message} cancelled while paused.")
                    return True # Indicates cancellation occurred
                time.sleep(0.5)
            if not self.isInterruptionRequested(): self.logger(f"   {context_message} resumed.")
        return False

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
        current_manga_date_file_counter_ref = self.manga_date_file_counter_ref
        if self.manga_mode_active and self.manga_filename_style == STYLE_DATE_BASED and \
           not self.extract_links_only and current_manga_date_file_counter_ref is None: # Check if it needs calculation
            series_scan_dir = self.output_dir
            if self.use_subfolders:
                if self.filter_character_list_objects_initial and self.filter_character_list_objects_initial[0] and self.filter_character_list_objects_initial[0].get("name"):
                    series_folder_name = clean_folder_name(self.filter_character_list_objects_initial[0]["name"])
                    series_scan_dir = os.path.join(series_scan_dir, series_folder_name)
                elif self.service and self.user_id:
                    creator_based_folder_name = clean_folder_name(self.user_id)
                    series_scan_dir = os.path.join(series_scan_dir, creator_based_folder_name)

            highest_num = 0
            if os.path.isdir(series_scan_dir):
                self.logger(f"ℹ️ [Thread] Manga Date Mode: Scanning for existing files in '{series_scan_dir}'...")
                for dirpath, _, filenames_in_dir in os.walk(series_scan_dir):
                    for filename_to_check in filenames_in_dir:
                        base_name_no_ext = os.path.splitext(filename_to_check)[0]
                        match = re.match(r"(\d{3,})", base_name_no_ext)
                        if match: highest_num = max(highest_num, int(match.group(1))) # Corrected indentation
            current_manga_date_file_counter_ref = [highest_num + 1, threading.Lock()]
            self.logger(f"ℹ️ [Thread] Manga Date Mode: Initialized counter at {current_manga_date_file_counter_ref[0]}.")
        elif self.manga_mode_active and self.manga_filename_style == STYLE_POST_TITLE_GLOBAL_NUMBERING and not self.extract_links_only and current_manga_date_file_counter_ref is None: # Use current_manga_date_file_counter_ref for STYLE_POST_TITLE_GLOBAL_NUMBERING as well
            # For global numbering, we always start from 1 for the session unless a ref is passed.
            # If you need to resume global numbering across sessions, similar scanning logic would be needed.
            # For now, it starts at 1 per session if no ref is provided.
            current_manga_date_file_counter_ref = [1, threading.Lock()] # Start global numbering at 1
            self.logger(f"ℹ️ [Thread] Manga Title+GlobalNum Mode: Initialized counter at {current_manga_date_file_counter_ref[0]}.")

        worker_signals_obj = PostProcessorSignals()
        try:
            worker_signals_obj.progress_signal.connect(self.progress_signal)
            worker_signals_obj.file_download_status_signal.connect(self.file_download_status_signal)
            worker_signals_obj.file_progress_signal.connect(self.file_progress_signal)
            worker_signals_obj.external_link_signal.connect(self.external_link_signal)
            worker_signals_obj.missed_character_post_signal.connect(self.missed_character_post_signal)

            self.logger("   Starting post fetch (single-threaded download process)...")
            post_generator = download_from_api(
                self.api_url_input,
                logger=self.logger,
                start_page=self.start_page,
                end_page=self.end_page,
                manga_mode=self.manga_mode_active,
                cancellation_event=self.cancellation_event, # type: ignore
                pause_event=self.pause_event, # Pass pause_event
                use_cookie=self.use_cookie, # Pass cookie settings for API calls
                cookie_text=self.cookie_text,
                selected_cookie_file=self.selected_cookie_file,
                app_base_dir=self.app_base_dir
            )

            for posts_batch_data in post_generator:
                if self._check_pause_self("Post batch processing"): was_process_cancelled = True; break
                if self.isInterruptionRequested(): was_process_cancelled = True; break
                for individual_post_data in posts_batch_data:
                    if self._check_pause_self(f"Individual post processing for {individual_post_data.get('id', 'N/A')}"): was_process_cancelled = True; break
                    if self.isInterruptionRequested(): was_process_cancelled = True; break

                    post_processing_worker = PostProcessorWorker(
                         post_data=individual_post_data,
                         download_root=self.output_dir,
                         known_names=self.known_names,
                         filter_character_list=self.filter_character_list_objects_initial, # Pass initial
                         dynamic_character_filter_holder=self.dynamic_filter_holder, # Pass the holder
                         unwanted_keywords=self.unwanted_keywords,
                         filter_mode=self.filter_mode,
                         skip_zip=self.skip_zip, skip_rar=self.skip_rar,
                         use_subfolders=self.use_subfolders, use_post_subfolders=self.use_post_subfolders,
                         target_post_id_from_initial_url=self.initial_target_post_id,
                         custom_folder_name=self.custom_folder_name,
                         compress_images=self.compress_images, download_thumbnails=self.download_thumbnails,
                         service=self.service, user_id=self.user_id,
                         api_url_input=self.api_url_input,
                         pause_event=self.pause_event, # Pass pause_event to worker
                         cancellation_event=self.cancellation_event, # emitter is PostProcessorSignals for single-thread
                         emitter=worker_signals_obj, # Pass the signals object as the emitter
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
                         manga_date_prefix=self.manga_date_prefix, # Pass the prefix
                         char_filter_scope=self.char_filter_scope,
                         remove_from_filename_words_list=self.remove_from_filename_words_list,
                         allow_multipart_download=self.allow_multipart_download,
                         selected_cookie_file=self.selected_cookie_file, # Pass selected cookie file
                         app_base_dir=self.app_base_dir, # Pass app_base_dir
                         cookie_text=self.cookie_text, # Pass cookie text
                         manga_global_file_counter_ref=self.manga_global_file_counter_ref, # Pass the ref
                         use_cookie=self.use_cookie, # Pass cookie setting to worker
                         manga_date_file_counter_ref=current_manga_date_file_counter_ref, # Pass the calculated or passed-in ref
                         )
                    try:
                        dl_count, skip_count, kept_originals_this_post, retryable_failures = post_processing_worker.process()
                        grand_total_downloaded_files += dl_count
                        grand_total_skipped_files += skip_count
                        if kept_originals_this_post:
                            grand_list_of_kept_original_filenames.extend(kept_originals_this_post)
                        if retryable_failures:
                            self.retryable_file_failed_signal.emit(retryable_failures)
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
                    worker_signals_obj.missed_character_post_signal.disconnect(self.missed_character_post_signal)
            except (TypeError, RuntimeError) as e:
                self.logger(f"ℹ️ Note during DownloadThread signal disconnection: {e}")
            
            self.finished_signal.emit(grand_total_downloaded_files, grand_total_skipped_files, self.isInterruptionRequested(), grand_list_of_kept_original_filenames)

    def receive_add_character_result(self, result):
        with QMutexLocker(self.prompt_mutex):
             self._add_character_response = result
        self.logger(f"   (DownloadThread) Received character prompt response: {'Yes (added/confirmed)' if result else 'No (declined/failed)'}")
