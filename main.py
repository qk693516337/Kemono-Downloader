import sys
import os
import time
import requests
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QListWidget,
    QRadioButton, QButtonGroup, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMutex, QMutexLocker
from urllib.parse import urlparse

KNOWN_NAMES = []

def clean_folder_name(name):
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')

def clean_filename(name):
     return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-', '.')).strip().replace(' ', '_')

def extract_folder_name_from_title(title, unwanted_keywords):
    title_lower = title.lower()
    tokens = title_lower.split()
    for token in tokens:
        clean_token = clean_folder_name(token)
        if clean_token and clean_token not in unwanted_keywords:
            return clean_token
    return 'Uncategorized'

def match_folders_from_title(title, known_names, unwanted_keywords):
    title_lower = title.lower()
    folders = []
    for name in known_names:
        cleaned_name = clean_folder_name(name.lower())
        if not cleaned_name:
             continue

        pattern = re.compile(r'\b' + re.escape(cleaned_name) + r'\b')

        if pattern.search(title_lower):
            folders.append(cleaned_name)

    folders = [f for f in folders if f not in unwanted_keywords]
    return folders

def is_image(filename):
    return filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and not filename.lower().endswith('.gif')

def is_video(filename):
    return filename.lower().endswith(('.mp4', '.mov', '.mkv', '.webm', '.gif'))

def is_zip(filename):
    return filename.lower().endswith('.zip')

def is_rar(filename):
    return filename.lower().endswith('.rar')


def is_post_url(url):
    return '/post/' in url and url.startswith("https://kemono.su/api/v1/")

def extract_post_info(api_url):
    parts = api_url.rstrip('/').split('/')
    try:
        post_index = parts.index('post')
        user_index = parts[post_index::-1].index('user')
        user_index_absolute = post_index - user_index
        if user_index_absolute > 0:
             if post_index - user_index_absolute >= 1:
                 service = parts[user_index_absolute - 1]
                 user_id = parts[user_index_absolute + 1]
                 post_id = parts[post_index + 1]
                 if service and user_id and post_id:
                     return service, user_id, post_id
    except ValueError:
        pass
    try:
        user_index = parts.index('user')
        if user_index > 0 and user_index + 1 < len(parts):
             service = parts[user_index - 1]
             user_id = parts[user_index + 1]
             return service, user_id, None
    except ValueError:
        pass

    return None, None, None

