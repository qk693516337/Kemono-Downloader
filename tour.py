import sys
import traceback # Added for enhanced error reporting
from PyQt5.QtWidgets import (
    QApplication, QDialog, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QSpacerItem, QSizePolicy, QCheckBox, QDesktopWidget
)
from PyQt5.QtCore import Qt, QSettings, pyqtSignal

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

        content_label = QLabel(content_text)
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignLeft)
        content_label.setTextFormat(Qt.RichText)
        # Adjusted line-height for bullet point readability
        content_label.setStyleSheet("font-size: 11pt; color: #C8C8C8; line-height: 1.8;")

        layout.addWidget(title_label)
        layout.addWidget(content_label)
        layout.addStretch(1)

class TourDialog(QDialog):
    """
    A dialog that shows a multi-page tour to the user.
    Includes a "Never show again" checkbox.
    Uses QSettings to remember this preference.
    """
    tour_finished_normally = pyqtSignal()
    tour_skipped = pyqtSignal()

    CONFIG_ORGANIZATION_NAME = "KemonoDownloader"
    CONFIG_APP_NAME_TOUR = "ApplicationTour"
    TOUR_SHOWN_KEY = "neverShowTourAgainV3" # Updated key for new tour content

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
        try:
            screen_geometry = QDesktopWidget().screenGeometry()
            dialog_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            dialog_geometry.moveCenter(center_point)
            self.move(dialog_geometry.topLeft())
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
            "Hello! This quick tour will walk you through the main features of the Kemono Downloader."
            "<ul>"
            "<li>Our goal is to help you easily download content from Kemono and Coomer.</li>"
            "<li>Use the <b>Next</b> and <b>Back</b> buttons to navigate.</li>"
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
            "   If downloading from a creator's page, you can specify a range of pages (e.g., pages 2 to 5). "
            "Leave blank for all pages. This is disabled for single post URLs or when <b>Manga/Comic Mode</b> is active.</li>"
            "</ul>"
        )
        self.step2 = TourStepWidget("① Getting Started", step2_content)

        step3_content = (
            "Refine what you download with these filters:"
            "<ul>"
            "<li><b>🎯 Filter by Character(s):</b><br>"
            "   Enter character names, comma-separated (e.g., <i>Tifa, Aerith</i>). "
            "   <ul><li>In <b>Normal Mode</b>, this filters individual files by matching their filenames.</li>"
            "       <li>In <b>Manga/Comic Mode</b>, this filters entire posts by matching the post title. Useful for targeting specific series.</li>"
            "       <li>Also helps in folder naming if 'Separate Folders' is enabled.</li></ul></li><br>"
            "<li><b>🚫 Skip with Words:</b><br>"
            "   Enter words, comma-separated (e.g., <i>WIP, sketch, preview</i>). "
            "   The <b>Scope</b> button (next to this input) cycles how this filter applies:"
            "   <ul><li><i>Scope: Files:</i> Skips files if their names contain any of these words.</li>"
            "       <li><i>Scope: Posts:</i> Skips entire posts if their titles contain any of these words.</li>"
            "       <li><i>Scope: Both:</i> Applies both file and post title skipping.</li></ul></li><br>"
            "<li><b>Filter Files (Radio Buttons):</b> Choose what to download:"
            "   <ul>"
            "   <li><i>All:</i> Downloads all file types found.</li>"
            "   <li><i>Images/GIFs:</i> Only common image formats and GIFs.</li>"
            "   <li><i>Videos:</i> Only common video formats.</li>"
            "   <li><b><i>📦 Only Archives:</i></b> Exclusively downloads <b>.zip</b> and <b>.rar</b> files. When selected, 'Skip .zip' and 'Skip .rar' checkboxes are automatically disabled and unchecked.</li>"
            "   <li><i>🔗 Only Links:</i> Extracts and displays external links from post descriptions instead of downloading files.</li>"
            "   </ul></li>"
            "</ul>"
        )
        self.step3 = TourStepWidget("② Filtering Downloads", step3_content)

        step4_content = (
            "More options to customize your downloads:"
            "<ul>"
            "<li><b>Skip .zip / Skip .rar:</b> Check these to avoid downloading these archive file types. "
            "   <i>(Note: These are disabled and ignored if '📦 Only Archives' mode is selected).</i></li><br>"
            "<li><b>Download Thumbnails Only:</b> Downloads small preview images instead of full-sized files (if available).</li><br>"
            "<li><b>Compress Large Images:</b> If the 'Pillow' library is installed, images larger than 1.5MB will be converted to WebP format if the WebP version is significantly smaller.</li><br>"
            "<li><b>🗄️ Custom Folder Name (Single Post Only):</b><br>"
            "   If you are downloading a single specific post URL AND 'Separate Folders by Name/Title' is enabled, "
            "you can enter a custom name here for that post's download folder.</li>"
            "</ul>"
        )
        self.step4 = TourStepWidget("③ Fine-Tuning Downloads", step4_content)

        step5_content = (
            "Organize your downloads and manage performance:"
            "<ul>"
            "<li><b>⚙️ Separate Folders by Name/Title:</b> Creates subfolders based on the 'Filter by Character(s)' input or post titles (can use the 'Known Shows/Characters' list as a fallback for folder names).</li><br>"
            "<li><b>Subfolder per Post:</b> If 'Separate Folders' is on, this creates an additional subfolder for <i>each individual post</i> inside the main character/title folder.</li><br>"
            "<li><b>🚀 Use Multithreading (Threads):</b> Enables faster downloads for creator pages by processing multiple posts or files concurrently. The number of threads can be adjusted. Single post URLs are processed using a single thread for post data but can use multiple threads for file downloads within that post.</li><br>"
            "<li><b>📖 Manga/Comic Mode (Creator URLs only):</b> Tailored for sequential content."
            "   <ul>"
            "   <li>Downloads posts from <b>oldest to newest</b>.</li>"
            "   <li>The 'Page Range' input is disabled as all posts are fetched.</li>"
            "   <li>A <b>filename style toggle button</b> (e.g., 'Name: Post Title' or 'Name: Original File') appears in the top-right of the log area when this mode is active for a creator feed. Click it to change naming:"
            "       <ul>"
            "       <li><b><i>Name: Post Title (Default):</i></b> The first file in a post is named after the post's title (e.g., <i>MyMangaChapter1.jpg</i>). Subsequent files in the <i>same post</i> (if any) will retain their original filenames.</li>"
            "       <li><b><i>Name: Original File:</i></b> All files will attempt to keep their original filenames as provided by the site (e.g., <i>001.jpg, page_02.png</i>). You'll see a recommendation to use 'Post Title' style if you choose this.</li>"
            "       </ul>"
            "   </li>"
            "   <li>For best results with 'Name: Post Title' style, use the 'Filter by Character(s)' field with the manga/series title.</li>"
            "   </ul></li><br>"
            "<li><b>🎭 Known Shows/Characters:</b> Add names here (e.g., <i>Game Title, Series Name, Character Full Name</i>). These are used for automatic folder creation when 'Separate Folders' is on and no specific 'Filter by Character(s)' is provided for a post.</li>"
            "</ul>"
        )
        self.step5 = TourStepWidget("④ Organization & Performance", step5_content)

        step6_content = (
            "Monitoring and Controls:"
            "<ul>"
            "<li><b>📜 Progress Log / Extracted Links Log:</b> Shows detailed download messages. If '🔗 Only Links' mode is active, this area displays the extracted links.</li><br>"
            "<li><b>Show External Links in Log:</b> If checked, a secondary log panel appears below the main log to display any external links found in post descriptions. <i>(This is disabled if '🔗 Only Links' or '📦 Only Archives' mode is active).</i></li><br>"
            "<li><b>Log Verbosity (Show Basic/Full Log):</b> Toggles the main log between showing all messages (Full) or only key summaries, errors, and warnings (Basic).</li><br>"
            "<li><b>🔄 Reset:</b> Clears all input fields, logs, and resets temporary settings to their defaults. Can only be used when no download is active.</li><br>"
            "<li><b>⬇️ Start Download / ❌ Cancel:</b> These buttons initiate or stop the current download/extraction process.</li>"
            "</ul>"
            "<br>You're all set! Click <b>'Finish'</b> to close the tour and start using the downloader."
        )
        self.step6 = TourStepWidget("⑤ Logs & Final Controls", step6_content)


        self.tour_steps = [self.step1, self.step2, self.step3, self.step4, self.step5, self.step6]
        for step_widget in self.tour_steps:
            self.stacked_widget.addWidget(step_widget)

        bottom_controls_layout = QVBoxLayout()
        bottom_controls_layout.setContentsMargins(15, 10, 15, 15) # Adjusted margins
        bottom_controls_layout.setSpacing(10)

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
            never_show_again = settings.value(TourDialog.TOUR_SHOWN_KEY, False, type=bool)

            if never_show_again:
                return QDialog.Rejected

            tour_dialog = TourDialog(parent_app_window)
            result = tour_dialog.exec_()
            return result
        except Exception as e:
            print(f"[Tour] CRITICAL ERROR in run_tour_if_needed: {e}")
            traceback.print_exc()
            return QDialog.Rejected

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # --- For testing: force the tour to show by resetting the flag ---
    # print("[Tour Test] Resetting 'Never show again' flag for testing purposes.")
    # test_settings = QSettings(TourDialog.CONFIG_ORGANIZATION_NAME, TourDialog.CONFIG_APP_NAME_TOUR)
    # test_settings.setValue(TourDialog.TOUR_SHOWN_KEY, False) # Set to False to force tour
    # test_settings.sync()
    # --- End testing block ---

    print("[Tour Test] Running tour standalone...")
    result = TourDialog.run_tour_if_needed(None)

    if result == QDialog.Accepted:
        print("[Tour Test] Tour dialog was accepted (Finished).")
    elif result == QDialog.Rejected:
        print("[Tour Test] Tour dialog was rejected (Skipped or previously set to 'Never show again').")

    final_settings = QSettings(TourDialog.CONFIG_ORGANIZATION_NAME, TourDialog.CONFIG_APP_NAME_TOUR)
    print(f"[Tour Test] Final state of '{TourDialog.TOUR_SHOWN_KEY}' in settings: {final_settings.value(TourDialog.TOUR_SHOWN_KEY, False, type=bool)}")

    sys.exit()