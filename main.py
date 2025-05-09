import sys
import os
import time
import requests
import re
import threading
import queue # Standard library queue, not directly used for the new link queue
import hashlib
import http.client
import traceback
import random # <-- Import random for generating delays
from collections import deque # <-- Import deque for the link queue

from concurrent.futures import ThreadPoolExecutor, CancelledError, Future

from PyQt5.QtGui import (
    QIcon,
    QIntValidator
)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QListWidget,
    QRadioButton, QButtonGroup, QCheckBox, QSplitter, QSizePolicy, QDialog
)
# Ensure QTimer is imported
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMutex, QMutexLocker, QObject, QTimer
from urllib.parse import urlparse

try:
    from PIL import Image
except ImportError:
    Image = None

from io import BytesIO

# --- Import from downloader_utils ---
try:
    print("Attempting to import from downloader_utils...")
    # Assuming downloader_utils_link_text is the correct version
    from downloader_utils import (
        KNOWN_NAMES,
        clean_folder_name,
        extract_post_info,
        download_from_api,
        PostProcessorSignals,
        PostProcessorWorker,
        DownloadThread as BackendDownloadThread
    )
    print("Successfully imported names from downloader_utils.")
except ImportError as e:
    print(f"--- IMPORT ERROR ---")
    print(f"Failed to import from 'downloader_utils.py': {e}")
    # ... (rest of error handling as in your original file) ...
    KNOWN_NAMES = []
    PostProcessorSignals = QObject
    PostProcessorWorker = object
    BackendDownloadThread = QThread
    def clean_folder_name(n): return str(n) # Fallback
    def extract_post_info(u): return None, None, None
    def download_from_api(*a, **k): yield []
except Exception as e:
    print(f"--- UNEXPECTED IMPORT ERROR ---")
    print(f"An unexpected error occurred during import: {e}")
    traceback.print_exc()
    print(f"-----------------------------", file=sys.stderr)
    sys.exit(1)
# --- End Import ---

# --- Import Tour Dialog ---
try:
    from tour import TourDialog
    print("Successfully imported TourDialog from tour.py.")
except ImportError as e:
    print(f"--- TOUR IMPORT ERROR ---")
    print(f"Failed to import TourDialog from 'tour.py': {e}")
    print("Tour functionality will be unavailable.")
    TourDialog = None # Fallback if tour.py is missing
except Exception as e:
    print(f"--- UNEXPECTED TOUR IMPORT ERROR ---")
    print(f"An unexpected error occurred during tour import: {e}")
    traceback.print_exc()
    TourDialog = None
# --- End Tour Import ---


# --- Constants for Thread Limits ---
MAX_THREADS = 200 # Absolute maximum allowed by the input validator
RECOMMENDED_MAX_THREADS = 50 # Threshold for showing the informational warning
# --- END ---

# --- ADDED: Prefix for HTML messages in main log ---
HTML_PREFIX = "<!HTML!>" # Used to identify HTML lines for insertHtml
# --- END ADDED ---

