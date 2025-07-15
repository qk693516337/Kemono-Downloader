# src/ui/dialogs/SupportDialog.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QFrame, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Assuming execution from project root, so we can import from utils
from ...utils.resolution import get_dark_theme

class SupportDialog(QDialog):
    """
    A dialog to show support and donation options.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.setWindowTitle("❤️ Support the Developer")
        self.setMinimumWidth(400)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title Label
        title_label = QLabel("Thank You for Your Support!")
        font = title_label.font()
        font.setPointSize(14)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Informational Text
        info_label = QLabel(
            "If you find this application useful, please consider supporting its development. "
            "Your contribution helps cover costs and encourages future updates and features."
        )
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Donation Options
        options_layout = QVBoxLayout()
        options_layout.setSpacing(10)

        # --- Ko-fi ---
        kofi_label = QLabel(
            '<a href="https://ko-fi.com/yuvi427183" style="color: #13C2C2; text-decoration: none;">'
            '☕ Buy me a Ko-fi'
            '</a>'
        )
        kofi_label.setOpenExternalLinks(True)
        kofi_label.setAlignment(Qt.AlignCenter)
        font.setPointSize(12)
        kofi_label.setFont(font)
        options_layout.addWidget(kofi_label)
        
        # --- GitHub Sponsors ---
        github_label = QLabel(
            '<a href="https://github.com/sponsors/Yuvi9587" style="color: #C9D1D9; text-decoration: none;">'
            '💜 Sponsor on GitHub'
            '</a>'
        )
        github_label.setOpenExternalLinks(True)
        github_label.setAlignment(Qt.AlignCenter)
        github_label.setFont(font)
        options_layout.addWidget(github_label)

        layout.addLayout(options_layout)

        # Close Button
        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)
        self._apply_theme()

    def _apply_theme(self):
        """Applies the current theme from the parent application."""
        if self.parent_app and hasattr(self.parent_app, 'current_theme') and self.parent_app.current_theme == "dark":
            scale = getattr(self.parent_app, 'scale_factor', 1)
            self.setStyleSheet(get_dark_theme(scale))
        else:
            self.setStyleSheet("")