def fetch_single_post(service, user_id, post_id, logger):
    api_url = f"https://kemono.su/api/v1/{service}/user/{user_id}/post/{post_id}"
    logger(f"🔄 Fetching single post: {post_id}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        response.raise_for_status()
        return [response.json()]
    except requests.exceptions.RequestException as e:
        logger(f"❌ Error fetching specific post {post_id}: {e}")
        return []
    except Exception as e:
        logger(f"❌ Unexpected error fetching post {post_id}: {e}")
        return []

def fetch_posts_paginated(api_url, headers, offset, logger):
    paginated_url = f'{api_url}?o={offset}'
    try:
        response = requests.get(paginated_url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error fetching page at offset {offset}: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error fetching page at offset {offset}: {e}")

def download_from_api(api_url, logger=print):
    headers = {'User-Agent': 'Mozilla/5.0'}
    service, user_id, post_id = extract_post_info(api_url)

    if service and user_id and post_id:
        posts = fetch_single_post(service, user_id, post_id, logger)
        if posts:
            logger(f"📦 Found 1 post (specific URL).")
            yield posts
        else:
            logger(f"❌ Could not fetch specific post {post_id}.")
        return
    elif service and user_id:
        api_base_url = f"https://kemono.su/api/v1/{service}/user/{user_id}"
        offset = 0
        page = 1
        while True:
            logger(f"\n🔄 Fetching page {page} from {api_base_url} (offset={offset})...")
            try:
                posts_batch = fetch_posts_paginated(api_base_url, headers, offset, logger)
            except RuntimeError as e:
                logger(f"❌ {e}")
                break

            if not posts_batch:
                logger("✅ No more posts to fetch.")
                break

            logger(f"📦 Found {len(posts_batch)} posts on this page.")
            yield posts_batch

            offset += 50
            page += 1
    else:
         logger(f"❌ Invalid URL format: {api_url}. Please provide a user page or specific post URL.")

def process_posts(posts, download_root, known_names, filter_character,
                  unwanted_keywords, logger, filter_mode, skip_zip, skip_rar, use_subfolders, thread):
    total_downloaded_batch = 0
    total_skipped_batch = 0
    headers = {'User-Agent': 'Mozilla.5.0'}
    url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')

    for post in posts:
        if thread.isInterruptionRequested():
             logger("⚠️ Cancellation requested.")
             return total_downloaded_batch, total_skipped_batch, True

        title = post.get('title', 'untitled_post')
        post_id = post.get('id', 'unknown_id')
        post_file = post.get('file')
        attachments = post.get('attachments', [])
        post_content = post.get('content', '')

        if not isinstance(attachments, list):
            logger(f"⚠️ Unexpected attachment format for post {post_id}: {type(attachments)}. Skipping attachments list.")
            attachments = []

        valid_folder_paths = []
        if use_subfolders:
            folder_names_for_post = []
            if filter_character:
                clean_char = clean_folder_name(filter_character.lower())
                matched_folders = match_folders_from_title(title, known_names, unwanted_keywords)
                if clean_char in matched_folders:
                    folder_names_for_post = [clean_char]
                    logger(f"✨ Filter match for post '{title}': Using folder '{clean_char}'.")
                else:
                    continue
            else:
                matched_folders = match_folders_from_title(title, known_names, unwanted_keywords)
                if matched_folders:
                    logger(f"🎭 Found known character(s) in title '{title}': Using folder(s) {matched_folders}.")
                    folder_names_for_post = matched_folders
                else:
                    folder_name = extract_folder_name_from_title(title, unwanted_keywords)
                    logger(f"📝 No known characters found in title '{title}'. Using folder name derived from title: '{folder_name}'.")
                    folder_names_for_post = [folder_name]

            for folder in folder_names_for_post:
                try:
                    folder_path_full = os.path.join(download_root, folder)
                    os.makedirs(folder_path_full, exist_ok=True)
                    valid_folder_paths.append(folder_path_full)
                except OSError as e:
                    logger(f"❌ Could not create directory {folder_path_full}: {e}")
        else:
            valid_folder_paths = [download_root]
            try:
                os.makedirs(download_root, exist_ok=True)
            except OSError as e:
                 logger(f"❌ Could not access download directory {download_root}: {e}")
                 continue


        if not valid_folder_paths:
            logger(f"⚠️ No valid folders/root directory available for post {post_id}. Skipping file processing and link extraction.")
            continue

        if post_content:
            found_links = url_pattern.findall(post_content)
            if found_links:
                logger(f"🔗 Links found in Post: {title} (ID: {post_id})")
                for link in found_links:
                    logger(f"   - {link}")

        all_files_to_process = []
        if post_file and isinstance(post_file, dict) and post_file.get('path') and (post_file.get('name') or os.path.basename(urlparse(post_file.get('path')).path)):
             all_files_to_process.append(post_file)

        if attachments:
             all_files_to_process.extend(attachments)

        if not all_files_to_process:
             continue

        for file_info in all_files_to_process:
             if thread.isInterruptionRequested():
                 logger("⚠️ Cancellation requested.")
                 return total_downloaded_batch, total_skipped_batch, True

             if hasattr(thread, 'skip_current_file') and thread.skip_current_file:
                 logger(f"⏭️ Skipping file: {file_info.get('name', 'unknown_file')}")
                 total_skipped_batch += 1
                 thread.skip_current_file = False
                 continue

             if not isinstance(file_info, dict):
                 logger(f"⚠️ Skipping invalid file entry in post {post_id}: {file_info}")
                 continue

             file_url_path = file_info.get('path')
             filename = file_info.get('name')

             if not filename and file_url_path:
                 try:
                     filename = os.path.basename(urlparse(file_url_path).path)
                 except Exception:
                     filename = None

             if not file_url_path or not filename:
                 logger(f"⚠️ Missing path or name for a file in post '{title}'. Skipping.")
                 continue

             is_img = is_image(filename)
             is_vid = is_video(filename)
             is_zip_file = is_zip(filename)
             is_rar_file = is_rar(filename)

             if filter_mode == 'image' and not is_img:
                 total_skipped_batch += 1
                 continue
             elif filter_mode == 'video' and not is_vid:
                 total_skipped_batch += 1
                 continue
             elif skip_zip and is_zip_file:
                 logger(f"⏭️ Skipping zip file based on user preference: {filename}")
                 total_skipped_batch += 1
                 continue
             elif skip_rar and is_rar_file:
                 logger(f"⏭️ Skipping rar file based on user preference: {filename}")
                 total_skipped_batch += 1
                 continue


             full_url = f"https://kemono.su/data/{file_url_path.lstrip('/')}"

             for folder_path in valid_folder_paths:
                 if thread.isInterruptionRequested():
                     logger("⚠️ Cancellation requested.")
                     return total_downloaded_batch, total_skipped_batch, True

                 if hasattr(thread, 'skip_current_file') and thread.skip_current_file:
                     logger(f"⏭️ Skipping file download to {os.path.basename(folder_path)}: {filename}")
                     total_skipped_batch += 1
                     thread.skip_current_file = False
                     break

                 save_filename = f"{clean_filename(title)}_{clean_filename(filename)}"
                 if len(save_filename) > 200:
                     save_filename = f"{post_id}_{clean_filename(filename)}"

                 save_path = os.path.join(folder_path, save_filename)

                 if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                      total_skipped_batch += 1
                      continue
                 else:
                     try:
                         logger(f"⬇️ Downloading {save_filename} to {os.path.basename(folder_path)}...")
                         thread.current_download_path = save_path
                         thread.is_downloading_file = True

                         with requests.get(full_url, headers=headers, timeout=60, stream=True) as r:
                             r.raise_for_status()

                             with open(save_path, 'wb') as f:
                                 for chunk in r.iter_content(chunk_size=8192):
                                     if thread.isInterruptionRequested() or (hasattr(thread, 'skip_current_file') and thread.skip_current_file):
                                         logger("⚠️ Download interrupted or skipped.")
                                         if os.path.exists(save_path):
                                             try: os.remove(save_path)
                                             except OSError: pass
                                         thread.current_download_path = None
                                         thread.is_downloading_file = False
                                         thread.skip_current_file = False
                                         if thread.isInterruptionRequested():
                                            return total_downloaded_batch, total_skipped_batch + 1, True
                                         else:
                                             total_skipped_batch += 1
                                             break

                                     if chunk:
                                         f.write(chunk)

                             if not (hasattr(thread, 'skip_current_file') and thread.skip_current_file):
                                total_downloaded_batch += 1
                                logger(f"✅ Saved in {os.path.basename(folder_path)}: {save_filename}")
                                time.sleep(0.5)

                         thread.current_download_path = None
                         thread.is_downloading_file = False
                         thread.skip_current_file = False

                         if not (hasattr(thread, 'skip_current_file') and thread.skip_current_file):
                            break

                     except requests.exceptions.RequestException as e:
                         logger(f"❌ Failed download {save_filename} to {os.path.basename(folder_path)}: {e}")
                         if os.path.exists(save_path):
                              try: os.remove(save_path)
                              except OSError: pass
                         thread.current_download_path = None
                         thread.is_downloading_file = False
                         thread.skip_current_file = False
                     except IOError as e:
                          logger(f"❌ Failed save {save_filename} to {os.path.basename(folder_path)}: {e}")
                          thread.current_download_path = None
                          thread.is_downloading_file = False
                          self.skip_current_file = False
                     except Exception as e:
                          logger(f"❌ Unexpected error for {save_filename} in {os.path.basename(folder_path)}: {e}")
                          thread.current_download_path = None
                          thread.is_downloading_file = False
                          thread.skip_current_file = False

    return total_downloaded_batch, total_skipped_batch, False

class DownloadThread(QThread):
    progress_signal = pyqtSignal(str)
    add_character_prompt_signal = pyqtSignal(str)
    add_character_result_signal = pyqtSignal(bool)
    file_download_status_signal = pyqtSignal(bool)

    def __init__(self, api_url, output_dir, known_names_copy,
                 filter_character=None, filter_mode='all', skip_zip=True, skip_rar=True, use_subfolders=True):
        super().__init__()
        self.api_url = api_url
        self.output_dir = output_dir
        self.known_names = list(known_names_copy)
        self.filter_character = filter_character
        self.filter_mode = filter_mode
        self.skip_zip = skip_zip
        self.skip_rar = skip_rar
        self.use_subfolders = use_subfolders
        self.mutex = QMutex()
        self._add_character_response = None
        self.skip_current_file = False
        self.current_download_path = None
        self.is_downloading_file = False

    def run(self):
        unwanted_keywords = {'spicy', 'hd', 'nsfw'}
        grand_total_downloaded = 0
        grand_total_skipped = 0
        cancelled_during_processing = False

        if self.filter_character and self.use_subfolders:
            clean_char = clean_folder_name(self.filter_character.lower())
            if clean_char not in (n.lower() for n in self.known_names):
                with QMutexLocker(self.mutex):
                    self._add_character_response = None

                self.add_character_prompt_signal.emit(clean_char)

                while self._add_character_response is None:
                    if self.isInterruptionRequested():
                        self.progress_signal.emit("⚠️ Download cancelled while waiting for user input.")
                        return
                    self.msleep(100)

                if self._add_character_response:
                    self.known_names.append(clean_char)
                else:
                    self.progress_signal.emit(f"❌ Character '{clean_char}' not added by user. Aborting task.")
                    return
        elif self.filter_character and not self.use_subfolders:
             clean_char = clean_folder_name(self.filter_character.lower())
             if clean_char not in (n.lower() for n in self.known_names):
                  self.progress_signal.emit(f"ℹ️ Character filter '{clean_char}' will be applied, but files will go to the single output folder as 'Download to Separate Folders' is unchecked.")


        try:
            post_generator = download_from_api(self.api_url, logger=self.update_progress)

            for posts_batch in post_generator:
                if self.isInterruptionRequested():
                    self.progress_signal.emit("⚠️ Download cancelled.")
                    cancelled_during_processing = True
                    break

                self.file_download_status_signal.emit(True)

                downloaded, skipped, cancelled_in_batch = process_posts(
                    posts=posts_batch,
                    download_root=self.output_dir,
                    known_names=self.known_names,
                    filter_character=self.filter_character,
                    unwanted_keywords=unwanted_keywords,
                    logger=self.update_progress,
                    filter_mode=self.filter_mode,
                    skip_zip=self.skip_zip,
                    skip_rar=self.skip_rar,
                    use_subfolders=self.use_subfolders,
                    thread=self
                )
                grand_total_downloaded += downloaded
                grand_total_skipped += skipped

                self.file_download_status_signal.emit(False)


                if cancelled_in_batch:
                    cancelled_during_processing = True
                    break

            if not cancelled_during_processing:
                 self.progress_signal.emit(f"\n🎉 Finished! Total downloaded: {grand_total_downloaded}, Skipped: {grand_total_skipped}")
            else:
                 self.progress_signal.emit(f"\n⚠️ Download cancelled. Total downloaded: {grand_total_downloaded}, Skipped: {grand_total_skipped}")


        except Exception as e:
            self.progress_signal.emit(f"\n❌ An unexpected error occurred in download thread: {e}")
            self.file_download_status_signal.emit(False)


    def update_progress(self, message):
        self.progress_signal.emit(message)

    def receive_add_character_result(self, result):
        with QMutexLocker(self.mutex):
            self._add_character_response = result

    def cancel(self):
        self.requestInterruption()

    def skip_file(self):
        if self.isRunning() and self.is_downloading_file:
             self.skip_current_file = True
             self.progress_signal.emit("⏭️ Skip requested for the current file.")


class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.config_file = "kemono_downloader_config.txt"
        self.load_known_names()
        self.setWindowTitle("Kemono Downloader")
        self.setGeometry(200, 200, 900, 580)
        self.setStyleSheet(self.get_dark_theme())
        self.init_ui()
        self.download_thread = None

    def load_known_names(self):
        global KNOWN_NAMES
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    KNOWN_NAMES = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"Error loading config '{self.config_file}': {e}")
                QMessageBox.warning(self, "Config Load Error", f"Could not load character list from {self.config_file}:\n{e}")
                KNOWN_NAMES = []
        else:
            print(f"Config file '{self.config_file}' not found. Starting with empty character list.")
            KNOWN_NAMES = []

    def save_known_names(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                for name in sorted(KNOWN_NAMES):
                    f.write(name + '\n')
        except Exception as e:
            QMessageBox.warning(self, "Config Save Error", f"Could not save character list to {self.config_file}:\n{e}")

    def closeEvent(self, event):
        self.save_known_names()
        if self.download_thread and self.download_thread.isRunning():
             reply = QMessageBox.question(self, "Confirm Exit",
                                          "A download is in progress. Are you sure you want to exit? This will cancel the download.",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
             if reply == QMessageBox.Yes:
                 self.download_thread.cancel()
                 self.download_thread.wait(2000)
                 event.accept()
             else:
                 event.ignore()
        else:
            event.accept()

    def init_ui(self):
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()

        self.link_label = QLabel("🔗 Kemono Creator Page or Post URL:")
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("e.g., https://kemono.su/patreon/user/12345 or .../post/67890")
        left_layout.addWidget(self.link_label)
        left_layout.addWidget(self.link_input)

        self.dir_label = QLabel("📁 Download Location:")
        self.dir_input = QLineEdit()
        self.dir_button = QPushButton("Browse")
        self.dir_button.clicked.connect(self.browse_directory)
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.dir_button)
        left_layout.addWidget(self.dir_label)
        left_layout.addLayout(dir_layout)

        self.character_label = QLabel("🎯 Filter by Character (optional):")
        self.character_input = QLineEdit()
        self.character_input.setPlaceholderText("Enter character name exactly as in list (case insensitive match)")
        left_layout.addWidget(self.character_label)
        left_layout.addWidget(self.character_input)

        self.radio_group = QButtonGroup(self)
        self.radio_all = QRadioButton("All Files")
        self.radio_images = QRadioButton("Images Only (no GIFs)")
        self.radio_videos = QRadioButton("Videos Only (includes GIFs)")
        self.radio_all.setChecked(True)
        self.radio_group.addButton(self.radio_all)
        self.radio_group.addButton(self.radio_images)
        self.radio_group.addButton(self.radio_videos)
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio_all)
        radio_layout.addWidget(self.radio_images)
        radio_layout.addWidget(self.radio_videos)
        left_layout.addLayout(radio_layout)

        # Create a new horizontal layout for the checkboxes
        checkbox_layout = QHBoxLayout()
        self.skip_zip_checkbox = QCheckBox("Skip Zip Files")
        self.skip_zip_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.skip_zip_checkbox)

        self.skip_rar_checkbox = QCheckBox("Skip RAR Files")
        self.skip_rar_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.skip_rar_checkbox)

        self.use_subfolders_checkbox = QCheckBox("Download to Separate Folders")
        self.use_subfolders_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.use_subfolders_checkbox)

        # Add the horizontal checkbox layout to the main left layout
        left_layout.addLayout(checkbox_layout)


        btn_layout = QHBoxLayout()
        self.download_btn = QPushButton("⬇️ Start Download")
        self.download_btn.clicked.connect(self.start_download)
        self.cancel_btn = QPushButton("❌ Cancel Download")
        self.cancel_btn.clicked.connect(self.cancel_download)
        self.cancel_btn.setEnabled(False)

        self.skip_file_btn = QPushButton("⏭️ Skip Current File")
        self.skip_file_btn.clicked.connect(self.skip_current_file)
        self.skip_file_btn.setEnabled(False)

        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.skip_file_btn)

        left_layout.addLayout(btn_layout)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        left_layout.addWidget(QLabel("📜 Progress Log:"))
        left_layout.addWidget(self.log_output)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("🎭 Known Characters:"))
        self.character_list = QListWidget()
        self.character_list.addItems(sorted(KNOWN_NAMES))
        right_layout.addWidget(self.character_list)

        self.new_char_input = QLineEdit()
        self.new_char_input.setPlaceholderText("Add new character name")
        self.add_char_button = QPushButton("➕ Add")
        self.delete_char_button = QPushButton("🗑️ Delete Selected")
        self.add_char_button.clicked.connect(self.add_new_character)
        self.new_char_input.returnPressed.connect(self.add_char_button.click)
        self.delete_char_button.clicked.connect(self.delete_selected_character)
        char_button_layout = QHBoxLayout()
        char_button_layout.addWidget(self.new_char_input, 2)
        char_button_layout.addWidget(self.add_char_button, 1)
        char_button_layout.addWidget(self.delete_char_button, 1)
        right_layout.addLayout(char_button_layout)

        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 2)
        self.setLayout(main_layout)

    def get_dark_theme(self):
        return """
        QWidget {
            background-color: #2b2b2b;
            color: #f0f0f0;
            font-family: Segoe UI, Arial, sans-serif;
            font-size: 10pt;
        }
        QLineEdit, QTextEdit, QListWidget {
            background-color: #3c3f41;
            border: 1px solid #555;
            padding: 5px;
            color: #f0f0f0;
            border-radius: 3px;
        }
        QPushButton {
            background-color: #555;
            color: #f0f0f0;
            border: 1px solid #666;
            padding: 6px 12px;
            border-radius: 3px;
            min-height: 20px;
        }
        QPushButton:hover {
            background-color: #666;
            border: 1px solid #777;
        }
        QPushButton:pressed {
            background-color: #444;
        }
        QPushButton:disabled {
            background-color: #444;
            color: #888;
            border-color: #555;
        }
        QLabel {
            font-weight: bold;
            padding-top: 4px;
        }
        QRadioButton {
            spacing: 5px;
            color: #f0f0f0;
        }
        QRadioButton::indicator {
            width: 13px;
            height: 13px;
        }
        QListWidget {
             alternate-background-color: #333;
             border: 1px solid #555;
        }
        QListWidget::item:selected {
            background-color: #0078d7;
            color: #ffffff;
        }
        QCheckBox {
             color: #f0f0f0;
             spacing: 5px;
        }
         QCheckBox::indicator {
             width: 13px;
             height: 13px;
         }
        """

    def browse_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.dir_input.setText(folder)

    def log(self, message):
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def get_filter_mode(self):
        if self.radio_images.isChecked():
            return 'image'
        elif self.radio_videos.isChecked():
            return 'video'
        return 'all'

    def add_new_character(self):
        global KNOWN_NAMES
        name = self.new_char_input.text().strip()
        if name:
            if name.lower() not in (n.lower() for n in KNOWN_NAMES):
                KNOWN_NAMES.append(name)
                self.character_list.clear()
                self.character_list.addItems(sorted(KNOWN_NAMES))
                self.log(f"✅ Added '{name}' to known characters.")
                self.new_char_input.clear()
                self.save_known_names()
            else:
                 QMessageBox.warning(self, "Duplicate", f"'{name}' is already in the list.")
        else:
             QMessageBox.warning(self, "Input Error", "Character name cannot be empty.")

    def delete_selected_character(self):
        global KNOWN_NAMES
        selected_items = self.character_list.selectedItems()
        if not selected_items:
             QMessageBox.warning(self, "Selection Error", "Please select a character to delete.")
             return

        confirm = QMessageBox.question(self, "Confirm Deletion",
                                       f"Are you sure you want to delete {len(selected_items)} selected character(s)?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirm == QMessageBox.Yes:
            names_to_remove = [item.text() for item in selected_items]
            original_count = len(KNOWN_NAMES)
            KNOWN_NAMES = [n for n in KNOWN_NAMES if n.lower() not in (rem.lower() for rem in names_to_remove)]
            removed_count = original_count - len(KNOWN_NAMES)
            if removed_count > 0:
                 self.log(f"🗑️ Removed {removed_count} character(s).")
                 self.character_list.clear()
                 self.character_list.addItems(sorted(KNOWN_NAMES))
                 self.save_known_names()
            else:
                 self.log("🤷 No matching characters found to remove.")

    def start_download(self):
        if self.download_thread and self.download_thread.isRunning():
            self.log("⚠️ Download already in progress.")
            return

        api_url = self.link_input.text().strip()
        output_dir = self.dir_input.text().strip()
        filter_character = self.character_input.text().strip()
        filter_mode = self.get_filter_mode()
        skip_zip = self.skip_zip_checkbox.isChecked()
        skip_rar = self.skip_rar_checkbox.isChecked()
        use_subfolders = self.use_subfolders_checkbox.isChecked()


        if not api_url:
            QMessageBox.warning(self, "Input Error", "Please enter a Kemono creator page or post URL.")
            return

        if not output_dir:
            QMessageBox.warning(self, "Input Error", "Please select a download location.")
            return

        if filter_character and use_subfolders and clean_folder_name(filter_character.lower()) not in (n.lower() for n in KNOWN_NAMES):
            self.log(f"ℹ️ Character '{filter_character}' not found in known list. Will prompt to add (only if using separate folders).")
        elif filter_character and not use_subfolders:
             self.log(f"ℹ️ Character filter '{filter_character}' will be applied, but files will go to the single output folder as 'Download to Separate Folders' is unchecked.")


        self.log_output.clear()
        self.log(f"🚀 Starting download from {api_url}...")
        self.log(f"📁 Saving to: {output_dir}")
        if filter_character:
             self.log(f"🎯 Filtering by Character: {filter_character}")
        self.log(f"📄 File Type Filter: {filter_mode}")
        self.log(f"🤐 Skip Zip Files: {'Yes' if skip_zip else 'No'}")
        self.log(f"📦 Skip RAR Files: {'Yes' if skip_rar else 'No'}")
        self.log(f"📂 Download Location Mode: {'Separate Folders' if use_subfolders else 'Single Folder'}")


        self.download_thread = DownloadThread(
            api_url=api_url,
            output_dir=output_dir,
            known_names_copy=list(KNOWN_NAMES),
            filter_character=filter_character if filter_character else None,
            filter_mode=filter_mode,
            skip_zip=skip_zip,
            skip_rar=skip_rar,
            use_subfolders=use_subfolders
        )

        self.download_thread.progress_signal.connect(self.log)
        self.download_thread.add_character_prompt_signal.connect(self.prompt_add_character)
        self.download_thread.add_character_result_signal.connect(self.download_thread.receive_add_character_result)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.file_download_status_signal.connect(self.update_skip_button_state)


        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)

        self.link_input.setEnabled(False)
        self.dir_input.setEnabled(False)
        self.dir_button.setEnabled(False)
        self.character_input.setEnabled(False)
        self.radio_all.setEnabled(False)
        self.radio_images.setEnabled(False)
        self.radio_videos.setEnabled(False)
        self.skip_zip_checkbox.setEnabled(False)
        self.skip_rar_checkbox.setEnabled(False)
        self.use_subfolders_checkbox.setEnabled(False)
        self.character_list.setEnabled(False)
        self.new_char_input.setEnabled(False)
        self.add_char_button.setEnabled(False)
        self.delete_char_button.setEnabled(False)

        self.download_thread.start()

    def cancel_download(self):
        if self.download_thread and self.download_thread.isRunning():
            self.log("⚠️ Requesting cancellation...")
            self.download_thread.cancel()

    def skip_current_file(self):
         if self.download_thread and self.download_thread.isRunning():
              self.download_thread.skip_file()

    def update_skip_button_state(self, is_downloading):
         self.skip_file_btn.setEnabled(is_downloading)


    def download_finished(self):
        self.log("Download thread finished.")
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.skip_file_btn.setEnabled(False)

        self.link_input.setEnabled(True)
        self.dir_input.setEnabled(True)
        self.dir_button.setEnabled(True)
        self.character_input.setEnabled(True)
        self.radio_all.setEnabled(True)
        self.radio_images.setEnabled(True)
        self.radio_videos.setEnabled(True)
        self.skip_zip_checkbox.setEnabled(True)
        self.skip_rar_checkbox.setEnabled(True)
        self.use_subfolders_checkbox.setEnabled(True)
        self.character_list.setEnabled(True)
        self.new_char_input.setEnabled(True)
        self.add_char_button.setEnabled(True)
        self.delete_char_button.setEnabled(True)

        self.download_thread = None

    def prompt_add_character(self, character_name):
         if self.download_thread and self.download_thread.use_subfolders:
             reply = QMessageBox.question(self, "Add Character?",
                                          f"Character '{character_name}' was found in a post title but is not in your known list.\n\nAdd '{character_name}' to your known characters list and download to its folder?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

             result = (reply == QMessageBox.Yes)
             self.download_thread.add_character_result_signal.emit(result)

             if result:
                 global KNOWN_NAMES
                 if character_name.lower() not in (n.lower() for n in KNOWN_NAMES):
                      KNOWN_NAMES.append(character_name)
                      self.character_list.clear()
                      self.character_list.addItems(sorted(KNOWN_NAMES))
                      self.log(f"✅ Added '{character_name}' to known characters (via prompt).")
                      self.save_known_names()
         else:
              self.download_thread.add_character_result_signal.emit(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    downloader = DownloaderApp()
    downloader.show()
    sys.exit(app.exec_())