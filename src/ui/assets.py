# --- Standard Library Imports ---
import os
import sys

# --- PyQt5 Imports ---
from PyQt5.QtGui import QIcon

# --- Asset Management ---

# This global variable will cache the icon so we don't have to load it from disk every time.
_app_icon_cache = None

def get_app_icon_object():
    """
    Loads and caches the application icon from the assets folder.
    This function is now centralized to prevent circular imports.

    Returns:
        QIcon: The application icon object.
    """
    global _app_icon_cache
    if _app_icon_cache and not _app_icon_cache.isNull():
        return _app_icon_cache

    # Declare a single variable to hold the base directory path.
    app_base_dir = ""
    
    # Determine the project's base directory, whether running from source or as a bundled app
    if getattr(sys, 'frozen', False):
        # The application is frozen (e.g., with PyInstaller).
        # The base directory is the one containing the executable.
        app_base_dir = os.path.dirname(sys.executable)
    else:
        # The application is running from a .py file.
        # This path navigates up from src/ui/assets.py to the project root.
        app_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    icon_path = os.path.join(app_base_dir, 'assets', 'Kemono.ico')
    
    if os.path.exists(icon_path):
        _app_icon_cache = QIcon(icon_path)
    else:
        # If the icon isn't found, especially in a frozen app, check the _MEIPASS directory as a fallback.
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            fallback_icon_path = os.path.join(sys._MEIPASS, 'assets', 'Kemono.ico')
            if os.path.exists(fallback_icon_path):
                _app_icon_cache = QIcon(fallback_icon_path)
                return _app_icon_cache
        
        print(f"Warning: Application icon not found at {icon_path}")
        _app_icon_cache = QIcon() # Return an empty icon as a fallback
        
    return _app_icon_cache