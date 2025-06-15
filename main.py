import sys 
import os 
import time 
import requests 
import re 
import threading 
import json 
import queue 
import hashlib 
import http .client 
import traceback 
import html 
import subprocess 
import datetime # Import the datetime module
import random 
from collections import deque 
import unicodedata 
from concurrent .futures import ThreadPoolExecutor ,CancelledError ,Future 

from PyQt5 .QtGui import (
QIcon ,
QIntValidator ,
QDesktopServices 
)
from PyQt5 .QtWidgets import (
QApplication ,QWidget ,QLabel ,QLineEdit ,QTextEdit ,QPushButton ,
QVBoxLayout ,QHBoxLayout ,QFileDialog ,QMessageBox ,QListWidget ,QRadioButton ,QButtonGroup ,QCheckBox ,QSplitter ,QComboBox ,QGroupBox ,
QDialog ,QStackedWidget ,QScrollArea ,QListWidgetItem ,QSizePolicy ,QProgressBar ,
QAbstractItemView ,
QFrame ,
QAbstractButton 
)
from PyQt5 .QtCore import Qt ,QThread ,pyqtSignal ,QMutex ,QMutexLocker ,QObject ,QTimer ,QSettings ,QStandardPaths ,QCoreApplication ,QUrl ,QSize ,QProcess 
from urllib .parse import urlparse 

try :
    from PIL import Image 
except ImportError :
    Image =None 

from io import BytesIO 

try :
    print ("Attempting to import from downloader_utils...")
    from downloader_utils import (
    KNOWN_NAMES ,
    clean_folder_name ,
    extract_post_info ,
    download_from_api ,
    PostProcessorSignals ,
    prepare_cookies_for_request ,
    PostProcessorWorker ,
    DownloadThread as BackendDownloadThread ,
    SKIP_SCOPE_FILES ,
    SKIP_SCOPE_POSTS ,
    SKIP_SCOPE_BOTH ,
    CHAR_SCOPE_TITLE ,
    CHAR_SCOPE_FILES ,
    CHAR_SCOPE_BOTH ,
    CHAR_SCOPE_COMMENTS ,
    FILE_DOWNLOAD_STATUS_SUCCESS ,
    FILE_DOWNLOAD_STATUS_SKIPPED ,
    FILE_DOWNLOAD_STATUS_FAILED_RETRYABLE_LATER ,
    STYLE_DATE_BASED ,
    STYLE_DATE_POST_TITLE, # Import new style
    STYLE_POST_TITLE_GLOBAL_NUMBERING ,
    CREATOR_DOWNLOAD_DEFAULT_FOLDER_IGNORE_WORDS ,
    download_mega_file as drive_download_mega_file ,
    download_gdrive_file ,
    download_dropbox_file 
    )
    print ("Successfully imported names from downloader_utils.")
except ImportError as e :
    print (f"--- IMPORT ERROR ---")
    print (f"Failed to import from 'downloader_utils.py': {e }")
    print (f"--- Check downloader_utils.py for syntax errors or missing dependencies. ---")
    KNOWN_NAMES =[]
    PostProcessorWorker =object 
    class _MockPostProcessorSignals (QObject ):
        progress_signal =pyqtSignal (str )
        file_download_status_signal =pyqtSignal (bool )
        external_link_signal =pyqtSignal (str ,str ,str ,str ,str )
        file_progress_signal =pyqtSignal (str ,object )
        missed_character_post_signal =pyqtSignal (str ,str )
        def __init__ (self ,parent =None ):
            super ().__init__ (parent )
            print ("WARNING: Using MOCK PostProcessorSignals due to import error from downloader_utils.py. Some functionalities might be impaired.")
    PostProcessorSignals =_MockPostProcessorSignals 
    BackendDownloadThread =QThread 
    def clean_folder_name (n ):return str (n )
    def extract_post_info (u ):return None ,None ,None 
    def download_from_api (*a ,**k ):yield []
    SKIP_SCOPE_FILES ="files"
    SKIP_SCOPE_POSTS ="posts"
    SKIP_SCOPE_BOTH ="both"
    CHAR_SCOPE_TITLE ="title"
    CHAR_SCOPE_FILES ="files"
    CHAR_SCOPE_BOTH ="both"
    CHAR_SCOPE_COMMENTS ="comments"
    FILE_DOWNLOAD_STATUS_SUCCESS ="success"
    FILE_DOWNLOAD_STATUS_SKIPPED ="skipped"
    FILE_DOWNLOAD_STATUS_FAILED_RETRYABLE_LATER ="failed_retry_later"
    STYLE_DATE_BASED ="date_based"
    STYLE_DATE_POST_TITLE = "date_post_title"
    STYLE_POST_TITLE_GLOBAL_NUMBERING ="post_title_global_numbering"
    CREATOR_DOWNLOAD_DEFAULT_FOLDER_IGNORE_WORDS =set ()
    def drive_download_mega_file (*args ,**kwargs ):print ("drive_download_mega_file (stub)");pass 
    def download_gdrive_file (*args ,**kwargs ):print ("download_gdrive_file (stub)");pass 
    def download_dropbox_file (*args ,**kwargs ):print ("download_dropbox_file (stub)");pass 

except Exception as e :
    print (f"--- UNEXPECTED IMPORT ERROR ---")
    print (f"An unexpected error occurred during import: {e }")
    traceback .print_exc ()
    print (f"-----------------------------",file =sys .stderr )
    sys .exit (1 )
try :
    from languages import get_translation 
except ImportError :
    print ("Failed to import get_translation from languages.py. Dialog translations will not work.")
    print (f"-----------------------------",file =sys .stderr )
    sys .exit (1 )


_app_icon_cache = None # Module-level cache

def get_app_icon_object():
    """
    Loads and caches the application icon.
    Returns a QIcon object.
    """
    global _app_icon_cache
    if _app_icon_cache is not None and not _app_icon_cache.isNull():
        return _app_icon_cache

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    icon_path = os.path.join(base_dir, 'assets', 'Kemono.ico')
    
    if os.path.exists(icon_path):
        _app_icon_cache = QIcon(icon_path)
        if _app_icon_cache.isNull():
            print(f"Warning: QIcon created from '{icon_path}' is null. Icon might be invalid.")
            _app_icon_cache = QIcon() # Store an empty icon to avoid re-processing
    else:
        print(f"Warning: Application icon 'assets/Kemono.ico' not found at {icon_path} (in get_app_icon_object)")
        _app_icon_cache = QIcon() # Store an empty icon
    
    return _app_icon_cache

MAX_THREADS =200 
RECOMMENDED_MAX_THREADS =50 
MAX_FILE_THREADS_PER_POST_OR_WORKER =10 
POST_WORKER_BATCH_THRESHOLD =30 
POST_WORKER_NUM_BATCHES =4 
SOFT_WARNING_THREAD_THRESHOLD =40 
POST_WORKER_BATCH_DELAY_SECONDS =2.5 
MAX_POST_WORKERS_WHEN_COMMENT_FILTERING =3 

HTML_PREFIX ="<!HTML!>"

CONFIG_ORGANIZATION_NAME ="KemonoDownloader"
CONFIG_APP_NAME_MAIN ="ApplicationSettings"
MANGA_FILENAME_STYLE_KEY ="mangaFilenameStyleV1"
STYLE_POST_TITLE ="post_title" # Already defined in downloader_utils, but kept for clarity if used locally
STYLE_ORIGINAL_NAME ="original_name"
STYLE_DATE_BASED ="date_based"
STYLE_POST_TITLE_GLOBAL_NUMBERING =STYLE_POST_TITLE_GLOBAL_NUMBERING 
SKIP_WORDS_SCOPE_KEY ="skipWordsScopeV1"
ALLOW_MULTIPART_DOWNLOAD_KEY ="allowMultipartDownloadV1"

USE_COOKIE_KEY ="useCookieV1"
COOKIE_TEXT_KEY ="cookieTextV1"
CHAR_FILTER_SCOPE_KEY ="charFilterScopeV1"
THEME_KEY ="currentThemeV2"
SCAN_CONTENT_IMAGES_KEY ="scanContentForImagesV1"
LANGUAGE_KEY ="currentLanguageV1"

CONFIRM_ADD_ALL_ACCEPTED =1 
FAVORITE_SCOPE_SELECTED_LOCATION ="selected_location"
FAVORITE_SCOPE_ARTIST_FOLDERS ="artist_folders"
CONFIRM_ADD_ALL_SKIP_ADDING =2 
CONFIRM_ADD_ALL_CANCEL_DOWNLOAD =3 
LOG_DISPLAY_LINKS ="links"
LOG_DISPLAY_DOWNLOAD_PROGRESS ="download_progress"

from collections import defaultdict 
class DownloadExtractedLinksDialog (QDialog ):
    """A dialog to select and initiate download for extracted supported links."""

    download_requested =pyqtSignal (list )


    def __init__ (self ,links_data ,parent_app ,parent =None ):


        super ().__init__ (parent )
        self .links_data =links_data 

        app_icon = get_app_icon_object()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)


        if parent :
            parent_width =parent .width ()
            parent_height =parent .height()
            screen_height = QApplication.primaryScreen().availableGeometry().height() if QApplication.primaryScreen() else 768 # Default to 768 if screen info unavailable
            scale_factor = screen_height / 768.0 # Scale based on height relative to 768p

            base_min_w ,base_min_h =500 ,400
            scaled_min_w = int(base_min_w * scale_factor)
            scaled_min_h = int(base_min_h * scale_factor)

            self.setMinimumSize(scaled_min_w, scaled_min_h)
            self.resize(max(int(parent_width * 0.6 * scale_factor), scaled_min_w), max(int(parent_height * 0.7 * scale_factor), scaled_min_h))



        layout =QVBoxLayout (self )
        self .main_info_label =QLabel ()
        self .main_info_label .setAlignment (Qt .AlignHCenter |Qt .AlignTop )
        self .main_info_label .setWordWrap (True )
        layout .addWidget (self .main_info_label )

        self .links_list_widget =QListWidget ()
        self .links_list_widget .setSelectionMode (QAbstractItemView .NoSelection )

        grouped_links =defaultdict (list )
        for link_info_item in self .links_data :
            post_title_for_group =link_info_item .get ('title','Untitled Post')
            grouped_links [post_title_for_group ].append (link_info_item )


        sorted_post_titles =sorted (grouped_links .keys (),key =lambda x :x .lower ())

        for post_title_key in sorted_post_titles :

            header_item =QListWidgetItem (f"{post_title_key }")
            header_item .setFlags (Qt .NoItemFlags )
            font =header_item .font ()
            font .setBold (True )
            font .setPointSize (font .pointSize ()+1 )
            header_item .setFont (font )
            if parent and hasattr (parent ,'current_theme')and parent .current_theme =="dark":
                header_item .setForeground (Qt .cyan )
            else :
                header_item .setForeground (Qt .blue )
            self .links_list_widget .addItem (header_item )

            for link_info_data in grouped_links [post_title_key ]:
                platform_display =link_info_data .get ('platform','unknown').upper ()
                display_text =f"  [{platform_display }] {link_info_data ['link_text']} ({link_info_data ['url']})"
                item =QListWidgetItem (display_text )
                item .setData (Qt .UserRole ,link_info_data )
                item .setFlags (item .flags ()|Qt .ItemIsUserCheckable )
                item .setCheckState (Qt .Checked )
                self .links_list_widget .addItem (item )




        layout .addWidget (self .links_list_widget )

        button_layout =QHBoxLayout ()
        self .select_all_button =QPushButton ()
        self .select_all_button .clicked .connect (lambda :self ._set_all_items_checked (Qt .Checked ))
        button_layout .addWidget (self .select_all_button )

        self .deselect_all_button =QPushButton ()
        self .deselect_all_button .clicked .connect (lambda :self ._set_all_items_checked (Qt .Unchecked ))
        button_layout .addWidget (self .deselect_all_button )
        button_layout .addStretch ()

        self .download_button =QPushButton ()
        self .download_button .clicked .connect (self ._handle_download_selected )
        self .download_button .setDefault (True )
        button_layout .addWidget (self .download_button )

        self .cancel_button =QPushButton ()
        self .cancel_button .clicked .connect (self .reject )
        button_layout .addWidget (self .cancel_button )
        layout .addLayout (button_layout )

        self .parent_app =parent_app 
        self ._retranslate_ui ()

        if parent and hasattr (parent ,'get_dark_theme')and parent .current_theme =="dark":
            self .setStyleSheet (parent .get_dark_theme ())

    def _tr (self ,key ,default_text =""):
        """Helper to get translation based on current app language."""
        if callable (get_translation )and self .parent_app :
            return get_translation (self .parent_app .current_selected_language ,key ,default_text )
        return default_text 

    def _retranslate_ui (self ):
        self .setWindowTitle (self ._tr ("download_external_links_dialog_title","Download Selected External Links"))

        self .main_info_label .setText (self ._tr ("download_external_links_dialog_main_label","Found {count} supported link(s)...").format (count =len (self .links_data )))
        self .select_all_button .setText (self ._tr ("select_all_button_text","Select All"))
        self .deselect_all_button .setText (self ._tr ("deselect_all_button_text","Deselect All"))
        self .download_button .setText (self ._tr ("download_selected_button_text","Download Selected"))
        self .cancel_button .setText (self ._tr ("fav_posts_cancel_button","Cancel"))

    def _set_all_items_checked (self ,check_state ):
        for i in range (self .links_list_widget .count ()):
            item =self .links_list_widget .item (i )
            if item .flags ()&Qt .ItemIsUserCheckable :
                item .setCheckState (check_state )

    def _handle_download_selected (self ):
        selected_links =[]
        for i in range (self .links_list_widget .count ()):
            item =self .links_list_widget .item (i )

            if item .flags ()&Qt .ItemIsUserCheckable and item .checkState ()==Qt .Checked and item .data (Qt .UserRole )is not None :
                selected_links .append (item .data (Qt .UserRole ))
        if selected_links :
            self .download_requested .emit (selected_links )
            self .accept ()
        else :
            QMessageBox .information (
            self ,
            self ._tr ("no_selection_title","No Selection"),
            self ._tr ("no_selection_message_links","Please select at least one link to download."))

class ConfirmAddAllDialog (QDialog ):
    """A dialog to confirm adding multiple new names to Known.txt."""
    def __init__ (self ,new_filter_objects_list ,parent_app ,parent =None ):
        super ().__init__ (parent )
        self .parent_app =parent_app 
        self .setModal (True )
        self .new_filter_objects_list =new_filter_objects_list 
        self.setWindowTitle(self._tr("confirm_add_all_dialog_title", "Confirm Adding New Names"))    
        self .user_choice =CONFIRM_ADD_ALL_CANCEL_DOWNLOAD 
        self .setWindowTitle (self ._tr ("confirm_add_all_dialog_title","Confirm Adding New Names"))

        screen_height = QApplication.primaryScreen().availableGeometry().height() if QApplication.primaryScreen() else 768
        scale_factor = screen_height / 768.0

        base_min_w ,base_min_h =480 ,350
        scaled_min_w = int(base_min_w * scale_factor)
        scaled_min_h = int(base_min_h * scale_factor)
        self.setMinimumSize(scaled_min_w, scaled_min_h)

        main_layout =QVBoxLayout (self )

        info_label =QLabel (
        "The following new names/groups from your 'Filter by Character(s)' input are not in 'Known.txt'.\n"
        "Adding them can improve folder organization for future downloads.\n\n"
        "Review the list and choose an action:")

        self .names_list_widget =QListWidget ()
        for filter_obj in self .new_filter_objects_list :
            item_text =filter_obj ["name"]
            list_item =QListWidgetItem (item_text )
            list_item .setFlags (list_item .flags ()|Qt .ItemIsUserCheckable )
            list_item .setCheckState (Qt .Checked )
            list_item .setData (Qt .UserRole ,filter_obj )
            self .names_list_widget .addItem (list_item )

        self .info_label =QLabel ()
        self .info_label .setWordWrap (True )
        main_layout .addWidget (self .info_label )

        main_layout .addWidget (self .names_list_widget )

        selection_buttons_layout =QHBoxLayout ()
        self .select_all_button =QPushButton ()
        self .select_all_button .clicked .connect (self ._select_all_items )
        selection_buttons_layout .addWidget (self .select_all_button )

        self .deselect_all_button =QPushButton ()
        self .deselect_all_button .clicked .connect (self ._deselect_all_items )
        selection_buttons_layout .addWidget (self .deselect_all_button )
        selection_buttons_layout .addStretch ()
        main_layout .addLayout (selection_buttons_layout )


        buttons_layout =QHBoxLayout ()

        self .add_selected_button =QPushButton ()
        self .add_selected_button .clicked .connect (self ._accept_add_selected )
        buttons_layout .addWidget (self .add_selected_button )

        self .skip_adding_button =QPushButton ()
        self .skip_adding_button .clicked .connect (self ._reject_skip_adding )
        buttons_layout .addWidget (self .skip_adding_button )
        buttons_layout .addStretch ()

        self .cancel_download_button =QPushButton ()
        self .cancel_download_button .clicked .connect (self ._reject_cancel_download )
        buttons_layout .addWidget (self .cancel_download_button )

        main_layout .addLayout (buttons_layout )
        self ._retranslate_ui ()

        if self .parent_app and hasattr (self .parent_app ,'get_dark_theme')and self .parent_app .current_theme =="dark":
            self .setStyleSheet (parent .get_dark_theme ())
        self .add_selected_button .setDefault (True )

    def _tr (self ,key ,default_text =""):
        
        if callable (get_translation )and self .parent_app :
            return get_translation (self .parent_app .current_selected_language ,key ,default_text )
        return default_text 

    def _retranslate_ui (self ):
        self .setWindowTitle (self ._tr ("confirm_add_all_dialog_title","Confirm Adding New Names"))
        self .info_label .setText (self ._tr ("confirm_add_all_info_label","The following new names/groups..."))
        self .select_all_button .setText (self ._tr ("confirm_add_all_select_all_button","Select All"))
        self .deselect_all_button .setText (self ._tr ("confirm_add_all_deselect_all_button","Deselect All"))
        self .add_selected_button .setText (self ._tr ("confirm_add_all_add_selected_button","Add Selected to Known.txt"))
        self .skip_adding_button .setText (self ._tr ("confirm_add_all_skip_adding_button","Skip Adding These"))
        self .cancel_download_button .setText (self ._tr ("confirm_add_all_cancel_download_button","Cancel Download"))

    def _select_all_items (self ):
        for i in range (self .names_list_widget .count ()):
            self .names_list_widget .item (i ).setCheckState (Qt .Checked )

    def _deselect_all_items (self ):
        for i in range (self .names_list_widget .count ()):
            self .names_list_widget .item (i ).setCheckState (Qt .Unchecked )

    def _accept_add_selected (self ):
        selected_objects =[]
        for i in range (self .names_list_widget .count ()):
            item =self .names_list_widget .item (i )
            if item .checkState ()==Qt .Checked :
                filter_obj =item .data (Qt .UserRole )
                if filter_obj :
                    selected_objects .append (filter_obj )

        self .user_choice =selected_objects 
        self .accept ()

    def _reject_skip_adding (self ):
        self .user_choice =CONFIRM_ADD_ALL_SKIP_ADDING 
        self .reject ()

    def _reject_cancel_download (self ):
        self .user_choice =CONFIRM_ADD_ALL_CANCEL_DOWNLOAD 
        self .reject ()

    def exec_ (self ):
        super ().exec_ ()
        if isinstance (self .user_choice ,list )and not self .user_choice :
            return CONFIRM_ADD_ALL_SKIP_ADDING 
        return self .user_choice 

class ExportOptionsDialog (QDialog ):
    """Dialog to choose export format for error file links."""
    EXPORT_MODE_LINK_ONLY =1 
    EXPORT_MODE_WITH_DETAILS =2 

    def __init__ (self ,parent_app ,parent =None ):
        super ().__init__ (parent )
        self .parent_app =parent_app 
        self .setModal (True )
        self .selected_option =self .EXPORT_MODE_LINK_ONLY 

        screen_height = QApplication.primaryScreen().availableGeometry().height() if QApplication.primaryScreen() else 768
        scale_factor = screen_height / 768.0

        base_min_w =350
        scaled_min_w = int(base_min_w * scale_factor)
        self.setMinimumWidth(scaled_min_w)

        layout =QVBoxLayout (self )

        self .description_label =QLabel ()
        layout .addWidget (self .description_label )

        self .radio_group =QButtonGroup (self )

        self .radio_link_only =QRadioButton ()

        self .radio_link_only .setChecked (True )
        self .radio_group .addButton (self .radio_link_only ,self .EXPORT_MODE_LINK_ONLY )
        layout .addWidget (self .radio_link_only )

        self .radio_with_details =QRadioButton ()

        self .radio_group .addButton (self .radio_with_details ,self .EXPORT_MODE_WITH_DETAILS )
        layout .addWidget (self .radio_with_details )

        button_layout =QHBoxLayout ()
        self .export_button =QPushButton ()
        self .export_button .clicked .connect (self ._handle_export )
        self .export_button .setDefault (True )

        self .cancel_button =QPushButton ()
        self .cancel_button .clicked .connect (self .reject )

        button_layout .addStretch (1 )
        button_layout .addWidget (self .export_button )
        button_layout .addWidget (self .cancel_button )
        layout .addLayout (button_layout )

        self ._retranslate_ui ()


        if self .parent_app and hasattr (self .parent_app ,'current_theme')and self .parent_app .current_theme =="dark":
            if hasattr (self .parent_app ,'get_dark_theme'):
                self .setStyleSheet (self .parent_app .get_dark_theme ())

    def _tr (self ,key ,default_text =""):
        """Helper to get translation based on current app language."""
        if callable (get_translation )and self .parent_app :
            return get_translation (self .parent_app .current_selected_language ,key ,default_text )
        return default_text 

    def _retranslate_ui (self ):
        self .setWindowTitle (self ._tr ("export_options_dialog_title","Export Options"))
        self .description_label .setText (self ._tr ("export_options_description_label","Choose the format for exporting error file links:"))
        self .radio_link_only .setText (self ._tr ("export_options_radio_link_only","Link per line (URL only)"))
        self .radio_link_only .setToolTip (self ._tr ("export_options_radio_link_only_tooltip","Exports only the direct download URL..."))
        self .radio_with_details .setText (self ._tr ("export_options_radio_with_details","Export with details (URL [Post, File info])"))
        self .radio_with_details .setToolTip (self ._tr ("export_options_radio_with_details_tooltip","Exports the URL followed by details..."))
        self .export_button .setText (self ._tr ("export_options_export_button","Export"))
        self .cancel_button .setText (self ._tr ("fav_posts_cancel_button","Cancel"))

    def _handle_export (self ):
        self .selected_option =self .radio_group .checkedId ()
        self .accept ()

    def get_selected_option (self ):
        return self .selected_option 

class ErrorFilesDialog (QDialog ):
    """Dialog to display files that were skipped due to errors."""
    retry_selected_signal =pyqtSignal (list )
    def __init__ (self ,error_files_info_list ,parent_app ,parent =None ):
        super ().__init__ (parent )
        self .parent_app =parent_app 
        self .setModal (True )
        self .error_files =error_files_info_list 

        screen_height = QApplication.primaryScreen().availableGeometry().height() if QApplication.primaryScreen() else 768
        scale_factor = screen_height / 768.0

        base_min_w ,base_min_h =500 ,300
        scaled_min_w = int(base_min_w * scale_factor)
        scaled_min_h = int(base_min_h * scale_factor)
        self.setMinimumSize(scaled_min_w, scaled_min_h)

        main_layout =QVBoxLayout (self )

        if not self .error_files :
            self .info_label =QLabel ()
            main_layout .addWidget (self .info_label )
        else :
            self .info_label =QLabel ()
            self .info_label .setWordWrap (True )
            main_layout .addWidget (self .info_label )

            self .files_list_widget =QListWidget ()
            self .files_list_widget .setSelectionMode (QAbstractItemView .NoSelection )
            for error_info in self .error_files :
                filename =error_info .get ('forced_filename_override',error_info .get ('file_info',{}).get ('name','Unknown Filename'))
                post_title =error_info .get ('post_title','Unknown Post')
                post_id =error_info .get ('original_post_id_for_log','N/A')
                item_text =f"File: {filename }\nFrom Post: '{post_title }' (ID: {post_id })"
                list_item =QListWidgetItem (item_text )
                list_item .setData (Qt .UserRole ,error_info )
                list_item .setFlags (list_item .flags ()|Qt .ItemIsUserCheckable )
                list_item .setCheckState (Qt .Unchecked )
                self .files_list_widget .addItem (list_item )
            main_layout .addWidget (self .files_list_widget )

        buttons_layout =QHBoxLayout ()
        self .select_all_button =QPushButton ()
        self .select_all_button .clicked .connect (self ._select_all_items )
        buttons_layout .addWidget (self .select_all_button )

        self .retry_button =QPushButton ()
        self .retry_button .clicked .connect (self ._handle_retry_selected )
        self .export_button =QPushButton ()
        self .export_button .clicked .connect (self ._handle_export_errors_to_txt )
        buttons_layout .addWidget (self .retry_button )

        buttons_layout .addStretch (1 )
        self .ok_button =QPushButton ()
        self .ok_button .clicked .connect (self .accept )
        buttons_layout .addWidget (self .ok_button )
        main_layout .addLayout (buttons_layout )
        buttons_layout .insertWidget (2 ,self .export_button )

        self ._retranslate_ui ()

        self .select_all_button .setEnabled (bool (self .error_files ))
        self .retry_button .setEnabled (bool (self .error_files ))
        self .export_button .setEnabled (bool (self .error_files ))

        if self .parent_app and hasattr (self .parent_app ,'get_dark_theme')and self .parent_app .current_theme =="dark":
            self .setStyleSheet (self .parent_app .get_dark_theme ())
        self .ok_button .setDefault (True )

    def _tr (self ,key ,default_text =""):
        """Helper to get translation based on current app language."""
        if callable (get_translation )and self .parent_app :
            return get_translation (self .parent_app .current_selected_language ,key ,default_text )
        return default_text 

    def _retranslate_ui (self ):
        self .setWindowTitle (self ._tr ("error_files_dialog_title","Files Skipped Due to Errors"))
        if not self .error_files :
            self .info_label .setText (self ._tr ("error_files_no_errors_label","No files were recorded..."))
        else :
            self .info_label .setText (self ._tr ("error_files_found_label","The following {count} file(s)...").format (count =len (self .error_files )))
        self .select_all_button .setText (self ._tr ("error_files_select_all_button","Select All"))
        self .retry_button .setText (self ._tr ("error_files_retry_selected_button","Retry Selected"))
        self .export_button .setText (self ._tr ("error_files_export_urls_button","Export URLs to .txt"))
        self .ok_button .setText (self ._tr ("ok_button","OK"))

    def _select_all_items (self ):
        for i in range (self .files_list_widget .count ()):
            self .files_list_widget .item (i ).setCheckState (Qt .Checked )

    def _handle_retry_selected (self ):
        selected_files_for_retry =[self .files_list_widget .item (i ).data (Qt .UserRole )for i in range (self .files_list_widget .count ())if self .files_list_widget .item (i ).checkState ()==Qt .Checked ]
        if selected_files_for_retry :
            self .retry_selected_signal .emit (selected_files_for_retry )
            self .accept ()
        else :
            QMessageBox .information (self ,self ._tr ("fav_artists_no_selection_title","No Selection"),self ._tr ("error_files_no_selection_retry_message","Please select at least one file to retry."))

    def _handle_export_errors_to_txt (self ):
        if not self .error_files :
            QMessageBox .information (self ,self ._tr ("error_files_no_errors_export_title","No Errors"),self ._tr ("error_files_no_errors_export_message","There are no error file URLs to export."))
            return 


        options_dialog =ExportOptionsDialog (parent_app =self .parent_app ,parent =self )
        if not options_dialog .exec_ ()==QDialog .Accepted :

            return 

        export_option =options_dialog .get_selected_option ()

        lines_to_export =[]
        for error_item in self .error_files :
            file_info =error_item .get ('file_info',{})
            url =file_info .get ('url')

            if url :
                if export_option ==ExportOptionsDialog .EXPORT_MODE_WITH_DETAILS :
                    original_filename =file_info .get ('name','Unknown Filename')
                    post_title =error_item .get ('post_title','Unknown Post')
                    post_id =error_item .get ('original_post_id_for_log','N/A')
                    details_string =f" [Post: '{post_title }' (ID: {post_id }), File: '{original_filename }']"
                    lines_to_export .append (f"{url }{details_string }")
                else :
                    lines_to_export .append (url )

        if not lines_to_export :
            QMessageBox .information (self ,self ._tr ("error_files_no_urls_found_export_title","No URLs Found"),self ._tr ("error_files_no_urls_found_export_message","Could not extract any URLs..."))
            return 

        default_filename ="error_file_links.txt"
        filepath ,_ =QFileDialog .getSaveFileName (
        self ,self ._tr ("error_files_save_dialog_title","Save Error File URLs"),default_filename ,"Text Files (*.txt);;All Files (*)"
        )

        if filepath :
            try :
                with open (filepath ,'w',encoding ='utf-8')as f :
                    for line in lines_to_export :
                        f .write (f"{line }\n")
                QMessageBox .information (self ,self ._tr ("error_files_export_success_title","Export Successful"),self ._tr ("error_files_export_success_message","Successfully exported...").format (count =len (lines_to_export ),filepath =filepath ))
            except Exception as e :
                QMessageBox .critical (self ,self ._tr ("error_files_export_error_title","Export Error"),self ._tr ("error_files_export_error_message","Could not export...").format (error =str (e )))
        else :

            pass 
class FutureSettingsDialog (QDialog ):
    """A simple dialog as a placeholder for future settings."""
    def __init__ (self ,parent_app_ref ,parent =None ):
        super ().__init__ (parent )
        self .parent_app =parent_app_ref 
        self .setModal (True )

        screen_height = QApplication.primaryScreen().availableGeometry().height() if QApplication.primaryScreen() else 768
        scale_factor = screen_height / 768.0

        base_min_w ,base_min_h =380 ,250
        scaled_min_w = int(base_min_w * scale_factor)
        scaled_min_h = int(base_min_h * scale_factor)
        self.setMinimumSize(scaled_min_w, scaled_min_h)

        layout =QVBoxLayout (self )


        self .appearance_group_box =QGroupBox ()
        appearance_layout =QVBoxLayout (self .appearance_group_box )

        self .theme_toggle_button =QPushButton ()
        self ._update_theme_toggle_button_text ()
        self .theme_toggle_button .clicked .connect (self ._toggle_theme )
        appearance_layout .addWidget (self .theme_toggle_button )
        layout .addWidget (self .appearance_group_box )


        self .language_group_box =QGroupBox ()
        language_group_layout =QVBoxLayout (self .language_group_box )

        self .language_selection_layout =QHBoxLayout ()
        self .language_label =QLabel ()
        self .language_selection_layout .addWidget (self .language_label )

        self .language_combo_box =QComboBox ()
        self .language_combo_box .currentIndexChanged .connect (self ._language_selection_changed )
        self .language_selection_layout .addWidget (self .language_combo_box ,1 )
        language_group_layout .addLayout (self .language_selection_layout )
        layout .addWidget (self .language_group_box )


        layout .addStretch (1 )

        self .ok_button =QPushButton ()
        self .ok_button .clicked .connect (self .accept )
        layout .addWidget (self .ok_button ,0 ,Qt .AlignRight |Qt .AlignBottom )

        self ._retranslate_ui ()
        self ._apply_dialog_theme ()
    def _tr (self ,key ,default_text =""):
        """Helper to get translation based on current app language."""
        if callable (get_translation ):
            return get_translation (self .parent_app .current_selected_language ,key ,default_text )
        return default_text 

    def _retranslate_ui (self ):
        self .setWindowTitle (self ._tr ("settings_dialog_title","Settings"))
        self .appearance_group_box .setTitle (self ._tr ("appearance_group_title","Appearance"))
        self .language_group_box .setTitle (self ._tr ("language_group_title","Language Settings"))
        self .language_label .setText (self ._tr ("language_label","Language:"))
        self ._update_theme_toggle_button_text ()
        self ._populate_language_combo_box ()
        self .ok_button .setText (self ._tr ("ok_button","OK"))
    def _update_theme_toggle_button_text (self ):
        if self .parent_app .current_theme =="dark":
            self .theme_toggle_button .setText (self ._tr ("theme_toggle_light","Switch to Light Mode"))
            self .theme_toggle_button .setToolTip (self ._tr ("theme_tooltip_light","Change the application appearance to light."))
        else :
            self .theme_toggle_button .setText (self ._tr ("theme_toggle_dark","Switch to Dark Mode"))
            self .theme_toggle_button .setToolTip (self ._tr ("theme_tooltip_dark","Change the application appearance to dark."))

    def _toggle_theme (self ):
        if self .parent_app .current_theme =="dark":
            self .parent_app .apply_theme ("light")
        else :
            self .parent_app .apply_theme ("dark")

        self ._retranslate_ui ()
        self ._apply_dialog_theme ()

    def _apply_dialog_theme (self ):
        if self .parent_app .current_theme =="dark":
            self .setStyleSheet (self .parent_app .get_dark_theme ())
        else :
            self .setStyleSheet ("")

    def _populate_language_combo_box (self ):
        self .language_combo_box .blockSignals (True )
        self .language_combo_box .clear ()
        languages =[
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
        for lang_code ,lang_name in languages :
            self .language_combo_box .addItem (lang_name ,lang_code )
            if self .parent_app .current_selected_language ==lang_code :
                self .language_combo_box .setCurrentIndex (self .language_combo_box .count ()-1 )
        self .language_combo_box .blockSignals (False )

    def _language_selection_changed (self ,index ):
        selected_lang_code =self .language_combo_box .itemData (index )
        if selected_lang_code and selected_lang_code !=self .parent_app .current_selected_language :
            self .parent_app .current_selected_language =selected_lang_code 
            self .parent_app .settings .setValue (LANGUAGE_KEY ,self .parent_app .current_selected_language )
            self .parent_app .settings .sync ()
            self ._retranslate_ui ()





            msg_box =QMessageBox (self )
            msg_box .setIcon (QMessageBox .Information )
            msg_box .setWindowTitle (self ._tr ("language_change_title","Language Changed"))
            msg_box .setText (self ._tr ("language_change_message","The language has been changed. A restart is required for all changes to take full effect."))
            msg_box .setInformativeText (self ._tr ("language_change_informative","Would you like to restart the application now?"))

            restart_button =msg_box .addButton (self ._tr ("restart_now_button","Restart Now"),QMessageBox .ApplyRole )
            ok_button =msg_box .addButton (self ._tr ("ok_button","OK"),QMessageBox .AcceptRole )

            msg_box .setDefaultButton (ok_button )
            msg_box .exec_ ()

            if msg_box .clickedButton ()==restart_button :
                self .parent_app ._request_restart_application ()

class EmptyPopupDialog (QDialog ):
    """A simple empty popup dialog."""
    SCOPE_CHARACTERS ="Characters"
    INITIAL_LOAD_LIMIT =200 
    SCOPE_CREATORS ="Creators"


    def __init__ (self ,app_base_dir ,parent_app_ref ,parent =None ):
        super ().__init__ (parent )
        self .setMinimumSize (400 ,300 )
        screen_height = QApplication.primaryScreen().availableGeometry().height() if QApplication.primaryScreen() else 768
        scale_factor = screen_height / 768.0
        self.setMinimumSize(int(400 * scale_factor), int(300 * scale_factor))
 
        self .parent_app =parent_app_ref 
        self .current_scope_mode =self .SCOPE_CHARACTERS 
        self .app_base_dir =app_base_dir 

        app_icon = get_app_icon_object()
        if app_icon and not app_icon.isNull():
            self.setWindowIcon(app_icon)
        self .selected_creators_for_queue =[]
        self .globally_selected_creators ={}
        self.fetched_posts_data = {} # Stores posts by (service, user_id)
        self.post_fetch_thread = None
        self.TITLE_COLUMN_WIDTH_FOR_POSTS = 70 # Define column width
        self.globally_selected_post_ids = set() # To store (service, user_id, post_id) tuples
        self._is_scrolling_titles = False # For scroll synchronization
        self._is_scrolling_dates = False  # For scroll synchronization

        # Main layout for the dialog will be a QHBoxLayout holding the splitter
        dialog_layout = QHBoxLayout(self)
        self.setLayout(dialog_layout)


        # --- Left Pane (Creator Selection) ---
        self.left_pane_widget = QWidget()
        left_pane_layout = QVBoxLayout(self.left_pane_widget)

        # Create a horizontal layout for search input and fetch button
        search_fetch_layout = QHBoxLayout()
        self .search_input =QLineEdit ()
        self .search_input .textChanged .connect (self ._filter_list )
        search_fetch_layout.addWidget(self.search_input, 1) # Give search input more stretch
        self.fetch_posts_button = QPushButton() # Placeholder text, will be translated
        self.fetch_posts_button.setEnabled(False) # Initially disabled
        self.fetch_posts_button.clicked.connect(self._handle_fetch_posts_click)
        search_fetch_layout.addWidget(self.fetch_posts_button)
        left_pane_layout.addLayout(search_fetch_layout)
        
        self .progress_bar =QProgressBar ()
        self .progress_bar .setRange (0 ,0 )
        self .progress_bar .setTextVisible (False )
        self .progress_bar .setVisible (False )
        left_pane_layout.addWidget (self .progress_bar )

        self .list_widget =QListWidget ()
        self .list_widget .itemChanged .connect (self ._handle_item_check_changed )
        left_pane_layout.addWidget (self .list_widget )

        # Bottom buttons for left pane
        left_bottom_buttons_layout =QHBoxLayout ()
        self .add_selected_button =QPushButton ()
        self .add_selected_button .setToolTip (
        "Add Selected Creators to URL Input\n\n"
        "Adds the names of all checked creators to the main URL input field,\n"
        "comma-separated, and closes this dialog."
        )
        self .add_selected_button .clicked .connect (self ._handle_add_selected )
        self .add_selected_button .setDefault (True )
        left_bottom_buttons_layout.addWidget (self .add_selected_button )
        self .scope_button =QPushButton ()
        self .scope_button .clicked .connect (self ._toggle_scope_mode )
        left_bottom_buttons_layout.addWidget (self .scope_button )
        left_pane_layout.addLayout(left_bottom_buttons_layout)

        # --- Right Pane (Posts - initially hidden) ---
        self.right_pane_widget = QWidget()
        right_pane_layout = QVBoxLayout(self.right_pane_widget)

        self.posts_area_title_label = QLabel("Fetched Posts")
        self.posts_area_title_label.setAlignment(Qt.AlignCenter)
        right_pane_layout.addWidget(self.posts_area_title_label)

        self.posts_search_input = QLineEdit()
        self.posts_search_input.setVisible(False) # Initially hidden until posts are fetched
        # Placeholder text will be set in _retranslate_ui
        self.posts_search_input.textChanged.connect(self._filter_fetched_posts_list)
        right_pane_layout.addWidget(self.posts_search_input) # Moved search input up

        # Headers for the new two-column layout (Title and Date)
        posts_headers_layout = QHBoxLayout()
        self.posts_title_header_label = QLabel() # Text set in _retranslate_ui
        self.posts_title_header_label.setStyleSheet("font-weight: bold; padding-left: 20px;") # Padding for checkbox alignment
        posts_headers_layout.addWidget(self.posts_title_header_label, 7) # 70% stretch factor

        self.posts_date_header_label = QLabel() # Text set in _retranslate_ui
        self.posts_date_header_label.setStyleSheet("font-weight: bold;")
        posts_headers_layout.addWidget(self.posts_date_header_label, 3) # 30% stretch factor
        right_pane_layout.addLayout(posts_headers_layout)


        # Splitter for Title and Date lists
        self.posts_content_splitter = QSplitter(Qt.Horizontal)

        self.posts_title_list_widget = QListWidget() # Renamed from self.posts_list_widget
        self.posts_title_list_widget.itemChanged.connect(self._handle_post_item_check_changed)
        self.posts_title_list_widget.setAlternatingRowColors(True) # Enable alternating row colors
        self.posts_content_splitter.addWidget(self.posts_title_list_widget)

        self.posts_date_list_widget = QListWidget() # New list for dates
        self.posts_date_list_widget.setSelectionMode(QAbstractItemView.NoSelection) # Dates are not selectable/interactive
        self.posts_date_list_widget.setAlternatingRowColors(True) # Enable alternating row colors
        self.posts_date_list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # No horizontal scroll for dates
        self.posts_content_splitter.addWidget(self.posts_date_list_widget)

        right_pane_layout.addWidget(self.posts_content_splitter, 1) # Add stretch factor of 1

        posts_buttons_top_layout = QHBoxLayout()
        self.posts_select_all_button = QPushButton() # Text set in _retranslate_ui
        self.posts_select_all_button.clicked.connect(self._handle_posts_select_all)
        posts_buttons_top_layout.addWidget(self.posts_select_all_button)

        self.posts_deselect_all_button = QPushButton() # Text set in _retranslate_ui
        self.posts_deselect_all_button.clicked.connect(self._handle_posts_deselect_all)
        posts_buttons_top_layout.addWidget(self.posts_deselect_all_button)
        right_pane_layout.addLayout(posts_buttons_top_layout)

        posts_buttons_bottom_layout = QHBoxLayout()
        self.posts_add_selected_button = QPushButton() # Text set in _retranslate_ui
        self.posts_add_selected_button.clicked.connect(self._handle_posts_add_selected_to_queue)
        posts_buttons_bottom_layout.addWidget(self.posts_add_selected_button)

        self.posts_close_button = QPushButton() # Text set in _retranslate_ui
        self.posts_close_button.clicked.connect(self._handle_posts_close_view)
        posts_buttons_bottom_layout.addWidget(self.posts_close_button)
        right_pane_layout.addLayout(posts_buttons_bottom_layout)
        
        self.right_pane_widget.hide() # Initially hidden




        # --- Splitter ---
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.addWidget(self.left_pane_widget)
        self.main_splitter.addWidget(self.right_pane_widget)
        self.main_splitter.setCollapsible(0, False) # Prevent left pane from collapsing
        self.main_splitter.setCollapsible(1, True) # Allow right pane to be hidden

        # Connect scrollbars for synchronized scrolling (AFTER both widgets are created)
        self.posts_title_list_widget.verticalScrollBar().valueChanged.connect(self._sync_scroll_dates)
        self.posts_date_list_widget.verticalScrollBar().valueChanged.connect(self._sync_scroll_titles)     
        dialog_layout.addWidget(self.main_splitter)

        self.original_size = self.sizeHint() # Store initial size hint
        self.main_splitter.setSizes([int(self.width() * scale_factor), 0]) # Left pane takes all width initially (before resize)

        self ._retranslate_ui ()

        if self .parent_app and hasattr (self .parent_app ,'get_dark_theme')and self .parent_app .current_theme =="dark":
            self .setStyleSheet (self .parent_app .get_dark_theme ())

        # Set initial size for the dialog (before fetching posts)
        self.resize(int((self.original_size.width() + 50) * scale_factor), int((self.original_size.height() + 100) * scale_factor)) # A bit larger than pure hint

        QTimer .singleShot (0 ,self ._perform_initial_load )

    def _center_on_screen(self):
        """Centers the dialog on the parent's screen or the primary screen."""
        if self.parent_app:
            parent_rect = self.parent_app.frameGeometry()
            self.move(parent_rect.center() - self.rect().center())
        else:
            try:
                screen_geo = QApplication.primaryScreen().availableGeometry()
                self.move(screen_geo.center() - self.rect().center())
            except AttributeError: # Fallback if no screen info (e.g., headless test)
                pass

    def _handle_fetch_posts_click(self):
        selected_creators = list(self.globally_selected_creators.values())
        if not selected_creators:
            QMessageBox.information(self, self._tr("no_selection_title", "No Selection"),
                                    "Please select at least one creator to fetch posts for.")
            return

        if self.parent_app:
            parent_geometry = self.parent_app.geometry()
            new_width = int(parent_geometry.width() * 0.75)
            new_height = int(parent_geometry.height() * 0.80)
            self.resize(new_width, new_height)
            self._center_on_screen()

        self.right_pane_widget.show()
        QTimer.singleShot(10, lambda: self.main_splitter.setSizes([int(self.width() * 0.3), int(self.width() * 0.7)]))
        # Set initial sizes for the new posts_content_splitter (70/30 for title/date)
        QTimer.singleShot(20, lambda: self.posts_content_splitter.setSizes([int(self.posts_content_splitter.width() * 0.7), int(self.posts_content_splitter.width() * 0.3)]))      
        self.add_selected_button.setEnabled(False)
        self.globally_selected_post_ids.clear() # Clear previous post selections    
        self.posts_search_input.setVisible(True)
        self.setWindowTitle(self._tr("creator_popup_title_fetching", "Creator Posts"))
        
        self.fetch_posts_button.setEnabled(False)
        self.posts_title_list_widget.clear()
        self.posts_date_list_widget.clear() # Clear date list as well       
        self.fetched_posts_data.clear()
        self.posts_area_title_label.setText(self._tr("fav_posts_loading_status", "Loading favorite posts...")) # Generic loading
        self.posts_title_list_widget.itemChanged.connect(self._handle_post_item_check_changed) # Connect here
        self.progress_bar.setVisible(True)

        if self.post_fetch_thread and self.post_fetch_thread.isRunning():
            self.post_fetch_thread.cancel()
            self.post_fetch_thread.wait()
        self.post_fetch_thread = PostsFetcherThread(selected_creators, self)
        self.post_fetch_thread.status_update.connect(self._handle_fetch_status_update)
        self.post_fetch_thread.posts_fetched_signal.connect(self._handle_posts_fetched)
        self.post_fetch_thread.fetch_error_signal.connect(self._handle_fetch_error)
        self.post_fetch_thread.finished_signal.connect(self._handle_fetch_finished)
        self.post_fetch_thread.start()

    def _tr (self ,key ,default_text =""):
        """Helper to get translation based on current app language."""
        if callable (get_translation )and self .parent_app :
            return get_translation (self .parent_app .current_selected_language ,key ,default_text )
        return default_text 

    def _retranslate_ui (self ):
        self .setWindowTitle (self ._tr ("creator_popup_title","Creator Selection"))
        self .search_input .setPlaceholderText (self ._tr ("creator_popup_search_placeholder","Search by name, service, or paste creator URL..."))
        self .add_selected_button .setText (self ._tr ("creator_popup_add_selected_button","Add Selected"))
        self .fetch_posts_button.setText(self._tr("fetch_posts_button_text", "Fetch Posts"))
        self ._update_scope_button_text_and_tooltip ()
        
        self.posts_search_input.setPlaceholderText(self._tr("creator_popup_posts_search_placeholder", "Search fetched posts by title..."))
        # Set header texts for the new two-column layout
        self.posts_title_header_label.setText(self._tr("column_header_post_title", "Post Title"))
        self.posts_date_header_label.setText(self._tr("column_header_date_uploaded", "Date Uploaded"))
        # Retranslate right pane elements
        self.posts_area_title_label.setText(self._tr("creator_popup_posts_area_title", "Fetched Posts")) # Placeholder key
        self.posts_select_all_button.setText(self._tr("select_all_button_text", "Select All"))
        self.posts_deselect_all_button.setText(self._tr("deselect_all_button_text", "Deselect All"))
        self.posts_add_selected_button.setText(self._tr("creator_popup_add_posts_to_queue_button", "Add Selected Posts to Queue")) # Placeholder key
        self.posts_close_button.setText(self._tr("fav_posts_cancel_button", "Cancel")) # Re-use cancel

    def _sync_scroll_dates(self, value):
        if not self._is_scrolling_titles: # Check flag
            self._is_scrolling_dates = True # Set own flag
            self.posts_date_list_widget.verticalScrollBar().setValue(value)
            self._is_scrolling_dates = False # Clear own flag

    def _sync_scroll_titles(self, value):
        if not self._is_scrolling_dates: # Check flag
            self._is_scrolling_titles = True # Set own flag
            self.posts_title_list_widget.verticalScrollBar().setValue(value)
            self._is_scrolling_titles = False # Clear own flag

    def _perform_initial_load (self ):
        """Called by QTimer to load data after dialog is shown."""
        self ._load_creators_from_json ()



    def _load_creators_from_json (self ):
        """Loads creators from creators.json and populates the list widget."""
        self .list_widget .clear ()

        self .progress_bar .setVisible (True )
        QCoreApplication .processEvents ()
        if not self .isVisible ():return 
        if getattr (sys ,'frozen',False )and hasattr (sys ,'_MEIPASS'):
            base_path_for_creators =sys ._MEIPASS 
        else :
            base_path_for_creators =self .app_base_dir 
        creators_file_path =os .path .join (base_path_for_creators ,"creators.json")

        if not os .path .exists (creators_file_path ):
            self .list_widget .addItem (f"Error: creators.json not found at {creators_file_path }")
            self .all_creators_data =[]
            self .progress_bar .setVisible (False )
            QCoreApplication .processEvents ()
            return 

        try :
            with open (creators_file_path ,'r',encoding ='utf-8')as f :
                data =json .load (f )
            QCoreApplication .processEvents ()
            if not self .isVisible ():return 

            raw_data_list =[]
            if isinstance (data ,list )and len (data )>0 and isinstance (data [0 ],list ):
                raw_data_list =data [0 ]
            elif isinstance (data ,list )and all (isinstance (item ,dict )for item in data ):
                raw_data_list =data 
            else :
                self .list_widget .addItem ("Error: Invalid format in creators.json.")
                self .all_creators_data =[]
                self .progress_bar .setVisible (False );QCoreApplication .processEvents ();return 


            unique_creators_map ={}
            duplicates_skipped_count =0 
            for creator_entry in raw_data_list :
                service =creator_entry .get ('service')
                creator_id =creator_entry .get ('id')
                name_for_log =creator_entry .get ('name','Unknown')

                if service and creator_id :
                    key =(str (service ).lower ().strip (),str (creator_id ).strip ())
                    if key not in unique_creators_map :
                        unique_creators_map [key ]=creator_entry 
                    else :
                        duplicates_skipped_count +=1 
                else :
                    print (f"Warning: Creator entry in creators.json missing service or ID: {name_for_log }")

            self .all_creators_data =list (unique_creators_map .values ())
            if duplicates_skipped_count >0 :
                print (f"INFO (Creator Popup): Skipped {duplicates_skipped_count } duplicate creator entries from creators.json based on (service, id).")

            self .all_creators_data .sort (key =lambda c :(-c .get ('favorited',0 ),c .get ('name','').lower ()))
            QCoreApplication .processEvents ()
            if not self .isVisible ():return 

        except json .JSONDecodeError :
            self .list_widget .addItem ("Error: Could not parse creators.json.")
            self .all_creators_data =[]
            self .progress_bar .setVisible (False );QCoreApplication .processEvents ();return 
        except Exception as e :
            self .list_widget .addItem (f"Error loading creators: {e }")
            self .all_creators_data =[]
            self .progress_bar .setVisible (False );QCoreApplication .processEvents ();return 



        self ._filter_list ()

    def _populate_list_widget (self ,creators_to_display ):
        """Clears and populates the list widget with the given creator data."""
        self .list_widget .blockSignals (True )
        self .list_widget .clear ()

        if not creators_to_display :
            self .list_widget .blockSignals (False )






            return 

        CHUNK_SIZE_POPULATE =100 
        for i in range (0 ,len (creators_to_display ),CHUNK_SIZE_POPULATE ):
            if not self .isVisible ():
                self .list_widget .blockSignals (False )
                return 

            chunk =creators_to_display [i :i +CHUNK_SIZE_POPULATE ]
            for creator in chunk :
                creator_name_raw =creator .get ('name')
                display_creator_name =creator_name_raw .strip ()if isinstance (creator_name_raw ,str )and creator_name_raw .strip ()else "Unknown Creator"
                service_display_name =creator .get ('service','N/A').capitalize ()
                display_text =f"{display_creator_name } ({service_display_name })"
                item =QListWidgetItem (display_text )
                item .setFlags (item .flags ()|Qt .ItemIsUserCheckable )
                item .setData (Qt .UserRole ,creator )
                service =creator .get ('service')
                creator_id =creator .get ('id')
                if service is not None and creator_id is not None :
                    unique_key =(str (service ),str (creator_id ))
                    if unique_key in self .globally_selected_creators :
                        item .setCheckState (Qt .Checked )
                    else :
                        item .setCheckState (Qt .Unchecked )
                else :
                    item .setCheckState (Qt .Unchecked )
                self .list_widget .addItem (item )

            QCoreApplication .processEvents ()

        self .list_widget .blockSignals (False )

    def _filter_list (self ):
        """Filters the list widget based on the search input."""
        raw_search_input =self .search_input .text ()



        check_search_text_for_empty =raw_search_input .lower ().strip ()

        QCoreApplication .processEvents ()
        if not self .isVisible ():return 

        if not check_search_text_for_empty :
            self .progress_bar .setVisible (False )
            creators_to_show =self .all_creators_data [:self .INITIAL_LOAD_LIMIT ]
            self ._populate_list_widget (creators_to_show )
            self .search_input .setToolTip ("Search by name, service, or paste creator URL...")
            QCoreApplication .processEvents ()
        else :
            self .progress_bar .setVisible (True )
            QCoreApplication .processEvents ()
            if not self .isVisible ():return 

            norm_search_casefolded =unicodedata .normalize ('NFKC',raw_search_input ).casefold ().strip ()








            scored_matches =[]


            parsed_service_from_url ,parsed_user_id_from_url ,_ =extract_post_info (raw_search_input )

            if parsed_service_from_url and parsed_user_id_from_url :

                self .search_input .setToolTip (f"Searching for URL: {raw_search_input [:50 ]}...")
                for creator_data in self .all_creators_data :
                    creator_service_lower =creator_data .get ('service','').lower ()

                    creator_id_str_lower =str (creator_data .get ('id','')).lower ()

                    if creator_service_lower ==parsed_service_from_url .lower ()and creator_id_str_lower ==parsed_user_id_from_url .lower ():
                        scored_matches .append ((5 ,creator_data ))

                        break 

            else :


                self .search_input .setToolTip ("Searching by name or service...")
                norm_search_casefolded =unicodedata .normalize ('NFKC',raw_search_input ).casefold ().strip ()

                CHUNK_SIZE_FILTER =500 
                for i in range (0 ,len (self .all_creators_data ),CHUNK_SIZE_FILTER ):
                    if not self .isVisible ():break 
                    chunk =self .all_creators_data [i :i +CHUNK_SIZE_FILTER ]
                    for creator_data in chunk :
                        creator_name_raw =creator_data .get ('name','')
                        creator_service_raw =creator_data .get ('service','')


                        norm_creator_name_casefolded =unicodedata .normalize ('NFKC',creator_name_raw ).casefold ()
                        norm_service_casefolded =unicodedata .normalize ('NFKC',creator_service_raw ).casefold ()

                        current_score =0 

                        if norm_search_casefolded ==norm_creator_name_casefolded :
                            current_score =4 

                        elif norm_creator_name_casefolded .startswith (norm_search_casefolded ):
                            current_score =3 

                        elif norm_search_casefolded in norm_creator_name_casefolded :
                            current_score =2 

                        elif norm_search_casefolded in norm_service_casefolded :
                            current_score =1 

                        if current_score >0 :
                            scored_matches .append ((current_score ,creator_data ))

                    QCoreApplication .processEvents ()



            scored_matches .sort (key =lambda x :(-x [0 ],unicodedata .normalize ('NFKC',x [1 ].get ('name','')).casefold ()))


            final_creators_to_display =[creator_data for score ,creator_data in scored_matches [:20 ]]

            self ._populate_list_widget (final_creators_to_display )
            self .progress_bar .setVisible (False )


            if parsed_service_from_url and parsed_user_id_from_url :
                if final_creators_to_display :
                    self .search_input .setToolTip (f"Found creator by URL: {final_creators_to_display [0 ].get ('name')}")
                else :
                    self .search_input .setToolTip (f"URL parsed, but no matching creator found in your creators.json.")
            else :
                if final_creators_to_display :
                    self .search_input .setToolTip (f"Showing top {len (final_creators_to_display )} match(es) for '{raw_search_input [:30 ]}...'")
                else :
                    self .search_input .setToolTip (f"No matches found for '{raw_search_input [:30 ]}...'")

    def _toggle_scope_mode (self ):
        """Toggles the scope mode and updates the button text."""
        if self .current_scope_mode ==self .SCOPE_CHARACTERS :
            self .current_scope_mode =self .SCOPE_CREATORS 
        else :
            self .current_scope_mode =self .SCOPE_CHARACTERS 
        self ._update_scope_button_text_and_tooltip ()

    def _update_scope_button_text_and_tooltip (self ):
        if self .current_scope_mode ==self .SCOPE_CHARACTERS :
            self .scope_button .setText (self ._tr ("creator_popup_scope_characters_button","Scope: Characters"))
        else :
            self .scope_button .setText (self ._tr ("creator_popup_scope_creators_button","Scope: Creators"))

        self .scope_button .setToolTip (
        f"Current Download Scope: {self .current_scope_mode }\n\n"
        f"Click to toggle between '{self .SCOPE_CHARACTERS }' and '{self .SCOPE_CREATORS }' scopes.\n"
        f"'{self .SCOPE_CHARACTERS }': Downloads into character-named folders directly in the main Download Location (artists mixed).\n"
        f"'{self .SCOPE_CREATORS }': Downloads into artist-named subfolders within the main Download Location, then character folders inside those.")

    def _handle_fetch_status_update(self, message):
        if self.parent_app:
            self.parent_app.log_signal.emit(f"[CreatorPopup Fetch] {message}")
        self.posts_area_title_label.setText(message)

    def _handle_posts_fetched(self, creator_info, posts_list):
        creator_key = (creator_info.get('service'), str(creator_info.get('id')))
        # Store both creator_info and the posts_list
        self.fetched_posts_data[creator_key] = (creator_info, posts_list)
        self._filter_fetched_posts_list() # Refresh list with current filter

    def _filter_fetched_posts_list(self):
        search_text = self.posts_search_input.text().lower().strip()
        
        data_for_rebuild = {} 

        if not self.fetched_posts_data:
            self.posts_area_title_label.setText(self._tr("no_posts_fetched_yet_status", "No posts fetched yet."))
        elif not search_text:
            data_for_rebuild = self.fetched_posts_data
            # Adjust for tuple structure: (creator_info, posts_list)
            total_posts_in_view = sum(len(posts_tuple[1]) for posts_tuple in data_for_rebuild.values())
            if total_posts_in_view > 0:
                self.posts_area_title_label.setText(self._tr("fetched_posts_count_label", "Fetched {count} post(s). Select to add to queue.").format(count=total_posts_in_view))
            else: 
                self.posts_area_title_label.setText(self._tr("no_posts_found_for_selection", "No posts found for selected creator(s)."))
        else: 
            for creator_key, (creator_data_tuple_part, posts_list_tuple_part) in self.fetched_posts_data.items(): # Unpack tuple
                matching_posts_for_creator = [
                    post for post in posts_list_tuple_part # Use posts_list_tuple_part
                    if search_text in post.get('title', '').lower()
                ]
                if matching_posts_for_creator:
                    # Store the tuple back, with original creator_info and filtered posts
                    data_for_rebuild[creator_key] = (creator_data_tuple_part, matching_posts_for_creator)
            
            # Adjust for tuple structure
            total_matching_posts = sum(len(posts_tuple[1]) for posts_tuple in data_for_rebuild.values())
            if total_matching_posts > 0:
                self.posts_area_title_label.setText(self._tr("fetched_posts_count_label_filtered", "Displaying {count} post(s) matching filter.").format(count=total_matching_posts))
            else:
                self.posts_area_title_label.setText(self._tr("no_posts_match_search_filter", "No posts match your search filter."))
        
        self._rebuild_posts_list_widget(filtered_data_map=data_for_rebuild)

    def _rebuild_posts_list_widget(self, filtered_data_map):
        self.posts_title_list_widget.blockSignals(True) # Block signals during repopulation
        self.posts_date_list_widget.blockSignals(True)       
        self.posts_title_list_widget.clear()
        self.posts_date_list_widget.clear() # Clear date list as well
        data_to_display = filtered_data_map 

        if not data_to_display:
            self.posts_title_list_widget.blockSignals(False) # Corrected widget name
            self.posts_date_list_widget.blockSignals(False)                      
            return

        # Sort creator keys based on the name stored within the fetched data tuple
        sorted_creator_keys = sorted(
            data_to_display.keys(),
            key=lambda k: data_to_display[k][0].get('name', '').lower() # data_to_display[k] is (creator_info, posts_list)
        )

        total_posts_shown = 0
        for creator_key in sorted_creator_keys:
            # Get creator_info and posts_for_this_creator from the stored tuple
            creator_info_original, posts_for_this_creator = data_to_display.get(creator_key, (None, []))

            if not creator_info_original or not posts_for_this_creator: # Ensure both parts of tuple are valid
                continue
            
            creator_header_item = QListWidgetItem(f"--- {self._tr('posts_for_creator_header', 'Posts for')} {creator_info_original['name']} ({creator_info_original['service']}) ---")
            font = creator_header_item.font()
            font.setBold(True)
            creator_header_item.setFont(font)
            creator_header_item.setFlags(Qt.NoItemFlags)
            self.posts_title_list_widget.addItem(creator_header_item)
            self.posts_date_list_widget.addItem(QListWidgetItem("")) # Add empty item to date list for spacing

            for post in posts_for_this_creator:
                post_title = post.get('title', self._tr('untitled_post_placeholder', 'Untitled Post'))

                # Add date prefix
                date_prefix_str = "[No Date]" # Default
                published_date_str = post.get('published')
                added_date_str = post.get('added')
                
                date_to_use_str = None
                if published_date_str:
                    date_to_use_str = published_date_str
                elif added_date_str:
                    date_to_use_str = added_date_str
                
                if date_to_use_str:
                    try:
                        # Assuming date is in ISO format like YYYY-MM-DDTHH:MM:SS
                        formatted_date = date_to_use_str.split('T')[0]
                        date_prefix_str = f"[{formatted_date}]"
                    except Exception: # pylint: disable=bare-except
                        pass # Keep "[No Date]" if parsing fails
                            
                # Determine date string
                date_display_str = "[No Date]" # Default
                published_date_str = post.get('published')
                added_date_str = post.get('added')
                
                date_to_use_str = None
                if published_date_str:
                    date_to_use_str = published_date_str
                elif added_date_str:
                    date_to_use_str = added_date_str
                
                if date_to_use_str:
                    try:
                        # Assuming date is in ISO format like YYYY-MM-DDTHH:MM:SS
                        formatted_date = date_to_use_str.split('T')[0]
                        date_display_str = f"[{formatted_date}]"
                    except Exception: # pylint: disable=bare-except
                        pass # Keep "[No Date]" if parsing fails
                
                # Title item
                title_item_text = f"  {post_title}" # Display full title, QListWidget handles ellipsis
                item = QListWidgetItem(title_item_text)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                item_data = {
                    'title': post_title,
                    'id': post.get('id'),
                    'service': creator_info_original['service'],
                    'user_id': creator_info_original['id'],
                    'creator_name': creator_info_original['name'],
                    'full_post_data': post,
                    'date_display_str': date_display_str, # Store formatted date for easy access
                    'published_date_for_sort': date_to_use_str # Store raw date for potential future sorting
                }
                item.setData(Qt.UserRole, item_data)
                post_unique_key = (
                    item_data['service'],
                    str(item_data['user_id']), 
                    str(item_data['id'])      
                )
                if post_unique_key in self.globally_selected_post_ids:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
              
                self.posts_title_list_widget.addItem(item)
                total_posts_shown += 1
                # Date item (purely display)
                date_item = QListWidgetItem(f"  {date_display_str}")
                date_item.setFlags(Qt.NoItemFlags) # Not selectable, not checkable
                self.posts_date_list_widget.addItem(date_item)

        self.posts_title_list_widget.blockSignals(False) # Unblock signals
        self.posts_date_list_widget.blockSignals(False)

    def _handle_fetch_error(self, creator_info, error_message):
        creator_name = creator_info.get('name', 'Unknown Creator')
        if self.parent_app:
            self.parent_app.log_signal.emit(f"[CreatorPopup Fetch ERROR] For {creator_name}: {error_message}")
        # Update title label to show there was an error for this creator
        self.posts_area_title_label.setText(self._tr("fetch_error_for_creator_label", "Error fetching for {creator_name}").format(creator_name=creator_name))


    def _handle_fetch_finished(self):
        self.fetch_posts_button.setEnabled(True)
        self.progress_bar.setVisible(False)

        if not self.fetched_posts_data: 
            if self.post_fetch_thread and self.post_fetch_thread.cancellation_flag.is_set():
                 self.posts_area_title_label.setText(self._tr("post_fetch_cancelled_status_done", "Post fetching cancelled."))
            else:
                 self.posts_area_title_label.setText(self._tr("failed_to_fetch_or_no_posts_label", "Failed to fetch posts or no posts found."))
            self.posts_search_input.setVisible(False)
        elif not self.posts_title_list_widget.count() and not self.posts_search_input.text().strip():
            self.posts_area_title_label.setText(self._tr("no_posts_found_for_selection", "No posts found for selected creator(s)."))
            self.posts_search_input.setVisible(True) 
        else: 
            QTimer.singleShot(10, lambda: self.posts_content_splitter.setSizes([int(self.posts_content_splitter.width() * 0.7), int(self.posts_content_splitter.width() * 0.3)]))
            self.posts_search_input.setVisible(True)

    def _handle_posts_select_all(self):
        self.posts_title_list_widget.blockSignals(True)      
        for i in range(self.posts_title_list_widget.count()):
            item = self.posts_title_list_widget.item(i)
            if item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(Qt.Checked)

                # Add to global selection if not already there
                item_data = item.data(Qt.UserRole)
                if item_data:
                    post_unique_key = (
                        item_data['service'],
                        str(item_data['user_id']),
                        str(item_data['id'])
                    )
                    self.globally_selected_post_ids.add(post_unique_key)
        self.posts_title_list_widget.blockSignals(False)

    def _handle_posts_deselect_all(self):
        self.posts_title_list_widget.blockSignals(True)      
        for i in range(self.posts_title_list_widget.count()):
            item = self.posts_title_list_widget.item(i)
            if item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(Qt.Unchecked)
        self.globally_selected_post_ids.clear() # Deselect all means clear all global selections
        self.posts_title_list_widget.blockSignals(False)

    def _handle_post_item_check_changed(self, item):
        if not item or not item.data(Qt.UserRole): # Ignore header items or invalid items
            return

        item_data = item.data(Qt.UserRole)
        post_unique_key = (
            item_data['service'],
            str(item_data['user_id']),
            str(item_data['id'])
        )

        if item.checkState() == Qt.Checked:
            self.globally_selected_post_ids.add(post_unique_key)
        else:
            self.globally_selected_post_ids.discard(post_unique_key)

    def _handle_posts_add_selected_to_queue(self):
        selected_posts_for_queue = []
        if not self.globally_selected_post_ids:
            QMessageBox.information(self, self._tr("no_selection_title", "No Selection"),
                                    self._tr("select_posts_to_queue_message", "Please select at least one post to add to the queue."))
            return

        for post_key in self.globally_selected_post_ids:
            service, user_id_str, post_id_str = post_key
            post_data_found = None
            creator_key_for_fetched_data = (service, user_id_str)
            
            # Access posts from the tuple structure in self.fetched_posts_data
            if creator_key_for_fetched_data in self.fetched_posts_data:
                _unused_creator_info, posts_in_list_for_creator = self.fetched_posts_data[creator_key_for_fetched_data]
                for post_in_list in posts_in_list_for_creator:
                    if str(post_in_list.get('id')) == post_id_str:
                        post_data_found = post_in_list
                        break
            
            if post_data_found:
                # Get creator_info from the fetched_posts_data tuple
                creator_info_original, _unused_posts = self.fetched_posts_data.get(creator_key_for_fetched_data, ({}, []))
                creator_name = creator_info_original.get('name', 'Unknown Creator') if creator_info_original else 'Unknown Creator'
                
                domain = self._get_domain_for_service(service)
                post_url = f"https://{domain}/{service}/user/{user_id_str}/post/{post_id_str}"
                queue_item = {
                    'type': 'single_post_from_popup',
                    'url': post_url,
                    'name': post_data_found.get('title', self._tr('untitled_post_placeholder', 'Untitled Post')),
                    'name_for_folder': creator_name, 
                    'service': service,
                    'user_id': user_id_str,
                    'post_id': post_id_str
                }
                selected_posts_for_queue.append(queue_item)
            else:
                # This case might happen if fetched_posts_data was cleared or modified unexpectedly
                # For robustness, we could try to reconstruct minimal info if needed,
                # or log that the full data for a selected post was not found.
                # For now, just log it if parent_app is available.
                if self.parent_app and hasattr(self.parent_app, 'log_signal'):
                    self.parent_app.log_signal.emit(f"⚠️ Could not find full post data for selected key: {post_key} when adding to queue.")
                # Fallback: create a queue item with minimal info from the key itself
                else: # Minimal fallback if full data is gone
                    domain = self._get_domain_for_service(service)
                    post_url = f"https://{domain}/{service}/user/{user_id_str}/post/{post_id_str}"
                    queue_item = {
                        'type': 'single_post_from_popup',
                        'url': post_url,
                        'name': f"post id {post_id_str}", # fallback name
                        'name_for_folder': user_id_str, # fallback folder name
                        'service': service,
                        'user_id': user_id_str,
                        'post_id': post_id_str
                    }
                    selected_posts_for_queue.append(queue_item)

        if selected_posts_for_queue:
            if self.parent_app and hasattr(self.parent_app, 'favorite_download_queue'):
                for qi in selected_posts_for_queue:
                    self.parent_app.favorite_download_queue.append(qi)
                self.parent_app.log_signal.emit(f"ℹ️ Added {len(selected_posts_for_queue)} selected posts to the download queue.")
                if self.parent_app.link_input:
                    self.parent_app.link_input.setPlaceholderText(
                        self._tr("items_in_queue_placeholder", "{count} items in queue from popup.").format(count=len(self.parent_app.favorite_download_queue))
                    )
                    self.parent_app.link_input.clear()
            self.accept()
        else:
            QMessageBox.information(self, self._tr("no_selection_title", "No Selection"),
                                    self._tr("select_posts_to_queue_message", "Please select at least one post to add to the queue."))

    def _handle_posts_close_view(self):
        self.right_pane_widget.hide()
        self.main_splitter.setSizes([self.width(), 0])
        self.posts_list_widget.itemChanged.disconnect(self._handle_post_item_check_changed) # Disconnect    
        if hasattr(self, '_handle_post_item_check_changed'): # Check if connected before disconnecting
            self.posts_title_list_widget.itemChanged.disconnect(self._handle_post_item_check_changed)      
        self.posts_search_input.setVisible(False)
        self.posts_search_input.clear()
        self.globally_selected_post_ids.clear()        
        self.add_selected_button.setEnabled(True)
        self.setWindowTitle(self._tr("creator_popup_title", "Creator Selection"))
        # Optionally clear posts list and data
        # self.posts_list_widget.clear()
        # self.fetched_posts_data.clear()

    def _get_domain_for_service (self ,service_name ):
        """Determines the base domain for a given service."""
        service_lower =service_name .lower ()
        if service_lower in ['onlyfans','fansly']:
            return "coomer.su"
        return "kemono.su"

    def _handle_add_selected (self ):
        """Gathers globally selected creators and processes them."""
        selected_display_names =[]
        self .selected_creators_for_queue .clear ()
        for creator_data in self .globally_selected_creators .values ():
            creator_name =creator_data .get ('name')
            self .selected_creators_for_queue .append (creator_data )
            if creator_name :
                selected_display_names .append (creator_name )

        if selected_display_names :
            main_app_window =self .parent ()
            if hasattr (main_app_window ,'link_input'):
                main_app_window .link_input .setText (", ".join (selected_display_names ))
            self .accept ()
        else :
            QMessageBox .information (self ,"No Selection","No creators selected to add.")

    def _handle_item_check_changed (self ,item ):
        """Updates the globally_selected_creators dict when an item's check state changes."""
        creator_data =item .data (Qt .UserRole )
        if not isinstance (creator_data ,dict ):
            return 

        service =creator_data .get ('service')
        creator_id =creator_data .get ('id')

        if service is None or creator_id is None :
            print (f"Warning: Creator data in list item missing service or id: {creator_data .get ('name')}")
            return 

        unique_key =(str (service ),str (creator_id ))

        if item .checkState ()==Qt .Checked :
            self .globally_selected_creators [unique_key ]=creator_data 
        else :
            if unique_key in self .globally_selected_creators :
                del self .globally_selected_creators [unique_key ]
        self.fetch_posts_button.setEnabled(bool(self.globally_selected_creators))

class PostsFetcherThread(QThread):
    status_update = pyqtSignal(str)
    posts_fetched_signal = pyqtSignal(object, list) # creator_info (dict), posts_list
    fetch_error_signal = pyqtSignal(object, str)   # creator_info (dict), error_message
    finished_signal = pyqtSignal()

    def __init__(self, creators_to_fetch, parent_dialog_ref):
        super().__init__()
        self.creators_to_fetch = creators_to_fetch
        self.parent_dialog = parent_dialog_ref
        self.cancellation_flag = threading.Event() # Use a threading.Event for cancellation

    def cancel(self):
        self.cancellation_flag.set() # Set the event
        self.status_update.emit(self.parent_dialog._tr("post_fetch_cancelled_status", "Post fetching cancellation requested..."))

    def run(self):
        if not self.creators_to_fetch:
            self.status_update.emit(self.parent_dialog._tr("no_creators_to_fetch_status", "No creators selected to fetch posts for."))
            self.finished_signal.emit()
            return

        for creator_data in self.creators_to_fetch:
            if self.cancellation_flag.is_set(): # Check the event
                break
            
            creator_name = creator_data.get('name', 'Unknown Creator')
            service = creator_data.get('service')
            user_id = creator_data.get('id')

            if not service or not user_id:
                self.fetch_error_signal.emit(creator_data, f"Missing service or ID for {creator_name}")
                continue

            self.status_update.emit(self.parent_dialog._tr("fetching_posts_for_creator_status_all_pages", "Fetching all posts for {creator_name} ({service})... This may take a while.").format(creator_name=creator_name, service=service))
            
            domain = self.parent_dialog._get_domain_for_service(service)
            api_url_base = f"https://{domain}/api/v1/{service}/user/{user_id}"
            
            # download_from_api will handle cookie preparation based on these params
            use_cookie_param = False
            cookie_text_param = ""
            selected_cookie_file_param = None
            app_base_dir_param = None

            if self.parent_dialog.parent_app:
                app = self.parent_dialog.parent_app
                use_cookie_param = app.use_cookie_checkbox.isChecked()
                cookie_text_param = app.cookie_text_input.text().strip()
                selected_cookie_file_param = app.selected_cookie_filepath
                app_base_dir_param = app.app_base_dir

            all_posts_for_this_creator = [] 
            try:
                post_generator = download_from_api(
                    api_url_base,
                    logger=lambda msg: self.status_update.emit(f"[API Fetch - {creator_name}] {msg}"),
                    # end_page=1, # REMOVED to fetch all pages
                    use_cookie=use_cookie_param,
                    cookie_text=cookie_text_param,
                    selected_cookie_file=selected_cookie_file_param,
                    app_base_dir=app_base_dir_param, # corrected comma
                    manga_filename_style_for_sort_check=None, # PostsFetcherThread doesn't use manga mode settings for its own fetching
                    cancellation_event=self.cancellation_flag
                )
                
                for posts_batch in post_generator:
                    if self.cancellation_flag.is_set(): # Check event here as well
                        self.status_update.emit(f"Post fetching for {creator_name} cancelled during pagination.")
                        break 
                    all_posts_for_this_creator.extend(posts_batch)
                    self.status_update.emit(f"Fetched {len(all_posts_for_this_creator)} posts so far for {creator_name}...")

                if not self.cancellation_flag.is_set():
                    self.posts_fetched_signal.emit(creator_data, all_posts_for_this_creator)
                    self.status_update.emit(f"Finished fetching {len(all_posts_for_this_creator)} posts for {creator_name}.")
                else:
                    self.posts_fetched_signal.emit(creator_data, all_posts_for_this_creator) # Emit partial if any
                    self.status_update.emit(f"Fetching for {creator_name} cancelled. {len(all_posts_for_this_creator)} posts collected.")

            except RuntimeError as e: 
                if "cancelled by user" in str(e).lower() or self.cancellation_flag.is_set():
                    self.status_update.emit(f"Post fetching for {creator_name} cancelled: {e}")
                    self.posts_fetched_signal.emit(creator_data, all_posts_for_this_creator) 
                else:
                    self.fetch_error_signal.emit(creator_data, f"Runtime error fetching posts for {creator_name}: {e}")
            except Exception as e:
                self.fetch_error_signal.emit(creator_data, f"Error fetching posts for {creator_name}: {e}")
            
            if self.cancellation_flag.is_set():
                break
            QThread.msleep(200)

        if self.cancellation_flag.is_set():
            self.status_update.emit(self.parent_dialog._tr("post_fetch_cancelled_status_done", "Post fetching cancelled."))
        else:
            self.status_update.emit(self.parent_dialog._tr("post_fetch_finished_status", "Finished fetching posts for selected creators."))
        self.finished_signal.emit()

class CookieHelpDialog (QDialog ):
    """A dialog to explain how to get a cookies.txt file."""
    CHOICE_PROCEED_WITHOUT_COOKIES =1 
    CHOICE_CANCEL_DOWNLOAD =2 
    CHOICE_OK_INFO_ONLY =3 
    _is_scrolling_titles = False # For scroll synchronization
    _is_scrolling_dates = False  # For scroll synchronization

    def __init__ (self ,parent_app ,parent =None ,offer_download_without_option =False ):
        super ().__init__ (parent )
        self .parent_app =parent_app 
        self .setModal (True )
        self .offer_download_without_option =offer_download_without_option 

        app_icon = get_app_icon_object()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        self .user_choice =None 
        main_layout =QVBoxLayout (self )

        self .info_label =QLabel ()
        self .info_label .setTextFormat (Qt .RichText )
        self .info_label .setOpenExternalLinks (True )
        self .info_label .setWordWrap (True )
        main_layout .addWidget (self .info_label )
        button_layout =QHBoxLayout ()
        if self .offer_download_without_option :
            button_layout .addStretch (1 )

            self .download_without_button =QPushButton ()
            self .download_without_button .clicked .connect (self ._proceed_without_cookies )
            button_layout .addWidget (self .download_without_button )

            self .cancel_button =QPushButton ()
            self .cancel_button .clicked .connect (self ._cancel_download )
            button_layout .addWidget (self .cancel_button )
        else :
            button_layout .addStretch (1 )
            self .ok_button =QPushButton ()
            self .ok_button .clicked .connect (self ._ok_info_only )
            button_layout .addWidget (self .ok_button )

        main_layout .addLayout (button_layout )

        self ._retranslate_ui ()

        if self .parent_app and hasattr (self .parent_app ,'get_dark_theme')and self .parent_app .current_theme =="dark":
            self .setStyleSheet (self .parent_app .get_dark_theme ())
        self .setMinimumWidth (500 )

    def _tr (self ,key ,default_text =""):
        if callable (get_translation )and self .parent_app :
            return get_translation (self .parent_app .current_selected_language ,key ,default_text )
        return default_text 

    def _retranslate_ui (self ):
        self .setWindowTitle (self ._tr ("cookie_help_dialog_title","Cookie File Instructions"))
        instruction_html =f"""
        {self ._tr ("cookie_help_instruction_intro","<p>To use cookies...</p>")}
        {self ._tr ("cookie_help_how_to_get_title","<p><b>How to get cookies.txt:</b></p>")}
        <ol>
            {self ._tr ("cookie_help_step1_extension_intro","<li>Install extension...</li>")}
            {self ._tr ("cookie_help_step2_login","<li>Go to website...</li>")}
            {self ._tr ("cookie_help_step3_click_icon","<li>Click icon...</li>")}
            {self ._tr ("cookie_help_step4_export","<li>Click export...</li>")}
            {self ._tr ("cookie_help_step5_save_file","<li>Save file...</li>")}
            {self ._tr ("cookie_help_step6_app_intro","<li>In this application:<ul>")}
            {self ._tr ("cookie_help_step6a_checkbox","<li>Ensure checkbox...</li>")}
            {self ._tr ("cookie_help_step6b_browse","<li>Click browse...</li>")}
            {self ._tr ("cookie_help_step6c_select","<li>Select file...</li></ul></li>")}
        </ol>
        {self ._tr ("cookie_help_alternative_paste","<p>Alternatively, paste...</p>")}
        """
        self .info_label .setText (instruction_html )

        if self .offer_download_without_option :
            self .download_without_button .setText (self ._tr ("cookie_help_proceed_without_button","Download without Cookies"))
            self .cancel_button .setText (self ._tr ("cookie_help_cancel_download_button","Cancel Download"))
        else :
            self .ok_button .setText (self ._tr ("ok_button","OK"))

    def _proceed_without_cookies (self ):
        self .user_choice =self .CHOICE_PROCEED_WITHOUT_COOKIES 
        self .accept ()

    def _cancel_download (self ):
        self .user_choice =self .CHOICE_CANCEL_DOWNLOAD 
        self .reject ()

    def _ok_info_only (self ):
        self .user_choice =self .CHOICE_OK_INFO_ONLY 
        self .accept ()

class DownloadHistoryDialog(QDialog):
    """Dialog to display download history."""
    def __init__(self, last_3_downloaded_entries, first_processed_entries, parent_app, parent=None):
        super().__init__(parent)
        self.parent_app = parent_app
        self.last_3_downloaded_entries = last_3_downloaded_entries
        self.first_processed_entries = first_processed_entries
        self.setModal(True)
        
        app_icon = get_app_icon_object()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)

        screen_height = QApplication.primaryScreen().availableGeometry().height() if QApplication.primaryScreen() else 768
        scale_factor = screen_height / 768.0
        base_min_w, base_min_h = 600, 450
        # Increase width to accommodate two panes
        scaled_min_w = int(base_min_w * 1.5 * scale_factor) 
        scaled_min_h = int(base_min_h * scale_factor)
        self.setMinimumSize(scaled_min_w, scaled_min_h)

        self.setWindowTitle(self._tr("download_history_dialog_title_combined", "Download History"))
                
        # Main layout for the dialog will be a QVBoxLayout
        dialog_layout = QVBoxLayout(self)
        self.setLayout(dialog_layout)

        # --- Splitter ---
        self.main_splitter = QSplitter(Qt.Horizontal)
        dialog_layout.addWidget(self.main_splitter)

        # --- Left Pane (Last 3 Downloaded Files) ---
        left_pane_widget = QWidget()
        left_layout = QVBoxLayout(left_pane_widget)
        left_header_label = QLabel(self._tr("history_last_downloaded_header", "Last 3 Files Downloaded:"))
        left_header_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(left_header_label)

        left_scroll_area = QScrollArea()
        left_scroll_area.setWidgetResizable(True)
        left_scroll_content_widget = QWidget()
        left_scroll_layout = QVBoxLayout(left_scroll_content_widget)

        if not self.last_3_downloaded_entries:
            no_left_history_label = QLabel(self._tr("no_download_history_header", "No Downloads Yet"))
            no_left_history_label.setAlignment(Qt.AlignCenter)
            left_scroll_layout.addWidget(no_left_history_label)
        else:
            for entry in self.last_3_downloaded_entries:
                group_box = QGroupBox(f"{self._tr('history_file_label', 'File:')} {entry.get('disk_filename', 'N/A')}")
                group_layout = QVBoxLayout(group_box)
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
                group_layout.addWidget(details_label)
                left_scroll_layout.addWidget(group_box)
        left_scroll_area.setWidget(left_scroll_content_widget)
        left_layout.addWidget(left_scroll_area)
        self.main_splitter.addWidget(left_pane_widget)

        # --- Right Pane (First Processed Posts) ---
        right_pane_widget = QWidget()
        right_layout = QVBoxLayout(right_pane_widget)
        right_header_label = QLabel(self._tr("first_files_processed_header", "First {count} Posts Processed This Session:").format(count=len(self.first_processed_entries)))
        right_header_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(right_header_label)

        right_scroll_area = QScrollArea()
        right_scroll_area.setWidgetResizable(True)
        right_scroll_content_widget = QWidget()
        right_scroll_layout = QVBoxLayout(right_scroll_content_widget)

        if not self.first_processed_entries:
            no_right_history_label = QLabel(self._tr("no_processed_history_header", "No Posts Processed Yet"))
            no_right_history_label.setAlignment(Qt.AlignCenter)
            right_scroll_layout.addWidget(no_right_history_label)
        else:
            for entry in self.first_processed_entries:
                # Using 'Post:' for the group title as it's more accurate for this section
                group_box = QGroupBox(f"{self._tr('history_post_label', 'Post:')} {entry.get('post_title', 'N/A')} (ID: {entry.get('post_id', 'N/A')})")
                group_layout = QVBoxLayout(group_box)
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
                group_layout.addWidget(details_label)
                right_scroll_layout.addWidget(group_box)
        right_scroll_area.setWidget(right_scroll_content_widget)
        right_layout.addWidget(right_scroll_area)
        self.main_splitter.addWidget(right_pane_widget)

        # Set initial splitter sizes (e.g., 50/50)
        QTimer.singleShot(0, lambda: self.main_splitter.setSizes([self.width() // 2, self.width() // 2]))

        # --- Bottom Button Layout ---
        bottom_button_layout = QHBoxLayout()
        self.save_history_button = QPushButton(self._tr("history_save_button_text", "Save History to .txt"))
        self.save_history_button.clicked.connect(self._save_history_to_txt)
        bottom_button_layout.addStretch(1) # Push to the right
        bottom_button_layout.addWidget(self.save_history_button)
        # Add this new layout to the main dialog layout
        dialog_layout.addLayout(bottom_button_layout)

        if self.parent_app and hasattr(self.parent_app, 'get_dark_theme') and self.parent_app.current_theme == "dark":
            self.setStyleSheet(self.parent_app.get_dark_theme())

    def _tr(self, key, default_text=""):
        if callable(get_translation) and self.parent_app:
            return get_translation(self.parent_app.current_selected_language, key, default_text)
        return default_text

    def _save_history_to_txt(self):
        if not self.last_3_downloaded_entries and not self.first_processed_entries:
            QMessageBox.information(self, self._tr("no_download_history_header", "No Downloads Yet"),
                                    self._tr("history_nothing_to_save_message", "There is no history to save."))
            return

        main_download_dir = self.parent_app.dir_input.text().strip()
        default_save_dir = ""
        if main_download_dir and os.path.isdir(main_download_dir):
            default_save_dir = main_download_dir
        else:
            fallback_dir = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
            if fallback_dir and os.path.isdir(fallback_dir):
                default_save_dir = fallback_dir
            else:
                default_save_dir = self.parent_app.app_base_dir

        default_filepath = os.path.join(default_save_dir, "download_history.txt")

        filepath, _ = QFileDialog.getSaveFileName(
            self, self._tr("history_save_dialog_title", "Save Download History"),
            default_filepath, "Text Files (*.txt);;All Files (*)"
        )

        if not filepath:
            return

        history_content = []
        history_content.append(f"{self._tr('history_last_downloaded_header', 'Last 3 Files Downloaded:')}\n")
        if self.last_3_downloaded_entries:
            for entry in self.last_3_downloaded_entries:
                history_content.append(f"  {self._tr('history_file_label', 'File:')} {entry.get('disk_filename', 'N/A')}")
                history_content.append(f"    {self._tr('history_from_post_label', 'From Post:')} {entry.get('post_title', 'N/A')} (ID: {entry.get('post_id', 'N/A')})")
                history_content.append(f"    {self._tr('history_creator_series_label', 'Creator/Series:')} {entry.get('creator_display_name', 'N/A')}")
                history_content.append(f"    {self._tr('history_post_uploaded_label', 'Post Uploaded:')} {entry.get('upload_date_str', 'N/A')}")
                history_content.append(f"    {self._tr('history_file_downloaded_label', 'File Downloaded:')} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry.get('download_timestamp', 0)))}")
                history_content.append(f"    {self._tr('history_saved_in_folder_label', 'Saved In Folder:')} {entry.get('download_path', 'N/A')}\n")
        else:
            history_content.append(f"  ({self._tr('no_download_history_header', 'No Downloads Yet')})\n")

        history_content.append(f"\n{self._tr('first_files_processed_header', 'First {count} Posts Processed This Session:').format(count=len(self.first_processed_entries))}\n")
        if self.first_processed_entries:
            for entry in self.first_processed_entries:
                history_content.append(f"  {self._tr('history_post_label', 'Post:')} {entry.get('post_title', 'N/A')} (ID: {entry.get('post_id', 'N/A')})")
                history_content.append(f"    {self._tr('history_creator_label', 'Creator:')} {entry.get('creator_name', 'N/A')}")
                history_content.append(f"    {self._tr('history_top_file_label', 'Top File:')} {entry.get('top_file_name', 'N/A')}")
                history_content.append(f"    {self._tr('history_num_files_label', 'Num Files in Post:')} {entry.get('num_files', 0)}")
                history_content.append(f"    {self._tr('history_post_uploaded_label', 'Post Uploaded:')} {entry.get('upload_date_str', 'N/A')}")
                history_content.append(f"    {self._tr('history_processed_on_label', 'Processed On:')} {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry.get('download_date_timestamp', 0)))}")
                history_content.append(f"    {self._tr('history_saved_to_folder_label', 'Saved To Folder:')} {entry.get('download_location', 'N/A')}\n")
        else:
            history_content.append(f"  ({self._tr('no_processed_history_header', 'No Posts Processed Yet')})\n")

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(history_content))
            QMessageBox.information(self, self._tr("history_export_success_title", "History Export Successful"),
                                    self._tr("history_export_success_message", "Successfully exported download history to:\n{filepath}").format(filepath=filepath))
        except Exception as e:
            QMessageBox.critical(self, self._tr("history_export_error_title", "History Export Error"),
                                 self._tr("history_export_error_message", "Could not export download history: {error}").format(error=str(e)))

class KnownNamesFilterDialog (QDialog ):
    """A dialog to select names from Known.txt to add to the filter input."""
    def __init__ (self ,known_names_list ,parent_app_ref ,parent =None ):
        super ().__init__ (parent )
        self .parent_app =parent_app_ref 
        self .setModal (True )
        self .all_known_name_entries =sorted (known_names_list ,key =lambda x :x ['name'].lower ())

        app_icon = get_app_icon_object()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        self .selected_entries_to_return =[]

        main_layout =QVBoxLayout (self )

        self .search_input =QLineEdit ()
        self .search_input .textChanged .connect (self ._filter_list_display )
        main_layout .addWidget (self .search_input )

        self .names_list_widget =QListWidget ()
        main_layout .addWidget (self .names_list_widget )

        buttons_layout =QHBoxLayout ()

        self .select_all_button =QPushButton ()
        self .select_all_button .clicked .connect (self ._select_all_items )
        buttons_layout .addWidget (self .select_all_button )

        self .deselect_all_button =QPushButton ()
        self .deselect_all_button .clicked .connect (self ._deselect_all_items )
        buttons_layout .addWidget (self .deselect_all_button )
        buttons_layout .addStretch (1 )

        self .add_button =QPushButton ()
        self .add_button .clicked .connect (self ._accept_selection_action )
        buttons_layout .addWidget (self .add_button )

        self .cancel_button =QPushButton ()
        self .cancel_button .clicked .connect (self .reject )
        buttons_layout .addWidget (self .cancel_button )
        main_layout .addLayout (buttons_layout )

        self ._retranslate_ui ()
        self ._populate_list_widget ()

        self .setMinimumWidth (350 )
        self .setMinimumHeight (400 )
        if self .parent_app and hasattr (self .parent_app ,'get_dark_theme')and self .parent_app .current_theme =="dark":
            self .setStyleSheet (self .parent_app .get_dark_theme ())
        self .add_button .setDefault (True )

    def _tr (self ,key ,default_text =""):
        """Helper to get translation based on current app language."""
        if callable (get_translation )and self .parent_app :
            return get_translation (self .parent_app .current_selected_language ,key ,default_text )
        return default_text 

    def _retranslate_ui (self ):
        self .setWindowTitle (self ._tr ("known_names_filter_dialog_title","Add Known Names to Filter"))
        self .search_input .setPlaceholderText (self ._tr ("known_names_filter_search_placeholder","Search names..."))
        self .select_all_button .setText (self ._tr ("known_names_filter_select_all_button","Select All"))
        self .deselect_all_button .setText (self ._tr ("known_names_filter_deselect_all_button","Deselect All"))
        self .add_button .setText (self ._tr ("known_names_filter_add_selected_button","Add Selected"))
        self .cancel_button .setText (self ._tr ("fav_posts_cancel_button","Cancel"))

    def _populate_list_widget (self ,names_to_display =None ):
        self .names_list_widget .clear ()
        current_entries_source =names_to_display if names_to_display is not None else self .all_known_name_entries 
        for entry_obj in current_entries_source :
            item =QListWidgetItem (entry_obj ['name'])
            item .setFlags (item .flags ()|Qt .ItemIsUserCheckable )
            item .setCheckState (Qt .Unchecked )
            item .setData (Qt .UserRole ,entry_obj )
            self .names_list_widget .addItem (item )

    def _filter_list_display (self ):
        search_text =self .search_input .text ().lower ()
        if not search_text :
            self ._populate_list_widget ()
            return 
        filtered_entries =[
        entry_obj for entry_obj in self .all_known_name_entries if search_text in entry_obj ['name'].lower ()
        ]
        self ._populate_list_widget (filtered_entries )

    def _accept_selection_action (self ):
        self .selected_entries_to_return =[]
        for i in range (self .names_list_widget .count ()):
            item =self .names_list_widget .item (i )
            if item .checkState ()==Qt .Checked :
                self .selected_entries_to_return .append (item .data (Qt .UserRole ))
        self .accept ()

    def _select_all_items (self ):
        """Checks all items in the list widget."""
        for i in range (self .names_list_widget .count ()):
            self .names_list_widget .item (i ).setCheckState (Qt .Checked )

    def _deselect_all_items (self ):
        """Unchecks all items in the list widget."""
        for i in range (self .names_list_widget .count ()):
            self .names_list_widget .item (i ).setCheckState (Qt .Unchecked )

    def get_selected_entries (self ):
        return self .selected_entries_to_return 

class FavoriteArtistsDialog (QDialog ):
    """Dialog to display and select favorite artists."""
    def __init__ (self ,parent_app ,cookies_config ):
        super ().__init__ (parent_app )
        self .parent_app =parent_app 
        self .cookies_config =cookies_config 
        self .all_fetched_artists =[]

        app_icon = get_app_icon_object()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
        self .selected_artist_urls =[]

        self .setModal (True )
        self .setMinimumSize (500 ,500 )

        self ._init_ui ()
        self ._fetch_favorite_artists ()

    def _get_domain_for_service (self ,service_name ):
        service_lower =service_name .lower ()
        coomer_primary_services ={'onlyfans','fansly','manyvids','candfans'}
        if service_lower in coomer_primary_services :
            return "coomer.su"
        else :
            return "kemono.su"

    def _tr (self ,key ,default_text =""):
        """Helper to get translation based on current app language."""
        if callable (get_translation )and self .parent_app :
            return get_translation (self .parent_app .current_selected_language ,key ,default_text )
        return default_text 

    def _retranslate_ui (self ):
        self .setWindowTitle (self ._tr ("fav_artists_dialog_title","Favorite Artists"))
        self .status_label .setText (self ._tr ("fav_artists_loading_status","Loading favorite artists..."))
        self .search_input .setPlaceholderText (self ._tr ("fav_artists_search_placeholder","Search artists..."))
        self .select_all_button .setText (self ._tr ("fav_artists_select_all_button","Select All"))
        self .deselect_all_button .setText (self ._tr ("fav_artists_deselect_all_button","Deselect All"))
        self .download_button .setText (self ._tr ("fav_artists_download_selected_button","Download Selected"))
        self .cancel_button .setText (self ._tr ("fav_artists_cancel_button","Cancel"))

    def _init_ui (self ):
        main_layout =QVBoxLayout (self )

        self .status_label =QLabel ()
        self .status_label .setAlignment (Qt .AlignCenter )
        main_layout .addWidget (self .status_label )

        self .search_input =QLineEdit ()
        self .search_input .textChanged .connect (self ._filter_artist_list_display )
        main_layout .addWidget (self .search_input )


        self .artist_list_widget =QListWidget ()
        self .artist_list_widget .setStyleSheet ("""
            QListWidget::item {
                border-bottom: 1px solid #4A4A4A; /* Slightly softer line */
                padding-top: 4px;
                padding-bottom: 4px;
            }""")
        main_layout .addWidget (self .artist_list_widget )
        self .artist_list_widget .setAlternatingRowColors (True )
        self .search_input .setVisible (False )
        self .artist_list_widget .setVisible (False )

        combined_buttons_layout =QHBoxLayout ()

        self .select_all_button =QPushButton ()
        self .select_all_button .clicked .connect (self ._select_all_items )
        combined_buttons_layout .addWidget (self .select_all_button )

        self .deselect_all_button =QPushButton ()
        self .deselect_all_button .clicked .connect (self ._deselect_all_items )
        combined_buttons_layout .addWidget (self .deselect_all_button )


        self .download_button =QPushButton ()
        self .download_button .clicked .connect (self ._accept_selection_action )
        self .download_button .setEnabled (False )
        self .download_button .setDefault (True )
        combined_buttons_layout .addWidget (self .download_button )

        self .cancel_button =QPushButton ()
        self .cancel_button .clicked .connect (self .reject )
        combined_buttons_layout .addWidget (self .cancel_button )

        combined_buttons_layout .addStretch (1 )
        main_layout .addLayout (combined_buttons_layout )

        self ._retranslate_ui ()
        if hasattr (self .parent_app ,'get_dark_theme')and self .parent_app .current_theme =="dark":
            self .setStyleSheet (self .parent_app .get_dark_theme ())


    def _logger (self ,message ):
        """Helper to log messages, either to parent app or console."""
        if hasattr (self .parent_app ,'log_signal')and self .parent_app .log_signal :
            self .parent_app .log_signal .emit (f"[FavArtistsDialog] {message }")
        else :
            print (f"[FavArtistsDialog] {message }")

    def _show_content_elements (self ,show ):
        """Helper to show/hide content-related widgets."""
        self .search_input .setVisible (show )
        self .artist_list_widget .setVisible (show )

    def _fetch_favorite_artists (self ):
        kemono_fav_url ="https://kemono.su/api/v1/account/favorites?type=artist"
        coomer_fav_url ="https://coomer.su/api/v1/account/favorites?type=artist"

        self .all_fetched_artists =[]
        fetched_any_successfully =False 
        errors_occurred =[]
        any_cookies_loaded_successfully_for_any_source =False 

        api_sources =[
        {"name":"Kemono.su","url":kemono_fav_url ,"domain":"kemono.su"},
        {"name":"Coomer.su","url":coomer_fav_url ,"domain":"coomer.su"}
        ]

        for source in api_sources :
            self ._logger (f"Attempting to fetch favorite artists from: {source ['name']} ({source ['url']})")
            self .status_label .setText (self ._tr ("fav_artists_loading_from_source_status","⏳ Loading favorites from {source_name}...").format (source_name =source ['name']))
            QCoreApplication .processEvents ()

            cookies_dict_for_source =None 
            if self .cookies_config ['use_cookie']:
                cookies_dict_for_source =prepare_cookies_for_request (
                True ,
                self .cookies_config ['cookie_text'],
                self .cookies_config ['selected_cookie_file'],
                self .cookies_config ['app_base_dir'],
                self ._logger ,
                target_domain =source ['domain']
                )
                if cookies_dict_for_source :
                    any_cookies_loaded_successfully_for_any_source =True 
                else :
                    self ._logger (f"Warning ({source ['name']}): Cookies enabled but could not be loaded for this domain. Fetch might fail if cookies are required.")
            try :
                headers ={'User-Agent':'Mozilla/5.0'}
                response =requests .get (source ['url'],headers =headers ,cookies =cookies_dict_for_source ,timeout =20 )
                response .raise_for_status ()
                artists_data_from_api =response .json ()

                if not isinstance (artists_data_from_api ,list ):
                    error_msg =f"Error ({source ['name']}): API did not return a list of artists (got {type (artists_data_from_api )})."
                    self ._logger (error_msg )
                    errors_occurred .append (error_msg )
                    continue 

                processed_artists_from_source =0 
                for artist_entry in artists_data_from_api :
                    artist_id =artist_entry .get ("id")
                    artist_name =html .unescape (artist_entry .get ("name","Unknown Artist").strip ())
                    artist_service_platform =artist_entry .get ("service")

                    if artist_id and artist_name and artist_service_platform :
                        artist_page_domain =self ._get_domain_for_service (artist_service_platform )
                        full_url =f"https://{artist_page_domain }/{artist_service_platform }/user/{artist_id }"

                        self .all_fetched_artists .append ({
                        'name':artist_name ,
                        'url':full_url ,
                        'service':artist_service_platform ,
                        'id':artist_id ,
                        '_source_api':source ['name']
                        })
                        processed_artists_from_source +=1 
                    else :
                        self ._logger (f"Warning ({source ['name']}): Skipping favorite artist entry due to missing data: {artist_entry }")

                if processed_artists_from_source >0 :
                    fetched_any_successfully =True 
                self ._logger (f"Fetched {processed_artists_from_source } artists from {source ['name']}.")

            except requests .exceptions .RequestException as e :
                error_msg =f"Error fetching favorites from {source ['name']}: {e }"
                self ._logger (error_msg )
                errors_occurred .append (error_msg )
            except Exception as e :
                error_msg =f"An unexpected error occurred with {source ['name']}: {e }"
                self ._logger (error_msg )
                errors_occurred .append (error_msg )


        if self .cookies_config ['use_cookie']and not any_cookies_loaded_successfully_for_any_source :
            self .status_label .setText (self ._tr ("fav_artists_cookies_required_status","Error: Cookies enabled but could not be loaded for any source."))
            self ._logger ("Error: Cookies enabled but no cookies loaded for any source. Showing help dialog.")
            cookie_help_dialog =CookieHelpDialog (self )
            cookie_help_dialog .exec_ ()
            self .download_button .setEnabled (False )
            if not fetched_any_successfully :
                 errors_occurred .append ("Cookies enabled but could not be loaded for any API source.")

        unique_artists_map ={}
        for artist in self .all_fetched_artists :
            key =(artist ['service'].lower (),str (artist ['id']).lower ())
            if key not in unique_artists_map :
                unique_artists_map [key ]=artist 
        self .all_fetched_artists =list (unique_artists_map .values ())

        self .all_fetched_artists .sort (key =lambda x :x ['name'].lower ())
        self ._populate_artist_list_widget ()

        if fetched_any_successfully and self .all_fetched_artists :
            self .status_label .setText (self ._tr ("fav_artists_found_status","Found {count} total favorite artist(s).").format (count =len (self .all_fetched_artists )))
            self ._show_content_elements (True )
            self .download_button .setEnabled (True )
        elif not fetched_any_successfully and not errors_occurred :
             self .status_label .setText (self ._tr ("fav_artists_none_found_status","No favorite artists found on Kemono.su or Coomer.su."))
             self ._show_content_elements (False )
             self .download_button .setEnabled (False )
        else :
            final_error_message =self ._tr ("fav_artists_failed_status","Failed to fetch favorites.")
            if errors_occurred :
                final_error_message +=" Errors: "+"; ".join (errors_occurred )
            self .status_label .setText (final_error_message )
            self ._show_content_elements (False )
            self .download_button .setEnabled (False )
            if fetched_any_successfully and not self .all_fetched_artists :
                 self .status_label .setText (self ._tr ("fav_artists_no_favorites_after_processing","No favorite artists found after processing."))

    def _populate_artist_list_widget (self ,artists_to_display =None ):
        self .artist_list_widget .clear ()
        source_list =artists_to_display if artists_to_display is not None else self .all_fetched_artists 
        for artist_data in source_list :
            item =QListWidgetItem (f"{artist_data ['name']} ({artist_data .get ('service','N/A').capitalize ()})")
            item .setFlags (item .flags ()|Qt .ItemIsUserCheckable )
            item .setCheckState (Qt .Unchecked )
            item .setData (Qt .UserRole ,artist_data )
            self .artist_list_widget .addItem (item )

    def _filter_artist_list_display (self ):
        search_text =self .search_input .text ().lower ().strip ()
        if not search_text :
            self ._populate_artist_list_widget ()
            return 

        filtered_artists =[
        artist for artist in self .all_fetched_artists 
        if search_text in artist ['name'].lower ()or search_text in artist ['url'].lower ()
        ]
        self ._populate_artist_list_widget (filtered_artists )

    def _select_all_items (self ):
        for i in range (self .artist_list_widget .count ()):
            self .artist_list_widget .item (i ).setCheckState (Qt .Checked )

    def _deselect_all_items (self ):
        for i in range (self .artist_list_widget .count ()):
            self .artist_list_widget .item (i ).setCheckState (Qt .Unchecked )

    def _accept_selection_action (self ):
        self .selected_artists_data =[]
        for i in range (self .artist_list_widget .count ()):
            item =self .artist_list_widget .item (i )
            if item .checkState ()==Qt .Checked :
                self .selected_artists_data .append (item .data (Qt .UserRole ))

        if not self .selected_artists_data :
            QMessageBox .information (self ,"No Selection","Please select at least one artist to download.")
            return 
        self .accept ()

    def get_selected_artists (self ):
        return self .selected_artists_data 

class FavoritePostsFetcherThread (QThread ):
    """Worker thread to fetch favorite posts and creator names."""
    status_update =pyqtSignal (str )
    progress_bar_update =pyqtSignal (int ,int )









    finished =pyqtSignal (list ,str )

    def __init__ (self ,cookies_config ,parent_logger_func ,target_domain_preference =None ):
        super ().__init__ ()
        self .cookies_config =cookies_config 
        self .parent_logger_func =parent_logger_func 
        self .target_domain_preference =target_domain_preference 
        self .cancellation_event =threading .Event ()
        self .error_key_map ={
        "Kemono.su":"kemono_su",
        "Coomer.su":"coomer_su"
        }

    def _logger (self ,message ):
        self .parent_logger_func (f"[FavPostsFetcherThread] {message }")

    def run (self ):
        kemono_fav_posts_url ="https://kemono.su/api/v1/account/favorites?type=post"
        coomer_fav_posts_url ="https://coomer.su/api/v1/account/favorites?type=post"

        all_fetched_posts_temp =[]
        error_messages_for_summary =[]
        fetched_any_successfully =False 
        any_cookies_loaded_successfully_for_any_source =False 

        self .status_update .emit ("key_fetching_fav_post_list_init")
        self .progress_bar_update .emit (0 ,0 )

        api_sources =[
        {"name":"Kemono.su","url":kemono_fav_posts_url ,"domain":"kemono.su"},
        {"name":"Coomer.su","url":coomer_fav_posts_url ,"domain":"coomer.su"}
        ]

        api_sources_to_try =[]
        if self .target_domain_preference :
            self ._logger (f"Targeting specific domain for favorites: {self .target_domain_preference }")
            for source_def in api_sources :
                if source_def ["domain"]==self .target_domain_preference :
                    api_sources_to_try .append (source_def )
                    break 
            if not api_sources_to_try :
                self ._logger (f"Warning: Preferred domain '{self .target_domain_preference }' not a recognized API source. Fetching from all.")
                api_sources_to_try =api_sources 
        else :
            self ._logger ("No specific domain preference, or both domains have cookies. Will attempt to fetch from all sources.")
            api_sources_to_try =api_sources 

        for source in api_sources_to_try :
            if self .cancellation_event .is_set ():
                self .finished .emit ([],"KEY_FETCH_CANCELLED_DURING")
                return 
            cookies_dict_for_source =None 
            if self .cookies_config ['use_cookie']:
                cookies_dict_for_source =prepare_cookies_for_request (
                True ,
                self .cookies_config ['cookie_text'],
                self .cookies_config ['selected_cookie_file'],
                self .cookies_config ['app_base_dir'],
                self ._logger ,
                target_domain =source ['domain']
                )
                if cookies_dict_for_source :
                    any_cookies_loaded_successfully_for_any_source =True 
                else :
                    self ._logger (f"Warning ({source ['name']}): Cookies enabled but could not be loaded for this domain. Fetch might fail if cookies are required.")

            self ._logger (f"Attempting to fetch favorite posts from: {source ['name']} ({source ['url']})")
            source_key_part =self .error_key_map .get (source ['name'],source ['name'].lower ().replace ('.','_'))
            self .status_update .emit (f"key_fetching_from_source_{source_key_part }")
            QCoreApplication .processEvents ()

            try :
                headers ={'User-Agent':'Mozilla/5.0'}
                response =requests .get (source ['url'],headers =headers ,cookies =cookies_dict_for_source ,timeout =20 )
                response .raise_for_status ()
                posts_data_from_api =response .json ()

                if not isinstance (posts_data_from_api ,list ):
                    err_detail =f"Error ({source ['name']}): API did not return a list of posts (got {type (posts_data_from_api )})."
                    self ._logger (err_detail )
                    error_messages_for_summary .append (err_detail )
                    continue 

                processed_posts_from_source =0 
                for post_entry in posts_data_from_api :
                    post_id =post_entry .get ("id")
                    post_title =html .unescape (post_entry .get ("title","Untitled Post").strip ())
                    service =post_entry .get ("service")
                    creator_id =post_entry .get ("user")
                    added_date_str =post_entry .get ("added",post_entry .get ("published",""))

                    if post_id and post_title and service and creator_id :
                        all_fetched_posts_temp .append ({
                        'post_id':post_id ,'title':post_title ,'service':service ,
                        'creator_id':creator_id ,'added_date':added_date_str ,
                        '_source_api':source ['name']
                        })
                        processed_posts_from_source +=1 
                    else :
                        self ._logger (f"Warning ({source ['name']}): Skipping favorite post entry due to missing data: {post_entry }")

                if processed_posts_from_source >0 :
                    fetched_any_successfully =True 
                self ._logger (f"Fetched {processed_posts_from_source } posts from {source ['name']}.")

            except requests .exceptions .RequestException as e :
                err_detail =f"Error fetching favorite posts from {source ['name']}: {e }"
                self ._logger (err_detail )
                error_messages_for_summary .append (err_detail )
                if e .response is not None and e .response .status_code ==401 :
                    self .finished .emit ([],"KEY_AUTH_FAILED")
                    self ._logger (f"Authorization failed for {source ['name']}, emitting KEY_AUTH_FAILED.")
                    return 
            except Exception as e :
                err_detail =f"An unexpected error occurred with {source ['name']}: {e }"
                self ._logger (err_detail )
                error_messages_for_summary .append (err_detail )

        if self .cancellation_event .is_set ():
            self .finished .emit ([],"KEY_FETCH_CANCELLED_AFTER")
            return 


        if self .cookies_config ['use_cookie']and not any_cookies_loaded_successfully_for_any_source :

            if self .target_domain_preference and not any_cookies_loaded_successfully_for_any_source :

                 domain_key_part =self .error_key_map .get (self .target_domain_preference ,self .target_domain_preference .lower ().replace ('.','_'))
                 self .finished .emit ([],f"KEY_COOKIES_REQUIRED_BUT_NOT_FOUND_FOR_DOMAIN_{domain_key_part }")
                 return 


            self .finished .emit ([],"KEY_COOKIES_REQUIRED_BUT_NOT_FOUND_GENERIC")
            return 

        unique_posts_map ={}
        for post in all_fetched_posts_temp :
            key =(post ['service'].lower (),str (post ['creator_id']).lower (),str (post ['post_id']).lower ())
            if key not in unique_posts_map :
                unique_posts_map [key ]=post 
        all_fetched_posts_temp =list (unique_posts_map .values ())

        all_fetched_posts_temp .sort (key =lambda x :(x .get ('_source_api','').lower (),x .get ('service','').lower (),str (x .get ('creator_id','')).lower (),(x .get ('added_date')or '')),reverse =False )

        if error_messages_for_summary :
            error_summary_str ="; ".join (error_messages_for_summary )
            if not fetched_any_successfully :
                self .finished .emit ([],f"KEY_FETCH_FAILED_GENERIC_{error_summary_str [:50 ]}")
            else :
                 self .finished .emit (all_fetched_posts_temp ,f"KEY_FETCH_PARTIAL_SUCCESS_{error_summary_str [:50 ]}")
        elif not all_fetched_posts_temp and not fetched_any_successfully and not self .target_domain_preference :
            self .finished .emit ([],"KEY_NO_FAVORITES_FOUND_ALL_PLATFORMS")
        else :
            self .finished .emit (all_fetched_posts_temp ,"KEY_FETCH_SUCCESS")

class PostListItemWidget (QWidget ):
    """Custom widget for displaying a single post in the FavoritePostsDialog list."""
    def __init__ (self ,post_data_dict ,parent_dialog_ref ,parent =None ):
        super ().__init__ (parent )
        self .post_data =post_data_dict 
        self .parent_dialog =parent_dialog_ref 

        self .layout =QHBoxLayout (self )
        self .layout .setContentsMargins (5 ,3 ,5 ,3 )
        self .layout .setSpacing (10 )

        self .checkbox =QCheckBox ()
        self .layout .addWidget (self .checkbox )

        self .info_label =QLabel ()
        self .info_label .setWordWrap (True )
        self .info_label .setTextFormat (Qt .RichText )
        self .layout .addWidget (self .info_label ,1 )

        self ._setup_display_text ()
    def _setup_display_text (self ):
        suffix_plain =self .post_data .get ('suffix_for_display',"")
        title_plain =self .post_data .get ('title','Untitled Post')
        escaped_suffix =html .escape (suffix_plain )
        escaped_title =html .escape (title_plain )
        p_style_paragraph ="font-size:10.5pt; margin:0; padding:0;"
        title_span_style ="font-weight:bold; color:#E0E0E0;"
        suffix_span_style ="color:#999999; font-weight:normal; font-size:9.5pt;"

        if escaped_suffix :
            display_html_content =f"<p style='{p_style_paragraph }'><span style='{title_span_style }'>{escaped_title }</span><span style='{suffix_span_style }'>{escaped_suffix }</span></p>"
        else :
            display_html_content =f"<p style='{p_style_paragraph }'><span style='{title_span_style }'>{escaped_title }</span></p>"

        self .info_label .setText (display_html_content )

    def isChecked (self ):return self .checkbox .isChecked ()
    def setCheckState (self ,state ):self .checkbox .setCheckState (state )
    def get_post_data (self ):return self .post_data 

class FavoritePostsDialog (QDialog ):
    """Dialog to display and select favorite posts."""
    def __init__ (self ,parent_app ,cookies_config ,known_names_list_ref ,target_domain_preference =None ):
        super ().__init__ (parent_app )
        self .parent_app =parent_app 
        self .cookies_config =cookies_config 
        self .all_fetched_posts =[]
        self .selected_posts_data =[]
        self .known_names_list_ref =known_names_list_ref 
        self .target_domain_preference_for_this_fetch =target_domain_preference 
        self .creator_name_cache ={}
        self .displayable_grouped_posts ={}
        self .fetcher_thread =None 

        app_icon = get_app_icon_object()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)

        self .setModal (True )
        self .setMinimumSize (600 ,600 )
        if hasattr (self .parent_app ,'get_dark_theme'):
            self .setStyleSheet (self .parent_app .get_dark_theme ())

        self ._init_ui ()
        self ._load_creator_names_from_file ()
        self ._retranslate_ui ()
        self ._start_fetching_favorite_posts ()

    def _update_status_label_from_key (self ,status_key ):
        """Translates a status key and updates the status label."""

        translated_status =self ._tr (status_key .lower (),status_key )
        self .status_label .setText (translated_status )

    def _init_ui (self ):
        main_layout =QVBoxLayout (self )

        self .status_label =QLabel ()
        self .status_label .setAlignment (Qt .AlignCenter )
        main_layout .addWidget (self .status_label )

        self .progress_bar =QProgressBar ()
        self .progress_bar .setTextVisible (False )
        self .progress_bar .setVisible (False )
        main_layout .addWidget (self .progress_bar )

        self .search_input =QLineEdit ()

        self .search_input .textChanged .connect (self ._filter_post_list_display )
        main_layout .addWidget (self .search_input )

        self .post_list_widget =QListWidget ()
        self .post_list_widget .setStyleSheet ("""
            QListWidget::item {
                border-bottom: 1px solid #4A4A4A;
                padding-top: 4px;
                padding-bottom: 4px;
            }""")
        self .post_list_widget .setAlternatingRowColors (True )
        main_layout .addWidget (self .post_list_widget )

        combined_buttons_layout =QHBoxLayout ()
        self .select_all_button =QPushButton ()
        self .select_all_button .clicked .connect (self ._select_all_items )
        combined_buttons_layout .addWidget (self .select_all_button )

        self .deselect_all_button =QPushButton ()
        self .deselect_all_button .clicked .connect (self ._deselect_all_items )
        combined_buttons_layout .addWidget (self .deselect_all_button )

        self .download_button =QPushButton ()
        self .download_button .clicked .connect (self ._accept_selection_action )
        self .download_button .setEnabled (False )
        self .download_button .setDefault (True )
        combined_buttons_layout .addWidget (self .download_button )

        self .cancel_button =QPushButton ()
        self .cancel_button .clicked .connect (self .reject )
        combined_buttons_layout .addWidget (self .cancel_button )
        combined_buttons_layout .addStretch (1 )
        main_layout .addLayout (combined_buttons_layout )

    def _tr (self ,key ,default_text =""):
        """Helper to get translation based on current app language."""
        if callable (get_translation )and self .parent_app :
            return get_translation (self .parent_app .current_selected_language ,key ,default_text )
        return default_text 

    def _retranslate_ui (self ):
        self .setWindowTitle (self ._tr ("fav_posts_dialog_title","Favorite Posts"))
        self .status_label .setText (self ._tr ("fav_posts_loading_status","Loading favorite posts..."))
        self .search_input .setPlaceholderText (self ._tr ("fav_posts_search_placeholder","Search posts (title, creator name, ID, service)..."))
        self .select_all_button .setText (self ._tr ("fav_posts_select_all_button","Select All"))
        self .deselect_all_button .setText (self ._tr ("fav_posts_deselect_all_button","Deselect All"))
        self .download_button .setText (self ._tr ("fav_posts_download_selected_button","Download Selected"))
        self .cancel_button .setText (self ._tr ("fav_posts_cancel_button","Cancel"))

    def _logger (self ,message ):
        if hasattr (self .parent_app ,'log_signal')and self .parent_app .log_signal :
            self .parent_app .log_signal .emit (f"[FavPostsDialog] {message }")
        else :
            print (f"[FavPostsDialog] {message }")

    def _load_creator_names_from_file (self ):
        """Loads creator id-name-service mappings from creators.txt."""
        self ._logger ("Attempting to load creators.json for Favorite Posts Dialog.")

        if getattr (sys ,'frozen',False )and hasattr (sys ,'_MEIPASS'):
            base_path_for_creators =sys ._MEIPASS 
            self ._logger (f"  Running bundled. Using _MEIPASS: {base_path_for_creators }")
        else :
            base_path_for_creators =self .parent_app .app_base_dir 
            self ._logger (f"  Not bundled or _MEIPASS unavailable. Using app_base_dir: {base_path_for_creators }")

        creators_file_path =os .path .join (base_path_for_creators ,"creators.json")
        self ._logger (f"Full path to creators.json: {creators_file_path }")

        if not os .path .exists (creators_file_path ):
            self ._logger (f"Warning: 'creators.json' not found at {creators_file_path }. Creator names will not be displayed.")
            return 

        try :
            with open (creators_file_path ,'r',encoding ='utf-8')as f :
                loaded_data =json .load (f )

                if isinstance (loaded_data ,list )and len (loaded_data )>0 and isinstance (loaded_data [0 ],list ):
                    creators_list =loaded_data [0 ]
                elif isinstance (loaded_data ,list )and all (isinstance (item ,dict )for item in loaded_data ):
                    creators_list =loaded_data 
                else :
                    self ._logger (f"Warning: 'creators.json' has an unexpected format. Expected a list of lists or a flat list of creator objects.")
                    return 

                for creator_data in creators_list :
                    creator_id =creator_data .get ("id")
                    name =creator_data .get ("name")
                    service =creator_data .get ("service")
                    if creator_id and name and service :
                        self .creator_name_cache [(service .lower (),str (creator_id ))]=name 
            self ._logger (f"Successfully loaded {len (self .creator_name_cache )} creator names from 'creators.json'.")
        except Exception as e :
            self ._logger (f"Error loading 'creators.json': {e }")

    def _start_fetching_favorite_posts (self ):
        self .download_button .setEnabled (False )
        self .status_label .setText ("Initializing favorite posts fetch...")

        self .fetcher_thread =FavoritePostsFetcherThread (
        self .cookies_config ,
        self .parent_app .log_signal .emit ,
        target_domain_preference =self .target_domain_preference_for_this_fetch 
        )
        self .fetcher_thread .status_update .connect (self ._update_status_label_from_key )
        self .fetcher_thread .finished .connect (self ._on_fetch_completed )
        self .fetcher_thread .progress_bar_update .connect (self ._set_progress_bar_value )
        self .progress_bar .setVisible (True )
        self .fetcher_thread .start ()

    def _set_progress_bar_value (self ,value ,maximum ):
        if maximum ==0 :
            self .progress_bar .setRange (0 ,0 )
            self .progress_bar .setValue (0 )
        else :
            self .progress_bar .setRange (0 ,maximum )
            self .progress_bar .setValue (value )

    def _on_fetch_completed (self ,fetched_posts_list ,status_key ):
        self .progress_bar .setVisible (False )

        proceed_to_display_posts =False 
        show_error_message_box =False 
        message_box_title_key ="fav_posts_fetch_error_title"
        message_box_text_key ="fav_posts_fetch_error_message"
        message_box_params ={'domain':self .target_domain_preference_for_this_fetch or "platform",'error_message_part':""}
        status_label_text_key =None 

        if status_key =="KEY_FETCH_SUCCESS":
            proceed_to_display_posts =True 
        elif status_key and status_key .startswith ("KEY_FETCH_PARTIAL_SUCCESS_")and fetched_posts_list :
            displayable_detail =status_key .replace ("KEY_FETCH_PARTIAL_SUCCESS_","").replace ("_"," ")
            self ._logger (f"Partial success with posts: {status_key } -> {displayable_detail }")


            proceed_to_display_posts =True 
        elif status_key :
            specific_domain_msg_part =f" for {self .target_domain_preference_for_this_fetch }"if self .target_domain_preference_for_this_fetch else ""

            if status_key .startswith ("KEY_COOKIES_REQUIRED_BUT_NOT_FOUND_FOR_DOMAIN_")or status_key =="KEY_COOKIES_REQUIRED_BUT_NOT_FOUND_GENERIC":
                status_label_text_key ="fav_posts_cookies_required_error"
                self ._logger (f"Cookie error: {status_key }. Showing help dialog.")
                cookie_help_dialog =CookieHelpDialog (self )
                cookie_help_dialog .exec_ ()
            elif status_key =="KEY_AUTH_FAILED":
                status_label_text_key ="fav_posts_auth_failed_title"
                self ._logger (f"Auth error: {status_key }. Showing help dialog.")
                QMessageBox .warning (self ,self ._tr ("fav_posts_auth_failed_title","Authorization Failed (Posts)"),
                self ._tr ("fav_posts_auth_failed_message_generic","...").format (domain_specific_part =specific_domain_msg_part ))
                cookie_help_dialog =CookieHelpDialog (self )
                cookie_help_dialog .exec_ ()
            elif status_key =="KEY_NO_FAVORITES_FOUND_ALL_PLATFORMS":
                status_label_text_key ="fav_posts_no_posts_found_status"
                self ._logger (status_key )
            elif status_key .startswith ("KEY_FETCH_CANCELLED"):
                status_label_text_key ="fav_posts_fetch_cancelled_status"
                self ._logger (status_key )
            else :
                displayable_error_detail =status_key 
                if status_key .startswith ("KEY_FETCH_FAILED_GENERIC_"):
                    displayable_error_detail =status_key .replace ("KEY_FETCH_FAILED_GENERIC_","").replace ("_"," ")
                elif status_key .startswith ("KEY_FETCH_PARTIAL_SUCCESS_"):
                    displayable_error_detail =status_key .replace ("KEY_FETCH_PARTIAL_SUCCESS_","Partial success but no posts: ").replace ("_"," ")

                message_box_params ['error_message_part']=f":\n\n{displayable_error_detail }"if displayable_error_detail else ""
                status_label_text_key ="fav_posts_fetch_error_message"
                show_error_message_box =True 
                self ._logger (f"Fetch error: {status_key } -> {displayable_error_detail }")

            if status_label_text_key :
                 self .status_label .setText (self ._tr (status_label_text_key ,status_label_text_key ).format (**message_box_params ))
            if show_error_message_box :
                 QMessageBox .critical (self ,self ._tr (message_box_title_key ),self ._tr (message_box_text_key ).format (**message_box_params ))

            self .download_button .setEnabled (False )
            return 


        if not proceed_to_display_posts :
            if not status_label_text_key :
                self .status_label .setText (self ._tr ("fav_posts_cookies_required_error","Error: Cookies are required for favorite posts but could not be loaded."))
            self .download_button .setEnabled (False )
            return 

        if not self .creator_name_cache :
            self ._logger ("Warning: Creator name cache is empty. Names will not be resolved from creators.json. Displaying IDs instead.")
        else :
            self ._logger (f"Creator name cache has {len (self .creator_name_cache )} entries. Attempting to resolve names...")
            sample_keys =list (self .creator_name_cache .keys ())[:3 ]
            if sample_keys :
                self ._logger (f"Sample keys from creator_name_cache: {sample_keys }")


        processed_one_missing_log =False 
        for post_entry in fetched_posts_list :
            service_from_post =post_entry .get ('service','')
            creator_id_from_post =post_entry .get ('creator_id','')

            lookup_key_service =service_from_post .lower ()
            lookup_key_id =str (creator_id_from_post )
            lookup_key_tuple =(lookup_key_service ,lookup_key_id )

            resolved_name =self .creator_name_cache .get (lookup_key_tuple )

            if resolved_name :
                post_entry ['creator_name_resolved']=resolved_name 
            else :
                post_entry ['creator_name_resolved']=str (creator_id_from_post )
                if not processed_one_missing_log and self .creator_name_cache :
                    self ._logger (f"Debug: Name not found for key {lookup_key_tuple }. Using ID '{creator_id_from_post }'.")
                    processed_one_missing_log =True 

        self .all_fetched_posts =fetched_posts_list 

        if not self .all_fetched_posts :
            self .status_label .setText (self ._tr ("fav_posts_no_posts_found_status","No favorite posts found."))
            self .download_button .setEnabled (False )
            return 

        try :
            self ._populate_post_list_widget ()
            self .status_label .setText (self ._tr ("fav_posts_found_status","{count} favorite post(s) found.").format (count =len (self .all_fetched_posts )))
            self .download_button .setEnabled (True )
        except Exception as e :
            self .status_label .setText (self ._tr ("fav_posts_display_error_status","Error displaying posts: {error}").format (error =str (e )))
            self ._logger (f"Error during _populate_post_list_widget: {e }\n{traceback .format_exc (limit =3 )}")
            QMessageBox .critical (self ,self ._tr ("fav_posts_ui_error_title","UI Error"),self ._tr ("fav_posts_ui_error_message","Could not display favorite posts: {error}").format (error =str (e )))
            self .download_button .setEnabled (False )


    def _find_best_known_name_match_in_title (self ,title_raw ):
        if not title_raw or not self .known_names_list_ref :
            return None 

        title_lower =title_raw .lower ()
        best_match_known_name_primary =None 
        longest_match_len =0 

        for known_entry in self .known_names_list_ref :
            aliases_to_check =set ()
            for alias_val in known_entry .get ("aliases",[]):
                aliases_to_check .add (alias_val )
            if not known_entry .get ("is_group",False ):
                aliases_to_check .add (known_entry ["name"])
            sorted_aliases_for_entry =sorted (list (aliases_to_check ),key =len ,reverse =True )

            for alias in sorted_aliases_for_entry :
                alias_lower =alias .lower ()
                if not alias_lower :
                    continue 
                if re .search (r'\b'+re .escape (alias_lower )+r'\b',title_lower ):
                    if len (alias_lower )>longest_match_len :
                        longest_match_len =len (alias_lower )
                        best_match_known_name_primary =known_entry ["name"]
                    break 
        return best_match_known_name_primary 

    def _populate_post_list_widget (self ,posts_to_display =None ):
        self .post_list_widget .clear ()

        source_list_for_grouping =posts_to_display if posts_to_display is not None else self .all_fetched_posts 
        grouped_posts ={}
        for post in source_list_for_grouping :
            service =post .get ('service','unknown_service')
            creator_id =post .get ('creator_id','unknown_id')
            group_key =(service ,creator_id )
            if group_key not in grouped_posts :
                grouped_posts [group_key ]=[]
            grouped_posts [group_key ].append (post )

        sorted_group_keys =sorted (grouped_posts .keys (),key =lambda x :(x [0 ].lower (),x [1 ].lower ()))

        self .displayable_grouped_posts ={
        key :sorted (grouped_posts [key ],key =lambda p :(p .get ('added_date')or ''),reverse =True )
        for key in sorted_group_keys 
        }
        for service ,creator_id_val in sorted_group_keys :
            creator_name_display =self .creator_name_cache .get (
            (service .lower (),str (creator_id_val )),
            str (creator_id_val )
            )
            artist_header_display_text =f"{creator_name_display } ({service .capitalize ()} / {creator_id_val })"
            artist_header_item =QListWidgetItem (f"🎨 {artist_header_display_text }")
            artist_header_item .setFlags (Qt .NoItemFlags )
            font =artist_header_item .font ()
            font .setBold (True )
            font .setPointSize (font .pointSize ()+1 )
            artist_header_item .setFont (font )
            artist_header_item .setForeground (Qt .cyan )
            self .post_list_widget .addItem (artist_header_item )
            for post_data in self .displayable_grouped_posts [(service ,creator_id_val )]:
                post_title_raw =post_data .get ('title','Untitled Post')
                found_known_name_primary =self ._find_best_known_name_match_in_title (post_title_raw )

                plain_text_title_for_list_item =post_title_raw 
                if found_known_name_primary :
                    suffix_text =f" [Known - {found_known_name_primary }]"
                    post_data ['suffix_for_display']=suffix_text 
                    plain_text_title_for_list_item =post_title_raw +suffix_text 
                else :
                    post_data .pop ('suffix_for_display',None )

                list_item =QListWidgetItem (self .post_list_widget )
                list_item .setText (plain_text_title_for_list_item )
                list_item .setFlags (list_item .flags ()|Qt .ItemIsUserCheckable )
                list_item .setCheckState (Qt .Unchecked )
                list_item .setData (Qt .UserRole ,post_data )
                self .post_list_widget .addItem (list_item )

    def _filter_post_list_display (self ):
        search_text =self .search_input .text ().lower ().strip ()
        if not search_text :
            self ._populate_post_list_widget (self .all_fetched_posts )
            return 

        filtered_posts_to_group =[]
        for post in self .all_fetched_posts :
            matches_post_title =search_text in post .get ('title','').lower ()
            matches_creator_name =search_text in post .get ('creator_name_resolved','').lower ()
            matches_creator_id =search_text in post .get ('creator_id','').lower ()
            matches_service =search_text in post ['service'].lower ()

            if matches_post_title or matches_creator_name or matches_creator_id or matches_service :
                filtered_posts_to_group .append (post )

        self ._populate_post_list_widget (filtered_posts_to_group )

    def _select_all_items (self ):
        for i in range (self .post_list_widget .count ()):
            item =self .post_list_widget .item (i )
            if item and item .flags ()&Qt .ItemIsUserCheckable :
                item .setCheckState (Qt .Checked )

    def _deselect_all_items (self ):
        for i in range (self .post_list_widget .count ()):
            item =self .post_list_widget .item (i )
            if item and item .flags ()&Qt .ItemIsUserCheckable :
                item .setCheckState (Qt .Unchecked )

    def _accept_selection_action (self ):
        self .selected_posts_data =[]
        for i in range (self .post_list_widget .count ()):
            item =self .post_list_widget .item (i )
            if item and item .checkState ()==Qt .Checked :
                post_data_for_download =item .data (Qt .UserRole )
                self .selected_posts_data .append (post_data_for_download )

        if not self .selected_posts_data :
            QMessageBox .information (self ,self ._tr ("fav_posts_no_selection_title","No Selection"),self ._tr ("fav_posts_no_selection_message","Please select at least one post to download."))
            return 
        self .accept ()

    def get_selected_posts (self ):
        return self .selected_posts_data 


class HelpGuideDialog (QDialog ):
    """A multi-page dialog for displaying the feature guide."""
    def __init__ (self ,steps_data ,parent_app ,parent =None ):
        super ().__init__ (parent )
        self .current_step =0 
        self .steps_data =steps_data 
        self .parent_app =parent_app 

        app_icon = get_app_icon_object()
        if not app_icon.isNull(): # Check if icon is valid
            self.setWindowIcon(app_icon)
        else: # Fallback to default if icon is null
            self.setWindowIcon(QIcon())
            self.setWindowIcon(app_icon)

        self .setModal (True )
        self .setFixedSize (650 ,600 )


        current_theme_style =""
        if hasattr (self .parent_app ,'current_theme')and self .parent_app .current_theme =="dark":
            if hasattr (self .parent_app ,'get_dark_theme'):
                current_theme_style =self .parent_app .get_dark_theme ()


        self .setStyleSheet (current_theme_style if current_theme_style else """
            QDialog { background-color: #2E2E2E; border: 1px solid #5A5A5A; }
            QLabel { color: #E0E0E0; }
            QPushButton { background-color: #555; color: #F0F0F0; border: 1px solid #6A6A6A; padding: 8px 15px; border-radius: 4px; min-height: 25px; font-size: 11pt; }
            QPushButton:hover { background-color: #656565; }
            QPushButton:pressed { background-color: #4A4A4A; }
        """)
        self ._init_ui ()
        if self .parent_app :
            self .move (self .parent_app .geometry ().center ()-self .rect ().center ())

    def _tr (self ,key ,default_text =""):
        """Helper to get translation based on current app language."""
        if callable (get_translation )and self .parent_app :
            return get_translation (self .parent_app .current_selected_language ,key ,default_text )
        return default_text 


    def _init_ui (self ):
        main_layout =QVBoxLayout (self )
        main_layout .setContentsMargins (0 ,0 ,0 ,0 )
        main_layout .setSpacing (0 )

        self .stacked_widget =QStackedWidget ()
        main_layout .addWidget (self .stacked_widget ,1 )

        self .tour_steps_widgets =[]
        for title ,content in self .steps_data :
            step_widget =TourStepWidget (title ,content )
            self .tour_steps_widgets .append (step_widget )
            self .stacked_widget .addWidget (step_widget )

        self .setWindowTitle (self ._tr ("help_guide_dialog_title","Kemono Downloader - Feature Guide"))

        buttons_layout =QHBoxLayout ()
        buttons_layout .setContentsMargins (15 ,10 ,15 ,15 )
        buttons_layout .setSpacing (10 )

        self .back_button =QPushButton (self ._tr ("tour_dialog_back_button","Back"))
        self .back_button .clicked .connect (self ._previous_step )
        self .back_button .setEnabled (False )

        if getattr (sys ,'frozen',False )and hasattr (sys ,'_MEIPASS'):
            assets_base_dir =sys ._MEIPASS 
        else :
            assets_base_dir =os .path .dirname (os .path .abspath (__file__ ))

        github_icon_path =os .path .join (assets_base_dir ,"assets","github.png")
        instagram_icon_path =os .path .join (assets_base_dir ,"assets","instagram.png")
        discord_icon_path =os .path .join (assets_base_dir ,"assets","discord.png")

        self .github_button =QPushButton (QIcon (github_icon_path ),"")
        self .instagram_button =QPushButton (QIcon (instagram_icon_path ),"")
        self .Discord_button =QPushButton (QIcon (discord_icon_path ),"")

        icon_size =QSize (24 ,24 )
        self .github_button .setIconSize (icon_size )
        self .instagram_button .setIconSize (icon_size )
        self .Discord_button .setIconSize (icon_size )

        self .next_button =QPushButton (self ._tr ("tour_dialog_next_button","Next"))
        self .next_button .clicked .connect (self ._next_step_action )
        self .next_button .setDefault (True )
        self .github_button .clicked .connect (self ._open_github_link )
        self .instagram_button .clicked .connect (self ._open_instagram_link )
        self .Discord_button .clicked .connect (self ._open_Discord_link )
        self .github_button .setToolTip (self ._tr ("help_guide_github_tooltip","Visit project's GitHub page (Opens in browser)"))
        self .instagram_button .setToolTip (self ._tr ("help_guide_instagram_tooltip","Visit our Instagram page (Opens in browser)"))
        self .Discord_button .setToolTip (self ._tr ("help_guide_discord_tooltip","Visit our Discord community (Opens in browser)"))


        social_layout =QHBoxLayout ()
        social_layout .setSpacing (10 )
        social_layout .addWidget (self .github_button )
        social_layout .addWidget (self .instagram_button )
        social_layout .addWidget (self .Discord_button )

        while buttons_layout .count ():
            item =buttons_layout .takeAt (0 )
            if item .widget ():
                item .widget ().setParent (None )
            elif item .layout ():
                pass 
        buttons_layout .addLayout (social_layout )
        buttons_layout .addStretch (1 )
        buttons_layout .addWidget (self .back_button )
        buttons_layout .addWidget (self .next_button )
        main_layout .addLayout (buttons_layout )
        self ._update_button_states ()

    def _next_step_action (self ):
        if self .current_step <len (self .tour_steps_widgets )-1 :
            self .current_step +=1 
            self .stacked_widget .setCurrentIndex (self .current_step )
        else :
            self .accept ()
        self ._update_button_states ()

    def _previous_step (self ):
        if self .current_step >0 :
            self .current_step -=1 
            self .stacked_widget .setCurrentIndex (self .current_step )
        self ._update_button_states ()

    def _update_button_states (self ):
        if self .current_step ==len (self .tour_steps_widgets )-1 :
            self .next_button .setText (self ._tr ("tour_dialog_finish_button","Finish"))
        else :
            self .next_button .setText (self ._tr ("tour_dialog_next_button","Next"))
        self .back_button .setEnabled (self .current_step >0 )

    def _open_github_link (self ):
        QDesktopServices .openUrl (QUrl ("https://github.com/Yuvi9587"))

    def _open_instagram_link (self ):
        QDesktopServices .openUrl (QUrl ("https://www.instagram.com/uvi.arts/"))

    def _open_Discord_link (self ):
        QDesktopServices .openUrl (QUrl ("https://discord.gg/BqP64XTdJN"))

class TourStepWidget (QWidget ):
    """A single step/page in the tour."""
    def __init__ (self ,title_text ,content_text ,parent =None ):
        super ().__init__ (parent )
        layout =QVBoxLayout (self )
        layout .setContentsMargins (20 ,20 ,20 ,20 )
        layout .setSpacing (10 )

        title_label =QLabel (title_text )
        title_label .setAlignment (Qt .AlignCenter )
        title_label .setStyleSheet ("font-size: 18px; font-weight: bold; color: #E0E0E0; padding-bottom: 15px;")
        layout .addWidget (title_label )
        scroll_area =QScrollArea ()
        scroll_area .setWidgetResizable (True )
        scroll_area .setFrameShape (QFrame .NoFrame )
        scroll_area .setHorizontalScrollBarPolicy (Qt .ScrollBarAlwaysOff )
        scroll_area .setVerticalScrollBarPolicy (Qt .ScrollBarAsNeeded )
        scroll_area .setStyleSheet ("background-color: transparent;")

        content_label =QLabel (content_text )
        content_label .setWordWrap (True )
        content_label .setAlignment (Qt .AlignLeft |Qt .AlignTop )
        content_label .setTextFormat (Qt .RichText )
        content_label .setStyleSheet ("font-size: 11pt; color: #C8C8C8; line-height: 1.8;")
        scroll_area .setWidget (content_label )
        layout .addWidget (scroll_area ,1 )


class TourDialog (QDialog ):
    """
    A dialog that shows a multi-page tour to the user.
    Includes a "Never show again" checkbox.
    Uses QSettings to remember this preference.
    """
    tour_finished_normally =pyqtSignal ()
    tour_skipped =pyqtSignal ()

    CONFIG_ORGANIZATION_NAME ="KemonoDownloader"
    CONFIG_APP_NAME_TOUR ="ApplicationTour"
    TOUR_SHOWN_KEY ="neverShowTourAgainV19"

    def __init__ (self ,parent =None ):
        super ().__init__ (parent )
        self .settings =QSettings (self .CONFIG_ORGANIZATION_NAME ,self .CONFIG_APP_NAME_TOUR )
        self .current_step =0 
        self .parent_app =parent 

        app_icon = get_app_icon_object()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)

        self .setModal (True )
        self .setFixedSize (600 ,620 )
        self .setStyleSheet ("""
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
        self ._init_ui ()
        self ._center_on_screen ()

    def _tr (self ,key ,default_text =""):
        """Helper to get translation based on current app language."""
        if callable (get_translation )and self .parent_app :
            return get_translation (self .parent_app .current_selected_language ,key ,default_text )
        return default_text 


    def _center_on_screen (self ):
        """Centers the dialog on the screen."""
        try :
            primary_screen =QApplication .primaryScreen ()
            if not primary_screen :
                screens =QApplication .screens ()
                if not screens :return 
                primary_screen =screens [0 ]

            available_geo =primary_screen .availableGeometry ()
            widget_geo =self .frameGeometry ()

            x =available_geo .x ()+(available_geo .width ()-widget_geo .width ())//2 
            y =available_geo .y ()+(available_geo .height ()-widget_geo .height ())//2 
            self .move (x ,y )
        except Exception as e :
            print (f"[Tour] Error centering dialog: {e }")


    def _init_ui (self ):
        main_layout =QVBoxLayout (self )
        main_layout .setContentsMargins (0 ,0 ,0 ,0 )
        main_layout .setSpacing (0 )

        self .stacked_widget =QStackedWidget ()
        main_layout .addWidget (self .stacked_widget ,1 )
        step1_content =(
        "Hello! This quick tour will walk you through the main features of the Kemono Downloader, including recent updates like enhanced filtering, manga mode improvements, and cookie management."
        )
        self .step1 =TourStepWidget (self ._tr ("tour_dialog_step1_title"),self ._tr ("tour_dialog_step1_content",step1_content ))

        step2_content =(
        "Let's start with the basics for downloading:"
        )
        self .step2 =TourStepWidget (self ._tr ("tour_dialog_step2_title"),self ._tr ("tour_dialog_step2_content",step2_content ))

        step3_content =(
        "Refine what you download with these filters (most are disabled in 'Only Links' or 'Only Archives' modes):"
        )
        self .step3_filtering =TourStepWidget (self ._tr ("tour_dialog_step3_title"),self ._tr ("tour_dialog_step3_content",step3_content ))

        step_favorite_mode_content =(
        "The application offers a 'Favorite Mode' for downloading content from artists you've favorited on Kemono.su."
        )
        self .step_favorite_mode =TourStepWidget (self ._tr ("tour_dialog_step4_title"),self ._tr ("tour_dialog_step4_content",step_favorite_mode_content ))

        step4_content =(
        "More options to customize your downloads:"
        )
        self .step4_fine_tuning =TourStepWidget (self ._tr ("tour_dialog_step5_title"),self ._tr ("tour_dialog_step5_content",step4_content ))

        step5_content =(
        "Organize your downloads and manage performance:"
        )
        self .step5_organization =TourStepWidget (self ._tr ("tour_dialog_step6_title"),self ._tr ("tour_dialog_step6_content",step5_content ))

        step6_errors_content =(
        "Sometimes, downloads might encounter issues. Here are a few common ones:"
        )
        self .step6_errors =TourStepWidget (self ._tr ("tour_dialog_step7_title"),self ._tr ("tour_dialog_step7_content",step6_errors_content ))

        step7_final_controls_content =(
        "Monitoring and Controls:"
        )
        self .step7_final_controls =TourStepWidget (self ._tr ("tour_dialog_step8_title"),self ._tr ("tour_dialog_step8_content",step7_final_controls_content ))


        self .tour_steps =[
        self .step1 ,
        self .step2 ,
        self .step3_filtering ,
        self .step_favorite_mode ,
        self .step4_fine_tuning ,
        self .step5_organization ,
        self .step6_errors ,self .step7_final_controls ]
        for step_widget in self .tour_steps :
            self .stacked_widget .addWidget (step_widget )

        self .setWindowTitle (self ._tr ("tour_dialog_title","Welcome to Kemono Downloader!"))

        bottom_controls_layout =QVBoxLayout ()
        bottom_controls_layout .setContentsMargins (15 ,10 ,15 ,15 )
        bottom_controls_layout .setSpacing (12 )

        self .never_show_again_checkbox =QCheckBox (self ._tr ("tour_dialog_never_show_checkbox","Never show this tour again"))
        bottom_controls_layout .addWidget (self .never_show_again_checkbox ,0 ,Qt .AlignLeft )

        buttons_layout =QHBoxLayout ()
        buttons_layout .setSpacing (10 )

        self .skip_button =QPushButton (self ._tr ("tour_dialog_skip_button","Skip Tour"))
        self .skip_button .clicked .connect (self ._skip_tour_action )

        self .back_button =QPushButton (self ._tr ("tour_dialog_back_button","Back"))
        self .back_button .clicked .connect (self ._previous_step )
        self .back_button .setEnabled (False )

        self .next_button =QPushButton (self ._tr ("tour_dialog_next_button","Next"))
        self .next_button .clicked .connect (self ._next_step_action )
        self .next_button .setDefault (True )

        buttons_layout .addWidget (self .skip_button )
        buttons_layout .addStretch (1 )
        buttons_layout .addWidget (self .back_button )
        buttons_layout .addWidget (self .next_button )

        bottom_controls_layout .addLayout (buttons_layout )
        main_layout .addLayout (bottom_controls_layout )

        self ._update_button_states ()

    def _handle_exit_actions (self ):
        pass 

    def _next_step_action (self ):
        if self .current_step <len (self .tour_steps )-1 :
            self .current_step +=1 
            self .stacked_widget .setCurrentIndex (self .current_step )
        else :
            self ._finish_tour_action ()
        self ._update_button_states ()

    def _previous_step (self ):
        if self .current_step >0 :
            self .current_step -=1 
            self .stacked_widget .setCurrentIndex (self .current_step )
        self ._update_button_states ()

    def _update_button_states (self ):
        if self .current_step ==len (self .tour_steps )-1 :
            self .next_button .setText (self ._tr ("tour_dialog_finish_button","Finish"))
        else :
            self .next_button .setText (self ._tr ("tour_dialog_next_button","Next"))
        self .back_button .setEnabled (self .current_step >0 )

    def _skip_tour_action (self ):
        self ._save_settings_if_checked ()
        self .tour_skipped .emit ()
        self .reject ()

    def _finish_tour_action (self ):
        self ._save_settings_if_checked ()
        self .tour_finished_normally .emit ()
        self .accept ()

    def _save_settings_if_checked (self ):
        if self .never_show_again_checkbox .isChecked ():
            self .settings .setValue (self .TOUR_SHOWN_KEY ,True )
        else :
            self .settings .setValue (self .TOUR_SHOWN_KEY ,False )
        self .settings .sync ()

    @staticmethod 
    def should_show_tour (parent_app_settings =None ):
        settings_to_use =QSettings (TourDialog .CONFIG_ORGANIZATION_NAME ,TourDialog .CONFIG_APP_NAME_TOUR )

        never_show =settings_to_use .value (TourDialog .TOUR_SHOWN_KEY ,False ,type =bool )
        return not never_show 

    def closeEvent (self ,event ):
        self ._skip_tour_action ()
        super ().closeEvent (event )

    @staticmethod 
    def run_tour_if_needed (parent_app_window ):
        try :
            settings =QSettings (TourDialog .CONFIG_ORGANIZATION_NAME ,TourDialog .CONFIG_APP_NAME_TOUR )
            never_show_again_from_settings =settings .value (TourDialog .TOUR_SHOWN_KEY ,False ,type =bool )

            primary_screen =QApplication .primaryScreen ()
            if not primary_screen :
                screens =QApplication .screens ()
                primary_screen =screens [0 ]if screens else None 

            dialog_width ,dialog_height =600 ,620 

            if primary_screen :
                available_geo =primary_screen .availableGeometry ()
                screen_w ,screen_h =available_geo .width (),available_geo .height ()
                pref_w =int (screen_w *0.50 )
                pref_h =int (screen_h *0.60 )
                min_w ,max_w =550 ,700 
                min_h ,max_h =580 ,750 

                dialog_width =max (min_w ,min (pref_w ,max_w ))
                dialog_height =max (min_h ,min (pref_h ,max_h ))

            if never_show_again_from_settings :
                print (f"[Tour] Skipped: '{TourDialog .TOUR_SHOWN_KEY }' is True in settings.")
                return QDialog .Rejected 

            tour_dialog =TourDialog (parent_app_window )
            tour_dialog .setFixedSize (dialog_width ,dialog_height )
            result =tour_dialog .exec_ ()
            return result 

        except Exception as e :
            print (f"[Tour] CRITICAL ERROR in run_tour_if_needed: {e }")
            return QDialog .Rejected 

class ExternalLinkDownloadThread (QThread ):
    """A QThread to handle downloading multiple external links sequentially."""
    progress_signal =pyqtSignal (str )
    file_complete_signal =pyqtSignal (str ,bool )
    finished_signal =pyqtSignal ()

    def __init__ (self ,tasks_to_download ,download_base_path ,parent_logger_func ,parent =None ):
        super ().__init__ (parent )
        self .tasks =tasks_to_download 
        self .download_base_path =download_base_path 
        self .parent_logger_func =parent_logger_func 
        self .is_cancelled =False 

    def run (self ):
        self .progress_signal .emit (f"ℹ️ Starting external link download thread for {len (self .tasks )} link(s).")
        for i ,task_info in enumerate (self .tasks ):
            if self .is_cancelled :
                self .progress_signal .emit ("External link download cancelled by user.")
                break 

            platform =task_info .get ('platform','unknown').lower ()
            full_mega_url =task_info ['url']
            post_title =task_info ['title']
            key =task_info .get ('key','')

            self .progress_signal .emit (f"Download ({i +1 }/{len (self .tasks )}): Starting '{post_title }' ({platform .upper ()}) from {full_mega_url }")

            try :
                if platform =='mega':

                    if key :
                        parsed_original_url =urlparse (full_mega_url )
                        if key not in parsed_original_url .fragment :
                            base_url_no_fragment =full_mega_url .split ('#')[0 ]
                            full_mega_url_with_key =f"{base_url_no_fragment }#{key }"
                            self .progress_signal .emit (f"   Adjusted Mega URL with key: {full_mega_url_with_key }")
                        else :
                            full_mega_url_with_key =full_mega_url 
                    else :
                        full_mega_url_with_key =full_mega_url 
                    drive_download_mega_file (full_mega_url_with_key ,self .download_base_path ,logger_func =self .parent_logger_func )
                elif platform =='google drive':
                    download_gdrive_file (full_mega_url ,self .download_base_path ,logger_func =self .parent_logger_func )
                elif platform =='dropbox':
                    download_dropbox_file (full_mega_url ,self .download_base_path ,logger_func =self .parent_logger_func )
                else :
                    self .progress_signal .emit (f"⚠️ Unsupported platform '{platform }' for link: {full_mega_url }")
                    self .file_complete_signal .emit (full_mega_url ,False )
                    continue 
                self .file_complete_signal .emit (full_mega_url ,True )
            except Exception as e :
                self .progress_signal .emit (f"❌ Error downloading ({platform .upper ()}) link '{full_mega_url }' (from post '{post_title }'): {e }")
                self .file_complete_signal .emit (full_mega_url ,False )
        self .finished_signal .emit ()

    def cancel (self ):
        self .is_cancelled =True 

class DynamicFilterHolder :
    def __init__ (self ,initial_filters =None ):
        self .lock =threading .Lock ()
        self ._filters =initial_filters if initial_filters is not None else []

    def get_filters (self ):
        with self .lock :
            return [dict (f )for f in self ._filters ]

    def set_filters (self ,new_filters ):
        with self .lock :
            self ._filters =[dict (f )for f in (new_filters if new_filters else [])]

class DownloaderApp (QWidget ):
    character_prompt_response_signal =pyqtSignal (bool )
    log_signal =pyqtSignal (str )
    add_character_prompt_signal =pyqtSignal (str )
    overall_progress_signal =pyqtSignal (int ,int )
    file_successfully_downloaded_signal = pyqtSignal(dict) # For actually downloaded files    
    post_processed_for_history_signal = pyqtSignal(dict) # For history data from DownloadThread   
    finished_signal =pyqtSignal (int ,int ,bool ,list )
    external_link_signal =pyqtSignal (str ,str ,str ,str ,str )
    file_progress_signal =pyqtSignal (str ,object )


    def __init__ (self ):
        super ().__init__ ()
        self .settings =QSettings (CONFIG_ORGANIZATION_NAME ,CONFIG_APP_NAME_MAIN )
        if getattr (sys ,'frozen',False ):
            self .app_base_dir =os .path .dirname (sys .executable )
        else :
            self .app_base_dir =os .path .dirname (os .path .abspath (__file__ ))
        self .config_file =os .path .join (self .app_base_dir ,"Known.txt")

        self .download_thread =None 
        self .thread_pool =None 
        self .cancellation_event =threading .Event ()
        self .external_link_download_thread =None 
        self .pause_event =threading .Event ()
        self .active_futures =[]
        self .total_posts_to_process =0 
        self .dynamic_character_filter_holder =DynamicFilterHolder ()
        self .processed_posts_count =0 
        self.creator_name_cache = {} # Initialize creator_name_cache
        self.log_signal.emit(f"ℹ️ App base directory: {self.app_base_dir}")
        
        # Persistent History Setup
        app_data_path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        self.last_downloaded_files_details = deque(maxlen=3) # For the new left-pane history       
        if not app_data_path: # Fallback if AppDataLocation is not available
            app_data_path = os.path.join(self.app_base_dir, "app_data")
        self.persistent_history_file = os.path.join(app_data_path, CONFIG_ORGANIZATION_NAME, CONFIG_APP_NAME_MAIN, "download_history.json")
        self.download_history_candidates = deque(maxlen=8)
        self.log_signal.emit(f"ℹ️ Persistent history file path set to: {self.persistent_history_file}")     
        self.final_download_history_entries = []   
        self .favorite_download_queue =deque ()
        self .is_processing_favorites_queue =False 
        self .download_counter =0 
        self .favorite_download_queue =deque ()
        self .permanently_failed_files_for_dialog =[]
        self .last_link_input_text_for_queue_sync =""
        self .is_fetcher_thread_running =False 
        self ._restart_pending =False 
        self .is_processing_favorites_queue =False 
        self.download_history_log = deque(maxlen=50) # For storing recent download history       
        self .skip_counter =0 
        self .all_kept_original_filenames =[]
        self .cancellation_message_logged_this_session =False 
        self .favorite_scope_toggle_button =None 
        self .favorite_download_scope =FAVORITE_SCOPE_SELECTED_LOCATION 

        self .manga_mode_checkbox =None 

        self .selected_cookie_filepath =None 
        self .retryable_failed_files_info =[]

        self .is_paused =False 
        self .worker_to_gui_queue =queue .Queue ()
        self .gui_update_timer =QTimer (self )
        self .actual_gui_signals =PostProcessorSignals ()

        self .worker_signals =PostProcessorSignals ()
        self .prompt_mutex =QMutex ()
        self ._add_character_response =None 

        self ._original_scan_content_tooltip =("If checked, the downloader will scan the HTML content of posts for image URLs (from <img> tags or direct links).\n"
        "now This includes resolving relative paths from <img> tags to full URLs.\n"
        "Relative paths in <img> tags (e.g., /data/image.jpg) will be resolved to full URLs.\n"
        "Useful for cases where images are in the post description but not in the API's file/attachment list.")

        self .downloaded_files =set ()
        self .downloaded_files_lock =threading .Lock ()
        self .downloaded_file_hashes =set ()
        self .downloaded_file_hashes_lock =threading .Lock ()

        self .show_external_links =False 
        self .external_link_queue =deque ()
        self ._is_processing_external_link_queue =False 
        self ._current_link_post_title =None 
        self .extracted_links_cache =[]
        self .manga_rename_toggle_button =None 
        self .favorite_mode_checkbox =None 
        self .url_or_placeholder_stack =None 
        self .url_input_widget =None 
        self .url_placeholder_widget =None 
        self .favorite_action_buttons_widget =None 
        self .favorite_mode_artists_button =None 
        self .favorite_mode_posts_button =None 
        self .standard_action_buttons_widget =None 
        self .bottom_action_buttons_stack =None 
        self .main_log_output =None 
        self .external_log_output =None 
        self .log_splitter =None 
        self .main_splitter =None 
        self .reset_button =None 
        self .progress_log_label =None 
        self .log_verbosity_toggle_button =None 

        self .missed_character_log_output =None 
        self .log_view_stack =None 
        self .current_log_view ='progress'

        self .link_search_input =None 
        self .link_search_button =None 
        self .export_links_button =None 
        self .radio_only_links =None 
        self .radio_only_archives =None 
        self .missed_title_key_terms_count ={}
        self .missed_title_key_terms_examples ={}
        self .logged_summary_for_key_term =set ()
        self .STOP_WORDS =set (["a","an","the","is","was","were","of","for","with","in","on","at","by","to","and","or","but","i","you","he","she","it","we","they","my","your","his","her","its","our","their","com","net","org","www"])
        self .already_logged_bold_key_terms =set ()
        self .missed_key_terms_buffer =[]
        self .char_filter_scope_toggle_button =None 
        self .skip_words_scope =SKIP_SCOPE_POSTS 
        self .char_filter_scope =CHAR_SCOPE_TITLE 
        self .manga_filename_style =self .settings .value (MANGA_FILENAME_STYLE_KEY ,STYLE_POST_TITLE ,type =str )
        self .current_theme =self .settings .value (THEME_KEY ,"dark",type =str )
        self .only_links_log_display_mode =LOG_DISPLAY_LINKS 
        self .mega_download_log_preserved_once =False 
        self .allow_multipart_download_setting =False 
        self .use_cookie_setting =False 
        self .scan_content_images_setting =self .settings .value (SCAN_CONTENT_IMAGES_KEY ,False ,type =bool )
        self .cookie_text_setting =""
        self .current_selected_language =self .settings .value (LANGUAGE_KEY ,"en",type =str )

        print (f"ℹ️ Known.txt will be loaded/saved at: {self .config_file }")

        # Explicitly set window icon for the main app window
        # This is in addition to QApplication.setWindowIcon in if __name__ == '__main__'
        try:
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # PyInstaller-like bundle
                base_dir_for_icon = sys._MEIPASS
            else:
                # Running as a script
                base_dir_for_icon = os.path.dirname(os.path.abspath(__file__))

            icon_path_for_window = os.path.join(base_dir_for_icon, 'assets', 'Kemono.ico') # <--- This is for QWidget
            if os.path.exists(icon_path_for_window):
                self.setWindowIcon(QIcon(icon_path_for_window))
            else:
                self.log_signal.emit(f"⚠️ Main window icon 'assets/Kemono.ico' not found at {icon_path_for_window} (tried in DownloaderApp init)")
        except Exception as e_icon_app:
            self.log_signal.emit(f"❌ Error setting main window icon in DownloaderApp init: {e_icon_app}")

        self .url_label_widget =None 
        self .download_location_label_widget =None 

        self .remove_from_filename_label_widget =None 
        self .skip_words_label_widget =None 

        self .setWindowTitle ("Kemono Downloader v5.0.0")

        self .init_ui ()
        self ._connect_signals ()
        self .log_signal .emit ("ℹ️ Local API server functionality has been removed.")
        self .log_signal .emit ("ℹ️ 'Skip Current File' button has been removed.")
        if hasattr (self ,'character_input'):
            self .character_input .setToolTip (self ._tr ("character_input_tooltip","Enter character names (comma-separated)..."))
        self .log_signal .emit (f"ℹ️ Manga filename style loaded: '{self .manga_filename_style }'")
        self .log_signal .emit (f"ℹ️ Skip words scope loaded: '{self .skip_words_scope }'")
        self .log_signal .emit (f"ℹ️ Character filter scope set to default: '{self .char_filter_scope }'")
        self .log_signal .emit (f"ℹ️ Multi-part download defaults to: {'Enabled'if self .allow_multipart_download_setting else 'Disabled'}")
        self .log_signal .emit (f"ℹ️ Cookie text defaults to: Empty on launch")
        self .log_signal .emit (f"ℹ️ 'Use Cookie' setting defaults to: Disabled on launch")
        self .log_signal .emit (f"ℹ️ Scan post content for images defaults to: {'Enabled'if self .scan_content_images_setting else 'Disabled'}")
        self .log_signal .emit (f"ℹ️ Application language loaded: '{self .current_selected_language .upper ()}' (UI may not reflect this yet).")
        self ._retranslate_main_ui ()
        self._load_persistent_history() # Load history after UI is mostly set up


    def _tr (self ,key ,default_text =""):
        """Helper to get translation based on current app language for the main window."""
        if callable (get_translation ):
            return get_translation (self .current_selected_language ,key ,default_text )
        return default_text 

    def _initialize_persistent_history_path(self):
        documents_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        if not documents_path: # Fallback if DocumentsLocation is not available
            self.log_signal.emit("⚠️ DocumentsLocation not found. Falling back to app base directory for history.")
            documents_path = self.app_base_dir # Fallback to app's base directory
        
        history_folder_name = "history" # User wants a folder named "history"
        self.persistent_history_file = os.path.join(documents_path, history_folder_name, "download_history.json")
        self.log_signal.emit(f"ℹ️ Persistent history file path set to: {self.persistent_history_file}")

    def _retranslate_main_ui (self ):
        """Retranslates static text elements in the main UI."""
        if self .url_label_widget :
            self .url_label_widget .setText (self ._tr ("creator_post_url_label","🔗 Kemono Creator/Post URL:"))
        if self .download_location_label_widget :
            self .download_location_label_widget .setText (self ._tr ("download_location_label","📁 Download Location:"))
        if hasattr (self ,'character_label')and self .character_label :
            self .character_label .setText (self ._tr ("filter_by_character_label","🎯 Filter by Character(s) (comma-separated):"))
        if self .skip_words_label_widget :
            self .skip_words_label_widget .setText (self ._tr ("skip_with_words_label","🚫 Skip with Words (comma-separated):"))
        if self .remove_from_filename_label_widget :
            self .remove_from_filename_label_widget .setText (self ._tr ("remove_words_from_name_label","✂️ Remove Words from name:"))
        if hasattr (self ,'radio_all'):self .radio_all .setText (self ._tr ("filter_all_radio","All"))
        if hasattr (self ,'radio_images'):self .radio_images .setText (self ._tr ("filter_images_radio","Images/GIFs"))
        if hasattr (self ,'radio_videos'):self .radio_videos .setText (self ._tr ("filter_videos_radio","Videos"))
        if hasattr (self ,'radio_only_archives'):self .radio_only_archives .setText (self ._tr ("filter_archives_radio","📦 Only Archives"))
        if hasattr (self ,'radio_only_links'):self .radio_only_links .setText (self ._tr ("filter_links_radio","🔗 Only Links"))
        if hasattr (self ,'radio_only_audio'):self .radio_only_audio .setText (self ._tr ("filter_audio_radio","🎧 Only Audio"))
        if hasattr (self ,'favorite_mode_checkbox'):self .favorite_mode_checkbox .setText (self ._tr ("favorite_mode_checkbox_label","⭐ Favorite Mode"))
        if hasattr (self ,'dir_button'):self .dir_button .setText (self ._tr ("browse_button_text","Browse..."))
        self ._update_char_filter_scope_button_text ()
        self ._update_skip_scope_button_text ()

        if hasattr (self ,'skip_zip_checkbox'):self .skip_zip_checkbox .setText (self ._tr ("skip_zip_checkbox_label","Skip .zip"))
        if hasattr (self ,'skip_rar_checkbox'):self .skip_rar_checkbox .setText (self ._tr ("skip_rar_checkbox_label","Skip .rar"))
        if hasattr (self ,'download_thumbnails_checkbox'):self .download_thumbnails_checkbox .setText (self ._tr ("download_thumbnails_checkbox_label","Download Thumbnails Only"))
        if hasattr (self ,'scan_content_images_checkbox'):self .scan_content_images_checkbox .setText (self ._tr ("scan_content_images_checkbox_label","Scan Content for Images"))
        if hasattr (self ,'compress_images_checkbox'):self .compress_images_checkbox .setText (self ._tr ("compress_images_checkbox_label","Compress to WebP"))
        if hasattr (self ,'use_subfolders_checkbox'):self .use_subfolders_checkbox .setText (self ._tr ("separate_folders_checkbox_label","Separate Folders by Name/Title"))
        if hasattr (self ,'use_subfolder_per_post_checkbox'):self .use_subfolder_per_post_checkbox .setText (self ._tr ("subfolder_per_post_checkbox_label","Subfolder per Post"))
        if hasattr (self ,'use_cookie_checkbox'):self .use_cookie_checkbox .setText (self ._tr ("use_cookie_checkbox_label","Use Cookie"))
        if hasattr (self ,'use_multithreading_checkbox'):self .update_multithreading_label (self .thread_count_input .text ()if hasattr (self ,'thread_count_input')else "1")
        if hasattr (self ,'external_links_checkbox'):self .external_links_checkbox .setText (self ._tr ("show_external_links_checkbox_label","Show External Links in Log"))
        if hasattr (self ,'manga_mode_checkbox'):self .manga_mode_checkbox .setText (self ._tr ("manga_comic_mode_checkbox_label","Manga/Comic Mode"))
        if hasattr (self ,'thread_count_label'):self .thread_count_label .setText (self ._tr ("threads_label","Threads:"))

        if hasattr (self ,'character_input'):
            self .character_input .setToolTip (self ._tr ("character_input_tooltip","Enter character names (comma-separated)..."))
        if hasattr (self ,'download_btn'):self .download_btn .setToolTip (self ._tr ("start_download_button_tooltip","Click to start the download or link extraction process with the current settings."))





        current_download_is_active =self ._is_download_active ()if hasattr (self ,'_is_download_active')else False 
        self .set_ui_enabled (not current_download_is_active )

        if hasattr (self ,'known_chars_label'):self .known_chars_label .setText (self ._tr ("known_chars_label_text","🎭 Known Shows/Characters (for Folder Names):"))
        if hasattr (self ,'open_known_txt_button'):self .open_known_txt_button .setText (self ._tr ("open_known_txt_button_text","Open Known.txt"));self .open_known_txt_button .setToolTip (self ._tr ("open_known_txt_button_tooltip","Open the 'Known.txt' file..."))
        if hasattr (self ,'add_char_button'):self .add_char_button .setText (self ._tr ("add_char_button_text","➕ Add"));self .add_char_button .setToolTip (self ._tr ("add_char_button_tooltip","Add the name from the input field..."))
        if hasattr (self ,'add_to_filter_button'):self .add_to_filter_button .setText (self ._tr ("add_to_filter_button_text","⤵️ Add to Filter"));self .add_to_filter_button .setToolTip (self ._tr ("add_to_filter_button_tooltip","Select names from 'Known Shows/Characters' list..."))
        if hasattr (self ,'character_list'):
            self .character_list .setToolTip (self ._tr ("known_chars_list_tooltip","This list contains names used for automatic folder creation..."))
        if hasattr (self ,'delete_char_button'):self .delete_char_button .setText (self ._tr ("delete_char_button_text","🗑️ Delete Selected"));self .delete_char_button .setToolTip (self ._tr ("delete_char_button_tooltip","Delete the selected name(s)..."))

        if hasattr (self ,'cancel_btn'):self .cancel_btn .setToolTip (self ._tr ("cancel_button_tooltip","Click to cancel the ongoing download/extraction process and reset the UI fields (preserving URL and Directory)."))
        if hasattr (self ,'error_btn'):self .error_btn .setText (self ._tr ("error_button_text","Error"));self .error_btn .setToolTip (self ._tr ("error_button_tooltip","View files skipped due to errors and optionally retry them."))
        if hasattr (self ,'progress_log_label'):self .progress_log_label .setText (self ._tr ("progress_log_label_text","📜 Progress Log:"))
        if hasattr (self ,'reset_button'):self .reset_button .setText (self ._tr ("reset_button_text","🔄 Reset"));self .reset_button .setToolTip (self ._tr ("reset_button_tooltip","Reset all inputs and logs to default state (only when idle)."))
        self ._update_multipart_toggle_button_text ()
        if hasattr (self ,'progress_label')and not self ._is_download_active ():self .progress_label .setText (self ._tr ("progress_idle_text","Progress: Idle"))
        if hasattr (self ,'favorite_mode_artists_button'):self .favorite_mode_artists_button .setText (self ._tr ("favorite_artists_button_text","🖼️ Favorite Artists"));self .favorite_mode_artists_button .setToolTip (self ._tr ("favorite_artists_button_tooltip","Browse and download from your favorite artists..."))
        if hasattr (self ,'favorite_mode_posts_button'):self .favorite_mode_posts_button .setText (self ._tr ("favorite_posts_button_text","📄 Favorite Posts"));self .favorite_mode_posts_button .setToolTip (self ._tr ("favorite_posts_button_tooltip","Browse and download your favorite posts..."))
        self ._update_favorite_scope_button_text ()
        if hasattr (self ,'page_range_label'):self .page_range_label .setText (self ._tr ("page_range_label_text","Page Range:"))
        if hasattr (self ,'start_page_input'):
            self .start_page_input .setPlaceholderText (self ._tr ("start_page_input_placeholder","Start"))
            self .start_page_input .setToolTip (self ._tr ("start_page_input_tooltip","For creator URLs: Specify the starting page number..."))
        if hasattr (self ,'to_label'):self .to_label .setText (self ._tr ("page_range_to_label_text","to"))
        if hasattr (self ,'end_page_input'):
            self .end_page_input .setPlaceholderText (self ._tr ("end_page_input_placeholder","End"))
            self .end_page_input .setToolTip (self ._tr ("end_page_input_tooltip","For creator URLs: Specify the ending page number..."))
        if hasattr (self ,'fav_mode_active_label'):
            self .fav_mode_active_label .setText (self ._tr ("fav_mode_active_label_text","⭐ Favorite Mode is active..."))
        if hasattr (self ,'cookie_browse_button'):
            self .cookie_browse_button .setToolTip (self ._tr ("cookie_browse_button_tooltip","Browse for a cookie file..."))
        self ._update_manga_filename_style_button_text ()
        if hasattr (self ,'export_links_button'):self .export_links_button .setText (self ._tr ("export_links_button_text","Export Links"))
        if hasattr (self ,'download_extracted_links_button'):self .download_extracted_links_button .setText (self ._tr ("download_extracted_links_button_text","Download"))
        self ._update_log_display_mode_button_text ()


        if hasattr (self ,'radio_all'):self .radio_all .setToolTip (self ._tr ("radio_all_tooltip","Download all file types found in posts."))
        if hasattr (self ,'radio_images'):self .radio_images .setToolTip (self ._tr ("radio_images_tooltip","Download only common image formats (JPG, PNG, GIF, WEBP, etc.)."))
        if hasattr (self ,'radio_videos'):self .radio_videos .setToolTip (self ._tr ("radio_videos_tooltip","Download only common video formats (MP4, MKV, WEBM, MOV, etc.)."))
        if hasattr (self ,'radio_only_archives'):self .radio_only_archives .setToolTip (self ._tr ("radio_only_archives_tooltip","Exclusively download .zip and .rar files. Other file-specific options are disabled."))
        if hasattr (self ,'radio_only_audio'):self .radio_only_audio .setToolTip (self ._tr ("radio_only_audio_tooltip","Download only common audio formats (MP3, WAV, FLAC, etc.)."))
        if hasattr (self ,'radio_only_links'):self .radio_only_links .setToolTip (self ._tr ("radio_only_links_tooltip","Extract and display external links from post descriptions instead of downloading files.\nDownload-related options will be disabled."))


        if hasattr (self ,'use_subfolders_checkbox'):self .use_subfolders_checkbox .setToolTip (self ._tr ("use_subfolders_checkbox_tooltip","Create subfolders based on 'Filter by Character(s)' input..."))
        if hasattr (self ,'use_subfolder_per_post_checkbox'):self .use_subfolder_per_post_checkbox .setToolTip (self ._tr ("use_subfolder_per_post_checkbox_tooltip","Creates a subfolder for each post..."))
        if hasattr (self ,'use_cookie_checkbox'):self .use_cookie_checkbox .setToolTip (self ._tr ("use_cookie_checkbox_tooltip","If checked, will attempt to use cookies..."))
        if hasattr (self ,'use_multithreading_checkbox'):self .use_multithreading_checkbox .setToolTip (self ._tr ("use_multithreading_checkbox_tooltip","Enables concurrent operations..."))
        if hasattr (self ,'thread_count_input'):self .thread_count_input .setToolTip (self ._tr ("thread_count_input_tooltip","Number of concurrent operations..."))
        if hasattr (self ,'external_links_checkbox'):self .external_links_checkbox .setToolTip (self ._tr ("external_links_checkbox_tooltip","If checked, a secondary log panel appears..."))
        if hasattr (self ,'manga_mode_checkbox'):self .manga_mode_checkbox .setToolTip (self ._tr ("manga_mode_checkbox_tooltip","Downloads posts from oldest to newest..."))

        if hasattr (self ,'scan_content_images_checkbox'):self .scan_content_images_checkbox .setToolTip (self ._tr ("scan_content_images_checkbox_tooltip",self ._original_scan_content_tooltip ))
        if hasattr (self ,'download_thumbnails_checkbox'):self .download_thumbnails_checkbox .setToolTip (self ._tr ("download_thumbnails_checkbox_tooltip","Downloads small preview images..."))
        if hasattr (self ,'skip_words_input'):
            self .skip_words_input .setToolTip (self ._tr ("skip_words_input_tooltip",
            ("Enter words, comma-separated, to skip downloading certain content (e.g., WIP, sketch, preview).\n\n"
            "The 'Scope: [Type]' button next to this input cycles how this filter applies:\n"
            "- Scope: Files: Skips individual files if their names contain any of these words.\n"
            "- Scope: Posts: Skips entire posts if their titles contain any of these words.\n"
            "- Scope: Both: Applies both (post title first, then individual files if post title is okay).")))
        if hasattr (self ,'remove_from_filename_input'):
            self .remove_from_filename_input .setToolTip (self ._tr ("remove_words_input_tooltip",
            ("Enter words, comma-separated, to remove from downloaded filenames (case-insensitive).\n"
            "Useful for cleaning up common prefixes/suffixes.\nExample: patreon, kemono, [HD], _final")))

        if hasattr (self ,'link_input'):
            self .link_input .setPlaceholderText (self ._tr ("link_input_placeholder_text","e.g., https://kemono.su/patreon/user/12345 or .../post/98765"))
            self .link_input .setToolTip (self ._tr ("link_input_tooltip_text","Enter the full URL..."))
        if hasattr (self ,'dir_input'):
            self .dir_input .setPlaceholderText (self ._tr ("dir_input_placeholder_text","Select folder where downloads will be saved"))
            self .dir_input .setToolTip (self ._tr ("dir_input_tooltip_text","Enter or browse to the main folder..."))
        if hasattr (self ,'character_input'):
            self .character_input .setPlaceholderText (self ._tr ("character_input_placeholder_text","e.g., Tifa, Aerith, (Cloud, Zack)"))
        if hasattr (self ,'custom_folder_input'):
            self .custom_folder_input .setPlaceholderText (self ._tr ("custom_folder_input_placeholder_text","Optional: Save this post to specific folder"))
            self .custom_folder_input .setToolTip (self ._tr ("custom_folder_input_tooltip_text","If downloading a single post URL..."))
        if hasattr (self ,'skip_words_input'):
            self .skip_words_input .setPlaceholderText (self ._tr ("skip_words_input_placeholder_text","e.g., WM, WIP, sketch, preview"))
        if hasattr (self ,'remove_from_filename_input'):
            self .remove_from_filename_input .setPlaceholderText (self ._tr ("remove_from_filename_input_placeholder_text","e.g., patreon, HD"))
        self ._update_cookie_input_placeholders_and_tooltips ()
        if hasattr (self ,'character_search_input'):
            self .character_search_input .setPlaceholderText (self ._tr ("character_search_input_placeholder_text","Search characters..."))
            self .character_search_input .setToolTip (self ._tr ("character_search_input_tooltip_text","Type here to filter the list..."))
        if hasattr (self ,'new_char_input'):
            self .new_char_input .setPlaceholderText (self ._tr ("new_char_input_placeholder_text","Add new show/character name"))
            self .new_char_input .setToolTip (self ._tr ("new_char_input_tooltip_text","Enter a new show, game, or character name..."))
        if hasattr (self ,'link_search_input'):
            self .link_search_input .setPlaceholderText (self ._tr ("link_search_input_placeholder_text","Search Links..."))
            self .link_search_input .setToolTip (self ._tr ("link_search_input_tooltip_text","When in 'Only Links' mode..."))
        if hasattr (self ,'manga_date_prefix_input'):
            self .manga_date_prefix_input .setPlaceholderText (self ._tr ("manga_date_prefix_input_placeholder_text","Prefix for Manga Filenames"))
            self .manga_date_prefix_input .setToolTip (self ._tr ("manga_date_prefix_input_tooltip_text","Optional prefix for 'Date Based'..."))
        if hasattr (self ,'empty_popup_button'):self .empty_popup_button .setToolTip (self ._tr ("empty_popup_button_tooltip_text","Open Creator Selection..."))
        if hasattr (self ,'known_names_help_button'):self .known_names_help_button .setToolTip (self ._tr ("known_names_help_button_tooltip_text","Open the application feature guide."))
        if hasattr (self ,'future_settings_button'):self .future_settings_button .setToolTip (self ._tr ("future_settings_button_tooltip_text","Open application settings..."))
        if hasattr (self ,'link_search_button'):self .link_search_button .setToolTip (self ._tr ("link_search_button_tooltip_text","Filter displayed links"))
    def apply_theme (self ,theme_name ,initial_load =False ):
        self .current_theme =theme_name 
        if not initial_load :
            self .settings .setValue (THEME_KEY ,theme_name )
            self .settings .sync ()

        if theme_name =="dark":
            self .setStyleSheet (self .get_dark_theme ())
            if not initial_load :
                self .log_signal .emit ("🎨 Switched to Dark Mode.")
        else :
            self .setStyleSheet ("")
            if not initial_load :
                self .log_signal .emit ("🎨 Switched to Light Mode.")
        self .update ()

    def _get_tooltip_for_character_input (self ):
        return (
        self ._tr ("character_input_tooltip","Default tooltip if translation fails.")
        )
    def _connect_signals (self ):
        self .actual_gui_signals .progress_signal .connect (self .handle_main_log )
        self .actual_gui_signals .file_progress_signal .connect (self .update_file_progress_display )
        self .actual_gui_signals .missed_character_post_signal .connect (self .handle_missed_character_post )
        self .actual_gui_signals .external_link_signal .connect (self .handle_external_link_signal )
        self .actual_gui_signals .file_successfully_downloaded_signal.connect(self._handle_actual_file_downloaded) # Connect new signal      
        self .actual_gui_signals .file_download_status_signal .connect (lambda status :None )

        if hasattr (self ,'character_input'):
            self .character_input .textChanged .connect (self ._on_character_input_changed_live )
        if hasattr (self ,'use_cookie_checkbox'):
            self .use_cookie_checkbox .toggled .connect (self ._update_cookie_input_visibility )
        if hasattr (self ,'link_input'):
            self .link_input .textChanged .connect (self ._sync_queue_with_link_input )
        if hasattr (self ,'cookie_browse_button'):
            self .cookie_browse_button .clicked .connect (self ._browse_cookie_file )
        if hasattr (self ,'cookie_text_input'):
            self .cookie_text_input .textChanged .connect (self ._handle_cookie_text_manual_change )
        if hasattr (self ,'download_thumbnails_checkbox'):
            self .download_thumbnails_checkbox .toggled .connect (self ._handle_thumbnail_mode_change )
        self .gui_update_timer .timeout .connect (self ._process_worker_queue )
        self .gui_update_timer .start (100 )
        self .log_signal .connect (self .handle_main_log )
        self .add_character_prompt_signal .connect (self .prompt_add_character )
        self .character_prompt_response_signal .connect (self .receive_add_character_result )
        self .overall_progress_signal .connect (self .update_progress_display )
        self.post_processed_for_history_signal.connect(self._add_to_history_candidates) # Connect new signal     
        self .finished_signal .connect (self .download_finished )
        if hasattr (self ,'character_search_input'):self .character_search_input .textChanged .connect (self .filter_character_list )
        if hasattr (self ,'external_links_checkbox'):self .external_links_checkbox .toggled .connect (self .update_external_links_setting )
        if hasattr (self ,'thread_count_input'):self .thread_count_input .textChanged .connect (self .update_multithreading_label )
        if hasattr (self ,'use_subfolder_per_post_checkbox'):self .use_subfolder_per_post_checkbox .toggled .connect (self .update_ui_for_subfolders )
        if hasattr (self ,'use_multithreading_checkbox'):self .use_multithreading_checkbox .toggled .connect (self ._handle_multithreading_toggle )

        if hasattr (self ,'radio_group')and self .radio_group :
            self .radio_group .buttonToggled .connect (self ._handle_filter_mode_change )

        if self .reset_button :self .reset_button .clicked .connect (self .reset_application_state )
        if self .log_verbosity_toggle_button :self .log_verbosity_toggle_button .clicked .connect (self .toggle_active_log_view )

        if self .link_search_button :self .link_search_button .clicked .connect (self ._filter_links_log )
        if self .link_search_input :
            self .link_search_input .returnPressed .connect (self ._filter_links_log )
            self .link_search_input .textChanged .connect (self ._filter_links_log )
        if self .export_links_button :self .export_links_button .clicked .connect (self ._export_links_to_file )

        if self .manga_mode_checkbox :self .manga_mode_checkbox .toggled .connect (self .update_ui_for_manga_mode )


        if hasattr (self ,'download_extracted_links_button'):
            self .download_extracted_links_button .clicked .connect (self ._show_download_extracted_links_dialog )

        if hasattr (self ,'log_display_mode_toggle_button'):
            self .log_display_mode_toggle_button .clicked .connect (self ._toggle_log_display_mode )

        if self .manga_rename_toggle_button :self .manga_rename_toggle_button .clicked .connect (self ._toggle_manga_filename_style )

        if hasattr (self ,'link_input'):
            self .link_input .textChanged .connect (lambda :self .update_ui_for_manga_mode (self .manga_mode_checkbox .isChecked ()if self .manga_mode_checkbox else False ))

        if self .skip_scope_toggle_button :
            self .skip_scope_toggle_button .clicked .connect (self ._cycle_skip_scope )

        if self .char_filter_scope_toggle_button :
            self .char_filter_scope_toggle_button .clicked .connect (self ._cycle_char_filter_scope )

        if hasattr (self ,'multipart_toggle_button'):self .multipart_toggle_button .clicked .connect (self ._toggle_multipart_mode )


        if hasattr (self ,'favorite_mode_checkbox'):
            self .favorite_mode_checkbox .toggled .connect (self ._handle_favorite_mode_toggle )

        if hasattr (self ,'open_known_txt_button'):
            self .open_known_txt_button .clicked .connect (self ._open_known_txt_file )

        if hasattr (self ,'add_to_filter_button'):
            self .add_to_filter_button .clicked .connect (self ._show_add_to_filter_dialog )
        if hasattr (self ,'favorite_mode_artists_button'):
            self .favorite_mode_artists_button .clicked .connect (self ._show_favorite_artists_dialog )
        if hasattr (self ,'favorite_mode_posts_button'):
            self .favorite_mode_posts_button .clicked .connect (self ._show_favorite_posts_dialog )
        if hasattr (self ,'favorite_scope_toggle_button'):
            self .favorite_scope_toggle_button .clicked .connect (self ._cycle_favorite_scope )
        if hasattr(self, 'history_button'): # Connect history button
            self.history_button.clicked.connect(self._show_download_history_dialog)       
        if hasattr (self ,'error_btn'):
            self .error_btn .clicked .connect (self ._show_error_files_dialog )

    def _on_character_input_changed_live (self ,text ):
        """
        Called when the character input field text changes.
        If a download is active (running or paused), this updates the dynamic filter holder.
        """
        if self ._is_download_active ():
            QCoreApplication .processEvents ()
            raw_character_filters_text =self .character_input .text ().strip ()
            parsed_filters =self ._parse_character_filters (raw_character_filters_text )

            self .dynamic_character_filter_holder .set_filters (parsed_filters )

    def _parse_character_filters (self ,raw_text ):
        """Helper to parse character filter string into list of objects."""
        parsed_character_filter_objects =[]
        if raw_text :
            raw_parts =[]
            current_part_buffer =""
            in_group_parsing =False 
            for char_token in raw_text :
                if char_token =='('and not in_group_parsing :
                    in_group_parsing =True 
                    current_part_buffer +=char_token 
                elif char_token ==')'and in_group_parsing :
                    in_group_parsing =False 
                    current_part_buffer +=char_token 
                elif char_token ==','and not in_group_parsing :
                    if current_part_buffer .strip ():raw_parts .append (current_part_buffer .strip ())
                    current_part_buffer =""
                else :
                    current_part_buffer +=char_token 
            if current_part_buffer .strip ():raw_parts .append (current_part_buffer .strip ())

            for part_str in raw_parts :
                part_str =part_str .strip ()
                if not part_str :continue 

                is_tilde_group =part_str .startswith ("(")and part_str .endswith (")~")
                is_standard_group_for_splitting =part_str .startswith ("(")and part_str .endswith (")")and not is_tilde_group 

                if is_tilde_group :
                    group_content_str =part_str [1 :-2 ].strip ()
                    aliases_in_group =[alias .strip ()for alias in group_content_str .split (',')if alias .strip ()]
                    if aliases_in_group :
                        group_folder_name =" ".join (aliases_in_group )
                        parsed_character_filter_objects .append ({"name":group_folder_name ,"is_group":True ,"aliases":aliases_in_group })
                elif is_standard_group_for_splitting :
                    group_content_str =part_str [1 :-1 ].strip ()
                    aliases_in_group =[alias .strip ()for alias in group_content_str .split (',')if alias .strip ()]
                    if aliases_in_group :
                        group_folder_name =" ".join (aliases_in_group )
                        parsed_character_filter_objects .append ({
                        "name":group_folder_name ,
                        "is_group":True ,
                        "aliases":aliases_in_group ,
                        "components_are_distinct_for_known_txt":True 
                        })
                else :
                    parsed_character_filter_objects .append ({"name":part_str ,"is_group":False ,"aliases":[part_str ],"components_are_distinct_for_known_txt":False })
        return parsed_character_filter_objects 

    def _process_worker_queue (self ):
        """Processes messages from the worker queue and emits Qt signals from the GUI thread."""
        while not self .worker_to_gui_queue .empty ():
            try :
                item =self .worker_to_gui_queue .get_nowait ()
                signal_type =item .get ('type')
                payload =item .get ('payload',tuple ())

                if signal_type =='progress':
                    self .actual_gui_signals .progress_signal .emit (*payload )
                elif signal_type =='file_download_status':
                    self .actual_gui_signals .file_download_status_signal .emit (*payload )
                elif signal_type =='external_link':
                    self .actual_gui_signals .external_link_signal .emit (*payload )
                elif signal_type =='file_progress':
                    self .actual_gui_signals .file_progress_signal .emit (*payload )
                elif signal_type =='missed_character_post':
                    self .actual_gui_signals .missed_character_post_signal .emit (*payload )
                elif signal_type == 'file_successfully_downloaded': # Handle new signal type from queue
                    self._handle_actual_file_downloaded(payload[0] if payload else {})               
                elif signal_type == 'file_successfully_downloaded':
                    self._handle_file_successfully_downloaded(payload[0]) # payload is (history_entry_dict,)              
                else :
                    self .log_signal .emit (f"⚠️ Unknown signal type from worker queue: {signal_type }")
                self .worker_to_gui_queue .task_done ()
            except queue .Empty :
                break 
            except Exception as e :
                self .log_signal .emit (f"❌ Error processing worker queue: {e }")

    def load_known_names_from_util (self ):
        global KNOWN_NAMES 
        if os .path .exists (self .config_file ):
            parsed_known_objects =[]
            try :
                with open (self .config_file ,'r',encoding ='utf-8')as f :
                    for line_num ,line in enumerate (f ,1 ):
                        line =line .strip ()
                        if not line :continue 

                        if line .startswith ("(")and line .endswith (")"):
                            content =line [1 :-1 ].strip ()
                            parts =[p .strip ()for p in content .split (',')if p .strip ()]
                            if parts :
                                folder_name_raw =content .replace (',',' ')
                                folder_name_cleaned =clean_folder_name (folder_name_raw )

                                unique_aliases_set ={p for p in parts }
                                final_aliases_list =sorted (list (unique_aliases_set ),key =str .lower )

                                if not folder_name_cleaned :
                                    if hasattr (self ,'log_signal'):self .log_signal .emit (f"⚠️ Group resulted in empty folder name after cleaning in Known.txt on line {line_num }: '{line }'. Skipping entry.")
                                    continue 

                                parsed_known_objects .append ({
                                "name":folder_name_cleaned ,
                                "is_group":True ,
                                "aliases":final_aliases_list 
                                })
                            else :
                                if hasattr (self ,'log_signal'):self .log_signal .emit (f"⚠️ Empty group found in Known.txt on line {line_num }: '{line }'")
                        else :
                            parsed_known_objects .append ({
                            "name":line ,
                            "is_group":False ,
                            "aliases":[line ]
                            })
                parsed_known_objects .sort (key =lambda x :x ["name"].lower ())
                KNOWN_NAMES [:]=parsed_known_objects 
                log_msg =f"ℹ️ Loaded {len (KNOWN_NAMES )} known entries from {self .config_file }"
            except Exception as e :
                log_msg =f"❌ Error loading config '{self .config_file }': {e }"
                QMessageBox .warning (self ,"Config Load Error",f"Could not load list from {self .config_file }:\n{e }")
                KNOWN_NAMES [:]=[]
        else :
            self .character_input .setToolTip ("Names, comma-separated. Group aliases: (alias1, alias2, alias3) becomes folder name 'alias1 alias2 alias3' (after cleaning).\nAll names in the group are used as aliases for matching.\nE.g., yor, (Boa, Hancock, Snake Princess)")
            log_msg =f"ℹ️ Config file '{self .config_file }' not found. It will be created on save."
            KNOWN_NAMES [:]=[]

        if hasattr (self ,'log_signal'):self .log_signal .emit (log_msg )

        if hasattr (self ,'character_list'):
            self .character_list .clear ()
            if not KNOWN_NAMES :
                self .log_signal .emit ("ℹ️ 'Known.txt' is empty or was not found. No default entries will be added.")

            self .character_list .addItems ([entry ["name"]for entry in KNOWN_NAMES ])

    def save_known_names (self ):
        global KNOWN_NAMES 
        try :
            with open (self .config_file ,'w',encoding ='utf-8')as f :
                for entry in KNOWN_NAMES :
                    if entry ["is_group"]:
                        f .write (f"({', '.join (sorted (entry ['aliases'],key =str .lower ))})\n")
                    else :
                        f .write (entry ["name"]+'\n')
            if hasattr (self ,'log_signal'):self .log_signal .emit (f"💾 Saved {len (KNOWN_NAMES )} known entries to {self .config_file }")
        except Exception as e :
            log_msg =f"❌ Error saving config '{self .config_file }': {e }"
            if hasattr (self ,'log_signal'):self .log_signal .emit (log_msg )
            QMessageBox .warning (self ,"Config Save Error",f"Could not save list to {self .config_file }:\n{e }")

    def closeEvent (self ,event ):
        self .save_known_names ()
        self .settings .setValue (MANGA_FILENAME_STYLE_KEY ,self .manga_filename_style )
        self .settings .setValue (ALLOW_MULTIPART_DOWNLOAD_KEY ,self .allow_multipart_download_setting )
        self .settings .setValue (COOKIE_TEXT_KEY ,self .cookie_text_input .text ()if hasattr (self ,'cookie_text_input')else "")
        self .settings .setValue (SCAN_CONTENT_IMAGES_KEY ,self .scan_content_images_checkbox .isChecked ()if hasattr (self ,'scan_content_images_checkbox')else False )
        self .settings .setValue (USE_COOKIE_KEY ,self .use_cookie_checkbox .isChecked ()if hasattr (self ,'use_cookie_checkbox')else False )
        self .settings .setValue (THEME_KEY ,self .current_theme )
        self .settings .setValue (LANGUAGE_KEY ,self .current_selected_language )
        self .settings .sync ()
        self._save_persistent_history() # Ensure history is saved on close

        should_exit =True 
        is_downloading =self ._is_download_active ()

        if is_downloading :
            reply =QMessageBox .question (self ,"Confirm Exit",
            "Download in progress. Are you sure you want to exit and cancel?",
            QMessageBox .Yes |QMessageBox .No ,QMessageBox .No )
            if reply ==QMessageBox .Yes :
                self .log_signal .emit ("⚠️ Cancelling active download due to application exit...")
                self .cancellation_event .set ()
                if self .download_thread and self .download_thread .isRunning ():
                    self .download_thread .requestInterruption ()
                    self .log_signal .emit ("   Signaled single download thread to interrupt.")
                if self .download_thread and self .download_thread .isRunning ():
                    self .log_signal .emit ("   Waiting for single download thread to finish...")
                    self .download_thread .wait (3000 )
                    if self .download_thread .isRunning ():
                        self .log_signal .emit ("   ⚠️ Single download thread did not terminate gracefully.")

                if self .thread_pool :
                    self .log_signal .emit ("   Shutting down thread pool (waiting for completion)...")
                    self .thread_pool .shutdown (wait =True ,cancel_futures =True )
                    self .log_signal .emit ("   Thread pool shutdown complete.")
                    self .thread_pool =None 
                self .log_signal .emit ("   Cancellation for exit complete.")
            else :
                should_exit =False 
                self .log_signal .emit ("ℹ️ Application exit cancelled.")
                event .ignore ()
                return 

        if should_exit :
            self .log_signal .emit ("ℹ️ Application closing.")
            if self .thread_pool :
                self .log_signal .emit ("   Final thread pool check: Shutting down...")
                self .cancellation_event .set ()
                self .thread_pool .shutdown (wait =True ,cancel_futures =True )
                self .thread_pool =None 
            self .log_signal .emit ("👋 Exiting application.")
            event .accept ()


    def _request_restart_application (self ):
        self .log_signal .emit ("🔄 Application restart requested by user for language change.")
        self ._restart_pending =True 
        self .close ()

    def _do_actual_restart (self ):
        try :
            self .log_signal .emit ("   Performing application restart...")
            python_executable =sys .executable 
            script_args =sys .argv 


            if getattr (sys ,'frozen',False ):



                QProcess .startDetached (python_executable ,script_args [1 :])
            else :


                QProcess .startDetached (python_executable ,script_args )

            QCoreApplication .instance ().quit ()
        except Exception as e :
            self .log_signal .emit (f"❌ CRITICAL: Failed to start new application instance: {e }")
            QMessageBox .critical (self ,"Restart Failed",
            f"Could not automatically restart the application: {e }\n\nPlease restart it manually.")


    def init_ui (self ):
        self .main_splitter =QSplitter (Qt .Horizontal )
        left_panel_widget =QWidget ()
        right_panel_widget =QWidget ()
        left_layout =QVBoxLayout (left_panel_widget )
        right_layout =QVBoxLayout (right_panel_widget )
        left_layout .setContentsMargins (10 ,10 ,10 ,10 )
        right_layout .setContentsMargins (10 ,10 ,10 ,10 )
        self .apply_theme (self .current_theme ,initial_load =True )

        self .url_input_widget =QWidget ()
        url_input_layout =QHBoxLayout (self .url_input_widget )
        url_input_layout .setContentsMargins (0 ,0 ,0 ,0 )

        self .url_label_widget =QLabel ()
        url_input_layout .addWidget (self .url_label_widget )
        self .link_input =QLineEdit ()
        self .link_input .setPlaceholderText ("e.g., https://kemono.su/patreon/user/12345 or .../post/98765")
        self .link_input .textChanged .connect (self .update_custom_folder_visibility )
        url_input_layout .addWidget (self .link_input ,1 )
        self .empty_popup_button =QPushButton ("🎨")
        self .empty_popup_button .setStyleSheet ("padding: 4px 6px;")
        self .empty_popup_button .clicked .connect (self ._show_empty_popup )
        url_input_layout .addWidget (self .empty_popup_button )

        self .page_range_label =QLabel (self ._tr ("page_range_label_text","Page Range:"))
        self .page_range_label .setStyleSheet ("font-weight: bold; padding-left: 10px;")
        url_input_layout .addWidget (self .page_range_label )
        self .start_page_input =QLineEdit ()
        self .start_page_input .setPlaceholderText (self ._tr ("start_page_input_placeholder","Start"))
        self .start_page_input .setFixedWidth (50 )
        self .start_page_input .setValidator (QIntValidator (1 ,99999 ))
        url_input_layout .addWidget (self .start_page_input )
        self .to_label =QLabel (self ._tr ("page_range_to_label_text","to"))
        url_input_layout .addWidget (self .to_label )
        self .end_page_input =QLineEdit ()
        self .end_page_input .setPlaceholderText (self ._tr ("end_page_input_placeholder","End"))
        self .end_page_input .setFixedWidth (50 )
        self .end_page_input .setToolTip (self ._tr ("end_page_input_tooltip","For creator URLs: Specify the ending page number..."))
        self .end_page_input .setValidator (QIntValidator (1 ,99999 ))
        url_input_layout .addWidget (self .end_page_input )

        self .url_placeholder_widget =QWidget ()
        placeholder_layout =QHBoxLayout (self .url_placeholder_widget )
        placeholder_layout .setContentsMargins (0 ,0 ,0 ,0 )
        self .fav_mode_active_label =QLabel (self ._tr ("fav_mode_active_label_text","⭐ Favorite Mode is active..."))
        self .fav_mode_active_label .setAlignment (Qt .AlignCenter )
        placeholder_layout .addWidget (self .fav_mode_active_label )

        self .url_or_placeholder_stack =QStackedWidget ()
        self .url_or_placeholder_stack .addWidget (self .url_input_widget )
        self .url_or_placeholder_stack .addWidget (self .url_placeholder_widget )
        left_layout .addWidget (self .url_or_placeholder_stack )

        self .favorite_action_buttons_widget =QWidget ()
        favorite_buttons_layout =QHBoxLayout (self .favorite_action_buttons_widget )
        favorite_buttons_layout .setContentsMargins (0 ,0 ,0 ,0 )
        self .favorite_mode_artists_button =QPushButton ("🖼️ Favorite Artists")
        self .favorite_mode_artists_button .setToolTip ("Browse and download from your favorite artists on Kemono.su.")
        self .favorite_mode_artists_button .setStyleSheet ("padding: 4px 12px;")
        self .favorite_mode_artists_button .setSizePolicy (QSizePolicy .Expanding ,QSizePolicy .Preferred )
        self .favorite_mode_posts_button =QPushButton ("📄 Favorite Posts")
        self .favorite_mode_posts_button .setToolTip ("Browse and download your favorite posts from Kemono.su.")
        self .favorite_mode_posts_button .setStyleSheet ("padding: 4px 12px;")
        self .favorite_mode_posts_button .setSizePolicy (QSizePolicy .Expanding ,QSizePolicy .Preferred )

        self .favorite_scope_toggle_button =QPushButton ()
        self .favorite_scope_toggle_button .setStyleSheet ("padding: 4px 10px;")
        self .favorite_scope_toggle_button .setSizePolicy (QSizePolicy .Expanding ,QSizePolicy .Preferred )

        favorite_buttons_layout .addWidget (self .favorite_mode_artists_button )
        favorite_buttons_layout .addWidget (self .favorite_mode_posts_button )
        favorite_buttons_layout .addWidget (self .favorite_scope_toggle_button )


        self .download_location_label_widget =QLabel ()
        left_layout .addWidget (self .download_location_label_widget )
        self .dir_input =QLineEdit ()
        self .dir_input .setPlaceholderText ("Select folder where downloads will be saved")
        self .dir_button =QPushButton ("Browse...")
        self .dir_button .setStyleSheet ("padding: 4px 10px;")
        self .dir_button .clicked .connect (self .browse_directory )
        dir_layout =QHBoxLayout ()
        dir_layout .addWidget (self .dir_input ,1 )
        dir_layout .addWidget (self .dir_button )
        left_layout .addLayout (dir_layout )


        self .filters_and_custom_folder_container_widget =QWidget ()
        filters_and_custom_folder_layout =QHBoxLayout (self .filters_and_custom_folder_container_widget )
        filters_and_custom_folder_layout .setContentsMargins (0 ,5 ,0 ,0 )
        filters_and_custom_folder_layout .setSpacing (10 )

        self .character_filter_widget =QWidget ()
        character_filter_v_layout =QVBoxLayout (self .character_filter_widget )
        character_filter_v_layout .setContentsMargins (0 ,0 ,0 ,0 )
        character_filter_v_layout .setSpacing (2 )

        self .character_label =QLabel ("🎯 Filter by Character(s) (comma-separated):")
        character_filter_v_layout .addWidget (self .character_label )

        char_input_and_button_layout =QHBoxLayout ()
        char_input_and_button_layout .setContentsMargins (0 ,0 ,0 ,0 )
        char_input_and_button_layout .setSpacing (10 )

        self .character_input =QLineEdit ()
        self .character_input .setPlaceholderText ("e.g., Tifa, Aerith, (Cloud, Zack)")
        char_input_and_button_layout .addWidget (self .character_input ,3 )


        self .char_filter_scope_toggle_button =QPushButton ()
        self ._update_char_filter_scope_button_text ()
        self .char_filter_scope_toggle_button .setStyleSheet ("padding: 4px 10px;")
        self .char_filter_scope_toggle_button .setMinimumWidth (100 )
        char_input_and_button_layout .addWidget (self .char_filter_scope_toggle_button ,1 )

        character_filter_v_layout .addLayout (char_input_and_button_layout )


        self .custom_folder_widget =QWidget ()
        custom_folder_v_layout =QVBoxLayout (self .custom_folder_widget )
        custom_folder_v_layout .setContentsMargins (0 ,0 ,0 ,0 )
        custom_folder_v_layout .setSpacing (2 )
        self .custom_folder_label =QLabel ("🗄️ Custom Folder Name (Single Post Only):")
        self .custom_folder_input =QLineEdit ()
        self .custom_folder_input .setPlaceholderText ("Optional: Save this post to specific folder")
        custom_folder_v_layout .addWidget (self .custom_folder_label )
        custom_folder_v_layout .addWidget (self .custom_folder_input )
        self .custom_folder_widget .setVisible (False )

        filters_and_custom_folder_layout .addWidget (self .character_filter_widget ,1 )
        filters_and_custom_folder_layout .addWidget (self .custom_folder_widget ,1 )

        left_layout .addWidget (self .filters_and_custom_folder_container_widget )
        word_manipulation_container_widget =QWidget ()
        word_manipulation_outer_layout =QHBoxLayout (word_manipulation_container_widget )
        word_manipulation_outer_layout .setContentsMargins (0 ,0 ,0 ,0 )
        word_manipulation_outer_layout .setSpacing (15 )
        skip_words_widget =QWidget ()
        skip_words_vertical_layout =QVBoxLayout (skip_words_widget )
        skip_words_vertical_layout .setContentsMargins (0 ,0 ,0 ,0 )
        skip_words_vertical_layout .setSpacing (2 )

        self .skip_words_label_widget =QLabel ()
        skip_words_vertical_layout .addWidget (self .skip_words_label_widget )

        skip_input_and_button_layout =QHBoxLayout ()
        skip_input_and_button_layout =QHBoxLayout ()
        skip_input_and_button_layout .setContentsMargins (0 ,0 ,0 ,0 )
        skip_input_and_button_layout .setSpacing (10 )
        self .skip_words_input =QLineEdit ()
        self .skip_words_input .setPlaceholderText ("e.g., WM, WIP, sketch, preview")
        skip_input_and_button_layout .addWidget (self .skip_words_input ,1 )

        self .skip_scope_toggle_button =QPushButton ()
        self ._update_skip_scope_button_text ()
        self .skip_scope_toggle_button .setStyleSheet ("padding: 4px 10px;")
        self .skip_scope_toggle_button .setMinimumWidth (100 )
        skip_input_and_button_layout .addWidget (self .skip_scope_toggle_button ,0 )
        skip_words_vertical_layout .addLayout (skip_input_and_button_layout )
        word_manipulation_outer_layout .addWidget (skip_words_widget ,7 )
        remove_words_widget =QWidget ()
        remove_words_vertical_layout =QVBoxLayout (remove_words_widget )
        remove_words_vertical_layout .setContentsMargins (0 ,0 ,0 ,0 )
        remove_words_vertical_layout .setSpacing (2 )
        self .remove_from_filename_label_widget =QLabel ()
        remove_words_vertical_layout .addWidget (self .remove_from_filename_label_widget )
        self .remove_from_filename_input =QLineEdit ()
        self .remove_from_filename_input .setPlaceholderText ("e.g., patreon, HD")
        remove_words_vertical_layout .addWidget (self .remove_from_filename_input )
        word_manipulation_outer_layout .addWidget (remove_words_widget ,3 )

        left_layout .addWidget (word_manipulation_container_widget )


        file_filter_layout =QVBoxLayout ()
        file_filter_layout .setContentsMargins (0 ,10 ,0 ,0 )
        file_filter_layout .addWidget (QLabel ("Filter Files:"))
        radio_button_layout =QHBoxLayout ()
        radio_button_layout .setSpacing (10 )
        self .radio_group =QButtonGroup (self )
        self .radio_all =QRadioButton ("All")
        self .radio_images =QRadioButton ("Images/GIFs")
        self .radio_videos =QRadioButton ("Videos")
        self .radio_only_archives =QRadioButton ("📦 Only Archives")
        self .radio_only_audio =QRadioButton ("🎧 Only Audio")
        self .radio_only_links =QRadioButton ("🔗 Only Links")
        self .radio_all .setChecked (True )
        self .radio_group .addButton (self .radio_all )
        self .radio_group .addButton (self .radio_images )
        self .radio_group .addButton (self .radio_videos )
        self .radio_group .addButton (self .radio_only_archives )
        self .radio_group .addButton (self .radio_only_audio )
        self .radio_group .addButton (self .radio_only_links )
        radio_button_layout .addWidget (self .radio_all )
        radio_button_layout .addWidget (self .radio_images )
        radio_button_layout .addWidget (self .radio_videos )
        radio_button_layout .addWidget (self .radio_only_archives )
        radio_button_layout .addWidget (self .radio_only_audio )
        file_filter_layout .addLayout (radio_button_layout )
        left_layout .addLayout (file_filter_layout )

        self .favorite_mode_checkbox =QCheckBox ()
        self .favorite_mode_checkbox .setChecked (False )
        radio_button_layout .addWidget (self .radio_only_links )
        radio_button_layout .addWidget (self .favorite_mode_checkbox )
        radio_button_layout .addStretch (1 )
        checkboxes_group_layout =QVBoxLayout ()
        checkboxes_group_layout .setSpacing (10 )

        row1_layout =QHBoxLayout ()
        row1_layout .setSpacing (10 )
        self .skip_zip_checkbox =QCheckBox ("Skip .zip")
        self .skip_zip_checkbox .setChecked (True )
        row1_layout .addWidget (self .skip_zip_checkbox )
        self .skip_rar_checkbox =QCheckBox ("Skip .rar")
        self .skip_rar_checkbox .setChecked (True )
        row1_layout .addWidget (self .skip_rar_checkbox )
        self .download_thumbnails_checkbox =QCheckBox ("Download Thumbnails Only")
        self .download_thumbnails_checkbox .setChecked (False )
        row1_layout .addWidget (self .download_thumbnails_checkbox )

        self .scan_content_images_checkbox =QCheckBox ("Scan Content for Images")
        self .scan_content_images_checkbox .setChecked (self .scan_content_images_setting )
        row1_layout .addWidget (self .scan_content_images_checkbox )

        self .compress_images_checkbox =QCheckBox ("Compress to WebP")
        self .compress_images_checkbox .setChecked (False )
        self .compress_images_checkbox .setToolTip ("Compress images > 1.5MB to WebP format (requires Pillow).")
        row1_layout .addWidget (self .compress_images_checkbox )

        row1_layout .addStretch (1 )
        checkboxes_group_layout .addLayout (row1_layout )

        advanced_settings_label =QLabel ("⚙️ Advanced Settings:")
        checkboxes_group_layout .addWidget (advanced_settings_label )

        advanced_row1_layout =QHBoxLayout ()
        advanced_row1_layout .setSpacing (10 )
        self .use_subfolders_checkbox =QCheckBox ("Separate Folders by Name/Title")
        self .use_subfolders_checkbox .setChecked (True )
        self .use_subfolders_checkbox .toggled .connect (self .update_ui_for_subfolders )
        advanced_row1_layout .addWidget (self .use_subfolders_checkbox )
        self .use_subfolder_per_post_checkbox =QCheckBox ("Subfolder per Post")
        self .use_subfolder_per_post_checkbox .setChecked (False )
        self .use_subfolder_per_post_checkbox .toggled .connect (self .update_ui_for_subfolders )
        advanced_row1_layout .addWidget (self .use_subfolder_per_post_checkbox )

        self .use_cookie_checkbox =QCheckBox ("Use Cookie")
        self .use_cookie_checkbox .setChecked (self .use_cookie_setting )

        self .cookie_text_input =QLineEdit ()
        self .cookie_text_input .setPlaceholderText ("if no Select cookies.txt)")
        self .cookie_text_input .setMinimumHeight (28 )
        self .cookie_text_input .setText (self .cookie_text_setting )

        advanced_row1_layout .addWidget (self .use_cookie_checkbox )
        advanced_row1_layout .addWidget (self .cookie_text_input ,2 )

        self .cookie_browse_button =QPushButton ("Browse...")
        self .cookie_browse_button .setFixedWidth (80 )
        self .cookie_browse_button .setStyleSheet ("padding: 4px 8px;")
        advanced_row1_layout .addWidget (self .cookie_browse_button )

        advanced_row1_layout .addStretch (1 )
        checkboxes_group_layout .addLayout (advanced_row1_layout )

        advanced_row2_layout =QHBoxLayout ()
        advanced_row2_layout .setSpacing (10 )

        multithreading_layout =QHBoxLayout ()
        multithreading_layout .setContentsMargins (0 ,0 ,0 ,0 )
        self .use_multithreading_checkbox =QCheckBox ("Use Multithreading")
        self .use_multithreading_checkbox .setChecked (True )
        multithreading_layout .addWidget (self .use_multithreading_checkbox )
        self .thread_count_label =QLabel ("Threads:")
        multithreading_layout .addWidget (self .thread_count_label )
        self .thread_count_input =QLineEdit ()
        self .thread_count_input .setFixedWidth (40 )
        self .thread_count_input .setText ("4")
        self .thread_count_input .setValidator (QIntValidator (1 ,MAX_THREADS ))
        multithreading_layout .addWidget (self .thread_count_input )
        advanced_row2_layout .addLayout (multithreading_layout )

        self .external_links_checkbox =QCheckBox ("Show External Links in Log")
        self .external_links_checkbox .setChecked (False )
        advanced_row2_layout .addWidget (self .external_links_checkbox )

        self .manga_mode_checkbox =QCheckBox ("Manga/Comic Mode")
        self .manga_mode_checkbox .setChecked (False )

        advanced_row2_layout .addWidget (self .manga_mode_checkbox )


        advanced_row2_layout .addStretch (1 )
        checkboxes_group_layout .addLayout (advanced_row2_layout )
        left_layout .addLayout (checkboxes_group_layout )

        self .standard_action_buttons_widget =QWidget ()
        btn_layout =QHBoxLayout ()
        btn_layout .setContentsMargins (0 ,0 ,0 ,0 )
        btn_layout .setSpacing (10 )
        self .download_btn =QPushButton ("⬇️ Start Download")
        self .download_btn .setStyleSheet ("padding: 4px 12px; font-weight: bold;")
        self .download_btn .clicked .connect (self .start_download )

        self .pause_btn =QPushButton ("⏸️ Pause Download")
        self .pause_btn .setEnabled (False )
        self .pause_btn .setStyleSheet ("padding: 4px 12px;")
        self .pause_btn .clicked .connect (self ._handle_pause_resume_action )

        self .cancel_btn =QPushButton ("❌ Cancel & Reset UI")

        self .cancel_btn .setEnabled (False )
        self .cancel_btn .setStyleSheet ("padding: 4px 12px;")
        self .cancel_btn .clicked .connect (self .cancel_download_button_action )

        self .error_btn =QPushButton ("Error")
        self .error_btn .setToolTip ("View error details (functionality TBD).")
        self .error_btn .setStyleSheet ("padding: 4px 8px;")
        self .error_btn .setEnabled (True )
        btn_layout .addWidget (self .download_btn )
        btn_layout .addWidget (self .pause_btn )
        btn_layout .addWidget (self .cancel_btn )
        btn_layout .addWidget (self .error_btn )
        self .standard_action_buttons_widget .setLayout (btn_layout )

        self .bottom_action_buttons_stack =QStackedWidget ()
        self .bottom_action_buttons_stack .addWidget (self .standard_action_buttons_widget )
        self .bottom_action_buttons_stack .addWidget (self .favorite_action_buttons_widget )
        left_layout .addWidget (self .bottom_action_buttons_stack )
        left_layout .addSpacing (10 )


        known_chars_label_layout =QHBoxLayout ()
        known_chars_label_layout .setSpacing (10 )
        self .known_chars_label =QLabel ("🎭 Known Shows/Characters (for Folder Names):")
        known_chars_label_layout .addWidget (self .known_chars_label )
        self .open_known_txt_button =QPushButton ("Open Known.txt")
        self .open_known_txt_button .setStyleSheet ("padding: 4px 8px;")
        self .open_known_txt_button .setFixedWidth (120 )
        known_chars_label_layout .addWidget (self .open_known_txt_button )
        self .character_search_input =QLineEdit ()
        self .character_search_input .setPlaceholderText ("Search characters...")
        known_chars_label_layout .addWidget (self .character_search_input ,1 )
        left_layout .addLayout (known_chars_label_layout )

        self .character_list =QListWidget ()
        self .character_list .setSelectionMode (QListWidget .ExtendedSelection )
        left_layout .addWidget (self .character_list ,1 )

        char_manage_layout =QHBoxLayout ()
        char_manage_layout .setSpacing (10 )
        self .new_char_input =QLineEdit ()
        self .new_char_input .setPlaceholderText ("Add new show/character name")
        self .new_char_input .setStyleSheet ("padding: 3px 5px;")

        self .add_char_button =QPushButton ("➕ Add")
        self .add_char_button .setStyleSheet ("padding: 4px 10px;")

        self .add_to_filter_button =QPushButton ("⤵️ Add to Filter")
        self .add_to_filter_button .setToolTip ("Select names from 'Known Shows/Characters' list to add to the 'Filter by Character(s)' field above.")
        self .add_to_filter_button .setStyleSheet ("padding: 4px 10px;")

        self .delete_char_button =QPushButton ("🗑️ Delete Selected")
        self .delete_char_button .setToolTip ("Delete the selected name(s) from the 'Known Shows/Characters' list.")
        self .delete_char_button .setStyleSheet ("padding: 4px 10px;")

        self .add_char_button .clicked .connect (self ._handle_ui_add_new_character )
        self .new_char_input .returnPressed .connect (self .add_char_button .click )
        self .delete_char_button .clicked .connect (self .delete_selected_character )

        char_manage_layout .addWidget (self .new_char_input ,2 )
        char_manage_layout .addWidget (self .add_char_button ,0 )

        self .known_names_help_button =QPushButton ("?")
        self .known_names_help_button .setFixedWidth (35 )
        self .known_names_help_button .setStyleSheet ("padding: 4px 6px;")
        self .known_names_help_button .clicked .connect (self ._show_feature_guide )

        self .history_button =QPushButton ("📜") # History emoji
        self .history_button .setFixedWidth (35 )
        self .history_button .setStyleSheet ("padding: 4px 6px;")
        self .history_button .setToolTip (self ._tr ("history_button_tooltip_text","View download history (Not Implemented Yet)"))

        self .future_settings_button =QPushButton ("⚙️")
        self .future_settings_button .setFixedWidth (35 )
        self .future_settings_button .setStyleSheet ("padding: 4px 6px;")
        self .future_settings_button .clicked .connect (self ._show_future_settings_dialog )
        char_manage_layout .addWidget (self .add_to_filter_button ,1 )
        char_manage_layout .addWidget (self .delete_char_button ,1 )
        char_manage_layout .addWidget (self .known_names_help_button ,0 )
        char_manage_layout .addWidget (self .history_button ,0 ) # Add the new history button
        char_manage_layout .addWidget (self .future_settings_button ,0 )
        left_layout .addLayout (char_manage_layout )
        left_layout .addStretch (0 )

        log_title_layout =QHBoxLayout ()
        self .progress_log_label =QLabel ("📜 Progress Log:")
        log_title_layout .addWidget (self .progress_log_label )
        log_title_layout .addStretch (1 )

        self .link_search_input =QLineEdit ()
        self .link_search_input .setPlaceholderText ("Search Links...")
        self .link_search_input .setVisible (False )

        log_title_layout .addWidget (self .link_search_input )
        self .link_search_button =QPushButton ("🔍")
        self .link_search_button .setVisible (False )
        self .link_search_button .setFixedWidth (30 )
        self .link_search_button .setStyleSheet ("padding: 4px 4px;")
        log_title_layout .addWidget (self .link_search_button )

        self .manga_rename_toggle_button =QPushButton ()
        self .manga_rename_toggle_button .setVisible (False )
        self .manga_rename_toggle_button .setFixedWidth (140 )
        self .manga_rename_toggle_button .setStyleSheet ("padding: 4px 8px;")
        self ._update_manga_filename_style_button_text ()
        log_title_layout .addWidget (self .manga_rename_toggle_button )
        self .manga_date_prefix_input =QLineEdit ()
        self .manga_date_prefix_input .setPlaceholderText ("Prefix for Manga Filenames")
        self .manga_date_prefix_input .setVisible (False )

        log_title_layout .addWidget (self .manga_date_prefix_input )

        self .multipart_toggle_button =QPushButton ()
        self .multipart_toggle_button .setToolTip ("Toggle between Multi-part and Single-stream downloads for large files.")
        self .multipart_toggle_button .setFixedWidth (130 )
        self .multipart_toggle_button .setStyleSheet ("padding: 4px 8px;")
        self ._update_multipart_toggle_button_text ()
        log_title_layout .addWidget (self .multipart_toggle_button )

        self .EYE_ICON ="\U0001F441"
        self .CLOSED_EYE_ICON ="\U0001F648"
        self .log_verbosity_toggle_button =QPushButton (self .EYE_ICON )
        self .log_verbosity_toggle_button .setFixedWidth (45 )
        self .log_verbosity_toggle_button .setStyleSheet ("font-size: 11pt; padding: 4px 2px;")
        log_title_layout .addWidget (self .log_verbosity_toggle_button )

        self .reset_button =QPushButton ("🔄 Reset")
        self .reset_button .setFixedWidth (80 )
        self .reset_button .setStyleSheet ("padding: 4px 8px;")
        log_title_layout .addWidget (self .reset_button )
        right_layout .addLayout (log_title_layout )

        self .log_splitter =QSplitter (Qt .Vertical )

        self .log_view_stack =QStackedWidget ()

        self .main_log_output =QTextEdit ()
        self .main_log_output .setReadOnly (True )
        self .main_log_output .setLineWrapMode (QTextEdit .NoWrap )
        self .log_view_stack .addWidget (self .main_log_output )

        self .missed_character_log_output =QTextEdit ()
        self .missed_character_log_output .setReadOnly (True )
        self .missed_character_log_output .setLineWrapMode (QTextEdit .NoWrap )
        self .log_view_stack .addWidget (self .missed_character_log_output )

        self .external_log_output =QTextEdit ()
        self .external_log_output .setReadOnly (True )
        self .external_log_output .setLineWrapMode (QTextEdit .NoWrap )
        self .external_log_output .hide ()

        self .log_splitter .addWidget (self .log_view_stack )
        self .log_splitter .addWidget (self .external_log_output )
        self .log_splitter .setSizes ([self .height (),0 ])
        right_layout .addWidget (self .log_splitter ,1 )

        export_button_layout =QHBoxLayout ()
        export_button_layout .addStretch (1 )
        self .export_links_button =QPushButton (self ._tr ("export_links_button_text","Export Links"))
        self .export_links_button .setFixedWidth (100 )
        self .export_links_button .setStyleSheet ("padding: 4px 8px; margin-top: 5px;")
        self .export_links_button .setEnabled (False )
        self .export_links_button .setVisible (False )
        export_button_layout .addWidget (self .export_links_button )

        self .download_extracted_links_button =QPushButton (self ._tr ("download_extracted_links_button_text","Download"))
        self .download_extracted_links_button .setFixedWidth (100 )
        self .download_extracted_links_button .setStyleSheet ("padding: 4px 8px; margin-top: 5px;")
        self .download_extracted_links_button .setEnabled (False )
        self .download_extracted_links_button .setVisible (False )
        export_button_layout .addWidget (self .download_extracted_links_button )
        self .log_display_mode_toggle_button =QPushButton ()
        self .log_display_mode_toggle_button .setFixedWidth (120 )
        self .log_display_mode_toggle_button .setStyleSheet ("padding: 4px 8px; margin-top: 5px;")
        self .log_display_mode_toggle_button .setVisible (False )
        export_button_layout .addWidget (self .log_display_mode_toggle_button )
        right_layout .addLayout (export_button_layout )


        self .progress_label =QLabel ("Progress: Idle")
        self .progress_label .setStyleSheet ("padding-top: 5px; font-style: italic;")
        right_layout .addWidget (self .progress_label )
        self .file_progress_label =QLabel ("")
        self .file_progress_label .setToolTip ("Shows the progress of individual file downloads, including speed and size.")
        self .file_progress_label .setWordWrap (True )
        self .file_progress_label .setStyleSheet ("padding-top: 2px; font-style: italic; color: #A0A0A0;")
        right_layout .addWidget (self .file_progress_label )


        self .main_splitter .addWidget (left_panel_widget )
        self .main_splitter .addWidget (right_panel_widget )

        if self .width ()==0 or self .height ()==0 :
            initial_width =1024 
        else :
            initial_width =self .width ()
        left_width =int (initial_width *0.35 )
        right_width =initial_width -left_width 
        self .main_splitter .setSizes ([left_width ,right_width ])

        top_level_layout =QHBoxLayout (self )
        top_level_layout .setContentsMargins (0 ,0 ,0 ,0 )
        top_level_layout .addWidget (self .main_splitter )

        self .update_ui_for_subfolders (self .use_subfolders_checkbox .isChecked ())
        self .update_external_links_setting (self .external_links_checkbox .isChecked ())
        self .update_multithreading_label (self .thread_count_input .text ())
        self .update_page_range_enabled_state ()
        if self .manga_mode_checkbox :
            self .update_ui_for_manga_mode (self .manga_mode_checkbox .isChecked ())
        if hasattr (self ,'link_input'):self .link_input .textChanged .connect (lambda :self .update_ui_for_manga_mode (self .manga_mode_checkbox .isChecked ()if self .manga_mode_checkbox else False ))
        
        self._load_creator_name_cache_from_json() # Load creator names for history and other features
        self .load_known_names_from_util ()
        self ._update_cookie_input_visibility (self .use_cookie_checkbox .isChecked ()if hasattr (self ,'use_cookie_checkbox')else False )
        self ._handle_multithreading_toggle (self .use_multithreading_checkbox .isChecked ())
        if hasattr (self ,'radio_group')and self .radio_group .checkedButton ():
            self ._handle_filter_mode_change (self .radio_group .checkedButton (),True )
        self ._update_manga_filename_style_button_text ()
        self ._update_skip_scope_button_text ()
        self ._update_char_filter_scope_button_text ()
        self ._update_multithreading_for_date_mode ()
        if hasattr (self ,'download_thumbnails_checkbox'):
            self ._handle_thumbnail_mode_change (self .download_thumbnails_checkbox .isChecked ())
        if hasattr (self ,'favorite_mode_checkbox'):

            self._handle_favorite_mode_toggle(False) # Ensure UI is in non-favorite state after reset

    def _load_persistent_history(self):
        """Loads download history from a persistent file."""
        self._initialize_persistent_history_path() # Ensure path is set before loading
        file_existed_before_load = os.path.exists(self.persistent_history_file)
        self.log_signal.emit(f"📜 Attempting to load history from: {self.persistent_history_file}")   
        if os.path.exists(self.persistent_history_file):
            try:
                with open(self.persistent_history_file, 'r', encoding='utf-8') as f:
                    loaded_history = json.load(f)
                if isinstance(loaded_history, list):
                    self.final_download_history_entries = loaded_history
                    self.log_signal.emit(f"✅ Loaded {len(loaded_history)} entries from persistent download history: {self.persistent_history_file}")
                elif loaded_history is None and os.path.getsize(self.persistent_history_file) == 0: # Handle empty file
                    self.log_signal.emit(f"ℹ️ Persistent history file is empty. Initializing with empty history.")
                    self.final_download_history_entries = []             
                else:
                    self.log_signal.emit(f"⚠️ Persistent history file has incorrect format. Expected list, got {type(loaded_history)}. Ignoring.")
                    self.final_download_history_entries = [] 
            except json.JSONDecodeError:
                self.log_signal.emit(f"⚠️ Error decoding persistent history file. It might be corrupted. Ignoring.")
                self.final_download_history_entries = []          
            except Exception as e:
                self.log_signal.emit(f"❌ Error loading persistent history: {e}")
                self.final_download_history_entries = []      
        else:
            self.log_signal.emit(f"⚠️ Persistent history file NOT FOUND at: {self.persistent_history_file}. Starting with empty history.")
            self.final_download_history_entries = [] # Initialize to empty if not found
            self._save_persistent_history() # Attempt to create the directory and an empty history file now

    def _save_persistent_history(self):
        """Saves download history to a persistent file."""
        if not hasattr(self, 'persistent_history_file') or not self.persistent_history_file:
            self._initialize_persistent_history_path() # Ensure path is set before saving
        self.log_signal.emit(f"📜 Attempting to save history to: {self.persistent_history_file}")
        try:
            history_dir = os.path.dirname(self.persistent_history_file)
            self.log_signal.emit(f"   History directory: {history_dir}")            
            if not os.path.exists(history_dir):
                os.makedirs(history_dir, exist_ok=True)
                self.log_signal.emit(f"   Created history directory: {history_dir}")
            
            with open(self.persistent_history_file, 'w', encoding='utf-8')as f:
                json.dump(self.final_download_history_entries, f, indent=2)
            self.log_signal.emit(f"✅ Saved {len(self.final_download_history_entries)} history entries to: {self.persistent_history_file}")
        except Exception as e:
            self.log_signal.emit(f"❌ Error saving persistent history to {self.persistent_history_file}: {e}")
    def _load_creator_name_cache_from_json(self):
        """Loads creator id-name-service mappings from creators.json into self.creator_name_cache."""
        self.log_signal.emit("ℹ️ Attempting to load creators.json for creator name cache.")

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path_for_creators = sys._MEIPASS
        else:
            base_path_for_creators = self.app_base_dir

        creators_file_path = os.path.join(base_path_for_creators, "creators.json")

        if not os.path.exists(creators_file_path):
            self.log_signal.emit(f"⚠️ 'creators.json' not found at {creators_file_path}. Creator name cache will be empty.")
            self.creator_name_cache.clear()
            return

        try:
            with open(creators_file_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)

            creators_list = []
            if isinstance(loaded_data, list) and len(loaded_data) > 0 and isinstance(loaded_data[0], list):
                creators_list = loaded_data[0]
            elif isinstance(loaded_data, list) and all(isinstance(item, dict) for item in loaded_data):
                creators_list = loaded_data
            else:
                self.log_signal.emit(f"⚠️ 'creators.json' has an unexpected format. Creator name cache may be incomplete.")

            for creator_data in creators_list:
                creator_id = creator_data.get("id")
                name = creator_data.get("name")
                service = creator_data.get("service")
                if creator_id and name and service:
                    self.creator_name_cache[(service.lower(), str(creator_id))] = name
            self.log_signal.emit(f"✅ Successfully loaded {len(self.creator_name_cache)} creator names into cache from 'creators.json'.")
        except Exception as e:
            self.log_signal.emit(f"❌ Error loading 'creators.json' for name cache: {e}")
            self.creator_name_cache.clear()

    def _show_download_history_dialog(self):
        """Shows the dialog with the finalized download history."""
        last_3_downloaded = list(self.last_downloaded_files_details)
        first_processed = self.final_download_history_entries

        if not last_3_downloaded and not first_processed:
            QMessageBox.information(
                self,
                self._tr("download_history_dialog_title_empty", "Download History (Empty)"),
                self._tr("no_download_history_header", "No Downloads Yet")
            )
            return

        dialog = DownloadHistoryDialog(last_3_downloaded, first_processed, self, self)
        dialog.exec_()

    def _handle_actual_file_downloaded(self, file_details_dict):
        """Handles a successfully downloaded file for the 'last 3 downloaded' history."""
        if not file_details_dict:
            return
        file_details_dict['download_timestamp'] = time.time() # Ensure timestamp is set
        creator_key = (file_details_dict.get('service', '').lower(), str(file_details_dict.get('user_id', '')))
        file_details_dict['creator_display_name'] = self.creator_name_cache.get(creator_key, file_details_dict.get('folder_context_name', 'Unknown Creator/Series'))
        self.last_downloaded_files_details.append(file_details_dict)
        # self.log_signal.emit(f"💾 Recorded successful download for history: {file_details_dict.get('disk_filename', 'N/A')}")

    def _handle_file_successfully_downloaded(self, history_entry_dict):
        """Handles a successfully downloaded file for history logging."""
        if len(self.download_history_log) >= self.download_history_log.maxlen:
            self.download_history_log.popleft() # Remove oldest if full
        self.download_history_log.append(history_entry_dict)
        # self.log_signal.emit(f"📜 Added to history log: {history_entry_dict.get('post_title', 'N/A')}")

    def _handle_actual_file_downloaded(self, file_details_dict):
        """Handles a successfully downloaded file for the 'last 3 downloaded' history."""
        if not file_details_dict:
            return

        file_details_dict['download_timestamp'] = time.time() # Ensure timestamp is set

        # Resolve creator name for display
        creator_key = (
            file_details_dict.get('service', '').lower(),
            str(file_details_dict.get('user_id', ''))
        )
        creator_display_name = self.creator_name_cache.get(creator_key, file_details_dict.get('folder_context_name', 'Unknown Creator'))
        file_details_dict['creator_display_name'] = creator_display_name

        self.last_downloaded_files_details.append(file_details_dict)
        # self.log_signal.emit(f"💾 Recorded successful download for history: {file_details_dict.get('disk_filename', 'N/A')}")

    def _handle_favorite_mode_toggle (self ,checked ):
        if not self .url_or_placeholder_stack or not self .bottom_action_buttons_stack :
            return 

            self ._handle_favorite_mode_toggle (self .favorite_mode_checkbox .isChecked ())
        self ._update_favorite_scope_button_text ()
        if hasattr (self ,'link_input'):
            self .last_link_input_text_for_queue_sync =self .link_input .text ()

    def _update_download_extracted_links_button_state (self ):
        if hasattr (self ,'download_extracted_links_button')and self .download_extracted_links_button :
            is_only_links =self .radio_only_links and self .radio_only_links .isChecked ()
            if not is_only_links :
                self .download_extracted_links_button .setEnabled (False )
                return 

            supported_platforms_for_button ={'mega','google drive','dropbox'}
            has_supported_links =any (
            link_info [3 ].lower ()in supported_platforms_for_button for link_info in self .extracted_links_cache 
            )
            self .download_extracted_links_button .setEnabled (is_only_links and has_supported_links )

    def _show_download_extracted_links_dialog (self ):
        """Shows the placeholder dialog for downloading extracted links."""
        if not (self .radio_only_links and self .radio_only_links .isChecked ()):
            self .log_signal .emit ("ℹ️ Download extracted links button clicked, but not in 'Only Links' mode.")
            return 

        supported_platforms ={'mega','google drive','dropbox'}
        links_to_show_in_dialog =[]
        for link_data_tuple in self .extracted_links_cache :
            platform =link_data_tuple [3 ].lower ()
            if platform in supported_platforms :
                links_to_show_in_dialog .append ({
                'title':link_data_tuple [0 ],
                'link_text':link_data_tuple [1 ],
                'url':link_data_tuple [2 ],
                'platform':platform ,
                'key':link_data_tuple [4 ]
                })

        if not links_to_show_in_dialog :
            QMessageBox .information (self ,"No Supported Links","No Mega, Google Drive, or Dropbox links were found in the extracted links.")
            return 

        dialog =DownloadExtractedLinksDialog (links_to_show_in_dialog ,self ,self )
        dialog .download_requested .connect (self ._handle_extracted_links_download_request )
        dialog .exec_ ()

    def _handle_extracted_links_download_request (self ,selected_links_info ):
        if not selected_links_info :
            self .log_signal .emit ("ℹ️ No links selected for download from dialog.")
            return 


        if self .radio_only_links and self .radio_only_links .isChecked ()and self .only_links_log_display_mode ==LOG_DISPLAY_DOWNLOAD_PROGRESS :
            self .main_log_output .clear ()
            self .log_signal .emit ("ℹ️ Displaying Mega download progress (extracted links hidden)...")
            self .mega_download_log_preserved_once =False 

        current_main_dir =self .dir_input .text ().strip ()
        download_dir_for_mega =""

        if current_main_dir and os .path .isdir (current_main_dir ):
            download_dir_for_mega =current_main_dir 
            self .log_signal .emit (f"ℹ️ Using existing main download location for external links: {download_dir_for_mega }")
        else :
            if not current_main_dir :
                self .log_signal .emit ("ℹ️ Main download location is empty. Prompting for download folder.")
            else :
                self .log_signal .emit (
                f"⚠️ Main download location '{current_main_dir }' is not a valid directory. Prompting for download folder.")


            suggestion_path =current_main_dir if current_main_dir else QStandardPaths .writableLocation (QStandardPaths .DownloadLocation )

            chosen_dir =QFileDialog .getExistingDirectory (
            self ,
            self ._tr ("select_download_folder_mega_dialog_title","Select Download Folder for External Links"),
            suggestion_path ,
            options =QFileDialog .ShowDirsOnly |QFileDialog .DontUseNativeDialog 
            )

            if not chosen_dir :
                self .log_signal .emit ("ℹ️ External links download cancelled - no download directory selected from prompt.")
                return 
            download_dir_for_mega =chosen_dir 


        self .log_signal .emit (f"ℹ️ Preparing to download {len (selected_links_info )} selected external link(s) to: {download_dir_for_mega }")
        if not os .path .exists (download_dir_for_mega ):
            self .log_signal .emit (f"❌ Critical Error: Selected download directory '{download_dir_for_mega }' does not exist.")
            return 


        tasks_for_thread =selected_links_info 

        if self .external_link_download_thread and self .external_link_download_thread .isRunning ():
            QMessageBox .warning (self ,"Busy","Another external link download is already in progress.")
            return 

        self .external_link_download_thread =ExternalLinkDownloadThread (
        tasks_for_thread ,
        download_dir_for_mega ,
        self .log_signal .emit ,
        self 
        )
        self .external_link_download_thread .finished .connect (self ._on_external_link_download_thread_finished )

        self .external_link_download_thread .progress_signal .connect (self .handle_main_log )
        self .external_link_download_thread .file_complete_signal .connect (self ._on_single_external_file_complete )



        self .set_ui_enabled (False )

        self .progress_label .setText (self ._tr ("progress_processing_post_text","Progress: Processing post {processed_posts}...").format (processed_posts =f"External Links (0/{len (tasks_for_thread )})"))
        self .external_link_download_thread .start ()

    def _on_external_link_download_thread_finished (self ):
        self .log_signal .emit ("✅ External link download thread finished.")
        self .progress_label .setText (f"{self ._tr ('status_completed','Completed')}: External link downloads. {self ._tr ('ready_for_new_task_text','Ready for new task.')}")

        self .mega_download_log_preserved_once =True 
        self .log_signal .emit ("INTERNAL: mega_download_log_preserved_once SET to True.")

        if self .radio_only_links and self .radio_only_links .isChecked ():
            self .log_signal .emit (HTML_PREFIX +"<br><hr>--- End of Mega Download Log ---<br>")



        self .set_ui_enabled (True )



        if self .mega_download_log_preserved_once :
            self .mega_download_log_preserved_once =False 
            self .log_signal .emit ("INTERNAL: mega_download_log_preserved_once RESET to False.")

        if self .external_link_download_thread :
            self .external_link_download_thread .deleteLater ()
            self .external_link_download_thread =None 

    def _on_single_external_file_complete (self ,url ,success ):


        pass 
    def _show_future_settings_dialog (self ):
        """Shows the placeholder dialog for future settings."""
        dialog =FutureSettingsDialog (self )
        dialog =FutureSettingsDialog (self ,self )
        dialog .exec_ ()

    def _sync_queue_with_link_input (self ,current_text ):
        """
        Synchronizes the favorite_download_queue with the link_input text.
        Removes creators from the queue if their names are removed from the input field.
        Only affects items added via 'creator_popup_selection'.
        """
        if not self .favorite_download_queue :
            self .last_link_input_text_for_queue_sync =current_text 
            return 

        current_names_in_input ={name .strip ().lower ()for name in current_text .split (',')if name .strip ()}

        queue_copy =list (self .favorite_download_queue )
        removed_count =0 

        for item in queue_copy :
            if item .get ('type')=='creator_popup_selection':
                item_name_lower =item .get ('name','').lower ()
                if item_name_lower and item_name_lower not in current_names_in_input :
                    try :
                        self .favorite_download_queue .remove (item )
                        self .log_signal .emit (f"ℹ️ Creator '{item .get ('name')}' removed from download queue due to removal from URL input.")
                        removed_count +=1 
                    except ValueError :
                        self .log_signal .emit (f"⚠️ Tried to remove '{item .get ('name')}' from queue, but it was not found (sync).")

        self .last_link_input_text_for_queue_sync =current_text 

    def _browse_cookie_file (self ):
        """Opens a file dialog to select a cookie file."""
        start_dir =QStandardPaths .writableLocation (QStandardPaths .DownloadLocation )
        if not start_dir :
            start_dir =os .path .dirname (self .config_file )

        filepath ,_ =QFileDialog .getOpenFileName (self ,"Select Cookie File",start_dir ,"Text files (*.txt);;All files (*)")
        if filepath :
            self .selected_cookie_filepath =filepath 
            self .log_signal .emit (f"ℹ️ Selected cookie file: {filepath }")
            if hasattr (self ,'cookie_text_input'):
                self .cookie_text_input .blockSignals (True )
                self .cookie_text_input .setText (filepath )
            self .cookie_text_input .setToolTip (self ._tr ("cookie_text_input_tooltip_file_selected","Using selected cookie file: {filepath}").format (filepath =filepath ))
            self .cookie_text_input .setPlaceholderText (self ._tr ("cookie_text_input_placeholder_with_file_selected_text","Using selected cookie file (see Browse...)"))
            self .cookie_text_input .setReadOnly (True )
            self .cookie_text_input .setPlaceholderText ("")
            self .cookie_text_input .blockSignals (False )

    def _update_cookie_input_placeholders_and_tooltips (self ):
        if hasattr (self ,'cookie_text_input'):
            if self .selected_cookie_filepath :
                self .cookie_text_input .setPlaceholderText (self ._tr ("cookie_text_input_placeholder_with_file_selected_text","Using selected cookie file..."))
                self .cookie_text_input .setToolTip (self ._tr ("cookie_text_input_tooltip_file_selected","Using selected cookie file: {filepath}").format (filepath =self .selected_cookie_filepath ))
            else :
                self .cookie_text_input .setPlaceholderText (self ._tr ("cookie_text_input_placeholder_no_file_selected_text","Cookie string (if no cookies.txt selected)"))
                self .cookie_text_input .setToolTip (self ._tr ("cookie_text_input_tooltip","Enter your cookie string directly..."))
                self .cookie_text_input .setReadOnly (True )
                self .cookie_text_input .setPlaceholderText ("")
                self .cookie_text_input .blockSignals (False )

    def _center_on_screen (self ):
        """Centers the widget on the screen."""
        try :
            primary_screen =QApplication .primaryScreen ()
            if not primary_screen :
                screens =QApplication .screens ()
                if not screens :return 
                primary_screen =screens [0 ]

            available_geo =primary_screen .availableGeometry ()
            widget_geo =self .frameGeometry ()

            x =available_geo .x ()+(available_geo .width ()-widget_geo .width ())//2 
            y =available_geo .y ()+(available_geo .height ()-widget_geo .height ())//2 
            self .move (x ,y )
        except Exception as e :
            self .log_signal .emit (f"⚠️ Error centering window: {e }")

    def _handle_cookie_text_manual_change (self ,text ):
        """Handles manual changes to the cookie text input, especially clearing a browsed path."""
        if not hasattr (self ,'cookie_text_input')or not hasattr (self ,'use_cookie_checkbox'):
            return 
        if self .selected_cookie_filepath and not text .strip ()and self .use_cookie_checkbox .isChecked ():
            self .selected_cookie_filepath =None 
            self .cookie_text_input .setReadOnly (False )
            self ._update_cookie_input_placeholders_and_tooltips ()
            self .log_signal .emit ("ℹ️ Browsed cookie file path cleared from input. Switched to manual cookie string mode.")


    def get_dark_theme (self ):
        return """
        QWidget { background-color: #2E2E2E; color: #E0E0E0; font-family: Segoe UI, Arial, sans-serif; font-size: 10pt; }
        QLineEdit, QListWidget { background-color: #3C3F41; border: 1px solid #5A5A5A; padding: 5px; color: #F0F0F0; border-radius: 4px; }
        QTextEdit { background-color: #3C3F41; border: 1px solid #5A5A5A; padding: 5px;
                          color: #F0F0F0; border-radius: 4px; 
                          font-family: Consolas, Courier New, monospace; font-size: 9.5pt; }
        QPushButton { background-color: #555; color: #F0F0F0; border: 1px solid #6A6A6A; padding: 6px 12px; border-radius: 4px; min-height: 22px; }
        QPushButton:hover { background-color: #656565; border: 1px solid #7A7A7A; }
        QPushButton:pressed { background-color: #4A4A4A; }
        QPushButton:disabled { background-color: #404040; color: #888; border-color: #555; }
        QLabel { font-weight: bold; padding-top: 4px; padding-bottom: 2px; color: #C0C0C0; }
        QRadioButton, QCheckBox { spacing: 5px; color: #E0E0E0; padding-top: 4px; padding-bottom: 4px; }
        QRadioButton::indicator, QCheckBox::indicator { width: 14px; height: 14px; }
        QListWidget { alternate-background-color: #353535; border: 1px solid #5A5A5A; }
        QListWidget::item:selected { background-color: #007ACC; color: #FFFFFF; }
        QToolTip { background-color: #4A4A4A; color: #F0F0F0; border: 1px solid #6A6A6A; padding: 4px; border-radius: 3px; }
        QSplitter::handle { background-color: #5A5A5A; }
        QSplitter::handle:horizontal { width: 5px; }
        QSplitter::handle:vertical { height: 5px; }
        QFrame[frameShape="4"], QFrame[frameShape="5"] { 
            border: 1px solid #4A4A4A; 
            border-radius: 3px;
        }
        """

    def browse_directory (self ):
        initial_dir_text =self .dir_input .text ()
        start_path =""
        if initial_dir_text and os .path .isdir (initial_dir_text ):
            start_path =initial_dir_text 
        else :
            home_location =QStandardPaths .writableLocation (QStandardPaths .HomeLocation )
            documents_location =QStandardPaths .writableLocation (QStandardPaths .DocumentsLocation )
            if home_location and os .path .isdir (home_location ):
                start_path =home_location 
            elif documents_location and os .path .isdir (documents_location ):
                start_path =documents_location 

        self .log_signal .emit (f"ℹ️ Opening folder dialog. Suggested start path: '{start_path }'")

        try :
            folder =QFileDialog .getExistingDirectory (
            self ,
            "Select Download Folder",
            start_path ,
            options =QFileDialog .DontUseNativeDialog |QFileDialog .ShowDirsOnly 
            )

            if folder :
                self .dir_input .setText (folder )
                self .log_signal .emit (f"ℹ️ Folder selected: {folder }")
            else :
                self .log_signal .emit (f"ℹ️ Folder selection cancelled by user.")
        except RuntimeError as e :
            self .log_signal .emit (f"❌ RuntimeError opening folder dialog: {e }. This might indicate a deeper Qt or system issue.")
            QMessageBox .critical (self ,"Dialog Error",f"A runtime error occurred while trying to open the folder dialog: {e }")
        except Exception as e :
            self .log_signal .emit (f"❌ Unexpected error opening folder dialog: {e }\n{traceback .format_exc (limit =3 )}")
            QMessageBox .critical (self ,"Dialog Error",f"An unexpected error occurred with the folder selection dialog: {e }")

    def handle_main_log (self ,message ):
        is_html_message =message .startswith (HTML_PREFIX )
        display_message =message 
        use_html =False 

        if is_html_message :
            display_message =message [len (HTML_PREFIX ):]
            use_html =True 

        try :
            safe_message =str (display_message ).replace ('\x00','[NULL]')
            if use_html :
                self .main_log_output .insertHtml (safe_message )
            else :
                self .main_log_output .append (safe_message )

            scrollbar =self .main_log_output .verticalScrollBar ()
            if scrollbar .value ()>=scrollbar .maximum ()-30 :
                scrollbar .setValue (scrollbar .maximum ())
        except Exception as e :
            print (f"GUI Main Log Error: {e }\nOriginal Message: {message }")
    def _extract_key_term_from_title (self ,title ):
        if not title :
            return None 
        title_cleaned =re .sub (r'\[.*?\]','',title )
        title_cleaned =re .sub (r'\(.*?\)','',title_cleaned )
        title_cleaned =title_cleaned .strip ()
        word_matches =list (re .finditer (r'\b[a-zA-Z][a-zA-Z0-9_-]*\b',title_cleaned ))

        capitalized_candidates =[]
        for match in word_matches :
            word =match .group (0 )
            if word .istitle ()and word .lower ()not in self .STOP_WORDS and len (word )>2 :
                if not (len (word )>3 and word .isupper ()):
                    capitalized_candidates .append ({'text':word ,'len':len (word ),'pos':match .start ()})

        if capitalized_candidates :
            capitalized_candidates .sort (key =lambda x :(x ['len'],x ['pos']),reverse =True )
            return capitalized_candidates [0 ]['text']
        non_capitalized_words_info =[]
        for match in word_matches :
            word =match .group (0 )
            if word .lower ()not in self .STOP_WORDS and len (word )>3 :
                non_capitalized_words_info .append ({'text':word ,'len':len (word ),'pos':match .start ()})

        if non_capitalized_words_info :
            non_capitalized_words_info .sort (key =lambda x :(x ['len'],x ['pos']),reverse =True )
            return non_capitalized_words_info [0 ]['text']

        return None 

    def handle_missed_character_post (self ,post_title ,reason ):
        if self .missed_character_log_output :
            key_term =self ._extract_key_term_from_title (post_title )

            if key_term :
                normalized_key_term =key_term .lower ()
                if normalized_key_term not in self .already_logged_bold_key_terms :
                    self .already_logged_bold_key_terms .add (normalized_key_term )
                    self .missed_key_terms_buffer .append (key_term )
                    self ._refresh_missed_character_log ()
        else :
            print (f"Debug (Missed Char Log): Title='{post_title }', Reason='{reason }'")

    def _refresh_missed_character_log (self ):
        if self .missed_character_log_output :
            self .missed_character_log_output .clear ()
            sorted_terms =sorted (self .missed_key_terms_buffer ,key =str .lower )
            separator_line ="-"*40 

            for term in sorted_terms :
                display_term =term .capitalize ()

                self .missed_character_log_output .append (separator_line )
                self .missed_character_log_output .append (f'<p align="center"><b><font style="font-size: 12.4pt; color: #87CEEB;">{display_term }</font></b></p>')
                self .missed_character_log_output .append (separator_line )
                self .missed_character_log_output .append ("")

            scrollbar =self .missed_character_log_output .verticalScrollBar ()
            scrollbar .setValue (0 )

    def _is_download_active (self ):
        single_thread_active =self .download_thread and self .download_thread .isRunning ()
        fetcher_active =hasattr (self ,'is_fetcher_thread_running')and self .is_fetcher_thread_running 
        pool_has_active_tasks =self .thread_pool is not None and any (not f .done ()for f in self .active_futures if f is not None )
        retry_pool_active =hasattr (self ,'retry_thread_pool')and self .retry_thread_pool is not None and hasattr (self ,'active_retry_futures')and any (not f .done ()for f in self .active_retry_futures if f is not None )


        external_dl_thread_active =hasattr (self ,'external_link_download_thread')and self .external_link_download_thread is not None and self .external_link_download_thread .isRunning ()

        return single_thread_active or fetcher_active or pool_has_active_tasks or retry_pool_active or external_dl_thread_active 

    def handle_external_link_signal (self ,post_title ,link_text ,link_url ,platform ,decryption_key ):
        link_data =(post_title ,link_text ,link_url ,platform ,decryption_key )
        self .external_link_queue .append (link_data )
        if self .radio_only_links and self .radio_only_links .isChecked ():
            self .extracted_links_cache .append (link_data )
            self ._update_download_extracted_links_button_state ()

        is_only_links_mode =self .radio_only_links and self .radio_only_links .isChecked ()
        should_display_in_external_log =self .show_external_links and not is_only_links_mode 

        if not (is_only_links_mode or should_display_in_external_log ):
            self ._is_processing_external_link_queue =False 
            if self .external_link_queue :
                QTimer .singleShot (0 ,self ._try_process_next_external_link )
            return 


        if link_data not in self .extracted_links_cache :
            self .extracted_links_cache .append (link_data )

    def _try_process_next_external_link (self ):
        if self ._is_processing_external_link_queue or not self .external_link_queue :
            return 

        is_only_links_mode =self .radio_only_links and self .radio_only_links .isChecked ()
        should_display_in_external_log =self .show_external_links and not is_only_links_mode 

        if not (is_only_links_mode or should_display_in_external_log ):
            self ._is_processing_external_link_queue =False 
            if self .external_link_queue :
                QTimer .singleShot (0 ,self ._try_process_next_external_link )
            return 

        self ._is_processing_external_link_queue =True 
        link_data =self .external_link_queue .popleft ()

        if is_only_links_mode :
            QTimer .singleShot (0 ,lambda data =link_data :self ._display_and_schedule_next (data ))
        elif self ._is_download_active ():
            delay_ms =random .randint (4000 ,8000 )
            QTimer .singleShot (delay_ms ,lambda data =link_data :self ._display_and_schedule_next (data ))
        else :
            QTimer .singleShot (0 ,lambda data =link_data :self ._display_and_schedule_next (data ))


    def _display_and_schedule_next (self ,link_data ):
        post_title ,link_text ,link_url ,platform ,decryption_key =link_data 
        is_only_links_mode =self .radio_only_links and self .radio_only_links .isChecked ()

        max_link_text_len =50 
        display_text =(link_text [:max_link_text_len ].strip ()+"..."
        if len (link_text )>max_link_text_len else link_text .strip ())
        formatted_link_info =f"{display_text } - {link_url } - {platform }"

        if decryption_key :
            formatted_link_info +=f" (Decryption Key: {decryption_key })"

        if is_only_links_mode :
            if post_title !=self ._current_link_post_title :
                separator_html ="<br>"+"-"*45 +"<br>"
                if self ._current_link_post_title is not None :
                    self .log_signal .emit (HTML_PREFIX +separator_html )
                title_html =f'<b style="color: #87CEEB;">{html .escape (post_title )}</b><br>'
                self .log_signal .emit (HTML_PREFIX +title_html )
                self ._current_link_post_title =post_title 

            self .log_signal .emit (formatted_link_info )
        elif self .show_external_links :
            separator ="-"*45 
            self ._append_to_external_log (formatted_link_info ,separator )

        self ._is_processing_external_link_queue =False 
        self ._try_process_next_external_link ()


    def _append_to_external_log (self ,formatted_link_text ,separator ):
        if not (self .external_log_output and self .external_log_output .isVisible ()):
            return 

        try :
            self .external_log_output .append (formatted_link_text )
            self .external_log_output .append ("")

            scrollbar =self .external_log_output .verticalScrollBar ()
            if scrollbar .value ()>=scrollbar .maximum ()-50 :
                scrollbar .setValue (scrollbar .maximum ())
        except Exception as e :
            self .log_signal .emit (f"GUI External Log Append Error: {e }\nOriginal Message: {formatted_link_text }")
            print (f"GUI External Log Error (Append): {e }\nOriginal Message: {formatted_link_text }")


    def update_file_progress_display (self ,filename ,progress_info ):
        if not filename and progress_info is None :
            self .file_progress_label .setText ("")
            return 

        if isinstance (progress_info ,list ):
            if not progress_info :
                self .file_progress_label .setText (self ._tr ("downloading_multipart_initializing_text","File: {filename} - Initializing parts...").format (filename =filename ))
                return 

            total_downloaded_overall =sum (cs .get ('downloaded',0 )for cs in progress_info )
            total_file_size_overall =sum (cs .get ('total',0 )for cs in progress_info )

            active_chunks_count =0 
            combined_speed_bps =0 
            for cs in progress_info :
                if cs .get ('active',False ):
                    active_chunks_count +=1 
                    combined_speed_bps +=cs .get ('speed_bps',0 )

            dl_mb =total_downloaded_overall /(1024 *1024 )
            total_mb =total_file_size_overall /(1024 *1024 )
            speed_MBps =(combined_speed_bps /8 )/(1024 *1024 )

            progress_text =self ._tr ("downloading_multipart_text","DL '{filename}...': {downloaded_mb:.1f}/{total_mb:.1f} MB ({parts} parts @ {speed:.2f} MB/s)").format (filename =filename [:20 ],downloaded_mb =dl_mb ,total_mb =total_mb ,parts =active_chunks_count ,speed =speed_MBps )
            self .file_progress_label .setText (progress_text )

        elif isinstance (progress_info ,tuple )and len (progress_info )==2 :
            downloaded_bytes ,total_bytes =progress_info 

            if not filename and total_bytes ==0 and downloaded_bytes ==0 :
                self .file_progress_label .setText ("")
                return 

            max_fn_len =25 
            disp_fn =filename if len (filename )<=max_fn_len else filename [:max_fn_len -3 ].strip ()+"..."

            dl_mb =downloaded_bytes /(1024 *1024 )
            if total_bytes >0 :
                tot_mb =total_bytes /(1024 *1024 )
                prog_text_base =self ._tr ("downloading_file_known_size_text","Downloading '{filename}' ({downloaded_mb:.1f}MB / {total_mb:.1f}MB)").format (filename =disp_fn ,downloaded_mb =dl_mb ,total_mb =tot_mb )
            else :
                prog_text_base =self ._tr ("downloading_file_unknown_size_text","Downloading '{filename}' ({downloaded_mb:.1f}MB)").format (filename =disp_fn ,downloaded_mb =dl_mb )

            self .file_progress_label .setText (prog_text_base )
        elif filename and progress_info is None :
            self .file_progress_label .setText ("")
        elif not filename and not progress_info :
            self .file_progress_label .setText ("")


    def update_external_links_setting (self ,checked ):
        is_only_links_mode =self .radio_only_links and self .radio_only_links .isChecked ()
        is_only_archives_mode =self .radio_only_archives and self .radio_only_archives .isChecked ()

        if is_only_links_mode or is_only_archives_mode :
            if self .external_log_output :self .external_log_output .hide ()
            if self .log_splitter :self .log_splitter .setSizes ([self .height (),0 ])
            return 

        self .show_external_links =checked 
        if checked :
            if self .external_log_output :self .external_log_output .show ()
            if self .log_splitter :self .log_splitter .setSizes ([self .height ()//2 ,self .height ()//2 ])
            if self .main_log_output :self .main_log_output .setMinimumHeight (50 )
            if self .external_log_output :self .external_log_output .setMinimumHeight (50 )
            self .log_signal .emit ("\n"+"="*40 +"\n🔗 External Links Log Enabled\n"+"="*40 )
            if self .external_log_output :
                self .external_log_output .clear ()
                self .external_log_output .append ("🔗 External Links Found:")
            self ._try_process_next_external_link ()
        else :
            if self .external_log_output :self .external_log_output .hide ()
            if self .log_splitter :self .log_splitter .setSizes ([self .height (),0 ])
            if self .main_log_output :self .main_log_output .setMinimumHeight (0 )
            if self .external_log_output :self .external_log_output .setMinimumHeight (0 )
            if self .external_log_output :self .external_log_output .clear ()
            self .log_signal .emit ("\n"+"="*40 +"\n🔗 External Links Log Disabled\n"+"="*40 )


    def _handle_filter_mode_change (self ,button ,checked ):
        if not button or not checked :
            return 


        is_only_links =(button ==self .radio_only_links )
        is_only_audio =(hasattr (self ,'radio_only_audio')and self .radio_only_audio is not None and button ==self .radio_only_audio )
        is_only_archives =(hasattr (self ,'radio_only_archives')and self .radio_only_archives is not None and button ==self .radio_only_archives )

        if self .skip_scope_toggle_button :
            self .skip_scope_toggle_button .setVisible (not (is_only_links or is_only_archives or is_only_audio ))
        if hasattr (self ,'multipart_toggle_button')and self .multipart_toggle_button :
            self .multipart_toggle_button .setVisible (not (is_only_links or is_only_archives or is_only_audio ))

        if self .link_search_input :self .link_search_input .setVisible (is_only_links )
        if self .link_search_button :self .link_search_button .setVisible (is_only_links )
        if self .export_links_button :
            self .export_links_button .setVisible (is_only_links )
            self .export_links_button .setEnabled (is_only_links and bool (self .extracted_links_cache ))

        if hasattr (self ,'download_extracted_links_button')and self .download_extracted_links_button :
            self .download_extracted_links_button .setVisible (is_only_links )
            self ._update_download_extracted_links_button_state ()

        if self .download_btn :
            if is_only_links :
                self .download_btn .setText (self ._tr ("extract_links_button_text","🔗 Extract Links"))
            else :
                self .download_btn .setText (self ._tr ("start_download_button_text","⬇️ Start Download"))
        if not is_only_links and self .link_search_input :self .link_search_input .clear ()

        file_download_mode_active =not is_only_links 



        if self .use_subfolders_checkbox :self .use_subfolders_checkbox .setEnabled (file_download_mode_active )
        if self .skip_words_input :self .skip_words_input .setEnabled (file_download_mode_active )
        if self .skip_scope_toggle_button :self .skip_scope_toggle_button .setEnabled (file_download_mode_active )
        if hasattr (self ,'remove_from_filename_input'):self .remove_from_filename_input .setEnabled (file_download_mode_active )

        if self .skip_zip_checkbox :
            can_skip_zip =file_download_mode_active and not is_only_archives 
            self .skip_zip_checkbox .setEnabled (can_skip_zip )
            if is_only_archives :
                self .skip_zip_checkbox .setChecked (False )

        if self .skip_rar_checkbox :
            can_skip_rar =file_download_mode_active and not is_only_archives 
            self .skip_rar_checkbox .setEnabled (can_skip_rar )
            if is_only_archives :
                self .skip_rar_checkbox .setChecked (False )

        other_file_proc_enabled =file_download_mode_active and not is_only_archives 
        if self .download_thumbnails_checkbox :self .download_thumbnails_checkbox .setEnabled (other_file_proc_enabled )
        if self .compress_images_checkbox :self .compress_images_checkbox .setEnabled (other_file_proc_enabled )

        if self .external_links_checkbox :
            can_show_external_log_option =file_download_mode_active and not is_only_archives 
            self .external_links_checkbox .setEnabled (can_show_external_log_option )
            if not can_show_external_log_option :
                self .external_links_checkbox .setChecked (False )


        if is_only_links :
            self .progress_log_label .setText ("📜 Extracted Links Log:")
            if self .external_log_output :self .external_log_output .hide ()
            if self .log_splitter :self .log_splitter .setSizes ([self .height (),0 ])


            do_clear_log_in_filter_change =True 
            if self .mega_download_log_preserved_once and self .only_links_log_display_mode ==LOG_DISPLAY_DOWNLOAD_PROGRESS :
                do_clear_log_in_filter_change =False 

            if self .main_log_output and do_clear_log_in_filter_change :
                self .log_signal .emit ("INTERNAL: _handle_filter_mode_change - About to clear log.")
                self .main_log_output .clear ()
                self .log_signal .emit ("INTERNAL: _handle_filter_mode_change - Log cleared by _handle_filter_mode_change.")

            if self .main_log_output :self .main_log_output .setMinimumHeight (0 )
            self .log_signal .emit ("="*20 +" Mode changed to: Only Links "+"="*20 )
            self ._try_process_next_external_link ()
        elif is_only_archives :
            self .progress_log_label .setText ("📜 Progress Log (Archives Only):")
            if self .external_log_output :self .external_log_output .hide ()
            if self .log_splitter :self .log_splitter .setSizes ([self .height (),0 ])
            if self .main_log_output :self .main_log_output .clear ()
            self .log_signal .emit ("="*20 +" Mode changed to: Only Archives "+"="*20 )
        elif is_only_audio :
            self .progress_log_label .setText (self ._tr ("progress_log_label_text","📜 Progress Log:")+f" ({self ._tr ('filter_audio_radio','🎧 Only Audio')})")
            if self .external_log_output :self .external_log_output .hide ()
            if self .log_splitter :self .log_splitter .setSizes ([self .height (),0 ])
            if self .main_log_output :self .main_log_output .clear ()
            self .log_signal .emit ("="*20 +f" Mode changed to: {self ._tr ('filter_audio_radio','🎧 Only Audio')} "+"="*20 )
        else :
            self .progress_log_label .setText (self ._tr ("progress_log_label_text","📜 Progress Log:"))
            self .update_external_links_setting (self .external_links_checkbox .isChecked ()if self .external_links_checkbox else False )
            self .log_signal .emit (f"="*20 +f" Mode changed to: {button .text ()} "+"="*20 )


        if is_only_links :
            self ._filter_links_log ()

        if hasattr (self ,'log_display_mode_toggle_button'):
            self .log_display_mode_toggle_button .setVisible (is_only_links )
            self ._update_log_display_mode_button_text ()

        subfolders_on =self .use_subfolders_checkbox .isChecked ()if self .use_subfolders_checkbox else False 
        manga_on =self .manga_mode_checkbox .isChecked ()if self .manga_mode_checkbox else False 

        character_filter_should_be_active =file_download_mode_active and not is_only_archives 

        if self .character_filter_widget :
            self .character_filter_widget .setVisible (character_filter_should_be_active )

        enable_character_filter_related_widgets =character_filter_should_be_active 

        if self .character_input :
            self .character_input .setEnabled (enable_character_filter_related_widgets )
            if not enable_character_filter_related_widgets :
                self .character_input .clear ()

        if self .char_filter_scope_toggle_button :
            self .char_filter_scope_toggle_button .setEnabled (enable_character_filter_related_widgets )

        self .update_ui_for_subfolders (subfolders_on )
        self .update_custom_folder_visibility ()
        self .update_ui_for_manga_mode (self .manga_mode_checkbox .isChecked ()if self .manga_mode_checkbox else False )


    def _filter_links_log (self ):
        if not (self .radio_only_links and self .radio_only_links .isChecked ()):return 

        search_term =self .link_search_input .text ().lower ().strip ()if self .link_search_input else ""

        if self .mega_download_log_preserved_once and self .only_links_log_display_mode ==LOG_DISPLAY_DOWNLOAD_PROGRESS :


            self .log_signal .emit ("INTERNAL: _filter_links_log - Preserving Mega log (due to mega_download_log_preserved_once).")
        elif self .only_links_log_display_mode ==LOG_DISPLAY_DOWNLOAD_PROGRESS :



            self .log_signal .emit ("INTERNAL: _filter_links_log - In Progress View. Clearing for placeholder.")
            if self .main_log_output :self .main_log_output .clear ()
            self .log_signal .emit ("INTERNAL: _filter_links_log - Cleared for progress placeholder.")
            self .log_signal .emit ("ℹ️ Switched to Mega download progress view. Extracted links are hidden.\n"
            "   Perform a Mega download to see its progress here, or switch back to 🔗 view.")
            self .log_signal .emit ("INTERNAL: _filter_links_log - Placeholder message emitted.")

        else :

            self .log_signal .emit ("INTERNAL: _filter_links_log - In links view branch. About to clear.")
            if self .main_log_output :self .main_log_output .clear ()
            self .log_signal .emit ("INTERNAL: _filter_links_log - Cleared for links view.")

            current_title_for_display =None 
            any_links_displayed_this_call =False 
            separator_html ="<br>"+"-"*45 +"<br>"

            for post_title ,link_text ,link_url ,platform ,decryption_key in self .extracted_links_cache :
                matches_search =(not search_term or 
                search_term in link_text .lower ()or 
                search_term in link_url .lower ()or 
                search_term in platform .lower ()or 
                (decryption_key and search_term in decryption_key .lower ()))
                if not matches_search :
                    continue 

                any_links_displayed_this_call =True 
                if post_title !=current_title_for_display :
                    if current_title_for_display is not None :
                        if self .main_log_output :self .main_log_output .insertHtml (separator_html )

                    title_html =f'<b style="color: #87CEEB;">{html .escape (post_title )}</b><br>'
                    if self .main_log_output :self .main_log_output .insertHtml (title_html )
                    current_title_for_display =post_title 

                max_link_text_len =50 
                display_text =(link_text [:max_link_text_len ].strip ()+"..."if len (link_text )>max_link_text_len else link_text .strip ())

                plain_link_info_line =f"{display_text } - {link_url } - {platform }"
                if decryption_key :
                    plain_link_info_line +=f" (Decryption Key: {decryption_key })"
                if self .main_log_output :
                    self .main_log_output .append (plain_link_info_line )

            if any_links_displayed_this_call :
                if self .main_log_output :self .main_log_output .append ("")
            elif not search_term and self .main_log_output :
                 self .log_signal .emit ("   (No links extracted yet or all filtered out in links view)")


        if self .main_log_output :self .main_log_output .verticalScrollBar ().setValue (self .main_log_output .verticalScrollBar ().maximum ())


    def _export_links_to_file (self ):
        if not (self .radio_only_links and self .radio_only_links .isChecked ()):
            QMessageBox .information (self ,"Export Links","Link export is only available in 'Only Links' mode.")
            return 
        if not self .extracted_links_cache :
            QMessageBox .information (self ,"Export Links","No links have been extracted yet.")
            return 

        default_filename ="extracted_links.txt"
        filepath ,_ =QFileDialog .getSaveFileName (self ,"Save Links",default_filename ,"Text Files (*.txt);;All Files (*)")

        if filepath :
            try :
                with open (filepath ,'w',encoding ='utf-8')as f :
                    current_title_for_export =None 
                    separator ="-"*60 +"\n"
                    for post_title ,link_text ,link_url ,platform ,decryption_key in self .extracted_links_cache :
                        if post_title !=current_title_for_export :
                            if current_title_for_export is not None :
                                f .write ("\n"+separator +"\n")
                            f .write (f"Post Title: {post_title }\n\n")
                            current_title_for_export =post_title 
                        line_to_write =f"  {link_text } - {link_url } - {platform }"
                        if decryption_key :
                            line_to_write +=f" (Decryption Key: {decryption_key })"
                        f .write (line_to_write +"\n")
                self .log_signal .emit (f"✅ Links successfully exported to: {filepath }")
                QMessageBox .information (self ,"Export Successful",f"Links exported to:\n{filepath }")
            except Exception as e :
                self .log_signal .emit (f"❌ Error exporting links: {e }")
                QMessageBox .critical (self ,"Export Error",f"Could not export links: {e }")


    def get_filter_mode (self ):
        if self .radio_only_links and self .radio_only_links .isChecked ():
            return 'all'
        elif self .radio_images .isChecked ():
            return 'image'
        elif self .radio_videos .isChecked ():
            return 'video'
        elif self .radio_only_archives and self .radio_only_archives .isChecked ():
            return 'archive'
        elif hasattr (self ,'radio_only_audio')and self .radio_only_audio .isChecked ():
            return 'audio'
        elif self .radio_all .isChecked ():
            return 'all'
        return 'all'


    def get_skip_words_scope (self ):
        return self .skip_words_scope 


    def _update_skip_scope_button_text (self ):
        if self .skip_scope_toggle_button :
            if self .skip_words_scope ==SKIP_SCOPE_FILES :
                self .skip_scope_toggle_button .setText (self ._tr ("skip_scope_files_text","Scope: Files"))
                self .skip_scope_toggle_button .setToolTip (self ._tr ("skip_scope_files_tooltip","Tooltip for skip scope files"))
            elif self .skip_words_scope ==SKIP_SCOPE_POSTS :
                self .skip_scope_toggle_button .setText (self ._tr ("skip_scope_posts_text","Scope: Posts"))
                self .skip_scope_toggle_button .setToolTip (self ._tr ("skip_scope_posts_tooltip","Tooltip for skip scope posts"))
            elif self .skip_words_scope ==SKIP_SCOPE_BOTH :
                self .skip_scope_toggle_button .setText (self ._tr ("skip_scope_both_text","Scope: Both"))
                self .skip_scope_toggle_button .setToolTip (self ._tr ("skip_scope_both_tooltip","Tooltip for skip scope both"))
            else :
                self .skip_scope_toggle_button .setText (self ._tr ("skip_scope_unknown_text","Scope: Unknown"))
                self .skip_scope_toggle_button .setToolTip (self ._tr ("skip_scope_unknown_tooltip","Tooltip for skip scope unknown"))


    def _cycle_skip_scope (self ):
        if self .skip_words_scope ==SKIP_SCOPE_POSTS :
            self .skip_words_scope =SKIP_SCOPE_FILES 
        elif self .skip_words_scope ==SKIP_SCOPE_FILES :
            self .skip_words_scope =SKIP_SCOPE_BOTH 
        elif self .skip_words_scope ==SKIP_SCOPE_BOTH :
            self .skip_words_scope =SKIP_SCOPE_POSTS 
        else :
            self .skip_words_scope =SKIP_SCOPE_POSTS 

        self ._update_skip_scope_button_text ()
        self .settings .setValue (SKIP_WORDS_SCOPE_KEY ,self .skip_words_scope )
        self .log_signal .emit (f"ℹ️ Skip words scope changed to: '{self .skip_words_scope }'")

    def get_char_filter_scope (self ):
        return self .char_filter_scope 

    def _update_char_filter_scope_button_text (self ):
        if self .char_filter_scope_toggle_button :
            if self .char_filter_scope ==CHAR_SCOPE_FILES :
                self .char_filter_scope_toggle_button .setText (self ._tr ("char_filter_scope_files_text","Filter: Files"))
                self .char_filter_scope_toggle_button .setToolTip (self ._tr ("char_filter_scope_files_tooltip","Tooltip for char filter files"))
            elif self .char_filter_scope ==CHAR_SCOPE_TITLE :
                self .char_filter_scope_toggle_button .setText (self ._tr ("char_filter_scope_title_text","Filter: Title"))
                self .char_filter_scope_toggle_button .setToolTip (self ._tr ("char_filter_scope_title_tooltip","Tooltip for char filter title"))
            elif self .char_filter_scope ==CHAR_SCOPE_BOTH :
                self .char_filter_scope_toggle_button .setText (self ._tr ("char_filter_scope_both_text","Filter: Both"))
                self .char_filter_scope_toggle_button .setToolTip (self ._tr ("char_filter_scope_both_tooltip","Tooltip for char filter both"))
            elif self .char_filter_scope ==CHAR_SCOPE_COMMENTS :
                self .char_filter_scope_toggle_button .setText (self ._tr ("char_filter_scope_comments_text","Filter: Comments (Beta)"))
                self .char_filter_scope_toggle_button .setToolTip (self ._tr ("char_filter_scope_comments_tooltip","Tooltip for char filter comments"))
            else :
                self .char_filter_scope_toggle_button .setText (self ._tr ("char_filter_scope_unknown_text","Filter: Unknown"))
                self .char_filter_scope_toggle_button .setToolTip (self ._tr ("char_filter_scope_unknown_tooltip","Tooltip for char filter unknown"))

    def _cycle_char_filter_scope (self ):
        if self .char_filter_scope ==CHAR_SCOPE_TITLE :
            self .char_filter_scope =CHAR_SCOPE_FILES 
        elif self .char_filter_scope ==CHAR_SCOPE_FILES :
            self .char_filter_scope =CHAR_SCOPE_BOTH 
        elif self .char_filter_scope ==CHAR_SCOPE_BOTH :
            self .char_filter_scope =CHAR_SCOPE_COMMENTS 
        elif self .char_filter_scope ==CHAR_SCOPE_COMMENTS :
            self .char_filter_scope =CHAR_SCOPE_TITLE 
        else :
            self .char_filter_scope =CHAR_SCOPE_TITLE 

        self ._update_char_filter_scope_button_text ()
        self .settings .setValue (CHAR_FILTER_SCOPE_KEY ,self .char_filter_scope )
        self .log_signal .emit (f"ℹ️ Character filter scope changed to: '{self .char_filter_scope }'")

    def _handle_ui_add_new_character (self ):
        """Handles adding a new character from the UI input field."""
        name_from_ui_input =self .new_char_input .text ().strip ()
        successfully_added_any =False 

        if not name_from_ui_input :
            QMessageBox .warning (self ,"Input Error","Name cannot be empty.")
            return 

        if name_from_ui_input .startswith ("(")and name_from_ui_input .endswith (")~"):
            content =name_from_ui_input [1 :-2 ].strip ()
            aliases =[alias .strip ()for alias in content .split (',')if alias .strip ()]
            if aliases :
                folder_name =" ".join (aliases )
                if self .add_new_character (name_to_add =folder_name ,
                is_group_to_add =True ,
                aliases_to_add =aliases ,
                suppress_similarity_prompt =False ):
                    successfully_added_any =True 
            else :
                QMessageBox .warning (self ,"Input Error","Empty group content for `~` format.")

        elif name_from_ui_input .startswith ("(")and name_from_ui_input .endswith (")"):
            content =name_from_ui_input [1 :-1 ].strip ()
            names_to_add_separately =[name .strip ()for name in content .split (',')if name .strip ()]
            if names_to_add_separately :
                for name_item in names_to_add_separately :
                    if self .add_new_character (name_to_add =name_item ,
                    is_group_to_add =False ,
                    aliases_to_add =[name_item ],
                    suppress_similarity_prompt =False ):
                        successfully_added_any =True 
            else :
                QMessageBox .warning (self ,"Input Error","Empty group content for standard group format.")
        else :
            if self .add_new_character (name_to_add =name_from_ui_input ,
            is_group_to_add =False ,
            aliases_to_add =[name_from_ui_input ],
            suppress_similarity_prompt =False ):
                successfully_added_any =True 

        if successfully_added_any :
            self .new_char_input .clear ()
            self .save_known_names ()


    def add_new_character (self ,name_to_add ,is_group_to_add ,aliases_to_add ,suppress_similarity_prompt =False ):
        global KNOWN_NAMES ,clean_folder_name 
        if not name_to_add :
            QMessageBox .warning (self ,"Input Error","Name cannot be empty.");return False 

        name_to_add_lower =name_to_add .lower ()
        for kn_entry in KNOWN_NAMES :
            if kn_entry ["name"].lower ()==name_to_add_lower :
                QMessageBox .warning (self ,"Duplicate Name",f"The primary folder name '{name_to_add }' already exists.");return False 
            if not is_group_to_add and name_to_add_lower in [a .lower ()for a in kn_entry ["aliases"]]:
                QMessageBox .warning (self ,"Duplicate Alias",f"The name '{name_to_add }' already exists as an alias for '{kn_entry ['name']}'.");return False 

        similar_names_details =[]
        for kn_entry in KNOWN_NAMES :
            for term_to_check_similarity_against in kn_entry ["aliases"]:
                term_lower =term_to_check_similarity_against .lower ()
                if name_to_add_lower !=term_lower and (name_to_add_lower in term_lower or term_lower in name_to_add_lower ):
                    similar_names_details .append ((name_to_add ,kn_entry ["name"]))
                    break 
            for new_alias in aliases_to_add :
                if new_alias .lower ()!=term_to_check_similarity_against .lower ()and (new_alias .lower ()in term_to_check_similarity_against .lower ()or term_to_check_similarity_against .lower ()in new_alias .lower ()):
                    similar_names_details .append ((new_alias ,kn_entry ["name"]))
                    break 

        if similar_names_details and not suppress_similarity_prompt :
            if similar_names_details :
                first_similar_new ,first_similar_existing =similar_names_details [0 ]
                shorter ,longer =sorted ([first_similar_new ,first_similar_existing ],key =len )

                msg_box =QMessageBox (self )
                msg_box .setIcon (QMessageBox .Warning )
                msg_box .setWindowTitle ("Potential Name Conflict")
                msg_box .setText (
                f"The name '{first_similar_new }' is very similar to an existing name: '{first_similar_existing }'.\n\n"
                f"This could lead to unexpected folder grouping (e.g., under '{clean_folder_name (shorter )}' instead of a more specific '{clean_folder_name (longer )}' or vice-versa).\n\n"
                "Do you want to change the name you are adding, or proceed anyway?"
                )
                change_button =msg_box .addButton ("Change Name",QMessageBox .RejectRole )
                proceed_button =msg_box .addButton ("Proceed Anyway",QMessageBox .AcceptRole )
                msg_box .setDefaultButton (proceed_button )
                msg_box .setEscapeButton (change_button )
                msg_box .exec_ ()

                if msg_box .clickedButton ()==change_button :
                    self .log_signal .emit (f"ℹ️ User chose to change '{first_similar_new }' due to similarity with an alias of '{first_similar_existing }'.")
                    return False 
                self .log_signal .emit (f"⚠️ User proceeded with adding '{first_similar_new }' despite similarity with an alias of '{first_similar_existing }'.")
        new_entry ={
        "name":name_to_add ,
        "is_group":is_group_to_add ,
        "aliases":sorted (list (set (aliases_to_add )),key =str .lower )
        }
        if is_group_to_add :
            for new_alias in new_entry ["aliases"]:
                if any (new_alias .lower ()==kn_entry ["name"].lower ()for kn_entry in KNOWN_NAMES if kn_entry ["name"].lower ()!=name_to_add_lower ):
                    QMessageBox .warning (self ,"Alias Conflict",f"Alias '{new_alias }' (for group '{name_to_add }') conflicts with an existing primary name.");return False 
        KNOWN_NAMES .append (new_entry )
        KNOWN_NAMES .sort (key =lambda x :x ["name"].lower ())

        self .character_list .clear ()
        self .character_list .addItems ([entry ["name"]for entry in KNOWN_NAMES ])
        self .filter_character_list (self .character_search_input .text ())

        log_msg_suffix =f" (as group with aliases: {', '.join (new_entry ['aliases'])})"if is_group_to_add and len (new_entry ['aliases'])>1 else ""
        self .log_signal .emit (f"✅ Added '{name_to_add }' to known names list{log_msg_suffix }.")
        self .new_char_input .clear ()
        return True 


    def delete_selected_character (self ):
        global KNOWN_NAMES 
        selected_items =self .character_list .selectedItems ()
        if not selected_items :
            QMessageBox .warning (self ,"Selection Error","Please select one or more names to delete.");return 

        primary_names_to_remove ={item .text ()for item in selected_items }
        confirm =QMessageBox .question (self ,"Confirm Deletion",
        f"Are you sure you want to delete {len (primary_names_to_remove )} selected entry/entries (and their aliases)?",
        QMessageBox .Yes |QMessageBox .No ,QMessageBox .No )
        if confirm ==QMessageBox .Yes :
            original_count =len (KNOWN_NAMES )
            KNOWN_NAMES [:]=[entry for entry in KNOWN_NAMES if entry ["name"]not in primary_names_to_remove ]
            removed_count =original_count -len (KNOWN_NAMES )

            if removed_count >0 :
                self .log_signal .emit (f"🗑️ Removed {removed_count } name(s).")
                self .character_list .clear ()
                self .character_list .addItems ([entry ["name"]for entry in KNOWN_NAMES ])
                self .filter_character_list (self .character_search_input .text ())
                self .save_known_names ()
            else :
                self .log_signal .emit ("ℹ️ No names were removed (they might not have been in the list).")


    def update_custom_folder_visibility (self ,url_text =None ):
        if url_text is None :
            url_text =self .link_input .text ()

        _ ,_ ,post_id =extract_post_info (url_text .strip ())

        is_single_post_url =bool (post_id )
        subfolders_enabled =self .use_subfolders_checkbox .isChecked ()if self .use_subfolders_checkbox else False 

        not_only_links_or_archives_mode =not (
        (self .radio_only_links and self .radio_only_links .isChecked ())or 
        (self .radio_only_archives and self .radio_only_archives .isChecked ())or 
        (hasattr (self ,'radio_only_audio')and self .radio_only_audio .isChecked ())
        )

        should_show_custom_folder =is_single_post_url and subfolders_enabled and not_only_links_or_archives_mode 

        if self .custom_folder_widget :
            self .custom_folder_widget .setVisible (should_show_custom_folder )

        if not (self .custom_folder_widget and self .custom_folder_widget .isVisible ()):
            if self .custom_folder_input :self .custom_folder_input .clear ()


    def update_ui_for_subfolders (self ,separate_folders_by_name_title_checked :bool ):
        is_only_links =self .radio_only_links and self .radio_only_links .isChecked ()
        is_only_archives =self .radio_only_archives and self .radio_only_archives .isChecked ()
        is_only_audio =hasattr (self ,'radio_only_audio')and self .radio_only_audio .isChecked ()

        can_enable_subfolder_per_post_checkbox =not is_only_links and not is_only_archives 

        if self .use_subfolder_per_post_checkbox :
            self .use_subfolder_per_post_checkbox .setEnabled (can_enable_subfolder_per_post_checkbox )

            if not can_enable_subfolder_per_post_checkbox :
                self .use_subfolder_per_post_checkbox .setChecked (False )

        self .update_custom_folder_visibility ()


    def _update_cookie_input_visibility (self ,checked ):
        cookie_text_input_exists =hasattr (self ,'cookie_text_input')
        cookie_browse_button_exists =hasattr (self ,'cookie_browse_button')

        if cookie_text_input_exists or cookie_browse_button_exists :
            is_only_links =self .radio_only_links and self .radio_only_links .isChecked ()
            if cookie_text_input_exists :self .cookie_text_input .setVisible (checked )
            if cookie_browse_button_exists :self .cookie_browse_button .setVisible (checked )

            can_enable_cookie_text =checked and not is_only_links 
            enable_state_for_fields =can_enable_cookie_text and (self .download_btn .isEnabled ()or self .is_paused )

            if cookie_text_input_exists :
                self .cookie_text_input .setEnabled (enable_state_for_fields )
                if self .selected_cookie_filepath and checked :
                    self .cookie_text_input .setText (self .selected_cookie_filepath )
                    self .cookie_text_input .setReadOnly (True )
                    self .cookie_text_input .setPlaceholderText ("")
                elif checked :
                    self .cookie_text_input .setReadOnly (False )
                    self .cookie_text_input .setPlaceholderText ("Cookie string (if no cookies.txt)")

            if cookie_browse_button_exists :self .cookie_browse_button .setEnabled (enable_state_for_fields )

            if not checked :
                self .selected_cookie_filepath =None 


    def update_page_range_enabled_state (self ):
        url_text =self .link_input .text ().strip ()if self .link_input else ""
        _ ,_ ,post_id =extract_post_info (url_text )

        is_creator_feed =not post_id if url_text else False 
        enable_page_range =is_creator_feed 

        for widget in [self .page_range_label ,self .start_page_input ,self .to_label ,self .end_page_input ]:
            if widget :widget .setEnabled (enable_page_range )

        if not enable_page_range :
            if self .start_page_input :self .start_page_input .clear ()
            if self .end_page_input :self .end_page_input .clear ()


    def _update_manga_filename_style_button_text (self ):
        if self .manga_rename_toggle_button :
            if self .manga_filename_style ==STYLE_POST_TITLE :
                self .manga_rename_toggle_button .setText (self ._tr ("manga_style_post_title_text","Name: Post Title"))

            elif self .manga_filename_style ==STYLE_ORIGINAL_NAME :
                self .manga_rename_toggle_button .setText (self ._tr ("manga_style_original_file_text","Name: Original File"))

            elif self .manga_filename_style ==STYLE_POST_TITLE_GLOBAL_NUMBERING :
                self .manga_rename_toggle_button .setText (self ._tr ("manga_style_title_global_num_text","Name: Title+G.Num"))

            elif self .manga_filename_style ==STYLE_DATE_BASED :
                self .manga_rename_toggle_button .setText (self ._tr ("manga_style_date_based_text","Name: Date Based"))


            elif self.manga_filename_style == STYLE_DATE_POST_TITLE: # New style
                self.manga_rename_toggle_button.setText(self._tr("manga_style_date_post_title_text", "Name: Date + Title")) # Key from languages.py

            else :
                self .manga_rename_toggle_button .setText (self ._tr ("manga_style_unknown_text","Name: Unknown Style"))


            self .manga_rename_toggle_button .setToolTip ("Click to cycle Manga Filename Style (when Manga Mode is active for a creator feed).")


    def _toggle_manga_filename_style (self ):
        current_style =self .manga_filename_style 
        new_style =""
        if current_style ==STYLE_POST_TITLE :
            new_style =STYLE_ORIGINAL_NAME 
        elif current_style ==STYLE_ORIGINAL_NAME :
            new_style =STYLE_DATE_POST_TITLE # Cycle to new style
        elif current_style == STYLE_DATE_POST_TITLE: # New style in cycle
            new_style =STYLE_POST_TITLE_GLOBAL_NUMBERING 
        elif current_style ==STYLE_POST_TITLE_GLOBAL_NUMBERING :
            new_style =STYLE_DATE_BASED 
        elif current_style == STYLE_DATE_BASED: # Last style in old cycle
            new_style =STYLE_POST_TITLE 
        else :
            self .log_signal .emit (f"⚠️ Unknown current manga filename style: {current_style }. Resetting to default ('{STYLE_POST_TITLE }').")
            new_style =STYLE_POST_TITLE 

        self .manga_filename_style =new_style 
        self .settings .setValue (MANGA_FILENAME_STYLE_KEY ,self .manga_filename_style )
        self .settings .sync ()
        self ._update_manga_filename_style_button_text ()
        self .update_ui_for_manga_mode (self .manga_mode_checkbox .isChecked ()if self .manga_mode_checkbox else False )
        self .log_signal .emit (f"ℹ️ Manga filename style changed to: '{self .manga_filename_style }'")

    def _handle_favorite_mode_toggle (self ,checked ):
        if not self .url_or_placeholder_stack or not self .bottom_action_buttons_stack :
            return 

        self .url_or_placeholder_stack .setCurrentIndex (1 if checked else 0 )
        self .bottom_action_buttons_stack .setCurrentIndex (1 if checked else 0 )

        if checked :
            if self .link_input :
                self .link_input .clear ()
                self .link_input .setEnabled (False )
            for widget in [self .page_range_label ,self .start_page_input ,self .to_label ,self .end_page_input ]:
                if widget :widget .setEnabled (False )
            if self .start_page_input :self .start_page_input .clear ()
            if self .end_page_input :self .end_page_input .clear ()

            self .update_custom_folder_visibility ()
            self .update_page_range_enabled_state ()
            if self .manga_mode_checkbox :
                self .manga_mode_checkbox .setChecked (False )
                self .manga_mode_checkbox .setEnabled (False )
            if hasattr (self ,'use_cookie_checkbox'):
                self .use_cookie_checkbox .setChecked (True )
                self .use_cookie_checkbox .setEnabled (False )
            if hasattr (self ,'use_cookie_checkbox'):
                self ._update_cookie_input_visibility (True )
            self .update_ui_for_manga_mode (False )

            if hasattr (self ,'favorite_mode_artists_button'):
                self .favorite_mode_artists_button .setEnabled (True )
            if hasattr (self ,'favorite_mode_posts_button'):
                self .favorite_mode_posts_button .setEnabled (True )

        else :
            if self .link_input :self .link_input .setEnabled (True )
            self .update_page_range_enabled_state ()
            self .update_custom_folder_visibility ()
            self .update_ui_for_manga_mode (self .manga_mode_checkbox .isChecked ()if self .manga_mode_checkbox else False )

            if hasattr (self ,'use_cookie_checkbox'):
                self .use_cookie_checkbox .setEnabled (True )
            if hasattr (self ,'use_cookie_checkbox'):
                self ._update_cookie_input_visibility (self .use_cookie_checkbox .isChecked ())

            if hasattr (self ,'favorite_mode_artists_button'):
                self .favorite_mode_artists_button .setEnabled (False )
            if hasattr (self ,'favorite_mode_posts_button'):
                self .favorite_mode_posts_button .setEnabled (False )

    def update_ui_for_manga_mode (self ,checked ):
        is_only_links_mode =self .radio_only_links and self .radio_only_links .isChecked ()
        is_only_archives_mode =self .radio_only_archives and self .radio_only_archives .isChecked ()
        is_only_audio_mode =hasattr (self ,'radio_only_audio')and self .radio_only_audio .isChecked ()

        url_text =self .link_input .text ().strip ()if self .link_input else ""
        _ ,_ ,post_id =extract_post_info (url_text )

        is_creator_feed =not post_id if url_text else False 
        is_favorite_mode_on =self .favorite_mode_checkbox .isChecked ()if self .favorite_mode_checkbox else False 

        if self .manga_mode_checkbox :
            self .manga_mode_checkbox .setEnabled (is_creator_feed and not is_favorite_mode_on )
            if not is_creator_feed and self .manga_mode_checkbox .isChecked ():
                self .manga_mode_checkbox .setChecked (False )
                checked =self .manga_mode_checkbox .isChecked ()

        manga_mode_effectively_on =is_creator_feed and checked 

        if self .manga_rename_toggle_button :
            self .manga_rename_toggle_button .setVisible (manga_mode_effectively_on and not (is_only_links_mode or is_only_archives_mode or is_only_audio_mode ))

        self .update_page_range_enabled_state ()

        current_filename_style =self .manga_filename_style 

        enable_char_filter_widgets =not is_only_links_mode and not is_only_archives_mode 

        if self .character_input :
            self .character_input .setEnabled (enable_char_filter_widgets )
            if not enable_char_filter_widgets :self .character_input .clear ()
        if self .char_filter_scope_toggle_button :
            self .char_filter_scope_toggle_button .setEnabled (enable_char_filter_widgets )
        if self .character_filter_widget :
            self .character_filter_widget .setVisible (enable_char_filter_widgets )

        show_date_prefix_input =(
        manga_mode_effectively_on and 
        (current_filename_style == STYLE_DATE_BASED or 
         current_filename_style == STYLE_ORIGINAL_NAME) and # Prefix input not for Date+Title
        not (is_only_links_mode or is_only_archives_mode or is_only_audio_mode )
        )
        if hasattr (self ,'manga_date_prefix_input'):
            self .manga_date_prefix_input .setVisible (show_date_prefix_input )
            if show_date_prefix_input :
                self .manga_date_prefix_input .setMaximumWidth (120 )
                self .manga_date_prefix_input .setMinimumWidth (60 )
            else :
                self .manga_date_prefix_input .clear ()
                self .manga_date_prefix_input .setMaximumWidth (16777215 )
                self .manga_date_prefix_input .setMinimumWidth (0 )

        if hasattr (self ,'multipart_toggle_button'):

            hide_multipart_button_due_mode =is_only_links_mode or is_only_archives_mode or is_only_audio_mode 
            hide_multipart_button_due_manga_mode =manga_mode_effectively_on 
            self .multipart_toggle_button .setVisible (not (hide_multipart_button_due_mode or hide_multipart_button_due_manga_mode ))

        self ._update_multithreading_for_date_mode ()


    def filter_character_list (self ,search_text ):
        search_text_lower =search_text .lower ()
        for i in range (self .character_list .count ()):
            item =self .character_list .item (i )
            item .setHidden (search_text_lower not in item .text ().lower ())


    def update_multithreading_label (self ,text ):
        if self .use_multithreading_checkbox .isChecked ():
            base_text =self ._tr ("use_multithreading_checkbox_base_label","Use Multithreading")
            try :
                num_threads_val =int (text )
                if num_threads_val >0 :self .use_multithreading_checkbox .setText (f"{base_text } ({num_threads_val } Threads)")
                else :self .use_multithreading_checkbox .setText (f"{base_text } (Invalid: >0)")
            except ValueError :
                self .use_multithreading_checkbox .setText (f"{base_text } (Invalid Input)")
        else :
            self .use_multithreading_checkbox .setText (f"{self ._tr ('use_multithreading_checkbox_base_label','Use Multithreading')} (1 Thread)")


    def _handle_multithreading_toggle (self ,checked ):
        if not checked :
            self .thread_count_input .setEnabled (False )
            self .thread_count_label .setEnabled (False )
            self .use_multithreading_checkbox .setText ("Use Multithreading (1 Thread)")
        else :
            self .thread_count_input .setEnabled (True )
            self .thread_count_label .setEnabled (True )
            self .update_multithreading_label (self .thread_count_input .text ())

    def _update_multithreading_for_date_mode (self ):
        """
        Checks if Manga Mode is ON and 'Date Based' style is selected.
        If so, disables multithreading. Otherwise, enables it.
        """
        if not hasattr (self ,'manga_mode_checkbox')or not hasattr (self ,'use_multithreading_checkbox'):
            return 

        manga_on =self .manga_mode_checkbox .isChecked ()
        is_sequential_style_requiring_single_thread =(
        self .manga_filename_style ==STYLE_DATE_BASED or 
        self .manga_filename_style ==STYLE_POST_TITLE_GLOBAL_NUMBERING 
        )
        if manga_on and is_sequential_style_requiring_single_thread :
            if self .use_multithreading_checkbox .isChecked ()or self .use_multithreading_checkbox .isEnabled ():
                if self .use_multithreading_checkbox .isChecked ():
                    self .log_signal .emit ("ℹ️ Manga Date Mode: Multithreading for post processing has been disabled to ensure correct sequential file numbering.")
                self .use_multithreading_checkbox .setChecked (False )
            self .use_multithreading_checkbox .setEnabled (False )
            self ._handle_multithreading_toggle (False )
        else :
            if not self .use_multithreading_checkbox .isEnabled ():
                self .use_multithreading_checkbox .setEnabled (True )
            self ._handle_multithreading_toggle (self .use_multithreading_checkbox .isChecked ())

    def update_progress_display (self ,total_posts ,processed_posts ):
        if total_posts >0 :
            progress_percent =(processed_posts /total_posts )*100 
            self .progress_label .setText (self ._tr ("progress_posts_text","Progress: {processed_posts} / {total_posts} posts ({progress_percent:.1f}%)").format (processed_posts =processed_posts ,total_posts =total_posts ,progress_percent =progress_percent ))
        elif processed_posts >0 :
            self .progress_label .setText (self ._tr ("progress_processing_post_text","Progress: Processing post {processed_posts}...").format (processed_posts =processed_posts ))
        else :
            self .progress_label .setText (self ._tr ("progress_starting_text","Progress: Starting..."))

        if total_posts >0 or processed_posts >0 :
            self .file_progress_label .setText ("")


    def start_download (self ,direct_api_url =None ,override_output_dir =None ):
        global KNOWN_NAMES ,BackendDownloadThread ,PostProcessorWorker ,extract_post_info ,clean_folder_name ,MAX_FILE_THREADS_PER_POST_OR_WORKER 

        if self ._is_download_active ():
            QMessageBox .warning (self ,"Busy","A download is already running.")
            return False 

        # If this call to start_download is not for a specific URL (e.g., user clicked main "Download" button)
        # AND there are items in the favorite queue AND we are not already processing it.
        if not direct_api_url and self.favorite_download_queue and not self.is_processing_favorites_queue:
            self.log_signal.emit(f"ℹ️ Detected {len(self.favorite_download_queue)} item(s) in the queue. Starting processing...")
            self.cancellation_message_logged_this_session = False # Reset for new queue processing session
            self._process_next_favorite_download() # Directly call this to start processing the queue
            return True # Indicate that the download process has been initiated via the queue

        # If we reach here, it means either:
        # 1. direct_api_url was provided (e.g., recursive call from _process_next_favorite_download)
        # 2. The favorite_download_queue was empty or already being processed, so we fall back to link_input.
        api_url = direct_api_url if direct_api_url else self.link_input.text().strip()
        self.download_history_candidates.clear() # Clear candidates buffer for new download session
        # self.final_download_history_entries.clear() # DO NOT CLEAR HERE - loaded history should persist until a new download successfully finalizes new history

        if self.favorite_mode_checkbox and self.favorite_mode_checkbox.isChecked() and not direct_api_url and not api_url: # Check api_url here too
            QMessageBox.information(self, "Favorite Mode Active",
                                    "Favorite Mode is active. Please use the 'Favorite Artists' or 'Favorite Posts' buttons to start downloads in this mode, or uncheck 'Favorite Mode' to use the URL input.")
            self.set_ui_enabled(True)
            return False

        main_ui_download_dir = self.dir_input.text().strip()

        if not api_url and not self.favorite_download_queue: # If still no api_url and queue is empty
            QMessageBox.critical(self, "Input Error", "URL is required.")
            return False
        elif not api_url and self.favorite_download_queue: # Safeguard: if URL input is empty but queue has items
            self.log_signal.emit("ℹ️ URL input is empty, but queue has items. Processing queue...")
            self.cancellation_message_logged_this_session = False
            self._process_next_favorite_download() # This was the line with the unexpected indent
            return True

        self.cancellation_message_logged_this_session = False
        use_subfolders = self.use_subfolders_checkbox.isChecked()
        use_post_subfolders = self.use_subfolder_per_post_checkbox.isChecked()
        compress_images = self.compress_images_checkbox.isChecked()
        download_thumbnails = self.download_thumbnails_checkbox.isChecked()

        use_multithreading_enabled_by_checkbox = self.use_multithreading_checkbox.isChecked()
        try:
            num_threads_from_gui = int(self.thread_count_input.text().strip())
            if num_threads_from_gui < 1: num_threads_from_gui = 1
        except ValueError:
            QMessageBox.critical(self, "Thread Count Error", "Invalid number of threads. Please enter a positive number.")
            return False

        if use_multithreading_enabled_by_checkbox:
            if num_threads_from_gui > MAX_THREADS:
                hard_warning_msg = (
                    f"You've entered a thread count ({num_threads_from_gui}) exceeding the maximum of {MAX_THREADS}.\n\n"
                    "Using an extremely high number of threads can lead to:\n"
                    "  - Diminishing returns (no significant speed increase).\n"
                    "  - Increased system instability or application crashes.\n"
                    "  - Higher chance of being rate-limited or temporarily IP-banned by the server.\n\n"
                    f"The thread count has been automatically capped to {MAX_THREADS} for stability."
                )
                QMessageBox.warning(self, "High Thread Count Warning", hard_warning_msg)
                num_threads_from_gui = MAX_THREADS
                self.thread_count_input.setText(str(MAX_THREADS))
                self.log_signal.emit(f"⚠️ User attempted {num_threads_from_gui} threads, capped to {MAX_THREADS}.")
            if SOFT_WARNING_THREAD_THRESHOLD < num_threads_from_gui <= MAX_THREADS:
                soft_warning_msg_box = QMessageBox(self)
                soft_warning_msg_box.setIcon(QMessageBox.Question)
                soft_warning_msg_box.setWindowTitle("Thread Count Advisory")
                soft_warning_msg_box.setText(
                    f"You've set the thread count to {num_threads_from_gui}.\n\n"
                    "While this is within the allowed limit, using a high number of threads (typically above 40-50) can sometimes lead to:\n"
                    "  - Increased errors or failed file downloads.\n"
                    "  - Connection issues with the server.\n"
                    "  - Higher system resource usage.\n\n"
                    "For most users and connections, 10-30 threads provide a good balance.\n\n"
                    f"Do you want to proceed with {num_threads_from_gui} threads, or would you like to change the value?"
                )
                proceed_button = soft_warning_msg_box.addButton("Proceed Anyway", QMessageBox.AcceptRole)
                change_button = soft_warning_msg_box.addButton("Change Thread Value", QMessageBox.RejectRole)
                soft_warning_msg_box.setDefaultButton(proceed_button)
                soft_warning_msg_box.setEscapeButton(change_button)
                soft_warning_msg_box.exec_()

                if soft_warning_msg_box.clickedButton() == change_button:
                    self.log_signal.emit(f"ℹ️ User opted to change thread count from {num_threads_from_gui} after advisory.")
                    self.thread_count_input.setFocus()
                    self.thread_count_input.selectAll()
                    return False

        raw_skip_words = self.skip_words_input.text().strip()
        skip_words_list = [word.strip().lower() for word in raw_skip_words.split(',') if word.strip()]

        raw_remove_filename_words = self.remove_from_filename_input.text().strip() if hasattr(self, 'remove_from_filename_input') else ""
        allow_multipart = self.allow_multipart_download_setting
        remove_from_filename_words_list = [word.strip() for word in raw_remove_filename_words.split(',') if word.strip()]
        scan_content_for_images = self.scan_content_images_checkbox.isChecked() if hasattr(self, 'scan_content_images_checkbox') else False
        use_cookie_from_checkbox = self.use_cookie_checkbox.isChecked() if hasattr(self, 'use_cookie_checkbox') else False
        app_base_dir_for_cookies = os.path.dirname(self.config_file)
        cookie_text_from_input = self.cookie_text_input.text().strip() if hasattr(self, 'cookie_text_input') and use_cookie_from_checkbox else ""

        use_cookie_for_this_run = use_cookie_from_checkbox
        selected_cookie_file_path_for_backend = self.selected_cookie_filepath if use_cookie_from_checkbox and self.selected_cookie_filepath else None

        if use_cookie_from_checkbox and not direct_api_url: # Only show cookie help if it's a fresh download start from UI
            temp_cookies_for_check = prepare_cookies_for_request(
                use_cookie_for_this_run,
                cookie_text_from_input,
                selected_cookie_file_path_for_backend,
                app_base_dir_for_cookies,
                lambda msg: self.log_signal.emit(f"[UI Cookie Check] {msg}")
            )
            if temp_cookies_for_check is None:
                cookie_dialog = CookieHelpDialog(self, self, offer_download_without_option=True)
                dialog_exec_result = cookie_dialog.exec_()

                if cookie_dialog.user_choice == CookieHelpDialog.CHOICE_PROCEED_WITHOUT_COOKIES and dialog_exec_result == QDialog.Accepted:
                    self.log_signal.emit("ℹ️ User chose to download without cookies for this session.")
                    use_cookie_for_this_run = False
                elif cookie_dialog.user_choice == CookieHelpDialog.CHOICE_CANCEL_DOWNLOAD or dialog_exec_result == QDialog.Rejected:
                    self.log_signal.emit("❌ Download cancelled by user at cookie prompt.")
                    return False
                else: # Should not happen if dialog is modal and choices are handled
                    self.log_signal.emit("⚠️ Cookie dialog closed or unexpected choice. Aborting download.")
                    return False

        current_skip_words_scope = self.get_skip_words_scope()
        manga_mode_is_checked = self.manga_mode_checkbox.isChecked() if self.manga_mode_checkbox else False

        extract_links_only = (self.radio_only_links and self.radio_only_links.isChecked())
        backend_filter_mode = self.get_filter_mode()
        checked_radio_button = self.radio_group.checkedButton()
        user_selected_filter_text = checked_radio_button.text() if checked_radio_button else "All"

        effective_output_dir_for_run = ""

        if selected_cookie_file_path_for_backend: # If a file is selected, cookie_text_from_input should be ignored by backend
            cookie_text_from_input = ""

        if backend_filter_mode == 'archive':
            effective_skip_zip = False
            effective_skip_rar = False
        else:
            effective_skip_zip = self.skip_zip_checkbox.isChecked()
            effective_skip_rar = self.skip_rar_checkbox.isChecked()
            if backend_filter_mode == 'audio': # Ensure audio mode doesn't force skip_zip/rar off
                effective_skip_zip = self.skip_zip_checkbox.isChecked()
                effective_skip_rar = self.skip_rar_checkbox.isChecked()

        if not api_url: # This check is now after the queue processing
            QMessageBox.critical(self, "Input Error", "URL is required.")
            return False

        if override_output_dir: # This is for items from the queue that need specific artist folders
            if not main_ui_download_dir: # Main download dir must be set for this
                QMessageBox.critical(self, "Configuration Error",
                                     "The main 'Download Location' must be set in the UI "
                                     "before downloading favorites with 'Artist Folders' scope.")
                if self.is_processing_favorites_queue:
                    self.log_signal.emit(f"❌ Favorite download for '{api_url}' skipped: Main download directory not set.")
                return False # Stop this specific item

            if not os.path.isdir(main_ui_download_dir):
                QMessageBox.critical(self, "Directory Error",
                                     f"The main 'Download Location' ('{main_ui_download_dir}') "
                                     "does not exist or is not a directory. Please set a valid one for 'Artist Folders' scope.")
                if self.is_processing_favorites_queue:
                    self.log_signal.emit(f"❌ Favorite download for '{api_url}' skipped: Main download directory invalid.")
                return False # Stop this specific item
            effective_output_dir_for_run = os.path.normpath(override_output_dir)
        else: # For direct URL input or items not needing override
            if not extract_links_only and not main_ui_download_dir:
                QMessageBox.critical(self, "Input Error", "Download Directory is required when not in 'Only Links' mode.")
                return False

            if not extract_links_only and main_ui_download_dir and not os.path.isdir(main_ui_download_dir):
                reply = QMessageBox.question(self, "Create Directory?",
                                             f"The directory '{main_ui_download_dir}' does not exist.\nCreate it now?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    try:
                        os.makedirs(main_ui_download_dir, exist_ok=True)
                        self.log_signal.emit(f"ℹ️ Created directory: {main_ui_download_dir}")
                    except Exception as e:
                        QMessageBox.critical(self, "Directory Error", f"Could not create directory: {e}")
                        return False
                else:
                    self.log_signal.emit("❌ Download cancelled: Output directory does not exist and was not created.")
                    return False
            effective_output_dir_for_run = os.path.normpath(main_ui_download_dir)

        service, user_id, post_id_from_url = extract_post_info(api_url)
        if not service or not user_id: # This check is fine here
            QMessageBox.critical(self, "Input Error", "Invalid or unsupported URL format.")
            return False

        # ... (rest of the start_download method remains the same)
            self ._process_next_favorite_download ()
            return True 


        if self .favorite_mode_checkbox and self .favorite_mode_checkbox .isChecked ()and not direct_api_url :
            QMessageBox .information (self ,"Favorite Mode Active",

            "Favorite Mode is active. Please use the 'Favorite Artists' or 'Favorite Posts' buttons to start downloads in this mode, or uncheck 'Favorite Mode' to use the URL input.")
            self .set_ui_enabled (True )
            return 
            return False 
        api_url =direct_api_url if direct_api_url else self .link_input .text ().strip ()
        main_ui_download_dir =self .dir_input .text ().strip ()

        self .cancellation_message_logged_this_session =False 
        use_subfolders =self .use_subfolders_checkbox .isChecked ()
        use_post_subfolders =self .use_subfolder_per_post_checkbox .isChecked ()
        compress_images =self .compress_images_checkbox .isChecked ()
        download_thumbnails =self .download_thumbnails_checkbox .isChecked ()

        use_multithreading_enabled_by_checkbox =self .use_multithreading_checkbox .isChecked ()
        try :
            num_threads_from_gui =int (self .thread_count_input .text ().strip ())
            if num_threads_from_gui <1 :num_threads_from_gui =1 
        except ValueError :
            QMessageBox .critical (self ,"Thread Count Error","Invalid number of threads. Please enter a positive number.")
            return False 

        if use_multithreading_enabled_by_checkbox :
            if num_threads_from_gui >MAX_THREADS :
                hard_warning_msg =(
                f"You've entered a thread count ({num_threads_from_gui }) exceeding the maximum of {MAX_THREADS }.\n\n"
                "Using an extremely high number of threads can lead to:\n"
                "  - Diminishing returns (no significant speed increase).\n"
                "  - Increased system instability or application crashes.\n"
                "  - Higher chance of being rate-limited or temporarily IP-banned by the server.\n\n"
                f"The thread count has been automatically capped to {MAX_THREADS } for stability."
                )
                QMessageBox .warning (self ,"High Thread Count Warning",hard_warning_msg )
                num_threads_from_gui =MAX_THREADS 
                self .thread_count_input .setText (str (MAX_THREADS ))
                self .log_signal .emit (f"⚠️ User attempted {num_threads_from_gui } threads, capped to {MAX_THREADS }.")
            if SOFT_WARNING_THREAD_THRESHOLD <num_threads_from_gui <=MAX_THREADS :
                soft_warning_msg_box =QMessageBox (self )
                soft_warning_msg_box .setIcon (QMessageBox .Question )
                soft_warning_msg_box .setWindowTitle ("Thread Count Advisory")
                soft_warning_msg_box .setText (
                f"You've set the thread count to {num_threads_from_gui }.\n\n"
                "While this is within the allowed limit, using a high number of threads (typically above 40-50) can sometimes lead to:\n"
                "  - Increased errors or failed file downloads.\n"
                "  - Connection issues with the server.\n"
                "  - Higher system resource usage.\n\n"
                "For most users and connections, 10-30 threads provide a good balance.\n\n"
                f"Do you want to proceed with {num_threads_from_gui } threads, or would you like to change the value?"
                )
                proceed_button =soft_warning_msg_box .addButton ("Proceed Anyway",QMessageBox .AcceptRole )
                change_button =soft_warning_msg_box .addButton ("Change Thread Value",QMessageBox .RejectRole )
                soft_warning_msg_box .setDefaultButton (proceed_button )
                soft_warning_msg_box .setEscapeButton (change_button )
                soft_warning_msg_box .exec_ ()

                if soft_warning_msg_box .clickedButton ()==change_button :
                    self .log_signal .emit (f"ℹ️ User opted to change thread count from {num_threads_from_gui } after advisory.")
                    self .thread_count_input .setFocus ()
                    self .thread_count_input .selectAll ()
                    return False 

        raw_skip_words =self .skip_words_input .text ().strip ()
        skip_words_list =[word .strip ().lower ()for word in raw_skip_words .split (',')if word .strip ()]

        raw_remove_filename_words =self .remove_from_filename_input .text ().strip ()if hasattr (self ,'remove_from_filename_input')else ""
        allow_multipart =self .allow_multipart_download_setting 
        remove_from_filename_words_list =[word .strip ()for word in raw_remove_filename_words .split (',')if word .strip ()]
        scan_content_for_images =self .scan_content_images_checkbox .isChecked ()if hasattr (self ,'scan_content_images_checkbox')else False 
        use_cookie_from_checkbox =self .use_cookie_checkbox .isChecked ()if hasattr (self ,'use_cookie_checkbox')else False 
        app_base_dir_for_cookies =os .path .dirname (self .config_file )
        cookie_text_from_input =self .cookie_text_input .text ().strip ()if hasattr (self ,'cookie_text_input')and use_cookie_from_checkbox else ""

        use_cookie_for_this_run =use_cookie_from_checkbox 
        selected_cookie_file_path_for_backend =self .selected_cookie_filepath if use_cookie_from_checkbox and self .selected_cookie_filepath else None 

        if use_cookie_from_checkbox and not direct_api_url :
            temp_cookies_for_check =prepare_cookies_for_request (
            use_cookie_for_this_run ,
            cookie_text_from_input ,
            selected_cookie_file_path_for_backend ,
            app_base_dir_for_cookies ,
            lambda msg :self .log_signal .emit (f"[UI Cookie Check] {msg }")
            )
            if temp_cookies_for_check is None :
                cookie_dialog =CookieHelpDialog (self ,self ,offer_download_without_option =True )
                dialog_exec_result =cookie_dialog .exec_ ()

                if cookie_dialog .user_choice ==CookieHelpDialog .CHOICE_PROCEED_WITHOUT_COOKIES and dialog_exec_result ==QDialog .Accepted :
                    self .log_signal .emit ("ℹ️ User chose to download without cookies for this session.")
                    use_cookie_for_this_run =False 
                elif cookie_dialog .user_choice ==CookieHelpDialog .CHOICE_CANCEL_DOWNLOAD or dialog_exec_result ==QDialog .Rejected :
                    self .log_signal .emit ("❌ Download cancelled by user at cookie prompt.")
                    return False 
                else :
                    self .log_signal .emit ("⚠️ Cookie dialog closed or unexpected choice. Aborting download.")
                    return False 

        current_skip_words_scope =self .get_skip_words_scope ()
        manga_mode_is_checked =self .manga_mode_checkbox .isChecked ()if self .manga_mode_checkbox else False 

        extract_links_only =(self .radio_only_links and self .radio_only_links .isChecked ())
        backend_filter_mode =self .get_filter_mode ()
        checked_radio_button =self .radio_group .checkedButton ()
        user_selected_filter_text =checked_radio_button .text ()if checked_radio_button else "All"


        effective_output_dir_for_run =""

        if selected_cookie_file_path_for_backend :
            cookie_text_from_input =""

        if backend_filter_mode =='archive':
            effective_skip_zip =False 
            effective_skip_rar =False 
        else :
            effective_skip_zip =self .skip_zip_checkbox .isChecked ()
            effective_skip_rar =self .skip_rar_checkbox .isChecked ()
            if backend_filter_mode =='audio':
                effective_skip_zip =self .skip_zip_checkbox .isChecked ()
                effective_skip_rar =self .skip_rar_checkbox .isChecked ()

        if not api_url :
            QMessageBox .critical (self ,"Input Error","URL is required.")
            return False 

        if override_output_dir :
            if not main_ui_download_dir :
                QMessageBox .critical (self ,"Configuration Error",
                "The main 'Download Location' must be set in the UI "
                "before downloading favorites with 'Artist Folders' scope.")
                if self .is_processing_favorites_queue :
                    self .log_signal .emit (f"❌ Favorite download for '{api_url }' skipped: Main download directory not set.")
                return False 

            if not os .path .isdir (main_ui_download_dir ):
                QMessageBox .critical (self ,"Directory Error",
                f"The main 'Download Location' ('{main_ui_download_dir }') "
                "does not exist or is not a directory. Please set a valid one for 'Artist Folders' scope.")
                if self .is_processing_favorites_queue :
                    self .log_signal .emit (f"❌ Favorite download for '{api_url }' skipped: Main download directory invalid.")
                return False 
            effective_output_dir_for_run =os .path .normpath (override_output_dir )
        else :
            if not extract_links_only and not main_ui_download_dir :
                QMessageBox .critical (self ,"Input Error","Download Directory is required when not in 'Only Links' mode.")
                return False 

            if not extract_links_only and main_ui_download_dir and not os .path .isdir (main_ui_download_dir ):
                reply =QMessageBox .question (self ,"Create Directory?",
                f"The directory '{main_ui_download_dir }' does not exist.\nCreate it now?",
                QMessageBox .Yes |QMessageBox .No ,QMessageBox .Yes )
                if reply ==QMessageBox .Yes :
                    try :
                        os .makedirs (main_ui_download_dir ,exist_ok =True )
                        self .log_signal .emit (f"ℹ️ Created directory: {main_ui_download_dir }")
                    except Exception as e :
                        QMessageBox .critical (self ,"Directory Error",f"Could not create directory: {e }")
                        return False 
                else :
                    self .log_signal .emit ("❌ Download cancelled: Output directory does not exist and was not created.")
                    return False 
            effective_output_dir_for_run =os .path .normpath (main_ui_download_dir )

        service ,user_id ,post_id_from_url =extract_post_info (api_url )
        if not service or not user_id :
            QMessageBox .critical (self ,"Input Error","Invalid or unsupported URL format.")
            return False 

        creator_folder_ignore_words_for_run =None 
        is_full_creator_download =not post_id_from_url 









        if compress_images and Image is None :
            QMessageBox .warning (self ,"Missing Dependency","Pillow library (for image compression) not found. Compression will be disabled.")
            compress_images =False ;self .compress_images_checkbox .setChecked (False )

        log_messages =["="*40 ,f"🚀 Starting {'Link Extraction'if extract_links_only else ('Archive Download'if backend_filter_mode =='archive'else 'Download')} @ {time .strftime ('%Y-%m-%d %H:%M:%S')}",f"    URL: {api_url }"]

        current_mode_log_text ="Download"
        if extract_links_only :current_mode_log_text ="Link Extraction"
        elif backend_filter_mode =='archive':current_mode_log_text ="Archive Download"
        elif backend_filter_mode =='audio':current_mode_log_text ="Audio Download"

        current_char_filter_scope =self .get_char_filter_scope ()
        manga_mode =manga_mode_is_checked and not post_id_from_url 

        manga_date_prefix_text =""
        if manga_mode and (self .manga_filename_style ==STYLE_DATE_BASED or self .manga_filename_style ==STYLE_ORIGINAL_NAME )and hasattr (self ,'manga_date_prefix_input'):
            manga_date_prefix_text =self .manga_date_prefix_input .text ().strip ()
            if manga_date_prefix_text :
                log_messages .append (f"      ↳ Manga Date Prefix: '{manga_date_prefix_text }'")

        start_page_str ,end_page_str =self .start_page_input .text ().strip (),self .end_page_input .text ().strip ()
        start_page ,end_page =None ,None 
        is_creator_feed =bool (not post_id_from_url )

        if is_creator_feed :
            try :
                if start_page_str :start_page =int (start_page_str )
                if end_page_str :end_page =int (end_page_str )

                if start_page is not None and start_page <=0 :raise ValueError ("Start page must be positive.")
                if end_page is not None and end_page <=0 :raise ValueError ("End page must be positive.")
                if start_page and end_page and start_page >end_page :raise ValueError ("Start page cannot be greater than end page.")

                if manga_mode and start_page and end_page :
                    msg_box =QMessageBox (self )
                    msg_box .setIcon (QMessageBox .Warning )
                    msg_box .setWindowTitle ("Manga Mode & Page Range Warning")
                    msg_box .setText (
                    "You have enabled <b>Manga/Comic Mode</b> and also specified a <b>Page Range</b>.\n\n"
                    "Manga Mode processes posts from oldest to newest across all available pages by default.\n"
                    "If you use a page range, you might miss parts of the manga/comic if it starts before your 'Start Page' or continues after your 'End Page'.\n\n"
                    "However, if you are certain the content you want is entirely within this page range (e.g., a short series, or you know the specific pages for a volume), then proceeding is okay.\n\n"
                    "Do you want to proceed with this page range in Manga Mode?"
                    )
                    proceed_button =msg_box .addButton ("Proceed Anyway",QMessageBox .AcceptRole )
                    cancel_button =msg_box .addButton ("Cancel Download",QMessageBox .RejectRole )
                    msg_box .setDefaultButton (proceed_button )
                    msg_box .setEscapeButton (cancel_button )
                    msg_box .exec_ ()

                    if msg_box .clickedButton ()==cancel_button :
                        self .log_signal .emit ("❌ Download cancelled by user due to Manga Mode & Page Range warning.")
                        return False 
            except ValueError as e :
                QMessageBox .critical (self ,"Page Range Error",f"Invalid page range: {e }")
                return False 
        self .external_link_queue .clear ();self .extracted_links_cache =[];self ._is_processing_external_link_queue =False ;self ._current_link_post_title =None 

        raw_character_filters_text =self .character_input .text ().strip ()
        parsed_character_filter_objects =self ._parse_character_filters (raw_character_filters_text )

        actual_filters_to_use_for_run =[]

        needs_folder_naming_validation =(use_subfolders or manga_mode )and not extract_links_only 

        if parsed_character_filter_objects :
            actual_filters_to_use_for_run =parsed_character_filter_objects 

            if not extract_links_only :
                self .log_signal .emit (f"ℹ️ Using character filters for matching: {', '.join (item ['name']for item in actual_filters_to_use_for_run )}")

                filter_objects_to_potentially_add_to_known_list =[]
                for filter_item_obj in parsed_character_filter_objects :
                    item_primary_name =filter_item_obj ["name"]
                    cleaned_name_test =clean_folder_name (item_primary_name )
                    if needs_folder_naming_validation and not cleaned_name_test :
                        QMessageBox .warning (self ,"Invalid Filter Name for Folder",f"Filter name '{item_primary_name }' is invalid for a folder and will be skipped for Known.txt interaction.")
                        self .log_signal .emit (f"⚠️ Skipping invalid filter for Known.txt interaction: '{item_primary_name }'")
                        continue 

                    an_alias_is_already_known =False 
                    if any (kn_entry ["name"].lower ()==item_primary_name .lower ()for kn_entry in KNOWN_NAMES ):
                        an_alias_is_already_known =True 
                    elif filter_item_obj ["is_group"]and needs_folder_naming_validation :
                        for alias_in_filter_obj in filter_item_obj ["aliases"]:
                            if any (kn_entry ["name"].lower ()==alias_in_filter_obj .lower ()or alias_in_filter_obj .lower ()in [a .lower ()for a in kn_entry ["aliases"]]for kn_entry in KNOWN_NAMES ):
                                an_alias_is_already_known =True ;break 

                    if an_alias_is_already_known and filter_item_obj ["is_group"]:
                        self .log_signal .emit (f"ℹ️ An alias from group '{item_primary_name }' is already known. Group will not be prompted for Known.txt addition.")

                    should_prompt_to_add_to_known_list =(
                    needs_folder_naming_validation and not manga_mode and 
                    not any (kn_entry ["name"].lower ()==item_primary_name .lower ()for kn_entry in KNOWN_NAMES )and 
                    not an_alias_is_already_known 
                    )
                    if should_prompt_to_add_to_known_list :
                        if not any (obj_to_add ["name"].lower ()==item_primary_name .lower ()for obj_to_add in filter_objects_to_potentially_add_to_known_list ):
                            filter_objects_to_potentially_add_to_known_list .append (filter_item_obj )
                    elif manga_mode and needs_folder_naming_validation and item_primary_name .lower ()not in {kn_entry ["name"].lower ()for kn_entry in KNOWN_NAMES }and not an_alias_is_already_known :
                        self .log_signal .emit (f"ℹ️ Manga Mode: Using filter '{item_primary_name }' for this session without adding to Known Names.")

                if filter_objects_to_potentially_add_to_known_list :
                    confirm_dialog =ConfirmAddAllDialog (filter_objects_to_potentially_add_to_known_list ,self ,self )
                    dialog_result =confirm_dialog .exec_ ()

                    if dialog_result ==CONFIRM_ADD_ALL_CANCEL_DOWNLOAD :
                        self .log_signal .emit ("❌ Download cancelled by user at new name confirmation stage.")
                        return False 
                    elif isinstance (dialog_result ,list ):
                        if dialog_result :
                            self .log_signal .emit (f"ℹ️ User chose to add {len (dialog_result )} new entry/entries to Known.txt.")
                            for filter_obj_to_add in dialog_result :
                                if filter_obj_to_add .get ("components_are_distinct_for_known_txt"):
                                    self .log_signal .emit (f"    Processing group '{filter_obj_to_add ['name']}' to add its components individually to Known.txt.")
                                    for alias_component in filter_obj_to_add ["aliases"]:
                                        self .add_new_character (
                                        name_to_add =alias_component ,
                                        is_group_to_add =False ,
                                        aliases_to_add =[alias_component ],
                                        suppress_similarity_prompt =True 
                                        )
                                else :
                                    self .add_new_character (
                                    name_to_add =filter_obj_to_add ["name"],
                                    is_group_to_add =filter_obj_to_add ["is_group"],
                                    aliases_to_add =filter_obj_to_add ["aliases"],
                                    suppress_similarity_prompt =True 
                                    )
                        else :
                            self .log_signal .emit ("ℹ️ User confirmed adding, but no names were selected in the dialog. No new names added to Known.txt.")
                    elif dialog_result ==CONFIRM_ADD_ALL_SKIP_ADDING :
                        self .log_signal .emit ("ℹ️ User chose not to add new names to Known.txt for this session.")
            else :
                self .log_signal .emit (f"ℹ️ Using character filters for link extraction: {', '.join (item ['name']for item in actual_filters_to_use_for_run )}")


        if manga_mode and not actual_filters_to_use_for_run and not extract_links_only :
            msg_box =QMessageBox (self )
            msg_box .setIcon (QMessageBox .Warning )
            msg_box .setWindowTitle ("Manga Mode Filter Warning")
            msg_box .setText (
            "Manga Mode is enabled, but 'Filter by Character(s)' is empty.\n\n"
            "For best results (correct file naming and folder organization if subfolders are on), "
            "please enter the Manga/Series title into the filter field.\n\n"
            "Proceed without a filter (names might be generic, folder might be less specific)?"
            )
            proceed_button =msg_box .addButton ("Proceed Anyway",QMessageBox .AcceptRole )
            cancel_button =msg_box .addButton ("Cancel Download",QMessageBox .RejectRole )
            msg_box .exec_ ()
            if msg_box .clickedButton ()==cancel_button :
                self .log_signal .emit ("❌ Download cancelled due to Manga Mode filter warning.")
                return False 
            else :
                self .log_signal .emit ("⚠️ Proceeding with Manga Mode without a specific title filter.")
        self .dynamic_character_filter_holder .set_filters (actual_filters_to_use_for_run )


        creator_folder_ignore_words_for_run =None 
        character_filters_are_empty =not actual_filters_to_use_for_run 
        if is_full_creator_download and character_filters_are_empty :
            creator_folder_ignore_words_for_run =CREATOR_DOWNLOAD_DEFAULT_FOLDER_IGNORE_WORDS 
            log_messages .append (f"    Creator Download (No Char Filter): Applying default folder name ignore list ({len (creator_folder_ignore_words_for_run )} words).")

        custom_folder_name_cleaned =None 
        if use_subfolders and post_id_from_url and self .custom_folder_widget and self .custom_folder_widget .isVisible ()and not extract_links_only :
            raw_custom_name =self .custom_folder_input .text ().strip ()
            if raw_custom_name :
                cleaned_custom =clean_folder_name (raw_custom_name )
                if cleaned_custom :custom_folder_name_cleaned =cleaned_custom 
                else :self .log_signal .emit (f"⚠️ Invalid custom folder name ignored: '{raw_custom_name }' (resulted in empty string after cleaning).")


        self .main_log_output .clear ()
        if extract_links_only :self .main_log_output .append ("🔗 Extracting Links...");
        elif backend_filter_mode =='archive':self .main_log_output .append ("📦 Downloading Archives Only...")

        if self .external_log_output :self .external_log_output .clear ()
        if self .show_external_links and not extract_links_only and backend_filter_mode !='archive':
            self .external_log_output .append ("🔗 External Links Found:")

        self .file_progress_label .setText ("");self .cancellation_event .clear ();self .active_futures =[]
        self .total_posts_to_process =0 ;self .processed_posts_count =0 ;self .download_counter =0 ;self .skip_counter =0 
        self .progress_label .setText (self ._tr ("progress_initializing_text","Progress: Initializing..."))

        self .retryable_failed_files_info .clear ()
        self .permanently_failed_files_for_dialog .clear ()

        manga_date_file_counter_ref_for_thread =None 
        if manga_mode and self .manga_filename_style ==STYLE_DATE_BASED and not extract_links_only :
            manga_date_file_counter_ref_for_thread =None 
            self .log_signal .emit (f"ℹ️ Manga Date Mode: File counter will be initialized by the download thread.")

        manga_global_file_counter_ref_for_thread =None 
        if manga_mode and self .manga_filename_style ==STYLE_POST_TITLE_GLOBAL_NUMBERING and not extract_links_only :
            manga_global_file_counter_ref_for_thread =None 
            self .log_signal .emit (f"ℹ️ Manga Title+GlobalNum Mode: File counter will be initialized by the download thread (starts at 1).")

        effective_num_post_workers =1 

        effective_num_file_threads_per_worker =1 

        if post_id_from_url :
            if use_multithreading_enabled_by_checkbox :
                effective_num_file_threads_per_worker =max (1 ,min (num_threads_from_gui ,MAX_FILE_THREADS_PER_POST_OR_WORKER ))
        else :
            if manga_mode and self .manga_filename_style ==STYLE_DATE_BASED :
                effective_num_post_workers =1 
            elif manga_mode and self .manga_filename_style ==STYLE_POST_TITLE_GLOBAL_NUMBERING :
                effective_num_post_workers =1 
                effective_num_file_threads_per_worker =1 
            elif use_multithreading_enabled_by_checkbox :
                effective_num_post_workers =max (1 ,min (num_threads_from_gui ,MAX_THREADS ))
                effective_num_file_threads_per_worker =1 

        if not extract_links_only :log_messages .append (f"    Save Location: {effective_output_dir_for_run }")

        if post_id_from_url :
            log_messages .append (f"    Mode: Single Post")
            log_messages .append (f"      ↳ File Downloads: Up to {effective_num_file_threads_per_worker } concurrent file(s)")
        else :
            log_messages .append (f"    Mode: Creator Feed")
            log_messages .append (f"    Post Processing: {'Multi-threaded ('+str (effective_num_post_workers )+' workers)'if effective_num_post_workers >1 else 'Single-threaded (1 worker)'}")
            log_messages .append (f"      ↳ File Downloads per Worker: Up to {effective_num_file_threads_per_worker } concurrent file(s)")
            pr_log ="All"
            if start_page or end_page :
                pr_log =f"{f'From {start_page } 'if start_page else ''}{'to 'if start_page and end_page else ''}{f'{end_page }'if end_page else (f'Up to {end_page }'if end_page else (f'From {start_page }'if start_page else 'Specific Range'))}".strip ()

            if manga_mode :
                log_messages .append (f"    Page Range: {pr_log if pr_log else 'All'} (Manga Mode - Oldest Posts Processed First within range)")
            else :
                log_messages .append (f"    Page Range: {pr_log if pr_log else 'All'}")


        if not extract_links_only :
            log_messages .append (f"    Subfolders: {'Enabled'if use_subfolders else 'Disabled'}")
            if use_subfolders :
                if custom_folder_name_cleaned :log_messages .append (f"    Custom Folder (Post): '{custom_folder_name_cleaned }'")
            if actual_filters_to_use_for_run :
                log_messages .append (f"    Character Filters: {', '.join (item ['name']for item in actual_filters_to_use_for_run )}")
                log_messages .append (f"      ↳ Char Filter Scope: {current_char_filter_scope .capitalize ()}")
            elif use_subfolders :
                log_messages .append (f"    Folder Naming: Automatic (based on title/known names)")


            log_messages .extend ([
            f"    File Type Filter: {user_selected_filter_text } (Backend processing as: {backend_filter_mode })",
            f"    Skip Archives: {'.zip'if effective_skip_zip else ''}{', 'if effective_skip_zip and effective_skip_rar else ''}{'.rar'if effective_skip_rar else ''}{'None (Archive Mode)'if backend_filter_mode =='archive'else ('None'if not (effective_skip_zip or effective_skip_rar )else '')}",
            f"    Skip Words (posts/files): {', '.join (skip_words_list )if skip_words_list else 'None'}",
            f"    Skip Words Scope: {current_skip_words_scope .capitalize ()}",
            f"    Remove Words from Filename: {', '.join (remove_from_filename_words_list )if remove_from_filename_words_list else 'None'}",
            f"    Compress Images: {'Enabled'if compress_images else 'Disabled'}",
            f"    Thumbnails Only: {'Enabled'if download_thumbnails else 'Disabled'}"
            ])
            log_messages .append (f"    Scan Post Content for Images: {'Enabled'if scan_content_for_images else 'Disabled'}")
        else :
            log_messages .append (f"    Mode: Extracting Links Only")

        log_messages .append (f"    Show External Links: {'Enabled'if self .show_external_links and not extract_links_only and backend_filter_mode !='archive'else 'Disabled'}")

        if manga_mode :
            log_messages .append (f"    Manga Mode (File Renaming by Post Title): Enabled")
            log_messages .append (f"      ↳ Manga Filename Style: {'Post Title Based'if self .manga_filename_style ==STYLE_POST_TITLE else 'Original File Name'}")
            if actual_filters_to_use_for_run :
                log_messages .append (f"      ↳ Manga Character Filter (for naming/folder): {', '.join (item ['name']for item in actual_filters_to_use_for_run )}")
            log_messages .append (f"      ↳ Manga Duplicates: Will be renamed with numeric suffix if names clash (e.g., _1, _2).")

        log_messages .append (f"    Use Cookie ('cookies.txt'): {'Enabled'if use_cookie_from_checkbox else 'Disabled'}")
        if use_cookie_from_checkbox and cookie_text_from_input :
            log_messages .append (f"      ↳ Cookie Text Provided: Yes (length: {len (cookie_text_from_input )})")
        elif use_cookie_from_checkbox and selected_cookie_file_path_for_backend :
            log_messages .append (f"      ↳ Cookie File Selected: {os .path .basename (selected_cookie_file_path_for_backend )}")
        should_use_multithreading_for_posts =use_multithreading_enabled_by_checkbox and not post_id_from_url 
        if manga_mode and (self .manga_filename_style ==STYLE_DATE_BASED or self .manga_filename_style ==STYLE_POST_TITLE_GLOBAL_NUMBERING )and not post_id_from_url :
            enforced_by_style ="Date Mode"if self .manga_filename_style ==STYLE_DATE_BASED else "Title+GlobalNum Mode"
            should_use_multithreading_for_posts =False 
            log_messages .append (f"    Threading: Single-threaded (posts) - Enforced by Manga {enforced_by_style } (Actual workers: {effective_num_post_workers if effective_num_post_workers >1 else 1 })")
        else :
            log_messages .append (f"    Threading: {'Multi-threaded (posts)'if should_use_multithreading_for_posts else 'Single-threaded (posts)'}")
        if should_use_multithreading_for_posts :
            log_messages .append (f"    Number of Post Worker Threads: {effective_num_post_workers }")
        log_messages .append ("="*40 )
        for msg in log_messages :self .log_signal .emit (msg )

        self .set_ui_enabled (False )


        from downloader_utils import FOLDER_NAME_STOP_WORDS 


        args_template ={
        'api_url_input':api_url ,
        'download_root':effective_output_dir_for_run ,
        'output_dir':effective_output_dir_for_run ,
        'known_names':list (KNOWN_NAMES ),
        'known_names_copy':list (KNOWN_NAMES ),
        'filter_character_list':actual_filters_to_use_for_run ,
        'filter_mode':backend_filter_mode ,
        'skip_zip':effective_skip_zip ,
        'skip_rar':effective_skip_rar ,
        'use_subfolders':use_subfolders ,
        'use_post_subfolders':use_post_subfolders ,
        'compress_images':compress_images ,
        'download_thumbnails':download_thumbnails ,
        'service':service ,
        'user_id':user_id ,
        'downloaded_files':self .downloaded_files ,
        'downloaded_files_lock':self .downloaded_files_lock ,
        'downloaded_file_hashes':self .downloaded_file_hashes ,
        'downloaded_file_hashes_lock':self .downloaded_file_hashes_lock ,
        'skip_words_list':skip_words_list ,
        'skip_words_scope':current_skip_words_scope ,
        'remove_from_filename_words_list':remove_from_filename_words_list ,
        'char_filter_scope':current_char_filter_scope ,
        'show_external_links':self .show_external_links ,
        'extract_links_only':extract_links_only ,
        'start_page':start_page ,
        'end_page':end_page ,
        'target_post_id_from_initial_url':post_id_from_url ,
        'custom_folder_name':custom_folder_name_cleaned ,
        'manga_mode_active':manga_mode ,
        'unwanted_keywords':FOLDER_NAME_STOP_WORDS ,
        'cancellation_event':self .cancellation_event ,
        'manga_date_prefix':manga_date_prefix_text ,
        'dynamic_character_filter_holder':self .dynamic_character_filter_holder ,
        'pause_event':self .pause_event ,
        'scan_content_for_images':scan_content_for_images ,
        'manga_filename_style':self .manga_filename_style ,
        'num_file_threads_for_worker':effective_num_file_threads_per_worker ,
        'manga_date_file_counter_ref':manga_date_file_counter_ref_for_thread ,
        'allow_multipart_download':allow_multipart ,
        'cookie_text':cookie_text_from_input ,
        'selected_cookie_file':selected_cookie_file_path_for_backend ,
        'manga_global_file_counter_ref':manga_global_file_counter_ref_for_thread ,
        'app_base_dir':app_base_dir_for_cookies ,
        'use_cookie':use_cookie_for_this_run ,
        'creator_download_folder_ignore_words':creator_folder_ignore_words_for_run ,
        }

        args_template ['override_output_dir']=override_output_dir 
        try :
            if should_use_multithreading_for_posts :
                self .log_signal .emit (f"    Initializing multi-threaded {current_mode_log_text .lower ()} with {effective_num_post_workers } post workers...")
                args_template ['emitter']=self .worker_to_gui_queue 
                self .start_multi_threaded_download (num_post_workers =effective_num_post_workers ,**args_template )
            else :
                self .log_signal .emit (f"    Initializing single-threaded {'link extraction'if extract_links_only else 'download'}...")
                dt_expected_keys =[
                'api_url_input','output_dir','known_names_copy','cancellation_event',
                'filter_character_list','filter_mode','skip_zip','skip_rar',
                'use_subfolders','use_post_subfolders','custom_folder_name',
                'compress_images','download_thumbnails','service','user_id',
                'downloaded_files','downloaded_file_hashes','pause_event','remove_from_filename_words_list',
                'downloaded_files_lock','downloaded_file_hashes_lock','dynamic_character_filter_holder',
                'skip_words_list','skip_words_scope','char_filter_scope',
                'show_external_links','extract_links_only','num_file_threads_for_worker',
                'start_page','end_page','target_post_id_from_initial_url',
                'manga_date_file_counter_ref',
                'manga_global_file_counter_ref','manga_date_prefix',
                'manga_mode_active','unwanted_keywords','manga_filename_style','scan_content_for_images',
                'allow_multipart_download','use_cookie','cookie_text','app_base_dir','selected_cookie_file','override_output_dir'
                ]
                args_template ['skip_current_file_flag']=None 
                single_thread_args ={key :args_template [key ]for key in dt_expected_keys if key in args_template }
                self .start_single_threaded_download (**single_thread_args )
        except Exception as e :
            self .log_signal .emit (f"❌ CRITICAL ERROR preparing download: {e }\n{traceback .format_exc ()}")
            QMessageBox .critical (self ,"Start Error",f"Failed to start process:\n{e }")
            self .download_finished (0 ,0 ,False ,[])
            if self .pause_event :self .pause_event .clear ()
            self .is_paused =False 
        return True 


    def start_single_threaded_download (self ,**kwargs ):
        global BackendDownloadThread 
        try :
            self .download_thread =BackendDownloadThread (**kwargs )
            if self .pause_event :self .pause_event .clear ()
            self .is_paused =False 
            if hasattr (self .download_thread ,'progress_signal'):self .download_thread .progress_signal .connect (self .handle_main_log )
            if hasattr (self .download_thread ,'add_character_prompt_signal'):self .download_thread .add_character_prompt_signal .connect (self .add_character_prompt_signal )
            if hasattr (self .download_thread ,'finished_signal'):self .download_thread .finished_signal .connect (self .download_finished )
            if hasattr (self .download_thread ,'receive_add_character_result'):self .character_prompt_response_signal .connect (self .download_thread .receive_add_character_result )
            if hasattr (self .download_thread ,'external_link_signal'):self .download_thread .external_link_signal .connect (self .handle_external_link_signal )
            if hasattr (self .download_thread ,'file_progress_signal'):self .download_thread .file_progress_signal .connect (self .update_file_progress_display )
            if hasattr (self .download_thread ,'missed_character_post_signal'):
                self .download_thread .missed_character_post_signal .connect (self .handle_missed_character_post )
            if hasattr (self .download_thread ,'retryable_file_failed_signal'):
                # Connect the new history signal from DownloadThread
                if hasattr(self.download_thread, 'file_successfully_downloaded_signal'): # Connect new signal for actual downloads
                    self.download_thread.file_successfully_downloaded_signal.connect(self._handle_actual_file_downloaded)               
                if hasattr(self.download_thread, 'post_processed_for_history_signal'): # Check if signal exists
                    self.download_thread.post_processed_for_history_signal.connect(self._add_to_history_candidates)               
                self .download_thread .retryable_file_failed_signal .connect (self ._handle_retryable_file_failure )
                if hasattr(self.download_thread, 'permanent_file_failed_signal'): # Ensure this signal exists on BackendDownloadThread
                    self.download_thread.permanent_file_failed_signal.connect(self._handle_permanent_file_failure_from_thread)
            self .download_thread .start ()
            self .log_signal .emit ("✅ Single download thread (for posts) started.")
        except Exception as e :
            self .log_signal .emit (f"❌ CRITICAL ERROR starting single-thread: {e }\n{traceback .format_exc ()}")
            QMessageBox .critical (self ,"Thread Start Error",f"Failed to start download process: {e }")
            if self .pause_event :self .pause_event .clear ()
            self .is_paused =False 

    def _show_error_files_dialog (self ):
        """Shows the dialog with files that were skipped due to errors."""
        if not self .permanently_failed_files_for_dialog :
            QMessageBox .information (
            self ,
            self ._tr ("no_errors_logged_title","No Errors Logged"),
            self ._tr ("no_errors_logged_message","No files were recorded as skipped due to errors in the last session or after retries."))
            return 
        dialog =ErrorFilesDialog (self .permanently_failed_files_for_dialog ,self ,self )
        dialog .retry_selected_signal .connect (self ._handle_retry_from_error_dialog )
        dialog .exec_ ()
    def _handle_retry_from_error_dialog (self ,selected_files_to_retry ):
        self ._start_failed_files_retry_session (files_to_retry_list =selected_files_to_retry )

    def _handle_retryable_file_failure (self ,list_of_retry_details ):
        """Appends details of files that failed but might be retryable later."""
        if list_of_retry_details :
            self .retryable_failed_files_info .extend (list_of_retry_details )

    def _handle_permanent_file_failure_from_thread(self, list_of_permanent_failure_details):
        """Handles permanently failed files signaled by the single BackendDownloadThread."""
        if list_of_permanent_failure_details:
            self.permanently_failed_files_for_dialog.extend(list_of_permanent_failure_details)
            self.log_signal.emit(f"ℹ️ {len(list_of_permanent_failure_details)} file(s) from single-thread download marked as permanently failed for this session.")

    def _submit_post_to_worker_pool (self ,post_data_item ,worker_args_template ,num_file_dl_threads_for_each_worker ,emitter_for_worker ,ppw_expected_keys ,ppw_optional_keys_with_defaults ):
        """Helper to prepare and submit a single post processing task to the thread pool."""
        global PostProcessorWorker 
        if not isinstance (post_data_item ,dict ):
            self .log_signal .emit (f"⚠️ Skipping invalid post data item (not a dict): {type (post_data_item )}");
            return False 

        worker_init_args ={}
        missing_keys =[]
        for key in ppw_expected_keys :
            if key =='post_data':worker_init_args [key ]=post_data_item 
            elif key =='num_file_threads':worker_init_args [key ]=num_file_dl_threads_for_each_worker 
            elif key =='emitter':worker_init_args [key ]=emitter_for_worker 
            elif key in worker_args_template :worker_init_args [key ]=worker_args_template [key ]
            elif key in ppw_optional_keys_with_defaults :pass 
            else :missing_keys .append (key )

        if missing_keys :
            self .log_signal .emit (f"❌ CRITICAL ERROR: Missing keys for PostProcessorWorker: {', '.join (missing_keys )}");
            self .cancellation_event .set ()
            return False 

        try :
            worker_instance =PostProcessorWorker (**worker_init_args )
            if self .thread_pool :
                future =self .thread_pool .submit (worker_instance .process )
                future .add_done_callback (self ._handle_future_result )
                self .active_futures .append (future )
                return True 
            else :
                self .log_signal .emit ("⚠️ Thread pool not available. Cannot submit task.");
                self .cancellation_event .set ()
                return False 
        except TypeError as te :
            self .log_signal .emit (f"❌ TypeError creating PostProcessorWorker: {te }\n    Passed Args: [{', '.join (sorted (worker_init_args .keys ()))}]\n{traceback .format_exc (limit =5 )}")
            self .cancellation_event .set ()
            return False 
        except RuntimeError :
            self .log_signal .emit (f"⚠️ RuntimeError submitting task (pool likely shutting down).")
            self .cancellation_event .set ()
            return False 
        except Exception as e :
            self .log_signal .emit (f"❌ Error submitting post {post_data_item .get ('id','N/A')} to worker: {e }")
            self .cancellation_event .set ()
            return False 

    def start_multi_threaded_download (self ,num_post_workers ,**kwargs ):
        global PostProcessorWorker 
        if self .thread_pool is None :
            if self .pause_event :self .pause_event .clear ()
            self .is_paused =False 
            self .thread_pool =ThreadPoolExecutor (max_workers =num_post_workers ,thread_name_prefix ='PostWorker_')

        self .active_futures =[]
        self .processed_posts_count =0 ;self .total_posts_to_process =0 ;self .download_counter =0 ;self .skip_counter =0 
        self .all_kept_original_filenames =[]
        self .is_fetcher_thread_running =True 

        fetcher_thread =threading .Thread (
        target =self ._fetch_and_queue_posts ,
        args =(kwargs ['api_url_input'],kwargs ,num_post_workers ),
        daemon =True ,
        name ="PostFetcher"
        )
        fetcher_thread .start ()
        self .log_signal .emit (f"✅ Post fetcher thread started. {num_post_workers } post worker threads initializing...")


    def _fetch_and_queue_posts (self ,api_url_input_for_fetcher ,worker_args_template ,num_post_workers ):
        global PostProcessorWorker ,download_from_api 
        all_posts_data =[]
        fetch_error_occurred =False 
        manga_mode_active_for_fetch =worker_args_template .get ('manga_mode_active',False )
        emitter_for_worker =worker_args_template .get ('emitter')
        if not emitter_for_worker :
            self .log_signal .emit ("❌ CRITICAL ERROR: Emitter (queue) missing for worker in _fetch_and_queue_posts.");
            self .finished_signal .emit (0 ,0 ,True ,[]);
            return 

        try :
            self .log_signal .emit ("    Fetching post data from API (this may take a moment for large feeds)...")
            post_generator =download_from_api (
            api_url_input_for_fetcher ,
            logger =lambda msg :self .log_signal .emit (f"[Fetcher] {msg }"),
            start_page =worker_args_template .get ('start_page'),
            end_page =worker_args_template .get ('end_page'),
            manga_mode =manga_mode_active_for_fetch ,
                cancellation_event=self.cancellation_event,
                pause_event=worker_args_template.get('pause_event'),
                use_cookie=worker_args_template.get('use_cookie'),
                cookie_text=worker_args_template.get('cookie_text'),
                selected_cookie_file=worker_args_template.get('selected_cookie_file'),
                app_base_dir=worker_args_template.get('app_base_dir'),
                manga_filename_style_for_sort_check=(
                    worker_args_template.get('manga_filename_style')
                    if manga_mode_active_for_fetch
                        else None
                )
            )

            for posts_batch in post_generator :
                if self .cancellation_event .is_set ():
                    fetch_error_occurred =True ;self .log_signal .emit ("    Post fetching cancelled by user.");break 
                if isinstance (posts_batch ,list ):
                    all_posts_data .extend (posts_batch )
                    self .total_posts_to_process =len (all_posts_data )
                    if self .total_posts_to_process >0 and self .total_posts_to_process %100 ==0 :
                        self .log_signal .emit (f"    Fetched {self .total_posts_to_process } posts so far...")
                else :
                    fetch_error_occurred =True ;self .log_signal .emit (f"❌ API fetcher returned non-list type: {type (posts_batch )}");break 

            if not fetch_error_occurred and not self .cancellation_event .is_set ():
                self .log_signal .emit (f"✅ Post fetching complete. Total posts to process: {self .total_posts_to_process }")
            unique_posts_dict ={}
            for post in all_posts_data :
                post_id =post .get ('id')
                if post_id is not None :
                    if post_id not in unique_posts_dict :
                        unique_posts_dict [post_id ]=post 
                else :
                    self .log_signal .emit (f"⚠️ Skipping post with no ID: {post .get ('title','Untitled')}")

            all_posts_data =list (unique_posts_dict .values ())

            self .total_posts_to_process =len (all_posts_data )
            self .log_signal .emit (f"    Processed {len (unique_posts_dict )} unique posts after de-duplication.")
            if len (unique_posts_dict )<len (all_posts_data ):
                self .log_signal .emit (f"    Note: {len (all_posts_data )-len (unique_posts_dict )} duplicate post IDs were removed.")

        except TypeError as te :
            self .log_signal .emit (f"❌ TypeError calling download_from_api: {te }\n    Check 'downloader_utils.py' signature.\n{traceback .format_exc (limit =2 )}");fetch_error_occurred =True 
        except RuntimeError as re_err :
            self .log_signal .emit (f"ℹ️ Post fetching runtime error (likely cancellation or API issue): {re_err }");fetch_error_occurred =True 
        except Exception as e :
            self .log_signal .emit (f"❌ Error during post fetching: {e }\n{traceback .format_exc (limit =2 )}");fetch_error_occurred =True 

        finally :
            self .is_fetcher_thread_running =False 
            self .log_signal .emit (f"ℹ️ Post fetcher thread (_fetch_and_queue_posts) has completed its task. is_fetcher_thread_running set to False.")

        if self .cancellation_event .is_set ()or fetch_error_occurred :
            self .finished_signal .emit (self .download_counter ,self .skip_counter ,self .cancellation_event .is_set (),self .all_kept_original_filenames )
            if self .thread_pool :self .thread_pool .shutdown (wait =False ,cancel_futures =True );self .thread_pool =None 
            return 

        if self .total_posts_to_process ==0 :
            self .log_signal .emit ("😕 No posts found or fetched to process.")
            self .finished_signal .emit (0 ,0 ,False ,[])
            return 

        self .log_signal .emit (f"    Preparing to submit {self .total_posts_to_process } post processing tasks to thread pool...")
        self .processed_posts_count =0 
        self .overall_progress_signal .emit (self .total_posts_to_process ,0 )

        num_file_dl_threads_for_each_worker =worker_args_template .get ('num_file_threads_for_worker',1 )


        ppw_expected_keys =[
        'post_data','download_root','known_names','filter_character_list','unwanted_keywords',
        'filter_mode','skip_zip','skip_rar','use_subfolders','use_post_subfolders',
        'target_post_id_from_initial_url','custom_folder_name','compress_images','emitter','pause_event',
        'download_thumbnails','service','user_id','api_url_input',
        'cancellation_event','downloaded_files','downloaded_file_hashes',
        'downloaded_files_lock','downloaded_file_hashes_lock','remove_from_filename_words_list','dynamic_character_filter_holder',
        'skip_words_list','skip_words_scope','char_filter_scope',
        'show_external_links','extract_links_only','allow_multipart_download','use_cookie','cookie_text',
        'app_base_dir','selected_cookie_file','override_output_dir',
        'num_file_threads','skip_current_file_flag','manga_date_file_counter_ref','scan_content_for_images',
        'manga_mode_active','manga_filename_style','manga_date_prefix',
        'manga_global_file_counter_ref'
        ,'creator_download_folder_ignore_words'
        ]

        ppw_optional_keys_with_defaults ={
        'skip_words_list','skip_words_scope','char_filter_scope','remove_from_filename_words_list',
        'show_external_links','extract_links_only','duplicate_file_mode',
        'num_file_threads','skip_current_file_flag','manga_mode_active','manga_filename_style','manga_date_prefix',
        'manga_date_file_counter_ref','use_cookie','cookie_text','app_base_dir','selected_cookie_file'
        }
        if num_post_workers >POST_WORKER_BATCH_THRESHOLD and self .total_posts_to_process >POST_WORKER_NUM_BATCHES :
            self .log_signal .emit (f"    High thread count ({num_post_workers }) detected. Batching post submissions into {POST_WORKER_NUM_BATCHES } parts.")

            import math 
            tasks_submitted_in_batch_segment =0 
            batch_size =math .ceil (self .total_posts_to_process /POST_WORKER_NUM_BATCHES )
            submitted_count_in_batching =0 

            for batch_num in range (POST_WORKER_NUM_BATCHES ):
                if self .cancellation_event .is_set ():break 

                if self .pause_event and self .pause_event .is_set ():
                    self .log_signal .emit (f"    [Fetcher] Batch submission paused before batch {batch_num +1 }/{POST_WORKER_NUM_BATCHES }...")
                    while self .pause_event .is_set ():
                        if self .cancellation_event .is_set ():
                            self .log_signal .emit ("    [Fetcher] Batch submission cancelled while paused.")
                            break 
                        time .sleep (0.5 )
                    if self .cancellation_event .is_set ():break 
                    if not self .cancellation_event .is_set ():
                        self .log_signal .emit (f"    [Fetcher] Batch submission resumed. Processing batch {batch_num +1 }/{POST_WORKER_NUM_BATCHES }.")

                start_index =batch_num *batch_size 
                end_index =min ((batch_num +1 )*batch_size ,self .total_posts_to_process )
                current_batch_posts =all_posts_data [start_index :end_index ]

                if not current_batch_posts :continue 

                self .log_signal .emit (f"    Submitting batch {batch_num +1 }/{POST_WORKER_NUM_BATCHES } ({len (current_batch_posts )} posts) to pool...")
                for post_data_item in current_batch_posts :
                    if self .cancellation_event .is_set ():break 
                    success =self ._submit_post_to_worker_pool (post_data_item ,worker_args_template ,num_file_dl_threads_for_each_worker ,emitter_for_worker ,ppw_expected_keys ,ppw_optional_keys_with_defaults )
                    if success :
                        submitted_count_in_batching +=1 
                        tasks_submitted_in_batch_segment +=1 
                        if tasks_submitted_in_batch_segment %10 ==0 :
                            time .sleep (0.005 )
                            tasks_submitted_in_batch_segment =0 
                    elif self .cancellation_event .is_set ():
                        break 

                if self .cancellation_event .is_set ():break 

                if batch_num <POST_WORKER_NUM_BATCHES -1 :
                    self .log_signal .emit (f"    Batch {batch_num +1 } submitted. Waiting {POST_WORKER_BATCH_DELAY_SECONDS }s before next batch...")
                    delay_start_time =time .time ()
                    while time .time ()-delay_start_time <POST_WORKER_BATCH_DELAY_SECONDS :
                        if self .cancellation_event .is_set ():break 
                        time .sleep (0.1 )
                    if self .cancellation_event .is_set ():break 

            self .log_signal .emit (f"    All {POST_WORKER_NUM_BATCHES } batches ({submitted_count_in_batching } total tasks) submitted to pool via batching.")

        else :
            self .log_signal .emit (f"    Submitting all {self .total_posts_to_process } tasks to pool directly...")
            submitted_count_direct =0 
            tasks_submitted_since_last_yield =0 
            for post_data_item in all_posts_data :
                if self .cancellation_event .is_set ():break 
                success =self ._submit_post_to_worker_pool (post_data_item ,worker_args_template ,num_file_dl_threads_for_each_worker ,emitter_for_worker ,ppw_expected_keys ,ppw_optional_keys_with_defaults )
                if success :
                    submitted_count_direct +=1 
                    tasks_submitted_since_last_yield +=1 
                    if tasks_submitted_since_last_yield %10 ==0 :
                        time .sleep (0.005 )
                        tasks_submitted_since_last_yield =0 
                elif self .cancellation_event .is_set ():
                    break 

            if not self .cancellation_event .is_set ():
                self .log_signal .emit (f"    All {submitted_count_direct } post processing tasks submitted directly to pool.")

        if self .cancellation_event .is_set ():
            self .log_signal .emit ("    Cancellation detected after/during task submission loop.")

            if self .external_link_download_thread and self .external_link_download_thread .isRunning ():
                self .mega_download_thread .cancel ()


            self .finished_signal .emit (self .download_counter ,self .skip_counter ,True ,self .all_kept_original_filenames )
            if self .thread_pool :self .thread_pool .shutdown (wait =False ,cancel_futures =True );self .thread_pool =None 

    def _handle_future_result (self ,future :Future ):
        self .processed_posts_count +=1 
        downloaded_files_from_future ,skipped_files_from_future =0 ,0 
        kept_originals_from_future =[]
        try :
            if future .cancelled ():
                if not self .cancellation_message_logged_this_session :
                    self .log_signal .emit ("    A post processing task was cancelled.")
                    self .cancellation_message_logged_this_session =True 
            elif future .exception ():
                self .log_signal .emit (f"❌ Post processing worker error: {future .exception ()}")
            else :
                # unpack the new history_data from the future's result
                result_tuple = future.result()
                downloaded_files_from_future, skipped_files_from_future, \
                kept_originals_from_future, retryable_failures_from_post, \
                permanent_failures_from_post, history_data_from_worker = result_tuple
                if history_data_from_worker: # if worker returned history data
                    self._add_to_history_candidates(history_data_from_worker)
            with self .downloaded_files_lock :
                self .download_counter +=downloaded_files_from_future 
                self .skip_counter +=skipped_files_from_future  # type: ignore

            if kept_originals_from_future :
                self .all_kept_original_filenames .extend (kept_originals_from_future )

            self .overall_progress_signal .emit (self .total_posts_to_process ,self .processed_posts_count )
        except Exception as e :
            self .log_signal .emit (f"❌ Error in _handle_future_result callback: {e }\n{traceback .format_exc (limit =2 )}")
            if self .processed_posts_count <self .total_posts_to_process :
                self .processed_posts_count =self .total_posts_to_process 

        if self .total_posts_to_process >0 and self .processed_posts_count >=self .total_posts_to_process :
            if all (f .done ()for f in self .active_futures ):
                QApplication .processEvents ()
                self .log_signal .emit ("🏁 All submitted post tasks have completed or failed.")
                self .finished_signal .emit (self .download_counter ,self .skip_counter ,self .cancellation_event .is_set (),self .all_kept_original_filenames )

    def _add_to_history_candidates(self, history_data):
        """Adds processed post data to the history candidates list."""
        if history_data and len(self.download_history_candidates) < 8:
            history_data['download_date_timestamp'] = time.time()
            creator_key = (history_data.get('service', '').lower(), str(history_data.get('user_id', '')))
            history_data['creator_name'] = self.creator_name_cache.get(creator_key, history_data.get('user_id', 'Unknown'))
            self.download_history_candidates.append(history_data)

    def _finalize_download_history(self):
        """Processes candidates and selects the final 3 history entries.
        Only updates final_download_history_entries if new candidates are available.
        """
        if not self.download_history_candidates:
            # No new candidates from this session, so don't touch existing
            # final_download_history_entries (which might be from a previous session).
            self.log_signal.emit("ℹ️ No new history candidates from this session. Preserving existing history.")
            # It's important to clear the candidates buffer for the next session,
            # even if we don't use them this time.
            self.download_history_candidates.clear()
            return

        candidates = list(self.download_history_candidates)
        now = datetime.datetime.now(datetime.timezone.utc) # Use timezone-aware now

        def get_sort_key(entry):
            upload_date_str = entry.get('upload_date_str')
            if not upload_date_str:
                return datetime.timedelta.max # Push entries with no date to the end
            try:
                # Attempt to parse ISO format, make it offset-naive if necessary
                upload_dt = datetime.datetime.fromisoformat(upload_date_str.replace('Z', '+00:00'))
                if upload_dt.tzinfo is None: # If still naive, assume UTC
                    upload_dt = upload_dt.replace(tzinfo=datetime.timezone.utc)
                return abs(now - upload_dt)
            except ValueError:
                return datetime.timedelta.max # Push unparseable dates to the end

        candidates.sort(key=get_sort_key)
        self.final_download_history_entries = candidates[:3]
        self.log_signal.emit(f"ℹ️ Finalized download history: {len(self.final_download_history_entries)} entries selected.")
        self.download_history_candidates.clear() # Clear candidates after processing

        # Always save the current state of final_download_history_entries
        self._save_persistent_history() 

    def _get_configurable_widgets_on_pause (self ):
        """Returns a list of widgets that should be re-enabled when paused."""
        return [
        self .dir_input ,self .dir_button ,
        self .character_input ,self .char_filter_scope_toggle_button ,
        self .skip_words_input ,self .skip_scope_toggle_button ,
        self .remove_from_filename_input ,
        self .radio_all ,self .radio_images ,self .radio_videos ,
        self .radio_only_archives ,self .radio_only_links ,
        self .skip_zip_checkbox ,self .skip_rar_checkbox ,
        self .download_thumbnails_checkbox ,self .compress_images_checkbox ,
        self .use_subfolders_checkbox ,self .use_subfolder_per_post_checkbox ,
        self .manga_mode_checkbox ,
        self .manga_rename_toggle_button ,
        self .cookie_browse_button ,
        self .favorite_mode_checkbox ,
        self .multipart_toggle_button ,
        self .cookie_text_input ,
        self .scan_content_images_checkbox ,
        self .use_cookie_checkbox ,
        self .external_links_checkbox 
        ]

    def set_ui_enabled (self ,enabled ):
        all_potentially_toggleable_widgets =[
        self .link_input ,self .dir_input ,self .dir_button ,
        self .page_range_label ,self .start_page_input ,self .to_label ,self .end_page_input ,
        self .character_input ,self .char_filter_scope_toggle_button ,self .character_filter_widget ,
        self .filters_and_custom_folder_container_widget ,
        self .custom_folder_label ,self .custom_folder_input ,
        self .skip_words_input ,self .skip_scope_toggle_button ,self .remove_from_filename_input ,
        self .radio_all ,self .radio_images ,self .radio_videos ,self .radio_only_archives ,self .radio_only_links ,
        self .skip_zip_checkbox ,self .skip_rar_checkbox ,self .download_thumbnails_checkbox ,self .compress_images_checkbox ,
        self .use_subfolders_checkbox ,self .use_subfolder_per_post_checkbox ,self .scan_content_images_checkbox ,
        self .use_multithreading_checkbox ,self .thread_count_input ,self .thread_count_label ,
        self .favorite_mode_checkbox ,
        self .external_links_checkbox ,self .manga_mode_checkbox ,self .manga_rename_toggle_button ,self .use_cookie_checkbox ,self .cookie_text_input ,self .cookie_browse_button ,
        self .multipart_toggle_button ,self .radio_only_audio ,
        self .character_search_input ,self .new_char_input ,self .add_char_button ,self .add_to_filter_button ,self .delete_char_button ,
        self .reset_button 
        ]

        widgets_to_enable_on_pause =self ._get_configurable_widgets_on_pause ()
        is_fav_mode_active =self .favorite_mode_checkbox .isChecked ()if self .favorite_mode_checkbox else False 
        download_is_active_or_paused =not enabled 

        if not enabled :
            if self .bottom_action_buttons_stack :
                self .bottom_action_buttons_stack .setCurrentIndex (0 )

            if self .external_link_download_thread and self .external_link_download_thread .isRunning ():
                self .log_signal .emit ("ℹ️ Cancelling active Mega download due to UI state change.")
                self .external_link_download_thread .cancel ()
        else :
            pass 


        for widget in all_potentially_toggleable_widgets :
            if not widget :continue 


            if widget is self .favorite_mode_artists_button or widget is self .favorite_mode_posts_button :continue 
            elif self .is_paused and widget in widgets_to_enable_on_pause :
                widget .setEnabled (True )
            elif widget is self .favorite_mode_checkbox :
                widget .setEnabled (enabled )
            elif widget is self .use_cookie_checkbox and is_fav_mode_active :
                widget .setEnabled (False )
            elif widget is self .use_cookie_checkbox and self .is_paused and widget in widgets_to_enable_on_pause :
                widget .setEnabled (True )
            else :
                widget .setEnabled (enabled )

        if self .link_input :
            self .link_input .setEnabled (enabled and not is_fav_mode_active )



        if not enabled :
            if self .favorite_mode_artists_button :
                self .favorite_mode_artists_button .setEnabled (False )
            if self .favorite_mode_posts_button :
                self .favorite_mode_posts_button .setEnabled (False )

        if self .download_btn :
            self .download_btn .setEnabled (enabled and not is_fav_mode_active )


        if self .external_links_checkbox :
            is_only_links =self .radio_only_links and self .radio_only_links .isChecked ()
            is_only_archives =self .radio_only_archives and self .radio_only_archives .isChecked ()
            is_only_audio =hasattr (self ,'radio_only_audio')and self .radio_only_audio .isChecked ()
            can_enable_ext_links =enabled and not is_only_links and not is_only_archives and not is_only_audio 
            self .external_links_checkbox .setEnabled (can_enable_ext_links )
            if self .is_paused and not is_only_links and not is_only_archives and not is_only_audio :
                self .external_links_checkbox .setEnabled (True )
        if hasattr (self ,'use_cookie_checkbox'):
            self ._update_cookie_input_visibility (self .use_cookie_checkbox .isChecked ())

        if self .log_verbosity_toggle_button :self .log_verbosity_toggle_button .setEnabled (True )

        multithreading_currently_on =self .use_multithreading_checkbox .isChecked ()
        if self .thread_count_input :self .thread_count_input .setEnabled (enabled and multithreading_currently_on )
        if self .thread_count_label :self .thread_count_label .setEnabled (enabled and multithreading_currently_on )

        subfolders_currently_on =self .use_subfolders_checkbox .isChecked ()
        if self .use_subfolder_per_post_checkbox :
            self .use_subfolder_per_post_checkbox .setEnabled (enabled or (self .is_paused and self .use_subfolder_per_post_checkbox in widgets_to_enable_on_pause ))
        if self .cancel_btn :self .cancel_btn .setEnabled (download_is_active_or_paused )
        if self .pause_btn :
            self .pause_btn .setEnabled (download_is_active_or_paused )
            if download_is_active_or_paused :
                self .pause_btn .setText (self ._tr ("resume_download_button_text","▶️ Resume Download")if self .is_paused else self ._tr ("pause_download_button_text","⏸️ Pause Download"))
                self .pause_btn .setToolTip (self ._tr ("resume_download_button_tooltip","Click to resume the download.")if self .is_paused else self ._tr ("pause_download_button_tooltip","Click to pause the download."))
            else :
                self .pause_btn .setText (self ._tr ("pause_download_button_text","⏸️ Pause Download"))
                self .pause_btn .setToolTip (self ._tr ("pause_download_button_tooltip","Click to pause the ongoing download process."))
                self .is_paused =False 
        if self .cancel_btn :self .cancel_btn .setText (self ._tr ("cancel_button_text","❌ Cancel & Reset UI"))
        if enabled :
            if self .pause_event :self .pause_event .clear ()
        if enabled or self .is_paused :
            self ._handle_multithreading_toggle (multithreading_currently_on )
            self .update_ui_for_manga_mode (self .manga_mode_checkbox .isChecked ()if self .manga_mode_checkbox else False )
            self .update_custom_folder_visibility (self .link_input .text ())
            self .update_page_range_enabled_state ()
            if self .radio_group and self .radio_group .checkedButton ():
                self ._handle_filter_mode_change (self .radio_group .checkedButton (),True )
            self .update_ui_for_subfolders (subfolders_currently_on )
            self ._handle_favorite_mode_toggle (is_fav_mode_active )

    def _handle_pause_resume_action (self ):
        if self ._is_download_active ():
            self .is_paused =not self .is_paused 
            if self .is_paused :
                if self .pause_event :self .pause_event .set ()
                self .log_signal .emit ("ℹ️ Download paused by user. Some settings can now be changed for subsequent operations.")
            else :
                if self .pause_event :self .pause_event .clear ()
                self .log_signal .emit ("ℹ️ Download resumed by user.")
            self .set_ui_enabled (False )

    def _perform_soft_ui_reset (self ,preserve_url =None ,preserve_dir =None ):
        """Resets UI elements and some state to app defaults, then applies preserved inputs."""
        self .log_signal .emit ("🔄 Performing soft UI reset...")
        self .link_input .clear ()
        self .dir_input .clear ()
        self .custom_folder_input .clear ();self .character_input .clear ();
        self .skip_words_input .clear ();self .start_page_input .clear ();self .end_page_input .clear ();self .new_char_input .clear ();
        if hasattr (self ,'remove_from_filename_input'):self .remove_from_filename_input .clear ()
        self .character_search_input .clear ();self .thread_count_input .setText ("4");self .radio_all .setChecked (True );
        self .skip_zip_checkbox .setChecked (True );self .skip_rar_checkbox .setChecked (True );self .download_thumbnails_checkbox .setChecked (False );
        self .compress_images_checkbox .setChecked (False );self .use_subfolders_checkbox .setChecked (True );
        self .use_subfolder_per_post_checkbox .setChecked (False );self .use_multithreading_checkbox .setChecked (True );
        if self .favorite_mode_checkbox :self .favorite_mode_checkbox .setChecked (False )
        if hasattr (self ,'scan_content_images_checkbox'):self .scan_content_images_checkbox .setChecked (False )
        self .external_links_checkbox .setChecked (False )
        if self .manga_mode_checkbox :self .manga_mode_checkbox .setChecked (False )
        if hasattr (self ,'use_cookie_checkbox'):self .use_cookie_checkbox .setChecked (self .use_cookie_setting )
        if not (hasattr (self ,'use_cookie_checkbox')and self .use_cookie_checkbox .isChecked ()):
            self .selected_cookie_filepath =None 
        if hasattr (self ,'cookie_text_input'):self .cookie_text_input .setText (self .cookie_text_setting if self .use_cookie_setting else "")
        self .allow_multipart_download_setting =False 
        self ._update_multipart_toggle_button_text ()

        self .skip_words_scope =SKIP_SCOPE_POSTS 
        self ._update_skip_scope_button_text ()

        if hasattr (self ,'manga_date_prefix_input'):self .manga_date_prefix_input .clear ()

        self .char_filter_scope =CHAR_SCOPE_TITLE 
        self ._update_char_filter_scope_button_text ()

        self .manga_filename_style =STYLE_POST_TITLE 
        self ._update_manga_filename_style_button_text ()
        if preserve_url is not None :
            self .link_input .setText (preserve_url )
        if preserve_dir is not None :
            self .dir_input .setText (preserve_dir )
        self .external_link_queue .clear ();self .extracted_links_cache =[]
        self ._is_processing_external_link_queue =False ;self ._current_link_post_title =None 
        if self .pause_event :self .pause_event .clear ()
        self .total_posts_to_process =0 ;self .processed_posts_count =0 
        self .download_counter =0 ;self .skip_counter =0 
        self .all_kept_original_filenames =[]
        self .is_paused =False 
        self ._handle_multithreading_toggle (self .use_multithreading_checkbox .isChecked ())
        self .favorite_download_queue .clear ()
        self .is_processing_favorites_queue =False 

        self .only_links_log_display_mode =LOG_DISPLAY_LINKS 

        if hasattr (self ,'link_input'):
            if self .download_extracted_links_button :
                self .download_extracted_links_button .setEnabled (False )

            self .last_link_input_text_for_queue_sync =self .link_input .text ()
        self .permanently_failed_files_for_dialog .clear ()
        self .filter_character_list (self .character_search_input .text ())
        self .favorite_download_scope =FAVORITE_SCOPE_SELECTED_LOCATION 
        self ._update_favorite_scope_button_text ()

        self .set_ui_enabled (True )
        self .update_custom_folder_visibility (self .link_input .text ())
        self .update_page_range_enabled_state ()
        self ._update_cookie_input_visibility (self .use_cookie_checkbox .isChecked ()if hasattr (self ,'use_cookie_checkbox')else False )
        if hasattr (self ,'favorite_mode_checkbox'):
            self ._handle_favorite_mode_toggle (False )

        self .log_signal .emit ("✅ Soft UI reset complete. Preserved URL and Directory (if provided).")

    def _update_log_display_mode_button_text (self ):
        if hasattr (self ,'log_display_mode_toggle_button'):
            if self .only_links_log_display_mode ==LOG_DISPLAY_LINKS :
                self .log_display_mode_toggle_button .setText (self ._tr ("log_display_mode_links_view_text","🔗 Links View"))
                self .log_display_mode_toggle_button .setToolTip (
                "Current View: Extracted Links.\n"
                "After Mega download, Mega log is shown THEN links are appended.\n"
                "Click to switch to 'Download Progress View'."
                )
            else :
                self .log_display_mode_toggle_button .setText (self ._tr ("log_display_mode_progress_view_text","⬇️ Progress View"))
                self .log_display_mode_toggle_button .setToolTip (
                "Current View: Mega Download Progress.\n"
                "After Mega download, ONLY Mega log is shown (links hidden).\n"
                "Click to switch to 'Extracted Links View'."
                )

    def _toggle_log_display_mode (self ):
        self .only_links_log_display_mode =LOG_DISPLAY_DOWNLOAD_PROGRESS if self .only_links_log_display_mode ==LOG_DISPLAY_LINKS else LOG_DISPLAY_LINKS 
        self ._update_log_display_mode_button_text ()
        self ._filter_links_log ()

    def cancel_download_button_action (self ):
        if not self .cancel_btn .isEnabled ()and not self .cancellation_event .is_set ():self .log_signal .emit ("ℹ️ No active download to cancel or already cancelling.");return 
        self .log_signal .emit ("⚠️ Requesting cancellation of download process (soft reset)...")

        if self .external_link_download_thread and self .external_link_download_thread .isRunning ():
            self .log_signal .emit ("    Cancelling active External Link download thread...")
            self .external_link_download_thread .cancel ()

        current_url =self .link_input .text ()
        current_dir =self .dir_input .text ()

        self .cancellation_event .set ()
        self .is_fetcher_thread_running =False 
        if self .download_thread and self .download_thread .isRunning ():self .download_thread .requestInterruption ();self .log_signal .emit ("    Signaled single download thread to interrupt.")
        if self .thread_pool :
            self .log_signal .emit ("    Initiating non-blocking shutdown and cancellation of worker pool tasks...")
            self .thread_pool .shutdown (wait =False ,cancel_futures =True )
            self .thread_pool =None 
            self .active_futures =[]

        self .external_link_queue .clear ();self ._is_processing_external_link_queue =False ;self ._current_link_post_title =None 

        self ._perform_soft_ui_reset (preserve_url =current_url ,preserve_dir =current_dir )

        self .progress_label .setText (f"{self ._tr ('status_cancelled_by_user','Cancelled by user')}. {self ._tr ('ready_for_new_task_text','Ready for new task.')}")
        self .file_progress_label .setText ("")
        if self .pause_event :self .pause_event .clear ()
        self .log_signal .emit ("ℹ️ UI reset. Ready for new operation. Background tasks are being terminated.")
        self .is_paused =False 
        if hasattr (self ,'retryable_failed_files_info')and self .retryable_failed_files_info :
            self .log_signal .emit (f"    Discarding {len (self .retryable_failed_files_info )} pending retryable file(s) due to cancellation.")
            self .cancellation_message_logged_this_session =False 
            self .retryable_failed_files_info .clear ()
        self .favorite_download_queue .clear ()
        self .permanently_failed_files_for_dialog .clear ()
        self .is_processing_favorites_queue =False 
        self .favorite_download_scope =FAVORITE_SCOPE_SELECTED_LOCATION 
        self ._update_favorite_scope_button_text ()
        if hasattr (self ,'link_input'):
            self .last_link_input_text_for_queue_sync =self .link_input .text ()
        self .cancellation_message_logged_this_session =False 

    def _get_domain_for_service(self, service_name: str) -> str:
        """Determines the base domain for a given service."""
        if not isinstance(service_name, str): # Basic type check
            return "kemono.su" # Default fallback
        service_lower = service_name.lower()
        coomer_primary_services = {'onlyfans', 'fansly', 'manyvids', 'candfans', 'gumroad', 'patreon', 'subscribestar', 'dlsite', 'discord', 'fantia', 'boosty', 'pixiv', 'fanbox'} # Added more from your general usage
        if service_lower in coomer_primary_services and service_lower not in ['patreon', 'discord', 'fantia', 'boosty', 'pixiv', 'fanbox']: # Explicitly keep these on kemono
            return "coomer.su"
        return "kemono.su"

    def download_finished (self ,total_downloaded ,total_skipped ,cancelled_by_user ,kept_original_names_list =None ):
        if kept_original_names_list is None :
            kept_original_names_list =list (self .all_kept_original_filenames )if hasattr (self ,'all_kept_original_filenames')else []
        if kept_original_names_list is None :
            kept_original_names_list =[]

        self._finalize_download_history() # Finalize history before UI updates
        status_message =self ._tr ("status_cancelled_by_user","Cancelled by user")if cancelled_by_user else self ._tr ("status_completed","Completed")
        if cancelled_by_user and self .retryable_failed_files_info :
            self .log_signal .emit (f"    Download cancelled, discarding {len (self .retryable_failed_files_info )} file(s) that were pending retry.")
            self .retryable_failed_files_info .clear ()

        summary_log ="="*40 
        summary_log +=f"\n🏁 Download {status_message }!\n    Summary: Downloaded Files={total_downloaded }, Skipped Files={total_skipped }\n"
        summary_log +="="*40 
        self .log_signal .emit (summary_log )

        if kept_original_names_list :
            intro_msg =(
            HTML_PREFIX +
            "<p>ℹ️ The following files from multi-file manga posts "
            "(after the first file) kept their <b>original names</b>:</p>"
            )
            self .log_signal .emit (intro_msg )

            html_list_items ="<ul>"
            for name in kept_original_names_list :
                html_list_items +=f"<li><b>{name }</b></li>"
            html_list_items +="</ul>"

            self .log_signal .emit (HTML_PREFIX +html_list_items )
            self .log_signal .emit ("="*40 )

        if self .download_thread :
            try :
                if hasattr (self .download_thread ,'progress_signal'):self .download_thread .progress_signal .disconnect (self .handle_main_log )
                if hasattr (self .download_thread ,'add_character_prompt_signal'):self .download_thread .add_character_prompt_signal .disconnect (self .add_character_prompt_signal )
                if hasattr (self .download_thread ,'finished_signal'):self .download_thread .finished_signal .disconnect (self .download_finished )
                if hasattr (self .download_thread ,'receive_add_character_result'):self .character_prompt_response_signal .disconnect (self .download_thread .receive_add_character_result )
                if hasattr (self .download_thread ,'external_link_signal'):self .download_thread .external_link_signal .disconnect (self .handle_external_link_signal )
                if hasattr (self .download_thread ,'file_progress_signal'):self .download_thread .file_progress_signal .disconnect (self .update_file_progress_display )
                if hasattr (self .download_thread ,'missed_character_post_signal'):
                    self .download_thread .missed_character_post_signal .disconnect (self .handle_missed_character_post )
                if hasattr (self .download_thread ,'retryable_file_failed_signal'):
                    self .download_thread .retryable_file_failed_signal .disconnect (self ._handle_retryable_file_failure )
                if hasattr(self.download_thread, 'file_successfully_downloaded_signal'): # Disconnect new signal
                    self.download_thread.file_successfully_downloaded_signal.disconnect(self._handle_actual_file_downloaded)              
                if hasattr(self.download_thread, 'post_processed_for_history_signal'): # Disconnect new signal
                    self.download_thread.post_processed_for_history_signal.disconnect(self._add_to_history_candidates)          
            except (TypeError ,RuntimeError )as e :
                self .log_signal .emit (f"ℹ️ Note during single-thread signal disconnection: {e }")

            if not self .download_thread .isRunning ():

                if self .download_thread :
                    self .download_thread .deleteLater ()
                self .download_thread =None 

        self .progress_label .setText (
        f"{status_message }: "
        f"{total_downloaded } {self ._tr ('files_downloaded_label','downloaded')}, "
        f"{total_skipped } {self ._tr ('files_skipped_label','skipped')}."
        )
        self .file_progress_label .setText ("")
        if not cancelled_by_user :self ._try_process_next_external_link ()

        if self .thread_pool :
            self .log_signal .emit ("    Ensuring worker thread pool is shut down...")
            self .thread_pool .shutdown (wait =True ,cancel_futures =True )
            self .thread_pool =None 

        self .active_futures =[]
        if self .pause_event :self .pause_event .clear ()
        self .cancel_btn .setEnabled (False )
        self .is_paused =False 
        if not cancelled_by_user and self .retryable_failed_files_info :
            num_failed =len (self .retryable_failed_files_info )
            reply =QMessageBox .question (self ,"Retry Failed Downloads?",
            f"{num_failed } file(s) failed with potentially recoverable errors (e.g., IncompleteRead).\n\n"
            "Would you like to attempt to download these failed files again?",
            QMessageBox .Yes |QMessageBox .No ,QMessageBox .Yes )
            if reply ==QMessageBox .Yes :
                self ._start_failed_files_retry_session ()
                return 
            else :
                self .log_signal .emit ("ℹ️ User chose not to retry failed files.")
                self .permanently_failed_files_for_dialog .extend (self .retryable_failed_files_info )
                if self .permanently_failed_files_for_dialog :
                    self .log_signal .emit (f"🆘 Error button enabled. {len (self .permanently_failed_files_for_dialog )} file(s) can be viewed.")
                self .cancellation_message_logged_this_session =False 
                self .retryable_failed_files_info .clear ()

        self .is_fetcher_thread_running =False 

        if self .is_processing_favorites_queue :
            if not self .favorite_download_queue :
                self .is_processing_favorites_queue =False 
                self .log_signal .emit (f"✅ All {self .current_processing_favorite_item_info .get ('type','item')} downloads from favorite queue have been processed.")
                self .set_ui_enabled (not self ._is_download_active ())
            else :
                self ._process_next_favorite_download ()
        else :
            self .set_ui_enabled (True )
        self .cancellation_message_logged_this_session =False 

    def _handle_thumbnail_mode_change (self ,thumbnails_checked ):
        """Handles UI changes when 'Download Thumbnails Only' is toggled."""
        if not hasattr (self ,'scan_content_images_checkbox'):
            return 

        if thumbnails_checked :
            self .scan_content_images_checkbox .setChecked (True )
            self .scan_content_images_checkbox .setEnabled (False )
            self .scan_content_images_checkbox .setToolTip (
            "Automatically enabled and locked because 'Download Thumbnails Only' is active.\n"
            "In this mode, only images found by content scanning will be downloaded."
            )
        else :
            self .scan_content_images_checkbox .setEnabled (True )
            self .scan_content_images_checkbox .setChecked (False )
            self .scan_content_images_checkbox .setToolTip (self ._original_scan_content_tooltip )

    def _start_failed_files_retry_session (self ,files_to_retry_list =None ):
        if files_to_retry_list :
            self .files_for_current_retry_session =list (files_to_retry_list )
            self .permanently_failed_files_for_dialog =[f for f in self .permanently_failed_files_for_dialog if f not in files_to_retry_list ]
        else :
            self .files_for_current_retry_session =list (self .retryable_failed_files_info )
            self .retryable_failed_files_info .clear ()
        self .log_signal .emit (f"🔄 Starting retry session for {len (self .files_for_current_retry_session )} file(s)...")
        self .set_ui_enabled (False )
        if self .cancel_btn :self .cancel_btn .setText (self ._tr ("cancel_retry_button_text","❌ Cancel Retry"))


        self .active_retry_futures =[]
        self .processed_retry_count =0 
        self .succeeded_retry_count =0 
        self .failed_retry_count_in_session =0 
        self .total_files_for_retry =len (self .files_for_current_retry_session )
        self .active_retry_futures_map ={}

        self .progress_label .setText (self ._tr ("progress_posts_text","Progress: {processed_posts} / {total_posts} posts ({progress_percent:.1f}%)").format (processed_posts =0 ,total_posts =self .total_files_for_retry ,progress_percent =0.0 ).replace ("posts","files"))
        self .cancellation_event .clear ()

        num_retry_threads =1 
        try :
            num_threads_from_gui =int (self .thread_count_input .text ().strip ())
            num_retry_threads =max (1 ,min (num_threads_from_gui ,MAX_FILE_THREADS_PER_POST_OR_WORKER ,self .total_files_for_retry if self .total_files_for_retry >0 else 1 ))
        except ValueError :
            num_retry_threads =1 

        self .retry_thread_pool =ThreadPoolExecutor (max_workers =num_retry_threads ,thread_name_prefix ='RetryFile_')
        common_ppw_args_for_retry ={
        'download_root':self .dir_input .text ().strip (),
        'known_names':list (KNOWN_NAMES ),
        'emitter':self .worker_to_gui_queue ,
        'unwanted_keywords':{'spicy','hd','nsfw','4k','preview','teaser','clip'},
        'filter_mode':self .get_filter_mode (),
        'skip_zip':self .skip_zip_checkbox .isChecked (),
        'skip_rar':self .skip_rar_checkbox .isChecked (),
        'use_subfolders':self .use_subfolders_checkbox .isChecked (),
        'use_post_subfolders':self .use_subfolder_per_post_checkbox .isChecked (),
        'compress_images':self .compress_images_checkbox .isChecked (),
        'download_thumbnails':self .download_thumbnails_checkbox .isChecked (),
        'pause_event':self .pause_event ,
        'cancellation_event':self .cancellation_event ,
        'downloaded_files':self .downloaded_files ,
        'downloaded_file_hashes':self .downloaded_file_hashes ,
        'downloaded_files_lock':self .downloaded_files_lock ,
        'downloaded_file_hashes_lock':self .downloaded_file_hashes_lock ,
        'skip_words_list':[word .strip ().lower ()for word in self .skip_words_input .text ().strip ().split (',')if word .strip ()],
        'skip_words_scope':self .get_skip_words_scope (),
        'char_filter_scope':self .get_char_filter_scope (),
        'remove_from_filename_words_list':[word .strip ()for word in self .remove_from_filename_input .text ().strip ().split (',')if word .strip ()]if hasattr (self ,'remove_from_filename_input')else [],
        'allow_multipart_download':self .allow_multipart_download_setting ,
        'filter_character_list':None ,
        'dynamic_character_filter_holder':None ,
        'target_post_id_from_initial_url':None ,
        'custom_folder_name':None ,
        'num_file_threads':1 ,
        'manga_date_file_counter_ref':None ,
        }

        for job_details in self .files_for_current_retry_session :
            future =self .retry_thread_pool .submit (self ._execute_single_file_retry ,job_details ,common_ppw_args_for_retry )
            future .add_done_callback (self ._handle_retry_future_result )
            self .active_retry_futures_map [future ]=job_details 
            self .active_retry_futures .append (future )

    def _execute_single_file_retry (self ,job_details ,common_args ):
        """Executes a single file download retry attempt."""
        dummy_post_data ={'id':job_details ['original_post_id_for_log'],'title':job_details ['post_title']}

        ppw_init_args ={
        **common_args ,
        'post_data':dummy_post_data ,
        'service':job_details .get ('service','unknown_service'),
        'user_id':job_details .get ('user_id','unknown_user'),
        'api_url_input':job_details .get ('api_url_input',''),
        'manga_mode_active':job_details .get ('manga_mode_active_for_file',False ),
        'manga_filename_style':job_details .get ('manga_filename_style_for_file',STYLE_POST_TITLE ),
        'scan_content_for_images':common_args .get ('scan_content_for_images',False ),
        'use_cookie':common_args .get ('use_cookie',False ),
        'cookie_text':common_args .get ('cookie_text',""),
        'selected_cookie_file':common_args .get ('selected_cookie_file',None ),
        'app_base_dir':common_args .get ('app_base_dir',None ),
        }
        worker =PostProcessorWorker (**ppw_init_args )

        dl_count ,skip_count ,filename_saved ,original_kept ,status ,_ =worker ._download_single_file (
        file_info =job_details ['file_info'],
        target_folder_path =job_details ['target_folder_path'],
        headers =job_details ['headers'],
        original_post_id_for_log =job_details ['original_post_id_for_log'],
        skip_event =None ,
        post_title =job_details ['post_title'],
        file_index_in_post =job_details ['file_index_in_post'],
        num_files_in_this_post =job_details ['num_files_in_this_post'],
        forced_filename_override =job_details .get ('forced_filename_override')
        )



        is_successful_download =(status ==FILE_DOWNLOAD_STATUS_SUCCESS )
        is_resolved_as_skipped =(status ==FILE_DOWNLOAD_STATUS_SKIPPED )

        return is_successful_download or is_resolved_as_skipped 

    def _handle_retry_future_result (self ,future ):
        self .processed_retry_count +=1 
        was_successful =False 
        try :
            if future .cancelled ():
                self .log_signal .emit ("    A retry task was cancelled.")
            elif future .exception ():
                self .log_signal .emit (f"❌ Retry task worker error: {future .exception ()}")
            else :
                was_successful =future .result ()
                job_details =self .active_retry_futures_map .pop (future ,None )
                if was_successful :
                    self .succeeded_retry_count +=1 
                else :
                    self .failed_retry_count_in_session +=1 
                    if job_details :
                        self .permanently_failed_files_for_dialog .append (job_details )
        except Exception as e :
            self .log_signal .emit (f"❌ Error in _handle_retry_future_result: {e }")
            self .failed_retry_count_in_session +=1 

        progress_percent_retry =(self .processed_retry_count /self .total_files_for_retry *100 )if self .total_files_for_retry >0 else 0 
        self .progress_label .setText (
        self ._tr ("progress_posts_text","Progress: {processed_posts} / {total_posts} posts ({progress_percent:.1f}%)").format (processed_posts =self .processed_retry_count ,total_posts =self .total_files_for_retry ,progress_percent =progress_percent_retry ).replace ("posts","files")+
        f" ({self ._tr ('succeeded_text','Succeeded')}: {self .succeeded_retry_count }, {self ._tr ('failed_text','Failed')}: {self .failed_retry_count_in_session })"
        )

        if self .processed_retry_count >=self .total_files_for_retry :
            if all (f .done ()for f in self .active_retry_futures ):
                QTimer .singleShot (0 ,self ._retry_session_finished )


    def _retry_session_finished (self ):
        self .log_signal .emit ("🏁 Retry session finished.")
        self .log_signal .emit (f"    Summary: {self .succeeded_retry_count } Succeeded, {self .failed_retry_count_in_session } Failed.")

        if self .retry_thread_pool :
            self .retry_thread_pool .shutdown (wait =True )
            self .retry_thread_pool =None 

        if self .external_link_download_thread and not self .external_link_download_thread .isRunning ():
            self .external_link_download_thread .deleteLater ()
            self .external_link_download_thread =None 

        self .active_retry_futures .clear ()
        self .active_retry_futures_map .clear ()
        self .files_for_current_retry_session .clear ()

        if self .permanently_failed_files_for_dialog :
            self .log_signal .emit (f"🆘 {self ._tr ('error_button_text','Error')} button enabled. {len (self .permanently_failed_files_for_dialog )} file(s) ultimately failed and can be viewed.")

        self .set_ui_enabled (not self ._is_download_active ())
        if self .cancel_btn :self .cancel_btn .setText (self ._tr ("cancel_button_text","❌ Cancel & Reset UI"))
        self .progress_label .setText (
        f"{self ._tr ('retry_finished_text','Retry Finished')}. "
        f"{self ._tr ('succeeded_text','Succeeded')}: {self .succeeded_retry_count }, "
        f"{self ._tr ('failed_text','Failed')}: {self .failed_retry_count_in_session }. "
        f"{self ._tr ('ready_for_new_task_text','Ready for new task.')}")
        self .file_progress_label .setText ("")
        if self .pause_event :self .pause_event .clear ()
        self .is_paused =False 

    def toggle_active_log_view (self ):
        if self .current_log_view =='progress':
            self .current_log_view ='missed_character'
            if self .log_view_stack :self .log_view_stack .setCurrentIndex (1 )
            if self .log_verbosity_toggle_button :
                self .log_verbosity_toggle_button .setText (self .CLOSED_EYE_ICON )
                self .log_verbosity_toggle_button .setToolTip ("Current View: Missed Character Log. Click to switch to Progress Log.")
            if self .progress_log_label :self .progress_log_label .setText (self ._tr ("missed_character_log_label_text","🚫 Missed Character Log:"))
        else :
            self .current_log_view ='progress'
            if self .log_view_stack :self .log_view_stack .setCurrentIndex (0 )
            if self .log_verbosity_toggle_button :
                self .log_verbosity_toggle_button .setText (self .EYE_ICON )
                self .log_verbosity_toggle_button .setToolTip ("Current View: Progress Log. Click to switch to Missed Character Log.")
            if self .progress_log_label :self .progress_log_label .setText (self ._tr ("progress_log_label_text","📜 Progress Log:"))

    def reset_application_state (self ):
        if self ._is_download_active ():QMessageBox .warning (self ,"Reset Error","Cannot reset while a download is in progress. Please cancel first.");return 
        self .log_signal .emit ("🔄 Resetting application state to defaults...");self ._reset_ui_to_defaults ()
        self .main_log_output .clear ();self .external_log_output .clear ()
        if self .missed_character_log_output :self .missed_character_log_output .clear ()

        self .current_log_view ='progress'
        if self .log_view_stack :self .log_view_stack .setCurrentIndex (0 )
        if self .progress_log_label :self .progress_log_label .setText (self ._tr ("progress_log_label_text","📜 Progress Log:"))
        if self .log_verbosity_toggle_button :
            self .log_verbosity_toggle_button .setText (self .EYE_ICON )
            self .log_verbosity_toggle_button .setToolTip ("Current View: Progress Log. Click to switch to Missed Character Log.")

        if self .show_external_links and not (self .radio_only_links and self .radio_only_links .isChecked ()):self .external_log_output .append ("🔗 External Links Found:")
        self .external_link_queue .clear ();self .extracted_links_cache =[];self ._is_processing_external_link_queue =False ;self ._current_link_post_title =None 
        self .progress_label .setText (self ._tr ("progress_idle_text","Progress: Idle"));self .file_progress_label .setText ("")
        with self .downloaded_files_lock :count =len (self .downloaded_files );self .downloaded_files .clear ();
        self .missed_title_key_terms_count .clear ()
        self .missed_title_key_terms_examples .clear ()
        self .logged_summary_for_key_term .clear ()
        self .already_logged_bold_key_terms .clear ()
        self .missed_key_terms_buffer .clear ()
        self .favorite_download_queue .clear ()
        self .only_links_log_display_mode =LOG_DISPLAY_LINKS 
        self .mega_download_log_preserved_once =False 
        self .permanently_failed_files_for_dialog .clear ()
        self .favorite_download_scope =FAVORITE_SCOPE_SELECTED_LOCATION 
        self ._update_favorite_scope_button_text ()
        self .retryable_failed_files_info .clear ()
        self .cancellation_message_logged_this_session =False 
        self .is_processing_favorites_queue =False 

        if count >0 :self .log_signal .emit (f"    Cleared {count } downloaded filename(s) from session memory.")
        with self .downloaded_file_hashes_lock :count =len (self .downloaded_file_hashes );self .downloaded_file_hashes .clear ();
        if count >0 :self .log_signal .emit (f"    Cleared {count } downloaded file hash(es) from session memory.")

        self .total_posts_to_process =0 ;self .processed_posts_count =0 ;self .download_counter =0 ;self .skip_counter =0 
        self .all_kept_original_filenames =[]
        self .cancellation_event .clear ()
        if self .pause_event :self .pause_event .clear ()
        self .is_paused =False 
        self .manga_filename_style =STYLE_POST_TITLE 
        self .settings .setValue (MANGA_FILENAME_STYLE_KEY ,self .manga_filename_style )

        self .skip_words_scope =SKIP_SCOPE_POSTS 
        self .settings .setValue (SKIP_WORDS_SCOPE_KEY ,self .skip_words_scope )
        self ._update_skip_scope_button_text ()

        self .char_filter_scope =CHAR_SCOPE_TITLE 
        self ._update_char_filter_scope_button_text ()

        self .settings .sync ()
        self ._update_manga_filename_style_button_text ()
        self .update_ui_for_manga_mode (self .manga_mode_checkbox .isChecked ()if self .manga_mode_checkbox else False )

    def _reset_ui_to_defaults (self ):
        self .link_input .clear ();self .dir_input .clear ();self .custom_folder_input .clear ();self .character_input .clear ();
        self .skip_words_input .clear ();self .start_page_input .clear ();self .end_page_input .clear ();self .new_char_input .clear ();
        if hasattr (self ,'remove_from_filename_input'):self .remove_from_filename_input .clear ()
        self .character_search_input .clear ();self .thread_count_input .setText ("4");self .radio_all .setChecked (True );
        self .skip_zip_checkbox .setChecked (True );self .skip_rar_checkbox .setChecked (True );self .download_thumbnails_checkbox .setChecked (False );
        self .compress_images_checkbox .setChecked (False );self .use_subfolders_checkbox .setChecked (True );
        self .use_subfolder_per_post_checkbox .setChecked (False );self .use_multithreading_checkbox .setChecked (True );
        if self .favorite_mode_checkbox :self .favorite_mode_checkbox .setChecked (False )
        self .external_links_checkbox .setChecked (False )
        if self .manga_mode_checkbox :self .manga_mode_checkbox .setChecked (False )
        if hasattr (self ,'use_cookie_checkbox'):self .use_cookie_checkbox .setChecked (False )
        self .selected_cookie_filepath =None 

        if hasattr (self ,'cookie_text_input'):self .cookie_text_input .clear ()
        self .missed_title_key_terms_count .clear ()
        self .missed_title_key_terms_examples .clear ()
        self .logged_summary_for_key_term .clear ()
        self .already_logged_bold_key_terms .clear ()
        if hasattr (self ,'manga_date_prefix_input'):self .manga_date_prefix_input .clear ()
        if self .pause_event :self .pause_event .clear ()
        self .is_paused =False 
        self .missed_key_terms_buffer .clear ()
        if self .download_extracted_links_button :
            self .only_links_log_display_mode =LOG_DISPLAY_LINKS 
            self .cancellation_message_logged_this_session =False 
            self .mega_download_log_preserved_once =False 
            self .download_extracted_links_button .setEnabled (False )

        if self .missed_character_log_output :self .missed_character_log_output .clear ()

        self .permanently_failed_files_for_dialog .clear ()
        self .allow_multipart_download_setting =False 
        self ._update_multipart_toggle_button_text ()

        self .skip_words_scope =SKIP_SCOPE_POSTS 
        self ._update_skip_scope_button_text ()
        self .char_filter_scope =CHAR_SCOPE_TITLE 
        self ._update_char_filter_scope_button_text ()

        self .current_log_view ='progress'
        self ._update_cookie_input_visibility (False );self ._update_cookie_input_placeholders_and_tooltips ()
        if self .log_view_stack :self .log_view_stack .setCurrentIndex (0 )
        if self .progress_log_label :self .progress_log_label .setText ("📜 Progress Log:")
        if self .progress_log_label :self .progress_log_label .setText (self ._tr ("progress_log_label_text","📜 Progress Log:"))
        self ._handle_filter_mode_change (self .radio_all ,True )
        self ._handle_multithreading_toggle (self .use_multithreading_checkbox .isChecked ())
        self .filter_character_list ("")

        self .download_btn .setEnabled (True );self .cancel_btn .setEnabled (False )
        if self .reset_button :self .reset_button .setEnabled (True );self .reset_button .setText (self ._tr ("reset_button_text","🔄 Reset"));self .reset_button .setToolTip (self ._tr ("reset_button_tooltip","Reset all inputs and logs to default state (only when idle)."))
        if self .log_verbosity_toggle_button :
            self .log_verbosity_toggle_button .setText (self .EYE_ICON )
            self .log_verbosity_toggle_button .setToolTip ("Current View: Progress Log. Click to switch to Missed Character Log.")
        self ._update_manga_filename_style_button_text ()
        self .update_ui_for_manga_mode (False )
        if hasattr (self ,'favorite_mode_checkbox'):
            self ._handle_favorite_mode_toggle (False )
        if hasattr (self ,'scan_content_images_checkbox'):
            self .scan_content_images_checkbox .setChecked (False )
        if hasattr (self ,'download_thumbnails_checkbox'):
            self ._handle_thumbnail_mode_change (self .download_thumbnails_checkbox .isChecked ())

    def _show_feature_guide (self ):
        steps_content_keys =[
        ("help_guide_step1_title","help_guide_step1_content"),
        ("help_guide_step2_title","help_guide_step2_content"),
        ("help_guide_step3_title","help_guide_step3_content"),
        ("help_guide_step4_title","help_guide_step4_content"),
        ("help_guide_step5_title","help_guide_step5_content"),
        ("help_guide_step6_title","help_guide_step6_content"),
        ("help_guide_step7_title","help_guide_step7_content"),
        ("help_guide_step8_title","help_guide_step8_content"),
        ("help_guide_step9_title","help_guide_step9_content"),
        ("column_header_post_title", "Post Title"), # For EmptyPopupDialog
        ("column_header_date_uploaded", "Date Uploaded"), # For EmptyPopupDialog
        ]

        steps =[
        ]
        for title_key ,content_key in steps_content_keys :
            title =self ._tr (title_key ,title_key )
            content =self ._tr (content_key ,f"Content for {content_key } not found.")
            steps .append ((title ,content ))

        guide_dialog =HelpGuideDialog (steps ,self )
        guide_dialog .exec_ ()

    def prompt_add_character (self ,character_name ):
        global KNOWN_NAMES 
        reply =QMessageBox .question (self ,"Add Filter Name to Known List?",f"The name '{character_name }' was encountered or used as a filter.\nIt's not in your known names list (used for folder suggestions).\nAdd it now?",QMessageBox .Yes |QMessageBox .No ,QMessageBox .Yes )
        result =(reply ==QMessageBox .Yes )
        if result :
            if self .add_new_character (name_to_add =character_name ,
            is_group_to_add =False ,
            aliases_to_add =[character_name ],
            suppress_similarity_prompt =False ):
                self .log_signal .emit (f"✅ Added '{character_name }' to known names via background prompt.")
            else :result =False ;self .log_signal .emit (f"ℹ️ Adding '{character_name }' via background prompt was declined, failed, or a similar name conflict was not overridden.")
        self .character_prompt_response_signal .emit (result )

    def receive_add_character_result (self ,result ):
        with QMutexLocker (self .prompt_mutex ):self ._add_character_response =result 
        self .log_signal .emit (f"    Main thread received character prompt response: {'Action resulted in addition/confirmation'if result else 'Action resulted in no addition/declined'}")

    def _update_multipart_toggle_button_text (self ):
        if hasattr (self ,'multipart_toggle_button'):
            if self .allow_multipart_download_setting :
                self .multipart_toggle_button .setText (self ._tr ("multipart_on_button_text","Multi-part: ON"))
                self .multipart_toggle_button .setToolTip (self ._tr ("multipart_on_button_tooltip","Tooltip for multipart ON"))
            else :
                self .multipart_toggle_button .setText (self ._tr ("multipart_off_button_text","Multi-part: OFF"))
                self .multipart_toggle_button .setToolTip (self ._tr ("multipart_off_button_tooltip","Tooltip for multipart OFF"))

    def _toggle_multipart_mode (self ):
        if not self .allow_multipart_download_setting :
            msg_box =QMessageBox (self )
            msg_box .setIcon (QMessageBox .Warning )
            msg_box .setWindowTitle ("Multi-part Download Advisory")
            msg_box .setText (
            "<b>Multi-part download advisory:</b><br><br>"
            "<ul>"
            "<li>Best suited for <b>large files</b> (e.g., single post videos).</li>"
            "<li>When downloading a full creator feed with many small files (like images):"
            "<ul><li>May not offer significant speed benefits.</li>"
            "<li>Could potentially make the UI feel <b>choppy</b>.</li>"
            "<li>May <b>spam the process log</b> with rapid, numerous small download messages.</li></ul></li>"
            "<li>Consider using the <b>'Videos' filter</b> if downloading a creator feed to primarily target large files for multi-part.</li>"
            "</ul><br>"
            "Do you want to enable multi-part download?"
            )
            proceed_button =msg_box .addButton ("Proceed Anyway",QMessageBox .AcceptRole )
            cancel_button =msg_box .addButton ("Cancel",QMessageBox .RejectRole )
            msg_box .setDefaultButton (proceed_button )
            msg_box .exec_ ()

            if msg_box .clickedButton ()==cancel_button :
                self .log_signal .emit ("ℹ️ Multi-part download enabling cancelled by user.")
                return 

        self .allow_multipart_download_setting =not self .allow_multipart_download_setting 
        self ._update_multipart_toggle_button_text ()
        self .settings .setValue (ALLOW_MULTIPART_DOWNLOAD_KEY ,self .allow_multipart_download_setting )
        self .log_signal .emit (f"ℹ️ Multi-part download set to: {'Enabled'if self .allow_multipart_download_setting else 'Disabled'}")

    def _open_known_txt_file (self ):
        if not os .path .exists (self .config_file ):
            QMessageBox .warning (self ,"File Not Found",
            f"The file 'Known.txt' was not found at:\n{self .config_file }\n\n"
            "It will be created automatically when you add a known name or close the application.")
            self .log_signal .emit (f"ℹ️ 'Known.txt' not found at {self .config_file }. It will be created later.")
            return 

        try :
            if sys .platform =="win32":
                os .startfile (self .config_file )
            elif sys .platform =="darwin":
                subprocess .call (['open',self .config_file ])
            else :
                subprocess .call (['xdg-open',self .config_file ])
            self .log_signal .emit (f"ℹ️ Attempted to open '{os .path .basename (self .config_file )}' with the default editor.")
        except FileNotFoundError :
            QMessageBox .critical (self ,"Error",f"Could not find '{os .path .basename (self .config_file )}' at {self .config_file } to open it.")
            self .log_signal .emit (f"❌ Error: '{os .path .basename (self .config_file )}' not found at {self .config_file } when trying to open.")
        except Exception as e :
            QMessageBox .critical (self ,"Error Opening File",f"Could not open '{os .path .basename (self .config_file )}':\n{e }")
            self .log_signal .emit (f"❌ Error opening '{os .path .basename (self .config_file )}': {e }")

    def _show_add_to_filter_dialog (self ):
        global KNOWN_NAMES 
        if not KNOWN_NAMES :
            QMessageBox .information (self ,"No Known Names","Your 'Known.txt' list is empty. Add some names first.")
            return 

        dialog =KnownNamesFilterDialog (KNOWN_NAMES ,self ,self )
        if dialog .exec_ ()==QDialog .Accepted :
            selected_entries =dialog .get_selected_entries ()
            if selected_entries :
                self ._add_names_to_character_filter_input (selected_entries )

    def _add_names_to_character_filter_input (self ,selected_entries ):
        """
        Adds the selected known name entries to the character filter input field.
        """
        if not selected_entries :
            return 

        names_to_add_str_list =[]
        for entry in selected_entries :
            if entry .get ("is_group"):
                aliases_str =", ".join (entry .get ("aliases",[]))
                names_to_add_str_list .append (f"({aliases_str })~")
            else :
                names_to_add_str_list .append (entry .get ("name",""))

        names_to_add_str_list =[s for s in names_to_add_str_list if s ]

        if not names_to_add_str_list :
            return 

        current_filter_text =self .character_input .text ().strip ()
        new_text_to_append =", ".join (names_to_add_str_list )

        self .character_input .setText (f"{current_filter_text }, {new_text_to_append }"if current_filter_text else new_text_to_append )
        self .log_signal .emit (f"ℹ️ Added to character filter: {new_text_to_append }")

    def _update_favorite_scope_button_text (self ):
        if not hasattr (self ,'favorite_scope_toggle_button')or not self .favorite_scope_toggle_button :
            return 
        if self .favorite_download_scope ==FAVORITE_SCOPE_SELECTED_LOCATION :
            self .favorite_scope_toggle_button .setText (self ._tr ("favorite_scope_selected_location_text","Scope: Selected Location"))

        elif self .favorite_download_scope ==FAVORITE_SCOPE_ARTIST_FOLDERS :
            self .favorite_scope_toggle_button .setText (self ._tr ("favorite_scope_artist_folders_text","Scope: Artist Folders"))

        else :
            self .favorite_scope_toggle_button .setText (self ._tr ("favorite_scope_unknown_text","Scope: Unknown"))


    def _cycle_favorite_scope (self ):
        if self .favorite_download_scope ==FAVORITE_SCOPE_SELECTED_LOCATION :
            self .favorite_download_scope =FAVORITE_SCOPE_ARTIST_FOLDERS 
        else :
            self .favorite_download_scope =FAVORITE_SCOPE_SELECTED_LOCATION 
        self ._update_favorite_scope_button_text ()
        self .log_signal .emit (f"ℹ️ Favorite download scope changed to: '{self .favorite_download_scope }'")

    def _show_empty_popup (self ):
        """Creates and shows the empty popup dialog."""
        dialog =EmptyPopupDialog (self .app_base_dir ,self ,self )
        if dialog .exec_ ()==QDialog .Accepted :
            if hasattr (dialog ,'selected_creators_for_queue')and dialog .selected_creators_for_queue :
                self .favorite_download_queue .clear ()

                for creator_data in dialog .selected_creators_for_queue :
                    service =creator_data .get ('service')
                    creator_id =creator_data .get ('id')
                    creator_name =creator_data .get ('name','Unknown Creator')
                    domain =dialog ._get_domain_for_service (service )

                    if service and creator_id :
                        url =f"https://{domain }/{service }/user/{creator_id }"
                        queue_item ={
                        'url':url ,
                        'name':creator_name ,
                        'name_for_folder':creator_name ,
                        'type':'creator_popup_selection',
                        'scope_from_popup':dialog .current_scope_mode 
                        }
                        self .favorite_download_queue .append (queue_item )

                if self .favorite_download_queue :
                    self .log_signal .emit (f"ℹ️ {len (self .favorite_download_queue )} creators added to download queue from popup. Click 'Start Download' to process.")
                    if hasattr (self ,'link_input'):
                        self .last_link_input_text_for_queue_sync =self .link_input .text ()

    def _show_favorite_artists_dialog (self ):
        if self ._is_download_active ()or self .is_processing_favorites_queue :
            QMessageBox .warning (self ,"Busy","Another download operation is already in progress.")
            return 

        cookies_config ={
        'use_cookie':self .use_cookie_checkbox .isChecked ()if hasattr (self ,'use_cookie_checkbox')else False ,
        'cookie_text':self .cookie_text_input .text ()if hasattr (self ,'cookie_text_input')else "",
        'selected_cookie_file':self .selected_cookie_filepath ,
        'app_base_dir':self .app_base_dir 
        }

        dialog =FavoriteArtistsDialog (self ,cookies_config )
        if dialog .exec_ ()==QDialog .Accepted :
            selected_artists =dialog .get_selected_artists ()
            if selected_artists :
                if len (selected_artists )>1 and self .link_input :
                    display_names =", ".join ([artist ['name']for artist in selected_artists ])
                    if self .link_input :
                        self .link_input .clear ()
                        self .link_input .setPlaceholderText (f"{len (selected_artists )} favorite artists selected for download queue.")
                    self .log_signal .emit (f"ℹ️ Multiple favorite artists selected. Displaying names: {display_names }")
                elif len (selected_artists )==1 :
                    self .link_input .setText (selected_artists [0 ]['url'])
                    self .log_signal .emit (f"ℹ️ Single favorite artist selected: {selected_artists [0 ]['name']}")

                self .log_signal .emit (f"ℹ️ Queuing {len (selected_artists )} favorite artist(s) for download.")
                for artist_data in selected_artists :
                    self .favorite_download_queue .append ({'url':artist_data ['url'],'name':artist_data ['name'],'name_for_folder':artist_data ['name'],'type':'artist'})

                if not self .is_processing_favorites_queue :
                    self ._process_next_favorite_download ()
            else :
                self .log_signal .emit ("ℹ️ No favorite artists were selected for download.")
                QMessageBox .information (self ,
                self ._tr ("fav_artists_no_selection_title","No Selection"),
                self ._tr ("fav_artists_no_selection_message","Please select at least one artist to download."))
        else :
            self .log_signal .emit ("ℹ️ Favorite artists selection cancelled.")

    def _show_favorite_posts_dialog (self ):
        if self ._is_download_active ()or self .is_processing_favorites_queue :
            QMessageBox .warning (self ,"Busy","Another download operation is already in progress.")
            return 

        cookies_config ={
        'use_cookie':self .use_cookie_checkbox .isChecked ()if hasattr (self ,'use_cookie_checkbox')else False ,
        'cookie_text':self .cookie_text_input .text ()if hasattr (self ,'cookie_text_input')else "",
        'selected_cookie_file':self .selected_cookie_filepath ,
        'app_base_dir':self .app_base_dir 
        }
        global KNOWN_NAMES 

        target_domain_preference_for_fetch =None 

        if cookies_config ['use_cookie']:
            self .log_signal .emit ("Favorite Posts: 'Use Cookie' is checked. Determining target domain...")
            kemono_cookies =prepare_cookies_for_request (
            cookies_config ['use_cookie'],
            cookies_config ['cookie_text'],
            cookies_config ['selected_cookie_file'],
            cookies_config ['app_base_dir'],
            lambda msg :self .log_signal .emit (f"[FavPosts Cookie Check - Kemono] {msg }"),
            target_domain ="kemono.su"
            )
            coomer_cookies =prepare_cookies_for_request (
            cookies_config ['use_cookie'],
            cookies_config ['cookie_text'],
            cookies_config ['selected_cookie_file'],
            cookies_config ['app_base_dir'],
            lambda msg :self .log_signal .emit (f"[FavPosts Cookie Check - Coomer] {msg }"),
            target_domain ="coomer.su"
            )

            kemono_ok =bool (kemono_cookies )
            coomer_ok =bool (coomer_cookies )

            if kemono_ok and not coomer_ok :
                target_domain_preference_for_fetch ="kemono.su"
                self .log_signal .emit ("  ↳ Only Kemono.su cookies loaded. Will fetch favorites from Kemono.su only.")
            elif coomer_ok and not kemono_ok :
                target_domain_preference_for_fetch ="coomer.su"
                self .log_signal .emit ("  ↳ Only Coomer.su cookies loaded. Will fetch favorites from Coomer.su only.")
            elif kemono_ok and coomer_ok :
                target_domain_preference_for_fetch =None 
                self .log_signal .emit ("  ↳ Cookies for both Kemono.su and Coomer.su loaded. Will attempt to fetch from both.")
            else :
                self .log_signal .emit ("  ↳ No valid cookies loaded for Kemono.su or Coomer.su.")
                cookie_help_dialog =CookieHelpDialog (self ,self )
                cookie_help_dialog .exec_ ()
                return 
        else :
            self .log_signal .emit ("Favorite Posts: 'Use Cookie' is NOT checked. Cookies are required.")
            cookie_help_dialog =CookieHelpDialog (self ,self )
            cookie_help_dialog .exec_ ()
            return 

        dialog =FavoritePostsDialog (self ,cookies_config ,KNOWN_NAMES ,target_domain_preference_for_fetch )
        if dialog .exec_ ()==QDialog .Accepted :
            selected_posts =dialog .get_selected_posts ()
            if selected_posts :
                self .log_signal .emit (f"ℹ️ Queuing {len (selected_posts )} favorite post(s) for download.")
                for post_data in selected_posts :
                    domain =self ._get_domain_for_service (post_data ['service'])
                    direct_post_url =f"https://{domain }/{post_data ['service']}/user/{str (post_data ['creator_id'])}/post/{str (post_data ['post_id'])}"

                    queue_item ={
                    'url':direct_post_url ,
                    'name':post_data ['title'],
                        'name_for_folder': post_data['creator_name_resolved'], # Use resolved name
                    'type':'post'
                    }
                    self .favorite_download_queue .append (queue_item )

                if not self .is_processing_favorites_queue :
                    self ._process_next_favorite_download ()
            else :
                self .log_signal .emit ("ℹ️ No favorite posts were selected for download.")
        else :
            self .log_signal .emit ("ℹ️ Favorite posts selection cancelled.")

    def _process_next_favorite_download (self ):
        if self ._is_download_active ():
            self .log_signal .emit ("ℹ️ Waiting for current download to finish before starting next favorite.")
            return 
        if not self .favorite_download_queue :
            if self .is_processing_favorites_queue :
                self .is_processing_favorites_queue =False 
                item_type_log ="item"
                if hasattr (self ,'current_processing_favorite_item_info')and self .current_processing_favorite_item_info :
                    item_type_log =self .current_processing_favorite_item_info .get ('type','item')
                self .log_signal .emit (f"✅ All {item_type_log } downloads from favorite queue have been processed.")
                self .set_ui_enabled (True )
            return 
        if not self .is_processing_favorites_queue :
            self .is_processing_favorites_queue =True 
        self .current_processing_favorite_item_info =self .favorite_download_queue .popleft ()
        next_url =self .current_processing_favorite_item_info ['url']
        item_display_name =self .current_processing_favorite_item_info .get ('name','Unknown Item')

        item_type = self.current_processing_favorite_item_info.get('type', 'artist')
        self .log_signal .emit (f"▶️ Processing next favorite from queue: '{item_display_name }' ({next_url })")

        override_dir =None 
        item_scope =self .current_processing_favorite_item_info .get ('scope_from_popup')
        if item_scope is None :
            item_scope =self .favorite_download_scope 

        main_download_dir =self .dir_input .text ().strip ()
        
        # Determine if folder override is needed based on scope
        # For 'creator_popup_selection', the scope is determined by dialog.current_scope_mode
        # For 'artist' or 'single_post_from_popup' (queued from Favorite Artists/Posts dialogs), it's self.favorite_download_scope
        should_create_artist_folder = False
        if item_type == 'creator_popup_selection' and item_scope == EmptyPopupDialog.SCOPE_CREATORS:
            should_create_artist_folder = True
        elif item_type != 'creator_popup_selection' and self.favorite_download_scope == FAVORITE_SCOPE_ARTIST_FOLDERS:
            should_create_artist_folder = True

        if should_create_artist_folder and main_download_dir:
            folder_name_key =self .current_processing_favorite_item_info .get ('name_for_folder','Unknown_Folder')
            item_specific_folder_name =clean_folder_name (folder_name_key )
            override_dir =os .path .normpath (os .path .join (main_download_dir ,item_specific_folder_name ))
            self .log_signal .emit (f"    Scope requires artist folder. Target directory: '{override_dir }'")

        success_starting_download =self .start_download (direct_api_url =next_url ,override_output_dir =override_dir )

        if not success_starting_download :
            self .log_signal .emit (f"⚠️ Failed to initiate download for '{item_display_name }'. Skipping this item in queue.")
            self .download_finished (total_downloaded =0 ,total_skipped =1 ,cancelled_by_user =True ,kept_original_names_list =[])

if __name__ =='__main__':
    import traceback 
    import sys 
    import os 
    import time 

    def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
        """Handles uncaught exceptions by logging them to a file."""
        # Determine base_dir for logs
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # PyInstaller-like bundle
            base_dir_for_log = sys._MEIPASS
        else:
            # Running as a script
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
            # If logging itself fails, print to stderr
            print(f"CRITICAL: Failed to write to uncaught_exceptions.log: {log_ex}", file=sys.stderr)
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr) # Log original exception to stderr
        sys.__excepthook__(exc_type, exc_value, exc_traceback) # Call the default excepthook

    sys.excepthook = handle_uncaught_exception # Set the custom excepthook

    try :
        qt_app =QApplication (sys .argv )
        # Set these after QApplication is initialized and before they might be needed
        QCoreApplication.setOrganizationName(CONFIG_ORGANIZATION_NAME)
        QCoreApplication.setApplicationName(CONFIG_APP_NAME_MAIN) # Using the same name as for QSettings path part    
        if getattr (sys ,'frozen',False ) and hasattr(sys, '_MEIPASS'): # Check for _MEIPASS for PyInstaller
            base_dir =sys ._MEIPASS 
        else: # This 'else' now correctly follows its 'if'
            base_dir =os .path .dirname (os .path .abspath (__file__ ))
        icon_path =os .path .join (base_dir , 'assets', 'Kemono.ico')
        if os .path .exists (icon_path ):qt_app .setWindowIcon (QIcon (icon_path ))
        else :print (f"Warning: Application icon 'assets/Kemono.ico' not found at {icon_path }")

        downloader_app_instance =DownloaderApp ()
        primary_screen =QApplication .primaryScreen ()
        if not primary_screen :
            screens =QApplication .screens ()
            if not screens :
                downloader_app_instance .resize (1024 ,768 )
                downloader_app_instance .show ()
                sys .exit (qt_app .exec_ ())
            primary_screen =screens [0 ]

        available_geo =primary_screen .availableGeometry ()
        screen_width =available_geo .width ()
        screen_height =available_geo .height ()
        min_app_width =960 
        min_app_height =680 
        desired_app_width_ratio =0.80 
        desired_app_height_ratio =0.85 

        app_width =max (min_app_width ,int (screen_width *desired_app_width_ratio ))
        app_height =max (min_app_height ,int (screen_height *desired_app_height_ratio ))
        app_width =min (app_width ,screen_width )
        app_height =min (app_height ,screen_height )

        downloader_app_instance .resize (app_width ,app_height )
        downloader_app_instance .show ()
        downloader_app_instance ._center_on_screen ()
        try :
            tour_result =TourDialog .run_tour_if_needed (downloader_app_instance )
            if tour_result ==QDialog .Accepted :print ("Tour completed by user.")
            elif tour_result ==QDialog .Rejected :print ("Tour skipped or was already shown.")
        except NameError :
            print ("[Main] TourDialog class not found. Skipping tour.")
        except Exception as e_tour :
            print (f"[Main] Error during tour execution: {e_tour }")

        exit_code =qt_app .exec_ ()
        print (f"Application finished with exit code: {exit_code }")
        sys .exit (exit_code )
    except SystemExit :pass 
    except Exception as e :
        print ("--- CRITICAL APPLICATION ERROR ---")
        print (f"An unhandled exception occurred: {e }")
        traceback .print_exc ()
        print ("--- END CRITICAL ERROR ---")