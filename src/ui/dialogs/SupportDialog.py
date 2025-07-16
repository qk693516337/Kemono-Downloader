# src/ui/dialogs/SupportDialog.py

# --- Standard Library Imports ---
import sys
import os

# --- PyQt5 Imports ---
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QFrame, QDialogButtonBox, QGridLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap

# --- Local Application Imports ---
from ...utils.resolution import get_dark_theme

# --- Helper function for robust asset loading ---
def get_asset_path(filename):
    """
    Gets the absolute path to a file in the assets folder,
    handling both development and frozen (PyInstaller) environments.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment from src/ui/dialogs/
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    return os.path.join(base_path, 'assets', filename)


class SupportDialog(QDialog):
    """
    A dialog to show support and donation options.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.setWindowTitle("❤️ Support the Developer")
        self.setMinimumWidth(450)

        self._init_ui()
        self._apply_theme()

    def _init_ui(self):
        """Initializes all UI components and layouts for the dialog."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        # Title Label
        title_label = QLabel("Thank You for Your Support!")
        font = title_label.font()
        font.setPointSize(14)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Informational Text
        info_label = QLabel(
            "If you find this application useful, please consider supporting its development. "
            "Your contribution helps cover costs and encourages future updates and features."
        )
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # --- Donation Options Layout (using a grid for icons and text) ---
        options_layout = QGridLayout()
        options_layout.setSpacing(18)
        options_layout.setColumnStretch(0, 1) # Add stretch to center the content horizontally
        options_layout.setColumnStretch(3, 1)

        link_font = self.font()
        link_font.setPointSize(12)
        link_font.setBold(True)
        
        scale = getattr(self.parent_app, 'scale_factor', 1.0)
        icon_size = int(32 * scale)

        # --- Ko-fi ---
        kofi_icon_label = QLabel()
        kofi_pixmap = QPixmap(get_asset_path("kofi.png"))
        if not kofi_pixmap.isNull():
            kofi_icon_label.setPixmap(kofi_pixmap.scaled(QSize(icon_size, icon_size), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        kofi_text_label = QLabel(
            '<a href="https://ko-fi.com/yuvi427183" style="color: #13C2C2; text-decoration: none;">'
            '☕ Buy me a Ko-fi'
            '</a>'
        )
        kofi_text_label.setOpenExternalLinks(True)
        kofi_text_label.setFont(link_font)
        
        options_layout.addWidget(kofi_icon_label, 0, 1, Qt.AlignRight | Qt.AlignVCenter)
        options_layout.addWidget(kofi_text_label, 0, 2, Qt.AlignLeft | Qt.AlignVCenter)

        # --- GitHub Sponsors ---
        github_icon_label = QLabel()
        github_pixmap = QPixmap(get_asset_path("github_sponsors.png"))
        if not github_pixmap.isNull():
            github_icon_label.setPixmap(github_pixmap.scaled(QSize(icon_size, icon_size), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        github_text_label = QLabel(
            '<a href="https://github.com/sponsors/Yuvi9587" style="color: #EA4AAA; text-decoration: none;">'
            '💜 Sponsor on GitHub'
            '</a>'
        )
        github_text_label.setOpenExternalLinks(True)
        github_text_label.setFont(link_font)

        options_layout.addWidget(github_icon_label, 1, 1, Qt.AlignRight | Qt.AlignVCenter)
        options_layout.addWidget(github_text_label, 1, 2, Qt.AlignLeft | Qt.AlignVCenter)

        # --- Buy Me a Coffee (New) ---
        bmac_icon_label = QLabel()
        bmac_pixmap = QPixmap(get_asset_path("bmac.png"))
        if not bmac_pixmap.isNull():
            bmac_icon_label.setPixmap(bmac_pixmap.scaled(QSize(icon_size, icon_size), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
        bmac_text_label = QLabel(
            '<a href="https://buymeacoffee.com/yuvi9587" style="color: #FFDD00; text-decoration: none;">'
            '🍺 Buy Me a Coffee'
            '</a>'
        )
        bmac_text_label.setOpenExternalLinks(True)
        bmac_text_label.setFont(link_font)
        
        options_layout.addWidget(bmac_icon_label, 2, 1, Qt.AlignRight | Qt.AlignVCenter)
        options_layout.addWidget(bmac_text_label, 2, 2, Qt.AlignLeft | Qt.AlignVCenter)

        main_layout.addLayout(options_layout)

        # Close Button
        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def _apply_theme(self):
        """Applies the current theme from the parent application."""
        if self.parent_app and hasattr(self.parent_app, 'current_theme') and self.parent_app.current_theme == "dark":
            scale = getattr(self.parent_app, 'scale_factor', 1)
            self.setStyleSheet(get_dark_theme(scale))
        else:
            self.setStyleSheet("")