# --- Standard Library Imports ---
import sys
import os
import time
import traceback

# --- PyQt5 Imports ---
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QCoreApplication

# --- Local Application Imports ---
# These imports reflect the new, organized project structure.
from src.ui.main_window import DownloaderApp
from src.ui.dialogs.TourDialog import TourDialog
from src.config.constants import CONFIG_ORGANIZATION_NAME, CONFIG_APP_NAME_MAIN


def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """
    Handles uncaught exceptions by logging them to a file for easier debugging,
    especially for bundled applications.
    """
    # Determine the base directory for logging
    if getattr(sys, 'frozen', False):
        base_dir_for_log = os.path.dirname(sys.executable)
    else:
        base_dir_for_log = os.path.dirname(os.path.abspath(__file__))

    log_dir = os.path.join(base_dir_for_log, "logs")
    log_file_path = os.path.join(log_dir, "uncaught_exceptions.log")

    try:
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
            f.write("-" * 80 + "\n\n")
    except Exception as log_ex:
        # Fallback to stderr if logging to file fails
        print(f"CRITICAL: Failed to write to uncaught_exceptions.log: {log_ex}", file=sys.stderr)
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
    
    # Also call the default excepthook
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def main():
    """Main entry point for the Kemono Downloader application."""
    
    # Set up global exception handling
    sys.excepthook = handle_uncaught_exception

    try:
        # Set up application metadata for QSettings
        QCoreApplication.setOrganizationName(CONFIG_ORGANIZATION_NAME)
        QCoreApplication.setApplicationName(CONFIG_APP_NAME_MAIN)
        
        qt_app = QApplication(sys.argv)

        # Create the main application window from its new module
        downloader_app_instance = DownloaderApp()

        # --- Window Sizing and Positioning ---
        # Logic moved from the old main.py to set an appropriate initial size
        primary_screen = QApplication.primaryScreen()
        if not primary_screen:
            # Fallback for systems with no primary screen detected
            downloader_app_instance.resize(1024, 768)
        else:
            available_geo = primary_screen.availableGeometry()
            screen_width = available_geo.width()
            screen_height = available_geo.height()
            
            # Define minimums and desired ratios
            min_app_width, min_app_height = 960, 680
            desired_width_ratio, desired_height_ratio = 0.80, 0.85

            app_width = max(min_app_width, int(screen_width * desired_width_ratio))
            app_height = max(min_app_height, int(screen_height * desired_height_ratio))

            # Ensure the window is not larger than the screen
            app_width = min(app_width, screen_width)
            app_height = min(app_height, screen_height)
            
            downloader_app_instance.resize(app_width, app_height)

        # Show the main window and center it
        downloader_app_instance.show()
        if hasattr(downloader_app_instance, '_center_on_screen'):
            downloader_app_instance._center_on_screen()

        # --- First-Run Welcome Tour ---
        # Check if the tour should be shown and run it.
        # This static method call keeps the logic clean and contained.
        if TourDialog.should_show_tour():
            tour_dialog = TourDialog(parent_app=downloader_app_instance)
            tour_dialog.exec_()

        # --- Start Application ---
        exit_code = qt_app.exec_()
        print(f"Application finished with exit code: {exit_code}")
        sys.exit(exit_code)

    except SystemExit:
        # Allow sys.exit() to work as intended
        pass
    except Exception as e:
        print("--- CRITICAL APPLICATION STARTUP ERROR ---")
        print(f"An unhandled exception occurred during application startup: {e}")
        traceback.print_exc()
        print("--- END CRITICAL ERROR ---")


if __name__ == '__main__':
    main()
