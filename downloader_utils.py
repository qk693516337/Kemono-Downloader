import os
import time
import requests
import re
import threading
import queue
import hashlib
from concurrent.futures import ThreadPoolExecutor, Future, CancelledError

from PyQt5.QtCore import QObject, pyqtSignal, QThread, QMutex, QMutexLocker
from urllib.parse import urlparse
try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow library not found. Please install it: pip install Pillow")
    Image = None

from io import BytesIO

fastapi_app = None
KNOWN_NAMES = []

def clean_folder_name(name):
    if not isinstance(name, str): name = str(name)
    cleaned = re.sub(r'[^\w\s\-\_]', '', name)
    return cleaned.strip().replace(' ', '_')

def clean_filename(name):
     if not isinstance(name, str): name = str(name)
     cleaned = re.sub(r'[^\w\s\-\_\.]', '', name)
     return cleaned.strip().replace(' ', '_')

def extract_folder_name_from_title(title, unwanted_keywords):
    if not title: return 'Uncategorized'
    title_lower = title.lower()
    tokens = title_lower.split()
    for token in tokens:
        clean_token = clean_folder_name(token)
        if clean_token and clean_token not in unwanted_keywords:
            return clean_token
    return 'Uncategorized'

def match_folders_from_title(title, known_names, unwanted_keywords):
    if not title: return []
    cleaned_title = clean_folder_name(title.lower())
    matched_cleaned_names = set()

    for name in known_names:
        cleaned_name_for_match = clean_folder_name(name.lower())
        if not cleaned_name_for_match: continue
        if cleaned_name_for_match in cleaned_title:
            if cleaned_name_for_match not in unwanted_keywords:
                 matched_cleaned_names.add(cleaned_name_for_match)
    return list(matched_cleaned_names)

def is_image(filename):
    if not filename: return False
    return filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))

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
    service, user_id, post_id = None, None, None
    if not isinstance(url_string, str) or not url_string.strip():
        return None, None, None
    try:
        parsed_url = urlparse(url_string.strip())
        domain = parsed_url.netloc.lower()
        path_parts = [part for part in parsed_url.path.strip('/').split('/') if part]
        is_kemono = 'kemono.su' in domain or 'kemono.party' in domain
        is_coomer = 'coomer.su' in domain or 'coomer.party' in domain
        if not (is_kemono or is_coomer):
            return None, None, None
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
    except ValueError:
        print(f"Debug: ValueError parsing URL '{url_string}'")
        return None, None, None
    except Exception as e:
        print(f"Debug: Exception during extract_post_info for URL '{url_string}': {e}")
        return None, None, None
    return None, None, None

def fetch_posts_paginated(api_url_base, headers, offset, logger):
    paginated_url = f'{api_url_base}?o={offset}'
    logger(f"   Fetching: {paginated_url}")
    try:
        response = requests.get(paginated_url, headers=headers, timeout=45)
        response.raise_for_status()
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
    except ValueError as e:
        raise RuntimeError(f"Error decoding JSON response for offset {offset}: {e}. Body: {response.text[:200]}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error processing page offset {offset}: {e}")

