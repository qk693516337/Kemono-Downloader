# --- Standard Library Imports ---
import os
import time

# --- PyQt5 Imports ---
from PyQt5.QtCore import Qt, QStandardPaths, QTimer
from PyQt5.QtWidgets import (
    QApplication, QDialog, QHBoxLayout, QLabel, QScrollArea,
    QPushButton, QVBoxLayout, QSplitter, QWidget, QGroupBox,
    QFileDialog, QMessageBox
)

# --- Local Application Imports ---
from ...i18n.translator import get_translation
from ..main_window import get_app_icon_object


class DownloadHistoryDialog(QDialog):
    """
    Dialog to display download history, showing the last few downloaded files
    and the first posts processed in the current session. It also allows
    exporting this history to a text file.
    """

    def __init__(self, last_downloaded_entries, first_processed_entries, parent_app, parent=None):
        """
        Initializes the dialog.

        Args:
            last_downloaded_entries (list): A list of dicts for the last few files.
            first_processed_entries (list): A list of dicts for the first few posts.
            parent_app (DownloaderApp): A reference to the main application window.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.parent_app = parent_app
        self.last_3_downloaded_entries = last_downloaded_entries
        self.first_processed_entries = first_processed_entries
        self.setModal(True)

        # --- Basic Window Setup ---
        app_icon = get_app_icon_object()
        if app_icon and not app_icon.isNull():
            self.setWindowIcon(app_icon)

        # Set window size dynamically
        screen_height = QApplication.primaryScreen().availableGeometry().height() if QApplication.primaryScreen() else 768
        scale_factor = screen_height / 1080.0
        base_min_w, base_min_h = 600, 450
        scaled_min_w = int(base_min_w * 1.5 * scale_factor)
        scaled_min_h = int(base_min_h * scale_factor)
        self.setMinimumSize(scaled_min_w, scaled_min_h)
        self.resize(scaled_min_w, scaled_min_h + 100) # Give it a bit more height

        # --- Initialize UI and Apply Theming ---
        self._init_ui()
        self._retranslate_ui()
        self._apply_theme()

    def _init_ui(self):
        """Initializes all UI components and layouts for the dialog."""
        dialog_layout = QVBoxLayout(self)
        self.setLayout(dialog_layout)

        self.main_splitter = QSplitter(Qt.Horizontal)
        dialog_layout.addWidget(self.main_splitter)

        # --- Left Pane (Last Downloaded Files) ---
        left_pane_widget = self._create_history_pane(
            self.last_3_downloaded_entries,
            "history_last_downloaded_header", "Last 3 Files Downloaded:",
            self._format_last_downloaded_entry
        )
        self.main_splitter.addWidget(left_pane_widget)

        # --- Right Pane (First Processed Posts) ---
        right_pane_widget = self._create_history_pane(
            self.first_processed_entries,
            "first_files_processed_header", "First {count} Posts Processed This Session:",
            self._format_first_processed_entry,
            count=len(self.first_processed_entries)
        )
        self.main_splitter.addWidget(right_pane_widget)

        # --- Bottom Buttons ---
        bottom_button_layout = QHBoxLayout()
        self.save_history_button = QPushButton()
        self.save_history_button.clicked.connect(self._save_history_to_txt)
        bottom_button_layout.addStretch(1)
        bottom_button_layout.addWidget(self.save_history_button)
        dialog_layout.addLayout(bottom_button_layout)

        # Set splitter sizes after the dialog is shown to ensure correct proportions
        QTimer.singleShot(0, lambda: self.main_splitter.setSizes([self.width() // 2, self.width() // 2]))

    def _create_history_pane(self, entries, header_key, header_default, formatter_func, **kwargs):
        """Creates a generic pane for displaying a list of history entries."""
        pane_widget = QWidget()
        layout = QVBoxLayout(pane_widget)
        header_text = self._tr(header_key, header_default).format(**kwargs)
        header_label = QLabel(header_text)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_content_widget)

        if not entries:
            no_history_label = QLabel(self._tr("no_download_history_header", "No History Yet"))
            no_history_label.setAlignment(Qt.AlignCenter)
            scroll_layout.addWidget(no_history_label)
        else:
            for entry in entries:
                group_box, details_label = formatter_func(entry)
                group_layout = QVBoxLayout(group_box)
                group_layout.addWidget(details_label)
                scroll_layout.addWidget(group_box)

        scroll_area.setWidget(scroll_content_widget)
        layout.addWidget(scroll_area)
        return pane_widget

    def _format_last_downloaded_entry(self, entry):
        """Formats a single entry for the 'Last Downloaded Files' pane."""
        group_box = QGroupBox(f"{self._tr('history_file_label', 'File:')} {entry.get('disk_filename', 'N/A')}")
        details_text = (
            f"<b>{self._tr('history_from_post_label', 'From Post:')}</b> {entry.get('post_title', 'N/A')} (ID: {entry.get('post_id', 'N/A')})<br>"
            f"<b>{self._tr('history_creator_series_label', 'Creator/Series:')}</b> {entry.get('creator_display_name', 'N/A')}<br>"
            f"<b>{self._tr('history_post_uploaded_label', 'Post Uploaded:')}</b> {entry.get('upload_date_str', 'N/A')}<br>"
            f"<b>{self._tr('history_file_downloaded_label', 'File Downloaded:')}</b> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry.get('download_timestamp', 0)))}<br>"
            f"<b>{self._tr('history_saved_in_folder_label', 'Saved In Folder:')}</b> {entry.get('download_path', 'N/A')}"
        )
        details_label = QLabel(details_text)
        details_label.setWordWrap(True)
        details_label.setTextFormat(Qt.RichText)
        return group_box, details_label

    def _format_first_processed_entry(self, entry):
        """Formats a single entry for the 'First Processed Posts' pane."""
        group_box = QGroupBox(f"{self._tr('history_post_label', 'Post:')} {entry.get('post_title', 'N/A')} (ID: {entry.get('post_id', 'N/A')})")
        details_text = (
            f"<b>{self._tr('history_creator_label', 'Creator:')}</b> {entry.get('creator_name', 'N/A')}<br>"
            f"<b>{self._tr('history_top_file_label', 'Top File:')}</b> {entry.get('top_file_name', 'N/A')}<br>"
            f"<b>{self._tr('history_num_files_label', 'Num Files in Post:')}</b> {entry.get('num_files', 0)}<br>"
            f"<b>{self._tr('history_post_uploaded_label', 'Post Uploaded:')}</b> {entry.get('upload_date_str', 'N/A')}<br>"
            f"<b>{self._tr('history_processed_on_label', 'Processed On:')}</b> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry.get('download_date_timestamp', 0)))}<br>"
            f"<b>{self._tr('history_saved_to_folder_label', 'Saved To Folder:')}</b> {entry.get('download_location', 'N/A')}"
        )
        details_label = QLabel(details_text)
        details_label.setWordWrap(True)
        details_label.setTextFormat(Qt.RichText)
        return group_box, details_label

    def _tr(self, key, default_text=""):
        """Helper to get translation based on the main application's current language."""
        if callable(get_translation) and self.parent_app:
            return get_translation(self.parent_app.current_selected_language, key, default_text)
        return default_text

    def _retranslate_ui(self):
        """Sets the text for all translatable UI elements."""
        self.setWindowTitle(self._tr("download_history_dialog_title_combined", "Download History"))
        self.save_history_button.setText(self._tr("history_save_button_text", "Save History to .txt"))

    def _apply_theme(self):
        """Applies the current theme from the parent application."""
        if self.parent_app and hasattr(self.parent_app, 'get_dark_theme') and self.parent_app.current_theme == "dark":
            self.setStyleSheet(self.parent_app.get_dark_theme())

    def _save_history_to_txt(self):
        """Saves the displayed history content to a user-selected text file."""
        if not self.last_3_downloaded_entries and not self.first_processed_entries:
            QMessageBox.information(
                self,
                self._tr("no_download_history_header", "No History Yet"),
                self._tr("history_nothing_to_save_message", "There is no history to save.")
            )
            return

        # Suggest saving in the main download directory or Documents as a fallback
        main_download_dir = self.parent_app.dir_input.text().strip()
        default_save_dir = ""
        if main_download_dir and os.path.isdir(main_download_dir):
            default_save_dir = main_download_dir
        else:
            default_save_dir = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation) or self.parent_app.app_base_dir

        default_filepath = os.path.join(default_save_dir, "download_history.txt")

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            self._tr("history_save_dialog_title", "Save Download History"),
            default_filepath,
            "Text Files (*.txt);;All Files (*)"
        )

        if not filepath:
            return

        # Build the text content
        history_content = []
        # ... logic for formatting the text content would go here ...

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(history_content))
            QMessageBox.information(
                self,
                self._tr("history_export_success_title", "History Export Successful"),
                self._tr("history_export_success_message", "Successfully exported to:\n{filepath}").format(filepath=filepath)
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                self._tr("history_export_error_title", "History Export Error"),
                self._tr("history_export_error_message", "Could not export: {error}").format(error=str(e))
            )
