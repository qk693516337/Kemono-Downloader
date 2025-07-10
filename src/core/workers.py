# --- Standard Library Imports ---
import os
import queue
import re
import threading
import time
import traceback
import uuid
import http
import html
import json
from collections import deque
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed, CancelledError, Future
from io import BytesIO
from urllib .parse import urlparse 
import requests
# --- Third-Party Library Imports ---
try:
    from PIL import Image
except ImportError:
    Image = None
# --- PyQt5 Imports ---
from PyQt5 .QtCore import Qt ,QThread ,pyqtSignal ,QMutex ,QMutexLocker ,QObject ,QTimer ,QSettings ,QStandardPaths ,QCoreApplication ,QUrl ,QSize ,QProcess 
# --- Local Application Imports ---
from .api_client import download_from_api, fetch_post_comments
from ..services.multipart_downloader import download_file_in_parts, MULTIPART_DOWNLOADER_AVAILABLE
from ..services.drive_downloader import (
    download_mega_file, download_gdrive_file, download_dropbox_file
)
# Corrected Imports:
from ..utils.file_utils import (
    is_image, is_video, is_zip, is_rar, is_archive, is_audio, KNOWN_NAMES,
    clean_filename, clean_folder_name
)
from ..utils.network_utils import prepare_cookies_for_request, get_link_platform
from ..utils.text_utils import (
    is_title_match_for_character, is_filename_match_for_character, strip_html_tags,
    extract_folder_name_from_title, # This was the function causing the error
    match_folders_from_title, match_folders_from_filename_enhanced
)
from ..config.constants import *

class PostProcessorSignals (QObject ):
    progress_signal =pyqtSignal (str )
    file_download_status_signal =pyqtSignal (bool )
    external_link_signal =pyqtSignal (str ,str ,str ,str ,str )
    file_progress_signal =pyqtSignal (str ,object )
    file_successfully_downloaded_signal =pyqtSignal (dict )
    missed_character_post_signal =pyqtSignal (str ,str )
    