def download_from_api(api_url_input, logger=print):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    service, user_id, target_post_id = extract_post_info(api_url_input)

    if not service or not user_id:
        logger(f"❌ Invalid or unrecognized URL: {api_url_input}. Cannot fetch.")
        return

    parsed_input = urlparse(api_url_input)
    api_domain = parsed_input.netloc if ('kemono.su' in parsed_input.netloc.lower() or 'coomer.su' in parsed_input.netloc.lower() or 'kemono.party' in parsed_input.netloc.lower() or 'coomer.party' in parsed_input.netloc.lower()) else "kemono.su"
    api_base_url = f"https://{api_domain}/api/v1/{service}/user/{user_id}"

    offset = 0
    page = 1
    processed_target_post = False

    while True:
        if target_post_id and processed_target_post:
            logger(f"✅ Target post {target_post_id} found and processed. Stopping.")
            break

        logger(f"\n🔄 Fetching page {page} (offset {offset}) for user {user_id} on {api_domain}...")
        try:
            posts_batch = fetch_posts_paginated(api_base_url, headers, offset, logger)
            if not isinstance(posts_batch, list):
                 logger(f"❌ API Error: Expected a list of posts, got {type(posts_batch)}. Response: {str(posts_batch)[:200]}")
                 break
        except RuntimeError as e:
            logger(f"❌ {e}")
            logger("   Aborting pagination due to error.")
            break
        except Exception as e:
             logger(f"❌ Unexpected error during fetch loop: {e}")
             break

        if not posts_batch:
            if page == 1 and not target_post_id:
                 logger("😕 No posts found for this creator.")
            elif not target_post_id:
                 logger("✅ Reached end of posts.")
            break

        logger(f"📦 Found {len(posts_batch)} posts on page {page}.")

        if target_post_id:
            matching_post = next((post for post in posts_batch if str(post.get('id')) == str(target_post_id)), None)

            if matching_post:
                logger(f"🎯 Found target post {target_post_id} on page {page}.")
                yield [matching_post]
                processed_target_post = True
            else:
                logger(f"   Target post {target_post_id} not found on this page.")
                pass
        else:
            yield posts_batch
        if not (target_post_id and processed_target_post):
            page_size = 50
            offset += page_size
            page += 1
            time.sleep(0.6)
    if target_post_id and not processed_target_post:
        logger(f"❌ Target post ID {target_post_id} was not found for this creator.")

class PostProcessorSignals(QObject):
    progress_signal = pyqtSignal(str)
    file_download_status_signal = pyqtSignal(bool)

