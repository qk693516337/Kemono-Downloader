from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QGroupBox, QCheckBox, QHBoxLayout, QLabel,
    QLineEdit, QDialogButtonBox, QIntValidator
)
from PyQt5.QtCore import Qt

class MultipartDialog(QDialog):
    """
    A dialog for configuring multipart download settings.
    """
    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Multipart Download Options")
        self.setMinimumWidth(350)

        self.settings = current_settings

        # Main layout
        layout = QVBoxLayout(self)

        # File types group
        types_group = QGroupBox("Apply to File Types")
        types_layout = QVBoxLayout()
        self.videos_checkbox = QCheckBox("Videos")
        self.archives_checkbox = QCheckBox("Archives")
        types_layout.addWidget(self.videos_checkbox)
        types_layout.addWidget(self.archives_checkbox)
        types_group.setLayout(types_layout)
        layout.addWidget(types_group)

        # File size group
        size_group = QGroupBox("Minimum File Size")
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Apply only if file size is over:"))
        self.min_size_input = QLineEdit()
        self.min_size_input.setValidator(QIntValidator(0, 99999))
        self.min_size_input.setFixedWidth(50)
        size_layout.addWidget(self.min_size_input)
        size_layout.addWidget(QLabel("MB"))
        size_layout.addStretch()
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)

        # Custom extensions group
        extensions_group = QGroupBox("Custom File Extensions")
        extensions_layout = QVBoxLayout()
        extensions_layout.addWidget(QLabel("Apply to these additional extensions (comma-separated):"))
        self.extensions_input = QLineEdit()
        self.extensions_input.setPlaceholderText("e.g., .psd, .blend, .mkv")
        extensions_layout.addWidget(self.extensions_input)
        extensions_group.setLayout(extensions_layout)
        layout.addWidget(extensions_group)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
        self._load_initial_settings()

    def _load_initial_settings(self):
        """Populates the dialog with the current settings."""
        self.videos_checkbox.setChecked(self.settings.get('apply_on_videos', False))
        self.archives_checkbox.setChecked(self.settings.get('apply_on_archives', False))
        self.min_size_input.setText(str(self.settings.get('min_size_mb', 200)))
        self.extensions_input.setText(", ".join(self.settings.get('custom_extensions', [])))

    def get_selected_options(self):
        """Returns the configured settings from the dialog."""
        custom_extensions_raw = self.extensions_input.text().strip().lower()
        custom_extensions = {ext.strip() for ext in custom_extensions_raw.split(',') if ext.strip().startswith('.')}

        return {
            "enabled": True, # Implied if dialog is saved
            "apply_on_videos": self.videos_checkbox.isChecked(),
            "apply_on_archives": self.archives_checkbox.isChecked(),
            "min_size_mb": int(self.min_size_input.text()) if self.min_size_input.text().isdigit() else 200,
            "custom_extensions": sorted(list(custom_extensions))
        }
