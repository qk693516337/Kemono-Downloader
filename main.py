import sys
import os
import time
import requests
import re
import threading
import queue
import hashlib
import http.client
import traceback
import subprocess # Added for opening files cross-platform
import random
from collections import deque

from concurrent.futures import ThreadPoolExecutor, CancelledError, Future

from PyQt5.QtGui import (
    QIcon,
    QIntValidator
)
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QListWidget, QRadioButton, QButtonGroup, QCheckBox, QSplitter,
    QDialog, QStackedWidget, QScrollArea,
    QFrame,
    QAbstractButton
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMutex, QMutexLocker, QObject, QTimer, QSettings, QStandardPaths, QCoreApplication
from urllib.parse import urlparse

try:
    from PIL import Image
except ImportError:
    Image = None

from io import BytesIO # Keep this if used elsewhere, though not directly in this diff

try:
    print("Attempting to import from downloader_utils...")
    from downloader_utils import (
        KNOWN_NAMES,
        clean_folder_name,
        extract_post_info,
        download_from_api,
        PostProcessorSignals,
        PostProcessorWorker,
        DownloadThread as BackendDownloadThread,
        SKIP_SCOPE_FILES,
        SKIP_SCOPE_POSTS,
        SKIP_SCOPE_BOTH,
        CHAR_SCOPE_TITLE, # Added for completeness if used directly
        CHAR_SCOPE_FILES, # Ensure this is imported
        CHAR_SCOPE_BOTH, 
        CHAR_SCOPE_COMMENTS,
        FILE_DOWNLOAD_STATUS_FAILED_RETRYABLE_LATER # Import the new status
    )
    print("Successfully imported names from downloader_utils.")
except ImportError as e:
    print(f"--- IMPORT ERROR ---")
    print(f"Failed to import from 'downloader_utils.py': {e}")
    KNOWN_NAMES = []
    PostProcessorSignals = QObject
    PostProcessorWorker = object
    BackendDownloadThread = QThread
    def clean_folder_name(n): return str(n)
    def extract_post_info(u): return None, None, None
    def download_from_api(*a, **k): yield []
    SKIP_SCOPE_FILES = "files"
    SKIP_SCOPE_POSTS = "posts"
    SKIP_SCOPE_BOTH = "both"
    CHAR_SCOPE_TITLE = "title"
    CHAR_SCOPE_FILES = "files"
    CHAR_SCOPE_BOTH = "both"
    CHAR_SCOPE_COMMENTS = "comments"
    FILE_DOWNLOAD_STATUS_FAILED_RETRYABLE_LATER = "failed_retry_later"

except Exception as e:
    print(f"--- UNEXPECTED IMPORT ERROR ---")
    print(f"An unexpected error occurred during import: {e}")
    traceback.print_exc()
    print(f"-----------------------------", file=sys.stderr)
    sys.exit(1)


MAX_THREADS = 200
RECOMMENDED_MAX_THREADS = 50
MAX_FILE_THREADS_PER_POST_OR_WORKER = 10
# New constants for batching high thread counts for post workers
POST_WORKER_BATCH_THRESHOLD = 30
POST_WORKER_NUM_BATCHES = 4
SOFT_WARNING_THREAD_THRESHOLD = 40 # New constant for soft warning
POST_WORKER_BATCH_DELAY_SECONDS = 2.5 # Seconds
MAX_POST_WORKERS_WHEN_COMMENT_FILTERING = 3 # New constant

HTML_PREFIX = "<!HTML!>"

CONFIG_ORGANIZATION_NAME = "KemonoDownloader"
CONFIG_APP_NAME_MAIN = "ApplicationSettings"
MANGA_FILENAME_STYLE_KEY = "mangaFilenameStyleV1"
STYLE_POST_TITLE = "post_title"
STYLE_ORIGINAL_NAME = "original_name"
STYLE_DATE_BASED = "date_based" # New style for date-based naming
SKIP_WORDS_SCOPE_KEY = "skipWordsScopeV1"
ALLOW_MULTIPART_DOWNLOAD_KEY = "allowMultipartDownloadV1"

USE_COOKIE_KEY = "useCookieV1" # New setting key
COOKIE_TEXT_KEY = "cookieTextV1" # New setting key for cookie text
CHAR_FILTER_SCOPE_KEY = "charFilterScopeV1"
# CHAR_SCOPE_TITLE, CHAR_SCOPE_FILES, CHAR_SCOPE_BOTH, CHAR_SCOPE_COMMENTS are already defined or imported

# --- Tour Classes (Moved from tour.py) ---
class TourStepWidget(QWidget):
    """A single step/page in the tour."""
    def __init__(self, title_text, content_text, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10) # Adjusted spacing between title and content for bullet points

        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignCenter)
        # Increased padding-bottom for more space below title
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #E0E0E0; padding-bottom: 15px;")
        layout.addWidget(title_label)

        # Create QScrollArea for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True) # Important for the content_label to resize correctly
        scroll_area.setFrameShape(QFrame.NoFrame) # Make it look seamless with the dialog
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Content is word-wrapped
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded) # Show scrollbar only when needed
        scroll_area.setStyleSheet("background-color: transparent;") # Match dialog background

        content_label = QLabel(content_text)
        content_label.setWordWrap(True)
        # AlignTop ensures text starts from the top if it's shorter than the scroll area view
        content_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        content_label.setTextFormat(Qt.RichText)
        # Adjusted line-height for bullet point readability
        content_label.setStyleSheet("font-size: 11pt; color: #C8C8C8; line-height: 1.8;")

        # Set the content_label as the widget for the scroll_area
        scroll_area.setWidget(content_label)

        # Add the scroll_area to the layout, allowing it to take available space
        layout.addWidget(scroll_area, 1) # The '1' is a stretch factor

        # Removed layout.addStretch(1) as the scroll_area now handles stretching.


class TourDialog(QDialog):
    """
    A dialog that shows a multi-page tour to the user.
    Includes a "Never show again" checkbox.
    Uses QSettings to remember this preference.
    """
    tour_finished_normally = pyqtSignal()
    tour_skipped = pyqtSignal()

    CONFIG_ORGANIZATION_NAME = "KemonoDownloader" # Shared with main app for consistency if needed, but can be distinct
    CONFIG_APP_NAME_TOUR = "ApplicationTour"    # Specific QSettings group for tour
    TOUR_SHOWN_KEY = "neverShowTourAgainV5"     # Updated key to re-show tour

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings(self.CONFIG_ORGANIZATION_NAME, self.CONFIG_APP_NAME_TOUR)
        self.current_step = 0

        self.setWindowTitle("Welcome to Kemono Downloader!")
        self.setModal(True)
        # Set fixed square size, smaller than main window
        self.setFixedSize(600, 620) # Slightly adjusted for potentially more text
        self.setStyleSheet("""
            QDialog {
                background-color: #2E2E2E;
                border: 1px solid #5A5A5A;
            }
            QLabel {
                color: #E0E0E0;
            }
            QCheckBox {
                color: #C0C0C0;
                font-size: 10pt;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
            }
            QPushButton {
                background-color: #555;
                color: #F0F0F0;
                border: 1px solid #6A6A6A;
                padding: 8px 15px;
                border-radius: 4px;
                min-height: 25px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #656565;
            }
            QPushButton:pressed {
                background-color: #4A4A4A;
            }
        """)
        self._init_ui()
        self._center_on_screen()

    def _center_on_screen(self):
        """Centers the dialog on the screen."""
        # Updated to use availableGeometry and center more reliably
        try:
            primary_screen = QApplication.primaryScreen()
            if not primary_screen:
                screens = QApplication.screens()
                if not screens: return # Cannot center
                primary_screen = screens[0]
            
            available_geo = primary_screen.availableGeometry()
            widget_geo = self.frameGeometry()
            
            x = available_geo.x() + (available_geo.width() - widget_geo.width()) // 2
            y = available_geo.y() + (available_geo.height() - widget_geo.height()) // 2
            self.move(x, y)
        except Exception as e:
            print(f"[Tour] Error centering dialog: {e}")
            

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)

        # --- Define Tour Steps with Updated Content ---
        step1_content = (
            "Hello! This quick tour will walk you through the main features of the Kemono Downloader, including recent updates like enhanced filtering, manga mode improvements, and cookie management."
            "<ul>"
            "<li>My goal is to help you easily download content from Kemono and Coomer.</li>"
            "<li>Use the <b>Next</b> and <b>Back</b> buttons to navigate.</li>"
            "<li>Many options have tooltips if you hover over them for more details.</li>"
            "<li>Click <b>Skip Tour</b> to close this guide at any time.</li>"
            "<li>Check <b>'Never show this tour again'</b> if you don't want to see this on future startups.</li>"
            "</ul>"
        )
        self.step1 = TourStepWidget("👋 Welcome!", step1_content)

        step2_content = (
            "Let's start with the basics for downloading:"
            "<ul>"
            "<li><b>🔗 Kemono Creator/Post URL:</b><br>"
            "   Paste the full web address (URL) of a creator's page (e.g., <i>https://kemono.su/patreon/user/12345</i>) "
            "or a specific post (e.g., <i>.../post/98765</i>).</li><br>"
            "<li><b>📁 Download Location:</b><br>"
            "   Click 'Browse...' to choose a folder on your computer where all downloaded files will be saved. "
            "This is required unless you are using 'Only Links' mode.</li><br>"
            "<li><b>📄 Page Range (Creator URLs only):</b><br>"
            "   If downloading from a creator's page, you can specify a range of pages to fetch (e.g., pages 2 to 5). "
            "Leave blank for all pages. This is disabled for single post URLs or when <b>Manga/Comic Mode</b> is active.</li>"
            "</ul>"
        )
        self.step2 = TourStepWidget("① Getting Started", step2_content)

        step3_content = (
            "Refine what you download with these filters:"
            "<ul>"
            "<li><b>🎯 Filter by Character(s):</b><br>"
            "   Enter character names, comma-separated (e.g., <i>Tifa, Aerith</i>). Group aliases for a combined folder name: <i>(alias1, alias2)</i> becomes folder 'alias1 alias2'.<br>"
            "   The <b>'Filter: [Scope]'</b> button next to this input controls how this filter is applied:"
            "   <ul><li><i>Filter: Files:</i> Checks individual filenames. A post is kept if any file matches; only matching files are downloaded. Folder naming uses the character from the matching filename.</li>"
            "       <li><i>Filter: Title:</i> Checks post titles. All files from a matching post are downloaded. Folder naming uses the character from the matching post title.</li>"
            "       <li><i>Filter: Both:</i> Checks post title first. If it matches, all files are downloaded. If not, it then checks filenames, and only matching files are downloaded. Folder naming prioritizes title match, then file match.</li>"
            "       <li><i>Filter: Comments (Beta):</i> Checks filenames first. If a file matches, all files from the post are downloaded. If no file match, it then checks post comments. If a comment matches, all files are downloaded. (Uses more API requests). Folder naming prioritizes file match, then comment match.</li></ul>"
            "   This filter also influences folder naming if 'Separate Folders by Name/Title' is enabled.</li><br>"
            "<li><b>🚫 Skip with Words:</b><br>"
            "   Enter words, comma-separated (e.g., <i>WIP, sketch, preview</i>). "
            "   The <b>'Scope: [Type]'</b> button (next to this input) cycles how this filter applies:"
            "   <ul><li><i>Scope: Files:</i> Skips files if their names contain any of these words.</li>"
            "       <li><i>Scope: Posts:</i> Skips entire posts if their titles contain any of these words.</li>"
            "       <li><i>Scope: Both:</i> Applies both file and post title skipping (post first, then files).</li></ul></li><br>"
            "<li><b>Filter Files (Radio Buttons):</b> Choose what to download:"
            "   <ul>"
            "   <li><i>All:</i> Downloads all file types found.</li>"
            "   <li><i>Images/GIFs:</i> Only common image formats and GIFs.</li>"
            "   <li><i>Videos:</i> Only common video formats.</li>"
            "   <li><b><i>📦 Only Archives:</i></b> Exclusively downloads <b>.zip</b> and <b>.rar</b> files. When selected, 'Skip .zip' and 'Skip .rar' checkboxes are automatically disabled and unchecked. 'Show External Links' is also disabled.</li>"
            "   <li><i>🔗 Only Links:</i> Extracts and displays external links from post descriptions instead of downloading files. Download-related options and 'Show External Links' are disabled.</li>"
            "   </ul></li>"
            "</ul>"
        )
        self.step3 = TourStepWidget("② Filtering Downloads", step3_content)

        step4_content = (
            "More options to customize your downloads:"
            "<ul>"
            "<li><b>Skip .zip / Skip .rar:</b> Check these to avoid downloading these archive file types. "
            "   <i>(Note: These are disabled and ignored if '📦 Only Archives' filter mode is selected).</i></li><br>"
            "<li><b>✂️ Remove Words from name:</b><br>"
            "   Enter words, comma-separated (e.g., <i>patreon, [HD]</i>), to remove from downloaded filenames (case-insensitive).</li><br>"
            "<li><b>Download Thumbnails Only:</b> Downloads small preview images instead of full-sized files (if available).</li><br>"
            "<li><b>Compress Large Images:</b> If the 'Pillow' library is installed, images larger than 1.5MB will be converted to WebP format if the WebP version is significantly smaller.</li><br>"
            "<li><b>🗄️ Custom Folder Name (Single Post Only):</b><br>"
            "   If you are downloading a single specific post URL AND 'Separate Folders by Name/Title' is enabled, "
            "you can enter a custom name here for that post's download folder.</li><br>"
            "<li><b>🍪 Use Cookie:</b> Check this to use cookies for requests. You can either:"
            "   <ul><li>Enter a cookie string directly into the text field (e.g., <i>name1=value1; name2=value2</i>).</li>"
            "       <li>Click 'Browse...' to select a <i>cookies.txt</i> file (Netscape format). The path will appear in the text field.</li></ul>"
            "   This is useful for accessing content that requires login. The text field takes precedence if filled.</li>"
            "</ul>"
        )
        self.step4 = TourStepWidget("③ Fine-Tuning Downloads", step4_content)

        step5_content = (
            "Organize your downloads and manage performance:"
            "<ul>"
            "<li><b>⚙️ Separate Folders by Name/Title:</b> Creates subfolders based on the 'Filter by Character(s)' input or post titles (can use the 'Known Shows/Characters' list as a fallback for folder names).</li><br>"
            "<li><b>Subfolder per Post:</b> If 'Separate Folders' is on, this creates an additional subfolder for <i>each individual post</i> inside the main character/title folder.</li><br>"
            "<li><b>🚀 Use Multithreading (Threads):</b> Enables faster operations. The number in 'Threads' input means:"
            "   <ul><li>For <b>Creator Feeds:</b> Number of posts to process simultaneously. Files within each post are downloaded sequentially by its worker (unless 'Date Based' manga naming is on, which forces 1 post worker).</li>"
            "       <li>For <b>Single Post URLs:</b> Number of files to download concurrently from that single post.</li></ul>"
            "   If unchecked, 1 thread is used. High thread counts (e.g., >40) may show an advisory.</li><br>"
            "<li><b>Multi-part Download Toggle (Top-right of log area):</b><br>"
            "   The <b>'Multi-part: [ON/OFF]'</b> button allows enabling/disabling multi-segment downloads for individual large files. "
            "   <ul><li><b>ON:</b> Can speed up large file downloads (e.g., videos) but may increase UI choppiness or log spam with many small files. An advisory will appear when enabling. If a multi-part download fails, it retries as single-stream.</li>"
            "       <li><b>OFF (Default):</b> Files are downloaded in a single stream.</li></ul>"
            "   This is disabled if 'Only Links' or 'Only Archives' mode is active.</li><br>"
            "<li><b>📖 Manga/Comic Mode (Creator URLs only):</b> Tailored for sequential content."
            "   <ul>"
            "   <li>Downloads posts from <b>oldest to newest</b>.</li>"
            "   <li>The 'Page Range' input is disabled as all posts are fetched.</li>"
            "   <li>A <b>filename style toggle button</b> (e.g., 'Name: Post Title') appears in the top-right of the log area when this mode is active for a creator feed. Click it to cycle through naming styles:"
            "       <ul>"
            "       <li><b><i>Name: Post Title (Default):</i></b> The first file in a post is named after the post's title. Subsequent files in the same post keep original names.</li>"
            "       <li><b><i>Name: Original File:</i></b> All files attempt to keep their original filenames.</li>"
            "       <li><b><i>Name: Date Based:</i></b> Files are named sequentially (001.ext, 002.ext, ...) based on post publication order. Multithreading for post processing is automatically disabled for this style.</li>"
            "       </ul>"
            "   </li>"
            "   <li>For best results with 'Name: Post Title' or 'Name: Date Based' styles, use the 'Filter by Character(s)' field with the manga/series title for folder organization.</li>"
            "   </ul></li><br>"
            "<li><b>🎭 Known.txt for Smart Folder Organization:</b><br>"
            "   Fine-grained control over automatic folder organization using a personalized list in <b>Known.txt</b>."
            "   <ul>"
            "       <li><b>Primary Names & Aliases:</b> Define a main folder name and link multiple aliases. For example, an entry like <code>([Power], powwr, pwr, Blood devil)</code> ensures any post matching \"Power\", \"powwr\", etc. (based on your filter scope) gets saved into a \"Power\" folder. Simple entries like <code>My Series</code> are also supported. The primary name for the folder is the one in <code>[]</code> brackets, or the first one if no brackets.</li>"
            "       <li><b>Intelligent Fallback:</b> When 'Separate Folders by Name/Title' is active, and if a post doesn't match any specific 'Filter by Character(s)' input, the downloader consults <code>Known.txt</code> to find a matching primary name for folder creation.</li>"
            "       <li><b>User-Friendly Management:</b> Add or remove primary names directly through the UI list below. For advanced editing (like setting up aliases or defining the primary name for a group), click <b>'Open Known.txt'</b> to edit the file directly.</li>"
            "   </ul>"
            "</li>"
            "</ul>"
        )
        self.step5 = TourStepWidget("④ Organization & Performance", step5_content)

        step6_content = (
            "Monitoring and Controls:"
            "<ul>"
            "<li><b>📜 Progress Log / Extracted Links Log:</b> Shows detailed download messages. If '🔗 Only Links' mode is active, this area displays the extracted links.</li><br>"
            "<li><b>Show External Links in Log:</b> If checked, a secondary log panel appears below the main log to display any external links found in post descriptions. <i>(This is disabled if '🔗 Only Links' or '📦 Only Archives' mode is active).</i></li><br>"
            "<li><b>Log View Toggle (👁️ / 🙈 Button):</b><br>"
            "   This button (top-right of log area) switches the main log view:"
            "   <ul><li><b>👁️ Progress Log (Default):</b> Shows all download activity, errors, and summaries.</li>"
            "       <li><b>🙈 Missed Character Log:</b> Displays a summarized list of key terms from post titles that were skipped due to your 'Filter by Character(s)' settings. Useful for identifying content you might be unintentionally missing.</li></ul></li><br>"
            "<li><b>🔄 Reset:</b> Clears all input fields, logs, and resets temporary settings to their defaults. Can only be used when no download is active.</li><br>"
            "<li><b>⬇️ Start Download / 🔗 Extract Links / ⏸️ Pause / ❌ Cancel:</b> These buttons control the process. 'Cancel & Reset UI' stops the current operation and performs a soft UI reset, preserving your URL and Directory inputs. 'Pause/Resume' allows temporarily halting and continuing.</li><br>"
            "<li>If some files fail with recoverable errors (like 'IncompleteRead'), you might be prompted to retry them at the end of a session.</li>"
            "</ul>"
            "<br>You're all set! Click <b>'Finish'</b> to close the tour and start using the downloader."
        )
        self.step6 = TourStepWidget("⑤ Logs & Final Controls", step6_content)


        self.tour_steps = [self.step1, self.step2, self.step3, self.step4, self.step5, self.step6]
        for step_widget in self.tour_steps:
            self.stacked_widget.addWidget(step_widget)

        bottom_controls_layout = QVBoxLayout()
        bottom_controls_layout.setContentsMargins(15, 10, 15, 15) # Adjusted margins
        bottom_controls_layout.setSpacing(12) # Slightly more spacing

        self.never_show_again_checkbox = QCheckBox("Never show this tour again")
        bottom_controls_layout.addWidget(self.never_show_again_checkbox, 0, Qt.AlignLeft)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.skip_button = QPushButton("Skip Tour")
        self.skip_button.clicked.connect(self._skip_tour_action)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self._previous_step)
        self.back_button.setEnabled(False)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self._next_step_action)
        self.next_button.setDefault(True)

        buttons_layout.addWidget(self.skip_button)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.next_button)

        bottom_controls_layout.addLayout(buttons_layout)
        main_layout.addLayout(bottom_controls_layout)

        self._update_button_states()

    def _handle_exit_actions(self):
        if self.never_show_again_checkbox.isChecked():
            self.settings.setValue(self.TOUR_SHOWN_KEY, True)
            self.settings.sync()
        # else:
            # print(f"[Tour] '{self.TOUR_SHOWN_KEY}' setting not set to True (checkbox was unchecked on exit).")


    def _next_step_action(self):
        if self.current_step < len(self.tour_steps) - 1:
            self.current_step += 1
            self.stacked_widget.setCurrentIndex(self.current_step)
        else:
            self._handle_exit_actions()
            self.tour_finished_normally.emit()
            self.accept()
        self._update_button_states()

    def _previous_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.stacked_widget.setCurrentIndex(self.current_step)
        self._update_button_states()

    def _skip_tour_action(self):
        self._handle_exit_actions()
        self.tour_skipped.emit()
        self.reject()

    def _update_button_states(self):
        if self.current_step == len(self.tour_steps) - 1:
            self.next_button.setText("Finish")
        else:
            self.next_button.setText("Next")
        self.back_button.setEnabled(self.current_step > 0)

    @staticmethod
    def run_tour_if_needed(parent_app_window):
        try:
            settings = QSettings(TourDialog.CONFIG_ORGANIZATION_NAME, TourDialog.CONFIG_APP_NAME_TOUR)
            never_show_again_from_settings = settings.value(TourDialog.TOUR_SHOWN_KEY, False, type=bool)
            
            primary_screen = QApplication.primaryScreen()
            if not primary_screen:
                screens = QApplication.screens()
                primary_screen = screens[0] if screens else None

            dialog_width, dialog_height = 600, 620 # Default fixed size

            if primary_screen:
                available_geo = primary_screen.availableGeometry()
                screen_w, screen_h = available_geo.width(), available_geo.height()

                # Calculate preferred size for tour dialog (e.g., 50% width, 60% height)
                pref_w = int(screen_w * 0.50)
                pref_h = int(screen_h * 0.60)

                # Apply constraints (min/max)
                min_w, max_w = 550, 700
                min_h, max_h = 580, 750
                
                dialog_width = max(min_w, min(pref_w, max_w))
                dialog_height = max(min_h, min(pref_h, max_h))

            if never_show_again_from_settings:
                print(f"[Tour] Skipped: '{TourDialog.TOUR_SHOWN_KEY}' is True in settings.")
                return QDialog.Rejected

            tour_dialog = TourDialog(parent_app_window)
            tour_dialog.setFixedSize(dialog_width, dialog_height) # Apply calculated fixed size
            result = tour_dialog.exec_()
            return result

        except Exception as e:
            print(f"[Tour] CRITICAL ERROR in run_tour_if_needed: {e}")
            # traceback.print_exc() # Keep console cleaner for this specific case
            return QDialog.Rejected
# --- End Tour Classes ---

# Helper class to hold dynamic character filters
class DynamicFilterHolder:
    def __init__(self, initial_filters=None):
        self.lock = threading.Lock()
        # Store filters as a list of dicts, same as parsed_character_filter_objects
        self._filters = initial_filters if initial_filters is not None else []

    def get_filters(self):
        with self.lock:
            # Return a deep copy to prevent modification of the internal list by workers
            # and to ensure thread safety if workers iterate over it while it's being set.
            return [dict(f) for f in self._filters]

    def set_filters(self, new_filters):
        with self.lock:
            # Store a deep copy, ensuring new_filters is a list of dicts
            self._filters = [dict(f) for f in (new_filters if new_filters else [])]

