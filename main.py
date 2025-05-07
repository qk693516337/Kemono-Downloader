import sys
import os
import time
import requests
import re
import threading
import queue
import hashlib
from concurrent.futures import ThreadPoolExecutor, Future, CancelledError

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QListWidget,
    QRadioButton, QButtonGroup, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMutex, QMutexLocker, QObject
from urllib.parse import urlparse

try:
    from PIL import Image
except ImportError:
    Image = None # Will be handled in downloader_utils

from io import BytesIO

# Import from the new utils/backend file
from downloader_utils import (
    KNOWN_NAMES,
    clean_folder_name,
    extract_post_info,
    download_from_api,
    PostProcessorSignals,
    PostProcessorWorker,
    DownloadThread as BackendDownloadThread # Rename to avoid conflict if any
)


class DownloaderApp(QWidget):
    character_prompt_response_signal = pyqtSignal(bool)
    log_signal = pyqtSignal(str)
    add_character_prompt_signal = pyqtSignal(str)
    file_download_status_signal = pyqtSignal(bool)
    overall_progress_signal = pyqtSignal(int, int)
    finished_signal = pyqtSignal(int, int, bool)


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
        self.worker_signals = PostProcessorSignals()
        self.prompt_mutex = QMutex()
        self._add_character_response = None
        self.downloaded_files = set()
        self.downloaded_files_lock = threading.Lock()
        self.downloaded_file_hashes = set()
        self.downloaded_file_hashes_lock = threading.Lock()
        self.load_known_names_from_util() # Changed to reflect it's from utils
        self.setWindowTitle("Kemono Downloader v2.3 (Content Dedupe & Skip)")
        self.setGeometry(150, 150, 1050, 820)
        self.setStyleSheet(self.get_dark_theme())
        self.init_ui()
        self._connect_signals()
        self.log_signal.emit("ℹ️ Local API server functionality has been removed.")


    def _connect_signals(self):
        self.worker_signals.progress_signal.connect(self.log)
        self.worker_signals.file_download_status_signal.connect(self.update_skip_button_state)
        self.log_signal.connect(self.log)
        self.add_character_prompt_signal.connect(self.prompt_add_character)
        self.character_prompt_response_signal.connect(self.receive_add_character_result)
        self.overall_progress_signal.connect(self.update_progress_display)
        self.finished_signal.connect(self.download_finished)
        self.character_search_input.textChanged.connect(self.filter_character_list)

    def load_known_names_from_util(self):
        # KNOWN_NAMES is now managed in downloader_utils, but GUI needs to populate its list
        # and this method also handles initial log messages.
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
                loaded_names = []
        else:
            log_msg = f"ℹ️ Config file '{self.config_file}' not found. Starting empty."
            loaded_names = []

        # Update the global KNOWN_NAMES in downloader_utils
        # This requires downloader_utils.KNOWN_NAMES to be mutable (it's a list)
        # Or pass the list back if it were a function in utils returning the list.
        # For simplicity with global-like config, directly modify.
        # Ensure downloader_utils.py defines KNOWN_NAMES = [] at the top.
        import downloader_utils
        downloader_utils.KNOWN_NAMES[:] = loaded_names # Modify in place

        if hasattr(self, 'log_output'):
             self.log_signal.emit(log_msg)
        else:
             print(log_msg)
        # Populate the GUI list if it exists
        if hasattr(self, 'character_list'):
            self.character_list.clear()
            self.character_list.addItems(downloader_utils.KNOWN_NAMES)


    def save_known_names(self):
        # KNOWN_NAMES is from downloader_utils
        import downloader_utils
        try:
            unique_sorted_names = sorted(list(set(filter(None, downloader_utils.KNOWN_NAMES))))
            with open(self.config_file, 'w', encoding='utf-8') as f:
                for name in unique_sorted_names:
                    f.write(name + '\n')
            downloader_utils.KNOWN_NAMES[:] = unique_sorted_names # Update in place
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
        self.save_known_names()
        should_exit = True
        is_downloading = (self.download_thread and self.download_thread.isRunning()) or (self.thread_pool is not None)

        if is_downloading:
             reply = QMessageBox.question(self, "Confirm Exit",
                                          "Download in progress. Are you sure you want to exit and cancel?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
             if reply == QMessageBox.Yes:
                 self.log_signal.emit("⚠️ Cancelling active download due to application exit...")
                 self.cancel_download()
             else:
                 should_exit = False
                 self.log_signal.emit("ℹ️ Application exit cancelled.")
                 event.ignore()
                 return

        if should_exit:
            self.log_signal.emit("ℹ️ Application closing.")
            self.log_signal.emit("👋 Exiting application.")
            event.accept()

    def init_ui(self):
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
        dir_layout.addWidget(self.dir_input, 1)
        dir_layout.addWidget(self.dir_button)
        left_layout.addLayout(dir_layout)
        self.custom_folder_widget = QWidget()
        custom_folder_layout = QVBoxLayout(self.custom_folder_widget)
        custom_folder_layout.setContentsMargins(0, 5, 0, 0)
        self.custom_folder_label = QLabel("🗄️ Custom Folder Name (Single Post Only):")
        self.custom_folder_input = QLineEdit()
        self.custom_folder_input.setPlaceholderText("Optional: Save this post to specific folder")
        custom_folder_layout.addWidget(self.custom_folder_label)
        custom_folder_layout.addWidget(self.custom_folder_input)
        self.custom_folder_widget.setVisible(False)
        left_layout.addWidget(self.custom_folder_widget)
        self.character_filter_widget = QWidget()
        character_filter_layout = QVBoxLayout(self.character_filter_widget)
        character_filter_layout.setContentsMargins(0, 5, 0, 0)
        self.character_label = QLabel("🎯 Filter by Show/Character Name:")
        self.character_input = QLineEdit()
        self.character_input.setPlaceholderText("Only download posts matching this known name in title")
        character_filter_layout.addWidget(self.character_label)
        character_filter_layout.addWidget(self.character_input)
        self.character_filter_widget.setVisible(True)
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

        self.download_thumbnails_checkbox = QCheckBox("Download Thumbnails Only")
        self.download_thumbnails_checkbox.setChecked(False)
        self.download_thumbnails_checkbox.setToolTip("Thumbnail download functionality is currently limited without the API.")
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
        self.use_multithreading_checkbox = QCheckBox(f"Use Multithreading ({4} Threads)")
        self.use_multithreading_checkbox.setChecked(True)
        self.use_multithreading_checkbox.setToolTip("Speeds up downloads for full creator pages.\nSingle post URLs always use one thread.")
        options_layout_4.addWidget(self.use_multithreading_checkbox)
        options_layout_4.addStretch(1)
        left_layout.addLayout(options_layout_4)
        btn_layout = QHBoxLayout()
        self.download_btn = QPushButton("⬇️ Start Download")
        self.download_btn.setStyleSheet("padding: 8px 15px; font-weight: bold;")
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
        left_layout.addSpacing(10)
        known_chars_label_layout = QHBoxLayout()
        self.known_chars_label = QLabel("🎭 Known Shows/Characters (for Folder Names):")
        self.character_search_input = QLineEdit()
        self.character_search_input.setPlaceholderText("Search characters...")
        known_chars_label_layout.addWidget(self.known_chars_label, 1)
        known_chars_label_layout.addWidget(self.character_search_input)

        left_layout.addLayout(known_chars_label_layout)

        self.character_list = QListWidget()
        # KNOWN_NAMES will be populated by load_known_names_from_util
        self.character_list.setSelectionMode(QListWidget.ExtendedSelection)
        left_layout.addWidget(self.character_list, 1)
        char_manage_layout = QHBoxLayout()
        self.new_char_input = QLineEdit()
        self.new_char_input.setPlaceholderText("Add new show/character name")
        self.add_char_button = QPushButton("➕ Add")
        self.delete_char_button = QPushButton("🗑️ Delete Selected")
        self.add_char_button.clicked.connect(self.add_new_character)
        self.new_char_input.returnPressed.connect(self.add_char_button.click)
        self.delete_char_button.clicked.connect(self.delete_selected_character)
        char_manage_layout.addWidget(self.new_char_input, 2)
        char_manage_layout.addWidget(self.add_char_button, 1)
        char_manage_layout.addWidget(self.delete_char_button, 1)
        left_layout.addLayout(char_manage_layout)
        right_layout.addWidget(QLabel("📜 Progress Log:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumWidth(450)
        self.log_output.setLineWrapMode(QTextEdit.WidgetWidth)
        right_layout.addWidget(self.log_output, 1)
        self.progress_label = QLabel("Progress: Idle")
        self.progress_label.setStyleSheet("padding-top: 5px; font-style: italic;")
        right_layout.addWidget(self.progress_label)
        main_layout.addLayout(left_layout, 5)
        main_layout.addLayout(right_layout, 4)
        self.setLayout(main_layout)
        self.update_ui_for_subfolders(self.use_subfolders_checkbox.isChecked())
        self.update_custom_folder_visibility()


    def get_dark_theme(self):
        return """
        QWidget {
            background-color: #2E2E2E;
            color: #E0E0E0;
            font-family: Segoe UI, Arial, sans-serif;
            font-size: 10pt;
        }
        QLineEdit, QTextEdit, QListWidget {
            background-color: #3C3F41;
            border: 1px solid #5A5A5A;
            padding: 5px;
            color: #F0F0F0;
            border-radius: 4px;
        }
        QTextEdit {
             font-family: Consolas, Courier New, monospace;
             font-size: 9.5pt;
        }
        QPushButton {
            background-color: #555;
            color: #F0F0F0;
            border: 1px solid #6A6A6A;
            padding: 6px 12px;
            border-radius: 4px;
            min-height: 22px;
        }
        QPushButton:hover {
            background-color: #656565;
            border: 1px solid #7A7A7A;
        }
        QPushButton:pressed {
            background-color: #4A4A4A;
        }
        QPushButton:disabled {
            background-color: #404040;
            color: #888;
            border-color: #555;
        }
        QLabel {
            font-weight: bold;
            padding-top: 4px;
            padding-bottom: 2px;
            color: #C0C0C0;
        }
        QRadioButton, QCheckBox {
            spacing: 5px;
            color: #E0E0E0;
            padding-top: 4px;
            padding-bottom: 4px;
        }
        QRadioButton::indicator, QCheckBox::indicator {
            width: 14px;
            height: 14px;
        }
        QListWidget {
             alternate-background-color: #353535;
             border: 1px solid #5A5A5A;
        }
        QListWidget::item:selected {
            background-color: #007ACC;
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
        try:
             safe_message = str(message).replace('\x00', '[NULL]')
             self.log_output.append(safe_message)
             scrollbar = self.log_output.verticalScrollBar()
             if scrollbar.value() >= scrollbar.maximum() - 30:
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
        import downloader_utils # Ensure we are using the list from utils
        name_to_add = self.new_char_input.text().strip()
        if not name_to_add:
             QMessageBox.warning(self, "Input Error", "Name cannot be empty.")
             return
        name_lower = name_to_add.lower()
        is_duplicate = any(existing.lower() == name_lower for existing in downloader_utils.KNOWN_NAMES)

        if not is_duplicate:
            downloader_utils.KNOWN_NAMES.append(name_to_add)
            downloader_utils.KNOWN_NAMES.sort(key=str.lower)
            self.character_list.clear()
            self.character_list.addItems(downloader_utils.KNOWN_NAMES)
            self.filter_character_list(self.character_search_input.text())
            self.log_signal.emit(f"✅ Added '{name_to_add}' to known names list.")
            self.new_char_input.clear()
            self.save_known_names()
        else:
             QMessageBox.warning(self, "Duplicate Name", f"The name '{name_to_add}' (or similar) already exists in the list.")


    def delete_selected_character(self):
        import downloader_utils
        selected_items = self.character_list.selectedItems()
        if not selected_items:
             QMessageBox.warning(self, "Selection Error", "Please select one or more names to delete.")
             return

        names_to_remove = {item.text() for item in selected_items}
        confirm = QMessageBox.question(self, "Confirm Deletion",
                                       f"Are you sure you want to delete {len(names_to_remove)} selected name(s)?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirm == QMessageBox.Yes:
            original_count = len(downloader_utils.KNOWN_NAMES)
            downloader_utils.KNOWN_NAMES = [n for n in downloader_utils.KNOWN_NAMES if n not in names_to_remove]
            removed_count = original_count - len(downloader_utils.KNOWN_NAMES)

            if removed_count > 0:
                 self.log_signal.emit(f"🗑️ Removed {removed_count} name(s) from the list.")
                 self.character_list.clear()
                 downloader_utils.KNOWN_NAMES.sort(key=str.lower)
                 self.character_list.addItems(downloader_utils.KNOWN_NAMES)
                 self.filter_character_list(self.character_search_input.text())
                 self.save_known_names()
            else:
                 self.log_signal.emit("ℹ️ No names were removed (selection might have changed?).")


    def update_custom_folder_visibility(self, url_text=None):
        if url_text is None:
            url_text = self.link_input.text()

        _, _, post_id = extract_post_info(url_text.strip()) # from downloader_utils
        should_show = bool(post_id) and self.use_subfolders_checkbox.isChecked()

        self.custom_folder_widget.setVisible(should_show)
        if not should_show:
             self.custom_folder_input.clear()


    def update_ui_for_subfolders(self, checked):
         self.character_filter_widget.setVisible(checked)
         self.update_custom_folder_visibility()
         if not checked:
              self.character_input.clear()

    def filter_character_list(self, search_text):
        search_text = search_text.lower()
        for i in range(self.character_list.count()):
            item = self.character_list.item(i)
            if search_text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)


    def update_progress_display(self, total_posts, processed_posts):
        if total_posts > 0:
            try:
                 percent = (processed_posts / total_posts) * 100
                 self.progress_label.setText(f"Progress: {processed_posts} / {total_posts} posts ({percent:.1f}%)")
            except ZeroDivisionError:
                 self.progress_label.setText(f"Progress: {processed_posts} / {total_posts} posts")
        elif processed_posts > 0:
             self.progress_label.setText(f"Progress: Processing post {processed_posts}...")
        else:
            self.progress_label.setText("Progress: Starting...")

    def start_download(self):
        import downloader_utils # For KNOWN_NAMES
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
        num_threads = 4
        raw_skip_words = self.skip_words_input.text().strip()
        skip_words_list = []
        if raw_skip_words:
            skip_words_list = [word.strip() for word in raw_skip_words.split(',') if word.strip()]
        service, user_id, post_id_from_url = extract_post_info(api_url) # from downloader_utils

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
             else:
                 return
        if compress_images and Image is None: # Image imported in this file
             QMessageBox.warning(self, "Dependency Missing", "Image compression requires the Pillow library, but it's not installed.\nPlease run: pip install Pillow\n\nCompression will be disabled for this session.")
             self.log_signal.emit("❌ Cannot compress images: Pillow library not found.")
             compress_images = False
        filter_character = None
        if use_subfolders and self.character_filter_widget.isVisible():
            filter_character = self.character_input.text().strip() or None

        custom_folder_name = None
        if use_subfolders and post_id_from_url and self.custom_folder_widget.isVisible():
            raw_custom_name = self.custom_folder_input.text().strip()
            if raw_custom_name:
                 cleaned_custom = clean_folder_name(raw_custom_name) # from downloader_utils
                 if cleaned_custom:
                     custom_folder_name = cleaned_custom
                 else:
                     QMessageBox.warning(self, "Input Warning", f"Custom folder name '{raw_custom_name}' is invalid and will be ignored.")
                     self.log_signal.emit(f"⚠️ Invalid custom folder name ignored: {raw_custom_name}")
        if use_subfolders and filter_character and not post_id_from_url:
            clean_char_filter = clean_folder_name(filter_character.lower()) # from downloader_utils
            known_names_lower = {name.lower() for name in downloader_utils.KNOWN_NAMES}

            if not clean_char_filter:
                self.log_signal.emit(f"❌ Filter name '{filter_character}' is invalid. Aborting.")
                QMessageBox.critical(self, "Filter Error", "The provided filter name is invalid (contains only spaces or special characters).")
                return
            elif filter_character.lower() not in known_names_lower:
                 reply = QMessageBox.question(self, "Add Filter Name?",
                                          f"The filter name '{filter_character}' is not in your known names list.\n\nAdd it now and continue?",
                                          QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)

                 if reply == QMessageBox.Yes:
                     self.new_char_input.setText(filter_character)
                     self.add_new_character()
                     if filter_character.lower() not in {name.lower() for name in downloader_utils.KNOWN_NAMES}:
                          self.log_signal.emit(f"⚠️ Failed to add '{filter_character}' automatically. Please add manually if needed.")
                     else:
                          self.log_signal.emit(f"✅ Added filter '{filter_character}' to list.")
                 elif reply == QMessageBox.No:
                     self.log_signal.emit(f"ℹ️ Proceeding without adding '{filter_character}'. Posts matching it might not be saved to a specific folder unless name is derived.")
                 else:
                     self.log_signal.emit("❌ Download cancelled by user during filter check.")
                     return
        self.log_output.clear()
        self.cancellation_event.clear()
        self.active_futures = []
        self.total_posts_to_process = 0
        self.processed_posts_count = 0
        self.download_counter = 0
        self.skip_counter = 0
        with self.downloaded_files_lock:
             self.downloaded_files.clear()
        with self.downloaded_file_hashes_lock:
             self.downloaded_file_hashes.clear()

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
                'known_names_copy': list(downloader_utils.KNOWN_NAMES), # From downloader_utils
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
                'downloaded_file_hashes': self.downloaded_file_hashes,
                'downloaded_file_hashes_lock': self.downloaded_file_hashes_lock,
                'skip_words_list': skip_words_list,
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
             self.download_finished(0, 0, False)


    def start_single_threaded_download(self, **kwargs):
        try:
            self.download_thread = BackendDownloadThread( # Use renamed import
                 cancellation_event = self.cancellation_event,
                 **kwargs
            )

            if self.download_thread._init_failed:
                 QMessageBox.critical(self, "Thread Error", "Failed to initialize the download thread.\nCheck the log for details.")
                 self.download_finished(0, 0, False)
                 return
            self.download_thread.progress_signal.connect(self.log_signal)
            self.download_thread.add_character_prompt_signal.connect(self.add_character_prompt_signal)
            self.download_thread.file_download_status_signal.connect(self.file_download_status_signal)
            self.download_thread.finished_signal.connect(self.finished_signal)
            self.character_prompt_response_signal.connect(self.download_thread.receive_add_character_result)

            self.download_thread.start()
            self.log_signal.emit("✅ Single download thread started.")

        except Exception as e:
             self.log_signal.emit(f"❌ CRITICAL ERROR starting single-thread task: {e}")
             import traceback
             self.log_signal.emit(traceback.format_exc())
             QMessageBox.critical(self, "Thread Start Error", f"Failed to start download thread:\n{e}")
             self.download_finished(0, 0, False)



    def start_multi_threaded_download(self, **kwargs):
        import downloader_utils # For KNOWN_NAMES
        num_threads = kwargs['num_threads']
        self.thread_pool = ThreadPoolExecutor(max_workers=num_threads, thread_name_prefix='Downloader_')
        self.active_futures = []
        self.processed_posts_count = 0
        self.total_posts_to_process = 0
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
        import downloader_utils # For download_from_api
        all_posts = []
        fetch_error = False
        try:
            self.log_signal.emit("   Starting post fetch...")
            def fetcher_logger(msg):
                self.log_signal.emit(f"[Fetcher] {msg}")

            post_generator = downloader_utils.download_from_api(api_url_input, logger=fetcher_logger)

            for posts_batch in post_generator:
                if self.cancellation_event.is_set():
                    self.log_signal.emit("⚠️ Post fetching cancelled by user.")
                    fetch_error = True
                    break
                if isinstance(posts_batch, list):
                    all_posts.extend(posts_batch)
                    self.total_posts_to_process = len(all_posts)
                    if self.total_posts_to_process % 250 == 0:
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
            return


        if self.total_posts_to_process == 0:
             self.log_signal.emit("😕 No posts found or fetched successfully.")
             self.finished_signal.emit(0, 0, False)
             return
        self.log_signal.emit(f"   Submitting {self.total_posts_to_process} post tasks to worker pool...")
        self.processed_posts_count = 0
        self.overall_progress_signal.emit(self.total_posts_to_process, 0)
        common_worker_args = {
             'download_root': worker_args_template['output_dir'],
             'known_names': worker_args_template['known_names_copy'], # Already a copy from KNOWN_NAMES
             'filter_character': worker_args_template['filter_character'],
             'unwanted_keywords': {'spicy', 'hd', 'nsfw', '4k', 'preview'},
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
             'api_url_input': worker_args_template['api_url'],
             'cancellation_event': self.cancellation_event,
             'signals': self.worker_signals,
             'downloaded_files': self.downloaded_files,
             'downloaded_files_lock': self.downloaded_files_lock,
             'downloaded_file_hashes': self.downloaded_file_hashes,
             'downloaded_file_hashes_lock': self.downloaded_file_hashes_lock,
             'skip_words_list': worker_args_template['skip_words_list'],
        }

        for post_data in all_posts:
            if self.cancellation_event.is_set():
                self.log_signal.emit("⚠️ Cancellation detected during task submission.")
                break

            if not isinstance(post_data, dict):
                self.log_signal.emit(f"⚠️ Skipping invalid post data item (type: {type(post_data)}).")
                self.processed_posts_count += 1
                self.total_posts_to_process -=1
                continue
            worker = PostProcessorWorker(post_data=post_data, **common_worker_args) # PostProcessorWorker from downloader_utils
            try:
                 if self.thread_pool:
                     future = self.thread_pool.submit(worker.process)
                     future.add_done_callback(self._handle_future_result)
                     self.active_futures.append(future)
                 else:
                     self.log_signal.emit("⚠️ Thread pool shutdown before submitting all tasks.")
                     break
            except RuntimeError as e:
                 self.log_signal.emit(f"⚠️ Error submitting task (pool might be shutting down): {e}")
                 break
            except Exception as e:
                 self.log_signal.emit(f"❌ Unexpected error submitting task: {e}")
                 break
        submitted_count = len(self.active_futures)
        self.log_signal.emit(f"   {submitted_count} / {self.total_posts_to_process} tasks submitted.")



    def _handle_future_result(self, future: Future):
        self.processed_posts_count += 1
        downloaded_res, skipped_res = 0, 0

        try:
            if future.cancelled():
                 pass
            elif future.exception():
                exc = future.exception()
                self.log_signal.emit(f"❌ Error in worker thread: {exc}")
                pass
            else:
                downloaded, skipped = future.result()
                downloaded_res = downloaded
                skipped_res = skipped

            with threading.Lock():
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
        self.skip_words_input.setEnabled(enabled)
        self.character_search_input.setEnabled(enabled)
        self.new_char_input.setEnabled(enabled)
        self.add_char_button.setEnabled(enabled)
        self.delete_char_button.setEnabled(enabled)
        subfolders_on = self.use_subfolders_checkbox.isChecked()
        self.custom_folder_widget.setEnabled(enabled and subfolders_on)
        self.character_filter_widget.setEnabled(enabled and subfolders_on)
        if enabled:
             self.update_ui_for_subfolders(subfolders_on)
             self.update_custom_folder_visibility()
        self.cancel_btn.setEnabled(not enabled)
        if enabled:
            self.skip_file_btn.setEnabled(False)

    def cancel_download(self):
        if not self.cancel_btn.isEnabled(): return

        self.log_signal.emit("⚠️ Requesting cancellation...")
        self.cancellation_event.set()
        self.cancel_btn.setEnabled(False)
        self.progress_label.setText("Progress: Cancelling...")
        if self.thread_pool and self.active_futures:
            cancelled_count = 0
            for future in self.active_futures:
                if future.cancel():
                    cancelled_count += 1
            if cancelled_count > 0:
                 self.log_signal.emit(f"   Attempted to cancel {cancelled_count} pending/running tasks.")


    def skip_current_file(self):
         if self.download_thread and self.download_thread.isRunning():
              self.download_thread.skip_file()
         elif self.thread_pool:
              self.log_signal.emit("ℹ️ Skipping individual files is not supported in multi-threaded mode.")
              QMessageBox.information(self, "Action Not Supported", "Skipping individual files is only available in single-threaded mode.")
         else:
              self.log_signal.emit("ℹ️ Skip requested,  but no download is active.")


    def update_skip_button_state(self, is_downloading_active):
         can_skip = (not self.download_btn.isEnabled()) and \
                    (self.download_thread and self.download_thread.isRunning()) and \
                    is_downloading_active
         if self.thread_pool is not None:
             can_skip = False

         self.skip_file_btn.setEnabled(can_skip)


    def download_finished(self, total_downloaded, total_skipped, cancelled):
        self.log_signal.emit("="*40)
        status = "Cancelled" if cancelled else "Finished"
        self.log_signal.emit(f"🏁 Download {status}!")
        self.log_signal.emit(f"   Summary: Downloaded={total_downloaded}, Skipped={total_skipped}")
        self.progress_label.setText(f"{status}: {total_downloaded} downloaded, {total_skipped} skipped.")
        self.log_signal.emit("="*40)
        if self.download_thread:
            try:
                 self.character_prompt_response_signal.disconnect(self.download_thread.receive_add_character_result)
            except TypeError: pass
            self.download_thread = None
        if self.thread_pool:
            self.log_signal.emit("   Shutting down worker thread pool...")
            self.thread_pool.shutdown(wait=False, cancel_futures=True)
            self.thread_pool = None
            self.active_futures = []
        self.cancellation_event.clear()
        self.set_ui_enabled(True)
        self.cancel_btn.setEnabled(False)
        self.skip_file_btn.setEnabled(False)

    def prompt_add_character(self, character_name):
        import downloader_utils # For KNOWN_NAMES
        reply = QMessageBox.question(self, "Add Filter Name?",
                                      f"The filter name '{character_name}' is not in your known list.\n\nAdd it now and continue download?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        result = (reply == QMessageBox.Yes)

        if result:
              self.new_char_input.setText(character_name)
              if character_name.lower() not in {n.lower() for n in downloader_utils.KNOWN_NAMES}:
                   self.add_new_character()
                   if character_name.lower() not in {n.lower() for n in downloader_utils.KNOWN_NAMES}:
                        self.log_signal.emit(f"⚠️ Failed to add '{character_name}' via prompt. Check for errors.")
                        result = False
              else:
                   self.log_signal.emit(f"ℹ️ Filter name '{character_name}' was already present or added.")
        self.character_prompt_response_signal.emit(result)

    def receive_add_character_result(self, result):
        with QMutexLocker(self.prompt_mutex):
             self._add_character_response = result
        self.log_signal.emit(f"   Received prompt response: {'Yes' if result else 'No'}")

if __name__ == '__main__':
    qt_app = QApplication(sys.argv)
    icon_path = os.path.join(os.path.dirname(__file__), 'Kemono.ico')
    if os.path.exists(icon_path):
        qt_app.setWindowIcon(QIcon(icon_path))

    downloader = DownloaderApp()
    downloader.show()
    exit_code = qt_app.exec_()
    print(f"Application finished with exit code: {exit_code}")
    sys.exit(exit_code)