class PostProcessorWorker:
    def __init__(self, post_data, download_root, known_names, filter_character,
                 unwanted_keywords, filter_mode, skip_zip, skip_rar,
                 use_subfolders, target_post_id_from_initial_url, custom_folder_name,
                 compress_images, download_thumbnails, service, user_id,
                 api_url_input, cancellation_event, signals,
                 downloaded_files, downloaded_file_hashes, downloaded_files_lock, downloaded_file_hashes_lock,
                 skip_words_list=None):
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
        self.api_url_input = api_url_input
        self.cancellation_event = cancellation_event
        self.signals = signals
        self.skip_current_file_flag = threading.Event()
        self.is_downloading_file = False
        self.current_download_path = None
        self.downloaded_files = downloaded_files
        self.downloaded_file_hashes = downloaded_file_hashes
        self.downloaded_files_lock = downloaded_files_lock
        self.downloaded_file_hashes_lock = downloaded_file_hashes_lock
        self.skip_words_list = skip_words_list if skip_words_list is not None else []
        if self.compress_images and Image is None:
            self.logger("⚠️ Image compression enabled, but Pillow library is not loaded. Disabling compression.")
            self.compress_images = False

    def logger(self, message):
        if self.signals and hasattr(self.signals, 'progress_signal'):
            self.signals.progress_signal.emit(message)
        else:
            print(f"(Worker Log): {message}")

    def check_cancel(self):
        is_cancelled = self.cancellation_event.is_set()
        return is_cancelled

    def skip_file(self):
        pass

    def process(self):
        if self.check_cancel(): return 0, 0

        total_downloaded_post = 0
        total_skipped_post = 0
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': f'https://{urlparse(self.api_url_input).netloc}/'}
        url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
        LARGE_THUMBNAIL_THRESHOLD = 1 * 1024 * 1024

        post = self.post
        api_title = post.get('title', '')
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
                    return 0, 1


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
            folder_names_for_post = []
            if self.filter_character:
                clean_char_filter = clean_folder_name(self.filter_character.lower())
                matched_names_in_title = match_folders_from_title(title, self.known_names, self.unwanted_keywords)

                if clean_char_filter and clean_char_filter in matched_names_in_title:
                    folder_names_for_post = [clean_char_filter]
                    folder_decision_reason = f"Character filter '{self.filter_character}' matched title. Using folder '{clean_char_filter}'."
                else:
                    self.logger(f"   -> Filter Skip Post {post_id}: Character filter '{self.filter_character}' not found in title matches ({matched_names_in_title}).")
                    return 0, 1
            else:
                matched_folders = match_folders_from_title(title, self.known_names, self.unwanted_keywords)
                if matched_folders:
                    folder_names_for_post = matched_folders
                    folder_decision_reason = f"Found known name(s) in title: {matched_folders}"
                else:
                    extracted_folder = extract_folder_name_from_title(title, self.unwanted_keywords)
                    folder_names_for_post = [extracted_folder]
                    folder_decision_reason = f"No known names in title. Using derived folder: '{extracted_folder}'"
            for folder_name in folder_names_for_post:
                folder_path_full = os.path.join(self.download_root, folder_name)
                valid_folder_paths.append(folder_path_full)
        if not valid_folder_paths:
            valid_folder_paths = [self.download_root]
            if not folder_decision_reason:
                folder_decision_reason = "Subfolders disabled or no specific folder determined. Using root download directory."


        self.logger(f"   Folder Decision: {folder_decision_reason}")
        if not valid_folder_paths:
             self.logger(f"   ERROR: No valid folder paths determined for post {post_id}. Skipping.")
             return 0, 1
        if post_content:
            try:
                found_links = re.findall(r'href=["\'](https?://[^"\']+)["\']', post_content)
                if found_links:
                    self.logger(f"🔗 Links found in post content:")
                    unique_links = sorted(list(set(found_links)))
                    for link in unique_links[:10]:
                        if not any(x in link for x in ['.css', '.js', 'javascript:']):
                             self.logger(f"   - {link}")
                    if len(unique_links) > 10:
                        self.logger(f"   - ... ({len(unique_links) - 10} more links not shown)")
            except Exception as e:
                 self.logger(f"⚠️ Error parsing content for links in post {post_id}: {e}")
        files_to_process_for_download = []
        api_domain = urlparse(self.api_url_input).netloc if ('kemono.su' in urlparse(self.api_url_input).netloc.lower() or 'coomer.su' in urlparse(self.api_url_input).netloc.lower() or 'kemono.party' in urlparse(self.api_url_input).netloc.lower() or 'coomer.party' in urlparse(self.api_url_input).netloc.lower()) else "kemono.su"

        if self.download_thumbnails:
            self.logger(f"   Mode: Attempting to download thumbnail...")
            self.logger("      Thumbnail download via API is disabled as the local API is not used.")
            self.logger(f"   -> Skipping Post {post_id}: Thumbnail download requested but API is disabled.")
            return 0, 1

        else:
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
                         if base and base != f"{post_id}_{attachment_counter}":
                             final_attach_name = f"{post_id}_{attachment_counter}_{base}{ext}"


                         attach_url = f"https://{api_domain}/data/{attach_path}"
                         files_to_process_for_download.append({
                             'url': attach_url, 'name': final_attach_name,
                             '_is_thumbnail': False, '_source': f'attachment_{idx+1}',
                             '_original_name_for_log': attach_name
                         })
                         attachment_counter += 1

                    else:
                          self.logger(f"   ⚠️ Skipping attachment {idx+1}: Missing filename (Path: {attach_path})")
                else:
                     self.logger(f"   ⚠️ Skipping invalid attachment entry {idx+1}: {str(attachment)[:100]}")


        if not files_to_process_for_download:
            self.logger(f"   No files found to download for post {post_id}.")
            return 0, 0

        self.logger(f"   Files identified for download: {len(files_to_process_for_download)}")
        post_download_count = 0
        post_skip_count = 0
        local_processed_filenames = set()
        local_filenames_lock = threading.Lock()


        for file_info in files_to_process_for_download:
            if self.check_cancel(): break
            if self.skip_current_file_flag.is_set():
                original_name_for_log = file_info.get('_original_name_for_log', file_info.get('name', 'unknown_file'))
                self.logger(f"⏭️ File skip requested: {original_name_for_log}")
                post_skip_count += 1
                self.skip_current_file_flag.clear()
                continue

            file_url = file_info.get('url')
            original_filename = file_info.get('name')
            is_thumbnail = file_info.get('_is_thumbnail', False)
            original_name_for_log = file_info.get('_original_name_for_log', original_filename)

            if not file_url or not original_filename:
                 self.logger(f"⚠️ Skipping file entry due to missing URL or name: {str(file_info)[:100]}")
                 post_skip_count += 1
                 continue

            cleaned_save_filename = clean_filename(original_filename)
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
                    continue
            if not self.download_thumbnails:
                file_skipped_by_filter = False
                is_img = is_image(cleaned_save_filename)
                is_vid = is_video(cleaned_save_filename)
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
                    continue
            file_downloaded_or_exists = False
            for folder_path in valid_folder_paths:
                if self.check_cancel(): break
                try:
                    os.makedirs(folder_path, exist_ok=True)
                except OSError as e:
                    self.logger(f"❌ Error ensuring directory exists {folder_path}: {e}. Skipping path.")
                    continue
                except Exception as e:
                    self.logger(f"❌ Unexpected error creating dir {folder_path}: {e}. Skipping path.")
                    continue

                save_path = os.path.join(folder_path, cleaned_save_filename)
                folder_basename = os.path.basename(folder_path)
                with local_filenames_lock:
                    if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                         self.logger(f"   -> Exists Skip: '{original_name_for_log}' in '{folder_basename}'")
                         post_skip_count += 1
                         file_downloaded_or_exists = True
                         with self.downloaded_files_lock:
                             self.downloaded_files.add(cleaned_save_filename)
                         break
                    elif cleaned_save_filename in local_processed_filenames:
                         self.logger(f"   -> Local Skip: '{original_name_for_log}' in '{folder_basename}' (already processed in this post)")
                         post_skip_count += 1
                         file_downloaded_or_exists = True
                         with self.downloaded_files_lock:
                             self.downloaded_files.add(cleaned_save_filename)
                         break
                    with self.downloaded_files_lock:
                         if cleaned_save_filename in self.downloaded_files:
                             self.logger(f"   -> Global Filename Skip: '{original_name_for_log}' in '{folder_basename}' (filename already downloaded globally)")
                             post_skip_count += 1
                             file_downloaded_or_exists = True
                             break
                try:
                    self.logger(f"⬇️ Downloading '{original_name_for_log}' to '{folder_basename}'...")
                    self.current_download_path = save_path
                    self.is_downloading_file = True
                    self.signals.file_download_status_signal.emit(True)
                    response = requests.get(file_url, headers=headers, timeout=(15, 300), stream=True)
                    response.raise_for_status()
                    file_content_bytes = BytesIO()
                    downloaded_size = 0
                    chunk_count = 0
                    md5_hash = hashlib.md5()

                    for chunk in response.iter_content(chunk_size=32 * 1024):
                        if self.check_cancel(): break
                        if self.skip_current_file_flag.is_set(): break

                        if chunk:
                            file_content_bytes.write(chunk)
                            md5_hash.update(chunk)
                            downloaded_size += len(chunk)
                            chunk_count += 1
                    if self.check_cancel() or self.skip_current_file_flag.is_set():
                        self.logger(f"   ⚠️ Download interrupted {'(cancelled)' if self.cancellation_event.is_set() else '(skipped)'} for {original_name_for_log}.")
                        if self.skip_current_file_flag.is_set():
                             post_skip_count += 1
                             self.skip_current_file_flag.clear()
                        break
                    final_save_path = save_path
                    current_filename_for_log = cleaned_save_filename
                    file_content_bytes.seek(0)

                    if downloaded_size == 0 and chunk_count > 0:
                         self.logger(f"⚠️ Warning: Downloaded 0 bytes despite receiving chunks for {original_name_for_log}. Skipping save.")
                         post_skip_count += 1
                         break

                    if downloaded_size > 0:
                        calculated_hash = md5_hash.hexdigest()
                        with self.downloaded_file_hashes_lock:
                             if calculated_hash in self.downloaded_file_hashes:
                                self.logger(f"   -> Content Skip: '{original_name_for_log}' (Hash: {calculated_hash}) already downloaded.")
                                post_skip_count += 1
                                file_downloaded_or_exists = True
                                with self.downloaded_files_lock:
                                     self.downloaded_files.add(cleaned_save_filename)
                                with local_filenames_lock:
                                     local_processed_filenames.add(cleaned_save_filename)
                                break
                             else:
                                 pass


                        if not file_downloaded_or_exists:
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
                                        img.save(compressed_bytes, format='WebP', quality=75, method=4)
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
                                        file_content_bytes.seek(0)
                                        final_bytes_to_save = file_content_bytes

                                except Exception as comp_e:
                                    self.logger(f"❌ Image compression failed for {original_name_for_log}: {comp_e}. Saving original.")
                                    file_content_bytes.seek(0)
                                    final_bytes_to_save = file_content_bytes
                                    final_save_path = save_path

                            elif is_img_for_compress and not is_thumbnail and self.compress_images:
                                 self.logger(f"   Skipping compression: Image size ({downloaded_size / 1024:.2f} KB) below threshold.")
                                 file_content_bytes.seek(0)
                                 final_bytes_to_save = file_content_bytes

                            elif is_thumbnail and downloaded_size > LARGE_THUMBNAIL_THRESHOLD:
                                  self.logger(f"⚠️ Downloaded thumbnail '{current_filename_for_log}' ({downloaded_size / 1024:.2f} KB) is large.")
                                  file_content_bytes.seek(0)
                                  final_bytes_to_save = file_content_bytes
                            else:
                                file_content_bytes.seek(0)
                                final_bytes_to_save = file_content_bytes
                            save_file = False
                            with self.downloaded_files_lock:
                                 with local_filenames_lock:
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
                                         save_file = True


                            if save_file:
                                try:
                                    with open(final_save_path, 'wb') as f:
                                        while True:
                                            chunk = final_bytes_to_save.read(64 * 1024)
                                            if not chunk: break
                                            f.write(chunk)
                                    with self.downloaded_file_hashes_lock:
                                         self.downloaded_file_hashes.add(calculated_hash)
                                    with self.downloaded_files_lock:
                                         self.downloaded_files.add(current_filename_for_log)
                                    with local_filenames_lock:
                                         local_processed_filenames.add(current_filename_for_log)

                                    post_download_count += 1
                                    file_downloaded_or_exists = True
                                    self.logger(f"✅ Saved: '{current_filename_for_log}' ({downloaded_size / 1024:.1f} KB, Hash: {calculated_hash[:8]}...) in '{folder_basename}'")
                                    time.sleep(0.05)

                                except IOError as io_err:
                                     self.logger(f"❌ Save Fail: '{current_filename_for_log}' to '{folder_basename}'. Error: {io_err}")
                                     post_skip_count += 1
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
                                     break
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
                     break
                except Exception as e:
                     self.logger(f"❌ Unexpected Error during download/save for {original_name_for_log}: {e}")
                     import traceback
                     self.logger(f"   Traceback: {traceback.format_exc(limit=2)}")
                     post_skip_count += 1
                     break

                finally:
                    self.is_downloading_file = False
                    self.current_download_path = None
                    self.signals.file_download_status_signal.emit(False)
            if self.check_cancel(): break
            if self.skip_current_file_flag.is_set():
                 self.skip_current_file_flag.clear()
            if not file_downloaded_or_exists:
                 pass
        if self.check_cancel():
            self.logger(f"   Post {post_id} processing cancelled.")
            return post_download_count, post_skip_count


        self.logger(f"   Post {post_id} Summary: Downloaded={post_download_count}, Skipped={post_skip_count}")
        return post_download_count, post_skip_count

