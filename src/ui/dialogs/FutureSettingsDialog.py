# --- Standard Library Imports ---
import os

# --- PyQt5 Imports ---
from PyQt5.QtCore import Qt, QStandardPaths
from PyQt5.QtWidgets import (
    QApplication, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
    QGroupBox, QComboBox, QMessageBox
)

# --- Local Application Imports ---
# This assumes the new project structure is in place.
from ...i18n.translator import get_translation
from ...utils.resolution import get_dark_theme
from ..main_window import get_app_icon_object
from ...config.constants import (
    THEME_KEY, LANGUAGE_KEY, DOWNLOAD_LOCATION_KEY
)


class FutureSettingsDialog(QDialog):
    """
    A dialog for managing application-wide settings like theme, language,
    and saving the default download path.
    """
    def __init__(self, parent_app_ref, parent=None):
        """
        Initializes the dialog.

        Args:
            parent_app_ref (DownloaderApp): A reference to the main application window.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.parent_app = parent_app_ref
        self.setModal(True)

        # --- Basic Window Setup ---
        app_icon = get_app_icon_object()
        if app_icon and not app_icon.isNull():
            self.setWindowIcon(app_icon)
        
        # Set window size dynamically
        screen_height = QApplication.primaryScreen().availableGeometry().height() if QApplication.primaryScreen() else 768
        scale_factor = screen_height / 768.0
        base_min_w, base_min_h = 380, 250
        scaled_min_w = int(base_min_w * scale_factor)
        scaled_min_h = int(base_min_h * scale_factor)
        self.setMinimumSize(scaled_min_w, scaled_min_h)

        # --- Initialize UI and Apply Theming ---
        self._init_ui()
        self._retranslate_ui()
        self._apply_theme()

    def _init_ui(self):
        """Initializes all UI components and layouts for the dialog."""
        layout = QVBoxLayout(self)

        # --- Appearance Settings ---
        self.appearance_group_box = QGroupBox()
        appearance_layout = QVBoxLayout(self.appearance_group_box)
        self.theme_toggle_button = QPushButton()
        self.theme_toggle_button.clicked.connect(self._toggle_theme)
        appearance_layout.addWidget(self.theme_toggle_button)
        layout.addWidget(self.appearance_group_box)

        # --- Language Settings ---
        self.language_group_box = QGroupBox()
        language_group_layout = QVBoxLayout(self.language_group_box)
        self.language_selection_layout = QHBoxLayout()
        self.language_label = QLabel()
        self.language_selection_layout.addWidget(self.language_label)
        self.language_combo_box = QComboBox()
        self.language_combo_box.currentIndexChanged.connect(self._language_selection_changed)
        self.language_selection_layout.addWidget(self.language_combo_box, 1)
        language_group_layout.addLayout(self.language_selection_layout)
        layout.addWidget(self.language_group_box)
        
        # --- Download Settings ---
        self.download_settings_group_box = QGroupBox()
        download_settings_layout = QVBoxLayout(self.download_settings_group_box)
        self.save_path_button = QPushButton()
        self.save_path_button.clicked.connect(self._save_download_path)
        download_settings_layout.addWidget(self.save_path_button)
        layout.addWidget(self.download_settings_group_box)

        layout.addStretch(1)

        # --- OK Button ---
        self.ok_button = QPushButton()
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button, 0, Qt.AlignRight | Qt.AlignBottom)

    def _tr(self, key, default_text=""):
        """Helper to get translation based on the main application's current language."""
        if callable(get_translation) and self.parent_app:
            return get_translation(self.parent_app.current_selected_language, key, default_text)
        return default_text

    def _retranslate_ui(self):
        """Sets the text for all translatable UI elements."""
        self.setWindowTitle(self._tr("settings_dialog_title", "Settings"))
        self.appearance_group_box.setTitle(self._tr("appearance_group_title", "Appearance"))
        self.language_group_box.setTitle(self._tr("language_group_title", "Language Settings"))
        self.download_settings_group_box.setTitle(self._tr("settings_download_group_title", "Download Settings"))
        self.language_label.setText(self._tr("language_label", "Language:"))
        self._update_theme_toggle_button_text()
        self._populate_language_combo_box()
        
        self.save_path_button.setText(self._tr("settings_save_path_button", "Save Current Download Path"))
        self.save_path_button.setToolTip(self._tr("settings_save_path_tooltip", "Save the current 'Download Location' for future sessions."))
        self.ok_button.setText(self._tr("ok_button", "OK"))

    def _apply_theme(self):
        """Applies the current theme from the parent application."""
        if self.parent_app and self.parent_app.current_theme == "dark":
            scale = getattr(self.parent_app, 'scale_factor', 1)
            self.setStyleSheet(get_dark_theme(scale))
        else:
            self.setStyleSheet("")

    def _update_theme_toggle_button_text(self):
        """Updates the theme button text and tooltip based on the current theme."""
        if self.parent_app.current_theme == "dark":
            self.theme_toggle_button.setText(self._tr("theme_toggle_light", "Switch to Light Mode"))
            self.theme_toggle_button.setToolTip(self._tr("theme_tooltip_light", "Change the application appearance to light."))
        else:
            self.theme_toggle_button.setText(self._tr("theme_toggle_dark", "Switch to Dark Mode"))
            self.theme_toggle_button.setToolTip(self._tr("theme_tooltip_dark", "Change the application appearance to dark."))

    def _toggle_theme(self):
        """Toggles the application theme and updates the UI."""
        new_theme = "light" if self.parent_app.current_theme == "dark" else "dark"
        self.parent_app.apply_theme(new_theme)
        self._retranslate_ui()
        self._apply_theme()

    def _populate_language_combo_box(self):
        """Populates the language dropdown with available languages."""
        self.language_combo_box.blockSignals(True)
        self.language_combo_box.clear()
        languages = [
        ("en","English"),
        ("ja","日本語 (Japanese)"),
        ("fr","Français (French)"),
        ("de","Deutsch (German)"),
        ("es","Español (Spanish)"),
        ("pt","Português (Portuguese)"),
        ("ru","Русский (Russian)"),
        ("zh_CN","简体中文 (Simplified Chinese)"),
        ("zh_TW","繁體中文 (Traditional Chinese)"),
        ("ko","한국어 (Korean)")
        ]
        for lang_code, lang_name in languages:
            self.language_combo_box.addItem(lang_name, lang_code)
            if self.parent_app.current_selected_language == lang_code:
                self.language_combo_box.setCurrentIndex(self.language_combo_box.count() - 1)
        self.language_combo_box.blockSignals(False)

    def _language_selection_changed(self, index):
        """Handles the user selecting a new language."""
        selected_lang_code = self.language_combo_box.itemData(index)
        if selected_lang_code and selected_lang_code != self.parent_app.current_selected_language:
            self.parent_app.current_selected_language = selected_lang_code
            self.parent_app.settings.setValue(LANGUAGE_KEY, selected_lang_code)
            self.parent_app.settings.sync()
            
            self._retranslate_ui()

            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle(self._tr("language_change_title", "Language Changed"))
            msg_box.setText(self._tr("language_change_message", "A restart is required..."))
            msg_box.setInformativeText(self._tr("language_change_informative", "Would you like to restart now?"))
            restart_button = msg_box.addButton(self._tr("restart_now_button", "Restart Now"), QMessageBox.ApplyRole)
            ok_button = msg_box.addButton(self._tr("ok_button", "OK"), QMessageBox.AcceptRole)
            msg_box.setDefaultButton(ok_button)
            msg_box.exec_()

            if msg_box.clickedButton() == restart_button:
                self.parent_app._request_restart_application()

    def _save_download_path(self):
        """Saves the current download path from the main window to settings."""
        if hasattr(self.parent_app, 'dir_input') and self.parent_app.dir_input:
            current_path = self.parent_app.dir_input.text().strip()
            if current_path:
                if os.path.isdir(current_path):
                    self.parent_app.settings.setValue(DOWNLOAD_LOCATION_KEY, current_path)
                    self.parent_app.settings.sync()
                    QMessageBox.information(self,
                        self._tr("settings_save_path_success_title", "Path Saved"),
                        self._tr("settings_save_path_success_message", "Download location '{path}' saved.").format(path=current_path))
                else:
                    QMessageBox.warning(self,
                        self._tr("settings_save_path_invalid_title", "Invalid Path"),
                        self._tr("settings_save_path_invalid_message", "The path '{path}' is not a valid directory.").format(path=current_path))
            else:
                QMessageBox.warning(self,
                    self._tr("settings_save_path_empty_title", "Empty Path"),
                    self._tr("settings_save_path_empty_message", "Download location cannot be empty."))
        else:
            QMessageBox.critical(self, "Error", "Could not access download path input from main application.")