class PostProcessorWorker:
    def __init__ (self ,post_data ,download_root ,known_names ,
    filter_character_list ,emitter ,
    unwanted_keywords ,filter_mode ,skip_zip ,skip_rar ,
    use_subfolders ,use_post_subfolders ,target_post_id_from_initial_url ,custom_folder_name ,
    compress_images ,download_thumbnails ,service ,user_id ,pause_event ,
    api_url_input ,cancellation_event ,
    downloaded_files ,downloaded_file_hashes ,downloaded_files_lock ,downloaded_file_hashes_lock ,
    dynamic_character_filter_holder =None ,skip_words_list =None ,
    skip_words_scope =SKIP_SCOPE_FILES ,
    show_external_links =False ,
    extract_links_only =False ,
    num_file_threads =4 ,skip_current_file_flag =None ,
    manga_mode_active =False ,
    manga_filename_style =STYLE_POST_TITLE ,
    char_filter_scope =CHAR_SCOPE_FILES ,
    remove_from_filename_words_list =None ,
    allow_multipart_download =True ,
    cookie_text ="",
    use_cookie =False ,
    override_output_dir =None ,
    selected_cookie_file =None ,
    app_base_dir =None ,
    manga_date_prefix =MANGA_DATE_PREFIX_DEFAULT ,
    manga_date_file_counter_ref =None ,
    scan_content_for_images =False ,
    creator_download_folder_ignore_words =None ,
    manga_global_file_counter_ref =None ,
    use_date_prefix_for_subfolder=False,
    session_file_path=None,
    session_lock=None,
    ):
        self .post =post_data 
        self .download_root =download_root 
        self .known_names =known_names 
        self .filter_character_list_objects_initial =filter_character_list if filter_character_list else []
        self .dynamic_filter_holder =dynamic_character_filter_holder 
        self .unwanted_keywords =unwanted_keywords if unwanted_keywords is not None else set ()
        self .filter_mode =filter_mode 
        self .skip_zip =skip_zip 
        self .skip_rar =skip_rar 
        self .use_subfolders =use_subfolders 
        self .use_post_subfolders =use_post_subfolders 
        self .target_post_id_from_initial_url =target_post_id_from_initial_url 
        self .custom_folder_name =custom_folder_name 
        self .compress_images =compress_images 
        self .download_thumbnails =download_thumbnails 
        self .service =service 
        self .user_id =user_id 
        self .api_url_input =api_url_input 
        self .cancellation_event =cancellation_event 
        self .pause_event =pause_event 
        self .emitter =emitter 
        if not self .emitter :
            raise ValueError ("PostProcessorWorker requires an emitter (signals object or queue).")
        self .skip_current_file_flag =skip_current_file_flag 
        self .downloaded_files =downloaded_files if downloaded_files is not None else set ()
        self .downloaded_file_hashes =downloaded_file_hashes if downloaded_file_hashes is not None else set ()
        self .downloaded_files_lock =downloaded_files_lock if downloaded_files_lock is not None else threading .Lock ()
        self .downloaded_file_hashes_lock =downloaded_file_hashes_lock if downloaded_file_hashes_lock is not None else threading .Lock ()
        self .skip_words_list =skip_words_list if skip_words_list is not None else []
        self .skip_words_scope =skip_words_scope 
        self .show_external_links =show_external_links 
        self .extract_links_only =extract_links_only 
        self .num_file_threads =num_file_threads 
        self .manga_mode_active =manga_mode_active 
        self .manga_filename_style =manga_filename_style 
        self .char_filter_scope =char_filter_scope 
        self .remove_from_filename_words_list =remove_from_filename_words_list if remove_from_filename_words_list is not None else []
        self .allow_multipart_download =allow_multipart_download 
        self .manga_date_file_counter_ref =manga_date_file_counter_ref 
        self .selected_cookie_file =selected_cookie_file 
        self .app_base_dir =app_base_dir 
        self .cookie_text =cookie_text 
        self .manga_date_prefix =manga_date_prefix 
        self .manga_global_file_counter_ref =manga_global_file_counter_ref 
        self .use_cookie =use_cookie 
        self .override_output_dir =override_output_dir 
        self .scan_content_for_images =scan_content_for_images 
        self .creator_download_folder_ignore_words =creator_download_folder_ignore_words 
        self.use_date_prefix_for_subfolder = use_date_prefix_for_subfolder
        self.session_file_path = session_file_path
        self.session_lock = session_lock
        if self .compress_images and Image is None :

            self .logger ("⚠️ Image compression disabled: Pillow library not found.")
            self .compress_images =False 
    def _emit_signal (self ,signal_type_str ,*payload_args ):
        """Helper to emit signal either directly or via queue."""
        if isinstance (self .emitter ,queue .Queue ):
            self .emitter .put ({'type':signal_type_str ,'payload':payload_args })
        elif self .emitter and hasattr (self .emitter ,f"{signal_type_str }_signal"):
            signal_attr =getattr (self .emitter ,f"{signal_type_str }_signal")
            signal_attr .emit (*payload_args )
        else :
            print (f"(Worker Log - Unrecognized Emitter for {signal_type_str }): {payload_args [0 ]if payload_args else ''}")
    def logger (self ,message ):
        self ._emit_signal ('progress',message )
    def check_cancel (self ):
        return self .cancellation_event .is_set ()
    def _check_pause (self ,context_message ="Operation"):
        if self .pause_event and self .pause_event .is_set ():
            self .logger (f"   {context_message } paused...")
            while self .pause_event .is_set ():
                if self .check_cancel ():
                    self .logger (f"   {context_message } cancelled while paused.")
                    return True 
                time .sleep (0.5 )
            if not self .check_cancel ():self .logger (f"   {context_message } resumed.")
        return False 
    def _download_single_file (self ,file_info ,target_folder_path ,headers ,original_post_id_for_log ,skip_event ,
    post_title ="",file_index_in_post =0 ,num_files_in_this_post =1 ,
    manga_date_file_counter_ref =None ):
        was_original_name_kept_flag =False 

        final_filename_saved_for_return =""
    def _get_current_character_filters (self ):
        if self .dynamic_filter_holder :
            return self .dynamic_filter_holder .get_filters ()
        return self .filter_character_list_objects_initial 

    def _download_single_file (self ,file_info ,target_folder_path ,headers ,original_post_id_for_log ,skip_event ,
    post_title ="",file_index_in_post =0 ,num_files_in_this_post =1 ,
    manga_date_file_counter_ref =None ,
    forced_filename_override =None ,
    manga_global_file_counter_ref =None ,folder_context_name_for_history =None ):
        was_original_name_kept_flag =False 
        final_filename_saved_for_return =""
        retry_later_details =None 



        if self ._check_pause (f"File download prep for '{file_info .get ('name','unknown file')}'"):return 0 ,1 ,"",False 
        if self .check_cancel ()or (skip_event and skip_event .is_set ()):return 0 ,1 ,"",False 



        file_url =file_info .get ('url')
        cookies_to_use_for_file =None 
        if self .use_cookie :

            cookies_to_use_for_file =prepare_cookies_for_request (self .use_cookie ,self .cookie_text ,self .selected_cookie_file ,self .app_base_dir ,self .logger )


        api_original_filename =file_info .get ('_original_name_for_log',file_info .get ('name'))


        filename_to_save_in_main_path =""
        if forced_filename_override :
            filename_to_save_in_main_path =forced_filename_override 
            self .logger (f"   Retrying with forced filename: '{filename_to_save_in_main_path }'")
        else :

            if self .skip_words_list and (self .skip_words_scope ==SKIP_SCOPE_FILES or self .skip_words_scope ==SKIP_SCOPE_BOTH ):
                filename_to_check_for_skip_words =api_original_filename .lower ()
                for skip_word in self .skip_words_list :
                    if skip_word .lower ()in filename_to_check_for_skip_words :
                        self .logger (f"   -> Skip File (Keyword in Original Name '{skip_word }'): '{api_original_filename }'. Scope: {self .skip_words_scope }")
                        return 0 ,1 ,api_original_filename ,False ,FILE_DOWNLOAD_STATUS_SKIPPED ,None 

            cleaned_original_api_filename =clean_filename (api_original_filename )

            original_filename_cleaned_base ,original_ext =os .path .splitext (cleaned_original_api_filename )

            if not original_ext .startswith ('.'):original_ext ='.'+original_ext if original_ext else ''
            if self .manga_mode_active :

                if self .manga_filename_style ==STYLE_ORIGINAL_NAME :
                    filename_to_save_in_main_path =cleaned_original_api_filename 
                    if self .manga_date_prefix and self .manga_date_prefix .strip ():
                        cleaned_prefix =clean_filename (self .manga_date_prefix .strip ())
                        if cleaned_prefix :
                            filename_to_save_in_main_path =f"{cleaned_prefix } {filename_to_save_in_main_path }"
                        else :
                            self .logger (f"⚠️ Manga Original Name Mode: Provided prefix '{self .manga_date_prefix }' was empty after cleaning. Using original name only.")
                    was_original_name_kept_flag =True 
                elif self .manga_filename_style ==STYLE_POST_TITLE :
                    if post_title and post_title .strip ():
                        cleaned_post_title_base =clean_filename (post_title .strip ())
                        if num_files_in_this_post >1 :
                            if file_index_in_post ==0 :
                                filename_to_save_in_main_path =f"{cleaned_post_title_base }{original_ext }"
                            else :
                                filename_to_save_in_main_path =f"{cleaned_post_title_base }_{file_index_in_post }{original_ext }"
                                was_original_name_kept_flag =False 
                        else :
                            filename_to_save_in_main_path =f"{cleaned_post_title_base }{original_ext }"
                    else :
                        filename_to_save_in_main_path =cleaned_original_api_filename 
                        self .logger (f"⚠️ Manga mode (Post Title Style): Post title missing for post {original_post_id_for_log }. Using cleaned original filename '{filename_to_save_in_main_path }'.")
                elif self .manga_filename_style ==STYLE_DATE_BASED :
                    current_thread_name =threading .current_thread ().name 
                    if manga_date_file_counter_ref is not None and len (manga_date_file_counter_ref )==2 :
                        counter_val_for_filename =-1 
                        counter_lock =manga_date_file_counter_ref [1 ]

                        with counter_lock :
                            counter_val_for_filename =manga_date_file_counter_ref [0 ]
                            manga_date_file_counter_ref [0 ]+=1 

                        base_numbered_name =f"{counter_val_for_filename :03d}"
                        if self .manga_date_prefix and self .manga_date_prefix .strip ():
                            cleaned_prefix =clean_filename (self .manga_date_prefix .strip ())
                            if cleaned_prefix :
                                filename_to_save_in_main_path =f"{cleaned_prefix } {base_numbered_name }{original_ext }"
                            else :
                                filename_to_save_in_main_path =f"{base_numbered_name }{original_ext }";self .logger (f"⚠️ Manga Date Mode: Provided prefix '{self .manga_date_prefix }' was empty after cleaning. Using number only.")
                        else :
                            filename_to_save_in_main_path =f"{base_numbered_name }{original_ext }"
                    else :
                        self .logger (f"⚠️ Manga Date Mode: Counter ref not provided or malformed for '{api_original_filename }'. Using original. Ref: {manga_date_file_counter_ref }")
                        filename_to_save_in_main_path =cleaned_original_api_filename 
                elif self .manga_filename_style ==STYLE_POST_TITLE_GLOBAL_NUMBERING :
                    if manga_global_file_counter_ref is not None and len (manga_global_file_counter_ref )==2 :
                        counter_val_for_filename =-1 
                        counter_lock =manga_global_file_counter_ref [1 ]

                        with counter_lock :
                            counter_val_for_filename =manga_global_file_counter_ref [0 ]
                            manga_global_file_counter_ref [0 ]+=1 

                        cleaned_post_title_base_for_global =clean_filename (post_title .strip ()if post_title and post_title .strip ()else "post")
                        filename_to_save_in_main_path =f"{cleaned_post_title_base_for_global }_{counter_val_for_filename :03d}{original_ext }"
                    else :
                        self .logger (f"⚠️ Manga Title+GlobalNum Mode: Counter ref not provided or malformed for '{api_original_filename }'. Using original. Ref: {manga_global_file_counter_ref }")
                        filename_to_save_in_main_path =cleaned_original_api_filename 
                        self .logger (f"⚠️ Manga mode (Title+GlobalNum Style Fallback): Using cleaned original filename '{filename_to_save_in_main_path }' for post {original_post_id_for_log }.")
                elif self.manga_filename_style == STYLE_POST_ID:
                    if original_post_id_for_log and original_post_id_for_log != 'unknown_id':
                        base_name = str(original_post_id_for_log)
                        # Always append the file index for consistency (e.g., xxxxxx_0, xxxxxx_1)
                        filename_to_save_in_main_path = f"{base_name}_{file_index_in_post}{original_ext}"
                    else:
                        # Fallback if post_id is somehow not available
                        self.logger(f"⚠️ Manga mode (Post ID Style): Post ID missing. Using cleaned original filename '{cleaned_original_api_filename}'.")
                        filename_to_save_in_main_path = cleaned_original_api_filename
                elif self .manga_filename_style ==STYLE_DATE_POST_TITLE :
                    published_date_str =self .post .get ('published')
                    added_date_str =self .post .get ('added')
                    formatted_date_str ="nodate"

                    if published_date_str :
                        try :
                            formatted_date_str =published_date_str .split ('T')[0 ]
                        except Exception :
                            self .logger (f"    ⚠️ Could not parse 'published' date '{published_date_str }' for STYLE_DATE_POST_TITLE. Using 'nodate'.")
                    elif added_date_str :
                        try :
                            formatted_date_str =added_date_str .split ('T')[0 ]
                            self .logger (f"    ⚠️ Post ID {original_post_id_for_log } missing 'published' date, using 'added' date '{added_date_str }' for STYLE_DATE_POST_TITLE naming.")
                        except Exception :
                            self .logger (f"    ⚠️ Could not parse 'added' date '{added_date_str }' for STYLE_DATE_POST_TITLE. Using 'nodate'.")
                    else :
                        self .logger (f"    ⚠️ Post ID {original_post_id_for_log } missing both 'published' and 'added' dates for STYLE_DATE_POST_TITLE. Using 'nodate'.")

                    if post_title and post_title .strip ():
                        temp_cleaned_title =clean_filename (post_title .strip ())
                        if not temp_cleaned_title or temp_cleaned_title .startswith ("untitled_file"):
                            self .logger (f"⚠️ Manga mode (Date+PostTitle Style): Post title for post {original_post_id_for_log } ('{post_title }') was empty or generic after cleaning. Using 'post' as title part.")
                            cleaned_post_title_for_filename ="post"
                        else :
                            cleaned_post_title_for_filename =temp_cleaned_title 

                        base_name_for_style =f"{formatted_date_str }_{cleaned_post_title_for_filename }"

                        if num_files_in_this_post >1 :
                            filename_to_save_in_main_path =f"{base_name_for_style }_{file_index_in_post }{original_ext }"if file_index_in_post >0 else f"{base_name_for_style }{original_ext }"
                        else :
                            filename_to_save_in_main_path =f"{base_name_for_style }{original_ext }"
                    else :
                        self .logger (f"⚠️ Manga mode (Date+PostTitle Style): Post title missing for post {original_post_id_for_log }. Using 'post' as title part with date prefix.")
                        cleaned_post_title_for_filename ="post"
                        base_name_for_style =f"{formatted_date_str }_{cleaned_post_title_for_filename }"
                        if num_files_in_this_post >1 :
                            filename_to_save_in_main_path =f"{base_name_for_style }_{file_index_in_post }{original_ext }"if file_index_in_post >0 else f"{base_name_for_style }{original_ext }"
                        else :
                            filename_to_save_in_main_path =f"{base_name_for_style }{original_ext }"
                        self .logger (f"⚠️ Manga mode (Title+GlobalNum Style Fallback): Using cleaned original filename '{filename_to_save_in_main_path }' for post {original_post_id_for_log }.")
                else :
                    self .logger (f"⚠️ Manga mode: Unknown filename style '{self .manga_filename_style }'. Defaulting to original filename for '{api_original_filename }'.")
                    filename_to_save_in_main_path =cleaned_original_api_filename 
                if not filename_to_save_in_main_path :
                    filename_to_save_in_main_path =f"manga_file_{original_post_id_for_log }_{file_index_in_post +1 }{original_ext }"
                    self .logger (f"⚠️ Manga mode: Generated filename was empty. Using generic fallback: '{filename_to_save_in_main_path }'.")
                    was_original_name_kept_flag =False 
            else :

                filename_to_save_in_main_path =cleaned_original_api_filename 
                was_original_name_kept_flag =False 



            if self .remove_from_filename_words_list and filename_to_save_in_main_path :

                base_name_for_removal ,ext_for_removal =os .path .splitext (filename_to_save_in_main_path )
                modified_base_name =base_name_for_removal 
                for word_to_remove in self .remove_from_filename_words_list :
                    if not word_to_remove :continue 
                    pattern =re .compile (re .escape (word_to_remove ),re .IGNORECASE )
                    modified_base_name =pattern .sub ("",modified_base_name )
                modified_base_name =re .sub (r'[_.\s-]+',' ',modified_base_name )
                modified_base_name =re .sub (r'\s+',' ',modified_base_name )
                modified_base_name =modified_base_name .strip ()
                if modified_base_name and modified_base_name !=ext_for_removal .lstrip ('.'):
                    filename_to_save_in_main_path =modified_base_name +ext_for_removal 
                else :
                    filename_to_save_in_main_path =base_name_for_removal +ext_for_removal 



        if not self .download_thumbnails :

            is_img_type =is_image (api_original_filename )
            is_vid_type =is_video (api_original_filename )
            is_archive_type =is_archive (api_original_filename )
            is_audio_type =is_audio (api_original_filename )
            if self .filter_mode =='archive':
                if not is_archive_type :
                    self .logger (f"   -> Filter Skip (Archive Mode): '{api_original_filename }' (Not an Archive).")
                    return 0 ,1 ,api_original_filename ,False ,FILE_DOWNLOAD_STATUS_SKIPPED ,None 
            elif self .filter_mode =='image':
                if not is_img_type :
                    self .logger (f"   -> Filter Skip: '{api_original_filename }' (Not Image).")
                    return 0 ,1 ,api_original_filename ,False ,FILE_DOWNLOAD_STATUS_SKIPPED ,None 
            elif self .filter_mode =='video':
                if not is_vid_type :
                    self .logger (f"   -> Filter Skip: '{api_original_filename }' (Not Video).")
                    return 0 ,1 ,api_original_filename ,False ,FILE_DOWNLOAD_STATUS_SKIPPED ,None 
            elif self .filter_mode =='audio':
                if not is_audio_type :
                    self .logger (f"   -> Filter Skip: '{api_original_filename }' (Not Audio).")
                    return 0 ,1 ,api_original_filename ,False ,FILE_DOWNLOAD_STATUS_SKIPPED ,None 
            if self .skip_zip and is_zip (api_original_filename ):
                self .logger (f"   -> Pref Skip: '{api_original_filename }' (ZIP).")
                return 0 ,1 ,api_original_filename ,False ,FILE_DOWNLOAD_STATUS_SKIPPED ,None 
            if self .skip_rar and is_rar (api_original_filename ):
                self .logger (f"   -> Pref Skip: '{api_original_filename }' (RAR).")
                return 0 ,1 ,api_original_filename ,False ,FILE_DOWNLOAD_STATUS_SKIPPED ,None 



        try :
            os .makedirs (target_folder_path ,exist_ok =True )

        except OSError as e :
            self .logger (f"   ❌ Critical error creating directory '{target_folder_path }': {e }. Skipping file '{api_original_filename }'.")
            return 0 ,1 ,api_original_filename ,False ,FILE_DOWNLOAD_STATUS_SKIPPED ,None 





        temp_file_base_for_unique_part ,temp_file_ext_for_unique_part =os .path .splitext (filename_to_save_in_main_path if filename_to_save_in_main_path else api_original_filename )
        unique_id_for_part_file =uuid .uuid4 ().hex [:8 ]
        unique_part_file_stem_on_disk =f"{temp_file_base_for_unique_part }_{unique_id_for_part_file }"
        max_retries =3 
        retry_delay =5 
        downloaded_size_bytes =0 
        calculated_file_hash =None 
        downloaded_part_file_path =None 
        was_multipart_download =False 
        total_size_bytes =0 
        download_successful_flag =False 
        last_exception_for_retry_later =None 

        response_for_this_attempt =None 
        for attempt_num_single_stream in range (max_retries +1 ):
            response_for_this_attempt =None 
            if self ._check_pause (f"File download attempt for '{api_original_filename }'"):break 
            if self .check_cancel ()or (skip_event and skip_event .is_set ()):break 
            try :
                if attempt_num_single_stream >0 :
                    self .logger (f"   Retrying download for '{api_original_filename }' (Overall Attempt {attempt_num_single_stream +1 }/{max_retries +1 })...")
                    time .sleep (retry_delay *(2 **(attempt_num_single_stream -1 )))
                self ._emit_signal ('file_download_status',True )
                response =requests .get (file_url ,headers =headers ,timeout =(15 ,300 ),stream =True ,cookies =cookies_to_use_for_file )
                response .raise_for_status ()
                total_size_bytes =int (response .headers .get ('Content-Length',0 ))
                num_parts_for_file =min (self .num_file_threads ,MAX_PARTS_FOR_MULTIPART_DOWNLOAD )
                attempt_multipart =(self .allow_multipart_download and MULTIPART_DOWNLOADER_AVAILABLE and 
                num_parts_for_file >1 and total_size_bytes >MIN_SIZE_FOR_MULTIPART_DOWNLOAD and 
                'bytes'in response .headers .get ('Accept-Ranges','').lower ())
                if self ._check_pause (f"Multipart decision for '{api_original_filename }'"):break 

                if attempt_multipart :
                    if response_for_this_attempt :
                        response_for_this_attempt .close ()
                        response_for_this_attempt =None 





                    mp_save_path_for_unique_part_stem_arg =os .path .join (target_folder_path ,f"{unique_part_file_stem_on_disk }{temp_file_ext_for_unique_part }")
                    mp_success ,mp_bytes ,mp_hash ,mp_file_handle =download_file_in_parts (
                    file_url ,mp_save_path_for_unique_part_stem_arg ,total_size_bytes ,num_parts_for_file ,headers ,api_original_filename ,
                    emitter_for_multipart =self .emitter ,cookies_for_chunk_session =cookies_to_use_for_file ,
                    cancellation_event =self .cancellation_event ,skip_event =skip_event ,logger_func =self .logger ,
                    pause_event =self .pause_event 
                    )
                    if mp_success :
                        download_successful_flag =True 
                        downloaded_size_bytes =mp_bytes 
                        calculated_file_hash =mp_hash 



                        downloaded_part_file_path =mp_save_path_for_unique_part_stem_arg +".part"
                        was_multipart_download =True 
                        if mp_file_handle :mp_file_handle .close ()
                        break 
                    else :
                        if attempt_num_single_stream <max_retries :
                            self .logger (f"   Multi-part download attempt failed for '{api_original_filename }'. Retrying with single stream.")
                        else :
                            download_successful_flag =False ;break 
                else :
                    self .logger (f"⬇️ Downloading (Single Stream): '{api_original_filename }' (Size: {total_size_bytes /(1024 *1024 ):.2f} MB if known) [Base Name: '{filename_to_save_in_main_path }']")

                    current_single_stream_part_path =os .path .join (target_folder_path ,f"{unique_part_file_stem_on_disk }{temp_file_ext_for_unique_part }.part")
                    current_attempt_downloaded_bytes =0 
                    md5_hasher =hashlib .md5 ()
                    last_progress_time =time .time ()

                    single_stream_exception =None 
                    try :
                        with open (current_single_stream_part_path ,'wb')as f_part :
                            for chunk in response .iter_content (chunk_size =1 *1024 *1024 ):
                                if self ._check_pause (f"Chunk download for '{api_original_filename }'"):break 
                                if self .check_cancel ()or (skip_event and skip_event .is_set ()):break 
                                if chunk :
                                    f_part .write (chunk )
                                    md5_hasher .update (chunk )
                                    current_attempt_downloaded_bytes +=len (chunk )
                                    if time .time ()-last_progress_time >1 and total_size_bytes >0 :
                                        self ._emit_signal ('file_progress',api_original_filename ,(current_attempt_downloaded_bytes ,total_size_bytes ))
                                        last_progress_time =time .time ()

                        if self .check_cancel ()or (skip_event and skip_event .is_set ())or (self .pause_event and self .pause_event .is_set ()and not (current_attempt_downloaded_bytes >0 or (total_size_bytes ==0 and response .status_code ==200 ))):
                            if os .path .exists (current_single_stream_part_path ):os .remove (current_single_stream_part_path )
                            break 


                        attempt_is_complete =False 
                        if response .status_code ==200 :
                            if total_size_bytes >0 :
                                if current_attempt_downloaded_bytes ==total_size_bytes :
                                    attempt_is_complete =True 
                                else :
                                    self .logger (f"   ⚠️ Single-stream attempt for '{api_original_filename }' incomplete: received {current_attempt_downloaded_bytes } of {total_size_bytes } bytes.")
                            elif total_size_bytes ==0 :
                                if current_attempt_downloaded_bytes ==0 :
                                    attempt_is_complete =True 
                                else :
                                    self .logger (f"   ⚠️ Mismatch for '{api_original_filename }': Server reported 0 bytes, but received {current_attempt_downloaded_bytes } bytes this attempt.")


                            elif current_attempt_downloaded_bytes >0 :
                                attempt_is_complete =True 
                                self .logger (f"   ⚠️ Single-stream for '{api_original_filename }' received {current_attempt_downloaded_bytes } bytes (no Content-Length from server). Assuming complete for this attempt as stream ended.")

                        if attempt_is_complete :
                            calculated_file_hash =md5_hasher .hexdigest ()
                            downloaded_size_bytes =current_attempt_downloaded_bytes 
                            downloaded_part_file_path =current_single_stream_part_path 
                            was_multipart_download =False 
                            download_successful_flag =True 
                            break 
                        else :
                            if os .path .exists (current_single_stream_part_path ):
                                try :os .remove (current_single_stream_part_path )
                                except OSError as e_rem_part :self .logger (f"  -> Failed to remove .part file after failed single stream attempt: {e_rem_part }")

                    except Exception as e_write :
                        self .logger (f"   ❌ Error writing single-stream to disk for '{api_original_filename }': {e_write }")
                        if os .path .exists (current_single_stream_part_path ):os .remove (current_single_stream_part_path )

                        raise 
                        single_stream_exception =e_write 
                    if single_stream_exception :
                        raise single_stream_exception 

            except (requests .exceptions .ConnectionError ,requests .exceptions .Timeout ,http .client .IncompleteRead )as e :
                self .logger (f"   ❌ Download Error (Retryable): {api_original_filename }. Error: {e }")
                last_exception_for_retry_later =e 
                if isinstance (e ,requests .exceptions .ConnectionError )and ("Failed to resolve"in str (e )or "NameResolutionError"in str (e )):
                    self .logger ("   💡 This looks like a DNS resolution problem. Please check your internet connection, DNS settings, or VPN.")
            except requests .exceptions .RequestException as e :
                self .logger (f"   ❌ Download Error (Non-Retryable): {api_original_filename }. Error: {e }")
                last_exception_for_retry_later =e 
                if ("Failed to resolve"in str (e )or "NameResolutionError"in str (e )):
                    self .logger ("   💡 This looks like a DNS resolution problem. Please check your internet connection, DNS settings, or VPN.")

                break 
            except Exception as e :
                self .logger (f"   ❌ Unexpected Download Error: {api_original_filename }: {e }\n{traceback .format_exc (limit =2 )}")
                last_exception_for_retry_later =e 
                break 
            finally :
                if response_for_this_attempt :
                    response_for_this_attempt .close ()
                self ._emit_signal ('file_download_status',False )

        final_total_for_progress =total_size_bytes if download_successful_flag and total_size_bytes >0 else downloaded_size_bytes 
        self ._emit_signal ('file_progress',api_original_filename ,(downloaded_size_bytes ,final_total_for_progress ))

        if self .check_cancel ()or (skip_event and skip_event .is_set ())or (self .pause_event and self .pause_event .is_set ()and not download_successful_flag ):
            self .logger (f"   ⚠️ Download process interrupted for {api_original_filename }.")
            if downloaded_part_file_path and os .path .exists (downloaded_part_file_path ):
                try :os .remove (downloaded_part_file_path )
                except OSError :pass 
            return 0 ,1 ,filename_to_save_in_main_path ,was_original_name_kept_flag ,FILE_DOWNLOAD_STATUS_SKIPPED ,None 

        if not download_successful_flag :
            self .logger (f"❌ Download failed for '{api_original_filename }' after {max_retries +1 } attempts.")


            is_actually_incomplete_read =False 
            if isinstance (last_exception_for_retry_later ,http .client .IncompleteRead ):
                is_actually_incomplete_read =True 
            elif hasattr (last_exception_for_retry_later ,'__cause__')and isinstance (last_exception_for_retry_later .__cause__ ,http .client .IncompleteRead ):
                is_actually_incomplete_read =True 

            elif last_exception_for_retry_later is not None :
                str_exc =str (last_exception_for_retry_later ).lower ()

                if "incompleteread"in str_exc or (isinstance (last_exception_for_retry_later ,tuple )and any ("incompleteread"in str (arg ).lower ()for arg in last_exception_for_retry_later if isinstance (arg ,(str ,Exception )))):
                    is_actually_incomplete_read =True 

            if is_actually_incomplete_read :
                self .logger (f"   Marking '{api_original_filename }' for potential retry later due to IncompleteRead.")
                retry_later_details ={
                'file_info':file_info ,
                'target_folder_path':target_folder_path ,
                'headers':headers ,
                'original_post_id_for_log':original_post_id_for_log ,
                'post_title':post_title ,
                'file_index_in_post':file_index_in_post ,
                'num_files_in_this_post':num_files_in_this_post ,
                'forced_filename_override':filename_to_save_in_main_path ,
                'manga_mode_active_for_file':self .manga_mode_active ,
                'manga_filename_style_for_file':self .manga_filename_style ,
                }
                return 0 ,1 ,filename_to_save_in_main_path ,was_original_name_kept_flag ,FILE_DOWNLOAD_STATUS_FAILED_RETRYABLE_LATER ,retry_later_details 
            else :
                self .logger (f"   Marking '{api_original_filename }' as permanently failed for this session.")
                permanent_failure_details ={
                'file_info':file_info ,
                'target_folder_path':target_folder_path ,
                'headers':headers ,
                'original_post_id_for_log':original_post_id_for_log ,
                'post_title':post_title ,
                'file_index_in_post':file_index_in_post ,
                'num_files_in_this_post':num_files_in_this_post ,
                'forced_filename_override':filename_to_save_in_main_path ,
                }
                return 0 ,1 ,filename_to_save_in_main_path ,was_original_name_kept_flag ,FILE_DOWNLOAD_STATUS_FAILED_PERMANENTLY_THIS_SESSION ,permanent_failure_details 
        if self ._check_pause (f"Post-download hash check for '{api_original_filename }'"):return 0 ,1 ,filename_to_save_in_main_path ,was_original_name_kept_flag ,FILE_DOWNLOAD_STATUS_SKIPPED ,None 
        with self .downloaded_file_hashes_lock :
            if calculated_file_hash in self .downloaded_file_hashes :
                self .logger (f"   -> Skip Saving Duplicate (Hash Match): '{api_original_filename }' (Hash: {calculated_file_hash [:8 ]}...).")
                with self .downloaded_files_lock :self .downloaded_files .add (filename_to_save_in_main_path )
                if downloaded_part_file_path and os .path .exists (downloaded_part_file_path ):
                    try :os .remove (downloaded_part_file_path )
                    except OSError as e_rem :self .logger (f"  -> Failed to remove .part file for hash duplicate: {e_rem }")
                return 0 ,1 ,filename_to_save_in_main_path ,was_original_name_kept_flag ,FILE_DOWNLOAD_STATUS_SKIPPED ,None 

        effective_save_folder =target_folder_path 
        filename_after_styling_and_word_removal =filename_to_save_in_main_path 

        try :
            os .makedirs (effective_save_folder ,exist_ok =True )
        except OSError as e :
            self .logger (f"   ❌ Critical error creating directory '{effective_save_folder }': {e }. Skipping file '{api_original_filename }'.")
            if downloaded_part_file_path and os .path .exists (downloaded_part_file_path ):
                try :os .remove (downloaded_part_file_path )
                except OSError :pass 
            return 0 ,1 ,api_original_filename ,False ,FILE_DOWNLOAD_STATUS_SKIPPED ,None 

        data_to_write_io =None 
        filename_after_compression =filename_after_styling_and_word_removal 
        is_img_for_compress_check =is_image (api_original_filename )

        if is_img_for_compress_check and self .compress_images and Image and downloaded_size_bytes >(1.5 *1024 *1024 ):
            self .logger (f"   Compressing '{api_original_filename }' ({downloaded_size_bytes /(1024 *1024 ):.2f} MB)...")
            if self ._check_pause (f"Image compression for '{api_original_filename }'"):return 0 ,1 ,filename_to_save_in_main_path ,was_original_name_kept_flag ,FILE_DOWNLOAD_STATUS_SKIPPED ,None 

            img_content_for_pillow =None 
            try :
                with open (downloaded_part_file_path ,'rb')as f_img_in :
                    img_content_for_pillow =BytesIO (f_img_in .read ())

                with Image .open (img_content_for_pillow )as img_obj :
                    if img_obj .mode =='P':img_obj =img_obj .convert ('RGBA')
                    elif img_obj .mode not in ['RGB','RGBA','L']:img_obj =img_obj .convert ('RGB')

                    compressed_output_io =BytesIO ()
                    img_obj .save (compressed_output_io ,format ='WebP',quality =80 ,method =4 )
                    compressed_size =compressed_output_io .getbuffer ().nbytes 

                    if compressed_size <downloaded_size_bytes *0.9 :
                        self .logger (f"   Compression success: {compressed_size /(1024 *1024 ):.2f} MB.")
                        data_to_write_io =compressed_output_io 
                        data_to_write_io .seek (0 )
                        base_name_orig ,_ =os .path .splitext (filename_after_compression )
                        filename_after_compression =base_name_orig +'.webp'
                        self .logger (f"   Updated filename (compressed): {filename_after_compression }")
                    else :
                        self .logger (f"   Compression skipped: WebP not significantly smaller.")

                        if compressed_output_io :compressed_output_io .close ()
            except Exception as comp_e :
                self .logger (f"❌ Compression failed for '{api_original_filename }': {comp_e }. Saving original.")

            finally :
                if img_content_for_pillow :img_content_for_pillow .close ()

        final_filename_on_disk =filename_after_compression 


        temp_base ,temp_ext =os .path .splitext (final_filename_on_disk )
        suffix_counter =1 
        while os .path .exists (os .path .join (effective_save_folder ,final_filename_on_disk )):
            final_filename_on_disk =f"{temp_base }_{suffix_counter }{temp_ext }"
            suffix_counter +=1 
        if final_filename_on_disk !=filename_after_compression :
            self .logger (f"     Applied numeric suffix in '{os .path .basename (effective_save_folder )}': '{final_filename_on_disk }' (was '{filename_after_compression }')")
        if self ._check_pause (f"File saving for '{final_filename_on_disk }'"):return 0 ,1 ,final_filename_on_disk ,was_original_name_kept_flag ,FILE_DOWNLOAD_STATUS_SKIPPED ,None 
        final_save_path =os .path .join (effective_save_folder ,final_filename_on_disk )
        try :
            if data_to_write_io :
                with open (final_save_path ,'wb')as f_out :
                    time .sleep (0.05 )
                    f_out .write (data_to_write_io .getvalue ())

                if downloaded_part_file_path and os .path .exists (downloaded_part_file_path ):
                    try :
                        os .remove (downloaded_part_file_path )
                    except OSError as e_rem :
                        self .logger (f"  -> Failed to remove .part after compression: {e_rem }")
            else :
                if downloaded_part_file_path and os .path .exists (downloaded_part_file_path ):
                    time .sleep (0.1 )
                    os .rename (downloaded_part_file_path ,final_save_path )
                else :
                    raise FileNotFoundError (f"Original .part file not found for saving: {downloaded_part_file_path }")
            with self .downloaded_file_hashes_lock :self .downloaded_file_hashes .add (calculated_file_hash )
            with self .downloaded_files_lock :self .downloaded_files .add (filename_to_save_in_main_path )
            final_filename_saved_for_return =final_filename_on_disk 
            self .logger (f"✅ Saved: '{final_filename_saved_for_return }' (from '{api_original_filename }', {downloaded_size_bytes /(1024 *1024 ):.2f} MB) in '{os .path .basename (effective_save_folder )}'")


            downloaded_file_details ={
            'disk_filename':final_filename_saved_for_return ,
            'post_title':post_title ,
            'post_id':original_post_id_for_log ,
            'upload_date_str':self .post .get ('published')or self .post .get ('added')or "N/A",
            'download_timestamp':time .time (),
            'download_path':effective_save_folder ,
            'service':self .service ,
            'user_id':self .user_id ,
            'api_original_filename':api_original_filename ,
            'folder_context_name':folder_context_name_for_history or os .path .basename (effective_save_folder )
            }
            self ._emit_signal ('file_successfully_downloaded',downloaded_file_details )
            time .sleep (0.05 )

            return 1 ,0 ,final_filename_saved_for_return ,was_original_name_kept_flag ,FILE_DOWNLOAD_STATUS_SUCCESS ,None 
        except Exception as save_err :
             self .logger (f"->>Save Fail for '{final_filename_on_disk }': {save_err }")
             if os .path .exists (final_save_path ):
                  try :os .remove (final_save_path );
                  except OSError :self .logger (f"  -> Failed to remove partially saved file: {final_save_path }")


             return 0 ,1 ,final_filename_saved_for_return ,was_original_name_kept_flag ,FILE_DOWNLOAD_STATUS_SKIPPED ,None 
        finally :
            if data_to_write_io and hasattr (data_to_write_io ,'close'):
                data_to_write_io .close ()

    def process (self ):
        if self ._check_pause (f"Post processing for ID {self .post .get ('id','N/A')}"):return 0 ,0 ,[],[],[],None 
        if self .check_cancel ():return 0 ,0 ,[],[],[],None 
        current_character_filters =self ._get_current_character_filters ()
        kept_original_filenames_for_log =[]
        retryable_failures_this_post =[]
        permanent_failures_this_post =[]
        total_downloaded_this_post =0 
        total_skipped_this_post =0 
        history_data_for_this_post =None 

        parsed_api_url =urlparse (self .api_url_input )
        referer_url =f"https://{parsed_api_url .netloc }/"
        headers ={'User-Agent':'Mozilla/5.0','Referer':referer_url ,'Accept':'*/*'}
        link_pattern =re .compile (r"""<a\s+.*?href=["'](https?://[^"']+)["'][^>]*>(.*?)</a>""",
        re .IGNORECASE |re .DOTALL )
        post_data =self .post 
        post_title =post_data .get ('title','')or 'untitled_post'
        post_id =post_data .get ('id','unknown_id')
        post_main_file_info =post_data .get ('file')
        post_attachments =post_data .get ('attachments',[])

        effective_unwanted_keywords_for_folder_naming =self .unwanted_keywords .copy ()
        is_full_creator_download_no_char_filter =not self .target_post_id_from_initial_url and not current_character_filters 
        if is_full_creator_download_no_char_filter and self .creator_download_folder_ignore_words :
            self .logger (f"   Applying creator download specific folder ignore words ({len (self .creator_download_folder_ignore_words )} words).")
            effective_unwanted_keywords_for_folder_naming .update (self .creator_download_folder_ignore_words )

        post_content_html =post_data .get ('content','')
        self .logger (f"\n--- Processing Post {post_id } ('{post_title [:50 ]}...') (Thread: {threading .current_thread ().name }) ---")
        num_potential_files_in_post =len (post_attachments or [])+(1 if post_main_file_info and post_main_file_info .get ('path')else 0 )
        post_is_candidate_by_title_char_match =False 
        char_filter_that_matched_title =None 
        post_is_candidate_by_comment_char_match =False 
        post_is_candidate_by_file_char_match_in_comment_scope =False 
        char_filter_that_matched_file_in_comment_scope =None 
        char_filter_that_matched_comment =None 
        if current_character_filters and (self .char_filter_scope ==CHAR_SCOPE_TITLE or self .char_filter_scope ==CHAR_SCOPE_BOTH ):
            if self ._check_pause (f"Character title filter for post {post_id }"):return 0 ,num_potential_files_in_post ,[],[],[],None 
            for idx ,filter_item_obj in enumerate (current_character_filters ):
                if self .check_cancel ():break 
                terms_to_check_for_title =list (filter_item_obj ["aliases"])
                if filter_item_obj ["is_group"]:
                    if filter_item_obj ["name"]not in terms_to_check_for_title :
                        terms_to_check_for_title .append (filter_item_obj ["name"])
                unique_terms_for_title_check =list (set (terms_to_check_for_title ))
                for term_to_match in unique_terms_for_title_check :
                    match_found_for_term =is_title_match_for_character (post_title ,term_to_match )
                    if match_found_for_term :
                        post_is_candidate_by_title_char_match =True 
                        char_filter_that_matched_title =filter_item_obj 
                        self .logger (f"   Post title matches char filter term '{term_to_match }' (from group/name '{filter_item_obj ['name']}', Scope: {self .char_filter_scope }). Post is candidate.")
                        break 
                if post_is_candidate_by_title_char_match :break 
        all_files_from_post_api_for_char_check =[]
        api_file_domain_for_char_check =urlparse (self .api_url_input ).netloc 
        if not api_file_domain_for_char_check or not any (d in api_file_domain_for_char_check .lower ()for d in ['kemono.su','kemono.party','coomer.su','coomer.party']):
            api_file_domain_for_char_check ="kemono.su"if "kemono"in self .service .lower ()else "coomer.party"
        if post_main_file_info and isinstance (post_main_file_info ,dict )and post_main_file_info .get ('path'):
            original_api_name =post_main_file_info .get ('name')or os .path .basename (post_main_file_info ['path'].lstrip ('/'))
            if original_api_name :
                all_files_from_post_api_for_char_check .append ({'_original_name_for_log':original_api_name })
        for att_info in post_attachments :
            if isinstance (att_info ,dict )and att_info .get ('path'):
                original_api_att_name =att_info .get ('name')or os .path .basename (att_info ['path'].lstrip ('/'))
                if original_api_att_name :
                    all_files_from_post_api_for_char_check .append ({'_original_name_for_log':original_api_att_name })
        if current_character_filters and self .char_filter_scope ==CHAR_SCOPE_COMMENTS :
            self .logger (f"   [Char Scope: Comments] Phase 1: Checking post files for matches before comments for post ID '{post_id }'.")
            if self ._check_pause (f"File check (comments scope) for post {post_id }"):return 0 ,num_potential_files_in_post ,[],[],[],None 
            for file_info_item in all_files_from_post_api_for_char_check :
                if self .check_cancel ():break 
                current_api_original_filename_for_check =file_info_item .get ('_original_name_for_log')
                if not current_api_original_filename_for_check :continue 
                for filter_item_obj in current_character_filters :
                    terms_to_check =list (filter_item_obj ["aliases"])
                    if filter_item_obj ["is_group"]and filter_item_obj ["name"]not in terms_to_check :
                        terms_to_check .append (filter_item_obj ["name"])
                    for term_to_match in terms_to_check :
                        if is_filename_match_for_character (current_api_original_filename_for_check ,term_to_match ):
                            post_is_candidate_by_file_char_match_in_comment_scope =True 
                            char_filter_that_matched_file_in_comment_scope =filter_item_obj 
                            self .logger (f"     Match Found (File in Comments Scope): File '{current_api_original_filename_for_check }' matches char filter term '{term_to_match }' (from group/name '{filter_item_obj ['name']}'). Post is candidate.")
                            break 
                    if post_is_candidate_by_file_char_match_in_comment_scope :break 
                if post_is_candidate_by_file_char_match_in_comment_scope :break 
            self .logger (f"   [Char Scope: Comments] Phase 1 Result: post_is_candidate_by_file_char_match_in_comment_scope = {post_is_candidate_by_file_char_match_in_comment_scope }")
        if current_character_filters and self .char_filter_scope ==CHAR_SCOPE_COMMENTS :
            if not post_is_candidate_by_file_char_match_in_comment_scope :
                if self ._check_pause (f"Comment check for post {post_id }"):return 0 ,num_potential_files_in_post ,[],[],[],None 
                self .logger (f"   [Char Scope: Comments] Phase 2: No file match found. Checking post comments for post ID '{post_id }'.")
                try :
                    parsed_input_url_for_comments =urlparse (self .api_url_input )
                    api_domain_for_comments =parsed_input_url_for_comments .netloc 
                    if not any (d in api_domain_for_comments .lower ()for d in ['kemono.su','kemono.party','coomer.su','coomer.party']):
                        self .logger (f"⚠️ Unrecognized domain '{api_domain_for_comments }' for comment API. Defaulting based on service.")
                        api_domain_for_comments ="kemono.su"if "kemono"in self .service .lower ()else "coomer.party"
                    comments_data =fetch_post_comments (
                    api_domain_for_comments ,self .service ,self .user_id ,post_id ,
                    headers ,self .logger ,self .cancellation_event ,self .pause_event ,
                    cookies_dict =prepare_cookies_for_request (
                    self .use_cookie ,self .cookie_text ,self .selected_cookie_file ,self .app_base_dir ,self .logger 
                    )
                    )
                    if comments_data :
                        self .logger (f"     Fetched {len (comments_data )} comments for post {post_id }.")
                        for comment_item_idx ,comment_item in enumerate (comments_data ):
                            if self .check_cancel ():break 
                            raw_comment_content =comment_item .get ('content','')
                            if not raw_comment_content :continue 
                            cleaned_comment_text =strip_html_tags (raw_comment_content )
                            if not cleaned_comment_text .strip ():continue 
                            for filter_item_obj in current_character_filters :
                                terms_to_check_comment =list (filter_item_obj ["aliases"])
                                if filter_item_obj ["is_group"]and filter_item_obj ["name"]not in terms_to_check_comment :
                                    terms_to_check_comment .append (filter_item_obj ["name"])
                                for term_to_match_comment in terms_to_check_comment :
                                    if is_title_match_for_character (cleaned_comment_text ,term_to_match_comment ):
                                        post_is_candidate_by_comment_char_match =True 
                                        char_filter_that_matched_comment =filter_item_obj 
                                        self .logger (f"     Match Found (Comment in Comments Scope): Comment in post {post_id } matches char filter term '{term_to_match_comment }' (from group/name '{filter_item_obj ['name']}'). Post is candidate.")
                                        self .logger (f"       Matching comment (first 100 chars): '{cleaned_comment_text [:100 ]}...'")
                                        break 
                                if post_is_candidate_by_comment_char_match :break 
                            if post_is_candidate_by_comment_char_match :break 
                    else :
                        self .logger (f"     No comments found or fetched for post {post_id } to check against character filters.")
                except RuntimeError as e_fetch_comment :
                    self .logger (f"   ⚠️ Error fetching or processing comments for post {post_id }: {e_fetch_comment }")
                except Exception as e_generic_comment :
                    self .logger (f"   ❌ Unexpected error during comment processing for post {post_id }: {e_generic_comment }\n{traceback .format_exc (limit =2 )}")
                self .logger (f"   [Char Scope: Comments] Phase 2 Result: post_is_candidate_by_comment_char_match = {post_is_candidate_by_comment_char_match }")
            else :
                self .logger (f"   [Char Scope: Comments] Phase 2: Skipped comment check for post ID '{post_id }' because a file match already made it a candidate.")
        if current_character_filters :
            if self .char_filter_scope ==CHAR_SCOPE_TITLE and not post_is_candidate_by_title_char_match :
                self .logger (f"   -> Skip Post (Scope: Title - No Char Match): Title '{post_title [:50 ]}' does not match character filters.")
                self ._emit_signal ('missed_character_post',post_title ,"No title match for character filter")
                return 0 ,num_potential_files_in_post ,[],[],[],None 
            if self .char_filter_scope ==CHAR_SCOPE_COMMENTS and not post_is_candidate_by_file_char_match_in_comment_scope and not post_is_candidate_by_comment_char_match :
                self .logger (f"   -> Skip Post (Scope: Comments - No Char Match in Comments): Post ID '{post_id }', Title '{post_title [:50 ]}...'")
                if self .emitter and hasattr (self .emitter ,'missed_character_post_signal'):
                    self ._emit_signal ('missed_character_post',post_title ,"No character match in files or comments (Comments scope)")
                return 0 ,num_potential_files_in_post ,[],[],[],None 
        if self .skip_words_list and (self .skip_words_scope ==SKIP_SCOPE_POSTS or self .skip_words_scope ==SKIP_SCOPE_BOTH ):
            if self ._check_pause (f"Skip words (post title) for post {post_id }"):return 0 ,num_potential_files_in_post ,[],[],[],None 
            post_title_lower =post_title .lower ()
            for skip_word in self .skip_words_list :
                if skip_word .lower ()in post_title_lower :
                    self .logger (f"   -> Skip Post (Keyword in Title '{skip_word }'): '{post_title [:50 ]}...'. Scope: {self .skip_words_scope }")
                    return 0 ,num_potential_files_in_post ,[],[],[],None 
        if not self .extract_links_only and self .manga_mode_active and current_character_filters and (self .char_filter_scope ==CHAR_SCOPE_TITLE or self .char_filter_scope ==CHAR_SCOPE_BOTH )and not post_is_candidate_by_title_char_match :
            self .logger (f"   -> Skip Post (Manga Mode with Title/Both Scope - No Title Char Match): Title '{post_title [:50 ]}' doesn't match filters.")
            self ._emit_signal ('missed_character_post',post_title ,"Manga Mode: No title match for character filter (Title/Both scope)")
            return 0 ,num_potential_files_in_post ,[],[],[],None 
        if not isinstance (post_attachments ,list ):
            self .logger (f"⚠️ Corrupt attachment data for post {post_id } (expected list, got {type (post_attachments )}). Skipping attachments.")
            post_attachments =[]
        base_folder_names_for_post_content =[]
        determined_post_save_path_for_history =self .override_output_dir if self .override_output_dir else self .download_root 
        if not self .extract_links_only and self .use_subfolders :
            if self ._check_pause (f"Subfolder determination for post {post_id }"):return 0 ,num_potential_files_in_post ,[],[],[],None 
            primary_char_filter_for_folder =None 
            log_reason_for_folder =""
            if self .char_filter_scope ==CHAR_SCOPE_COMMENTS and char_filter_that_matched_comment :
                if post_is_candidate_by_file_char_match_in_comment_scope and char_filter_that_matched_file_in_comment_scope :
                    primary_char_filter_for_folder =char_filter_that_matched_file_in_comment_scope 
                    log_reason_for_folder ="Matched char filter in filename (Comments scope)"
                elif post_is_candidate_by_comment_char_match and char_filter_that_matched_comment :
                    primary_char_filter_for_folder =char_filter_that_matched_comment 
                    log_reason_for_folder ="Matched char filter in comments (Comments scope, no file match)"
            elif (self .char_filter_scope ==CHAR_SCOPE_TITLE or self .char_filter_scope ==CHAR_SCOPE_BOTH )and char_filter_that_matched_title :
                primary_char_filter_for_folder =char_filter_that_matched_title 
                log_reason_for_folder ="Matched char filter in title"
            if primary_char_filter_for_folder :
                base_folder_names_for_post_content =[clean_folder_name (primary_char_filter_for_folder ["name"])]
                cleaned_primary_folder_name =clean_folder_name (primary_char_filter_for_folder ["name"])
                if cleaned_primary_folder_name .lower ()in effective_unwanted_keywords_for_folder_naming and cleaned_primary_folder_name .lower ()!="untitled_folder":
                    self .logger (f"   ⚠️ Primary char filter folder name '{cleaned_primary_folder_name }' is in ignore list. Using generic name.")
                    base_folder_names_for_post_content =["Generic Post Content"]
                else :
                    base_folder_names_for_post_content =[cleaned_primary_folder_name ]
                self .logger (f"   Base folder name(s) for post content ({log_reason_for_folder }): {', '.join (base_folder_names_for_post_content )}")
            elif not current_character_filters :

                derived_folders_from_title_via_known_txt =match_folders_from_title (
                post_title ,
                self .known_names ,
                effective_unwanted_keywords_for_folder_naming 
                )

                valid_derived_folders_from_title_known_txt =[
                name for name in derived_folders_from_title_via_known_txt 
                if name and name .strip ()and name .lower ()!="untitled_folder"
                ]

                if valid_derived_folders_from_title_known_txt :
                    base_folder_names_for_post_content .extend (valid_derived_folders_from_title_known_txt )
                    self .logger (f"   Base folder name(s) for post content (Derived from Known.txt & Post Title): {', '.join (base_folder_names_for_post_content )}")
                else :




                    candidate_name_from_title_basic_clean =extract_folder_name_from_title (
                    post_title ,
                    FOLDER_NAME_STOP_WORDS 
                    )

                    title_is_only_creator_ignored_words =False 
                    if candidate_name_from_title_basic_clean and candidate_name_from_title_basic_clean .lower ()!="untitled_folder"and self .creator_download_folder_ignore_words :

                        candidate_title_words ={word .lower ()for word in candidate_name_from_title_basic_clean .split ()}
                        if candidate_title_words and candidate_title_words .issubset (self .creator_download_folder_ignore_words ):
                            title_is_only_creator_ignored_words =True 
                            self .logger (f"   Title-derived name '{candidate_name_from_title_basic_clean }' consists only of creator-specific ignore words.")

                    if title_is_only_creator_ignored_words :

                        self .logger (f"   Attempting Known.txt match on filenames as title was poor ('{candidate_name_from_title_basic_clean }').")

                        filenames_to_check =[
                        f_info ['_original_name_for_log']for f_info in all_files_from_post_api_for_char_check 
                        if f_info .get ('_original_name_for_log')
                        ]

                        derived_folders_from_filenames_known_txt =set ()
                        if filenames_to_check :
                            for fname in filenames_to_check :
                                matches =match_folders_from_title (
                                fname ,
                                self .known_names ,
                                effective_unwanted_keywords_for_folder_naming 
                                )
                                for m in matches :
                                    if m and m .strip ()and m .lower ()!="untitled_folder":
                                        derived_folders_from_filenames_known_txt .add (m )

                        if derived_folders_from_filenames_known_txt :
                            base_folder_names_for_post_content .extend (list (derived_folders_from_filenames_known_txt ))
                            self .logger (f"   Base folder name(s) for post content (Derived from Known.txt & Filenames): {', '.join (base_folder_names_for_post_content )}")
                        else :
                            final_title_extract =extract_folder_name_from_title (
                            post_title ,effective_unwanted_keywords_for_folder_naming 
                            )
                            base_folder_names_for_post_content .append (final_title_extract )
                            self .logger (f"   No Known.txt match from filenames. Using title-derived name (with full ignore list): '{final_title_extract }'")
                    else :
                        extracted_name_from_title_full_ignore =extract_folder_name_from_title (
                        post_title ,effective_unwanted_keywords_for_folder_naming 
                        )
                        base_folder_names_for_post_content .append (extracted_name_from_title_full_ignore )
                        self .logger (f"   Base folder name(s) for post content (Generic title parsing - title not solely creator-ignored words): {', '.join (base_folder_names_for_post_content )}")

                base_folder_names_for_post_content =[
                name for name in base_folder_names_for_post_content if name and name .strip ()
                ]
                if not base_folder_names_for_post_content :
                    final_fallback_name =clean_folder_name (post_title if post_title and post_title .strip ()else "Generic Post Content")
                    base_folder_names_for_post_content =[final_fallback_name ]
                    self .logger (f"   Ultimate fallback folder name: {final_fallback_name }")

            if base_folder_names_for_post_content :
                determined_post_save_path_for_history =os .path .join (determined_post_save_path_for_history ,base_folder_names_for_post_content [0 ])

        if not self .extract_links_only and self .use_post_subfolders :
            cleaned_post_title_for_sub =clean_folder_name (post_title )
            post_id_for_fallback =self .post .get ('id','unknown_id')


            if not cleaned_post_title_for_sub or cleaned_post_title_for_sub =="untitled_folder":
                self .logger (f"   ⚠️ Post title '{post_title }' resulted in a generic subfolder name. Using 'post_{post_id_for_fallback }' as base.")
                original_cleaned_post_title_for_sub =f"post_{post_id_for_fallback }"
            else :
                original_cleaned_post_title_for_sub =cleaned_post_title_for_sub 

            if self.use_date_prefix_for_subfolder:
                # Prioritize 'published' date, fall back to 'added' date
                published_date_str = self.post.get('published') or self.post.get('added')
                if published_date_str:
                    try:
                        # Extract just the date part (YYYY-MM-DD)
                        date_prefix = published_date_str.split('T')[0]
                        # Prepend the date to the folder name
                        original_cleaned_post_title_for_sub = f"{date_prefix} {original_cleaned_post_title_for_sub}"
                        self.logger(f"   ℹ️ Applying date prefix to subfolder: '{original_cleaned_post_title_for_sub}'")
                    except Exception as e:
                        self.logger(f"   ⚠️ Could not parse date '{published_date_str}' for prefix. Using original name. Error: {e}")
                else:
                    self.logger("   ⚠️ 'Date Prefix' is checked, but post has no 'published' or 'added' date. Omitting prefix.")

            base_path_for_post_subfolder =determined_post_save_path_for_history 

            suffix_counter =0 
            final_post_subfolder_name =""

            while True :
                if suffix_counter ==0 :
                    name_candidate =original_cleaned_post_title_for_sub 
                else :
                    name_candidate =f"{original_cleaned_post_title_for_sub }_{suffix_counter }"

                potential_post_subfolder_path =os .path .join (base_path_for_post_subfolder ,name_candidate )

                try :
                    os .makedirs (potential_post_subfolder_path ,exist_ok =False )
                    final_post_subfolder_name =name_candidate 
                    if suffix_counter >0 :
                         self .logger (f"   Post subfolder name conflict: Using '{final_post_subfolder_name }' instead of '{original_cleaned_post_title_for_sub }' to avoid mixing posts.")
                    break 
                except FileExistsError :
                    suffix_counter +=1 
                    if suffix_counter >100 :
                        self .logger (f"   ⚠️ Exceeded 100 attempts to find unique subfolder name for '{original_cleaned_post_title_for_sub }'. Using UUID.")
                        final_post_subfolder_name =f"{original_cleaned_post_title_for_sub }_{uuid .uuid4 ().hex [:8 ]}"
                        os .makedirs (os .path .join (base_path_for_post_subfolder ,final_post_subfolder_name ),exist_ok =True )
                        break 
                except OSError as e_mkdir :
                    self .logger (f"   ❌ Error creating directory '{potential_post_subfolder_path }': {e_mkdir }. Files for this post might be saved in parent or fail.")
                    final_post_subfolder_name =original_cleaned_post_title_for_sub 
                    break 

            determined_post_save_path_for_history =os .path .join (base_path_for_post_subfolder ,final_post_subfolder_name )

        if not self .extract_links_only and self .use_subfolders and self .skip_words_list :
            if self ._check_pause (f"Folder keyword skip check for post {post_id }"):return 0 ,num_potential_files_in_post ,[],[],[],None 
            for folder_name_to_check in base_folder_names_for_post_content :
                if not folder_name_to_check :continue 
                if any (skip_word .lower ()in folder_name_to_check .lower ()for skip_word in self .skip_words_list ):
                    matched_skip =next ((sw for sw in self .skip_words_list if sw .lower ()in folder_name_to_check .lower ()),"unknown_skip_word")
                    self .logger (f"   -> Skip Post (Folder Keyword): Potential folder '{folder_name_to_check }' contains '{matched_skip }'.")
                    return 0 ,num_potential_files_in_post ,[],[],[],None 
        if (self .show_external_links or self .extract_links_only )and post_content_html :
            if self ._check_pause (f"External link extraction for post {post_id }"):return 0 ,num_potential_files_in_post ,[],[],[],None 
            try :
                mega_key_pattern =re .compile (r'\b([a-zA-Z0-9_-]{43}|[a-zA-Z0-9_-]{22})\b')
                unique_links_data ={}
                for match in link_pattern .finditer (post_content_html ):
                    link_url =match .group (1 ).strip ()
                    link_url =html .unescape (link_url )
                    link_inner_text =match .group (2 )
                    if not any (ext in link_url .lower ()for ext in ['.css','.js','.ico','.xml','.svg'])and not link_url .startswith ('javascript:')and link_url not in unique_links_data :
                        clean_link_text =re .sub (r'<.*?>','',link_inner_text )
                        clean_link_text =html .unescape (clean_link_text ).strip ()
                        display_text =clean_link_text if clean_link_text else "[Link]"
                        unique_links_data [link_url ]=display_text 
                links_emitted_count =0 
                scraped_platforms ={'kemono','coomer','patreon'}
                for link_url ,link_text in unique_links_data .items ():
                    platform =get_link_platform (link_url )
                    decryption_key_found =""
                    if platform =='mega':
                        parsed_mega_url =urlparse (link_url )
                        if parsed_mega_url .fragment :
                            potential_key_from_fragment =parsed_mega_url .fragment .split ('!')[-1 ]
                            if mega_key_pattern .fullmatch (potential_key_from_fragment ):
                                decryption_key_found =potential_key_from_fragment 

                        if not decryption_key_found and link_text :
                            key_match_in_text =mega_key_pattern .search (link_text )
                            if key_match_in_text :
                                decryption_key_found =key_match_in_text .group (1 )
                        if not decryption_key_found and self .extract_links_only and post_content_html :
                            key_match_in_content =mega_key_pattern .search (strip_html_tags (post_content_html ))
                            if key_match_in_content :
                                decryption_key_found =key_match_in_content .group (1 )
                    if platform not in scraped_platforms :
                        self ._emit_signal ('external_link',post_title ,link_text ,link_url ,platform ,decryption_key_found or "")
                        links_emitted_count +=1 
                if links_emitted_count >0 :self .logger (f"   🔗 Found {links_emitted_count } potential external link(s) in post content.")
            except Exception as e :self .logger (f"⚠️ Error parsing post content for links: {e }\n{traceback .format_exc (limit =2 )}")
        if self .extract_links_only :
            self .logger (f"   Extract Links Only mode: Finished processing post {post_id } for links.")
            return 0 ,0 ,[],[],[],None 
        all_files_from_post_api =[]
        api_file_domain =urlparse (self .api_url_input ).netloc 
        if not api_file_domain or not any (d in api_file_domain .lower ()for d in ['kemono.su','kemono.party','coomer.su','coomer.party']):
            api_file_domain ="kemono.su"if "kemono"in self .service .lower ()else "coomer.party"
        if post_main_file_info and isinstance (post_main_file_info ,dict )and post_main_file_info .get ('path'):
            file_path =post_main_file_info ['path'].lstrip ('/')
            original_api_name =post_main_file_info .get ('name')or os .path .basename (file_path )
            if original_api_name :
                all_files_from_post_api .append ({
                'url':f"https://{api_file_domain }{file_path }"if file_path .startswith ('/')else f"https://{api_file_domain }/data/{file_path }",
                'name':original_api_name ,
                '_original_name_for_log':original_api_name ,
                '_is_thumbnail':is_image (original_api_name )
                })
            else :self .logger (f"   ⚠️ Skipping main file for post {post_id }: Missing name (Path: {file_path })")
        for idx ,att_info in enumerate (post_attachments ):
            if isinstance (att_info ,dict )and att_info .get ('path'):
                att_path =att_info ['path'].lstrip ('/')
                original_api_att_name =att_info .get ('name')or os .path .basename (att_path )
                if original_api_att_name :
                    all_files_from_post_api .append ({
                    'url':f"https://{api_file_domain }{att_path }"if att_path .startswith ('/')else f"https://{api_file_domain }/data/{att_path }",
                    'name':original_api_att_name ,
                    '_original_name_for_log':original_api_att_name ,
                    '_is_thumbnail':is_image (original_api_att_name )
                    })
                else :self .logger (f"   ⚠️ Skipping attachment {idx +1 } for post {post_id }: Missing name (Path: {att_path })")
            else :self .logger (f"   ⚠️ Skipping invalid attachment {idx +1 } for post {post_id }: {str (att_info )[:100 ]}")
        if self .scan_content_for_images and post_content_html and not self .extract_links_only :
            self .logger (f"   Scanning post content for additional image URLs (Post ID: {post_id })...")
            parsed_input_url =urlparse (self .api_url_input )
            base_url_for_relative_paths =f"{parsed_input_url .scheme }://{parsed_input_url .netloc }"
            img_ext_pattern ="|".join (ext .lstrip ('.')for ext in IMAGE_EXTENSIONS )
            direct_url_pattern_str =r"""(?i)\b(https?://[^\s"'<>\[\]\{\}\|\^\\^~\[\]`]+\.(?:"""+img_ext_pattern +r"""))\b"""
            img_tag_src_pattern_str =r"""<img\s+[^>]*?src\s*=\s*["']([^"']+)["']"""
            found_image_sources =set ()
            for direct_url_match in re .finditer (direct_url_pattern_str ,post_content_html ):
                found_image_sources .add (direct_url_match .group (1 ))
            for img_tag_match in re .finditer (img_tag_src_pattern_str ,post_content_html ,re .IGNORECASE ):
                src_attr =img_tag_match .group (1 ).strip ()
                src_attr =html .unescape (src_attr )
                if not src_attr :continue 
                resolved_src_url =""
                if src_attr .startswith (('http://','https://')):
                    resolved_src_url =src_attr 
                elif src_attr .startswith ('//'):
                    resolved_src_url =f"{parsed_input_url .scheme }:{src_attr }"
                elif src_attr .startswith ('/'):
                    resolved_src_url =f"{base_url_for_relative_paths }{src_attr }"
                if resolved_src_url :
                    parsed_resolved_url =urlparse (resolved_src_url )
                    if any (parsed_resolved_url .path .lower ().endswith (ext )for ext in IMAGE_EXTENSIONS ):
                        found_image_sources .add (resolved_src_url )
            if found_image_sources :
                self .logger (f"      Found {len (found_image_sources )} potential image URLs/sources in content.")
                existing_urls_in_api_list ={f_info ['url']for f_info in all_files_from_post_api }
                for found_url in found_image_sources :
                    if self .check_cancel ():break 
                    if found_url in existing_urls_in_api_list :
                        self .logger (f"         Skipping URL from content (already in API list or previously added from content): {found_url [:70 ]}...")
                        continue 
                    try :
                        parsed_found_url =urlparse (found_url )
                        url_filename =os .path .basename (parsed_found_url .path )
                        if not url_filename or not is_image (url_filename ):
                            self .logger (f"         Skipping URL from content (no filename part or not an image extension): {found_url [:70 ]}...")
                            continue 
                        self .logger (f"      Adding image from content: {url_filename } (URL: {found_url [:70 ]}...)")
                        all_files_from_post_api .append ({
                        'url':found_url ,
                        'name':url_filename ,
                        '_original_name_for_log':url_filename ,
                        '_is_thumbnail':False ,
                        '_from_content_scan':True 
                        })
                        existing_urls_in_api_list .add (found_url )
                    except Exception as e_url_parse :
                        self .logger (f"         Error processing URL from content '{found_url [:70 ]}...': {e_url_parse }")
            else :
                self .logger (f"      No additional image URLs found in post content scan for post {post_id }.")
        if self .download_thumbnails :
            if self .scan_content_for_images :
                self .logger (f"   Mode: 'Download Thumbnails Only' + 'Scan Content for Images' active. Prioritizing images from content scan for post {post_id }.")
                all_files_from_post_api =[finfo for finfo in all_files_from_post_api if finfo .get ('_from_content_scan')]
                if not all_files_from_post_api :
                    self .logger (f"   -> No images found via content scan for post {post_id } in this combined mode.")
                    return 0 ,0 ,[],[],[],None 
            else :
                self .logger (f"   Mode: 'Download Thumbnails Only' active. Filtering for API thumbnails for post {post_id }.")
                all_files_from_post_api =[finfo for finfo in all_files_from_post_api if finfo .get ('_is_thumbnail')]
                if not all_files_from_post_api :
                    self .logger (f"   -> No API image thumbnails found for post {post_id } in thumbnail-only mode.")
                    return 0 ,0 ,[],[],[],None 
        if self .manga_mode_active and self .manga_filename_style ==STYLE_DATE_BASED :
            def natural_sort_key_for_files (file_api_info ):
                name =file_api_info .get ('_original_name_for_log','').lower ()
                return [int (text )if text .isdigit ()else text for text in re .split ('([0-9]+)',name )]
            all_files_from_post_api .sort (key =natural_sort_key_for_files )
            self .logger (f"   Manga Date Mode: Sorted {len (all_files_from_post_api )} files within post {post_id } by original name for sequential numbering.")
        if not all_files_from_post_api :
            self .logger (f"   No files found to download for post {post_id }.")
            return 0 ,0 ,[],[],[],None 
        files_to_download_info_list =[]
        processed_original_filenames_in_this_post =set ()
        for file_info in all_files_from_post_api :
            current_api_original_filename =file_info .get ('_original_name_for_log')
            if current_api_original_filename in processed_original_filenames_in_this_post :
                self .logger (f"   -> Skip Duplicate Original Name (within post {post_id }): '{current_api_original_filename }' already processed/listed for this post.")
                total_skipped_this_post +=1 
            else :
                files_to_download_info_list .append (file_info )
                if current_api_original_filename :
                    processed_original_filenames_in_this_post .add (current_api_original_filename )
        if not files_to_download_info_list :
            self .logger (f"   All files for post {post_id } were duplicate original names or skipped earlier.")
            return 0 ,total_skipped_this_post ,[],[],[],None 

        self .logger (f"   Identified {len (files_to_download_info_list )} unique original file(s) for potential download from post {post_id }.")
        with ThreadPoolExecutor (max_workers =self .num_file_threads ,thread_name_prefix =f'P{post_id }File_')as file_pool :
            futures_list =[]
            for file_idx ,file_info_to_dl in enumerate (files_to_download_info_list ):
                if self ._check_pause (f"File processing loop for post {post_id }, file {file_idx }"):break 
                if self .check_cancel ():break 
                current_api_original_filename =file_info_to_dl .get ('_original_name_for_log')
                file_is_candidate_by_char_filter_scope =False 
                char_filter_info_that_matched_file =None 
                if not current_character_filters :
                    file_is_candidate_by_char_filter_scope =True 
                else :
                    if self .char_filter_scope ==CHAR_SCOPE_FILES :
                        for filter_item_obj in current_character_filters :
                            terms_to_check_for_file =list (filter_item_obj ["aliases"])
                            if filter_item_obj ["is_group"]and filter_item_obj ["name"]not in terms_to_check_for_file :
                                terms_to_check_for_file .append (filter_item_obj ["name"])
                            unique_terms_for_file_check =list (set (terms_to_check_for_file ))
                            for term_to_match in unique_terms_for_file_check :
                                if is_filename_match_for_character (current_api_original_filename ,term_to_match ):
                                    file_is_candidate_by_char_filter_scope =True 
                                    char_filter_info_that_matched_file =filter_item_obj 
                                    self .logger (f"   File '{current_api_original_filename }' matches char filter term '{term_to_match }' (from '{filter_item_obj ['name']}'). Scope: Files.")
                                    break 
                            if file_is_candidate_by_char_filter_scope :break 
                    elif self .char_filter_scope ==CHAR_SCOPE_TITLE :
                        if post_is_candidate_by_title_char_match :
                            file_is_candidate_by_char_filter_scope =True 
                            char_filter_info_that_matched_file =char_filter_that_matched_title 
                            self .logger (f"   File '{current_api_original_filename }' is candidate because post title matched. Scope: Title.")
                    elif self .char_filter_scope ==CHAR_SCOPE_BOTH :
                        if post_is_candidate_by_title_char_match :
                            file_is_candidate_by_char_filter_scope =True 
                            char_filter_info_that_matched_file =char_filter_that_matched_title 
                            self .logger (f"   File '{current_api_original_filename }' is candidate because post title matched. Scope: Both (Title part).")
                        else :
                            for filter_item_obj_both_file in current_character_filters :
                                terms_to_check_for_file_both =list (filter_item_obj_both_file ["aliases"])
                                if filter_item_obj_both_file ["is_group"]and filter_item_obj_both_file ["name"]not in terms_to_check_for_file_both :
                                    terms_to_check_for_file_both .append (filter_item_obj_both_file ["name"])
                                unique_terms_for_file_both_check =list (set (terms_to_check_for_file_both ))
                                for term_to_match in unique_terms_for_file_both_check :
                                    if is_filename_match_for_character (current_api_original_filename ,term_to_match ):
                                        file_is_candidate_by_char_filter_scope =True 
                                        char_filter_info_that_matched_file =filter_item_obj_both_file 
                                        self .logger (f"   File '{current_api_original_filename }' matches char filter term '{term_to_match }' (from '{filter_item_obj ['name']}'). Scope: Both (File part).")
                                        break 
                                if file_is_candidate_by_char_filter_scope :break 
                    elif self .char_filter_scope ==CHAR_SCOPE_COMMENTS :
                        if post_is_candidate_by_file_char_match_in_comment_scope :
                            file_is_candidate_by_char_filter_scope =True 
                            char_filter_info_that_matched_file =char_filter_that_matched_file_in_comment_scope 
                            self .logger (f"   File '{current_api_original_filename }' is candidate because a file in this post matched char filter (Overall Scope: Comments).")
                        elif post_is_candidate_by_comment_char_match :
                            file_is_candidate_by_char_filter_scope =True 
                            char_filter_info_that_matched_file =char_filter_that_matched_comment 
                            self .logger (f"   File '{current_api_original_filename }' is candidate because post comments matched char filter (Overall Scope: Comments).")
                if not file_is_candidate_by_char_filter_scope :
                    self .logger (f"   -> Skip File (Char Filter Scope '{self .char_filter_scope }'): '{current_api_original_filename }' no match.")
                    total_skipped_this_post +=1 
                    continue 


                target_base_folders_for_this_file_iteration =[]

                if current_character_filters :
                    char_title_subfolder_name =None 
                    if self .target_post_id_from_initial_url and self .custom_folder_name :
                        char_title_subfolder_name =self .custom_folder_name 
                    elif char_filter_info_that_matched_file :
                        char_title_subfolder_name =clean_folder_name (char_filter_info_that_matched_file ["name"])
                    elif char_filter_that_matched_title :
                        char_title_subfolder_name =clean_folder_name (char_filter_that_matched_title ["name"])
                    elif char_filter_that_matched_comment :
                         char_title_subfolder_name =clean_folder_name (char_filter_that_matched_comment ["name"])
                    if char_title_subfolder_name :
                        target_base_folders_for_this_file_iteration .append (char_title_subfolder_name )
                    else :
                        self .logger (f"⚠️ File '{current_api_original_filename }' candidate by char filter, but no folder name derived. Using post title.")
                        target_base_folders_for_this_file_iteration .append (clean_folder_name (post_title ))
                else :
                    if base_folder_names_for_post_content :
                        target_base_folders_for_this_file_iteration .extend (base_folder_names_for_post_content )
                    else :
                        target_base_folders_for_this_file_iteration .append (clean_folder_name (post_title ))

                if not target_base_folders_for_this_file_iteration :
                    target_base_folders_for_this_file_iteration .append (clean_folder_name (post_title if post_title else "Uncategorized_Post_Content"))

                for target_base_folder_name_for_instance in target_base_folders_for_this_file_iteration :
                    current_path_for_file_instance =self .override_output_dir if self .override_output_dir else self .download_root 
                    if self .use_subfolders and target_base_folder_name_for_instance :
                        current_path_for_file_instance =os .path .join (current_path_for_file_instance ,target_base_folder_name_for_instance )
                    if self .use_post_subfolders :

                        current_path_for_file_instance =os .path .join (current_path_for_file_instance ,final_post_subfolder_name )

                    manga_date_counter_to_pass =self .manga_date_file_counter_ref if self .manga_mode_active and self .manga_filename_style ==STYLE_DATE_BASED else None 
                    manga_global_counter_to_pass =self .manga_global_file_counter_ref if self .manga_mode_active and self .manga_filename_style ==STYLE_POST_TITLE_GLOBAL_NUMBERING else None 


                    folder_context_for_file =target_base_folder_name_for_instance if self .use_subfolders and target_base_folder_name_for_instance else clean_folder_name (post_title )

                    futures_list .append (file_pool .submit (
                    self ._download_single_file ,
                    file_info =file_info_to_dl ,
                    target_folder_path =current_path_for_file_instance ,
                    headers =headers ,original_post_id_for_log =post_id ,skip_event =self .skip_current_file_flag ,
                    post_title =post_title ,manga_date_file_counter_ref =manga_date_counter_to_pass ,
                    manga_global_file_counter_ref =manga_global_counter_to_pass ,folder_context_name_for_history =folder_context_for_file ,
                    file_index_in_post =file_idx ,num_files_in_this_post =len (files_to_download_info_list )
                    ))

            for future in as_completed (futures_list ):
                if self .check_cancel ():
                    for f_to_cancel in futures_list :
                        if not f_to_cancel .done ():
                            f_to_cancel .cancel ()
                    break 
                try :
                    dl_count ,skip_count ,actual_filename_saved ,original_kept_flag ,status ,details_for_dialog_or_retry =future .result ()
                    total_downloaded_this_post +=dl_count 
                    total_skipped_this_post +=skip_count 
                    if original_kept_flag and dl_count >0 and actual_filename_saved :
                        kept_original_filenames_for_log .append (actual_filename_saved )
                    if status ==FILE_DOWNLOAD_STATUS_FAILED_RETRYABLE_LATER and details_for_dialog_or_retry :
                        retryable_failures_this_post .append (details_for_dialog_or_retry )
                    elif status ==FILE_DOWNLOAD_STATUS_FAILED_PERMANENTLY_THIS_SESSION and details_for_dialog_or_retry :
                        permanent_failures_this_post .append (details_for_dialog_or_retry )
                except CancelledError :
                    self .logger (f"   File download task for post {post_id } was cancelled.")
                    total_skipped_this_post +=1 
                except Exception as exc_f :
                    self .logger (f"❌ File download task for post {post_id } resulted in error: {exc_f }")
                    total_skipped_this_post +=1 
        self ._emit_signal ('file_progress',"",None )

        # After a post's files are all processed, update the session file to mark this post as done.
        if self.session_file_path and self.session_lock:
            try:
                with self.session_lock:
                    if os.path.exists(self.session_file_path): # Only update if the session file exists
                        # Read current state
                        with open(self.session_file_path, 'r', encoding='utf-8') as f:
                            session_data = json.load(f)
                        
                        # Modify in memory
                        if not isinstance(session_data.get('download_state', {}).get('processed_post_ids'), list):
                            if 'download_state' not in session_data:
                                session_data['download_state'] = {}
                            session_data['download_state']['processed_post_ids'] = []
                        session_data['download_state']['processed_post_ids'].append(self.post.get('id'))
                        # Write to temp file and then atomically replace
                        temp_file_path = self.session_file_path + ".tmp"
                        with open(temp_file_path, 'w', encoding='utf-8') as f_tmp:
                            json.dump(session_data, f_tmp, indent=2)
                        os.replace(temp_file_path, self.session_file_path)
            except Exception as e:
                self.logger(f"⚠️ Could not update session file for post {post_id}: {e}")

        if not self .extract_links_only and (total_downloaded_this_post >0 or not (
        (current_character_filters and (
        (self .char_filter_scope ==CHAR_SCOPE_TITLE and not post_is_candidate_by_title_char_match )or 
        (self .char_filter_scope ==CHAR_SCOPE_COMMENTS and not post_is_candidate_by_file_char_match_in_comment_scope and not post_is_candidate_by_comment_char_match )
        ))or 
        (self .skip_words_list and (self .skip_words_scope ==SKIP_SCOPE_POSTS or self .skip_words_scope ==SKIP_SCOPE_BOTH )and any (sw .lower ()in post_title .lower ()for sw in self .skip_words_list ))
        )):
            top_file_name_for_history ="N/A"
            if post_main_file_info and post_main_file_info .get ('name'):
                top_file_name_for_history =post_main_file_info ['name']
            elif post_attachments and post_attachments [0 ].get ('name'):
                top_file_name_for_history =post_attachments [0 ]['name']

            history_data_for_this_post ={
            'post_title':post_title ,'post_id':post_id ,
            'top_file_name':top_file_name_for_history ,
            'num_files':num_potential_files_in_post ,
            'upload_date_str':post_data .get ('published')or post_data .get ('added')or "Unknown",
            'download_location':determined_post_save_path_for_history ,
            'service':self .service ,'user_id':self .user_id ,
            }
        if self .check_cancel ():self .logger (f"   Post {post_id } processing interrupted/cancelled.");
        else :self .logger (f"   Post {post_id } Summary: Downloaded={total_downloaded_this_post }, Skipped Files={total_skipped_this_post }")

        if not self .extract_links_only and self .use_post_subfolders and total_downloaded_this_post ==0 :

            path_to_check_for_emptiness =determined_post_save_path_for_history 
            try :
                if os .path .isdir (path_to_check_for_emptiness )and not os .listdir (path_to_check_for_emptiness ):
                    self .logger (f"   🗑️ Removing empty post-specific subfolder: '{path_to_check_for_emptiness }'")
                    os .rmdir (path_to_check_for_emptiness )
            except OSError as e_rmdir :
                self .logger (f"   ⚠️ Could not remove empty post-specific subfolder '{path_to_check_for_emptiness }': {e_rmdir }")

        return total_downloaded_this_post ,total_skipped_this_post ,kept_original_filenames_for_log ,retryable_failures_this_post ,permanent_failures_this_post ,history_data_for_this_post 