class DownloadThread(QThread):
    progress_signal = pyqtSignal(str)
    add_character_prompt_signal = pyqtSignal(str)
    file_download_status_signal = pyqtSignal(bool)
    finished_signal = pyqtSignal(int, int, bool)


    def __init__(self, api_url, output_dir, known_names_copy,
                 cancellation_event, single_post_id=None,
                 filter_character=None, filter_mode='all', skip_zip=True, skip_rar=True,
                 use_subfolders=True, custom_folder_name=None, compress_images=False,
                 download_thumbnails=False, service=None, user_id=None,
                 downloaded_files=None, downloaded_files_lock=None,
                 downloaded_file_hashes=None, downloaded_file_hashes_lock=None,
                 skip_words_list=None):
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
        self.service = service
        self.user_id = user_id
        self.skip_words_list = skip_words_list if skip_words_list is not None else []
        self.downloaded_files = downloaded_files if downloaded_files is not None else set()
        self.downloaded_files_lock = downloaded_files_lock if downloaded_files_lock is not None else threading.Lock()
        self.downloaded_file_hashes = downloaded_file_hashes if downloaded_file_hashes is not None else set()
        self.downloaded_file_hashes_lock = downloaded_file_hashes_lock if downloaded_file_hashes_lock is not None else threading.Lock()
        self.skip_current_file_flag = threading.Event()
        self.is_downloading_file = False
        self.current_download_path = None
        self._add_character_response = None
        self.prompt_mutex = QMutex()
        if not self.service or not self.user_id:
             log_msg = f"❌ Thread Init Error: Missing service ('{self.service}') or user ID ('{self.user_id}') for URL '{api_url}'"
             print(log_msg)
             try: self.progress_signal.emit(log_msg)
             except RuntimeError: pass
             self._init_failed = True


    def run(self):
        if self._init_failed:
             self.finished_signal.emit(0, 0, False)
             return

        unwanted_keywords = {'spicy', 'hd', 'nsfw', '4k', 'preview'}
        grand_total_downloaded = 0
        grand_total_skipped = 0
        cancelled_by_user = False

        try:
            if self.use_subfolders and self.filter_character and not self.custom_folder_name:
                if not self._check_and_prompt_filter_character():
                    self.finished_signal.emit(0, 0, False)
                    return
            worker_signals_adapter = PostProcessorSignals()
            worker_signals_adapter.progress_signal.connect(self.progress_signal)
            worker_signals_adapter.file_download_status_signal.connect(self.file_download_status_signal)

            post_worker = PostProcessorWorker(
                 post_data=None,
                 download_root=self.output_dir,
                 known_names=self.known_names,
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
                 cancellation_event=self.cancellation_event,
                 signals=worker_signals_adapter,
                 downloaded_files=self.downloaded_files,
                 downloaded_files_lock=self.downloaded_files_lock,
                 downloaded_file_hashes=self.downloaded_file_hashes,
                 downloaded_file_hashes_lock=self.downloaded_file_hashes_lock,
                 skip_words_list=self.skip_words_list,
            )
            post_worker.skip_current_file_flag = self.skip_current_file_flag
            self.progress_signal.emit("   Starting post fetch...")
            def thread_logger(msg):
                self.progress_signal.emit(msg)

            post_generator = download_from_api(self.api_url_input, logger=thread_logger)

            for posts_batch in post_generator:
                if self.isInterruptionRequested():
                    self.progress_signal.emit("⚠️ Download cancelled before processing batch.")
                    cancelled_by_user = True
                    break

                for post in posts_batch:
                    if self.isInterruptionRequested():
                        self.progress_signal.emit("⚠️ Download cancelled during post processing.")
                        cancelled_by_user = True
                        break
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
                         grand_total_skipped += 1
                    self.msleep(20)

                if cancelled_by_user:
                    break
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
            cancelled_by_user = False

        finally:
            self.finished_signal.emit(grand_total_downloaded, grand_total_skipped, cancelled_by_user)


    def _check_and_prompt_filter_character(self):
        clean_char_filter = clean_folder_name(self.filter_character.lower())
        known_names_lower = {name.lower() for name in self.known_names}

        if not clean_char_filter:
             self.progress_signal.emit(f"❌ Filter name '{self.filter_character}' is invalid. Aborting.")
             return False

        if self.filter_character.lower() not in known_names_lower:
            self.progress_signal.emit(f"❓ Filter '{self.filter_character}' not found in known list.")
            with QMutexLocker(self.prompt_mutex):
                 self._add_character_response = None
            self.add_character_prompt_signal.emit(self.filter_character)
            self.progress_signal.emit("   Waiting for user confirmation to add filter name...")
            while self._add_character_response is None:
                if self.isInterruptionRequested():
                    self.progress_signal.emit("⚠️ Cancelled while waiting for user input on filter name.")
                    return False
                self.msleep(200)
            if self._add_character_response:
                self.progress_signal.emit(f"✅ User confirmed adding '{self.filter_character}'. Continuing.")
                if self.filter_character not in self.known_names:
                    self.known_names.append(self.filter_character)
                return True
            else:
                self.progress_signal.emit(f"❌ User declined to add filter '{self.filter_character}'. Aborting download.")
                return False
        return True


    def skip_file(self):
        if self.isRunning() and self.is_downloading_file:
             self.progress_signal.emit("⏭️ Skip requested for current file.")
             self.skip_current_file_flag.set()
        elif self.isRunning():
             self.progress_signal.emit("ℹ️ Skip requested, but no file download active.")


    def receive_add_character_result(self, result):
        with QMutexLocker(self.prompt_mutex):
             self._add_character_response = result
        self.progress_signal.emit(f"   Received prompt response: {'Yes' if result else 'No'}")


    def isInterruptionRequested(self):
        return super().isInterruptionRequested() or self.cancellation_event.is_set()