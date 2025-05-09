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
        layout.setContentsMargins(20, 20, 20, 20) # Padding around content
        layout.setSpacing(15) # Spacing between title and content

        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #E0E0E0; padding-bottom: 10px;")

        content_label = QLabel(content_text)
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignLeft) # Align text to the left for readability
        content_label.setTextFormat(Qt.RichText) 
        content_label.setStyleSheet("font-size: 12px; color: #C8C8C8; line-height: 1.6;") 

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
    TOUR_SHOWN_KEY = "neverShowTourAgainV2" 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings(self.CONFIG_ORGANIZATION_NAME, self.CONFIG_APP_NAME_TOUR)
        self.current_step = 0

        self.setWindowTitle("Welcome to Kemono Downloader!")
        self.setModal(True)
        self.setMinimumSize(520, 450) 
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
        self._center_on_screen() # Call method to center the dialog

    def _center_on_screen(self):
        """Centers the dialog on the screen."""
        try:
            # Get the geometry of the screen
            screen_geometry = QDesktopWidget().screenGeometry()
            # Get the geometry of the dialog
            dialog_geometry = self.frameGeometry()
            
            # Calculate the center point for the dialog
            center_point = screen_geometry.center()
            dialog_geometry.moveCenter(center_point)
            
            # Move the top-left point of the dialog to the calculated position
            self.move(dialog_geometry.topLeft())
            print(f"[Tour] Dialog centered at: {dialog_geometry.topLeft()}")
        except Exception as e:
            print(f"[Tour] Error centering dialog: {e}")


    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0) 
        main_layout.setSpacing(0)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1) 

        # --- Define Tour Steps ---
        step1_content = (
            "Hello! This quick tour will walk you through the main features of the Kemono Downloader. "
            "Our goal is to help you easily download content from Kemono and Coomer.<br><br>" 
            " • Use the <b>Next</b> and <b>Back</b> buttons to navigate.<br>"
            " • Click <b>Skip Tour</b> to close this guide at any time.<br>"
            " • Check <b>'Never show this tour again'</b> if you don't want to see this on future startups."
        )
        self.step1 = TourStepWidget("👋 Welcome!", step1_content)

        step2_content = (
            "Let's start with the basics for downloading:<br><br>"
            " • <b>🔗 Kemono Creator/Post URL:</b><br>"
            "   Paste the full web address (URL) of a creator's page (e.g., <i>https://kemono.su/patreon/user/12345</i>) "
            "or a specific post (e.g., <i>.../post/98765</i>). This tells the downloader where to look for content.<br><br>"
            " • <b>📁 Download Location:</b><br>"
            "   Click 'Browse...' to choose a folder on your computer where all downloaded files will be saved. "
            "It's important to select this before starting.<br><br>"
            " • <b>📄 Page Range (for Creator URLs only):</b><br>"
            "   If you're downloading from a creator's page, you can specify a range of pages to download (e.g., pages 2 to 5). "
            "Leave blank to try and download all pages. This is disabled if you enter a single post URL or use Manga Mode."
        )
        self.step2 = TourStepWidget("① Getting Started: URLs & Location", step2_content)

        step3_content = (
            "Refine what you download with these filters:<br><br>"
            " • <b>🎯 Filter by Character(s):</b><br>"
            "   Enter character names, separated by commas (e.g., <i>Tifa, Aerith</i>). "
            "If 'Separate Folders by Name/Title' is on, this helps sort files into folders. "
            "In Manga Mode, this filters posts by matching the post title. In Normal Mode, it filters individual files by their filename.<br><br>"
            " • <b>🚫 Skip Posts/Files with Words:</b><br>"
            "   Enter words, separated by commas (e.g., <i>WIP, sketch</i>). "
            "Files or posts containing these words in their name (or post title if 'Separate Folders' is off and not Manga Mode) will be skipped.<br><br>"
            " • <b>Filter Files (Radio Buttons):</b><br>"
            "   - <i>All:</i> Download all file types.<br>"
            "   - <i>Images/GIFs:</i> Only download common image formats and GIFs.<br>"
            "   - <i>Videos:</i> Only download common video formats.<br>"
            "   - <i>🔗 Only Links:</i> Don't download files; instead, extract and display any external links found in post descriptions (like Mega, Google Drive links). The log area will show these links."
        )
        self.step3 = TourStepWidget("② Filtering Your Downloads", step3_content)

        step4_content = (
            "More options to customize your downloads:<br><br>"
            " • <b>Skip .zip / Skip .rar:</b><br>"
            "   Check these to avoid downloading .zip or .rar archive files.<br><br>"
            " • <b>Download Thumbnails Only:</b><br>"
            "   If checked, only downloads the small preview images (thumbnails) instead of full-sized files. Useful for a quick overview.<br><br>"
            " • <b>Compress Large Images:</b><br>"
            "   If you have the 'Pillow' library installed, this will try to convert very large images (over 1.5MB) to a smaller WebP format to save space. If WebP isn't smaller, the original is kept.<br><br>"
            " • <b>🗄️ Custom Folder Name (Single Post Only):</b><br>"
            "   When downloading a single post URL and using subfolders, you can type a specific name here for that post's folder."
        )
        self.step4 = TourStepWidget("③ Fine-Tuning: Archives & Images", step4_content)
        
        step5_content = (
            "Organize your downloads and manage performance:<br><br>"
            " • <b>⚙️ Separate Folders by Name/Title:</b><br>"
            "   If checked, the downloader tries to create subfolders based on character names (if you used the Character Filter) or by deriving a name from the post title using your 'Known Shows/Characters' list.<br><br>"
            " • <b>Subfolder per Post:</b><br>"
            "   Only active if 'Separate Folders' is on. Creates an additional subfolder for <i>each individual post</i> inside the character/title folder, named like 'PostID_PostTitle'.<br><br>"
            " • <b>🚀 Use Multithreading (Threads):</b><br>"
            "   For creator pages, this can speed up downloads by processing multiple posts at once. For single post URLs, it always uses one thread. Be cautious with very high thread counts.<br><br>"
            " • <b>📖 Manga/Comic Mode (Creator URLs only):</b><br>"
            "   Downloads posts from oldest to newest. It also renames files based on the post title and an extracted or generated sequence number (e.g., <i>MangaTitle - 01.jpg, MangaTitle - 02.jpg</i>). Best used with a character filter matching the series title for correct naming.<br><br>"
            " • <b>🎭 Known Shows/Characters:</b><br>"
            "   Add names here (e.g., a game title, a character's full name). When 'Separate Folders' is on and no character filter is used, the app looks for these known names in post titles to create appropriate folders."
        )
        self.step5 = TourStepWidget("④ Organization & Performance", step5_content)

        step6_content = (
            "Monitoring and Controls:<br><br>"
            " • <b>📜 Progress Log / Extracted Links Log:</b><br>"
            "   This area shows detailed messages about the download process or lists extracted links if 'Only Links' mode is active.<br><br>"
            " • <b>Show External Links in Log (Checkbox):</b><br>"
            "   If checked (and not in 'Only Links' mode), a second log panel appears to show external links found in post descriptions.<br><br>"
            " • <b>Show Basic/Full Log (Button):</b><br>"
            "   Toggles the main log between showing all messages (Full) or only important ones (Basic).<br><br>"
            " • <b>🔄 Reset (Button):</b><br>"
            "   Clears all input fields and logs to their default state. Only works when no download is active.<br><br>"
            " • <b>⬇️ Start Download / ❌ Cancel (Buttons):</b><br>"
            "   Start begins the process. Cancel stops an ongoing download."
            "<br><br>You're ready to start downloading! Click <b>'Finish'</b>."
        )
        self.step6 = TourStepWidget("⑤ Logs & Final Controls", step6_content)


        self.tour_steps = [self.step1, self.step2, self.step3, self.step4, self.step5, self.step6]
        for step_widget in self.tour_steps:
            self.stacked_widget.addWidget(step_widget)

        bottom_controls_layout = QVBoxLayout() 
        bottom_controls_layout.setContentsMargins(15, 10, 15, 15)
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
            print(f"[Tour] '{self.TOUR_SHOWN_KEY}' setting updated to True.")
        else:
            print(f"[Tour] '{self.TOUR_SHOWN_KEY}' setting not set to True (checkbox was unchecked on exit).")


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
        print("[Tour] Attempting to run tour (run_tour_if_needed called)...")
        try:
            settings = QSettings(TourDialog.CONFIG_ORGANIZATION_NAME, TourDialog.CONFIG_APP_NAME_TOUR)
            never_show_again = settings.value(TourDialog.TOUR_SHOWN_KEY, False, type=bool) 
            print(f"[Tour] Current '{TourDialog.TOUR_SHOWN_KEY}' setting is: {never_show_again}")

            if never_show_again:
                print("[Tour] Skipping tour because 'Never show again' was previously selected.")
                return QDialog.Rejected 

            print("[Tour] 'Never show again' is False. Proceeding to create and show tour dialog.")
            tour_dialog = TourDialog(parent_app_window) # _center_on_screen is called in __init__
            print("[Tour] TourDialog instance created successfully.")
            
            result = tour_dialog.exec_() 
            print(f"[Tour] Tour dialog exec_() finished. Result code: {result} (Accepted={QDialog.Accepted}, Rejected={QDialog.Rejected})")
            return result
        except Exception as e:
            print(f"[Tour] CRITICAL ERROR in run_tour_if_needed: {e}")
            traceback.print_exc() 
            return QDialog.Rejected 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # print("[Tour Test] Resetting 'Never show again' flag for testing purposes.")
    # test_settings = QSettings(TourDialog.CONFIG_ORGANIZATION_NAME, TourDialog.CONFIG_APP_NAME_TOUR)
    # print(f"[Tour Test] Before reset, '{TourDialog.TOUR_SHOWN_KEY}' is: {test_settings.value(TourDialog.TOUR_SHOWN_KEY, False, type=bool)}")
    # test_settings.setValue(TourDialog.TOUR_SHOWN_KEY, False)
    # test_settings.sync() 
    # print(f"[Tour Test] After reset, '{TourDialog.TOUR_SHOWN_KEY}' is: {test_settings.value(TourDialog.TOUR_SHOWN_KEY, False, type=bool)}")

    print("[Tour Test] Running tour standalone...")
    result = TourDialog.run_tour_if_needed(None) 

    if result == QDialog.Accepted:
        print("[Tour Test] Tour dialog was accepted (Finished).")
    elif result == QDialog.Rejected:
        print("[Tour Test] Tour dialog was rejected (Skipped or previously set to 'Never show again').")
    
    final_settings = QSettings(TourDialog.CONFIG_ORGANIZATION_NAME, TourDialog.CONFIG_APP_NAME_TOUR)
    print(f"[Tour Test] Final state of '{TourDialog.TOUR_SHOWN_KEY}' in settings: {final_settings.value(TourDialog.TOUR_SHOWN_KEY, False, type=bool)}")

    sys.exit()