class DownloaderApp(QWidget):
    character_prompt_response_signal = pyqtSignal(bool)
    log_signal = pyqtSignal(str)
    add_character_prompt_signal = pyqtSignal(str)
    overall_progress_signal = pyqtSignal(int, int)
    finished_signal = pyqtSignal(int, int, bool, list)
    external_link_signal = pyqtSignal(str, str, str, str)
    # Changed to object to handle both (int, int) for single stream and list for multipart
    file_progress_signal = pyqtSignal(str, object)


    def __init__(self):
        super().__init__()
        self.settings = QSettings(CONFIG_ORGANIZATION_NAME, CONFIG_APP_NAME_MAIN)

        # Determine path for Known.txt in the application's directory
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Application is frozen (bundled with PyInstaller or similar)
            # sys.executable is the path to the .exe file
            app_base_dir = os.path.dirname(sys.executable)
        else:
            # This is the directory where main.py (and thus potentially cookies.txt) resides
            # Application is running as a script
            # __file__ is the path to the script file
            app_base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(app_base_dir, "Known.txt")

        self.download_thread = None
        self.thread_pool = None
        self.cancellation_event = threading.Event()
        self.pause_event = threading.Event() # New event for pausing
        self.active_futures = []
        self.total_posts_to_process = 0
        self.dynamic_character_filter_holder = DynamicFilterHolder() # For live character filter updates
        self.processed_posts_count = 0
        self.download_counter = 0
        self.skip_counter = 0
        self.selected_cookie_filepath = None # For storing path from browse button
        self.retryable_failed_files_info = [] # For storing info about files that failed but can be retried

        self.is_paused = False # New state for pause functionality
        # For handling signals from worker threads via a queue
        self.worker_to_gui_queue = queue.Queue()
        self.gui_update_timer = QTimer(self)
        self.actual_gui_signals = PostProcessorSignals() # Renamed from self.worker_signals

        self.worker_signals = PostProcessorSignals()
        self.prompt_mutex = QMutex()
        self._add_character_response = None

        self.downloaded_files = set()
        self.downloaded_files_lock = threading.Lock()
        self.downloaded_file_hashes = set()
        self.downloaded_file_hashes_lock = threading.Lock()

        self.show_external_links = False
        self.external_link_queue = deque()
        self._is_processing_external_link_queue = False
        self._current_link_post_title = None
        self.extracted_links_cache = []
        
        # self.basic_log_mode = False # No longer used with this button
        # self.log_verbosity_button = None # Old text button, already removed
        self.manga_rename_toggle_button = None
        
        self.main_log_output = None
        self.external_log_output = None
        self.log_splitter = None
        self.main_splitter = None
        self.reset_button = None
        self.progress_log_label = None
        self.log_verbosity_toggle_button = None # New icon button

        self.missed_character_log_output = None # New log area
        self.log_view_stack = None # To switch between progress and missed char logs
        self.current_log_view = 'progress' # 'progress' or 'missed_character'

        self.link_search_input = None
        self.link_search_button = None # For filtering links log
        self.export_links_button = None # For exporting links
        self.radio_only_links = None
        self.radio_only_archives = None

        # For Missed Character Log summarization
        self.missed_title_key_terms_count = {}
        self.missed_title_key_terms_examples = {}
        self.logged_summary_for_key_term = set()
        # self.missed_character_log_threshold = 4 # No longer needed for new style
        self.STOP_WORDS = set(["a", "an", "the", "is", "was", "were", "of", "for", "with", "in", "on", "at", "by", "to", "and", "or", "but", "i", "you", "he", "she", "it", "we", "they", "my", "your", "his", "her", "its", "our", "their", "com", "net", "org", "www"])
        self.already_logged_bold_key_terms = set() # For the new simple bolded list
        self.missed_key_terms_buffer = [] # To store terms for alphabetical sorting
        self.char_filter_scope_toggle_button = None

        self.manga_filename_style = self.settings.value(MANGA_FILENAME_STYLE_KEY, STYLE_POST_TITLE, type=str)
        self.skip_words_scope = self.settings.value(SKIP_WORDS_SCOPE_KEY, SKIP_SCOPE_POSTS, type=str)
        self.char_filter_scope = self.settings.value(CHAR_FILTER_SCOPE_KEY, CHAR_SCOPE_FILES, type=str) # Default to Files
        # Always default multi-part download to OFF on launch, ignoring any saved setting.
        self.allow_multipart_download_setting = False 

        # Ensure "Use Cookie" is unchecked and text is empty by default on every launch
        self.use_cookie_setting = False # Always default to False on launch
        self.cookie_text_setting = ""   # Always default to empty on launch

        print(f"ℹ️ Known.txt will be loaded/saved at: {self.config_file}")


        self.load_known_names_from_util()
        self.setWindowTitle("Kemono Downloader v3.5.0")
        # self.setGeometry(150, 150, 1050, 820) # Initial geometry will be set after showing
        self.setStyleSheet(self.get_dark_theme())

        self.init_ui()
        self._connect_signals()

        self.log_signal.emit("ℹ️ Local API server functionality has been removed.")
        self.log_signal.emit("ℹ️ 'Skip Current File' button has been removed.")
        if hasattr(self, 'character_input'):
            self.character_input.setToolTip("Names, comma-separated. Group aliases: (alias1, alias2) for combined folder name 'alias1 alias2'. E.g., yor, (Boa, Hancock)")
        self.log_signal.emit(f"ℹ️ Manga filename style loaded: '{self.manga_filename_style}'")
        self.log_signal.emit(f"ℹ️ Skip words scope loaded: '{self.skip_words_scope}'")
        self.log_signal.emit(f"ℹ️ Character filter scope loaded: '{self.char_filter_scope}'")
        self.log_signal.emit(f"ℹ️ Multi-part download defaults to: {'Enabled' if self.allow_multipart_download_setting else 'Disabled'} on launch")
        self.log_signal.emit(f"ℹ️ Cookie text defaults to: Empty on launch")
        self.log_signal.emit(f"ℹ️ 'Use Cookie' setting defaults to: Disabled on launch")


    def _connect_signals(self):
        # Signals from the GUI's perspective (emitted by _process_worker_queue or directly)
        self.actual_gui_signals.progress_signal.connect(self.handle_main_log)
        self.actual_gui_signals.file_progress_signal.connect(self.update_file_progress_display)
        self.actual_gui_signals.missed_character_post_signal.connect(self.handle_missed_character_post)
        self.actual_gui_signals.external_link_signal.connect(self.handle_external_link_signal)
        self.actual_gui_signals.file_download_status_signal.connect(lambda status: None) # Placeholder if needed, or connect to UI
        
        if hasattr(self, 'character_input'): # Connect live update for character input
            self.character_input.textChanged.connect(self._on_character_input_changed_live)
        # Timer for processing the worker queue
        if hasattr(self, 'use_cookie_checkbox'): 
            self.use_cookie_checkbox.toggled.connect(self._update_cookie_input_visibility)
        if hasattr(self, 'cookie_browse_button'): # Connect the new browse button
            self.cookie_browse_button.clicked.connect(self._browse_cookie_file)
        if hasattr(self, 'cookie_text_input'): # Connect text changed for manual clear detection
            self.cookie_text_input.textChanged.connect(self._handle_cookie_text_manual_change)
        self.gui_update_timer.timeout.connect(self._process_worker_queue)
        self.gui_update_timer.start(100) # Check queue every 100ms

        # Direct GUI signals
        self.log_signal.connect(self.handle_main_log)
        self.add_character_prompt_signal.connect(self.prompt_add_character)
        self.character_prompt_response_signal.connect(self.receive_add_character_result)
        self.overall_progress_signal.connect(self.update_progress_display)
        self.finished_signal.connect(self.download_finished)
        # self.external_link_signal.connect(self.handle_external_link_signal) # Covered by actual_gui_signals
        # self.retryable_file_failed_signal will be connected in start_single_threaded_download
        # self.file_progress_signal.connect(self.update_file_progress_display) # Covered by actual_gui_signals

        # UI element connections
        if hasattr(self, 'character_search_input'): self.character_search_input.textChanged.connect(self.filter_character_list)
        if hasattr(self, 'external_links_checkbox'): self.external_links_checkbox.toggled.connect(self.update_external_links_setting)
        if hasattr(self, 'thread_count_input'): self.thread_count_input.textChanged.connect(self.update_multithreading_label)
        if hasattr(self, 'use_subfolder_per_post_checkbox'): self.use_subfolder_per_post_checkbox.toggled.connect(self.update_ui_for_subfolders)
        if hasattr(self, 'use_multithreading_checkbox'): self.use_multithreading_checkbox.toggled.connect(self._handle_multithreading_toggle)

        if hasattr(self, 'radio_group') and self.radio_group:
            self.radio_group.buttonToggled.connect(self._handle_filter_mode_change)

        if self.reset_button: self.reset_button.clicked.connect(self.reset_application_state)
        if self.log_verbosity_toggle_button: self.log_verbosity_toggle_button.clicked.connect(self.toggle_active_log_view)

        if self.link_search_button: self.link_search_button.clicked.connect(self._filter_links_log)
        if self.link_search_input:
            self.link_search_input.returnPressed.connect(self._filter_links_log)
            self.link_search_input.textChanged.connect(self._filter_links_log)
        if self.export_links_button: self.export_links_button.clicked.connect(self._export_links_to_file)

        if self.manga_mode_checkbox: self.manga_mode_checkbox.toggled.connect(self.update_ui_for_manga_mode)
        if self.manga_rename_toggle_button: self.manga_rename_toggle_button.clicked.connect(self._toggle_manga_filename_style)

        if hasattr(self, 'link_input'):
            self.link_input.textChanged.connect(lambda: self.update_ui_for_manga_mode(self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False))
        
        if self.skip_scope_toggle_button:
            self.skip_scope_toggle_button.clicked.connect(self._cycle_skip_scope)

        if self.char_filter_scope_toggle_button:
            self.char_filter_scope_toggle_button.clicked.connect(self._cycle_char_filter_scope)
        
        if hasattr(self, 'multipart_toggle_button'): self.multipart_toggle_button.clicked.connect(self._toggle_multipart_mode) # Keep this if it's separate

        if hasattr(self, 'open_known_txt_button'): # Connect the new button
            self.open_known_txt_button.clicked.connect(self._open_known_txt_file)

    def _on_character_input_changed_live(self, text):
        """
        Called when the character input field text changes.
        If a download is active (running or paused), this updates the dynamic filter holder.
        """
        if self._is_download_active(): # Only update if download is active/paused
            # self.log_signal.emit("ℹ️ Character filter input changed during active session. Updating dynamic filters...")
            # Use QCoreApplication.processEvents() to keep UI responsive during parsing if it's complex
            QCoreApplication.processEvents()
            raw_character_filters_text = self.character_input.text().strip()
            parsed_filters = self._parse_character_filters(raw_character_filters_text)
            
            self.dynamic_character_filter_holder.set_filters(parsed_filters)
            # Limit logging to avoid spamming if typing fast
            # self.log_signal.emit(f"   Dynamic filters updated to: {', '.join(item['name'] for item in parsed_filters) if parsed_filters else 'None'}")

    def _parse_character_filters(self, raw_text):
        """Helper to parse character filter string into list of objects."""
        parsed_character_filter_objects = []
        if raw_text:
            raw_parts = []
            current_part_buffer = ""
            in_group_parsing = False
            for char_token in raw_text:
                if char_token == '(':
                    in_group_parsing = True
                    current_part_buffer += char_token
                elif char_token == ')':
                    in_group_parsing = False
                    current_part_buffer += char_token
                elif char_token == ',' and not in_group_parsing:
                    if current_part_buffer.strip(): raw_parts.append(current_part_buffer.strip())
                    current_part_buffer = ""
                else:
                    current_part_buffer += char_token
            if current_part_buffer.strip(): raw_parts.append(current_part_buffer.strip())

            for part_str in raw_parts:
                part_str = part_str.strip()
                if not part_str: continue
                if part_str.startswith("(") and part_str.endswith(")"):
                    group_content_str = part_str[1:-1].strip()
                    aliases_in_group = [alias.strip() for alias in group_content_str.split(',') if alias.strip()]
                    if aliases_in_group:
                        group_folder_name = " ".join(aliases_in_group)
                        parsed_character_filter_objects.append({"name": group_folder_name, "is_group": True, "aliases": aliases_in_group})
                else:
                    parsed_character_filter_objects.append({"name": part_str, "is_group": False, "aliases": [part_str]})
        return parsed_character_filter_objects

    def _process_worker_queue(self):
        """Processes messages from the worker queue and emits Qt signals from the GUI thread."""
        while not self.worker_to_gui_queue.empty():
            try:
                item = self.worker_to_gui_queue.get_nowait()
                signal_type = item.get('type')
                payload = item.get('payload', tuple()) # Default to empty tuple

                if signal_type == 'progress':
                    self.actual_gui_signals.progress_signal.emit(*payload)
                elif signal_type == 'file_download_status': # Changed from 'file_status'
                    self.actual_gui_signals.file_download_status_signal.emit(*payload)
                elif signal_type == 'external_link': # Changed from 'ext_link'
                    self.actual_gui_signals.external_link_signal.emit(*payload)
                elif signal_type == 'file_progress':
                    self.actual_gui_signals.file_progress_signal.emit(*payload)
                elif signal_type == 'missed_character_post':
                    self.actual_gui_signals.missed_character_post_signal.emit(*payload)
                else:
                    self.log_signal.emit(f"⚠️ Unknown signal type from worker queue: {signal_type}")
                self.worker_to_gui_queue.task_done()
            except queue.Empty:
                break # Should not happen with while not empty, but good practice
            except Exception as e:
                self.log_signal.emit(f"❌ Error processing worker queue: {e}")

    def load_known_names_from_util(self):
        global KNOWN_NAMES
        if os.path.exists(self.config_file):
            parsed_known_objects = []
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line: continue

                        if line.startswith("(") and line.endswith(")"):
                            content = line[1:-1].strip()
                            parts = [p.strip() for p in content.split(',') if p.strip()]
                            if parts:
                                potential_primary_name = None
                                all_aliases_in_line = []
                                remaining_parts = list(parts) # Create a mutable copy

                                # First, find and process the bracketed primary name
                                for i, part_check_brackets in enumerate(parts):
                                    if part_check_brackets.startswith('[') and part_check_brackets.endswith(']'):
                                        potential_primary_name = part_check_brackets[1:-1].strip()
                                        if potential_primary_name:
                                            all_aliases_in_line.append(potential_primary_name)
                                            remaining_parts.pop(i) # Remove the processed primary name part
                                        break # Found the bracketed name

                                # If no bracketed name was found, use the first part as primary (fallback)
                                if not potential_primary_name and parts:
                                    potential_primary_name = parts[0].strip()
                                    all_aliases_in_line.append(potential_primary_name)
                                    if remaining_parts and remaining_parts[0] == potential_primary_name: # Avoid double-adding if it was the first
                                        remaining_parts.pop(0)

                                # Add remaining parts as unique aliases
                                for part in remaining_parts:
                                    cleaned_part = part.strip()
                                    if cleaned_part and cleaned_part not in all_aliases_in_line:
                                        all_aliases_in_line.append(cleaned_part)

                                if not potential_primary_name: # Should not happen if parts is not empty
                                    if hasattr(self, 'log_signal'): self.log_signal.emit(f"⚠️ Could not determine primary name in Known.txt on line {line_num}: '{line}'")
                                    continue
                                else: # This is the 'else' statement from the error
                                    parsed_known_objects.append({ # This block needs to be indented
                                        "name": potential_primary_name,
                                        "is_group": True,
                                        "aliases": all_aliases_in_line # Already unique and primary is first
                                    })
                            else:
                                if hasattr(self, 'log_signal'): self.log_signal.emit(f"⚠️ Empty group found in Known.txt on line {line_num}: '{line}'")
                        else:
                            parsed_known_objects.append({
                                "name": line,
                                "is_group": False,
                                "aliases": [line] # Simple entry, alias is itself
                            })
                
                # Sort by primary name, case-insensitive
                parsed_known_objects.sort(key=lambda x: x["name"].lower())
                KNOWN_NAMES[:] = parsed_known_objects # Update global list
                log_msg = f"ℹ️ Loaded {len(KNOWN_NAMES)} known entries from {self.config_file}"
            except Exception as e:
                log_msg = f"❌ Error loading config '{self.config_file}': {e}"
                QMessageBox.warning(self, "Config Load Error", f"Could not load list from {self.config_file}:\n{e}")
                KNOWN_NAMES[:] = []
        else:
            log_msg = f"ℹ️ Config file '{self.config_file}' not found. Starting with default entries."
            KNOWN_NAMES[:] = []
        
        if hasattr(self, 'log_signal'): self.log_signal.emit(log_msg)
        
        if hasattr(self, 'character_list'):
            self.character_list.clear()
            # Display only the primary 'name' in the QListWidget

            # Add default entries if the list is empty after loading (meaning file didn't exist)
            if not KNOWN_NAMES:
                default_entry = {
                    "name": "Yor",
                    "is_group": True,
                    "aliases": sorted(list(set(["Yor Forger", "Yor", "Yor Briar"]))) # Ensure unique and sorted aliases
                }
                KNOWN_NAMES.append(default_entry)
                # Add more defaults here if needed
                self.save_known_names() # Save to disk immediately if file was created with defaults
                self.log_signal.emit("ℹ️ Added default entry for 'Yor Forger'.")

            self.character_list.addItems([entry["name"] for entry in KNOWN_NAMES])

    def save_known_names(self):
        global KNOWN_NAMES
        try:
            # KNOWN_NAMES is already sorted by primary name during load/add
            with open(self.config_file, 'w', encoding='utf-8') as f:
                for entry in KNOWN_NAMES:
                    if entry["is_group"] and len(entry["aliases"]) > 1:
                        # New format: Mark primary name (first alias) with brackets
                        primary_name = entry['aliases'][0]
                        other_aliases = entry['aliases'][1:]
                        formatted_aliases_for_file = [f"[{primary_name}]"] + other_aliases
                        f.write(f"({', '.join(formatted_aliases_for_file)})\n")
                    elif entry["is_group"] and len(entry["aliases"]) == 1: # Group with only one name (the primary)
                        f.write(f"([{entry['aliases'][0]}])\n") # Save as ([PrimaryName])
                    else: # Simple entry or group with only one alias (the name itself)
                        f.write(entry["name"] + '\n') # Non-grouped items are saved as plain names
            if hasattr(self, 'log_signal'): self.log_signal.emit(f"💾 Saved {len(KNOWN_NAMES)} known entries to {self.config_file}")
        except Exception as e:
            log_msg = f"❌ Error saving config '{self.config_file}': {e}"
            if hasattr(self, 'log_signal'): self.log_signal.emit(log_msg)
            QMessageBox.warning(self, "Config Save Error", f"Could not save list to {self.config_file}:\n{e}")

    def closeEvent(self, event):
        self.save_known_names()
        self.settings.setValue(MANGA_FILENAME_STYLE_KEY, self.manga_filename_style)
        self.settings.setValue(SKIP_WORDS_SCOPE_KEY, self.skip_words_scope)
        self.settings.setValue(CHAR_FILTER_SCOPE_KEY, self.char_filter_scope)
        self.settings.setValue(ALLOW_MULTIPART_DOWNLOAD_KEY, self.allow_multipart_download_setting)
        self.settings.setValue(COOKIE_TEXT_KEY, self.cookie_text_input.text() if hasattr(self, 'cookie_text_input') else "")
        self.settings.setValue(USE_COOKIE_KEY, self.use_cookie_checkbox.isChecked() if hasattr(self, 'use_cookie_checkbox') else False)
        self.settings.sync()

        should_exit = True
        is_downloading = self._is_download_active()

        if is_downloading:
             reply = QMessageBox.question(self, "Confirm Exit",
                                          "Download in progress. Are you sure you want to exit and cancel?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
             if reply == QMessageBox.Yes:
                 self.log_signal.emit("⚠️ Cancelling active download due to application exit...")
                 
                 # Direct cancellation for exit - different from button cancel
                 self.cancellation_event.set()
                 if self.download_thread and self.download_thread.isRunning():
                     self.download_thread.requestInterruption()
                     self.log_signal.emit("   Signaled single download thread to interrupt.")
                 
                 # For thread pool, we want to wait on exit.
                 if self.download_thread and self.download_thread.isRunning():
                     self.log_signal.emit("   Waiting for single download thread to finish...")
                     self.download_thread.wait(3000)
                     if self.download_thread.isRunning():
                         self.log_signal.emit("   ⚠️ Single download thread did not terminate gracefully.")

                 if self.thread_pool:
                     self.log_signal.emit("   Shutting down thread pool (waiting for completion)...")
                     self.thread_pool.shutdown(wait=True, cancel_futures=True)
                     self.log_signal.emit("   Thread pool shutdown complete.")
                     self.thread_pool = None
                 self.log_signal.emit("   Cancellation for exit complete.")
             else:
                 should_exit = False
                 self.log_signal.emit("ℹ️ Application exit cancelled.")
                 event.ignore()
                 return

        if should_exit:
            self.log_signal.emit("ℹ️ Application closing.")
            if self.thread_pool:
                 self.log_signal.emit("   Final thread pool check: Shutting down...")
                 self.cancellation_event.set()
                 self.thread_pool.shutdown(wait=True, cancel_futures=True)
                 self.thread_pool = None
            self.log_signal.emit("👋 Exiting application.")
            event.accept()


    def init_ui(self):
        self.main_splitter = QSplitter(Qt.Horizontal)
        left_panel_widget = QWidget()
        right_panel_widget = QWidget()
        left_layout = QVBoxLayout(left_panel_widget)
        right_layout = QVBoxLayout(right_panel_widget)
        left_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setContentsMargins(10, 10, 10, 10)


        url_page_layout = QHBoxLayout()
        url_page_layout.setContentsMargins(0,0,0,0)
        url_page_layout.addWidget(QLabel("🔗 Kemono Creator/Post URL:"))
        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("e.g., https://kemono.su/patreon/user/12345 or .../post/98765")
        self.link_input.setToolTip("Enter the full URL of a Kemono/Coomer creator's page or a specific post.\nExample (Creator): https://kemono.su/patreon/user/12345\nExample (Post): https://kemono.su/patreon/user/12345/post/98765")
        self.link_input.textChanged.connect(self.update_custom_folder_visibility)
        url_page_layout.addWidget(self.link_input, 1) # URL input takes available space


        self.page_range_label = QLabel("Page Range:")
        self.page_range_label.setStyleSheet("font-weight: bold; padding-left: 10px;")
        self.start_page_input = QLineEdit()
        self.start_page_input.setPlaceholderText("Start")
        self.start_page_input.setFixedWidth(50)
        self.start_page_input.setToolTip("For creator URLs: Specify the starting page number to download from (e.g., 1, 2, 3).\nLeave blank or set to 1 to start from the first page.\nDisabled for single post URLs or Manga/Comic Mode.")
        self.start_page_input.setValidator(QIntValidator(1, 99999))
        self.to_label = QLabel("to")
        self.end_page_input = QLineEdit()
        self.end_page_input.setPlaceholderText("End")
        self.end_page_input.setFixedWidth(50)
        self.end_page_input.setToolTip("For creator URLs: Specify the ending page number to download up to (e.g., 5, 10).\nLeave blank to download all pages from the start page.\nDisabled for single post URLs or Manga/Comic Mode.")
        self.end_page_input.setValidator(QIntValidator(1, 99999))
        url_page_layout.addWidget(self.page_range_label)
        url_page_layout.addWidget(self.start_page_input)
        url_page_layout.addWidget(self.to_label)
        url_page_layout.addWidget(self.end_page_input)
        left_layout.addLayout(url_page_layout)

        left_layout.addWidget(QLabel("📁 Download Location:"))
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select folder where downloads will be saved")
        self.dir_input.setToolTip("Enter or browse to the main folder where all downloaded content will be saved.\nThis is required unless 'Only Links' mode is selected.")
        self.dir_button = QPushButton("Browse...")
        self.dir_button.clicked.connect(self.browse_directory)
        self.dir_button.setToolTip("Click to open a dialog to select the main download folder.")
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.dir_input, 1)
        dir_layout.addWidget(self.dir_button)
        left_layout.addLayout(dir_layout)


        self.filters_and_custom_folder_container_widget = QWidget()
        filters_and_custom_folder_layout = QHBoxLayout(self.filters_and_custom_folder_container_widget)
        filters_and_custom_folder_layout.setContentsMargins(0, 5, 0, 0)
        filters_and_custom_folder_layout.setSpacing(10)

        self.character_filter_widget = QWidget()
        character_filter_v_layout = QVBoxLayout(self.character_filter_widget)
        character_filter_v_layout.setContentsMargins(0,0,0,0)
        character_filter_v_layout.setSpacing(2)
        
        self.character_label = QLabel("🎯 Filter by Character(s) (comma-separated):")
        character_filter_v_layout.addWidget(self.character_label)

        char_input_and_button_layout = QHBoxLayout()
        char_input_and_button_layout.setContentsMargins(0, 0, 0, 0)
        char_input_and_button_layout.setSpacing(10)

        self.character_input = QLineEdit()
        self.character_input.setPlaceholderText("e.g., Tifa, Aerith, (Cloud, Zack)")
        self.character_input.setToolTip(
            "Filter by character/series names (comma-separated, e.g., Tifa, Aerith).\n"
            "The behavior of this filter (Files, Title, Both, or Comments) is controlled by the 'Filter: [Scope]' button next to this input.\n"
            "Also used for folder naming if 'Separate Folders' is enabled.\n"
            "Group aliases for a combined folder name: (alias1, alias2) -> folder 'alias1 alias2'.\n"
            "Example: yor, Tifa, (Boa, Hancock)")
        char_input_and_button_layout.addWidget(self.character_input, 3)

        self.char_filter_scope_toggle_button = QPushButton()
        # Initial text and tooltip will be set by calling _update_char_filter_scope_button_text()
        # at the end of init_ui or when the scope is first set.
        self._update_char_filter_scope_button_text()
        self.char_filter_scope_toggle_button.setStyleSheet("padding: 6px 10px;")
        self.char_filter_scope_toggle_button.setMinimumWidth(100)
        char_input_and_button_layout.addWidget(self.char_filter_scope_toggle_button, 1)

        character_filter_v_layout.addLayout(char_input_and_button_layout)


        self.custom_folder_widget = QWidget()
        custom_folder_v_layout = QVBoxLayout(self.custom_folder_widget)
        custom_folder_v_layout.setContentsMargins(0,0,0,0)
        custom_folder_v_layout.setSpacing(2)
        self.custom_folder_label = QLabel("🗄️ Custom Folder Name (Single Post Only):")
        self.custom_folder_input = QLineEdit()
        self.custom_folder_input.setToolTip(
            "If downloading a single post URL AND 'Separate Folders by Name/Title' is enabled,\n"
            "you can enter a custom name here for that post's download folder.\n"
            "Example: My Favorite Scene")
        self.custom_folder_input.setPlaceholderText("Optional: Save this post to specific folder")
        custom_folder_v_layout.addWidget(self.custom_folder_label)
        custom_folder_v_layout.addWidget(self.custom_folder_input)
        self.custom_folder_widget.setVisible(False)

        filters_and_custom_folder_layout.addWidget(self.character_filter_widget, 1)
        filters_and_custom_folder_layout.addWidget(self.custom_folder_widget, 1)

        left_layout.addWidget(self.filters_and_custom_folder_container_widget)


        # --- Word Manipulation Section (Skip Words & Remove from Filename) ---
        word_manipulation_container_widget = QWidget()
        word_manipulation_outer_layout = QHBoxLayout(word_manipulation_container_widget)
        word_manipulation_outer_layout.setContentsMargins(0,0,0,0) # No margins for the outer container
        word_manipulation_outer_layout.setSpacing(15) # Spacing between the two vertical groups

        # Group 1: Skip Words (Left, ~70% space)
        skip_words_widget = QWidget()
        skip_words_vertical_layout = QVBoxLayout(skip_words_widget)
        skip_words_vertical_layout.setContentsMargins(0,0,0,0) # No margins for the inner group
        skip_words_vertical_layout.setSpacing(2) # Small spacing between label and input row

        skip_words_label = QLabel("🚫 Skip with Words (comma-separated):")
        skip_words_vertical_layout.addWidget(skip_words_label)

        skip_input_and_button_layout = QHBoxLayout()
        skip_input_and_button_layout = QHBoxLayout()
        skip_input_and_button_layout.setContentsMargins(0, 0, 0, 0)
        skip_input_and_button_layout.setSpacing(10)
        self.skip_words_input = QLineEdit()
        self.skip_words_input.setToolTip(
            "Enter words, comma-separated, to skip downloading certain files or posts.\n"
            "The 'Scope' button determines if this applies to file names, post titles, or both.\n"
            "Example: WIP, sketch, preview, text post"
        )
        self.skip_words_input.setPlaceholderText("e.g., WM, WIP, sketch, preview")
        skip_input_and_button_layout.addWidget(self.skip_words_input, 1) # Input field takes available space
        self.skip_scope_toggle_button = QPushButton()
        self._update_skip_scope_button_text()
        self.skip_scope_toggle_button.setStyleSheet("padding: 6px 10px;")
        self.skip_scope_toggle_button.setMinimumWidth(100)
        skip_input_and_button_layout.addWidget(self.skip_scope_toggle_button, 0) # Button takes its minimum
        skip_words_vertical_layout.addLayout(skip_input_and_button_layout)
        word_manipulation_outer_layout.addWidget(skip_words_widget, 7) # 70% stretch for left group

        # Group 2: Remove Words from name (Right, ~30% space)
        remove_words_widget = QWidget()
        remove_words_vertical_layout = QVBoxLayout(remove_words_widget)
        remove_words_vertical_layout.setContentsMargins(0,0,0,0) # No margins for the inner group
        remove_words_vertical_layout.setSpacing(2)
        self.remove_from_filename_label = QLabel("✂️ Remove Words from name:")
        remove_words_vertical_layout.addWidget(self.remove_from_filename_label)
        self.remove_from_filename_input = QLineEdit()
        self.remove_from_filename_input.setToolTip(
            "Enter words, comma-separated, to remove from downloaded filenames (case-insensitive).\n"
            "Useful for cleaning up common prefixes/suffixes.\n"
            "Example: patreon, kemono, [HD], _final"
        )
        self.remove_from_filename_input.setPlaceholderText("e.g., patreon, HD") # Placeholder for the new field
        remove_words_vertical_layout.addWidget(self.remove_from_filename_input)
        word_manipulation_outer_layout.addWidget(remove_words_widget, 3) # 30% stretch for right group

        left_layout.addWidget(word_manipulation_container_widget)
        # --- End Word Manipulation Section ---


        file_filter_layout = QVBoxLayout()
        file_filter_layout.setContentsMargins(0,10,0,0)
        file_filter_layout.addWidget(QLabel("Filter Files:"))
        radio_button_layout = QHBoxLayout()
        radio_button_layout.setSpacing(10)
        self.radio_group = QButtonGroup(self)
        self.radio_all = QRadioButton("All")
        self.radio_all.setToolTip("Download all file types found in posts.")
        self.radio_images = QRadioButton("Images/GIFs")
        self.radio_images.setToolTip("Download only common image formats (JPG, PNG, GIF, WEBP, etc.).")
        self.radio_videos = QRadioButton("Videos")
        self.radio_videos.setToolTip("Download only common video formats (MP4, MKV, WEBM, MOV, etc.).")
        self.radio_only_archives = QRadioButton("📦 Only Archives")
        self.radio_only_archives.setToolTip("Exclusively download .zip and .rar files. Other file-specific options are disabled.")
        self.radio_only_links = QRadioButton("🔗 Only Links")
        self.radio_only_links.setToolTip("Extract and display external links from post descriptions instead of downloading files.\nDownload-related options will be disabled.")
        self.radio_all.setChecked(True)
        self.radio_group.addButton(self.radio_all)
        self.radio_group.addButton(self.radio_images)
        self.radio_group.addButton(self.radio_videos)
        self.radio_group.addButton(self.radio_only_archives)
        self.radio_group.addButton(self.radio_only_links)
        radio_button_layout.addWidget(self.radio_all)
        radio_button_layout.addWidget(self.radio_images)
        radio_button_layout.addWidget(self.radio_videos)
        radio_button_layout.addWidget(self.radio_only_archives)
        radio_button_layout.addWidget(self.radio_only_links)
        radio_button_layout.addStretch(1)
        file_filter_layout.addLayout(radio_button_layout)
        left_layout.addLayout(file_filter_layout)

        checkboxes_group_layout = QVBoxLayout()
        checkboxes_group_layout.setSpacing(10)
        
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(10)
        self.skip_zip_checkbox = QCheckBox("Skip .zip")
        self.skip_zip_checkbox.setToolTip("If checked, .zip archive files will not be downloaded.\n(Disabled if 'Only Archives' is selected).")
        self.skip_zip_checkbox.setChecked(True)
        row1_layout.addWidget(self.skip_zip_checkbox)
        self.skip_rar_checkbox = QCheckBox("Skip .rar")
        self.skip_rar_checkbox.setToolTip("If checked, .rar archive files will not be downloaded.\n(Disabled if 'Only Archives' is selected).")
        self.skip_rar_checkbox.setChecked(True)
        row1_layout.addWidget(self.skip_rar_checkbox)
        self.download_thumbnails_checkbox = QCheckBox("Download Thumbnails Only")
        # Tooltip already exists for download_thumbnails_checkbox
        self.download_thumbnails_checkbox.setChecked(False)
        self.download_thumbnails_checkbox.setToolTip("Thumbnail download functionality is currently limited without the API.")
        row1_layout.addWidget(self.download_thumbnails_checkbox)
        self.compress_images_checkbox = QCheckBox("Compress Large Images (to WebP)")
        self.compress_images_checkbox.setChecked(False)
        self.compress_images_checkbox.setToolTip("Compress images > 1.5MB to WebP format (requires Pillow).")
        row1_layout.addWidget(self.compress_images_checkbox)
        row1_layout.addStretch(1)
        checkboxes_group_layout.addLayout(row1_layout)

        advanced_settings_label = QLabel("⚙️ Advanced Settings:")
        checkboxes_group_layout.addWidget(advanced_settings_label)
        
        advanced_row1_layout = QHBoxLayout()
        advanced_row1_layout.setSpacing(10)
        self.use_subfolders_checkbox = QCheckBox("Separate Folders by Name/Title")
        self.use_subfolders_checkbox.setToolTip(
            "Create subfolders based on 'Filter by Character(s)' input or post titles.\n"
            "Uses 'Known Shows/Characters' list as a fallback for folder names if no specific filter matches.\n"
            "Enables the 'Filter by Character(s)' input and 'Custom Folder Name' for single posts.")
        self.use_subfolders_checkbox.setChecked(True)
        self.use_subfolders_checkbox.toggled.connect(self.update_ui_for_subfolders)
        advanced_row1_layout.addWidget(self.use_subfolders_checkbox)
        self.use_subfolder_per_post_checkbox = QCheckBox("Subfolder per Post")
        self.use_subfolder_per_post_checkbox.setChecked(False)
        self.use_subfolder_per_post_checkbox.setToolTip(
            "Creates a subfolder for each post. If 'Separate Folders' is also on, it's inside the character/title folder."
        )
        self.use_subfolder_per_post_checkbox.toggled.connect(self.update_ui_for_subfolders)
        advanced_row1_layout.addWidget(self.use_subfolder_per_post_checkbox)

        self.use_cookie_checkbox = QCheckBox("Use Cookie")
        self.use_cookie_checkbox.setToolTip("If checked, will attempt to use cookies from 'cookies.txt' (Netscape format)\n"
                                            "in the application directory for requests.\n"
                                            "Useful for accessing content that requires login on Kemono/Coomer.")
        self.use_cookie_checkbox.setChecked(self.use_cookie_setting) # Set from loaded setting
        
        self.cookie_text_input = QLineEdit()
        self.cookie_text_input.setPlaceholderText("if no Select cookies.txt)")
        self.cookie_text_input.setMinimumHeight(28) # Slightly increase height for better visibility
        self.cookie_text_input.setToolTip("Enter your cookie string directly.\n"
                                          "This will be used if 'Use Cookie' is checked AND 'cookies.txt' is not found or this field is not empty.\n"
                                          "The format depends on how the backend will parse it (e.g., 'name1=value1; name2=value2').")
        self.cookie_text_input.setText(self.cookie_text_setting) # Set from loaded setting
        
        advanced_row1_layout.addWidget(self.use_cookie_checkbox)
        advanced_row1_layout.addWidget(self.cookie_text_input, 2) # Stretch factor 2

        self.cookie_browse_button = QPushButton("Browse...")
        self.cookie_browse_button.setToolTip("Browse for a cookie file (Netscape format, typically cookies.txt).\nThis will be used if 'Use Cookie' is checked and the text field above is empty.")
        self.cookie_browse_button.setFixedWidth(80) # Make it a bit compact
        self.cookie_browse_button.setStyleSheet("padding: 4px 8px;")
        advanced_row1_layout.addWidget(self.cookie_browse_button)

        advanced_row1_layout.addStretch(1)
        checkboxes_group_layout.addLayout(advanced_row1_layout)

        advanced_row2_layout = QHBoxLayout()
        advanced_row2_layout.setSpacing(10)
        
        multithreading_layout = QHBoxLayout()
        multithreading_layout.setContentsMargins(0,0,0,0)
        self.use_multithreading_checkbox = QCheckBox("Use Multithreading")
        # Tooltip already exists for use_multithreading_checkbox
        self.use_multithreading_checkbox.setChecked(True)
        self.use_multithreading_checkbox.setToolTip(
            "Enables concurrent operations. See 'Threads' input for details."
        )
        multithreading_layout.addWidget(self.use_multithreading_checkbox)
        self.thread_count_label = QLabel("Threads:")
        multithreading_layout.addWidget(self.thread_count_label)
        self.thread_count_input = QLineEdit()
        # Tooltip already exists for thread_count_input
        self.thread_count_input.setFixedWidth(40)
        self.thread_count_input.setText("4")
        self.thread_count_input.setToolTip(
            f"Number of concurrent operations.\n"
            f"- Single Post: Concurrent file downloads (1-{MAX_FILE_THREADS_PER_POST_OR_WORKER} recommended).\n"
            f"- Creator Feed URL: Number of posts to process simultaneously (1-{MAX_THREADS} recommended).\n"
            f"  Files within each post are downloaded one by one by its worker.\n"
            f"If 'Use Multithreading' is unchecked, 1 thread is used."
        )
        self.thread_count_input.setValidator(QIntValidator(1, MAX_THREADS))
        multithreading_layout.addWidget(self.thread_count_input)
        advanced_row2_layout.addLayout(multithreading_layout)

        self.external_links_checkbox = QCheckBox("Show External Links in Log")
        self.external_links_checkbox.setToolTip(
            "If checked, a secondary log panel appears below the main log to display external links found in post descriptions.\n"
            "(Disabled if 'Only Links' or 'Only Archives' mode is active).")
        self.external_links_checkbox.setChecked(False)
        advanced_row2_layout.addWidget(self.external_links_checkbox)

        self.manga_mode_checkbox = QCheckBox("Manga/Comic Mode")
        # Tooltip already exists for manga_mode_checkbox
        self.manga_mode_checkbox.setToolTip("Downloads posts from oldest to newest and renames files based on post title (for creator feeds only).")
        self.manga_mode_checkbox.setChecked(False)
        advanced_row2_layout.addWidget(self.manga_mode_checkbox) # Keep manga mode checkbox here

        advanced_row2_layout.addStretch(1)
        checkboxes_group_layout.addLayout(advanced_row2_layout)
        left_layout.addLayout(checkboxes_group_layout)


        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.download_btn = QPushButton("⬇️ Start Download")
        self.download_btn.setToolTip("Click to start the download or link extraction process with the current settings.")
        self.download_btn.setStyleSheet("padding: 8px 15px; font-weight: bold;")
        self.download_btn.clicked.connect(self.start_download)
        self.cancel_btn = QPushButton("❌ Cancel & Reset UI") # Updated button text for clarity
        self.pause_btn = QPushButton("⏸️ Pause Download")
        self.pause_btn.setToolTip("Click to pause the ongoing download process.")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self._handle_pause_resume_action)

        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setToolTip("Click to cancel the ongoing download/extraction process and reset the UI fields (preserving URL and Directory).")
        self.cancel_btn.clicked.connect(self.cancel_download_button_action) # Changed connection
        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.pause_btn) # Add pause button in the middle
        btn_layout.addWidget(self.cancel_btn)
        left_layout.addLayout(btn_layout)
        left_layout.addSpacing(10)


        known_chars_label_layout = QHBoxLayout()
        known_chars_label_layout.setSpacing(10)
        self.known_chars_label = QLabel("🎭 Known Shows/Characters (for Folder Names):")
        known_chars_label_layout.addWidget(self.known_chars_label) # Add label first

        # Create and add the "Open Known.txt" button BEFORE the search input
        self.open_known_txt_button = QPushButton("Open Known.txt")
        self.open_known_txt_button.setToolTip("Open the 'Known.txt' file in your default text editor.\nThe file is located in the application's directory.")
        self.open_known_txt_button.setStyleSheet("padding: 4px 8px;") # Consistent small button style
        self.open_known_txt_button.setFixedWidth(120) # Adjust width as needed
        known_chars_label_layout.addWidget(self.open_known_txt_button) # Add button second

        # Then create and add the character search input, allowing it to stretch
        self.character_search_input = QLineEdit()
        self.character_search_input.setToolTip("Type here to filter the list of known shows/characters below.")
        self.character_search_input.setPlaceholderText("Search characters...")
        known_chars_label_layout.addWidget(self.character_search_input, 1) # Added stretch factor of 1
        left_layout.addLayout(known_chars_label_layout)

        self.character_list = QListWidget()
        self.character_list.setToolTip(
            "This list contains names used for automatic folder creation when 'Separate Folders' is on\n"
            "and no specific 'Filter by Character(s)' is provided or matches a post.\n"
            "Add names of series, games, or characters you frequently download.")
        self.character_list.setSelectionMode(QListWidget.ExtendedSelection)
        left_layout.addWidget(self.character_list, 1)

        char_manage_layout = QHBoxLayout()
        char_manage_layout.setSpacing(10)
        self.new_char_input = QLineEdit()
        self.new_char_input.setToolTip("Enter a new show, game, or character name to add to the list above.")
        self.new_char_input.setPlaceholderText("Add new show/character name")
        self.add_char_button = QPushButton("➕ Add")
        self.add_char_button.setToolTip("Add the name from the input field to the 'Known Shows/Characters' list.")
        self.delete_char_button = QPushButton("🗑️ Delete Selected")
        self.delete_char_button.setToolTip("Delete the selected name(s) from the 'Known Shows/Characters' list.")
        self.add_char_button.clicked.connect(self.add_new_character)
        self.new_char_input.returnPressed.connect(self.add_char_button.click)
        self.delete_char_button.clicked.connect(self.delete_selected_character)
        char_manage_layout.addWidget(self.new_char_input, 2)
        char_manage_layout.addWidget(self.add_char_button, 1)
        char_manage_layout.addWidget(self.delete_char_button, 1)
        left_layout.addLayout(char_manage_layout)
        left_layout.addStretch(0)

        log_title_layout = QHBoxLayout()
        self.progress_log_label = QLabel("📜 Progress Log:")
        log_title_layout.addWidget(self.progress_log_label)
        log_title_layout.addStretch(1)

        self.link_search_input = QLineEdit()
        self.link_search_input.setToolTip("When in 'Only Links' mode, type here to filter the displayed links by text, URL, or platform.")
        self.link_search_input.setPlaceholderText("Search Links...")
        self.link_search_input.setVisible(False)
        self.link_search_input.setFixedWidth(150)
        log_title_layout.addWidget(self.link_search_input)
        self.link_search_button = QPushButton("🔍")
        self.link_search_button.setToolTip("Filter displayed links")
        self.link_search_button.setVisible(False)
        self.link_search_button.setFixedWidth(30)
        self.link_search_button.setStyleSheet("padding: 4px 4px;")
        log_title_layout.addWidget(self.link_search_button)

        self.manga_rename_toggle_button = QPushButton()
        self.manga_rename_toggle_button.setVisible(False)
        self.manga_rename_toggle_button.setFixedWidth(140)
        self.manga_rename_toggle_button.setStyleSheet("padding: 4px 8px;")
        self._update_manga_filename_style_button_text()
        log_title_layout.addWidget(self.manga_rename_toggle_button)
        
        self.multipart_toggle_button = QPushButton()
        self.multipart_toggle_button.setToolTip("Toggle between Multi-part and Single-stream downloads for large files.")
        self.multipart_toggle_button.setFixedWidth(130) # Adjust width as needed
        self.multipart_toggle_button.setStyleSheet("padding: 4px 8px;") # Added padding
        self._update_multipart_toggle_button_text() # Set initial text
        log_title_layout.addWidget(self.multipart_toggle_button) # Add to layout

        self.EYE_ICON = "\U0001F441"  # 👁️
        self.CLOSED_EYE_ICON = "\U0001F648" # 🙈
        self.log_verbosity_toggle_button = QPushButton(self.EYE_ICON) # Initial state: Progress Log visible
        self.log_verbosity_toggle_button.setToolTip("Current View: Progress Log. Click to switch to Missed Character Log.")
        self.log_verbosity_toggle_button.setFixedWidth(45) # Adjusted for emoji
        self.log_verbosity_toggle_button.setStyleSheet("font-size: 11pt; padding: 2px 2px 3px 2px;")
        log_title_layout.addWidget(self.log_verbosity_toggle_button)

        self.reset_button = QPushButton("🔄 Reset")
        self.reset_button.setToolTip("Reset all inputs and logs to default state (only when idle).")
        self.reset_button.setFixedWidth(80)
        self.reset_button.setStyleSheet("padding: 4px 8px;")
        log_title_layout.addWidget(self.reset_button)
        right_layout.addLayout(log_title_layout)

        self.log_splitter = QSplitter(Qt.Vertical)
        
        self.log_view_stack = QStackedWidget() # Create the stack

        self.main_log_output = QTextEdit()
        self.main_log_output.setToolTip("Displays progress messages, errors, and summaries. In 'Only Links' mode, shows extracted links.")
        self.main_log_output.setReadOnly(True)
        self.main_log_output.setLineWrapMode(QTextEdit.NoWrap)
        self.main_log_output.setStyleSheet("""
            QTextEdit { background-color: #3C3F41; border: 1px solid #5A5A5A; padding: 5px;
                         color: #F0F0F0; border-radius: 4px; font-family: Consolas, Courier New, monospace; font-size: 9.5pt; }""")
        self.log_view_stack.addWidget(self.main_log_output) # Add progress log to stack

        self.missed_character_log_output = QTextEdit() # Create missed character log
        self.missed_character_log_output.setToolTip("Displays information about posts/files skipped due to character filters.")
        self.missed_character_log_output.setReadOnly(True)
        self.missed_character_log_output.setLineWrapMode(QTextEdit.NoWrap) # Or QTextEdit.WidgetWidth
        self.missed_character_log_output.setStyleSheet(self.main_log_output.styleSheet()) # Use same style
        self.log_view_stack.addWidget(self.missed_character_log_output) # Add missed char log to stack

        self.external_log_output = QTextEdit()
        self.external_log_output.setToolTip("If 'Show External Links in Log' is checked, this panel displays external links found in post descriptions.")
        self.external_log_output.setReadOnly(True)
        self.external_log_output.setLineWrapMode(QTextEdit.NoWrap)
        self.external_log_output.setStyleSheet("""
            QTextEdit { background-color: #3C3F41; border: 1px solid #5A5A5A; padding: 5px;
                         color: #F0F0F0; border-radius: 4px; font-family: Consolas, Courier New, monospace; font-size: 9.5pt; }""")
        self.external_log_output.hide()

        self.log_splitter.addWidget(self.log_view_stack) # Add stack to splitter (first widget)
        self.log_splitter.addWidget(self.external_log_output)
        self.log_splitter.setSizes([self.height(), 0])
        right_layout.addWidget(self.log_splitter, 1)

        export_button_layout = QHBoxLayout()
        export_button_layout.addStretch(1)
        self.export_links_button = QPushButton("Export Links")
        # Tooltip already exists for export_links_button
        self.export_links_button.setToolTip("Export all extracted links to a .txt file.")
        self.export_links_button.setFixedWidth(100)
        self.export_links_button.setStyleSheet("padding: 4px 8px; margin-top: 5px;")
        self.export_links_button.setEnabled(False)
        self.export_links_button.setVisible(False)
        export_button_layout.addWidget(self.export_links_button)
        right_layout.addLayout(export_button_layout)


        self.progress_label = QLabel("Progress: Idle")
        self.progress_label.setToolTip("Shows the overall progress of the download or link extraction process (e.g., posts processed).")
        self.progress_label.setStyleSheet("padding-top: 5px; font-style: italic;")
        right_layout.addWidget(self.progress_label)
        self.file_progress_label = QLabel("")
        self.file_progress_label.setToolTip("Shows the progress of individual file downloads, including speed and size.")
        self.file_progress_label.setWordWrap(True)
        self.file_progress_label.setStyleSheet("padding-top: 2px; font-style: italic; color: #A0A0A0;")
        right_layout.addWidget(self.file_progress_label)


        self.main_splitter.addWidget(left_panel_widget)
        self.main_splitter.addWidget(right_panel_widget)
        initial_width = self.width()
        left_width = int(initial_width * 0.35)
        right_width = initial_width - left_width
        self.main_splitter.setSizes([left_width, right_width])

        top_level_layout = QHBoxLayout(self)
        top_level_layout.setContentsMargins(0,0,0,0)
        top_level_layout.addWidget(self.main_splitter)

        self.update_ui_for_subfolders(self.use_subfolders_checkbox.isChecked())
        self.update_external_links_setting(self.external_links_checkbox.isChecked())
        self.update_multithreading_label(self.thread_count_input.text())
        self.update_page_range_enabled_state()
        if self.manga_mode_checkbox:
            self.update_ui_for_manga_mode(self.manga_mode_checkbox.isChecked())
        if hasattr(self, 'link_input'): self.link_input.textChanged.connect(lambda: self.update_ui_for_manga_mode(self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False)) # Also trigger manga UI update
        self.load_known_names_from_util()
        self._update_cookie_input_visibility(self.use_cookie_checkbox.isChecked() if hasattr(self, 'use_cookie_checkbox') else False) # Initial visibility
        self._handle_multithreading_toggle(self.use_multithreading_checkbox.isChecked())
        if hasattr(self, 'radio_group') and self.radio_group.checkedButton():
            self._handle_filter_mode_change(self.radio_group.checkedButton(), True)
        self._update_manga_filename_style_button_text()
        self._update_skip_scope_button_text()
        self._update_char_filter_scope_button_text()
        self._update_multithreading_for_date_mode() # Ensure correct initial state
        
    def _browse_cookie_file(self):
        """Opens a file dialog to select a cookie file."""
        # Start in the user's documents directory or current app dir if not available
        start_dir = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        if not start_dir:
            start_dir = os.path.dirname(self.config_file) # App directory

        filepath, _ = QFileDialog.getOpenFileName(self, "Select Cookie File", start_dir, "Text files (*.txt);;All files (*)")
        if filepath:
            self.selected_cookie_filepath = filepath
            self.log_signal.emit(f"ℹ️ Selected cookie file: {filepath}")
            if hasattr(self, 'cookie_text_input'):
                # Block signals temporarily to prevent textChanged handler from misinterpreting this programmatic change
                self.cookie_text_input.blockSignals(True)
                self.cookie_text_input.setText(filepath)
                self.cookie_text_input.setReadOnly(True)
                self.cookie_text_input.setPlaceholderText("") # No placeholder when showing a path
                self.cookie_text_input.blockSignals(False)

    def _center_on_screen(self):
        """Centers the widget on the screen."""
        # Updated to use availableGeometry and center more reliably        
        try:
            primary_screen = QApplication.primaryScreen()
            if not primary_screen:
                screens = QApplication.screens()
                if not screens: return # Cannot center
                primary_screen = screens[0]
            
            available_geo = primary_screen.availableGeometry()
            widget_geo = self.frameGeometry()
            
            x = available_geo.x() + (available_geo.width() - widget_geo.width()) // 2
            y = available_geo.y() + (available_geo.height() - widget_geo.height()) // 2
            self.move(x, y)
        except Exception as e:
            self.log_signal.emit(f"⚠️ Error centering window: {e}")
            
    def _handle_cookie_text_manual_change(self, text):
        """Handles manual changes to the cookie text input, especially clearing a browsed path."""
        if not hasattr(self, 'cookie_text_input') or not hasattr(self, 'use_cookie_checkbox'):
            return

        # If a file was selected AND the text field is now empty (user deleted the path)
        if self.selected_cookie_filepath and not text.strip() and self.use_cookie_checkbox.isChecked():
            self.selected_cookie_filepath = None
            self.cookie_text_input.setReadOnly(False)
            self.cookie_text_input.setPlaceholderText("Cookie string (if no cookies.txt)")
            self.log_signal.emit("ℹ️ Browsed cookie file path cleared from input. Switched to manual cookie string mode.")


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
        QSplitter::handle { background-color: #5A5A5A; }
        QSplitter::handle:horizontal { width: 5px; }
        QSplitter::handle:vertical { height: 5px; }
        QFrame[frameShape="4"], QFrame[frameShape="5"] { 
            border: 1px solid #4A4A4A; 
            border-radius: 3px;
        }
        """

    def browse_directory(self):
        current_dir = self.dir_input.text() if os.path.isdir(self.dir_input.text()) else ""
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", current_dir)
        if folder:
            self.dir_input.setText(folder)

    def handle_main_log(self, message):
        is_html_message = message.startswith(HTML_PREFIX)
        display_message = message
        use_html = False
        
        if is_html_message:
             display_message = message[len(HTML_PREFIX):]
             use_html = True
        # Basic log mode toggle is removed for this button. Progress log is always "full".
        
        try:
             safe_message = str(display_message).replace('\x00', '[NULL]')
             if use_html:
                 self.main_log_output.insertHtml(safe_message)
             else:
                 self.main_log_output.append(safe_message)

             scrollbar = self.main_log_output.verticalScrollBar()
             if scrollbar.value() >= scrollbar.maximum() - 30:
                 scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
             print(f"GUI Main Log Error: {e}\nOriginal Message: {message}")
    def _extract_key_term_from_title(self, title):
        if not title:
            return None
        # Try to find words that look like names/keywords
        title_cleaned = re.sub(r'\[.*?\]', '', title) # Remove content in square brackets
        title_cleaned = re.sub(r'\(.*?\)', '', title_cleaned) # Remove content in parentheses
        title_cleaned = title_cleaned.strip()

        # Find all words and their original start positions
        word_matches = list(re.finditer(r'\b[a-zA-Z][a-zA-Z0-9_-]*\b', title_cleaned))
        
        capitalized_candidates = []
        for match in word_matches:
            word = match.group(0)
            # istitle() checks if first char is upper and rest lower (or non-cased like numbers)
            # We also check if the whole word is not uppercase (like "AI") unless it's short
            if word.istitle() and word.lower() not in self.STOP_WORDS and len(word) > 2:
                 if not (len(word) > 3 and word.isupper()): # Avoid all-caps words unless short (like "AI")
                    capitalized_candidates.append({'text': word, 'len': len(word), 'pos': match.start()})
        
        if capitalized_candidates:
            # Sort by length (desc), then by original position (desc - later words preferred if same length)
            capitalized_candidates.sort(key=lambda x: (x['len'], x['pos']), reverse=True)
            return capitalized_candidates[0]['text']

        # Fallback: longest word not in stop words, if no good capitalized word found
        non_capitalized_words_info = []
        for match in word_matches:
            word = match.group(0)
            if word.lower() not in self.STOP_WORDS and len(word) > 3: # Min length 4 for non-capitalized
                 non_capitalized_words_info.append({'text': word, 'len': len(word), 'pos': match.start()})
        
        if non_capitalized_words_info:
            # Sort by length (desc), then position (desc - later preferred if same length)
            non_capitalized_words_info.sort(key=lambda x: (x['len'], x['pos']), reverse=True)
            return non_capitalized_words_info[0]['text']
                
        return None

    def handle_missed_character_post(self, post_title, reason):
        if self.missed_character_log_output:
            key_term = self._extract_key_term_from_title(post_title)

            if key_term:
                normalized_key_term = key_term.lower()
                if normalized_key_term not in self.already_logged_bold_key_terms:
                    # Use the extracted key_term directly to preserve its original casing for display
                    self.already_logged_bold_key_terms.add(normalized_key_term)
                    self.missed_key_terms_buffer.append(key_term) # Store original case
                    self._refresh_missed_character_log()
        else: # Fallback if UI element isn't ready (should not happen in normal operation)
            print(f"Debug (Missed Char Log): Title='{post_title}', Reason='{reason}'")

    def _refresh_missed_character_log(self):
        if self.missed_character_log_output:
            self.missed_character_log_output.clear()
            # Sort case-insensitively but keep original casing from buffer
            sorted_terms = sorted(self.missed_key_terms_buffer, key=str.lower)
            separator_line = "-" * 40  # Define the separator
            
            for term in sorted_terms:
                display_term = term.capitalize() # Ensure first letter is capitalized

                self.missed_character_log_output.append(separator_line)
                # Center the bold, blue text using a <p> tag with align attribute
                self.missed_character_log_output.append(f'<p align="center"><b><font style="font-size: 12.4pt; color: #87CEEB;">{display_term}</font></b></p>')
                self.missed_character_log_output.append(separator_line)
                self.missed_character_log_output.append("") # Add a blank line for spacing
            
            scrollbar = self.missed_character_log_output.verticalScrollBar()
            scrollbar.setValue(0) # Scroll to top after refresh

    def _is_download_active(self):
        single_thread_active = self.download_thread and self.download_thread.isRunning()
        pool_active = self.thread_pool is not None and any(not f.done() for f in self.active_futures if f is not None)
        return single_thread_active or pool_active

    def handle_external_link_signal(self, post_title, link_text, link_url, platform):
        link_data = (post_title, link_text, link_url, platform)
        self.external_link_queue.append(link_data)
        if self.radio_only_links and self.radio_only_links.isChecked():
            self.extracted_links_cache.append(link_data)
        self._try_process_next_external_link()

    def _try_process_next_external_link(self):
        if self._is_processing_external_link_queue or not self.external_link_queue:
             return

        is_only_links_mode = self.radio_only_links and self.radio_only_links.isChecked()
        should_display_in_external_log = self.show_external_links and not is_only_links_mode

        if not (is_only_links_mode or should_display_in_external_log):
             self._is_processing_external_link_queue = False
             if self.external_link_queue:
                 QTimer.singleShot(0, self._try_process_next_external_link)
             return

        self._is_processing_external_link_queue = True
        link_data = self.external_link_queue.popleft()

        if is_only_links_mode:
            delay_ms = 80
            QTimer.singleShot(delay_ms, lambda data=link_data: self._display_and_schedule_next(data))
        elif self._is_download_active():
            delay_ms = random.randint(4000, 8000)
            QTimer.singleShot(delay_ms, lambda data=link_data: self._display_and_schedule_next(data))
        else:
            QTimer.singleShot(0, lambda data=link_data: self._display_and_schedule_next(data))


    def _display_and_schedule_next(self, link_data):
        post_title, link_text, link_url, platform = link_data
        is_only_links_mode = self.radio_only_links and self.radio_only_links.isChecked()

        max_link_text_len = 35
        display_text = link_text[:max_link_text_len].strip() + "..." if len(link_text) > max_link_text_len else link_text
        formatted_link_info = f"{display_text} - {link_url} - {platform}"
        separator = "-" * 45

        if is_only_links_mode:
            if post_title != self._current_link_post_title:
                self.log_signal.emit(HTML_PREFIX + "<br>" + separator + "<br>")
                title_html = f'<b style="color: #87CEEB;">{post_title}</b><br>'
                self.log_signal.emit(HTML_PREFIX + title_html)
                self._current_link_post_title = post_title
            self.log_signal.emit(formatted_link_info)
        elif self.show_external_links:
             self._append_to_external_log(formatted_link_info, separator)

        self._is_processing_external_link_queue = False
        self._try_process_next_external_link()


    def _append_to_external_log(self, formatted_link_text, separator):
        if not (self.external_log_output and self.external_log_output.isVisible()):
            return

        try:
            self.external_log_output.append(formatted_link_text)
            self.external_log_output.append("")

            scrollbar = self.external_log_output.verticalScrollBar()
            if scrollbar.value() >= scrollbar.maximum() - 50:
                scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
             self.log_signal.emit(f"GUI External Log Append Error: {e}\nOriginal Message: {formatted_link_text}")
             print(f"GUI External Log Error (Append): {e}\nOriginal Message: {formatted_link_text}")


    def update_file_progress_display(self, filename, progress_info):
        if not filename and progress_info is None: # Explicit clear
            self.file_progress_label.setText("")
            return

        if isinstance(progress_info, list):  # Multi-part progress (list of chunk dicts)
            if not progress_info: # Empty list
                self.file_progress_label.setText(f"File: {filename} - Initializing parts...")
                return

            total_downloaded_overall = sum(cs.get('downloaded', 0) for cs in progress_info)
            # total_file_size_overall should ideally be from progress_data['total_file_size']
            # For now, we sum chunk totals. This assumes all chunks are for the same file.
            total_file_size_overall = sum(cs.get('total', 0) for cs in progress_info)
            
            active_chunks_count = 0
            combined_speed_bps = 0
            for cs in progress_info:
                if cs.get('active', False):
                    active_chunks_count += 1
                    combined_speed_bps += cs.get('speed_bps', 0)

            dl_mb = total_downloaded_overall / (1024 * 1024)
            total_mb = total_file_size_overall / (1024 * 1024)
            speed_MBps = (combined_speed_bps / 8) / (1024 * 1024)

            progress_text = f"DL '{filename[:20]}...': {dl_mb:.1f}/{total_mb:.1f} MB ({active_chunks_count} parts @ {speed_MBps:.2f} MB/s)"
            self.file_progress_label.setText(progress_text)

        elif isinstance(progress_info, tuple) and len(progress_info) == 2:  # Single stream (downloaded_bytes, total_bytes)
            downloaded_bytes, total_bytes = progress_info
            if not filename and total_bytes == 0 and downloaded_bytes == 0: # Clear if no info
                self.file_progress_label.setText("")
                return

            max_fn_len = 25
            disp_fn = filename if len(filename) <= max_fn_len else filename[:max_fn_len-3].strip()+"..."
            
            dl_mb = downloaded_bytes / (1024*1024)
            prog_text_base = f"Downloading '{disp_fn}' ({dl_mb:.1f}MB"
            if total_bytes > 0:
                tot_mb = total_bytes / (1024*1024)
                prog_text_base += f" / {tot_mb:.1f}MB)"
            else:
                prog_text_base += ")"
            
            self.file_progress_label.setText(prog_text_base)
        elif filename and progress_info is None: # Explicit request to clear for a specific file (e.g. download finished/failed)
            self.file_progress_label.setText("")
        elif not filename and not progress_info: # General clear
             self.file_progress_label.setText("")


    def update_external_links_setting(self, checked):
        is_only_links_mode = self.radio_only_links and self.radio_only_links.isChecked()
        is_only_archives_mode = self.radio_only_archives and self.radio_only_archives.isChecked()

        if is_only_links_mode or is_only_archives_mode:
             if self.external_log_output: self.external_log_output.hide()
             if self.log_splitter: self.log_splitter.setSizes([self.height(), 0])
             return

        self.show_external_links = checked
        if checked:
            if self.external_log_output: self.external_log_output.show()
            if self.log_splitter: self.log_splitter.setSizes([self.height() // 2, self.height() // 2])
            if self.main_log_output: self.main_log_output.setMinimumHeight(50)
            if self.external_log_output: self.external_log_output.setMinimumHeight(50)
            self.log_signal.emit("\n" + "="*40 + "\n🔗 External Links Log Enabled\n" + "="*40)
            if self.external_log_output:
                self.external_log_output.clear()
                self.external_log_output.append("🔗 External Links Found:")
            self._try_process_next_external_link()
        else:
            if self.external_log_output: self.external_log_output.hide()
            if self.log_splitter: self.log_splitter.setSizes([self.height(), 0])
            if self.main_log_output: self.main_log_output.setMinimumHeight(0)
            if self.external_log_output: self.external_log_output.setMinimumHeight(0)
            if self.external_log_output: self.external_log_output.clear()
            self.log_signal.emit("\n" + "="*40 + "\n🔗 External Links Log Disabled\n" + "="*40)


    def _handle_filter_mode_change(self, button, checked):
        if not button or not checked:
            return

        filter_mode_text = button.text()
        is_only_links = (filter_mode_text == "🔗 Only Links")
        is_only_archives = (filter_mode_text == "📦 Only Archives")

        # --- Visibility for log header buttons ---
        # Hide these buttons if in "Only Links" or "Only Archives" mode
        if self.skip_scope_toggle_button:
            self.skip_scope_toggle_button.setVisible(not (is_only_links or is_only_archives))
        if hasattr(self, 'multipart_toggle_button') and self.multipart_toggle_button:
            self.multipart_toggle_button.setVisible(not (is_only_links or is_only_archives))
        # Other log header buttons (manga, char filter scope) are handled by update_ui_for_manga_mode and update_ui_for_subfolders

        if self.link_search_input: self.link_search_input.setVisible(is_only_links)
        if self.link_search_button: self.link_search_button.setVisible(is_only_links)
        if self.export_links_button:
            self.export_links_button.setVisible(is_only_links)
            self.export_links_button.setEnabled(is_only_links and bool(self.extracted_links_cache))
        
        if self.download_btn: # Update download button text
            if is_only_links:
                self.download_btn.setText("🔗 Extract Links")
            else:
                self.download_btn.setText("⬇️ Start Download")
        if not is_only_links and self.link_search_input: self.link_search_input.clear()

        file_download_mode_active = not is_only_links

        if self.dir_input: self.dir_input.setEnabled(file_download_mode_active)
        if self.dir_button: self.dir_button.setEnabled(file_download_mode_active)
        if self.use_subfolders_checkbox: self.use_subfolders_checkbox.setEnabled(file_download_mode_active)
        if self.skip_words_input: self.skip_words_input.setEnabled(file_download_mode_active)
        if self.skip_scope_toggle_button: self.skip_scope_toggle_button.setEnabled(file_download_mode_active)
        if hasattr(self, 'remove_from_filename_input'): self.remove_from_filename_input.setEnabled(file_download_mode_active)
        
        if self.skip_zip_checkbox:
            can_skip_zip = not is_only_links and not is_only_archives
            self.skip_zip_checkbox.setEnabled(can_skip_zip)
            if is_only_archives:
                self.skip_zip_checkbox.setChecked(False)
        
        if self.skip_rar_checkbox:
            can_skip_rar = not is_only_links and not is_only_archives
            self.skip_rar_checkbox.setEnabled(can_skip_rar)
            if is_only_archives:
                self.skip_rar_checkbox.setChecked(False)

        other_file_proc_enabled = not is_only_links and not is_only_archives
        if self.download_thumbnails_checkbox: self.download_thumbnails_checkbox.setEnabled(other_file_proc_enabled)
        if self.compress_images_checkbox: self.compress_images_checkbox.setEnabled(other_file_proc_enabled)
        
        if self.external_links_checkbox: 
            can_show_external_log_option = not is_only_links and not is_only_archives
            self.external_links_checkbox.setEnabled(can_show_external_log_option)
            if not can_show_external_log_option:
                 self.external_links_checkbox.setChecked(False)


        if is_only_links:
            self.progress_log_label.setText("📜 Extracted Links Log:")
            if self.external_log_output: self.external_log_output.hide()
            if self.log_splitter: self.log_splitter.setSizes([self.height(), 0])
            if self.main_log_output: self.main_log_output.clear(); self.main_log_output.setMinimumHeight(0)
            if self.external_log_output: self.external_log_output.clear(); self.external_log_output.setMinimumHeight(0)
            self.log_signal.emit("="*20 + " Mode changed to: Only Links " + "="*20)
            self._filter_links_log()
            self._try_process_next_external_link()
        elif is_only_archives:
            self.progress_log_label.setText("📜 Progress Log (Archives Only):")
            if self.external_log_output: self.external_log_output.hide()
            if self.log_splitter: self.log_splitter.setSizes([self.height(), 0])
            if self.main_log_output: self.main_log_output.clear()
            self.log_signal.emit("="*20 + " Mode changed to: Only Archives " + "="*20)
        else:
            self.progress_log_label.setText("📜 Progress Log:")
            self.update_external_links_setting(self.external_links_checkbox.isChecked() if self.external_links_checkbox else False)
            self.log_signal.emit(f"="*20 + f" Mode changed to: {filter_mode_text} " + "="*20)

        subfolders_on = self.use_subfolders_checkbox.isChecked() if self.use_subfolders_checkbox else False
        
        manga_on = self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False
        
        enable_character_filter_related_widgets = file_download_mode_active and (subfolders_on or manga_on)

        if self.character_input:
            self.character_input.setEnabled(enable_character_filter_related_widgets)
            if not enable_character_filter_related_widgets:
                self.character_input.clear()
        
        if self.char_filter_scope_toggle_button:
            self.char_filter_scope_toggle_button.setEnabled(enable_character_filter_related_widgets)
        
        self.update_ui_for_subfolders(subfolders_on)
        self.update_custom_folder_visibility()
        # Ensure manga mode UI updates (which includes the visibility of manga_rename_toggle_button)
        self.update_ui_for_manga_mode(self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False)


    def _filter_links_log(self):
        if not (self.radio_only_links and self.radio_only_links.isChecked()): return

        search_term = self.link_search_input.text().lower().strip() if self.link_search_input else ""
        self.main_log_output.clear()
        current_title_for_display = None
        separator = "-" * 45

        for post_title, link_text, link_url, platform in self.extracted_links_cache:
            matches_search = (
                not search_term or
                search_term in link_text.lower() or
                search_term in link_url.lower() or
                search_term in platform.lower()
            )
            if matches_search:
                if post_title != current_title_for_display:
                    self.main_log_output.insertHtml("<br>" + separator + "<br>")
                    title_html = f'<b style="color: #87CEEB;">{post_title}</b><br>'
                    self.main_log_output.insertHtml(title_html)
                    current_title_for_display = post_title
                
                max_link_text_len = 35
                display_text = link_text[:max_link_text_len].strip() + "..." if len(link_text) > max_link_text_len else link_text
                formatted_link_info = f"{display_text} - {link_url} - {platform}"
                self.main_log_output.append(formatted_link_info)

        if self.main_log_output.toPlainText().strip():
            self.main_log_output.append("")
        self.main_log_output.verticalScrollBar().setValue(0)


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
                    separator = "-" * 60 + "\n"
                    for post_title, link_text, link_url, platform in self.extracted_links_cache:
                        if post_title != current_title_for_export:
                            if current_title_for_export is not None:
                                f.write("\n" + separator + "\n")
                            f.write(f"Post Title: {post_title}\n\n")
                            current_title_for_export = post_title
                        f.write(f"  {link_text} - {link_url} - {platform}\n")
                self.log_signal.emit(f"✅ Links successfully exported to: {filepath}")
                QMessageBox.information(self, "Export Successful", f"Links exported to:\n{filepath}")
            except Exception as e:
                self.log_signal.emit(f"❌ Error exporting links: {e}")
                QMessageBox.critical(self, "Export Error", f"Could not export links: {e}")


    def get_filter_mode(self):
        if self.radio_only_links and self.radio_only_links.isChecked():
            return 'all' 
        elif self.radio_images.isChecked():
            return 'image'
        elif self.radio_videos.isChecked():
            return 'video'
        elif self.radio_only_archives and self.radio_only_archives.isChecked():
            return 'archive'
        elif self.radio_all.isChecked():
            return 'all'
        return 'all'


    def get_skip_words_scope(self):
        return self.skip_words_scope


    def _update_skip_scope_button_text(self):
        if self.skip_scope_toggle_button:
            if self.skip_words_scope == SKIP_SCOPE_FILES:
                self.skip_scope_toggle_button.setText("Scope: Files")
                self.skip_scope_toggle_button.setToolTip(
                    "Current Skip Scope: Files\n\n"
                    "Skips individual files if their names contain any of the 'Skip with Words'.\n"
                    "Example: Skip words \"WIP, sketch\".\n"
                    "- File \"art_WIP.jpg\" -> SKIPPED.\n"
                    "- File \"final_art.png\" -> DOWNLOADED (if other conditions met).\n"
                    "Post is still processed for other non-skipped files.\n\n"
                    "Click to cycle to: Posts"
                )
            elif self.skip_words_scope == SKIP_SCOPE_POSTS:
                self.skip_scope_toggle_button.setText("Scope: Posts")
                self.skip_scope_toggle_button.setToolTip(
                    "Current Skip Scope: Posts\n\n"
                    "Skips entire posts if their titles contain any of the 'Skip with Words'.\n"
                    "All files from a skipped post are ignored.\n"
                    "Example: Skip words \"preview, announcement\".\n"
                    "- Post \"Exciting Announcement!\" -> SKIPPED.\n"
                    "- Post \"Finished Artwork\" -> PROCESSED (if other conditions met).\n\n"
                    "Click to cycle to: Both"
                )
            elif self.skip_words_scope == SKIP_SCOPE_BOTH:
                self.skip_scope_toggle_button.setText("Scope: Both")
                self.skip_scope_toggle_button.setToolTip(
                    "Current Skip Scope: Both (Posts then Files)\n\n"
                    "1. Checks post title: If title contains a skip word, the entire post is SKIPPED.\n"
                    "2. If post title is OK, then checks individual filenames: If a filename contains a skip word, only that file is SKIPPED.\n"
                    "Example: Skip words \"WIP, sketch\".\n"
                    "- Post \"Sketches and WIPs\" (title match) -> ENTIRE POST SKIPPED.\n"
                    "- Post \"Art Update\" (title OK) with files:\n"
                    "    - \"character_WIP.jpg\" (file match) -> SKIPPED.\n"
                    "    - \"final_scene.png\" (file OK) -> DOWNLOADED.\n\n"
                    "Click to cycle to: Files"
                )
            else:
                self.skip_scope_toggle_button.setText("Scope: Unknown")
                self.skip_scope_toggle_button.setToolTip(
                    "Current Skip Scope: Unknown\n\n"
                    "The skip words scope is in an unknown state. Please cycle or reset.\n\n"
                    "Click to cycle to: Files"
                )


    def _cycle_skip_scope(self):
        if self.skip_words_scope == SKIP_SCOPE_FILES:
            self.skip_words_scope = SKIP_SCOPE_POSTS
        elif self.skip_words_scope == SKIP_SCOPE_POSTS:
            self.skip_words_scope = SKIP_SCOPE_BOTH
        elif self.skip_words_scope == SKIP_SCOPE_BOTH:
            self.skip_words_scope = SKIP_SCOPE_FILES
        else:
            self.skip_words_scope = SKIP_SCOPE_FILES
        
        self._update_skip_scope_button_text()
        self.settings.setValue(SKIP_WORDS_SCOPE_KEY, self.skip_words_scope)
        self.log_signal.emit(f"ℹ️ Skip words scope changed to: '{self.skip_words_scope}'")

    def get_char_filter_scope(self):
        return self.char_filter_scope

    def _update_char_filter_scope_button_text(self):
        if self.char_filter_scope_toggle_button:
            if self.char_filter_scope == CHAR_SCOPE_FILES:
                self.char_filter_scope_toggle_button.setText("Filter: Files")
                self.char_filter_scope_toggle_button.setToolTip(
                    "Current Scope: Files\n\n"
                    "Filters individual files by name. A post is kept if any file matches.\n"
                    "Only matching files from that post are downloaded.\n"
                    "Example: Filter 'Tifa'. File 'Tifa_artwork.jpg' matches and is downloaded.\n"
                    "Folder Naming: Uses character from matching filename.\n\n"
                    "Click to cycle to: Title"
                )
            elif self.char_filter_scope == CHAR_SCOPE_TITLE:
                self.char_filter_scope_toggle_button.setText("Filter: Title")
                self.char_filter_scope_toggle_button.setToolTip(
                    "Current Scope: Title\n\n"
                    "Filters entire posts by their title. All files from a matching post are downloaded.\n"
                    "Example: Filter 'Aerith'. Post titled 'Aerith's Garden' matches; all its files are downloaded.\n"
                    "Folder Naming: Uses character from matching post title.\n\n"
                    "Click to cycle to: Both"
                )
            elif self.char_filter_scope == CHAR_SCOPE_BOTH:
                self.char_filter_scope_toggle_button.setText("Filter: Both")
                self.char_filter_scope_toggle_button.setToolTip(
                    "Current Scope: Both (Title then Files)\n\n"
                    "1. Checks post title: If matches, all files from post are downloaded.\n"
                    "2. If title doesn't match, checks filenames: If any file matches, only that file is downloaded.\n"
                    "Example: Filter 'Cloud'.\n"
                    " - Post 'Cloud Strife' (title match) -> all files downloaded.\n"
                    " - Post 'Bike Chase' with 'Cloud_fenrir.jpg' (file match) -> only 'Cloud_fenrir.jpg' downloaded.\n"
                    "Folder Naming: Prioritizes title match, then file match.\n\n"
                    "Click to cycle to: Comments"
                )
            elif self.char_filter_scope == CHAR_SCOPE_COMMENTS:
                self.char_filter_scope_toggle_button.setText("Filter: Comments (Beta)")
                self.char_filter_scope_toggle_button.setToolTip(
                    "Current Scope: Comments (Beta - Files first, then Comments as fallback)\n\n"
                    "1. Checks filenames: If any file in the post matches the filter, the entire post is downloaded. Comments are NOT checked for this filter term.\n"
                    "2. If no file matches, THEN checks post comments: If a comment matches, the entire post is downloaded.\n"
                    "Example: Filter 'Barret'.\n"
                    " - Post A: Files 'Barret_gunarm.jpg', 'other.png'. File 'Barret_gunarm.jpg' matches. All files from Post A downloaded. Comments not checked for 'Barret'.\n"
                    " - Post B: Files 'dyne.jpg', 'weapon.gif'. Comments: '...a drawing of Barret Wallace...'. No file match for 'Barret'. Comment matches. All files from Post B downloaded.\n"
                    "Folder Naming: Prioritizes character from file match, then from comment match.\n\n"
                    "Click to cycle to: Files"
                )
            else:
                self.char_filter_scope_toggle_button.setText("Filter: Unknown")
                self.char_filter_scope_toggle_button.setToolTip(
                    "Current Scope: Unknown\n\n"
                    "The character filter scope is in an unknown state. Please cycle or reset.\n\n"
                    "Click to cycle to: Files"
                )

    def _cycle_char_filter_scope(self):
        # Cycle: Files -> Title -> Both -> Comments -> Files
        if self.char_filter_scope == CHAR_SCOPE_FILES:
            self.char_filter_scope = CHAR_SCOPE_TITLE
        elif self.char_filter_scope == CHAR_SCOPE_TITLE:
            self.char_filter_scope = CHAR_SCOPE_BOTH
        elif self.char_filter_scope == CHAR_SCOPE_BOTH:
             self.char_filter_scope = CHAR_SCOPE_COMMENTS
        elif self.char_filter_scope == CHAR_SCOPE_COMMENTS:
            self.char_filter_scope = CHAR_SCOPE_FILES
        else:
            self.char_filter_scope = CHAR_SCOPE_FILES # Default fallback
        
        self._update_char_filter_scope_button_text()
        self.settings.setValue(CHAR_FILTER_SCOPE_KEY, self.char_filter_scope)
        self.log_signal.emit(f"ℹ️ Character filter scope changed to: '{self.char_filter_scope}'")



    def add_new_character(self):
        global KNOWN_NAMES, clean_folder_name
        name_to_add = self.new_char_input.text().strip()
        if not name_to_add:
             QMessageBox.warning(self, "Input Error", "Name cannot be empty."); return False

        name_to_add_lower = name_to_add.lower()

        # Check for duplicates (primary name or any alias)
        for kn_entry in KNOWN_NAMES:
            if kn_entry["name"].lower() == name_to_add_lower:
                 QMessageBox.warning(self, "Duplicate Name", f"The name '{name_to_add}' already exists as a primary folder name."); return False
            for alias in kn_entry["aliases"]:
                if alias.lower() == name_to_add_lower:
                    QMessageBox.warning(self, "Duplicate Alias", f"The name '{name_to_add}' already exists as an alias for '{kn_entry['name']}'."); return False

        similar_names_details = []
        # Check for similarity with existing primary names or aliases
        for kn_entry in KNOWN_NAMES:
            for term_to_check_similarity_against in kn_entry["aliases"]: # Check against all aliases
                term_lower = term_to_check_similarity_against.lower()
                if name_to_add_lower != term_lower and \
                   (name_to_add_lower in term_lower or term_lower in name_to_add_lower):
                    # Warn about similarity with the primary name of the group
                    similar_names_details.append((name_to_add, kn_entry["name"])) 
                    break # Found a similarity for this entry, no need to check its other aliases
        
        if similar_names_details:
            first_similar_new, first_similar_existing = similar_names_details[0]
            shorter, longer = sorted([first_similar_new, first_similar_existing], key=len)

            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Potential Name Conflict")
            msg_box.setText(
                f"The name '{first_similar_new}' is very similar to an existing name: '{first_similar_existing}'.\n\n"
                f"This could lead to unexpected folder grouping (e.g., under '{clean_folder_name(shorter)}' instead of a more specific '{clean_folder_name(longer)}' or vice-versa).\n\n"
                "Do you want to change the name you are adding, or proceed anyway?"
            )
            change_button = msg_box.addButton("Change Name", QMessageBox.RejectRole)
            proceed_button = msg_box.addButton("Proceed Anyway", QMessageBox.AcceptRole)
            msg_box.setDefaultButton(proceed_button)
            msg_box.setEscapeButton(change_button)
            msg_box.exec_()

            if msg_box.clickedButton() == change_button:
                self.log_signal.emit(f"ℹ️ User chose to change '{first_similar_new}' due to similarity with an alias of '{first_similar_existing_primary}'.")
                return False

            self.log_signal.emit(f"⚠️ User proceeded with adding '{first_similar_new}' despite similarity with an alias of '{first_similar_existing_primary}'.")

        # Add as a simple (non-group) entry
        new_entry = {
            "name": name_to_add,
            "is_group": False,
            "aliases": [name_to_add]
        }
        KNOWN_NAMES.append(new_entry)
        KNOWN_NAMES.sort(key=lambda x: x["name"].lower()) # Sort by primary name

        self.character_list.clear()
        self.character_list.addItems([entry["name"] for entry in KNOWN_NAMES])
        self.filter_character_list(self.character_search_input.text())

        self.log_signal.emit(f"✅ Added '{name_to_add}' to known names list.")
        self.new_char_input.clear()
        self.save_known_names()
        return True


    def delete_selected_character(self):
        global KNOWN_NAMES
        selected_items = self.character_list.selectedItems()
        if not selected_items:
             QMessageBox.warning(self, "Selection Error", "Please select one or more names to delete."); return

        primary_names_to_remove = {item.text() for item in selected_items}
        confirm = QMessageBox.question(self, "Confirm Deletion",
                                       f"Are you sure you want to delete {len(primary_names_to_remove)} selected entry/entries (and their aliases)?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            original_count = len(KNOWN_NAMES)
            KNOWN_NAMES[:] = [entry for entry in KNOWN_NAMES if entry["name"] not in primary_names_to_remove]
            removed_count = original_count - len(KNOWN_NAMES)

            if removed_count > 0:
                 self.log_signal.emit(f"🗑️ Removed {removed_count} name(s).")
                 self.character_list.clear()
                 self.character_list.addItems([entry["name"] for entry in KNOWN_NAMES])
                 self.filter_character_list(self.character_search_input.text())
                 self.save_known_names()
            else:
                 self.log_signal.emit("ℹ️ No names were removed (they might not have been in the list).")


    def update_custom_folder_visibility(self, url_text=None):
        if url_text is None:
            url_text = self.link_input.text()

        _, _, post_id = extract_post_info(url_text.strip())
        
        is_single_post_url = bool(post_id)
        subfolders_enabled = self.use_subfolders_checkbox.isChecked() if self.use_subfolders_checkbox else False
        
        not_only_links_or_archives_mode = not (
            (self.radio_only_links and self.radio_only_links.isChecked()) or
            (self.radio_only_archives and self.radio_only_archives.isChecked())
        )

        should_show_custom_folder = is_single_post_url and subfolders_enabled and not_only_links_or_archives_mode
        
        if self.custom_folder_widget:
            self.custom_folder_widget.setVisible(should_show_custom_folder)

        if not (self.custom_folder_widget and self.custom_folder_widget.isVisible()):
            if self.custom_folder_input: self.custom_folder_input.clear()


    def update_ui_for_subfolders(self, checked): 
        is_only_links = self.radio_only_links and self.radio_only_links.isChecked()
        is_only_archives = self.radio_only_archives and self.radio_only_archives.isChecked()

        if self.use_subfolder_per_post_checkbox:
            self.use_subfolder_per_post_checkbox.setEnabled(not is_only_links and not is_only_archives)

        if hasattr(self, 'use_cookie_checkbox'):
            self.use_cookie_checkbox.setEnabled(not is_only_links) # Cookies might be relevant for archives


        enable_character_filter_related_widgets = checked and not is_only_links and not is_only_archives
 

        if self.character_filter_widget:
            self.character_filter_widget.setVisible(enable_character_filter_related_widgets)
            if not self.character_filter_widget.isVisible():
                if self.character_input: self.character_input.clear()
                if self.char_filter_scope_toggle_button: self.char_filter_scope_toggle_button.setEnabled(False)
            else:
                if self.char_filter_scope_toggle_button: self.char_filter_scope_toggle_button.setEnabled(True)
        
        self.update_custom_folder_visibility()


    def _update_cookie_input_visibility(self, checked):
        cookie_text_input_exists = hasattr(self, 'cookie_text_input')
        cookie_browse_button_exists = hasattr(self, 'cookie_browse_button')

        if cookie_text_input_exists or cookie_browse_button_exists:
            is_only_links = self.radio_only_links and self.radio_only_links.isChecked()
            
            # Cookie text input and browse button are visible if "Use Cookie" is checked
            if cookie_text_input_exists: self.cookie_text_input.setVisible(checked)
            if cookie_browse_button_exists: self.cookie_browse_button.setVisible(checked)
            
            can_enable_cookie_text = checked and not is_only_links
            enable_state_for_fields = can_enable_cookie_text and (self.download_btn.isEnabled() or self.is_paused)

            if cookie_text_input_exists:
                # Text input is always enabled if its parent "Use Cookie" is checked and conditions met,
                # unless a file path is displayed (then it's read-only).
                self.cookie_text_input.setEnabled(enable_state_for_fields)
                if self.selected_cookie_filepath and checked: # If a file is selected and "Use Cookie" is on
                    self.cookie_text_input.setText(self.selected_cookie_filepath)
                    self.cookie_text_input.setReadOnly(True)
                    self.cookie_text_input.setPlaceholderText("")
                elif checked: # "Use Cookie" is on, but no file selected
                    self.cookie_text_input.setReadOnly(False)
                    self.cookie_text_input.setPlaceholderText("Cookie string (if no cookies.txt)")

            if cookie_browse_button_exists: self.cookie_browse_button.setEnabled(enable_state_for_fields)

            if not checked: # If "Use Cookie" is unchecked, clear the selected file path
                self.selected_cookie_filepath = None


    def update_page_range_enabled_state(self):
        url_text = self.link_input.text().strip() if self.link_input else ""
        _, _, post_id = extract_post_info(url_text)

        is_creator_feed = not post_id if url_text else False
        manga_mode_active = self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False

        enable_page_range = is_creator_feed and not manga_mode_active

        for widget in [self.page_range_label, self.start_page_input, self.to_label, self.end_page_input]:
            if widget: widget.setEnabled(enable_page_range)

        if not enable_page_range:
            if self.start_page_input: self.start_page_input.clear()
            if self.end_page_input: self.end_page_input.clear()


    def _update_manga_filename_style_button_text(self):
        if self.manga_rename_toggle_button:
            if self.manga_filename_style == STYLE_POST_TITLE:
                self.manga_rename_toggle_button.setText("Name: Post Title")
                self.manga_rename_toggle_button.setToolTip(
                    "Manga Filename Style: Post Title\n\n"
                    "When Manga/Comic Mode is active for a creator feed:\n"
                    "- The *first* file in a post is named after the post's title (e.g., \"MyMangaChapter1.jpg\").\n"
                    "- Any *subsequent* files within the *same post* will retain their original filenames (e.g., \"page_02.png\", \"bonus_art.jpg\").\n"
                    "- This is generally recommended for better organization of sequential content.\n"
                    "- Example: Post \"Chapter 1: The Beginning\" with files \"001.jpg\", \"002.jpg\".\n"
                    "  Downloads as: \"Chapter 1 The Beginning.jpg\", \"002.jpg\".\n\n"
                    "Click to change to: Original File Name"
                )
            elif self.manga_filename_style == STYLE_ORIGINAL_NAME:
                self.manga_rename_toggle_button.setText("Name: Original File")
                self.manga_rename_toggle_button.setToolTip(
                    "Manga Filename Style: Original File Name\n\n"
                    "When Manga/Comic Mode is active for a creator feed:\n"
                    "- *All* files in a post will attempt to keep their original filenames as provided by the site (e.g., \"001.jpg\", \"page_02.png\").\n"
                    "- This can be useful if original names are already well-structured and sequential.\n"
                    "- If original names are inconsistent, using \"Post Title\" style is often better.\n"
                    "- Example: Post \"Chapter 1: The Beginning\" with files \"001.jpg\", \"002.jpg\".\n"
                    "  Downloads as: \"001.jpg\", \"002.jpg\".\n\n"
                    "Click to change to: Post Title"
                )
            elif self.manga_filename_style == STYLE_DATE_BASED:
                self.manga_rename_toggle_button.setText("Name: Date Based")
                self.manga_rename_toggle_button.setToolTip(
                    "Manga Filename Style: Date Based\n\n"
                    "When Manga/Comic Mode is active for a creator feed:\n"
                    "- Files will be named sequentially (001.ext, 002.ext, ...) based on post publication order (oldest to newest).\n"
                    "- To ensure correct numbering, multithreading for post processing is automatically disabled when this style is active.\n\n"
                    "Click to change to: Post Title"
                )

            else:
                self.manga_rename_toggle_button.setText("Name: Unknown Style")
                self.manga_rename_toggle_button.setToolTip(
                    "Manga Filename Style: Unknown\n\n"
                    "The manga filename style is in an unknown state. Please cycle or reset.\n\n"
                    "Click to change to: Post Title"
                )


    def _toggle_manga_filename_style(self):
        current_style = self.manga_filename_style
        new_style = ""

        if current_style == STYLE_POST_TITLE: # Title -> Original
            new_style = STYLE_ORIGINAL_NAME
            # The warning for original name style
            # reply = QMessageBox.information(self, "Manga Filename Preference",
            #                                "Using 'Name: Post Title' (first file by title, others original) is recommended for Manga Mode.\n\n"
            #                                "Using 'Name: Original File' for all files might lead to less organized downloads if original names are inconsistent or non-sequential.\n\n"
            #                                "Proceed with using 'Name: Original File' for all files?",
            #                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            # if reply == QMessageBox.No:
            #     self.log_signal.emit("ℹ️ Manga filename style change to 'Original File' cancelled by user.")
            #     return
        elif current_style == STYLE_ORIGINAL_NAME: # Original -> Date
            new_style = STYLE_DATE_BASED
        elif current_style == STYLE_DATE_BASED: # Date -> Title
            new_style = STYLE_POST_TITLE
        else:
            self.log_signal.emit(f"⚠️ Unknown current manga filename style: {current_style}. Resetting to default ('{STYLE_POST_TITLE}').")
            new_style = STYLE_POST_TITLE

        self.manga_filename_style = new_style
        self.settings.setValue(MANGA_FILENAME_STYLE_KEY, self.manga_filename_style)
        self.settings.sync()
        self._update_manga_filename_style_button_text()
        self._update_multithreading_for_date_mode() # Update multithreading state based on new style
        self.log_signal.emit(f"ℹ️ Manga filename style changed to: '{self.manga_filename_style}'")


    def update_ui_for_manga_mode(self, checked):
        # Get current filter mode status
        is_only_links_mode = self.radio_only_links and self.radio_only_links.isChecked()
        is_only_archives_mode = self.radio_only_archives and self.radio_only_archives.isChecked()

        url_text = self.link_input.text().strip() if self.link_input else ""
        _, _, post_id = extract_post_info(url_text)

        is_creator_feed = not post_id if url_text else False

        # Manga mode checkbox itself is only enabled for creator feeds
        if self.manga_mode_checkbox:
            self.manga_mode_checkbox.setEnabled(is_creator_feed)
            if not is_creator_feed and self.manga_mode_checkbox.isChecked():
                # If URL changes to non-creator feed, uncheck manga mode
                self.manga_mode_checkbox.setChecked(False)
                checked = self.manga_mode_checkbox.isChecked() 

        manga_mode_effectively_on = is_creator_feed and checked

        if self.manga_rename_toggle_button:
            # Visible if manga mode is on AND not in "Only Links" or "Only Archives" mode
            self.manga_rename_toggle_button.setVisible(manga_mode_effectively_on and not (is_only_links_mode or is_only_archives_mode))


        if manga_mode_effectively_on:
            if self.page_range_label: self.page_range_label.setEnabled(False)
            if self.start_page_input: self.start_page_input.setEnabled(False); self.start_page_input.clear()
            if self.to_label: self.to_label.setEnabled(False)
            if self.end_page_input: self.end_page_input.setEnabled(False); self.end_page_input.clear()
        else:
            self.update_page_range_enabled_state()
        
        file_download_mode_active = not (self.radio_only_links and self.radio_only_links.isChecked())
        subfolders_on = self.use_subfolders_checkbox.isChecked() if self.use_subfolders_checkbox else False
        enable_char_filter_widgets = file_download_mode_active and (subfolders_on or manga_mode_effectively_on)

        if self.character_input:
            self.character_input.setEnabled(enable_char_filter_widgets)
            if not enable_char_filter_widgets: self.character_input.clear()
        if self.char_filter_scope_toggle_button:
            self.char_filter_scope_toggle_button.setEnabled(enable_char_filter_widgets)
        self._update_multithreading_for_date_mode() # Update multithreading state based on manga mode


    def filter_character_list(self, search_text):
        search_text_lower = search_text.lower()
        for i in range(self.character_list.count()):
            item = self.character_list.item(i)
            item.setHidden(search_text_lower not in item.text().lower())


    def update_multithreading_label(self, text):
        if self.use_multithreading_checkbox.isChecked():
            try:
                num_threads_val = int(text)
                if num_threads_val > 0 : self.use_multithreading_checkbox.setText(f"Use Multithreading ({num_threads_val} Threads)")
                else: self.use_multithreading_checkbox.setText("Use Multithreading (Invalid: >0)")
            except ValueError:
                self.use_multithreading_checkbox.setText("Use Multithreading (Invalid Input)")
        else:
            self.use_multithreading_checkbox.setText("Use Multithreading (1 Thread)")


    def _handle_multithreading_toggle(self, checked):
        if not checked:
            self.thread_count_input.setEnabled(False)
            self.thread_count_label.setEnabled(False)
            self.use_multithreading_checkbox.setText("Use Multithreading (1 Thread)")
        else:
            self.thread_count_input.setEnabled(True)
            self.thread_count_label.setEnabled(True)
            self.update_multithreading_label(self.thread_count_input.text())

    def _update_multithreading_for_date_mode(self):
        """
        Checks if Manga Mode is ON and 'Date Based' style is selected.
        If so, disables multithreading. Otherwise, enables it.
        """
        if not hasattr(self, 'manga_mode_checkbox') or not hasattr(self, 'use_multithreading_checkbox'):
            return # UI elements not ready

        manga_on = self.manga_mode_checkbox.isChecked()
        is_date_style = (self.manga_filename_style == STYLE_DATE_BASED)

        if manga_on and is_date_style:
            if self.use_multithreading_checkbox.isChecked() or self.use_multithreading_checkbox.isEnabled():
                # Only log if a change is made or it was previously enabled
                if self.use_multithreading_checkbox.isChecked():
                    self.log_signal.emit("ℹ️ Manga Date Mode: Multithreading for post processing has been disabled to ensure correct sequential file numbering.")
                self.use_multithreading_checkbox.setChecked(False)
            self.use_multithreading_checkbox.setEnabled(False)
            self._handle_multithreading_toggle(False) # Update label to show "1 Thread"
        else:
            if not self.use_multithreading_checkbox.isEnabled(): # Only re-enable if it was disabled by this logic
                self.use_multithreading_checkbox.setEnabled(True)
            self._handle_multithreading_toggle(self.use_multithreading_checkbox.isChecked()) # Update label based on current state

    def update_progress_display(self, total_posts, processed_posts):
        if total_posts > 0:
            progress_percent = (processed_posts / total_posts) * 100
            self.progress_label.setText(f"Progress: {processed_posts} / {total_posts} posts ({progress_percent:.1f}%)")
        elif processed_posts > 0 :
             self.progress_label.setText(f"Progress: Processing post {processed_posts}...")
        else:
            self.progress_label.setText("Progress: Starting...")
        
        if total_posts > 0 or processed_posts > 0 :
            self.file_progress_label.setText("")


    def start_download(self):
        global KNOWN_NAMES, BackendDownloadThread, PostProcessorWorker, extract_post_info, clean_folder_name, MAX_FILE_THREADS_PER_POST_OR_WORKER
        
        if self._is_download_active():
            QMessageBox.warning(self, "Busy", "A download is already running."); return

        api_url = self.link_input.text().strip()
        output_dir = self.dir_input.text().strip()
        
        use_subfolders = self.use_subfolders_checkbox.isChecked()
        use_post_subfolders = self.use_subfolder_per_post_checkbox.isChecked()
        compress_images = self.compress_images_checkbox.isChecked()
        download_thumbnails = self.download_thumbnails_checkbox.isChecked()
        
        use_multithreading_enabled_by_checkbox = self.use_multithreading_checkbox.isChecked()
        try:
            # num_threads_from_gui is used for post workers or file workers depending on context
            num_threads_from_gui = int(self.thread_count_input.text().strip())
            if num_threads_from_gui < 1: num_threads_from_gui = 1
        except ValueError:
            QMessageBox.critical(self, "Thread Count Error", "Invalid number of threads. Please enter a positive number.")
            self.set_ui_enabled(True)
            return

        if use_multithreading_enabled_by_checkbox:
            # Hard Warning: Threads > MAX_THREADS (200)
            if num_threads_from_gui > MAX_THREADS:
                hard_warning_msg = (
                    f"You've entered a thread count ({num_threads_from_gui}) exceeding the maximum of {MAX_THREADS}.\n\n"
                    "Using an extremely high number of threads can lead to:\n"
                    "  - Diminishing returns (no significant speed increase).\n"
                    "  - Increased system instability or application crashes.\n"
                    "  - Higher chance of being rate-limited or temporarily IP-banned by the server.\n\n"
                    f"The thread count has been automatically capped to {MAX_THREADS} for stability."
                )
                QMessageBox.warning(self, "High Thread Count Warning", hard_warning_msg)
                num_threads_from_gui = MAX_THREADS
                self.thread_count_input.setText(str(MAX_THREADS)) # Update the input field
                self.log_signal.emit(f"⚠️ User attempted {num_threads_from_gui} threads, capped to {MAX_THREADS}.")

            # Soft Warning: SOFT_WARNING_THREAD_THRESHOLD < Threads <= MAX_THREADS
            # This uses the potentially capped num_threads_from_gui from the hard warning
            if SOFT_WARNING_THREAD_THRESHOLD < num_threads_from_gui <= MAX_THREADS:
                soft_warning_msg_box = QMessageBox(self)
                soft_warning_msg_box.setIcon(QMessageBox.Question)
                soft_warning_msg_box.setWindowTitle("Thread Count Advisory")
                soft_warning_msg_box.setText(
                    f"You've set the thread count to {num_threads_from_gui}.\n\n"
                    "While this is within the allowed limit, using a high number of threads (typically above 40-50) can sometimes lead to:\n"
                    "  - Increased errors or failed file downloads.\n"
                    "  - Connection issues with the server.\n"
                    "  - Higher system resource usage.\n\n"
                    "For most users and connections, 10-30 threads provide a good balance.\n\n"
                    f"Do you want to proceed with {num_threads_from_gui} threads, or would you like to change the value?"
                )
                proceed_button = soft_warning_msg_box.addButton("Proceed Anyway", QMessageBox.AcceptRole)
                change_button = soft_warning_msg_box.addButton("Change Thread Value", QMessageBox.RejectRole)
                soft_warning_msg_box.setDefaultButton(proceed_button)
                soft_warning_msg_box.setEscapeButton(change_button)
                soft_warning_msg_box.exec_()

                if soft_warning_msg_box.clickedButton() == change_button:
                    self.log_signal.emit(f"ℹ️ User opted to change thread count from {num_threads_from_gui} after advisory.")
                    self.thread_count_input.setFocus()
                    self.thread_count_input.selectAll()
                    return # Exit start_download to allow user to change value

        raw_skip_words = self.skip_words_input.text().strip()
        skip_words_list = [word.strip().lower() for word in raw_skip_words.split(',') if word.strip()]

        raw_remove_filename_words = self.remove_from_filename_input.text().strip() if hasattr(self, 'remove_from_filename_input') else ""
        allow_multipart = self.allow_multipart_download_setting # Use the internal setting
        remove_from_filename_words_list = [word.strip() for word in raw_remove_filename_words.split(',') if word.strip()]
        use_cookie_from_checkbox = self.use_cookie_checkbox.isChecked() if hasattr(self, 'use_cookie_checkbox') else False
        app_base_dir_for_cookies = os.path.dirname(self.config_file) # Directory of Known.txt
        cookie_text_from_input = self.cookie_text_input.text().strip() if hasattr(self, 'cookie_text_input') and use_cookie_from_checkbox else ""
        selected_cookie_file_path_for_backend = self.selected_cookie_filepath if use_cookie_from_checkbox and self.selected_cookie_filepath else None
        current_skip_words_scope = self.get_skip_words_scope()
        current_char_filter_scope = self.get_char_filter_scope()
        manga_mode_is_checked = self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False
        
        extract_links_only = (self.radio_only_links and self.radio_only_links.isChecked())
        backend_filter_mode = self.get_filter_mode()
        user_selected_filter_text = self.radio_group.checkedButton().text() if self.radio_group.checkedButton() else "All"

        # If a file path is selected, cookie_text_from_input should be considered empty for backend logic
        if selected_cookie_file_path_for_backend:
            cookie_text_from_input = ""

        if backend_filter_mode == 'archive':
            effective_skip_zip = False
            effective_skip_rar = False
        else:
            effective_skip_zip = self.skip_zip_checkbox.isChecked()
            effective_skip_rar = self.skip_rar_checkbox.isChecked()

        if not api_url: QMessageBox.critical(self, "Input Error", "URL is required."); return
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
                try: os.makedirs(output_dir, exist_ok=True); self.log_signal.emit(f"ℹ️ Created directory: {output_dir}")
                except Exception as e: QMessageBox.critical(self, "Directory Error", f"Could not create directory: {e}"); return
            else: self.log_signal.emit("❌ Download cancelled: Output directory does not exist and was not created."); return

        if compress_images and Image is None:
            QMessageBox.warning(self, "Missing Dependency", "Pillow library (for image compression) not found. Compression will be disabled.")
            compress_images = False; self.compress_images_checkbox.setChecked(False)

        manga_mode = manga_mode_is_checked and not post_id_from_url


        start_page_str, end_page_str = self.start_page_input.text().strip(), self.end_page_input.text().strip()
        start_page, end_page = None, None
        is_creator_feed = bool(not post_id_from_url)
        if is_creator_feed and not manga_mode:
            try:
                if start_page_str: start_page = int(start_page_str)
                if end_page_str: end_page = int(end_page_str)
                if start_page is not None and start_page <= 0: raise ValueError("Start page must be positive.")
                if end_page is not None and end_page <= 0: raise ValueError("End page must be positive.")
                if start_page and end_page and start_page > end_page: raise ValueError("Start page cannot be greater than end page.")
            except ValueError as e: QMessageBox.critical(self, "Page Range Error", f"Invalid page range: {e}"); return
        elif manga_mode:
            start_page, end_page = None, None 
        
        # Manga Mode specific duplicate handling is now managed entirely within downloader_utils.py
        self.external_link_queue.clear(); self.extracted_links_cache = []; self._is_processing_external_link_queue = False; self._current_link_post_title = None

        raw_character_filters_text = self.character_input.text().strip() # Get current text
        parsed_character_filter_objects = self._parse_character_filters(raw_character_filters_text) # Parse it

        filter_character_list_to_pass = None
        needs_folder_naming_validation = (use_subfolders or manga_mode) and not extract_links_only

        if parsed_character_filter_objects and not extract_links_only :
            self.log_signal.emit(f"ℹ️ Validating character filters: {', '.join(item['name'] + (' (Group: ' + '/'.join(item['aliases']) + ')' if item['is_group'] else '') for item in parsed_character_filter_objects)}")
            valid_filters_for_backend = []
            user_cancelled_validation = False

            for filter_item_obj in parsed_character_filter_objects:
                item_primary_name = filter_item_obj["name"]
                cleaned_name_test = clean_folder_name(item_primary_name)


                if needs_folder_naming_validation and not cleaned_name_test:
                    QMessageBox.warning(self, "Invalid Filter Name for Folder", f"Filter name '{item_primary_name}' is invalid for a folder and will be skipped for folder naming.")
                    self.log_signal.emit(f"⚠️ Skipping invalid filter for folder naming: '{item_primary_name}'")
                    continue

                # --- New: Check if any alias of a group is already known ---
                an_alias_is_already_known = False
                if filter_item_obj["is_group"] and needs_folder_naming_validation:
                    for alias in filter_item_obj["aliases"]:
                        if any(existing_known.lower() == alias.lower() for existing_known in KNOWN_NAMES):
                            an_alias_is_already_known = True
                            self.log_signal.emit(f"ℹ️ Alias '{alias}' (from group '{item_primary_name}') is already in Known Names. Group name '{item_primary_name}' will not be added to Known.txt.")
                            break
                # --- End new check ---

                if an_alias_is_already_known:
                    valid_filters_for_backend.append(filter_item_obj)
                    continue

                # Determine if we should prompt to add the name to the Known.txt list.
                # Prompt if:
                #   - Folder naming validation is relevant (subfolders or manga mode, and not just extracting links)
                #   - AND Manga Mode is OFF (this is the key change for your request)
                #   - AND the primary name of the filter isn't already in Known.txt
                should_prompt_to_add_to_known_list = (
                    needs_folder_naming_validation and
                    not manga_mode and  # Do NOT prompt if Manga Mode is ON
                    item_primary_name.lower() not in {kn_entry["name"].lower() for kn_entry in KNOWN_NAMES}
                )

                if should_prompt_to_add_to_known_list:
                    reply = QMessageBox.question(self, "Add to Known List?",
                                               f"Filter name '{item_primary_name}' (used for folder/manga naming) is not in known names list.\nAdd it now?",
                                               QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
                    if reply == QMessageBox.Yes:
                        self.new_char_input.setText(item_primary_name) # Use the primary name for adding
                        if self.add_new_character():
                            valid_filters_for_backend.append(filter_item_obj)
                    elif reply == QMessageBox.Cancel:
                        user_cancelled_validation = True; break
                    # If 'No', the filter is not used and not added to Known.txt for this session.
                else:
                    # Add to filters to be used for this session if:
                    # - Prompting is not needed (e.g., name already known, or not manga_mode but name is known)
                    # - OR Manga Mode is ON (filter is used without adding to Known.txt)
                    # - OR extract_links_only is true (folder naming validation is false)
                    valid_filters_for_backend.append(filter_item_obj)
                    if manga_mode and needs_folder_naming_validation and item_primary_name.lower() not in {kn_entry["name"].lower() for kn_entry in KNOWN_NAMES}:
                        self.log_signal.emit(f"ℹ️ Manga Mode: Using filter '{item_primary_name}' for this session without adding to Known Names.")

            if user_cancelled_validation: return

            if valid_filters_for_backend:
                filter_character_list_to_pass = valid_filters_for_backend
                self.log_signal.emit(f"   Using validated character filters: {', '.join(item['name'] for item in filter_character_list_to_pass)}")
            else:
                self.log_signal.emit("⚠️ No valid character filters to use for this session.")
        elif parsed_character_filter_objects : # If not extract_links_only is false, but filters exist
            filter_character_list_to_pass = parsed_character_filter_objects
            self.log_signal.emit(f"ℹ️ Character filters provided (folder naming validation may not apply): {', '.join(item['name'] for item in filter_character_list_to_pass)}")


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
            if msg_box.clickedButton() == cancel_button:
                self.log_signal.emit("❌ Download cancelled due to Manga Mode filter warning."); return
            else:
                self.log_signal.emit("⚠️ Proceeding with Manga Mode without a specific title filter.")

        # Set the dynamic filter holder with the filters determined for this run
        # This ensures workers get the correct initial set if they start before any live changes.
        self.dynamic_character_filter_holder.set_filters(filter_character_list_to_pass if filter_character_list_to_pass else [])

        custom_folder_name_cleaned = None
        if use_subfolders and post_id_from_url and self.custom_folder_widget and self.custom_folder_widget.isVisible() and not extract_links_only: 
            raw_custom_name = self.custom_folder_input.text().strip()
            if raw_custom_name:
                 cleaned_custom = clean_folder_name(raw_custom_name)
                 if cleaned_custom: custom_folder_name_cleaned = cleaned_custom
                 else: self.log_signal.emit(f"⚠️ Invalid custom folder name ignored: '{raw_custom_name}' (resulted in empty string after cleaning).")


        self.main_log_output.clear()
        if extract_links_only: self.main_log_output.append("🔗 Extracting Links...");
        elif backend_filter_mode == 'archive': self.main_log_output.append("📦 Downloading Archives Only...")
        
        if self.external_log_output: self.external_log_output.clear()
        if self.show_external_links and not extract_links_only and backend_filter_mode != 'archive': 
            self.external_log_output.append("🔗 External Links Found:")
        
        self.file_progress_label.setText(""); self.cancellation_event.clear(); self.active_futures = []
        self.total_posts_to_process = 0; self.processed_posts_count = 0; self.download_counter = 0; self.skip_counter = 0
        self.progress_label.setText("Progress: Initializing...")

        self.retryable_failed_files_info.clear() # Clear previous retryable failures before new session
        # Manga date file counter initialization is now moved into DownloadThread.run()
        # We will pass None or a placeholder if needed, and DownloadThread will calculate it.
        manga_date_file_counter_ref_for_thread = None
        if manga_mode and self.manga_filename_style == STYLE_DATE_BASED and not extract_links_only:
            # Pass None; DownloadThread will calculate if it's a single-threaded download.
            # For multi-threaded, this ref needs to be created here and shared.
            # However, with date_based manga mode forcing single post worker, this specific ref might only be used by that one worker.
            # Let's keep it as None for now, assuming DownloadThread handles its init if it's the one doing sequential processing.
            # If multi-threaded post processing were allowed with date-based, this would need careful shared state.
            manga_date_file_counter_ref_for_thread = None
            self.log_signal.emit(f"ℹ️ Manga Date Mode: File counter will be initialized by the download thread.")
        effective_num_post_workers = 1
        effective_num_file_threads_per_worker = 1 # Default to 1 for all cases initially

        if post_id_from_url:
            # Single post URL: UI threads control concurrent file downloads for that post
            if use_multithreading_enabled_by_checkbox:
                effective_num_file_threads_per_worker = max(1, min(num_threads_from_gui, MAX_FILE_THREADS_PER_POST_OR_WORKER))
            # else: effective_num_file_threads_per_worker remains 1
            # effective_num_post_workers remains 1 (not used for post thread pool)        
        else:
            # Creator feed URL
            if manga_mode and self.manga_filename_style == STYLE_DATE_BASED:
                # Force single post worker for date-based manga mode
                effective_num_post_workers = 1
                # File threads per worker can still be > 1 if user set it
                effective_num_file_threads_per_worker = 1 # Files are sequential for this worker too
            elif use_multithreading_enabled_by_checkbox: # Standard creator feed with multithreading enabled
                effective_num_post_workers = max(1, min(num_threads_from_gui, MAX_THREADS)) # For posts
                effective_num_file_threads_per_worker = 1 # Files within each post worker are sequential
            # else (not multithreading for creator feed):
            # effective_num_post_workers remains 1, effective_num_file_threads_per_worker remains 1

        log_messages = ["="*40, f"🚀 Starting {'Link Extraction' if extract_links_only else ('Archive Download' if backend_filter_mode == 'archive' else 'Download')} @ {time.strftime('%Y-%m-%d %H:%M:%S')}", f"   URL: {api_url}"]
        if not extract_links_only: log_messages.append(f"   Save Location: {output_dir}")
        
        if post_id_from_url:
            log_messages.append(f"   Mode: Single Post")
            log_messages.append(f"     ↳ File Downloads: Up to {effective_num_file_threads_per_worker} concurrent file(s)")
        else:
            log_messages.append(f"   Mode: Creator Feed")
            log_messages.append(f"   Post Processing: {'Multi-threaded (' + str(effective_num_post_workers) + ' workers)' if effective_num_post_workers > 1 else 'Single-threaded (1 worker)'}")
            log_messages.append(f"     ↳ File Downloads per Worker: Up to {effective_num_file_threads_per_worker} concurrent file(s)")
            if is_creator_feed:
                if manga_mode: log_messages.append("   Page Range: All (Manga Mode - Oldest Posts Processed First)")
                else:
                    pr_log = "All"
                    if start_page or end_page: 
                        pr_log = f"{f'From {start_page} ' if start_page else ''}{'to ' if start_page and end_page else ''}{f'{end_page}' if end_page else (f'Up to {end_page}' if end_page else (f'From {start_page}' if start_page else 'Specific Range'))}".strip()
                    log_messages.append(f"   Page Range: {pr_log if pr_log else 'All'}")


        if not extract_links_only:
            log_messages.append(f"   Subfolders: {'Enabled' if use_subfolders else 'Disabled'}")
            if use_subfolders:
                 if custom_folder_name_cleaned: log_messages.append(f"   Custom Folder (Post): '{custom_folder_name_cleaned}'")
            if filter_character_list_to_pass:
                log_messages.append(f"   Character Filters: {', '.join(item['name'] for item in filter_character_list_to_pass)}")
                log_messages.append(f"     ↳ Char Filter Scope: {current_char_filter_scope.capitalize()}")
            elif use_subfolders:
                 log_messages.append(f"   Folder Naming: Automatic (based on title/known names)")


            log_messages.extend([
                f"   File Type Filter: {user_selected_filter_text} (Backend processing as: {backend_filter_mode})",
                f"   Skip Archives: {'.zip' if effective_skip_zip else ''}{', ' if effective_skip_zip and effective_skip_rar else ''}{'.rar' if effective_skip_rar else ''}{'None (Archive Mode)' if backend_filter_mode == 'archive' else ('None' if not (effective_skip_zip or effective_skip_rar) else '')}",
                f"   Skip Words (posts/files): {', '.join(skip_words_list) if skip_words_list else 'None'}",
                f"   Skip Words Scope: {current_skip_words_scope.capitalize()}",
                f"   Remove Words from Filename: {', '.join(remove_from_filename_words_list) if remove_from_filename_words_list else 'None'}",
                f"   Compress Images: {'Enabled' if compress_images else 'Disabled'}",
                f"   Thumbnails Only: {'Enabled' if download_thumbnails else 'Disabled'}" # Removed duplicate file handling log
            ])
        else:
            # If only_links, cookie might still be relevant for accessing the page
            log_messages.append(f"   Mode: Extracting Links Only")

        log_messages.append(f"   Show External Links: {'Enabled' if self.show_external_links and not extract_links_only and backend_filter_mode != 'archive' else 'Disabled'}")
        
        if manga_mode:
            log_messages.append(f"   Manga Mode (File Renaming by Post Title): Enabled")
            log_messages.append(f"     ↳ Manga Filename Style: {'Post Title Based' if self.manga_filename_style == STYLE_POST_TITLE else 'Original File Name'}")
            if filter_character_list_to_pass:
                 log_messages.append(f"     ↳ Manga Character Filter (for naming/folder): {', '.join(item['name'] for item in filter_character_list_to_pass)}")
            log_messages.append(f"     ↳ Manga Duplicates: Will be renamed with numeric suffix if names clash (e.g., _1, _2).")

        log_messages.append(f"   Use Cookie ('cookies.txt'): {'Enabled' if use_cookie_from_checkbox else 'Disabled'}")
        if use_cookie_from_checkbox and cookie_text_from_input:
            log_messages.append(f"     ↳ Cookie Text Provided: Yes (length: {len(cookie_text_from_input)})")
        elif use_cookie_from_checkbox and selected_cookie_file_path_for_backend:
            log_messages.append(f"     ↳ Cookie File Selected: {os.path.basename(selected_cookie_file_path_for_backend)}")
        should_use_multithreading_for_posts = use_multithreading_enabled_by_checkbox and not post_id_from_url
        # Adjust log message if date-based manga mode forced single thread
        if manga_mode and self.manga_filename_style == STYLE_DATE_BASED and not post_id_from_url:
            log_messages.append(f"   Threading: Single-threaded (posts) - Enforced by Manga Date Mode")
            should_use_multithreading_for_posts = False # Ensure this reflects the forced state
        else:
            log_messages.append(f"   Threading: {'Multi-threaded (posts)' if should_use_multithreading_for_posts else 'Single-threaded (posts)'}")
        if should_use_multithreading_for_posts:
            log_messages.append(f"   Number of Post Worker Threads: {effective_num_post_workers}")
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
            'filter_mode': backend_filter_mode,
            'skip_zip': effective_skip_zip,
            'skip_rar': effective_skip_rar,
            'use_subfolders': use_subfolders,
            'use_post_subfolders': use_post_subfolders,
            'compress_images': compress_images,
            'download_thumbnails': download_thumbnails,
            'service': service,
            'user_id': user_id,
            'downloaded_files': self.downloaded_files,
            'downloaded_files_lock': self.downloaded_files_lock,
            'downloaded_file_hashes': self.downloaded_file_hashes,
            'downloaded_file_hashes_lock': self.downloaded_file_hashes_lock,
            'skip_words_list': skip_words_list,
            'skip_words_scope': current_skip_words_scope,
            'remove_from_filename_words_list': remove_from_filename_words_list,
            'char_filter_scope': current_char_filter_scope,
            'show_external_links': self.show_external_links,
            'extract_links_only': extract_links_only,
            'start_page': start_page,
            'end_page': end_page,
            'target_post_id_from_initial_url': post_id_from_url,
            'custom_folder_name': custom_folder_name_cleaned,
            'manga_mode_active': manga_mode,
            'unwanted_keywords': unwanted_keywords_for_folders,
            'cancellation_event': self.cancellation_event,
            'dynamic_character_filter_holder': self.dynamic_character_filter_holder, # Pass the holder
            'pause_event': self.pause_event, # Explicitly add pause_event here
            # 'emitter' will be set based on single/multi-thread mode below
            'manga_filename_style': self.manga_filename_style,
            'num_file_threads_for_worker': effective_num_file_threads_per_worker,
            'manga_date_file_counter_ref': manga_date_file_counter_ref_for_thread,
            'allow_multipart_download': allow_multipart,
            'cookie_text': cookie_text_from_input, # Pass cookie text
            'selected_cookie_file': selected_cookie_file_path_for_backend, # Pass selected cookie file
            'app_base_dir': app_base_dir_for_cookies, # Pass app base dir
            'use_cookie': use_cookie_from_checkbox, # Pass cookie setting
            # 'duplicate_file_mode' and session-wide tracking removed
        }

        try:
            if should_use_multithreading_for_posts:
                self.log_signal.emit(f"   Initializing multi-threaded {'link extraction' if extract_links_only else 'download'} with {effective_num_post_workers} post workers...")
                args_template['emitter'] = self.worker_to_gui_queue # For multi-threaded, use the queue
                self.start_multi_threaded_download(num_post_workers=effective_num_post_workers, **args_template)
            else:
                self.log_signal.emit(f"   Initializing single-threaded {'link extraction' if extract_links_only else 'download'}...")
                # For single-threaded, DownloadThread creates its own PostProcessorSignals and passes it as emitter.
                dt_expected_keys = [
                    'api_url_input', 'output_dir', 'known_names_copy', 'cancellation_event',
                    'filter_character_list', 'filter_mode', 'skip_zip', 'skip_rar',
                    'use_subfolders', 'use_post_subfolders', 'custom_folder_name',
                    'compress_images', 'download_thumbnails', 'service', 'user_id',
                    'downloaded_files', 'downloaded_file_hashes', 'pause_event', 'remove_from_filename_words_list', # Added pause_event
                    'downloaded_files_lock', 'downloaded_file_hashes_lock', 'dynamic_character_filter_holder', # Added holder
                    'skip_words_list', 'skip_words_scope', 'char_filter_scope',
                    'show_external_links', 'extract_links_only', 'num_file_threads_for_worker',
                    'start_page', 'end_page', 'target_post_id_from_initial_url',
                    'manga_date_file_counter_ref', # Ensure this is passed for single thread mode
                    'manga_mode_active', 'unwanted_keywords', 'manga_filename_style',
                    'allow_multipart_download', 'use_cookie', 'cookie_text', 'app_base_dir', 'selected_cookie_file' # Added selected_cookie_file
                ]
                args_template['skip_current_file_flag'] = None
                single_thread_args = {key: args_template[key] for key in dt_expected_keys if key in args_template}
                self.start_single_threaded_download(**single_thread_args)
        except Exception as e:
            self.log_signal.emit(f"❌ CRITICAL ERROR preparing download: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Start Error", f"Failed to start process:\n{e}")
            self.download_finished(0,0,False, [])
            if self.pause_event: self.pause_event.clear()
            self.is_paused = False # Ensure pause state is reset on error


    def start_single_threaded_download(self, **kwargs):
        global BackendDownloadThread
        try:
            self.download_thread = BackendDownloadThread(**kwargs)
            if self.pause_event: self.pause_event.clear() # Clear pause before starting
            self.is_paused = False # Reset pause state
            if hasattr(self.download_thread, 'progress_signal'): self.download_thread.progress_signal.connect(self.handle_main_log)
            if hasattr(self.download_thread, 'add_character_prompt_signal'): self.download_thread.add_character_prompt_signal.connect(self.add_character_prompt_signal)
            if hasattr(self.download_thread, 'finished_signal'): self.download_thread.finished_signal.connect(self.download_finished)
            if hasattr(self.download_thread, 'receive_add_character_result'): self.character_prompt_response_signal.connect(self.download_thread.receive_add_character_result)
            if hasattr(self.download_thread, 'external_link_signal'): self.download_thread.external_link_signal.connect(self.handle_external_link_signal)
            if hasattr(self.download_thread, 'file_progress_signal'): self.download_thread.file_progress_signal.connect(self.update_file_progress_display)
            if hasattr(self.download_thread, 'missed_character_post_signal'): # New
                self.download_thread.missed_character_post_signal.connect(self.handle_missed_character_post)
            if hasattr(self.download_thread, 'retryable_file_failed_signal'): # New for retry
                self.download_thread.retryable_file_failed_signal.connect(self._handle_retryable_file_failure)
            self.download_thread.start()
            self.log_signal.emit("✅ Single download thread (for posts) started.")
        except Exception as e:
            self.log_signal.emit(f"❌ CRITICAL ERROR starting single-thread: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Thread Start Error", f"Failed to start download process: {e}")
            if self.pause_event: self.pause_event.clear()            
            self.is_paused = False # Ensure pause state is reset on error

    def _handle_retryable_file_failure(self, list_of_retry_details):
        """Appends details of files that failed but might be retryable later."""
        if list_of_retry_details:
            self.retryable_failed_files_info.extend(list_of_retry_details)
    
    def _submit_post_to_worker_pool(self, post_data_item, worker_args_template, num_file_dl_threads_for_each_worker, emitter_for_worker, ppw_expected_keys, ppw_optional_keys_with_defaults):
        """Helper to prepare and submit a single post processing task to the thread pool."""
        global PostProcessorWorker # Ensure PostProcessorWorker is accessible
        if not isinstance(post_data_item, dict):
            self.log_signal.emit(f"⚠️ Skipping invalid post data item (not a dict): {type(post_data_item)}");
            # Note: This skip does not directly increment processed_posts_count here,
            # as that counter is tied to future completion.
            # The overall effect is that total_posts_to_process might be higher than actual futures.
            return False # Indicate failure or skip

        worker_init_args = {}
        missing_keys = []
        for key in ppw_expected_keys:
            if key == 'post_data': worker_init_args[key] = post_data_item
            elif key == 'num_file_threads': worker_init_args[key] = num_file_dl_threads_for_each_worker
            elif key == 'emitter': worker_init_args[key] = emitter_for_worker
            elif key in worker_args_template: worker_init_args[key] = worker_args_template[key]
            elif key in ppw_optional_keys_with_defaults: pass # It has a default in PostProcessorWorker
            else: missing_keys.append(key)

        if missing_keys:
            self.log_signal.emit(f"❌ CRITICAL ERROR: Missing keys for PostProcessorWorker: {', '.join(missing_keys)}");
            self.cancellation_event.set()
            return False

        try:
            worker_instance = PostProcessorWorker(**worker_init_args)
            if self.thread_pool:
                future = self.thread_pool.submit(worker_instance.process)
                future.add_done_callback(self._handle_future_result)
                self.active_futures.append(future)
                return True # Indicate success
            else:
                self.log_signal.emit("⚠️ Thread pool not available. Cannot submit task.");
                self.cancellation_event.set() # Signal cancellation as we can't proceed
                return False
        except TypeError as te:
            self.log_signal.emit(f"❌ TypeError creating PostProcessorWorker: {te}\n   Passed Args: [{', '.join(sorted(worker_init_args.keys()))}]\n{traceback.format_exc(limit=5)}")
            self.cancellation_event.set()
            return False
        except RuntimeError: # Pool likely shutting down
            self.log_signal.emit(f"⚠️ RuntimeError submitting task (pool likely shutting down).")
            self.cancellation_event.set()
            return False
        except Exception as e:
            self.log_signal.emit(f"❌ Error submitting post {post_data_item.get('id','N/A')} to worker: {e}")
            self.cancellation_event.set()
            return False

    def start_multi_threaded_download(self, num_post_workers, **kwargs):
        global PostProcessorWorker
        if self.thread_pool is None:
            if self.pause_event: self.pause_event.clear() # Clear pause before starting
            self.is_paused = False # Reset pause state
            self.thread_pool = ThreadPoolExecutor(max_workers=num_post_workers, thread_name_prefix='PostWorker_')
        
        self.active_futures = []
        self.processed_posts_count = 0; self.total_posts_to_process = 0; self.download_counter = 0; self.skip_counter = 0
        self.all_kept_original_filenames = []

        fetcher_thread = threading.Thread(
            target=self._fetch_and_queue_posts,
            args=(kwargs['api_url_input'], kwargs, num_post_workers),
            daemon=True,
            name="PostFetcher"
        )
        fetcher_thread.start()
        self.log_signal.emit(f"✅ Post fetcher thread started. {num_post_workers} post worker threads initializing...")


    def _fetch_and_queue_posts(self, api_url_input_for_fetcher, worker_args_template, num_post_workers):
        global PostProcessorWorker, download_from_api # Ensure PostProcessorWorker is in scope
        all_posts_data = []
        fetch_error_occurred = False
        manga_mode_active_for_fetch = worker_args_template.get('manga_mode_active', False)

        # In multi-threaded mode, the emitter is the queue.
        emitter_for_worker = worker_args_template.get('emitter') # This should be self.worker_to_gui_queue
        if not emitter_for_worker: # Should not happen if logic in start_download is correct
             self.log_signal.emit("❌ CRITICAL ERROR: Emitter (queue) missing for worker in _fetch_and_queue_posts.");
             self.finished_signal.emit(0,0,True, []);
             return

        try:
            self.log_signal.emit("   Fetching post data from API (this may take a moment for large feeds)...")
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
                    fetch_error_occurred = True; self.log_signal.emit(f"❌ API fetcher returned non-list type: {type(posts_batch)}"); break
            
            if not fetch_error_occurred and not self.cancellation_event.is_set():
                self.log_signal.emit(f"✅ Post fetching complete. Total posts to process: {self.total_posts_to_process}")

            # --- De-duplicate posts by ID ---
            unique_posts_dict = {}
            for post in all_posts_data:
                post_id = post.get('id')
                if post_id is not None:
                    # Keep the first occurrence of each post ID
                    if post_id not in unique_posts_dict:
                        unique_posts_dict[post_id] = post
                else:
                    self.log_signal.emit(f"⚠️ Skipping post with no ID: {post.get('title', 'Untitled')}")

            all_posts_data = list(unique_posts_dict.values())
            # --- End De-duplication ---

            self.total_posts_to_process = len(all_posts_data)
            self.log_signal.emit(f"   Processed {len(unique_posts_dict)} unique posts after de-duplication.")
            if len(unique_posts_dict) < len(all_posts_data):
                 self.log_signal.emit(f"   Note: {len(all_posts_data) - len(unique_posts_dict)} duplicate post IDs were removed.")

        except TypeError as te:
            self.log_signal.emit(f"❌ TypeError calling download_from_api: {te}\n   Check 'downloader_utils.py' signature.\n{traceback.format_exc(limit=2)}"); fetch_error_occurred = True
        except RuntimeError as re_err:
            self.log_signal.emit(f"ℹ️ Post fetching runtime error (likely cancellation or API issue): {re_err}"); fetch_error_occurred = True
        except Exception as e:
            self.log_signal.emit(f"❌ Error during post fetching: {e}\n{traceback.format_exc(limit=2)}"); fetch_error_occurred = True


        if self.cancellation_event.is_set() or fetch_error_occurred:
            self.finished_signal.emit(self.download_counter, self.skip_counter, self.cancellation_event.is_set(), self.all_kept_original_filenames)
            if self.thread_pool: self.thread_pool.shutdown(wait=False, cancel_futures=True); self.thread_pool = None
            return

        if self.total_posts_to_process == 0:
            self.log_signal.emit("😕 No posts found or fetched to process.")
            self.finished_signal.emit(0,0,False, [])
            return

        self.log_signal.emit(f"   Preparing to submit {self.total_posts_to_process} post processing tasks to thread pool...")
        self.processed_posts_count = 0
        self.overall_progress_signal.emit(self.total_posts_to_process, 0) # Emit initial progress
        
        num_file_dl_threads_for_each_worker = worker_args_template.get('num_file_threads_for_worker', 1)


        ppw_expected_keys = [
            'post_data', 'download_root', 'known_names', 'filter_character_list', 'unwanted_keywords',
            'filter_mode', 'skip_zip', 'skip_rar', 'use_subfolders', 'use_post_subfolders',
            'target_post_id_from_initial_url', 'custom_folder_name', 'compress_images', 'emitter', 'pause_event', # Added pause_event
            'download_thumbnails', 'service', 'user_id', 'api_url_input',
            'cancellation_event', 'downloaded_files', 'downloaded_file_hashes',
            'downloaded_files_lock', 'downloaded_file_hashes_lock', 'remove_from_filename_words_list', 'dynamic_character_filter_holder', # Added holder
            'skip_words_list', 'skip_words_scope', 'char_filter_scope',
            'show_external_links', 'extract_links_only', 'allow_multipart_download', 'use_cookie', 'cookie_text', 'app_base_dir', 'selected_cookie_file', # Added selected_cookie_file
            'num_file_threads', 'skip_current_file_flag', 'manga_date_file_counter_ref',
            'manga_mode_active', 'manga_filename_style'
        ]
        # Ensure 'allow_multipart_download' is also considered for optional keys if it has a default in PostProcessorWorker
        ppw_optional_keys_with_defaults = {
            'skip_words_list', 'skip_words_scope', 'char_filter_scope', 'remove_from_filename_words_list',
            'show_external_links', 'extract_links_only', 'duplicate_file_mode', # Added duplicate_file_mode here
            'num_file_threads', 'skip_current_file_flag', 'manga_mode_active', 'manga_filename_style',
            'manga_date_file_counter_ref', 'use_cookie', 'cookie_text', 'app_base_dir', 'selected_cookie_file' # Added selected_cookie_file
        }
        
        # --- Batching Logic ---
        if num_post_workers > POST_WORKER_BATCH_THRESHOLD and self.total_posts_to_process > POST_WORKER_NUM_BATCHES :
            self.log_signal.emit(f"   High thread count ({num_post_workers}) detected. Batching post submissions into {POST_WORKER_NUM_BATCHES} parts.")
            
            import math # Moved import here
            batch_size = math.ceil(self.total_posts_to_process / POST_WORKER_NUM_BATCHES)
            submitted_count_in_batching = 0

            for batch_num in range(POST_WORKER_NUM_BATCHES):
                if self.cancellation_event.is_set(): break
                
                if self.pause_event and self.pause_event.is_set():
                    self.log_signal.emit(f"   [Fetcher] Batch submission paused before batch {batch_num + 1}/{POST_WORKER_NUM_BATCHES}...")
                    while self.pause_event.is_set():
                        if self.cancellation_event.is_set():
                            self.log_signal.emit("   [Fetcher] Batch submission cancelled while paused.")
                            break
                        time.sleep(0.5) 
                    if self.cancellation_event.is_set(): break
                    if not self.cancellation_event.is_set():
                        self.log_signal.emit(f"   [Fetcher] Batch submission resumed. Processing batch {batch_num + 1}/{POST_WORKER_NUM_BATCHES}.")
                
                start_index = batch_num * batch_size
                end_index = min((batch_num + 1) * batch_size, self.total_posts_to_process)
                current_batch_posts = all_posts_data[start_index:end_index]

                if not current_batch_posts: continue

                self.log_signal.emit(f"   Submitting batch {batch_num + 1}/{POST_WORKER_NUM_BATCHES} ({len(current_batch_posts)} posts) to pool...")
                for post_data_item in current_batch_posts:
                    if self.cancellation_event.is_set(): break
                    success = self._submit_post_to_worker_pool(post_data_item, worker_args_template, num_file_dl_threads_for_each_worker, emitter_for_worker, ppw_expected_keys, ppw_optional_keys_with_defaults)
                    if success:
                        submitted_count_in_batching += 1
                    elif self.cancellation_event.is_set(): 
                        break 
                
                if self.cancellation_event.is_set(): break

                if batch_num < POST_WORKER_NUM_BATCHES - 1: 
                    self.log_signal.emit(f"   Batch {batch_num + 1} submitted. Waiting {POST_WORKER_BATCH_DELAY_SECONDS}s before next batch...")
                    delay_start_time = time.time()
                    while time.time() - delay_start_time < POST_WORKER_BATCH_DELAY_SECONDS:
                        if self.cancellation_event.is_set(): break
                        time.sleep(0.1) 
                    if self.cancellation_event.is_set(): break
            
            self.log_signal.emit(f"   All {POST_WORKER_NUM_BATCHES} batches ({submitted_count_in_batching} total tasks) submitted to pool via batching.")

        else: # Standard submission (no batching)
            self.log_signal.emit(f"   Submitting all {self.total_posts_to_process} tasks to pool directly...")
            submitted_count_direct = 0
            for post_data_item in all_posts_data:
                if self.cancellation_event.is_set(): break
                success = self._submit_post_to_worker_pool(post_data_item, worker_args_template, num_file_dl_threads_for_each_worker, emitter_for_worker, ppw_expected_keys, ppw_optional_keys_with_defaults)
                if success:
                    submitted_count_direct += 1
                elif self.cancellation_event.is_set():
                    break
            
            if not self.cancellation_event.is_set():
                self.log_signal.emit(f"   All {submitted_count_direct} post processing tasks submitted directly to pool.")

        if self.cancellation_event.is_set():
            self.log_signal.emit("   Cancellation detected after/during task submission loop.")

            self.finished_signal.emit(self.download_counter, self.skip_counter, True, self.all_kept_original_filenames)
            if self.thread_pool: self.thread_pool.shutdown(wait=False, cancel_futures=True); self.thread_pool = None

    def _handle_future_result(self, future: Future):
        self.processed_posts_count += 1
        downloaded_files_from_future, skipped_files_from_future = 0, 0
        kept_originals_from_future = []
        try:
            if future.cancelled():
                self.log_signal.emit("   A post processing task was cancelled.")
            elif future.exception():
                self.log_signal.emit(f"❌ Post processing worker error: {future.exception()}")
            else: # Future completed successfully
                downloaded_files_from_future, skipped_files_from_future, kept_originals_from_future, retryable_failures_from_post = future.result()
                if retryable_failures_from_post:
                    self.retryable_failed_files_info.extend(retryable_failures_from_post)

            with self.downloaded_files_lock:
                self.download_counter += downloaded_files_from_future
                self.skip_counter += skipped_files_from_future

            if kept_originals_from_future:
                self.all_kept_original_filenames.extend(kept_originals_from_future)

            self.overall_progress_signal.emit(self.total_posts_to_process, self.processed_posts_count)
        except Exception as e:
            self.log_signal.emit(f"❌ Error in _handle_future_result callback: {e}\n{traceback.format_exc(limit=2)}")
            # If an error occurs, ensure we don't get stuck waiting for this future
            if self.processed_posts_count < self.total_posts_to_process:
                 self.processed_posts_count = self.total_posts_to_process # Mark as if all processed to allow finish

        if self.total_posts_to_process > 0 and self.processed_posts_count >= self.total_posts_to_process:
            if all(f.done() for f in self.active_futures):
                QApplication.processEvents()
                self.log_signal.emit("🏁 All submitted post tasks have completed or failed.")
                self.finished_signal.emit(self.download_counter, self.skip_counter, self.cancellation_event.is_set(), self.all_kept_original_filenames)
    def _get_configurable_widgets_on_pause(self):
        """Returns a list of widgets that should be re-enabled when paused."""
        return [
            self.dir_input, self.dir_button,
            self.character_input, self.char_filter_scope_toggle_button,
            self.skip_words_input, self.skip_scope_toggle_button,
            self.remove_from_filename_input,
            self.radio_all, self.radio_images, self.radio_videos, 
            self.radio_only_archives, self.radio_only_links, # Radio buttons themselves
            self.skip_zip_checkbox, self.skip_rar_checkbox,
            self.download_thumbnails_checkbox, self.compress_images_checkbox,
            self.use_subfolders_checkbox, self.use_subfolder_per_post_checkbox,
            self.manga_mode_checkbox, 
            self.manga_rename_toggle_button, # Visibility handled by update_ui_for_manga_mode
            self.cookie_browse_button, # Add cookie browse button
            self.multipart_toggle_button,
            self.cookie_text_input, # Add cookie text input
            self.use_cookie_checkbox, # Add cookie checkbox here
            self.external_links_checkbox
        ]

    def set_ui_enabled(self, enabled):
        # This list contains all widgets whose enabled state might change.
        all_potentially_toggleable_widgets = [
            self.link_input, self.dir_input, self.dir_button,
            self.page_range_label, self.start_page_input, self.to_label, self.end_page_input,
            self.character_input, self.char_filter_scope_toggle_button,
            self.custom_folder_label, self.custom_folder_input,
            self.skip_words_input, self.skip_scope_toggle_button, self.remove_from_filename_input,
            self.radio_all, self.radio_images, self.radio_videos, self.radio_only_archives, self.radio_only_links,
            self.skip_zip_checkbox, self.skip_rar_checkbox, self.download_thumbnails_checkbox, self.compress_images_checkbox,
            self.use_subfolders_checkbox, self.use_subfolder_per_post_checkbox,
            self.use_multithreading_checkbox, self.thread_count_input, self.thread_count_label,
            self.external_links_checkbox, self.manga_mode_checkbox, self.manga_rename_toggle_button, self.use_cookie_checkbox, self.cookie_text_input, self.cookie_browse_button,
            self.multipart_toggle_button,
            self.character_search_input, self.new_char_input, self.add_char_button, self.delete_char_button,
            self.reset_button
        ]
        
        widgets_to_enable_on_pause = self._get_configurable_widgets_on_pause()
        download_is_active_or_paused = not enabled # True if a download is running or paused

        for widget in all_potentially_toggleable_widgets:
            if not widget: continue

            if self.is_paused and widget in widgets_to_enable_on_pause:
                widget.setEnabled(True) # Re-enable specific widgets if paused
            else:
                widget.setEnabled(enabled) # Standard behavior: enable if idle, disable if running
        
        if enabled:
            self._handle_filter_mode_change(self.radio_group.checkedButton(), True)
        
        if self.external_links_checkbox:
            is_only_links = self.radio_only_links and self.radio_only_links.isChecked()
            is_only_archives = self.radio_only_archives and self.radio_only_archives.isChecked()
            can_enable_ext_links = enabled and not is_only_links and not is_only_archives
            self.external_links_checkbox.setEnabled(can_enable_ext_links)
            if self.is_paused and not is_only_links and not is_only_archives:
                self.external_links_checkbox.setEnabled(True)

        # Handle "Use Cookie" checkbox and text input
        if hasattr(self, 'use_cookie_checkbox'):
            self.use_cookie_checkbox.setEnabled(enabled or self.is_paused)
            self._update_cookie_input_visibility(self.use_cookie_checkbox.isChecked()) # This will handle cookie_text_input's enabled state

        if hasattr(self, 'use_cookie_checkbox'): self.use_cookie_checkbox.setEnabled(enabled or self.is_paused)

        if self.log_verbosity_toggle_button: self.log_verbosity_toggle_button.setEnabled(True) # New button, always enabled

        multithreading_currently_on = self.use_multithreading_checkbox.isChecked()
        # Thread count related widgets follow 'enabled' strictly (disabled if paused)
        if self.thread_count_input: self.thread_count_input.setEnabled(enabled and multithreading_currently_on)
        if self.thread_count_label: self.thread_count_label.setEnabled(enabled and multithreading_currently_on)

        subfolders_currently_on = self.use_subfolders_checkbox.isChecked()
        if self.use_subfolder_per_post_checkbox:
            self.use_subfolder_per_post_checkbox.setEnabled(enabled or (self.is_paused and self.use_subfolder_per_post_checkbox in widgets_to_enable_on_pause))

        # --- Main Action Buttons ---
        self.download_btn.setEnabled(enabled) # Start Download only enabled when fully idle
        self.cancel_btn.setEnabled(download_is_active_or_paused) # Cancel enabled if running or paused

        # Pause button logic
        if self.pause_btn:
            self.pause_btn.setEnabled(download_is_active_or_paused)
            if download_is_active_or_paused:
                self.pause_btn.setText("▶️ Resume Download" if self.is_paused else "⏸️ Pause Download")
                self.pause_btn.setToolTip("Click to resume the download." if self.is_paused else "Click to pause the download.")
            else: # Download not active
                self.pause_btn.setText("⏸️ Pause Download")
                self.pause_btn.setToolTip("Click to pause the ongoing download process.")
                self.is_paused = False # Ensure pause state is reset if download finishes/cancels

        if enabled: # Ensure these are updated based on current (possibly reset) checkbox states
                if self.pause_event: self.pause_event.clear()

        # --- UI Updates based on current states ---
        # These should run if UI is idle OR if paused (to reflect changes made during pause)
        if enabled or self.is_paused:             
            self._handle_multithreading_toggle(multithreading_currently_on)
            self.update_ui_for_manga_mode(self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False)
            self.update_custom_folder_visibility(self.link_input.text())
            self.update_page_range_enabled_state()
            # Re-evaluate filter mode as radio buttons might have been changed during pause
            if self.radio_group and self.radio_group.checkedButton():
                 self._handle_filter_mode_change(self.radio_group.checkedButton(), True)
            self.update_ui_for_subfolders(subfolders_currently_on) # Re-evaluate subfolder UI

    def _handle_pause_resume_action(self):
        if self._is_download_active(): # Check if a download is actually running
            self.is_paused = not self.is_paused
            if self.is_paused:
                if self.pause_event: self.pause_event.set()
                self.log_signal.emit("ℹ️ Download paused by user. Some settings can now be changed for subsequent operations.")
            else:
                if self.pause_event: self.pause_event.clear()
                self.log_signal.emit("ℹ️ Download resumed by user.")
            self.set_ui_enabled(False) # Re-evaluate UI state (buttons will update)

    def _perform_soft_ui_reset(self, preserve_url=None, preserve_dir=None):
        """Resets UI elements and some state to app defaults, then applies preserved inputs."""
        self.log_signal.emit("🔄 Performing soft UI reset...")

        # 1. Reset UI fields to their visual defaults
        self.link_input.clear() # Will be set later if preserve_url is given
        self.dir_input.clear()  # Will be set later if preserve_dir is given
        self.custom_folder_input.clear(); self.character_input.clear();
        self.skip_words_input.clear(); self.start_page_input.clear(); self.end_page_input.clear(); self.new_char_input.clear();
        if hasattr(self, 'remove_from_filename_input'): self.remove_from_filename_input.clear()
        self.character_search_input.clear(); self.thread_count_input.setText("4"); self.radio_all.setChecked(True);
        self.skip_zip_checkbox.setChecked(True); self.skip_rar_checkbox.setChecked(True); self.download_thumbnails_checkbox.setChecked(False);
        self.compress_images_checkbox.setChecked(False); self.use_subfolders_checkbox.setChecked(True);
        self.use_subfolder_per_post_checkbox.setChecked(False); self.use_multithreading_checkbox.setChecked(True);
        self.external_links_checkbox.setChecked(False)
        if self.manga_mode_checkbox: self.manga_mode_checkbox.setChecked(False)
        if hasattr(self, 'use_cookie_checkbox'): self.use_cookie_checkbox.setChecked(self.use_cookie_setting) # Reset to loaded or False
        
        # For soft reset, if a cookie file was selected, keep it displayed if "Use Cookie" remains checked.
        # Otherwise, clear it. The _update_cookie_input_visibility will handle the display.
        if not (hasattr(self, 'use_cookie_checkbox') and self.use_cookie_checkbox.isChecked()):
            self.selected_cookie_filepath = None 
        if hasattr(self, 'cookie_text_input'): self.cookie_text_input.setText(self.cookie_text_setting if self.use_cookie_setting else "") # Reset to loaded or empty

        # 2. Reset internal state for UI-managed settings to app defaults (not from QSettings)
        self.allow_multipart_download_setting = False # Default to OFF
        self._update_multipart_toggle_button_text()

        self.skip_words_scope = SKIP_SCOPE_POSTS # Default
        self._update_skip_scope_button_text()

        self.char_filter_scope = CHAR_SCOPE_TITLE # Default
        self._update_char_filter_scope_button_text()

        self.manga_filename_style = STYLE_POST_TITLE # Reset to app default
        self._update_manga_filename_style_button_text()

        # 3. Restore preserved URL and Directory
        if preserve_url is not None:
            self.link_input.setText(preserve_url)
        if preserve_dir is not None:
            self.dir_input.setText(preserve_dir)

        # 4. Reset operational state variables (but not session-based downloaded_files/hashes)
        self.external_link_queue.clear(); self.extracted_links_cache = []
        self._is_processing_external_link_queue = False; self._current_link_post_title = None
        if self.pause_event: self.pause_event.clear()        
        self.total_posts_to_process = 0; self.processed_posts_count = 0
        self.download_counter = 0; self.skip_counter = 0
        self.all_kept_original_filenames = []
        self.is_paused = False # Reset pause state on soft reset

        # 5. Update UI based on new (default or preserved) states
        self._handle_filter_mode_change(self.radio_group.checkedButton(), True)
        self._handle_multithreading_toggle(self.use_multithreading_checkbox.isChecked())
        self.filter_character_list(self.character_search_input.text())

        self.set_ui_enabled(True) # This enables buttons and calls other UI update methods

        # Explicitly call these to ensure they reflect changes from preserved inputs
        self.update_custom_folder_visibility(self.link_input.text())
        self.update_page_range_enabled_state()
        self._update_cookie_input_visibility(self.use_cookie_checkbox.isChecked() if hasattr(self, 'use_cookie_checkbox') else False)
        # update_ui_for_manga_mode is called within set_ui_enabled

        self.log_signal.emit("✅ Soft UI reset complete. Preserved URL and Directory (if provided).")


    def cancel_download_button_action(self):
        if not self.cancel_btn.isEnabled() and not self.cancellation_event.is_set(): self.log_signal.emit("ℹ️ No active download to cancel or already cancelling."); return
        self.log_signal.emit("⚠️ Requesting cancellation of download process (soft reset)...")

        current_url = self.link_input.text()
        current_dir = self.dir_input.text()

        self.cancellation_event.set()
        if self.download_thread and self.download_thread.isRunning(): self.download_thread.requestInterruption(); self.log_signal.emit("   Signaled single download thread to interrupt.")
        if self.thread_pool:
            self.log_signal.emit("   Initiating non-blocking shutdown and cancellation of worker pool tasks...")
            self.thread_pool.shutdown(wait=False, cancel_futures=True)
            self.thread_pool = None # Allow recreation for next download
            self.active_futures = []

        self.external_link_queue.clear(); self._is_processing_external_link_queue = False; self._current_link_post_title = None

        self._perform_soft_ui_reset(preserve_url=current_url, preserve_dir=current_dir)

        self.progress_label.setText("Progress: Cancelled. Ready for new task.")
        self.file_progress_label.setText("")
        if self.pause_event: self.pause_event.clear()        
        self.log_signal.emit("ℹ️ UI reset. Ready for new operation. Background tasks are being terminated.")
        self.is_paused = False # Ensure pause state is reset
        
        # Also clear retryable files on a manual cancel, as the context is lost.
        if self.retryable_failed_files_info:
            self.log_signal.emit(f"   Discarding {len(self.retryable_failed_files_info)} pending retryable file(s) due to cancellation.")
            self.retryable_failed_files_info.clear()

    def download_finished(self, total_downloaded, total_skipped, cancelled_by_user, kept_original_names_list=None):
        if kept_original_names_list is None:
            kept_original_names_list = self.all_kept_original_filenames if hasattr(self, 'all_kept_original_filenames') else []
        if kept_original_names_list is None:
            kept_original_names_list = []

        status_message = "Cancelled by user" if cancelled_by_user else "Finished"

        # If cancelled, don't offer retry for this session's failures
        if cancelled_by_user and self.retryable_failed_files_info:
            self.log_signal.emit(f"   Download cancelled, discarding {len(self.retryable_failed_files_info)} file(s) that were pending retry.")
            self.retryable_failed_files_info.clear()

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

        if self.download_thread:
            try:
                if hasattr(self.download_thread, 'progress_signal'): self.download_thread.progress_signal.disconnect(self.handle_main_log)
                if hasattr(self.download_thread, 'add_character_prompt_signal'): self.download_thread.add_character_prompt_signal.disconnect(self.add_character_prompt_signal)
                if hasattr(self.download_thread, 'finished_signal'): self.download_thread.finished_signal.disconnect(self.download_finished)
                if hasattr(self.download_thread, 'receive_add_character_result'): self.character_prompt_response_signal.disconnect(self.download_thread.receive_add_character_result)
                if hasattr(self.download_thread, 'external_link_signal'): self.download_thread.external_link_signal.disconnect(self.handle_external_link_signal)
                if hasattr(self.download_thread, 'file_progress_signal'): self.download_thread.file_progress_signal.disconnect(self.update_file_progress_display)
                if hasattr(self.download_thread, 'missed_character_post_signal'): # New
                    self.download_thread.missed_character_post_signal.disconnect(self.handle_missed_character_post)
                if hasattr(self.download_thread, 'retryable_file_failed_signal'): # New
                    self.download_thread.retryable_file_failed_signal.disconnect(self._handle_retryable_file_failure)
            except (TypeError, RuntimeError) as e: 
                self.log_signal.emit(f"ℹ️ Note during single-thread signal disconnection: {e}")
            
            if not self.download_thread.isRunning(): # Check if it was this thread
                 self.download_thread = None

        self.progress_label.setText(f"{status_message}: {total_downloaded} downloaded, {total_skipped} skipped.")
        self.file_progress_label.setText("")
        if not cancelled_by_user: self._try_process_next_external_link()

        if self.thread_pool:
            self.log_signal.emit("   Ensuring worker thread pool is shut down...")
            self.thread_pool.shutdown(wait=True, cancel_futures=True)
            self.thread_pool = None
        
        self.active_futures = []
        if self.pause_event: self.pause_event.clear()
        self.cancel_btn.setEnabled(False)
        self.is_paused = False # Reset pause state when download finishes

        # Offer to retry failed files if any were collected and not cancelled
        if not cancelled_by_user and self.retryable_failed_files_info:
            num_failed = len(self.retryable_failed_files_info)
            reply = QMessageBox.question(self, "Retry Failed Downloads?",
                                         f"{num_failed} file(s) failed with potentially recoverable errors (e.g., IncompleteRead).\n\n"
                                         "Would you like to attempt to download these failed files again?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self._start_failed_files_retry_session()
                return # Don't fully reset UI if retrying
            else:
                self.log_signal.emit("ℹ️ User chose not to retry failed files.")
                self.retryable_failed_files_info.clear() # Clear if not retrying

        self.set_ui_enabled(True) # Full UI reset if not retrying

    def _start_failed_files_retry_session(self):
        self.log_signal.emit(f"🔄 Starting retry session for {len(self.retryable_failed_files_info)} file(s)...")
        self.set_ui_enabled(False) # Disable UI, but cancel button will be enabled
        if self.cancel_btn: self.cancel_btn.setText("❌ Cancel Retry")

        self.files_for_current_retry_session = list(self.retryable_failed_files_info)
        self.retryable_failed_files_info.clear() # Clear original list

        self.active_retry_futures = []
        self.processed_retry_count = 0
        self.succeeded_retry_count = 0
        self.failed_retry_count_in_session = 0 # Renamed to avoid clash
        self.total_files_for_retry = len(self.files_for_current_retry_session)

        self.progress_label.setText(f"Retrying 0 / {self.total_files_for_retry} files...")
        self.cancellation_event.clear() # Clear main cancellation for retry session

        num_retry_threads = 1
        try:
            num_threads_from_gui = int(self.thread_count_input.text().strip())
            num_retry_threads = max(1, min(num_threads_from_gui, MAX_FILE_THREADS_PER_POST_OR_WORKER, self.total_files_for_retry if self.total_files_for_retry > 0 else 1))
        except ValueError:
            num_retry_threads = 1 # Default to 1 if input is bad

        self.retry_thread_pool = ThreadPoolExecutor(max_workers=num_retry_threads, thread_name_prefix='RetryFile_')

        # Prepare common arguments for PostProcessorWorker instances during retry
        common_ppw_args_for_retry = {
            'download_root': self.dir_input.text().strip(),
            'known_names': list(KNOWN_NAMES),
            'emitter': self.worker_to_gui_queue, # Use main queue for progress
            'unwanted_keywords': {'spicy', 'hd', 'nsfw', '4k', 'preview', 'teaser', 'clip'},
            'filter_mode': self.get_filter_mode(), # Use current filter mode
            'skip_zip': self.skip_zip_checkbox.isChecked(),
            'skip_rar': self.skip_rar_checkbox.isChecked(),
            'use_subfolders': self.use_subfolders_checkbox.isChecked(),
            'use_post_subfolders': self.use_subfolder_per_post_checkbox.isChecked(),
            'compress_images': self.compress_images_checkbox.isChecked(),
            'download_thumbnails': self.download_thumbnails_checkbox.isChecked(),
            'pause_event': self.pause_event,
            'cancellation_event': self.cancellation_event,
            'downloaded_files': self.downloaded_files, # Share session's downloaded sets
            'downloaded_file_hashes': self.downloaded_file_hashes,
            'downloaded_files_lock': self.downloaded_files_lock,
            'downloaded_file_hashes_lock': self.downloaded_file_hashes_lock,
            'skip_words_list': [word.strip().lower() for word in self.skip_words_input.text().strip().split(',') if word.strip()],
            'skip_words_scope': self.get_skip_words_scope(),
            'char_filter_scope': self.get_char_filter_scope(),
            'remove_from_filename_words_list': [word.strip() for word in self.remove_from_filename_input.text().strip().split(',') if word.strip()] if hasattr(self, 'remove_from_filename_input') else [],
            'allow_multipart_download': self.allow_multipart_download_setting,
            # These are not strictly needed for retry of a single file if path is fixed, but good to pass
            'filter_character_list': None, 
            'dynamic_character_filter_holder': None,
            'target_post_id_from_initial_url': None, # Not relevant for file retry
            'custom_folder_name': None, # Path is already determined
            'num_file_threads': 1, # Each retry task is one file, multipart handled by _download_single_file
            'manga_date_file_counter_ref': None, # Filename is forced
        }

        for job_details in self.files_for_current_retry_session:
            future = self.retry_thread_pool.submit(self._execute_single_file_retry, job_details, common_ppw_args_for_retry)
            future.add_done_callback(self._handle_retry_future_result)
            self.active_retry_futures.append(future)

    def _execute_single_file_retry(self, job_details, common_args):
        """Executes a single file download retry attempt."""
        # Construct a dummy post_data, service, user_id, api_url_input for PPW init
        dummy_post_data = {'id': job_details['original_post_id_for_log'], 'title': job_details['post_title']}
        # Extract service/user from a known URL or pass them if available in job_details
        # For simplicity, assuming we might not have original service/user easily.
        # This might affect some logging or minor details in PPW if it relies on them beyond post_id.
        # Let's assume job_details can store 'service' and 'user_id' from the original post.
        
        ppw_init_args = {
            **common_args,
            'post_data': dummy_post_data,
            'service': job_details.get('service', 'unknown_service'), # Get from job_details or default
            'user_id': job_details.get('user_id', 'unknown_user'),   # Get from job_details or default
            'api_url_input': job_details.get('api_url_input', ''), # Original post's API URL
            'manga_mode_active': job_details.get('manga_mode_active_for_file', False),
            'manga_filename_style': job_details.get('manga_filename_style_for_file', STYLE_POST_TITLE),
        }
        worker = PostProcessorWorker(**ppw_init_args)
        
        dl_count, skip_count, filename_saved, original_kept, status, _ = worker._download_single_file(
            file_info=job_details['file_info'],
            target_folder_path=job_details['target_folder_path'],
            headers=job_details['headers'],
            original_post_id_for_log=job_details['original_post_id_for_log'],
            skip_event=None, # No individual skip for retry items
            post_title=job_details['post_title'],
            file_index_in_post=job_details['file_index_in_post'],
            num_files_in_this_post=job_details['num_files_in_this_post'],
            forced_filename_override=job_details.get('forced_filename_override')
        )
        return dl_count > 0 # True if successful, False otherwise

    def _handle_retry_future_result(self, future):
        self.processed_retry_count += 1
        was_successful = False
        try:
            if future.cancelled():
                self.log_signal.emit("   A retry task was cancelled.")
            elif future.exception():
                self.log_signal.emit(f"❌ Retry task worker error: {future.exception()}")
            else:
                was_successful = future.result()
                if was_successful:
                    self.succeeded_retry_count += 1
                else:
                    self.failed_retry_count_in_session += 1
        except Exception as e:
            self.log_signal.emit(f"❌ Error in _handle_retry_future_result: {e}")
            self.failed_retry_count_in_session +=1

        self.progress_label.setText(f"Retrying {self.processed_retry_count} / {self.total_files_for_retry} files... (Succeeded: {self.succeeded_retry_count}, Failed: {self.failed_retry_count_in_session})")

        if self.processed_retry_count >= self.total_files_for_retry:
            if all(f.done() for f in self.active_retry_futures):
                self._retry_session_finished()

    def _retry_session_finished(self):
        self.log_signal.emit("🏁 Retry session finished.")
        self.log_signal.emit(f"   Summary: {self.succeeded_retry_count} Succeeded, {self.failed_retry_count_in_session} Failed.")
        
        if self.retry_thread_pool:
            self.retry_thread_pool.shutdown(wait=True)
            self.retry_thread_pool = None
        
        self.active_retry_futures.clear()
        self.files_for_current_retry_session.clear()
        
        self.set_ui_enabled(True) # Re-enable UI
        if self.cancel_btn: self.cancel_btn.setText("❌ Cancel & Reset UI") # Reset cancel button text
        self.progress_label.setText(f"Retry Finished. Succeeded: {self.succeeded_retry_count}, Failed: {self.failed_retry_count_in_session}. Ready for new task.")
        self.file_progress_label.setText("")
        if self.pause_event: self.pause_event.clear()
        self.is_paused = False

    def toggle_active_log_view(self):
        if self.current_log_view == 'progress':
            self.current_log_view = 'missed_character'
            if self.log_view_stack: self.log_view_stack.setCurrentIndex(1) # Show missed character log
            if self.log_verbosity_toggle_button:
                self.log_verbosity_toggle_button.setText(self.CLOSED_EYE_ICON) # Monkey icon
                self.log_verbosity_toggle_button.setToolTip("Current View: Missed Character Log. Click to switch to Progress Log.")
            if self.progress_log_label: self.progress_log_label.setText("🚫 Missed Character Log:")
            # self.log_signal.emit("="*20 + " Switched to Missed Character Log View " + "="*20) # Optional log message
        else: # current_log_view == 'missed_character'
            self.current_log_view = 'progress'
            if self.log_view_stack: self.log_view_stack.setCurrentIndex(0) # Show progress log
            if self.log_verbosity_toggle_button:
                self.log_verbosity_toggle_button.setText(self.EYE_ICON) # Open eye icon
                self.log_verbosity_toggle_button.setToolTip("Current View: Progress Log. Click to switch to Missed Character Log.")
            if self.progress_log_label: self.progress_log_label.setText("📜 Progress Log:")
            # self.log_signal.emit("="*20 + " Switched to Progress Log View " + "="*20) # Optional log message

    def reset_application_state(self):
        if self._is_download_active(): QMessageBox.warning(self, "Reset Error", "Cannot reset while a download is in progress. Please cancel first."); return
        self.log_signal.emit("🔄 Resetting application state to defaults..."); self._reset_ui_to_defaults()
        self.main_log_output.clear(); self.external_log_output.clear()
        if self.missed_character_log_output: self.missed_character_log_output.clear()

        self.current_log_view = 'progress' # Reset to progress log view
        if self.log_view_stack: self.log_view_stack.setCurrentIndex(0)
        if self.progress_log_label: self.progress_log_label.setText("📜 Progress Log:")
        if self.log_verbosity_toggle_button:
            self.log_verbosity_toggle_button.setText(self.EYE_ICON)
            self.log_verbosity_toggle_button.setToolTip("Current View: Progress Log. Click to switch to Missed Character Log.")

        if self.show_external_links and not (self.radio_only_links and self.radio_only_links.isChecked()): self.external_log_output.append("🔗 External Links Found:")
        self.external_link_queue.clear(); self.extracted_links_cache = []; self._is_processing_external_link_queue = False; self._current_link_post_title = None
        self.progress_label.setText("Progress: Idle"); self.file_progress_label.setText("")
        with self.downloaded_files_lock: count = len(self.downloaded_files); self.downloaded_files.clear();
        # Reset old summarization state (if any remnants) and new bold list state
        self.missed_title_key_terms_count.clear()
        self.missed_title_key_terms_examples.clear()
        self.logged_summary_for_key_term.clear()
        self.already_logged_bold_key_terms.clear()
        self.missed_key_terms_buffer.clear()

        if count > 0: self.log_signal.emit(f"   Cleared {count} downloaded filename(s) from session memory.")
        with self.downloaded_file_hashes_lock: count = len(self.downloaded_file_hashes); self.downloaded_file_hashes.clear();
        if count > 0: self.log_signal.emit(f"   Cleared {count} downloaded file hash(es) from session memory.")

        self.total_posts_to_process = 0; self.processed_posts_count = 0; self.download_counter = 0; self.skip_counter = 0
        self.all_kept_original_filenames = []
        self.cancellation_event.clear()
        if self.pause_event: self.pause_event.clear()
        self.is_paused = False # Reset pause state on full reset
        self.manga_filename_style = STYLE_POST_TITLE
        self.settings.setValue(MANGA_FILENAME_STYLE_KEY, self.manga_filename_style)
        
        self.skip_words_scope = SKIP_SCOPE_POSTS
        self.settings.setValue(SKIP_WORDS_SCOPE_KEY, self.skip_words_scope)
        self._update_skip_scope_button_text()

        self.char_filter_scope = CHAR_SCOPE_FILES # Default to Files on full reset
        self.settings.setValue(CHAR_FILTER_SCOPE_KEY, self.char_filter_scope) 
        self._update_char_filter_scope_button_text() 

        self.settings.sync()
        self._update_manga_filename_style_button_text()
        self.update_ui_for_manga_mode(self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False)

    def _reset_ui_to_defaults(self):
        self.link_input.clear(); self.dir_input.clear(); self.custom_folder_input.clear(); self.character_input.clear();
        self.skip_words_input.clear(); self.start_page_input.clear(); self.end_page_input.clear(); self.new_char_input.clear();
        if hasattr(self, 'remove_from_filename_input'): self.remove_from_filename_input.clear()
        self.character_search_input.clear(); self.thread_count_input.setText("4"); self.radio_all.setChecked(True);
        self.skip_zip_checkbox.setChecked(True); self.skip_rar_checkbox.setChecked(True); self.download_thumbnails_checkbox.setChecked(False);
        self.compress_images_checkbox.setChecked(False); self.use_subfolders_checkbox.setChecked(True);
        self.use_subfolder_per_post_checkbox.setChecked(False); self.use_multithreading_checkbox.setChecked(True);
        self.external_links_checkbox.setChecked(False)
        if self.manga_mode_checkbox: self.manga_mode_checkbox.setChecked(False)        
        if hasattr(self, 'use_cookie_checkbox'): self.use_cookie_checkbox.setChecked(False) # Default to False on full reset
        
        # On full reset, always clear the selected cookie file path
        self.selected_cookie_filepath = None

        if hasattr(self, 'cookie_text_input'): self.cookie_text_input.clear() # Clear cookie text on full reset

        # Reset old summarization state (if any remnants) and new bold list state
        self.missed_title_key_terms_count.clear()
        self.missed_title_key_terms_examples.clear()
        self.logged_summary_for_key_term.clear()
        self.already_logged_bold_key_terms.clear()
        if self.pause_event: self.pause_event.clear()
        self.is_paused = False # Reset pause state
        self.missed_key_terms_buffer.clear()
        if self.missed_character_log_output: self.missed_character_log_output.clear()

        self.allow_multipart_download_setting = False # Default to OFF
        self._update_multipart_toggle_button_text() # Update button text

        self.skip_words_scope = SKIP_SCOPE_POSTS
        self._update_skip_scope_button_text()
        self.char_filter_scope = CHAR_SCOPE_FILES # Default to Files
        self._update_char_filter_scope_button_text()

        self.current_log_view = 'progress' # Reset to progress log view
        self._update_cookie_input_visibility(False) # Hide cookie text input on full reset
        if self.log_view_stack: self.log_view_stack.setCurrentIndex(0)
        if self.progress_log_label: self.progress_log_label.setText("📜 Progress Log:")

        self._handle_filter_mode_change(self.radio_all, True)
        self._handle_multithreading_toggle(self.use_multithreading_checkbox.isChecked())
        self.filter_character_list("")

        self.download_btn.setEnabled(True); self.cancel_btn.setEnabled(False)
        if self.reset_button: self.reset_button.setEnabled(True)
        # self.basic_log_mode is False after reset, so Full Log is active
        if self.log_verbosity_toggle_button: # Reset eye button to show Progress Log
            self.log_verbosity_toggle_button.setText(self.EYE_ICON)
            self.log_verbosity_toggle_button.setToolTip("Current View: Progress Log. Click to switch to Missed Character Log.")
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

    def _update_multipart_toggle_button_text(self):
        if hasattr(self, 'multipart_toggle_button'):
            text = "Multi-part: ON" if self.allow_multipart_download_setting else "Multi-part: OFF"
            self.multipart_toggle_button.setText(text)
            if self.allow_multipart_download_setting:
                self.multipart_toggle_button.setToolTip(
                    "Multi-part Download: ON\n\n"
                    "Enables downloading large files in multiple segments (parts) simultaneously.\n"
                    "- Can significantly speed up downloads for *single large files* (e.g., videos, large archives) if the server supports it.\n"
                    "- May increase CPU/network usage.\n"
                    "- For creator feeds with many *small files* (e.g., images), this might not offer speed benefits and could make the UI/log feel busy.\n"
                    "- If a multi-part download fails for a file, it will automatically retry with a single stream.\n"
                    "- Example: A 500MB video might be downloaded in 5 parts of 100MB each, concurrently.\n\n"
                    "Click to turn OFF (use single-stream for all files)."
                )
            else:
                self.multipart_toggle_button.setToolTip(
                    "Multi-part Download: OFF\n\n"
                    "All files will be downloaded using a single connection (stream).\n"
                    "- This is generally stable and works well for most scenarios, especially for feeds with many smaller files.\n"
                    "- Large files will be downloaded sequentially in one go.\n"
                    "- Example: A 500MB video will be downloaded as one continuous stream.\n\n"
                    "Click to turn ON (enable multi-part for large files, see advisory on click)."
                )

    def _toggle_multipart_mode(self):
        # If currently OFF, and user is trying to turn it ON
        if not self.allow_multipart_download_setting:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Multi-part Download Advisory")
            msg_box.setText(
                "<b>Multi-part download advisory:</b><br><br>"
                "<ul>"
                "<li>Best suited for <b>large files</b> (e.g., single post videos).</li>"
                "<li>When downloading a full creator feed with many small files (like images):"
                "<ul><li>May not offer significant speed benefits.</li>"
                "<li>Could potentially make the UI feel <b>choppy</b>.</li>"
                "<li>May <b>spam the process log</b> with rapid, numerous small download messages.</li></ul></li>"
                "<li>Consider using the <b>'Videos' filter</b> if downloading a creator feed to primarily target large files for multi-part.</li>"
                "</ul><br>"
                "Do you want to enable multi-part download?"
            )
            proceed_button = msg_box.addButton("Proceed Anyway", QMessageBox.AcceptRole)
            cancel_button = msg_box.addButton("Cancel", QMessageBox.RejectRole)
            msg_box.setDefaultButton(proceed_button) # Default to Proceed
            msg_box.exec_()

            if msg_box.clickedButton() == cancel_button:
                # User cancelled, so don't change the setting (it's already False)
                self.log_signal.emit("ℹ️ Multi-part download enabling cancelled by user.")
                return # Exit without changing the state or button text
        
        self.allow_multipart_download_setting = not self.allow_multipart_download_setting # Toggle the actual setting
        self._update_multipart_toggle_button_text()
        self.settings.setValue(ALLOW_MULTIPART_DOWNLOAD_KEY, self.allow_multipart_download_setting)
        self.log_signal.emit(f"ℹ️ Multi-part download set to: {'Enabled' if self.allow_multipart_download_setting else 'Disabled'}")

    def _open_known_txt_file(self):
        if not os.path.exists(self.config_file):
            QMessageBox.warning(self, "File Not Found",
                                f"The file 'Known.txt' was not found at:\n{self.config_file}\n\n"
                                "It will be created automatically when you add a known name or close the application.")
            self.log_signal.emit(f"ℹ️ 'Known.txt' not found at {self.config_file}. It will be created later.")
            return

        try:
            if sys.platform == "win32":
                os.startfile(self.config_file)
            elif sys.platform == "darwin":  # macOS
                subprocess.call(['open', self.config_file])
            else:  # Linux and other Unix-like
                subprocess.call(['xdg-open', self.config_file])
            self.log_signal.emit(f"ℹ️ Attempted to open '{os.path.basename(self.config_file)}' with the default editor.")
        except FileNotFoundError: # Should be caught by os.path.exists, but as a fallback
            QMessageBox.critical(self, "Error", f"Could not find '{os.path.basename(self.config_file)}' at {self.config_file} to open it.")
            self.log_signal.emit(f"❌ Error: '{os.path.basename(self.config_file)}' not found at {self.config_file} when trying to open.")
        except Exception as e:
            QMessageBox.critical(self, "Error Opening File", f"Could not open '{os.path.basename(self.config_file)}':\n{e}")
            self.log_signal.emit(f"❌ Error opening '{os.path.basename(self.config_file)}': {e}")

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

        # --- Calculate initial window size based on screen dimensions ---
        primary_screen = QApplication.primaryScreen()
        if not primary_screen:
            screens = QApplication.screens()
            if not screens:
                # Absolute fallback if no screen information is available
                downloader_app_instance.resize(1024, 768)
                downloader_app_instance.show()
                sys.exit(qt_app.exec_())
            primary_screen = screens[0]

        available_geo = primary_screen.availableGeometry()
        screen_width = available_geo.width()
        screen_height = available_geo.height()

        # Define desired size relative to screen and minimums
        min_app_width = 960    # Minimum width for the app to be usable
        min_app_height = 680   # Minimum height
        desired_app_width_ratio = 0.80  # Use 80% of available screen width
        desired_app_height_ratio = 0.85 # Use 85% of available screen height

        app_width = max(min_app_width, int(screen_width * desired_app_width_ratio))
        app_height = max(min_app_height, int(screen_height * desired_app_height_ratio))

        # Ensure the calculated size doesn't exceed the available screen space
        app_width = min(app_width, screen_width)
        app_height = min(app_height, screen_height)
        
        downloader_app_instance.resize(app_width, app_height)
        downloader_app_instance.show()
        downloader_app_instance._center_on_screen()

        # TourDialog is now defined in this file, so we can call it directly.
        try:
            tour_result = TourDialog.run_tour_if_needed(downloader_app_instance)
            if tour_result == QDialog.Accepted: print("Tour completed by user.")
            elif tour_result == QDialog.Rejected: print("Tour skipped or was already shown.")
        except NameError:
            print("[Main] TourDialog class not found. Skipping tour.") # Should not happen if code is correct
        except Exception as e_tour:
            print(f"[Main] Error during tour execution: {e_tour}")

        exit_code = qt_app.exec_()
        print(f"Application finished with exit code: {exit_code}")
        sys.exit(exit_code)
    except SystemExit: pass
    except Exception as e:
        print("--- CRITICAL APPLICATION ERROR ---")
        print(f"An unhandled exception occurred: {e}")
        traceback.print_exc()
        print("--- END CRITICAL ERROR ---")
