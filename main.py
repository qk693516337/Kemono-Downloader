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
    QRadioButton, QButtonGroup, QCheckBox, QSplitter, QSizePolicy, QDialog,
    QFrame,
    QAbstractButton
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMutex, QMutexLocker, QObject, QTimer, QSettings
from urllib.parse import urlparse

try:
    from PIL import Image
except ImportError:
    Image = None

from io import BytesIO

# --- Import from downloader_utils ---
try:
    print("Attempting to import from downloader_utils...")
    from downloader_utils import (
        KNOWN_NAMES,
        clean_folder_name,
        extract_post_info,
        download_from_api,
        PostProcessorSignals,
        PostProcessorWorker,
        DownloadThread as BackendDownloadThread, # Renamed to avoid conflict
        SKIP_SCOPE_FILES,
        SKIP_SCOPE_POSTS,
        SKIP_SCOPE_BOTH
    )
    print("Successfully imported names from downloader_utils.")
except ImportError as e:
    print(f"--- IMPORT ERROR ---")
    print(f"Failed to import from 'downloader_utils.py': {e}")
    # Define fallbacks if import fails, so the app might still run with limited functionality or show an error.
    KNOWN_NAMES = []
    PostProcessorSignals = QObject # Fallback to base QObject
    PostProcessorWorker = object # Fallback to base object
    BackendDownloadThread = QThread # Fallback to base QThread
    def clean_folder_name(n): return str(n) # Simple fallback
    def extract_post_info(u): return None, None, None # Fallback
    def download_from_api(*a, **k): yield [] # Fallback generator
    SKIP_SCOPE_FILES = "files"
    SKIP_SCOPE_POSTS = "posts"
    SKIP_SCOPE_BOTH = "both"
    # Potentially show a critical error to the user here if downloader_utils is essential
    # For now, printing to console is the primary error indication.
except Exception as e:
    print(f"--- UNEXPECTED IMPORT ERROR ---")
    print(f"An unexpected error occurred during import: {e}")
    traceback.print_exc()
    print(f"-----------------------------", file=sys.stderr)
    sys.exit(1) # Exit if a critical, unexpected error occurs during import
# --- End Import ---

# --- Import Tour Dialog ---
try:
    from tour import TourDialog # Assuming tour.py exists in the same directory
    print("Successfully imported TourDialog from tour.py.")
except ImportError as e:
    print(f"--- TOUR IMPORT ERROR ---")
    print(f"Failed to import TourDialog from 'tour.py': {e}")
    print("Tour functionality will be unavailable.")
    TourDialog = None # Fallback if tour.py is not found
except Exception as e:
    print(f"--- UNEXPECTED TOUR IMPORT ERROR ---")
    print(f"An unexpected error occurred during tour import: {e}")
    traceback.print_exc()
    TourDialog = None
# --- End Tour Import ---


# --- Constants for Thread Limits ---
MAX_THREADS = 200 # Max post workers for creator feeds
RECOMMENDED_MAX_THREADS = 50 # Recommended max post workers
MAX_FILE_THREADS_PER_POST_OR_WORKER = 10 # Max file download threads for single post or per creator feed worker
# --- END ---

HTML_PREFIX = "<!HTML!>" # Prefix to indicate a log message is HTML

# --- QSettings Constants ---
CONFIG_ORGANIZATION_NAME = "KemonoDownloader" # Company/Organization Name for settings
CONFIG_APP_NAME_MAIN = "ApplicationSettings"  # Application Name for settings
MANGA_FILENAME_STYLE_KEY = "mangaFilenameStyleV1" # Key for storing manga filename style
STYLE_POST_TITLE = "post_title" # Constant for post title filename style
STYLE_ORIGINAL_NAME = "original_name" # Constant for original filename style
SKIP_WORDS_SCOPE_KEY = "skipWordsScopeV1" # Key for storing skip words scope
# --- END QSettings ---


