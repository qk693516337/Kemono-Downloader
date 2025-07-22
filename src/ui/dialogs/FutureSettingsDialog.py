# --- Standard Library Imports ---
import os
import json

# --- PyQt5 Imports ---
from PyQt5.QtCore import Qt, QStandardPaths
from PyQt5.QtWidgets import (
    QApplication, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
    QGroupBox, QComboBox, QMessageBox, QGridLayout, QCheckBox
)

# --- Local Application Imports ---
from ...i18n.translator import get_translation
from ...utils.resolution import get_dark_theme
from ..main_window import get_app_icon_object
from ...config.constants import (
    THEME_KEY, LANGUAGE_KEY, DOWNLOAD_LOCATION_KEY,
    RESOLUTION_KEY, UI_SCALE_KEY, SAVE_CREATOR_JSON_KEY 
)


class FutureSettingsDialog(QDialog):
    """
    A dialog for managing application-wide settings like theme, language,
    and display options, with an organized layout.
    """
    def __init__(self, parent_app_ref, parent=None):
        super().__init__(parent)
        self.parent_app = parent_app_ref
        self.setModal(True)

        app_icon = get_app_icon_object()
        if app_icon and not app_icon.isNull():
            self.setWindowIcon(app_icon)

        screen_height = QApplication.primaryScreen().availableGeometry().height() if QApplication.primaryScreen() else 800
        scale_factor = screen_height / 800.0
        base_min_w, base_min_h = 420, 360 # Adjusted height for new layout
        scaled_min_w = int(base_min_w * scale_factor)
        scaled_min_h = int(base_min_h * scale_factor)
        self.setMinimumSize(scaled_min_w, scaled_min_h)

        self._init_ui()
        self._retranslate_ui()
        self._apply_theme()

    def _init_ui(self):
        """Initializes all UI components and layouts for the dialog."""
        main_layout = QVBoxLayout(self)

        # --- Group 1: Interface Settings ---
        self.interface_group_box = QGroupBox()
        interface_layout = QGridLayout(self.interface_group_box)

        # Theme
        self.theme_label = QLabel()
        self.theme_toggle_button = QPushButton()
        self.theme_toggle_button.clicked.connect(self._toggle_theme)
        interface_layout.addWidget(self.theme_label, 0, 0)
        interface_layout.addWidget(self.theme_toggle_button, 0, 1)

        # UI Scale
        self.ui_scale_label = QLabel()
        self.ui_scale_combo_box = QComboBox()
        self.ui_scale_combo_box.currentIndexChanged.connect(self._display_setting_changed)
        interface_layout.addWidget(self.ui_scale_label, 1, 0)
        interface_layout.addWidget(self.ui_scale_combo_box, 1, 1)
        
        # Language
        self.language_label = QLabel()
        self.language_combo_box = QComboBox()
        self.language_combo_box.currentIndexChanged.connect(self._language_selection_changed)
        interface_layout.addWidget(self.language_label, 2, 0)
        interface_layout.addWidget(self.language_combo_box, 2, 1)

        main_layout.addWidget(self.interface_group_box)

        # --- Group 2: Download & Window Settings ---
        self.download_window_group_box = QGroupBox()
        download_window_layout = QGridLayout(self.download_window_group_box)

        # Window Size (Resolution)
        self.window_size_label = QLabel()
        self.resolution_combo_box = QComboBox()
        self.resolution_combo_box.currentIndexChanged.connect(self._display_setting_changed)
        download_window_layout.addWidget(self.window_size_label, 0, 0)
        download_window_layout.addWidget(self.resolution_combo_box, 0, 1)

        # Default Path
        self.default_path_label = QLabel()
        self.save_path_button = QPushButton()
        self.save_path_button.clicked.connect(self._save_download_path)
        download_window_layout.addWidget(self.default_path_label, 1, 0)
        download_window_layout.addWidget(self.save_path_button, 1, 1)

        # Save Creator.json Checkbox
        self.save_creator_json_checkbox = QCheckBox()
        self.save_creator_json_checkbox.stateChanged.connect(self._creator_json_setting_changed) 
        download_window_layout.addWidget(self.save_creator_json_checkbox, 2, 0, 1, 2)

        main_layout.addWidget(self.download_window_group_box)

        main_layout.addStretch(1)

        # --- OK Button ---
        self.ok_button = QPushButton()
        self.ok_button.clicked.connect(self.accept)
        main_layout.addWidget(self.ok_button, 0, Qt.AlignRight | Qt.AlignBottom)

    def _load_checkbox_states(self):
        """Loads the initial state for all checkboxes from settings."""
        self.save_creator_json_checkbox.blockSignals(True)
        # Default to True so the feature is on by default for users
        should_save = self.parent_app.settings.value(SAVE_CREATOR_JSON_KEY, True, type=bool)
        self.save_creator_json_checkbox.setChecked(should_save)
        self.save_creator_json_checkbox.blockSignals(False)

    def _creator_json_setting_changed(self, state):
        """Saves the state of the 'Save Creator.json' checkbox."""
        is_checked = state == Qt.Checked
        self.parent_app.settings.setValue(SAVE_CREATOR_JSON_KEY, is_checked)
        self.parent_app.settings.sync()

    def _tr(self, key, default_text=""):
        if callable(get_translation) and self.parent_app:
            return get_translation(self.parent_app.current_selected_language, key, default_text)
        return default_text

    def _retranslate_ui(self):
        self.setWindowTitle(self._tr("settings_dialog_title", "Settings"))
        
        # Group Box Titles
        self.interface_group_box.setTitle(self._tr("interface_group_title", "Interface Settings"))
        self.download_window_group_box.setTitle(self._tr("download_window_group_title", "Download & Window Settings"))

        # Interface Group Labels
        self.theme_label.setText(self._tr("theme_label", "Theme:"))
        self.ui_scale_label.setText(self._tr("ui_scale_label", "UI Scale:"))
        self.language_label.setText(self._tr("language_label", "Language:"))
        
        # Download & Window Group Labels
        self.window_size_label.setText(self._tr("window_size_label", "Window Size:"))
        self.default_path_label.setText(self._tr("default_path_label", "Default Path:"))
        self.save_creator_json_checkbox.setText(self._tr("save_creator_json_label", "Save Creator.json file"))
        
        # Buttons and Controls
        self._update_theme_toggle_button_text()
        self.save_path_button.setText(self._tr("settings_save_path_button", "Save Current Download Path"))
        self.save_path_button.setToolTip(self._tr("settings_save_path_tooltip", "Save the current 'Download Location' for future sessions."))
        self.ok_button.setText(self._tr("ok_button", "OK"))

        # Populate dropdowns
        self._populate_display_combo_boxes()
        self._populate_language_combo_box()
        self._load_checkbox_states()

    def _apply_theme(self):
        if self.parent_app and self.parent_app.current_theme == "dark":
            scale = getattr(self.parent_app, 'scale_factor', 1)
            self.setStyleSheet(get_dark_theme(scale))
        else:
            self.setStyleSheet("")

    def _update_theme_toggle_button_text(self):
        if self.parent_app.current_theme == "dark":
            self.theme_toggle_button.setText(self._tr("theme_toggle_light", "Switch to Light Mode"))
        else:
            self.theme_toggle_button.setText(self._tr("theme_toggle_dark", "Switch to Dark Mode"))

    def _toggle_theme(self):
        new_theme = "light" if self.parent_app.current_theme == "dark" else "dark"
        self.parent_app.settings.setValue(THEME_KEY, new_theme)
        self.parent_app.settings.sync()
        self.parent_app.current_theme = new_theme
        self._apply_theme()
        if hasattr(self.parent_app, '_apply_theme_and_restart_prompt'):
            self.parent_app._apply_theme_and_restart_prompt()

    def _populate_display_combo_boxes(self):
        self.resolution_combo_box.blockSignals(True)
        self.resolution_combo_box.clear()
        resolutions = [
            ("Auto", self._tr("auto_resolution", "Auto (System Default)")),
            ("1280x720", "1280 x 720"),
            ("1600x900", "1600 x 900"),
            ("1920x1080", "1920 x 1080 (Full HD)"),
            ("2560x1440", "2560 x 1440 (2K)"),
            ("3840x2160", "3840 x 2160 (4K)")
        ]
        current_res = self.parent_app.settings.value(RESOLUTION_KEY, "Auto")
        for res_key, res_name in resolutions:
            self.resolution_combo_box.addItem(res_name, res_key)
            if current_res == res_key:
                self.resolution_combo_box.setCurrentIndex(self.resolution_combo_box.count() - 1)
        self.resolution_combo_box.blockSignals(False)

        self.ui_scale_combo_box.blockSignals(True)
        self.ui_scale_combo_box.clear()
        scales = [
            (0.5, "50%"),
            (0.7, "70%"),
            (0.9, "90%"),
            (1.0, "100% (Default)"),
            (1.25, "125%"),
            (1.50, "150%"),
            (1.75, "175%"),
            (2.0, "200%")
        ]

        current_scale = float(self.parent_app.settings.value(UI_SCALE_KEY, 1.0))
        for scale_val, scale_name in scales:
            self.ui_scale_combo_box.addItem(scale_name, scale_val)
            if abs(current_scale - scale_val) < 0.01:
                self.ui_scale_combo_box.setCurrentIndex(self.ui_scale_combo_box.count() - 1)
        self.ui_scale_combo_box.blockSignals(False)

    def _display_setting_changed(self):
        selected_res = self.resolution_combo_box.currentData()
        selected_scale = self.ui_scale_combo_box.currentData()

        self.parent_app.settings.setValue(RESOLUTION_KEY, selected_res)
        self.parent_app.settings.setValue(UI_SCALE_KEY, selected_scale)
        self.parent_app.settings.sync()

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(self._tr("display_change_title", "Display Settings Changed"))
        msg_box.setText(self._tr("language_change_message", "A restart is required for these changes to take effect."))
        msg_box.setInformativeText(self._tr("language_change_informative", "Would you like to restart now?"))
        restart_button = msg_box.addButton(self._tr("restart_now_button", "Restart Now"), QMessageBox.ApplyRole)
        ok_button = msg_box.addButton(self._tr("ok_button", "OK"), QMessageBox.AcceptRole)
        msg_box.setDefaultButton(ok_button)
        msg_box.exec_()

        if msg_box.clickedButton() == restart_button:
            self.parent_app._request_restart_application()

    def _populate_language_combo_box(self):
        self.language_combo_box.blockSignals(True)
        self.language_combo_box.clear()
        languages = [
            ("en", "English"), ("ja", "日本語 (Japanese)"), ("fr", "Français (French)"),
            ("de", "Deutsch (German)"), ("es", "Español (Spanish)"), ("pt", "Português (Portuguese)"),
            ("ru", "Русский (Russian)"), ("zh_CN", "简体中文 (Simplified Chinese)"),
            ("zh_TW", "繁體中文 (Traditional Chinese)"), ("ko", "한국어 (Korean)")
        ]
        current_lang = self.parent_app.current_selected_language
        for lang_code, lang_name in languages:
            self.language_combo_box.addItem(lang_name, lang_code)
            if current_lang == lang_code:
                self.language_combo_box.setCurrentIndex(self.language_combo_box.count() - 1)
        self.language_combo_box.blockSignals(False)

    def _language_selection_changed(self, index):
        selected_lang_code = self.language_combo_box.itemData(index)
        if selected_lang_code and selected_lang_code != self.parent_app.current_selected_language:
            self.parent_app.settings.setValue(LANGUAGE_KEY, selected_lang_code)
            self.parent_app.settings.sync()
            self.parent_app.current_selected_language = selected_lang_code
            
            self._retranslate_ui()
            if hasattr(self.parent_app, '_retranslate_main_ui'):
                 self.parent_app._retranslate_main_ui()
            
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
        if hasattr(self.parent_app, 'dir_input') and self.parent_app.dir_input:
            current_path = self.parent_app.dir_input.text().strip()
            if current_path and os.path.isdir(current_path):
                self.parent_app.settings.setValue(DOWNLOAD_LOCATION_KEY, current_path)
                self.parent_app.settings.sync()
                QMessageBox.information(self,
                    self._tr("settings_save_path_success_title", "Path Saved"),
                    self._tr("settings_save_path_success_message", "Download location '{path}' saved.").format(path=current_path))
            elif not current_path:
                 QMessageBox.warning(self,
                    self._tr("settings_save_path_empty_title", "Empty Path"),
                    self._tr("settings_save_path_empty_message", "Download location cannot be empty."))
            else:
                QMessageBox.warning(self,
                    self._tr("settings_save_path_invalid_title", "Invalid Path"),
                    self._tr("settings_save_path_invalid_message", "The path '{path}' is not a valid directory.").format(path=current_path))
        else:
            QMessageBox.critical(self, "Error", "Could not access download path input from main application.")