class DownloaderApp(QWidget):
    character_prompt_response_signal = pyqtSignal(bool)
    log_signal = pyqtSignal(str)
    add_character_prompt_signal = pyqtSignal(str)
    overall_progress_signal = pyqtSignal(int, int)
    finished_signal = pyqtSignal(int, int, bool)
    # Signal now carries link_text (ensure this matches downloader_utils)
    external_link_signal = pyqtSignal(str, str, str, str) # post_title, link_text, link_url, platform
    file_progress_signal = pyqtSignal(str, int, int)


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
        self.worker_signals = PostProcessorSignals() # Instance of signals for multi-thread workers
        self.prompt_mutex = QMutex()
        self._add_character_response = None
        self.downloaded_files = set()
        self.downloaded_files_lock = threading.Lock()
        self.downloaded_file_hashes = set()
        self.downloaded_file_hashes_lock = threading.Lock()
        # self.external_links = [] # This list seems unused now
        self.show_external_links = False

        # --- For sequential delayed link display ---
        self.external_link_queue = deque()
        self._is_processing_external_link_queue = False
        self._current_link_post_title = None # Track title for grouping
        self.extracted_links_cache = [] # Store all links when in "Only Links" mode
        # --- END ---

        # --- For Log Verbosity ---
        self.basic_log_mode = False # Start with full log (basic_log_mode is False)
        self.log_verbosity_button = None
        # --- END ---

        self.main_log_output = None
        self.external_log_output = None
        self.log_splitter = None # This is the VERTICAL splitter for logs
        self.main_splitter = None # This will be the main HORIZONTAL splitter
        self.reset_button = None
        self.progress_log_label = None # To change title

        # --- For Link Search ---
        self.link_search_input = None
        self.link_search_button = None
        # --- END ---

        # --- For Export Links ---
        self.export_links_button = None
        # --- END ---

        self.manga_mode_checkbox = None
        self.radio_only_links = None # Define radio button attribute

        self.load_known_names_from_util()
        self.setWindowTitle("Kemono Downloader v2.9 (Manga Mode - No Skip Button)")
        self.setGeometry(150, 150, 1050, 820) # Initial size
        self.setStyleSheet(self.get_dark_theme())
        self.init_ui()
        self._connect_signals()
        self.log_signal.emit("ℹ️ Local API server functionality has been removed.")
        self.log_signal.emit("ℹ️ 'Skip Current File' button has been removed.")
        self.character_input.setToolTip("Enter one or more character names, separated by commas (e.g., yor, makima)")


    def _connect_signals(self):
        # Signals from the worker_signals object (used by PostProcessorWorker in multi-threaded mode)
        if hasattr(self.worker_signals, 'progress_signal'):
             self.worker_signals.progress_signal.connect(self.handle_main_log)
        if hasattr(self.worker_signals, 'file_progress_signal'):
            self.worker_signals.file_progress_signal.connect(self.update_file_progress_display)
        # Connect the external_link_signal from worker_signals to the queue handler
        if hasattr(self.worker_signals, 'external_link_signal'):
            self.worker_signals.external_link_signal.connect(self.handle_external_link_signal)

        # App's own signals (some of which might be emitted by DownloadThread which then connects to these handlers)
        self.log_signal.connect(self.handle_main_log)
        self.add_character_prompt_signal.connect(self.prompt_add_character)
        self.character_prompt_response_signal.connect(self.receive_add_character_result)
        self.overall_progress_signal.connect(self.update_progress_display)
        self.finished_signal.connect(self.download_finished)
        # Connect the app's external_link_signal also to the queue handler
        self.external_link_signal.connect(self.handle_external_link_signal)
        self.file_progress_signal.connect(self.update_file_progress_display)


        self.character_search_input.textChanged.connect(self.filter_character_list)
        self.external_links_checkbox.toggled.connect(self.update_external_links_setting)
        self.thread_count_input.textChanged.connect(self.update_multithreading_label)
        self.use_subfolder_per_post_checkbox.toggled.connect(self.update_ui_for_subfolders)

        # --- MODIFIED: Connect multithreading checkbox toggle ---
        self.use_multithreading_checkbox.toggled.connect(self._handle_multithreading_toggle)
        # --- END MODIFIED ---

        # --- MODIFIED: Connect radio group toggle ---
        if self.radio_group:
            self.radio_group.buttonToggled.connect(self._handle_filter_mode_change) # Use buttonToggled for group signal
        # --- END MODIFIED ---

        if self.reset_button:
            self.reset_button.clicked.connect(self.reset_application_state)

        # Connect log verbosity button if it exists
        if self.log_verbosity_button:
            self.log_verbosity_button.clicked.connect(self.toggle_log_verbosity)

        # --- ADDED: Connect link search elements ---
        if self.link_search_button:
            self.link_search_button.clicked.connect(self._filter_links_log)
        if self.link_search_input:
            self.link_search_input.returnPressed.connect(self._filter_links_log)
            self.link_search_input.textChanged.connect(self._filter_links_log) # Real-time filtering
        # --- END ADDED ---

        # --- ADDED: Connect export links button ---
        if self.export_links_button:
            self.export_links_button.clicked.connect(self._export_links_to_file)
        # --- END ADDED ---

        if self.manga_mode_checkbox:
            self.manga_mode_checkbox.toggled.connect(self.update_ui_for_manga_mode)
        self.link_input.textChanged.connect(lambda: self.update_ui_for_manga_mode(self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False))

    # --- load_known_names_from_util, save_known_names, closeEvent ---
    # These methods remain unchanged from your original file

    def load_known_names_from_util(self):
        global KNOWN_NAMES
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    raw_names = [line.strip() for line in f]
                    # Filter out empty strings before setting KNOWN_NAMES
                    KNOWN_NAMES[:] = sorted(list(set(filter(None, raw_names))))
                log_msg = f"ℹ️ Loaded {len(KNOWN_NAMES)} known names from {self.config_file}"
            except Exception as e:
                log_msg = f"❌ Error loading config '{self.config_file}': {e}"
                QMessageBox.warning(self, "Config Load Error", f"Could not load list from {self.config_file}:\n{e}")
                KNOWN_NAMES[:] = []
        else:
            log_msg = f"ℹ️ Config file '{self.config_file}' not found. Starting empty."
            KNOWN_NAMES[:] = []

        self.log_signal.emit(log_msg)

        if hasattr(self, 'character_list'): # Ensure character_list widget exists
            self.character_list.clear()
            self.character_list.addItems(KNOWN_NAMES)


    def save_known_names(self):
        global KNOWN_NAMES
        try:
            # Ensure KNOWN_NAMES contains unique, non-empty, sorted strings
            unique_sorted_names = sorted(list(set(filter(None, KNOWN_NAMES))))
            KNOWN_NAMES[:] = unique_sorted_names # Update global list in place

            with open(self.config_file, 'w', encoding='utf-8') as f:
                for name in unique_sorted_names:
                    f.write(name + '\n')
            self.log_signal.emit(f"💾 Saved {len(unique_sorted_names)} known names to {self.config_file}")
        except Exception as e:
            log_msg = f"❌ Error saving config '{self.config_file}': {e}"
            self.log_signal.emit(log_msg)
            QMessageBox.warning(self, "Config Save Error", f"Could not save list to {self.config_file}:\n{e}")

    def closeEvent(self, event):
        self.save_known_names()
        should_exit = True
        is_downloading = (self.download_thread and self.download_thread.isRunning()) or \
                         (self.thread_pool is not None and any(not f.done() for f in self.active_futures if f is not None))


        if is_downloading:
             reply = QMessageBox.question(self, "Confirm Exit",
                                          "Download in progress. Are you sure you want to exit and cancel?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
             if reply == QMessageBox.Yes:
                 self.log_signal.emit("⚠️ Cancelling active download due to application exit...")
                 self.cancel_download() # Signal cancellation
                 # --- MODIFICATION START: Wait for threads to finish ---
                 self.log_signal.emit("   Waiting briefly for threads to acknowledge cancellation...")
                 # Wait for the single thread if it exists
                 if self.download_thread and self.download_thread.isRunning():
                     self.download_thread.wait(3000) # Wait up to 3 seconds
                     if self.download_thread.isRunning():
                         self.log_signal.emit("   ⚠️ Single download thread did not terminate gracefully.")
                 # Wait for the thread pool if it exists
                 if self.thread_pool:
                     # Shutdown was already initiated by cancel_download, just wait here
                     # Use wait=True here for cleaner exit
                     self.thread_pool.shutdown(wait=True, cancel_futures=True)
                     self.log_signal.emit("   Thread pool shutdown complete.")
                     self.thread_pool = None # Clear reference
                 # --- MODIFICATION END ---
             else:
                 should_exit = False
                 self.log_signal.emit("ℹ️ Application exit cancelled.")
                 event.ignore()
                 return

        if should_exit:
            self.log_signal.emit("ℹ️ Application closing.")
            # Ensure thread pool is None if already shut down above
            if self.thread_pool:
                 self.log_signal.emit("   Final thread pool check: Shutting down...")
                 self.cancellation_event.set()
                 self.thread_pool.shutdown(wait=True, cancel_futures=True)
                 self.thread_pool = None
            self.log_signal.emit("👋 Exiting application.")
            event.accept()

    def init_ui(self):
        # --- MODIFIED: Use QSplitter for main layout ---
        self.main_splitter = QSplitter(Qt.Horizontal)

        # Create container widgets for left and right panels
        left_panel_widget = QWidget()
        right_panel_widget = QWidget()

        # Setup layouts for the panels
        left_layout = QVBoxLayout(left_panel_widget) # Apply layout to widget
        right_layout = QVBoxLayout(right_panel_widget) # Apply layout to widget
        left_layout.setContentsMargins(10, 10, 10, 10) # Add some margins
        right_layout.setContentsMargins(10, 10, 10, 10)

        # --- Populate Left Panel (Controls) ---
        # (All the QLineEdit, QCheckBox, QPushButton, etc. setup code goes here, adding to left_layout)
        # URL and Page Range Input
        url_page_layout = QHBoxLayout()
        url_page_layout.setContentsMargins(0,0,0,0)
        url_page_layout.addWidget(QLabel("🔗 Kemono Creator/Post URL:"))
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("e.g., https://kemono.su/patreon/user/12345 or .../post/98765")
        self.link_input.textChanged.connect(self.update_custom_folder_visibility)
        # self.link_input.setFixedWidth(int(self.width() * 0.45)) # Remove fixed width for splitter
        url_page_layout.addWidget(self.link_input, 1) # Give it stretch factor

        self.page_range_label = QLabel("Page Range:")
        self.page_range_label.setStyleSheet("font-weight: bold; padding-left: 10px;")
        self.start_page_input = QLineEdit()
        self.start_page_input.setPlaceholderText("Start")
        self.start_page_input.setFixedWidth(50)
        self.start_page_input.setValidator(QIntValidator(1, 99999)) # Min 1
        self.to_label = QLabel("to")
        self.end_page_input = QLineEdit()
        self.end_page_input.setPlaceholderText("End")
        self.end_page_input.setFixedWidth(50)
        self.end_page_input.setValidator(QIntValidator(1, 99999)) # Min 1
        url_page_layout.addWidget(self.page_range_label)
        url_page_layout.addWidget(self.start_page_input)
        url_page_layout.addWidget(self.to_label)
        url_page_layout.addWidget(self.end_page_input)
        # url_page_layout.addStretch(1) # No need for stretch with splitter
        left_layout.addLayout(url_page_layout)

        # Download Directory Input
        left_layout.addWidget(QLabel("📁 Download Location:"))
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select folder where downloads will be saved")
        self.dir_button = QPushButton("Browse...")
        self.dir_button.clicked.connect(self.browse_directory)
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.dir_input, 1) # Input takes more space
        dir_layout.addWidget(self.dir_button)
        left_layout.addLayout(dir_layout)

        # Custom Folder Name (for single post)
        self.custom_folder_widget = QWidget() # Use a widget to hide/show group
        custom_folder_layout = QVBoxLayout(self.custom_folder_widget)
        custom_folder_layout.setContentsMargins(0, 5, 0, 0) # No top margin if hidden
        self.custom_folder_label = QLabel("🗄️ Custom Folder Name (Single Post Only):")
        self.custom_folder_input = QLineEdit()
        self.custom_folder_input.setPlaceholderText("Optional: Save this post to specific folder")
        custom_folder_layout.addWidget(self.custom_folder_label)
        custom_folder_layout.addWidget(self.custom_folder_input)
        self.custom_folder_widget.setVisible(False) # Initially hidden
        left_layout.addWidget(self.custom_folder_widget)

        # Character Filter Input
        self.character_filter_widget = QWidget()
        character_filter_layout = QVBoxLayout(self.character_filter_widget)
        character_filter_layout.setContentsMargins(0,5,0,0)
        self.character_label = QLabel("🎯 Filter by Character(s) (comma-separated):")
        self.character_input = QLineEdit()
        self.character_input.setPlaceholderText("e.g., yor, Tifa, Reyna")
        character_filter_layout.addWidget(self.character_label)
        character_filter_layout.addWidget(self.character_input)
        self.character_filter_widget.setVisible(True) # Visible by default
        left_layout.addWidget(self.character_filter_widget)

        # Skip Words Input
        left_layout.addWidget(QLabel("🚫 Skip Posts/Files with Words (comma-separated):"))
        self.skip_words_input = QLineEdit()
        self.skip_words_input.setPlaceholderText("e.g., WM, WIP, sketch, preview")
        left_layout.addWidget(self.skip_words_input)

        # --- MODIFIED: File Type Filter Radio Buttons ---
        file_filter_layout = QVBoxLayout() # Group label and radio buttons
        file_filter_layout.setContentsMargins(0,0,0,0) # Compact
        file_filter_layout.addWidget(QLabel("Filter Files:"))
        radio_button_layout = QHBoxLayout()
        radio_button_layout.setSpacing(10)
        self.radio_group = QButtonGroup(self) # Ensures one selection
        self.radio_all = QRadioButton("All")
        self.radio_images = QRadioButton("Images/GIFs")
        self.radio_videos = QRadioButton("Videos")
        self.radio_only_links = QRadioButton("🔗 Only Links") # New button
        self.radio_all.setChecked(True)
        self.radio_group.addButton(self.radio_all)
        self.radio_group.addButton(self.radio_images)
        self.radio_group.addButton(self.radio_videos)
        self.radio_group.addButton(self.radio_only_links) # Add to group
        radio_button_layout.addWidget(self.radio_all)
        radio_button_layout.addWidget(self.radio_images)
        radio_button_layout.addWidget(self.radio_videos)
        radio_button_layout.addWidget(self.radio_only_links) # Add to layout
        radio_button_layout.addStretch(1) # Pushes buttons to left
        file_filter_layout.addLayout(radio_button_layout)
        left_layout.addLayout(file_filter_layout)
        # --- END MODIFIED ---

        # Checkboxes Group
        checkboxes_group_layout = QVBoxLayout()
        checkboxes_group_layout.setSpacing(10) # Spacing between rows of checkboxes

        row1_layout = QHBoxLayout() # First row of checkboxes
        row1_layout.setSpacing(10)
        self.skip_zip_checkbox = QCheckBox("Skip .zip")
        self.skip_zip_checkbox.setChecked(True)
        row1_layout.addWidget(self.skip_zip_checkbox)
        self.skip_rar_checkbox = QCheckBox("Skip .rar")
        self.skip_rar_checkbox.setChecked(True)
        row1_layout.addWidget(self.skip_rar_checkbox)
        self.download_thumbnails_checkbox = QCheckBox("Download Thumbnails Only")
        self.download_thumbnails_checkbox.setChecked(False)
        self.download_thumbnails_checkbox.setToolTip("Thumbnail download functionality is currently limited without the API.")
        row1_layout.addWidget(self.download_thumbnails_checkbox)
        self.compress_images_checkbox = QCheckBox("Compress Large Images (to WebP)")
        self.compress_images_checkbox.setChecked(False)
        self.compress_images_checkbox.setToolTip("Compress images > 1.5MB to WebP format (requires Pillow).")
        row1_layout.addWidget(self.compress_images_checkbox)
        row1_layout.addStretch(1) # Pushes checkboxes to left
        checkboxes_group_layout.addLayout(row1_layout)

        # Advanced Settings Section
        advanced_settings_label = QLabel("⚙️ Advanced Settings:")
        checkboxes_group_layout.addWidget(advanced_settings_label)

        advanced_row1_layout = QHBoxLayout() # Subfolders options
        advanced_row1_layout.setSpacing(10)
        self.use_subfolders_checkbox = QCheckBox("Separate Folders by Name/Title")
        self.use_subfolders_checkbox.setChecked(True)
        self.use_subfolders_checkbox.toggled.connect(self.update_ui_for_subfolders)
        advanced_row1_layout.addWidget(self.use_subfolders_checkbox)
        self.use_subfolder_per_post_checkbox = QCheckBox("Subfolder per Post")
        self.use_subfolder_per_post_checkbox.setChecked(False)
        self.use_subfolder_per_post_checkbox.setToolTip("Creates a subfolder for each post inside the character/title folder.")
        self.use_subfolder_per_post_checkbox.toggled.connect(self.update_ui_for_subfolders) # Also update UI
        advanced_row1_layout.addWidget(self.use_subfolder_per_post_checkbox)
        advanced_row1_layout.addStretch(1)
        checkboxes_group_layout.addLayout(advanced_row1_layout)

        advanced_row2_layout = QHBoxLayout() # Multithreading, External Links, Manga Mode
        advanced_row2_layout.setSpacing(10)
        multithreading_layout = QHBoxLayout() # Group multithreading checkbox and input
        multithreading_layout.setContentsMargins(0,0,0,0)
        self.use_multithreading_checkbox = QCheckBox("Use Multithreading")
        self.use_multithreading_checkbox.setChecked(True)
        self.use_multithreading_checkbox.setToolTip("Speeds up downloads for full creator pages.\nSingle post URLs always use one thread.")
        multithreading_layout.addWidget(self.use_multithreading_checkbox)
        self.thread_count_label = QLabel("Threads:")
        multithreading_layout.addWidget(self.thread_count_label)
        self.thread_count_input = QLineEdit()
        self.thread_count_input.setFixedWidth(40)
        self.thread_count_input.setText("4")
        # --- MODIFIED: Updated tooltip to remove recommendation ---
        self.thread_count_input.setToolTip(f"Number of threads (max: {MAX_THREADS}).")
        # --- END MODIFIED ---
        self.thread_count_input.setValidator(QIntValidator(1, MAX_THREADS)) # Use constant
        multithreading_layout.addWidget(self.thread_count_input)
        advanced_row2_layout.addLayout(multithreading_layout)

        self.external_links_checkbox = QCheckBox("Show External Links in Log")
        self.external_links_checkbox.setChecked(False)
        advanced_row2_layout.addWidget(self.external_links_checkbox)

        self.manga_mode_checkbox = QCheckBox("Manga/Comic Mode")
        self.manga_mode_checkbox.setToolTip("Process newest posts first, rename files based on post title (for creator feeds only).")
        self.manga_mode_checkbox.setChecked(False)
        advanced_row2_layout.addWidget(self.manga_mode_checkbox)
        advanced_row2_layout.addStretch(1)
        checkboxes_group_layout.addLayout(advanced_row2_layout)

        left_layout.addLayout(checkboxes_group_layout)

        # Download and Cancel Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.download_btn = QPushButton("⬇️ Start Download")
        self.download_btn.setStyleSheet("padding: 8px 15px; font-weight: bold;") # Make it prominent
        self.download_btn.clicked.connect(self.start_download)
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setEnabled(False) # Initially disabled
        self.cancel_btn.clicked.connect(self.cancel_download)
        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.cancel_btn)
        left_layout.addLayout(btn_layout)
        left_layout.addSpacing(10) # Some space before known characters list

        # Known Characters/Shows List Management
        known_chars_label_layout = QHBoxLayout()
        known_chars_label_layout.setSpacing(10)
        self.known_chars_label = QLabel("🎭 Known Shows/Characters (for Folder Names):")
        self.character_search_input = QLineEdit()
        self.character_search_input.setPlaceholderText("Search characters...")
        known_chars_label_layout.addWidget(self.known_chars_label, 1) # Label takes more space
        known_chars_label_layout.addWidget(self.character_search_input)
        left_layout.addLayout(known_chars_label_layout)

        self.character_list = QListWidget()
        self.character_list.setSelectionMode(QListWidget.ExtendedSelection) # Allow multi-select for delete
        left_layout.addWidget(self.character_list, 1) # Takes remaining vertical space

        char_manage_layout = QHBoxLayout() # Add/Delete character buttons
        char_manage_layout.setSpacing(10)
        self.new_char_input = QLineEdit()
        self.new_char_input.setPlaceholderText("Add new show/character name")
        self.add_char_button = QPushButton("➕ Add")
        self.delete_char_button = QPushButton("🗑️ Delete Selected")
        self.add_char_button.clicked.connect(self.add_new_character)
        self.new_char_input.returnPressed.connect(self.add_char_button.click) # Add on Enter
        self.delete_char_button.clicked.connect(self.delete_selected_character)
        char_manage_layout.addWidget(self.new_char_input, 2) # Input field wider
        char_manage_layout.addWidget(self.add_char_button, 1)
        char_manage_layout.addWidget(self.delete_char_button, 1)
        left_layout.addLayout(char_manage_layout)
        left_layout.addStretch(0) # Prevent vertical stretching of controls

        # --- Populate Right Panel (Logs) ---
        log_title_layout = QHBoxLayout()
        self.progress_log_label = QLabel("📜 Progress Log:") # Store label reference
        log_title_layout.addWidget(self.progress_log_label)
        log_title_layout.addStretch(1)

        # --- ADDED: Link Search Bar ---
        self.link_search_input = QLineEdit()
        self.link_search_input.setPlaceholderText("Search Links...")
        self.link_search_input.setVisible(False) # Initially hidden
        self.link_search_input.setFixedWidth(150) # Adjust width
        log_title_layout.addWidget(self.link_search_input)

        self.link_search_button = QPushButton("🔍")
        self.link_search_button.setToolTip("Filter displayed links")
        self.link_search_button.setVisible(False) # Initially hidden
        self.link_search_button.setFixedWidth(30)
        self.link_search_button.setStyleSheet("padding: 4px 4px;")
        log_title_layout.addWidget(self.link_search_button)
        # --- END ADDED ---

        # --- ADDED: Log Verbosity Button ---
        self.log_verbosity_button = QPushButton("Show Basic Log") # Default text
        self.log_verbosity_button.setToolTip("Toggle between full and basic log details.")
        self.log_verbosity_button.setFixedWidth(110) # Adjust width as needed
        self.log_verbosity_button.setStyleSheet("padding: 4px 8px;")
        log_title_layout.addWidget(self.log_verbosity_button)
        # --- END ADDED ---

        self.reset_button = QPushButton("🔄 Reset")
        self.reset_button.setToolTip("Reset all inputs and logs to default state (only when idle).")
        self.reset_button.setFixedWidth(80)
        self.reset_button.setStyleSheet("padding: 4px 8px;") # Smaller padding
        log_title_layout.addWidget(self.reset_button)
        right_layout.addLayout(log_title_layout)

        self.log_splitter = QSplitter(Qt.Vertical) # Keep the vertical splitter for logs
        self.main_log_output = QTextEdit()
        self.main_log_output.setReadOnly(True)
        # self.main_log_output.setMinimumWidth(450) # Remove minimum width
        self.main_log_output.setLineWrapMode(QTextEdit.NoWrap) # Disable line wrapping
        self.main_log_output.setStyleSheet("""
            QTextEdit {
                 background-color: #3C3F41; border: 1px solid #5A5A5A; padding: 5px;
                 color: #F0F0F0; border-radius: 4px; font-family: Consolas, Courier New, monospace; font-size: 9.5pt;
            }""")
        self.external_log_output = QTextEdit()
        self.external_log_output.setReadOnly(True)
        # self.external_log_output.setMinimumWidth(450) # Remove minimum width
        self.external_log_output.setLineWrapMode(QTextEdit.NoWrap) # Disable line wrapping
        self.external_log_output.setStyleSheet("""
            QTextEdit {
                 background-color: #3C3F41; border: 1px solid #5A5A5A; padding: 5px;
                 color: #F0F0F0; border-radius: 4px; font-family: Consolas, Courier New, monospace; font-size: 9.5pt;
            }""")
        self.external_log_output.hide() # Initially hidden
        self.log_splitter.addWidget(self.main_log_output)
        self.log_splitter.addWidget(self.external_log_output)
        self.log_splitter.setSizes([self.height(), 0]) # Main log takes all space initially
        right_layout.addWidget(self.log_splitter, 1) # Log splitter takes available vertical space

        # --- ADDED: Export Links Button ---
        export_button_layout = QHBoxLayout()
        export_button_layout.addStretch(1) # Push button to the right
        self.export_links_button = QPushButton("Export Links")
        self.export_links_button.setToolTip("Export all extracted links to a .txt file.")
        self.export_links_button.setFixedWidth(100)
        self.export_links_button.setStyleSheet("padding: 4px 8px; margin-top: 5px;")
        self.export_links_button.setEnabled(False) # Initially disabled
        self.export_links_button.setVisible(False) # Initially hidden
        export_button_layout.addWidget(self.export_links_button)
        right_layout.addLayout(export_button_layout) # Add to bottom of right panel
        # --- END ADDED ---

        self.progress_label = QLabel("Progress: Idle")
        self.progress_label.setStyleSheet("padding-top: 5px; font-style: italic;")
        right_layout.addWidget(self.progress_label)

        self.file_progress_label = QLabel("") # For individual file progress
        self.file_progress_label.setWordWrap(True) # Enable word wrapping for the status label
        self.file_progress_label.setStyleSheet("padding-top: 2px; font-style: italic; color: #A0A0A0;")
        right_layout.addWidget(self.file_progress_label)

        # --- Add panels to the main horizontal splitter ---
        self.main_splitter.addWidget(left_panel_widget)
        self.main_splitter.addWidget(right_panel_widget)

        # --- Set initial sizes for the splitter ---
        # Calculate initial sizes (e.g., left 30%, right 70%)
        initial_width = self.width() # Use the initial window width
        left_width = int(initial_width * 0.30)
        right_width = initial_width - left_width
        self.main_splitter.setSizes([left_width, right_width])

        # --- Set the main splitter as the central layout ---
        # Need a top-level layout to hold the splitter
        top_level_layout = QHBoxLayout(self) # Apply layout directly to the main widget (self)
        top_level_layout.setContentsMargins(0,0,0,0) # No margins for the main layout
        top_level_layout.addWidget(self.main_splitter)
        # self.setLayout(top_level_layout) # Already set above

        # --- End Layout Modification ---

        # Initial UI state updates
        self.update_ui_for_subfolders(self.use_subfolders_checkbox.isChecked())
        self.update_custom_folder_visibility()
        self.update_external_links_setting(self.external_links_checkbox.isChecked())
        self.update_multithreading_label(self.thread_count_input.text())
        self.update_page_range_enabled_state()
        if self.manga_mode_checkbox: # Ensure it exists before accessing
            self.update_ui_for_manga_mode(self.manga_mode_checkbox.isChecked())
        self.link_input.textChanged.connect(self.update_page_range_enabled_state) # Connect after init
        self.load_known_names_from_util() # Load names into the list widget
        self._handle_multithreading_toggle(self.use_multithreading_checkbox.isChecked()) # Set initial state
        self._handle_filter_mode_change(self.radio_group.checkedButton(), True) # Set initial filter mode UI state


    def get_dark_theme(self):
        return """
        QWidget { background-color: #2E2E2E; color: #E0E0E0; font-family: Segoe UI, Arial, sans-serif; font-size: 10pt; }
        QLineEdit, QListWidget { background-color: #3C3F41; border: 1px solid #5A5A5A; padding: 5px; color: #F0F0F0; border-radius: 4px; }
        QTextEdit { background-color: #3C3F41; border: 1px solid #5A5A5A; padding: 5px; color: #F0F0F0; border-radius: 4px; }
        QPushButton { background-color: #555; color: #F0F0F0; border: 1px solid #6A6A6A; padding: 6px 12px; border-radius: 4px; min-height: 22px; }
        QPushButton:hover { background-color: #656565; border: 1px solid #7A7A7A; }
        QPushButton:pressed { background-color: #4A4A4A; }
        QPushButton:disabled { background-color: #404040; color: #888; border-color: #555; }
        QLabel { font-weight: bold; padding-top: 4px; padding-bottom: 2px; color: #C0C0C0; }
        QRadioButton, QCheckBox { spacing: 5px; color: #E0E0E0; padding-top: 4px; padding-bottom: 4px; }
        QRadioButton::indicator, QCheckBox::indicator { width: 14px; height: 14px; }
        QListWidget { alternate-background-color: #353535; border: 1px solid #5A5A5A; }
        QListWidget::item:selected { background-color: #007ACC; color: #FFFFFF; }
        QToolTip { background-color: #4A4A4A; color: #F0F0F0; border: 1px solid #6A6A6A; padding: 4px; border-radius: 3px; }
        QSplitter::handle { background-color: #5A5A5A; width: 5px; /* Make handle slightly wider */ }
        QSplitter::handle:horizontal { width: 5px; }
        QSplitter::handle:vertical { height: 5px; }
        """ # Added styling for splitter handle

    def browse_directory(self):
        current_dir = self.dir_input.text() if os.path.isdir(self.dir_input.text()) else ""
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", current_dir)
        if folder:
            self.dir_input.setText(folder)

    def handle_main_log(self, message):
        # --- MODIFIED: Check for HTML_PREFIX ---
        is_html_message = message.startswith(HTML_PREFIX)

        if is_html_message:
             # If it's HTML, strip the prefix and use insertHtml
             display_message = message[len(HTML_PREFIX):]
             use_html = True
        elif self.basic_log_mode: # Apply basic filtering only if NOT HTML
            # Define keywords/prefixes for messages to ALWAYS show in basic mode
            basic_keywords = [
                '🚀 starting download', '🏁 download finished', '🏁 download cancelled',
                '❌', '⚠️', '✅ all posts processed', '✅ reached end of posts',
                'summary:', 'progress:', '[fetcher]', # Show fetcher logs for context
                'critical error', 'import error', 'error', 'fail', 'timeout',
                'unsupported url', 'invalid url', 'no posts found', 'could not create directory',
                'missing dependency', 'high thread count', 'manga mode filter warning',
                'duplicate name', 'potential name conflict', 'invalid filter name',
                'no valid character filters'
            ]
            message_lower = message.lower()
            if not any(keyword in message_lower for keyword in basic_keywords):
                 if not message.strip().startswith("✅ Saved:") and \
                    not message.strip().startswith("✅ Added") and \
                    not message.strip().startswith("✅ Application reset complete"):
                    return # Skip appending less important messages in basic mode
            display_message = message # Use original message if it passes basic filter
            use_html = False
        else: # Full log mode and not HTML
             display_message = message
             use_html = False
        # --- END MODIFIED ---

        try:
             # Ensure message is a string and replace null characters that can crash QTextEdit
             safe_message = str(display_message).replace('\x00', '[NULL]')
             if use_html:
                 self.main_log_output.insertHtml(safe_message) # Use insertHtml for formatted titles
             else:
                 self.main_log_output.append(safe_message) # Use append for plain text
             # Auto-scroll if near the bottom
             scrollbar = self.main_log_output.verticalScrollBar()
             if scrollbar.value() >= scrollbar.maximum() - 30: # Threshold for auto-scroll
                 scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
             # Fallback logging if GUI logging fails
             print(f"GUI Main Log Error: {e}\nOriginal Message: {message}")

    # --- ADDED: Helper to check download state ---
    def _is_download_active(self):
        """Checks if a download thread or pool is currently active."""
        single_thread_active = self.download_thread and self.download_thread.isRunning()
        # Check if pool exists AND has any futures that are not done
        pool_active = self.thread_pool is not None and any(not f.done() for f in self.active_futures if f is not None)
        return single_thread_active or pool_active
    # --- END ADDED ---

    # --- ADDED: New system for handling external links with sequential CONDIITONAL delay ---
    # MODIFIED: Slot now takes link_text as the second argument
    def handle_external_link_signal(self, post_title, link_text, link_url, platform):
        """Receives link signals, adds them to a queue, and triggers processing."""
        link_data = (post_title, link_text, link_url, platform)
        self.external_link_queue.append(link_data)
        # --- ADDED: Cache link if in "Only Links" mode ---
        if self.radio_only_links and self.radio_only_links.isChecked():
            self.extracted_links_cache.append(link_data)
        # --- END ADDED ---
        self._try_process_next_external_link()

    def _try_process_next_external_link(self):
        """Processes the next link from the queue if not already processing."""
        if self._is_processing_external_link_queue or not self.external_link_queue:
             return # Don't process if busy or queue empty

        # Determine if we should display based on mode and checkbox state
        is_only_links_mode = self.radio_only_links and self.radio_only_links.isChecked()
        should_display_in_external = self.show_external_links and not is_only_links_mode

        # Only proceed if displaying in *either* log is currently possible/enabled
        if not (is_only_links_mode or should_display_in_external):
             # If neither log is active/visible for this link, still need to allow queue processing
             self._is_processing_external_link_queue = False
             if self.external_link_queue:
                 QTimer.singleShot(0, self._try_process_next_external_link)
             return

        self._is_processing_external_link_queue = True

        link_data = self.external_link_queue.popleft()

        # --- MODIFIED: Schedule the display AND the next step based on mode ---
        if is_only_links_mode:
            # Schedule with fixed 0.4s delay for "Only Links" mode
            delay_ms = 80 # 0.08 seconds
            QTimer.singleShot(delay_ms, lambda data=link_data: self._display_and_schedule_next(data))
        elif self._is_download_active():
            # Schedule with random delay for other modes during download
            delay_ms = random.randint(4000, 8000)
            QTimer.singleShot(delay_ms, lambda data=link_data: self._display_and_schedule_next(data))
        else:
            # No download active in other modes, process immediately
            QTimer.singleShot(0, lambda data=link_data: self._display_and_schedule_next(data))
        # --- END MODIFIED ---

    # --- NEW Method ---
    def _display_and_schedule_next(self, link_data):
        """Displays the link in the correct log and schedules the check for the next link."""
        post_title, link_text, link_url, platform = link_data # Unpack all data
        is_only_links_mode = self.radio_only_links and self.radio_only_links.isChecked()

        # Format the link text part
        max_link_text_len = 35
        display_text = link_text[:max_link_text_len].strip() + "..." if len(link_text) > max_link_text_len else link_text
        formatted_link_info = f"{display_text} - {link_url} - {platform}"
        separator = "-" * 45

        if is_only_links_mode:
            # Check if the post title has changed
            if post_title != self._current_link_post_title:
                # Emit separator and new title (formatted as HTML)
                self.log_signal.emit(HTML_PREFIX + "<br>" + separator + "<br>")
                # Use HTML for bold blue title
                title_html = f'<b style="color: #87CEEB;">{post_title}</b><br>'
                self.log_signal.emit(HTML_PREFIX + title_html)
                self._current_link_post_title = post_title # Update current title

            # Emit the link info as plain text (handle_main_log will append it)
            self.log_signal.emit(formatted_link_info)

        elif self.show_external_links:
             # Append directly to external log (plain text)
             self._append_to_external_log(formatted_link_info, separator)

        # Allow the next link to be processed
        self._is_processing_external_link_queue = False
        self._try_process_next_external_link() # Check queue again
    # --- END NEW Method ---

    # --- RENAMED and MODIFIED: Appends ONLY to external log ---
    def _append_to_external_log(self, formatted_link_text, separator):
        """Appends a single formatted link to the external_log_output widget."""
        # Visibility check is done before calling this now
        if not (self.external_log_output and self.external_log_output.isVisible()):
            return

        try:
            self.external_log_output.append(separator)
            self.external_log_output.append(formatted_link_text)
            self.external_log_output.append("") # Add a blank line for spacing

            # Auto-scroll
            scrollbar = self.external_log_output.verticalScrollBar()
            if scrollbar.value() >= scrollbar.maximum() - 50: # Adjust threshold if needed
                scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
             # Log errors related to external log to the main log
             self.log_signal.emit(f"GUI External Log Append Error: {e}\nOriginal Message: {formatted_link_text}")
             print(f"GUI External Log Error (Append): {e}\nOriginal Message: {formatted_link_text}")
    # --- END MODIFIED ---


    def update_file_progress_display(self, filename, downloaded_bytes, total_bytes):
        if not filename and total_bytes == 0 and downloaded_bytes == 0: # Clear signal
            self.file_progress_label.setText("")
            return

        # MODIFIED: Truncate filename more aggressively (e.g., max 25 chars)
        max_filename_len = 25
        display_filename = filename[:max_filename_len-3].strip() + "..." if len(filename) > max_filename_len else filename

        if total_bytes > 0:
            downloaded_mb = downloaded_bytes / (1024 * 1024)
            total_mb = total_bytes / (1024 * 1024)
            progress_text = f"Downloading '{display_filename}' ({downloaded_mb:.1f}MB / {total_mb:.1f}MB)"
        else: # If total size is unknown
             downloaded_mb = downloaded_bytes / (1024 * 1024)
             progress_text = f"Downloading '{display_filename}' ({downloaded_mb:.1f}MB)"

        # Check if the resulting text might still be too long (heuristic)
        # This is a basic check, might need refinement based on typical log width
        if len(progress_text) > 75: # Example threshold, adjust as needed
             # If still too long, truncate the display_filename even more
             display_filename = filename[:15].strip() + "..." if len(filename) > 18 else display_filename
             if total_bytes > 0:
                 progress_text = f"DL '{display_filename}' ({downloaded_mb:.1f}/{total_mb:.1f}MB)"
             else:
                 progress_text = f"DL '{display_filename}' ({downloaded_mb:.1f}MB)"

        self.file_progress_label.setText(progress_text)


    def update_external_links_setting(self, checked):
        # This function is now primarily controlled by _handle_filter_mode_change
        # when the "Only Links" mode is NOT selected.
        is_only_links_mode = self.radio_only_links and self.radio_only_links.isChecked()
        if is_only_links_mode:
            # In "Only Links" mode, the external log is always hidden.
             if self.external_log_output: self.external_log_output.hide()
             if self.log_splitter: self.log_splitter.setSizes([self.height(), 0])
             return

        # Proceed only if NOT in "Only Links" mode
        self.show_external_links = checked
        if checked:
            if self.external_log_output: self.external_log_output.show()
            # Adjust splitter, give both logs some space
            if self.log_splitter: self.log_splitter.setSizes([self.height() // 2, self.height() // 2])
            if self.main_log_output: self.main_log_output.setMinimumHeight(50) # Ensure it doesn't disappear
            if self.external_log_output: self.external_log_output.setMinimumHeight(50)
            self.log_signal.emit("\n" + "="*40 + "\n🔗 External Links Log Enabled\n" + "="*40)
            if self.external_log_output:
                self.external_log_output.clear() # Clear previous content
                self.external_log_output.append("🔗 External Links Found:") # Header
            # Try processing queue if log becomes visible
            self._try_process_next_external_link()
        else:
            if self.external_log_output: self.external_log_output.hide()
            # Adjust splitter
            if self.log_splitter: self.log_splitter.setSizes([self.height(), 0]) # Main log takes all space
            if self.main_log_output: self.main_log_output.setMinimumHeight(0) # Reset min height
            if self.external_log_output: self.external_log_output.setMinimumHeight(0)
            if self.external_log_output: self.external_log_output.clear() # Clear content when hidden
            self.log_signal.emit("\n" + "="*40 + "\n🔗 External Links Log Disabled\n" + "="*40)

    # --- ADDED: Handler for filter mode radio buttons ---
    def _handle_filter_mode_change(self, button, checked):
        # button can be None during initial setup sometimes
        if not button or not checked:
            return

        filter_mode_text = button.text()
        is_only_links = (filter_mode_text == "🔗 Only Links")

        # --- MODIFIED: Enable/disable widgets based on mode ---
        file_options_enabled = not is_only_links
        widgets_to_disable_in_links_mode = [
            self.dir_input, self.dir_button, # Download Location
            self.skip_zip_checkbox, self.skip_rar_checkbox,
            self.download_thumbnails_checkbox, self.compress_images_checkbox,
            self.use_subfolders_checkbox, self.use_subfolder_per_post_checkbox,
            self.character_filter_widget, # Includes label and input
            self.skip_words_input,
            self.custom_folder_widget # Includes label and input
        ]
        # --- END MODIFIED ---
        for widget in widgets_to_disable_in_links_mode:
            if widget: widget.setEnabled(file_options_enabled)

        # --- ADDED: Show/hide link search bar and export button ---
        if self.link_search_input: self.link_search_input.setVisible(is_only_links)
        if self.link_search_button: self.link_search_button.setVisible(is_only_links)
        if self.export_links_button:
            self.export_links_button.setVisible(is_only_links)
            self.export_links_button.setEnabled(is_only_links and bool(self.extracted_links_cache)) # Enable if cache has items
        if not is_only_links and self.link_search_input: self.link_search_input.clear() # Clear search when hiding
        # --- END ADDED ---

        # Specific handling for "Only Links" mode vs others
        if is_only_links:
            self.progress_log_label.setText("📜 Extracted Links Log:") # Change title
            # Ensure external log is hidden and main log takes full vertical space
            if self.external_log_output: self.external_log_output.hide()
            if self.log_splitter: self.log_splitter.setSizes([self.height(), 0])
            if self.main_log_output: self.main_log_output.setMinimumHeight(0)
            if self.external_log_output: self.external_log_output.setMinimumHeight(0)
            # Clear logs for the new mode
            if self.main_log_output: self.main_log_output.clear()
            if self.external_log_output: self.external_log_output.clear()
            # External links checkbox is irrelevant in this mode, keep it enabled but ignored
            if self.external_links_checkbox: self.external_links_checkbox.setEnabled(True)
            self.log_signal.emit("="*20 + " Mode changed to: Only Links " + "="*20)
            # Start processing links immediately for the main log display
            self._filter_links_log() # Display initially filtered (all) links
            self._try_process_next_external_link() # Start paced display

        else: # Other modes (All, Images, Videos)
            self.progress_log_label.setText("📜 Progress Log:") # Restore title
            if self.external_links_checkbox:
                self.external_links_checkbox.setEnabled(True) # Ensure checkbox is enabled
            # Restore log visibility based on checkbox state
            self.update_external_links_setting(self.external_links_checkbox.isChecked())
            # Re-enable potentially disabled subfolder options if needed
            self.update_ui_for_subfolders(self.use_subfolders_checkbox.isChecked())
            self.log_signal.emit(f"="*20 + f" Mode changed to: {filter_mode_text} " + "="*20)

    # --- END ADDED ---

    # --- ADDED: Method to filter links in "Only Links" mode ---
    def _filter_links_log(self):
        """Filters and displays links from the cache in the main log."""
        if not (self.radio_only_links and self.radio_only_links.isChecked()):
            return # Only filter when in "Only Links" mode

        search_term = self.link_search_input.text().lower().strip()
        self.main_log_output.clear() # Clear current display

        current_title_for_display = None # Track title for grouping in this filtered view
        separator = "-" * 45

        for post_title, link_text, link_url, platform in self.extracted_links_cache:
            # Check if the search term matches any part of the link info
            matches_search = (
                not search_term or
                search_term in link_text.lower() or
                search_term in link_url.lower() or
                search_term in platform.lower()
            )

            if matches_search:
                # Check if the post title has changed
                if post_title != current_title_for_display:
                    # Append separator and new title (formatted as HTML)
                    self.main_log_output.insertHtml("<br>" + separator + "<br>")
                    title_html = f'<b style="color: #87CEEB;">{post_title}</b><br>'
                    self.main_log_output.insertHtml(title_html)
                    current_title_for_display = post_title # Update current title

                # Format and append the link info as plain text
                max_link_text_len = 35
                display_text = link_text[:max_link_text_len].strip() + "..." if len(link_text) > max_link_text_len else link_text
                formatted_link_info = f"{display_text} - {link_url} - {platform}"
                self.main_log_output.append(formatted_link_info)

        # Add a final blank line if any links were displayed
        if self.main_log_output.toPlainText().strip():
             self.main_log_output.append("")

        # Scroll to top after filtering
        self.main_log_output.verticalScrollBar().setValue(0)
    # --- END ADDED ---

    # --- ADDED: Method to export links ---
    def _export_links_to_file(self):
        if not (self.radio_only_links and self.radio_only_links.isChecked()):
            QMessageBox.information(self, "Export Links", "Link export is only available in 'Only Links' mode.")
            return
        if not self.extracted_links_cache:
            QMessageBox.information(self, "Export Links", "No links have been extracted yet.")
            return

        default_filename = "extracted_links.txt"
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Links", default_filename, "Text Files (*.txt);;All Files (*)")

        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    current_title_for_export = None
                    separator = "-" * 60 + "\n" # For file output

                    for post_title, link_text, link_url, platform in self.extracted_links_cache:
                        if post_title != current_title_for_export:
                            if current_title_for_export is not None: # Add separator before new title, except for the first one
                                f.write("\n" + separator + "\n")
                            f.write(f"Post Title: {post_title}\n\n")
                            current_title_for_export = post_title

                        f.write(f"  {link_text} - {link_url} - {platform}\n")

                self.log_signal.emit(f"✅ Links successfully exported to: {filepath}")
                QMessageBox.information(self, "Export Successful", f"Links exported to:\n{filepath}")
            except Exception as e:
                self.log_signal.emit(f"❌ Error exporting links: {e}")
                QMessageBox.critical(self, "Export Error", f"Could not export links: {e}")
    # --- END ADDED ---


    def get_filter_mode(self):
        # This method returns the simplified filter mode string for the backend
        if self.radio_only_links and self.radio_only_links.isChecked():
             # When "Only Links" is checked, the backend doesn't filter by file type,
             # but it does need a 'filter_mode'. 'all' is a safe default.
             # The actual link extraction is controlled by the 'extract_links_only' flag.
             return 'all'
        elif self.radio_images.isChecked(): return 'image'
        elif self.radio_videos.isChecked(): return 'video'
        return 'all' # Default for "All" radio or if somehow no radio is checked.

    def add_new_character(self):
        global KNOWN_NAMES, clean_folder_name # Ensure clean_folder_name is accessible
        name_to_add = self.new_char_input.text().strip()
        if not name_to_add:
             QMessageBox.warning(self, "Input Error", "Name cannot be empty.")
             return False # Indicate failure

        name_lower = name_to_add.lower()

        # 1. Exact Duplicate Check (case-insensitive)
        is_exact_duplicate = any(existing.lower() == name_lower for existing in KNOWN_NAMES)
        if is_exact_duplicate:
             QMessageBox.warning(self, "Duplicate Name", f"The name '{name_to_add}' (case-insensitive) already exists.")
             return False

        # 2. Similarity Check (substring, case-insensitive)
        similar_names_details = [] # Store tuples of (new_name, existing_name)
        for existing_name in KNOWN_NAMES:
            existing_name_lower = existing_name.lower()
            # Avoid self-comparison if somehow name_lower was already in a different case
            if name_lower != existing_name_lower:
                if name_lower in existing_name_lower or existing_name_lower in name_lower:
                    similar_names_details.append((name_to_add, existing_name))

        if similar_names_details:
            first_similar_new, first_similar_existing = similar_names_details[0]

            # Determine shorter and longer for the example message
            shorter_name_for_msg, longer_name_for_msg = sorted(
                [first_similar_new, first_similar_existing], key=len
            )

            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Potential Name Conflict")
            msg_box.setText(
                f"The name '{first_similar_new}' is very similar to an existing name: '{first_similar_existing}'.\n\n"
                f"For example, if a post title primarily matches the shorter name ('{shorter_name_for_msg}'), "
                f"files might be saved under a folder for '{clean_folder_name(shorter_name_for_msg)}', "
                f"even if the longer name ('{longer_name_for_msg}') was also relevant or intended for a more specific folder.\n"
                "This could lead to files being grouped into less specific or overly broad folders than desired.\n\n"
                "Do you want to change the name you are adding, or proceed anyway?"
            )
            change_button = msg_box.addButton("Change Name", QMessageBox.RejectRole)
            proceed_button = msg_box.addButton("Proceed Anyway", QMessageBox.AcceptRole)
            msg_box.setDefaultButton(proceed_button) # Default to proceed
            msg_box.setEscapeButton(change_button)   # Escape cancels/rejects

            msg_box.exec_()

            if msg_box.clickedButton() == change_button:
                self.log_signal.emit(f"ℹ️ User chose to change the name '{first_similar_new}' due to similarity with '{first_similar_existing}'.")
                return False # Don't add, user will change input and click "Add" again
            # If proceed_button is clicked (or dialog is closed and proceed is default)
            self.log_signal.emit(f"⚠️ User chose to proceed with adding '{first_similar_new}' despite similarity with '{first_similar_existing}'.")
            # Fall through to add the name

        # If no exact duplicate, and (no similar names OR user chose to proceed with similar name)
        KNOWN_NAMES.append(name_to_add)
        KNOWN_NAMES.sort(key=str.lower) # Keep the list sorted (case-insensitive for sorting)
        self.character_list.clear()
        self.character_list.addItems(KNOWN_NAMES)
        self.filter_character_list(self.character_search_input.text()) # Re-apply filter
        self.log_signal.emit(f"✅ Added '{name_to_add}' to known names list.")
        self.new_char_input.clear()
        self.save_known_names() # Save to file
        return True # Indicate success


    def delete_selected_character(self):
        global KNOWN_NAMES
        selected_items = self.character_list.selectedItems()
        if not selected_items:
             QMessageBox.warning(self, "Selection Error", "Please select one or more names to delete.")
             return

        names_to_remove = {item.text() for item in selected_items}
        confirm = QMessageBox.question(self, "Confirm Deletion",
                                       f"Are you sure you want to delete {len(names_to_remove)} name(s)?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirm == QMessageBox.Yes:
            original_count = len(KNOWN_NAMES)
            # Filter out names to remove
            KNOWN_NAMES = [n for n in KNOWN_NAMES if n not in names_to_remove]
            removed_count = original_count - len(KNOWN_NAMES)

            if removed_count > 0:
                 self.log_signal.emit(f"🗑️ Removed {removed_count} name(s).")
                 self.character_list.clear() # Update UI
                 self.character_list.addItems(KNOWN_NAMES)
                 self.filter_character_list(self.character_search_input.text()) # Re-apply filter
                 self.save_known_names() # Save changes
            else:
                 self.log_signal.emit("ℹ️ No names were removed (they might not have been in the list or already deleted).")


    def update_custom_folder_visibility(self, url_text=None):
        if url_text is None: url_text = self.link_input.text() # Get current text if not passed
        _, _, post_id = extract_post_info(url_text.strip())
        # Show if it's a post URL AND subfolders are generally enabled
        should_show = bool(post_id) and self.use_subfolders_checkbox.isChecked()
        # --- MODIFIED: Also hide if in "Only Links" mode ---
        is_only_links = self.radio_only_links and self.radio_only_links.isChecked()
        self.custom_folder_widget.setVisible(should_show and not is_only_links)
        # --- END MODIFIED ---
        if not self.custom_folder_widget.isVisible(): self.custom_folder_input.clear() # Clear if hidden

    def update_ui_for_subfolders(self, checked):
        # Character filter input visibility depends on subfolder usage
        is_only_links = self.radio_only_links and self.radio_only_links.isChecked()
        self.character_filter_widget.setVisible(checked and not is_only_links) # Hide if only links
        if not checked: self.character_input.clear() # Clear filter if hiding

        self.update_custom_folder_visibility() # Custom folder also depends on this

        # "Subfolder per Post" is only enabled if "Separate Folders" is also checked
        self.use_subfolder_per_post_checkbox.setEnabled(checked and not is_only_links) # Disable if only links
        if not checked or is_only_links: self.use_subfolder_per_post_checkbox.setChecked(False) # Uncheck if parent is disabled or only links

    def update_page_range_enabled_state(self):
        url_text = self.link_input.text().strip()
        service, user_id, post_id = extract_post_info(url_text)
        # Page range is for creator feeds (no post_id)
        is_creator_feed = service is not None and user_id is not None and post_id is None

        manga_mode_active = self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False
        # Enable page range if it's a creator feed AND manga mode is NOT active
        enable_page_range = is_creator_feed and not manga_mode_active

        for widget in [self.page_range_label, self.start_page_input, self.to_label, self.end_page_input]:
            if widget: widget.setEnabled(enable_page_range)
        if not enable_page_range: # Clear inputs if disabled
            self.start_page_input.clear()
            self.end_page_input.clear()

    def update_ui_for_manga_mode(self, checked):
        url_text = self.link_input.text().strip()
        _, _, post_id = extract_post_info(url_text)
        is_creator_feed = not post_id if url_text else False # Manga mode only for creator feeds

        if self.manga_mode_checkbox: # Ensure checkbox exists
            self.manga_mode_checkbox.setEnabled(is_creator_feed) # Only enable for creator feeds
            if not is_creator_feed and self.manga_mode_checkbox.isChecked():
                self.manga_mode_checkbox.setChecked(False) # Uncheck if URL changes to non-creator feed

        # If manga mode is active (checked and enabled), disable page range
        if is_creator_feed and self.manga_mode_checkbox and self.manga_mode_checkbox.isChecked():
            self.page_range_label.setEnabled(False)
            self.start_page_input.setEnabled(False); self.start_page_input.clear()
            self.to_label.setEnabled(False)
            self.end_page_input.setEnabled(False); self.end_page_input.clear()
        else: # Otherwise, let update_page_range_enabled_state handle it
            self.update_page_range_enabled_state()


    def filter_character_list(self, search_text):
        search_text_lower = search_text.lower()
        for i in range(self.character_list.count()):
            item = self.character_list.item(i)
            item.setHidden(search_text_lower not in item.text().lower())

    def update_multithreading_label(self, text):
        # This method only updates the checkbox label text
        # The actual enabling/disabling is handled by _handle_multithreading_toggle
        if self.use_multithreading_checkbox.isChecked():
            try:
                num_threads = int(text)
                if num_threads > 0 :
                    self.use_multithreading_checkbox.setText(f"Use Multithreading ({num_threads} Threads)")
                else:
                    self.use_multithreading_checkbox.setText("Use Multithreading (Invalid: >0)")
            except ValueError:
                self.use_multithreading_checkbox.setText("Use Multithreading (Invalid Input)")
        else:
             self.use_multithreading_checkbox.setText("Use Multithreading (1 Thread)") # Show 1 thread when disabled

    # --- ADDED: Handler for multithreading checkbox toggle ---
    def _handle_multithreading_toggle(self, checked):
        """Handles enabling/disabling the thread count input."""
        if not checked:
            # Unchecked: Set to 1 and disable
            self.thread_count_input.setText("1")
            self.thread_count_input.setEnabled(False)
            self.thread_count_label.setEnabled(False)
            self.use_multithreading_checkbox.setText("Use Multithreading (1 Thread)")
        else:
            # Checked: Enable and update label based on current value
            self.thread_count_input.setEnabled(True)
            self.thread_count_label.setEnabled(True)
            self.update_multithreading_label(self.thread_count_input.text())
    # --- END ADDED ---


    def update_progress_display(self, total_posts, processed_posts):
        if total_posts > 0:
            progress_percent = (processed_posts / total_posts) * 100
            self.progress_label.setText(f"Progress: {processed_posts} / {total_posts} posts ({progress_percent:.1f}%)")
        elif processed_posts > 0 : # If total_posts is unknown (e.g., single post)
             self.progress_label.setText(f"Progress: Processing post {processed_posts}...")
        else: # Initial state or no posts
            self.progress_label.setText("Progress: Starting...")

        if total_posts > 0 or processed_posts > 0 : self.file_progress_label.setText("") # Clear file progress


    def start_download(self):
        global KNOWN_NAMES, BackendDownloadThread, PostProcessorWorker, extract_post_info, clean_folder_name

        if (self.download_thread and self.download_thread.isRunning()) or self.thread_pool:
            QMessageBox.warning(self, "Busy", "A download is already running.")
            return

        api_url = self.link_input.text().strip()
        output_dir = self.dir_input.text().strip()
        skip_zip = self.skip_zip_checkbox.isChecked()
        skip_rar = self.skip_rar_checkbox.isChecked()
        use_subfolders = self.use_subfolders_checkbox.isChecked()
        use_post_subfolders = self.use_subfolder_per_post_checkbox.isChecked() and use_subfolders
        compress_images = self.compress_images_checkbox.isChecked()
        download_thumbnails = self.download_thumbnails_checkbox.isChecked()
        use_multithreading = self.use_multithreading_checkbox.isChecked()
        raw_skip_words = self.skip_words_input.text().strip()
        skip_words_list = [word.strip().lower() for word in raw_skip_words.split(',') if word.strip()]

        manga_mode_is_checked = self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False

        extract_links_only = (self.radio_only_links and self.radio_only_links.isChecked())

        # --- MODIFICATION FOR FILTER MODE ---
        # Get the simplified filter mode for the backend (e.g., 'image', 'video', 'all')
        backend_filter_mode = self.get_filter_mode()
        # Get the user-facing text of the selected radio button for logging purposes
        user_selected_filter_text = self.radio_group.checkedButton().text() if self.radio_group.checkedButton() else "All"
        # --- END MODIFICATION FOR FILTER MODE ---


        if not api_url:
            QMessageBox.critical(self, "Input Error", "URL is required."); return
        if not extract_links_only and not output_dir:
             QMessageBox.critical(self, "Input Error", "Download Directory is required when not in 'Only Links' mode."); return

        service, user_id, post_id_from_url = extract_post_info(api_url)
        if not service or not user_id:
            QMessageBox.critical(self, "Input Error", "Invalid or unsupported URL format."); return

        if not extract_links_only and not os.path.isdir(output_dir):
            reply = QMessageBox.question(self, "Create Directory?",
                                         f"The directory '{output_dir}' does not exist.\nCreate it now?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    self.log_signal.emit(f"ℹ️ Created directory: {output_dir}")
                except Exception as e:
                    QMessageBox.critical(self, "Directory Error", f"Could not create directory: {e}"); return
            else:
                self.log_signal.emit("❌ Download cancelled: Output directory does not exist and was not created.")
                return

        if compress_images and Image is None:
            QMessageBox.warning(self, "Missing Dependency", "Pillow library (for image compression) not found. Compression will be disabled.")
            compress_images = False
            self.compress_images_checkbox.setChecked(False)

        manga_mode = manga_mode_is_checked and not post_id_from_url

        num_threads_str = self.thread_count_input.text().strip()
        num_threads = 1
        if use_multithreading:
            try:
                num_threads_requested = int(num_threads_str)
                if num_threads_requested > MAX_THREADS:
                    warning_message = (
                        f"You have requested {num_threads_requested} threads, which is above the maximum limit of {MAX_THREADS}.\n\n"
                        f"High thread counts can lead to instability or rate-limiting.\n\n"
                        f"The thread count will be automatically capped at {MAX_THREADS} for this download."
                    )
                    QMessageBox.warning(self, "High Thread Count Warning", warning_message)
                    self.log_signal.emit(f"⚠️ High thread count requested ({num_threads_requested}). Capping at {MAX_THREADS}.")
                    num_threads = MAX_THREADS
                    self.thread_count_input.setText(str(num_threads))
                elif num_threads_requested > RECOMMENDED_MAX_THREADS:
                     QMessageBox.information(self, "High Thread Count Note",
                                            f"Using {num_threads_requested} threads (above {RECOMMENDED_MAX_THREADS}) may increase resource usage and risk rate-limiting from the site.\n\nProceeding with caution.")
                     self.log_signal.emit(f"ℹ️ Using high thread count: {num_threads_requested}.")
                     num_threads = num_threads_requested
                elif num_threads_requested < 1:
                    self.log_signal.emit(f"⚠️ Invalid thread count ({num_threads_requested}). Using 1 thread.")
                    num_threads = 1
                    self.thread_count_input.setText(str(num_threads))
                else:
                    num_threads = num_threads_requested
            except ValueError:
                QMessageBox.critical(self, "Thread Count Error", "Invalid number of threads. Please enter a numeric value."); return
        else:
            num_threads = 1


        start_page_str, end_page_str = self.start_page_input.text().strip(), self.end_page_input.text().strip()
        start_page, end_page = None, None
        is_creator_feed = bool(not post_id_from_url)

        if is_creator_feed and not manga_mode:
            try:
                if start_page_str: start_page = int(start_page_str)
                if end_page_str: end_page = int(end_page_str)
                if start_page is not None and start_page <= 0: raise ValueError("Start page must be positive.")
                if end_page is not None and end_page <= 0: raise ValueError("End page must be positive.")
                if start_page and end_page and start_page > end_page:
                    raise ValueError("Start page cannot be greater than end page.")
            except ValueError as e:
                QMessageBox.critical(self, "Page Range Error", f"Invalid page range: {e}"); return
        elif manga_mode:
            start_page, end_page = None, None

        self.external_link_queue.clear()
        self.extracted_links_cache = []
        self._is_processing_external_link_queue = False
        self._current_link_post_title = None


        raw_character_filters_text = self.character_input.text().strip()
        parsed_character_list = None
        if raw_character_filters_text:
            temp_list = [name.strip() for name in raw_character_filters_text.split(',') if name.strip()]
            if temp_list: parsed_character_list = temp_list

        filter_character_list_to_pass = None
        if use_subfolders and parsed_character_list and not post_id_from_url and not extract_links_only:
            self.log_signal.emit(f"ℹ️ Validating character filters for subfolder naming: {', '.join(parsed_character_list)}")
            valid_filters_for_backend = []
            user_cancelled_validation = False
            for char_name in parsed_character_list:
                cleaned_name_test = clean_folder_name(char_name)
                if not cleaned_name_test:
                    QMessageBox.warning(self, "Invalid Filter Name", f"Filter name '{char_name}' is invalid for a folder and will be skipped.")
                    self.log_signal.emit(f"⚠️ Skipping invalid filter for folder: '{char_name}'")
                    continue

                if char_name.lower() not in {kn.lower() for kn in KNOWN_NAMES}:
                    reply = QMessageBox.question(self, "Add Filter Name to Known List?",
                                                 f"The character filter '{char_name}' is not in your known names list (used for folder suggestions).\nAdd it now?",
                                                 QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
                    if reply == QMessageBox.Yes:
                        self.new_char_input.setText(char_name)
                        if self.add_new_character():
                            self.log_signal.emit(f"✅ Added '{char_name}' to known names via filter prompt.")
                            valid_filters_for_backend.append(char_name)
                        else:
                             self.log_signal.emit(f"⚠️ Failed to add '{char_name}' via filter prompt (or user opted out). It will still be used for filtering this session if valid.")
                             if cleaned_name_test: valid_filters_for_backend.append(char_name)
                    elif reply == QMessageBox.Cancel:
                        self.log_signal.emit(f"❌ Download cancelled by user during filter validation for '{char_name}'.")
                        user_cancelled_validation = True; break
                    else:
                        self.log_signal.emit(f"ℹ️ Proceeding with filter '{char_name}' for matching without adding to known list.")
                        if cleaned_name_test: valid_filters_for_backend.append(char_name)
                else:
                    if cleaned_name_test: valid_filters_for_backend.append(char_name)

            if user_cancelled_validation: return

            if valid_filters_for_backend:
                filter_character_list_to_pass = valid_filters_for_backend
                self.log_signal.emit(f"   Using validated character filters for subfolders: {', '.join(filter_character_list_to_pass)}")
            else:
                self.log_signal.emit("⚠️ No valid character filters remaining after validation for subfolder naming.")
        elif parsed_character_list :
            filter_character_list_to_pass = parsed_character_list
            self.log_signal.emit(f"ℹ️ Character filters provided: {', '.join(filter_character_list_to_pass)} (Subfolder creation rules may differ).")

        if manga_mode and not filter_character_list_to_pass and not extract_links_only:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Manga Mode Filter Warning")
            msg_box.setText(
                "Manga Mode is enabled, but the 'Filter by Character(s)' field is empty.\n\n"
                "For best results (correct file naming and grouping), please enter the exact Manga/Series title "
                "(as used by the creator on the site) into the filter field.\n\n"
                "Do you want to proceed without a filter (file names might be generic) or cancel?"
            )
            proceed_button = msg_box.addButton("Proceed Anyway", QMessageBox.AcceptRole)
            cancel_button = msg_box.addButton("Cancel Download", QMessageBox.RejectRole)

            msg_box.exec_()

            if msg_box.clickedButton() == cancel_button:
                self.log_signal.emit("❌ Download cancelled by user due to Manga Mode filter warning.")
                return
            else:
                self.log_signal.emit("⚠️ Proceeding with Manga Mode without a specific title filter.")


        custom_folder_name_cleaned = None
        if use_subfolders and post_id_from_url and self.custom_folder_widget.isVisible() and not extract_links_only:
            raw_custom_name = self.custom_folder_input.text().strip()
            if raw_custom_name:
                 cleaned_custom = clean_folder_name(raw_custom_name)
                 if cleaned_custom: custom_folder_name_cleaned = cleaned_custom
                 else: self.log_signal.emit(f"⚠️ Invalid custom folder name ignored: '{raw_custom_name}'")

        self.main_log_output.clear()
        if extract_links_only:
            self.main_log_output.append("🔗 Extracting Links...")
            if self.external_log_output: self.external_log_output.clear()
        elif self.show_external_links:
            self.external_log_output.clear()
            self.external_log_output.append("🔗 External Links Found:")
        self.file_progress_label.setText("")
        self.cancellation_event.clear()
        self.active_futures = []
        self.total_posts_to_process = self.processed_posts_count = self.download_counter = self.skip_counter = 0
        self.progress_label.setText("Progress: Initializing...")

        log_messages = [
            "="*40, f"🚀 Starting {'Link Extraction' if extract_links_only else 'Download'} @ {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"   URL: {api_url}",
        ]
        if not extract_links_only:
            log_messages.append(f"   Save Location: {output_dir}")

        log_messages.append(f"   Mode: {'Single Post' if post_id_from_url else 'Creator Feed'}")

        if is_creator_feed:
            if manga_mode:
                log_messages.append("   Page Range: All (Manga Mode - Oldest Posts Processed First)")
            else:
                pr_log = "All"
                if start_page or end_page:
                    pr_log = f"{f'From {start_page} ' if start_page else ''}{'to ' if start_page and end_page else ''}{f'{end_page}' if end_page else (f'Up to {end_page}' if end_page else (f'From {start_page}' if start_page else 'Specific Range'))}".strip()
                log_messages.append(f"   Page Range: {pr_log if pr_log else 'All'}")

        if not extract_links_only:
            log_messages.append(f"   Subfolders: {'Enabled' if use_subfolders else 'Disabled'}")
            if use_subfolders:
                 if custom_folder_name_cleaned: log_messages.append(f"   Custom Folder (Post): '{custom_folder_name_cleaned}'")
                 elif filter_character_list_to_pass and not post_id_from_url: log_messages.append(f"   Character Filters for Folders: {', '.join(filter_character_list_to_pass)}")
                 else: log_messages.append(f"   Folder Naming: Automatic (based on title/known names)")
                 log_messages.append(f"   Subfolder per Post: {'Enabled' if use_post_subfolders else 'Disabled'}")

            log_messages.extend([
                # --- MODIFIED LOGGING FOR FILTER MODE ---
                f"   File Type Filter: {user_selected_filter_text} (Backend processing as: {backend_filter_mode})",
                # --- END MODIFIED LOGGING ---
                f"   Skip Archives: {'.zip' if skip_zip else ''}{', ' if skip_zip and skip_rar else ''}{'.rar' if skip_rar else ''}{'None' if not (skip_zip or skip_rar) else ''}",
                f"   Skip Words (posts/files): {', '.join(skip_words_list) if skip_words_list else 'None'}",
                f"   Compress Images: {'Enabled' if compress_images else 'Disabled'}",
                f"   Thumbnails Only: {'Enabled' if download_thumbnails else 'Disabled'}",
            ])
        else:
             log_messages.append(f"   Mode: Extracting Links Only") # This handles the "Only Links" case

        log_messages.append(f"   Show External Links: {'Enabled' if self.show_external_links else 'Disabled'}")
        if manga_mode: log_messages.append(f"   Manga Mode (File Renaming by Post Title): Enabled")

        should_use_multithreading = use_multithreading and not post_id_from_url
        log_messages.append(f"   Threading: {'Multi-threaded (posts)' if should_use_multithreading else 'Single-threaded (posts)'}")
        if should_use_multithreading: log_messages.append(f"   Number of Post Worker Threads: {num_threads}")
        log_messages.append("="*40)
        for msg in log_messages: self.log_signal.emit(msg)

        self.set_ui_enabled(False)

        unwanted_keywords_for_folders = {'spicy', 'hd', 'nsfw', '4k', 'preview', 'teaser', 'clip'}

        args_template = {
            'api_url_input': api_url,
            'download_root': output_dir,
            'output_dir': output_dir,
            'known_names': list(KNOWN_NAMES),
            'known_names_copy': list(KNOWN_NAMES),
            'filter_character_list': filter_character_list_to_pass,
            # --- MODIFIED: Pass the correct backend_filter_mode ---
            'filter_mode': backend_filter_mode,
            # --- END MODIFICATION ---
            'skip_zip': skip_zip, 'skip_rar': skip_rar,
            'use_subfolders': use_subfolders, 'use_post_subfolders': use_post_subfolders,
            'compress_images': compress_images, 'download_thumbnails': download_thumbnails,
            'service': service, 'user_id': user_id,
            'downloaded_files': self.downloaded_files,
            'downloaded_files_lock': self.downloaded_files_lock,
            'downloaded_file_hashes': self.downloaded_file_hashes,
            'downloaded_file_hashes_lock': self.downloaded_file_hashes_lock,
            'skip_words_list': skip_words_list,
            'show_external_links': self.show_external_links,
            'extract_links_only': extract_links_only,
            'start_page': start_page,
            'end_page': end_page,
            'target_post_id_from_initial_url': post_id_from_url,
            'custom_folder_name': custom_folder_name_cleaned,
            'manga_mode_active': manga_mode,
            'unwanted_keywords': unwanted_keywords_for_folders,
            'cancellation_event': self.cancellation_event,
            'signals': self.worker_signals,
        }


        try:
            if should_use_multithreading:
                self.log_signal.emit(f"   Initializing multi-threaded {'link extraction' if extract_links_only else 'download'} with {num_threads} post workers...")
                self.start_multi_threaded_download(num_post_workers=num_threads, **args_template)
            else:
                self.log_signal.emit(f"   Initializing single-threaded {'link extraction' if extract_links_only else 'download'}...")
                dt_expected_keys = [
                    'api_url_input', 'output_dir', 'known_names_copy', 'cancellation_event',
                    'filter_character_list', 'filter_mode', 'skip_zip', 'skip_rar',
                    'use_subfolders', 'use_post_subfolders', 'custom_folder_name',
                    'compress_images', 'download_thumbnails', 'service', 'user_id',
                    'downloaded_files', 'downloaded_file_hashes', 'downloaded_files_lock',
                    'downloaded_file_hashes_lock', 'skip_words_list', 'show_external_links',
                    'extract_links_only',
                    'num_file_threads_for_worker', 'skip_current_file_flag',
                    'start_page', 'end_page', 'target_post_id_from_initial_url',
                    'manga_mode_active', 'unwanted_keywords'
                ]
                args_template['num_file_threads_for_worker'] = 1
                args_template['skip_current_file_flag'] = None

                single_thread_args = {}
                for key in dt_expected_keys:
                     if key in args_template:
                         single_thread_args[key] = args_template[key]

                self.start_single_threaded_download(**single_thread_args)

        except Exception as e:
            self.log_signal.emit(f"❌ CRITICAL ERROR preparing {'link extraction' if extract_links_only else 'download'}: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Start Error", f"Failed to start process:\n{e}")
            self.download_finished(0,0,False)


    def start_single_threaded_download(self, **kwargs):
        global BackendDownloadThread
        try:
            self.download_thread = BackendDownloadThread(**kwargs)

            if hasattr(self.download_thread, 'progress_signal'):
                self.download_thread.progress_signal.connect(self.handle_main_log)
            if hasattr(self.download_thread, 'add_character_prompt_signal'):
                self.download_thread.add_character_prompt_signal.connect(self.add_character_prompt_signal)
            if hasattr(self.download_thread, 'finished_signal'):
                self.download_thread.finished_signal.connect(self.finished_signal)
            if hasattr(self.download_thread, 'receive_add_character_result'):
                self.character_prompt_response_signal.connect(self.download_thread.receive_add_character_result)
            if hasattr(self.download_thread, 'external_link_signal'):
                self.download_thread.external_link_signal.connect(self.handle_external_link_signal)
            if hasattr(self.download_thread, 'file_progress_signal'):
                self.download_thread.file_progress_signal.connect(self.update_file_progress_display)

            self.download_thread.start()
            self.log_signal.emit("✅ Single download thread (for posts) started.")
        except Exception as e:
            self.log_signal.emit(f"❌ CRITICAL ERROR starting single-thread: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Thread Start Error", f"Failed to start download process: {e}")
            self.download_finished(0,0,False)


    def start_multi_threaded_download(self, num_post_workers, **kwargs):
        global PostProcessorWorker
        self.thread_pool = ThreadPoolExecutor(max_workers=num_post_workers, thread_name_prefix='PostWorker_')
        self.active_futures = []
        self.processed_posts_count = 0
        self.total_posts_to_process = 0
        self.download_counter = 0
        self.skip_counter = 0

        fetcher_thread = threading.Thread(
            target=self._fetch_and_queue_posts,
            args=(kwargs['api_url_input'], kwargs, num_post_workers),
            daemon=True, name="PostFetcher"
        )
        fetcher_thread.start()
        self.log_signal.emit(f"✅ Post fetcher thread started. {num_post_workers} post worker threads initializing...")


    def _fetch_and_queue_posts(self, api_url_input_for_fetcher, worker_args_template, num_post_workers):
        global PostProcessorWorker, download_from_api
        all_posts_data = []
        fetch_error_occurred = False

        manga_mode_active_for_fetch = worker_args_template.get('manga_mode_active', False)
        signals_for_worker = worker_args_template.get('signals')
        if not signals_for_worker:
             self.log_signal.emit("❌ CRITICAL ERROR: Signals object missing for worker in _fetch_and_queue_posts.")
             self.finished_signal.emit(0,0,True)
             return

        try:
            self.log_signal.emit("   Fetching post data from API...")
            post_generator = download_from_api(
                api_url_input_for_fetcher,
                logger=lambda msg: self.log_signal.emit(f"[Fetcher] {msg}"),
                start_page=worker_args_template.get('start_page'),
                end_page=worker_args_template.get('end_page'),
                manga_mode=manga_mode_active_for_fetch,
                cancellation_event=self.cancellation_event
            )
            for posts_batch in post_generator:
                if self.cancellation_event.is_set():
                    fetch_error_occurred = True; self.log_signal.emit("   Post fetching cancelled by user."); break
                if isinstance(posts_batch, list):
                    all_posts_data.extend(posts_batch)
                    self.total_posts_to_process = len(all_posts_data)
                    if self.total_posts_to_process > 0 and self.total_posts_to_process % 100 == 0 :
                        self.log_signal.emit(f"   Fetched {self.total_posts_to_process} posts so far...")
                else:
                    fetch_error_occurred = True
                    self.log_signal.emit(f"❌ API fetcher returned non-list type: {type(posts_batch)}"); break

            if not fetch_error_occurred and not self.cancellation_event.is_set():
                self.log_signal.emit(f"✅ Post fetching complete. Total posts to process: {self.total_posts_to_process}")
        except TypeError as te:
            self.log_signal.emit(f"❌ TypeError calling download_from_api: {te}")
            self.log_signal.emit("   Check if 'downloader_utils.py' has the correct 'download_from_api' signature (including 'manga_mode' and 'cancellation_event').")
            self.log_signal.emit(traceback.format_exc(limit=2))
            fetch_error_occurred = True
        except RuntimeError as re:
            self.log_signal.emit(f"ℹ️ Post fetching runtime error (likely cancellation): {re}")
            fetch_error_occurred = True
        except Exception as e:
            self.log_signal.emit(f"❌ Error during post fetching: {e}\n{traceback.format_exc(limit=2)}")
            fetch_error_occurred = True

        if self.cancellation_event.is_set() or fetch_error_occurred:
            self.finished_signal.emit(self.download_counter, self.skip_counter, self.cancellation_event.is_set())
            if self.thread_pool:
                self.thread_pool.shutdown(wait=False, cancel_futures=True); self.thread_pool = None
            return

        if self.total_posts_to_process == 0:
            self.log_signal.emit("😕 No posts found or fetched to process.")
            self.finished_signal.emit(0,0,False); return

        self.log_signal.emit(f"   Submitting {self.total_posts_to_process} post processing tasks to thread pool...")
        self.processed_posts_count = 0
        self.overall_progress_signal.emit(self.total_posts_to_process, 0)

        num_file_dl_threads = 4

        ppw_expected_keys = [
            'post_data', 'download_root', 'known_names', 'filter_character_list',
            'unwanted_keywords', 'filter_mode', 'skip_zip', 'skip_rar',
            'use_subfolders', 'use_post_subfolders', 'target_post_id_from_initial_url',
            'custom_folder_name', 'compress_images', 'download_thumbnails', 'service',
            'user_id', 'api_url_input', 'cancellation_event', 'signals',
            'downloaded_files', 'downloaded_file_hashes', 'downloaded_files_lock',
            'downloaded_file_hashes_lock', 'skip_words_list', 'show_external_links',
            'extract_links_only', 'num_file_threads', 'skip_current_file_flag',
            'manga_mode_active'
        ]
        ppw_optional_keys_with_defaults = {
            'skip_words_list', 'show_external_links', 'extract_links_only',
            'num_file_threads', 'skip_current_file_flag', 'manga_mode_active'
        }


        for post_data_item in all_posts_data:
            if self.cancellation_event.is_set(): break
            if not isinstance(post_data_item, dict):
                self.log_signal.emit(f"⚠️ Skipping invalid post data item (not a dict): {type(post_data_item)}")
                self.processed_posts_count += 1
                continue

            worker_init_args = {}
            missing_keys = []
            for key in ppw_expected_keys:
                if key == 'post_data': worker_init_args[key] = post_data_item
                elif key == 'num_file_threads': worker_init_args[key] = num_file_dl_threads
                elif key == 'signals': worker_init_args[key] = signals_for_worker
                elif key in worker_args_template: worker_init_args[key] = worker_args_template[key]
                elif key in ppw_optional_keys_with_defaults: pass
                else: missing_keys.append(key)


            if missing_keys:
                 self.log_signal.emit(f"❌ CRITICAL ERROR: Missing expected keys for PostProcessorWorker: {', '.join(missing_keys)}")
                 self.cancellation_event.set()
                 break

            try:
                worker_instance = PostProcessorWorker(**worker_init_args)
                if self.thread_pool:
                    future = self.thread_pool.submit(worker_instance.process)
                    future.add_done_callback(self._handle_future_result)
                    self.active_futures.append(future)
                else:
                    self.log_signal.emit("⚠️ Thread pool not available. Cannot submit more tasks.")
                    break
            except TypeError as te:
                 self.log_signal.emit(f"❌ TypeError creating PostProcessorWorker: {te}")
                 passed_keys_str = ", ".join(sorted(worker_init_args.keys()))
                 self.log_signal.emit(f"   Passed Args: [{passed_keys_str}]")
                 self.log_signal.emit(traceback.format_exc(limit=5))
                 self.cancellation_event.set(); break
            except RuntimeError:
                self.log_signal.emit("⚠️ Runtime error submitting task (pool likely shutting down)."); break
            except Exception as e:
                self.log_signal.emit(f"❌ Error submitting post {post_data_item.get('id','N/A')} to worker: {e}"); break

        if not self.cancellation_event.is_set():
            self.log_signal.emit(f"   {len(self.active_futures)} post processing tasks submitted to pool.")
        else:
            self.finished_signal.emit(self.download_counter, self.skip_counter, True)
            if self.thread_pool:
                self.thread_pool.shutdown(wait=False, cancel_futures=True); self.thread_pool = None


    def _handle_future_result(self, future: Future):
        self.processed_posts_count += 1
        downloaded_files_from_future = 0
        skipped_files_from_future = 0
        try:
            if future.cancelled():
                self.log_signal.emit("   A post processing task was cancelled.")
            elif future.exception():
                worker_exception = future.exception()
                self.log_signal.emit(f"❌ Post processing worker error: {worker_exception}")
            else: # Success
                downloaded_files_from_future, skipped_files_from_future = future.result()

            with self.downloaded_files_lock:
                 self.download_counter += downloaded_files_from_future
                 self.skip_counter += skipped_files_from_future

            self.overall_progress_signal.emit(self.total_posts_to_process, self.processed_posts_count)

        except Exception as e:
            self.log_signal.emit(f"❌ Error in _handle_future_result callback: {e}\n{traceback.format_exc(limit=2)}")

        if self.total_posts_to_process > 0 and self.processed_posts_count >= self.total_posts_to_process:
            all_done = all(f.done() for f in self.active_futures)
            if all_done:
                QApplication.processEvents()
                self.log_signal.emit("🏁 All submitted post tasks have completed or failed.")
                self.finished_signal.emit(self.download_counter, self.skip_counter, self.cancellation_event.is_set())


    def set_ui_enabled(self, enabled):
        widgets_to_toggle = [
            self.download_btn, self.link_input,
            self.radio_all, self.radio_images, self.radio_videos, self.radio_only_links,
            self.skip_zip_checkbox, self.skip_rar_checkbox,
            self.use_subfolders_checkbox, self.compress_images_checkbox,
            self.download_thumbnails_checkbox, self.use_multithreading_checkbox,
            self.skip_words_input, self.character_search_input, self.new_char_input,
            self.add_char_button, self.delete_char_button,
            self.start_page_input, self.end_page_input, self.page_range_label, self.to_label,
            self.character_input, self.custom_folder_input, self.custom_folder_label,
            self.reset_button,
            self.manga_mode_checkbox
        ]
        for widget in widgets_to_toggle:
            if widget:
                widget.setEnabled(enabled)

        if self.external_links_checkbox:
            is_only_links = self.radio_only_links and self.radio_only_links.isChecked()
            self.external_links_checkbox.setEnabled(not is_only_links)
        if self.log_verbosity_button:
             self.log_verbosity_button.setEnabled(True)


        multithreading_currently_on = self.use_multithreading_checkbox.isChecked()
        self.thread_count_input.setEnabled(enabled and multithreading_currently_on)
        self.thread_count_label.setEnabled(enabled and multithreading_currently_on)


        subfolders_currently_on = self.use_subfolders_checkbox.isChecked()
        self.use_subfolder_per_post_checkbox.setEnabled(enabled and subfolders_currently_on)

        self.cancel_btn.setEnabled(not enabled)

        if enabled:
            self._handle_filter_mode_change(self.radio_group.checkedButton(), True)
            self._handle_multithreading_toggle(multithreading_currently_on)


    def cancel_download(self):
        if not self.cancel_btn.isEnabled() and not self.cancellation_event.is_set():
            self.log_signal.emit("ℹ️ No active download to cancel or already cancelling.")
            return

        self.log_signal.emit("⚠️ Requesting cancellation of download process...")
        self.cancellation_event.set()

        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.requestInterruption()
            self.log_signal.emit("   Signaled single download thread to interrupt.")

        if self.thread_pool:
            self.log_signal.emit("   Initiating immediate shutdown and cancellation of worker pool tasks...")
            self.thread_pool.shutdown(wait=False, cancel_futures=True)

        self.external_link_queue.clear()
        self._is_processing_external_link_queue = False
        self._current_link_post_title = None

        self.cancel_btn.setEnabled(False)
        self.progress_label.setText("Progress: Cancelling...")
        self.file_progress_label.setText("")


    def download_finished(self, total_downloaded, total_skipped, cancelled_by_user):
        status_message = "Cancelled by user" if cancelled_by_user else "Finished"
        self.log_signal.emit("="*40 + f"\n🏁 Download {status_message}!\n   Summary: Downloaded Files={total_downloaded}, Skipped Files={total_skipped}\n" + "="*40)
        self.progress_label.setText(f"{status_message}: {total_downloaded} downloaded, {total_skipped} skipped.")
        self.file_progress_label.setText("")

        if not cancelled_by_user:
            self._try_process_next_external_link()

        if self.download_thread:
            try:
                if hasattr(self.download_thread, 'progress_signal'): self.download_thread.progress_signal.disconnect(self.handle_main_log)
                if hasattr(self.download_thread, 'add_character_prompt_signal'): self.download_thread.add_character_prompt_signal.disconnect(self.add_character_prompt_signal)
                if hasattr(self.download_thread, 'finished_signal'): self.download_thread.finished_signal.disconnect(self.finished_signal)
                if hasattr(self.download_thread, 'receive_add_character_result'): self.character_prompt_response_signal.disconnect(self.download_thread.receive_add_character_result)
                if hasattr(self.download_thread, 'external_link_signal'): self.download_thread.external_link_signal.disconnect(self.handle_external_link_signal)
                if hasattr(self.download_thread, 'file_progress_signal'): self.download_thread.file_progress_signal.disconnect(self.update_file_progress_display)
            except (TypeError, RuntimeError) as e:
                 self.log_signal.emit(f"ℹ️ Note during single-thread signal disconnection: {e}")
            self.download_thread = None

        if self.thread_pool:
            self.log_signal.emit("   Ensuring worker thread pool is shut down...")
            self.thread_pool.shutdown(wait=True, cancel_futures=True)
            self.thread_pool = None
        self.active_futures = []


        self.set_ui_enabled(True)
        self.cancel_btn.setEnabled(False)

    def toggle_log_verbosity(self):
        self.basic_log_mode = not self.basic_log_mode
        if self.basic_log_mode:
            self.log_verbosity_button.setText("Show Full Log")
            self.log_signal.emit("="*20 + " Basic Log Mode Enabled " + "="*20)
        else:
            self.log_verbosity_button.setText("Show Basic Log")
            self.log_signal.emit("="*20 + " Full Log Mode Enabled " + "="*20)

    def reset_application_state(self):
        is_running = (self.download_thread and self.download_thread.isRunning()) or \
                     (self.thread_pool is not None and any(not f.done() for f in self.active_futures if f is not None))
        if is_running:
            QMessageBox.warning(self, "Reset Error", "Cannot reset while a download is in progress. Please cancel the download first.")
            return

        self.log_signal.emit("🔄 Resetting application state to defaults...")
        self._reset_ui_to_defaults()
        self.main_log_output.clear()
        self.external_log_output.clear()
        if self.show_external_links:
             self.external_log_output.append("🔗 External Links Found:")

        self.external_link_queue.clear()
        self.extracted_links_cache = []
        self._is_processing_external_link_queue = False
        self._current_link_post_title = None

        self.progress_label.setText("Progress: Idle")
        self.file_progress_label.setText("")

        with self.downloaded_files_lock:
            count = len(self.downloaded_files)
            self.downloaded_files.clear()
            if count > 0: self.log_signal.emit(f"   Cleared {count} downloaded filename(s) from session memory.")
        with self.downloaded_file_hashes_lock:
            count = len(self.downloaded_file_hashes)
            self.downloaded_file_hashes.clear()
            if count > 0: self.log_signal.emit(f"   Cleared {count} downloaded file hash(es) from session memory.")

        self.total_posts_to_process = 0
        self.processed_posts_count = 0
        self.download_counter = 0
        self.skip_counter = 0

        self.cancellation_event.clear()

        self.basic_log_mode = False
        if self.log_verbosity_button:
            self.log_verbosity_button.setText("Show Basic Log")

        self.log_signal.emit("✅ Application reset complete.")


    def _reset_ui_to_defaults(self):
        self.link_input.clear()
        self.dir_input.clear()
        self.custom_folder_input.clear()
        self.character_input.clear()
        self.skip_words_input.clear()
        self.start_page_input.clear()
        self.end_page_input.clear()
        self.new_char_input.clear()
        self.character_search_input.clear()
        self.thread_count_input.setText("4")

        self.radio_all.setChecked(True)
        self.skip_zip_checkbox.setChecked(True)
        self.skip_rar_checkbox.setChecked(True)
        self.download_thumbnails_checkbox.setChecked(False)
        self.compress_images_checkbox.setChecked(False)
        self.use_subfolders_checkbox.setChecked(True)
        self.use_subfolder_per_post_checkbox.setChecked(False)
        self.use_multithreading_checkbox.setChecked(True)
        self.external_links_checkbox.setChecked(False)
        if self.manga_mode_checkbox:
            self.manga_mode_checkbox.setChecked(False)

        self._handle_filter_mode_change(self.radio_all, True)
        self._handle_multithreading_toggle(self.use_multithreading_checkbox.isChecked())

        self.filter_character_list("")

        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        if self.reset_button: self.reset_button.setEnabled(True)
        if self.log_verbosity_button: self.log_verbosity_button.setText("Show Basic Log")


    def prompt_add_character(self, character_name):
        global KNOWN_NAMES
        reply = QMessageBox.question(self, "Add Filter Name to Known List?",
                                      f"The name '{character_name}' was encountered or used as a filter.\nIt's not in your known names list (used for folder suggestions).\nAdd it now?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        result = (reply == QMessageBox.Yes)
        if result:
              self.new_char_input.setText(character_name)
              if self.add_new_character():
                   self.log_signal.emit(f"✅ Added '{character_name}' to known names via background prompt.")
              else:
                   result = False
                   self.log_signal.emit(f"ℹ️ Adding '{character_name}' via background prompt was declined or failed (e.g., similarity warning, duplicate).")
        self.character_prompt_response_signal.emit(result)

    def receive_add_character_result(self, result):
        with QMutexLocker(self.prompt_mutex):
             self._add_character_response = result
        self.log_signal.emit(f"   Main thread received character prompt response: {'Action resulted in addition/confirmation' if result else 'Action resulted in no addition/declined'}")


if __name__ == '__main__':
    import traceback
    try:
        qt_app = QApplication(sys.argv)
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        icon_path = os.path.join(base_dir, 'Kemono.ico')
        if os.path.exists(icon_path):
            qt_app.setWindowIcon(QIcon(icon_path))
        else:
             print(f"Warning: Application icon 'Kemono.ico' not found at {icon_path}")

        downloader_app_instance = DownloaderApp()
        downloader_app_instance.show()

        # --- ADDED: Show Tour Dialog if needed ---
        if TourDialog: # Check if TourDialog was imported successfully
            tour_result = TourDialog.run_tour_if_needed(downloader_app_instance)
            if tour_result == QDialog.Accepted:
                print("Tour completed by user.")
            elif tour_result == QDialog.Rejected:
                # This means tour was skipped OR already shown.
                # You can use TourDialog.settings.value(TourDialog.TOUR_SHOWN_KEY)
                # to differentiate if needed, but run_tour_if_needed handles the "show once" logic.
                print("Tour skipped or was already shown.")
        # --- END ADDED ---

        exit_code = qt_app.exec_()
        print(f"Application finished with exit code: {exit_code}")
        sys.exit(exit_code)
    except SystemExit:
        pass # Allow clean exit
    except Exception as e:
        print("--- CRITICAL APPLICATION ERROR ---")
        print(f"An unhandled exception occurred: {e}")
        traceback.print_exc()
        print("--- END CRITICAL ERROR ---")
        sys.exit(1)