class DownloaderApp(QWidget):
    # Signals for cross-thread communication and UI updates
    character_prompt_response_signal = pyqtSignal(bool) # Signal for character prompt response
    log_signal = pyqtSignal(str) # Signal for logging messages to the UI
    add_character_prompt_signal = pyqtSignal(str) # Signal to prompt adding a character
    overall_progress_signal = pyqtSignal(int, int) # Signal for overall download progress (total, processed)
    finished_signal = pyqtSignal(int, int, bool, list) # Signal when download finishes (dl_count, skip_count, cancelled, kept_original_names)
    external_link_signal = pyqtSignal(str, str, str, str) # Signal for found external links (post_title, link_text, url, platform)
    file_progress_signal = pyqtSignal(str, int, int) # Signal for individual file download progress (filename, downloaded_bytes, total_bytes)


    def __init__(self):
        super().__init__()
        # Initialize QSettings for storing application settings persistently
        self.settings = QSettings(CONFIG_ORGANIZATION_NAME, CONFIG_APP_NAME_MAIN)
        self.config_file = "Known.txt" # File to store known character/show names

        # Download process related attributes
        self.download_thread = None # Holds the single download thread instance
        self.thread_pool = None # Holds the ThreadPoolExecutor for multi-threaded downloads
        self.cancellation_event = threading.Event() # Event to signal cancellation to threads
        self.active_futures = [] # List of active Future objects from the thread pool
        self.total_posts_to_process = 0 # Total posts identified for the current download
        self.processed_posts_count = 0 # Number of posts processed so far
        self.download_counter = 0 # Total files downloaded in the current session/run
        self.skip_counter = 0 # Total files skipped in the current session/run

        # Signals object for PostProcessorWorker instances
        self.worker_signals = PostProcessorSignals()
        # Mutex and response attribute for synchronous character add prompt
        self.prompt_mutex = QMutex()
        self._add_character_response = None

        # Sets to keep track of downloaded files/hashes to avoid re-downloads in the same session
        self.downloaded_files = set() # Set of downloaded filenames (final saved names)
        self.downloaded_files_lock = threading.Lock() # Lock for accessing downloaded_files set
        self.downloaded_file_hashes = set() # Set of MD5 hashes of downloaded files
        self.downloaded_file_hashes_lock = threading.Lock() # Lock for accessing downloaded_file_hashes set

        # External links related attributes
        self.show_external_links = False # Flag to control display of external links log
        self.external_link_queue = deque() # Queue for processing external links with delays
        self._is_processing_external_link_queue = False # Flag to prevent concurrent processing of the link queue
        self._current_link_post_title = None # Tracks current post title for grouping links in "Only Links" mode
        self.extracted_links_cache = [] # Cache of all extracted links for "Only Links" mode display and export

        # UI and Logging related attributes
        self.basic_log_mode = False # Flag for toggling basic/full log verbosity
        self.log_verbosity_button = None # Button to toggle log verbosity
        self.manga_rename_toggle_button = None # Button to toggle manga filename style

        self.main_log_output = None # QTextEdit for main progress log
        self.external_log_output = None # QTextEdit for external links log
        self.log_splitter = None # QSplitter for main and external logs
        self.main_splitter = None # Main QSplitter for left (controls) and right (logs) panels
        self.reset_button = None # Button to reset application state
        self.progress_log_label = None # Label above the main log area

        self.link_search_input = None # QLineEdit for searching in extracted links
        self.link_search_button = None # QPushButton to trigger link search/filter
        self.export_links_button = None # QPushButton to export extracted links

        self.manga_mode_checkbox = None # QCheckBox for enabling Manga/Comic mode
        self.radio_only_links = None # QRadioButton for "Only Links" filter mode
        self.radio_only_archives = None # QRadioButton for "Only Archives" filter mode
        
        self.skip_scope_toggle_button = None # Button to cycle skip words scope

        # List to store filenames that kept their original names (for manga mode logging)
        self.all_kept_original_filenames = []

        # Load persistent settings or use defaults
        self.manga_filename_style = self.settings.value(MANGA_FILENAME_STYLE_KEY, STYLE_POST_TITLE, type=str)
        self.skip_words_scope = self.settings.value(SKIP_WORDS_SCOPE_KEY, SKIP_SCOPE_FILES, type=str)


        self.load_known_names_from_util() # Load known names from config file
        self.setWindowTitle("Kemono Downloader v3.1.0") # Update version number
        self.setGeometry(150, 150, 1050, 820) # Set initial window size and position
        self.setStyleSheet(self.get_dark_theme()) # Apply a dark theme stylesheet
        self.init_ui() # Initialize the user interface elements
        self._connect_signals() # Connect signals to their respective slots

        # Initial log messages
        self.log_signal.emit("ℹ️ Local API server functionality has been removed.")
        self.log_signal.emit("ℹ️ 'Skip Current File' button has been removed.")
        if hasattr(self, 'character_input'): # Set tooltip for character input if it exists
            self.character_input.setToolTip("Enter one or more character names, separated by commas (e.g., yor, makima)")
        self.log_signal.emit(f"ℹ️ Manga filename style loaded: '{self.manga_filename_style}'")
        self.log_signal.emit(f"ℹ️ Skip words scope loaded: '{self.skip_words_scope}'")


    def _connect_signals(self):
        """Connects various signals from UI elements and worker threads to their handler methods."""
        # Worker signals (from PostProcessorWorker via PostProcessorSignals)
        if hasattr(self.worker_signals, 'progress_signal'):
             self.worker_signals.progress_signal.connect(self.handle_main_log)
        if hasattr(self.worker_signals, 'file_progress_signal'):
            self.worker_signals.file_progress_signal.connect(self.update_file_progress_display)
        if hasattr(self.worker_signals, 'external_link_signal'):
            self.worker_signals.external_link_signal.connect(self.handle_external_link_signal)

        # Internal app signals
        self.log_signal.connect(self.handle_main_log)
        self.add_character_prompt_signal.connect(self.prompt_add_character)
        self.character_prompt_response_signal.connect(self.receive_add_character_result)
        self.overall_progress_signal.connect(self.update_progress_display)
        self.finished_signal.connect(self.download_finished)
        self.external_link_signal.connect(self.handle_external_link_signal) # Also connect direct app signal
        self.file_progress_signal.connect(self.update_file_progress_display) # Also connect direct app signal

        # UI element signals
        if hasattr(self, 'character_search_input'): self.character_search_input.textChanged.connect(self.filter_character_list)
        if hasattr(self, 'external_links_checkbox'): self.external_links_checkbox.toggled.connect(self.update_external_links_setting)
        if hasattr(self, 'thread_count_input'): self.thread_count_input.textChanged.connect(self.update_multithreading_label)
        if hasattr(self, 'use_subfolder_per_post_checkbox'): self.use_subfolder_per_post_checkbox.toggled.connect(self.update_ui_for_subfolders)
        if hasattr(self, 'use_multithreading_checkbox'): self.use_multithreading_checkbox.toggled.connect(self._handle_multithreading_toggle)

        # Radio button group for file filters
        if hasattr(self, 'radio_group') and self.radio_group:
            # Connect only once to the buttonToggled signal of the QButtonGroup
            self.radio_group.buttonToggled.connect(self._handle_filter_mode_change)

        # Button clicks
        if self.reset_button: self.reset_button.clicked.connect(self.reset_application_state)
        if self.log_verbosity_button: self.log_verbosity_button.clicked.connect(self.toggle_log_verbosity)

        # Link search UI signals (for "Only Links" mode)
        if self.link_search_button: self.link_search_button.clicked.connect(self._filter_links_log)
        if self.link_search_input:
            self.link_search_input.returnPressed.connect(self._filter_links_log) # Filter on Enter
            self.link_search_input.textChanged.connect(self._filter_links_log) # Live filtering as text changes
        if self.export_links_button: self.export_links_button.clicked.connect(self._export_links_to_file)

        # Manga mode UI signals
        if self.manga_mode_checkbox: self.manga_mode_checkbox.toggled.connect(self.update_ui_for_manga_mode)
        if self.manga_rename_toggle_button: self.manga_rename_toggle_button.clicked.connect(self._toggle_manga_filename_style)

        # URL input text change (affects manga mode UI and page range)
        if hasattr(self, 'link_input'):
            self.link_input.textChanged.connect(lambda: self.update_ui_for_manga_mode(self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False))
        
        # Skip words scope toggle button
        if self.skip_scope_toggle_button:
            self.skip_scope_toggle_button.clicked.connect(self._cycle_skip_scope)


    def load_known_names_from_util(self):
        """Loads known character/show names from the config file into the global KNOWN_NAMES list."""
        global KNOWN_NAMES # Access the global list (potentially shared with downloader_utils)
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    raw_names = [line.strip() for line in f]
                    # Update KNOWN_NAMES in-place to ensure shared references (like in downloader_utils) are updated
                    KNOWN_NAMES[:] = sorted(list(set(filter(None, raw_names)))) # Unique, sorted, non-empty names
                log_msg = f"ℹ️ Loaded {len(KNOWN_NAMES)} known names from {self.config_file}"
            except Exception as e:
                log_msg = f"❌ Error loading config '{self.config_file}': {e}"
                QMessageBox.warning(self, "Config Load Error", f"Could not load list from {self.config_file}:\n{e}")
                KNOWN_NAMES[:] = [] # Reset to empty if loading fails
        else:
            log_msg = f"ℹ️ Config file '{self.config_file}' not found. Starting empty."
            KNOWN_NAMES[:] = [] # Ensure it's empty if file doesn't exist

        if hasattr(self, 'log_signal'): self.log_signal.emit(log_msg) # Log loading status
        
        # Update the QListWidget in the UI with the loaded names
        if hasattr(self, 'character_list'):
            self.character_list.clear()
            self.character_list.addItems(KNOWN_NAMES)

    def save_known_names(self):
        """Saves the current list of known names to the config file."""
        global KNOWN_NAMES # Access the global (potentially shared) list
        try:
            # Ensure KNOWN_NAMES itself is updated to the unique sorted list before saving
            unique_sorted_names = sorted(list(set(filter(None, KNOWN_NAMES))))
            KNOWN_NAMES[:] = unique_sorted_names # Modify in-place

            with open(self.config_file, 'w', encoding='utf-8') as f:
                for name in unique_sorted_names:
                    f.write(name + '\n')
            if hasattr(self, 'log_signal'): self.log_signal.emit(f"💾 Saved {len(unique_sorted_names)} known names to {self.config_file}")
        except Exception as e:
            log_msg = f"❌ Error saving config '{self.config_file}': {e}"
            if hasattr(self, 'log_signal'): self.log_signal.emit(log_msg)
            QMessageBox.warning(self, "Config Save Error", f"Could not save list to {self.config_file}:\n{e}")

    def closeEvent(self, event):
        """Handles the application close event. Saves settings and manages active downloads."""
        # Save known names and other persistent settings
        self.save_known_names()
        self.settings.setValue(MANGA_FILENAME_STYLE_KEY, self.manga_filename_style)
        self.settings.setValue(SKIP_WORDS_SCOPE_KEY, self.skip_words_scope)
        self.settings.sync() # Ensure settings are written to disk

        should_exit = True
        is_downloading = self._is_download_active() # Check if any download is currently active

        if is_downloading:
             # Confirm with the user if they want to exit while a download is in progress
             reply = QMessageBox.question(self, "Confirm Exit",
                                          "Download in progress. Are you sure you want to exit and cancel?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No) # Default to No
             if reply == QMessageBox.Yes:
                 self.log_signal.emit("⚠️ Cancelling active download due to application exit...")
                 self.cancel_download() # Signal cancellation to active threads/pool
                 self.log_signal.emit("   Waiting briefly for threads to acknowledge cancellation...")
                 
                 # Wait for threads to finish, with a timeout
                 if self.download_thread and self.download_thread.isRunning():
                     self.download_thread.wait(3000) # Wait up to 3 seconds for single thread
                     if self.download_thread.isRunning():
                         self.log_signal.emit("   ⚠️ Single download thread did not terminate gracefully.")
                 if self.thread_pool:
                     # Shutdown with cancel_futures=True. The wait=True here might block,
                     # but cancel_download should have already signaled futures.
                     self.thread_pool.shutdown(wait=True, cancel_futures=True)
                     self.log_signal.emit("   Thread pool shutdown complete.")
                     self.thread_pool = None # Clear the reference
             else:
                 should_exit = False # User chose not to exit
                 self.log_signal.emit("ℹ️ Application exit cancelled.")
                 event.ignore() # Ignore the close event
                 return # Don't proceed to exit

        if should_exit:
            self.log_signal.emit("ℹ️ Application closing.")
            # Ensure any remaining pool is shut down if not already handled
            if self.thread_pool:
                 self.log_signal.emit("   Final thread pool check: Shutting down...")
                 self.cancellation_event.set() # Ensure cancellation event is set
                 self.thread_pool.shutdown(wait=True, cancel_futures=True) # Wait for shutdown
                 self.thread_pool = None
            self.log_signal.emit("👋 Exiting application.")
            event.accept() # Accept the close event


    def init_ui(self):
        """Initializes all UI elements and layouts."""
        # Main layout splitter (divides window into left controls panel and right logs panel)
        self.main_splitter = QSplitter(Qt.Horizontal)
        left_panel_widget = QWidget() # Container widget for the left panel
        right_panel_widget = QWidget() # Container widget for the right panel
        left_layout = QVBoxLayout(left_panel_widget) # Main vertical layout for the left panel
        right_layout = QVBoxLayout(right_panel_widget) # Main vertical layout for the right panel
        left_layout.setContentsMargins(10, 10, 10, 10) # Add some padding around left panel contents
        right_layout.setContentsMargins(10, 10, 10, 10) # Add padding around right panel contents

        # --- Left Panel (Controls) ---

        # URL and Page Range Input Section
        url_page_layout = QHBoxLayout() # Horizontal layout for URL and page range inputs
        url_page_layout.setContentsMargins(0,0,0,0) # No internal margins for this specific QHBoxLayout
        url_page_layout.addWidget(QLabel("🔗 Kemono Creator/Post URL:"))
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("e.g., https://kemono.su/patreon/user/12345 or .../post/98765")
        self.link_input.textChanged.connect(self.update_custom_folder_visibility) # Connect to update custom folder UI
        url_page_layout.addWidget(self.link_input, 1) # Allow URL input to stretch

        # Page range inputs (Start and End)
        self.page_range_label = QLabel("Page Range:")
        self.page_range_label.setStyleSheet("font-weight: bold; padding-left: 10px;") # Style for emphasis
        self.start_page_input = QLineEdit()
        self.start_page_input.setPlaceholderText("Start")
        self.start_page_input.setFixedWidth(50) # Fixed width for small input
        self.start_page_input.setValidator(QIntValidator(1, 99999)) # Allow only positive integers
        self.to_label = QLabel("to") # Simple "to" label between inputs
        self.end_page_input = QLineEdit()
        self.end_page_input.setPlaceholderText("End")
        self.end_page_input.setFixedWidth(50)
        self.end_page_input.setValidator(QIntValidator(1, 99999))
        # Add page range widgets to the horizontal layout
        url_page_layout.addWidget(self.page_range_label)
        url_page_layout.addWidget(self.start_page_input)
        url_page_layout.addWidget(self.to_label)
        url_page_layout.addWidget(self.end_page_input)
        left_layout.addLayout(url_page_layout) # Add URL/Page layout to the main left layout

        # Download Directory Input Section
        left_layout.addWidget(QLabel("📁 Download Location:"))
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select folder where downloads will be saved")
        self.dir_button = QPushButton("Browse...") # Button to open file dialog
        self.dir_button.clicked.connect(self.browse_directory)
        dir_layout = QHBoxLayout() # Horizontal layout for directory input and browse button
        dir_layout.addWidget(self.dir_input, 1) # Allow directory input to stretch
        dir_layout.addWidget(self.dir_button)
        left_layout.addLayout(dir_layout)


        # Container for Character Filter and Custom Folder (to manage visibility together)
        self.filters_and_custom_folder_container_widget = QWidget()
        filters_and_custom_folder_layout = QHBoxLayout(self.filters_and_custom_folder_container_widget)
        filters_and_custom_folder_layout.setContentsMargins(0, 5, 0, 0) # Top margin, no others
        filters_and_custom_folder_layout.setSpacing(10) # Spacing between filter and custom folder

        # Character Filter (will be added to the container)
        self.character_filter_widget = QWidget() # Dedicated widget for character filter
        character_filter_v_layout = QVBoxLayout(self.character_filter_widget)
        character_filter_v_layout.setContentsMargins(0,0,0,0) # No internal margins for this VBox
        character_filter_v_layout.setSpacing(2) # Minimal spacing between label and input
        self.character_label = QLabel("🎯 Filter by Character(s) (comma-separated):")
        self.character_input = QLineEdit()
        self.character_input.setPlaceholderText("e.g., yor, Tifa, Reyna")
        character_filter_v_layout.addWidget(self.character_label)
        character_filter_v_layout.addWidget(self.character_input)

        # Custom Folder Name (will be added to the container)
        self.custom_folder_widget = QWidget() # Dedicated widget for custom folder input
        custom_folder_v_layout = QVBoxLayout(self.custom_folder_widget)
        custom_folder_v_layout.setContentsMargins(0,0,0,0) # No internal margins
        custom_folder_v_layout.setSpacing(2)
        self.custom_folder_label = QLabel("🗄️ Custom Folder Name (Single Post Only):")
        self.custom_folder_input = QLineEdit()
        self.custom_folder_input.setPlaceholderText("Optional: Save this post to specific folder")
        custom_folder_v_layout.addWidget(self.custom_folder_label)
        custom_folder_v_layout.addWidget(self.custom_folder_input)
        self.custom_folder_widget.setVisible(False) # Initially hidden, shown based on URL and settings

        # Add character filter and custom folder widgets to their container layout
        filters_and_custom_folder_layout.addWidget(self.character_filter_widget, 1) # Allow stretch
        filters_and_custom_folder_layout.addWidget(self.custom_folder_widget, 1)  # Allow stretch

        # Add the container widget to the main left layout
        left_layout.addWidget(self.filters_and_custom_folder_container_widget)


        # Skip Words Input Section
        left_layout.addWidget(QLabel("🚫 Skip with Words (comma-separated):"))
        skip_input_and_button_layout = QHBoxLayout() # Horizontal layout for skip words input and scope button
        skip_input_and_button_layout.setContentsMargins(0, 0, 0, 0)
        skip_input_and_button_layout.setSpacing(10)
        self.skip_words_input = QLineEdit()
        self.skip_words_input.setPlaceholderText("e.g., WM, WIP, sketch, preview")
        skip_input_and_button_layout.addWidget(self.skip_words_input, 3) # Give more space to input
        self.skip_scope_toggle_button = QPushButton() # Text set by _update_skip_scope_button_text
        self._update_skip_scope_button_text() # Set initial text based on loaded/default scope
        self.skip_scope_toggle_button.setToolTip("Click to cycle skip scope (Files -> Posts -> Both)")
        self.skip_scope_toggle_button.setStyleSheet("padding: 6px 10px;") # Ensure consistent padding
        self.skip_scope_toggle_button.setMinimumWidth(100) # Ensure button is wide enough for text
        skip_input_and_button_layout.addWidget(self.skip_scope_toggle_button, 1) # Add scope button
        left_layout.addLayout(skip_input_and_button_layout)


        # File Filter Radio Buttons Section
        file_filter_layout = QVBoxLayout() # Vertical layout for the file filter section
        file_filter_layout.setContentsMargins(0,10,0,0) # Add some top margin for separation
        file_filter_layout.addWidget(QLabel("Filter Files:")) # Section label
        radio_button_layout = QHBoxLayout() # Horizontal layout for the radio buttons themselves
        radio_button_layout.setSpacing(10) # Adjusted spacing between radio buttons
        self.radio_group = QButtonGroup(self) # Group to ensure only one radio button is selected
        # Define radio buttons
        self.radio_all = QRadioButton("All")
        self.radio_images = QRadioButton("Images/GIFs")
        self.radio_videos = QRadioButton("Videos")
        self.radio_only_archives = QRadioButton("📦 Only Archives") # New radio button for archives
        self.radio_only_links = QRadioButton("🔗 Only Links")
        self.radio_all.setChecked(True) # Default selection
        # Add buttons to the group
        self.radio_group.addButton(self.radio_all)
        self.radio_group.addButton(self.radio_images)
        self.radio_group.addButton(self.radio_videos)
        self.radio_group.addButton(self.radio_only_archives) # Add new button to group
        self.radio_group.addButton(self.radio_only_links)
        # Add buttons to the horizontal layout
        radio_button_layout.addWidget(self.radio_all)
        radio_button_layout.addWidget(self.radio_images)
        radio_button_layout.addWidget(self.radio_videos)
        radio_button_layout.addWidget(self.radio_only_archives) # Add new button to layout
        radio_button_layout.addWidget(self.radio_only_links)
        radio_button_layout.addStretch(1) # Push buttons to the left, filling remaining space
        file_filter_layout.addLayout(radio_button_layout) # Add radio button layout to section layout
        left_layout.addLayout(file_filter_layout) # Add section layout to main left layout

        # Checkboxes Group Section (for various download options)
        checkboxes_group_layout = QVBoxLayout() # Vertical layout for checkbox groups
        checkboxes_group_layout.setSpacing(10) # Spacing between rows of checkboxes
        
        # Row 1 of Checkboxes (Skip ZIP/RAR, Thumbnails, Compress)
        row1_layout = QHBoxLayout() # Horizontal layout for the first row of checkboxes
        row1_layout.setSpacing(10)
        self.skip_zip_checkbox = QCheckBox("Skip .zip")
        self.skip_zip_checkbox.setChecked(True) # Default to skipping ZIPs
        row1_layout.addWidget(self.skip_zip_checkbox)
        self.skip_rar_checkbox = QCheckBox("Skip .rar")
        self.skip_rar_checkbox.setChecked(True) # Default to skipping RARs
        row1_layout.addWidget(self.skip_rar_checkbox)
        self.download_thumbnails_checkbox = QCheckBox("Download Thumbnails Only")
        self.download_thumbnails_checkbox.setChecked(False) # Default to not downloading only thumbnails
        self.download_thumbnails_checkbox.setToolTip("Thumbnail download functionality is currently limited without the API.")
        row1_layout.addWidget(self.download_thumbnails_checkbox)
        self.compress_images_checkbox = QCheckBox("Compress Large Images (to WebP)")
        self.compress_images_checkbox.setChecked(False) # Default to not compressing images
        self.compress_images_checkbox.setToolTip("Compress images > 1.5MB to WebP format (requires Pillow).")
        row1_layout.addWidget(self.compress_images_checkbox)
        row1_layout.addStretch(1) # Push checkboxes to the left
        checkboxes_group_layout.addLayout(row1_layout) # Add row to the group layout

        # Advanced Settings Label and Checkboxes
        advanced_settings_label = QLabel("⚙️ Advanced Settings:") # Label for advanced settings section
        checkboxes_group_layout.addWidget(advanced_settings_label)
        
        # Advanced Row 1 (Subfolders)
        advanced_row1_layout = QHBoxLayout() # Horizontal layout for first row of advanced checkboxes
        advanced_row1_layout.setSpacing(10)
        self.use_subfolders_checkbox = QCheckBox("Separate Folders by Name/Title")
        self.use_subfolders_checkbox.setChecked(True) # Default to using subfolders
        self.use_subfolders_checkbox.toggled.connect(self.update_ui_for_subfolders) # Connect to update UI
        advanced_row1_layout.addWidget(self.use_subfolders_checkbox)
        self.use_subfolder_per_post_checkbox = QCheckBox("Subfolder per Post")
        self.use_subfolder_per_post_checkbox.setChecked(False) # Default to not using subfolder per post
        self.use_subfolder_per_post_checkbox.setToolTip("Creates a subfolder for each post inside the character/title folder.")
        self.use_subfolder_per_post_checkbox.toggled.connect(self.update_ui_for_subfolders) # Connect to update UI
        advanced_row1_layout.addWidget(self.use_subfolder_per_post_checkbox)
        advanced_row1_layout.addStretch(1) # Push to left
        checkboxes_group_layout.addLayout(advanced_row1_layout)

        # Advanced Row 2 (Multithreading, External Links, Manga Mode)
        advanced_row2_layout = QHBoxLayout() # Horizontal layout for second row of advanced checkboxes
        advanced_row2_layout.setSpacing(10)
        
        # Multithreading specific layout (checkbox, label, input)
        multithreading_layout = QHBoxLayout()
        multithreading_layout.setContentsMargins(0,0,0,0) # No internal margins for this group
        self.use_multithreading_checkbox = QCheckBox("Use Multithreading")
        self.use_multithreading_checkbox.setChecked(True) # Default to using multithreading
        self.use_multithreading_checkbox.setToolTip( # Updated tooltip explaining thread count usage
            "Enables concurrent operations. See 'Threads' input for details."
        )
        multithreading_layout.addWidget(self.use_multithreading_checkbox)
        self.thread_count_label = QLabel("Threads:") # Label for thread count input
        multithreading_layout.addWidget(self.thread_count_label)
        self.thread_count_input = QLineEdit() # Input for number of threads
        self.thread_count_input.setFixedWidth(40) # Small fixed width
        self.thread_count_input.setText("4") # Default thread count
        self.thread_count_input.setToolTip( # Updated tooltip explaining thread usage contexts
            f"Number of concurrent operations.\n"
            f"- Single Post: Concurrent file downloads (1-{MAX_FILE_THREADS_PER_POST_OR_WORKER} recommended).\n"
            f"- Creator Feed: Concurrent post processing (1-{MAX_THREADS}).\n"
            f"  File downloads per post worker also use this value (1-{MAX_FILE_THREADS_PER_POST_OR_WORKER} recommended)."
        )
        self.thread_count_input.setValidator(QIntValidator(1, MAX_THREADS)) # Validate input (1 to MAX_THREADS)
        multithreading_layout.addWidget(self.thread_count_input)
        advanced_row2_layout.addLayout(multithreading_layout) # Add multithreading group to advanced row 2

        # External Links Checkbox
        self.external_links_checkbox = QCheckBox("Show External Links in Log")
        self.external_links_checkbox.setChecked(False) # Default to not showing external links log separately
        advanced_row2_layout.addWidget(self.external_links_checkbox)

        # Manga Mode Checkbox
        self.manga_mode_checkbox = QCheckBox("Manga/Comic Mode")
        self.manga_mode_checkbox.setToolTip("Downloads posts from oldest to newest and renames files based on post title (for creator feeds only).")
        self.manga_mode_checkbox.setChecked(False) # Default to manga mode off
        advanced_row2_layout.addWidget(self.manga_mode_checkbox)
        advanced_row2_layout.addStretch(1) # Push to left
        checkboxes_group_layout.addLayout(advanced_row2_layout) # Add advanced row 2 to group layout
        left_layout.addLayout(checkboxes_group_layout) # Add checkbox group layout to main left layout


        # Download and Cancel Buttons Section
        btn_layout = QHBoxLayout() # Horizontal layout for main action buttons
        btn_layout.setSpacing(10)
        self.download_btn = QPushButton("⬇️ Start Download")
        self.download_btn.setStyleSheet("padding: 8px 15px; font-weight: bold;") # Make download button prominent
        self.download_btn.clicked.connect(self.start_download) # Connect to start download logic
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setEnabled(False) # Initially disabled, enabled when download is active
        self.cancel_btn.clicked.connect(self.cancel_download) # Connect to cancel download logic
        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.cancel_btn)
        left_layout.addLayout(btn_layout) # Add button layout to main left layout
        left_layout.addSpacing(10) # Add some space after buttons

        # Known Characters/Shows List Section
        known_chars_label_layout = QHBoxLayout() # Layout for label and search input for known characters
        known_chars_label_layout.setSpacing(10)
        self.known_chars_label = QLabel("🎭 Known Shows/Characters (for Folder Names):")
        self.character_search_input = QLineEdit() # Input to filter the character list
        self.character_search_input.setPlaceholderText("Search characters...")
        known_chars_label_layout.addWidget(self.known_chars_label, 1) # Allow label to take space
        known_chars_label_layout.addWidget(self.character_search_input)
        left_layout.addLayout(known_chars_label_layout)

        self.character_list = QListWidget() # List to display known characters
        self.character_list.setSelectionMode(QListWidget.ExtendedSelection) # Allow multiple selections for deletion
        left_layout.addWidget(self.character_list, 1) # Allow list to stretch vertically

        # Character Management Buttons Section (Add/Delete)
        char_manage_layout = QHBoxLayout() # Layout for adding/deleting characters from the list
        char_manage_layout.setSpacing(10)
        self.new_char_input = QLineEdit() # Input for new character name
        self.new_char_input.setPlaceholderText("Add new show/character name")
        self.add_char_button = QPushButton("➕ Add") # Button to add new character
        self.delete_char_button = QPushButton("🗑️ Delete Selected") # Button to delete selected characters
        self.add_char_button.clicked.connect(self.add_new_character) # Connect add button
        self.new_char_input.returnPressed.connect(self.add_char_button.click) # Allow adding on Enter key press
        self.delete_char_button.clicked.connect(self.delete_selected_character) # Connect delete button
        char_manage_layout.addWidget(self.new_char_input, 2) # Give more space to input field
        char_manage_layout.addWidget(self.add_char_button, 1)
        char_manage_layout.addWidget(self.delete_char_button, 1)
        left_layout.addLayout(char_manage_layout) # Add management buttons layout to main left layout
        left_layout.addStretch(0) # Prevent excessive stretching at the bottom of left panel

        # --- Right Panel (Logs) ---
        log_title_layout = QHBoxLayout() # Layout for log title and utility buttons (verbosity, reset)
        self.progress_log_label = QLabel("📜 Progress Log:") # Main label for the log area
        log_title_layout.addWidget(self.progress_log_label)
        log_title_layout.addStretch(1) # Push utility buttons to the right

        # Link Search Input and Button (initially hidden, for "Only Links" mode)
        self.link_search_input = QLineEdit()
        self.link_search_input.setPlaceholderText("Search Links...")
        self.link_search_input.setVisible(False) # Hidden by default
        self.link_search_input.setFixedWidth(150)
        log_title_layout.addWidget(self.link_search_input)
        self.link_search_button = QPushButton("🔍") # Search icon button
        self.link_search_button.setToolTip("Filter displayed links")
        self.link_search_button.setVisible(False) # Hidden by default
        self.link_search_button.setFixedWidth(30)
        self.link_search_button.setStyleSheet("padding: 4px 4px;") # Compact padding
        log_title_layout.addWidget(self.link_search_button)

        # Manga Rename Toggle Button (initially hidden, for Manga Mode)
        self.manga_rename_toggle_button = QPushButton() # Text set by _update_manga_filename_style_button_text
        self.manga_rename_toggle_button.setVisible(False) # Hidden by default
        self.manga_rename_toggle_button.setFixedWidth(140) # Adjusted width for text
        self.manga_rename_toggle_button.setStyleSheet("padding: 4px 8px;")
        self._update_manga_filename_style_button_text() # Set initial text based on loaded style
        log_title_layout.addWidget(self.manga_rename_toggle_button)

        # Log Verbosity Toggle Button
        self.log_verbosity_button = QPushButton("Show Basic Log") # Button to toggle log detail
        self.log_verbosity_button.setToolTip("Toggle between full and basic log details.")
        self.log_verbosity_button.setFixedWidth(110) # Fixed width
        self.log_verbosity_button.setStyleSheet("padding: 4px 8px;")
        log_title_layout.addWidget(self.log_verbosity_button)

        # Reset Button
        self.reset_button = QPushButton("🔄 Reset") # Button to reset application state
        self.reset_button.setToolTip("Reset all inputs and logs to default state (only when idle).")
        self.reset_button.setFixedWidth(80)
        self.reset_button.setStyleSheet("padding: 4px 8px;")
        log_title_layout.addWidget(self.reset_button)
        right_layout.addLayout(log_title_layout) # Add log title/utility layout to main right layout

        # Log Output Areas (Splitter for Main and External Logs)
        self.log_splitter = QSplitter(Qt.Vertical) # Vertical splitter for two log areas
        self.main_log_output = QTextEdit() # Main log display
        self.main_log_output.setReadOnly(True) # Make it read-only
        self.main_log_output.setLineWrapMode(QTextEdit.NoWrap) # No wrap for better log readability
        self.main_log_output.setStyleSheet("""
            QTextEdit { background-color: #3C3F41; border: 1px solid #5A5A5A; padding: 5px;
                         color: #F0F0F0; border-radius: 4px; font-family: Consolas, Courier New, monospace; font-size: 9.5pt; }""")
        self.external_log_output = QTextEdit() # External links log display
        self.external_log_output.setReadOnly(True)
        self.external_log_output.setLineWrapMode(QTextEdit.NoWrap)
        self.external_log_output.setStyleSheet("""
            QTextEdit { background-color: #3C3F41; border: 1px solid #5A5A5A; padding: 5px;
                         color: #F0F0F0; border-radius: 4px; font-family: Consolas, Courier New, monospace; font-size: 9.5pt; }""")
        self.external_log_output.hide() # Initially hidden, shown when "Show External Links" is checked
        self.log_splitter.addWidget(self.main_log_output) # Add main log to splitter
        self.log_splitter.addWidget(self.external_log_output) # Add external log to splitter
        self.log_splitter.setSizes([self.height(), 0]) # Main log takes all space initially
        right_layout.addWidget(self.log_splitter, 1) # Allow splitter to stretch vertically

        # Export Links Button (initially hidden, for "Only Links" mode)
        export_button_layout = QHBoxLayout() # Layout to push button to the right
        export_button_layout.addStretch(1) # Push to right
        self.export_links_button = QPushButton("Export Links")
        self.export_links_button.setToolTip("Export all extracted links to a .txt file.")
        self.export_links_button.setFixedWidth(100)
        self.export_links_button.setStyleSheet("padding: 4px 8px; margin-top: 5px;")
        self.export_links_button.setEnabled(False) # Initially disabled
        self.export_links_button.setVisible(False) # Initially hidden
        export_button_layout.addWidget(self.export_links_button)
        right_layout.addLayout(export_button_layout)


        # Progress Labels (Overall and Individual File)
        self.progress_label = QLabel("Progress: Idle") # Label for overall download progress
        self.progress_label.setStyleSheet("padding-top: 5px; font-style: italic;")
        right_layout.addWidget(self.progress_label)
        self.file_progress_label = QLabel("") # Label for individual file download progress
        self.file_progress_label.setWordWrap(True) # Allow text to wrap if long
        self.file_progress_label.setStyleSheet("padding-top: 2px; font-style: italic; color: #A0A0A0;")
        right_layout.addWidget(self.file_progress_label)


        # Add left and right panels to the main splitter
        self.main_splitter.addWidget(left_panel_widget)
        self.main_splitter.addWidget(right_panel_widget)
        # Set initial splitter sizes (e.g., 35% for left controls, 65% for right logs)
        initial_width = self.width()
        left_width = int(initial_width * 0.35)
        right_width = initial_width - left_width
        self.main_splitter.setSizes([left_width, right_width])

        # Set main layout for the window
        top_level_layout = QHBoxLayout(self) # Top-level layout for the main window
        top_level_layout.setContentsMargins(0,0,0,0) # No margins for the top-level layout itself
        top_level_layout.addWidget(self.main_splitter) # Add the main splitter to the window's layout

        # Initial UI state updates based on defaults and loaded settings
        self.update_ui_for_subfolders(self.use_subfolders_checkbox.isChecked())
        self.update_external_links_setting(self.external_links_checkbox.isChecked())
        self.update_multithreading_label(self.thread_count_input.text())
        self.update_page_range_enabled_state() # Call after link_input is created
        if self.manga_mode_checkbox: # Ensure checkbox exists before accessing
            self.update_ui_for_manga_mode(self.manga_mode_checkbox.isChecked()) # Call after manga_mode_checkbox created
        if hasattr(self, 'link_input'): self.link_input.textChanged.connect(self.update_page_range_enabled_state) # Connect page range update
        self.load_known_names_from_util() # Load known names into the list widget
        self._handle_multithreading_toggle(self.use_multithreading_checkbox.isChecked()) # Set initial state of thread count input
        if hasattr(self, 'radio_group') and self.radio_group.checkedButton(): # Ensure radio group and a checked button exist
            self._handle_filter_mode_change(self.radio_group.checkedButton(), True) # Set initial UI based on default radio selection
        self._update_manga_filename_style_button_text() # Set initial text for manga rename button
        self._update_skip_scope_button_text() # Set initial text for skip scope button


    def get_dark_theme(self):
        """Returns a string containing CSS for a dark theme."""
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
        QSplitter::handle { background-color: #5A5A5A; /* Thicker handle for easier grabbing */ }
        QSplitter::handle:horizontal { width: 5px; }
        QSplitter::handle:vertical { height: 5px; }
        /* Style for QFrame used as a separator or container if needed */
        QFrame[frameShape="4"], QFrame[frameShape="5"] { /* HLine, VLine */
            border: 1px solid #4A4A4A; /* Darker line for subtle separation */
            border-radius: 3px;
        }
        """

    def browse_directory(self):
        """Opens a dialog to select the download directory."""
        # Get current directory from input if valid, otherwise use home directory or last used
        current_dir = self.dir_input.text() if os.path.isdir(self.dir_input.text()) else ""
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", current_dir)
        if folder: # If a folder was selected
            self.dir_input.setText(folder) # Update the directory input field

    def handle_main_log(self, message):
        """Appends a message to the main log output area, handling HTML and basic log mode."""
        is_html_message = message.startswith(HTML_PREFIX) # Check if message is flagged as HTML
        display_message = message
        use_html = False

        if is_html_message:
             display_message = message[len(HTML_PREFIX):] # Remove HTML prefix
             use_html = True
        elif self.basic_log_mode: # If basic log mode is active, filter messages
            # Keywords that indicate a message should be shown in basic mode
            basic_keywords = [
                '🚀 starting download', '🏁 download finished', '🏁 download cancelled', # Start/End messages
                '❌', '⚠️', '✅ all posts processed', '✅ reached end of posts', # Errors, Warnings, Key Milestones
                'summary:', 'progress:', '[fetcher]', # Summaries, Progress, Fetcher logs
                'critical error', 'import error', 'error', 'fail', 'timeout', # Specific error types
                'unsupported url', 'invalid url', 'no posts found', 'could not create directory', # Common operational issues
                'missing dependency', 'high thread count', 'manga mode filter warning', # Configuration/Setup warnings
                'duplicate name', 'potential name conflict', 'invalid filter name', # Known list issues
                'no valid character filters' # Filter issues
            ]
            message_lower = message.lower() # For case-insensitive keyword check
            if not any(keyword in message_lower for keyword in basic_keywords):
                 # Allow specific success messages even in basic mode if they are not too verbose
                 if not message.strip().startswith("✅ Saved:") and \
                    not message.strip().startswith("✅ Added") and \
                    not message.strip().startswith("✅ Application reset complete"):
                    return # Skip message if not matching keywords and not an allowed specific success message
        
        try:
             # Sanitize null characters that can crash QTextEdit
             safe_message = str(display_message).replace('\x00', '[NULL]')
             if use_html:
                 self.main_log_output.insertHtml(safe_message) # Insert as HTML
             else:
                 self.main_log_output.append(safe_message) # Append as plain text

             # Auto-scroll if the scrollbar is near the bottom
             scrollbar = self.main_log_output.verticalScrollBar()
             if scrollbar.value() >= scrollbar.maximum() - 30: # Threshold for auto-scroll
                 scrollbar.setValue(scrollbar.maximum()) # Scroll to the bottom
        except Exception as e:
             # Fallback print if GUI logging fails for some reason
             print(f"GUI Main Log Error: {e}\nOriginal Message: {message}")


    def _is_download_active(self):
        """Checks if any download process (single or multi-threaded for posts) is currently active."""
        single_thread_active = self.download_thread and self.download_thread.isRunning()
        # Check if thread_pool exists and has any non-done futures
        pool_active = self.thread_pool is not None and any(not f.done() for f in self.active_futures if f is not None)
        return single_thread_active or pool_active


    def handle_external_link_signal(self, post_title, link_text, link_url, platform):
        """Handles external links found by worker threads by adding them to a queue for processing."""
        link_data = (post_title, link_text, link_url, platform)
        self.external_link_queue.append(link_data) # Add to queue
        if self.radio_only_links and self.radio_only_links.isChecked():
            self.extracted_links_cache.append(link_data) # Also add to cache for "Only Links" mode display
        self._try_process_next_external_link() # Attempt to process immediately or schedule

    def _try_process_next_external_link(self):
        """Processes the next external link from the queue with appropriate delays to avoid flooding the UI."""
        if self._is_processing_external_link_queue or not self.external_link_queue:
             # Already processing or queue is empty, so return
             return

        # Determine if links should be displayed in the external log or main log (for "Only Links" mode)
        is_only_links_mode = self.radio_only_links and self.radio_only_links.isChecked()
        should_display_in_external_log = self.show_external_links and not is_only_links_mode

        if not (is_only_links_mode or should_display_in_external_log):
             # Neither "Only Links" mode nor "Show External Links" is active for displaying this link now.
             # It's queued, but we don't need to display it immediately.
             self._is_processing_external_link_queue = False # Ensure flag is reset
             if self.external_link_queue: # If there are still items, try again later (e.g., if settings change)
                 QTimer.singleShot(0, self._try_process_next_external_link) # Check again soon
             return

        self._is_processing_external_link_queue = True # Set flag that we are processing one
        link_data = self.external_link_queue.popleft() # Get the next link from the queue

        # Apply different delays based on context to manage UI updates
        if is_only_links_mode:
            # Shorter delay for "Only Links" mode as it's the primary output
            delay_ms = 80 # milliseconds
            QTimer.singleShot(delay_ms, lambda data=link_data: self._display_and_schedule_next(data))
        elif self._is_download_active(): # If a download is active, use a longer, randomized delay
            delay_ms = random.randint(4000, 8000) # 4-8 seconds
            QTimer.singleShot(delay_ms, lambda data=link_data: self._display_and_schedule_next(data))
        else: # No download active, process with minimal delay
            QTimer.singleShot(0, lambda data=link_data: self._display_and_schedule_next(data))


    def _display_and_schedule_next(self, link_data):
        """Displays a single external link and schedules the processing of the next one from the queue."""
        post_title, link_text, link_url, platform = link_data
        is_only_links_mode = self.radio_only_links and self.radio_only_links.isChecked()

        # Format link for display (truncate long link text)
        max_link_text_len = 35
        display_text = link_text[:max_link_text_len].strip() + "..." if len(link_text) > max_link_text_len else link_text
        formatted_link_info = f"{display_text} - {link_url} - {platform}"
        separator = "-" * 45 # Separator for visual grouping by post in "Only Links" mode

        if is_only_links_mode:
            # In "Only Links" mode, display in the main log
            if post_title != self._current_link_post_title: # If it's a new post title
                self.log_signal.emit(HTML_PREFIX + "<br>" + separator + "<br>") # Add separator and space using HTML
                title_html = f'<b style="color: #87CEEB;">{post_title}</b><br>' # Make post title prominent
                self.log_signal.emit(HTML_PREFIX + title_html) # Emit title as HTML
                self._current_link_post_title = post_title # Update current title tracker
            self.log_signal.emit(formatted_link_info) # Emit the link info as plain text
        elif self.show_external_links: # If "Show External Links" is checked (and not "Only Links" mode)
            # Display in the dedicated external links log
             self._append_to_external_log(formatted_link_info, separator) # Pass separator for consistency if needed

        # Reset flag and try to process the next link in the queue
        self._is_processing_external_link_queue = False
        self._try_process_next_external_link()


    def _append_to_external_log(self, formatted_link_text, separator):
        """Appends a formatted link to the external log output if it's visible."""
        if not (self.external_log_output and self.external_log_output.isVisible()):
            return # Don't append if log area is hidden

        try:
            # Append the formatted link text
            self.external_log_output.append(formatted_link_text)
            self.external_log_output.append("") # Add a blank line for spacing between links

            # Auto-scroll if near the bottom
            scrollbar = self.external_log_output.verticalScrollBar()
            if scrollbar.value() >= scrollbar.maximum() - 50: # Threshold for auto-scroll
                scrollbar.setValue(scrollbar.maximum()) # Scroll to bottom
        except Exception as e:
             # Fallback if GUI logging fails
             self.log_signal.emit(f"GUI External Log Append Error: {e}\nOriginal Message: {formatted_link_text}") # Log to main log as fallback
             print(f"GUI External Log Error (Append): {e}\nOriginal Message: {formatted_link_text}")


    def update_file_progress_display(self, filename, downloaded_bytes, total_bytes):
        """Updates the label showing individual file download progress."""
        if not filename and total_bytes == 0 and downloaded_bytes == 0: # Clear signal
            self.file_progress_label.setText("") # Clear the progress label
            return

        max_filename_len = 25 # Max length for filename part of the string for display
        display_filename = filename
        if len(filename) > max_filename_len: # Truncate if too long
            display_filename = filename[:max_filename_len-3].strip() + "..." 

        # Format progress text
        if total_bytes > 0: # If total size is known
            downloaded_mb = downloaded_bytes / (1024 * 1024)
            total_mb = total_bytes / (1024 * 1024)
            progress_text = f"Downloading '{display_filename}' ({downloaded_mb:.1f}MB / {total_mb:.1f}MB)"
        else: # If total size is unknown
             downloaded_mb = downloaded_bytes / (1024 * 1024)
             progress_text = f"Downloading '{display_filename}' ({downloaded_mb:.1f}MB)"

        # Further shorten if the whole string is too long for the UI label
        if len(progress_text) > 75: # Heuristic length limit for the label
             # Shorter truncate for filename if the whole string is still too long
             display_filename = filename[:15].strip() + "..." if len(filename) > 18 else display_filename 
             if total_bytes > 0: progress_text = f"DL '{display_filename}' ({downloaded_mb:.1f}/{total_mb:.1f}MB)"
             else: progress_text = f"DL '{display_filename}' ({downloaded_mb:.1f}MB)"

        self.file_progress_label.setText(progress_text) # Update the label text


    def update_external_links_setting(self, checked):
        """Handles changes to the 'Show External Links in Log' checkbox, updating UI visibility."""
        is_only_links_mode = self.radio_only_links and self.radio_only_links.isChecked()
        is_only_archives_mode = self.radio_only_archives and self.radio_only_archives.isChecked() # Check new mode

        # External links log is not shown for "Only Links" or "Only Archives" mode, regardless of checkbox state
        if is_only_links_mode or is_only_archives_mode:
             if self.external_log_output: self.external_log_output.hide() # Hide external log
             if self.log_splitter: self.log_splitter.setSizes([self.height(), 0]) # Main log takes all space
             # self.show_external_links should ideally be false if these modes are active,
             # and the checkbox should be disabled by _handle_filter_mode_change.
             return # Exit early, no further action needed for these modes

        self.show_external_links = checked # Update the internal flag based on checkbox state
        if checked:
            # Show the external log area
            if self.external_log_output: self.external_log_output.show()
            if self.log_splitter: self.log_splitter.setSizes([self.height() // 2, self.height() // 2]) # Split space between logs
            if self.main_log_output: self.main_log_output.setMinimumHeight(50) # Ensure some min height for main log
            if self.external_log_output: self.external_log_output.setMinimumHeight(50) # Ensure min height for external log
            self.log_signal.emit("\n" + "="*40 + "\n🔗 External Links Log Enabled\n" + "="*40) # Log change
            if self.external_log_output: # Clear and add title if showing external log
                self.external_log_output.clear()
                self.external_log_output.append("🔗 External Links Found:")
            self._try_process_next_external_link() # Process any queued links now that log is visible
        else:
            # Hide the external log area
            if self.external_log_output: self.external_log_output.hide()
            if self.log_splitter: self.log_splitter.setSizes([self.height(), 0]) # Main log takes all space
            if self.main_log_output: self.main_log_output.setMinimumHeight(0) # Reset min height
            if self.external_log_output: self.external_log_output.setMinimumHeight(0) # Reset min height
            if self.external_log_output: self.external_log_output.clear() # Clear content when hiding
            self.log_signal.emit("\n" + "="*40 + "\n🔗 External Links Log Disabled\n" + "="*40) # Log change


    def _handle_filter_mode_change(self, button, checked):
        """Handles changes in the file filter radio buttons, updating UI accordingly."""
        if not button or not checked: # Only act on the button that was toggled to 'checked'
            return

        filter_mode_text = button.text() # Get text of the selected radio button
        is_only_links = (filter_mode_text == "🔗 Only Links")
        is_only_archives = (filter_mode_text == "📦 Only Archives") # Check for "Only Archives" mode

        # --- Visibility of Link-Specific UI (Search, Export) ---
        if self.link_search_input: self.link_search_input.setVisible(is_only_links)
        if self.link_search_button: self.link_search_button.setVisible(is_only_links)
        if self.export_links_button:
            self.export_links_button.setVisible(is_only_links)
            # Enable export button only if in links mode and there are cached links
            self.export_links_button.setEnabled(is_only_links and bool(self.extracted_links_cache))
        if not is_only_links and self.link_search_input: self.link_search_input.clear() # Clear search if not in links mode

        # --- Enable/Disable State of General Download-Related Widgets ---
        # File download mode is active if NOT "Only Links" mode
        file_download_mode_active = not is_only_links

        # Widgets generally active for file downloads (All, Images, Videos, Archives)
        if self.dir_input: self.dir_input.setEnabled(file_download_mode_active)
        if self.dir_button: self.dir_button.setEnabled(file_download_mode_active)
        if self.use_subfolders_checkbox: self.use_subfolders_checkbox.setEnabled(file_download_mode_active)
        # Skip words input and scope button are relevant if downloading files
        if self.skip_words_input: self.skip_words_input.setEnabled(file_download_mode_active)
        if self.skip_scope_toggle_button: self.skip_scope_toggle_button.setEnabled(file_download_mode_active)
        
        # --- Skip Archive Checkboxes Logic ---
        # Enabled if NOT "Only Links" AND NOT "Only Archives"
        # Unchecked and disabled if "Only Archives" mode is selected
        if self.skip_zip_checkbox:
            can_skip_zip = not is_only_links and not is_only_archives
            self.skip_zip_checkbox.setEnabled(can_skip_zip)
            if is_only_archives:
                self.skip_zip_checkbox.setChecked(False) # Ensure unchecked in "Only Archives" mode
        
        if self.skip_rar_checkbox:
            can_skip_rar = not is_only_links and not is_only_archives
            self.skip_rar_checkbox.setEnabled(can_skip_rar)
            if is_only_archives:
                self.skip_rar_checkbox.setChecked(False) # Ensure unchecked in "Only Archives" mode

        # --- Other File Processing Checkboxes (Thumbnails, Compression) ---
        # Enabled if NOT "Only Links" AND NOT "Only Archives"
        other_file_proc_enabled = not is_only_links and not is_only_archives
        if self.download_thumbnails_checkbox: self.download_thumbnails_checkbox.setEnabled(other_file_proc_enabled)
        if self.compress_images_checkbox: self.compress_images_checkbox.setEnabled(other_file_proc_enabled)
        
        # --- External Links Checkbox Logic ---
        # Enabled if NOT "Only Links" AND NOT "Only Archives"
        if self.external_links_checkbox: 
            can_show_external_log_option = not is_only_links and not is_only_archives
            self.external_links_checkbox.setEnabled(can_show_external_log_option)
            if not can_show_external_log_option: # If disabled due to current mode
                 self.external_links_checkbox.setChecked(False) # Uncheck it


        # --- Log Area and Specific Mode UI Updates ---
        if is_only_links: # "Only Links" mode specific UI
            self.progress_log_label.setText("📜 Extracted Links Log:") # Change log label
            if self.external_log_output: self.external_log_output.hide() # Hide separate external log area
            if self.log_splitter: self.log_splitter.setSizes([self.height(), 0]) # Main log takes all space
            if self.main_log_output: self.main_log_output.clear(); self.main_log_output.setMinimumHeight(0) # Clear main log
            if self.external_log_output: self.external_log_output.clear(); self.external_log_output.setMinimumHeight(0) # Clear external log
            self.log_signal.emit("="*20 + " Mode changed to: Only Links " + "="*20) # Log mode change
            self._filter_links_log() # Refresh link log display based on current cache and search
            self._try_process_next_external_link() # Process any queued links for this mode
        elif is_only_archives: # "Only Archives" mode specific UI
            self.progress_log_label.setText("📜 Progress Log (Archives Only):") # Change log label
            if self.external_log_output: self.external_log_output.hide() # Hide external links log for archives mode
            if self.log_splitter: self.log_splitter.setSizes([self.height(), 0]) # Main log takes all space
            if self.main_log_output: self.main_log_output.clear() # Clear main log for new mode
            self.log_signal.emit("="*20 + " Mode changed to: Only Archives " + "="*20) # Log mode change
        else: # All, Images, Videos modes
            self.progress_log_label.setText("📜 Progress Log:") # Default log label
            # For these modes, the external links log visibility depends on its checkbox state
            self.update_external_links_setting(self.external_links_checkbox.isChecked() if self.external_links_checkbox else False)
            self.log_signal.emit(f"="*20 + f" Mode changed to: {filter_mode_text} " + "="*20) # Log mode change

        # --- Common UI Updates based on current states (called after mode-specific changes) ---
        # Update subfolder related UI (character filter, per-post subfolder checkbox, custom folder input)
        if self.use_subfolders_checkbox: # Ensure it exists
             self.update_ui_for_subfolders(self.use_subfolders_checkbox.isChecked())
        
        # Update visibility of custom folder input (depends on single post URL and subfolder settings)
        self.update_custom_folder_visibility()


    def _filter_links_log(self):
        """Filters and displays links in the main log when 'Only Links' mode is active, based on search input."""
        if not (self.radio_only_links and self.radio_only_links.isChecked()): return # Only run in "Only Links" mode

        search_term = self.link_search_input.text().lower().strip() if self.link_search_input else ""
        self.main_log_output.clear() # Clear previous content from the main log
        current_title_for_display = None # To group links by post title in the display
        separator = "-" * 45 # Visual separator between post sections

        # Iterate through the cached extracted links
        for post_title, link_text, link_url, platform in self.extracted_links_cache:
            # Check if any part of the link data matches the search term (case-insensitive)
            matches_search = (
                not search_term or # Show all if no search term is provided
                search_term in link_text.lower() or
                search_term in link_url.lower() or
                search_term in platform.lower()
            )
            if matches_search: # If the link matches the search criteria
                if post_title != current_title_for_display: # If it's a new post section
                    self.main_log_output.insertHtml("<br>" + separator + "<br>") # Add separator and space using HTML
                    title_html = f'<b style="color: #87CEEB;">{post_title}</b><br>' # Format post title
                    self.main_log_output.insertHtml(title_html) # Insert title as HTML
                    current_title_for_display = post_title # Update current title tracker
                
                # Format and display the link information
                max_link_text_len = 35 # Truncate long link text for display
                display_text = link_text[:max_link_text_len].strip() + "..." if len(link_text) > max_link_text_len else link_text
                formatted_link_info = f"{display_text} - {link_url} - {platform}"
                self.main_log_output.append(formatted_link_info) # Append link info as plain text

        if self.main_log_output.toPlainText().strip(): # Add a final newline if content was added
            self.main_log_output.append("")
        self.main_log_output.verticalScrollBar().setValue(0) # Scroll to top of the log


    def _export_links_to_file(self):
        """Exports extracted links to a text file when in 'Only Links' mode."""
        if not (self.radio_only_links and self.radio_only_links.isChecked()):
            QMessageBox.information(self, "Export Links", "Link export is only available in 'Only Links' mode.")
            return
        if not self.extracted_links_cache:
            QMessageBox.information(self, "Export Links", "No links have been extracted yet.")
            return

        # Suggest a default filename for the export
        default_filename = "extracted_links.txt"
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Links", default_filename, "Text Files (*.txt);;All Files (*)")

        if filepath: # If a filepath was chosen
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    current_title_for_export = None # To group links by post title in the file
                    separator = "-" * 60 + "\n" # Separator for file content
                    for post_title, link_text, link_url, platform in self.extracted_links_cache:
                        if post_title != current_title_for_export: # If it's a new post section
                            if current_title_for_export is not None: # Add separator before new post section (if not the first)
                                f.write("\n" + separator + "\n")
                            f.write(f"Post Title: {post_title}\n\n") # Write post title
                            current_title_for_export = post_title # Update current title tracker
                        # Write link details
                        f.write(f"  {link_text} - {link_url} - {platform}\n")
                self.log_signal.emit(f"✅ Links successfully exported to: {filepath}")
                QMessageBox.information(self, "Export Successful", f"Links exported to:\n{filepath}")
            except Exception as e:
                self.log_signal.emit(f"❌ Error exporting links: {e}")
                QMessageBox.critical(self, "Export Error", f"Could not export links: {e}")


    def get_filter_mode(self):
        """Determines the backend filter mode ('all', 'image', 'video', 'archive') based on radio button selection."""
        if self.radio_only_links and self.radio_only_links.isChecked():
            # Backend expects 'all' for link extraction, even if UI says "Only Links",
            # as the worker will then be told to extract_links_only.
            return 'all' 
        elif self.radio_images.isChecked():
            return 'image'
        elif self.radio_videos.isChecked():
            return 'video'
        elif self.radio_only_archives and self.radio_only_archives.isChecked(): # Check for "Only Archives" mode
            return 'archive'
        elif self.radio_all.isChecked(): # Explicitly check for 'All' if others aren't matched
            return 'all'
        return 'all' # Default if somehow no button is checked (should not happen with QButtonGroup)


    def get_skip_words_scope(self):
        """Returns the current scope for skip words (files, posts, or both) from the internal attribute."""
        return self.skip_words_scope


    def _update_skip_scope_button_text(self):
        """Updates the text of the skip scope toggle button based on the current self.skip_words_scope."""
        if self.skip_scope_toggle_button: # Ensure button exists
            if self.skip_words_scope == SKIP_SCOPE_FILES:
                self.skip_scope_toggle_button.setText("Scope: Files")
            elif self.skip_words_scope == SKIP_SCOPE_POSTS:
                self.skip_scope_toggle_button.setText("Scope: Posts")
            elif self.skip_words_scope == SKIP_SCOPE_BOTH:
                self.skip_scope_toggle_button.setText("Scope: Both")
            else: # Should not happen if logic is correct
                self.skip_scope_toggle_button.setText("Scope: Unknown")


    def _cycle_skip_scope(self):
        """Cycles through the available skip word scopes (Files -> Posts -> Both -> Files) and updates UI and settings."""
        if self.skip_words_scope == SKIP_SCOPE_FILES:
            self.skip_words_scope = SKIP_SCOPE_POSTS
        elif self.skip_words_scope == SKIP_SCOPE_POSTS:
            self.skip_words_scope = SKIP_SCOPE_BOTH
        elif self.skip_words_scope == SKIP_SCOPE_BOTH:
            self.skip_words_scope = SKIP_SCOPE_FILES
        else: # Default to files if current state is unknown (should not occur)
            self.skip_words_scope = SKIP_SCOPE_FILES
        
        self._update_skip_scope_button_text() # Update button text to reflect new scope
        self.settings.setValue(SKIP_WORDS_SCOPE_KEY, self.skip_words_scope) # Save the new scope to settings
        self.log_signal.emit(f"ℹ️ Skip words scope changed to: '{self.skip_words_scope}'") # Log the change


    def add_new_character(self):
        """Adds a new character/show name to the known list, with validation and conflict checks."""
        global KNOWN_NAMES, clean_folder_name # Ensure we use the potentially shared KNOWN_NAMES and utility function
        name_to_add = self.new_char_input.text().strip() # Get name from input and strip whitespace
        if not name_to_add: # Check for empty input
             QMessageBox.warning(self, "Input Error", "Name cannot be empty."); return False # Indicate failure

        name_lower = name_to_add.lower() # For case-insensitive comparisons
        # Check for exact duplicates (case-insensitive)
        if any(existing.lower() == name_lower for existing in KNOWN_NAMES):
             QMessageBox.warning(self, "Duplicate Name", f"The name '{name_to_add}' (case-insensitive) already exists."); return False

        # Check for potential conflicts (substrings or superstrings)
        similar_names_details = []
        for existing_name in KNOWN_NAMES:
            existing_name_lower = existing_name.lower()
            # Check if new name is in existing OR existing is in new name (but not identical)
            if name_lower != existing_name_lower and (name_lower in existing_name_lower or existing_name_lower in name_lower):
                similar_names_details.append((name_to_add, existing_name)) # Store pair for message

        if similar_names_details: # If potential conflicts found
            first_similar_new, first_similar_existing = similar_names_details[0]
            # Determine which name is shorter for the example message to illustrate potential grouping issue
            shorter, longer = sorted([first_similar_new, first_similar_existing], key=len)

            # Warn user about potential conflict and ask for confirmation
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Potential Name Conflict")
            msg_box.setText(
                f"The name '{first_similar_new}' is very similar to an existing name: '{first_similar_existing}'.\n\n"
                f"This could lead to files being grouped into less specific folders (e.g., under '{clean_folder_name(shorter)}' instead of a more specific '{clean_folder_name(longer)}').\n\n"
                "Do you want to change the name you are adding, or proceed anyway?"
            )
            change_button = msg_box.addButton("Change Name", QMessageBox.RejectRole) # Option to change
            proceed_button = msg_box.addButton("Proceed Anyway", QMessageBox.AcceptRole) # Option to proceed
            msg_box.setDefaultButton(proceed_button) # Default to proceed
            msg_box.setEscapeButton(change_button) # Escape cancels/changes
            msg_box.exec_()

            if msg_box.clickedButton() == change_button: # If user chose to change
                self.log_signal.emit(f"ℹ️ User chose to change '{first_similar_new}' due to similarity with '{first_similar_existing}'.")
                return False # Indicate user chose to change, so don't add this one

            # If user chose to proceed, log it
            self.log_signal.emit(f"⚠️ User proceeded with adding '{first_similar_new}' despite similarity with '{first_similar_existing}'.")

        # If no conflict or user chose to proceed, add the name to KNOWN_NAMES
        KNOWN_NAMES.append(name_to_add)
        KNOWN_NAMES.sort(key=str.lower) # Keep the list sorted case-insensitively

        # Update UI list (QListWidget)
        self.character_list.clear()
        self.character_list.addItems(KNOWN_NAMES)
        self.filter_character_list(self.character_search_input.text()) # Re-apply search filter if any

        self.log_signal.emit(f"✅ Added '{name_to_add}' to known names list.")
        self.new_char_input.clear() # Clear input field after adding
        self.save_known_names() # Persist changes to the config file
        return True # Indicate success


    def delete_selected_character(self):
        """Deletes selected character/show names from the known list and UI."""
        global KNOWN_NAMES # Ensure we use the potentially shared KNOWN_NAMES
        selected_items = self.character_list.selectedItems() # Get selected items from QListWidget
        if not selected_items: # If no items selected
             QMessageBox.warning(self, "Selection Error", "Please select one or more names to delete."); return

        names_to_remove = {item.text() for item in selected_items} # Get unique names to remove
        # Confirm deletion with the user
        confirm = QMessageBox.question(self, "Confirm Deletion",
                                       f"Are you sure you want to delete {len(names_to_remove)} name(s)?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No) # Default to No
        if confirm == QMessageBox.Yes:
            original_count = len(KNOWN_NAMES)
            # Filter out the names to remove from KNOWN_NAMES (modify in-place)
            KNOWN_NAMES[:] = [n for n in KNOWN_NAMES if n not in names_to_remove]
            removed_count = original_count - len(KNOWN_NAMES)

            if removed_count > 0: # If names were actually removed
                 self.log_signal.emit(f"🗑️ Removed {removed_count} name(s).")
                 # Update UI list
                 self.character_list.clear()
                 self.character_list.addItems(KNOWN_NAMES)
                 self.filter_character_list(self.character_search_input.text()) # Re-apply search filter
                 self.save_known_names() # Persist changes to config file
            else: # Should not happen if items were selected, but good to handle
                 self.log_signal.emit("ℹ️ No names were removed (they might not have been in the list).")


    def update_custom_folder_visibility(self, url_text=None):
        """Shows or hides the custom folder input based on URL type (single post) and subfolder settings."""
        if url_text is None: # If called without arg (e.g., from other UI changes that affect this)
            url_text = self.link_input.text() # Get current URL from input

        _, _, post_id = extract_post_info(url_text.strip()) # Check if it's a single post URL
        
        is_single_post_url = bool(post_id) # True if a post ID was extracted
        # Subfolders must be generally enabled for custom folder to be relevant
        subfolders_enabled = self.use_subfolders_checkbox.isChecked() if self.use_subfolders_checkbox else False
        
        # Custom folder input is NOT relevant if in "Only Links" or "Only Archives" mode,
        # as these modes might not use folder structures in the same way or at all.
        not_only_links_or_archives_mode = not (
            (self.radio_only_links and self.radio_only_links.isChecked()) or
            (self.radio_only_archives and self.radio_only_archives.isChecked())
        )

        # Show custom folder input if all conditions are met:
        # 1. It's a single post URL.
        # 2. "Separate Folders by Name/Title" (main subfolder option) is checked.
        # 3. It's NOT "Only Links" or "Only Archives" mode.
        should_show_custom_folder = is_single_post_url and subfolders_enabled and not_only_links_or_archives_mode
        
        if self.custom_folder_widget: # Ensure custom folder widget exists
            self.custom_folder_widget.setVisible(should_show_custom_folder) # Set visibility

        # If the custom folder input is hidden, clear its content
        if not (self.custom_folder_widget and self.custom_folder_widget.isVisible()):
            if self.custom_folder_input: self.custom_folder_input.clear()


    def update_ui_for_subfolders(self, checked): 
        """Updates UI elements related to subfolder settings (character filter, per-post subfolder checkbox)."""
        # "Only Links" and "Only Archives" modes generally don't use character-based subfolders or per-post subfolders.
        is_only_links = self.radio_only_links and self.radio_only_links.isChecked()
        is_only_archives = self.radio_only_archives and self.radio_only_archives.isChecked()

        # Character filter and per-post subfolder options are relevant if:
        # 1. The main "Separate Folders by Name/Title" (passed as 'checked' arg) is ON.
        # 2. It's NOT "Only Links" mode AND NOT "Only Archives" mode.
        enable_char_and_post_subfolder_options = checked and not is_only_links and not is_only_archives

        # Character filter widget visibility
        if self.character_filter_widget: # Ensure widget exists
            self.character_filter_widget.setVisible(enable_char_and_post_subfolder_options)
            if not self.character_filter_widget.isVisible() and self.character_input: 
                self.character_input.clear() # Clear character input if hidden

        # "Subfolder per Post" checkbox enabled state
        if self.use_subfolder_per_post_checkbox: # Ensure checkbox exists
            self.use_subfolder_per_post_checkbox.setEnabled(enable_char_and_post_subfolder_options)
            if not enable_char_and_post_subfolder_options: # If disabled by current conditions
                self.use_subfolder_per_post_checkbox.setChecked(False) # Also uncheck it
        
        # Update custom folder visibility, as it depends on subfolder settings too
        self.update_custom_folder_visibility()


    def update_page_range_enabled_state(self):
        """Enables/disables page range inputs based on URL type (creator feed vs single post) and Manga Mode."""
        url_text = self.link_input.text().strip() if self.link_input else ""
        _, _, post_id = extract_post_info(url_text) # Check if it's a single post URL

        is_creator_feed = not post_id if url_text else False # True if URL is present and not a post URL
        # Manga mode overrides page range (downloads all posts, sorted oldest first)
        manga_mode_active = self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False

        # Enable page range if it's a creator feed AND Manga Mode is OFF
        enable_page_range = is_creator_feed and not manga_mode_active

        # Enable/disable page range UI elements
        for widget in [self.page_range_label, self.start_page_input, self.to_label, self.end_page_input]:
            if widget: widget.setEnabled(enable_page_range)

        # If page range is disabled, clear the input fields
        if not enable_page_range:
            if self.start_page_input: self.start_page_input.clear()
            if self.end_page_input: self.end_page_input.clear()


    def _update_manga_filename_style_button_text(self):
        """Updates the text and tooltip of the manga filename style toggle button based on current style."""
        if self.manga_rename_toggle_button: # Ensure button exists
            if self.manga_filename_style == STYLE_POST_TITLE:
                self.manga_rename_toggle_button.setText("Name: Post Title")
                self.manga_rename_toggle_button.setToolTip(
                    "Manga files: First file named by post title. Subsequent files in same post keep original names.\n"
                    "Click to change to original file names for all files."
                )
            elif self.manga_filename_style == STYLE_ORIGINAL_NAME:
                self.manga_rename_toggle_button.setText("Name: Original File")
                self.manga_rename_toggle_button.setToolTip(
                    "Manga files will keep their original names as provided by the site (e.g., 001.jpg, page_01.png).\n"
                    "Click to change to post title based naming for the first file."
                )
            else: # Fallback for unknown style (should not happen)
                self.manga_rename_toggle_button.setText("Name: Unknown Style")
                self.manga_rename_toggle_button.setToolTip("Manga filename style is in an unknown state.")


    def _toggle_manga_filename_style(self):
        """Toggles the manga filename style between 'post_title' and 'original_name', updates UI and settings."""
        current_style = self.manga_filename_style
        new_style = ""

        if current_style == STYLE_POST_TITLE: # If current is Post Title, switch to Original Name
            new_style = STYLE_ORIGINAL_NAME
            # Optional: Warn user if they switch away from the recommended style for manga
            reply = QMessageBox.information(self, "Manga Filename Preference",
                                           "Using 'Name: Post Title' (first file by title, others original) is recommended for Manga Mode.\n\n"
                                           "Using 'Name: Original File' for all files might lead to less organized downloads if original names are inconsistent or non-sequential.\n\n"
                                           "Proceed with using 'Name: Original File' for all files?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No) # Default to No
            if reply == QMessageBox.No: # If user cancels the change
                self.log_signal.emit("ℹ️ Manga filename style change to 'Original File' cancelled by user.")
                return # Don't change if user cancels
        elif current_style == STYLE_ORIGINAL_NAME: # If current is Original Name, switch to Post Title
            new_style = STYLE_POST_TITLE
        else: # If current style is unknown (e.g., corrupted setting), reset to default
            self.log_signal.emit(f"⚠️ Unknown current manga filename style: {current_style}. Resetting to default ('{STYLE_POST_TITLE}').")
            new_style = STYLE_POST_TITLE

        self.manga_filename_style = new_style # Update internal attribute
        self.settings.setValue(MANGA_FILENAME_STYLE_KEY, self.manga_filename_style) # Save new style to settings
        self.settings.sync() # Ensure setting is written to disk
        self._update_manga_filename_style_button_text() # Update button UI text and tooltip
        self.log_signal.emit(f"ℹ️ Manga filename style changed to: '{self.manga_filename_style}'") # Log the change


    def update_ui_for_manga_mode(self, checked): # 'checked' is the state of the manga_mode_checkbox
        """Updates UI elements based on Manga Mode state (checkbox state and URL type)."""
        url_text = self.link_input.text().strip() if self.link_input else ""
        _, _, post_id = extract_post_info(url_text) # Check if it's a single post URL

        # Manga mode is only applicable to creator feeds (not single posts)
        is_creator_feed = not post_id if url_text else False

        # Enable/disable the Manga Mode checkbox itself based on whether it's a creator feed
        if self.manga_mode_checkbox: # Ensure checkbox exists
            self.manga_mode_checkbox.setEnabled(is_creator_feed)
            if not is_creator_feed and self.manga_mode_checkbox.isChecked(): # If URL changes to single post, uncheck manga mode
                self.manga_mode_checkbox.setChecked(False)
                # 'checked' variable (passed in) might now be stale, so re-evaluate based on checkbox's current state
                checked = self.manga_mode_checkbox.isChecked() 

        # Manga mode is effectively ON if the checkbox is checked AND it's a creator feed
        manga_mode_effectively_on = is_creator_feed and checked # Use the potentially updated 'checked' value

        # Show/hide the manga filename style toggle button
        if self.manga_rename_toggle_button: # Ensure button exists
            self.manga_rename_toggle_button.setVisible(manga_mode_effectively_on)

        # If manga mode is on, page range is disabled (as it downloads all posts, sorted)
        if manga_mode_effectively_on:
            if self.page_range_label: self.page_range_label.setEnabled(False)
            if self.start_page_input: self.start_page_input.setEnabled(False); self.start_page_input.clear()
            if self.to_label: self.to_label.setEnabled(False)
            if self.end_page_input: self.end_page_input.setEnabled(False); self.end_page_input.clear()
        else: # If manga mode is off (or not applicable), re-evaluate page range normally
            self.update_page_range_enabled_state()


    def filter_character_list(self, search_text):
        """Filters the QListWidget of known characters based on the provided search text."""
        search_text_lower = search_text.lower() # For case-insensitive search
        for i in range(self.character_list.count()): # Iterate through all items in the list
            item = self.character_list.item(i)
            # Hide item if search text is not in item text (case-insensitive)
            item.setHidden(search_text_lower not in item.text().lower())


    def update_multithreading_label(self, text): # 'text' is the current text of thread_count_input
        """Updates the multithreading checkbox text to show the current thread count if enabled."""
        if self.use_multithreading_checkbox.isChecked(): # If multithreading is enabled
            try:
                num_threads_val = int(text) # Convert input text to integer
                if num_threads_val > 0 : self.use_multithreading_checkbox.setText(f"Use Multithreading ({num_threads_val} Threads)")
                else: self.use_multithreading_checkbox.setText("Use Multithreading (Invalid: >0)") # Should be caught by validator
            except ValueError: # If text is not a valid integer
                self.use_multithreading_checkbox.setText("Use Multithreading (Invalid Input)")
        else: # If multithreading is unchecked, it implies 1 thread (main thread operation)
            self.use_multithreading_checkbox.setText("Use Multithreading (1 Thread)")


    def _handle_multithreading_toggle(self, checked): # 'checked' is the state of use_multithreading_checkbox
        """Enables/disables the thread count input based on the multithreading checkbox state."""
        if not checked: # Multithreading disabled (checkbox unchecked)
            self.thread_count_input.setEnabled(False) # Disable thread count input
            self.thread_count_label.setEnabled(False) # Disable thread count label
            # Update checkbox text to reflect single-threaded operation
            self.use_multithreading_checkbox.setText("Use Multithreading (1 Thread)")
        else: # Multithreading enabled (checkbox checked)
            self.thread_count_input.setEnabled(True) # Enable thread count input
            self.thread_count_label.setEnabled(True) # Enable thread count label
            # Update checkbox text based on current value in thread_count_input
            self.update_multithreading_label(self.thread_count_input.text())


    def update_progress_display(self, total_posts, processed_posts):
        """Updates the overall progress label in the UI."""
        if total_posts > 0: # If total number of posts is known
            progress_percent = (processed_posts / total_posts) * 100
            self.progress_label.setText(f"Progress: {processed_posts} / {total_posts} posts ({progress_percent:.1f}%)")
        elif processed_posts > 0 : # If total is unknown but some posts are processed (e.g., single post mode)
             self.progress_label.setText(f"Progress: Processing post {processed_posts}...")
        else: # Initial state or no posts found yet
            self.progress_label.setText("Progress: Starting...")
        
        # Clear individual file progress when overall progress updates (unless it's a clear signal for file progress)
        if total_posts > 0 or processed_posts > 0 :
            self.file_progress_label.setText("") # Clear individual file progress label


    def start_download(self):
        """Initiates the download process based on current UI settings and validations."""
        # Ensure access to global/utility functions and classes from downloader_utils
        global KNOWN_NAMES, BackendDownloadThread, PostProcessorWorker, extract_post_info, clean_folder_name, MAX_FILE_THREADS_PER_POST_OR_WORKER
        
        if self._is_download_active(): # Prevent multiple concurrent downloads from starting
            QMessageBox.warning(self, "Busy", "A download is already running."); return

        # --- Gather all settings from UI ---
        api_url = self.link_input.text().strip()
        output_dir = self.dir_input.text().strip()
        
        use_subfolders = self.use_subfolders_checkbox.isChecked()
        # Per-post subfolders only make sense if main subfolders are also enabled
        use_post_subfolders = self.use_subfolder_per_post_checkbox.isChecked() and use_subfolders
        compress_images = self.compress_images_checkbox.isChecked()
        download_thumbnails = self.download_thumbnails_checkbox.isChecked()
        
        use_multithreading_enabled_by_checkbox = self.use_multithreading_checkbox.isChecked()
        try: # Get and validate thread count from GUI
            num_threads_from_gui = int(self.thread_count_input.text().strip())
            if num_threads_from_gui < 1: num_threads_from_gui = 1 # Ensure at least 1 thread
        except ValueError: # If input is not a valid integer
            QMessageBox.critical(self, "Thread Count Error", "Invalid number of threads. Please enter a positive number.")
            self.set_ui_enabled(True) # Re-enable UI if error occurs before download starts
            return
            
        raw_skip_words = self.skip_words_input.text().strip() # Get raw skip words string
        # Parse skip words into a list of lowercase, stripped words
        skip_words_list = [word.strip().lower() for word in raw_skip_words.split(',') if word.strip()]
        current_skip_words_scope = self.get_skip_words_scope() # Get current scope for skip words
        manga_mode_is_checked = self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False
        
        # Determine filter mode and if only links are being extracted
        extract_links_only = (self.radio_only_links and self.radio_only_links.isChecked())
        backend_filter_mode = self.get_filter_mode() # This will be 'archive' if that radio button is selected
        # Get text of the selected filter radio button for logging purposes
        user_selected_filter_text = self.radio_group.checkedButton().text() if self.radio_group.checkedButton() else "All"

        # Determine effective skip_zip and skip_rar based on the selected filter mode
        # If "Only Archives" mode is selected, we want to download archives, so skip flags must be False.
        if backend_filter_mode == 'archive':
            effective_skip_zip = False
            effective_skip_rar = False
        else: # For other modes (All, Images, Videos, Only Links), respect the checkbox states
            effective_skip_zip = self.skip_zip_checkbox.isChecked()
            effective_skip_rar = self.skip_rar_checkbox.isChecked()

        # --- Validations ---
        if not api_url: QMessageBox.critical(self, "Input Error", "URL is required."); return
        # Output directory is required unless only extracting links
        if not extract_links_only and not output_dir:
             QMessageBox.critical(self, "Input Error", "Download Directory is required when not in 'Only Links' mode."); return
        
        service, user_id, post_id_from_url = extract_post_info(api_url) # Extract info from URL
        if not service or not user_id: # Basic URL validation (must have service and user ID)
            QMessageBox.critical(self, "Input Error", "Invalid or unsupported URL format."); return

        # Create output directory if it doesn't exist (and not in links-only mode)
        if not extract_links_only and not os.path.isdir(output_dir):
            reply = QMessageBox.question(self, "Create Directory?",
                                         f"The directory '{output_dir}' does not exist.\nCreate it now?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) # Default to Yes
            if reply == QMessageBox.Yes:
                try: os.makedirs(output_dir, exist_ok=True); self.log_signal.emit(f"ℹ️ Created directory: {output_dir}")
                except Exception as e: QMessageBox.critical(self, "Directory Error", f"Could not create directory: {e}"); return
            else: self.log_signal.emit("❌ Download cancelled: Output directory does not exist and was not created."); return

        # Check for Pillow library if image compression is enabled
        if compress_images and Image is None: # Image is None if Pillow import failed
            QMessageBox.warning(self, "Missing Dependency", "Pillow library (for image compression) not found. Compression will be disabled.")
            compress_images = False; self.compress_images_checkbox.setChecked(False) # Update UI and flag

        # Manga mode is only applicable for creator feeds (not single posts)
        manga_mode = manga_mode_is_checked and not post_id_from_url


        # Page range validation (only if not manga mode and it's a creator feed)
        start_page_str, end_page_str = self.start_page_input.text().strip(), self.end_page_input.text().strip()
        start_page, end_page = None, None # Initialize to None
        is_creator_feed = bool(not post_id_from_url) # True if URL is present and not a single post URL
        if is_creator_feed and not manga_mode: # Page range applies only to creator feeds not in manga mode
            try: # Validate page range inputs
                if start_page_str: start_page = int(start_page_str)
                if end_page_str: end_page = int(end_page_str)
                if start_page is not None and start_page <= 0: raise ValueError("Start page must be positive.")
                if end_page is not None and end_page <= 0: raise ValueError("End page must be positive.")
                if start_page and end_page and start_page > end_page: raise ValueError("Start page cannot be greater than end page.")
            except ValueError as e: QMessageBox.critical(self, "Page Range Error", f"Invalid page range: {e}"); return
        elif manga_mode: # In manga mode, ignore page range inputs (downloads all)
            start_page, end_page = None, None 

        # --- Reset state for new download ---
        self.external_link_queue.clear(); self.extracted_links_cache = []; self._is_processing_external_link_queue = False; self._current_link_post_title = None
        self.all_kept_original_filenames = [] # Reset list of filenames that kept their original names

        # Character filter validation and prompt (if subfolders enabled and not links only mode)
        raw_character_filters_text = self.character_input.text().strip()
        # Parse character filters from comma-separated string
        parsed_character_list = [name.strip() for name in raw_character_filters_text.split(',') if name.strip()] if raw_character_filters_text else None
        filter_character_list_to_pass = None # This will be passed to the backend download logic

        # Validate character filters if subfolders are used, it's a creator feed, and not extracting only links
        if use_subfolders and parsed_character_list and not post_id_from_url and not extract_links_only:
            self.log_signal.emit(f"ℹ️ Validating character filters for subfolder naming: {', '.join(parsed_character_list)}")
            valid_filters_for_backend = [] # List of filters confirmed to be valid
            user_cancelled_validation = False # Flag if user cancels during validation
            for char_name in parsed_character_list:
                cleaned_name_test = clean_folder_name(char_name) # Test if name is valid for a folder name
                if not cleaned_name_test: # If cleaning results in empty or invalid name
                    QMessageBox.warning(self, "Invalid Filter Name", f"Filter name '{char_name}' is invalid for a folder and will be skipped.")
                    self.log_signal.emit(f"⚠️ Skipping invalid filter for folder: '{char_name}'"); continue

                # Check if name is in known list (Known.txt), prompt to add if not
                if char_name.lower() not in {kn.lower() for kn in KNOWN_NAMES}:
                    reply = QMessageBox.question(self, "Add Filter Name to Known List?",
                                               f"Filter '{char_name}' is not in known names list.\nAdd it now?",
                                               QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
                    if reply == QMessageBox.Yes: # User wants to add
                        self.new_char_input.setText(char_name) # Pre-fill input for user convenience
                        if self.add_new_character(): # Try to add it (this calls save_known_names)
                            self.log_signal.emit(f"✅ Added '{char_name}' to known names via filter prompt.")
                            valid_filters_for_backend.append(char_name) # Add to list to pass if successful
                        else: # Add failed (e.g., user cancelled sub-prompt or conflict during add_new_character)
                            self.log_signal.emit(f"⚠️ Failed to add '{char_name}' via filter prompt (might have been a conflict or cancellation).")
                            # Still add if it was a valid folder name, even if not added to known list, for this run
                            if cleaned_name_test: valid_filters_for_backend.append(char_name)
                    elif reply == QMessageBox.Cancel: # User cancelled the whole download process
                        self.log_signal.emit(f"❌ Download cancelled during filter validation for '{char_name}'."); user_cancelled_validation = True; break
                    else: # User chose No (don't add to known list, but proceed with filter for this run)
                        self.log_signal.emit(f"ℹ️ Proceeding with filter '{char_name}' without adding to known list.")
                        if cleaned_name_test: valid_filters_for_backend.append(char_name) # Add if valid folder name
                else: # Already in known list
                    if cleaned_name_test: valid_filters_for_backend.append(char_name) # Add if valid folder name

            if user_cancelled_validation: return # Stop if user cancelled during prompt

            if valid_filters_for_backend: # If there are valid filters after validation
                filter_character_list_to_pass = valid_filters_for_backend
                self.log_signal.emit(f"   Using validated character filters for subfolders: {', '.join(filter_character_list_to_pass)}")
            else: # If no valid filters remain
                self.log_signal.emit("⚠️ No valid character filters remaining for subfolder naming (after validation).")
        elif parsed_character_list : # If not using subfolders or it's a single post, still pass the list for other filtering purposes (e.g., file content filtering)
            filter_character_list_to_pass = parsed_character_list
            self.log_signal.emit(f"ℹ️ Character filters provided: {', '.join(filter_character_list_to_pass)} (Subfolder rules may differ or not apply).")


        # Manga mode warning if no character filter is provided (as filter is used for naming/folder)
        if manga_mode and not filter_character_list_to_pass and not extract_links_only:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Manga Mode Filter Warning")
            msg_box.setText(
                "Manga Mode is enabled, but 'Filter by Character(s)' is empty.\n\n"
                "For best results (correct file naming and folder organization if subfolders are on), "
                "please enter the Manga/Series title into the filter field.\n\n"
                "Proceed without a filter (names might be generic, folder might be less specific)?"
            )
            proceed_button = msg_box.addButton("Proceed Anyway", QMessageBox.AcceptRole)
            cancel_button = msg_box.addButton("Cancel Download", QMessageBox.RejectRole)
            msg_box.exec_()
            if msg_box.clickedButton() == cancel_button: # If user cancels
                self.log_signal.emit("❌ Download cancelled due to Manga Mode filter warning."); return
            else: # User proceeds
                self.log_signal.emit("⚠️ Proceeding with Manga Mode without a specific title filter.")


        # Custom folder name for single post downloads
        custom_folder_name_cleaned = None # Initialize
        # Check if custom folder input is relevant and visible
        if use_subfolders and post_id_from_url and self.custom_folder_widget and self.custom_folder_widget.isVisible() and not extract_links_only: 
            raw_custom_name = self.custom_folder_input.text().strip() # Get raw custom folder name
            if raw_custom_name: # If a name was provided
                 cleaned_custom = clean_folder_name(raw_custom_name) # Clean it for folder usage
                 if cleaned_custom: custom_folder_name_cleaned = cleaned_custom # Use if valid
                 else: self.log_signal.emit(f"⚠️ Invalid custom folder name ignored: '{raw_custom_name}' (resulted in empty string after cleaning).")


        # --- Clear logs and reset progress counters ---
        self.main_log_output.clear() # Clear main log
        if extract_links_only: self.main_log_output.append("🔗 Extracting Links..."); # Initial message for links mode
        elif backend_filter_mode == 'archive': self.main_log_output.append("📦 Downloading Archives Only...") # Log for new archive mode
        
        if self.external_log_output: self.external_log_output.clear() # Clear external log
        # Show external log title only if it's relevant for the current mode and setting
        if self.show_external_links and not extract_links_only and backend_filter_mode != 'archive': 
            self.external_log_output.append("🔗 External Links Found:")
        
        self.file_progress_label.setText(""); self.cancellation_event.clear(); self.active_futures = [] # Reset progress and cancellation
        self.total_posts_to_process = self.processed_posts_count = self.download_counter = self.skip_counter = 0 # Reset counters
        self.progress_label.setText("Progress: Initializing...") # Initial progress message

        # Determine effective number of threads for posts and files based on settings
        effective_num_post_workers = 1 # Default for single post or non-multithreaded creator feed
        effective_num_file_threads_per_worker = 1 # Default number of file download threads per worker
        
        if post_id_from_url: # Single post URL
            if use_multithreading_enabled_by_checkbox: # Use GUI thread count for file downloads for this single post
                effective_num_file_threads_per_worker = max(1, min(num_threads_from_gui, MAX_FILE_THREADS_PER_POST_OR_WORKER))
        else: # Creator feed URL
            if use_multithreading_enabled_by_checkbox: # If multithreading is enabled for creator feed
                effective_num_post_workers = max(1, min(num_threads_from_gui, MAX_THREADS)) # For concurrent post processing
                # The same GUI thread count is also used as the *max* for files per worker, capped appropriately
                effective_num_file_threads_per_worker = max(1, min(num_threads_from_gui, MAX_FILE_THREADS_PER_POST_OR_WORKER))


        # --- Log initial download parameters to the main log ---
        log_messages = ["="*40, f"🚀 Starting {'Link Extraction' if extract_links_only else ('Archive Download' if backend_filter_mode == 'archive' else 'Download')} @ {time.strftime('%Y-%m-%d %H:%M:%S')}", f"   URL: {api_url}"]
        if not extract_links_only: log_messages.append(f"   Save Location: {output_dir}")
        
        if post_id_from_url: # Logging for Single Post download
            log_messages.append(f"   Mode: Single Post")
            log_messages.append(f"     ↳ File Downloads: Up to {effective_num_file_threads_per_worker} concurrent file(s)")
        else: # Logging for Creator Feed download
            log_messages.append(f"   Mode: Creator Feed")
            log_messages.append(f"   Post Processing: {'Multi-threaded (' + str(effective_num_post_workers) + ' workers)' if effective_num_post_workers > 1 else 'Single-threaded (1 worker)'}")
            log_messages.append(f"     ↳ File Downloads per Worker: Up to {effective_num_file_threads_per_worker} concurrent file(s)")
            if is_creator_feed: # Only log page range for creator feeds
                if manga_mode: log_messages.append("   Page Range: All (Manga Mode - Oldest Posts Processed First)")
                else: # Construct a readable page range string for logging
                    pr_log = "All" # Default if no pages specified
                    if start_page or end_page: 
                        pr_log = f"{f'From {start_page} ' if start_page else ''}{'to ' if start_page and end_page else ''}{f'{end_page}' if end_page else (f'Up to {end_page}' if end_page else (f'From {start_page}' if start_page else 'Specific Range'))}".strip()
                    log_messages.append(f"   Page Range: {pr_log if pr_log else 'All'}")


        if not extract_links_only: # Settings relevant to file downloading
            log_messages.append(f"   Subfolders: {'Enabled' if use_subfolders else 'Disabled'}")
            if use_subfolders: # Log subfolder naming details
                 if custom_folder_name_cleaned: log_messages.append(f"   Custom Folder (Post): '{custom_folder_name_cleaned}'")
                 elif filter_character_list_to_pass and not post_id_from_url: log_messages.append(f"   Character Filters for Folders: {', '.join(filter_character_list_to_pass)}")
                 else: log_messages.append(f"   Folder Naming: Automatic (based on title/known names)")
                 log_messages.append(f"   Subfolder per Post: {'Enabled' if use_post_subfolders else 'Disabled'}")

            log_messages.extend([
                f"   File Type Filter: {user_selected_filter_text} (Backend processing as: {backend_filter_mode})",
                f"   Skip Archives: {'.zip' if effective_skip_zip else ''}{', ' if effective_skip_zip and effective_skip_rar else ''}{'.rar' if effective_skip_rar else ''}{'None (Archive Mode)' if backend_filter_mode == 'archive' else ('None' if not (effective_skip_zip or effective_skip_rar) else '')}", # Clarify for archive mode
                f"   Skip Words (posts/files): {', '.join(skip_words_list) if skip_words_list else 'None'}",
                f"   Skip Words Scope: {current_skip_words_scope.capitalize()}",
                f"   Compress Images: {'Enabled' if compress_images else 'Disabled'}",
                f"   Thumbnails Only: {'Enabled' if download_thumbnails else 'Disabled'}"
            ])
        else: # Link extraction mode logging
            log_messages.append(f"   Mode: Extracting Links Only")

        # Log external links setting (relevant unless in "Only Links" or "Only Archives" mode where it's forced off)
        log_messages.append(f"   Show External Links: {'Enabled' if self.show_external_links and not extract_links_only and backend_filter_mode != 'archive' else 'Disabled'}")
        
        if manga_mode: # Manga mode specific logs
            log_messages.append(f"   Manga Mode (File Renaming by Post Title): Enabled")
            log_messages.append(f"     ↳ Manga Filename Style: {'Post Title Based' if self.manga_filename_style == STYLE_POST_TITLE else 'Original File Name'}")

        # Determine if multithreading for posts is actually used for logging
        # It's used if checkbox is checked AND it's a creator feed (not single post)
        should_use_multithreading_for_posts = use_multithreading_enabled_by_checkbox and not post_id_from_url
        log_messages.append(f"   Threading: {'Multi-threaded (posts)' if should_use_multithreading_for_posts else 'Single-threaded (posts)'}")
        if should_use_multithreading_for_posts: # Log number of post workers only if actually using them
            log_messages.append(f"   Number of Post Worker Threads: {effective_num_post_workers}")
        log_messages.append("="*40) # End of parameter logging
        for msg in log_messages: self.log_signal.emit(msg) # Emit all log messages

        # --- Disable UI and prepare for download ---
        self.set_ui_enabled(False) # Disable UI elements during download

        unwanted_keywords_for_folders = {'spicy', 'hd', 'nsfw', '4k', 'preview', 'teaser', 'clip'} # Example set of keywords to avoid in folder names
        
        # --- Prepare arguments dictionary for backend thread/worker ---
        # This template holds all possible arguments that might be needed by either single or multi-threaded download logic
        args_template = {
            'api_url_input': api_url,
            'download_root': output_dir, # Used by PostProcessorWorker if it creates folders
            'output_dir': output_dir, # Passed to DownloadThread for consistency (though it might use download_root)
            'known_names': list(KNOWN_NAMES), # Pass a copy of the current known names
            'known_names_copy': list(KNOWN_NAMES), # Legacy, ensure it's there if used by older parts of backend
            'filter_character_list': filter_character_list_to_pass,
            'filter_mode': backend_filter_mode, # 'all', 'image', 'video', or 'archive'
            'skip_zip': effective_skip_zip, # Use the determined effective value based on mode
            'skip_rar': effective_skip_rar, # Use the determined effective value based on mode
            'use_subfolders': use_subfolders,
            'use_post_subfolders': use_post_subfolders,
            'compress_images': compress_images,
            'download_thumbnails': download_thumbnails,
            'service': service, # Extracted from URL
            'user_id': user_id, # Extracted from URL
            'downloaded_files': self.downloaded_files, # Pass shared set for session-based skip
            'downloaded_files_lock': self.downloaded_files_lock, # Pass shared lock
            'downloaded_file_hashes': self.downloaded_file_hashes, # Pass shared set for hash-based skip
            'downloaded_file_hashes_lock': self.downloaded_file_hashes_lock, # Pass shared lock
            'skip_words_list': skip_words_list,
            'skip_words_scope': current_skip_words_scope,
            'show_external_links': self.show_external_links, # For worker to know if it should emit external_link_signal
            'extract_links_only': extract_links_only, # For worker to know if it should only extract links
            'start_page': start_page, # Validated start page
            'end_page': end_page, # Validated end page
            'target_post_id_from_initial_url': post_id_from_url, # The specific post ID if a single post URL was given
            'custom_folder_name': custom_folder_name_cleaned, # Cleaned custom folder name for single post
            'manga_mode_active': manga_mode, # Flag for manga mode
            'unwanted_keywords': unwanted_keywords_for_folders, # For folder naming logic in worker
            'cancellation_event': self.cancellation_event, # Shared cancellation event for all threads/workers
            'signals': self.worker_signals, # Signals object for PostProcessorWorker instances to communicate back to GUI
            'manga_filename_style': self.manga_filename_style, # Current manga filename style
            # Pass the effective number of file threads for the worker/post processor to use internally
            'num_file_threads_for_worker': effective_num_file_threads_per_worker
        }

        # --- Start download (single-threaded for posts or multi-threaded for posts) ---
        try:
            if should_use_multithreading_for_posts: # Multi-threaded for posts (creator feed with multithreading enabled)
                self.log_signal.emit(f"   Initializing multi-threaded {'link extraction' if extract_links_only else 'download'} with {effective_num_post_workers} post workers...")
                self.start_multi_threaded_download(num_post_workers=effective_num_post_workers, **args_template)
            else: # Single-threaded for posts (either single post URL or creator feed with multithreading off)
                self.log_signal.emit(f"   Initializing single-threaded {'link extraction' if extract_links_only else 'download'}...")
                # Define keys expected by BackendDownloadThread constructor for clarity and to avoid passing unexpected args
                dt_expected_keys = [
                    'api_url_input', 'output_dir', 'known_names_copy', 'cancellation_event',
                    'filter_character_list', 'filter_mode', 'skip_zip', 'skip_rar',
                    'use_subfolders', 'use_post_subfolders', 'custom_folder_name',
                    'compress_images', 'download_thumbnails', 'service', 'user_id',
                    'downloaded_files', 'downloaded_file_hashes',
                    'downloaded_files_lock', 'downloaded_file_hashes_lock',
                    'skip_words_list', 'skip_words_scope', 'show_external_links', 'extract_links_only',
                    'num_file_threads_for_worker', # This is for the PostProcessorWorker that BackendDownloadThread might create
                    'skip_current_file_flag', # Event for skipping a single file (if feature existed)
                    'start_page', 'end_page', 'target_post_id_from_initial_url',
                    'manga_mode_active', 'unwanted_keywords', 'manga_filename_style'
                ]
                # For single threaded (post) download, the 'num_file_threads_for_worker' from args_template
                # will be used by the PostProcessorWorker if it needs to download multiple files for that single post.
                args_template['skip_current_file_flag'] = None # Ensure this is explicitly set (or passed if it were a feature)
                # Filter args_template to only include keys expected by BackendDownloadThread constructor
                single_thread_args = {key: args_template[key] for key in dt_expected_keys if key in args_template}
                self.start_single_threaded_download(**single_thread_args) # Start the single download thread
        except Exception as e: # Catch any errors during the preparation/start of download
            self.log_signal.emit(f"❌ CRITICAL ERROR preparing download: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Start Error", f"Failed to start process:\n{e}")
            self.download_finished(0,0,False, []) # Ensure UI is re-enabled and state is reset


    def start_single_threaded_download(self, **kwargs):
        """Starts the download process in a single QThread (BackendDownloadThread).
           This thread handles post fetching and then processes each post sequentially (though file downloads within a post can be multi-threaded by PostProcessorWorker).
        """
        global BackendDownloadThread # The class imported from downloader_utils
        try:
            self.download_thread = BackendDownloadThread(**kwargs) # Instantiate with all necessary arguments
            # Connect signals from the backend thread to GUI handler methods
            if hasattr(self.download_thread, 'progress_signal'): self.download_thread.progress_signal.connect(self.handle_main_log)
            if hasattr(self.download_thread, 'add_character_prompt_signal'): self.download_thread.add_character_prompt_signal.connect(self.add_character_prompt_signal)
            if hasattr(self.download_thread, 'finished_signal'): self.download_thread.finished_signal.connect(self.download_finished)
            # For character prompt response flowing back from GUI to the backend thread
            if hasattr(self.download_thread, 'receive_add_character_result'): self.character_prompt_response_signal.connect(self.download_thread.receive_add_character_result)
            if hasattr(self.download_thread, 'external_link_signal'): self.download_thread.external_link_signal.connect(self.handle_external_link_signal)
            if hasattr(self.download_thread, 'file_progress_signal'): self.download_thread.file_progress_signal.connect(self.update_file_progress_display)

            self.download_thread.start() # Start the QThread
            self.log_signal.emit("✅ Single download thread (for posts) started.")
        except Exception as e: # Catch errors during thread instantiation or start
            self.log_signal.emit(f"❌ CRITICAL ERROR starting single-thread: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Thread Start Error", f"Failed to start download process: {e}")
            self.download_finished(0,0,False, []) # Ensure UI is re-enabled and state is reset


    def start_multi_threaded_download(self, num_post_workers, **kwargs):
        """Starts the download process using a ThreadPoolExecutor for fetching and processing posts concurrently."""
        global PostProcessorWorker # The worker class from downloader_utils
        # Ensure thread pool is created if it doesn't exist or was previously shut down
        if self.thread_pool is None:
            self.thread_pool = ThreadPoolExecutor(max_workers=num_post_workers, thread_name_prefix='PostWorker_')
        
        self.active_futures = [] # Reset list of active futures for this download run
        # Reset progress counters for this run
        self.processed_posts_count = 0; self.total_posts_to_process = 0; self.download_counter = 0; self.skip_counter = 0
        self.all_kept_original_filenames = [] # Reset list of kept original filenames for this run

        # 'num_file_threads_for_worker' is already in kwargs from the main start_download logic.
        # This will be passed to each PostProcessorWorker instance created by _fetch_and_queue_posts.

        # Start a separate Python thread (not QThread) to fetch post data and submit tasks to the pool.
        # This prevents the GUI from freezing during the initial API calls to get all post data,
        # especially for large creator feeds.
        fetcher_thread = threading.Thread(
            target=self._fetch_and_queue_posts, # Method to run in the new thread
            args=(kwargs['api_url_input'], kwargs, num_post_workers), # Pass API URL, base args, and worker count
            daemon=True, # Daemon thread will exit when the main application exits
            name="PostFetcher" # Name for the thread (useful for debugging)
        )
        fetcher_thread.start() # Start the fetcher thread
        self.log_signal.emit(f"✅ Post fetcher thread started. {num_post_workers} post worker threads initializing...")


    def _fetch_and_queue_posts(self, api_url_input_for_fetcher, worker_args_template, num_post_workers):
        """
        (This method runs in a separate Python thread, not the main GUI thread)
        Fetches all post data using download_from_api and submits each post as a task to the ThreadPoolExecutor.
        """
        global PostProcessorWorker, download_from_api # Ensure access to these from downloader_utils
        all_posts_data = [] # List to store all fetched post data
        fetch_error_occurred = False # Flag to track if an error occurs during fetching
        manga_mode_active_for_fetch = worker_args_template.get('manga_mode_active', False) # Get manga mode status

        # Ensure signals object is available for workers (it's created in DownloaderApp.__init__)
        signals_for_worker = worker_args_template.get('signals')
        if not signals_for_worker: # This should not happen if setup is correct
             self.log_signal.emit("❌ CRITICAL ERROR: Signals object missing for worker in _fetch_and_queue_posts.");
             self.finished_signal.emit(0,0,True, []); # Signal failure to GUI
             return

        try: # Fetch post data from API
            self.log_signal.emit("   Fetching post data from API (this may take a moment for large feeds)...")
            post_generator = download_from_api( # Call the API fetching function from downloader_utils
                api_url_input_for_fetcher,
                logger=lambda msg: self.log_signal.emit(f"[Fetcher] {msg}"), # Prefix fetcher logs for clarity
                start_page=worker_args_template.get('start_page'),
                end_page=worker_args_template.get('end_page'),
                manga_mode=manga_mode_active_for_fetch, # Pass manga mode for correct fetching order
                cancellation_event=self.cancellation_event # Pass shared cancellation event
            )

            for posts_batch in post_generator: # download_from_api yields batches of posts
                if self.cancellation_event.is_set(): # Check for cancellation
                    fetch_error_occurred = True; self.log_signal.emit("   Post fetching cancelled by user."); break
                if isinstance(posts_batch, list): # Ensure API returned a list
                    all_posts_data.extend(posts_batch) # Add fetched posts to the list
                    self.total_posts_to_process = len(all_posts_data) # Update total post count
                    # Log progress periodically for very large feeds to show activity
                    if self.total_posts_to_process > 0 and self.total_posts_to_process % 100 == 0 : # e.g., log every 100 posts
                        self.log_signal.emit(f"   Fetched {self.total_posts_to_process} posts so far...")
                else: # Should not happen if download_from_api is implemented correctly
                    fetch_error_occurred = True; self.log_signal.emit(f"❌ API fetcher returned non-list type: {type(posts_batch)}"); break
            
            if not fetch_error_occurred and not self.cancellation_event.is_set(): # If fetching completed without error/cancellation
                self.log_signal.emit(f"✅ Post fetching complete. Total posts to process: {self.total_posts_to_process}")

        except TypeError as te: # Error in calling download_from_api (e.g., wrong arguments)
            self.log_signal.emit(f"❌ TypeError calling download_from_api: {te}\n   Check 'downloader_utils.py' signature.\n{traceback.format_exc(limit=2)}"); fetch_error_occurred = True
        except RuntimeError as re_err: # Typically from cancellation within fetch_posts_paginated or API errors
            self.log_signal.emit(f"ℹ️ Post fetching runtime error (likely cancellation or API issue): {re_err}"); fetch_error_occurred = True
        except Exception as e: # Other unexpected errors during fetching
            self.log_signal.emit(f"❌ Error during post fetching: {e}\n{traceback.format_exc(limit=2)}"); fetch_error_occurred = True


        if self.cancellation_event.is_set() or fetch_error_occurred:
            # If fetching was cancelled or failed, signal completion to GUI and clean up thread pool
            self.finished_signal.emit(self.download_counter, self.skip_counter, self.cancellation_event.is_set(), self.all_kept_original_filenames)
            if self.thread_pool: self.thread_pool.shutdown(wait=False, cancel_futures=True); self.thread_pool = None # Don't wait if already cancelling
            return

        if self.total_posts_to_process == 0: # No posts found or fetched
            self.log_signal.emit("😕 No posts found or fetched to process.");
            self.finished_signal.emit(0,0,False, []); # Signal completion with zero counts
            return

        # --- Submit fetched posts to the thread pool for processing ---
        self.log_signal.emit(f"   Submitting {self.total_posts_to_process} post processing tasks to thread pool...")
        self.processed_posts_count = 0 # Reset counter for this run
        self.overall_progress_signal.emit(self.total_posts_to_process, 0) # Update GUI progress bar/label
        
        # 'num_file_threads_for_worker' should be in worker_args_template from start_download,
        # this is the number of file download threads each PostProcessorWorker will use.
        num_file_dl_threads_for_each_worker = worker_args_template.get('num_file_threads_for_worker', 1)


        # Define keys expected by PostProcessorWorker constructor for clarity and safety when preparing arguments
        ppw_expected_keys = [
            'post_data', 'download_root', 'known_names', 'filter_character_list', 'unwanted_keywords',
            'filter_mode', 'skip_zip', 'skip_rar', 'use_subfolders', 'use_post_subfolders',
            'target_post_id_from_initial_url', 'custom_folder_name', 'compress_images',
            'download_thumbnails', 'service', 'user_id', 'api_url_input',
            'cancellation_event', 'signals', 'downloaded_files', 'downloaded_file_hashes',
            'downloaded_files_lock', 'downloaded_file_hashes_lock',
            'skip_words_list', 'skip_words_scope', 'show_external_links', 'extract_links_only',
            'num_file_threads', # This will be num_file_dl_threads_for_each_worker for the worker's internal pool
            'skip_current_file_flag', # Event for skipping a single file within a worker (if feature existed)
            'manga_mode_active', 'manga_filename_style'
        ]
        # Keys that are optional for PostProcessorWorker or have defaults defined there
        ppw_optional_keys_with_defaults = {
            'skip_words_list', 'skip_words_scope', 'show_external_links', 'extract_links_only',
            'num_file_threads', 'skip_current_file_flag', 'manga_mode_active', 'manga_filename_style'
            # Note: 'unwanted_keywords' also has a default in the worker if not provided in args
        }


        for post_data_item in all_posts_data: # Iterate through each fetched post data
            if self.cancellation_event.is_set(): break # Stop submitting new tasks if cancellation is requested
            if not isinstance(post_data_item, dict): # Sanity check on post data type
                self.log_signal.emit(f"⚠️ Skipping invalid post data item (not a dict): {type(post_data_item)}");
                self.processed_posts_count += 1; # Count as processed to not hang progress if this happens
                continue

            # Prepare arguments for this specific PostProcessorWorker instance
            worker_init_args = {}; missing_keys = [] # To store args for worker and track any missing ones
            for key in ppw_expected_keys: # Iterate through expected keys for the worker
                if key == 'post_data': worker_init_args[key] = post_data_item # Set the current post's data
                elif key == 'num_file_threads': worker_init_args[key] = num_file_dl_threads_for_each_worker # Set file threads for this worker
                elif key == 'signals': worker_init_args[key] = signals_for_worker # Use the shared signals object for this batch of workers
                elif key in worker_args_template: worker_init_args[key] = worker_args_template[key] # Get from template if available
                elif key in ppw_optional_keys_with_defaults: pass # Worker has a default, so no need to pass if not in template
                else: missing_keys.append(key) # Should not happen if ppw_expected_keys is correct and covers all mandatory args

            if missing_keys: # If any mandatory arguments are missing
                self.log_signal.emit(f"❌ CRITICAL ERROR: Missing keys for PostProcessorWorker: {', '.join(missing_keys)}");
                self.cancellation_event.set(); break # Stop everything if critical args are missing

            try: # Submit the worker task to the thread pool
                worker_instance = PostProcessorWorker(**worker_init_args) # Create worker instance
                if self.thread_pool: # Ensure pool still exists and is active
                    future = self.thread_pool.submit(worker_instance.process) # Submit the worker's process method as a task
                    future.add_done_callback(self._handle_future_result) # Add callback for when this task finishes
                    self.active_futures.append(future) # Keep track of the submitted future
                else: # Pool was shut down or never created (should not happen if logic is correct)
                    self.log_signal.emit("⚠️ Thread pool not available. Cannot submit more tasks."); break
            except TypeError as te: self.log_signal.emit(f"❌ TypeError creating PostProcessorWorker: {te}\n   Passed Args: [{', '.join(sorted(worker_init_args.keys()))}]\n{traceback.format_exc(limit=5)}"); self.cancellation_event.set(); break
            except RuntimeError: self.log_signal.emit("⚠️ Runtime error submitting task (pool likely shutting down)."); break
            except Exception as e: self.log_signal.emit(f"❌ Error submitting post {post_data_item.get('id','N/A')} to worker: {e}"); break

        if not self.cancellation_event.is_set(): self.log_signal.emit(f"   {len(self.active_futures)} post processing tasks submitted to pool.")
        else:
            self.finished_signal.emit(self.download_counter, self.skip_counter, True, self.all_kept_original_filenames)
            if self.thread_pool: self.thread_pool.shutdown(wait=False, cancel_futures=True); self.thread_pool = None

    def _handle_future_result(self, future: Future):
        self.processed_posts_count += 1
        downloaded_files_from_future, skipped_files_from_future = 0, 0
        kept_originals_from_future = []
        try:
            if future.cancelled(): self.log_signal.emit("   A post processing task was cancelled.")
            elif future.exception(): self.log_signal.emit(f"❌ Post processing worker error: {future.exception()}")
            else:
                downloaded_files_from_future, skipped_files_from_future, kept_originals_from_future = future.result()

            with self.downloaded_files_lock:
                self.download_counter += downloaded_files_from_future
                self.skip_counter += skipped_files_from_future

            if kept_originals_from_future:
                self.all_kept_original_filenames.extend(kept_originals_from_future)

            self.overall_progress_signal.emit(self.total_posts_to_process, self.processed_posts_count)
        except Exception as e: self.log_signal.emit(f"❌ Error in _handle_future_result callback: {e}\n{traceback.format_exc(limit=2)}")

        if self.total_posts_to_process > 0 and self.processed_posts_count >= self.total_posts_to_process:
            if all(f.done() for f in self.active_futures):
                QApplication.processEvents()
                self.log_signal.emit("🏁 All submitted post tasks have completed or failed.")
                self.finished_signal.emit(self.download_counter, self.skip_counter, self.cancellation_event.is_set(), self.all_kept_original_filenames)

    def set_ui_enabled(self, enabled):
        widgets_to_toggle = [ self.download_btn, self.link_input, self.radio_all, self.radio_images, self.radio_videos, self.radio_only_links,
            self.skip_zip_checkbox, self.skip_rar_checkbox, self.use_subfolders_checkbox, self.compress_images_checkbox,
            self.download_thumbnails_checkbox, self.use_multithreading_checkbox, self.skip_words_input, self.character_search_input,
            self.new_char_input, self.add_char_button, self.delete_char_button, self.start_page_input, self.end_page_input,
            self.page_range_label, self.to_label, self.character_input, self.custom_folder_input, self.custom_folder_label,
            self.reset_button, self.manga_mode_checkbox, self.manga_rename_toggle_button,
            self.skip_scope_toggle_button # Ensure the new button is in this list
        ]
        
        for widget in widgets_to_toggle:
            if widget: widget.setEnabled(enabled)
        
        if enabled:
            # When re-enabling UI, ensure skip scope button is correctly enabled/disabled by _handle_filter_mode_change
            self._handle_filter_mode_change(self.radio_group.checkedButton(), True)
        # else: # When disabling, the loop above handles the skip_scope_toggle_button

        if self.external_links_checkbox:
            is_only_links = self.radio_only_links and self.radio_only_links.isChecked()
            self.external_links_checkbox.setEnabled(enabled and not is_only_links)

        if self.log_verbosity_button: self.log_verbosity_button.setEnabled(True)

        multithreading_currently_on = self.use_multithreading_checkbox.isChecked()
        self.thread_count_input.setEnabled(enabled and multithreading_currently_on)
        self.thread_count_label.setEnabled(enabled and multithreading_currently_on)

        subfolders_currently_on = self.use_subfolders_checkbox.isChecked()
        self.use_subfolder_per_post_checkbox.setEnabled(enabled and subfolders_currently_on)

        self.cancel_btn.setEnabled(not enabled)

        if enabled:
            # _handle_filter_mode_change is already called above, which should handle the button's enabled state
            self._handle_multithreading_toggle(multithreading_currently_on)
            self.update_ui_for_manga_mode(self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False)

    def cancel_download(self):
        if not self.cancel_btn.isEnabled() and not self.cancellation_event.is_set(): self.log_signal.emit("ℹ️ No active download to cancel or already cancelling."); return
        self.log_signal.emit("⚠️ Requesting cancellation of download process..."); self.cancellation_event.set()
        if self.download_thread and self.download_thread.isRunning(): self.download_thread.requestInterruption(); self.log_signal.emit("   Signaled single download thread to interrupt.")
        if self.thread_pool: self.log_signal.emit("   Initiating immediate shutdown and cancellation of worker pool tasks..."); self.thread_pool.shutdown(wait=False, cancel_futures=True)
        self.external_link_queue.clear(); self._is_processing_external_link_queue = False; self._current_link_post_title = None
        self.cancel_btn.setEnabled(False); self.progress_label.setText("Progress: Cancelling..."); self.file_progress_label.setText("")

    def download_finished(self, total_downloaded, total_skipped, cancelled_by_user, kept_original_names_list=None):
        if kept_original_names_list is None:
            kept_original_names_list = self.all_kept_original_filenames if hasattr(self, 'all_kept_original_filenames') else []
        if kept_original_names_list is None:
            kept_original_names_list = []


        status_message = "Cancelled by user" if cancelled_by_user else "Finished"

        summary_log = "="*40
        summary_log += f"\n🏁 Download {status_message}!\n   Summary: Downloaded Files={total_downloaded}, Skipped Files={total_skipped}\n"
        summary_log += "="*40
        self.log_signal.emit(summary_log)

        if kept_original_names_list:
            intro_msg = (
                HTML_PREFIX +
                "<p>ℹ️ The following files from multi-file manga posts "
                "(after the first file) kept their <b>original names</b>:</p>"
            )
            self.log_signal.emit(intro_msg)

            html_list_items = "<ul>"
            for name in kept_original_names_list:
                html_list_items += f"<li><b>{name}</b></li>"
            html_list_items += "</ul>"

            self.log_signal.emit(HTML_PREFIX + html_list_items)
            self.log_signal.emit("="*40)


        self.progress_label.setText(f"{status_message}: {total_downloaded} downloaded, {total_skipped} skipped."); self.file_progress_label.setText("")
        if not cancelled_by_user: self._try_process_next_external_link()

        if self.download_thread:
            try:
                if hasattr(self.download_thread, 'progress_signal'): self.download_thread.progress_signal.disconnect(self.handle_main_log)
                if hasattr(self.download_thread, 'add_character_prompt_signal'): self.download_thread.add_character_prompt_signal.disconnect(self.add_character_prompt_signal)
                if hasattr(self.download_thread, 'finished_signal'): self.download_thread.finished_signal.disconnect(self.download_finished)
                if hasattr(self.download_thread, 'receive_add_character_result'): self.character_prompt_response_signal.disconnect(self.download_thread.receive_add_character_result)
                if hasattr(self.download_thread, 'external_link_signal'): self.download_thread.external_link_signal.disconnect(self.handle_external_link_signal)
                if hasattr(self.download_thread, 'file_progress_signal'): self.download_thread.file_progress_signal.disconnect(self.update_file_progress_display)
            except (TypeError, RuntimeError) as e: self.log_signal.emit(f"ℹ️ Note during single-thread signal disconnection: {e}")
            self.download_thread = None
        if self.thread_pool: self.log_signal.emit("   Ensuring worker thread pool is shut down..."); self.thread_pool.shutdown(wait=True, cancel_futures=True); self.thread_pool = None
        self.active_futures = []

        self.set_ui_enabled(True); self.cancel_btn.setEnabled(False)

    def toggle_log_verbosity(self):
        self.basic_log_mode = not self.basic_log_mode
        if self.basic_log_mode: self.log_verbosity_button.setText("Show Full Log"); self.log_signal.emit("="*20 + " Basic Log Mode Enabled " + "="*20)
        else: self.log_verbosity_button.setText("Show Basic Log"); self.log_signal.emit("="*20 + " Full Log Mode Enabled " + "="*20)

    def reset_application_state(self):
        if self._is_download_active(): QMessageBox.warning(self, "Reset Error", "Cannot reset while a download is in progress. Please cancel first."); return
        self.log_signal.emit("🔄 Resetting application state to defaults..."); self._reset_ui_to_defaults()
        self.main_log_output.clear(); self.external_log_output.clear()
        if self.show_external_links and not (self.radio_only_links and self.radio_only_links.isChecked()): self.external_log_output.append("🔗 External Links Found:")
        self.external_link_queue.clear(); self.extracted_links_cache = []; self._is_processing_external_link_queue = False; self._current_link_post_title = None
        self.progress_label.setText("Progress: Idle"); self.file_progress_label.setText("")

        with self.downloaded_files_lock: count = len(self.downloaded_files); self.downloaded_files.clear();
        if count > 0: self.log_signal.emit(f"   Cleared {count} downloaded filename(s) from session memory.")
        with self.downloaded_file_hashes_lock: count = len(self.downloaded_file_hashes); self.downloaded_file_hashes.clear();
        if count > 0: self.log_signal.emit(f"   Cleared {count} downloaded file hash(es) from session memory.")

        self.total_posts_to_process = 0; self.processed_posts_count = 0; self.download_counter = 0; self.skip_counter = 0
        self.all_kept_original_filenames = []
        self.cancellation_event.clear(); self.basic_log_mode = False
        if self.log_verbosity_button: self.log_verbosity_button.setText("Show Basic Log")

        self.manga_filename_style = STYLE_POST_TITLE
        self.settings.setValue(MANGA_FILENAME_STYLE_KEY, self.manga_filename_style)
        
        self.skip_words_scope = SKIP_SCOPE_FILES # Reset to default "Files"
        self.settings.setValue(SKIP_WORDS_SCOPE_KEY, self.skip_words_scope)
        self._update_skip_scope_button_text() # Update button text

        self.settings.sync()
        self._update_manga_filename_style_button_text()
        self.update_ui_for_manga_mode(self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False)

        self.log_signal.emit("✅ Application reset complete.")

    def _reset_ui_to_defaults(self):
        self.link_input.clear(); self.dir_input.clear(); self.custom_folder_input.clear(); self.character_input.clear();
        self.skip_words_input.clear(); self.start_page_input.clear(); self.end_page_input.clear(); self.new_char_input.clear();
        self.character_search_input.clear(); self.thread_count_input.setText("4"); self.radio_all.setChecked(True);
        self.skip_zip_checkbox.setChecked(True); self.skip_rar_checkbox.setChecked(True); self.download_thumbnails_checkbox.setChecked(False);
        self.compress_images_checkbox.setChecked(False); self.use_subfolders_checkbox.setChecked(True);
        self.use_subfolder_per_post_checkbox.setChecked(False); self.use_multithreading_checkbox.setChecked(True);
        self.external_links_checkbox.setChecked(False)
        if self.manga_mode_checkbox: self.manga_mode_checkbox.setChecked(False)
        
        self.skip_words_scope = SKIP_SCOPE_FILES # Reset scope variable
        self._update_skip_scope_button_text() # Update button text


        self._handle_filter_mode_change(self.radio_all, True)
        self._handle_multithreading_toggle(self.use_multithreading_checkbox.isChecked())
        self.filter_character_list("")

        self.download_btn.setEnabled(True); self.cancel_btn.setEnabled(False)
        if self.reset_button: self.reset_button.setEnabled(True)
        if self.log_verbosity_button: self.log_verbosity_button.setText("Show Basic Log")

        self._update_manga_filename_style_button_text()
        self.update_ui_for_manga_mode(False)

    def prompt_add_character(self, character_name):
        global KNOWN_NAMES
        reply = QMessageBox.question(self, "Add Filter Name to Known List?", f"The name '{character_name}' was encountered or used as a filter.\nIt's not in your known names list (used for folder suggestions).\nAdd it now?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        result = (reply == QMessageBox.Yes)
        if result:
              self.new_char_input.setText(character_name)
              if self.add_new_character(): self.log_signal.emit(f"✅ Added '{character_name}' to known names via background prompt.")
              else: result = False; self.log_signal.emit(f"ℹ️ Adding '{character_name}' via background prompt was declined or failed.")
        self.character_prompt_response_signal.emit(result)

    def receive_add_character_result(self, result):
        with QMutexLocker(self.prompt_mutex): self._add_character_response = result
        self.log_signal.emit(f"   Main thread received character prompt response: {'Action resulted in addition/confirmation' if result else 'Action resulted in no addition/declined'}")


if __name__ == '__main__':
    import traceback
    try:
        qt_app = QApplication(sys.argv)
        if getattr(sys, 'frozen', False): base_dir = sys._MEIPASS
        else: base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir, 'Kemono.ico')
        if os.path.exists(icon_path): qt_app.setWindowIcon(QIcon(icon_path))
        else: print(f"Warning: Application icon 'Kemono.ico' not found at {icon_path}")

        downloader_app_instance = DownloaderApp()
        downloader_app_instance.show()

        if TourDialog:
            tour_result = TourDialog.run_tour_if_needed(downloader_app_instance)
            if tour_result == QDialog.Accepted: print("Tour completed by user.")
            elif tour_result == QDialog.Rejected: print("Tour skipped or was already shown.")

        exit_code = qt_app.exec_()
        print(f"Application finished with exit code: {exit_code}")
        sys.exit(exit_code)
    except SystemExit: pass
    except Exception as e:
        print("--- CRITICAL APPLICATION ERROR ---")
        print(f"An unhandled exception occurred: {e}")
        traceback.print_exc()
        print("--- END CRITICAL ERROR ---")
        sys.exit(1)