class DownloadThread (QThread ):
    progress_signal =pyqtSignal (str )
    add_character_prompt_signal =pyqtSignal (str )
    file_download_status_signal =pyqtSignal (bool )
    finished_signal =pyqtSignal (int ,int ,bool ,list )
    external_link_signal =pyqtSignal (str ,str ,str ,str ,str )
    file_successfully_downloaded_signal =pyqtSignal (dict )
    file_progress_signal =pyqtSignal (str ,object )
    retryable_file_failed_signal =pyqtSignal (list )
    missed_character_post_signal =pyqtSignal (str ,str )
    post_processed_for_history_signal =pyqtSignal (dict )
    final_history_entries_signal =pyqtSignal (list )
    permanent_file_failed_signal =pyqtSignal (list )
    def __init__ (self ,api_url_input ,output_dir ,known_names_copy ,
    cancellation_event ,
    pause_event ,filter_character_list =None ,dynamic_character_filter_holder =None ,
    filter_mode ='all',skip_zip =True ,skip_rar =True ,
    use_subfolders =True ,use_post_subfolders =False ,custom_folder_name =None ,compress_images =False ,
    download_thumbnails =False ,service =None ,user_id =None ,
    downloaded_files =None ,downloaded_file_hashes =None ,downloaded_files_lock =None ,downloaded_file_hashes_lock =None ,
    skip_words_list =None ,
    skip_words_scope =SKIP_SCOPE_FILES ,
    show_external_links =False ,
    extract_links_only =False ,
    num_file_threads_for_worker =1 ,
    skip_current_file_flag =None ,
    start_page =None ,end_page =None ,
    target_post_id_from_initial_url =None ,
    manga_mode_active =False ,
    unwanted_keywords =None ,
    manga_filename_style =STYLE_POST_TITLE ,
    char_filter_scope =CHAR_SCOPE_FILES ,
    remove_from_filename_words_list =None ,
    manga_date_prefix =MANGA_DATE_PREFIX_DEFAULT ,
    allow_multipart_download =True ,
    selected_cookie_file =None ,
    override_output_dir =None ,
    app_base_dir =None ,
    manga_date_file_counter_ref =None ,
    manga_global_file_counter_ref =None ,
    use_cookie =False ,
    scan_content_for_images =False ,
    creator_download_folder_ignore_words =None ,
    use_date_prefix_for_subfolder=False,
    cookie_text ="",
    session_file_path=None,
    session_lock=None,
    ):
        super ().__init__ ()
        self .api_url_input =api_url_input 
        self .output_dir =output_dir 
        self .known_names =list (known_names_copy )
        self .cancellation_event =cancellation_event 
        self .pause_event =pause_event 
        self .skip_current_file_flag =skip_current_file_flag 
        self .initial_target_post_id =target_post_id_from_initial_url 
        self .filter_character_list_objects_initial =filter_character_list if filter_character_list else []
        self .dynamic_filter_holder =dynamic_character_filter_holder 
        self .filter_mode =filter_mode 
        self .skip_zip =skip_zip 
        self .skip_rar =skip_rar 
        self .use_subfolders =use_subfolders 
        self .use_post_subfolders =use_post_subfolders 
        self .custom_folder_name =custom_folder_name 
        self .compress_images =compress_images 
        self .download_thumbnails =download_thumbnails 
        self .service =service 
        self .user_id =user_id 
        self .skip_words_list =skip_words_list if skip_words_list is not None else []
        self .skip_words_scope =skip_words_scope 
        self .downloaded_files =downloaded_files 
        self .downloaded_files_lock =downloaded_files_lock 
        self .downloaded_file_hashes =downloaded_file_hashes 
        self .downloaded_file_hashes_lock =downloaded_file_hashes_lock 
        self ._add_character_response =None 
        self .prompt_mutex =QMutex ()
        self .show_external_links =show_external_links 
        self .extract_links_only =extract_links_only 
        self .num_file_threads_for_worker =num_file_threads_for_worker 
        self .start_page =start_page 
        self .end_page =end_page 
        self .manga_mode_active =manga_mode_active 
        self .unwanted_keywords =unwanted_keywords if unwanted_keywords is not None else {'spicy','hd','nsfw','4k','preview','teaser','clip'}
        self .manga_filename_style =manga_filename_style 
        self .char_filter_scope =char_filter_scope 
        self .remove_from_filename_words_list =remove_from_filename_words_list 
        self .manga_date_prefix =manga_date_prefix 
        self .allow_multipart_download =allow_multipart_download 
        self .selected_cookie_file =selected_cookie_file 
        self .app_base_dir =app_base_dir 
        self .cookie_text =cookie_text 
        self .use_cookie =use_cookie 
        self .override_output_dir =override_output_dir 
        self .manga_date_file_counter_ref =manga_date_file_counter_ref 
        self .scan_content_for_images =scan_content_for_images 
        self .creator_download_folder_ignore_words =creator_download_folder_ignore_words 
        self.use_date_prefix_for_subfolder = use_date_prefix_for_subfolder
        self .manga_global_file_counter_ref =manga_global_file_counter_ref 
        self.session_file_path = session_file_path
        self.session_lock = session_lock
        self.history_candidates_buffer =deque (maxlen =8 )
        if self .compress_images and Image is None :
            self .logger ("⚠️ Image compression disabled: Pillow library not found (DownloadThread).")
            self .compress_images =False 
    def logger (self ,message ):
        self .progress_signal .emit (str (message ))
    def isInterruptionRequested (self ):
        return self .cancellation_event .is_set ()or super ().isInterruptionRequested ()
    def _check_pause_self (self ,context_message ="DownloadThread operation"):
        if self .pause_event and self .pause_event .is_set ():
            self .logger (f"   {context_message } paused...")
            while self .pause_event .is_set ():
                if self .isInterruptionRequested ():
                    self .logger (f"   {context_message } cancelled while paused.")
                    return True 
                time .sleep (0.5 )
            if not self .isInterruptionRequested ():self .logger (f"   {context_message } resumed.")
        return False 
    def skip_file (self ):
        if self .isRunning ()and self .skip_current_file_flag :
             self .logger ("⏭️ Skip requested for current file (single-thread mode).")
             self .skip_current_file_flag .set ()
        else :self .logger ("ℹ️ Skip file: No download active or skip flag not available for current context.")
    def run (self ):
        grand_total_downloaded_files =0 
        grand_total_skipped_files =0 
        grand_list_of_kept_original_filenames =[]
        was_process_cancelled =False 

        if self .manga_mode_active and self .manga_filename_style ==STYLE_DATE_BASED and not self .extract_links_only and self .manga_date_file_counter_ref is None :
            series_scan_dir =self .output_dir 
            if self .use_subfolders :
                if self .filter_character_list_objects_initial and self .filter_character_list_objects_initial [0 ]and self .filter_character_list_objects_initial [0 ].get ("name"):
                    series_folder_name =clean_folder_name (self .filter_character_list_objects_initial [0 ]["name"])
                    series_scan_dir =os .path .join (series_scan_dir ,series_folder_name )
                elif self .service and self .user_id :
                    creator_based_folder_name =clean_folder_name (str (self .user_id ))
                    series_scan_dir =os .path .join (series_scan_dir ,creator_based_folder_name )
            highest_num =0 
            if os .path .isdir (series_scan_dir ):
                self .logger (f"ℹ️ [Thread] Manga Date Mode: Scanning for existing files in '{series_scan_dir }'...")
                for dirpath ,_ ,filenames_in_dir in os .walk (series_scan_dir ):
                    for filename_to_check in filenames_in_dir :

                        prefix_to_check =clean_filename (self .manga_date_prefix .strip ())if self .manga_date_prefix and self .manga_date_prefix .strip ()else ""
                        name_part_to_match =filename_to_check 
                        if prefix_to_check and name_part_to_match .startswith (prefix_to_check ):
                            name_part_to_match =name_part_to_match [len (prefix_to_check ):].lstrip ()

                        base_name_no_ext =os .path .splitext (name_part_to_match )[0 ]
                        match =re .match (r"(\d+)",base_name_no_ext )
                        if match :highest_num =max (highest_num ,int (match .group (1 )))
            self .manga_date_file_counter_ref =[highest_num +1 ,threading .Lock ()]
            self .logger (f"ℹ️ [Thread] Manga Date Mode: Initialized date-based counter at {self .manga_date_file_counter_ref [0 ]}.")


        if self .manga_mode_active and self .manga_filename_style ==STYLE_POST_TITLE_GLOBAL_NUMBERING and not self .extract_links_only and self .manga_global_file_counter_ref is None :
            self .manga_global_file_counter_ref =[1 ,threading .Lock ()]
            self .logger (f"ℹ️ [Thread] Manga Title+GlobalNum Mode: Initialized global counter at {self .manga_global_file_counter_ref [0 ]}.")
        worker_signals_obj = PostProcessorSignals ()
        try :
            worker_signals_obj .progress_signal .connect (self .progress_signal )
            worker_signals_obj .file_download_status_signal .connect (self .file_download_status_signal )
            worker_signals_obj .file_progress_signal .connect (self .file_progress_signal )
            worker_signals_obj .external_link_signal .connect (self .external_link_signal )
            worker_signals_obj .missed_character_post_signal .connect (self .missed_character_post_signal )
            worker_signals_obj .file_successfully_downloaded_signal .connect (self .file_successfully_downloaded_signal )
            self .logger ("   Starting post fetch (single-threaded download process)...")
            post_generator =download_from_api (
            self .api_url_input ,
            logger =self .logger ,
            start_page =self .start_page ,
            end_page =self .end_page ,
            manga_mode =self .manga_mode_active ,
            cancellation_event =self .cancellation_event ,
            pause_event =self .pause_event ,
            use_cookie =self .use_cookie ,
            cookie_text =self .cookie_text ,
            selected_cookie_file =self .selected_cookie_file ,
            app_base_dir =self .app_base_dir ,
            manga_filename_style_for_sort_check =self .manga_filename_style if self .manga_mode_active else None 
            )
            for posts_batch_data in post_generator :
                if self ._check_pause_self ("Post batch processing"):was_process_cancelled =True ;break 
                if self .isInterruptionRequested ():was_process_cancelled =True ;break 
                for individual_post_data in posts_batch_data :
                    if self ._check_pause_self (f"Individual post processing for {individual_post_data .get ('id','N/A')}"):was_process_cancelled =True ;break 
                    if self .isInterruptionRequested ():was_process_cancelled =True ;break 
                    post_processing_worker =PostProcessorWorker (
                    post_data =individual_post_data ,
                    download_root =self .output_dir ,
                    known_names =self .known_names ,
                    filter_character_list =self .filter_character_list_objects_initial ,
                    dynamic_character_filter_holder =self .dynamic_filter_holder ,
                    unwanted_keywords =self .unwanted_keywords ,
                    filter_mode =self .filter_mode ,
                    skip_zip =self .skip_zip ,skip_rar =self .skip_rar ,
                    use_subfolders =self .use_subfolders ,use_post_subfolders =self .use_post_subfolders ,
                    target_post_id_from_initial_url =self .initial_target_post_id ,
                    custom_folder_name =self .custom_folder_name ,
                    compress_images =self .compress_images ,download_thumbnails =self .download_thumbnails ,
                    service =self .service ,user_id =self .user_id ,
                    api_url_input =self .api_url_input ,
                    pause_event =self .pause_event ,
                    cancellation_event =self .cancellation_event ,
                    emitter =worker_signals_obj ,
                    downloaded_files =self .downloaded_files ,
                    downloaded_file_hashes =self .downloaded_file_hashes ,
                    downloaded_files_lock =self .downloaded_files_lock ,
                    downloaded_file_hashes_lock =self .downloaded_file_hashes_lock ,
                    skip_words_list =self .skip_words_list ,
                    skip_words_scope =self .skip_words_scope ,
                    show_external_links =self .show_external_links ,
                    extract_links_only =self .extract_links_only ,
                    num_file_threads =self .num_file_threads_for_worker ,
                    skip_current_file_flag =self .skip_current_file_flag ,
                    manga_mode_active =self .manga_mode_active ,
                    manga_filename_style =self .manga_filename_style ,
                    manga_date_prefix =self .manga_date_prefix ,
                    char_filter_scope =self .char_filter_scope ,
                    remove_from_filename_words_list =self .remove_from_filename_words_list ,
                    allow_multipart_download =self .allow_multipart_download ,
                    selected_cookie_file =self .selected_cookie_file ,
                    app_base_dir =self .app_base_dir ,
                    cookie_text =self .cookie_text ,
                    override_output_dir =self .override_output_dir ,
                    manga_global_file_counter_ref =self .manga_global_file_counter_ref ,
                    use_cookie =self .use_cookie ,
                    manga_date_file_counter_ref =self .manga_date_file_counter_ref ,
                    use_date_prefix_for_subfolder=self.use_date_prefix_for_subfolder,
                    creator_download_folder_ignore_words =self .creator_download_folder_ignore_words ,
                    session_file_path=self.session_file_path,
                    session_lock=self.session_lock,
                    )
                    try :
                        dl_count ,skip_count ,kept_originals_this_post ,retryable_failures ,permanent_failures ,history_data =post_processing_worker .process ()
                        grand_total_downloaded_files +=dl_count 
                        grand_total_skipped_files +=skip_count 
                        if kept_originals_this_post :
                            grand_list_of_kept_original_filenames .extend (kept_originals_this_post )
                        if retryable_failures :
                            self .retryable_file_failed_signal .emit (retryable_failures )
                        if history_data :
                            if len (self .history_candidates_buffer )<8 :
                                self .post_processed_for_history_signal .emit (history_data )
                        if permanent_failures :
                            self .permanent_file_failed_signal .emit (permanent_failures )
                    except Exception as proc_err :
                         post_id_for_err =individual_post_data .get ('id','N/A')
                         self .logger (f"❌ Error processing post {post_id_for_err } in DownloadThread: {proc_err }")
                         traceback .print_exc ()
                         num_potential_files_est =len (individual_post_data .get ('attachments',[]))+(1 if individual_post_data .get ('file')else 0 )
                         grand_total_skipped_files +=num_potential_files_est 
                    if self .skip_current_file_flag and self .skip_current_file_flag .is_set ():
                        self .skip_current_file_flag .clear ()
                        self .logger ("   Skip current file flag was processed and cleared by DownloadThread.")
                    self .msleep (10 )
                if was_process_cancelled :break 
            if not was_process_cancelled and not self .isInterruptionRequested ():
                 self .logger ("✅ All posts processed or end of content reached by DownloadThread.")

        except Exception as main_thread_err :
            self .logger (f"\n❌ Critical error within DownloadThread run loop: {main_thread_err }")
            traceback .print_exc ()
            if not self .isInterruptionRequested ():was_process_cancelled =False 
        finally :
            try :
                if worker_signals_obj :
                    worker_signals_obj .progress_signal .disconnect (self .progress_signal )
                    worker_signals_obj .file_download_status_signal .disconnect (self .file_download_status_signal )
                    worker_signals_obj .external_link_signal .disconnect (self .external_link_signal )
                    worker_signals_obj .file_progress_signal .disconnect (self .file_progress_signal )
                    worker_signals_obj .missed_character_post_signal .disconnect (self .missed_character_post_signal )
                    worker_signals_obj .file_successfully_downloaded_signal .disconnect (self .file_successfully_downloaded_signal )

            except (TypeError ,RuntimeError )as e :
                self .logger (f"ℹ️ Note during DownloadThread signal disconnection: {e }")
            self .finished_signal .emit (grand_total_downloaded_files ,grand_total_skipped_files ,self .isInterruptionRequested (),grand_list_of_kept_original_filenames )
    def receive_add_character_result (self ,result ):
        with QMutexLocker (self .prompt_mutex ):
             self ._add_character_response =result 
        self .logger (f"   (DownloadThread) Received character prompt response: {'Yes (added/confirmed)'if result else 'No (declined/failed)'}")

class InterruptedError(Exception):
    """Custom exception for handling cancellations gracefully."""
    pass