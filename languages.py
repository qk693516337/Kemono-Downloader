# languages.py
translations = {
    "en": {
        "settings_dialog_title": "Settings",
        "language_label": "Language:",
        "lang_english": "English",
        "lang_japanese": "日本語 (Japanese)", # Japanese name in English context
        "theme_toggle_light": "Switch to Light Mode",
        "theme_toggle_dark": "Switch to Dark Mode",
        "theme_tooltip_light": "Change the application appearance to light.",
        "theme_tooltip_dark": "Change the application appearance to dark.",
        "ok_button": "OK",
        "appearance_group_title": "Appearance",
        "language_group_title": "Language Settings",
        "creator_post_url_label": "🔗 Kemono Creator/Post URL:",
        "download_location_label": "📁 Download Location:",
        "filter_by_character_label": "🎯 Filter by Character(s) (comma-separated):",
        "skip_with_words_label": "🚫 Skip with Words (comma-separated):",
        "remove_words_from_name_label": "✂️ Remove Words from name:",
        "filter_all_radio": "All",
        "filter_images_radio": "Images/GIFs",
        "filter_videos_radio": "Videos",
        "filter_archives_radio": "📦 Only Archives",
        "filter_links_radio": "🔗 Only Links",
        "filter_audio_radio": "🎧 Only Audio",
        "favorite_mode_checkbox_label": "⭐ Favorite Mode",
        "browse_button_text": "Browse...",
        "char_filter_scope_files_text": "Filter: Files",
        "char_filter_scope_files_tooltip": "Current Scope: Files\n\nFilters individual files by name. A post is kept if any file matches.\nOnly matching files from that post are downloaded.\nExample: Filter 'Tifa'. File 'Tifa_artwork.jpg' matches and is downloaded.\nFolder Naming: Uses character from matching filename.\n\nClick to cycle to: Both",
        "char_filter_scope_title_text": "Filter: Title", # Keep existing
        "char_filter_scope_title_tooltip": "Current Scope: Title\n\nFilters entire posts by their title. All files from a matching post are downloaded.\nExample: Filter 'Aerith'. Post titled 'Aerith's Garden' matches; all its files are downloaded.\nFolder Naming: Uses character from matching post title.\n\nClick to cycle to: Files",
        "char_filter_scope_both_text": "Filter: Both", # Keep existing
        "char_filter_scope_both_tooltip": "Current Scope: Both (Title then Files)\n\n1. Checks post title: If matches, all files from post are downloaded.\n2. If title doesn't match, checks filenames: If any file matches, only that file is downloaded.\nExample: Filter 'Cloud'.\n - Post 'Cloud Strife' (title match) -> all files downloaded.\n - Post 'Bike Chase' with 'Cloud_fenrir.jpg' (file match) -> only 'Cloud_fenrir.jpg' downloaded.\nFolder Naming: Prioritizes title match, then file match.\n\nClick to cycle to: Comments",
        "char_filter_scope_comments_text": "Filter: Comments (Beta)", # Keep existing
        "char_filter_scope_comments_tooltip": "Current Scope: Comments (Beta - Files first, then Comments as fallback)\n\n1. Checks filenames: If any file in the post matches the filter, the entire post is downloaded. Comments are NOT checked for this filter term.\n2. If no file matches, THEN checks post comments: If a comment matches, the entire post is downloaded.\nExample: Filter 'Barret'.\n - Post A: Files 'Barret_gunarm.jpg', 'other.png'. File 'Barret_gunarm.jpg' matches. All files from Post A downloaded. Comments not checked for 'Barret'.\n - Post B: Files 'dyne.jpg', 'weapon.gif'. Comments: '...a drawing of Barret Wallace...'. No file match for 'Barret'. Comment matches. All files from Post B downloaded.\nFolder Naming: Prioritizes character from file match, then from comment match.\n\nClick to cycle to: Title",
        "char_filter_scope_unknown_text": "Filter: Unknown", # Keep existing
        "char_filter_scope_unknown_tooltip": "Current Scope: Unknown\n\nThe character filter scope is in an unknown state. Please cycle or reset.\n\nClick to cycle to: Title",
        "skip_words_input_tooltip": (
            "Enter words, comma-separated, to skip downloading certain content (e.g., WIP, sketch, preview).\n\n"
            "The 'Scope: [Type]' button next to this input cycles how this filter applies:\n"
            "- Scope: Files: Skips individual files if their names contain any of these words.\n"
            "- Scope: Posts: Skips entire posts if their titles contain any of these words.\n"
            "- Scope: Both: Applies both (post title first, then individual files if post title is okay)."
        ),
        "remove_words_input_tooltip": (
            "Enter words, comma-separated, to remove from downloaded filenames (case-insensitive).\n"
            "Useful for cleaning up common prefixes/suffixes.\n"
            "Example: patreon, kemono, [HD], _final"
        ),       
        "skip_scope_files_text": "Scope: Files",
        "skip_scope_files_tooltip": "Current Skip Scope: Files\n\nSkips individual files if their names contain any of the 'Skip with Words'.\nExample: Skip words \"WIP, sketch\".\n- File \"art_WIP.jpg\" -> SKIPPED.\n- File \"final_art.png\" -> DOWNLOADED (if other conditions met).\n\nPost is still processed for other non-skipped files.\nClick to cycle to: Both",
        "skip_scope_posts_text": "Scope: Posts",
        "skip_scope_posts_tooltip": "Current Skip Scope: Posts\n\nSkips entire posts if their titles contain any of the 'Skip with Words'.\nAll files from a skipped post are ignored.\nExample: Skip words \"preview, announcement\".\n- Post \"Exciting Announcement!\" -> SKIPPED.\n- Post \"Finished Artwork\" -> PROCESSED (if other conditions met).\n\nClick to cycle to: Files",
        "skip_scope_both_text": "Scope: Both",
        "skip_scope_both_tooltip": "Current Skip Scope: Both (Posts then Files)\n\n1. Checks post title: If title contains a skip word, the entire post is SKIPPED.\n2. If post title is OK, then checks individual filenames: If a filename contains a skip word, only that file is SKIPPED.\nExample: Skip words \"WIP, sketch\".\n- Post \"Sketches and WIPs\" (title match) -> ENTIRE POST SKIPPED.\n- Post \"Art Update\" (title OK) with files:\n    - \"character_WIP.jpg\" (file match) -> SKIPPED.\n    - \"final_scene.png\" (file OK) -> DOWNLOADED.\n\nClick to cycle to: Posts",
        "skip_scope_unknown_text": "Scope: Unknown",
        "skip_scope_unknown_tooltip": "Current Skip Scope: Unknown\n\nThe skip words scope is in an unknown state. Please cycle or reset.\n\nClick to cycle to: Posts",
        "language_change_title": "Language Changed",
        "language_change_message": "The language has been changed. A restart is required for all changes to take full effect.",
        "language_change_informative": "Would you like to restart the application now?",
        "restart_now_button": "Restart Now",
        "skip_zip_checkbox_label": "Skip .zip",
        "skip_rar_checkbox_label": "Skip .rar",
        "download_thumbnails_checkbox_label": "Download Thumbnails Only",
        "scan_content_images_checkbox_label": "Scan Content for Images",
        "compress_images_checkbox_label": "Compress to WebP",
        "separate_folders_checkbox_label": "Separate Folders by Name/Title",
        "subfolder_per_post_checkbox_label": "Subfolder per Post",
        "use_cookie_checkbox_label": "Use Cookie",
        "use_multithreading_checkbox_base_label": "Use Multithreading",
        "show_external_links_checkbox_label": "Show External Links in Log",
        "manga_comic_mode_checkbox_label": "Manga/Comic Mode",
        "threads_label": "Threads:",
        "start_download_button_text": "⬇️ Start Download",
        "start_download_button_tooltip": "Click to start the download or link extraction process with the current settings.",
        "extract_links_button_text": "🔗 Extract Links",
        "pause_download_button_text": "⏸️ Pause Download",
        "pause_download_button_tooltip": "Click to pause the ongoing download process.",
        "resume_download_button_text": "▶️ Resume Download",
        "resume_download_button_tooltip": "Click to resume the download.",
        "cancel_button_text": "❌ Cancel & Reset UI",
        "cancel_button_tooltip": "Click to cancel the ongoing download/extraction process and reset the UI fields (preserving URL and Directory).",
        "error_button_text": "Error",
        "error_button_tooltip": "View files skipped due to errors and optionally retry them.",
        "cancel_retry_button_text": "❌ Cancel Retry",
        "known_chars_label_text": "🎭 Known Shows/Characters (for Folder Names):",
        "open_known_txt_button_text": "Open Known.txt",
        "known_chars_list_tooltip": "This list contains names used for automatic folder creation when 'Separate Folders' is on\nand no specific 'Filter by Character(s)' is provided or matches a post.\nAdd names of series, games, or characters you frequently download.",
        "open_known_txt_button_tooltip": "Open the 'Known.txt' file in your default text editor.\nThe file is located in the application's directory.",
        "add_char_button_text": "➕ Add",
        "add_char_button_tooltip": "Add the name from the input field to the 'Known Shows/Characters' list.",
        "add_to_filter_button_text": "⤵️ Add to Filter",
        "add_to_filter_button_tooltip": "Select names from 'Known Shows/Characters' list to add to the 'Filter by Character(s)' field above.",
        "delete_char_button_text": "🗑️ Delete Selected",
        "delete_char_button_tooltip": "Delete the selected name(s) from the 'Known Shows/Characters' list.",        
        "progress_log_label_text": "📜 Progress Log:",
        "radio_all_tooltip": "Download all file types found in posts.", # Keep existing
        "radio_images_tooltip": "Download only common image formats (JPG, PNG, GIF, WEBP, etc.).", # Keep existing
        "radio_videos_tooltip": "Download only common video formats (MP4, MKV, WEBM, MOV, etc.).", # Keep existing
        "radio_only_archives_tooltip": "Exclusively download .zip and .rar files. Other file-specific options are disabled.", # Keep existing
        "radio_only_audio_tooltip": "Download only common audio formats (MP3, WAV, FLAC, etc.).", # Keep existing
        "radio_only_links_tooltip": "Extract and display external links from post descriptions instead of downloading files.\nDownload-related options will be disabled.", # Keep existing
        "favorite_mode_checkbox_tooltip": "Enable Favorite Mode to browse saved artists/posts.\nThis will replace the URL input with Favorite selection buttons.",
        "skip_zip_checkbox_tooltip": "If checked, .zip archive files will not be downloaded.\n(Disabled if 'Only Archives' is selected).",
        "skip_rar_checkbox_tooltip": "If checked, .rar archive files will not be downloaded.\n(Disabled if 'Only Archives' is selected).",
        "download_thumbnails_checkbox_tooltip": "Downloads small preview images from the API instead of full-sized files (if available).\nIf 'Scan Post Content for Image URLs' is also checked, this mode will *only* download images found by the content scan (ignoring API thumbnails).",
        "scan_content_images_checkbox_tooltip": "If checked, the downloader will scan the HTML content of posts for image URLs (from <img> tags or direct links).\nThis includes resolving relative paths from <img> tags to full URLs.\nRelative paths in <img> tags (e.g., /data/image.jpg) will be resolved to full URLs.\nUseful for cases where images are in the post description but not in the API's file/attachment list.",
        "compress_images_checkbox_tooltip": "Compress images > 1.5MB to WebP format (requires Pillow).",
        "use_subfolders_checkbox_tooltip": "Create subfolders based on 'Filter by Character(s)' input or post titles.\nUses 'Known Shows/Characters' list as a fallback for folder names if no specific filter matches.\nEnables the 'Filter by Character(s)' input and 'Custom Folder Name' for single posts.",
        "use_subfolder_per_post_checkbox_tooltip": "Creates a subfolder for each post. If 'Separate Folders' is also on, it's inside the character/title folder.",
        "use_cookie_checkbox_tooltip": "If checked, will attempt to use cookies from 'cookies.txt' (Netscape format)\nin the application directory for requests.\nUseful for accessing content that requires login on Kemono/Coomer.",
        "cookie_text_input_tooltip": "Enter your cookie string directly.\nThis will be used if 'Use Cookie' is checked AND 'cookies.txt' is not found or this field is not empty.\nThe format depends on how the backend will parse it (e.g., 'name1=value1; name2=value2').",
        "use_multithreading_checkbox_tooltip": "Enables concurrent operations. See 'Threads' input for details.", # Keep existing
        "thread_count_input_tooltip": ( # New tooltip
            "Number of concurrent operations.\n- Single Post: Concurrent file downloads (1-10 recommended).\n"
            "- Creator Feed URL: Number of posts to process simultaneously (1-200 recommended).\n"
            "  Files within each post are downloaded one by one by its worker.\nIf 'Use Multithreading' is unchecked, 1 thread is used."),
        "external_links_checkbox_tooltip": "If checked, a secondary log panel appears below the main log to display external links found in post descriptions.\n(Disabled if 'Only Links' or 'Only Archives' mode is active).",
        "manga_mode_checkbox_tooltip": "Downloads posts from oldest to newest and renames files based on post title (for creator feeds only).",        "multipart_on_button_text": "Multi-part: ON",
        "multipart_on_button_tooltip": "Multi-part Download: ON\n\nEnables downloading large files in multiple segments simultaneously.\n- Can speed up downloads for single large files (e.g., videos).\n- May increase CPU/network usage.\n- For feeds with many small files, this might not offer speed benefits and could make UI/log busy.\n- If multi-part fails, it retries as single-stream.\n\nClick to turn OFF.",
        "multipart_off_button_text": "Multi-part: OFF",
        "multipart_off_button_tooltip": "Multi-part Download: OFF\n\nAll files downloaded using a single stream.\n- Stable and works well for most scenarios, especially many smaller files.\n- Large files downloaded sequentially.\n\nClick to turn ON (see advisory).",
        "reset_button_text": "🔄 Reset",
        "reset_button_tooltip": "Reset all inputs and logs to default state (only when idle).",
        "progress_idle_text": "Progress: Idle",
        "missed_character_log_label_text": "🚫 Missed Character Log:",
        "creator_popup_title": "Creator Selection",
        "creator_popup_search_placeholder": "Search by name, service, or paste creator URL...",
        "creator_popup_add_selected_button": "Add Selected",
        "creator_popup_scope_characters_button": "Scope: Characters",
        "creator_popup_scope_creators_button": "Scope: Creators",
        "favorite_artists_button_text": "🖼️ Favorite Artists",
        "favorite_artists_button_tooltip": "Browse and download from your favorite artists on Kemono.su/Coomer.su.",
        "favorite_posts_button_text": "📄 Favorite Posts",
        "favorite_posts_button_tooltip": "Browse and download your favorite posts from Kemono.su/Coomer.su.",
        "favorite_scope_selected_location_text": "Scope: Selected Location",
        "favorite_scope_selected_location_tooltip": "Current Favorite Download Scope: Selected Location\n\nAll selected favorite artists/posts will be downloaded into the main 'Download Location' specified in the UI.\nFilters (character, skip words, file type) will apply globally to all content.\n\nClick to change to: Artist Folders",
        "favorite_scope_artist_folders_text": "Scope: Artist Folders",
        "favorite_scope_artist_folders_tooltip": "Current Favorite Download Scope: Artist Folders\n\nFor each selected favorite artist/post, a new subfolder (named after the artist) will be created inside the main 'Download Location'.\nContent for that artist/post will be downloaded into their specific subfolder.\nFilters (character, skip words, file type) will apply *within* each artist's folder.\n\nClick to change to: Selected Location",
        "favorite_scope_unknown_text": "Scope: Unknown",
        "favorite_scope_unknown_tooltip": "Favorite download scope is unknown. Click to cycle.",
        "manga_style_post_title_text": "Name: Post Title",
        "manga_style_original_file_text": "Name: Original File",
        "manga_style_date_based_text": "Name: Date Based",
        "manga_style_title_global_num_text": "Name: Title+G.Num",
        "manga_style_unknown_text": "Name: Unknown Style",
        "fav_artists_dialog_title": "Favorite Artists",
        "fav_artists_loading_status": "Loading favorite artists...",
        "fav_artists_search_placeholder": "Search artists...",
        "fav_artists_select_all_button": "Select All",
        "fav_artists_deselect_all_button": "Deselect All",
        "fav_artists_download_selected_button": "Download Selected",
        "fav_artists_cancel_button": "Cancel",
        "fav_artists_loading_from_source_status": "⏳ Loading favorites from {source_name}...", # Placeholder for dynamic source name
        "fav_artists_found_status": "Found {count} total favorite artist(s).", # Placeholder for dynamic count
        "fav_artists_none_found_status": "No favorite artists found on Kemono.su or Coomer.su.",
        "fav_artists_failed_status": "Failed to fetch favorites.",
        "fav_artists_cookies_required_status": "Error: Cookies enabled but could not be loaded for any source.",
        "fav_artists_no_favorites_after_processing": "No favorite artists found after processing.",
        "fav_artists_no_selection_title": "No Selection",
        "fav_artists_no_selection_message": "Please select at least one artist to download.",

        "fav_posts_dialog_title": "Favorite Posts",
        "fav_posts_loading_status": "Loading favorite posts...",
        "fav_posts_search_placeholder": "Search posts (title, creator, ID, service)...",
        "fav_posts_select_all_button": "Select All",
        "fav_posts_deselect_all_button": "Deselect All",
        "fav_posts_download_selected_button": "Download Selected",
        "fav_posts_cancel_button": "Cancel",
        "fav_posts_cookies_required_error": "Error: Cookies are required for favorite posts but could not be loaded.",
        "fav_posts_auth_failed_title": "Authorization Failed (Posts)", # Clarified title
        "fav_posts_auth_failed_message": "Could not fetch favorites{domain_specific_part} due to an authorization error:\n\n{error_message}\n\nThis usually means your cookies are missing, invalid, or expired for the site. Please check your cookie setup.",
        "fav_posts_fetch_error_title": "Fetch Error",
        "fav_posts_fetch_error_message": "Error fetching favorites from {domain}{error_message_part}",
        "fav_posts_no_posts_found_status": "No favorite posts found.",
        "fav_posts_found_status": "{count} favorite post(s) found.",
        "fav_posts_display_error_status": "Error displaying posts: {error}",
        "fav_posts_ui_error_title": "UI Error",
        "fav_posts_ui_error_message": "Could not display favorite posts: {error}",
        "fav_posts_auth_failed_message_generic": "Could not fetch favorites{domain_specific_part} due to an authorization error. This usually means your cookies are missing, invalid, or expired for the site. Please check your cookie setup.",
        "key_fetching_fav_post_list_init": "Fetching list of favorite posts...",
        "key_fetching_from_source_kemono_su": "Fetching favorites from Kemono.su...",
        "key_fetching_from_source_coomer_su": "Fetching favorites from Coomer.su...",
        "fav_posts_fetch_cancelled_status": "Favorite post fetch cancelled.",

        "known_names_filter_dialog_title": "Add Known Names to Filter",
        "known_names_filter_search_placeholder": "Search names...",
        "known_names_filter_select_all_button": "Select All",
        "known_names_filter_deselect_all_button": "Deselect All",
        "known_names_filter_add_selected_button": "Add Selected",

        "error_files_dialog_title": "Files Skipped Due to Errors",
        "error_files_no_errors_label": "No files were recorded as skipped due to errors in the last session or after retries.",
        "error_files_found_label": "The following {count} file(s) were skipped due to download errors:",
        "error_files_select_all_button": "Select All",
        "error_files_retry_selected_button": "Retry Selected",
        "error_files_export_urls_button": "Export URLs to .txt",
        "error_files_no_selection_retry_message": "Please select at least one file to retry.",
        "error_files_no_errors_export_title": "No Errors",
        "error_files_no_errors_export_message": "There are no error file URLs to export.",
        "error_files_no_urls_found_export_title": "No URLs Found",
        "error_files_no_urls_found_export_message": "Could not extract any URLs from the error file list to export.",
        "error_files_save_dialog_title": "Save Error File URLs",
        "error_files_export_success_title": "Export Successful",
        "error_files_export_success_message": "Successfully exported {count} entries to:\n{filepath}",
        "error_files_export_error_title": "Export Error",
        "error_files_export_error_message": "Could not export file links: {error}",
        "export_options_dialog_title": "Export Options",
        "export_options_description_label": "Choose the format for exporting error file links:",
        "export_options_radio_link_only": "Link per line (URL only)",
        "export_options_radio_link_only_tooltip": "Exports only the direct download URL for each failed file, one URL per line.",
        "export_options_radio_with_details": "Export with details (URL [Post, File info])",
        "export_options_radio_with_details_tooltip": "Exports the URL followed by details like Post Title, Post ID, and Original Filename in brackets.",
        "export_options_export_button": "Export",

        "no_errors_logged_title": "No Errors Logged",
        "no_errors_logged_message": "No files were recorded as skipped due to errors in the last session or after retries.",

        "progress_initializing_text": "Progress: Initializing...",
        "progress_posts_text": "Progress: {processed_posts} / {total_posts} posts ({progress_percent:.1f}%)",
        "progress_processing_post_text": "Progress: Processing post {processed_posts}...",
        "progress_starting_text": "Progress: Starting...",
        "downloading_file_known_size_text": "Downloading '{filename}' ({downloaded_mb:.1f}MB / {total_mb:.1f}MB)",
        "downloading_file_unknown_size_text": "Downloading '{filename}' ({downloaded_mb:.1f}MB)",
        "downloading_multipart_text": "DL '{filename}...': {downloaded_mb:.1f}/{total_mb:.1f} MB ({parts} parts @ {speed:.2f} MB/s)",
        "downloading_multipart_initializing_text": "File: {filename} - Initializing parts...",
        "status_completed": "Completed", # Already exists, but used in progress label
        "status_cancelled_by_user": "Cancelled by user", # Already exists, but used in progress label
        "files_downloaded_label": "downloaded", # Used in progress label summary
        "files_skipped_label": "skipped", # Used in progress label summary
        "retry_finished_text": "Retry Finished",
        "succeeded_text": "Succeeded",
        "failed_text": "Failed",
        "ready_for_new_task_text": "Ready for new task."
        ,"fav_mode_active_label_text": "⭐ Favorite Mode is active. Please select filters below before choosing your favorite artists/posts. Select action below.",
        "export_links_button_text": "Export Links",
        "download_extracted_links_button_text": "Download",
        "download_selected_button_text": "Download Selected", # Generic download selected        
        "link_input_placeholder_text": "e.g., https://kemono.su/patreon/user/12345 or .../post/98765",
        "link_input_tooltip_text": "Enter the full URL of a Kemono/Coomer creator's page or a specific post.\nExample (Creator): https://kemono.su/patreon/user/12345\nExample (Post): https://kemono.su/patreon/user/12345/post/98765",
        "dir_input_placeholder_text": "Select folder where downloads will be saved",
        "dir_input_tooltip_text": "Enter or browse to the main folder where all downloaded content will be saved.\nThis is required unless 'Only Links' mode is selected.",
        "character_input_placeholder_text": "e.g., Tifa, Aerith, (Cloud, Zack)",
        "custom_folder_input_placeholder_text": "Optional: Save this post to specific folder",
        "custom_folder_input_tooltip_text": "If downloading a single post URL AND 'Separate Folders by Name/Title' is enabled,\nyou can enter a custom name here for that post's download folder.\nExample: My Favorite Scene",
        "skip_words_input_placeholder_text": "e.g., WM, WIP, sketch, preview",
        "remove_from_filename_input_placeholder_text": "e.g., patreon, HD",
        "cookie_text_input_placeholder_no_file_selected_text": "Cookie string (if no cookies.txt selected)",
        "cookie_text_input_placeholder_with_file_selected_text": "Using selected cookie file (see Browse...)",
        "character_search_input_placeholder_text": "Search characters...",
        "character_search_input_tooltip_text": "Type here to filter the list of known shows/characters below.",
        "new_char_input_placeholder_text": "Add new show/character name",
        "new_char_input_tooltip_text": "Enter a new show, game, or character name to add to the list above.",
        "link_search_input_placeholder_text": "Search Links...",
        "link_search_input_tooltip_text": "When in 'Only Links' mode, type here to filter the displayed links by text, URL, or platform.",
        "manga_date_prefix_input_placeholder_text": "Prefix for Manga Filenames",
        "manga_date_prefix_input_tooltip_text": "Optional prefix for 'Date Based' or 'Original File' manga filenames (e.g., 'Series Name').\nIf empty, files will be named based on the style without a prefix.",
        "log_display_mode_links_view_text": "🔗 Links View",
        "log_display_mode_progress_view_text": "⬇️ Progress View",
        "download_external_links_dialog_title": "Download Selected External Links",
        "select_all_button_text": "Select All",
        "deselect_all_button_text": "Deselect All",
        "cookie_browse_button_tooltip": "Browse for a cookie file (Netscape format, typically cookies.txt).\nThis will be used if 'Use Cookie' is checked and the text field above is empty."        
        ,
        "page_range_label_text": "Page Range:",
        "start_page_input_placeholder": "Start",
        "start_page_input_tooltip": "For creator URLs: Specify the starting page number to download from (e.g., 1, 2, 3).\nLeave blank or set to 1 to start from the first page.\nDisabled for single post URLs or Manga/Comic Mode.",
        "page_range_to_label_text": "to",
        "end_page_input_placeholder": "End",
        "end_page_input_tooltip": "For creator URLs: Specify the ending page number to download up to (e.g., 5, 10).\nLeave blank to download all pages from the start page.\nDisabled for single post URLs or Manga/Comic Mode.",
        "known_names_help_button_tooltip_text": "Open the application feature guide.",
        "future_settings_button_tooltip_text": "Open application settings (Theme, Language, etc.).",
        "link_search_button_tooltip_text": "Filter displayed links",
        "confirm_add_all_dialog_title": "Confirm Adding New Names",
        "confirm_add_all_info_label": "The following new names/groups from your 'Filter by Character(s)' input are not in 'Known.txt'.\nAdding them can improve folder organization for future downloads.\n\nReview the list and choose an action:",
        "confirm_add_all_select_all_button": "Select All",
        "confirm_add_all_deselect_all_button": "Deselect All",
        "confirm_add_all_add_selected_button": "Add Selected to Known.txt",
        "confirm_add_all_skip_adding_button": "Skip Adding These",
        "confirm_add_all_cancel_download_button": "Cancel Download",
        "cookie_help_dialog_title": "Cookie File Instructions",
        "cookie_help_instruction_intro": "<p>To use cookies, you typically need a <b>cookies.txt</b> file from your browser.</p>",
        "cookie_help_how_to_get_title": "<p><b>How to get cookies.txt:</b></p>",
        "cookie_help_step1_extension_intro": "<li>Install the 'Get cookies.txt LOCALLY' extension for your Chrome-based browser:<br><a href=\"https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc\" style=\"color: #87CEEB;\">Get cookies.txt LOCALLY on Chrome Web Store</a></li>",
        "cookie_help_step2_login": "<li>Go to the website (e.g., kemono.su or coomer.su) and log in if necessary.</li>",
        "cookie_help_step3_click_icon": "<li>Click the extension's icon in your browser toolbar.</li>",
        "cookie_help_step4_export": "<li>Click an 'Export' button (e.g., \"Export As\", \"Export cookies.txt\" - the exact wording might vary depending on the extension version).</li>",
        "cookie_help_step5_save_file": "<li>Save the downloaded <code>cookies.txt</code> file to your computer.</li>",
        "cookie_help_step6_app_intro": "<li>In this application:<ul>",
        "cookie_help_step6a_checkbox": "<li>Ensure the 'Use Cookie' checkbox is checked.</li>",
        "cookie_help_step6b_browse": "<li>Click the 'Browse...' button next to the cookie text field.</li>",
        "cookie_help_step6c_select": "<li>Select the <code>cookies.txt</code> file you just saved.</li></ul></li>",
        "cookie_help_alternative_paste": "<p>Alternatively, some extensions might allow you to copy the cookie string directly. If so, you can paste it into the text field instead of browsing for a file.</p>",
        "cookie_help_proceed_without_button": "Download without Cookies",
        "cookie_help_cancel_download_button": "Cancel Download",       
        "character_input_tooltip": (
            "Enter character names (comma-separated). Supports advanced grouping and affects folder naming "
            "if 'Separate Folders' is enabled.\n\n"
            "Examples:\n"
            "- Nami → Matches 'Nami', creates folder 'Nami'.\n"
            "- (Ulti, Vivi) → Matches either, folder 'Ulti Vivi', adds both to Known.txt separately.\n"
            "- (Boa, Hancock)~ → Matches either, folder 'Boa Hancock', adds as one group in Known.txt.\n\n"
            "Names are treated as aliases for matching.\n\n"
            "Filter Modes (button cycles):\n"
            "- Files: Filters by filename.\n"
            "- Title: Filters by post title.\n"
            "- Both: Title first, then filename.\n"
            "- Comments (Beta): Filename first, then post comments."
        ),
        "tour_dialog_title": "Welcome to Kemono Downloader!",
        "tour_dialog_never_show_checkbox": "Never show this tour again",
        "tour_dialog_skip_button": "Skip Tour",
        "tour_dialog_back_button": "Back",
        "tour_dialog_next_button": "Next",
        "tour_dialog_finish_button": "Finish",
        "tour_dialog_step1_title": "👋 Welcome!",
        "tour_dialog_step1_content": """Hello! This quick tour will walk you through the main features of the Kemono Downloader, including recent updates like enhanced filtering, manga mode improvements, and cookie management.
        <ul>
        <li>My goal is to help you easily download content from <b>Kemono</b> and <b>Coomer</b>.</li><br>
        <li><b>🎨 Creator Selection Button:</b> Next to the URL input, click the palette icon to open a dialog. Browse and select creators from your <code>creators.json</code> file to quickly add their names to the URL input.</li><br>
        <li><b>Important Tip: App '(Not Responding)'?</b><br>
          After clicking 'Start Download', especially for large creator feeds or with many threads, the application might temporarily show as '(Not Responding)'. Your operating system (Windows, macOS, Linux) might even suggest you 'End Process' or 'Force Quit'.<br>
          <b>Please be patient!</b> The app is often still working hard in the background. Before force-closing, try checking your chosen 'Download Location' in your file explorer. If you see new folders being created or files appearing, it means the download is progressing correctly. Give it some time to become responsive again.</li><br>
        <li>Use the <b>Next</b> and <b>Back</b> buttons to navigate.</li><br>
        <li>Many options have tooltips if you hover over them for more details.</li><br>
        <li>Click <b>Skip Tour</b> to close this guide at any time.</li><br>        
        <li>Check <b>'Never show this tour again'</b> if you don't want to see this on future startups.</li>
        </ul>""",
        "tour_dialog_step2_title": "① Getting Started",
        "tour_dialog_step2_content": """Let's start with the basics for downloading:
        <ul>
        <li><b>🔗 Kemono Creator/Post URL:</b><br>
          Paste the full web address (URL) of a creator's page (e.g., <i>https://kemono.su/patreon/user/12345</i>) 
        or a specific post (e.g., <i>.../post/98765</i>).</li><br>
          or a Coomer creator (e.g., <i>https://coomer.su/onlyfans/user/artistname</i>) 
        <li><b>📁 Download Location:</b><br>
          Click 'Browse...' to choose a folder on your computer where all downloaded files will be saved. 
        This is required unless you are using 'Only Links' mode.</li><br>
        <li><b>📄 Page Range (Creator URLs only):</b><br>
          If downloading from a creator's page, you can specify a range of pages to fetch (e.g., pages 2 to 5). 
        Leave blank for all pages. This is disabled for single post URLs or when <b>Manga/Comic Mode</b> is active.</li>
        </ul>""",
        "tour_dialog_step3_title": "② Filtering Downloads",
        "tour_dialog_step3_content": """Refine what you download with these filters (most are disabled in 'Only Links' or 'Only Archives' modes):
        <ul>
        <li><b>🎯 Filter by Character(s):</b><br>
          Enter character names, comma-separated (e.g., <i>Tifa, Aerith</i>). Group aliases for a combined folder name: <i>(alias1, alias2, alias3)</i> becomes folder 'alias1 alias2 alias3' (after cleaning). All names in the group are used as aliases for matching.<br>
          The <b>'Filter: [Type]'</b> button (next to this input) cycles how this filter applies:
          <ul><li><i>Filter: Files:</i> Checks individual filenames. A post is kept if any file matches; only matching files are downloaded. Folder naming uses the character from the matching filename (if 'Separate Folders' is on).</li><br>
            <li><i>Filter: Title:</i> Checks post titles. All files from a matching post are downloaded. Folder naming uses the character from the matching post title.</li>
            <li><b>⤵️ Add to Filter Button (Known Names):</b> Next to the 'Add' button for Known Names (see Step 5), this opens a popup. Select names from your <code>Known.txt</code> list via checkboxes (with a search bar) to quickly add them to the 'Filter by Character(s)' field. Grouped names like <code>(Boa, Hancock)</code> from Known.txt will be added as <code>(Boa, Hancock)~</code> to the filter.</li><br>
            <li><i>Filter: Both:</i> Checks post title first. If it matches, all files are downloaded. If not, it then checks filenames, and only matching files are downloaded. Folder naming prioritizes title match, then file match.</li><br>
            <li><i>Filter: Comments (Beta):</i> Checks filenames first. If a file matches, all files from the post are downloaded. If no file match, it then checks post comments. If a comment matches, all files are downloaded. (Uses more API requests). Folder naming prioritizes file match, then comment match.</li></ul>
          This filter also influences folder naming if 'Separate Folders by Name/Title' is enabled.</li><br>
        <li><b>🚫 Skip with Words:</b><br>
          Enter words, comma-separated (e.g., <i>WIP, sketch, preview</i>). 
          The <b>'Scope: [Type]'</b> button (next to this input) cycles how this filter applies:
          <ul><li><i>Scope: Files:</i> Skips files if their names contain any of these words.</li><br>
            <li><i>Scope: Posts:</i> Skips entire posts if their titles contain any of these words.</li><br>
            <li><i>Scope: Both:</i> Applies both file and post title skipping (post first, then files).</li></ul></li><br>
        <li><b>Filter Files (Radio Buttons):</b> Choose what to download:
          <ul>
          <li><i>All:</i> Downloads all file types found.</li><br>
          <li><i>Images/GIFs:</i> Only common image formats and GIFs.</li><br>
          <li><i>Videos:</i> Only common video formats.</li><br>
          <li><b><i>📦 Only Archives:</i></b> Exclusively downloads <b>.zip</b> and <b>.rar</b> files. When selected, 'Skip .zip' and 'Skip .rar' checkboxes are automatically disabled and unchecked. 'Show External Links' is also disabled.</li><br>
          <li><i>🎧 Only Audio:</i> Only common audio formats (MP3, WAV, FLAC, etc.).</li><br>
          <li><i>🔗 Only Links:</i> Extracts and displays external links from post descriptions instead of downloading files. Download-related options and 'Show External Links' are disabled.</li>
          </ul></li>
        </ul>""",
        "tour_dialog_step4_title": "③ Favorite Mode (Alternative Download)",
        "tour_dialog_step4_content": """The application offers a 'Favorite Mode' for downloading content from artists you've favorited on Kemono.su.
        <ul>
        <li><b>⭐ Favorite Mode Checkbox:</b><br>
          Located next to the '🔗 Only Links' radio button. Check this to activate Favorite Mode.</li><br>
        <li><b>What Happens in Favorite Mode:</b>
          <ul><li>The '🔗 Kemono Creator/Post URL' input area is replaced with a message indicating Favorite Mode is active.</li><br>
            <li>The standard 'Start Download', 'Pause', 'Cancel' buttons are replaced with '🖼️ Favorite Artists' and '📄 Favorite Posts' buttons (Note: 'Favorite Posts' is planned for the future).</li><br>
            <li>The '🍪 Use Cookie' option is automatically enabled and locked, as cookies are required to fetch your favorites.</li></ul></li><br>
        <li><b>🖼️ Favorite Artists Button:</b><br>
          Click this to open a dialog listing your favorited artists from Kemono.su. You can select one or more artists to download.</li><br>
        <li><b>Favorite Download Scope (Button):</b><br>
          This button (next to 'Favorite Posts') controls where selected favorites are downloaded:
          <ul><li><i>Scope: Selected Location:</i> All selected artists are downloaded into the main 'Download Location' you've set. Filters apply globally.</li><br>
            <li><i>Scope: Artist Folders:</i> A subfolder (named after the artist) is created inside your main 'Download Location' for each selected artist. Content for that artist goes into their specific subfolder. Filters apply within each artist's folder.</li></ul></li><br>
        <li><b>Filters in Favorite Mode:</b><br>
          The 'Filter by Character(s)', 'Skip with Words', and 'Filter Files' options still apply to the content downloaded from your selected favorite artists.</li>
        </ul>""",
        "tour_dialog_step5_title": "④ Fine-Tuning Downloads",
        "tour_dialog_step5_content": """More options to customize your downloads:
        <ul>
        <li><b>Skip .zip / Skip .rar:</b> Check these to avoid downloading these archive file types. 
          <i>(Note: These are disabled and ignored if '📦 Only Archives' filter mode is selected).</i></li><br>
        <li><b>✂️ Remove Words from name:</b><br>
          Enter words, comma-separated (e.g., <i>patreon, [HD]</i>), to remove from downloaded filenames (case-insensitive).</li><br>
        <li><b>Download Thumbnails Only:</b> Downloads small preview images instead of full-sized files (if available).</li><br>
        <li><b>Compress Large Images:</b> If the 'Pillow' library is installed, images larger than 1.5MB will be converted to WebP format if the WebP version is significantly smaller.</li><br>
        <li><b>🗄️ Custom Folder Name (Single Post Only):</b><br>
          If you are downloading a single specific post URL AND 'Separate Folders by Name/Title' is enabled, 
        you can enter a custom name here for that post's download folder.</li><br>
        <li><b>🍪 Use Cookie:</b> Check this to use cookies for requests. You can either:
          <ul><li>Enter a cookie string directly into the text field (e.g., <i>name1=value1; name2=value2</i>).</li><br>
            <li>Click 'Browse...' to select a <i>cookies.txt</i> file (Netscape format). The path will appear in the text field.</li></ul>
          This is useful for accessing content that requires login. The text field takes precedence if filled. 
        If 'Use Cookie' is checked but both the text field and browsed file are empty, it will try to load 'cookies.txt' from the app's directory.</li>
        </ul>""",
        "tour_dialog_step6_title": "⑤ Organization & Performance",
        "tour_dialog_step6_content": """Organize your downloads and manage performance:
        <ul>
        <li><b>⚙️ Separate Folders by Name/Title:</b> Creates subfolders based on the 'Filter by Character(s)' input or post titles (can use the <b>Known.txt</b> list as a fallback for folder names).</li><br>
        <li><b>Subfolder per Post:</b> If 'Separate Folders' is on, this creates an additional subfolder for <i>each individual post</i> inside the main character/title folder.</li><br>
        <li><b>🚀 Use Multithreading (Threads):</b> Enables faster operations. The number in 'Threads' input means:
          <ul><li>For <b>Creator Feeds:</b> Number of posts to process simultaneously. Files within each post are downloaded sequentially by its worker (unless 'Date Based' manga naming is on, which forces 1 post worker).</li><br>
            <li>For <b>Single Post URLs:</b> Number of files to download concurrently from that single post.</li></ul>
          If unchecked, 1 thread is used. High thread counts (e.g., >40) may show an advisory.</li><br>
        <li><b>Multi-part Download Toggle (Top-right of log area):</b><br>
          The <b>'Multi-part: [ON/OFF]'</b> button allows enabling/disabling multi-segment downloads for individual large files. 
          <ul><li><b>ON:</b> Can speed up large file downloads (e.g., videos) but may increase UI choppiness or log spam with many small files. An advisory will appear when enabling. If a multi-part download fails, it retries as single-stream.</li><br>
            <li><b>OFF (Default):</b> Files are downloaded in a single stream.</li></ul>
          This is disabled if 'Only Links' or 'Only Archives' mode is active.</li><br>
        <li><b>📖 Manga/Comic Mode (Creator URLs only):</b> Tailored for sequential content.
          <ul>
          <li>Downloads posts from <b>oldest to newest</b>.</li><br>
          <li>The 'Page Range' input is disabled as all posts are fetched.</li><br>
          <li>A <b>filename style toggle button</b> (e.g., 'Name: Post Title') appears in the top-right of the log area when this mode is active for a creator feed. Click it to cycle through naming styles:
            <ul>
            <li><b><i>Name: Post Title (Default):</i></b> The first file in a post is named after the post's cleaned title (e.g., 'My Chapter 1.jpg'). Subsequent files within the *same post* will attempt to keep their original filenames (e.g., 'page_02.png', 'bonus_art.jpg'). If the post has only one file, it's named after the post title. This is generally recommended for most manga/comics.</li><br>
            <li><b><i>Name: Original File:</i></b> All files attempt to keep their original filenames. An optional prefix (e.g., 'MySeries_') can be entered in the input field that appears next to the style button. Example: 'MySeries_OriginalFile.jpg'.</li><br>
            <li><b><i>Name: Title+G.Num (Post Title + Global Numbering):</i></b> All files across all posts in the current download session are named sequentially using the post's cleaned title as a prefix, followed by a global counter. For example: Post 'Chapter 1' (2 files) -> 'Chapter 1_001.jpg', 'Chapter 1_002.png'. The next post, 'Chapter 2' (1 file), would continue the numbering -> 'Chapter 2_003.jpg'. Multithreading for post processing is automatically disabled for this style to ensure correct global numbering.</li><br>
            <li><b><i>Name: Date Based:</i></b> Files are named sequentially (001.ext, 002.ext, ...) based on post publication order. An optional prefix (e.g., 'MySeries_') can be entered in the input field that appears next to the style button. Example: 'MySeries_001.jpg'. Multithreading for post processing is automatically disabled for this style.</li>
            </ul>
          </li><br>
          <li>For best results with 'Name: Post Title', 'Name: Title+G.Num', or 'Name: Date Based' styles, use the 'Filter by Character(s)' field with the manga/series title for folder organization.</li>
          </ul></li><br>
        <li><b>🎭 Known.txt for Smart Folder Organization:</b><br>
          <code>Known.txt</code> (in the app's directory) allows fine-grained control over automatic folder organization when 'Separate Folders by Name/Title' is active.
          <ul>
            <li><b>How it Works:</b> Each line in <code>Known.txt</code> is an entry. 
              <ul><li>A simple line like <code>My Awesome Series</code> means content matching this will go into a folder named "My Awesome Series".</li><br>
                <li>A grouped line like <code>(Character A, Char A, Alt Name A)</code> means content matching "Character A", "Char A", OR "Alt Name A" will ALL go into a single folder named "Character A Char A Alt Name A" (after cleaning). All terms in the parentheses become aliases for that folder.</li></ul></li>
            <li><b>Intelligent Fallback:</b> When 'Separate Folders by Name/Title' is active, and if a post doesn't match any specific 'Filter by Character(s)' input, the downloader consults <code>Known.txt</code> to find a matching primary name for folder creation.</li><br>
            <li><b>User-Friendly Management:</b> Add simple (non-grouped) names via the UI list below. For advanced editing (like creating/modifying grouped aliases), click <b>'Open Known.txt'</b> to edit the file in your text editor. The app reloads it on next use or startup.</li>
          </ul>
        </li>
        </ul>""",
        "tour_dialog_step7_title": "⑥ Common Errors & Troubleshooting",
        "tour_dialog_step7_content": """Sometimes, downloads might encounter issues. Here are a few common ones:
        <ul>
        <li><b>Character Input Tooltip:</b><br>
          Enter character names, comma-separated (e.g., <i>Tifa, Aerith</i>).<br>
          Group aliases for a combined folder name: <i>(alias1, alias2, alias3)</i> becomes folder 'alias1 alias2 alias3'.<br>
          All names in the group are used as aliases for matching content.<br><br>
          The 'Filter: [Type]' button next to this input cycles how this filter applies:<br>
          - Filter: Files: Checks individual filenames. Only matching files are downloaded.<br>
          - Filter: Title: Checks post titles. All files from a matching post are downloaded.<br>
          - Filter: Both: Checks post title first. If no match, then checks filenames.<br>
          - Filter: Comments (Beta): Checks filenames first. If no match, then checks post comments.<br><br>
          This filter also influences folder naming if 'Separate Folders by Name/Title' is enabled.</li><br>      
        <li><b>502 Bad Gateway / 503 Service Unavailable / 504 Gateway Timeout:</b><br>
          These usually indicate temporary server-side problems with Kemono/Coomer. The site might be overloaded, down for maintenance, or experiencing issues. <br>
          <b>Solution:</b> Wait a while (e.g., 30 minutes to a few hours) and try again later. Check the site directly in your browser.</li><br>
        <li><b>Connection Lost / Connection Refused / Timeout (during file download):</b><br>
          This can happen due to your internet connection, server instability, or if the server drops the connection for a large file. <br>
          <b>Solution:</b> Check your internet. Try reducing the number of 'Threads' if it's high. The app might prompt to retry some failed files at the end of a session.</li><br>
        <li><b>IncompleteRead Error:</b><br>
          The server sent less data than expected. Often a temporary network hiccup or server issue. <br>
          <b>Solution:</b> The app will often mark these files for a retry attempt at the end of the download session.</li><br>
        <li><b>403 Forbidden / 401 Unauthorized (less common for public posts):</b><br>
          You might not have permission to access the content. For some paywalled or private content, using the 'Use Cookie' option with valid cookies from your browser session might help. Ensure your cookies are fresh.</li><br>
        <li><b>404 Not Found:</b><br>
          The post or file URL is incorrect, or the content has been removed from the site. Double-check the URL.</li><br>
        <li><b>'No posts found' / 'Target post not found':</b><br>
          Ensure the URL is correct and the creator/post exists. If using page ranges, make sure they are valid for the creator. For very new posts, there might be a slight delay before they appear in the API.</li><br>
        <li><b>General Slowness / App '(Not Responding)':</b><br>
          As mentioned in Step 1, if the app seems to hang after starting, especially with large creator feeds or many threads, please give it time. It's likely processing data in the background. Reducing thread count can sometimes improve responsiveness if this is frequent.</li>
        </ul>""",
        "tour_dialog_step8_title": "⑦ Logs & Final Controls",
        "tour_dialog_step8_content": """Monitoring and Controls:
        <ul>
        <li><b>📜 Progress Log / Extracted Links Log:</b> Shows detailed download messages. If '🔗 Only Links' mode is active, this area displays the extracted links.</li><br>
        <li><b>Show External Links in Log:</b> If checked, a secondary log panel appears below the main log to display any external links found in post descriptions. <i>(This is disabled if '🔗 Only Links' or '📦 Only Archives' mode is active).</i></li><br>
        <li><b>Log View Toggle (👁️ / 🙈 Button):</b><br>
          This button (top-right of log area) switches the main log view:
          <ul><li><b>👁️ Progress Log (Default):</b> Shows all download activity, errors, and summaries.</li><br>
            <li><b>🙈 Missed Character Log:</b> Displays a list of key terms from post titles that were skipped due to your 'Filter by Character(s)' settings. Useful for identifying content you might be unintentionally missing.</li></ul></li><br>
        <li><b>🔄 Reset:</b> Clears all input fields, logs, and resets temporary settings to their defaults. Can only be used when no download is active.</li><br>
        <li><b>⬇️ Start Download / 🔗 Extract Links / ⏸️ Pause / ❌ Cancel:</b> These buttons control the process. 'Cancel & Reset UI' stops the current operation and performs a soft UI reset, preserving your URL and Directory inputs. 'Pause/Resume' allows temporarily halting and continuing.</li><br>
        <li>If some files fail with recoverable errors (like 'IncompleteRead'), you might be prompted to retry them at the end of a session.</li>
        </ul>
        <br>You're all set! Click <b>'Finish'</b> to close the tour and start using the downloader."""
    },
    "ja": {
        "settings_dialog_title": "設定", # Settings
        "language_label": "言語:",    # Language:
        "lang_english": "英語",      # English
        "lang_japanese": "日本語",    # Japanese
        "theme_toggle_light": "ライトモードに切り替え", # Switch to Light Mode
        "theme_toggle_dark": "ダークモードに切り替え",  # Switch to Dark Mode
        "theme_tooltip_light": "アプリケーションの外観を明るく変更します。", # Change the application appearance to light.
        "theme_tooltip_dark": "アプリケーションの外観を暗く変更します。", # Change the application appearance to dark.
        "ok_button": "OK", # OK (often kept as OK or はい)
        "appearance_group_title": "外観", # Appearance
        "language_group_title": "言語設定", # Language Settings
        "creator_post_url_label": "🔗 Kemonoクリエイター/投稿URL:",
        "download_location_label": "📁 ダウンロード場所:",
        "filter_by_character_label": "🎯 キャラクターでフィルタリング (コンマ区切り):",
        "skip_with_words_label": "🚫 スキップする単語 (コンマ区切り):",
        "remove_words_from_name_label": "✂️ 名前から単語を削除:",
        "filter_all_radio": "すべて", # All
        "filter_images_radio": "画像/GIF", # Images/GIFs
        "filter_videos_radio": "動画", # Videos
        "filter_archives_radio": "📦 アーカイブのみ", # Only Archives
        "filter_links_radio": "🔗 リンクのみ", # Only Links
        "filter_audio_radio": "🎧 音声のみ", # Only Audio
        "favorite_mode_checkbox_label": "⭐ お気に入りモード", # Favorite Mode
        "browse_button_text": "参照...",
        "char_filter_scope_files_text": "フィルター: ファイル",
        "char_filter_scope_files_tooltip": "現在のスコープ: ファイル\n\nファイル名で個々のファイルをフィルターします。いずれかのファイルが一致すれば投稿は保持されます。\nその投稿から一致するファイルのみがダウンロードされます。\n例: フィルター「ティファ」。ファイル「ティファ_アートワーク.jpg」が一致し、ダウンロードされます。\nフォルダー命名: 一致するファイル名のキャラクターを使用します。\n\nクリックして次に循環: 両方",
        "char_filter_scope_title_text": "フィルター: タイトル",
        "char_filter_scope_title_tooltip": "現在のスコープ: タイトル\n\n投稿タイトルで投稿全体をフィルターします。一致する投稿のすべてのファイルがダウンロードされます。\n例: フィルター「エアリス」。タイトル「エアリスの庭」の投稿が一致し、すべてのファイルがダウンロードされます。\nフォルダー命名: 一致する投稿タイトルのキャラクターを使用します。\n\nクリックして次に循環: ファイル",
        "char_filter_scope_both_text": "フィルター: 両方", # Keep existing
        "char_filter_scope_both_tooltip": "現在のスコープ: 両方 (タイトル、次にファイル)\n\n1. 投稿タイトルを確認: 一致する場合、投稿のすべてのファイルがダウンロードされます。\n2. タイトルが一致しない場合、ファイル名を確認: いずれかのファイルが一致する場合、そのファイルのみがダウンロードされます。\n例: フィルター「クラウド」。\n - 投稿「クラウド・ストライフ」(タイトル一致) -> すべてのファイルがダウンロードされます。\n - 投稿「バイクチェイス」と「クラウド_フェンリル.jpg」(ファイル一致) -> 「クラウド_フェンリル.jpg」のみがダウンロードされます。\nフォルダー命名: タイトル一致を優先し、次にファイル一致を優先します。\n\nクリックして次に循環: コメント",
        "char_filter_scope_comments_text": "フィルター: コメント (ベータ)",
        "char_filter_scope_comments_tooltip": "現在のスコープ: コメント (ベータ - ファイル優先、次にコメントをフォールバック)\n\n1. ファイル名を確認: 投稿内のいずれかのファイルがフィルターに一致する場合、投稿全体がダウンロードされます。このフィルター用語についてはコメントはチェックされません。\n2. ファイルが一致しない場合、次に投稿コメントを確認: コメントが一致する場合、投稿全体がダウンロードされます。\n例: フィルター「バレット」。\n - 投稿A: ファイル「バレット_ガンアーム.jpg」、「other.png」。ファイル「バレット_ガンアーム.jpg」が一致。投稿Aのすべてのファイルがダウンロードされます。「バレット」についてはコメントはチェックされません。\n - 投稿B: ファイル「ダイン.jpg」、「ウェポン.gif」。コメント: 「...バレット・ウォーレスの絵...」。「バレット」にファイル一致なし。コメントが一致。投稿Bのすべてのファイルがダウンロードされます。\nフォルダー命名: ファイル一致のキャラクターを優先し、次にコメント一致のキャラクターを優先します。\n\nクリックして次に循環: タイトル",
        "char_filter_scope_unknown_text": "フィルター: 不明",
        "char_filter_scope_unknown_tooltip": "現在のスコープ: 不明\n\nキャラクターフィルタースコープが不明な状態です。循環またはリセットしてください。\n\nクリックして次に循環: タイトル",
        "skip_words_input_tooltip": (
            "特定のコンテンツのダウンロードをスキップするために、単語をカンマ区切りで入力します（例: WIP, sketch, preview）。\n\n"
            "この入力の隣にある「スコープ: [タイプ]」ボタンは、このフィルターの適用方法を循環します:\n"
            "- スコープ: ファイル: 名前にこれらの単語のいずれかを含む場合、個々のファイルをスキップします。\n"
            "- スコープ: 投稿: タイトルにこれらの単語のいずれかを含む場合、投稿全体をスキップします。\n"
            "- スコープ: 両方: 両方を適用します（まず投稿タイトル、次に投稿タイトルがOKな場合は個々のファイル）。"
        ),
        "remove_words_input_tooltip": (
            "ダウンロードしたファイル名から削除する単語をカンマ区切りで入力します（大文字・小文字を区別しません）。\n"
            "一般的な接頭辞や接尾辞を整理するのに役立ちます。\n"
            "例: patreon, kemono, [HD], _final"
        ),       
        "skip_scope_files_text": "スコープ: ファイル",
        "skip_scope_files_tooltip": "現在のスキップスコープ: ファイル\n\n「スキップする単語」のいずれかを含む場合、個々のファイルをスキップします。\n例: スキップする単語「WIP、スケッチ」。\n- ファイル「art_WIP.jpg」-> スキップ。\n- ファイル「final_art.png」-> ダウンロード (他の条件が満たされた場合)。\n\n投稿は他のスキップされないファイルについて引き続き処理されます。\nクリックして次に循環: 両方",
        "skip_scope_posts_text": "スコープ: 投稿",
        "skip_scope_posts_tooltip": "現在のスキップスコープ: 投稿\n\n「スキップする単語」のいずれかを含む場合、投稿全体をスキップします。\nスキップされた投稿のすべてのファイルは無視されます。\n例: スキップする単語「プレビュー、お知らせ」。\n- 投稿「エキサイティングなお知らせ！」-> スキップ。\n- 投稿「完成したアートワーク」-> 処理 (他の条件が満たされた場合)。\n\nクリックして次に循環: ファイル",
        "skip_scope_both_text": "スコープ: 両方",
        "skip_scope_both_tooltip": "現在のスキップスコープ: 両方 (投稿、次にファイル)\n\n1. 投稿タイトルを確認: タイトルにスキップワードが含まれている場合、投稿全体がスキップされます。\n2. 投稿タイトルがOKの場合、次に個々のファイル名を確認: ファイル名にスキップワードが含まれている場合、そのファイルのみがスキップされます。\n例: スキップする単語「WIP、スケッチ」。\n- 投稿「スケッチとWIP」(タイトル一致) -> 投稿全体がスキップされます。\n- 投稿「アートアップデート」(タイトルOK) とファイル:\n    - 「キャラクター_WIP.jpg」(ファイル一致) -> スキップ。\n    - 「最終シーン.png」(ファイルOK) -> ダウンロード。\n\nクリックして次に循環: 投稿",
        "skip_scope_unknown_text": "スコープ: 不明",
        "skip_scope_unknown_tooltip": "現在のスキップスコープ: 不明\n\nスキップワードスコープが不明な状態です。循環またはリセットしてください。\n\nクリックして次に循環: 投稿",
        "language_change_title": "言語が変更されました", # Language Changed
        "language_change_message": "言語が変更されました。すべての変更を完全に有効にするには、再起動が必要です。", # The language has been changed. A restart is required for all changes to take full effect.
        "language_change_informative": "今すぐアプリケーションを再起動しますか？", # Would you like to restart the application now?
        "restart_now_button": "今すぐ再起動", # Restart Now
        "skip_zip_checkbox_label": ".zipをスキップ",
        "skip_rar_checkbox_label": ".rarをスキップ",
        "download_thumbnails_checkbox_label": "サムネイルのみダウンロード",
        "scan_content_images_checkbox_label": "コンテンツ内の画像をスキャン",
        "compress_images_checkbox_label": "WebPに圧縮",
        "separate_folders_checkbox_label": "名前/タイトルでフォルダを分ける",
        "subfolder_per_post_checkbox_label": "投稿ごとにサブフォルダ",
        "use_cookie_checkbox_label": "Cookieを使用",
        "use_multithreading_checkbox_base_label": "マルチスレッドを使用",
        "show_external_links_checkbox_label": "ログに外部リンクを表示",
        "manga_comic_mode_checkbox_label": "マンガ/コミックモード",
        "threads_label": "スレッド数:",
        "start_download_button_text": "⬇️ ダウンロード開始",
        "start_download_button_tooltip": "現在の設定でダウンロードまたはリンク抽出プロセスを開始します。",
        "extract_links_button_text": "🔗 リンクを抽出",
        "pause_download_button_text": "⏸️ 一時停止",
        "pause_download_button_tooltip": "進行中のダウンロードプロセスを一時停止します。",
        "resume_download_button_text": "▶️ 再開",
        "resume_download_button_tooltip": "ダウンロードを再開します。",
        "cancel_button_text": "❌ 中止してUIリセット",
        "cancel_button_tooltip": "進行中のダウンロード/抽出プロセスを中止し、UIフィールドをリセットします（URLとディレクトリは保持）。",
        "error_button_text": "エラー",
        "error_button_tooltip": "エラーによりスキップされたファイルを表示し、オプションで再試行します。",
        "cancel_retry_button_text": "❌ 再試行を中止",
        "known_chars_label_text": "🎭 既知の番組/キャラクター (フォルダ名用):",
        "open_known_txt_button_text": "Known.txtを開く",
        "known_chars_list_tooltip": "このリストには、「フォルダを分ける」がオンで、特定の「キャラクターでフィルタリング」が提供されていないか、投稿に一致しない場合に、自動フォルダ作成に使用される名前が含まれています。\n頻繁にダウンロードするシリーズ、ゲーム、またはキャラクターの名前を追加してください。",
        "open_known_txt_button_tooltip": "デフォルトのテキストエディタで「Known.txt」ファイルを開きます。\nファイルはアプリケーションのディレクトリにあります。",
        "add_char_button_text": "➕ 追加",
        "add_char_button_tooltip": "入力フィールドの名前を「既知の番組/キャラクター」リストに追加します。",
        "add_to_filter_button_text": "⤵️ フィルターに追加",
        "add_to_filter_button_tooltip": "「既知の番組/キャラクター」リストから名前を選択して、上の「キャラクターでフィルタリング」フィールドに追加します。",
        "delete_char_button_text": "🗑️ 選択項目を削除",
        "delete_char_button_tooltip": "選択した名前を「既知の番組/キャラクター」リストから削除します。",        
        "radio_all_tooltip": "投稿で見つかったすべてのファイルタイプをダウンロードします。", # Japanese translation
        "radio_images_tooltip": "一般的な画像形式（JPG、PNG、GIF、WEBPなど）のみをダウンロードします。", # Japanese translation
        "radio_videos_tooltip": "一般的な動画形式（MP4、MKV、WEBM、MOVなど）のみをダウンロードします。", # Japanese translation
        "radio_only_archives_tooltip": ".zipおよび.rarファイルのみを排他的にダウンロードします。他のファイル固有のオプションは無効になります。", # Japanese translation
        "radio_only_audio_tooltip": "一般的な音声形式（MP3、WAV、FLACなど）のみをダウンロードします。", # Japanese translation
        "radio_only_links_tooltip": "ファイルをダウンロードする代わりに、投稿の説明から外部リンクを抽出して表示します。\nダウンロード関連のオプションは無効になります。", # Japanese translation
        "favorite_mode_checkbox_tooltip": "お気に入りモードを有効にして、保存したアーティスト/投稿を閲覧します。\nこれにより、URL入力がお気に入り選択ボタンに置き換えられます。",
        "skip_zip_checkbox_tooltip": "チェックすると、.zipアーカイブファイルはダウンロードされません。\n（「アーカイブのみ」が選択されている場合は無効）。",
        "skip_rar_checkbox_tooltip": "チェックすると、.rarアーカイブファイルはダウンロードされません。\n（「アーカイブのみ」が選択されている場合は無効）。",
        "download_thumbnails_checkbox_tooltip": "フルサイズのファイルの代わりにAPIから小さなプレビュー画像をダウンロードします（利用可能な場合）。\n「コンテンツ内の画像をスキャン」もチェックされている場合、このモードではコンテンツスキャンで見つかった画像のみがダウンロードされます（APIサムネイルは無視）。",
        "scan_content_images_checkbox_tooltip": "チェックすると、ダウンローダーは投稿のHTMLコンテンツをスキャンして画像URL（<img>タグまたは直接リンクから）を探します。\nこれには、<img>タグの相対パスを完全なURLに解決することも含まれます。\n<img>タグの相対パス（例: /data/image.jpg）は完全なURLに解決されます。\n画像が投稿の説明にあるがAPIのファイル/添付ファイルリストにない場合に便利です。",
        "compress_images_checkbox_tooltip": "1.5MBを超える画像をWebP形式に圧縮します（Pillowが必要）。",
        "use_subfolders_checkbox_tooltip": "「キャラクターでフィルタリング」入力または投稿タイトルに基づいてサブフォルダを作成します。\n特定のフィルターが投稿に一致しない場合、フォルダ名のフォールバックとして「既知の番組/キャラクター」リストを使用します。\n単一投稿の「キャラクターでフィルタリング」入力と「カスタムフォルダ名」を有効にします。",
        "use_subfolder_per_post_checkbox_tooltip": "投稿ごとにサブフォルダを作成します。「フォルダを分ける」もオンの場合、キャラクター/タイトルフォルダ内に作成されます。",
        "use_cookie_checkbox_tooltip": "チェックすると、リクエストにアプリケーションディレクトリの「cookies.txt」（Netscape形式）のCookieを使用しようとします。\nKemono/Coomerでログインが必要なコンテンツにアクセスするのに便利です。",
        "cookie_text_input_tooltip": "Cookie文字列を直接入力します。\n「Cookieを使用」がチェックされていて、「cookies.txt」が見つからないか、このフィールドが空でない場合に使用されます。\n形式はバックエンドがどのように解析するかに依存します（例: 「name1=value1; name2=value2」）。",
        "use_multithreading_checkbox_tooltip": "同時操作を有効にします。詳細については、「スレッド数」入力を参照してください。", # Keep existing
        "thread_count_input_tooltip": ( # New Japanese tooltip
            "同時操作の数。\n- 単一投稿: 同時ファイルダウンロード数（1～10推奨）。\n"
            "- クリエイターフィードURL: 同時に処理する投稿数（1～200推奨）。\n"
            "  各投稿内のファイルはそのワーカーによって1つずつダウンロードされます。\n「マルチスレッドを使用」がオフの場合、1スレッドが使用されます。"),
        "external_links_checkbox_tooltip": "チェックすると、メインログの下にセカンダリログパネルが表示され、投稿の説明で見つかった外部リンクが表示されます。\n（「リンクのみ」または「アーカイブのみ」モードがアクティブな場合は無効）。",
        "manga_mode_checkbox_tooltip": "投稿を古いものから新しいものへダウンロードし、ファイル名を投稿タイトルに基づいて変更します（クリエイターフィードのみ）。",       
        "progress_log_label_text": "📜 進捗ログ:",
        "multipart_on_button_text": "マルチパート: オン",
        "multipart_on_button_tooltip": "マルチパートダウンロード: オン\n\n大きなファイルを複数のセグメントで同時にダウンロードします。\n- 単一の大きなファイル（例: 動画）のダウンロードを高速化できます。\n- CPU/ネットワーク使用量が増加する可能性があります。\n- 多くの小さなファイルがあるフィードでは、速度の利点はなく、UI/ログが煩雑になることがあります。\n- マルチパートが失敗した場合、シングルストリームで再試行します。\n\nクリックしてオフにします。",
        "multipart_off_button_text": "マルチパート: オフ",
        "multipart_off_button_tooltip": "マルチパートダウンロード: オフ\n\nすべてのファイルが単一のストリームを使用してダウンロードされます。\n- 安定しており、ほとんどのシナリオ、特に多くの小さなファイルに適しています。\n- 大きなファイルは連続してダウンロードされます。\n\nクリックしてオンにします（アドバイザリを参照）。",
        "reset_button_text": "🔄 リセット",
        "reset_button_tooltip": "すべての入力とログをデフォルト状態にリセットします（アイドル時のみ）。",
        "progress_idle_text": "進捗: アイドル",
        "missed_character_log_label_text": "🚫 見逃したキャラクターログ:",
        "creator_popup_title": "クリエイター選択",
        "creator_popup_search_placeholder": "名前、サービスで検索、またはクリエイターURLを貼り付け...",
        "creator_popup_add_selected_button": "選択項目を追加",
        "creator_popup_scope_characters_button": "スコープ: キャラクター",
        "creator_popup_scope_creators_button": "スコープ: クリエイター",
        "favorite_artists_button_text": "🖼️ お気に入りアーティスト",
        "favorite_artists_button_tooltip": "Kemono.su/Coomer.suでお気に入りのアーティストを閲覧してダウンロードします。",
        "favorite_posts_button_text": "📄 お気に入り投稿",
        "favorite_posts_button_tooltip": "Kemono.su/Coomer.suでお気に入りの投稿を閲覧してダウンロードします。",
        "favorite_scope_selected_location_text": "スコープ: 選択場所",
        "favorite_scope_selected_location_tooltip": "現在のお気に入りダウンロードスコープ: 選択場所\n\n選択したすべてのお気に入りアーティスト/投稿は、UIで指定されたメインの「ダウンロード場所」にダウンロードされます。\nフィルター（キャラクター、スキップワード、ファイルタイプ）は、これらのアーティストのすべてのコンテンツにグローバルに適用されます。\n\nクリックして変更: アーティストフォルダ",
        "favorite_scope_artist_folders_text": "スコープ: アーティストフォルダ",
        "favorite_scope_artist_folders_tooltip": "現在のお気に入りダウンロードスコープ: アーティストフォルダ\n\n選択した各お気に入りアーティスト/投稿に対して、メインの「ダウンロード場所」内に新しいサブフォルダ（アーティスト名）が作成されます。\nそのアーティスト/投稿のコンテンツは、特定のサブフォルダにダウンロードされます。\nフィルター（キャラクター、スキップワード、ファイルタイプ）は、各アーティストのフォルダ内で適用されます。\n\nクリックして変更: 選択場所",
        "favorite_scope_unknown_text": "スコープ: 不明",
        "favorite_scope_unknown_tooltip": "お気に入りのダウンロードスコープが不明です。クリックして循環します。",
        "manga_style_post_title_text": "名前: 投稿タイトル",
        "manga_style_original_file_text": "名前: 元ファイル名",
        "manga_style_date_based_text": "名前: 日付順",
        "manga_style_title_global_num_text": "名前: タイトル+通し番号",
        "manga_style_unknown_text": "名前: 不明なスタイル",
        "fav_artists_dialog_title": "お気に入りアーティスト",
        "fav_artists_loading_status": "お気に入りアーティストを読み込み中...",
        "fav_artists_search_placeholder": "アーティストを検索...",
        "fav_artists_select_all_button": "すべて選択",
        "fav_artists_deselect_all_button": "すべて選択解除",
        "fav_artists_download_selected_button": "選択項目をダウンロード",
        "fav_artists_cancel_button": "キャンセル",
        "fav_artists_loading_from_source_status": "⏳ {source_name} からお気に入りを読み込み中...",
        "fav_artists_found_status": "{count} 人のお気に入りアーティストが見つかりました。",
        "fav_artists_none_found_status": "Kemono.suまたはCoomer.suにお気に入りアーティストが見つかりません。",
        "fav_artists_failed_status": "お気に入りの取得に失敗しました。",
        "fav_artists_cookies_required_status": "エラー: Cookieが有効ですが、どのソースからも読み込めませんでした。",
        "fav_artists_no_favorites_after_processing": "処理後にお気に入りアーティストが見つかりませんでした。",
        "fav_artists_no_selection_title": "選択なし",
        "fav_artists_no_selection_message": "ダウンロードするアーティストを少なくとも1人選択してください。",

        "fav_posts_dialog_title": "お気に入り投稿",
        "fav_posts_loading_status": "お気に入り投稿を読み込み中...",
        "fav_posts_search_placeholder": "投稿を検索 (タイトル、クリエイター、ID、サービス)...",
        "fav_posts_select_all_button": "すべて選択",
        "fav_posts_deselect_all_button": "すべて選択解除",
        "fav_posts_download_selected_button": "選択項目をダウンロード",
        "fav_posts_cancel_button": "キャンセル",
        "fav_posts_cookies_required_error": "エラー: お気に入り投稿にはCookieが必要ですが、読み込めませんでした。",
        "fav_posts_auth_failed_title": "認証失敗 (投稿)", # Clarified title
        "fav_posts_auth_failed_message": "認証エラーのため、お気に入り{domain_specific_part}を取得できませんでした:\n\n{error_message}\n\nこれは通常、サイトのCookieがないか、無効であるか、期限切れであることを意味します。Cookieの設定を確認してください。",
        "fav_posts_fetch_error_title": "取得エラー",
        "fav_posts_fetch_error_message": "{domain}からのお気に入り取得エラー{error_message_part}",
        "fav_posts_no_posts_found_status": "お気に入り投稿が見つかりません。",
        "fav_posts_found_status": "{count}件のお気に入り投稿が見つかりました。",
        "fav_posts_display_error_status": "投稿の表示エラー: {error}",
        "fav_posts_ui_error_title": "UIエラー",
        "fav_posts_ui_error_message": "お気に入り投稿を表示できませんでした: {error}",
        "fav_posts_auth_failed_message_generic": "認証エラーのため、お気に入り{domain_specific_part}を取得できませんでした。これは通常、サイトのCookieがないか、無効であるか、期限切れであることを意味します。Cookieの設定を確認してください。",
        "key_fetching_fav_post_list_init": "お気に入り投稿リストを取得中...",
        "key_fetching_from_source_kemono_su": "Kemono.suからお気に入りを取得中...",
        "key_fetching_from_source_coomer_su": "Coomer.suからお気に入りを取得中...",
        "fav_posts_fetch_cancelled_status": "お気に入り投稿の取得がキャンセルされました。",

        "known_names_filter_dialog_title": "既知の名前をフィルターに追加",
        "known_names_filter_search_placeholder": "名前を検索...",
        "known_names_filter_select_all_button": "すべて選択",
        "known_names_filter_deselect_all_button": "すべて選択解除",
        "known_names_filter_add_selected_button": "選択項目を追加",

        "error_files_dialog_title": "エラーによりスキップされたファイル",
        "error_files_no_errors_label": "前回のセッションまたは再試行後にエラーでスキップされたと記録されたファイルはありません。",
        "error_files_found_label": "以下の{count}個のファイルがダウンロードエラーによりスキップされました:",
        "error_files_select_all_button": "すべて選択",
        "error_files_retry_selected_button": "選択項目を再試行",
        "error_files_export_urls_button": "URLを.txtにエクスポート",
        "error_files_no_selection_retry_message": "再試行するファイルを少なくとも1つ選択してください。",
        "error_files_no_errors_export_title": "エラーなし",
        "error_files_no_errors_export_message": "エクスポートするエラーファイルのURLはありません。",
        "error_files_no_urls_found_export_title": "URLが見つかりません",
        "error_files_no_urls_found_export_message": "エラーファイルリストからエクスポートするURLを抽出できませんでした。",
        "error_files_save_dialog_title": "エラーファイルのURLを保存",
        "error_files_export_success_title": "エクスポート成功",
        "error_files_export_success_message": "{count}件のエントリを正常にエクスポートしました:\n{filepath}",
        "error_files_export_error_title": "エクスポートエラー",
        "error_files_export_error_message": "ファイルリンクをエクスポートできませんでした: {error}",
        "export_options_dialog_title": "エクスポートオプション",
        "export_options_description_label": "エラーファイルリンクのエクスポート形式を選択してください:",
        "export_options_radio_link_only": "1行に1リンク (URLのみ)",
        "export_options_radio_link_only_tooltip": "失敗した各ファイルの直接ダウンロードURLのみを1行に1URLずつエクスポートします。",
        "export_options_radio_with_details": "詳細付きでエクスポート (URL [投稿、ファイル情報])",
        "export_options_radio_with_details_tooltip": "URLの後に投稿タイトル、投稿ID、元のファイル名などの詳細を角括弧で囲んでエクスポートします。",
        "export_options_export_button": "エクスポート",

        "no_errors_logged_title": "エラー記録なし",
        "no_errors_logged_message": "前回のセッションまたは再試行後にエラーでスキップされたと記録されたファイルはありません。",

        "progress_initializing_text": "進捗: 初期化中...",
        "progress_posts_text": "進捗: {processed_posts} / {total_posts} 件の投稿 ({progress_percent:.1f}%)",
        "progress_processing_post_text": "進捗: 投稿 {processed_posts} を処理中...",
        "progress_starting_text": "進捗: 開始中...",
        "downloading_file_known_size_text": "'{filename}' をダウンロード中 ({downloaded_mb:.1f}MB / {total_mb:.1f}MB)",
        "downloading_file_unknown_size_text": "'{filename}' をダウンロード中 ({downloaded_mb:.1f}MB)",
        "downloading_multipart_text": "DL '{filename}...': {downloaded_mb:.1f}/{total_mb:.1f} MB ({parts}パーツ @ {speed:.2f} MB/s)",
        "downloading_multipart_initializing_text": "ファイル: {filename} - パーツを初期化中...",
        "status_cancelled_by_user": "ユーザーによってキャンセルされました",
        "files_downloaded_label": "ダウンロード済み",
        "files_skipped_label": "スキップ済み",
        "retry_finished_text": "再試行完了",
        "succeeded_text": "成功",
        "status_completed": "完了",
        "failed_text": "失敗",
        "ready_for_new_task_text": "新しいタスクの準備ができました。",
        "fav_mode_active_label_text": "⭐ お気に入りモードが有効です。お気に入りのアーティスト/投稿を選択する前に、以下のフィルターを選択してください。下のアクションを選択してください。",
        "export_links_button_text": "リンクをエクスポート",
        "download_extracted_links_button_text": "ダウンロード",
        "log_display_mode_links_view_text": "🔗 リンク表示",
        "download_selected_links_dialog_button_text": "選択項目をダウンロード",
        "download_external_links_dialog_title": "選択した外部リンクのダウンロード",
        "download_external_links_dialog_main_label": "サポートされているリンクが{count}件見つかりました (Mega, GDrive, Dropbox)。ダウンロードするものを選択してください:",
        "select_all_button_text": "すべて選択", # Generic select all
        "deselect_all_button_text": "すべて選択解除", # Generic deselect all
        "download_selected_button_text": "選択項目をダウンロード", # Generic download selected        
        "link_input_placeholder_text": "例: https://kemono.su/patreon/user/12345 または .../post/98765",
        "link_input_tooltip_text": "Kemono/Coomerクリエイターのページまたは特定の投稿の完全なURLを入力します。\n例 (クリエイター): https://kemono.su/patreon/user/12345\n例 (投稿): https://kemono.su/patreon/user/12345/post/98765",
        "dir_input_placeholder_text": "ダウンロードを保存するフォルダを選択",
        "dir_input_tooltip_text": "ダウンロードされたすべてのコンテンツが保存されるメインフォルダを入力または参照します。\n「リンクのみ」モードが選択されていない限り必須です。",
        "character_input_placeholder_text": "例: ティファ, エアリス, (クラウド, ザックス)",
        "custom_folder_input_placeholder_text": "任意: この投稿を特定のフォルダに保存",
        "custom_folder_input_tooltip_text": "単一の投稿URLをダウンロードし、かつ「名前/タイトルでフォルダを分ける」が有効な場合、\nその投稿のダウンロードフォルダにカスタム名を入力できます。\n例: お気に入りのシーン",
        "skip_words_input_placeholder_text": "例: WM, WIP, スケッチ, プレビュー",
        "remove_from_filename_input_placeholder_text": "例: patreon, HD",
        "cookie_text_input_placeholder_no_file_selected_text": "Cookie文字列 (cookies.txt未選択時)",
        "cookie_text_input_placeholder_with_file_selected_text": "選択されたCookieファイルを使用中 (参照...を参照)",
        "character_search_input_placeholder_text": "キャラクターを検索...",
        "character_search_input_tooltip_text": "既知の番組/キャラクターのリストを以下でフィルタリングするには、ここに入力します。",
        "new_char_input_placeholder_text": "新しい番組/キャラクター名を追加",
        "new_char_input_tooltip_text": "上記のリストに新しい番組、ゲーム、またはキャラクター名を入力します。",
        "link_search_input_placeholder_text": "リンクを検索...",
        "link_search_input_tooltip_text": "「リンクのみ」モードの場合、表示されるリンクをテキスト、URL、またはプラットフォームでフィルタリングするには、ここに入力します。",
        "manga_date_prefix_input_placeholder_text": "マンガファイル名のプレフィックス",
        "manga_date_prefix_input_tooltip_text": "「日付順」または「元ファイル名」マンガファイル名のオプションのプレフィックス（例: 「シリーズ名」）。\n空の場合、ファイルはプレフィックスなしのスタイルに基づいて名前が付けられます。",
        "empty_popup_button_tooltip_text": "クリエイター選択を開く\n\n「creators.json」ファイルからクリエイターを閲覧・選択します。\n選択したクリエイター名がURL入力フィールドに追加されます。",
        "log_display_mode_progress_view_text": "⬇️ 進捗表示",
        "cookie_browse_button_tooltip": "Cookieファイル（Netscape形式、通常はcookies.txt）を参照します。\n「Cookieを使用」がチェックされていて、上のテキストフィールドが空の場合に使用されます。",       
        "page_range_label_text": "ページ範囲:",
        "thread_count_input_tooltip": "同時操作の数。クリエイターフィードの投稿処理または単一投稿のファイルダウンロードに影響します。「マルチスレッドを使用」がオフの場合、1スレッドが使用されます。",       
        "start_page_input_placeholder": "開始",
        "start_page_input_tooltip": "クリエイターURLの場合: ダウンロードを開始する開始ページ番号を指定します（例: 1, 2, 3）。\n最初のページから開始する場合は空白にするか、1に設定します。\n単一投稿URLまたはマンガ/コミックモードでは無効です。",
        "page_range_to_label_text": "から", # "to" can be tricky, "から" (kara - from) or "まで" (made - until) or "～". Using "から" for "Start to End" -> "開始 から 終了"
        "end_page_input_placeholder": "終了",
        "end_page_input_tooltip": "クリエイターURLの場合: ダウンロードする終了ページ番号を指定します（例: 5, 10）。\n開始ページからすべてのページをダウンロードする場合は空白にします。\n単一投稿URLまたはマンガ/コミックモードでは無効です。",
        "known_names_help_button_tooltip_text": "アプリケーション機能ガイドを開きます。",
        "future_settings_button_tooltip_text": "アプリケーション設定を開きます（テーマ、言語など）。",
        "link_search_button_tooltip_text": "表示されたリンクをフィルター",
        "confirm_add_all_dialog_title": "新しい名前の追加を確認",
        "confirm_add_all_info_label": "「キャラクターでフィルタリング」入力からの以下の新しい名前/グループは「Known.txt」にありません。\n追加すると、将来のダウンロードのフォルダ整理が改善されます。\n\nリストを確認してアクションを選択してください:",
        "confirm_add_all_select_all_button": "すべて選択",
        "confirm_add_all_deselect_all_button": "すべて選択解除",
        "confirm_add_all_add_selected_button": "選択項目をKnown.txtに追加",
        "confirm_add_all_skip_adding_button": "これらの追加をスキップ",
        "confirm_add_all_cancel_download_button": "ダウンロードをキャンセル",
        "cookie_help_dialog_title": "Cookieファイルの説明",
        "cookie_help_instruction_intro": "<p>Cookieを使用するには、通常ブラウザから<b>cookies.txt</b>ファイルが必要です。</p>",
        "cookie_help_how_to_get_title": "<p><b>cookies.txtの入手方法:</b></p>",
        "cookie_help_step1_extension_intro": "<li>Chromeベースのブラウザに「Get cookies.txt LOCALLY」拡張機能をインストールします:<br><a href=\"https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc\" style=\"color: #87CEEB;\">ChromeウェブストアでGet cookies.txt LOCALLYを入手</a></li>",
        "cookie_help_step2_login": "<li>ウェブサイト（例: kemono.suまたはcoomer.su）にアクセスし、必要に応じてログインします。</li>",
        "cookie_help_step3_click_icon": "<li>ブラウザのツールバーにある拡張機能のアイコンをクリックします。</li>",
        "cookie_help_step4_export": "<li>「エクスポート」ボタン（例: 「名前を付けてエクスポート」、「cookies.txtをエクスポート」 - 正確な文言は拡張機能のバージョンによって異なる場合があります）をクリックします。</li>",
        "cookie_help_step5_save_file": "<li>ダウンロードした<code>cookies.txt</code>ファイルをコンピュータに保存します。</li>",
        "cookie_help_step6_app_intro": "<li>このアプリケーションで:<ul>",
        "cookie_help_step6a_checkbox": "<li>「Cookieを使用」チェックボックスがオンになっていることを確認します。</li>",
        "cookie_help_step6b_browse": "<li>Cookieテキストフィールドの隣にある「参照...」ボタンをクリックします。</li>",
        "cookie_help_step6c_select": "<li>保存した<code>cookies.txt</code>ファイルを選択します。</li></ul></li>",
        "cookie_help_alternative_paste": "<p>または、一部の拡張機能ではCookie文字列を直接コピーできる場合があります。その場合は、ファイルを参照する代わりにテキストフィールドに貼り付けることができます。</p>",
        "cookie_help_proceed_without_button": "Cookieなしでダウンロード",
        "cookie_help_cancel_download_button": "ダウンロードをキャンセル",       
        "character_input_tooltip": (
            "キャラクター名を入力してください（カンマ区切り）。「フォルダを分ける」が有効な場合、高度なグルーピングに対応し、フォルダ名に影響します。\n\n"
            "例:\n"
            "- Nami → 'Nami'に一致し、「Nami」フォルダが作成されます。\n"
            "- (Ulti, Vivi) → いずれかに一致し、「Ulti Vivi」フォルダが作成され、両方の名前がKnown.txtに個別に追加されます。\n"
            "- (Boa, Hancock)~ → いずれかに一致し、「Boa Hancock」フォルダが作成され、Known.txtに1つのグループとして追加されます。\n\n"
            "入力された名前は、コンテンツ照合時のエイリアスとして機能します。\n\n"
            "フィルターモード（ボタンで切り替え）:\n"
            "- ファイル: ファイル名でフィルターします。\n"
            "- タイトル: 投稿タイトルでフィルターします。\n"
            "- 両方: まず投稿タイトルを確認し、一致しない場合はファイル名を確認します。\n"
            "- コメント（ベータ版）: まずファイル名を確認し、一致しない場合は投稿コメントを確認します。"
        ),
        "tour_dialog_title": "Kemonoダウンローダーへようこそ！",
        "tour_dialog_never_show_checkbox": "今後このツアーを表示しない",
        "tour_dialog_skip_button": "ツアーをスキップ",
        "tour_dialog_back_button": "戻る",
        "tour_dialog_next_button": "次へ",
        "tour_dialog_finish_button": "完了",
        "tour_dialog_step1_title": "👋 ようこそ！",
        "tour_dialog_step1_content": """このクイックツアーでは、Kemonoダウンローダーの主な機能（強化されたフィルタリング、マンガモードの改善、Cookie管理など、最近の更新を含む）を説明します。
        <ul>
        <li>私の目標は、<b>Kemono</b>と<b>Coomer</b>からコンテンツを簡単にダウンロードできるようにすることです。</li><br>
        <li><b>🎨 クリエイター選択ボタン:</b> URL入力の隣にあるパレットアイコンをクリックするとダイアログが開きます。<code>creators.json</code>ファイルからクリエイターを閲覧・選択して、URL入力に名前をすばやく追加できます。</li><br>
        <li><b>重要ヒント: アプリが「(応答なし)」になる場合</b><br>
          「ダウンロード開始」をクリックした後、特に大規模なクリエイターフィードや多数のスレッドを使用する場合、アプリケーションが一時的に「(応答なし)」と表示されることがあります。お使いのオペレーティングシステム（Windows、macOS、Linux）が「プロセスの終了」や「強制終了」を提案することさえあるかもしれません。<br>
          <b>しばらくお待ちください！</b> アプリは多くの場合、バックグラウンドで懸命に動作しています。強制終了する前に、選択した「ダウンロード場所」をファイルエクスプローラーで確認してみてください。新しいフォルダが作成されたり、ファイルが表示されたりしている場合は、ダウンロードが正しく進行していることを意味します。応答性が回復するまでしばらく時間をおいてください。</li><br>
        <li><b>次へ</b>と<b>戻る</b>ボタンで移動します。</li><br>
        <li>多くのオプションには、マウスオーバーすると詳細が表示されるツールチップがあります。</li><br>
        <li>いつでもこのガイドを閉じるには<b>ツアーをスキップ</b>をクリックします。</li><br>        
        <li>今後の起動時にこれを見たくない場合は<b>「今後このツアーを表示しない」</b>をチェックします。</li>
        </ul>""", # JA_PLACEHOLDER
        "tour_dialog_step2_title": "①はじめに",
        "tour_dialog_step2_content": """ダウンロードの基本から始めましょう:
        <ul>
        <li><b>🔗 Kemonoクリエイター/投稿URL:</b><br>
          クリエイターのページ（例: <i>https://kemono.su/patreon/user/12345</i>）
        または特定の投稿（例: <i>.../post/98765</i>）の完全なウェブアドレス（URL）を貼り付けます。</li><br>
          またはCoomerクリエイター（例: <i>https://coomer.su/onlyfans/user/artistname</i>）
        <li><b>📁 ダウンロード場所:</b><br>
          「参照...」をクリックして、ダウンロードしたすべてのファイルが保存されるコンピュータ上のフォルダを選択します。
        「リンクのみ」モードを使用している場合を除き、これは必須です。</li><br>
        <li><b>📄 ページ範囲（クリエイターURLのみ）:</b><br>
          クリエイターのページからダウンロードする場合、取得するページの範囲を指定できます（例: 2ページから5ページ）。
        すべてのページを取得するには空白のままにします。これは単一の投稿URLまたは<b>マンガ/コミックモード</b>がアクティブな場合は無効になります。</li>
        </ul>""", # JA_PLACEHOLDER
        "tour_dialog_step3_title": "② ダウンロードのフィルタリング",
        "tour_dialog_step3_content": """これらのフィルターでダウンロードするものを絞り込みます（ほとんどは「リンクのみ」または「アーカイブのみ」モードでは無効になります）:
        <ul>
        <li><b>🎯 キャラクターでフィルタリング:</b><br>
          キャラクター名をコンマ区切りで入力します（例: <i>ティファ, エアリス</i>）。結合されたフォルダ名のエイリアスをグループ化します: <i>(エイリアス1, エイリアス2, エイリアス3)</i> は「エイリアス1 エイリアス2 エイリアス3」（クリーニング後）というフォルダになります。グループ内のすべての名前が照合用のエイリアスとして使用されます。<br>
          この入力の隣にある<b>「フィルター: [タイプ]」</b>ボタンは、このフィルターの適用方法を循環します:
          <ul><li><i>フィルター: ファイル:</i> 個々のファイル名を確認します。いずれかのファイルが一致すれば投稿は保持され、一致するファイルのみがダウンロードされます。「フォルダを分ける」がオンの場合、フォルダ名は一致するファイル名のキャラクターを使用します。</li><br>
            <li><i>フィルター: タイトル:</i> 投稿タイトルを確認します。一致する投稿のすべてのファイルがダウンロードされます。フォルダ名は一致する投稿タイトルのキャラクターを使用します。</li>
            <li><b>⤵️ フィルターに追加ボタン（既知の名前）:</b> 既知の名前の「追加」ボタン（ステップ5参照）の隣にあり、これをクリックするとポップアップが開きます。<code>Known.txt</code>リストからチェックボックス（検索バー付き）で名前を選択し、「キャラクターでフィルタリング」フィールドにすばやく追加します。Known.txtの<code>(ボア, ハンコック)</code>のようなグループ化された名前は、フィルターフィールドに<code>(ボア, ハンコック)~</code>として追加されます。</li><br>
            <li><i>フィルター: 両方:</i> まず投稿タイトルを確認します。一致する場合、すべてのファイルがダウンロードされます。一致しない場合、次にファイル名を確認し、一致するファイルのみがダウンロードされます。フォルダ名はタイトル一致を優先し、次にファイル一致を優先します。</li><br>
            <li><i>フィルター: コメント（ベータ）:</i> まずファイル名を確認します。ファイルが一致する場合、投稿のすべてのファイルがダウンロードされます。ファイル一致がない場合、次に投稿コメントを確認します。コメントが一致する場合、投稿のすべてのファイルがダウンロードされます。（より多くのAPIリクエストを使用します）。フォルダ名はファイル一致を優先し、次にコメント一致を優先します。</li></ul>
          「名前/タイトルでフォルダを分ける」が有効な場合、このフィルターはフォルダ名にも影響します。</li><br>
        <li><b>🚫 スキップする単語:</b><br>
          単語をコンマ区切りで入力します（例: <i>WIP, スケッチ, プレビュー</i>）。
          この入力の隣にある<b>「スコープ: [タイプ]」</b>ボタンは、このフィルターの適用方法を循環します:
          <ul><li><i>スコープ: ファイル:</i> 名前にこれらの単語のいずれかを含む場合、ファイルをスキップします。</li><br>
            <li><i>スコープ: 投稿:</i> タイトルにこれらの単語のいずれかを含む場合、投稿全体をスキップします。</li><br>
            <li><i>スコープ: 両方:</i> ファイルと投稿タイトルの両方のスキップを適用します（まず投稿、次にファイル）。</li></ul></li><br>
        <li><b>ファイルフィルター（ラジオボタン）:</b> ダウンロードするものを選択します:
          <ul>
          <li><i>すべて:</i> 見つかったすべてのファイルタイプをダウンロードします。</li><br>
          <li><i>画像/GIF:</i> 一般的な画像形式とGIFのみ。</li><br>
          <li><i>動画:</i> 一般的な動画形式のみ。</li><br>
          <li><b><i>📦 アーカイブのみ:</i></b> <b>.zip</b>と<b>.rar</b>ファイルのみをダウンロードします。選択すると、「.zipをスキップ」と「.rarをスキップ」チェックボックスは自動的に無効になり、チェックが外れます。「外部リンクをログに表示」も無効になります。</li><br>
          <li><i>🎧 音声のみ:</i> 一般的な音声形式のみ（MP3、WAV、FLACなど）。</li><br>
          <li><i>🔗 リンクのみ:</i> ファイルをダウンロードする代わりに、投稿の説明から外部リンクを抽出して表示します。ダウンロード関連のオプションと「外部リンクをログに表示」は無効になります。</li>
          </ul></li>
        </ul>""", # JA_PLACEHOLDER
        "tour_dialog_step4_title": "③ お気に入りモード（代替ダウンロード）",
        "tour_dialog_step4_content": """アプリケーションは、Kemono.suでお気に入りに登録したアーティストからコンテンツをダウンロードするための「お気に入りモード」を提供しています。
        <ul>
        <li><b>⭐ お気に入りモードチェックボックス:</b><br>
          「🔗 リンクのみ」ラジオボタンの隣にあります。これをチェックするとお気に入りモードが有効になります。</li><br>
        <li><b>お気に入りモードでの動作:</b>
          <ul><li>「🔗 Kemonoクリエイター/投稿URL」入力エリアは、お気に入りモードがアクティブであることを示すメッセージに置き換えられます。</li><br>
            <li>標準の「ダウンロード開始」、「一時停止」、「キャンセル」ボタンは、「🖼️ お気に入りアーティスト」と「📄 お気に入り投稿」ボタンに置き換えられます（注意: 「お気に入り投稿」は将来の機能です）。</li><br>
            <li>お気に入りを取得するにはCookieが必要なため、「🍪 Cookieを使用」オプションは自動的に有効になり、ロックされます。</li></ul></li><br>
        <li><b>🖼️ お気に入りアーティストボタン:</b><br>
          これをクリックすると、Kemono.suでお気に入りに登録したアーティストのリストが表示されるダイアログが開きます。このリストから1人以上のアーティストを選択してダウンロードできます。</li><br>
        <li><b>お気に入りダウンロードスコープ（ボタン）:</b><br>
          このボタン（「お気に入り投稿」の隣）は、選択したお気に入りのダウンロード場所を制御します:
          <ul><li><i>スコープ: 選択場所:</i> 選択したすべてのアーティストは、UIで設定したメインの「ダウンロード場所」にダウンロードされます。フィルターはグローバルに適用されます。</li><br>
            <li><i>スコープ: アーティストフォルダ:</i> 選択した各アーティストについて、メインの「ダウンロード場所」内にサブフォルダ（アーティスト名）が作成されます。そのアーティストのコンテンツは、特定のサブフォルダにダウンロードされます。フィルターは各アーティストのフォルダ内で適用されます。</li></ul></li><br>
        <li><b>お気に入りモードでのフィルター:</b><br>
          「キャラクターでフィルタリング」、「スキップする単語」、「ファイルフィルター」オプションは、選択したお気に入りアーティストからダウンロードされるコンテンツにも適用されます。</li>
        </ul>""", # JA_PLACEHOLDER
        "tour_dialog_step5_title": "④ ダウンロードの微調整",
        "tour_dialog_step5_content": """ダウンロードをカスタマイズするためのその他のオプション:
        <ul>
        <li><b>.zipをスキップ / .rarをスキップ:</b> これらのアーカイブファイルタイプをダウンロードしないようにするには、これらをチェックします。
          <i>（注意: 「📦 アーカイブのみ」フィルターモードが選択されている場合、これらは無効になり、無視されます）。</i></li><br>
        <li><b>✂️ 名前から単語を削除:</b><br>
          ダウンロードしたファイル名から削除する単語をコンマ区切りで入力します（大文字と小文字を区別しません）（例: <i>patreon, [HD]</i>）。</li><br>
        <li><b>サムネイルのみダウンロード:</b> フルサイズのファイルの代わりに小さなプレビュー画像をダウンロードします（利用可能な場合）。</li><br>
        <li><b>大きな画像を圧縮:</b> 「Pillow」ライブラリがインストールされている場合、1.5MBより大きい画像は、WebPバージョンが大幅に小さい場合にWebP形式に変換されます。</li><br>
        <li><b>🗄️ カスタムフォルダ名（単一投稿のみ）:</b><br>
          単一の特定の投稿URLをダウンロードしていて、かつ「名前/タイトルでフォルダを分ける」が有効な場合、
        その投稿のダウンロードフォルダにカスタム名を入力できます。</li><br>
        <li><b>🍪 Cookieを使用:</b> リクエストにCookieを使用するには、これをチェックします。次のいずれかを実行できます:
          <ul><li>Cookie文字列をテキストフィールドに直接入力します（例: <i>name1=value1; name2=value2</i>）。</li><br>
            <li>「参照...」をクリックして<i>cookies.txt</i>ファイル（Netscape形式）を選択します。パスがテキストフィールドに表示されます。</li></ul>
          これは、ログインが必要なコンテンツにアクセスする場合に便利です。テキストフィールド（入力されている場合）が優先されます。
        「Cookieを使用」がチェックされていて、テキストフィールドと参照されたファイルの両方が空の場合、アプリのディレクトリから「cookies.txt」を読み込もうとします。</li>
        </ul>""", # JA_PLACEHOLDER
        "tour_dialog_step6_title": "⑤ 整理とパフォーマンス",
        "tour_dialog_step6_content": """ダウンロードを整理し、パフォーマンスを管理します:
        <ul>
        <li><b>⚙️ 名前/タイトルでフォルダを分ける:</b> 「キャラクターでフィルタリング」入力または投稿タイトルに基づいてサブフォルダを作成します（特定のフィルターが投稿に一致しない場合、フォルダ名のフォールバックとして<b>Known.txt</b>リストを使用できます）。</li><br>
        <li><b>投稿ごとにサブフォルダ:</b> 「フォルダを分ける」がオンの場合、メインのキャラクター/タイトルフォルダ内に<i>個々の投稿</i>ごとに追加のサブフォルダを作成します。</li><br>
        <li><b>🚀 マルチスレッドを使用（スレッド数）:</b> より高速な操作を可能にします。「スレッド数」入力の数値の意味:
          <ul><li><b>クリエイターフィードの場合:</b> 同時に処理する投稿の数。各投稿内のファイルは、そのワーカーによって順番にダウンロードされます（「日付順」マンガ命名がオンの場合を除く。これは1つの投稿ワーカーを強制します）。</li><br>
            <li><b>単一投稿URLの場合:</b> その単一投稿から同時にダウンロードするファイルの数。</li></ul>
          チェックされていない場合、1スレッドが使用されます。高いスレッド数（例: >40）はアドバイザリを表示する場合があります。</li><br>
        <li><b>マルチパートダウンロード切り替え（ログエリアの右上）:</b><br>
          <b>「マルチパート: [オン/オフ]」</b>ボタンは、個々の大きなファイルのマルチセグメントダウンロードを有効/無効にできます。
          <ul><li><b>オン:</b> 大きなファイルのダウンロード（例: 動画）を高速化できますが、多くの小さなファイルがある場合、UIの途切れやログのスパムが増加する可能性があります。有効にするとアドバイザリが表示されます。マルチパートダウンロードが失敗した場合、シングルストリームで再試行します。</li><br>
            <li><b>オフ（デフォルト）:</b> ファイルは単一のストリームでダウンロードされます。</li></ul>
          「リンクのみ」または「アーカイブのみ」モードがアクティブな場合は無効になります。</li><br>
        <li><b>📖 マンガ/コミックモード（クリエイターURLのみ）:</b> シーケンシャルコンテンツ向けに調整されています。
          <ul>
          <li>投稿を<b>古いものから新しいものへ</b>ダウンロードします。</li><br>
          <li>すべての投稿が取得されるため、「ページ範囲」入力は無効になります。</li><br>
          <li>このモードがクリエイターフィードでアクティブな場合、ログエリアの右上に<b>ファイル名スタイル切り替えボタン</b>（例: 「名前: 投稿タイトル」）が表示されます。クリックすると命名スタイルが循環します:
            <ul>
            <li><b><i>名前: 投稿タイトル（デフォルト）:</i></b> 投稿の最初のファイルは、投稿のクリーンなタイトルにちなんで名付けられます（例: 「My Chapter 1.jpg」）。*同じ投稿*内の後続のファイルは、元のファイル名を保持しようとします（例: 「page_02.png」、「bonus_art.jpg」）。投稿にファイルが1つしかない場合は、投稿タイトルにちなんで名付けられます。これはほとんどのマンガ/コミックに一般的に推奨されます。</li><br>
            <li><b><i>名前: 元ファイル名:</i></b> すべてのファイルが元のファイル名を保持しようとします。オプションのプレフィックス（例: 「MySeries_」）を、このスタイルボタンの隣に表示される入力フィールドに入力できます。例: 「MySeries_OriginalFile.jpg」。</li><br>
            <li><b><i>名前: タイトル+通し番号（投稿タイトル+グローバル番号付け）:</i></b> 現在のダウンロードセッションのすべての投稿のすべてのファイルが、投稿のクリーンなタイトルをプレフィックスとして使用し、グローバルカウンターを続けて順番に名付けられます。例: 投稿「Chapter 1」（2ファイル）-> 「Chapter 1_001.jpg」、「Chapter 1_002.png」。次の投稿「Chapter 2」（1ファイル）は番号付けを続けます -> 「Chapter 2_003.jpg」。このスタイルの場合、正しいグローバル番号付けを保証するために、投稿処理のマルチスレッドは自動的に無効になります。</li><br>
            <li><b><i>名前: 日付順:</i></b> ファイルは投稿の公開順に基づいて順番に名付けられます（001.ext、002.extなど）。オプションのプレフィックス（例: 「MySeries_」）を、このスタイルボタンの隣に表示される入力フィールドに入力できます。例: 「MySeries_001.jpg」。このスタイルの場合、投稿処理のマルチスレッドは自動的に無効になります。</li>
            </ul>
          </li><br>
          <li>「名前: 投稿タイトル」、「名前: タイトル+通し番号」、または「名前: 日付順」スタイルで最良の結果を得るには、「キャラクターでフィルタリング」フィールドにマンガ/シリーズのタイトルを入力してフォルダを整理します。</li>
          </ul></li><br>
        <li><b>🎭 Known.txtによるスマートなフォルダ整理:</b><br>
          <code>Known.txt</code>（アプリのディレクトリ内）は、「名前/タイトルでフォルダを分ける」がアクティブな場合の自動フォルダ整理を細かく制御できます。
          <ul> # JA_PLACEHOLDER
            <li><b>仕組み:</b> <code>Known.txt</code>の各行がエントリです。
              <ul><li><code>My Awesome Series</code>のような単純な行は、これに一致するコンテンツが「My Awesome Series」という名前のフォルダに入ることを意味します。</li><br>
                <li><code>(Character A, Char A, Alt Name A)</code>のようなグループ化された行は、「Character A」、「Char A」、または「Alt Name A」に一致するコンテンツがすべて「Character A Char A Alt Name A」（クリーニング後）という名前の単一フォルダに入ることを意味します。括弧内のすべての用語がそのフォルダのエイリアスになります。</li></ul></li>
            <li><b>インテリジェントなフォールバック:</b> 「名前/タイトルでフォルダを分ける」がアクティブで、投稿が特定の「キャラクターでフィルタリング」入力に一致しない場合、ダウンローダーは<code>Known.txt</code>を参照して、フォルダ作成用の一致するプライマリ名を見つけます。</li><br>
            <li><b>ユーザーフレンドリーな管理:</b> UIリスト（下記）から単純な（グループ化されていない）名前を追加します。高度な編集（グループ化されたエイリアスの作成/変更など）の場合は、<b>「Known.txtを開く」</b>をクリックしてテキストエディタでファイルを編集します。アプリは次回使用時または起動時に再読み込みします。</li>
          </ul>
        </li>
        </ul>""", # JA_PLACEHOLDER
        "tour_dialog_step7_title": "⑥ 一般的なエラーとトラブルシューティング",
        "tour_dialog_step7_content": """ダウンロード中に問題が発生することがあります。一般的なものをいくつか紹介します:
        <ul>
        <li><b>キャラクター入力ツールチップ:</b><br>
          キャラクター名をコンマ区切りで入力します (例: <i>ティファ, エアリス</i>)。<br>
          結合されたフォルダ名のエイリアスをグループ化します: <i>(エイリアス1, エイリアス2, エイリアス3)</i> はフォルダ「エイリアス1 エイリアス2 エイリアス3」になります。<br>
          グループ内のすべての名前が照合用のエイリアスとして使用されます。<br><br>
          この入力の隣にある「フィルター: [タイプ]」ボタンは、このフィルターの適用方法を循環します:<br>
          - フィルター: ファイル: 個々のファイル名を確認します。一致するファイルのみがダウンロードされます。<br>
          - フィルター: タイトル: 投稿タイトルを確認します。一致する投稿のすべてのファイルがダウンロードされます。<br>
          - フィルター: 両方: まず投稿タイトルを確認します。一致しない場合、次にファイル名を確認します。<br>
          - フィルター: コメント (ベータ): まずファイル名を確認します。一致しない場合、次に投稿コメントを確認します。<br><br>
          「名前/タイトルでフォルダを分ける」が有効な場合、このフィルターはフォルダ名にも影響します。</li><br>      
        <li><b>502 Bad Gateway / 503 Service Unavailable / 504 Gateway Timeout:</b><br>
          これらは通常、Kemono/Coomerのサーバー側の一時的な問題を示します。サイトが過負荷になっているか、メンテナンス中であるか、問題が発生している可能性があります。<br>
          <b>解決策:</b> しばらく（例: 30分から数時間）待ってから、後でもう一度試してください。ブラウザで直接サイトを確認してください。</li><br>
        <li><b>接続喪失 / 接続拒否 / タイムアウト（ファイルダウンロード中）:</b><br>
          これは、インターネット接続、サーバーの不安定性、またはサーバーが大きなファイルの接続を切断した場合に発生する可能性があります。<br>
          <b>解決策:</b> インターネットを確認してください。「スレッド数」が高い場合は減らしてみてください。セッションの最後に一部の失敗したファイルを再試行するようアプリが促す場合があります。</li><br>
        <li><b>IncompleteReadエラー:</b><br>
          サーバーが予期したよりも少ないデータを送信しました。多くの場合、一時的なネットワークの不具合またはサーバーの問題です。<br>
          <b>解決策:</b> アプリは多くの場合、ダウンロードセッションの最後にこれらのファイルを再試行対象としてマークします。</li><br>
        <li><b>403 Forbidden / 401 Unauthorized（公開投稿ではあまり一般的ではありません）:</b><br>
          コンテンツにアクセスする権限がない可能性があります。一部の有料またはプライベートコンテンツの場合、「Cookieを使用」オプションをブラウザセッションの有効なCookieと共に使用すると役立つ場合があります。Cookieが最新であることを確認してください。</li><br>
        <li><b>404 Not Found:</b><br>
          投稿またはファイルのURLが正しくないか、コンテンツがサイトから削除されています。URLを再確認してください。</li><br>
        <li><b>「投稿が見つかりません」/「対象の投稿が見つかりません」:</b><br>
          URLが正しく、クリエイター/投稿が存在することを確認してください。ページ範囲を使用している場合は、クリエイターに対して有効であることを確認してください。非常に新しい投稿の場合、APIに表示されるまでにわずかな遅延がある場合があります。</li><br>
        <li><b>全体的な遅さ / アプリ「(応答なし)」:</b><br>
          ステップ1で述べたように、特に大規模なクリエイターフィードや多くのスレッドで開始後にアプリがハングするように見える場合は、しばらくお待ちください。バックグラウンドでデータを処理している可能性が高いです。これが頻繁に発生する場合は、スレッド数を減らすと応答性が向上することがあります。</li>
        </ul>""", # JA_PLACEHOLDER
        "tour_dialog_step8_title": "⑦ ログと最終コントロール",
        "tour_dialog_step8_content": """監視とコントロール:
        <ul>
        <li><b>📜 進捗ログ / 抽出リンクログ:</b> 詳細なダウンロードメッセージを表示します。「🔗 リンクのみ」モードがアクティブな場合、このエリアには抽出されたリンクが表示されます。</li><br>
        <li><b>ログに外部リンクを表示:</b> チェックすると、メインログの下にセカンダリログパネルが表示され、投稿の説明で見つかった外部リンクが表示されます。<i>（「🔗 リンクのみ」または「📦 アーカイブのみ」モードがアクティブな場合は無効になります）。</i></li><br>
        <li><b>ログビュー切り替え（👁️ / 🙈 ボタン）:</b><br>
          このボタン（ログエリアの右上）は、メインログビューを切り替えます:
          <ul><li><b>👁️ 進捗ログ（デフォルト）:</b> すべてのダウンロードアクティビティ、エラー、概要を表示します。</li><br>
            <li><b>🙈 見逃したキャラクターログ:</b> 「キャラクターでフィルタリング」設定のためにスキップされた投稿タイトルのキーワードのリストを表示します。意図せずに見逃している可能性のあるコンテンツを特定するのに役立ちます。</li></ul></li><br>
        <li><b>🔄 リセット:</b> すべての入力フィールド、ログをクリアし、一時的な設定をデフォルトにリセットします。ダウンロードがアクティブでない場合にのみ使用できます。</li><br>
        <li><b>⬇️ ダウンロード開始 / 🔗 リンクを抽出 / ⏸️ 一時停止 / ❌ 中止:</b> これらのボタンでプロセスを制御します。「中止してUIリセット」は現在の操作を停止し、URLとディレクトリ入力を保持してソフトUIリセットを実行します。「一時停止/再開」は一時的な停止と継続を可能にします。</li><br>
        <li>一部のファイルが回復可能なエラー（「IncompleteRead」など）で失敗した場合、セッションの最後に再試行するよう促される場合があります。</li>
        </ul>
        <br>準備完了です！<b>「完了」</b>をクリックしてツアーを閉じ、ダウンローダーの使用を開始します。""" # JA_PLACEHOLDER
    }
} # End of "ja" translations

translations["fr"] = {
    "settings_dialog_title": "Paramètres",
    "language_label": "Langue :",
    "lang_english": "Anglais (English)",
    "lang_japanese": "Japonais (日本語)",
    "theme_toggle_light": "Passer en mode clair",
    "theme_toggle_dark": "Passer en mode sombre",
    "theme_tooltip_light": "Changer l'apparence de l'application en clair.",
    "theme_tooltip_dark": "Changer l'apparence de l'application en sombre.",
    "ok_button": "OK",
    "appearance_group_title": "Apparence",
    "language_group_title": "Paramètres de langue",
    "creator_post_url_label": "🔗 URL Créateur/Post Kemono :",
    "download_location_label": "📁 Emplacement de téléchargement :",
    "filter_by_character_label": "🎯 Filtrer par Personnage(s) (séparés par des virgules) :",
    "skip_with_words_label": "🚫 Ignorer avec les mots (séparés par des virgules) :",
    "remove_words_from_name_label": "✂️ Supprimer les mots du nom :",
    "filter_all_radio": "Tout",
    "filter_images_radio": "Images/GIFs",
    "filter_videos_radio": "Vidéos",
    "filter_archives_radio": "📦 Archives Uniquement",
    "filter_links_radio": "🔗 Liens Uniquement",
    "filter_audio_radio": "🎧 Audio Uniquement",
    "favorite_mode_checkbox_label": "⭐ Mode Favori",
    "browse_button_text": "Parcourir...",
    "char_filter_scope_files_text": "Filtre : Fichiers",
    "char_filter_scope_files_tooltip": "Portée actuelle : Fichiers\n\nFiltre les fichiers individuels par nom. Une publication est conservée si un fichier correspond.\nSeuls les fichiers correspondants de cette publication sont téléchargés.\nExemple : Filtre 'Tifa'. Le fichier 'Tifa_artwork.jpg' correspond et est téléchargé.\nNommage du dossier : Utilise le personnage du nom de fichier correspondant.\n\nCliquez pour passer à : Les deux",
    "char_filter_scope_title_text": "Filtre : Titre",
    "char_filter_scope_title_tooltip": "Portée actuelle : Titre\n\nFiltre les publications entières par leur titre. Tous les fichiers d'une publication correspondante sont téléchargés.\nExemple : Filtre 'Aerith'. La publication intitulée 'Le jardin d'Aerith' correspond ; tous ses fichiers sont téléchargés.\nNommage du dossier : Utilise le personnage du titre de la publication correspondante.\n\nCliquez pour passer à : Fichiers",
    "char_filter_scope_both_text": "Filtre : Les deux",
    "char_filter_scope_both_tooltip": "Portée actuelle : Les deux (Titre puis Fichiers)\n\n1. Vérifie le titre de la publication : S'il correspond, tous les fichiers de la publication sont téléchargés.\n2. Si le titre ne correspond pas, vérifie les noms de fichiers : Si un fichier correspond, seul ce fichier est téléchargé.\nExemple : Filtre 'Cloud'.\n - Publication 'Cloud Strife' (correspondance de titre) -> tous les fichiers sont téléchargés.\n - Publication 'Course de moto' avec 'Cloud_fenrir.jpg' (correspondance de fichier) -> seul 'Cloud_fenrir.jpg' est téléchargé.\nNommage du dossier : Priorise la correspondance de titre, puis la correspondance de fichier.\n\nCliquez pour passer à : Commentaires",
    "char_filter_scope_comments_text": "Filtre : Commentaires (Bêta)",
    "char_filter_scope_comments_tooltip": "Portée actuelle : Commentaires (Bêta - Fichiers d'abord, puis Commentaires en repli)\n\n1. Vérifie les noms de fichiers : Si un fichier dans la publication correspond au filtre, la publication entière est téléchargée. Les commentaires ne sont PAS vérifiés pour ce terme de filtre.\n2. Si aucun fichier ne correspond, ALORS vérifie les commentaires de la publication : Si un commentaire correspond, la publication entière est téléchargée.\nExemple : Filtre 'Barret'.\n - Publication A : Fichiers 'Barret_gunarm.jpg', 'other.png'. Le fichier 'Barret_gunarm.jpg' correspond. Tous les fichiers de la publication A sont téléchargés. Les commentaires ne sont pas vérifiés pour 'Barret'.\n - Publication B : Fichiers 'dyne.jpg', 'weapon.gif'. Commentaires : '...un dessin de Barret Wallace...'. Aucune correspondance de fichier pour 'Barret'. Le commentaire correspond. Tous les fichiers de la publication B sont téléchargés.\nNommage du dossier : Priorise le personnage de la correspondance de fichier, puis de la correspondance de commentaire.\n\nCliquez pour passer à : Titre",
    "char_filter_scope_unknown_text": "Filtre : Inconnu",
    "char_filter_scope_unknown_tooltip": "Portée actuelle : Inconnue\n\nLa portée du filtre de personnage est dans un état inconnu. Veuillez cycler ou réinitialiser.\n\nCliquez pour passer à : Titre",
    "skip_words_input_tooltip": "Saisissez des mots, séparés par des virgules, pour ignorer le téléchargement de certains contenus (par ex., WIP, sketch, preview).\n\nLe bouton 'Portée : [Type]' à côté de cette entrée change la façon dont ce filtre s'applique :\n- Portée : Fichiers : Ignore les fichiers individuels si leurs noms contiennent l'un de ces mots.\n- Portée : Publications : Ignore les publications entières si leurs titres contiennent l'un de ces mots.\n- Portée : Les deux : Applique les deux (titre de la publication d'abord, puis fichiers individuels si le titre de la publication est OK).",
    "remove_words_input_tooltip": "Saisissez des mots, séparés par des virgules, à supprimer des noms de fichiers téléchargés (insensible à la casse).\nUtile pour nettoyer les préfixes/suffixes courants.\nExemple : patreon, kemono, [HD], _final",
    "skip_scope_files_text": "Portée : Fichiers",
    "skip_scope_files_tooltip": "Portée d'omission actuelle : Fichiers\n\nIgnore les fichiers individuels si leurs noms contiennent l'un des 'Mots à ignorer'.\nExemple : Mots à ignorer \"WIP, sketch\".\n- Fichier \"art_WIP.jpg\" -> IGNORÉ.\n- Fichier \"final_art.png\" -> TÉLÉCHARGÉ (si les autres conditions sont remplies).\n\nLa publication est toujours traitée pour les autres fichiers non ignorés.\nCliquez pour passer à : Les deux",
    "skip_scope_posts_text": "Portée : Publications",
    "skip_scope_posts_tooltip": "Portée d'omission actuelle : Publications\n\nIgnore les publications entières si leurs titres contiennent l'un des 'Mots à ignorer'.\nTous les fichiers d'une publication ignorée sont ignorés.\nExemple : Mots à ignorer \"preview, announcement\".\n- Publication \"Annonce excitante !\" -> IGNORÉE.\n- Publication \"Œuvre terminée\" -> TRAITÉE (si les autres conditions sont remplies).\n\nCliquez pour passer à : Fichiers",
    "skip_scope_both_text": "Portée : Les deux",
    "skip_scope_both_tooltip": "Portée d'omission actuelle : Les deux (Publications puis Fichiers)\n\n1. Vérifie le titre de la publication : Si le titre contient un mot à ignorer, la publication entière est IGNORÉE.\n2. Si le titre de la publication est OK, alors vérifie les noms de fichiers individuels : Si un nom de fichier contient un mot à ignorer, seul ce fichier est IGNORÉ.\nExemple : Mots à ignorer \"WIP, sketch\".\n- Publication \"Croquis et WIPs\" (correspondance de titre) -> PUBLICATION ENTIÈRE IGNORÉE.\n- Publication \"Mise à jour artistique\" (titre OK) avec les fichiers :\n  - \"character_WIP.jpg\" (correspondance de fichier) -> IGNORÉ.\n  - \"final_scene.png\" (fichier OK) -> TÉLÉCHARGÉ.\n\nCliquez pour passer à : Publications",
    "skip_scope_unknown_text": "Portée : Inconnue",
    "skip_scope_unknown_tooltip": "Portée d'omission actuelle : Inconnue\n\nLa portée des mots à ignorer est dans un état inconnu. Veuillez cycler ou réinitialiser.\n\nCliquez pour passer à : Publications",
    "language_change_title": "Langue modifiée",
    "language_change_message": "La langue a été modifiée. Un redémarrage est nécessaire pour que toutes les modifications prennent pleinement effet.",
    "language_change_informative": "Voulez-vous redémarrer l'application maintenant ?",
    "restart_now_button": "Redémarrer maintenant",
    "skip_zip_checkbox_label": "Ignorer .zip",
    "skip_rar_checkbox_label": "Ignorer .rar",
    "download_thumbnails_checkbox_label": "Télécharger les miniatures uniquement",
    "scan_content_images_checkbox_label": "Analyser le contenu pour les images",
    "compress_images_checkbox_label": "Compresser en WebP",
    "separate_folders_checkbox_label": "Dossiers séparés par Nom/Titre",
    "subfolder_per_post_checkbox_label": "Sous-dossier par publication",
    "use_cookie_checkbox_label": "Utiliser le cookie",
    "use_multithreading_checkbox_base_label": "Utiliser le multithreading",
    "show_external_links_checkbox_label": "Afficher les liens externes dans le journal",
    "manga_comic_mode_checkbox_label": "Mode Manga/BD",
    "threads_label": "Threads :",
    "start_download_button_text": "⬇️ Démarrer le téléchargement",
    "start_download_button_tooltip": "Cliquez pour démarrer le processus de téléchargement ou d'extraction de liens avec les paramètres actuels.",
    "extract_links_button_text": "🔗 Extraire les liens",
    "pause_download_button_text": "⏸️ Mettre en pause le téléchargement",
    "pause_download_button_tooltip": "Cliquez pour mettre en pause le processus de téléchargement en cours.",
    "resume_download_button_text": "▶️ Reprendre le téléchargement",
    "resume_download_button_tooltip": "Cliquez pour reprendre le téléchargement.",
    "cancel_button_text": "❌ Annuler & Réinitialiser l'UI",
    "cancel_button_tooltip": "Cliquez pour annuler le processus de téléchargement/extraction en cours et réinitialiser les champs de l'UI (en conservant l'URL et le répertoire).",
    "error_button_text": "Erreur",
    "error_button_tooltip": "Voir les fichiers ignorés en raison d'erreurs et éventuellement les réessayer.",
    "cancel_retry_button_text": "❌ Annuler la nouvelle tentative",
    "known_chars_label_text": "🎭 Séries/Personnages connus (pour les noms de dossiers) :",
    "open_known_txt_button_text": "Ouvrir Known.txt",
    "known_chars_list_tooltip": "Cette liste contient les noms utilisés pour la création automatique de dossiers lorsque 'Dossiers séparés' est activé\net qu'aucun 'Filtrer par Personnage(s)' spécifique n'est fourni ou ne correspond à une publication.\nAjoutez les noms des séries, jeux ou personnages que vous téléchargez fréquemment.",
    "open_known_txt_button_tooltip": "Ouvrir le fichier 'Known.txt' dans votre éditeur de texte par défaut.\nLe fichier se trouve dans le répertoire de l'application.",
    "add_char_button_text": "➕ Ajouter",
    "add_char_button_tooltip": "Ajouter le nom du champ de saisie à la liste 'Séries/Personnages connus'.",
    "add_to_filter_button_text": "⤵️ Ajouter au filtre",
    "add_to_filter_button_tooltip": "Sélectionnez des noms dans la liste 'Séries/Personnages connus' pour les ajouter au champ 'Filtrer par Personnage(s)' ci-dessus.",
    "delete_char_button_text": "🗑️ Supprimer la sélection",
    "delete_char_button_tooltip": "Supprimer le(s) nom(s) sélectionné(s) de la liste 'Séries/Personnages connus'.",
    "progress_log_label_text": "📜 Journal de progression :",
    "radio_all_tooltip": "Télécharger tous les types de fichiers trouvés dans les publications.",
    "radio_images_tooltip": "Télécharger uniquement les formats d'image courants (JPG, PNG, GIF, WEBP, etc.).",
    "radio_videos_tooltip": "Télécharger uniquement les formats vidéo courants (MP4, MKV, WEBM, MOV, etc.).",
    "radio_only_archives_tooltip": "Télécharger exclusivement les fichiers .zip et .rar. Les autres options spécifiques aux fichiers sont désactivées.",
    "radio_only_audio_tooltip": "Télécharger uniquement les formats audio courants (MP3, WAV, FLAC, etc.).",
    "radio_only_links_tooltip": "Extraire et afficher les liens externes des descriptions de publications au lieu de télécharger des fichiers.\nLes options liées au téléchargement seront désactivées.",
    "favorite_mode_checkbox_tooltip": "Activer le Mode Favori pour parcourir les artistes/publications enregistrés.\nCela remplacera le champ de saisie de l'URL par des boutons de sélection de Favoris.",
    "skip_zip_checkbox_tooltip": "Si coché, les fichiers d'archive .zip ne seront pas téléchargés.\n(Désactivé si 'Archives Uniquement' est sélectionné).",
    "skip_rar_checkbox_tooltip": "Si coché, les fichiers d'archive .rar ne seront pas téléchargés.\n(Désactivé si 'Archives Uniquement' est sélectionné).",
    "download_thumbnails_checkbox_tooltip": "Télécharge les petites images d'aperçu de l'API au lieu des fichiers en taille réelle (si disponible).\nSi 'Analyser le contenu de la publication pour les URL d'images' est également coché, ce mode ne téléchargera *que* les images trouvées par l'analyse de contenu (ignorant les miniatures de l'API).",
    "scan_content_images_checkbox_tooltip": "Si coché, le téléchargeur analysera le contenu HTML des publications à la recherche d'URL d'images (à partir des balises <img> ou des liens directs).\nCela inclut la résolution des chemins relatifs des balises <img> en URL complètes.\nLes chemins relatifs dans les balises <img> (par ex., /data/image.jpg) seront résolus en URL complètes.\nUtile pour les cas où les images se trouvent dans la description de la publication mais pas dans la liste des fichiers/pièces jointes de l'API.",
    "compress_images_checkbox_tooltip": "Compresser les images > 1.5 Mo au format WebP (nécessite Pillow).",
    "use_subfolders_checkbox_tooltip": "Créer des sous-dossiers basés sur l'entrée 'Filtrer par Personnage(s)' ou les titres des publications.\nUtilise la liste 'Séries/Personnages connus' comme solution de repli pour les noms de dossiers si aucun filtre spécifique ne correspond.\nActive l'entrée 'Filtrer par Personnage(s)' et 'Nom de dossier personnalisé' pour les publications uniques.",
    "use_subfolder_per_post_checkbox_tooltip": "Crée un sous-dossier pour chaque publication. Si 'Dossiers séparés' est également activé, il se trouve à l'intérieur du dossier personnage/titre.",
    "use_cookie_checkbox_tooltip": "Si coché, tentera d'utiliser les cookies de 'cookies.txt' (format Netscape)\ndans le répertoire de l'application pour les requêtes.\nUtile pour accéder au contenu nécessitant une connexion sur Kemono/Coomer.",
    "cookie_text_input_tooltip": "Saisissez votre chaîne de cookie directement.\nCelle-ci sera utilisée si 'Utiliser le cookie' est coché ET si 'cookies.txt' n'est pas trouvé ou si ce champ n'est pas vide.\nLe format dépend de la manière dont le backend l'analysera (par ex., 'nom1=valeur1; nom2=valeur2').",
    "use_multithreading_checkbox_tooltip": "Active les opérations concurrentes. Voir le champ 'Threads' pour plus de détails.",
    "thread_count_input_tooltip": "Nombre d'opérations concurrentes.\n- Publication unique : Téléchargements de fichiers concurrents (1-10 recommandé).\n- URL de flux de créateur : Nombre de publications à traiter simultanément (1-200 recommandé).\n  Les fichiers de chaque publication sont téléchargés un par un par son worker.\nSi 'Utiliser le multithreading' est décoché, 1 thread est utilisé.",
    "external_links_checkbox_tooltip": "Si coché, un panneau de journal secondaire apparaît sous le journal principal pour afficher les liens externes trouvés dans les descriptions de publications.\n(Désactivé si le mode 'Liens Uniquement' ou 'Archives Uniquement' est actif).",
    "manga_mode_checkbox_tooltip": "Télécharge les publications du plus ancien au plus récent et renomme les fichiers en fonction du titre de la publication (pour les flux de créateurs uniquement).",
    "multipart_on_button_text": "Multi-partie : ON",
    "multipart_on_button_tooltip": "Téléchargement multi-partie : ON\n\nActive le téléchargement de gros fichiers en plusieurs segments simultanément.\n- Peut accélérer les téléchargements de fichiers volumineux uniques (par ex., des vidéos).\n- Peut augmenter l'utilisation du CPU/réseau.\n- Pour les flux avec de nombreux petits fichiers, cela pourrait ne pas offrir d'avantages en termes de vitesse et pourrait rendre l'UI/le journal chargé.\n- Si le multi-partie échoue, il réessaie en flux unique.\n\nCliquez pour désactiver.",
    "multipart_off_button_text": "Multi-partie : OFF",
    "multipart_off_button_tooltip": "Téléchargement multi-partie : OFF\n\nTous les fichiers sont téléchargés en utilisant un seul flux.\n- Stable et fonctionne bien pour la plupart des scénarios, en particulier de nombreux petits fichiers.\n- Gros fichiers téléchargés séquentiellement.\n\nCliquez pour activer (voir l'avertissement).",
    "reset_button_text": "🔄 Réinitialiser",
    "reset_button_tooltip": "Réinitialiser toutes les entrées et les journaux à leur état par défaut (uniquement lorsque l'application est inactive).",
    "progress_idle_text": "Progression : Inactif",
    "missed_character_log_label_text": "🚫 Journal des personnages manqués :",
    "creator_popup_title": "Sélection du créateur",
    "creator_popup_search_placeholder": "Rechercher par nom, service, ou coller l'URL du créateur...",
    "creator_popup_add_selected_button": "Ajouter la sélection",
    "creator_popup_scope_characters_button": "Portée : Personnages",
    "creator_popup_scope_creators_button": "Portée : Créateurs",
    "favorite_artists_button_text": "🖼️ Artistes favoris",
    "favorite_artists_button_tooltip": "Parcourez et téléchargez depuis vos artistes favoris sur Kemono.su/Coomer.su.",
    "favorite_posts_button_text": "📄 Publications favorites",
    "favorite_posts_button_tooltip": "Parcourez et téléchargez vos publications favorites depuis Kemono.su/Coomer.su.",
    "favorite_scope_selected_location_text": "Portée : Emplacement sélectionné",
    "favorite_scope_selected_location_tooltip": "Portée de téléchargement des favoris actuelle : Emplacement sélectionné\n\nTous les artistes/publications favoris sélectionnés seront téléchargés dans l' 'Emplacement de téléchargement' principal spécifié dans l'UI.\nLes filtres (personnage, mots à ignorer, type de fichier) s'appliqueront globalement à tout le contenu.\n\nCliquez pour changer pour : Dossiers d'artistes",
    "favorite_scope_artist_folders_text": "Portée : Dossiers d'artistes",
    "favorite_scope_artist_folders_tooltip": "Portée de téléchargement des favoris actuelle : Dossiers d'artistes\n\nPour chaque artiste/publication favori sélectionné, un nouveau sous-dossier (nommé d'après l'artiste) sera créé à l'intérieur de l' 'Emplacement de téléchargement' principal.\nLe contenu de cet artiste/publication sera téléchargé dans son sous-dossier spécifique.\nLes filtres (personnage, mots à ignorer, type de fichier) s'appliqueront *à l'intérieur* de chaque dossier d'artiste.\n\nCliquez pour changer pour : Emplacement sélectionné",
    "favorite_scope_unknown_text": "Portée : Inconnue",
    "favorite_scope_unknown_tooltip": "La portée de téléchargement des favoris est inconnue. Cliquez pour cycler.",
    "manga_style_post_title_text": "Nom : Titre de la publication",
    "manga_style_original_file_text": "Nom : Fichier original",
    "manga_style_date_based_text": "Nom : Basé sur la date",
    "manga_style_title_global_num_text": "Nom : Titre+Num.G",
    "manga_style_unknown_text": "Nom : Style inconnu",
    "fav_artists_dialog_title": "Artistes favoris",
    "fav_artists_loading_status": "Chargement des artistes favoris...",
    "fav_artists_search_placeholder": "Rechercher des artistes...",
    "fav_artists_select_all_button": "Tout sélectionner",
    "fav_artists_deselect_all_button": "Tout désélectionner",
    "fav_artists_download_selected_button": "Télécharger la sélection",
    "fav_artists_cancel_button": "Annuler",
    "fav_artists_loading_from_source_status": "⏳ Chargement des favoris depuis {source_name}...",
    "fav_artists_found_status": "{count} artiste(s) favori(s) trouvé(s) au total.",
    "fav_artists_none_found_status": "Aucun artiste favori trouvé sur Kemono.su ou Coomer.su.",
    "fav_artists_failed_status": "Échec de la récupération des favoris.",
    "fav_artists_cookies_required_status": "Erreur : Cookies activés mais n'ont pas pu être chargés pour aucune source.",
    "fav_artists_no_favorites_after_processing": "Aucun artiste favori trouvé après traitement.",
    "fav_artists_no_selection_title": "Aucune sélection",
    "fav_artists_no_selection_message": "Veuillez sélectionner au moins un artiste à télécharger.",
    "fav_posts_dialog_title": "Publications favorites",
    "fav_posts_loading_status": "Chargement des publications favorites...",
    "fav_posts_search_placeholder": "Rechercher des publications (titre, créateur, ID, service)...",
    "fav_posts_select_all_button": "Tout sélectionner",
    "fav_posts_deselect_all_button": "Tout désélectionner",
    "fav_posts_download_selected_button": "Télécharger la sélection",
    "fav_posts_cancel_button": "Annuler",
    "fav_posts_cookies_required_error": "Erreur : Les cookies sont requis pour les publications favorites mais n'ont pas pu être chargés.",
    "fav_posts_auth_failed_title": "Échec de l'autorisation (Publications)",
    "fav_posts_auth_failed_message": "Impossible de récupérer les favoris{domain_specific_part} en raison d'une erreur d'autorisation :\n\n{error_message}\n\nCela signifie généralement que vos cookies sont manquants, invalides ou expirés pour le site. Veuillez vérifier votre configuration de cookies.",
    "fav_posts_fetch_error_title": "Erreur de récupération",
    "fav_posts_fetch_error_message": "Erreur lors de la récupération des favoris de {domain}{error_message_part}",
    "fav_posts_no_posts_found_status": "Aucune publication favorite trouvée.",
    "fav_posts_found_status": "{count} publication(s) favorite(s) trouvée(s).",
    "fav_posts_display_error_status": "Erreur d'affichage des publications : {error}",
    "fav_posts_ui_error_title": "Erreur d'UI",
    "fav_posts_ui_error_message": "Impossible d'afficher les publications favorites : {error}",
    "fav_posts_auth_failed_message_generic": "Impossible de récupérer les favoris{domain_specific_part} en raison d'une erreur d'autorisation. Cela signifie généralement que vos cookies sont manquants, invalides ou expirés pour le site. Veuillez vérifier votre configuration de cookies.",
    "key_fetching_fav_post_list_init": "Récupération de la liste des publications favorites...",
    "key_fetching_from_source_kemono_su": "Récupération des favoris de Kemono.su...",
    "key_fetching_from_source_coomer_su": "Récupération des favoris de Coomer.su...",
    "fav_posts_fetch_cancelled_status": "Récupération des publications favorites annulée.",
    "known_names_filter_dialog_title": "Ajouter des noms connus au filtre",
    "known_names_filter_search_placeholder": "Rechercher des noms...",
    "known_names_filter_select_all_button": "Tout sélectionner",
    "known_names_filter_deselect_all_button": "Tout désélectionner",
    "known_names_filter_add_selected_button": "Ajouter la sélection",
    "error_files_dialog_title": "Fichiers ignorés en raison d'erreurs",
    "error_files_no_errors_label": "Aucun fichier n'a été enregistré comme ignoré en raison d'erreurs lors de la dernière session ou après les nouvelles tentatives.",
    "error_files_found_label": "Le(s) {count} fichier(s) suivant(s) a(ont) été ignoré(s) en raison d'erreurs de téléchargement :",
    "error_files_select_all_button": "Tout sélectionner",
    "error_files_retry_selected_button": "Réessayer la sélection",
    "error_files_export_urls_button": "Exporter les URL en .txt",
    "error_files_no_selection_retry_message": "Veuillez sélectionner au moins un fichier à réessayer.",
    "error_files_no_errors_export_title": "Aucune erreur",
    "error_files_no_errors_export_message": "Il n'y a aucune URL de fichier en erreur à exporter.",
    "error_files_no_urls_found_export_title": "Aucune URL trouvée",
    "error_files_no_urls_found_export_message": "Impossible d'extraire des URL de la liste des fichiers en erreur à exporter.",
    "error_files_save_dialog_title": "Enregistrer les URL des fichiers en erreur",
    "error_files_export_success_title": "Exportation réussie",
    "error_files_export_success_message": "{count} entrées exportées avec succès vers :\n{filepath}",
    "error_files_export_error_title": "Erreur d'exportation",
    "error_files_export_error_message": "Impossible d'exporter les liens de fichiers : {error}",
    "export_options_dialog_title": "Options d'exportation",
    "export_options_description_label": "Choisissez le format d'exportation des liens de fichiers en erreur :",
    "export_options_radio_link_only": "Lien par ligne (URL uniquement)",
    "export_options_radio_link_only_tooltip": "Exporte uniquement l'URL de téléchargement direct pour chaque fichier échoué, une URL par ligne.",
    "export_options_radio_with_details": "Exporter avec les détails (URL [Publication, Infos fichier])",
    "export_options_radio_with_details_tooltip": "Exporte l'URL suivie de détails comme le titre de la publication, l'ID de la publication et le nom de fichier original entre crochets.",
    "export_options_export_button": "Exporter",
    "no_errors_logged_title": "Aucune erreur enregistrée",
    "no_errors_logged_message": "Aucun fichier n'a été enregistré comme ignoré en raison d'erreurs lors de la dernière session ou après les nouvelles tentatives.",
    "progress_initializing_text": "Progression : Initialisation...",
    "progress_posts_text": "Progression : {processed_posts} / {total_posts} publications ({progress_percent:.1f}%)",
    "progress_processing_post_text": "Progression : Traitement de la publication {processed_posts}...",
    "progress_starting_text": "Progression : Démarrage...",
    "downloading_file_known_size_text": "Téléchargement de '{filename}' ({downloaded_mb:.1f}Mo / {total_mb:.1f}Mo)",
    "downloading_file_unknown_size_text": "Téléchargement de '{filename}' ({downloaded_mb:.1f}Mo)",
    "downloading_multipart_text": "DL '{filename}...': {downloaded_mb:.1f}/{total_mb:.1f} Mo ({parts} parties @ {speed:.2f} Mo/s)",
    "downloading_multipart_initializing_text": "Fichier : {filename} - Initialisation des parties...",
    "status_completed": "Terminé",
    "status_cancelled_by_user": "Annulé par l'utilisateur",
    "files_downloaded_label": "téléchargés",
    "files_skipped_label": "ignorés",
    "retry_finished_text": "Nouvelle tentative terminée",
    "succeeded_text": "Réussi",
    "failed_text": "Échoué",
    "ready_for_new_task_text": "Prêt pour une nouvelle tâche.",
    "fav_mode_active_label_text": "⭐ Le Mode Favori est actif. Veuillez sélectionner les filtres ci-dessous avant de choisir vos artistes/publications favoris. Sélectionnez une action ci-dessous.",
    "export_links_button_text": "Exporter les liens",
    "download_extracted_links_button_text": "Télécharger",
    "download_selected_button_text": "Télécharger la sélection",
    "link_input_placeholder_text": "ex., https://kemono.su/patreon/user/12345 ou .../post/98765",
    "link_input_tooltip_text": "Saisissez l'URL complète d'une page de créateur Kemono/Coomer ou d'une publication spécifique.\nExemple (Créateur) : https://kemono.su/patreon/user/12345\nExemple (Publication) : https://kemono.su/patreon/user/12345/post/98765",
    "dir_input_placeholder_text": "Sélectionnez le dossier où les téléchargements seront enregistrés",
    "dir_input_tooltip_text": "Saisissez ou parcourez jusqu'au dossier principal où tout le contenu téléchargé sera enregistré.\nCeci est requis sauf si le mode 'Liens Uniquement' est sélectionné.",
    "character_input_placeholder_text": "ex., Tifa, Aerith, (Cloud, Zack)",
    "custom_folder_input_placeholder_text": "Optionnel : Enregistrer cette publication dans un dossier spécifique",
    "custom_folder_input_tooltip_text": "Si vous téléchargez une URL de publication unique ET que 'Dossiers séparés par Nom/Titre' est activé,\nvous pouvez saisir un nom personnalisé ici pour le dossier de téléchargement de cette publication.\nExemple : Ma Scène Favorite",
    "skip_words_input_placeholder_text": "ex., WM, WIP, sketch, preview",
    "remove_from_filename_input_placeholder_text": "ex., patreon, HD",
    "cookie_text_input_placeholder_no_file_selected_text": "Chaîne de cookie (si aucun cookies.txt n'est sélectionné)",
    "cookie_text_input_placeholder_with_file_selected_text": "Utilisation du fichier de cookie sélectionné (voir Parcourir...)",
    "character_search_input_placeholder_text": "Rechercher des personnages...",
    "character_search_input_tooltip_text": "Tapez ici pour filtrer la liste des séries/personnages connus ci-dessous.",
    "new_char_input_placeholder_text": "Ajouter un nouveau nom de série/personnage",
    "new_char_input_tooltip_text": "Saisissez un nouveau nom de série, de jeu ou de personnage à ajouter à la liste ci-dessus.",
    "link_search_input_placeholder_text": "Rechercher des liens...",
    "link_search_input_tooltip_text": "En mode 'Liens Uniquement', tapez ici pour filtrer les liens affichés par texte, URL ou plateforme.",
    "manga_date_prefix_input_placeholder_text": "Préfixe pour les noms de fichiers Manga",
    "manga_date_prefix_input_tooltip_text": "Préfixe optionnel pour les noms de fichiers manga 'Basé sur la date' ou 'Fichier original' (ex., 'Nom de la Série').\nSi vide, les fichiers seront nommés en fonction du style sans préfixe.",
    "log_display_mode_links_view_text": "🔗 Vue des liens",
    "log_display_mode_progress_view_text": "⬇️ Vue de la progression",
    "download_external_links_dialog_title": "Télécharger les liens externes sélectionnés",
    "select_all_button_text": "Tout sélectionner",
    "deselect_all_button_text": "Tout désélectionner",
    "cookie_browse_button_tooltip": "Rechercher un fichier de cookie (format Netscape, généralement cookies.txt).\nCelui-ci sera utilisé si 'Utiliser le cookie' est coché et que le champ de texte ci-dessus est vide.",
    "page_range_label_text": "Plage de pages :",
    "start_page_input_placeholder": "Début",
    "start_page_input_tooltip": "Pour les URL de créateurs : Spécifiez le numéro de la page de départ pour le téléchargement (ex., 1, 2, 3).\nLaissez vide ou mettez 1 pour commencer à la première page.\nDésactivé pour les URL de publications uniques ou en Mode Manga/BD.",
    "page_range_to_label_text": "à",
    "end_page_input_placeholder": "Fin",
    "end_page_input_tooltip": "Pour les URL de créateurs : Spécifiez le numéro de la page de fin pour le téléchargement (ex., 5, 10).\nLaissez vide pour télécharger toutes les pages à partir de la page de départ.\nDésactivé pour les URL de publications uniques ou en Mode Manga/BD.",
    "known_names_help_button_tooltip_text": "Ouvrir le guide des fonctionnalités de l'application.",
    "future_settings_button_tooltip_text": "Ouvrir les paramètres de l'application (Thème, Langue, etc.).",
    "link_search_button_tooltip_text": "Filtrer les liens affichés",
    "confirm_add_all_dialog_title": "Confirmer l'ajout de nouveaux noms",
    "confirm_add_all_info_label": "Les nouveaux noms/groupes suivants de votre entrée 'Filtrer par Personnage(s)' ne sont pas dans 'Known.txt'.\nLeur ajout peut améliorer l'organisation des dossiers pour les futurs téléchargements.\n\nVeuillez examiner la liste et choisir une action :",
    "confirm_add_all_select_all_button": "Tout sélectionner",
    "confirm_add_all_deselect_all_button": "Tout désélectionner",
    "confirm_add_all_add_selected_button": "Ajouter la sélection à Known.txt",
    "confirm_add_all_skip_adding_button": "Ignorer l'ajout de ceux-ci",
    "confirm_add_all_cancel_download_button": "Annuler le téléchargement",
    "cookie_help_dialog_title": "Instructions pour le fichier de cookies",
    "cookie_help_instruction_intro": "<p>Pour utiliser les cookies, vous avez généralement besoin d'un fichier <b>cookies.txt</b> de votre navigateur.</p>",
    "cookie_help_how_to_get_title": "<p><b>Comment obtenir cookies.txt :</b></p>",
    "cookie_help_step1_extension_intro": "<li>Installez l'extension 'Get cookies.txt LOCALLY' pour votre navigateur basé sur Chrome :<br><a href=\"https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc\" style=\"color: #87CEEB;\">Get cookies.txt LOCALLY sur le Chrome Web Store</a></li>",
    "cookie_help_step2_login": "<li>Allez sur le site web (ex., kemono.su ou coomer.su) et connectez-vous si nécessaire.</li>",
    "cookie_help_step3_click_icon": "<li>Cliquez sur l'icône de l'extension dans la barre d'outils de votre navigateur.</li>",
    "cookie_help_step4_export": "<li>Cliquez sur un bouton 'Exporter' (ex., \"Exporter sous\", \"Exporter cookies.txt\" - le libellé exact peut varier selon la version de l'extension).</li>",
    "cookie_help_step5_save_file": "<li>Enregistrez le fichier <code>cookies.txt</code> téléchargé sur votre ordinateur.</li>",
    "cookie_help_step6_app_intro": "<li>Dans cette application :<ul>",
    "cookie_help_step6a_checkbox": "<li>Assurez-vous que la case 'Utiliser le cookie' est cochée.</li>",
    "cookie_help_step6b_browse": "<li>Cliquez sur le bouton 'Parcourir...' à côté du champ de texte du cookie.</li>",
    "cookie_help_step6c_select": "<li>Sélectionnez le fichier <code>cookies.txt</code> que vous venez d'enregistrer.</li></ul></li>",
    "cookie_help_alternative_paste": "<p>Alternativement, certaines extensions peuvent vous permettre de copier la chaîne de cookie directement. Si c'est le cas, vous pouvez la coller dans le champ de texte au lieu de rechercher un fichier.</p>",
    "cookie_help_proceed_without_button": "Télécharger sans cookies",
    "cookie_help_cancel_download_button": "Annuler le téléchargement",
    "character_input_tooltip": "Saisissez les noms des personnages (séparés par des virgules). Prend en charge le groupement avancé et affecte le nommage des dossiers si 'Dossiers séparés' est activé.\n\nExemples :\n- Nami → Correspond à 'Nami', crée le dossier 'Nami'.\n- (Ulti, Vivi) → Correspond à l'un ou l'autre, dossier 'Ulti Vivi', ajoute les deux à Known.txt séparément.\n- (Boa, Hancock)~ → Correspond à l'un ou l'autre, dossier 'Boa Hancock', ajoute comme un seul groupe dans Known.txt.\n\nLes noms sont traités comme des alias pour la correspondance.\n\nModes de filtre (le bouton cycle) :\n- Fichiers : Filtre par nom de fichier.\n- Titre : Filtre par titre de publication.\n- Les deux : Titre d'abord, puis nom de fichier.\n- Commentaires (Bêta) : Nom de fichier d'abord, puis commentaires de la publication.",
    "tour_dialog_title": "Bienvenue dans Kemono Downloader !",
    "tour_dialog_never_show_checkbox": "Ne plus jamais afficher cette visite",
    "tour_dialog_skip_button": "Passer la visite",
    "tour_dialog_back_button": "Retour",
    "tour_dialog_next_button": "Suivant",
    "tour_dialog_finish_button": "Terminer",
    "tour_dialog_step1_title": "👋 Bienvenue !",
    "tour_dialog_step1_content": "Bonjour ! Cette visite rapide vous guidera à travers les principales fonctionnalités de Kemono Downloader, y compris les mises à jour récentes comme le filtrage amélioré, les améliorations du mode manga et la gestion des cookies.\n<ul>\n<li>Mon objectif est de vous aider à télécharger facilement du contenu de <b>Kemono</b> et <b>Coomer</b>.</li><br>\n<li><b>🎨 Bouton de sélection du créateur :</b> À côté de la saisie de l'URL, cliquez sur l'icône de la palette pour ouvrir une boîte de dialogue. Parcourez et sélectionnez les créateurs de votre fichier <code>creators.json</code> pour ajouter rapidement leurs noms à la saisie de l'URL.</li><br>\n<li><b>Conseil important : L'application '(Ne répond pas)' ?</b><br>\nAprès avoir cliqué sur 'Démarrer le téléchargement', en particulier pour les grands flux de créateurs ou avec de nombreux threads, l'application peut temporairement afficher '(Ne répond pas)'. Votre système d'exploitation (Windows, macOS, Linux) pourrait même vous suggérer de 'Terminer le processus' ou de 'Forcer à quitter'.<br>\n<b>Veuillez être patient !</b> L'application travaille souvent d'arrache-pied en arrière-plan. Avant de forcer la fermeture, essayez de vérifier votre 'Emplacement de téléchargement' choisi dans votre explorateur de fichiers. Si vous voyez de nouveaux dossiers se créer ou des fichiers apparaître, cela signifie que le téléchargement progresse correctement. Donnez-lui un peu de temps pour redevenir réactif.</li><br>\n<li>Utilisez les boutons <b>Suivant</b> et <b>Retour</b> pour naviguer.</li><br>\n<li>De nombreuses options ont des info-bulles si vous les survolez pour plus de détails.</li><br>\n<li>Cliquez sur <b>Passer la visite</b> pour fermer ce guide à tout moment.</li><br>\n<li>Cochez <b>'Ne plus jamais afficher cette visite'</b> si vous ne voulez pas voir cela lors des démarrages futurs.</li>\n</ul>",
    "tour_dialog_step2_title": "① Pour commencer",
    "tour_dialog_step2_content": "Commençons par les bases du téléchargement :\n<ul>\n<li><b>🔗 URL Créateur/Post Kemono :</b><br>\nCollez l'adresse web complète (URL) de la page d'un créateur (par ex., <i>https://kemono.su/patreon/user/12345</i>) \nou d'une publication spécifique (par ex., <i>.../post/98765</i>).<br>\nou d'un créateur Coomer (par ex., <i>https://coomer.su/onlyfans/user/artistname</i>)</li><br>\n<li><b>📁 Emplacement de téléchargement :</b><br>\nCliquez sur 'Parcourir...' pour choisir un dossier sur votre ordinateur où tous les fichiers téléchargés seront enregistrés. \nCeci est requis sauf si vous utilisez le mode 'Liens Uniquement'.</li><br>\n<li><b>📄 Plage de pages (URL de créateur uniquement) :</b><br>\nSi vous téléchargez depuis la page d'un créateur, vous pouvez spécifier une plage de pages à récupérer (par ex., pages 2 à 5). \nLaissez vide pour toutes les pages. Ceci est désactivé pour les URL de publications uniques ou lorsque le <b>Mode Manga/BD</b> est actif.</li>\n</ul>",
    "tour_dialog_step3_title": "② Filtrage des téléchargements",
    "tour_dialog_step3_content": "Affinez ce que vous téléchargez avec ces filtres (la plupart sont désactivés en modes 'Liens Uniquement' ou 'Archives Uniquement') :\n<ul>\n<li><b>🎯 Filtrer par Personnage(s) :</b><br>\nSaisissez les noms des personnages, séparés par des virgules (par ex., <i>Tifa, Aerith</i>). Groupez les alias pour un nom de dossier combiné : <i>(alias1, alias2, alias3)</i> devient le dossier 'alias1 alias2 alias3' (après nettoyage). Tous les noms du groupe sont utilisés comme alias pour la correspondance.<br>\nLe bouton <b>'Filtre : [Type]'</b> (à côté de cette entrée) change la façon dont ce filtre s'applique :\n<ul><li><i>Filtre : Fichiers :</i> Vérifie les noms de fichiers individuels. Une publication est conservée si un fichier correspond ; seuls les fichiers correspondants sont téléchargés. Le nommage du dossier utilise le personnage du nom de fichier correspondant (si 'Dossiers séparés' est activé).</li><br>\n<li><i>Filtre : Titre :</i> Vérifie les titres des publications. Tous les fichiers d'une publication correspondante sont téléchargés. Le nommage du dossier utilise le personnage du titre de la publication correspondante.</li>\n<li><b>⤵️ Bouton Ajouter au filtre (Noms connus) :</b> À côté du bouton 'Ajouter' pour les Noms connus (voir Étape 5), cela ouvre une popup. Sélectionnez les noms de votre liste <code>Known.txt</code> via des cases à cocher (avec une barre de recherche) pour les ajouter rapidement au champ 'Filtrer par Personnage(s)'. Les noms groupés comme <code>(Boa, Hancock)</code> de Known.txt seront ajoutés comme <code>(Boa, Hancock)~</code> au filtre.</li><br>\n<li><i>Filtre : Les deux :</i> Vérifie d'abord le titre de la publication. S'il correspond, tous les fichiers sont téléchargés. Sinon, il vérifie ensuite les noms de fichiers, et seuls les fichiers correspondants sont téléchargés. Le nommage du dossier priorise la correspondance de titre, puis la correspondance de fichier.</li><br>\n<li><i>Filtre : Commentaires (Bêta) :</i> Vérifie d'abord les noms de fichiers. Si un fichier correspond, tous les fichiers de la publication sont téléchargés. Si aucune correspondance de fichier, il vérifie alors les commentaires de la publication. Si un commentaire correspond, tous les fichiers sont téléchargés. (Utilise plus de requêtes API). Le nommage du dossier priorise la correspondance de fichier, puis la correspondance de commentaire.</li></ul>\nCe filtre influence également le nommage des dossiers si 'Dossiers séparés par Nom/Titre' est activé.</li><br>\n<li><b>🚫 Ignorer avec les mots :</b><br>\nSaisissez des mots, séparés par des virgules (par ex., <i>WIP, sketch, preview</i>). \nLe bouton <b>'Portée : [Type]'</b> (à côté de cette entrée) change la façon dont ce filtre s'applique :\n<ul><li><i>Portée : Fichiers :</i> Ignore les fichiers si leurs noms contiennent l'un de ces mots.</li><br>\n<li><i>Portée : Publications :</i> Ignore les publications entières si leurs titres contiennent l'un de ces mots.</li><br>\n<li><i>Portée : Les deux :</i> Applique à la fois l'omission par titre de fichier et de publication (publication d'abord, puis fichiers).</li></ul></li><br>\n<li><b>Filtrer les fichiers (Boutons radio) :</b> Choisissez ce qu'il faut télécharger :\n<ul>\n<li><i>Tout :</i> Télécharge tous les types de fichiers trouvés.</li><br>\n<li><i>Images/GIFs :</i> Uniquement les formats d'image courants et les GIFs.</li><br>\n<li><i>Vidéos :</i> Uniquement les formats vidéo courants.</li><br>\n<li><b><i>📦 Archives Uniquement :</i></b> Télécharge exclusivement les fichiers <b>.zip</b> et <b>.rar</b>. Lorsque cette option est sélectionnée, les cases à cocher 'Ignorer .zip' et 'Ignorer .rar' sont automatiquement désactivées et décochées. 'Afficher les liens externes' est également désactivé.</li><br>\n<li><i>🎧 Audio Uniquement :</i> Uniquement les formats audio courants (MP3, WAV, FLAC, etc.).</li><br>\n<li><i>🔗 Liens Uniquement :</i> Extrait et affiche les liens externes des descriptions de publications au lieu de télécharger des fichiers. Les options liées au téléchargement et 'Afficher les liens externes' sont désactivées.</li>\n</ul></li>\n</ul>",
    "tour_dialog_step4_title": "③ Mode Favori (Téléchargement alternatif)",
    "tour_dialog_step4_content": "L'application propose un 'Mode Favori' pour télécharger du contenu d'artistes que vous avez mis en favoris sur Kemono.su.\n<ul>\n<li><b>⭐ Case à cocher Mode Favori :</b><br>\nSituée à côté du bouton radio '🔗 Liens Uniquement'. Cochez cette case pour activer le Mode Favori.</li><br>\n<li><b>Que se passe-t-il en Mode Favori :</b>\n<ul><li>La zone de saisie '🔗 URL Créateur/Post Kemono' est remplacée par un message indiquant que le Mode Favori est actif.</li><br>\n<li>Les boutons standard 'Démarrer le téléchargement', 'Pause', 'Annuler' sont remplacés par les boutons '🖼️ Artistes favoris' et '📄 Publications favorites' (Note : 'Publications favorites' est prévu pour le futur).</li><br>\n<li>L'option '🍪 Utiliser le cookie' est automatiquement activée et verrouillée, car les cookies sont nécessaires pour récupérer vos favoris.</li></ul></li><br>\n<li><b>🖼️ Bouton Artistes favoris :</b><br>\nCliquez ici pour ouvrir une boîte de dialogue listant vos artistes favoris de Kemono.su. Vous pouvez sélectionner un ou plusieurs artistes à télécharger.</li><br>\n<li><b>Portée de téléchargement des favoris (Bouton) :</b><br>\nCe bouton (à côté de 'Publications favorites') contrôle où les favoris sélectionnés sont téléchargés :\n<ul><li><i>Portée : Emplacement sélectionné :</i> Tous les artistes sélectionnés sont téléchargés dans l' 'Emplacement de téléchargement' principal que vous avez défini. Les filtres s'appliquent globalement.</li><br>\n<li><i>Portée : Dossiers d'artistes :</i> Un sous-dossier (nommé d'après l'artiste) est créé dans votre 'Emplacement de téléchargement' principal pour chaque artiste sélectionné. Le contenu de cet artiste va dans son dossier spécifique. Les filtres s'appliquent à l'intérieur de chaque dossier d'artiste.</li></ul></li><br>\n<li><b>Filtres en Mode Favori :</b><br>\nLes options 'Filtrer par Personnage(s)', 'Ignorer avec les mots' et 'Filtrer les fichiers' s'appliquent toujours au contenu téléchargé de vos artistes favoris sélectionnés.</li>\n</ul>",
    "tour_dialog_step5_title": "④ Affiner les téléchargements",
    "tour_dialog_step5_content": "Plus d'options pour personnaliser vos téléchargements :\n<ul>\n<li><b>Ignorer .zip / Ignorer .rar :</b> Cochez ces cases pour éviter de télécharger ces types de fichiers d'archive. \n<i>(Note : Celles-ci sont désactivées et ignorées si le mode de filtre '📦 Archives Uniquement' est sélectionné).</i></li><br>\n<li><b>✂️ Supprimer les mots du nom :</b><br>\nSaisissez des mots, séparés par des virgules (par ex., <i>patreon, [HD]</i>), à supprimer des noms de fichiers téléchargés (insensible à la casse).</li><br>\n<li><b>Télécharger les miniatures uniquement :</b> Télécharge les petites images d'aperçu au lieu des fichiers en taille réelle (si disponible).</li><br>\n<li><b>Compresser les grandes images :</b> Si la bibliothèque 'Pillow' est installée, les images de plus de 1.5 Mo seront converties au format WebP si la version WebP est significativement plus petite.</li><br>\n<li><b>🗄️ Nom de dossier personnalisé (Publication unique uniquement) :</b><br>\nSi vous téléchargez une URL de publication spécifique ET que 'Dossiers séparés par Nom/Titre' est activé, \nvous pouvez saisir un nom personnalisé ici pour le dossier de téléchargement de cette publication.</li><br>\n<li><b>🍪 Utiliser le cookie :</b> Cochez cette case pour utiliser des cookies pour les requêtes. Vous pouvez soit :\n<ul><li>Saisir une chaîne de cookie directement dans le champ de texte (par ex., <i>nom1=valeur1; nom2=valeur2</i>).</li><br>\n<li>Cliquer sur 'Parcourir...' pour sélectionner un fichier <i>cookies.txt</i> (format Netscape). Le chemin apparaîtra dans le champ de texte.</li></ul>\nCeci est utile pour accéder au contenu qui nécessite une connexion. Le champ de texte a la priorité s'il est rempli. \nSi 'Utiliser le cookie' est coché mais que le champ de texte et le fichier parcouru sont vides, il essaiera de charger 'cookies.txt' depuis le répertoire de l'application.</li>\n</ul>",
    "tour_dialog_step6_title": "⑤ Organisation & Performance",
    "tour_dialog_step6_content": "Organisez vos téléchargements et gérez les performances :\n<ul>\n<li><b>⚙️ Dossiers séparés par Nom/Titre :</b> Crée des sous-dossiers basés sur l'entrée 'Filtrer par Personnage(s)' ou les titres des publications (peut utiliser la liste <b>Known.txt</b> comme solution de repli pour les noms de dossiers).</li><br>\n<li><b>Sous-dossier par publication :</b> Si 'Dossiers séparés' est activé, cela crée un sous-dossier supplémentaire pour <i>chaque publication individuelle</i> à l'intérieur du dossier principal personnage/titre.</li><br>\n<li><b>🚀 Utiliser le multithreading (Threads) :</b> Active des opérations plus rapides. Le nombre dans l'entrée 'Threads' signifie :\n<ul><li>Pour les <b>Flux de créateurs :</b> Nombre de publications à traiter simultanément. Les fichiers de chaque publication sont téléchargés séquentiellement par son worker (sauf si le nommage de manga 'Basé sur la date' est activé, ce qui force 1 worker de publication).</li><br>\n<li>Pour les <b>URL de publications uniques :</b> Nombre de fichiers à télécharger simultanément à partir de cette seule publication.</li></ul>\nSi décoché, 1 thread est utilisé. Des nombres élevés de threads (par ex., >40) peuvent afficher un avertissement.</li><br>\n<li><b>Bascule de téléchargement multi-partie (en haut à droite de la zone du journal) :</b><br>\nLe bouton <b>'Multi-partie : [ON/OFF]'</b> permet d'activer/désactiver les téléchargements multi-segments pour les fichiers volumineux individuels. \n<ul><li><b>ON :</b> Peut accélérer les téléchargements de fichiers volumineux (par ex., des vidéos) mais peut augmenter les saccades de l'UI ou le spam du journal avec de nombreux petits fichiers. Un avertissement apparaîtra lors de l'activation. Si un téléchargement multi-partie échoue, il réessaie en flux unique.</li><br>\n<li><b>OFF (Défaut) :</b> Les fichiers sont téléchargés en un seul flux.</li></ul>\nCeci est désactivé si le mode 'Liens Uniquement' ou 'Archives Uniquement' est actif.</li><br>\n<li><b>📖 Mode Manga/BD (URL de créateur uniquement) :</b> Conçu pour le contenu séquentiel.\n<ul>\n<li>Télécharge les publications du <b>plus ancien au plus récent</b>.</li><br>\n<li>L'entrée 'Plage de pages' est désactivée car toutes les publications sont récupérées.</li><br>\n<li>Un <b>bouton de bascule de style de nom de fichier</b> (par ex., 'Nom : Titre de la publication') apparaît en haut à droite de la zone du journal lorsque ce mode est actif pour un flux de créateur. Cliquez dessus pour cycler entre les styles de nommage :\n<ul>\n<li><b><i>Nom : Titre de la publication (Défaut) :</i></b> Le premier fichier d'une publication est nommé d'après le titre nettoyé de la publication (par ex., 'Mon Chapitre 1.jpg'). Les fichiers suivants dans la *même publication* tenteront de conserver leurs noms de fichiers originaux (par ex., 'page_02.png', 'bonus_art.jpg'). Si la publication n'a qu'un seul fichier, il est nommé d'après le titre de la publication. C'est généralement recommandé pour la plupart des mangas/BD.</li><br>\n<li><b><i>Nom : Fichier original :</i></b> Tous les fichiers tentent de conserver leurs noms de fichiers originaux. Un préfixe optionnel (par ex., 'MaSerie_') peut être saisi dans le champ de saisie qui apparaît à côté du bouton de style. Exemple : 'MaSerie_FichierOriginal.jpg'.</li><br>\n<li><b><i>Nom : Titre+Num.G (Titre de la publication + Numérotation globale) :</i></b> Tous les fichiers de toutes les publications de la session de téléchargement actuelle sont nommés séquentiellement en utilisant le titre nettoyé de la publication comme préfixe, suivi d'un compteur global. Par exemple : Publication 'Chapitre 1' (2 fichiers) -> 'Chapitre 1_001.jpg', 'Chapitre 1_002.png'. La publication suivante, 'Chapitre 2' (1 fichier), continuerait la numérotation -> 'Chapitre 2_003.jpg'. Le multithreading pour le traitement des publications est automatiquement désactivé pour ce style afin d'assurer une numérotation globale correcte.</li><br>\n<li><b><i>Nom : Basé sur la date :</i></b> Les fichiers sont nommés séquentiellement (001.ext, 002.ext, ...) en fonction de l'ordre de publication des publications. Un préfixe optionnel (par ex., 'MaSerie_') peut être saisi dans le champ de saisie qui apparaît à côté du bouton de style. Exemple : 'MaSerie_001.jpg'. Le multithreading pour le traitement des publications est automatiquement désactivé pour ce style.</li>\n</ul>\n</li><br>\n<li>Pour de meilleurs résultats avec les styles 'Nom : Titre de la publication', 'Nom : Titre+Num.G' ou 'Nom : Basé sur la date', utilisez le champ 'Filtrer par Personnage(s)' avec le titre du manga/de la série pour l'organisation des dossiers.</li>\n</ul></li><br>\n<li><b>🎭 Known.txt pour une organisation intelligente des dossiers :</b><br>\n<code>Known.txt</code> (dans le répertoire de l'application) permet un contrôle fin de l'organisation automatique des dossiers lorsque 'Dossiers séparés par Nom/Titre' est actif.\n<ul>\n<li><b>Comment ça marche :</b> Chaque ligne de <code>Known.txt</code> est une entrée. \n<ul><li>Une ligne simple comme <code>Ma Super Série</code> signifie que le contenu correspondant ira dans un dossier nommé \"Ma Super Série\".</li><br>\n<li>Une ligne groupée comme <code>(Personnage A, Perso A, Nom Alt A)</code> signifie que le contenu correspondant à \"Personnage A\", \"Perso A\", OU \"Nom Alt A\" ira TOUS dans un seul dossier nommé \"Personnage A Perso A Nom Alt A\" (après nettoyage). Tous les termes entre parenthèses deviennent des alias pour ce dossier.</li></ul></li>\n<li><b>Repli intelligent :</b> Lorsque 'Dossiers séparés par Nom/Titre' est actif, et si une publication ne correspond à aucune entrée spécifique 'Filtrer par Personnage(s)', le téléchargeur consulte <code>Known.txt</code> pour trouver un nom principal correspondant pour la création du dossier.</li><br>\n<li><b>Gestion conviviale :</b> Ajoutez des noms simples (non groupés) via la liste de l'UI ci-dessous. Pour une édition avancée (comme la création/modification d'alias groupés), cliquez sur <b>'Ouvrir Known.txt'</b> pour éditer le fichier dans votre éditeur de texte. L'application le recharge à la prochaine utilisation ou au prochain démarrage.</li>\n</ul>\n</li>\n</ul>",
    "tour_dialog_step7_title": "⑥ Erreurs courantes & Dépannage",
    "tour_dialog_step7_content": "Parfois, les téléchargements peuvent rencontrer des problèmes. Voici quelques-uns des plus courants :\n<ul>\n<li><b>Info-bulle de saisie de personnage :</b><br>\nSaisissez les noms des personnages, séparés par des virgules (par ex., <i>Tifa, Aerith</i>).<br>\nGroupez les alias pour un nom de dossier combiné : <i>(alias1, alias2, alias3)</i> devient le dossier 'alias1 alias2 alias3'.<br>\nTous les noms du groupe sont utilisés comme alias pour la correspondance de contenu.<br><br>\nLe bouton 'Filtre : [Type]' à côté de cette entrée change la façon dont ce filtre s'applique :<br>\n- Filtre : Fichiers : Vérifie les noms de fichiers individuels. Seuls les fichiers correspondants sont téléchargés.<br>\n- Filtre : Titre : Vérifie les titres des publications. Tous les fichiers d'une publication correspondante sont téléchargés.<br>\n- Filtre : Les deux : Vérifie d'abord le titre de la publication. Si aucune correspondance, vérifie ensuite les noms de fichiers.<br>\n- Filtre : Commentaires (Bêta) : Vérifie d'abord les noms de fichiers. Si aucune correspondance, vérifie ensuite les commentaires de la publication.<br><br>\nCe filtre influence également le nommage des dossiers si 'Dossiers séparés par Nom/Titre' est activé.</li><br>\n<li><b>502 Bad Gateway / 503 Service Unavailable / 504 Gateway Timeout :</b><br>\nCeux-ci indiquent généralement des problèmes temporaires côté serveur avec Kemono/Coomer. Le site peut être surchargé, en maintenance ou rencontrer des problèmes. <br>\n<b>Solution :</b> Attendez un peu (par ex., 30 minutes à quelques heures) et réessayez plus tard. Vérifiez le site directement dans votre navigateur.</li><br>\n<li><b>Connexion perdue / Connexion refusée / Timeout (pendant le téléchargement de fichier) :</b><br>\nCela peut arriver à cause de votre connexion internet, de l'instabilité du serveur, ou si le serveur interrompt la connexion pour un fichier volumineux. <br>\n<b>Solution :</b> Vérifiez votre internet. Essayez de réduire le nombre de 'Threads' s'il est élevé. L'application pourrait proposer de réessayer certains fichiers échoués à la fin d'une session.</li><br>\n<li><b>Erreur IncompleteRead :</b><br>\nLe serveur a envoyé moins de données que prévu. Souvent un problème réseau temporaire ou un problème de serveur. <br>\n<b>Solution :</b> L'application marquera souvent ces fichiers pour une nouvelle tentative à la fin de la session de téléchargement.</li><br>\n<li><b>403 Forbidden / 401 Unauthorized (moins courant pour les publications publiques) :</b><br>\nVous n'avez peut-être pas la permission d'accéder au contenu. Pour certains contenus payants ou privés, l'utilisation de l'option 'Utiliser le cookie' avec des cookies valides de votre session de navigateur pourrait aider. Assurez-vous que vos cookies sont à jour.</li><br>\n<li><b>404 Not Found :</b><br>\nL'URL de la publication ou du fichier est incorrecte, ou le contenu a été supprimé du site. Vérifiez l'URL.</li><br>\n<li><b>'Aucune publication trouvée' / 'Publication cible non trouvée' :</b><br>\nAssurez-vous que l'URL est correcte et que le créateur/la publication existe. Si vous utilisez des plages de pages, assurez-vous qu'elles sont valides pour le créateur. Pour les publications très récentes, il peut y avoir un léger délai avant qu'elles n'apparaissent dans l'API.</li><br>\n<li><b>Lenteur générale / Application '(Ne répond pas)' :</b><br>\nComme mentionné à l'étape 1, si l'application semble se bloquer après le démarrage, en particulier avec de grands flux de créateurs ou de nombreux threads, veuillez lui donner du temps. Elle traite probablement des données en arrière-plan. Réduire le nombre de threads peut parfois améliorer la réactivité si cela est fréquent.</li>\n</ul>",
    "tour_dialog_step8_title": "⑦ Journaux & Contrôles finaux",
    "tour_dialog_step8_content": "Surveillance et Contrôles :\n<ul>\n<li><b>📜 Journal de progression / Journal des liens extraits :</b> Affiche les messages de téléchargement détaillés. Si le mode '🔗 Liens Uniquement' est actif, cette zone affiche les liens extraits.</li><br>\n<li><b>Afficher les liens externes dans le journal :</b> Si coché, un panneau de journal secondaire apparaît sous le journal principal pour afficher les liens externes trouvés dans les descriptions de publications. <i>(Ceci est désactivé si le mode '🔗 Liens Uniquement' ou '📦 Archives Uniquement' est actif).</i></li><br>\n<li><b>Bascule d'affichage du journal (Bouton 👁️ / 🙈) :</b><br>\nCe bouton (en haut à droite de la zone du journal) change la vue du journal principal :\n<ul><li><b>👁️ Journal de progression (Défaut) :</b> Affiche toute l'activité de téléchargement, les erreurs et les résumés.</li><br>\n<li><b>🙈 Journal des personnages manqués :</b> Affiche une liste de termes clés des titres de publications qui ont été ignorés en raison de vos paramètres 'Filtrer par Personnage(s)'. Utile pour identifier le contenu que vous pourriez manquer involontairement.</li></ul></li><br>\n<li><b>🔄 Réinitialiser :</b> Efface tous les champs de saisie, les journaux et réinitialise les paramètres temporaires à leurs valeurs par défaut. Ne peut être utilisé que lorsqu'aucun téléchargement n'est actif.</li><br>\n<li><b>⬇️ Démarrer le téléchargement / 🔗 Extraire les liens / ⏸️ Pause / ❌ Annuler :</b> Ces boutons contrôlent le processus. 'Annuler & Réinitialiser l'UI' arrête l'opération en cours et effectue une réinitialisation logicielle de l'UI, en conservant vos entrées d'URL et de répertoire. 'Pause/Reprendre' permet d'arrêter temporairement et de continuer.</li><br>\n<li>Si certains fichiers échouent avec des erreurs récupérables (comme 'IncompleteRead'), il se peut que l'on vous propose de les réessayer à la fin d'une session.</li>\n</ul>\n<br>Vous êtes prêt ! Cliquez sur <b>'Terminer'</b> pour fermer la visite et commencer à utiliser le téléchargeur.",
    "help_guide_dialog_title": "Kemono Downloader - Guide des fonctionnalités",
    "help_guide_github_tooltip": "Visiter la page GitHub du projet (S'ouvre dans le navigateur)",
    "help_guide_instagram_tooltip": "Visiter notre page Instagram (S'ouvre dans le navigateur)",
    "help_guide_discord_tooltip": "Rejoindre notre communauté Discord (S'ouvre dans le navigateur)",
    "help_guide_step1_title": "① Introduction & Entrées principales",
    "help_guide_step1_content": "<html><head/><body>\n<p>Ce guide offre un aperçu des fonctionnalités, des champs et des boutons de Kemono Downloader.</p>\n<h3>Zone de saisie principale (en haut à gauche)</h3>\n<ul>\n<li><b>🔗 URL Créateur/Post Kemono :</b>\n<ul>\n<li>Saisissez l'adresse web complète de la page d'un créateur (par ex., <i>https://kemono.su/patreon/user/12345</i>) ou d'une publication spécifique (par ex., <i>.../post/98765</i>).</li>\n<li>Prend en charge les URL de Kemono (kemono.su, kemono.party) et Coomer (coomer.su, coomer.party).</li>\n</ul>\n</li>\n<li><b>Plage de pages (Début à Fin) :</b>\n<ul>\n<li>Pour les URL de créateurs : Spécifiez une plage de pages à récupérer (par ex., pages 2 à 5). Laissez vide pour toutes les pages.</li>\n<li>Désactivé pour les URL de publications uniques ou lorsque le <b>Mode Manga/BD</b> est actif.</li>\n</ul>\n</li>\n<li><b>📁 Emplacement de téléchargement :</b>\n<ul>\n<li>Cliquez sur <b>'Parcourir...'</b> pour choisir un dossier principal sur votre ordinateur où tous les fichiers téléchargés seront enregistrés.</li>\n<li>Ce champ est requis sauf si vous utilisez le mode <b>'🔗 Liens Uniquement'</b>.</li>\n</ul>\n</li>\n<li><b>🎨 Bouton de sélection du créateur (à côté de la saisie de l'URL) :</b>\n<ul>\n<li>Cliquez sur l'icône de la palette (🎨) pour ouvrir la boîte de dialogue 'Sélection du créateur'.</li>\n<li>Cette boîte de dialogue charge les créateurs depuis votre fichier <code>creators.json</code> (qui doit se trouver dans le répertoire de l'application).</li>\n<li><b>À l'intérieur de la boîte de dialogue :</b>\n<ul>\n<li><b>Barre de recherche :</b> Tapez pour filtrer la liste des créateurs par nom ou service.</li>\n<li><b>Liste des créateurs :</b> Affiche les créateurs de votre <code>creators.json</code>. Les créateurs que vous avez mis en 'favoris' (dans les données JSON) apparaissent en haut.</li>\n<li><b>Cases à cocher :</b> Sélectionnez un ou plusieurs créateurs en cochant la case à côté de leur nom.</li>\n<li><b>Bouton 'Portée' (par ex., 'Portée : Personnages') :</b> Ce bouton bascule l'organisation du téléchargement lors de l'initiation des téléchargements à partir de cette popup :\n<ul><li><i>Portée : Personnages :</i> Les téléchargements seront organisés dans des dossiers nommés d'après les personnages directement dans votre 'Emplacement de téléchargement' principal. Les œuvres de différents créateurs pour le même personnage seront regroupées.</li>\n<li><i>Portée : Créateurs :</i> Les téléchargements créeront d'abord un dossier nommé d'après le créateur dans votre 'Emplacement de téléchargement' principal. Les sous-dossiers nommés d'après les personnages seront ensuite créés à l'intérieur du dossier de chaque créateur.</li></ul>\n</li>\n<li><b>Bouton 'Ajouter la sélection' :</b> Cliquer sur ce bouton prendra les noms de tous les créateurs cochés et les ajoutera au champ de saisie principal '🔗 URL Créateur/Post Kemono', séparés par des virgules. La boîte de dialogue se fermera alors.</li>\n</ul>\n</li>\n<li>Cette fonctionnalité offre un moyen rapide de remplir le champ URL pour plusieurs créateurs sans avoir à taper ou coller manuellement chaque URL.</li>\n</ul>\n</li>\n</ul></body></html>",
    "help_guide_step2_title": "② Filtrage des téléchargements",
    "help_guide_step2_content": "<html><head/><body>\n<h3>Filtrage des téléchargements (Panneau de gauche)</h3>\n<ul>\n<li><b>🎯 Filtrer par Personnage(s) :</b>\n<ul>\n<li>Saisissez les noms, séparés par des virgules (par ex., <code>Tifa, Aerith</code>).</li>\n<li><b>Alias groupés pour dossier partagé (Entrées Known.txt séparées) :</b> <code>(Vivi, Ulti, Uta)</code>.\n<ul><li>Le contenu correspondant à \"Vivi\", \"Ulti\", OU \"Uta\" ira dans un dossier partagé nommé \"Vivi Ulti Uta\" (après nettoyage).</li>\n<li>Si ces noms sont nouveaux, il vous sera demandé d'ajouter \"Vivi\", \"Ulti\" et \"Uta\" comme des <i>entrées individuelles séparées</i> à <code>Known.txt</code>.</li>\n</ul>\n</li>\n<li><b>Alias groupés pour dossier partagé (Entrée Known.txt unique) :</b> <code>(Yuffie, Sonon)~</code> (notez le tilde <code>~</code>).\n<ul><li>Le contenu correspondant à \"Yuffie\" OU \"Sonon\" ira dans un dossier partagé nommé \"Yuffie Sonon\".</li>\n<li>Si nouveau, \"Yuffie Sonon\" (avec les alias Yuffie, Sonon) sera proposé pour être ajouté comme une <i>entrée de groupe unique</i> à <code>Known.txt</code>.</li>\n</ul>\n</li>\n<li>Ce filtre influence le nommage des dossiers si 'Dossiers séparés par Nom/Titre' est activé.</li>\n</ul>\n</li>\n<li><b>Filtre : Bouton [Type] (Portée du filtre de personnage) :</b> Cycle la façon dont le 'Filtrer par Personnage(s)' s'applique :\n<ul>\n<li><code>Filtre : Fichiers</code> : Vérifie les noms de fichiers individuels. Une publication est conservée si un fichier correspond ; seuls les fichiers correspondants sont téléchargés. Le nommage du dossier utilise le personnage du nom de fichier correspondant.</li>\n<li><code>Filtre : Titre</code> : Vérifie les titres des publications. Tous les fichiers d'une publication correspondante sont téléchargés. Le nommage du dossier utilise le personnage du titre de la publication correspondante.</li>\n<li><code>Filtre : Les deux</code> : Vérifie d'abord le titre de la publication. S'il correspond, tous les fichiers sont téléchargés. Sinon, il vérifie ensuite les noms de fichiers, et seuls les fichiers correspondants sont téléchargés. Le nommage du dossier priorise la correspondance de titre, puis la correspondance de fichier.</li>\n<li><code>Filtre : Commentaires (Bêta)</code> : Vérifie d'abord les noms de fichiers. Si un fichier correspond, tous les fichiers de la publication sont téléchargés. Si aucune correspondance de fichier, il vérifie alors les commentaires de la publication. Si un commentaire correspond, tous les fichiers sont téléchargés. (Utilise plus de requêtes API). Le nommage du dossier priorise la correspondance de fichier, puis la correspondance de commentaire.</li>\n</ul>\n</li>\n<li><b>🗄️ Nom de dossier personnalisé (Publication unique uniquement) :</b>\n<ul>\n<li>Visible et utilisable uniquement lors du téléchargement d'une URL de publication spécifique ET si 'Dossiers séparés par Nom/Titre' est activé.</li>\n<li>Permet de spécifier un nom personnalisé pour le dossier de téléchargement de cette seule publication.</li>\n</ul>\n</li>\n<li><b>🚫 Ignorer avec les mots :</b>\n<ul><li>Saisissez des mots, séparés par des virgules (par ex., <code>WIP, sketch, preview</code>) pour ignorer certains contenus.</li></ul>\n</li>\n<li><b>Portée : Bouton [Type] (Portée des mots à ignorer) :</b> Cycle la façon dont 'Ignorer avec les mots' s'applique :\n<ul>\n<li><code>Portée : Fichiers</code> : Ignore les fichiers individuels si leurs noms contiennent l'un de ces mots.</li>\n<li><code>Portée : Publications</code> : Ignore les publications entières si leurs titres contiennent l'un de ces mots.</li>\n<li><code>Portée : Les deux</code> : Applique les deux (titre de la publication d'abord, puis fichiers individuels).</li>\n</ul>\n</li>\n<li><b>✂️ Supprimer les mots du nom :</b>\n<ul><li>Saisissez des mots, séparés par des virgules (par ex., <code>patreon, [HD]</code>), à supprimer des noms de fichiers téléchargés (insensible à la casse).</li></ul>\n</li>\n<li><b>Filtrer les fichiers (Boutons radio) :</b> Choisissez ce qu'il faut télécharger :\n<ul>\n<li><code>Tout</code> : Télécharge tous les types de fichiers trouvés.</li>\n<li><code>Images/GIFs</code> : Uniquement les formats d'image courants (JPG, PNG, GIF, WEBP, etc.) et les GIFs.</li>\n<li><code>Vidéos</code> : Uniquement les formats vidéo courants (MP4, MKV, WEBM, MOV, etc.).</li>\n<li><code>📦 Archives Uniquement</code> : Télécharge exclusivement les fichiers <b>.zip</b> et <b>.rar</b>. Lorsque cette option est sélectionnée, les cases à cocher 'Ignorer .zip' et 'Ignorer .rar' sont automatiquement désactivées et décochées. 'Afficher les liens externes' est également désactivé.</li>\n<li><code>🎧 Audio Uniquement</code> : Télécharge uniquement les formats audio courants (MP3, WAV, FLAC, M4A, OGG, etc.). Les autres options spécifiques aux fichiers se comportent comme en mode 'Images' ou 'Vidéos'.</li>\n<li><code>🔗 Liens Uniquement</code> : Extrait et affiche les liens externes des descriptions de publications au lieu de télécharger des fichiers. Les options liées au téléchargement et 'Afficher les liens externes' sont désactivées. Le bouton de téléchargement principal devient '🔗 Extraire les liens'.</li>\n</ul>\n</li>\n</ul></body></html>",
    "help_guide_step3_title": "③ Options de téléchargement & Paramètres",
    "help_guide_step3_content": "<html><head/><body>\n<h3>Options de téléchargement & Paramètres (Panneau de gauche)</h3>\n<ul>\n<li><b>Ignorer .zip / Ignorer .rar :</b> Cases à cocher pour éviter de télécharger ces types de fichiers d'archive. (Désactivées et ignorées si le mode de filtre '📦 Archives Uniquement' est sélectionné).</li>\n<li><b>Télécharger les miniatures uniquement :</b> Télécharge les petites images d'aperçu au lieu des fichiers en taille réelle (si disponible).</li>\n<li><b>Compresser les grandes images (en WebP) :</b> Si la bibliothèque 'Pillow' (PIL) est installée, les images de plus de 1.5 Mo seront converties au format WebP si la version WebP est significativement plus petite.</li>\n<li><b>⚙️ Paramètres avancés :</b>\n<ul>\n<li><b>Dossiers séparés par Nom/Titre :</b> Crée des sous-dossiers basés sur l'entrée 'Filtrer par Personnage(s)' ou les titres des publications. Peut utiliser la liste <b>Known.txt</b> comme solution de repli pour les noms de dossiers.</li></ul></li></ul></body></html>",
    "help_guide_step4_title": "④ Paramètres avancés (Partie 1)",
    "help_guide_step4_content": "<html><head/><body><h3>⚙️ Paramètres avancés (Suite)</h3><ul><ul>\n<li><b>Sous-dossier par publication :</b> Si 'Dossiers séparés' est activé, cela crée un sous-dossier supplémentaire pour <i>chaque publication individuelle</i> à l'intérieur du dossier principal personnage/titre.</li>\n<li><b>Utiliser le cookie :</b> Cochez cette case pour utiliser des cookies pour les requêtes.\n<ul>\n<li><b>Champ de texte :</b> Saisissez une chaîne de cookie directement (par ex., <code>nom1=valeur1; nom2=valeur2</code>).</li>\n<li><b>Parcourir... :</b> Sélectionnez un fichier <code>cookies.txt</code> (format Netscape). Le chemin apparaîtra dans le champ de texte.</li>\n<li><b>Priorité :</b> Le champ de texte (s'il est rempli) a la priorité sur un fichier parcouru. Si 'Utiliser le cookie' est coché mais que les deux sont vides, il tente de charger <code>cookies.txt</code> depuis le répertoire de l'application.</li>\n</ul>\n</li>\n<li><b>Utiliser le multithreading & Entrée Threads :</b>\n<ul>\n<li>Active des opérations plus rapides. Le nombre dans l'entrée 'Threads' signifie :\n<ul>\n<li>Pour les <b>Flux de créateurs :</b> Nombre de publications à traiter simultanément. Les fichiers de chaque publication sont téléchargés séquentiellement par son worker (sauf si le nommage de manga 'Basé sur la date' est activé, ce qui force 1 worker de publication).</li>\n<li>Pour les <b>URL de publications uniques :</b> Nombre de fichiers à télécharger simultanément à partir de cette seule publication.</li>\n</ul>\n</li>\n<li>Si décoché, 1 thread est utilisé. Des nombres élevés de threads (par ex., >40) peuvent afficher un avertissement.</li>\n</ul>\n</li></ul></ul></body></html>",
    "help_guide_step5_title": "⑤ Paramètres avancés (Partie 2) & Actions",
    "help_guide_step5_content": "<html><head/><body><h3>⚙️ Paramètres avancés (Suite)</h3><ul><ul>\n<li><b>Afficher les liens externes dans le journal :</b> Si coché, un panneau de journal secondaire apparaît sous le journal principal pour afficher les liens externes trouvés dans les descriptions de publications. (Désactivé si le mode '🔗 Liens Uniquement' ou '📦 Archives Uniquement' est actif).</li>\n<li><b>📖 Mode Manga/BD (URL de créateur uniquement) :</b> Conçu pour le contenu séquentiel.\n<ul>\n<li>Télécharge les publications du <b>plus ancien au plus récent</b>.</li>\n<li>L'entrée 'Plage de pages' est désactivée car toutes les publications sont récupérées.</li>\n<li>Un <b>bouton de bascule de style de nom de fichier</b> (par ex., 'Nom : Titre de la publication') apparaît en haut à droite de la zone du journal lorsque ce mode est actif pour un flux de créateur. Cliquez dessus pour cycler entre les styles de nommage :\n<ul>\n<li><code>Nom : Titre de la publication (Défaut)</code> : Le premier fichier d'une publication est nommé d'après le titre nettoyé de la publication (par ex., 'Mon Chapitre 1.jpg'). Les fichiers suivants dans la *même publication* tenteront de conserver leurs noms de fichiers originaux (par ex., 'page_02.png', 'bonus_art.jpg'). Si la publication n'a qu'un seul fichier, il est nommé d'après le titre de la publication. C'est généralement recommandé pour la plupart des mangas/BD.</li>\n<li><code>Nom : Fichier original</code> : Tous les fichiers tentent de conserver leurs noms de fichiers originaux.</li>\n<li><code>Nom : Fichier original</code> : Tous les fichiers tentent de conserver leurs noms de fichiers originaux. Lorsque ce style est actif, un champ de saisie pour un <b>préfixe de nom de fichier optionnel</b> (par ex., 'MaSerie_') apparaîtra à côté de ce bouton de style. Exemple : 'MaSerie_FichierOriginal.jpg'.</li>\n<li><code>Nom : Titre+Num.G (Titre de la publication + Numérotation globale)</code> : Tous les fichiers de toutes les publications de la session de téléchargement actuelle sont nommés séquentiellement en utilisant le titre nettoyé de la publication comme préfixe, suivi d'un compteur global. Exemple : Publication 'Chapitre 1' (2 fichiers) -> 'Chapitre 1 001.jpg', 'Chapitre 1 002.png'. Publication suivante 'Chapitre 2' (1 fichier) -> 'Chapitre 2 003.jpg'. Le multithreading pour le traitement des publications est automatiquement désactivé pour ce style.</li>\n<li><code>Nom : Basé sur la date</code> : Les fichiers sont nommés séquentiellement (001.ext, 002.ext, ...) en fonction de l'ordre de publication. Lorsque ce style est actif, un champ de saisie pour un <b>préfixe de nom de fichier optionnel</b> (par ex., 'MaSerie_') apparaîtra à côté de ce bouton de style. Exemple : 'MaSerie_001.jpg'. Le multithreading pour le traitement des publications est automatiquement désactivé pour ce style.</li>\n</ul>\n</li>\n<li>Pour de meilleurs résultats avec les styles 'Nom : Titre de la publication', 'Nom : Titre+Num.G' ou 'Nom : Basé sur la date', utilisez le champ 'Filtrer par Personnage(s)' avec le titre du manga/de la série pour l'organisation des dossiers.</li>\n</ul>\n</li>\n</ul></li></ul>\n<h3>Actions principales (Panneau de gauche)</h3>\n<ul>\n<li><b>⬇️ Démarrer le téléchargement / 🔗 Extraire les liens :</b> Le texte et la fonction de ce bouton changent en fonction de la sélection du bouton radio 'Filtrer les fichiers'. Il démarre l'opération principale.</li>\n<li><b>⏸️ Mettre en pause le téléchargement / ▶️ Reprendre le téléchargement :</b> Permet d'arrêter temporairement le processus de téléchargement/extraction en cours et de le reprendre plus tard. Certains paramètres de l'UI peuvent être modifiés pendant la pause.</li>\n<li><b>❌ Annuler & Réinitialiser l'UI :</b> Arrête l'opération en cours et effectue une réinitialisation logicielle de l'UI. Vos entrées d'URL et de répertoire de téléchargement sont conservées, mais les autres paramètres et journaux sont effacés.</li>\n</ul></body></html>",
    "help_guide_step6_title": "⑥ Liste des séries/personnages connus",
    "help_guide_step6_content": "<html><head/><body>\n<h3>Gestion de la liste des séries/personnages connus (en bas à gauche)</h3>\n<p>Cette section aide à gérer le fichier <code>Known.txt</code>, qui est utilisé pour l'organisation intelligente des dossiers lorsque 'Dossiers séparés par Nom/Titre' est activé, en particulier comme solution de repli si une publication ne correspond pas à votre entrée active 'Filtrer par Personnage(s)'.</p>\n<ul>\n<li><b>Ouvrir Known.txt :</b> Ouvre le fichier <code>Known.txt</code> (situé dans le répertoire de l'application) dans votre éditeur de texte par défaut pour une édition avancée (comme la création d'alias groupés complexes).</li>\n<li><b>Rechercher des personnages... :</b> Filtre la liste des noms connus affichée ci-dessous.</li>\n<li><b>Widget de liste :</b> Affiche les noms principaux de votre <code>Known.txt</code>. Sélectionnez des entrées ici pour les supprimer.</li>\n<li><b>Ajouter un nouveau nom de série/personnage (Champ de saisie) :</b> Saisissez un nom ou un groupe à ajouter.\n<ul>\n<li><b>Nom simple :</b> par ex., <code>Ma Super Série</code>. Ajoute comme une seule entrée.</li>\n<li><b>Groupe pour des entrées Known.txt séparées :</b> par ex., <code>(Vivi, Ulti, Uta)</code>. Ajoute \"Vivi\", \"Ulti\" et \"Uta\" comme trois entrées individuelles séparées à <code>Known.txt</code>.</li>\n<li><b>Groupe pour dossier partagé & Entrée Known.txt unique (Tilde <code>~</code>) :</b> par ex., <code>(Personnage A, Perso A)~</code>. Ajoute une entrée à <code>Known.txt</code> nommée \"Personnage A Perso A\". \"Personnage A\" et \"Perso A\" deviennent des alias pour ce seul dossier/entrée.</li>\n</ul>\n</li>\n<li><b>Bouton ➕ Ajouter :</b> Ajoute le nom/groupe du champ de saisie ci-dessus à la liste et à <code>Known.txt</code>.</li>\n<li><b>Bouton ⤵️ Ajouter au filtre :</b>\n<ul>\n<li>Situé à côté du bouton '➕ Ajouter' pour la liste 'Séries/Personnages connus'.</li>\n<li>Cliquer sur ce bouton ouvre une fenêtre popup affichant tous les noms de votre fichier <code>Known.txt</code>, chacun avec une case à cocher.</li>\n<li>La popup inclut une barre de recherche pour filtrer rapidement la liste des noms.</li>\n<li>Vous pouvez sélectionner un ou plusieurs noms en utilisant les cases à cocher.</li>\n<li>Cliquez sur 'Ajouter la sélection' pour insérer les noms choisis dans le champ de saisie 'Filtrer par Personnage(s)' de la fenêtre principale.</li>\n<li>Si un nom sélectionné dans <code>Known.txt</code> était à l'origine un groupe (par ex., défini comme <code>(Boa, Hancock)</code> dans Known.txt), il sera ajouté au champ de filtre comme <code>(Boa, Hancock)~</code>. Les noms simples sont ajoutés tels quels.</li>\n<li>Les boutons 'Tout sélectionner' et 'Tout désélectionner' sont disponibles dans la popup pour plus de commodité.</li>\n<li>Cliquez sur 'Annuler' pour fermer la popup sans aucune modification.</li>\n</ul>\n</li>\n<li><b>Bouton 🗑️ Supprimer la sélection :</b> Supprime le(s) nom(s) sélectionné(s) de la liste et de <code>Known.txt</code>.</li>\n<li><b>Bouton ❓ (Celui-ci !) :</b> Affiche ce guide d'aide complet.</li>\n</ul></body></html>",
    "help_guide_step7_title": "⑦ Zone de journal & Contrôles",
    "help_guide_step7_content": "<html><head/><body>\n<h3>Zone de journal & Contrôles (Panneau de droite)</h3>\n<ul>\n<li><b>📜 Journal de progression / Journal des liens extraits (Étiquette) :</b> Titre de la zone de journal principale ; change si le mode '🔗 Liens Uniquement' est actif.</li>\n<li><b>Rechercher des liens... / Bouton 🔍 (Recherche de liens) :</b>\n<ul><li>Visible uniquement lorsque le mode '🔗 Liens Uniquement' est actif. Permet de filtrer en temps réel les liens extraits affichés dans le journal principal par texte, URL ou plateforme.</li></ul>\n</li>\n<li><b>Nom : Bouton [Style] (Style de nom de fichier Manga) :</b>\n<ul><li>Visible uniquement lorsque le <b>Mode Manga/BD</b> est actif pour un flux de créateur et non en mode 'Liens Uniquement' ou 'Archives Uniquement'.</li>\n<li>Cycle entre les styles de nom de fichier : <code>Titre de la publication</code>, <code>Fichier original</code>, <code>Basé sur la date</code>. (Voir la section Mode Manga/BD pour plus de détails).</li>\n<li>Lorsque le style 'Fichier original' ou 'Basé sur la date' est actif, un champ de saisie pour un <b>préfixe de nom de fichier optionnel</b> apparaîtra à côté de ce bouton.</li>\n</ul>\n</li>\n<li><b>Bouton Multi-partie : [ON/OFF] :</b>\n<ul><li>Bascule les téléchargements multi-segments pour les fichiers volumineux individuels.\n<ul><li><b>ON :</b> Peut accélérer les téléchargements de fichiers volumineux (par ex., des vidéos) mais peut augmenter les saccades de l'UI ou le spam du journal avec de nombreux petits fichiers. Un avertissement apparaît lors de l'activation. Si un téléchargement multi-partie échoue, il réessaie en flux unique.</li>\n<li><b>OFF (Défaut) :</b> Les fichiers sont téléchargés en un seul flux.</li>\n</ul>\n<li>Désactivé si le mode '🔗 Liens Uniquement' ou '📦 Archives Uniquement' est actif.</li>\n</ul>\n</li>\n<li><b>Bouton 👁️ / 🙈 (Bascule d'affichage du journal) :</b> Change la vue du journal principal :\n<ul>\n<li><b>👁️ Journal de progression (Défaut) :</b> Affiche toute l'activité de téléchargement, les erreurs et les résumés.</li>\n<li><b>🙈 Journal des personnages manqués :</b> Affiche une liste de termes clés des titres/contenus de publications qui ont été ignorés en raison de vos paramètres 'Filtrer par Personnage(s)'. Utile pour identifier le contenu que vous pourriez manquer involontairement.</li>\n</ul>\n</li>\n<li><b>Bouton 🔄 Réinitialiser :</b> Efface tous les champs de saisie, les journaux et réinitialise les paramètres temporaires à leurs valeurs par défaut. Ne peut être utilisé que lorsqu'aucun téléchargement n'est actif.</li>\n<li><b>Sortie du journal principal (Zone de texte) :</b> Affiche les messages de progression détaillés, les erreurs et les résumés. Si le mode '🔗 Liens Uniquement' est actif, cette zone affiche les liens extraits.</li>\n<li><b>Sortie du journal des personnages manqués (Zone de texte) :</b> (Visible via la bascule 👁️ / 🙈) Affiche les publications/fichiers ignorés en raison des filtres de personnages.</li>\n<li><b>Sortie du journal externe (Zone de texte) :</b> Apparaît sous le journal principal si 'Afficher les liens externes dans le journal' est coché. Affiche les liens externes trouvés dans les descriptions de publications.</li>\n<li><b>Bouton Exporter les liens :</b>\n<ul><li>Visible et activé uniquement lorsque le mode '🔗 Liens Uniquement' est actif et que des liens ont été extraits.</li>\n<li>Permet d'enregistrer tous les liens extraits dans un fichier <code>.txt</code>.</li>\n</ul>\n</li>\n<li><b>Étiquette de progression : [Statut] :</b> Affiche la progression globale du processus de téléchargement ou d'extraction de liens (par ex., publications traitées).</li>\n<li><b>Étiquette de progression des fichiers :</b> Affiche la progression des téléchargements de fichiers individuels, y compris la vitesse et la taille, ou l'état du téléchargement multi-partie.</li>\n</ul></body></html>",
    "help_guide_step8_title": "⑧ Mode Favori & Fonctionnalités futures",
    "help_guide_step8_content": "<html><head/><body>\n<h3>Mode Favori (Téléchargement depuis vos favoris Kemono.su)</h3>\n<p>Ce mode vous permet de télécharger du contenu directement depuis les artistes que vous avez mis en favoris sur Kemono.su.</p>\n<ul>\n<li><b>⭐ Comment l'activer :</b>\n<ul>\n<li>Cochez la case <b>'⭐ Mode Favori'</b>, située à côté du bouton radio '🔗 Liens Uniquement'.</li>\n</ul>\n</li>\n<li><b>Changements de l'UI en Mode Favori :</b>\n<ul>\n<li>La zone de saisie '🔗 URL Créateur/Post Kemono' est remplacée par un message indiquant que le Mode Favori est actif.</li>\n<li>Les boutons standard 'Démarrer le téléchargement', 'Pause', 'Annuler' sont remplacés par :\n<ul>\n<li>Bouton <b>'🖼️ Artistes favoris'</b></li>\n<li>Bouton <b>'📄 Publications favorites'</b></li>\n</ul>\n</li>\n<li>L'option '🍪 Utiliser le cookie' est automatiquement activée et verrouillée, car les cookies sont nécessaires pour récupérer vos favoris.</li>\n</ul>\n</li>\n<li><b>Bouton 🖼️ Artistes favoris :</b>\n<ul>\n<li>Cliquer ici ouvre une boîte de dialogue qui liste tous les artistes que vous avez mis en favoris sur Kemono.su.</li>\n<li>Vous pouvez sélectionner un ou plusieurs artistes de cette liste pour télécharger leur contenu.</li>\n</ul>\n</li>\n<li><b>Bouton 📄 Publications favorites (Fonctionnalité future) :</b>\n<ul>\n<li>Le téléchargement de <i>publications</i> spécifiques mises en favoris (en particulier dans un ordre séquentiel de type manga si elles font partie d'une série) est une fonctionnalité actuellement en développement.</li>\n<li>La meilleure façon de gérer les publications favorites, en particulier pour une lecture séquentielle comme les mangas, est encore à l'étude.</li>\n<li>Si vous avez des idées spécifiques ou des cas d'utilisation sur la façon dont vous aimeriez télécharger et organiser les publications favorites (par ex., \"style manga\" à partir des favoris), veuillez envisager d'ouvrir une issue ou de rejoindre la discussion sur la page GitHub du projet. Votre contribution est précieuse !</li>\n</ul>\n</li>\n<li><b>Portée de téléchargement des favoris (Bouton) :</b>\n<ul>\n<li>Ce bouton (à côté de 'Publications favorites') contrôle où le contenu des artistes favoris sélectionnés est téléchargé :\n<ul>\n<li><b><i>Portée : Emplacement sélectionné :</i></b> Tous les artistes sélectionnés sont téléchargés dans l' 'Emplacement de téléchargement' principal que vous avez défini dans l'UI. Les filtres s'appliquent globalement à tout le contenu.</li>\n<li><b><i>Portée : Dossiers d'artistes :</i></b> Pour chaque artiste sélectionné, un sous-dossier (nommé d'après l'artiste) est automatiquement créé à l'intérieur de votre 'Emplacement de téléchargement' principal. Le contenu de cet artiste va dans son dossier spécifique. Les filtres s'appliquent à l'intérieur du dossier dédié de chaque artiste.</li>\n</ul>\n</li>\n</ul>\n</li>\n<li><b>Filtres en Mode Favori :</b>\n<ul>\n<li>Les options '🎯 Filtrer par Personnage(s)', '🚫 Ignorer avec les mots' et 'Filtrer les fichiers' que vous avez définies dans l'UI s'appliqueront toujours au contenu téléchargé de vos artistes favoris sélectionnés.</li>\n</ul>\n</li>\n</ul></body></html>",
    "help_guide_step9_title": "⑨ Fichiers clés & Visite",
    "help_guide_step9_content": "<html><head/><body>\n<h3>Fichiers clés utilisés par l'application</h3>\n<ul>\n<li><b><code>Known.txt</code> :</b>\n<ul>\n<li>Situé dans le répertoire de l'application (où se trouve le <code>.exe</code> ou <code>main.py</code>).</li>\n<li>Stocke votre liste de séries, personnages ou titres de séries connus pour l'organisation automatique des dossiers lorsque 'Dossiers séparés par Nom/Titre' est activé.</li>\n<li><b>Format :</b>\n<ul>\n<li>Chaque ligne est une entrée.</li>\n<li><b>Nom simple :</b> par ex., <code>Ma Super Série</code>. Le contenu correspondant ira dans un dossier nommé \"Ma Super Série\".</li>\n<li><b>Alias groupés :</b> par ex., <code>(Personnage A, Perso A, Nom Alt A)</code>. Le contenu correspondant à \"Personnage A\", \"Perso A\", OU \"Nom Alt A\" ira TOUS dans un seul dossier nommé \"Personnage A Perso A Nom Alt A\" (après nettoyage). Tous les termes entre parenthèses deviennent des alias pour ce dossier.</li>\n</ul>\n</li>\n<li><b>Utilisation :</b> Sert de solution de repli pour le nommage des dossiers si une publication ne correspond pas à votre entrée active 'Filtrer par Personnage(s)'. Vous pouvez gérer les entrées simples via l'UI ou éditer le fichier directement pour les alias complexes. L'application le recharge au démarrage ou à la prochaine utilisation.</li>\n</ul>\n</li>\n<li><b><code>cookies.txt</code> (Optionnel) :</b>\n<ul>\n<li>Si vous utilisez la fonctionnalité 'Utiliser le cookie' et que vous ne fournissez pas de chaîne de cookie directe ou que vous ne parcourez pas un fichier spécifique, l'application cherchera un fichier nommé <code>cookies.txt</code> dans son répertoire.</li>\n<li><b>Format :</b> Doit être au format de fichier de cookie Netscape.</li>\n<li><b>Utilisation :</b> Permet au téléchargeur d'utiliser la session de connexion de votre navigateur pour accéder au contenu qui pourrait être derrière une connexion sur Kemono/Coomer.</li>\n</ul>\n</li>\n</ul>\n<h3>Visite pour le premier utilisateur</h3>\n<ul>\n<li>Au premier lancement (ou si réinitialisé), une boîte de dialogue de visite de bienvenue apparaît, vous guidant à travers les principales fonctionnalités. Vous pouvez la passer ou choisir de \"Ne plus jamais afficher cette visite.\"</li>\n</ul>\n<p><em>De nombreux éléments de l'UI ont également des info-bulles qui apparaissent lorsque vous survolez votre souris, fournissant des conseils rapides.</em></p>\n</body></html>"
}
 # Basic French placeholders
translations["en"].update({
    "help_guide_dialog_title": "Kemono Downloader - Feature Guide",
    "help_guide_github_tooltip": "Visit project's GitHub page (Opens in browser)",
    "help_guide_instagram_tooltip": "Visit our Instagram page (Opens in browser)",
    "help_guide_discord_tooltip": "Visit our Discord community (Opens in browser)",
    "help_guide_step1_title": "① Introduction & Main Inputs",
    "help_guide_step1_content": """<html><head/><body>
    <p>This guide provides an overview of the Kemono Downloader's features, fields, and buttons.</p>
    <h3>Main Input Area (Top Left)</h3>
    <ul>
        <li><b>🔗 Kemono Creator/Post URL:</b>
            <ul>
                <li>Enter the full web address of a creator's page (e.g., <i>https://kemono.su/patreon/user/12345</i>) or a specific post (e.g., <i>.../post/98765</i>).</li>
                <li>Supports Kemono (kemono.su, kemono.party) and Coomer (coomer.su, coomer.party) URLs.</li>
            </ul>
        </li>
        <li><b>Page Range (Start to End):</b>
            <ul>
                <li>For creator URLs: Specify a range of pages to fetch (e.g., pages 2 to 5). Leave blank for all pages.</li>
                <li>Disabled for single post URLs or when <b>Manga/Comic Mode</b> is active.</li>
            </ul>
        </li>
        <li><b>📁 Download Location:</b>
            <ul>
                <li>Click <b>'Browse...'</b> to choose a main folder on your computer where all downloaded files will be saved.</li>
                <li>This field is required unless you are using <b>'🔗 Only Links'</b> mode.</li>
            </ul>
        </li>
        <li><b>🎨 Creator Selection Button (Next to URL Input):</b>
            <ul>
                <li>Click the palette icon (🎨) to open the 'Creator Selection' dialog.</li>
                <li>This dialog loads creators from your <code>creators.json</code> file (which should be in the application's directory).</li>
                <li><b>Inside the Dialog:</b>
                    <ul>
                        <li><b>Search Bar:</b> Type to filter the list of creators by name or service.</li>
                        <li><b>Creator List:</b> Displays creators from your <code>creators.json</code>. Creators you have 'favorited' (in the JSON data) appear at the top.</li>
                        <li><b>Checkboxes:</b> Select one or more creators by checking the box next to their name.</li>
                        <li><b>'Scope' Button (e.g., 'Scope: Characters'):</b> This button toggles the download organization when initiating downloads from this popup:
                            <ul><li><i>Scope: Characters:</i> Downloads will be organized into character-named folders directly within your main 'Download Location'. Art from different creators for the same character will be grouped together.</li>
                                <li><i>Scope: Creators:</i> Downloads will first create a folder named after the creator within your main 'Download Location'. Character-named subfolders will then be created inside each creator's folder.</li></ul>
                        </li>
                        <li><b>'Add Selected' Button:</b> Clicking this will take the names of all checked creators and add them to the main '🔗 Kemono Creator/Post URL' input field, separated by commas. The dialog will then close.</li>
                    </ul>
                </li>
                <li>This feature provides a quick way to populate the URL field for multiple creators without manually typing or pasting each URL.</li>
            </ul>
        </li>
    </ul></body></html>""",
    "help_guide_step2_title": "② Filtering Downloads",
    "help_guide_step2_content": """<html><head/><body>
    <h3>Filtering Downloads (Left Panel)</h3>
    <ul>
        <li><b>🎯 Filter by Character(s):</b>
            <ul>
                <li>Enter names, comma-separated (e.g., <code>Tifa, Aerith</code>).</li>
                <li><b>Grouped Aliases for Shared Folder (Separate Known.txt Entries):</b> <code>(Vivi, Ulti, Uta)</code>.
                    <ul><li>Content matching "Vivi", "Ulti", OR "Uta" will go into a shared folder named "Vivi Ulti Uta" (after cleaning).</li>
                        <li>If these names are new, "Vivi", "Ulti", and "Uta" will be prompted to be added as <i>separate individual entries</i> to <code>Known.txt</code>.</li>
                    </ul>
                </li>
                <li><b>Grouped Aliases for Shared Folder (Single Known.txt Entry):</b> <code>(Yuffie, Sonon)~</code> (note the tilde <code>~</code>).
                    <ul><li>Content matching "Yuffie" OR "Sonon" will go into a shared folder named "Yuffie Sonon".</li>
                        <li>If new, "Yuffie Sonon" (with aliases Yuffie, Sonon) will be prompted to be added as a <i>single group entry</i> to <code>Known.txt</code>.</li>
                    </ul>
                </li>
                <li>This filter influences folder naming if 'Separate Folders by Name/Title' is enabled.</li>
            </ul>
        </li>
        <li><b>Filter: [Type] Button (Character Filter Scope):</b> Cycles how the 'Filter by Character(s)' applies:
            <ul>
                <li><code>Filter: Files</code>: Checks individual filenames. A post is kept if any file matches; only matching files are downloaded. Folder naming uses the character from the matching filename.</li>
                <li><code>Filter: Title</code>: Checks post titles. All files from a matching post are downloaded. Folder naming uses the character from the matching post title.</li>
                <li><code>Filter: Both</code>: Checks post title first. If it matches, all files are downloaded. If not, it then checks filenames, and only matching files are downloaded. Folder naming prioritizes title match, then file match.</li>
                <li><code>Filter: Comments (Beta)</code>: Checks filenames first. If a file matches, all files from the post are downloaded. If no file match, it then checks post comments. If a comment matches, all files are downloaded. (Uses more API requests). Folder naming prioritizes file match, then comment match.</li>
            </ul>
        </li>
        <li><b>🗄️ Custom Folder Name (Single Post Only):</b>
            <ul>
                <li>Visible and usable only when downloading a single specific post URL AND 'Separate Folders by Name/Title' is enabled.</li>
                <li>Allows you to specify a custom name for that single post's download folder.</li>
            </ul>
        </li>
        <li><b>🚫 Skip with Words:</b>
            <ul><li>Enter words, comma-separated (e.g., <code>WIP, sketch, preview</code>) to skip certain content.</li></ul>
        </li>
        <li><b>Scope: [Type] Button (Skip Words Scope):</b> Cycles how 'Skip with Words' applies:
            <ul>
                <li><code>Scope: Files</code>: Skips individual files if their names contain any of these words.</li>
                <li><code>Scope: Posts</code>: Skips entire posts if their titles contain any of these words.</li>
                <li><code>Scope: Both</code>: Applies both (post title first, then individual files).</li>
            </ul>
        </li>
        <li><b>✂️ Remove Words from name:</b>
            <ul><li>Enter words, comma-separated (e.g., <code>patreon, [HD]</code>), to remove from downloaded filenames (case-insensitive).</li></ul>
        </li>
        <li><b>Filter Files (Radio Buttons):</b> Choose what to download:
            <ul>
                <li><code>All</code>: Downloads all file types found.</li>
                <li><code>Images/GIFs</code>: Only common image formats (JPG, PNG, GIF, WEBP, etc.) and GIFs.</li>
                <li><code>Videos</code>: Only common video formats (MP4, MKV, WEBM, MOV, etc.).</li>
                <li><code>📦 Only Archives</code>: Exclusively downloads <b>.zip</b> and <b>.rar</b> files. When selected, 'Skip .zip' and 'Skip .rar' checkboxes are automatically disabled and unchecked. 'Show External Links' is also disabled.</li>
                <li><code>🎧 Only Audio</code>: Downloads only common audio formats (MP3, WAV, FLAC, M4A, OGG, etc.). Other file-specific options behave as with 'Images' or 'Videos' mode.</li>
                <li><code>🔗 Only Links</code>: Extracts and displays external links from post descriptions instead of downloading files. Download-related options and 'Show External Links' are disabled. The main download button changes to '🔗 Extract Links'.</li>                    
            </ul>
        </li>
    </ul></body></html>""",
    "help_guide_step3_title": "③ Download Options & Settings",
    "help_guide_step3_content": """<html><head/><body>
    <h3>Download Options & Settings (Left Panel)</h3>
    <ul>
        <li><b>Skip .zip / Skip .rar:</b> Checkboxes to avoid downloading these archive file types. (Disabled and ignored if '📦 Only Archives' filter mode is selected).</li>
        <li><b>Download Thumbnails Only:</b> Downloads small preview images instead of full-sized files (if available).</li>
        <li><b>Compress Large Images (to WebP):</b> If the 'Pillow' (PIL) library is installed, images larger than 1.5MB will be converted to WebP format if the WebP version is significantly smaller.</li>
        <li><b>⚙️ Advanced Settings:</b>
            <ul>
                <li><b>Separate Folders by Name/Title:</b> Creates subfolders based on the 'Filter by Character(s)' input or post titles. Can use the <b>Known.txt</b> list as a fallback for folder names.</li></ul></li></ul></body></html>""",
    "help_guide_step4_title": "④ Advanced Settings (Part 1)",
    "help_guide_step4_content": """<html><head/><body><h3>⚙️ Advanced Settings (Continued)</h3><ul><ul>
                <li><b>Subfolder per Post:</b> If 'Separate Folders' is on, this creates an additional subfolder for <i>each individual post</i> inside the main character/title folder.</li>
                <li><b>Use Cookie:</b> Check this to use cookies for requests.
                    <ul>
                        <li><b>Text Field:</b> Enter a cookie string directly (e.g., <code>name1=value1; name2=value2</code>).</li>
                        <li><b>Browse...:</b> Select a <code>cookies.txt</code> file (Netscape format). The path will appear in the text field.</li>
                        <li><b>Precedence:</b> The text field (if filled) takes precedence over a browsed file. If 'Use Cookie' is checked but both are empty, it attempts to load <code>cookies.txt</code> from the app's directory.</li>
                    </ul>
                </li>
                <li><b>Use Multithreading & Threads Input:</b>
                    <ul>
                        <li>Enables faster operations. The number in 'Threads' input means:
                            <ul>
                                <li>For <b>Creator Feeds:</b> Number of posts to process simultaneously. Files within each post are downloaded sequentially by its worker (unless 'Date Based' manga naming is on, which forces 1 post worker).</li>
                                <li>For <b>Single Post URLs:</b> Number of files to download concurrently from that single post.</li>
                            </ul>
                        </li>
                        <li>If unchecked, 1 thread is used. High thread counts (e.g., >40) may show an advisory.</li>
                    </ul>
                </li></ul></ul></body></html>""",
    "help_guide_step5_title": "⑤ Advanced Settings (Part 2) & Actions",
    "help_guide_step5_content": """<html><head/><body><h3>⚙️ Advanced Settings (Continued)</h3><ul><ul>
                <li><b>Show External Links in Log:</b> If checked, a secondary log panel appears below the main log to display any external links found in post descriptions. (Disabled if '🔗 Only Links' or '📦 Only Archives' mode is active).</li>
                <li><b>📖 Manga/Comic Mode (Creator URLs only):</b> Tailored for sequential content.
                    <ul>
                        <li>Downloads posts from <b>oldest to newest</b>.</li>
                        <li>The 'Page Range' input is disabled as all posts are fetched.</li>
                        <li>A <b>filename style toggle button</b> (e.g., 'Name: Post Title') appears in the top-right of the log area when this mode is active for a creator feed. Click it to cycle through naming styles:
                            <ul>
                                <li><code>Name: Post Title (Default)</code>: The first file in a post is named after the post's cleaned title (e.g., 'My Chapter 1.jpg'). Subsequent files within the *same post* will attempt to keep their original filenames (e.g., 'page_02.png', 'bonus_art.jpg'). If the post has only one file, it's named after the post title. This is generally recommended for most manga/comics.</li>
                                <li><code>Name: Original File</code>: All files attempt to keep their original filenames.</li>
                                <li><code>Name: Original File</code>: All files attempt to keep their original filenames. When this style is active, an input field for an <b>optional filename prefix</b> (e.g., 'MySeries_') will appear next to this style button. Example: 'MySeries_OriginalFile.jpg'.</li>
                                <li><code>Name: Title+G.Num (Post Title + Global Numbering)</code>: All files across all posts in the current download session are named sequentially using the post's cleaned title as a prefix, followed by a global counter. Example: Post 'Chapter 1' (2 files) -> 'Chapter 1 001.jpg', 'Chapter 1 002.png'. Next post 'Chapter 2' (1 file) -> 'Chapter 2 003.jpg'. Multithreading for post processing is automatically disabled for this style.</li>
                                <li><code>Name: Date Based</code>: Files are named sequentially (001.ext, 002.ext, ...) based on post publication order. When this style is active, an input field for an <b>optional filename prefix</b> (e.g., 'MySeries_') will appear next to this style button. Example: 'MySeries_001.jpg'. Multithreading for post processing is automatically disabled for this style.</li>
                            </ul>
                        </li>
                        <li>For best results with 'Name: Post Title', 'Name: Title+G.Num', or 'Name: Date Based' styles, use the 'Filter by Character(s)' field with the manga/series title for folder organization.</li>
                    </ul>
                </li>
            </ul></li></ul>
    
    <h3>Main Action Buttons (Left Panel)</h3>
    <ul>
        <li><b>⬇️ Start Download / 🔗 Extract Links:</b> This button's text and function change based on the 'Filter Files' radio button selection. It starts the primary operation.</li>
        <li><b>⏸️ Pause Download / ▶️ Resume Download:</b> Allows you to temporarily halt the current download/extraction process and resume it later. Some UI settings can be changed while paused.</li>
        <li><b>❌ Cancel & Reset UI:</b> Stops the current operation and performs a soft UI reset. Your URL and Download Directory inputs are preserved, but other settings and logs are cleared.</li>
    </ul></body></html>""",
    "help_guide_step6_title": "⑥ Known Shows/Characters List",
    "help_guide_step6_content": """<html><head/><body>
    <h3>Known Shows/Characters List Management (Bottom Left)</h3>
    <p>This section helps manage the <code>Known.txt</code> file, which is used for smart folder organization when 'Separate Folders by Name/Title' is enabled, especially as a fallback if a post doesn't match your active 'Filter by Character(s)' input.</p>
    <ul>
        <li><b>Open Known.txt:</b> Opens the <code>Known.txt</code> file (located in the app's directory) in your default text editor for advanced editing (like creating complex grouped aliases).</li>
        <li><b>Search characters...:</b> Filters the list of known names displayed below.</li>
        <li><b>List Widget:</b> Displays the primary names from your <code>Known.txt</code>. Select entries here to delete them.</li>
        <li><b>Add new show/character name (Input Field):</b> Enter a name or group to add.
            <ul>
                <li><b>Simple Name:</b> e.g., <code>My Awesome Series</code>. Adds as a single entry.</li>
                <li><b>Group for Separate Known.txt Entries:</b> e.g., <code>(Vivi, Ulti, Uta)</code>. Adds "Vivi", "Ulti", and "Uta" as three separate individual entries to <code>Known.txt</code>.</li>
                <li><b>Group for Shared Folder & Single Known.txt Entry (Tilde <code>~</code>):</b> e.g., <code>(Character A, Char A)~</code>. Adds one entry to <code>Known.txt</code> named "Character A Char A". "Character A" and "Char A" become aliases for this single folder/entry.</li>
            </ul>
        </li>
        <li><b>➕ Add Button:</b> Adds the name/group from the input field above to the list and <code>Known.txt</code>.</li>
        <li><b>⤵️ Add to Filter Button:</b>
            <ul>
                <li>Located next to the '➕ Add' button for the 'Known Shows/Characters' list.</li>
                <li>Clicking this button opens a popup window displaying all names from your <code>Known.txt</code> file, each with a checkbox.</li>
                <li>The popup includes a search bar to quickly filter the list of names.</li>
                <li>You can select one or more names using the checkboxes.</li>
                <li>Click 'Add Selected' to insert the chosen names into the 'Filter by Character(s)' input field in the main window.</li>
                <li>If a selected name from <code>Known.txt</code> was originally a group (e.g., defined as <code>(Boa, Hancock)</code> in Known.txt), it will be added to the filter field as <code>(Boa, Hancock)~</code>. Simple names are added as-is.</li>
                <li>'Select All' and 'Deselect All' buttons are available in the popup for convenience.</li>
                <li>Click 'Cancel' to close the popup without any changes.</li>
            </ul>
        </li>
        <li><b>🗑️ Delete Selected Button:</b> Deletes the selected name(s) from the list and <code>Known.txt</code>.</li>
        <li><b>❓ Button (This one!):</b> Displays this comprehensive help guide.</li>
    </ul></body></html>""",
    "help_guide_step7_title": "⑦ Log Area & Controls",
    "help_guide_step7_content": """<html><head/><body>
    <h3>Log Area & Controls (Right Panel)</h3>
    <ul>
        <li><b>📜 Progress Log / Extracted Links Log (Label):</b> Title for the main log area; changes if '🔗 Only Links' mode is active.</li>
        <li><b>Search Links... / 🔍 Button (Link Search):</b>
            <ul><li>Visible only when '🔗 Only Links' mode is active. Allows real-time filtering of the extracted links displayed in the main log by text, URL, or platform.</li></ul>
        </li>
        <li><b>Name: [Style] Button (Manga Filename Style):</b>
            <ul><li>Visible only when <b>Manga/Comic Mode</b> is active for a creator feed and not in 'Only Links' or 'Only Archives' mode.</li>
                <li>Cycles through filename styles: <code>Post Title</code>, <code>Original File</code>, <code>Date Based</code>. (See Manga/Comic Mode section for details).</li>
                <li>When 'Original File' or 'Date Based' style is active, an input field for an <b>optional filename prefix</b> will appear next to this button.</li>
            </ul>                
        </li>
        <li><b>Multi-part: [ON/OFF] Button:</b>
            <ul><li>Toggles multi-segment downloads for individual large files.
                <ul><li><b>ON:</b> Can speed up large file downloads (e.g., videos) but may increase UI choppiness or log spam with many small files. An advisory appears when enabling. If a multi-part download fails, it retries as single-stream.</li>
                    <li><b>OFF (Default):</b> Files are downloaded in a single stream.</li>
                </ul>
                <li>Disabled if '🔗 Only Links' or '📦 Only Archives' mode is active.</li>
            </ul>
        </li>
        <li><b>👁️ / 🙈 Button (Log View Toggle):</b> Switches the main log view:
            <ul>
                <li><b>👁️ Progress Log (Default):</b> Shows all download activity, errors, and summaries.</li>
                <li><b>🙈 Missed Character Log:</b> Displays a list of key terms from post titles/content that were skipped due to your 'Filter by Character(s)' settings. Useful for identifying content you might be unintentionally missing.</li>
            </ul>
        </li>
        <li><b>🔄 Reset Button:</b> Clears all input fields, logs, and resets temporary settings to their defaults. Can only be used when no download is active.</li>
        <li><b>Main Log Output (Text Area):</b> Displays detailed progress messages, errors, and summaries. If '🔗 Only Links' mode is active, this area displays the extracted links.</li>
        <li><b>Missed Character Log Output (Text Area):</b> (Viewable via 👁️ / 🙈 toggle) Displays posts/files skipped due to character filters.</li>
        <li><b>External Log Output (Text Area):</b> Appears below the main log if 'Show External Links in Log' is checked. Displays external links found in post descriptions.</li>
        <li><b>Export Links Button:</b>
            <ul><li>Visible and enabled only when '🔗 Only Links' mode is active and links have been extracted.</li>
                <li>Allows you to save all extracted links to a <code>.txt</code> file.</li>
            </ul>
        </li>
        <li><b>Progress: [Status] Label:</b> Shows the overall progress of the download or link extraction process (e.g., posts processed).</li>
        <li><b>File Progress Label:</b> Shows the progress of individual file downloads, including speed and size, or multi-part download status.</li>
    </ul></body></html>""",
    "help_guide_step8_title": "⑧ Favorite Mode & Future Features",
    "help_guide_step8_content": """<html><head/><body>
    <h3>Favorite Mode (Downloading from Your Kemono.su Favorites)</h3>
    <p>This mode allows you to download content directly from artists you've favorited on Kemono.su.</p>
    <ul>
        <li><b>⭐ How to Enable:</b>
            <ul>
                <li>Check the <b>'⭐ Favorite Mode'</b> checkbox, located next to the '🔗 Only Links' radio button.</li>
            </ul>
        </li>
        <li><b>UI Changes in Favorite Mode:</b>
            <ul>
                <li>The '🔗 Kemono Creator/Post URL' input area is replaced with a message indicating Favorite Mode is active.</li>
                <li>The standard 'Start Download', 'Pause', 'Cancel' buttons are replaced with:
                    <ul>
                        <li><b>'🖼️ Favorite Artists'</b> button</li>
                        <li><b>'📄 Favorite Posts'</b> button</li>
                    </ul>
                </li>
                <li>The '🍪 Use Cookie' option is automatically enabled and locked, as cookies are required to fetch your favorites.</li>
            </ul>
        </li>
        <li><b>🖼️ Favorite Artists Button:</b>
            <ul>
                <li>Clicking this opens a dialog that lists all artists you have favorited on Kemono.su.</li>
                <li>You can select one or more artists from this list to download their content.</li>
            </ul>
        </li>
        <li><b>📄 Favorite Posts Button (Future Feature):</b>
            <ul>
                <li>Downloading specific favorited <i>posts</i> (especially in a manga-like sequential order if they are part of a series) is a feature currently under development.</li>
                <li>The best way to handle favorited posts, particularly for sequential reading like manga, is still being explored.</li>
                <li>If you have specific ideas or use cases for how you'd like to download and organize favorited posts (e.g., "manga-style" from favorites), please consider opening an issue or joining the discussion on the project's GitHub page. Your input is valuable!</li>
            </ul>
        </li>
        <li><b>Favorite Download Scope (Button):</b>
            <ul>
                <li>This button (next to 'Favorite Posts') controls where content from selected favorite artists is downloaded:
                    <ul>
                        <li><b><i>Scope: Selected Location:</i></b> All selected artists are downloaded into the main 'Download Location' you've set in the UI. Filters apply globally to all content.</li>
                        <li><b><i>Scope: Artist Folders:</i></b> For each selected artist, a subfolder (named after the artist) is automatically created inside your main 'Download Location'. Content for that artist goes into their specific subfolder. Filters apply within each artist's dedicated folder.</li>
                    </ul>
                </li>
            </ul>
        </li>
        <li><b>Filters in Favorite Mode:</b>
            <ul>
                <li>The '🎯 Filter by Character(s)', '🚫 Skip with Words', and 'Filter Files' options you've set in the UI will still apply to the content downloaded from your selected favorite artists.</li>
            </ul>
        </li>
    </ul></body></html>""",
    "help_guide_step9_title": "⑨ Key Files & Tour",
    "help_guide_step9_content": """<html><head/><body>
    <h3>Key Files Used by the Application</h3>
    <ul>
        <li><b><code>Known.txt</code>:</b>
            <ul>
                <li>Located in the application's directory (where the <code>.exe</code> or <code>main.py</code> is).</li>
                <li>Stores your list of known shows, characters, or series titles for automatic folder organization when 'Separate Folders by Name/Title' is enabled.</li>
                <li><b>Format:</b>
                    <ul>
                        <li>Each line is an entry.</li>
                        <li><b>Simple Name:</b> e.g., <code>My Awesome Series</code>. Content matching this will go into a folder named "My Awesome Series".</li>
                        <li><b>Grouped Aliases:</b> e.g., <code>(Character A, Char A, Alt Name A)</code>. Content matching "Character A", "Char A", OR "Alt Name A" will ALL go into a single folder named "Character A Char A Alt Name A" (after cleaning). All terms in the parentheses become aliases for that folder.</li>
                    </ul>
                </li>
                <li><b>Usage:</b> Serves as a fallback for folder naming if a post doesn't match your active 'Filter by Character(s)' input. You can manage simple entries via the UI or edit the file directly for complex aliases. The app reloads it on startup or next use.</li>
            </ul>
        </li>
        <li><b><code>cookies.txt</code> (Optional):</b>
            <ul>
                <li>If you use the 'Use Cookie' feature and don't provide a direct cookie string or browse to a specific file, the application will look for a file named <code>cookies.txt</code> in its directory.</li>
                <li><b>Format:</b> Must be in Netscape cookie file format.</li>
                <li><b>Usage:</b> Allows the downloader to use your browser's login session for accessing content that might be behind a login on Kemono/Coomer.</li>
            </ul>
        </li>
    </ul>

    <h3>First-Time User Tour</h3>
    <ul>
        <li>On the first launch (or if reset), a welcome tour dialog appears, guiding you through the main features. You can skip it or choose to "Never show this tour again."</li>
    </ul>
    <p><em>Many UI elements also have tooltips that appear when you hover your mouse over them, providing quick hints.</em></p>
    </body></html>"""
})

translations["ja"].update({
    "help_guide_dialog_title": "Kemonoダウンローダー - 機能ガイド",
    "help_guide_github_tooltip": "プロジェクトのGitHubページにアクセス (ブラウザで開きます)",
    "help_guide_instagram_tooltip": "Instagramページにアクセス (ブラウザで開きます)",
    "help_guide_discord_tooltip": "Discordコミュニティにアクセス (ブラウザで開きます)",
    "help_guide_step1_title": "① 概要と主な入力",
    "help_guide_step1_content": """<html><head/><body>
    <p>このガイドでは、Kemonoダウンローダーの機能、フィールド、ボタンの概要を説明します。</p>
    <h3>メイン入力エリア (左上)</h3>
    <ul>
        <li><b>🔗 Kemonoクリエイター/投稿URL:</b>
            <ul>
                <li>クリエイターのページ（例: <i>https://kemono.su/patreon/user/12345</i>）または特定の投稿（例: <i>.../post/98765</i>）の完全なウェブアドレスを入力します。</li>
                <li>Kemono (kemono.su, kemono.party) および Coomer (coomer.su, coomer.party) のURLをサポートしています。</li>
            </ul>
        </li>
        <li><b>ページ範囲 (開始から終了):</b>
            <ul>
                <li>クリエイターURLの場合: 取得するページの範囲を指定します（例: 2ページから5ページ）。すべてのページを取得する場合は空白のままにします。</li>
                <li>単一の投稿URLまたは<b>マンガ/コミックモード</b>がアクティブな場合は無効になります。</li>
            </ul>
        </li>
        <li><b>📁 ダウンロード場所:</b>
            <ul>
                <li><b>「参照...」</b>をクリックして、ダウンロードしたすべてのファイルが保存されるコンピュータ上のメインフォルダを選択します。</li>
                <li><b>「🔗 リンクのみ」</b>モードを使用している場合を除き、このフィールドは必須です。</li>
            </ul>
        </li>
        <li><b>🎨 クリエイター選択ボタン (URL入力の隣):</b>
            <ul>
                <li>パレットアイコン (🎨) をクリックすると、「クリエイター選択」ダイアログが開きます。</li>
                <li>このダイアログは、<code>creators.json</code>ファイル（アプリケーションのディレクトリにある必要があります）からクリエイターを読み込みます。</li>
                <li><b>ダイアログ内:</b>
                    <ul>
                        <li><b>検索バー:</b> 名前またはサービスでクリエイターのリストをフィルタリングします。</li>
                        <li><b>クリエイターリスト:</b> <code>creators.json</code>ファイルからクリエイターを表示します。JSONデータでお気に入りに登録したクリエイターはリストの上部に表示されます。</li>
                        <li><b>チェックボックス:</b> 名前の隣にあるチェックボックスをオンにして、1人以上のクリエイターを選択します。</li>
                        <li><b>「スコープ」ボタン (例: 「スコープ: キャラクター」):</b> このポップアップからダウンロードを開始する際のダウンロード整理方法を切り替えます:
                            <ul><li><i>スコープ: キャラクター:</i> ダウンロードは、メインの「ダウンロード場所」内に直接キャラクター名のフォルダに整理されます。同じキャラクターの異なるクリエイターのアートは一緒にグループ化されます。</li>
                                <li><i>スコープ: クリエイター:</i> ダウンロードは、まずメインの「ダウンロード場所」内にクリエイター名のフォルダを作成します。その後、各クリエイターのフォルダ内にキャラクター名のサブフォルダが作成されます。</li></ul>
                        </li>
                        <li><b>「選択項目を追加」ボタン:</b> これをクリックすると、チェックされたすべてのクリエイターの名前がメインの「🔗 Kemonoクリエイター/投稿URL」入力フィールドにコンマ区切りで追加され、ダイアログが閉じます。</li>
                    </ul>
                </li>
                <li>この機能は、各URLを手動で入力または貼り付けずに、複数のクリエイターのURLフィールドをすばやく入力する方法を提供します。</li>
            </ul>
        </li>
    </ul></body></html>""", # JA_PLACEHOLDER - 上記の日本語HTMLコンテンツをここに入力してください
    "help_guide_step2_title": "② ダウンロードのフィルタリング",
    "help_guide_step2_content": """<html><head/><body>
    <h3>ダウンロードのフィルタリング（左パネル）</h3>
    <ul>
        <li><b>🎯 キャラクターでフィルタリング:</b>
            <ul>
                <li>名前をコンマ区切りで入力します（例: <code>ティファ, エアリス</code>）。</li>
                <li><b>共有フォルダ用のグループ化されたエイリアス (個別のKnown.txtエントリ):</b> <code>(ビビ, ウルティ, ウタ)</code>。
                    <ul><li>「ビビ」、「ウルティ」、または「ウタ」に一致するコンテンツは、「ビビ ウルティ ウタ」（クリーニング後）という名前の共有フォルダに入ります。</li>
                        <li>これらの名前が新しい場合、「ビビ」、「ウルティ」、「ウタ」は<code>Known.txt</code>に<i>個別のエントリ</i>として追加するよう促されます。</li>
                    </ul>
                </li>
                <li><b>共有フォルダ用のグループ化されたエイリアス (単一のKnown.txtエントリ):</b> <code>(ユフィ, ソノン)~</code> (チルダ<code>~</code>に注意)。
                    <ul><li>「ユフィ」または「ソノン」に一致するコンテンツは、「ユフィ ソノン」という名前の共有フォルダに入ります。</li>
                        <li>新しい場合、「ユフィ ソノン」(エイリアス: ユフィ, ソノン) は<code>Known.txt</code>に<i>単一のグループエントリ</i>として追加するよう促されます。</li>
                    </ul>
                </li>
                <li>「名前/タイトルでフォルダを分ける」が有効な場合、このフィルターはフォルダ名にも影響します。</li>
            </ul>
        </li>
        <li><b>フィルター: [タイプ] ボタン (キャラクターフィルタースコープ):</b> 「キャラクターでフィルタリング」の適用方法を循環します:
            <ul>
                <li><code>フィルター: ファイル</code>: 個々のファイル名を確認します。いずれかのファイルが一致すれば投稿は保持され、一致するファイルのみがダウンロードされます。フォルダ名は一致するファイル名のキャラクターを使用します。</li>
                <li><code>フィルター: タイトル</code>: 投稿タイトルを確認します。一致する投稿のすべてのファイルがダウンロードされます。フォルダ名は一致する投稿タイトルのキャラクターを使用します。</li>
                <li><code>フィルター: 両方</code>: まず投稿タイトルを確認します。一致する場合、すべてのファイルがダウンロードされます。一致しない場合、次にファイル名を確認し、一致するファイルのみがダウンロードされます。フォルダ名はタイトル一致を優先し、次にファイル一致を優先します。</li>
                <li><code>フィルター: コメント (ベータ)</code>: まずファイル名を確認します。ファイルが一致する場合、投稿のすべてのファイルがダウンロードされます。ファイル一致がない場合、次に投稿コメントを確認します。コメントが一致する場合、投稿のすべてのファイルがダウンロードされます。(より多くのAPIリクエストを使用します)。フォルダ名はファイル一致を優先し、次にコメント一致を優先します。</li>
            </ul>
        </li>
        <li><b>🗄️ カスタムフォルダ名 (単一投稿のみ):</b>
            <ul>
                <li>単一の特定の投稿URLをダウンロードしていて、かつ「名前/タイトルでフォルダを分ける」が有効な場合にのみ表示され、使用可能です。</li>
                <li>その単一投稿のダウンロードフォルダにカスタム名を指定できます。</li>
            </ul>
        </li>
        <li><b>🚫 スキップする単語:</b>
            <ul><li>特定のコンテンツをスキップするために、単語をコンマ区切りで入力します（例: <code>WIP, スケッチ, プレビュー</code>）。</li></ul>
        </li>
        <li><b>スコープ: [タイプ] ボタン (スキップワードスコープ):</b> 「スキップする単語」の適用方法を循環します:
            <ul>
                <li><code>スコープ: ファイル</code>: 名前にこれらの単語のいずれかを含む場合、個々のファイルをスキップします。</li>
                <li><code>スコープ: 投稿</code>: タイトルにこれらの単語のいずれかを含む場合、投稿全体をスキップします。</li>
                <li><code>スコープ: 両方</code>: 両方を適用します（まず投稿タイトル、次に個々のファイル）。</li>
            </ul>
        </li>
        <li><b>✂️ 名前から単語を削除:</b>
            <ul><li>ダウンロードしたファイル名から削除する単語をコンマ区切りで入力します（大文字と小文字を区別しません）（例: <code>patreon, [HD]</code>）。</li></ul>
        </li>
        <li><b>ファイルフィルター (ラジオボタン):</b> ダウンロードするものを選択します:
            <ul>
                <li><code>すべて</code>: 見つかったすべてのファイルタイプをダウンロードします。</li>
                <li><code>画像/GIF</code>: 一般的な画像形式（JPG, PNG, GIF, WEBPなど）とGIFのみ。</li>
                <li><code>動画</code>: 一般的な動画形式（MP4, MKV, WEBM, MOVなど）のみ。</li>
                <li><code>📦 アーカイブのみ</code>: <b>.zip</b>と<b>.rar</b>ファイルのみをダウンロードします。選択すると、「.zipをスキップ」と「.rarをスキップ」チェックボックスは自動的に無効になり、チェックが外れます。「外部リンクをログに表示」も無効になります。</li>
                <li><code>🎧 音声のみ</code>: 一般的な音声形式（MP3, WAV, FLAC, M4A, OGGなど）のみダウンロードします。他のファイル固有のオプションは、「画像」または「動画」モードと同様に動作します。</li>
                <li><code>🔗 リンクのみ</code>: ファイルをダウンロードする代わりに、投稿の説明から外部リンクを抽出して表示します。ダウンロード関連のオプションと「外部リンクをログに表示」は無効になります。メインのダウンロードボタンは「🔗 リンクを抽出」に変わります。</li>                    
            </ul>
        </li>
    </ul></body></html>""", # JA_PLACEHOLDER - 上記の日本語HTMLコンテンツをここに入力してください
    "help_guide_step3_title": "③ ダウンロードオプションと設定",
    "help_guide_step3_content": """<html><head/><body>
    <h3>ダウンロードオプションと設定（左パネル）</h3>
    <ul>
        <li><b>.zipをスキップ / .rarをスキップ:</b> これらのアーカイブファイルタイプをダウンロードしないようにするためのチェックボックス。(「📦 アーカイブのみ」フィルターモードが選択されている場合は無効になり、無視されます)。</li>
        <li><b>サムネイルのみダウンロード:</b> フルサイズのファイルの代わりに小さなプレビュー画像をダウンロードします（利用可能な場合）。</li>
        <li><b>大きな画像を圧縮 (WebPへ):</b> 「Pillow」(PIL) ライブラリがインストールされている場合、1.5MBより大きい画像は、WebPバージョンが大幅に小さい場合にWebP形式に変換されます。</li>
        <li><b>⚙️ 詳細設定:</b>
            <ul>
                <li><b>名前/タイトルでフォルダを分ける:</b> 「キャラクターでフィルタリング」入力または投稿タイトルに基づいてサブフォルダを作成します。<b>Known.txt</b>リストをフォルダ名のフォールバックとして使用できます。</li></ul></li></ul></body></html>""", # JA_PLACEHOLDER
    "help_guide_step4_title": "④ 詳細設定（その1）",
    "help_guide_step4_content": """<html><head/><body><h3>⚙️ 詳細設定（続き）</h3><ul><ul>
                <li><b>投稿ごとにサブフォルダ:</b> 「フォルダを分ける」がオンの場合、メインのキャラクター/タイトルフォルダ内に<i>個々の投稿</i>ごとに追加のサブフォルダを作成します。</li>
                <li><b>Cookieを使用:</b> リクエストにCookieを使用するには、これをチェックします。
                    <ul>
                        <li><b>テキストフィールド:</b> Cookie文字列を直接入力します（例: <code>name1=value1; name2=value2</code>）。</li>
                        <li><b>参照...:</b> <code>cookies.txt</code>ファイル（Netscape形式）を選択します。パスがテキストフィールドに表示されます。</li>
                        <li><b>優先順位:</b> テキストフィールド (入力されている場合) が参照されたファイルよりも優先されます。「Cookieを使用」がチェックされていて両方が空の場合、アプリのディレクトリから<code>cookies.txt</code>を読み込もうとします。</li>
                    </ul>
                </li>
                <li><b>マルチスレッドを使用 & スレッド数入力:</b>
                    <ul>
                        <li>より高速な操作を可能にします。「スレッド数」入力の数値の意味:
                            <ul>
                                <li><b>クリエイターフィードの場合:</b> 同時に処理する投稿の数。各投稿内のファイルは、そのワーカーによって順番にダウンロードされます（「日付順」マンガ命名がオンの場合を除く。これは1つの投稿ワーカーを強制します）。</li>
                                <li><b>単一投稿URLの場合:</b> その単一投稿から同時にダウンロードするファイルの数。</li>
                            </ul>
                        </li>
                        <li>チェックされていない場合、1スレッドが使用されます。高いスレッド数（例: >40）はアドバイザリを表示する場合があります。</li>
                    </ul>
                </li></ul></ul></body></html>""", # JA_PLACEHOLDER
    "help_guide_step5_title": "⑤ 詳細設定（その2）とアクション",
    "help_guide_step5_content": """<html><head/><body><h3>⚙️ 詳細設定（続き）</h3><ul><ul>
                <li><b>ログに外部リンクを表示:</b> チェックすると、メインログの下にセカンダリログパネルが表示され、投稿の説明で見つかった外部リンクが表示されます。(「🔗 リンクのみ」または「📦 アーカイブのみ」モードがアクティブな場合は無効になります)。</li>
                <li><b>📖 マンガ/コミックモード (クリエイターURLのみ):</b> シーケンシャルコンテンツ向けに調整されています。
                    <ul>
                        <li>投稿を<b>古いものから新しいものへ</b>ダウンロードします。</li>
                        <li>すべての投稿が取得されるため、「ページ範囲」入力は無効になります。</li>
                        <li>このモードがクリエイターフィードでアクティブな場合、ログエリアの右上に<b>ファイル名スタイル切り替えボタン</b>（例: 「名前: 投稿タイトル」）が表示されます。クリックすると命名スタイルが循環します:
                            <ul>
                                <li><code>名前: 投稿タイトル (デフォルト)</code>: 投稿の最初のファイルは、投稿のクリーンなタイトルにちなんで名付けられます（例: 「My Chapter 1.jpg」）。*同じ投稿*内の後続のファイルは、元のファイル名を保持しようとします（例: 「page_02.png」、「bonus_art.jpg」）。投稿にファイルが1つしかない場合は、投稿タイトルにちなんで名付けられます。これはほとんどのマンガ/コミックに一般的に推奨されます。</li>
                                <li><code>名前: 元ファイル名</code>: すべてのファイルが元のファイル名を保持しようとします。</li>
                                <li><code>名前: 元ファイル名</code>: すべてのファイルが元のファイル名を保持しようとします。このスタイルがアクティブな場合、オプションのファイル名プレフィックス（例: 「MySeries_」）をこのスタイルボタンの隣に表示される入力フィールドに入力できます。例: 「MySeries_OriginalFile.jpg」。</li>
                                <li><code>名前: タイトル+通し番号 (投稿タイトル+グローバル番号付け)</code>: 現在のダウンロードセッションのすべての投稿のすべてのファイルが、投稿のクリーンなタイトルをプレフィックスとして使用し、グローバルカウンターを続けて順番に名付けられます。例: 投稿「Chapter 1」（2ファイル）-> 「Chapter 1 001.jpg」、「Chapter 1 002.png」。次の投稿「Chapter 2」（1ファイル）は番号付けを続けます -> 「Chapter 2 003.jpg」。このスタイルの場合、正しいグローバル番号付けを保証するために、投稿処理のマルチスレッドは自動的に無効になります。</li>
                                <li><code>名前: 日付順</code>: ファイルは投稿の公開順に基づいて順番に名付けられます（001.ext、002.extなど）。このスタイルがアクティブな場合、オプションのファイル名プレフィックス（例: 「MySeries_」）をこのスタイルボタンの隣に表示される入力フィールドに入力できます。例: 「MySeries_001.jpg」。このスタイルの場合、投稿処理のマルチスレッドは自動的に無効になります。</li>
                            </ul>
                        </li>
                        <li>「名前: 投稿タイトル」、「名前: タイトル+通し番号」、または「名前: 日付順」スタイルで最良の結果を得るには、「キャラクターでフィルタリング」フィールドにマンガ/シリーズのタイトルを入力してフォルダを整理します。</li>
                    </ul>
                </li>
            </ul></li></ul>
    
    <h3>メインアクションボタン（左パネル）</h3>
    <ul>
        <li><b>⬇️ ダウンロード開始 / 🔗 リンクを抽出:</b> このボタンのテキストと機能は、「ファイルフィルター」ラジオボタンの選択に基づいて変わります。主要な操作を開始します。</li>
        <li><b>⏸️ 一時停止 / ▶️ 再開:</b> 現在のダウンロード/抽出プロセスを一時的に停止し、後で再開できます。一時停止中に一部のUI設定を変更できます。</li>
        <li><b>❌ 中止してUIリセット:</b> 現在の操作を停止し、ソフトUIリセットを実行します。URLとダウンロードディレクトリ入力は保持されますが、他の設定とログはクリアされます。</li>
    </ul></body></html>""", # JA_PLACEHOLDER - 上記の日本語HTMLコンテンツをここに入力してください
    "help_guide_step6_title": "⑥ 既知の番組/キャラクターリスト",
    "help_guide_step6_content": """<html><head/><body>
    <h3>既知の番組/キャラクターリスト管理（左下）</h3>
    <p>このセクションは、<code>Known.txt</code>ファイルの管理に役立ちます。このファイルは、「名前/タイトルでフォルダを分ける」が有効な場合にスマートなフォルダ整理に使用され、特に投稿がアクティブな「キャラクターでフィルタリング」入力に一致しない場合のフォールバックとして機能します。</p>
    <ul>
        <li><b>Known.txtを開く:</b> <code>Known.txt</code>ファイル（アプリのディレクトリにあります）をデフォルトのテキストエディタで開き、高度な編集（複雑なグループ化されたエイリアスの作成など）を行います。</li>
        <li><b>キャラクターを検索...:</b> 以下に表示される既知の名前のリストをフィルタリングします。</li>
        <li><b>リストウィジェット:</b> <code>Known.txt</code>からプライマリ名を表示します。削除するエントリをここで選択します。</li>
        <li><b>新しい番組/キャラクター名を追加 (入力フィールド):</b> 追加する名前またはグループを入力します。
            <ul>
                <li><b>単純な名前:</b> 例: <code>My Awesome Series</code>。単一のエントリとして追加されます。</li>
                <li><b>個別のKnown.txtエントリ用のグループ:</b> 例: <code>(ビビ, ウルティ, ウタ)</code>。「ビビ」、「ウルティ」、「ウタ」が3つの個別のエントリとして<code>Known.txt</code>に追加されます。</li>
                <li><b>共有フォルダ & 単一Known.txtエントリ用のグループ (チルダ<code>~</code>):</b> 例: <code>(キャラクターA, キャラA)~</code>。「キャラクターA キャラA」という名前の1つのエントリが<code>Known.txt</code>に追加されます。「キャラクターA」と「キャラA」がこの単一フォルダ/エントリのエイリアスになります。</li>
            </ul>
        </li>
        <li><b>➕ 追加ボタン:</b> 上の入力フィールドの名前/グループをリストと<code>Known.txt</code>に追加します。</li>
        <li><b>⤵️ フィルターに追加ボタン:</b>
            <ul>
                <li>「既知の番組/キャラクター」リストの「➕ 追加」ボタンの隣にあります。</li>
                <li>これをクリックすると、<code>Known.txt</code>ファイルのすべての名前がチェックボックス付きで表示されるポップアップウィンドウが開きます。</li>
                <li>ポップアップには、名前のリストをすばやくフィルタリングするための検索バーが含まれています。</li>
                <li>チェックボックスを使用して1つ以上の名前を選択できます。</li>
                <li>「選択項目を追加」をクリックすると、選択した名前がメインウィンドウの「キャラクターでフィルタリング」入力フィールドに挿入されます。</li>
                <li><code>Known.txt</code>から選択した名前が元々グループだった場合（例: Known.txtで<code>(ボア, ハンコック)</code>と定義されていた場合）、フィルターフィールドに<code>(ボア, ハンコック)~</code>として追加されます。単純な名前はそのまま追加されます。</li>
                <li>ポップアップには、「すべて選択」と「すべて選択解除」ボタンが便宜上用意されています。</li>
                <li>「キャンセル」をクリックすると、変更なしでポップアップが閉じます。</li>
            </ul>
        </li>
        <li><b>🗑️ 選択項目を削除ボタン:</b> 選択した名前をリストと<code>Known.txt</code>から削除します。</li>
        <li><b>❓ ボタン（これです！):</b> この包括的なヘルプガイドを表示します。</li>
    </ul></body></html>""", # JA_PLACEHOLDER - 上記の日本語HTMLコンテンツをここに入力してください
    "help_guide_step7_title": "⑦ ログエリアとコントロール",
    "help_guide_step7_content": """<html><head/><body>
    <h3>ログエリアとコントロール（右パネル）</h3>
    <ul>
        <li><b>📜 進捗ログ / 抽出リンクログ (ラベル):</b> メインログエリアのタイトル。「🔗 リンクのみ」モードがアクティブな場合は変わります。</li>
        <li><b>リンクを検索... / 🔍 ボタン (リンク検索):</b>
            <ul><li>「🔗 リンクのみ」モードがアクティブな場合にのみ表示されます。メインログに表示される抽出されたリンクをテキスト、URL、またはプラットフォームでリアルタイムにフィルタリングできます。</li></ul>
        </li>
        <li><b>名前: [スタイル] ボタン (マンガファイル名スタイル):</b>
            <ul><li><b>マンガ/コミックモード</b>がクリエイターフィードでアクティブで、かつ「🔗 リンクのみ」または「📦 アーカイブのみ」モードでない場合にのみ表示されます。</li>
                <li>ファイル名スタイルを循環します: <code>投稿タイトル</code>、<code>元ファイル名</code>、<code>日付順</code>。（詳細はマンガ/コミックモードのセクションを参照）。</li>
                <li>「元ファイル名」または「日付順」スタイルがアクティブな場合、オプションのファイル名プレフィックス用の入力フィールドがこのスタイルボタンの隣に表示されます。</li>
            </ul>                
        </li>
        <li><b>マルチパート: [オン/オフ] ボタン:</b>
            <ul><li>個々の大きなファイルのマルチセグメントダウンロードを切り替えます。
                <ul><li><b>オン:</b> 大きなファイルのダウンロード（例: 動画）を高速化できますが、多くの小さなファイルがある場合、UIの途切れやログのスパムが増加する可能性があります。有効にするとアドバイザリが表示されます。マルチパートダウンロードが失敗した場合、シングルストリームで再試行します。</li>
                    <li><b>オフ（デフォルト）:</b> ファイルは単一のストリームでダウンロードされます。</li>
                </ul>
                <li>「🔗 リンクのみ」または「📦 アーカイブのみ」モードがアクティブな場合は無効になります。</li>
            </ul>
        </li>
        <li><b>👁️ / 🙈 ボタン (ログビュー切り替え):</b> メインログビューを切り替えます:
            <ul>
                <li><b>👁️ 進捗ログ（デフォルト）:</b> すべてのダウンロードアクティビティ、エラー、概要を表示します。</li>
                <li><b>🙈 見逃したキャラクターログ:</b> 「キャラクターでフィルタリング」設定のためにスキップされた投稿タイトル/コンテンツのキーワードのリストを表示します。意図せずに見逃している可能性のあるコンテンツを特定するのに役立ちます。</li>
            </ul>
        </li>
        <li><b>🔄 リセットボタン:</b> すべての入力フィールド、ログをクリアし、一時的な設定をデフォルトにリセットします。ダウンロードがアクティブでない場合にのみ使用できます。</li>
        <li><b>メインログ出力 (テキストエリア):</b> 詳細な進捗メッセージ、エラー、概要を表示します。「🔗 リンクのみ」モードがアクティブな場合、このエリアには抽出されたリンクが表示されます。</li>
        <li><b>見逃したキャラクターログ出力 (テキストエリア):</b> （👁️ / 🙈 切り替えで表示可能）キャラクターフィルターのためにスキップされた投稿/ファイルを表示します。</li>
        <li><b>外部リンク出力 (テキストエリア):</b> 「ログに外部リンクを表示」がチェックされている場合、メインログの下に表示されます。投稿の説明で見つかった外部リンクを表示します。</li>
        <li><b>リンクをエクスポートボタン:</b>
            <ul><li>「🔗 リンクのみ」モードがアクティブで、リンクが抽出されている場合にのみ表示され、有効になります。</li>
                <li>抽出されたすべてのリンクを<code>.txt</code>ファイルに保存できます。</li>
            </ul>
        </li>
        <li><b>進捗: [ステータス] ラベル:</b> ダウンロードまたはリンク抽出プロセスの全体的な進捗（例: 処理済み投稿）を表示します。</li>
        <li><b>ファイル進捗ラベル:</b> 個々のファイルダウンロードの進捗（速度とサイズを含む）またはマルチパートダウンロードのステータスを表示します。</li>
    </ul></body></html>""", # JA_PLACEHOLDER - 上記の日本語HTMLコンテンツをここに入力してください
    "help_guide_step8_title": "⑧ お気に入りモードと将来の機能",
    "help_guide_step8_content": """<html><head/><body>
    <h3>お気に入りモード（Kemono.su/Coomer.suのお気に入りからダウンロード）</h3>
    <p>このモードでは、Kemono.suでお気に入りに登録したアーティストから直接コンテンツをダウンロードできます。</p>
    <ul>
        <li><b>⭐ 有効にする方法:</b>
            <ul>
                <li>「🔗 リンクのみ」ラジオボタンの隣にある<b>「⭐ お気に入りモード」</b>チェックボックスをオンにします。</li>
            </ul>
        </li>
        <li><b>お気に入りモードでのUIの変更:</b>
            <ul>
                <li>「🔗 Kemonoクリエイター/投稿URL」入力エリアは、お気に入りモードがアクティブであることを示すメッセージに置き換えられます。</li>
                <li>標準の「ダウンロード開始」、「一時停止」、「キャンセル」ボタンは、以下に置き換えられます:
                    <ul>
                        <li><b>「🖼️ お気に入りアーティスト」</b>ボタン</li>
                        <li><b>「📄 お気に入り投稿」</b>ボタン</li>
                    </ul>
                </li>
                <li>お気に入りを取得するにはCookieが必要なため、「🍪 Cookieを使用」オプションは自動的に有効になり、ロックされます。</li>
            </ul>
        </li>
        <li><b>🖼️ お気に入りアーティストボタン:</b>
            <ul>
                <li>これをクリックすると、Kemono.suでお気に入りに登録したすべてのアーティストのリストが表示されるダイアログが開きます。</li>
                <li>このリストから1人以上のアーティストを選択して、コンテンツをダウンロードできます。</li>
            </ul>
        </li>
        <li><b>📄 お気に入り投稿ボタン (将来の機能):</b>
            <ul>
                <li>特定のお気に入り<i>投稿</i>のダウンロード（特にシリーズの一部である場合のマンガのようなシーケンシャルな順序でのダウンロード）は、現在開発中の機能です。</li>
                <li>お気に入りの投稿、特にマンガのようなシーケンシャルな読書のための最適な処理方法は、まだ検討中です。</li>
                <li>お気に入りの投稿をダウンロードして整理する方法（例: お気に入りからの「マンガスタイル」）について具体的なアイデアやユースケースがある場合は、プロジェクトのGitHubページでイシューを開くか、ディスカッションに参加することを検討してください。あなたの意見は貴重です！</li>
            </ul>
        </li>
        <li><b>お気に入りダウンロードスコープ (ボタン):</b>
            <ul>
                <li>このボタン（「お気に入り投稿」の隣）は、選択したお気に入りアーティストのコンテンツのダウンロード場所を制御します:
                    <ul>
                        <li><b><i>スコープ: 選択場所:</i></b> 選択したすべてのアーティストは、UIで設定したメインの「ダウンロード場所」にダウンロードされます。フィルターはすべてのコンテンツにグローバルに適用されます。</li>
                        <li><b><i>スコープ: アーティストフォルダ:</i></b> 選択した各アーティストについて、メインの「ダウンロード場所」内にサブフォルダ（アーティスト名）が自動的に作成されます。そのアーティストのコンテンツは、特定のサブフォルダにダウンロードされます。フィルターは各アーティストの専用フォルダ内で適用されます。</li>
                    </ul>
                </li>
            </ul>
        </li>
        <li><b>お気に入りモードでのフィルター:</b>
            <ul>
                <li>UIで設定した「🎯 キャラクターでフィルタリング」、「🚫 スキップする単語」、「ファイルフィルター」オプションは、選択したお気に入りアーティストからダウンロードされるコンテンツにも適用されます。</li>
            </ul>
        </li>
    </ul></body></html>""", # JA_PLACEHOLDER - 上記の日本語HTMLコンテンツをここに入力してください
    "help_guide_step9_title": "⑨ 主要ファイルとツアー",
    "help_guide_step9_content": """<html><head/><body>
    <h3>アプリケーションが使用するキーファイル</h3>
    <ul>
        <li><b><code>Known.txt</code>:</b>
            <ul>
                <li>アプリケーションのディレクトリ（<code>.exe</code>または<code>main.py</code>がある場所）にあります。</li>
                <li>「名前/タイトルでフォルダを分ける」が有効な場合に、自動フォルダ整理のために既知の番組、キャラクター、またはシリーズタイトルのリストを保存します。</li>
                <li><b>形式:</b>
                    <ul>
                        <li>各行がエントリです。</li>
                        <li><b>単純な名前:</b> 例: <code>My Awesome Series</code>。これに一致するコンテンツは「My Awesome Series」という名前のフォルダに入ります。</li>
                        <li><b>グループ化されたエイリアス:</b> 例: <code>(キャラクターA, キャラA, 別名A)</code>。「キャラクターA」、「キャラA」、または「別名A」に一致するコンテンツはすべて、「キャラクターA キャラA 別名A」（クリーニング後）という名前の単一フォルダに入ります。括弧内のすべての用語がそのフォルダのエイリアスになります。</li>
                    </ul>
                </li>
                <li><b>使用法:</b> 投稿がアクティブな「キャラクターでフィルタリング」入力に一致しない場合のフォルダ名のフォールバックとして機能します。UIから単純なエントリを管理したり、複雑なエイリアスを作成するためにファイルを直接編集したりできます。アプリは起動時または次回使用時に再読み込みします。</li>
            </ul>
        </li>
        <li><b><code>cookies.txt</code> (オプション):</b>
            <ul>
                <li>「Cookieを使用」機能を使用し、直接Cookie文字列を提供しないか、特定のファイルを参照しない場合、アプリケーションはそのディレクトリにある<code>cookies.txt</code>という名前のファイルを探します。</li>
                <li><b>形式:</b> Netscape Cookieファイル形式である必要があります。</li>
                <li><b>使用法:</b> ダウンローダーがブラウザのログインセッションを使用して、Kemono/Coomerでログインが必要な可能性のあるコンテンツにアクセスできるようにします。</li>
            </ul>
        </li>
    </ul>

    <h3>初回ユーザーツアー</h3>
    <ul>
        <li>初回起動時（またはリセット時）に、主な機能を案内するウェルカムツアーダイアログが表示されます。スキップするか、「今後このツアーを表示しない」を選択できます。</li>
    </ul>
    <p><em>多くのUI要素には、マウスオーバーするとクイックヒントが表示されるツールチップもあります。</em></p>
    </body></html>""" # JA_PLACEHOLDER - 上記の日本語HTMLコンテンツをここに入力してください
})

translations["zh_CN"] = {} # Initialize the dictionary for zh_CN
translations["zh_CN"].update({
    "settings_dialog_title": "设置",
    "language_label": "语言：",
    "lang_english": "英语 (English)",
    "lang_japanese": "日语 (日本語)",
    "theme_toggle_light": "切换到浅色模式",
    "theme_toggle_dark": "切换到深色模式",
    "theme_tooltip_light": "将应用程序外观更改为浅色。",
    "theme_tooltip_dark": "将应用程序外观更改为深色。",
    "ok_button": "确定",
    "appearance_group_title": "外观",
    "language_group_title": "语言设置",
    "creator_post_url_label": "🔗 Kemono 作者/帖子 URL：",
    "download_location_label": "📁 下载位置：",
    "filter_by_character_label": "🎯 按角色筛选 (逗号分隔)：",
    "skip_with_words_label": "🚫 使用关键词跳过 (逗号分隔)：",
    "remove_words_from_name_label": "✂️ 从名称中删除词语：",
    "filter_all_radio": "全部",
    "filter_images_radio": "图片/GIF",
    "filter_videos_radio": "视频",
    "filter_archives_radio": "📦 仅存档",
    "filter_links_radio": "🔗 仅链接",
    "filter_audio_radio": "🎧 仅音频",
    "favorite_mode_checkbox_label": "⭐ 收藏模式",
    "browse_button_text": "浏览...",
    "char_filter_scope_files_text": "筛选：文件",
    "char_filter_scope_files_tooltip": "当前范围：文件\n\n按文件名筛选单个文件。如果任何文件匹配，则保留帖子。\n只下载该帖子中匹配的文件。\n示例：筛选“Tifa”。文件“Tifa_artwork.jpg”匹配并被下载。\n文件夹命名：使用匹配文件名中的角色。\n\n点击切换到：两者",
    "char_filter_scope_title_text": "筛选：标题",
    "char_filter_scope_title_tooltip": "当前范围：标题\n\n按帖子标题筛选整个帖子。匹配帖子的所有文件都将被下载。\n示例：筛选“Aerith”。标题为“Aerith's Garden”的帖子匹配；其所有文件都将被下载。\n文件夹命名：使用匹配帖子标题中的角色。\n\n点击切换到：文件",
    "char_filter_scope_both_text": "筛选：两者",
    "char_filter_scope_both_tooltip": "当前范围：两者 (标题优先，然后是文件)\n\n1. 检查帖子标题：如果匹配，则下载帖子中的所有文件。\n2. 如果标题不匹配，则检查文件名：如果任何文件匹配，则仅下载该文件。\n示例：筛选“Cloud”。\n - 帖子“Cloud Strife”(标题匹配) -> 所有文件都被下载。\n - 帖子“Bike Chase”中包含“Cloud_fenrir.jpg”(文件匹配) -> 仅下载“Cloud_fenrir.jpg”。\n文件夹命名：优先考虑标题匹配，然后是文件匹配。\n\n点击切换到：评论",
    "char_filter_scope_comments_text": "筛选：评论 (测试版)",
    "char_filter_scope_comments_tooltip": "当前范围：评论 (测试版 - 文件优先，然后是评论作为后备)\n\n1. 检查文件名：如果帖子中的任何文件与筛选器匹配，则下载整个帖子。评论不会针对此筛选词进行检查。\n2. 如果没有文件匹配，则检查帖子评论：如果评论匹配，则下载整个帖子。\n示例：筛选“Barret”。\n - 帖子 A：文件“Barret_gunarm.jpg”、“other.png”。文件“Barret_gunarm.jpg”匹配。帖子 A 的所有文件都被下载。评论中不会检查“Barret”。\n - 帖子 B：文件“dyne.jpg”、“weapon.gif”。评论：“...一张 Barret Wallace 的画...”。没有文件匹配“Barret”。评论匹配。帖子 B 的所有文件都被下载。\n文件夹命名：优先考虑文件匹配中的角色，然后是评论匹配中的角色。\n\n点击切换到：标题",
    "char_filter_scope_unknown_text": "筛选：未知",
    "char_filter_scope_unknown_tooltip": "当前范围：未知\n\n角色筛选范围处于未知状态。请循环或重置。\n\n点击切换到：标题",
    "skip_words_input_tooltip": "输入词语，以逗号分隔，以跳过下载某些内容（例如，WIP、sketch、preview）。\n\n此输入旁边的“范围：[类型]”按钮可循环此筛选器的应用方式：\n- 范围：文件：如果文件名包含任何这些词语，则跳过单个文件。\n- 范围：帖子：如果帖子标题包含任何这些词语，则跳过整个帖子。\n- 范围：两者：同时应用两者（首先是帖子标题，如果帖子标题可以，则应用单个文件）。",
    "remove_words_input_tooltip": "输入词语，以逗号分隔，以从下载的文件名中删除（不区分大小写）。\n用于清理常见的前缀/后缀。\n示例：patreon、kemono、[HD]、_final",
    "skip_scope_files_text": "范围：文件",
    "skip_scope_files_tooltip": "当前跳过范围：文件\n\n如果文件名包含任何“要跳过的词语”，则跳过单个文件。\n示例：跳过词语“WIP，sketch”。\n- 文件“art_WIP.jpg”-> 已跳过。\n- 文件“final_art.png”-> 已下载（如果满足其他条件）。\n\n帖子仍会处理其他未跳过的文件。\n点击切换到：两者",
    "skip_scope_posts_text": "范围：帖子",
    "skip_scope_posts_tooltip": "当前跳过范围：帖子\n\n如果帖子标题包含任何“要跳过的词语”，则跳过整个帖子。\n跳过的帖子中的所有文件都将被忽略。\n示例：跳过词语“preview，announcement”。\n- 帖子“激动人心的公告！”-> 已跳过。\n- 帖子“完成的艺术品”-> 已处理（如果满足其他条件）。\n\n点击切换到：文件",
    "skip_scope_both_text": "范围：两者",
    "skip_scope_both_tooltip": "当前跳过范围：两者（帖子优先，然后是文件）\n\n1. 检查帖子标题：如果标题包含跳过词语，则整个帖子被跳过。\n2. 如果帖子标题可以，则检查单个文件名：如果文件名包含跳过词语，则仅跳过该文件。\n示例：跳过词语“WIP，sketch”。\n- 帖子“草图和WIPs”（标题匹配）-> 整个帖子被跳过。\n- 帖子“艺术更新”（标题可以），包含文件：\n- “character_WIP.jpg”（文件匹配）-> 已跳过。\n- “final_scene.png”（文件可以）-> 已下载。\n\n点击切换到：帖子",
    "skip_scope_unknown_text": "范围：未知",
    "skip_scope_unknown_tooltip": "当前跳过范围：未知\n\n跳过词语的范围处于未知状态。请循环或重置。\n\n点击切换到：帖子",
    "language_change_title": "语言已更改",
    "language_change_message": "语言已更改。需要重新启动才能使所有更改完全生效。",
    "language_change_informative": "您想现在重新启动应用程序吗？",
    "restart_now_button": "立即重启",
    "skip_zip_checkbox_label": "跳过 .zip",
    "skip_rar_checkbox_label": "跳过 .rar",
    "download_thumbnails_checkbox_label": "仅下载缩略图",
    "scan_content_images_checkbox_label": "扫描内容中的图片",
    "compress_images_checkbox_label": "压缩为 WebP",
    "separate_folders_checkbox_label": "按名称/标题分文件夹",
    "subfolder_per_post_checkbox_label": "每篇帖子一个子文件夹",
    "use_cookie_checkbox_label": "使用 Cookie",
    "use_multithreading_checkbox_base_label": "使用多线程",
    "show_external_links_checkbox_label": "在日志中显示外部链接",
    "manga_comic_mode_checkbox_label": "漫画/动漫模式",
    "threads_label": "线程数：",
    "start_download_button_text": "⬇️ 开始下载",
    "start_download_button_tooltip": "点击以使用当前设置开始下载或链接提取过程。",
    "extract_links_button_text": "🔗 提取链接",
    "pause_download_button_text": "⏸️ 暂停下载",
    "pause_download_button_tooltip": "点击以暂停正在进行的下载过程。",
    "resume_download_button_text": "▶️ 继续下载",
    "resume_download_button_tooltip": "点击以继续下载。",
    "cancel_button_text": "❌ 取消并重置界面",
    "cancel_button_tooltip": "点击以取消正在进行的下载/提取过程并重置界面字段（保留 URL 和目录）。",
    "error_button_text": "错误",
    "error_button_tooltip": "查看因错误而跳过的文件，并可选择重试。",
    "cancel_retry_button_text": "❌ 取消重试",
    "known_chars_label_text": "🎭 已知系列/角色（用于文件夹名称）：",
    "open_known_txt_button_text": "打开 Known.txt",
    "known_chars_list_tooltip": "此列表包含在启用“分文件夹”且未提供或未匹配帖子的特定“按角色筛选”时用于自动创建文件夹的名称。\n添加您经常下载的系列、游戏或角色的名称。",
    "open_known_txt_button_tooltip": "在您的默认文本编辑器中打开“Known.txt”文件。\n该文件位于应用程序的目录中。",
    "add_char_button_text": "➕ 添加",
    "add_char_button_tooltip": "将输入字段中的名称添加到“已知系列/角色”列表中。",
    "add_to_filter_button_text": "⤵️ 添加到筛选器",
    "add_to_filter_button_tooltip": "从“已知系列/角色”列表中选择名称以添加到上面的“按角色筛选”字段。",
    "delete_char_button_text": "🗑️ 删除所选",
    "delete_char_button_tooltip": "从“已知系列/角色”列表中删除所选的名称。",
    "progress_log_label_text": "📜 进度日志：",
    "radio_all_tooltip": "下载帖子中找到的所有文件类型。",
    "radio_images_tooltip": "仅下载常见的图像格式（JPG、PNG、GIF、WEBP 等）。",
    "radio_videos_tooltip": "仅下载常见的视频格式（MP4、MKV、WEBM、MOV 等）。",
    "radio_only_archives_tooltip": "专门下载 .zip 和 .rar 文件。其他特定于文件的选项将被禁用。",
    "radio_only_audio_tooltip": "仅下载常见的音频格式（MP3、WAV、FLAC 等）。",
    "radio_only_links_tooltip": "从帖子描述中提取并显示外部链接，而不是下载文件。\n与下载相关的选项将被禁用。",
    "favorite_mode_checkbox_tooltip": "启用收藏模式以浏览已保存的艺术家/帖子。\n这将用收藏选择按钮替换 URL 输入。",
    "skip_zip_checkbox_tooltip": "如果选中，将不下载 .zip 存档文件。\n（如果选择了“仅存档”，则禁用）。",
    "skip_rar_checkbox_tooltip": "如果选中，将不下载 .rar 存档文件。\n（如果选择了“仅存档”，则禁用）。",
    "download_thumbnails_checkbox_tooltip": "下载 API 中的小预览图像，而不是全尺寸文件（如果可用）。\n如果还选中了“扫描帖子内容以查找图像 URL”，则此模式将*仅*下载内容扫描找到的图像（忽略 API 缩略图）。",
    "scan_content_images_checkbox_tooltip": "如果选中，下载器将扫描帖子的 HTML 内容以查找图像 URL（来自 <img> 标签或直接链接）。\n这包括将 <img> 标签中的相对路径解析为完整 URL。\n<img> 标签中的相对路径（例如，/data/image.jpg）将被解析为完整 URL。\n在图像位于帖子描述中但不在 API 的文件/附件列表中的情况下很有用。",
    "compress_images_checkbox_tooltip": "将大于 1.5MB 的图像压缩为 WebP 格式（需要 Pillow）。",
    "use_subfolders_checkbox_tooltip": "根据“按角色筛选”输入或帖子标题创建子文件夹。\n如果没有特定筛选器匹配，则使用“已知系列/角色”列表作为文件夹名称的后备。\n为单个帖子启用“按角色筛选”输入和“自定义文件夹名称”。",
    "use_subfolder_per_post_checkbox_tooltip": "为每个帖子创建一个子文件夹。如果“分文件夹”也打开，则它位于角色/标题文件夹内。",
    "use_cookie_checkbox_tooltip": "如果选中，将尝试使用应用程序目录中的“cookies.txt”（Netscape 格式）中的 cookie 进行请求。\n用于访问需要在 Kemono/Coomer 上登录的内容。",
    "cookie_text_input_tooltip": "直接输入您的 cookie 字符串。\n如果选中了“使用 Cookie”并且“cookies.txt”未找到或此字段不为空，则将使用此字符串。\n格式取决于后端如何解析它（例如，“name1=value1; name2=value2”）。",
    "use_multithreading_checkbox_tooltip": "启用并发操作。有关详细信息，请参见“线程数”输入。",
    "thread_count_input_tooltip": "并发操作的数量。\n- 单个帖子：并发文件下载（建议 1-10 个）。\n- 创建者源 URL：要同时处理的帖子数量（建议 1-200 个）。\n每个帖子中的文件都由其工作线程逐个下载。\n如果未选中“使用多线程”，则使用 1 个线程。",
    "external_links_checkbox_tooltip": "如果选中，主日志下方会出现一个辅助日志面板，以显示在帖子描述中找到的外部链接。\n（如果“仅链接”或“仅存档”模式处于活动状态，则禁用）。",
    "manga_mode_checkbox_tooltip": "从最旧到最新下载帖子，并根据帖子标题重命名文件（仅限创建者源）。",
    "multipart_on_button_text": "多部分：开",
    "multipart_on_button_tooltip": "多部分下载：开\n\n启用同时以多个分段下载大文件。\n- 可以加快单个大文件（例如视频）的下载速度。\n- 可能会增加 CPU/网络使用率。\n- 对于有许多小文件的源，这可能不会带来速度优势，并且可能会使界面/日志变得繁忙。\n- 如果多部分下载失败，它会以单流方式重试。\n\n点击关闭。",
    "multipart_off_button_text": "多部分：关",
    "multipart_off_button_tooltip": "多部分下载：关\n\n所有文件都使用单流下载。\n- 稳定，适用于大多数情况，尤其是许多较小的文件。\n- 大文件按顺序下载。\n\n点击开启（请参阅建议）。",
    "reset_button_text": "🔄 重置",
    "reset_button_tooltip": "将所有输入和日志重置为默认状态（仅在空闲时）。",
    "progress_idle_text": "进度：空闲",
    "missed_character_log_label_text": "🚫 错过的角色日志：",
    "creator_popup_title": "创作者选择",
    "creator_popup_search_placeholder": "按名称、服务搜索或粘贴创作者 URL...",
    "creator_popup_add_selected_button": "添加所选",
    "creator_popup_scope_characters_button": "范围：角色",
    "creator_popup_scope_creators_button": "范围：创作者",
    "favorite_artists_button_text": "🖼️ 收藏的艺术家",
    "favorite_artists_button_tooltip": "浏览并从您在 Kemono.su/Coomer.su 上收藏的艺术家那里下载。",
    "favorite_posts_button_text": "📄 收藏的帖子",
    "favorite_posts_button_tooltip": "浏览并下载您在 Kemono.su/Coomer.su 上收藏的帖子。",
    "favorite_scope_selected_location_text": "范围：所选位置",
    "favorite_scope_selected_location_tooltip": "当前收藏下载范围：所选位置\n\n所有选定的收藏艺术家/帖子都将下载到界面中指定的主“下载位置”。\n筛选器（角色、跳过词语、文件类型）将全局应用于所有内容。\n\n点击以更改为：艺术家文件夹",
    "favorite_scope_artist_folders_text": "范围：艺术家文件夹",
    "favorite_scope_artist_folders_tooltip": "当前收藏下载范围：艺术家文件夹\n\n对于每个选定的收藏艺术家/帖子，将在主“下载位置”内创建一个新的子文件夹（以艺术家命名）。\n该艺术家/帖子的内容将下载到其特定的子文件夹中。\n筛选器（角色、跳过词语、文件类型）将*在*每个艺术家的文件夹内应用。\n\n点击以更改为：所选位置",
    "favorite_scope_unknown_text": "范围：未知",
    "favorite_scope_unknown_tooltip": "收藏下载范围未知。点击以循环。",
    "manga_style_post_title_text": "名称：帖子标题",
    "manga_style_original_file_text": "名称：原始文件",
    "manga_style_date_based_text": "名称：基于日期",
    "manga_style_title_global_num_text": "名称：标题+全局编号",
    "manga_style_unknown_text": "名称：未知样式",
    "fav_artists_dialog_title": "收藏的艺术家",
    "fav_artists_loading_status": "正在加载收藏的艺术家...",
    "fav_artists_search_placeholder": "搜索艺术家...",
    "fav_artists_select_all_button": "全选",
    "fav_artists_deselect_all_button": "取消全选",
    "fav_artists_download_selected_button": "下载所选",
    "fav_artists_cancel_button": "取消",
    "fav_artists_loading_from_source_status": "⏳ 正在从 {source_name} 加载收藏...",
    "fav_artists_found_status": "总共找到 {count} 位收藏的艺术家。",
    "fav_artists_none_found_status": "在 Kemono.su 或 Coomer.su 上未找到收藏的艺术家。",
    "fav_artists_failed_status": "获取收藏失败。",
    "fav_artists_cookies_required_status": "错误：已启用 Cookie，但无法为任何来源加载。",
    "fav_artists_no_favorites_after_processing": "处理后未找到收藏的艺术家。",
    "fav_artists_no_selection_title": "未选择",
    "fav_artists_no_selection_message": "请至少选择一位要下载的艺术家。",
    "fav_posts_dialog_title": "收藏的帖子",
    "fav_posts_loading_status": "正在加载收藏的帖子...",
    "fav_posts_search_placeholder": "搜索帖子（标题、创作者、ID、服务）...",
    "fav_posts_select_all_button": "全选",
    "fav_posts_deselect_all_button": "取消全选",
    "fav_posts_download_selected_button": "下载所选",
    "fav_posts_cancel_button": "取消",
    "fav_posts_cookies_required_error": "错误：收藏的帖子需要 Cookie，但无法加载。",
    "fav_posts_auth_failed_title": "授权失败（帖子）",
    "fav_posts_auth_failed_message": "由于授权错误，无法获取收藏{domain_specific_part}：\n\n{error_message}\n\n这通常意味着您的 cookie 丢失、无效或已过期。请检查您的 cookie 设置。",
    "fav_posts_fetch_error_title": "获取错误",
    "fav_posts_fetch_error_message": "从 {domain}{error_message_part} 获取收藏时出错",
    "fav_posts_no_posts_found_status": "未找到收藏的帖子。",
    "fav_posts_found_status": "找到 {count} 个收藏的帖子。",
    "fav_posts_display_error_status": "显示帖子时出错：{error}",
    "fav_posts_ui_error_title": "界面错误",
    "fav_posts_ui_error_message": "无法显示收藏的帖子：{error}",
    "fav_posts_auth_failed_message_generic": "由于授权错误，无法获取收藏{domain_specific_part}。这通常意味着您的 cookie 丢失、无效或已过期。请检查您的 cookie 设置。",
    "key_fetching_fav_post_list_init": "正在获取收藏的帖子列表...",
    "key_fetching_from_source_kemono_su": "正在从 Kemono.su 获取收藏...",
    "key_fetching_from_source_coomer_su": "正在从 Coomer.su 获取收藏...",
    "fav_posts_fetch_cancelled_status": "收藏帖子获取已取消。",
    "known_names_filter_dialog_title": "将已知名称添加到筛选器",
    "known_names_filter_search_placeholder": "搜索名称...",
    "known_names_filter_select_all_button": "全选",
    "known_names_filter_deselect_all_button": "取消全选",
    "known_names_filter_add_selected_button": "添加所选",
    "error_files_dialog_title": "因错误而跳过的文件",
    "error_files_no_errors_label": "在上次会话中或重试后，没有文件因错误而被记录为已跳过。",
    "error_files_found_label": "由于下载错误，以下 {count} 个文件已被跳过：",
    "error_files_select_all_button": "全选",
    "error_files_retry_selected_button": "重试所选",
    "error_files_export_urls_button": "将 URL 导出到 .txt",
    "error_files_no_selection_retry_message": "请至少选择一个文件进行重试。",
    "error_files_no_errors_export_title": "无错误",
    "error_files_no_errors_export_message": "没有要导出的错误文件 URL。",
    "error_files_no_urls_found_export_title": "未找到 URL",
    "error_files_no_urls_found_export_message": "无法从错误文件列表中提取任何 URL 进行导出。",
    "error_files_save_dialog_title": "保存错误文件 URL",
    "error_files_export_success_title": "导出成功",
    "error_files_export_success_message": "成功将 {count} 个条目导出到：\n{filepath}",
    "error_files_export_error_title": "导出错误",
    "error_files_export_error_message": "无法导出文件链接：{error}",
    "export_options_dialog_title": "导出选项",
    "export_options_description_label": "选择导出错误文件链接的格式：",
    "export_options_radio_link_only": "每行一个链接（仅 URL）",
    "export_options_radio_link_only_tooltip": "仅导出每个失败文件的直接下载 URL，每行一个 URL。",
    "export_options_radio_with_details": "导出时附带详细信息（URL [帖子、文件信息]）",
    "export_options_radio_with_details_tooltip": "导出 URL，后跟帖子标题、帖子 ID 和原始文件名等详细信息（在括号中）。",
    "export_options_export_button": "导出",
    "no_errors_logged_title": "未记录错误",
    "no_errors_logged_message": "在上次会话中或重试后，没有文件因错误而被记录为已跳过。",
    "progress_initializing_text": "进度：正在初始化...",
    "progress_posts_text": "进度：{processed_posts} / {total_posts} 个帖子 ({progress_percent:.1f}%)",
    "progress_processing_post_text": "进度：正在处理帖子 {processed_posts}...",
    "progress_starting_text": "进度：正在开始...",
    "downloading_file_known_size_text": "正在下载“{filename}”({downloaded_mb:.1f}MB / {total_mb:.1f}MB)",
    "downloading_file_unknown_size_text": "正在下载“{filename}”({downloaded_mb:.1f}MB)",
    "downloading_multipart_text": "下载“{filename}...”：{downloaded_mb:.1f}/{total_mb:.1f} MB（{parts} 个部分 @ {speed:.2f} MB/s）",
    "downloading_multipart_initializing_text": "文件：{filename} - 正在初始化部分...",
    "status_completed": "已完成",
    "status_cancelled_by_user": "用户已取消",
    "files_downloaded_label": "已下载",
    "files_skipped_label": "已跳过",
    "retry_finished_text": "重试完成",
    "succeeded_text": "成功",
    "failed_text": "失败",
    "ready_for_new_task_text": "准备好执行新任务。",
    "fav_mode_active_label_text": "⭐ 收藏模式已激活。请在选择您收藏的艺术家/帖子之前选择下面的筛选器。在下面选择操作。",
    "export_links_button_text": "导出链接",
    "download_extracted_links_button_text": "下载",
    "download_selected_button_text": "下载所选",
    "link_input_placeholder_text": "例如，https://kemono.su/patreon/user/12345 或 .../post/98765",
    "link_input_tooltip_text": "输入 Kemono/Coomer 创建者页面或特定帖子的完整 URL。\n示例（创建者）：https://kemono.su/patreon/user/12345\n示例（帖子）：https://kemono.su/patreon/user/12345/post/98765",
    "dir_input_placeholder_text": "选择将保存下载的文件夹",
    "dir_input_tooltip_text": "输入或浏览到将保存所有下载内容的主文件夹。\n除非选择了“仅链接”模式，否则此字段是必需的。",
    "character_input_placeholder_text": "例如，Tifa、Aerith、(Cloud, Zack)",
    "custom_folder_input_placeholder_text": "可选：将此帖子保存到特定文件夹",
    "custom_folder_input_tooltip_text": "如果下载单个帖子 URL 并且启用了“按名称/标题分文件夹”，\n您可以在此处为该帖子的下载文件夹输入自定义名称。\n示例：我最喜欢的场景",
    "skip_words_input_placeholder_text": "例如，WM、WIP、sketch、preview",
    "remove_from_filename_input_placeholder_text": "例如，patreon、HD",
    "cookie_text_input_placeholder_no_file_selected_text": "Cookie 字符串（如果未选择 cookies.txt）",
    "cookie_text_input_placeholder_with_file_selected_text": "正在使用所选的 cookie 文件（请参阅浏览...）",
    "character_search_input_placeholder_text": "搜索角色...",
    "character_search_input_tooltip_text": "在此处键入以筛选下面已知的系列/角色列表。",
    "new_char_input_placeholder_text": "添加新的系列/角色名称",
    "new_char_input_tooltip_text": "输入要添加到上面列表的新系列、游戏或角色名称。",
    "link_search_input_placeholder_text": "搜索链接...",
    "link_search_input_tooltip_text": "在“仅链接”模式下，在此处键入以按文本、URL 或平台筛选显示的链接。",
    "manga_date_prefix_input_placeholder_text": "漫画文件名前缀",
    "manga_date_prefix_input_tooltip_text": "“基于日期”或“原始文件”漫画文件名的可选前缀（例如，“系列名称”）。\n如果为空，文件将根据样式命名，不带前缀。",
    "log_display_mode_links_view_text": "🔗 链接视图",
    "log_display_mode_progress_view_text": "⬇️ 进度视图",
    "download_external_links_dialog_title": "下载所选的外部链接",
    "select_all_button_text": "全选",
    "deselect_all_button_text": "取消全选",
    "cookie_browse_button_tooltip": "浏览 cookie 文件（Netscape 格式，通常为 cookies.txt）。\n如果选中了“使用 Cookie”并且上面的文本字段为空，则将使用此文件。",
    "page_range_label_text": "页面范围：",
    "start_page_input_placeholder": "开始",
    "start_page_input_tooltip": "对于创建者 URL：指定要从中下载的起始页码（例如，1、2、3）。\n留空或设置为 1 以从第一页开始。\n对于单个帖子 URL 或漫画/动漫模式禁用。",
    "page_range_to_label_text": "到",
    "end_page_input_placeholder": "结束",
    "end_page_input_tooltip": "对于创建者 URL：指定要下载到的结束页码（例如，5、10）。\n留空以从起始页下载所有页面。\n对于单个帖子 URL 或漫画/动漫模式禁用。",
    "known_names_help_button_tooltip_text": "打开应用程序功能指南。",
    "future_settings_button_tooltip_text": "打开应用程序设置（主题、语言等）。",
    "link_search_button_tooltip_text": "筛选显示的链接",
    "confirm_add_all_dialog_title": "确认添加新名称",
    "confirm_add_all_info_label": "您输入的“按角色筛选”中的以下新名称/组不在“Known.txt”中。\n添加它们可以改善将来下载的文件夹组织。\n\n请查看列表并选择一个操作：",
    "confirm_add_all_select_all_button": "全选",
    "confirm_add_all_deselect_all_button": "取消全选",
    "confirm_add_all_add_selected_button": "将所选添加到 Known.txt",
    "confirm_add_all_skip_adding_button": "跳过添加这些",
    "confirm_add_all_cancel_download_button": "取消下载",
    "cookie_help_dialog_title": "Cookie 文件说明",
    "cookie_help_instruction_intro": "<p>要使用 cookie，您通常需要浏览器中的 <b>cookies.txt</b> 文件。</p>",
    "cookie_help_how_to_get_title": "<p><b>如何获取 cookies.txt：</b></p>",
    "cookie_help_step1_extension_intro": "<li>为您的基于 Chrome 的浏览器安装“Get cookies.txt LOCALLY”扩展程序：<br><a href=\"https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc\" style=\"color: #87CEEB;\">在 Chrome 网上应用店获取 Get cookies.txt LOCALLY</a></li>",
    "cookie_help_step2_login": "<li>转到网站（例如，kemono.su 或 coomer.su）并根据需要登录。</li>",
    "cookie_help_step3_click_icon": "<li>单击浏览器工具栏中的扩展程序图标。</li>",
    "cookie_help_step4_export": "<li>单击“导出”按钮（例如，“导出为”、“导出 cookies.txt”——确切的措辞可能会因扩展程序版本而异）。</li>",
    "cookie_help_step5_save_file": "<li>将下载的 <code>cookies.txt</code> 文件保存到您的计算机。</li>",
    "cookie_help_step6_app_intro": "<li>在此应用程序中：<ul>",
    "cookie_help_step6a_checkbox": "<li>确保选中“使用 Cookie”复选框。</li>",
    "cookie_help_step6b_browse": "<li>单击 cookie 文本字段旁边的“浏览...”按钮。</li>",
    "cookie_help_step6c_select": "<li>选择您刚刚保存的 <code>cookies.txt</code> 文件。</li></ul></li>",
    "cookie_help_alternative_paste": "<p>或者，某些扩展程序可能允许您直接复制 cookie 字符串。如果是这样，您可以将其粘贴到文本字段中，而不是浏览文件。</p>",
    "cookie_help_proceed_without_button": "不使用 Cookie 下载",
    "cookie_help_cancel_download_button": "取消下载",
    "character_input_tooltip": "输入角色名称（以逗号分隔）。支持高级分组，并在启用“分文件夹”时影响文件夹命名。\n\n示例：\n- Nami → 匹配“Nami”，创建文件夹“Nami”。\n- (Ulti, Vivi) → 匹配任一者，文件夹“Ulti Vivi”，将两者分别添加到 Known.txt。\n- (Boa, Hancock)~ → 匹配任一者，文件夹“Boa Hancock”，在 Known.txt 中添加为一个组。\n\n名称被视为匹配的别名。\n\n筛选模式（按钮循环）：\n- 文件：按文件名筛选。\n- 标题：按帖子标题筛选。\n- 两者：标题优先，然后是文件名。\n- 评论（测试版）：文件名优先，然后是帖子评论。",
    "tour_dialog_title": "欢迎使用 Kemono Downloader！",
    "tour_dialog_never_show_checkbox": "不再显示此导览",
    "tour_dialog_skip_button": "跳过导览",
    "tour_dialog_back_button": "返回",
    "tour_dialog_next_button": "下一步",
    "tour_dialog_finish_button": "完成",
    "tour_dialog_step1_title": "👋 欢迎！",
    "tour_dialog_step1_content": "您好！此快速导览将带您了解 Kemono Downloader 的主要功能，包括最近的更新，如增强的筛选、漫画模式改进和 cookie 管理。\n<ul>\n<li>我的目标是帮助您轻松地从 <b>Kemono</b> 和 <b>Coomer</b> 下载内容。</li><br>\n<li><b>🎨 创建者选择按钮：</b>在 URL 输入旁边，单击调色板图标以打开一个对话框。浏览并从您的 <code>creators.json</code> 文件中选择创建者，以快速将其名称添加到 URL 输入中。</li><br>\n<li><b>重要提示：应用程序“（无响应）”？</b><br>\n单击“开始下载”后，尤其是在处理大型创建者源或使用许多线程时，应用程序可能会暂时显示为“（无响应）”。您的操作系统（Windows、macOS、Linux）甚至可能会建议您“结束进程”或“强制退出”。<br>\n<b>请耐心等待！</b>应用程序通常仍在后台努力工作。在强制关闭之前，请尝试在文件浏览器中检查您选择的“下载位置”。如果您看到正在创建新文件夹或出现文件，则表示下载正在正确进行。给它一些时间以再次响应。</li><br>\n<li>使用<b>下一步</b>和<b>返回</b>按钮进行导航。</li><br>\n<li>将鼠标悬停在许多选项上可以查看更多详细信息的工具提示。</li><br>\n<li>随时单击<b>跳过导览</b>以关闭本指南。</li><br>\n<li>如果您不希望在将来启动时看到此导览，请选中<b>“不再显示此导览”</b>。</li>\n</ul>",
    "tour_dialog_step2_title": "① 入门",
    "tour_dialog_step2_content": "让我们从下载的基础知识开始：\n<ul>\n<li><b>🔗 Kemono 创建者/帖子 URL：</b><br>\n粘贴创建者页面的完整网址（URL）（例如，<i>https://kemono.su/patreon/user/12345</i>）\n或特定帖子（例如，<i>.../post/98765</i>）。<br>\n或 Coomer 创建者（例如，<i>https://coomer.su/onlyfans/user/artistname</i>）</li><br>\n<li><b>📁 下载位置：</b><br>\n单击“浏览...”以选择计算机上的一个文件夹，所有下载的文件都将保存在该文件夹中。\n除非您使用“仅链接”模式，否则此字段是必需的。</li><br>\n<li><b>📄 页面范围（仅限创建者 URL）：</b><br>\n如果从创建者页面下载，您可以指定要获取的页面范围（例如，第 2 到 5 页）。\n留空以获取所有页面。对于单个帖子 URL 或当<b>漫画/动漫模式</b>处于活动状态时，此功能被禁用。</li>\n</ul>",
    "tour_dialog_step3_title": "② 筛选下载",
    "tour_dialog_step3_content": "使用这些筛选器优化您的下载（在“仅链接”或“仅存档”模式下，大多数筛选器都被禁用）：\n<ul>\n<li><b>🎯 按角色筛选：</b><br>\n输入角色名称，以逗号分隔（例如，<i>Tifa, Aerith</i>）。将别名分组以获得组合的文件夹名称：<i>(alias1, alias2, alias3)</i> 变为文件夹“alias1 alias2 alias3”（清理后）。组中的所有名称都用作匹配的别名。<br>\n此输入旁边的<b>“筛选：[类型]”</b>按钮可循环此筛选器的应用方式：\n<ul><li><i>筛选：文件：</i>检查单个文件名。如果任何文件匹配，则保留帖子；仅下载匹配的文件。文件夹命名使用匹配文件名中的角色（如果启用了“分文件夹”）。</li><br>\n<li><i>筛选：标题：</i>检查帖子标题。匹配帖子的所有文件都将被下载。文件夹命名使用匹配帖子标题中的角色。</li>\n<li><b>⤵️ 添加到筛选器按钮（已知名称）：</b>在已知名称的“添加”按钮旁边（参见第 5 步），这将打开一个弹出窗口。通过复选框（带搜索栏）从您的 <code>Known.txt</code> 列表中选择名称，以快速将其添加到“按角色筛选”字段。来自 Known.txt 的分组名称（如 <code>(Boa, Hancock)</code>）将作为 <code>(Boa, Hancock)~</code> 添加到筛选器中。</li><br>\n<li><i>筛选：两者：</i>首先检查帖子标题。如果匹配，则下载所有文件。如果不匹配，则检查文件名，并且仅下载匹配的文件。文件夹命名优先考虑标题匹配，然后是文件匹配。</li><br>\n<li><i>筛选：评论（测试版）：</i>首先检查文件名。如果文件匹配，则下载帖子中的所有文件。如果没有文件匹配，则检查帖子评论。如果评论匹配，则下载所有文件。（使用更多的 API 请求）。文件夹命名优先考虑文件匹配，然后是评论匹配。</li></ul>\n如果启用了“按名称/标题分文件夹”，此筛选器也会影响文件夹命名。</li><br>\n<li><b>🚫 使用关键词跳过：</b><br>\n输入词语，以逗号分隔（例如，<i>WIP, sketch, preview</i>）。\n此输入旁边的<b>“范围：[类型]”</b>按钮可循环此筛选器的应用方式：\n<ul><li><i>范围：文件：</i>如果文件名包含任何这些词语，则跳过文件。</li><br>\n<li><i>范围：帖子：</i>如果帖子标题包含任何这些词语，则跳过整个帖子。</li><br>\n<li><i>范围：两者：</i>同时应用文件和帖子标题跳过（帖子优先，然后是文件）。</li></ul></li><br>\n<li><b>筛选文件（单选按钮）：</b>选择要下载的内容：\n<ul>\n<li><i>全部：</i>下载找到的所有文件类型。</li><br>\n<li><i>图片/GIF：</i>仅常见的图像格式和 GIF。</li><br>\n<li><i>视频：</i>仅常见的视频格式。</li><br>\n<li><b><i>📦 仅存档：</i></b>专门下载 <b>.zip</b> 和 <b>.rar</b> 文件。选择此选项后，“跳过 .zip”和“跳过 .rar”复选框将自动禁用并取消选中。“显示外部链接”也将被禁用。</li><br>\n<li><i>🎧 仅音频：</i>仅常见的音频格式（MP3、WAV、FLAC 等）。</li><br>\n<li><i>🔗 仅链接：</i>从帖子描述中提取并显示外部链接，而不是下载文件。与下载相关的选项和“显示外部链接”将被禁用。</li>\n</ul></li>\n</ul>",
    "tour_dialog_step4_title": "③ 收藏模式（替代下载）",
    "tour_dialog_step4_content": "该应用程序提供“收藏模式”，用于从您在 Kemono.su 上收藏的艺术家那里下载内容。\n<ul>\n<li><b>⭐ 收藏模式复选框：</b><br>\n位于“🔗 仅链接”单选按钮旁边。选中此项以激活收藏模式。</li><br>\n<li><b>收藏模式下的情况：</b>\n<ul><li>“🔗 Kemono 创建者/帖子 URL”输入区域被一条消息替换，指示收藏模式已激活。</li><br>\n<li>标准的“开始下载”、“暂停”、“取消”按钮被替换为“🖼️ 收藏的艺术家”和“📄 收藏的帖子”按钮（注意：“收藏的帖子”计划在将来推出）。</li><br>\n<li>“🍪 使用 Cookie”选项被自动启用并锁定，因为获取您的收藏需要 cookie。</li></ul></li><br>\n<li><b>🖼️ 收藏的艺术家按钮：</b><br>\n单击此按钮可打开一个对话框，其中列出了您在 Kemono.su 上收藏的艺术家。您可以选择一个或多个艺术家进行下载。</li><br>\n<li><b>收藏下载范围（按钮）：</b><br>\n此按钮（在“收藏的帖子”旁边）控制所选收藏的下载位置：\n<ul><li><i>范围：所选位置：</i>所有选定的艺术家都下载到您设置的主“下载位置”。筛选器全局应用。</li><br>\n<li><i>范围：艺术家文件夹：</i>在您的主“下载位置”内为每个选定的艺术家创建一个子文件夹（以艺术家命名）。该艺术家的内容将进入其特定的子文件夹。筛选器在每个艺术家的文件夹内应用。</li></ul></li><br>\n<li><b>收藏模式下的筛选器：</b><br>\n“按角色筛选”、“使用关键词跳过”和“筛选文件”选项仍然适用于从您选定的收藏艺术家那里下载的内容。</li>\n</ul>",
    "tour_dialog_step5_title": "④ 微调下载",
    "tour_dialog_step5_content": "更多选项可自定义您的下载：\n<ul>\n<li><b>跳过 .zip / 跳过 .rar：</b>选中这些项以避免下载这些存档文件类型。\n<i>（注意：如果选择了“📦 仅存档”筛选模式，这些项将被禁用和忽略）。</i></li><br>\n<li><b>✂️ 从名称中删除词语：</b><br>\n输入词语，以逗号分隔（例如，<i>patreon, [HD]</i>），以从下载的文件名中删除（不区分大小写）。</li><br>\n<li><b>仅下载缩略图：</b>下载小预览图像，而不是全尺寸文件（如果可用）。</li><br>\n<li><b>压缩大图像：</b>如果安装了“Pillow”库，大于 1.5MB 的图像如果 WebP 版本明显更小，将被转换为 WebP 格式。</li><br>\n<li><b>🗄️ 自定义文件夹名称（仅限单个帖子）：</b><br>\n如果您正在下载单个特定帖子 URL 并且启用了“按名称/标题分文件夹”，\n您可以在此处为该帖子的下载文件夹输入自定义名称。</li><br>\n<li><b>🍪 使用 Cookie：</b>选中此项以使用 cookie 进行请求。您可以：\n<ul><li>直接在文本字段中输入 cookie 字符串（例如，<i>name1=value1; name2=value2</i>）。</li><br>\n<li>单击“浏览...”以选择一个 <i>cookies.txt</i> 文件（Netscape 格式）。路径将显示在文本字段中。</li></ul>\n这对于访问需要登录的内容很有用。如果填写，文本字段优先。\n如果选中了“使用 Cookie”，但文本字段和浏览的文件都为空，它将尝试从应用程序的目录加载“cookies.txt”。</li>\n</ul>",
    "tour_dialog_step6_title": "⑤ 组织与性能",
    "tour_dialog_step6_content": "组织您的下载并管理性能：\n<ul>\n<li><b>⚙️ 按名称/标题分文件夹：</b>根据“按角色筛选”输入或帖子标题创建子文件夹（如果帖子与您的活动“按角色筛选”输入不匹配，可以使用 <b>Known.txt</b> 列表作为后备）。</li><br>\n<li><b>每篇帖子一个子文件夹：</b>如果“分文件夹”打开，这将在主角色/标题文件夹内为<i>每篇单独的帖子</i>创建一个额外的子文件夹。</li><br>\n<li><b>🚀 使用多线程（线程数）：</b>启用更快的操作。“线程数”输入中的数字表示：\n<ul><li>对于<b>创建者源：</b>要同时处理的帖子数量。每个帖子中的文件都由其工作线程按顺序下载（除非启用了“基于日期”的漫画命名，这会强制使用 1 个帖子工作线程）。</li><br>\n<li>对于<b>单个帖子 URL：</b>要从该单个帖子同时下载的文件数量。</li></ul>\n如果未选中，则使用 1 个线程。高线程数（例如 >40）可能会显示建议。</li><br>\n<li><b>多部分下载切换（日志区域右上角）：</b><br>\n<b>“多部分：[开/关]”</b>按钮允许为单个大文件启用/禁用多段下载。\n<ul><li><b>开：</b>可以加快大文件的下载速度（例如视频），但可能会增加界面的卡顿或在有许多小文件时产生日志垃圾信息。启用时会出现建议。如果多部分下载失败，它会以单流方式重试。</li><br>\n<li><b>关（默认）：</b>文件以单流方式下载。</li></ul>\n如果“仅链接”或“仅存档”模式处于活动状态，此功能将被禁用。</li><br>\n<li><b>📖 漫画/动漫模式（仅限创建者 URL）：</b>专为顺序内容量身定制。\n<ul>\n<li>从<b>最旧到最新</b>下载帖子。</li><br>\n<li>“页面范围”输入被禁用，因为所有帖子都将被获取。</li><br>\n<li>当此模式对创建者源处于活动状态时，日志区域的右上角会出现一个<b>文件名样式切换按钮</b>（例如，“名称：帖子标题”）。单击它以在命名样式之间循环：\n<ul>\n<li><b><i>名称：帖子标题（默认）：</i></b>帖子中的第一个文件以帖子的清理标题命名（例如，“我的第一章.jpg”）。*同一帖子*中的后续文件将尝试保留其原始文件名（例如，“page_02.png”、“bonus_art.jpg”）。如果帖子只有一个文件，则以帖子标题命名。这通常是大多数漫画/动漫的推荐设置。</li><br>\n<li><b><i>名称：原始文件：</i></b>所有文件都尝试保留其原始文件名。可以在样式按钮旁边出现的输入字段中输入可选的前缀（例如，“我的系列_”）。示例：“我的系列_原始文件.jpg”。</li><br>\n<li><b><i>名称：标题+全局编号（帖子标题 + 全局编号）：</i></b>当前下载会话中所有帖子的所有文件都使用帖子的清理标题作为前缀，后跟一个全局计数器，按顺序命名。例如：帖子“第一章”（2 个文件）->“第一章_001.jpg”、“第一章_002.png”。下一个帖子“第二章”（1 个文件）将继续编号 ->“第二章_003.jpg”。为了确保正确的全局编号，此样式的帖子处理多线程被自动禁用。</li><br>\n<li><b><i>名称：基于日期：</i></b>文件根据帖子发布顺序按顺序命名（001.ext、002.ext ...）。可以在样式按钮旁边出现的输入字段中输入可选的前缀（例如，“我的系列_”）。示例：“我的系列_001.jpg”。此样式的帖子处理多线程被自动禁用。</li>\n</ul>\n</li><br>\n<li>为了在使用“名称：帖子标题”、“名称：标题+全局编号”或“名称：基于日期”样式时获得最佳效果，请使用“按角色筛选”字段以及漫画/系列标题进行文件夹组织。</li>\n</ul></li><br>\n<li><b>🎭 Known.txt 用于智能文件夹组织：</b><br>\n<code>Known.txt</code>（在应用程序的目录中）允许在启用“按名称/标题分文件夹”时对自动文件夹组织进行精细控制。\n<ul>\n<li><b>工作原理：</b><code>Known.txt</code> 中的每一行都是一个条目。\n<ul><li>像 <code>我的精彩系列</code> 这样的简单行意味着匹配此内容的内容将进入名为“我的精彩系列”的文件夹。</li><br>\n<li>像 <code>(角色 A, 角色 A, 备用名 A)</code> 这样的分组行意味着匹配“角色 A”、“角色 A”或“备用名 A”的内容将全部进入一个名为“角色 A 角色 A 备用名 A”的文件夹（清理后）。括号中的所有术语都成为该文件夹的别名。</li></ul></li>\n<li><b>智能后备：</b>当“按名称/标题分文件夹”处于活动状态，并且帖子与任何特定的“按角色筛选”输入不匹配时，下载器会查阅 <code>Known.txt</code> 以查找匹配的主名称以创建文件夹。</li><br>\n<li><b>用户友好的管理：</b>通过下面的 UI 列表添加简单（非分组）的名称。对于高级编辑（如创建/修改分组别名），请单击<b>“打开 Known.txt”</b>以在文本编辑器中编辑文件。应用程序会在下次使用或启动时重新加载它。</li>\n</ul>\n</li>\n</ul>",
    "tour_dialog_step7_title": "⑥ 常见错误与故障排除",
    "tour_dialog_step7_content": "有时，下载可能会遇到问题。以下是一些常见问题：\n<ul>\n<li><b>角色输入工具提示：</b><br>\n输入角色名称，以逗号分隔（例如，<i>Tifa, Aerith</i>）。<br>\n将别名分组以获得组合的文件夹名称：<i>(alias1, alias2, alias3)</i> 变为文件夹“alias1 alias2 alias3”。<br>\n组中的所有名称都用作匹配内容的别名。<br><br>\n此输入旁边的“筛选：[类型]”按钮可循环此筛选器的应用方式：<br>\n- 筛选：文件：检查单个文件名。仅下载匹配的文件。<br>\n- 筛选：标题：检查帖子标题。匹配帖子的所有文件都将被下载。<br>\n- 筛选：两者：首先检查帖子标题。如果不匹配，则检查文件名。<br>\n- 筛选：评论（测试版）：首先检查文件名。如果不匹配，则检查帖子评论。<br><br>\n如果启用了“按名称/标题分文件夹”，此筛选器也会影响文件夹命名。</li><br>\n<li><b>502 Bad Gateway / 503 Service Unavailable / 504 Gateway Timeout：</b><br>\n这些通常表示 Kemono/Coomer 存在临时服务器端问题。网站可能超载、停机维护或遇到问题。<br>\n<b>解决方法：</b>稍等片刻（例如，30 分钟到几个小时），然后重试。直接在浏览器中检查网站。</li><br>\n<li><b>连接丢失/连接被拒绝/超时（文件下载期间）：</b><br>\n这可能是由于您的互联网连接、服务器不稳定或服务器断开大文件连接所致。<br>\n<b>解决方法：</b>检查您的互联网。如果“线程数”很高，请尝试减少它。应用程序可能会在会话结束时提示重试某些失败的文件。</li><br>\n<li><b>IncompleteRead 错误：</b><br>\n服务器发送的数据少于预期。通常是暂时的网络故障或服务器问题。<br>\n<b>解决方法：</b>应用程序通常会将这些文件标记为在下载会话结束时重试。</li><br>\n<li><b>403 Forbidden / 401 Unauthorized（对于公共帖子不太常见）：</b><br>\n您可能没有访问内容的权限。对于某些付费或私人内容，使用“使用 Cookie”选项以及来自浏览器会话的有效 cookie 可能会有所帮助。请确保您的 cookie 是最新的。</li><br>\n<li><b>404 Not Found：</b><br>\n帖子或文件 URL 不正确，或者内容已从网站上删除。请仔细检查 URL。</li><br>\n<li><b>“未找到帖子”/“未找到目标帖子”：</b><br>\n确保 URL 正确，并且创建者/帖子存在。如果使用页面范围，请确保它们对创建者有效。对于非常新的帖子，API 中可能会有轻微延迟。</li><br>\n<li><b>普遍缓慢/应用程序“（无响应）”：</b><br>\n如第 1 步所述，如果应用程序在启动后似乎挂起，尤其是在处理大型创建者源或使用许多线程时，请给它一些时间。它很可能正在后台处理数据。如果这种情况频繁发生，减少线程数有时可以提高响应能力。</li>\n</ul>",
    "tour_dialog_step8_title": "⑦ 日志与最终控件",
    "tour_dialog_step8_content": "监控与控件：\n<ul>\n<li><b>📜 进度日志/提取的链接日志：</b>显示详细的下载消息。如果“🔗 仅链接”模式处于活动状态，此区域将显示提取的链接。</li><br>\n<li><b>在日志中显示外部链接：</b>如果选中，主日志下方会出现一个辅助日志面板，以显示在帖子描述中找到的任何外部链接。<i>（如果“🔗 仅链接”或“📦 仅存档”模式处于活动状态，则禁用）。</i></li><br>\n<li><b>日志视图切换（👁️ / 🙈 按钮）：</b><br>\n此按钮（日志区域右上角）可切换主日志视图：\n<ul><li><b>👁️ 进度日志（默认）：</b>显示所有下载活动、错误和摘要。</li><br>\n<li><b>🙈 错过的角色日志：</b>显示由于您的“按角色筛选”设置而跳过的帖子标题中的关键词列表。用于识别您可能无意中错过的内容。</li></ul></li><br>\n<li><b>🔄 重置：</b>清除所有输入字段、日志，并将临时设置重置为默认值。仅在没有下载活动时才能使用。</li><br>\n<li><b>⬇️ 开始下载/🔗 提取链接/⏸️ 暂停/❌ 取消：</b>这些按钮控制过程。“取消并重置界面”会停止当前操作并执行软界面重置，保留您的 URL 和目录输入。“暂停/继续”允许临时停止和继续。</li><br>\n<li>如果某些文件因可恢复的错误（如“IncompleteRead”）而失败，您可能会在会话结束时被提示重试它们。</li>\n</ul>\n<br>一切就绪！单击<b>“完成”</b>关闭导览并开始使用下载器。",
    "help_guide_dialog_title": "Kemono Downloader - 功能指南",
    "help_guide_github_tooltip": "访问项目的 GitHub 页面（在浏览器中打开）",
    "help_guide_instagram_tooltip": "访问我们的 Instagram 页面（在浏览器中打开）",
    "help_guide_discord_tooltip": "访问我们的 Discord 社区（在浏览器中打开）",
    "help_guide_step1_title": "① 简介与主要输入",
    "help_guide_step1_content": "<html><head/><body>\n<p>本指南概述了 Kemono Downloader 的功能、字段和按钮。</p>\n<h3>主要输入区（左上角）</h3>\n<ul>\n<li><b>🔗 Kemono 创建者/帖子 URL：</b>\n<ul>\n<li>输入创建者页面的完整网址（例如，<i>https://kemono.su/patreon/user/12345</i>）或特定帖子（例如，<i>.../post/98765</i>）。</li>\n<li>支持 Kemono (kemono.su, kemono.party) 和 Coomer (coomer.su, coomer.party) 的 URL。</li>\n</ul>\n</li>\n<li><b>页面范围（开始到结束）：</b>\n<ul>\n<li>对于创建者 URL：指定要获取的页面范围（例如，第 2 到 5 页）。留空以获取所有页面。</li>\n<li>对于单个帖子 URL 或当<b>漫画/动漫模式</b>处于活动状态时禁用。</li>\n</ul>\n</li>\n<li><b>📁 下载位置：</b>\n<ul>\n<li>单击<b>“浏览...”</b>以选择计算机上的一个主文件夹，所有下载的文件都将保存在该文件夹中。</li>\n<li>除非您使用<b>“🔗 仅链接”</b>模式，否则此字段是必需的。</li>\n</ul>\n</li>\n<li><b>🎨 创建者选择按钮（URL 输入旁边）：</b>\n<ul>\n<li>单击调色板图标（🎨）以打开“创建者选择”对话框。</li>\n<li>此对话框从您的 <code>creators.json</code> 文件（应位于应用程序的目录中）加载创建者。</li>\n<li><b>对话框内部：</b>\n<ul>\n<li><b>搜索栏：</b>键入以按名称或服务筛选创建者列表。</li>\n<li><b>创建者列表：</b>显示来自您的 <code>creators.json</code> 的创建者。您已“收藏”的创建者（在 JSON 数据中）显示在顶部。</li>\n<li><b>复选框：</b>通过选中其名称旁边的框来选择一个或多个创建者。</li>\n<li><b>“范围”按钮（例如，“范围：角色”）：</b>此按钮在从此弹出窗口启动下载时切换下载组织：\n<ul><li><i>范围：角色：</i>下载将直接组织到您主“下载位置”中以角色命名的文件夹中。来自不同创建者的同一角色的艺术作品将被分组在一起。</li>\n<li><i>范围：创建者：</i>下载将首先在您的主“下载位置”内创建一个以创建者命名的文件夹。然后，以角色命名的子文件夹将创建在每个创建者的文件夹内。</li></ul>\n</li>\n<li><b>“添加所选”按钮：</b>单击此按钮将获取所有选定创建者的名称，并将其以逗号分隔的方式添加到主“🔗 Kemono 创建者/帖子 URL”输入字段中。然后对话框将关闭。</li>\n</ul>\n</li>\n<li>此功能提供了一种快速填充多个创建者 URL 字段的方法，而无需手动键入或粘贴每个 URL。</li>\n</ul>\n</li>\n</ul></body></html>",
    "help_guide_step2_title": "② 筛选下载",
    "help_guide_step2_content": "<html><head/><body>\n<h3>筛选下载（左侧面板）</h3>\n<ul>\n<li><b>🎯 按角色筛选：</b>\n<ul>\n<li>输入名称，以逗号分隔（例如，<code>Tifa, Aerith</code>）。</li>\n<li><b>用于共享文件夹的分组别名（单独的 Known.txt 条目）：</b><code>(Vivi, Ulti, Uta)</code>。\n<ul><li>匹配“Vivi”、“Ulti”或“Uta”的内容将进入名为“Vivi Ulti Uta”的共享文件夹（清理后）。</li>\n<li>如果这些名称是新的，系统将提示将“Vivi”、“Ulti”和“Uta”作为<i>单独的单个条目</i>添加到 <code>Known.txt</code>。</li>\n</ul>\n</li>\n<li><b>用于共享文件夹的分组别名（单个 Known.txt 条目）：</b><code>(Yuffie, Sonon)~</code>（注意波浪号 <code>~</code>）。\n<ul><li>匹配“Yuffie”或“Sonon”的内容将进入名为“Yuffie Sonon”的共享文件夹。</li>\n<li>如果是新的，“Yuffie Sonon”（别名为 Yuffie, Sonon）将被提示作为<i>单个组条目</i>添加到 <code>Known.txt</code>。</li>\n</ul>\n</li>\n<li>如果启用了“按名称/标题分文件夹”，此筛选器会影响文件夹命名。</li>\n</ul>\n</li>\n<li><b>筛选：[类型] 按钮（角色筛选范围）：</b>循环“按角色筛选”的应用方式：\n<ul>\n<li><code>筛选：文件</code>：检查单个文件名。如果任何文件匹配，则保留帖子；仅下载匹配的文件。文件夹命名使用匹配文件名中的角色。</li>\n<li><code>筛选：标题</code>：检查帖子标题。匹配帖子的所有文件都将被下载。文件夹命名使用匹配帖子标题中的角色。</li>\n<li><code>筛选：两者</code>：首先检查帖子标题。如果匹配，则下载所有文件。如果不匹配，则检查文件名，并且仅下载匹配的文件。文件夹命名优先考虑标题匹配，然后是文件匹配。</li>\n<li><code>筛选：评论（测试版）</code>：首先检查文件名。如果文件匹配，则下载帖子中的所有文件。如果没有文件匹配，则检查帖子评论。如果评论匹配，则下载所有文件。（使用更多的 API 请求）。文件夹命名优先考虑文件匹配，然后是评论匹配。</li>\n</ul>\n</li>\n<li><b>🗄️ 自定义文件夹名称（仅限单个帖子）：</b>\n<ul>\n<li>仅在下载单个特定帖子 URL 并且启用了“按名称/标题分文件夹”时可见和可用。</li>\n<li>允许您为该单个帖子的下载文件夹指定自定义名称。</li>\n</ul>\n</li>\n<li><b>🚫 使用关键词跳过：</b>\n<ul><li>输入词语，以逗号分隔（例如，<code>WIP, sketch, preview</code>）以跳过某些内容。</li></ul>\n</li>\n<li><b>范围：[类型] 按钮（跳过词语范围）：</b>循环“使用关键词跳过”的应用方式：\n<ul>\n<li><code>范围：文件</code>：如果文件名包含任何这些词语，则跳过单个文件。</li>\n<li><code>范围：帖子</code>：如果帖子标题包含任何这些词语，则跳过整个帖子。</li>\n<li><code>范围：两者</code>：同时应用两者（帖子标题优先，然后是单个文件）。</li>\n</ul>\n</li>\n<li><b>✂️ 从名称中删除词语：</b>\n<ul><li>输入词语，以逗号分隔（例如，<code>patreon, [HD]</code>），以从下载的文件名中删除（不区分大小写）。</li></ul>\n</li>\n<li><b>筛选文件（单选按钮）：</b>选择要下载的内容：\n<ul>\n<li><code>全部</code>：下载找到的所有文件类型。</li>\n<li><code>图片/GIF</code>：仅常见的图像格式（JPG、PNG、GIF、WEBP 等）和 GIF。</li>\n<li><code>视频</code>：仅常见的视频格式（MP4、MKV、WEBM、MOV 等）。</li>\n<li><code>📦 仅存档</code>：专门下载 <b>.zip</b> 和 <b>.rar</b> 文件。选择此选项后，“跳过 .zip”和“跳过 .rar”复选框将自动禁用并取消选中。“显示外部链接”也将被禁用。</li>\n<li><code>🎧 仅音频</code>：仅下载常见的音频格式（MP3、WAV、FLAC、M4A、OGG 等）。其他特定于文件的选项的行为与“图片”或“视频”模式相同。</li>\n<li><code>🔗 仅链接</code>：从帖子描述中提取并显示外部链接，而不是下载文件。与下载相关的选项和“显示外部链接”将被禁用。主下载按钮变为“🔗 提取链接”。</li>\n</ul>\n</li>\n</ul></body></html>",
    "help_guide_step3_title": "③ 下载选项与设置",
    "help_guide_step3_content": "<html><head/><body>\n<h3>下载选项与设置（左侧面板）</h3>\n<ul>\n<li><b>跳过 .zip / 跳过 .rar：</b>用于避免下载这些存档文件类型的复选框。（如果选择了“📦 仅存档”筛选模式，则禁用和忽略）。</li>\n<li><b>仅下载缩略图：</b>下载小预览图像，而不是全尺寸文件（如果可用）。</li>\n<li><b>压缩大图像（为 WebP）：</b>如果安装了“Pillow”（PIL）库，大于 1.5MB 的图像如果 WebP 版本明显更小，将被转换为 WebP 格式。</li>\n<li><b>⚙️ 高级设置：</b>\n<ul>\n<li><b>按名称/标题分文件夹：</b>根据“按角色筛选”输入或帖子标题创建子文件夹。可以使用 <b>Known.txt</b> 列表作为文件夹名称的后备。</li></ul></li></ul></body></html>",
    "help_guide_step4_title": "④ 高级设置（第 1 部分）",
    "help_guide_step4_content": "<html><head/><body><h3>⚙️ 高级设置（续）</h3><ul><ul>\n<li><b>每篇帖子一个子文件夹：</b>如果“分文件夹”打开，这将在主角色/标题文件夹内为<i>每篇单独的帖子</i>创建一个额外的子文件夹。</li>\n<li><b>使用 Cookie：</b>选中此项以使用 cookie 进行请求。\n<ul>\n<li><b>文本字段：</b>直接输入 cookie 字符串（例如，<code>name1=value1; name2=value2</code>）。</li>\n<li><b>浏览...：</b>选择一个 <code>cookies.txt</code> 文件（Netscape 格式）。路径将显示在文本字段中。</li>\n<li><b>优先级：</b>文本字段（如果填写）优先于浏览的文件。如果选中了“使用 Cookie”，但两者都为空，它将尝试从应用程序的目录加载 <code>cookies.txt</code>。</li>\n</ul>\n</li>\n<li><b>使用多线程和线程数输入：</b>\n<ul>\n<li>启用更快的操作。“线程数”输入中的数字表示：\n<ul>\n<li>对于<b>创建者源：</b>要同时处理的帖子数量。每个帖子中的文件都由其工作线程按顺序下载（除非启用了“基于日期”的漫画命名，这会强制使用 1 个帖子工作线程）。</li>\n<li>对于<b>单个帖子 URL：</b>要从该单个帖子同时下载的文件数量。</li>\n</ul>\n</li>\n<li>如果未选中，则使用 1 个线程。高线程数（例如 >40）可能会显示建议。</li>\n</ul>\n</li></ul></ul></body></html>",
    "help_guide_step5_title": "⑤ 高级设置（第 2 部分）与操作",
    "help_guide_step5_content": "<html><head/><body><h3>⚙️ 高级设置（续）</h3><ul><ul>\n<li><b>在日志中显示外部链接：</b>如果选中，主日志下方会出现一个辅助日志面板，以显示在帖子描述中找到的任何外部链接。（如果“🔗 仅链接”或“📦 仅存档”模式处于活动状态，则禁用）。</li>\n<li><b>📖 漫画/动漫模式（仅限创建者 URL）：</b>专为顺序内容量身定制。\n<ul>\n<li>从<b>最旧到最新</b>下载帖子。</li>\n<li>“页面范围”输入被禁用，因为所有帖子都将被获取。</li>\n<li>当此模式对创建者源处于活动状态时，日志区域的右上角会出现一个<b>文件名样式切换按钮</b>（例如，“名称：帖子标题”）。单击它以在命名样式之间循环：\n<ul>\n<li><code>名称：帖子标题（默认）</code>：帖子中的第一个文件以帖子的清理标题命名（例如，“我的第一章.jpg”）。*同一帖子*中的后续文件将尝试保留其原始文件名（例如，“page_02.png”、“bonus_art.jpg”）。如果帖子只有一个文件，则以帖子标题命名。这通常是大多数漫画/动漫的推荐设置。</li>\n<li><code>名称：原始文件</code>：所有文件都尝试保留其原始文件名。</li>\n<li><code>名称：原始文件</code>：所有文件都尝试保留其原始文件名。当此样式处于活动状态时，样式按钮旁边会出现一个用于<b>可选文件名前缀</b>的输入字段（例如，“我的系列_”）。示例：“我的系列_原始文件.jpg”。</li>\n<li><code>名称：标题+全局编号（帖子标题 + 全局编号）</code>：当前下载会话中所有帖子的所有文件都使用帖子的清理标题作为前缀，后跟一个全局计数器，按顺序命名。示例：帖子“第一章”（2 个文件）->“第一章 001.jpg”、“第一章 002.png”。下一个帖子“第二章”（1 个文件）->“第二章 003.jpg”。为了确保正确的全局编号，此样式的帖子处理多线程被自动禁用。</li>\n<li><code>名称：基于日期</code>：文件根据帖子发布顺序按顺序命名（001.ext、002.ext ...）。当此样式处于活动状态时，样式按钮旁边会出现一个用于<b>可选文件名前缀</b>的输入字段（例如，“我的系列_”）。示例：“我的系列_001.jpg”。此样式的帖子处理多线程被自动禁用。</li>\n</ul>\n</li>\n<li>为了在使用“名称：帖子标题”、“名称：标题+全局编号”或“名称：基于日期”样式时获得最佳效果，请使用“按角色筛选”字段以及漫画/系列标题进行文件夹组织。</li>\n</ul>\n</li>\n</ul></li></ul>\n<h3>主要操作按钮（左侧面板）</h3>\n<ul>\n<li><b>⬇️ 开始下载/🔗 提取链接：</b>此按钮的文本和功能根据“筛选文件”单选按钮的选择而变化。它启动主要操作。</li>\n<li><b>⏸️ 暂停下载/▶️ 继续下载：</b>允许您临时停止当前下载/提取过程并稍后继续。暂停时可以更改某些界面设置。</li>\n<li><b>❌ 取消并重置界面：</b>停止当前操作并执行软界面重置。您的 URL 和下载目录输入将被保留，但其他设置和日志将被清除。</li>\n</ul></body></html>",
    "help_guide_step6_title": "⑥ 已知系列/角色列表",
    "help_guide_step6_content": "<html><head/><body>\n<h3>已知系列/角色列表管理（左下角）</h3>\n<p>本节帮助管理 <code>Known.txt</code> 文件，该文件用于在启用“按名称/标题分文件夹”时进行智能文件夹组织，尤其是在帖子与您的活动“按角色筛选”输入不匹配时作为后备。</p>\n<ul>\n<li><b>打开 Known.txt：</b>在您的默认文本编辑器中打开 <code>Known.txt</code> 文件（位于应用程序的目录中），以进行高级编辑（如创建复杂的分组别名）。</li>\n<li><b>搜索角色...：</b>筛选下面显示的已知名称列表。</li>\n<li><b>列表小部件：</b>显示来自您的 <code>Known.txt</code> 的主名称。在此处选择条目以将其删除。</li>\n<li><b>添加新的系列/角色名称（输入字段）：</b>输入要添加的名称或组。\n<ul>\n<li><b>简单名称：</b>例如，<code>我的精彩系列</code>。作为单个条目添加。</li>\n<li><b>用于单独的 Known.txt 条目的组：</b>例如，<code>(Vivi, Ulti, Uta)</code>。将“Vivi”、“Ulti”和“Uta”作为三个单独的单个条目添加到 <code>Known.txt</code>。</li>\n<li><b>用于共享文件夹和单个 Known.txt 条目的组（波浪号 <code>~</code>）：</b>例如，<code>(角色 A, 角色 A)~</code>。在 <code>Known.txt</code> 中添加一个名为“角色 A 角色 A”的条目。“角色 A”和“角色 A”成为此单个文件夹/条目的别名。</li>\n</ul>\n</li>\n<li><b>➕ 添加按钮：</b>将上面输入字段中的名称/组添加到列表和 <code>Known.txt</code>。</li>\n<li><b>⤵️ 添加到筛选器按钮：</b>\n<ul>\n<li>位于“已知系列/角色”列表的“➕ 添加”按钮旁边。</li>\n<li>单击此按钮将打开一个弹出窗口，其中显示来自您的 <code>Known.txt</code> 文件的所有名称，每个名称都有一个复选框。</li>\n<li>该弹出窗口包括一个搜索栏，可快速筛选名称列表。</li>\n<li>您可以使用复选框选择一个或多个名称。</li>\n<li>单击“添加所选”以将所选名称插入主窗口中的“按角色筛选”输入字段。</li>\n<li>如果从 <code>Known.txt</code> 中选择的名称最初是一个组（例如，在 Known.txt 中定义为 <code>(Boa, Hancock)</code>），它将被添加为 <code>(Boa, Hancock)~</code> 到筛选字段。简单名称按原样添加。</li>\n<li>为了方便起见，弹出窗口中提供了“全选”和“取消全选”按钮。</li>\n<li>单击“取消”以关闭弹出窗口而不进行任何更改。</li>\n</ul>\n</li>\n<li><b>🗑️ 删除所选按钮：</b>从列表和 <code>Known.txt</code> 中删除所选的名称。</li>\n<li><b>❓ 按钮（就是这个！）：</b>显示此综合帮助指南。</li>\n</ul></body></html>",
    "help_guide_step7_title": "⑦ 日志区与控件",
    "help_guide_step7_content": "<html><head/><body>\n<h3>日志区与控件（右侧面板）</h3>\n<ul>\n<li><b>📜 进度日志/提取的链接日志（标签）：</b>主日志区的标题；如果“🔗 仅链接”模式处于活动状态，则会更改。</li>\n<li><b>搜索链接... / 🔍 按钮（链接搜索）：</b>\n<ul><li>仅在“🔗 仅链接”模式处于活动状态时可见。允许按文本、URL 或平台实时筛选主日志中显示的提取链接。</li></ul>\n</li>\n<li><b>名称：[样式] 按钮（漫画文件名样式）：</b>\n<ul><li>仅在<b>漫画/动漫模式</b>对创建者源处于活动状态且不在“仅链接”或“仅存档”模式时可见。</li>\n<li>在文件名样式之间循环：<code>帖子标题</code>、<code>原始文件</code>、<code>基于日期</code>。（有关详细信息，请参阅漫画/动漫模式部分）。</li>\n<li>当“原始文件”或“基于日期”样式处于活动状态时，此按钮旁边会出现一个用于<b>可选文件名前缀</b>的输入字段。</li>\n</ul>\n</li>\n<li><b>多部分：[开/关] 按钮：</b>\n<ul><li>切换单个大文件的多段下载。\n<ul><li><b>开：</b>可以加快大文件的下载速度（例如视频），但可能会增加界面的卡顿或在有许多小文件时产生日志垃圾信息。启用时会出现建议。如果多部分下载失败，它会以单流方式重试。</li>\n<li><b>关（默认）：</b>文件以单流方式下载。</li>\n</ul>\n<li>如果“🔗 仅链接”或“📦 仅存档”模式处于活动状态，则禁用。</li>\n</ul>\n</li>\n<li><b>👁️ / 🙈 按钮（日志视图切换）：</b>切换主日志视图：\n<ul>\n<li><b>👁️ 进度日志（默认）：</b>显示所有下载活动、错误和摘要。</li>\n<li><b>🙈 错过的角色日志：</b>显示由于您的“按角色筛选”设置而跳过的帖子标题/内容中的关键词列表。用于识别您可能无意中错过的内容。</li>\n</ul>\n</li>\n<li><b>🔄 重置按钮：</b>清除所有输入字段、日志，并将临时设置重置为默认值。仅在没有下载活动时才能使用。</li>\n<li><b>主日志输出（文本区）：</b>显示详细的进度消息、错误和摘要。如果“🔗 仅链接”模式处于活动状态，此区域将显示提取的链接。</li>\n<li><b>错过的角色日志输出（文本区）：</b>（可通过 👁️ / 🙈 切换查看）显示由于角色筛选器而跳过的帖子/文件。</li>\n<li><b>外部日志输出（文本区）：</b>如果选中“在日志中显示外部链接”，则显示在主日志下方。显示在帖子描述中找到的外部链接。</li>\n<li><b>导出链接按钮：</b>\n<ul><li>仅在“🔗 仅链接”模式处于活动状态且已提取链接时可见和启用。</li>\n<li>允许您将所有提取的链接保存到 <code>.txt</code> 文件。</li>\n</ul>\n</li>\n<li><b>进度：[状态] 标签：</b>显示下载或链接提取过程的总体进度（例如，已处理的帖子）。</li>\n<li><b>文件进度标签：</b>显示单个文件下载的进度，包括速度和大小，或多部分下载状态。</li>\n</ul></body></html>",
    "help_guide_step8_title": "⑧ 收藏模式与未来功能",
    "help_guide_step8_content": "<html><head/><body>\n<h3>收藏模式（从您的 Kemono.su 收藏中下载）</h3>\n<p>此模式允许您直接从您在 Kemono.su 上收藏的艺术家那里下载内容。</p>\n<ul>\n<li><b>⭐ 如何启用：</b>\n<ul>\n<li>选中位于“🔗 仅链接”单选按钮旁边的<b>“⭐ 收藏模式”</b>复选框。</li>\n</ul>\n</li>\n<li><b>收藏模式下的界面更改：</b>\n<ul>\n<li>“🔗 Kemono 创建者/帖子 URL”输入区域被一条消息替换，指示收藏模式已激活。</li>\n<li>标准的“开始下载”、“暂停”、“取消”按钮被替换为：\n<ul>\n<li><b>“🖼️ 收藏的艺术家”</b>按钮</li>\n<li><b>“📄 收藏的帖子”</b>按钮</li>\n</ul>\n</li>\n<li>“🍪 使用 Cookie”选项被自动启用并锁定，因为获取您的收藏需要 cookie。</li>\n</ul>\n</li>\n<li><b>🖼️ 收藏的艺术家按钮：</b>\n<ul>\n<li>单击此按钮将打开一个对话框，其中列出了您在 Kemono.su 上收藏的所有艺术家。</li>\n<li>您可以从此列表中选择一个或多个艺术家以下载其内容。</li>\n</ul>\n</li>\n<li><b>📄 收藏的帖子按钮（未来功能）：</b>\n<ul>\n<li>下载特定的收藏<i>帖子</i>（尤其是在它们是系列的一部分时，以类似漫画的顺序）是目前正在开发的功能。</li>\n<li>处理收藏帖子的最佳方式，特别是对于像漫画这样的顺序阅读，仍在探索中。</li>\n<li>如果您对如何下载和组织收藏帖子有具体的想法或用例（例如，从收藏中“漫画风格”），请考虑在项目的 GitHub 页面上提出问题或加入讨论。您的意见非常宝贵！</li>\n</ul>\n</li>\n<li><b>收藏下载范围（按钮）：</b>\n<ul>\n<li>此按钮（在“收藏的帖子”旁边）控制从所选收藏艺术家那里下载内容的位置：\n<ul>\n<li><b><i>范围：所选位置：</i></b>所有选定的艺术家都下载到您在界面中设置的主“下载位置”。筛选器全局应用于所有内容。</li>\n<li><b><i>范围：艺术家文件夹：</i></b>对于每个选定的艺术家，将在您的主“下载位置”内自动创建一个子文件夹（以艺术家命名）。该艺术家的内容将进入其特定的子文件夹。筛选器在每个艺术家的专用文件夹内应用。</li>\n</ul>\n</li>\n</ul>\n</li>\n<li><b>收藏模式下的筛选器：</b>\n<ul>\n<li>您在界面中设置的“🎯 按角色筛选”、“🚫 使用关键词跳过”和“筛选文件”选项仍将适用于从您选定的收藏艺术家那里下载的内容。</li>\n</ul>\n</li>\n</ul></body></html>",
    "help_guide_step9_title": "⑨ 关键文件与导览",
    "help_guide_step9_content": "<html><head/><body>\n<h3>应用程序使用的关键文件</h3>\n<ul>\n<li><b><code>Known.txt</code>：</b>\n<ul>\n<li>位于应用程序的目录中（<code>.exe</code> 或 <code>main.py</code> 所在的位置）。</li>\n<li>在启用“按名称/标题分文件夹”时，存储您已知的系列、角色或系列标题列表，用于自动文件夹组织。</li>\n<li><b>格式：</b>\n<ul>\n<li>每一行都是一个条目。</li>\n<li><b>简单名称：</b>例如，<code>我的精彩系列</code>。匹配此内容的内容将进入名为“我的精彩系列”的文件夹。</li>\n<li><b>分组别名：</b>例如，<code>(角色 A, 角色 A, 备用名 A)</code>。匹配“角色 A”、“角色 A”或“备用名 A”的内容将全部进入一个名为“角色 A 角色 A 备用名 A”的文件夹（清理后）。括号中的所有术语都成为该文件夹的别名。</li>\n</ul>\n</li>\n<li><b>用法：</b>如果帖子与您的活动“按角色筛选”输入不匹配，则用作文件夹命名的后备。您可以通过界面管理简单的条目，或直接编辑文件以获取复杂的别名。应用程序会在启动或下次使用时重新加载它。</li>\n</ul>\n</li>\n<li><b><code>cookies.txt</code>（可选）：</b>\n<ul>\n<li>如果您使用“使用 Cookie”功能并且不提供直接的 cookie 字符串或浏览到特定文件，应用程序将在其目录中查找名为 <code>cookies.txt</code> 的文件。</li>\n<li><b>格式：</b>必须是 Netscape cookie 文件格式。</li>\n<li><b>用法：</b>允许下载器使用您的浏览器的登录会话来访问可能需要在 Kemono/Coomer 上登录的内容。</li>\n</ul>\n</li>\n</ul>\n<h3>首次用户导览</h3>\n<ul>\n<li>在首次启动时（或如果重置），会出现一个欢迎导览对话框，引导您了解主要功能。您可以跳过它或选择“不再显示此导览”。</li>\n</ul>\n<p><em>许多界面元素还具有工具提示，当您将鼠标悬停在它们上面时会出现，提供快速提示。</em></p>\n</body></html>"
})

translations["ru"] = {}
translations["ru"].update({
    "settings_dialog_title": "Настройки",
    "language_label": "Язык:",
    "lang_english": "Английский (English)",
    "lang_japanese": "Японский (日本語)",
    "theme_toggle_light": "Переключиться на светлый режим",
    "theme_toggle_dark": "Переключиться на темный режим",
    "theme_tooltip_light": "Изменить внешний вид приложения на светлый.",
    "theme_tooltip_dark": "Изменить внешний вид приложения на темный.",
    "ok_button": "ОК",
    "appearance_group_title": "Внешний вид",
    "language_group_title": "Языковые настройки",
    "creator_post_url_label": "🔗 URL автора/поста Kemono:",
    "download_location_label": "📁 Место для скачивания:",
    "filter_by_character_label": "🎯 Фильтровать по персонажу(ам) (через запятую):",
    "skip_with_words_label": "🚫 Пропускать со словами (через запятую):",
    "remove_words_from_name_label": "✂️ Удалить слова из названия:",
    "filter_all_radio": "Все",
    "filter_images_radio": "Изображения/GIF",
    "filter_videos_radio": "Видео",
    "filter_archives_radio": "📦 Только архивы",
    "filter_links_radio": "🔗 Только ссылки",
    "filter_audio_radio": "🎧 Только аудио",
    "favorite_mode_checkbox_label": "⭐ Режим избранного",
    "browse_button_text": "Обзор...",
    "char_filter_scope_files_text": "Фильтр: Файлы",
    "char_filter_scope_files_tooltip": "Текущая область: Файлы\n\nФильтрует отдельные файлы по имени. Пост сохраняется, если совпадает хотя бы один файл.\nСкачиваются только совпадающие файлы из этого поста.\nПример: Фильтр 'Tifa'. Файл 'Tifa_artwork.jpg' совпадает и скачивается.\nИменование папок: Используется персонаж из совпадающего имени файла.\n\nНажмите для переключения на: Оба",
    "char_filter_scope_title_text": "Фильтр: Заголовок",
    "char_filter_scope_title_tooltip": "Текущая область: Заголовок\n\nФильтрует целые посты по их заголовку. Скачиваются все файлы из совпадающего поста.\nПример: Фильтр 'Aerith'. Пост с заголовком 'Сад Аэрис' совпадает; все его файлы скачиваются.\nИменование папок: Используется персонаж из совпадающего заголовка поста.\n\nНажмите для переключения на: Файлы",
    "char_filter_scope_both_text": "Фильтр: Оба",
    "char_filter_scope_both_tooltip": "Текущая область: Оба (сначала заголовок, затем файлы)\n\n1. Проверяет заголовок поста: Если совпадает, скачиваются все файлы из поста.\n2. Если заголовок не совпадает, проверяет имена файлов: Если совпадает какой-либо файл, скачивается только этот файл.\nПример: Фильтр 'Cloud'.\n - Пост 'Cloud Strife' (совпадение заголовка) -> скачиваются все файлы.\n - Пост 'Погоня на мотоцикле' с 'Cloud_fenrir.jpg' (совпадение файла) -> скачивается только 'Cloud_fenrir.jpg'.\nИменование папок: Приоритет отдается совпадению заголовка, затем совпадению файла.\n\nНажмите для переключения на: Комментарии",
    "char_filter_scope_comments_text": "Фильтр: Комментарии (бета)",
    "char_filter_scope_comments_tooltip": "Текущая область: Комментарии (бета - сначала файлы, затем комментарии в качестве запасного варианта)\n\n1. Проверяет имена файлов: Если какой-либо файл в посте совпадает с фильтром, скачивается весь пост. Комментарии НЕ проверяются на этот фильтрующий термин.\n2. Если файлы не совпадают, ТОГДА проверяет комментарии к посту: Если комментарий совпадает, скачивается весь пост.\nПример: Фильтр 'Barret'.\n - Пост А: Файлы 'Barret_gunarm.jpg', 'other.png'. Файл 'Barret_gunarm.jpg' совпадает. Все файлы из поста А скачиваются. Комментарии не проверяются на 'Barret'.\n - Пост Б: Файлы 'dyne.jpg', 'weapon.gif'. Комментарии: '...рисунок Баррета Уоллеса...'. Нет совпадений по файлам для 'Barret'. Комментарий совпадает. Все файлы из поста Б скачиваются.\nИменование папок: Приоритет отдается персонажу из совпадения файла, затем из совпадения комментария.\n\nНажмите для переключения на: Заголовок",
    "char_filter_scope_unknown_text": "Фильтр: Неизвестно",
    "char_filter_scope_unknown_tooltip": "Текущая область: Неизвестно\n\nОбласть фильтрации персонажей находится в неизвестном состоянии. Пожалуйста, переключите или сбросьте.\n\nНажмите для переключения на: Заголовок",
    "skip_words_input_tooltip": "Введите слова через запятую, чтобы пропустить скачивание определенного контента (например, WIP, sketch, preview).\n\nКнопка 'Область: [Тип]' рядом с этим полем ввода циклически изменяет способ применения этого фильтра:\n- Область: Файлы: Пропускает отдельные файлы, если их имена содержат какие-либо из этих слов.\n- Область: Посты: Пропускает целые посты, если их заголовки содержат какие-либо из этих слов.\n- Область: Оба: Применяет оба (сначала заголовок поста, затем отдельные файлы, если заголовок поста подходит).",
    "remove_words_input_tooltip": "Введите слова через запятую для удаления из имен скачиваемых файлов (без учета регистра).\nПолезно для очистки распространенных префиксов/суффиксов.\nПример: patreon, kemono, [HD], _final",
    "skip_scope_files_text": "Область: Файлы",
    "skip_scope_files_tooltip": "Текущая область пропуска: Файлы\n\nПропускает отдельные файлы, если их имена содержат какие-либо из 'Слов для пропуска'.\nПример: Слова для пропуска \"WIP, sketch\".\n- Файл \"art_WIP.jpg\" -> ПРОПУЩЕН.\n- Файл \"final_art.png\" -> СКАЧАН (если выполнены другие условия).\n\nПост по-прежнему обрабатывается на наличие других не пропущенных файлов.\nНажмите для переключения на: Оба",
    "skip_scope_posts_text": "Область: Посты",
    "skip_scope_posts_tooltip": "Текущая область пропуска: Посты\n\nПропускает целые посты, если их заголовки содержат какие-либо из 'Слов для пропуска'.\nВсе файлы из пропущенного поста игнорируются.\nПример: Слова для пропуска \"preview, announcement\".\n- Пост \"Захватывающее объявление!\" -> ПРОПУЩЕН.\n- Пост \"Готовое произведение искусства\" -> ОБРАБОТАН (если выполнены другие условия).\n\nНажмите для переключения на: Файлы",
    "skip_scope_both_text": "Область: Оба",
    "skip_scope_both_tooltip": "Текущая область пропуска: Оба (сначала посты, затем файлы)\n\n1. Проверяет заголовок поста: Если заголовок содержит слово для пропуска, весь пост ПРОПУСКАЕТСЯ.\n2. Если заголовок поста в порядке, проверяет имена отдельных файлов: Если имя файла содержит слово для пропуска, пропускается только этот файл.\nПример: Слова для пропуска \"WIP, sketch\".\n- Пост \"Эскизы и WIPs\" (совпадение заголовка) -> ВЕСЬ ПОСТ ПРОПУЩЕН.\n- Пост \"Обновление артов\" (заголовок в порядке) с файлами:\n  - \"character_WIP.jpg\" (совпадение файла) -> ПРОПУЩЕН.\n  - \"final_scene.png\" (файл в порядке) -> СКАЧАН.\n\nНажмите для переключения на: Посты",
    "skip_scope_unknown_text": "Область: Неизвестно",
    "skip_scope_unknown_tooltip": "Текущая область пропуска: Неизвестно\n\nОбласть слов для пропуска находится в неизвестном состоянии. Пожалуйста, переключите или сбросьте.\n\nНажмите для переключения на: Посты",
    "language_change_title": "Язык изменен",
    "language_change_message": "Язык был изменен. Для полного вступления изменений в силу требуется перезагрузка.",
    "language_change_informative": "Хотите перезапустить приложение сейчас?",
    "restart_now_button": "Перезапустить сейчас",
    "skip_zip_checkbox_label": "Пропускать .zip",
    "skip_rar_checkbox_label": "Пропускать .rar",
    "download_thumbnails_checkbox_label": "Скачивать только миниатюры",
    "scan_content_images_checkbox_label": "Сканировать контент на наличие изображений",
    "compress_images_checkbox_label": "Сжимать в WebP",
    "separate_folders_checkbox_label": "Раздельные папки по имени/заголовку",
    "subfolder_per_post_checkbox_label": "Подпапка для каждого поста",
    "use_cookie_checkbox_label": "Использовать cookie",
    "use_multithreading_checkbox_base_label": "Использовать многопоточность",
    "show_external_links_checkbox_label": "Показывать внешние ссылки в журнале",
    "manga_comic_mode_checkbox_label": "Режим манги/комиксов",
    "threads_label": "Потоки:",
    "start_download_button_text": "⬇️ Начать скачивание",
    "start_download_button_tooltip": "Нажмите, чтобы начать процесс скачивания или извлечения ссылок с текущими настройками.",
    "extract_links_button_text": "🔗 Извлечь ссылки",
    "pause_download_button_text": "⏸️ Приостановить скачивание",
    "pause_download_button_tooltip": "Нажмите, чтобы приостановить текущий процесс скачивания.",
    "resume_download_button_text": "▶️ Возобновить скачивание",
    "resume_download_button_tooltip": "Нажмите, чтобы возобновить скачивание.",
    "cancel_button_text": "❌ Отменить и сбросить интерфейс",
    "cancel_button_tooltip": "Нажмите, чтобы отменить текущий процесс скачивания/извлечения и сбросить поля интерфейса (сохраняя URL и каталог).",
    "error_button_text": "Ошибка",
    "error_button_tooltip": "Просмотреть файлы, пропущенные из-за ошибок, и при необходимости повторить их скачивание.",
    "cancel_retry_button_text": "❌ Отменить повтор",
    "known_chars_label_text": "🎭 Известные шоу/персонажи (для названий папок):",
    "open_known_txt_button_text": "Открыть Known.txt",
    "known_chars_list_tooltip": "Этот список содержит имена, используемые для автоматического создания папок, когда включена опция 'Раздельные папки'\nи не указан или не совпадает с постом конкретный 'Фильтр по персонажу(ам)'.\nДобавьте названия сериалов, игр или персонажей, которые вы часто скачиваете.",
    "open_known_txt_button_tooltip": "Открыть файл 'Known.txt' в вашем текстовом редакторе по умолчанию.\nФайл находится в каталоге приложения.",
    "add_char_button_text": "➕ Добавить",
    "add_char_button_tooltip": "Добавить имя из поля ввода в список 'Известные шоу/персонажи'.",
    "add_to_filter_button_text": "⤵️ Добавить в фильтр",
    "add_to_filter_button_tooltip": "Выберите имена из списка 'Известные шоу/персонажи', чтобы добавить их в поле 'Фильтровать по персонажу(ам)' выше.",
    "delete_char_button_text": "🗑️ Удалить выбранные",
    "delete_char_button_tooltip": "Удалить выбранные имена из списка 'Известные шоу/персонажи'.",
    "progress_log_label_text": "� Журнал прогресса:",
    "radio_all_tooltip": "Скачивать все типы файлов, найденные в постах.",
    "radio_images_tooltip": "Скачивать только распространенные форматы изображений (JPG, PNG, GIF, WEBP и т. д.).",
    "radio_videos_tooltip": "Скачивать только распространенные форматы видео (MP4, MKV, WEBM, MOV и т. д.).",
    "radio_only_archives_tooltip": "Скачивать исключительно файлы .zip и .rar. Другие опции, специфичные для файлов, отключены.",
    "radio_only_audio_tooltip": "Скачивать только распространенные аудиоформаты (MP3, WAV, FLAC и т. д.).",
    "radio_only_links_tooltip": "Извлекать и отображать внешние ссылки из описаний постов вместо скачивания файлов.\nОпции, связанные со скачиванием, будут отключены.",
    "favorite_mode_checkbox_tooltip": "Включить режим избранного для просмотра сохраненных художников/постов.\nЭто заменит поле ввода URL на кнопки выбора избранного.",
    "skip_zip_checkbox_tooltip": "Если отмечено, архивные файлы .zip не будут скачиваться.\n(Отключено, если выбрано 'Только архивы').",
    "skip_rar_checkbox_tooltip": "Если отмечено, архивные файлы .rar не будут скачиваться.\n(Отключено, если выбрано 'Только архивы').",
    "download_thumbnails_checkbox_tooltip": "Скачивает небольшие изображения предварительного просмотра из API вместо полноразмерных файлов (если доступны).\nЕсли также отмечено 'Сканировать контент поста на наличие URL изображений', этот режим будет скачивать *только* изображения, найденные при сканировании контента (игнорируя миниатюры API).",
    "scan_content_images_checkbox_tooltip": "Если отмечено, загрузчик будет сканировать HTML-содержимое постов на наличие URL-адресов изображений (из тегов <img> или прямых ссылок).\nЭто включает в себя преобразование относительных путей из тегов <img> в полные URL-адреса.\nОтносительные пути в тегах <img> (например, /data/image.jpg) будут преобразованы в полные URL-адреса.\nПолезно в случаях, когда изображения находятся в описании поста, но не в списке файлов/вложений API.",
    "compress_images_checkbox_tooltip": "Сжимать изображения > 1,5 МБ в формат WebP (требуется Pillow).",
    "use_subfolders_checkbox_tooltip": "Создавать подпапки на основе ввода 'Фильтровать по персонажу(ам)' или заголовков постов.\nИспользует список 'Известные шоу/персонажи' в качестве запасного варианта для названий папок, если конкретный фильтр не совпадает.\nВключает ввод 'Фильтровать по персонажу(ам)' и 'Пользовательское имя папки' для отдельных постов.",
    "use_subfolder_per_post_checkbox_tooltip": "Создает подпапку для каждого поста. Если также включена опция 'Раздельные папки', она находится внутри папки персонажа/заголовка.",
    "use_cookie_checkbox_tooltip": "Если отмечено, будет предпринята попытка использовать файлы cookie из 'cookies.txt' (формат Netscape)\nв каталоге приложения для запросов.\nПолезно для доступа к контенту, требующему входа в систему на Kemono/Coomer.",
    "cookie_text_input_tooltip": "Введите вашу строку cookie напрямую.\nОна будет использована, если отмечено 'Использовать cookie' И 'cookies.txt' не найден или это поле не пустое.\nФормат зависит от того, как его будет разбирать бэкенд (например, 'name1=value1; name2=value2').",
    "use_multithreading_checkbox_tooltip": "Включает параллельные операции. Подробности см. в поле 'Потоки'.",
    "thread_count_input_tooltip": "Количество параллельных операций.\n- Один пост: параллельная загрузка файлов (рекомендуется 1-10).\n- URL ленты автора: количество постов для одновременной обработки (рекомендуется 1-200).\n  Файлы в каждом посте загружаются один за другим его рабочим потоком.\nЕсли 'Использовать многопоточность' не отмечено, используется 1 поток.",
    "external_links_checkbox_tooltip": "Если отмечено, под основным журналом появится дополнительная панель журнала для отображения внешних ссылок, найденных в описаниях постов.\n(Отключено, если активен режим 'Только ссылки' или 'Только архивы').",
    "manga_mode_checkbox_tooltip": "Скачивает посты от самых старых к самым новым и переименовывает файлы на основе заголовка поста (только для лент авторов).",
    "multipart_on_button_text": "Многочаст.: ВКЛ",
    "multipart_on_button_tooltip": "Многочастная загрузка: ВКЛ\n\nВключает одновременную загрузку больших файлов несколькими сегментами.\n- Может ускорить загрузку отдельных больших файлов (например, видео).\n- Может увеличить использование ЦП/сети.\n- Для лент с множеством мелких файлов это может не дать преимуществ в скорости и может сделать интерфейс/журнал перегруженным.\n- Если многочастная загрузка не удалась, она повторяется в однопоточном режиме.\n\nНажмите, чтобы ВЫКЛ.",
    "multipart_off_button_text": "Многочаст.: ВЫКЛ",
    "multipart_off_button_tooltip": "Многочастная загрузка: ВЫКЛ\n\nВсе файлы скачиваются одним потоком.\n- Стабильно и хорошо работает в большинстве случаев, особенно с множеством мелких файлов.\n- Большие файлы скачиваются последовательно.\n\nНажмите, чтобы ВКЛ (см. предупреждение).",
    "reset_button_text": "🔄 Сброс",
    "reset_button_tooltip": "Сбросить все вводы и журналы до состояния по умолчанию (только в режиме ожидания).",
    "progress_idle_text": "Прогресс: Ожидание",
    "missed_character_log_label_text": "🚫 Журнал пропущенных персонажей:",
    "creator_popup_title": "Выбор автора",
    "creator_popup_search_placeholder": "Искать по имени, сервису или вставить URL автора...",
    "creator_popup_add_selected_button": "Добавить выбранные",
    "creator_popup_scope_characters_button": "Область: Персонажи",
    "creator_popup_scope_creators_button": "Область: Авторы",
    "favorite_artists_button_text": "🖼️ Избранные художники",
    "favorite_artists_button_tooltip": "Просматривайте и скачивайте работы ваших любимых художников на Kemono.su/Coomer.su.",
    "favorite_posts_button_text": "📄 Избранные посты",
    "favorite_posts_button_tooltip": "Просматривайте и скачивайте ваши любимые посты с Kemono.su/Coomer.su.",
    "favorite_scope_selected_location_text": "Область: Выбранное место",
    "favorite_scope_selected_location_tooltip": "Текущая область скачивания избранного: Выбранное место\n\nВсе выбранные избранные художники/посты будут скачаны в основное 'Место для скачивания', указанное в интерфейсе.\nФильтры (персонаж, слова для пропуска, тип файла) будут применяться глобально ко всему контенту.\n\nНажмите, чтобы изменить на: Папки художников",
    "favorite_scope_artist_folders_text": "Область: Папки художников",
    "favorite_scope_artist_folders_tooltip": "Текущая область скачивания избранного: Папки художников\n\nДля каждого выбранного избранного художника/поста будет создана новая подпапка (с именем художника) внутри основного 'Места для скачивания'.\nКонтент этого художника/поста будет скачан в их конкретную подпапку.\nФильтры (персонаж, слова для пропуска, тип файла) будут применяться *внутри* папки каждого художника.\n\nНажмите, чтобы изменить на: Выбранное место",
    "favorite_scope_unknown_text": "Область: Неизвестно",
    "favorite_scope_unknown_tooltip": "Область скачивания избранного неизвестна. Нажмите для переключения.",
    "manga_style_post_title_text": "Название: Заголовок поста",
    "manga_style_original_file_text": "Название: Исходный файл",
    "manga_style_date_based_text": "Название: На основе даты",
    "manga_style_title_global_num_text": "Название: Заголовок+Г.ном.",
    "manga_style_unknown_text": "Название: Неизвестный стиль",
    "fav_artists_dialog_title": "Избранные художники",
    "fav_artists_loading_status": "Загрузка избранных художников...",
    "fav_artists_search_placeholder": "Поиск художников...",
    "fav_artists_select_all_button": "Выбрать все",
    "fav_artists_deselect_all_button": "Снять выделение со всех",
    "fav_artists_download_selected_button": "Скачать выбранные",
    "fav_artists_cancel_button": "Отмена",
    "fav_artists_loading_from_source_status": "⏳ Загрузка избранного из {source_name}...",
    "fav_artists_found_status": "Найдено всего {count} избранных художников.",
    "fav_artists_none_found_status": "На Kemono.su или Coomer.su не найдено избранных художников.",
    "fav_artists_failed_status": "Не удалось загрузить избранное.",
    "fav_artists_cookies_required_status": "Ошибка: Cookie включены, но не могут быть загружены ни для одного источника.",
    "fav_artists_no_favorites_after_processing": "После обработки не найдено избранных художников.",
    "fav_artists_no_selection_title": "Ничего не выбрано",
    "fav_artists_no_selection_message": "Пожалуйста, выберите хотя бы одного художника для скачивания.",
    "fav_posts_dialog_title": "Избранные посты",
    "fav_posts_loading_status": "Загрузка избранных постов...",
    "fav_posts_search_placeholder": "Поиск постов (заголовок, автор, ID, сервис)...",
    "fav_posts_select_all_button": "Выбрать все",
    "fav_posts_deselect_all_button": "Снять выделение со всех",
    "fav_posts_download_selected_button": "Скачать выбранные",
    "fav_posts_cancel_button": "Отмена",
    "fav_posts_cookies_required_error": "Ошибка: для избранных постов требуются файлы cookie, но их не удалось загрузить.",
    "fav_posts_auth_failed_title": "Ошибка авторизации (посты)",
    "fav_posts_auth_failed_message": "Не удалось загрузить избранное{domain_specific_part} из-за ошибки авторизации:\n\n{error_message}\n\nЭто обычно означает, что ваши файлы cookie отсутствуют, недействительны или истек срок их действия для сайта. Пожалуйста, проверьте настройки cookie.",
    "fav_posts_fetch_error_title": "Ошибка загрузки",
    "fav_posts_fetch_error_message": "Ошибка загрузки избранного с {domain}{error_message_part}",
    "fav_posts_no_posts_found_status": "Избранных постов не найдено.",
    "fav_posts_found_status": "Найдено {count} избранных постов.",
    "fav_posts_display_error_status": "Ошибка отображения постов: {error}",
    "fav_posts_ui_error_title": "Ошибка интерфейса",
    "fav_posts_ui_error_message": "Не удалось отобразить избранные посты: {error}",
    "fav_posts_auth_failed_message_generic": "Не удалось загрузить избранное{domain_specific_part} из-за ошибки авторизации. Это обычно означает, что ваши файлы cookie отсутствуют, недействительны или истек срок их действия для сайта. Пожалуйста, проверьте настройки cookie.",
    "key_fetching_fav_post_list_init": "Загрузка списка избранных постов...",
    "key_fetching_from_source_kemono_su": "Загрузка избранного с Kemono.su...",
    "key_fetching_from_source_coomer_su": "Загрузка избранного с Coomer.su...",
    "fav_posts_fetch_cancelled_status": "Загрузка избранных постов отменена.",
    "known_names_filter_dialog_title": "Добавить известные имена в фильтр",
    "known_names_filter_search_placeholder": "Поиск имен...",
    "known_names_filter_select_all_button": "Выбрать все",
    "known_names_filter_deselect_all_button": "Снять выделение со всех",
    "known_names_filter_add_selected_button": "Добавить выбранные",
    "error_files_dialog_title": "Файлы, пропущенные из-за ошибок",
    "error_files_no_errors_label": "Ни один файл не был записан как пропущенный из-за ошибок в последней сессии или после повторных попыток.",
    "error_files_found_label": "Следующие {count} файлов были пропущены из-за ошибок скачивания:",
    "error_files_select_all_button": "Выбрать все",
    "error_files_retry_selected_button": "Повторить выбранные",
    "error_files_export_urls_button": "Экспортировать URL в .txt",
    "error_files_no_selection_retry_message": "Пожалуйста, выберите хотя бы один файл для повторной попытки.",
    "error_files_no_errors_export_title": "Нет ошибок",
    "error_files_no_errors_export_message": "Нет URL-адресов файлов с ошибками для экспорта.",
    "error_files_no_urls_found_export_title": "URL не найдены",
    "error_files_no_urls_found_export_message": "Не удалось извлечь URL-адреса из списка файлов с ошибками для экспорта.",
    "error_files_save_dialog_title": "Сохранить URL-адреса файлов с ошибками",
    "error_files_export_success_title": "Экспорт успешен",
    "error_files_export_success_message": "Успешно экспортировано {count} записей в:\n{filepath}",
    "error_files_export_error_title": "Ошибка экспорта",
    "error_files_export_error_message": "Не удалось экспортировать ссылки на файлы: {error}",
    "export_options_dialog_title": "Параметры экспорта",
    "export_options_description_label": "Выберите формат для экспорта ссылок на файлы с ошибками:",
    "export_options_radio_link_only": "Ссылка на строку (только URL)",
    "export_options_radio_link_only_tooltip": "Экспортирует только прямую ссылку для скачивания каждого не удавшегося файла, по одной ссылке на строку.",
    "export_options_radio_with_details": "Экспортировать с подробностями (URL [Пост, Информация о файле])",
    "export_options_radio_with_details_tooltip": "Экспортирует URL, за которым следуют подробности, такие как заголовок поста, ID поста и исходное имя файла в скобках.",
    "export_options_export_button": "Экспорт",
    "no_errors_logged_title": "Ошибок не зарегистрировано",
    "no_errors_logged_message": "Ни один файл не был записан как пропущенный из-за ошибок в последней сессии или после повторных попыток.",
    "progress_initializing_text": "Прогресс: Инициализация...",
    "progress_posts_text": "Прогресс: {processed_posts} / {total_posts} постов ({progress_percent:.1f}%)",
    "progress_processing_post_text": "Прогресс: Обработка поста {processed_posts}...",
    "progress_starting_text": "Прогресс: Запуск...",
    "downloading_file_known_size_text": "Скачивание '{filename}' ({downloaded_mb:.1f}МБ / {total_mb:.1f}МБ)",
    "downloading_file_unknown_size_text": "Скачивание '{filename}' ({downloaded_mb:.1f}МБ)",
    "downloading_multipart_text": "Скач. '{filename}...': {downloaded_mb:.1f}/{total_mb:.1f} МБ ({parts} частей @ {speed:.2f} МБ/с)",
    "downloading_multipart_initializing_text": "Файл: {filename} - Инициализация частей...",
    "status_completed": "Завершено",
    "status_cancelled_by_user": "Отменено пользователем",
    "files_downloaded_label": "скачано",
    "files_skipped_label": "пропущено",
    "retry_finished_text": "Повторная попытка завершена",
    "succeeded_text": "Успешно",
    "failed_text": "Не удалось",
    "ready_for_new_task_text": "Готов к новой задаче.",
    "fav_mode_active_label_text": "⭐Выберите фильтры ниже, прежде чем выбрать понравившиеся.",
    "export_links_button_text": "Экспортировать ссылки",
    "download_extracted_links_button_text": "Скачать",
    "download_selected_button_text": "Скачать выбранные",
    "link_input_placeholder_text": "например, https://kemono.su/patreon/user/12345 или .../post/98765",
    "link_input_tooltip_text": "Введите полный URL-адрес страницы автора Kemono/Coomer или конкретного поста.\nПример (Автор): https://kemono.su/patreon/user/12345\nПример (Пост): https://kemono.su/patreon/user/12345/post/98765",
    "dir_input_placeholder_text": "Выберите папку, куда будут сохраняться скачанные файлы",
    "dir_input_tooltip_text": "Введите или перейдите к основной папке, куда будет сохраняться весь скачанный контент.\nЭто поле является обязательным, если не выбран режим 'Только ссылки'.",
    "character_input_placeholder_text": "например, Tifa, Aerith, (Cloud, Zack)",
    "custom_folder_input_placeholder_text": "Необязательно: Сохранить этот пост в определенную папку",
    "custom_folder_input_tooltip_text": "Если вы скачиваете URL-адрес одного поста И включена опция 'Раздельные папки по имени/заголовку',\nвы можете ввести здесь пользовательское имя для папки загрузки этого поста.\nПример: Моя любимая сцена",
    "skip_words_input_placeholder_text": "например, WM, WIP, sketch, preview",
    "remove_from_filename_input_placeholder_text": "например, patreon, HD",
    "cookie_text_input_placeholder_no_file_selected_text": "Строка cookie (если не выбран cookies.txt)",
    "cookie_text_input_placeholder_with_file_selected_text": "Использование выбранного файла cookie (см. Обзор...)",
    "character_search_input_placeholder_text": "Поиск персонажей...",
    "character_search_input_tooltip_text": "Введите здесь, чтобы отфильтровать список известных шоу/персонажей ниже.",
    "new_char_input_placeholder_text": "Добавить новое название шоу/персонажа",
    "new_char_input_tooltip_text": "Введите новое название шоу, игры или персонажа, чтобы добавить в список выше.",
    "link_search_input_placeholder_text": "Поиск ссылок...",
    "link_search_input_tooltip_text": "В режиме 'Только ссылки' введите здесь, чтобы отфильтровать отображаемые ссылки по тексту, URL или платформе.",
    "manga_date_prefix_input_placeholder_text": "Префикс для имен файлов манги",
    "manga_date_prefix_input_tooltip_text": "Необязательный префикс для имен файлов манги 'На основе даты' или 'Исходный файл' (например, 'Название серии').\nЕсли пусто, файлы будут названы в соответствии со стилем без префикса.",
    "log_display_mode_links_view_text": "🔗 Просмотр ссылок",
    "log_display_mode_progress_view_text": "⬇️ Просмотр прогресса",
    "download_external_links_dialog_title": "Скачать выбранные внешние ссылки",
    "select_all_button_text": "Выбрать все",
    "deselect_all_button_text": "Снять выделение со всех",
    "cookie_browse_button_tooltip": "Обзор файла cookie (формат Netscape, обычно cookies.txt).\nОн будет использован, если отмечено 'Использовать cookie' и текстовое поле выше пустое.",
    "page_range_label_text": "Диапазон страниц:",
    "start_page_input_placeholder": "Начало",
    "start_page_input_tooltip": "Для URL авторов: Укажите начальный номер страницы для скачивания (например, 1, 2, 3).\nОставьте пустым или установите 1, чтобы начать с первой страницы.\nОтключено для URL отдельных постов или в режиме манги/комиксов.",
    "page_range_to_label_text": "до",
    "end_page_input_placeholder": "Конец",
    "end_page_input_tooltip": "Для URL авторов: Укажите конечный номер страницы для скачивания (например, 5, 10).\nОставьте пустым, чтобы скачать все страницы с начальной страницы.\nОтключено для URL отдельных постов или в режиме манги/комиксов.",
    "known_names_help_button_tooltip_text": "Открыть руководство по функциям приложения.",
    "future_settings_button_tooltip_text": "Открыть настройки приложения (тема, язык и т. д.).",
    "link_search_button_tooltip_text": "Фильтровать отображаемые ссылки",
    "confirm_add_all_dialog_title": "Подтвердить добавление новых имен",
    "confirm_add_all_info_label": "Следующие новые имена/группы из вашего ввода 'Фильтровать по персонажу(ам)' отсутствуют в 'Known.txt'.\nИх добавление может улучшить организацию папок для будущих загрузок.\n\nПросмотрите список и выберите действие:",
    "confirm_add_all_select_all_button": "Выбрать все",
    "confirm_add_all_deselect_all_button": "Снять выделение со всех",
    "confirm_add_all_add_selected_button": "Добавить выбранные в Known.txt",
    "confirm_add_all_skip_adding_button": "Пропустить добавление этих",
    "confirm_add_all_cancel_download_button": "Отменить скачивание",
    "cookie_help_dialog_title": "Инструкции по файлу cookie",
    "cookie_help_instruction_intro": "<p>Для использования файлов cookie обычно требуется файл <b>cookies.txt</b> из вашего браузера.</p>",
    "cookie_help_how_to_get_title": "<p><b>Как получить cookies.txt:</b></p>",
    "cookie_help_step1_extension_intro": "<li>Установите расширение 'Get cookies.txt LOCALLY' для вашего браузера на основе Chrome:<br><a href=\"https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc\" style=\"color: #87CEEB;\">Получить cookies.txt LOCALLY в Chrome Web Store</a></li>",
    "cookie_help_step2_login": "<li>Перейдите на веб-сайт (например, kemono.su или coomer.su) и при необходимости войдите в систему.</li>",
    "cookie_help_step3_click_icon": "<li>Нажмите на значок расширения на панели инструментов вашего браузера.</li>",
    "cookie_help_step4_export": "<li>Нажмите кнопку 'Экспорт' (например, 'Экспортировать как', 'Экспортировать cookies.txt' - точная формулировка может отличаться в зависимости от версии расширения).</li>",
    "cookie_help_step5_save_file": "<li>Сохраните загруженный файл <code>cookies.txt</code> на свой компьютер.</li>",
    "cookie_help_step6_app_intro": "<li>В этом приложении:<ul>",
    "cookie_help_step6a_checkbox": "<li>Убедитесь, что установлен флажок 'Использовать cookie'.</li>",
    "cookie_help_step6b_browse": "<li>Нажмите кнопку 'Обзор...' рядом с текстовым полем cookie.</li>",
    "cookie_help_step6c_select": "<li>Выберите только что сохраненный файл <code>cookies.txt</code>.</li></ul></li>",
    "cookie_help_alternative_paste": "<p>Кроме того, некоторые расширения могут позволить вам скопировать строку cookie напрямую. В этом случае вы можете вставить ее в текстовое поле вместо просмотра файла.</p>",
    "cookie_help_proceed_without_button": "Скачать без файлов cookie",
    "cookie_help_cancel_download_button": "Отменить скачивание",
    "character_input_tooltip": "Введите имена персонажей (через запятую). Поддерживает расширенную группировку и влияет на именование папок, если включена опция 'Раздельные папки'.\n\nПримеры:\n- Nami → Совпадает с 'Nami', создает папку 'Nami'.\n- (Ulti, Vivi) → Совпадает с любым из них, папка 'Ulti Vivi', добавляет оба в Known.txt отдельно.\n- (Boa, Hancock)~ → Совпадает с любым из них, папка 'Boa Hancock', добавляет как одну группу в Known.txt.\n\nИмена рассматриваются как псевдонимы для сопоставления.\n\nРежимы фильтра (кнопка переключает):\n- Файлы: Фильтрует по имени файла.\n- Заголовок: Фильтрует по заголовку поста.\n- Оба: Сначала заголовок, затем имя файла.\n- Комментарии (бета): Сначала имя файла, затем комментарии к посту.",
    "tour_dialog_title": "Добро пожаловать в Kemono Downloader!",
    "tour_dialog_never_show_checkbox": "Больше не показывать это руководство",
    "tour_dialog_skip_button": "Пропустить руководство",
    "tour_dialog_back_button": "Назад",
    "tour_dialog_next_button": "Далее",
    "tour_dialog_finish_button": "Готово",
    "tour_dialog_step1_title": "👋 Добро пожаловать!",
    "tour_dialog_step1_content": "Здравствуйте! Этот краткий обзор проведет вас по основным функциям Kemono Downloader, включая последние обновления, такие как улучшенная фильтрация, улучшения режима манги и управление файлами cookie.\n<ul>\n<li>Моя цель - помочь вам легко скачивать контент с <b>Kemono</b> и <b>Coomer</b>.</li><br>\n<li><b>🎨 Кнопка выбора автора:</b> Рядом с полем ввода URL нажмите на значок палитры, чтобы открыть диалоговое окно. Просмотрите и выберите авторов из вашего файла <code>creators.json</code>, чтобы быстро добавить их имена в поле ввода URL.</li><br>\n<li><b>Важный совет: Приложение '(Не отвечает)'?</b><br>\nПосле нажатия 'Начать скачивание', особенно для больших лент авторов или с большим количеством потоков, приложение может временно отображаться как '(Не отвечает)'. Ваша операционная система (Windows, macOS, Linux) может даже предложить вам 'Завершить процесс' или 'Принудительно завершить'.<br>\n<b>Пожалуйста, будьте терпеливы!</b> Приложение часто все еще усердно работает в фоновом режиме. Прежде чем принудительно закрывать, попробуйте проверить выбранное 'Место для скачивания' в вашем файловом менеджере. Если вы видите, что создаются новые папки или появляются файлы, это означает, что скачивание идет правильно. Дайте ему немного времени, чтобы снова стать отзывчивым.</li><br>\n<li>Используйте кнопки <b>Далее</b> и <b>Назад</b> для навигации.</li><br>\n<li>Многие опции имеют всплывающие подсказки, если вы наведете на них курсор, для получения дополнительной информации.</li><br>\n<li>Нажмите <b>Пропустить руководство</b>, чтобы закрыть это руководство в любое время.</li><br>\n<li>Установите флажок <b>'Больше не показывать это руководство'</b>, если вы не хотите видеть его при будущих запусках.</li>\n</ul>",
    "tour_dialog_step2_title": "① Начало работы",
    "tour_dialog_step2_content": "Давайте начнем с основ скачивания:\n<ul>\n<li><b>🔗 URL автора/поста Kemono:</b><br>\nВставьте полный веб-адрес (URL) страницы автора (например, <i>https://kemono.su/patreon/user/12345</i>)\nили конкретного поста (например, <i>.../post/98765</i>).<br>\nили автора Coomer (например, <i>https://coomer.su/onlyfans/user/artistname</i>)</li><br>\n<li><b>📁 Место для скачивания:</b><br>\nНажмите 'Обзор...', чтобы выбрать папку на вашем компьютере, куда будут сохраняться все скачанные файлы.\nЭто поле является обязательным, если вы не используете режим 'Только ссылки'.</li><br>\n<li><b>📄 Диапазон страниц (только URL автора):</b><br>\nЕсли вы скачиваете со страницы автора, вы можете указать диапазон страниц для загрузки (например, страницы со 2 по 5).\nОставьте пустым для всех страниц. Эта опция отключена для URL отдельных постов или когда активен <b>Режим манги/комиксов</b>.</li>\n</ul>",
    "tour_dialog_step3_title": "② Фильтрация загрузок",
    "tour_dialog_step3_content": "Уточните, что вы скачиваете, с помощью этих фильтров (большинство из них отключены в режимах 'Только ссылки' или 'Только архивы'):\n<ul>\n<li><b>🎯 Фильтровать по персонажу(ам):</b><br>\nВведите имена персонажей через запятую (например, <i>Tifa, Aerith</i>). Сгруппируйте псевдонимы для общего имени папки: <i>(псевдоним1, псевдоним2, псевдоним3)</i> становится папкой 'псевдоним1 псевдоним2 псевдоним3' (после очистки). Все имена в группе используются как псевдонимы для сопоставления.<br>\nКнопка <b>'Фильтр: [Тип]'</b> (рядом с этим полем ввода) циклически изменяет способ применения этого фильтра:\n<ul><li><i>Фильтр: Файлы:</i> Проверяет имена отдельных файлов. Пост сохраняется, если совпадает хотя бы один файл; скачиваются только совпадающие файлы. Именование папок использует персонажа из совпадающего имени файла (если включена опция 'Раздельные папки').</li><br>\n<li><i>Фильтр: Заголовок:</i> Проверяет заголовки постов. Скачиваются все файлы из совпадающего поста. Именование папок использует персонажа из совпадающего заголовка поста.</li>\n<li><b>⤵️ Кнопка 'Добавить в фильтр' (Известные имена):</b> Рядом с кнопкой 'Добавить' для известных имен (см. Шаг 5), это открывает всплывающее окно. Выберите имена из вашего списка <code>Known.txt</code> с помощью флажков (с панелью поиска), чтобы быстро добавить их в поле 'Фильтровать по персонажу(ам)'. Сгруппированные имена, такие как <code>(Boa, Hancock)</code> из Known.txt, будут добавлены в фильтр как <code>(Boa, Hancock)~</code>.</li><br>\n<li><i>Фильтр: Оба:</i> Сначала проверяет заголовок поста. Если он совпадает, скачиваются все файлы. Если нет, то проверяет имена файлов, и скачиваются только совпадающие файлы. Именование папок отдает приоритет совпадению заголовка, затем совпадению файла.</li><br>\n<li><i>Фильтр: Комментарии (бета):</i> Сначала проверяет имена файлов. Если файл совпадает, скачиваются все файлы из поста. Если совпадения по файлам нет, то проверяет комментарии к посту. Если комментарий совпадает, скачиваются все файлы. (Использует больше запросов к API). Именование папок отдает приоритет совпадению файла, затем совпадению комментария.</li></ul>\nЭтот фильтр также влияет на именование папок, если включена опция 'Раздельные папки по имени/заголовку'.</li><br>\n<li><b>🚫 Пропускать со словами:</b><br>\nВведите слова через запятую (например, <i>WIP, sketch, preview</i>).\nКнопка <b>'Область: [Тип]'</b> (рядом с этим полем ввода) циклически изменяет способ применения этого фильтра:\n<ul><li><i>Область: Файлы:</i> Пропускает файлы, если их имена содержат какие-либо из этих слов.</li><br>\n<li><i>Область: Посты:</i> Пропускает целые посты, если их заголовки содержат какие-либо из этих слов.</li><br>\n<li><i>Область: Оба:</i> Применяет пропуск как по названию файла, так и по заголовку поста (сначала пост, затем файлы).</li></ul></li><br>\n<li><b>Фильтровать файлы (Радиокнопки):</b> Выберите, что скачивать:\n<ul>\n<li><i>Все:</i> Скачивает все найденные типы файлов.</li><br>\n<li><i>Изображения/GIF:</i> Только распространенные форматы изображений и GIF.</li><br>\n<li><i>Видео:</i> Только распространенные форматы видео.</li><br>\n<li><b><i>📦 Только архивы:</i></b> Скачивает исключительно файлы <b>.zip</b> и <b>.rar</b>. При выборе этой опции флажки 'Пропускать .zip' и 'Пропускать .rar' автоматически отключаются и снимаются. 'Показывать внешние ссылки' также отключается.</li><br>\n<li><i>🎧 Только аудио:</i> Только распространенные аудиоформаты (MP3, WAV, FLAC и т. д.).</li><br>\n<li><i>🔗 Только ссылки:</i> Извлекает и отображает внешние ссылки из описаний постов вместо скачивания файлов. Опции, связанные со скачиванием, и 'Показывать внешние ссылки' отключаются.</li>\n</ul></li>\n</ul>",
    "tour_dialog_step4_title": "③ Режим избранного (альтернативная загрузка)",
    "tour_dialog_step4_content": "Приложение предлагает 'Режим избранного' для скачивания контента от художников, которых вы добавили в избранное на Kemono.su.\n<ul>\n<li><b>⭐ Флажок 'Режим избранного':</b><br>\nРасположен рядом с радиокнопкой '🔗 Только ссылки'. Установите этот флажок, чтобы активировать режим избранного.</li><br>\n<li><b>Что происходит в режиме избранного:</b>\n<ul><li>Область ввода '🔗 URL автора/поста Kemono' заменяется сообщением о том, что режим избранного активен.</li><br>\n<li>Стандартные кнопки 'Начать скачивание', 'Пауза', 'Отмена' заменяются кнопками '🖼️ Избранные художники' и '📄 Избранные посты' (Примечание: 'Избранные посты' планируется в будущем).</li><br>\n<li>Опция '🍪 Использовать cookie' автоматически включается и блокируется, так как для загрузки избранного требуются файлы cookie.</li></ul></li><br>\n<li><b>🖼️ Кнопка 'Избранные художники':</b><br>\nНажмите эту кнопку, чтобы открыть диалоговое окно со списком ваших избранных художников с Kemono.su. Вы можете выбрать одного или нескольких художников для скачивания.</li><br>\n<li><b>Область скачивания избранного (Кнопка):</b><br>\nЭта кнопка (рядом с 'Избранными постами') управляет тем, куда скачивается выбранное избранное:\n<ul><li><i>Область: Выбранное место:</i> Все выбранные художники скачиваются в основное 'Место для скачивания', которое вы установили. Фильтры применяются глобально.</li><br>\n<li><i>Область: Папки художников:</i> В вашем основном 'Месте для скачивания' для каждого выбранного художника создается подпапка (с именем художника). Контент этого художника попадает в его конкретную папку. Фильтры применяются внутри папки каждого художника.</li></ul></li><br>\n<li><b>Фильтры в режиме избранного:</b><br>\nОпции 'Фильтровать по персонажу(ам)', 'Пропускать со словами' и 'Фильтровать файлы' по-прежнему применяются к контенту, скачиваемому от ваших избранных художников.</li>\n</ul>",
    "tour_dialog_step5_title": "④ Тонкая настройка загрузок",
    "tour_dialog_step5_content": "Дополнительные опции для настройки ваших загрузок:\n<ul>\n<li><b>Пропускать .zip / Пропускать .rar:</b> Установите эти флажки, чтобы избежать скачивания этих типов архивных файлов.\n<i>(Примечание: Они отключены и игнорируются, если выбран режим фильтра '📦 Только архивы').</i></li><br>\n<li><b>✂️ Удалить слова из названия:</b><br>\nВведите слова через запятую (например, <i>patreon, [HD]</i>) для удаления из имен скачиваемых файлов (без учета регистра).</li><br>\n<li><b>Скачивать только миниатюры:</b> Скачивает небольшие изображения предварительного просмотра вместо полноразмерных файлов (если доступны).</li><br>\n<li><b>Сжимать большие изображения:</b> Если установлена библиотека 'Pillow', изображения размером более 1,5 МБ будут преобразованы в формат WebP, если версия WebP значительно меньше.</li><br>\n<li><b>🗄️ Пользовательское имя папки (только для одного поста):</b><br>\nЕсли вы скачиваете URL-адрес одного конкретного поста И включена опция 'Раздельные папки по имени/заголовку',\nвы можете ввести здесь пользовательское имя для папки загрузки этого поста.</li><br>\n<li><b>🍪 Использовать cookie:</b> Установите этот флажок для использования файлов cookie для запросов. Вы можете либо:\n<ul><li>Ввести строку cookie непосредственно в текстовое поле (например, <i>name1=value1; name2=value2</i>).</li><br>\n<li>Нажать 'Обзор...', чтобы выбрать файл <i>cookies.txt</i> (формат Netscape). Путь появится в текстовом поле.</li></ul>\nЭто полезно для доступа к контенту, требующему входа в систему. Текстовое поле имеет приоритет, если оно заполнено.\nЕсли флажок 'Использовать cookie' установлен, но и текстовое поле, и просматриваемый файл пусты, он попытается загрузить 'cookies.txt' из каталога приложения.</li>\n</ul>",
    "tour_dialog_step6_title": "⑤ Организация и производительность",
    "tour_dialog_step6_content": "Организуйте свои загрузки и управляйте производительностью:\n<ul>\n<li><b>⚙️ Раздельные папки по имени/заголовку:</b> Создает подпапки на основе ввода 'Фильтровать по персонажу(ам)' или заголовков постов (может использовать список <b>Known.txt</b> в качестве запасного варианта для названий папок).</li><br>\n<li><b>Подпапка для каждого поста:</b> Если опция 'Раздельные папки' включена, это создает дополнительную подпапку для <i>каждого отдельного поста</i> внутри основной папки персонажа/заголовка.</li><br>\n<li><b>🚀 Использовать многопоточность (Потоки):</b> Включает более быстрые операции. Число в поле 'Потоки' означает:\n<ul><li>Для <b>Лент авторов:</b> Количество постов для одновременной обработки. Файлы в каждом посте скачиваются последовательно его рабочим потоком (если не включено именование манги 'На основе даты', что принудительно использует 1 рабочий поток для поста).</li><br>\n<li>Для <b>URL отдельных постов:</b> Количество файлов для одновременной загрузки из этого одного поста.</li></ul>\nЕсли флажок не установлен, используется 1 поток. Высокое количество потоков (например, >40) может показать предупреждение.</li><br>\n<li><b>Переключатель многочастной загрузки (верхний правый угол области журнала):</b><br>\nКнопка <b>'Многочаст.: [ВКЛ/ВЫКЛ]'</b> позволяет включать/отключать многосегментную загрузку для отдельных больших файлов.\n<ul><li><b>ВКЛ:</b> Может ускорить загрузку больших файлов (например, видео), но может увеличить 'дерганье' интерфейса или спам в журнале при большом количестве мелких файлов. При включении появляется предупреждение. Если многочастная загрузка не удалась, она повторяется в однопоточном режиме.</li><br>\n<li><b>ВЫКЛ (по умолчанию):</b> Файлы скачиваются одним потоком.</li></ul>\nЭта опция отключена, если активен режим 'Только ссылки' или 'Только архивы'.</li><br>\n<li><b>📖 Режим манги/комиксов (только URL автора):</b> Специально для последовательного контента.\n<ul>\n<li>Скачивает посты от <b>самых старых к самым новым</b>.</li><br>\n<li>Поле 'Диапазон страниц' отключено, так как скачиваются все посты.</li><br>\n<li>Кнопка <b>переключения стиля имени файла</b> (например, 'Название: Заголовок поста') появляется в верхнем правом углу области журнала, когда этот режим активен для ленты автора. Нажмите ее, чтобы переключаться между стилями именования:\n<ul>\n<li><b><i>Название: Заголовок поста (по умолчанию):</i></b> Первый файл в посте называется по очищенному заголовку поста (например, 'Моя глава 1.jpg'). Последующие файлы в *том же посте* попытаются сохранить свои исходные имена файлов (например, 'page_02.png', 'bonus_art.jpg'). Если в посте только один файл, он называется по заголовку поста. Это обычно рекомендуется для большинства манг/комиксов.</li><br>\n<li><b><i>Название: Исходный файл:</i></b> Все файлы пытаются сохранить свои исходные имена файлов. Необязательный префикс (например, 'МояСерия_') можно ввести в поле ввода, которое появляется рядом с кнопкой стиля. Пример: 'МояСерия_ИсходныйФайл.jpg'.</li><br>\n<li><b><i>Название: Заголовок+Г.ном. (Заголовок поста + Глобальная нумерация):</i></b> Все файлы во всех постах текущей сессии скачивания именуются последовательно с использованием очищенного заголовка поста в качестве префикса, за которым следует глобальный счетчик. Например: Пост 'Глава 1' (2 файла) -> 'Глава 1_001.jpg', 'Глава 1_002.png'. Следующий пост 'Глава 2' (1 файл) продолжит нумерацию -> 'Глава 2_003.jpg'. Многопоточность для обработки постов автоматически отключается для этого стиля, чтобы обеспечить правильную глобальную нумерацию.</li><br>\n<li><b><i>Название: На основе даты:</i></b> Файлы именуются последовательно (001.ext, 002.ext, ...) на основе порядка публикации постов. Необязательный префикс (например, 'МояСерия_') можно ввести в поле ввода, которое появляется рядом с кнопкой стиля. Пример: 'МояСерия_001.jpg'. Многопоточность для обработки постов автоматически отключается для этого стиля.</li>\n</ul>\n</li><br>\n<li>Для достижения наилучших результатов со стилями 'Название: Заголовок поста', 'Название: Заголовок+Г.ном.' или 'Название: На основе даты' используйте поле 'Фильтровать по персонажу(ам)' с названием манги/серии для организации папок.</li>\n</ul></li><br>\n<li><b>🎭 Known.txt для умной организации папок:</b><br>\n<code>Known.txt</code> (в каталоге приложения) позволяет точно контролировать автоматическую организацию папок, когда включена опция 'Раздельные папки по имени/заголовку'.\n<ul>\n<li><b>Как это работает:</b> Каждая строка в <code>Known.txt</code> является записью.\n<ul><li>Простая строка, такая как <code>Моя потрясающая серия</code>, означает, что контент, соответствующий этому, попадет в папку с названием 'Моя потрясающая серия'.</li><br>\n<li>Сгруппированная строка, такая как <code>(Персонаж А, Перс А, Альтернативное имя А)</code>, означает, что контент, соответствующий 'Персонаж А', 'Перс А' ИЛИ 'Альтернативное имя А', попадет в ОДНУ папку с названием 'Персонаж А Перс А Альтернативное имя А' (после очистки). Все термины в скобках становятся псевдонимами для этой папки.</li></ul></li>\n<li><b>Интеллектуальный запасной вариант:</b> Когда опция 'Раздельные папки по имени/заголовку' активна, и если пост не соответствует какому-либо конкретному вводу 'Фильтровать по персонажу(ам)', загрузчик обращается к <code>Known.txt</code>, чтобы найти соответствующее основное имя для создания папки.</li><br>\n<li><b>Удобное управление:</b> Добавляйте простые (не сгруппированные) имена через список в интерфейсе ниже. Для расширенного редактирования (например, создания/изменения сгруппированных псевдонимов) нажмите <b>'Открыть Known.txt'</b>, чтобы отредактировать файл в вашем текстовом редакторе. Приложение перезагружает его при следующем использовании или запуске.</li>\n</ul>\n</li>\n</ul>",
    "tour_dialog_step7_title": "⑥ Распространенные ошибки и устранение неполадок",
    "tour_dialog_step7_content": "Иногда при загрузке могут возникать проблемы. Вот несколько распространенных:\n<ul>\n<li><b>Подсказка для ввода персонажа:</b><br>\nВведите имена персонажей через запятую (например, <i>Tifa, Aerith</i>).<br>\nСгруппируйте псевдонимы для общего имени папки: <i>(псевдоним1, псевдоним2, псевдоним3)</i> становится папкой 'псевдоним1 псевдоним2 псевдоним3'.<br>\nВсе имена в группе используются как псевдонимы для сопоставления контента.<br><br>\nКнопка 'Фильтр: [Тип]' рядом с этим полем ввода циклически изменяет способ применения этого фильтра:<br>\n- Фильтр: Файлы: Проверяет имена отдельных файлов. Скачиваются только совпадающие файлы.<br>\n- Фильтр: Заголовок: Проверяет заголовки постов. Скачиваются все файлы из совпадающего поста.<br>\n- Фильтр: Оба: Сначала проверяет заголовок поста. Если совпадения нет, то проверяет имена файлов.<br>\n- Фильтр: Комментарии (бета): Сначала проверяет имена файлов. Если совпадения нет, то проверяет комментарии к посту.<br><br>\nЭтот фильтр также влияет на именование папок, если включена опция 'Раздельные папки по имени/заголовку'.</li><br>\n<li><b>502 Bad Gateway / 503 Service Unavailable / 504 Gateway Timeout:</b><br>\nЭто обычно указывает на временные проблемы на стороне сервера с Kemono/Coomer. Сайт может быть перегружен, находиться на обслуживании или испытывать проблемы.<br>\n<b>Решение:</b> Подождите некоторое время (например, от 30 минут до нескольких часов) и попробуйте снова позже. Проверьте сайт непосредственно в вашем браузере.</li><br>\n<li><b>Потеряно соединение / Соединение отклонено / Тайм-аут (во время загрузки файла):</b><br>\nЭто может произойти из-за вашего интернет-соединения, нестабильности сервера или если сервер разрывает соединение для большого файла.<br>\n<b>Решение:</b> Проверьте ваше интернет-соединение. Попробуйте уменьшить количество 'Потоков', если оно велико. Приложение может предложить повторить некоторые неудачные файлы в конце сеанса.</li><br>\n<li><b>Ошибка IncompleteRead:</b><br>\nСервер отправил меньше данных, чем ожидалось. Часто это временный сбой сети или проблема с сервером.<br>\n<b>Решение:</b> Приложение часто помечает эти файлы для повторной попытки в конце сеанса загрузки.</li><br>\n<li><b>403 Forbidden / 401 Unauthorized (реже для общедоступных постов):</b><br>\nУ вас может не быть разрешения на доступ к контенту. Для некоторого платного или частного контента может помочь использование опции 'Использовать cookie' с действительными файлами cookie из вашей сессии браузера. Убедитесь, что ваши файлы cookie свежие.</li><br>\n<li><b>404 Not Found:</b><br>\nURL поста или файла неверен, или контент был удален с сайта. Дважды проверьте URL.</li><br>\n<li><b>'Постов не найдено' / 'Целевой пост не найден':</b><br>\nУбедитесь, что URL правильный и автор/пост существует. Если вы используете диапазоны страниц, убедитесь, что они действительны для автора. Для очень новых постов может быть небольшая задержка, прежде чем они появятся в API.</li><br>\n<li><b>Общая медлительность / Приложение '(Не отвечает)':</b><br>\nКак упоминалось в Шаге 1, если приложение кажется зависшим после запуска, особенно с большими лентами авторов или большим количеством потоков, пожалуйста, дайте ему время. Вероятно, оно обрабатывает данные в фоновом режиме. Уменьшение количества потоков иногда может улучшить отзывчивость, если это происходит часто.</li>\n</ul>",
    "tour_dialog_step8_title": "⑦ Журнал и финальные элементы управления",
    "tour_dialog_step8_content": "Мониторинг и элементы управления:\n<ul>\n<li><b>📜 Журнал прогресса / Журнал извлеченных ссылок:</b> Показывает подробные сообщения о загрузке. Если активен режим '🔗 Только ссылки', эта область отображает извлеченные ссылки.</li><br>\n<li><b>Показывать внешние ссылки в журнале:</b> Если отмечено, под основным журналом появится дополнительная панель журнала для отображения любых внешних ссылок, найденных в описаниях постов. <i>(Эта опция отключена, если активен режим '🔗 Только ссылки' или '📦 Только архивы').</i></li><br>\n<li><b>Переключатель вида журнала (Кнопка 👁️ / 🙈):</b><br>\nЭта кнопка (в верхнем правом углу области журнала) переключает вид основного журнала:\n<ul><li><b>👁️ Журнал прогресса (по умолчанию):</b> Показывает всю активность загрузки, ошибки и сводки.</li><br>\n<li><b>🙈 Журнал пропущенных персонажей:</b> Отображает список ключевых терминов из заголовков постов, которые были пропущены из-за ваших настроек 'Фильтровать по персонажу(ам)'. Полезно для выявления контента, который вы можете непреднамеренно пропускать.</li></ul></li><br>\n<li><b>🔄 Сброс:</b> Очищает все поля ввода, журналы и сбрасывает временные настройки до их значений по умолчанию. Может использоваться только тогда, когда загрузка не активна.</li><br>\n<li><b>⬇️ Начать скачивание / 🔗 Извлечь ссылки / ⏸️ Пауза / ❌ Отмена:</b> Эти кнопки управляют процессом. 'Отменить и сбросить интерфейс' останавливает текущую операцию и выполняет мягкий сброс интерфейса, сохраняя ваши вводы URL и каталога. 'Пауза/Возобновить' позволяет временно останавливать и продолжать.</li><br>\n<li>Если некоторые файлы завершаются сбоем с устранимыми ошибками (например, 'IncompleteRead'), вам может быть предложено повторить их в конце сеанса.</li>\n</ul>\n<br>Вы готовы! Нажмите <b>'Готово'</b>, чтобы закрыть руководство и начать использовать загрузчик.",
    "help_guide_dialog_title": "Kemono Downloader - Руководство по функциям",
    "help_guide_github_tooltip": "Посетить страницу проекта на GitHub (открывается в браузере)",
    "help_guide_instagram_tooltip": "Посетить нашу страницу в Instagram (открывается в браузере)",
    "help_guide_discord_tooltip": "Посетить наше сообщество в Discord (открывается в браузере)",
    "help_guide_step1_title": "① Введение и основные поля ввода",
    "help_guide_step1_content": "<html><head/><body>\n<p>Это руководство представляет обзор функций, полей и кнопок Kemono Downloader.</p>\n<h3>Основная область ввода (вверху слева)</h3>\n<ul>\n<li><b>🔗 URL автора/поста Kemono:</b>\n<ul>\n<li>Введите полный веб-адрес страницы автора (например, <i>https://kemono.su/patreon/user/12345</i>) или конкретного поста (например, <i>.../post/98765</i>).</li>\n<li>Поддерживает URL-адреса Kemono (kemono.su, kemono.party) и Coomer (coomer.su, coomer.party).</li>\n</ul>\n</li>\n<li><b>Диапазон страниц (от и до):</b>\n<ul>\n<li>Для URL-адресов авторов: укажите диапазон страниц для загрузки (например, со 2 по 5 страницу). Оставьте пустым для всех страниц.</li>\n<li>Отключено для URL-адресов отдельных постов или когда активен <b>Режим манги/комиксов</b>.</li>\n</ul>\n</li>\n<li><b>📁 Место для скачивания:</b>\n<ul>\n<li>Нажмите <b>'Обзор...'</b>, чтобы выбрать основную папку на вашем компьютере, куда будут сохраняться все скачанные файлы.</li>\n<li>Это поле обязательно, если вы не используете режим <b>'🔗 Только ссылки'</b>.</li>\n</ul>\n</li>\n<li><b>🎨 Кнопка выбора автора (рядом с полем ввода URL):</b>\n<ul>\n<li>Нажмите на значок палитры (🎨), чтобы открыть диалоговое окно 'Выбор автора'.</li>\n<li>Это диалоговое окно загружает авторов из вашего файла <code>creators.json</code> (который должен находиться в каталоге приложения).</li>\n<li><b>Внутри диалогового окна:</b>\n<ul>\n<li><b>Панель поиска:</b> Введите текст для фильтрации списка авторов по имени или сервису.</li>\n<li><b>Список авторов:</b> Отображает авторов из вашего <code>creators.json</code>. Авторы, которых вы добавили в 'избранное' (в данных JSON), отображаются вверху.</li>\n<li><b>Флажки:</b> Выберите одного или нескольких авторов, установив флажок рядом с их именем.</li>\n<li><b>Кнопка 'Область' (например, 'Область: Персонажи'):</b> Эта кнопка переключает организацию загрузки при запуске загрузок из этого всплывающего окна:\n<ul><li><i>Область: Персонажи:</i> Загрузки будут организованы в папки с именами персонажей непосредственно в вашем основном 'Месте для скачивания'. Работы разных авторов для одного и того же персонажа будут сгруппированы вместе.</li>\n<li><i>Область: Авторы:</i> Загрузки сначала создадут папку с именем автора в вашем основном 'Месте для скачивания'. Затем внутри папки каждого автора будут созданы подпапки с именами персонажей.</li></ul>\n</li>\n<li><b>Кнопка 'Добавить выбранные':</b> Нажатие этой кнопки возьмет имена всех отмеченных авторов и добавит их в основное поле ввода '🔗 URL автора/поста Kemono', разделенные запятыми. Затем диалоговое окно закроется.</li>\n</ul>\n</li>\n<li>Эта функция предоставляет быстрый способ заполнить поле URL для нескольких авторов без ручного ввода или вставки каждого URL.</li>\n</ul>\n</li>\n</ul></body></html>",
    "help_guide_step2_title": "② Фильтрация загрузок",
    "help_guide_step2_content": "<html><head/><body>\n<h3>Фильтрация загрузок (левая панель)</h3>\n<ul>\n<li><b>🎯 Фильтровать по персонажу(ам):</b>\n<ul>\n<li>Введите имена через запятую (например, <code>Tifa, Aerith</code>).</li>\n<li><b>Сгруппированные псевдонимы для общей папки (отдельные записи в Known.txt):</b> <code>(Vivi, Ulti, Uta)</code>.\n<ul><li>Контент, соответствующий 'Vivi', 'Ulti' ИЛИ 'Uta', попадет в общую папку с названием 'Vivi Ulti Uta' (после очистки).</li>\n<li>Если эти имена новые, будет предложено добавить 'Vivi', 'Ulti' и 'Uta' как <i>отдельные индивидуальные записи</i> в <code>Known.txt</code>.</li>\n</ul>\n</li>\n<li><b>Сгруппированные псевдонимы для общей папки (одна запись в Known.txt):</b> <code>(Yuffie, Sonon)~</code> (обратите внимание на тильду <code>~</code>).\n<ul><li>Контент, соответствующий 'Yuffie' ИЛИ 'Sonon', попадет в общую папку с названием 'Yuffie Sonon'.</li>\n<li>Если новый, 'Yuffie Sonon' (с псевдонимами Yuffie, Sonon) будет предложено добавить как <i>одну групповую запись</i> в <code>Known.txt</code>.</li>\n</ul>\n</li>\n<li>Этот фильтр влияет на именование папок, если включена опция 'Раздельные папки по имени/заголовку'.</li>\n</ul>\n</li>\n<li><b>Фильтр: кнопка [Тип] (область фильтрации персонажей):</b> Переключает способ применения 'Фильтровать по персонажу(ам)':\n<ul>\n<li><code>Фильтр: Файлы</code>: Проверяет имена отдельных файлов. Пост сохраняется, если совпадает хотя бы один файл; скачиваются только совпадающие файлы. Именование папок использует персонажа из совпадающего имени файла.</li>\n<li><code>Фильтр: Заголовок</code>: Проверяет заголовки постов. Скачиваются все файлы из совпадающего поста. Именование папок использует персонажа из совпадающего заголовка поста.</li>\n<li><code>Фильтр: Оба</code>: Сначала проверяет заголовок поста. Если он совпадает, скачиваются все файлы. Если нет, то проверяет имена файлов, и скачиваются только совпадающие файлы. Именование папок отдает приоритет совпадению заголовка, затем совпадению файла.</li>\n<li><code>Фильтр: Комментарии (бета)</code>: Сначала проверяет имена файлов. Если файл совпадает, скачиваются все файлы из поста. Если совпадения по файлам нет, то проверяет комментарии к посту. Если комментарий совпадает, скачиваются все файлы. (Использует больше запросов к API). Именование папок отдает приоритет совпадению файла, затем совпадению комментария.</li>\n</ul>\n</li>\n<li><b>🗄️ Пользовательское имя папки (только для одного поста):</b>\n<ul>\n<li>Видно и доступно только при загрузке URL-адреса одного конкретного поста И когда включена опция 'Раздельные папки по имени/заголовку'.</li>\n<li>Позволяет указать пользовательское имя для папки загрузки этого одного поста.</li>\n</ul>\n</li>\n<li><b>🚫 Пропускать со словами:</b>\n<ul><li>Введите слова через запятую (например, <code>WIP, sketch, preview</code>), чтобы пропустить определенный контент.</li></ul>\n</li>\n<li><b>Область: кнопка [Тип] (область слов для пропуска):</b> Переключает способ применения 'Пропускать со словами':\n<ul>\n<li><code>Область: Файлы</code>: Пропускает отдельные файлы, если их имена содержат какие-либо из этих слов.</li>\n<li><code>Область: Посты</code>: Пропускает целые посты, если их заголовки содержат какие-либо из этих слов.</li>\n<li><code>Область: Оба</code>: Применяет оба (сначала заголовок поста, затем отдельные файлы).</li>\n</ul>\n</li>\n<li><b>✂️ Удалить слова из названия:</b>\n<ul><li>Введите слова через запятую (например, <code>patreon, [HD]</code>) для удаления из имен скачиваемых файлов (без учета регистра).</li></ul>\n</li>\n<li><b>Фильтровать файлы (радиокнопки):</b> Выберите, что скачивать:\n<ul>\n<li><code>Все</code>: Скачивает все найденные типы файлов.</li>\n<li><code>Изображения/GIF</code>: Только распространенные форматы изображений (JPG, PNG, GIF, WEBP и т. д.) и GIF.</li>\n<li><code>Видео</code>: Только распространенные форматы видео (MP4, MKV, WEBM, MOV и т. д.).</li>\n<li><code>📦 Только архивы</code>: Скачивает исключительно файлы <b>.zip</b> и <b>.rar</b>. При выборе этой опции флажки 'Пропускать .zip' и 'Пропускать .rar' автоматически отключаются и снимаются. 'Показывать внешние ссылки' также отключается.</li>\n<li><code>🎧 Только аудио</code>: Скачивает только распространенные аудиоформаты (MP3, WAV, FLAC, M4A, OGG и т. д.). Другие специфичные для файлов опции ведут себя так же, как в режиме 'Изображения' или 'Видео'.</li>\n<li><code>🔗 Только ссылки</code>: Извлекает и отображает внешние ссылки из описаний постов вместо скачивания файлов. Опции, связанные со скачиванием, и 'Показывать внешние ссылки' отключаются. Основная кнопка загрузки меняется на '🔗 Извлечь ссылки'.</li>\n</ul>\n</li>\n</ul></body></html>",
    "help_guide_step3_title": "③ Параметры и настройки загрузки",
    "help_guide_step3_content": "<html><head/><body>\n<h3>Параметры и настройки загрузки (левая панель)</h3>\n<ul>\n<li><b>Пропускать .zip / Пропускать .rar:</b> Флажки для предотвращения загрузки этих типов архивных файлов. (Отключены и игнорируются, если выбран режим фильтра '📦 Только архивы').</li>\n<li><b>Скачивать только миниатюры:</b> Скачивает небольшие изображения предварительного просмотра вместо полноразмерных файлов (если доступны).</li>\n<li><b>Сжимать большие изображения (в WebP):</b> Если установлена библиотека 'Pillow' (PIL), изображения размером более 1,5 МБ будут преобразованы в формат WebP, если версия WebP значительно меньше.</li>\n<li><b>⚙️ Расширенные настройки:</b>\n<ul>\n<li><b>Раздельные папки по имени/заголовку:</b> Создает подпапки на основе ввода 'Фильтровать по персонажу(ам)' или заголовков постов. Может использовать список <b>Known.txt</b> в качестве запасного варианта для названий папок.</li></ul></li></ul></body></html>",
    "help_guide_step4_title": "④ Расширенные настройки (Часть 1)",
    "help_guide_step4_content": "<html><head/><body><h3>⚙️ Расширенные настройки (продолжение)</h3><ul><ul>\n<li><b>Подпапка для каждого поста:</b> Если опция 'Раздельные папки' включена, это создает дополнительную подпапку для <i>каждого отдельного поста</i> внутри основной папки персонажа/заголовка.</li>\n<li><b>Использовать cookie:</b> Установите этот флажок для использования файлов cookie для запросов.\n<ul>\n<li><b>Текстовое поле:</b> Введите строку cookie напрямую (например, <code>name1=value1; name2=value2</code>).</li>\n<li><b>Обзор...:</b> Выберите файл <code>cookies.txt</code> (формат Netscape). Путь появится в текстовом поле.</li>\n<li><b>Приоритет:</b> Текстовое поле (если заполнено) имеет приоритет над просматриваемым файлом. Если флажок 'Использовать cookie' установлен, но оба поля пусты, он попытается загрузить <code>cookies.txt</code> из каталога приложения.</li>\n</ul>\n</li>\n<li><b>Использовать многопоточность и ввод потоков:</b>\n<ul>\n<li>Включает более быстрые операции. Число в поле 'Потоки' означает:\n<ul>\n<li>Для <b>Лент авторов:</b> Количество постов для одновременной обработки. Файлы в каждом посте скачиваются последовательно его рабочим потоком (если не включено именование манги 'На основе даты', что принудительно использует 1 рабочий поток для поста).</li>\n<li>Для <b>URL отдельных постов:</b> Количество файлов для одновременной загрузки из этого одного поста.</li>\n</ul>\n</li>\n<li>Если флажок не установлен, используется 1 поток. Высокое количество потоков (например, >40) может показать предупреждение.</li>\n</ul>\n</li></ul></ul></body></html>",
    "help_guide_step5_title": "⑤ Расширенные настройки (Часть 2) и действия",
    "help_guide_step5_content": "<html><head/><body><h3>⚙️ Расширенные настройки (продолжение)</h3><ul><ul>\n<li><b>Показывать внешние ссылки в журнале:</b> Если отмечено, под основным журналом появится дополнительная панель журнала для отображения любых внешних ссылок, найденных в описаниях постов. (Отключено, если активен режим '🔗 Только ссылки' или '📦 Только архивы').</li>\n<li><b>📖 Режим манги/комиксов (только URL автора):</b> Специально для последовательного контента.\n<ul>\n<li>Скачивает посты от <b>самых старых к самым новым</b>.</li>\n<li>Поле 'Диапазон страниц' отключено, так как скачиваются все посты.</li>\n<li>Кнопка <b>переключения стиля имени файла</b> (например, 'Название: Заголовок поста') появляется в верхнем правом углу области журнала, когда этот режим активен для ленты автора. Нажмите ее, чтобы переключаться между стилями именования:\n<ul>\n<li><code>Название: Заголовок поста (по умолчанию)</code>: Первый файл в посте называется по очищенному заголовку поста (например, 'Моя глава 1.jpg'). Последующие файлы в *том же посте* попытаются сохранить свои исходные имена файлов (например, 'page_02.png', 'bonus_art.jpg'). Если в посте только один файл, он называется по заголовку поста. Это обычно рекомендуется для большинства манг/комиксов.</li>\n<li><code>Название: Исходный файл</code>: Все файлы пытаются сохранить свои исходные имена файлов.</li>\n<li><code>Название: Исходный файл</code>: Все файлы пытаются сохранить свои исходные имена файлов. Когда этот стиль активен, рядом с этой кнопкой стиля появится поле ввода для <b>необязательного префикса имени файла</b> (например, 'МояСерия_'). Пример: 'МояСерия_ИсходныйФайл.jpg'.</li>\n<li><code>Название: Заголовок+Г.ном. (Заголовок поста + Глобальная нумерация)</code>: Все файлы во всех постах текущей сессии скачивания именуются последовательно с использованием очищенного заголовка поста в качестве префикса, за которым следует глобальный счетчик. Пример: Пост 'Глава 1' (2 файла) -> 'Глава 1 001.jpg', 'Глава 1 002.png'. Следующий пост 'Глава 2' (1 файл) -> 'Глава 2 003.jpg'. Многопоточность для обработки постов автоматически отключается для этого стиля.</li>\n<li><code>Название: На основе даты</code>: Файлы именуются последовательно (001.ext, 002.ext, ...) на основе порядка публикации. Когда этот стиль активен, рядом с этой кнопкой стиля появится поле ввода для <b>необязательного префикса имени файла</b> (например, 'МояСерия_'). Пример: 'МояСерия_001.jpg'. Многопоточность для обработки постов автоматически отключается для этого стиля.</li>\n</ul>\n</li>\n<li>Для достижения наилучших результатов со стилями 'Название: Заголовок поста', 'Название: Заголовок+Г.ном.' или 'Название: На основе даты' используйте поле 'Фильтровать по персонажу(ам)' с названием манги/серии для организации папок.</li>\n</ul>\n</li>\n</ul></li></ul>\n<h3>Основные кнопки действий (левая панель)</h3>\n<ul>\n<li><b>⬇️ Начать скачивание / 🔗 Извлечь ссылки:</b> Текст и функция этой кнопки меняются в зависимости от выбора радиокнопки 'Фильтровать файлы'. Она запускает основную операцию.</li>\n<li><b>⏸️ Приостановить скачивание / ▶️ Возобновить скачивание:</b> Позволяет временно остановить текущий процесс скачивания/извлечения и возобновить его позже. Некоторые настройки интерфейса можно изменить во время паузы.</li>\n<li><b>❌ Отменить и сбросить интерфейс:</b> Останавливает текущую операцию и выполняет мягкий сброс интерфейса. Ваши вводы URL и каталога загрузки сохраняются, но другие настройки и журналы очищаются.</li>\n</ul></body></html>",
    "help_guide_step6_title": "⑥ Список известных шоу/персонажей",
    "help_guide_step6_content": "<html><head/><body>\n<h3>Управление списком известных шоу/персонажей (внизу слева)</h3>\n<p>Этот раздел помогает управлять файлом <code>Known.txt</code>, который используется для умной организации папок, когда включена опция 'Раздельные папки по имени/заголовку', особенно в качестве запасного варианта, если пост не соответствует вашему активному вводу 'Фильтровать по персонажу(ам)'.</p>\n<ul>\n<li><b>Открыть Known.txt:</b> Открывает файл <code>Known.txt</code> (расположенный в каталоге приложения) в вашем текстовом редакторе по умолчанию для расширенного редактирования (например, создания сложных сгруппированных псевдонимов).</li>\n<li><b>Поиск персонажей...:</b> Фильтрует список известных имен, отображаемый ниже.</li>\n<li><b>Виджет списка:</b> Отображает основные имена из вашего <code>Known.txt</code>. Выберите здесь записи для их удаления.</li>\n<li><b>Добавить новое название шоу/персонажа (поле ввода):</b> Введите имя или группу для добавления.\n<ul>\n<li><b>Простое имя:</b> например, <code>Моя потрясающая серия</code>. Добавляется как одна запись.</li>\n<li><b>Группа для отдельных записей в Known.txt:</b> например, <code>(Vivi, Ulti, Uta)</code>. Добавляет 'Vivi', 'Ulti' и 'Uta' как три отдельные индивидуальные записи в <code>Known.txt</code>.</li>\n<li><b>Группа для общей папки и одной записи в Known.txt (тильда <code>~</code>):</b> например, <code>(Персонаж А, Перс А)~</code>. Добавляет одну запись в <code>Known.txt</code> с названием 'Персонаж А Перс А'. 'Персонаж А' и 'Перс А' становятся псевдонимами для этой одной папки/записи.</li>\n</ul>\n</li>\n<li><b>➕ Кнопка 'Добавить':</b> Добавляет имя/группу из поля ввода выше в список и <code>Known.txt</code>.</li>\n<li><b>⤵️ Кнопка 'Добавить в фильтр':</b>\n<ul>\n<li>Расположена рядом с кнопкой '➕ Добавить' для списка 'Известные шоу/персонажи'.</li>\n<li>Нажатие этой кнопки открывает всплывающее окно со списком всех имен из вашего файла <code>Known.txt</code>, каждое с флажком.</li>\n<li>Всплывающее окно включает панель поиска для быстрой фильтрации списка имен.</li>\n<li>Вы можете выбрать одно или несколько имен, используя флажки.</li>\n<li>Нажмите 'Добавить выбранные', чтобы вставить выбранные имена в поле ввода 'Фильтровать по персонажу(ам)' в главном окне.</li>\n<li>Если выбранное имя из <code>Known.txt</code> изначально было группой (например, определено как <code>(Boa, Hancock)</code> в Known.txt), оно будет добавлено в поле фильтра как <code>(Boa, Hancock)~</code>. Простые имена добавляются как есть.</li>\n<li>Для удобства во всплывающем окне доступны кнопки 'Выбрать все' и 'Снять выделение со всех'.</li>\n<li>Нажмите 'Отмена', чтобы закрыть всплывающее окно без каких-либо изменений.</li>\n</ul>\n</li>\n<li><b>🗑️ Кнопка 'Удалить выбранные':</b> Удаляет выбранные имена из списка и <code>Known.txt</code>.</li>\n<li><b>❓ Кнопка (именно эта!):</b> Отображает это подробное руководство по помощи.</li>\n</ul></body></html>",
    "help_guide_step7_title": "⑦ Область журнала и элементы управления",
    "help_guide_step7_content": "<html><head/><body>\n<h3>Область журнала и элементы управления (правая панель)</h3>\n<ul>\n<li><b>📜 Журнал прогресса / Журнал извлеченных ссылок (метка):</b> Заголовок для основной области журнала; меняется, если активен режим '🔗 Только ссылки'.</li>\n<li><b>Поиск ссылок... / 🔍 Кнопка (поиск ссылок):</b>\n<ul><li>Видно только тогда, когда активен режим '🔗 Только ссылки'. Позволяет в реальном времени фильтровать извлеченные ссылки, отображаемые в основном журнале, по тексту, URL или платформе.</li></ul>\n</li>\n<li><b>Название: кнопка [Стиль] (стиль имени файла манги):</b>\n<ul><li>Видно только тогда, когда активен <b>Режим манги/комиксов</b> для ленты автора и не в режиме 'Только ссылки' или 'Только архивы'.</li>\n<li>Переключает стили имен файлов: <code>Заголовок поста</code>, <code>Исходный файл</code>, <code>На основе даты</code>. (Подробности см. в разделе 'Режим манги/комиксов').</li>\n<li>Когда активен стиль 'Исходный файл' или 'На основе даты', рядом с этой кнопкой появится поле ввода для <b>необязательного префикса имени файла</b>.</li>\n</ul>\n</li>\n<li><b>Многочаст.: кнопка [ВКЛ/ВЫКЛ]:</b>\n<ul><li>Переключает многосегментную загрузку для отдельных больших файлов.\n<ul><li><b>ВКЛ:</b> Может ускорить загрузку больших файлов (например, видео), но может увеличить 'дерганье' интерфейса или спам в журнале при большом количестве мелких файлов. При включении появляется предупреждение. Если многочастная загрузка не удалась, она повторяется в однопоточном режиме.</li>\n<li><b>ВЫКЛ (по умолчанию):</b> Файлы скачиваются одним потоком.</li>\n</ul>\n<li>Отключено, если активен режим '🔗 Только ссылки' или '📦 Только архивы'.</li>\n</ul>\n</li>\n<li><b>👁️ / 🙈 Кнопка (переключатель вида журнала):</b> Переключает вид основного журнала:\n<ul>\n<li><b>👁️ Журнал прогресса (по умолчанию):</b> Показывает всю активность загрузки, ошибки и сводки.</li>\n<li><b>🙈 Журнал пропущенных персонажей:</b> Отображает список ключевых терминов из заголовков/содержимого постов, которые были пропущены из-за ваших настроек 'Фильтровать по персонажу(ам)'. Полезно для выявления контента, который вы можете непреднамеренно пропускать.</li>\n</ul>\n</li>\n<li><b>🔄 Кнопка 'Сброс':</b> Очищает все поля ввода, журналы и сбрасывает временные настройки до их значений по умолчанию. Может использоваться только тогда, когда загрузка не активна.</li>\n<li><b>Основной вывод журнала (текстовая область):</b> Отображает подробные сообщения о ходе выполнения, ошибки и сводки. Если активен режим '🔗 Только ссылки', эта область отображает извлеченные ссылки.</li>\n<li><b>Вывод журнала пропущенных персонажей (текстовая область):</b> (Просматривается с помощью переключателя 👁️ / 🙈) Отображает посты/файлы, пропущенные из-за фильтров персонажей.</li>\n<li><b>Вывод внешнего журнала (текстовая область):</b> Появляется под основным журналом, если отмечен флажок 'Показывать внешние ссылки в журнале'. Отображает внешние ссылки, найденные в описаниях постов.</li>\n<li><b>Кнопка 'Экспортировать ссылки':</b>\n<ul><li>Видно и доступно только тогда, когда активен режим '🔗 Только ссылки' и были извлечены ссылки.</li>\n<li>Позволяет сохранить все извлеченные ссылки в файл <code>.txt</code>.</li>\n</ul>\n</li>\n<li><b>Прогресс: метка [Статус]:</b> Показывает общий ход процесса скачивания или извлечения ссылок (например, обработанные посты).</li>\n<li><b>Метка прогресса файла:</b> Показывает ход скачивания отдельных файлов, включая скорость и размер, или статус многочастной загрузки.</li>\n</ul></body></html>",
    "help_guide_step8_title": "⑧ Режим избранного и будущие функции",
    "help_guide_step8_content": "<html><head/><body>\n<h3>Режим избранного (скачивание из ваших избранных на Kemono.su)</h3>\n<p>Этот режим позволяет скачивать контент непосредственно от художников, которых вы добавили в избранное на Kemono.su.</p>\n<ul>\n<li><b>⭐ Как включить:</b>\n<ul>\n<li>Установите флажок <b>'⭐ Режим избранного'</b>, расположенный рядом с радиокнопкой '🔗 Только ссылки'.</li>\n</ul>\n</li>\n<li><b>Изменения интерфейса в режиме избранного:</b>\n<ul>\n<li>Область ввода '🔗 URL автора/поста Kemono' заменяется сообщением о том, что режим избранного активен.</li>\n<li>Стандартные кнопки 'Начать скачивание', 'Пауза', 'Отмена' заменяются на:\n<ul>\n<li>Кнопка <b>'🖼️ Избранные художники'</b></li>\n<li>Кнопка <b>'📄 Избранные посты'</b></li>\n</ul>\n</li>\n<li>Опция '🍪 Использовать cookie' автоматически включается и блокируется, так как для загрузки избранного требуются файлы cookie.</li>\n</ul>\n</li>\n<li><b>🖼️ Кнопка 'Избранные художники':</b>\n<ul>\n<li>Нажатие этой кнопки открывает диалоговое окно со списком всех художников, которых вы добавили в избранное на Kemono.su.</li>\n<li>Вы можете выбрать одного или нескольких художников из этого списка для скачивания их контента.</li>\n</ul>\n</li>\n<li><b>📄 Кнопка 'Избранные посты' (будущая функция):</b>\n<ul>\n<li>Скачивание конкретных избранных <i>постов</i> (особенно в последовательном порядке, как манга, если они являются частью серии) — это функция, которая в настоящее время находится в разработке.</li>\n<li>Лучший способ обработки избранных постов, особенно для последовательного чтения, как манга, все еще изучается.</li>\n<li>Если у вас есть конкретные идеи или варианты использования того, как вы хотели бы скачивать и организовывать избранные посты (например, 'в стиле манги' из избранного), пожалуйста, рассмотрите возможность открыть issue или присоединиться к обсуждению на странице проекта на GitHub. Ваш вклад очень ценен!</li>\n</ul>\n</li>\n<li><b>Область скачивания избранного (кнопка):</b>\n<ul>\n<li>Эта кнопка (рядом с 'Избранными постами') управляет тем, куда скачивается контент от выбранных избранных художников:\n<ul>\n<li><b><i>Область: Выбранное место:</i></b> Все выбранные художники скачиваются в основное 'Место для скачивания', которое вы установили в интерфейсе. Фильтры применяются глобально ко всему контенту.</li>\n<li><b><i>Область: Папки художников:</i></b> Для каждого выбранного художника в вашем основном 'Месте для скачивания' автоматически создается подпапка (с именем художника). Контент этого художника попадает в их конкретную подпапку. Фильтры применяются внутри выделенной папки каждого художника.</li>\n</ul>\n</li>\n</ul>\n</li>\n<li><b>Фильтры в режиме избранного:</b>\n<ul>\n<li>Опции '🎯 Фильтровать по персонажу(ам)', '🚫 Пропускать со словами' и 'Фильтровать файлы', которые вы установили в интерфейсе, по-прежнему будут применяться к контенту, скачиваемому от ваших избранных художников.</li>\n</ul>\n</li>\n</ul></body></html>",
    "help_guide_step9_title": "⑨ Ключевые файлы и руководство",
    "help_guide_step9_content": "<html><head/><body>\n<h3>Ключевые файлы, используемые приложением</h3>\n<ul>\n<li><b><code>Known.txt</code>:</b>\n<ul>\n<li>Находится в каталоге приложения (там же, где <code>.exe</code> или <code>main.py</code>).</li>\n<li>Хранит ваш список известных шоу, персонажей или названий серий для автоматической организации папок, когда включена опция 'Раздельные папки по имени/заголовку'.</li>\n<li><b>Формат:</b>\n<ul>\n<li>Каждая строка - это запись.</li>\n<li><b>Простое имя:</b> например, <code>Моя потрясающая серия</code>. Контент, соответствующий этому, попадет в папку с названием 'Моя потрясающая серия'.</li>\n<li><b>Сгруппированные псевдонимы:</b> например, <code>(Персонаж А, Перс А, Альтернативное имя А)</code>. Контент, соответствующий 'Персонаж А', 'Перс А' ИЛИ 'Альтернативное имя А', попадет в ОДНУ папку с названием 'Персонаж А Перс А Альтернативное имя А' (после очистки). Все термины в скобках становятся псевдонимами для этой папки.</li>\n</ul>\n</li>\n<li><b>Использование:</b> Служит запасным вариантом для именования папок, если пост не соответствует вашему активному вводу 'Фильтровать по персонажу(ам)'. Вы можете управлять простыми записями через интерфейс или редактировать файл напрямую для сложных псевдонимов. Приложение перезагружает его при запуске или следующем использовании.</li>\n</ul>\n</li>\n<li><b><code>cookies.txt</code> (необязательно):</b>\n<ul>\n<li>Если вы используете функцию 'Использовать cookie' и не предоставляете прямую строку cookie или не просматриваете конкретный файл, приложение будет искать файл с именем <code>cookies.txt</code> в своем каталоге.</li>\n<li><b>Формат:</b> Должен быть в формате файла cookie Netscape.</li>\n<li><b>Использование:</b> Позволяет загрузчику использовать сеанс входа в ваш браузер для доступа к контенту, который может быть заблокирован на Kemono/Coomer.</li>\n</ul>\n</li>\n</ul>\n<h3>Руководство для первого пользователя</h3>\n<ul>\n<li>При первом запуске (или при сбросе) появляется диалоговое окно приветственного руководства, которое проведет вас по основным функциям. Вы можете пропустить его или выбрать 'Больше не показывать это руководство'.</li>\n</ul>\n<p><em>Многие элементы интерфейса также имеют всплывающие подсказки, которые появляются при наведении на них курсора мыши, предоставляя быстрые подсказки.</em></p>\n</body></html>"
})

translations["ko"] = {} # Initialize the dictionary for zh_CN
translations["ko"].update({
    "settings_dialog_title": "설정",
    "language_label": "언어:",
    "lang_english": "영어 (English)",
    "lang_japanese": "일본어 (日本語)",
    "theme_toggle_light": "라이트 모드로 전환",
    "theme_toggle_dark": "다크 모드로 전환",
    "theme_tooltip_light": "애플리케이션 모양을 라이트 모드로 변경합니다.",
    "theme_tooltip_dark": "애플리케이션 모양을 다크 모드로 변경합니다.",
    "ok_button": "확인",
    "appearance_group_title": "모양",
    "language_group_title": "언어 설정",
    "creator_post_url_label": "🔗 Kemono 작가/게시물 URL:",
    "download_location_label": "📁 다운로드 위치:",
    "filter_by_character_label": "🎯 캐릭터로 필터링 (쉼표로 구분):",
    "skip_with_words_label": "🚫 단어로 건너뛰기 (쉼표로 구분):",
    "remove_words_from_name_label": "✂️ 이름에서 단어 제거:",
    "filter_all_radio": "전체",
    "filter_images_radio": "이미지/GIF",
    "filter_videos_radio": "비디오",
    "filter_archives_radio": "📦 아카이브만",
    "filter_links_radio": "🔗 링크만",
    "filter_audio_radio": "� 오디오만",
    "favorite_mode_checkbox_label": "⭐ 즐겨찾기 모드",
    "browse_button_text": "찾아보기...",
    "char_filter_scope_files_text": "필터: 파일",
    "char_filter_scope_files_tooltip": "현재 범위: 파일\n\n이름으로 개별 파일을 필터링합니다. 파일이 하나라도 일치하면 게시물이 유지됩니다.\n해당 게시물에서 일치하는 파일만 다운로드됩니다.\n예: 필터 'Tifa'. 'Tifa_artwork.jpg' 파일이 일치하여 다운로드됩니다.\n폴더 이름 지정: 일치하는 파일 이름의 캐릭터를 사용합니다.\n\n클릭하여 다음으로 전환: 둘 다",
    "char_filter_scope_title_text": "필터: 제목",
    "char_filter_scope_title_tooltip": "현재 범위: 제목\n\n제목으로 전체 게시물을 필터링합니다. 일치하는 게시물의 모든 파일이 다운로드됩니다.\n예: 필터 'Aerith'. 'Aerith's Garden'이라는 제목의 게시물이 일치하여 모든 파일이 다운로드됩니다.\n폴더 이름 지정: 일치하는 게시물 제목의 캐릭터를 사용합니다.\n\n클릭하여 다음으로 전환: 파일",
    "char_filter_scope_both_text": "필터: 둘 다",
    "char_filter_scope_both_tooltip": "현재 범위: 둘 다 (제목 우선, 그 다음 파일)\n\n1. 게시물 제목을 확인합니다: 일치하면 게시물의 모든 파일이 다운로드됩니다.\n2. 제목이 일치하지 않으면 파일 이름을 확인합니다: 파일이 일치하면 해당 파일만 다운로드됩니다.\n예: 필터 'Cloud'.\n - 'Cloud Strife' 게시물 (제목 일치) -> 모든 파일 다운로드.\n - 'Bike Chase' 게시물에 'Cloud_fenrir.jpg' 파일 (파일 일치) -> 'Cloud_fenrir.jpg'만 다운로드.\n폴더 이름 지정: 제목 일치를 우선으로 하고, 그 다음 파일 일치를 따릅니다.\n\n클릭하여 다음으로 전환: 댓글",
    "char_filter_scope_comments_text": "필터: 댓글 (베타)",
    "char_filter_scope_comments_tooltip": "현재 범위: 댓글 (베타 - 파일 우선, 그 다음 댓글을 예비로 사용)\n\n1. 파일 이름을 확인합니다: 게시물의 파일이 필터와 일치하면 전체 게시물이 다운로드됩니다. 이 필터 용어에 대해 댓글은 확인되지 않습니다.\n2. 파일이 일치하지 않으면 게시물 댓글을 확인합니다: 댓글이 일치하면 전체 게시물이 다운로드됩니다.\n예: 필터 'Barret'.\n - 게시물 A: 파일 'Barret_gunarm.jpg', 'other.png'. 'Barret_gunarm.jpg' 파일 일치. 게시물 A의 모든 파일 다운로드. 'Barret'에 대한 댓글은 확인되지 않음.\n - 게시물 B: 파일 'dyne.jpg', 'weapon.gif'. 댓글: '...Barret Wallace의 그림...'. 'Barret'에 대한 파일 일치 없음. 댓글 일치. 게시물 B의 모든 파일 다운로드.\n폴더 이름 지정: 파일 일치의 캐릭터를 우선으로 하고, 그 다음 댓글 일치의 캐릭터를 따릅니다.\n\n클릭하여 다음으로 전환: 제목",
    "char_filter_scope_unknown_text": "필터: 알 수 없음",
    "char_filter_scope_unknown_tooltip": "현재 범위: 알 수 없음\n\n캐릭터 필터 범위가 알 수 없는 상태입니다. 순환하거나 재설정하십시오.\n\n클릭하여 다음으로 전환: 제목",
    "skip_words_input_tooltip": "쉼표로 구분된 단어를 입력하여 특정 콘텐츠(예: WIP, 스케치, 미리보기)의 다운로드를 건너뜁니다.\n\n이 입력 옆에 있는 '범위: [유형]' 버튼은 이 필터가 적용되는 방식을 순환합니다:\n- 범위: 파일: 파일 이름에 이 단어 중 하나라도 포함되어 있으면 개별 파일을 건너뜁니다.\n- 범위: 게시물: 게시물 제목에 이 단어 중 하나라도 포함되어 있으면 전체 게시물을 건너뜁니다.\n- 범위: 둘 다: 둘 다 적용합니다 (게시물 제목이 먼저, 게시물 제목이 괜찮으면 개별 파일).",
    "remove_words_input_tooltip": "다운로드한 파일 이름에서 제거할 단어를 쉼표로 구분하여 입력합니다(대소문자 구분 없음).\n일반적인 접두사/접미사를 정리하는 데 유용합니다.\n예: patreon, kemono, [HD], _final",
    "skip_scope_files_text": "범위: 파일",
    "skip_scope_files_tooltip": "현재 건너뛰기 범위: 파일\n\n파일 이름에 '건너뛸 단어'가 포함되어 있으면 개별 파일을 건너뜁니다.\n예: 건너뛸 단어 \"WIP, sketch\".\n- 파일 \"art_WIP.jpg\" -> 건너뜀.\n- 파일 \"final_art.png\" -> 다운로드됨 (다른 조건이 충족될 경우).\n\n게시물은 다른 건너뛰지 않은 파일에 대해 계속 처리됩니다.\n클릭하여 다음으로 전환: 둘 다",
    "skip_scope_posts_text": "범위: 게시물",
    "skip_scope_posts_tooltip": "현재 건너뛰기 범위: 게시물\n\n게시물 제목에 '건너뛸 단어'가 포함되어 있으면 전체 게시물을 건너뜁니다.\n건너뛴 게시물의 모든 파일은 무시됩니다.\n예: 건너뛸 단어 \"preview, announcement\".\n- 게시물 \"흥미로운 발표!\" -> 건너뜀.\n- 게시물 \"완성된 작품\" -> 처리됨 (다른 조건이 충족될 경우).\n\n클릭하여 다음으로 전환: 파일",
    "skip_scope_both_text": "범위: 둘 다",
    "skip_scope_both_tooltip": "현재 건너뛰기 범위: 둘 다 (게시물 우선, 그 다음 파일)\n\n1. 게시물 제목을 확인합니다: 제목에 건너뛸 단어가 포함되어 있으면 전체 게시물을 건너뜁니다.\n2. 게시물 제목이 괜찮으면 개별 파일 이름을 확인합니다: 파일 이름에 건너뛸 단어가 포함되어 있으면 해당 파일만 건너뜁니다.\n예: 건너뛸 단어 \"WIP, sketch\".\n- 게시물 \"스케치 및 WIP\" (제목 일치) -> 전체 게시물 건너뜀.\n- 게시물 \"아트 업데이트\" (제목 괜찮음)와 파일:\n  - \"character_WIP.jpg\" (파일 일치) -> 건너뜀.\n  - \"final_scene.png\" (파일 괜찮음) -> 다운로드됨.\n\n클릭하여 다음으로 전환: 게시물",
    "skip_scope_unknown_text": "범위: 알 수 없음",
    "skip_scope_unknown_tooltip": "현재 건너뛰기 범위가 알 수 없는 상태입니다. 순환하거나 재설정하십시오.\n\n클릭하여 다음으로 전환: 게시물",
    "language_change_title": "언어 변경됨",
    "language_change_message": "언어가 변경되었습니다. 모든 변경 사항이 완전히 적용되려면 다시 시작해야 합니다.",
    "language_change_informative": "지금 애플리케이션을 다시 시작하시겠습니까?",
    "restart_now_button": "지금 다시 시작",
    "skip_zip_checkbox_label": ".zip 건너뛰기",
    "skip_rar_checkbox_label": ".rar 건너뛰기",
    "download_thumbnails_checkbox_label": "썸네일만 다운로드",
    "scan_content_images_checkbox_label": "이미지 콘텐츠 스캔",
    "compress_images_checkbox_label": "WebP로 압축",
    "separate_folders_checkbox_label": "이름/제목별로 폴더 분리",
    "subfolder_per_post_checkbox_label": "게시물당 하위 폴더",
    "use_cookie_checkbox_label": "쿠키 사용",
    "use_multithreading_checkbox_base_label": "멀티스레딩 사용",
    "show_external_links_checkbox_label": "로그에 외부 링크 표시",
    "manga_comic_mode_checkbox_label": "만화/코믹 모드",
    "threads_label": "스레드:",
    "start_download_button_text": "⬇️ 다운로드 시작",
    "start_download_button_tooltip": "현재 설정으로 다운로드 또는 링크 추출 프로세스를 시작하려면 클릭하십시오.",
    "extract_links_button_text": "🔗 링크 추출",
    "pause_download_button_text": "⏸️ 다운로드 일시 중지",
    "pause_download_button_tooltip": "진행 중인 다운로드 프로세스를 일시 중지하려면 클릭하십시오.",
    "resume_download_button_text": "▶️ 다운로드 재개",
    "resume_download_button_tooltip": "다운로드를 재개하려면 클릭하십시오.",
    "cancel_button_text": "❌ 취소 및 UI 재설정",
    "cancel_button_tooltip": "진행 중인 다운로드/추출 프로세스를 취소하고 UI 필드를 재설정하려면 클릭하십시오(URL 및 디렉토리 보존).",
    "error_button_text": "오류",
    "error_button_tooltip": "오류로 인해 건너뛴 파일을 보고 선택적으로 다시 시도하십시오.",
    "cancel_retry_button_text": "❌ 재시도 취소",
    "known_chars_label_text": "🎭 알려진 프로그램/캐릭터 (폴더 이름용):",
    "open_known_txt_button_text": "Known.txt 열기",
    "known_chars_list_tooltip": "이 목록에는 '폴더 분리'가 켜져 있고 특정 '캐릭터로 필터링'이 제공되지 않거나 게시물과 일치하지 않을 때 자동 폴더 생성에 사용되는 이름이 포함되어 있습니다.\n자주 다운로드하는 시리즈, 게임 또는 캐릭터의 이름을 추가하십시오.",
    "open_known_txt_button_tooltip": "기본 텍스트 편집기에서 'Known.txt' 파일을 엽니다.\n파일은 애플리케이션 디렉토리에 있습니다.",
    "add_char_button_text": "➕ 추가",
    "add_char_button_tooltip": "입력 필드의 이름을 '알려진 프로그램/캐릭터' 목록에 추가합니다.",
    "add_to_filter_button_text": "⤵️ 필터에 추가",
    "add_to_filter_button_tooltip": "'알려진 프로그램/캐릭터' 목록에서 이름을 선택하여 위의 '캐릭터로 필터링' 필드에 추가합니다.",
    "delete_char_button_text": "🗑️ 선택 항목 삭제",
    "delete_char_button_tooltip": "'알려진 프로그램/캐릭터' 목록에서 선택한 이름을 삭제합니다.",
    "progress_log_label_text": "📜 진행률 로그:",
    "radio_all_tooltip": "게시물에서 찾은 모든 파일 유형을 다운로드합니다.",
    "radio_images_tooltip": "일반적인 이미지 형식(JPG, PNG, GIF, WEBP 등)만 다운로드합니다.",
    "radio_videos_tooltip": "일반적인 비디오 형식(MP4, MKV, WEBM, MOV 등)만 다운로드합니다.",
    "radio_only_archives_tooltip": ".zip 및 .rar 파일만 독점적으로 다운로드합니다. 다른 파일 관련 옵션은 비활성화됩니다.",
    "radio_only_audio_tooltip": "일반적인 오디오 형식(MP3, WAV, FLAC 등)만 다운로드합니다.",
    "radio_only_links_tooltip": "파일을 다운로드하는 대신 게시물 설명에서 외부 링크를 추출하여 표시합니다.\n다운로드 관련 옵션은 비활성화됩니다.",
    "favorite_mode_checkbox_tooltip": "저장된 아티스트/게시물을 탐색하려면 즐겨찾기 모드를 활성화하십시오.\n이렇게 하면 URL 입력이 즐겨찾기 선택 버튼으로 대체됩니다.",
    "skip_zip_checkbox_tooltip": "선택하면 .zip 아카이브 파일이 다운로드되지 않습니다.\n('아카이브만'을 선택하면 비활성화됨).",
    "skip_rar_checkbox_tooltip": "선택하면 .rar 아카이브 파일이 다운로드되지 않습니다.\n('아카이브만'을 선택하면 비활성화됨).",
    "download_thumbnails_checkbox_tooltip": "전체 크기 파일 대신 API에서 작은 미리보기 이미지를 다운로드합니다(사용 가능한 경우).\n'이미지 URL에 대한 게시물 콘텐츠 스캔'도 선택하면 이 모드는 콘텐츠 스캔에서 찾은 이미지만 다운로드합니다(API 썸네일 무시).",
    "scan_content_images_checkbox_tooltip": "선택하면 다운로더가 게시물의 HTML 콘텐츠에서 이미지 URL(<img> 태그 또는 직접 링크에서)을 스캔합니다.\n여기에는 <img> 태그의 상대 경로를 전체 URL로 확인하는 것이 포함됩니다.\n<img> 태그의 상대 경로(예: /data/image.jpg)는 전체 URL로 확인됩니다.\n이미지가 게시물 설명에 있지만 API의 파일/첨부 파일 목록에 없는 경우에 유용합니다.",
    "compress_images_checkbox_tooltip": "1.5MB보다 큰 이미지를 WebP 형식으로 압축합니다(Pillow 필요).",
    "use_subfolders_checkbox_tooltip": "'캐릭터로 필터링' 입력 또는 게시물 제목을 기반으로 하위 폴더를 만듭니다.\n특정 필터가 일치하지 않으면 '알려진 프로그램/캐릭터' 목록을 폴더 이름의 대체 수단으로 사용합니다.\n단일 게시물에 대해 '캐릭터로 필터링' 입력 및 '사용자 지정 폴더 이름'을 활성화합니다.",
    "use_subfolder_per_post_checkbox_tooltip": "각 게시물에 대한 하위 폴더를 만듭니다. '폴더 분리'도 켜져 있으면 캐릭터/제목 폴더 안에 있습니다.",
    "use_cookie_checkbox_tooltip": "선택하면 요청에 애플리케이션 디렉토리의 'cookies.txt'(Netscape 형식)에서 쿠키를 사용하려고 시도합니다.\nKemono/Coomer에서 로그인해야 하는 콘텐츠에 액세스하는 데 유용합니다.",
    "cookie_text_input_tooltip": "쿠키 문자열을 직접 입력하십시오.\n'쿠키 사용'이 선택되어 있고 'cookies.txt'를 찾을 수 없거나 이 필드가 비어 있지 않은 경우 사용됩니다.\n형식은 백엔드가 구문 분석하는 방식에 따라 다릅니다(예: 'name1=value1; name2=value2').",
    "use_multithreading_checkbox_tooltip": "동시 작업을 활성화합니다. 자세한 내용은 '스레드' 입력을 참조하십시오.",
    "thread_count_input_tooltip": "동시 작업 수.\n- 단일 게시물: 동시 파일 다운로드 (1-10 권장).\n- 작성자 피드 URL: 동시에 처리할 게시물 수 (1-200 권장).\n  각 게시물 내의 파일은 해당 작업자에 의해 하나씩 다운로드됩니다.\n'멀티스레딩 사용'을 선택하지 않으면 1개의 스레드가 사용됩니다.",
    "external_links_checkbox_tooltip": "선택하면 주 로그 패널 아래에 보조 로그 패널이 나타나 게시물 설명에서 찾은 외부 링크를 표시합니다.\n('링크만' 또는 '아카이브만' 모드가 활성화된 경우 비활성화됨).",
    "manga_mode_checkbox_tooltip": "게시물을 가장 오래된 것부터 최신 것까지 다운로드하고 게시물 제목에 따라 파일 이름을 바꿉니다(작성자 피드 전용).",
    "multipart_on_button_text": "다중 파트: 켬",
    "multipart_on_button_tooltip": "다중 파트 다운로드: 켬\n\n여러 세그먼트로 대용량 파일을 동시에 다운로드할 수 있습니다.\n- 단일 대용량 파일(예: 비디오)의 다운로드 속도를 높일 수 있습니다.\n- CPU/네트워크 사용량이 증가할 수 있습니다.\n- 파일이 많은 피드의 경우 속도 이점이 없을 수 있으며 UI/로그가 복잡해질 수 있습니다.\n- 다중 파트가 실패하면 단일 스트림으로 다시 시도합니다.\n\n클릭하여 끄기.",
    "multipart_off_button_text": "다중 파트: 끔",
    "multipart_off_button_tooltip": "다중 파트 다운로드: 끔\n\n모든 파일은 단일 스트림을 사용하여 다운로드됩니다.\n- 안정적이며 대부분의 시나리오, 특히 많은 작은 파일에 적합합니다.\n- 대용량 파일은 순차적으로 다운로드됩니다.\n\n클릭하여 켜기(권장 사항 참조).",
    "reset_button_text": "🔄 재설정",
    "reset_button_tooltip": "모든 입력 및 로그를 기본 상태로 재설정합니다(유휴 상태일 때만).",
    "progress_idle_text": "진행률: 유휴",
    "missed_character_log_label_text": "🚫 누락된 캐릭터 로그:",
    "creator_popup_title": "작성자 선택",
    "creator_popup_search_placeholder": "이름, 서비스로 검색하거나 작성자 URL을 붙여넣으십시오...",
    "creator_popup_add_selected_button": "선택 항목 추가",
    "creator_popup_scope_characters_button": "범위: 캐릭터",
    "creator_popup_scope_creators_button": "범위: 작성자",
    "favorite_artists_button_text": "🖼️ 즐겨찾는 아티스트",
    "favorite_artists_button_tooltip": "Kemono.su/Coomer.su에서 즐겨찾는 아티스트를 탐색하고 다운로드하십시오.",
    "favorite_posts_button_text": "📄 즐겨찾는 게시물",
    "favorite_posts_button_tooltip": "Kemono.su/Coomer.su에서 즐겨찾는 게시물을 탐색하고 다운로드하십시오.",
    "favorite_scope_selected_location_text": "범위: 선택한 위치",
    "favorite_scope_selected_location_tooltip": "현재 즐겨찾기 다운로드 범위: 선택한 위치\n\n선택한 모든 즐겨찾는 아티스트/게시물은 UI에 지정된 기본 '다운로드 위치'에 다운로드됩니다.\n필터(캐릭터, 건너뛸 단어, 파일 유형)는 모든 콘텐츠에 전역적으로 적용됩니다.\n\n클릭하여 다음으로 변경: 아티스트 폴더",
    "favorite_scope_artist_folders_text": "범위: 아티스트 폴더",
    "favorite_scope_artist_folders_tooltip": "현재 즐겨찾기 다운로드 범위: 아티스트 폴더\n\n선택한 각 즐겨찾는 아티스트/게시물에 대해 기본 '다운로드 위치' 내에 새 하위 폴더(아티스트 이름)가 생성됩니다.\n해당 아티스트/게시물의 콘텐츠는 특정 하위 폴더에 다운로드됩니다.\n필터(캐릭터, 건너뛸 단어, 파일 유형)는 각 아티스트의 폴더 *내에서* 적용됩니다.\n\n클릭하여 다음으로 변경: 선택한 위치",
    "favorite_scope_unknown_text": "범위: 알 수 없음",
    "favorite_scope_unknown_tooltip": "즐겨찾기 다운로드 범위가 알 수 없습니다. 클릭하여 순환하십시오.",
    "manga_style_post_title_text": "이름: 게시물 제목",
    "manga_style_original_file_text": "이름: 원본 파일",
    "manga_style_date_based_text": "이름: 날짜 기반",
    "manga_style_title_global_num_text": "이름: 제목+전역 번호",
    "manga_style_unknown_text": "이름: 알 수 없는 스타일",
    "fav_artists_dialog_title": "즐겨찾는 아티스트",
    "fav_artists_loading_status": "즐겨찾는 아티스트 로드 중...",
    "fav_artists_search_placeholder": "아티스트 검색...",
    "fav_artists_select_all_button": "모두 선택",
    "fav_artists_deselect_all_button": "모두 선택 해제",
    "fav_artists_download_selected_button": "선택 항목 다운로드",
    "fav_artists_cancel_button": "취소",
    "fav_artists_loading_from_source_status": "⏳ {source_name}에서 즐겨찾기 로드 중...",
    "fav_artists_found_status": "총 {count}명의 즐겨찾는 아티스트를 찾았습니다.",
    "fav_artists_none_found_status": "Kemono.su 또는 Coomer.su에서 즐겨찾는 아티스트를 찾을 수 없습니다.",
    "fav_artists_failed_status": "즐겨찾기를 가져오는 데 실패했습니다.",
    "fav_artists_cookies_required_status": "오류: 쿠키가 활성화되었지만 어떤 소스에 대해서도 로드할 수 없습니다.",
    "fav_artists_no_favorites_after_processing": "처리 후 즐겨찾는 아티스트를 찾을 수 없습니다.",
    "fav_artists_no_selection_title": "선택 항목 없음",
    "fav_artists_no_selection_message": "다운로드할 아티스트를 하나 이상 선택하십시오.",
    "fav_posts_dialog_title": "즐겨찾는 게시물",
    "fav_posts_loading_status": "즐겨찾는 게시물 로드 중...",
    "fav_posts_search_placeholder": "게시물 검색 (제목, 작성자, ID, 서비스)...",
    "fav_posts_select_all_button": "모두 선택",
    "fav_posts_deselect_all_button": "모두 선택 해제",
    "fav_posts_download_selected_button": "선택 항목 다운로드",
    "fav_posts_cancel_button": "취소",
    "fav_posts_cookies_required_error": "오류: 즐겨찾는 게시물에는 쿠키가 필요하지만 로드할 수 없습니다.",
    "fav_posts_auth_failed_title": "인증 실패 (게시물)",
    "fav_posts_auth_failed_message": "인증 오류로 인해 {domain_specific_part}에서 즐겨찾기를 가져올 수 없습니다:\n\n{error_message}\n\n이는 일반적으로 사이트에 대한 쿠키가 없거나 유효하지 않거나 만료되었음을 의미합니다. 쿠키 설정을 확인하십시오.",
    "fav_posts_fetch_error_title": "가져오기 오류",
    "fav_posts_fetch_error_message": "{domain}{error_message_part}에서 즐겨찾기를 가져오는 중 오류 발생",
    "fav_posts_no_posts_found_status": "즐겨찾는 게시물을 찾을 수 없습니다.",
    "fav_posts_found_status": "{count}개의 즐겨찾는 게시물을 찾았습니다.",
    "fav_posts_display_error_status": "게시물 표시 오류: {error}",
    "fav_posts_ui_error_title": "UI 오류",
    "fav_posts_ui_error_message": "즐겨찾는 게시물을 표시할 수 없습니다: {error}",
    "fav_posts_auth_failed_message_generic": "인증 오류로 인해 {domain_specific_part}에서 즐겨찾기를 가져올 수 없습니다. 이는 일반적으로 사이트에 대한 쿠키가 없거나 유효하지 않거나 만료되었음을 의미합니다. 쿠키 설정을 확인하십시오.",
    "key_fetching_fav_post_list_init": "즐겨찾는 게시물 목록 가져오는 중...",
    "key_fetching_from_source_kemono_su": "Kemono.su에서 즐겨찾기 가져오는 중...",
    "key_fetching_from_source_coomer_su": "Coomer.su에서 즐겨찾기 가져오는 중...",
    "fav_posts_fetch_cancelled_status": "즐겨찾는 게시물 가져오기가 취소되었습니다.",
    "known_names_filter_dialog_title": "필터에 알려진 이름 추가",
    "known_names_filter_search_placeholder": "이름 검색...",
    "known_names_filter_select_all_button": "모두 선택",
    "known_names_filter_deselect_all_button": "모두 선택 해제",
    "known_names_filter_add_selected_button": "선택 항목 추가",
    "error_files_dialog_title": "오류로 인해 건너뛴 파일",
    "error_files_no_errors_label": "마지막 세션 또는 재시도 후 오류로 인해 건너뛴 것으로 기록된 파일이 없습니다.",
    "error_files_found_label": "다운로드 오류로 인해 다음 {count}개의 파일이 건너뛰어졌습니다:",
    "error_files_select_all_button": "모두 선택",
    "error_files_retry_selected_button": "선택 항목 다시 시도",
    "error_files_export_urls_button": "URL을 .txt로 내보내기",
    "error_files_no_selection_retry_message": "다시 시도할 파일을 하나 이상 선택하십시오.",
    "error_files_no_errors_export_title": "오류 없음",
    "error_files_no_errors_export_message": "내보낼 오류 파일 URL이 없습니다.",
    "error_files_no_urls_found_export_title": "URL을 찾을 수 없음",
    "error_files_no_urls_found_export_message": "내보낼 오류 파일 목록에서 URL을 추출할 수 없습니다.",
    "error_files_save_dialog_title": "오류 파일 URL 저장",
    "error_files_export_success_title": "내보내기 성공",
    "error_files_export_success_message": "{count}개의 항목을 다음으로 성공적으로 내보냈습니다:\n{filepath}",
    "error_files_export_error_title": "내보내기 오류",
    "error_files_export_error_message": "파일 링크를 내보낼 수 없습니다: {error}",
    "export_options_dialog_title": "내보내기 옵션",
    "export_options_description_label": "오류 파일 링크를 내보낼 형식을 선택하십시오:",
    "export_options_radio_link_only": "줄당 링크 (URL만)",
    "export_options_radio_link_only_tooltip": "실패한 각 파일에 대한 직접 다운로드 URL만 내보냅니다. 줄당 하나의 URL.",
    "export_options_radio_with_details": "세부 정보와 함께 내보내기 (URL [게시물, 파일 정보])",
    "export_options_radio_with_details_tooltip": "URL 다음에 게시물 제목, 게시물 ID, 원본 파일 이름과 같은 세부 정보를 대괄호 안에 내보냅니다.",
    "export_options_export_button": "내보내기",
    "no_errors_logged_title": "기록된 오류 없음",
    "no_errors_logged_message": "마지막 세션 또는 재시도 후 오류로 인해 건너뛴 것으로 기록된 파일이 없습니다.",
    "progress_initializing_text": "진행률: 초기화 중...",
    "progress_posts_text": "진행률: {processed_posts} / {total_posts} 게시물 ({progress_percent:.1f}%)",
    "progress_processing_post_text": "진행률: 게시물 {processed_posts} 처리 중...",
    "progress_starting_text": "진행률: 시작 중...",
    "downloading_file_known_size_text": "'{filename}' 다운로드 중 ({downloaded_mb:.1f}MB / {total_mb:.1f}MB)",
    "downloading_file_unknown_size_text": "'{filename}' 다운로드 중 ({downloaded_mb:.1f}MB)",
    "downloading_multipart_text": "DL '{filename}...': {downloaded_mb:.1f}/{total_mb:.1f} MB ({parts} 파트 @ {speed:.2f} MB/s)",
    "downloading_multipart_initializing_text": "파일: {filename} - 파트 초기화 중...",
    "status_completed": "완료됨",
    "status_cancelled_by_user": "사용자가 취소함",
    "files_downloaded_label": "다운로드됨",
    "files_skipped_label": "건너뜀",
    "retry_finished_text": "재시도 완료",
    "succeeded_text": "성공",
    "failed_text": "실패",
    "ready_for_new_task_text": "새 작업 준비 완료.",
    "fav_mode_active_label_text": "⭐ 즐겨찾기 모드가 활성화되었습니다. 즐겨찾는 아티스트/게시물을 선택하기 전에 아래 필터를 선택하십시오. 아래 작업을 선택하십시오.",
    "export_links_button_text": "링크 내보내기",
    "download_extracted_links_button_text": "다운로드",
    "download_selected_button_text": "선택 항목 다운로드",
    "link_input_placeholder_text": "예: https://kemono.su/patreon/user/12345 또는 .../post/98765",
    "link_input_tooltip_text": "Kemono/Coomer 작성자 페이지 또는 특정 게시물의 전체 URL을 입력하십시오.\n예 (작성자): https://kemono.su/patreon/user/12345\n예 (게시물): https://kemono.su/patreon/user/12345/post/98765",
    "dir_input_placeholder_text": "다운로드 항목이 저장될 폴더를 선택하십시오",
    "dir_input_tooltip_text": "모든 다운로드된 콘텐츠가 저장될 기본 폴더를 입력하거나 찾으십시오.\n'링크만' 모드를 선택하지 않은 경우 이 필드는 필수입니다.",
    "character_input_placeholder_text": "예: Tifa, Aerith, (Cloud, Zack)",
    "custom_folder_input_placeholder_text": "선택 사항: 이 게시물을 특정 폴더에 저장",
    "custom_folder_input_tooltip_text": "단일 게시물 URL을 다운로드하고 '이름/제목별로 폴더 분리'가 활성화된 경우,\n해당 게시물의 다운로드 폴더에 대한 사용자 지정 이름을 여기에 입력할 수 있습니다.\n예: 내가 가장 좋아하는 장면",
    "skip_words_input_placeholder_text": "예: WM, WIP, 스케치, 미리보기",
    "remove_from_filename_input_placeholder_text": "예: patreon, HD",
    "cookie_text_input_placeholder_no_file_selected_text": "쿠키 문자열 (cookies.txt가 선택되지 않은 경우)",
    "cookie_text_input_placeholder_with_file_selected_text": "선택한 쿠키 파일 사용 중 (찾아보기... 참조)",
    "character_search_input_placeholder_text": "캐릭터 검색...",
    "character_search_input_tooltip_text": "아래 알려진 프로그램/캐릭터 목록을 필터링하려면 여기에 입력하십시오.",
    "new_char_input_placeholder_text": "새 프로그램/캐릭터 이름 추가",
    "new_char_input_tooltip_text": "위 목록에 추가할 새 프로그램, 게임 또는 캐릭터 이름을 입력하십시오.",
    "link_search_input_placeholder_text": "링크 검색...",
    "link_search_input_tooltip_text": "'링크만' 모드일 때 텍스트, URL 또는 플랫폼으로 표시된 링크를 필터링하려면 여기에 입력하십시오.",
    "manga_date_prefix_input_placeholder_text": "만화 파일 이름 접두사",
    "manga_date_prefix_input_tooltip_text": "'날짜 기반' 또는 '원본 파일' 만화 파일 이름에 대한 선택적 접두사(예: '시리즈 이름').\n비어 있으면 파일은 접두사 없이 스타일에 따라 이름이 지정됩니다.",
    "log_display_mode_links_view_text": "🔗 링크 보기",
    "log_display_mode_progress_view_text": "⬇️ 진행률 보기",
    "download_external_links_dialog_title": "선택한 외부 링크 다운로드",
    "select_all_button_text": "모두 선택",
    "deselect_all_button_text": "모두 선택 해제",
    "cookie_browse_button_tooltip": "쿠키 파일(Netscape 형식, 일반적으로 cookies.txt)을 찾으십시오.\n'쿠키 사용'이 선택되어 있고 위 텍스트 필드가 비어 있는 경우 사용됩니다.",
    "page_range_label_text": "페이지 범위:",
    "start_page_input_placeholder": "시작",
    "start_page_input_tooltip": "작성자 URL의 경우: 다운로드할 시작 페이지 번호(예: 1, 2, 3)를 지정하십시오.\n첫 페이지부터 시작하려면 비워두거나 1로 설정하십시오.\n단일 게시물 URL 또는 만화/코믹 모드에서는 비활성화됩니다.",
    "page_range_to_label_text": "에서",
    "end_page_input_placeholder": "끝",
    "end_page_input_tooltip": "작성자 URL의 경우: 다운로드할 끝 페이지 번호(예: 5, 10)를 지정하십시오.\n시작 페이지부터 모든 페이지를 다운로드하려면 비워두십시오.\n단일 게시물 URL 또는 만화/코믹 모드에서는 비활성화됩니다.",
    "known_names_help_button_tooltip_text": "애플리케이션 기능 가이드 열기.",
    "future_settings_button_tooltip_text": "애플리케이션 설정 열기 (테마, 언어 등).",
    "link_search_button_tooltip_text": "표시된 링크 필터링",
    "confirm_add_all_dialog_title": "새 이름 추가 확인",
    "confirm_add_all_info_label": "'캐릭터로 필터링' 입력의 다음 새 이름/그룹이 'Known.txt'에 없습니다.\n이를 추가하면 향후 다운로드를 위한 폴더 구성을 개선할 수 있습니다.\n\n목록을 검토하고 작업을 선택하십시오:",
    "confirm_add_all_select_all_button": "모두 선택",
    "confirm_add_all_deselect_all_button": "모두 선택 해제",
    "confirm_add_all_add_selected_button": "선택 항목을 Known.txt에 추가",
    "confirm_add_all_skip_adding_button": "이 항목 추가 건너뛰기",
    "confirm_add_all_cancel_download_button": "다운로드 취소",
    "cookie_help_dialog_title": "쿠키 파일 지침",
    "cookie_help_instruction_intro": "<p>쿠키를 사용하려면 일반적으로 브라우저에서 <b>cookies.txt</b> 파일이 필요합니다.</p>",
    "cookie_help_how_to_get_title": "<p><b>cookies.txt를 얻는 방법:</b></p>",
    "cookie_help_step1_extension_intro": "<li>Chrome 기반 브라우저용 'Get cookies.txt LOCALLY' 확장 프로그램을 설치하십시오:<br><a href=\"https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc\" style=\"color: #87CEEB;\">Chrome 웹 스토어에서 Get cookies.txt LOCALLY 받기</a></li>",
    "cookie_help_step2_login": "<li>웹사이트(예: kemono.su 또는 coomer.su)로 이동하여 필요한 경우 로그인하십시오.</li>",
    "cookie_help_step3_click_icon": "<li>브라우저 도구 모음에서 확장 프로그램 아이콘을 클릭하십시오.</li>",
    "cookie_help_step4_export": "<li>'내보내기' 버튼(예: \"다른 이름으로 내보내기\", \"cookies.txt 내보내기\" - 정확한 문구는 확장 프로그램 버전에 따라 다를 수 있음)을 클릭하십시오.</li>",
    "cookie_help_step5_save_file": "<li>다운로드한 <code>cookies.txt</code> 파일을 컴퓨터에 저장하십시오.</li>",
    "cookie_help_step6_app_intro": "<li>이 애플리케이션에서:<ul>",
    "cookie_help_step6a_checkbox": "<li>'쿠키 사용' 확인란이 선택되어 있는지 확인하십시오.</li>",
    "cookie_help_step6b_browse": "<li>쿠키 텍스트 필드 옆에 있는 '찾아보기...' 버튼을 클릭하십시오.</li>",
    "cookie_help_step6c_select": "<li>방금 저장한 <code>cookies.txt</code> 파일을 선택하십시오.</li></ul></li>",
    "cookie_help_alternative_paste": "<p>또는 일부 확장 프로그램에서는 쿠키 문자열을 직접 복사할 수 있습니다. 그렇다면 파일을 찾는 대신 텍스트 필드에 붙여넣을 수 있습니다.</p>",
    "cookie_help_proceed_without_button": "쿠키 없이 다운로드",
    "cookie_help_cancel_download_button": "다운로드 취소",
    "character_input_tooltip": "캐릭터 이름을 쉼표로 구분하여 입력하십시오. 고급 그룹화를 지원하며 '폴더 분리'가 활성화된 경우 폴더 이름 지정에 영향을 줍니다.\n\n예:\n- Nami → 'Nami'와 일치, 'Nami' 폴더 생성.\n- (Ulti, Vivi) → 둘 중 하나와 일치, 'Ulti Vivi' 폴더, 둘 다 Known.txt에 별도로 추가.\n- (Boa, Hancock)~ → 둘 중 하나와 일치, 'Boa Hancock' 폴더, Known.txt에 하나의 그룹으로 추가.\n\n이름은 일치를 위한 별칭으로 처리됩니다.\n\n필터 모드 (버튼 순환):\n- 파일: 파일 이름으로 필터링.\n- 제목: 게시물 제목으로 필터링.\n- 둘 다: 제목 우선, 그 다음 파일 이름.\n- 댓글 (베타): 파일 이름 우선, 그 다음 게시물 댓글.",
    "tour_dialog_title": "Kemono Downloader에 오신 것을 환영합니다!",
    "tour_dialog_never_show_checkbox": "다시는 이 둘러보기를 표시하지 않음",
    "tour_dialog_skip_button": "둘러보기 건너뛰기",
    "tour_dialog_back_button": "뒤로",
    "tour_dialog_next_button": "다음",
    "tour_dialog_finish_button": "완료",
    "tour_dialog_step1_title": "👋 환영합니다!",
    "tour_dialog_step1_content": "안녕하세요! 이 빠른 둘러보기에서는 향상된 필터링, 만화 모드 개선 및 쿠키 관리와 같은 최근 업데이트를 포함하여 Kemono Downloader의 주요 기능을 안내합니다.\n<ul>\n<li>제 목표는 여러분이 <b>Kemono</b> 및 <b>Coomer</b>에서 콘텐츠를 쉽게 다운로드할 수 있도록 돕는 것입니다.</li><br>\n<li><b>🎨 작성자 선택 버튼:</b> URL 입력 옆에 있는 팔레트 아이콘을 클릭하여 대화 상자를 엽니다. <code>creators.json</code> 파일에서 작성자를 찾아보고 선택하여 URL 입력에 이름을 빠르게 추가하십시오.</li><br>\n<li><b>중요 팁: 앱이 '(응답 없음)' 상태인가요?</b><br>\n'다운로드 시작'을 클릭한 후, 특히 대규모 작성자 피드나 많은 스레드가 있는 경우 애플리케이션이 일시적으로 '(응답 없음)'으로 표시될 수 있습니다. 운영 체제(Windows, macOS, Linux)에서 '프로세스 종료' 또는 '강제 종료'를 제안할 수도 있습니다.<br>\n<b>기다려 주십시오!</b> 앱은 종종 백그라운드에서 열심히 작동하고 있습니다. 강제 종료하기 전에 파일 탐색기에서 선택한 '다운로드 위치'를 확인해 보십시오. 새 폴더가 생성되거나 파일이 나타나면 다운로드가 올바르게 진행되고 있음을 의미합니다. 다시 응답할 때까지 시간을 주십시오.</li><br>\n<li><b>다음</b> 및 <b>뒤로</b> 버튼을 사용하여 탐색하십시오.</li><br>\n<li>많은 옵션에는 자세한 내용을 보려면 마우스를 가져가면 나타나는 도구 설명이 있습니다.</li><br>\n<li>언제든지 이 가이드를 닫으려면 <b>둘러보기 건너뛰기</b>를 클릭하십시오.</li><br>\n<li>향후 시작 시 이 둘러보기를 보고 싶지 않으면 <b>'다시는 이 둘러보기를 표시하지 않음'</b>을 선택하십시오.</li>\n</ul>",
    "tour_dialog_step2_title": "① 시작하기",
    "tour_dialog_step2_content": "다운로드 기본 사항부터 시작하겠습니다:\n<ul>\n<li><b>🔗 Kemono 작성자/게시물 URL:</b><br>\n작성자 페이지의 전체 웹 주소(URL)(예: <i>https://kemono.su/patreon/user/12345</i>)\n또는 특정 게시물(예: <i>.../post/98765</i>)을 붙여넣으십시오.<br>\n또는 Coomer 작성자(예: <i>https://coomer.su/onlyfans/user/artistname</i>)</li><br>\n<li><b>📁 다운로드 위치:</b><br>\n'찾아보기...'를 클릭하여 다운로드한 모든 파일이 저장될 컴퓨터의 폴더를 선택하십시오.\n'링크만' 모드를 사용하지 않는 한 이 필드는 필수입니다.</li><br>\n<li><b>📄 페이지 범위 (작성자 URL만):</b><br>\n작성자 페이지에서 다운로드하는 경우 가져올 페이지 범위(예: 2-5페이지)를 지정할 수 있습니다.\n모든 페이지에 대해 비워두십시오. 단일 게시물 URL 또는 <b>만화/코믹 모드</b>가 활성화된 경우 이 기능은 비활성화됩니다.</li>\n</ul>",
    "tour_dialog_step3_title": "② 다운로드 필터링",
    "tour_dialog_step3_content": "이러한 필터로 다운로드할 항목을 구체화하십시오('링크만' 또는 '아카이브만' 모드에서는 대부분 비활성화됨):\n<ul>\n<li><b>🎯 캐릭터로 필터링:</b><br>\n캐릭터 이름을 쉼표로 구분하여 입력하십시오(예: <i>Tifa, Aerith</i>). 결합된 폴더 이름에 대한 별칭 그룹화: <i>(별칭1, 별칭2, 별칭3)</i>은 '별칭1 별칭2 별칭3' 폴더가 됩니다(정리 후). 그룹의 모든 이름은 일치를 위한 별칭으로 사용됩니다.<br>\n이 입력 옆에 있는 <b>'필터: [유형]'</b> 버튼은 이 필터가 적용되는 방식을 순환합니다:\n<ul><li><i>필터: 파일:</i> 개별 파일 이름을 확인합니다. 파일이 하나라도 일치하면 게시물이 유지됩니다. 일치하는 파일만 다운로드됩니다. 폴더 이름 지정은 일치하는 파일 이름의 캐릭터를 사용합니다('폴더 분리'가 켜져 있는 경우).</li><br>\n<li><i>필터: 제목:</i> 게시물 제목을 확인합니다. 일치하는 게시물의 모든 파일이 다운로드됩니다. 폴더 이름 지정은 일치하는 게시물 제목의 캐릭터를 사용합니다.</li>\n<li><b>⤵️ 필터에 추가 버튼 (알려진 이름):</b> 알려진 이름에 대한 '추가' 버튼 옆에 있습니다(5단계 참조). 팝업이 열립니다. <code>Known.txt</code> 목록에서 확인란(검색 창 포함)을 통해 이름을 선택하여 '캐릭터로 필터링' 필드에 빠르게 추가하십시오. <code>(Boa, Hancock)</code>와 같은 그룹화된 이름은 <code>(Boa, Hancock)~</code>로 필터에 추가됩니다.</li><br>\n<li><i>필터: 둘 다:</i> 먼저 게시물 제목을 확인합니다. 일치하면 모든 파일이 다운로드됩니다. 일치하지 않으면 파일 이름을 확인하고 일치하는 파일만 다운로드됩니다. 폴더 이름 지정은 제목 일치를 우선으로 하고 그 다음 파일 일치를 따릅니다.</li><br>\n<li><i>필터: 댓글 (베타):</i> 먼저 파일 이름을 확인합니다. 파일이 일치하면 게시물의 모든 파일이 다운로드됩니다. 파일이 일치하지 않으면 게시물 댓글을 확인합니다. 댓글이 일치하면 모든 파일이 다운로드됩니다. (더 많은 API 요청을 사용합니다). 폴더 이름 지정은 파일 일치를 우선으로 하고 그 다음 댓글 일치를 따릅니다.</li></ul>\n이 필터는 '이름/제목별로 폴더 분리'가 활성화된 경우 폴더 이름 지정에도 영향을 줍니다.</li><br>\n<li><b>🚫 단어로 건너뛰기:</b><br>\n쉼표로 구분된 단어(예: <i>WIP, 스케치, 미리보기</i>)를 입력하십시오.\n이 입력 옆에 있는 <b>'범위: [유형]'</b> 버튼은 이 필터가 적용되는 방식을 순환합니다:\n<ul><li><i>범위: 파일:</i> 파일 이름에 이 단어 중 하나라도 포함되어 있으면 파일을 건너뜁니다.</li><br>\n<li><i>범위: 게시물:</i> 게시물 제목에 이 단어 중 하나라도 포함되어 있으면 전체 게시물을 건너뜁니다.</li><br>\n<li><i>범위: 둘 다:</i> 파일 및 게시물 제목 건너뛰기를 모두 적용합니다(게시물 우선, 그 다음 파일).</li></ul></li><br>\n<li><b>파일 필터링 (라디오 버튼):</b> 다운로드할 항목을 선택하십시오:\n<ul>\n<li><i>전체:</i> 찾은 모든 파일 유형을 다운로드합니다.</li><br>\n<li><i>이미지/GIF:</i> 일반적인 이미지 형식 및 GIF만.</li><br>\n<li><i>비디오:</i> 일반적인 비디오 형식만.</li><br>\n<li><b><i>📦 아카이브만:</i></b> <b>.zip</b> 및 <b>.rar</b> 파일만 독점적으로 다운로드합니다. 이 옵션을 선택하면 '.zip 건너뛰기' 및 '.rar 건너뛰기' 확인란이 자동으로 비활성화되고 선택 취소됩니다. '외부 링크 표시'도 비활성화됩니다.</li><br>\n<li><i>🎧 오디오만:</i> 일반적인 오디오 형식(MP3, WAV, FLAC 등)만.</li><br>\n<li><i>🔗 링크만:</i> 파일을 다운로드하는 대신 게시물 설명에서 외부 링크를 추출하여 표시합니다. 다운로드 관련 옵션 및 '외부 링크 표시'는 비활성화됩니다.</li>\n</ul></li>\n</ul>",
    "tour_dialog_step4_title": "③ 즐겨찾기 모드 (대체 다운로드)",
    "tour_dialog_step4_content": "이 애플리케이션은 Kemono.su에서 즐겨찾기에 추가한 아티스트의 콘텐츠를 다운로드하기 위한 '즐겨찾기 모드'를 제공합니다.\n<ul>\n<li><b>⭐ 즐겨찾기 모드 확인란:</b><br>\n'🔗 링크만' 라디오 버튼 옆에 있습니다. 즐겨찾기 모드를 활성화하려면 이 확인란을 선택하십시오.</li><br>\n<li><b>즐겨찾기 모드에서 일어나는 일:</b>\n<ul><li>'🔗 Kemono 작성자/게시물 URL' 입력 영역이 즐겨찾기 모드가 활성화되었음을 나타내는 메시지로 바뀝니다.</li><br>\n<li>표준 '다운로드 시작', '일시 중지', '취소' 버튼이 '🖼️ 즐겨찾는 아티스트' 및 '📄 즐겨찾는 게시물' 버튼으로 바뀝니다(참고: '즐겨찾는 게시물'은 향후 예정).</li><br>\n<li>'🍪 쿠키 사용' 옵션은 즐겨찾기를 가져오는 데 쿠키가 필요하므로 자동으로 활성화되고 잠깁니다.</li></ul></li><br>\n<li><b>🖼️ 즐겨찾는 아티스트 버튼:</b><br>\nKemono.su에서 즐겨찾기에 추가한 아티스트 목록이 있는 대화 상자를 열려면 이 버튼을 클릭하십시오. 다운로드할 아티스트를 한 명 이상 선택할 수 있습니다.</li><br>\n<li><b>즐겨찾기 다운로드 범위 (버튼):</b><br>\n이 버튼('즐겨찾는 게시물' 옆)은 선택한 즐겨찾기가 다운로드되는 위치를 제어합니다:\n<ul><li><i>범위: 선택한 위치:</i> 선택한 모든 아티스트가 설정한 기본 '다운로드 위치'에 다운로드됩니다. 필터는 전역적으로 적용됩니다.</li><br>\n<li><i>범위: 아티스트 폴더:</i> 선택한 각 아티스트에 대해 기본 '다운로드 위치' 내에 하위 폴더(아티스트 이름)가 생성됩니다. 해당 아티스트의 콘텐츠는 특정 폴더로 이동합니다. 필터는 각 아티스트의 폴더 내에서 적용됩니다.</li></ul></li><br>\n<li><b>즐겨찾기 모드의 필터:</b><br>\n'캐릭터로 필터링', '단어로 건너뛰기' 및 '파일 필터링' 옵션은 선택한 즐겨찾는 아티스트에서 다운로드한 콘텐츠에 계속 적용됩니다.</li>\n</ul>",
    "tour_dialog_step5_title": "④ 다운로드 미세 조정",
    "tour_dialog_step5_content": "다운로드를 사용자 지정하는 추가 옵션:\n<ul>\n<li><b>.zip 건너뛰기 / .rar 건너뛰기:</b> 이러한 아카이브 파일 유형의 다운로드를 피하려면 이 확인란을 선택하십시오.\n<i>(참고: '📦 아카이브만' 필터 모드를 선택하면 비활성화되고 무시됩니다).</i></li><br>\n<li><b>✂️ 이름에서 단어 제거:</b><br>\n다운로드한 파일 이름에서 제거할 단어를 쉼표로 구분하여 입력하십시오(대소문자 구분 없음).</li><br>\n<li><b>썸네일만 다운로드:</b> 전체 크기 파일 대신 작은 미리보기 이미지를 다운로드합니다(사용 가능한 경우).</li><br>\n<li><b>대용량 이미지 압축:</b> 'Pillow' 라이브러리가 설치된 경우 WebP 버전이 훨씬 작으면 1.5MB보다 큰 이미지가 WebP 형식으로 변환됩니다.</li><br>\n<li><b>🗄️ 사용자 지정 폴더 이름 (단일 게시물만):</b><br>\n특정 단일 게시물 URL을 다운로드하고 '이름/제목별로 폴더 분리'가 활성화된 경우,\n해당 게시물의 다운로드 폴더에 대한 사용자 지정 이름을 여기에 입력할 수 있습니다.</li><br>\n<li><b>🍪 쿠키 사용:</b> 요청에 쿠키를 사용하려면 이 확인란을 선택하십시오. 다음 중 하나를 수행할 수 있습니다:\n<ul><li>쿠키 문자열을 텍스트 필드에 직접 입력하십시오(예: <i>name1=value1; name2=value2</i>).</li><br>\n<li>'찾아보기...'를 클릭하여 <i>cookies.txt</i> 파일(Netscape 형식)을 선택하십시오. 경로가 텍스트 필드에 나타납니다.</li></ul>\n이는 로그인이 필요한 콘텐츠에 액세스하는 데 유용합니다. 텍스트 필드는 채워진 경우 우선합니다.\n'쿠키 사용'이 선택되어 있지만 텍스트 필드와 찾아본 파일이 모두 비어 있으면 앱 디렉토리에서 'cookies.txt'를 로드하려고 시도합니다.</li>\n</ul>",
    "tour_dialog_step6_title": "⑤ 구성 및 성능",
    "tour_dialog_step6_content": "다운로드를 구성하고 성능을 관리하십시오:\n<ul>\n<li><b>⚙️ 이름/제목별로 폴더 분리:</b> '캐릭터로 필터링' 입력 또는 게시물 제목을 기반으로 하위 폴더를 만듭니다(<b>Known.txt</b> 목록을 폴더 이름의 대체 수단으로 사용할 수 있음).</li><br>\n<li><b>게시물당 하위 폴더:</b> '폴더 분리'가 켜져 있으면 기본 캐릭터/제목 폴더 내에 <i>각 개별 게시물</i>에 대한 추가 하위 폴더가 생성됩니다.</li><br>\n<li><b>🚀 멀티스레딩 사용 (스레드):</b> 더 빠른 작업을 활성화합니다. '스레드' 입력의 숫자는 다음을 의미합니다:\n<ul><li><b>작성자 피드:</b> 동시에 처리할 게시물 수. 각 게시물 내의 파일은 해당 작업자에 의해 순차적으로 다운로드됩니다('날짜 기반' 만화 이름 지정이 켜져 있지 않은 한, 이 경우 1개의 게시물 작업자가 강제됨).</li><br>\n<li><b>단일 게시물 URL:</b> 해당 단일 게시물에서 동시에 다운로드할 파일 수.</li></ul>\n선택하지 않으면 1개의 스레드가 사용됩니다. 스레드 수가 많으면(예: >40) 권장 사항이 표시될 수 있습니다.</li><br>\n<li><b>다중 파트 다운로드 전환 (로그 영역 오른쪽 상단):</b><br>\n<b>'다중 파트: [켜기/끄기]'</b> 버튼을 사용하여 개별 대용량 파일에 대한 다중 세그먼트 다운로드를 활성화/비활성화할 수 있습니다.\n<ul><li><b>켜기:</b> 대용량 파일(예: 비디오)의 다운로드 속도를 높일 수 있지만 작은 파일이 많은 경우 UI 끊김이나 로그 스팸이 증가할 수 있습니다. 활성화하면 권장 사항이 나타납니다. 다중 파트 다운로드가 실패하면 단일 스트림으로 다시 시도합니다.</li><br>\n<li><b>끄기 (기본값):</b> 파일은 단일 스트림으로 다운로드됩니다.</li></ul>\n'링크만' 또는 '아카이브만' 모드가 활성화된 경우 이 기능은 비활성화됩니다.</li><br>\n<li><b>📖 만화/코믹 모드 (작성자 URL만):</b> 순차적 콘텐츠에 맞게 조정되었습니다.\n<ul>\n<li>게시물을 <b>가장 오래된 것부터 최신 것까지</b> 다운로드합니다.</li><br>\n<li>모든 게시물이 가져오므로 '페이지 범위' 입력은 비활성화됩니다.</li><br>\n<li>작성자 피드에 이 모드가 활성화되면 로그 영역의 오른쪽 상단에 <b>파일 이름 스타일 전환 버튼</b>(예: '이름: 게시물 제목')이 나타납니다. 클릭하여 이름 지정 스타일을 순환하십시오:\n<ul>\n<li><b><i>이름: 게시물 제목 (기본값):</i></b> 게시물의 첫 번째 파일은 게시물의 정리된 제목(예: '내 1장.jpg')으로 이름이 지정됩니다. *동일한 게시물* 내의 후속 파일은 원래 파일 이름(예: 'page_02.png', 'bonus_art.jpg')을 유지하려고 시도합니다. 게시물에 파일이 하나만 있으면 게시물 제목으로 이름이 지정됩니다. 이는 대부분의 만화/코믹에 일반적으로 권장됩니다.</li><br>\n<li><b><i>이름: 원본 파일:</i></b> 모든 파일은 원래 파일 이름을 유지하려고 시도합니다. 스타일 버튼 옆에 나타나는 입력 필드에 선택적 접두사(예: '내 시리즈_')를 입력할 수 있습니다. 예: '내 시리즈_원본 파일.jpg'.</li><br>\n<li><b><i>이름: 제목+전역 번호 (게시물 제목 + 전역 번호 매기기):</i></b> 현재 다운로드 세션의 모든 게시물에 있는 모든 파일은 게시물의 정리된 제목을 접두사로 사용하고 전역 카운터를 사용하여 순차적으로 이름이 지정됩니다. 예: 게시물 '1장' (파일 2개) -> '1장_001.jpg', '1장_002.png'. 다음 게시물 '2장' (파일 1개)은 번호 매기기를 계속합니다 -> '2장_003.jpg'. 올바른 전역 번호 매기기를 보장하기 위해 이 스타일에 대한 게시물 처리 멀티스레딩은 자동으로 비활성화됩니다.</li><br>\n<li><b><i>이름: 날짜 기반:</i></b> 파일은 게시물 게시 순서에 따라 순차적으로 이름이 지정됩니다(001.ext, 002.ext, ...). 스타일 버튼 옆에 나타나는 입력 필드에 선택적 접두사(예: '내 시리즈_')를 입력할 수 있습니다. 예: '내 시리즈_001.jpg'. 이 스타일에 대한 게시물 처리 멀티스레딩은 자동으로 비활성화됩니다.</li>\n</ul>\n</li><br>\n<li>'이름: 게시물 제목', '이름: 제목+전역 번호' 또는 '이름: 날짜 기반' 스타일로 최상의 결과를 얻으려면 폴더 구성을 위해 '캐릭터로 필터링' 필드를 만화/시리즈 제목과 함께 사용하십시오.</li>\n</ul></li><br>\n<li><b>🎭 스마트 폴더 구성을 위한 Known.txt:</b><br>\n<code>Known.txt</code>(앱 디렉토리 내)는 '이름/제목별로 폴더 분리'가 활성화된 경우 자동 폴더 구성에 대한 세분화된 제어를 허용합니다.\n<ul>\n<li><b>작동 방식:</b> <code>Known.txt</code>의 각 줄은 항목입니다.\n<ul><li><code>내 멋진 시리즈</code>와 같은 간단한 줄은 이와 일치하는 콘텐츠가 '내 멋진 시리즈'라는 폴더로 이동함을 의미합니다.</li><br>\n<li><code>(캐릭터 A, 캐릭 A, 대체 이름 A)</code>와 같은 그룹화된 줄은 '캐릭터 A', '캐릭 A' 또는 '대체 이름 A'와 일치하는 콘텐츠가 모두 '캐릭터 A 캐릭 A 대체 이름 A'라는 단일 폴더(정리 후)로 이동함을 의미합니다. 괄호 안의 모든 용어는 해당 폴더의 별칭이 됩니다.</li></ul></li>\n<li><b>지능형 대체:</b> '이름/제목별로 폴더 분리'가 활성화되어 있고 게시물이 특정 '캐릭터로 필터링' 입력과 일치하지 않는 경우 다운로더는 <code>Known.txt</code>를 참조하여 폴더 생성을 위한 일치하는 기본 이름을 찾습니다.</li><br>\n<li><b>사용자 친화적인 관리:</b> 아래 UI 목록을 통해 간단한(그룹화되지 않은) 이름을 추가하십시오. 고급 편집(예: 그룹화된 별칭 생성/수정)의 경우 텍스트 편집기에서 파일을 편집하려면 <b>'Known.txt 열기'</b>를 클릭하십시오. 앱은 다음에 사용하거나 시작할 때 다시 로드합니다.</li>\n</ul>\n</li>\n</ul>",
    "tour_dialog_step7_title": "⑥ 일반적인 오류 및 문제 해결",
    "tour_dialog_step7_content": "때때로 다운로드에 문제가 발생할 수 있습니다. 다음은 몇 가지 일반적인 문제입니다:\n<ul>\n<li><b>캐릭터 입력 도구 설명:</b><br>\n캐릭터 이름을 쉼표로 구분하여 입력하십시오(예: <i>Tifa, Aerith</i>).<br>\n결합된 폴더 이름에 대한 별칭 그룹화: <i>(별칭1, 별칭2, 별칭3)</i>은 '별칭1 별칭2 별칭3' 폴더가 됩니다.<br>\n그룹의 모든 이름은 콘텐츠 일치를 위한 별칭으로 사용됩니다.<br><br>\n이 입력 옆에 있는 '필터: [유형]' 버튼은 이 필터가 적용되는 방식을 순환합니다:<br>\n- 필터: 파일: 개별 파일 이름을 확인합니다. 일치하는 파일만 다운로드됩니다.<br>\n- 필터: 제목: 게시물 제목을 확인합니다. 일치하는 게시물의 모든 파일이 다운로드됩니다.<br>\n- 필터: 둘 다: 먼저 게시물 제목을 확인합니다. 일치하지 않으면 파일 이름을 확인합니다.<br>\n- 필터: 댓글 (베타): 먼저 파일 이름을 확인합니다. 일치하지 않으면 게시물 댓글을 확인합니다.<br><br>\n이 필터는 '이름/제목별로 폴더 분리'가 활성화된 경우 폴더 이름 지정에도 영향을 줍니다.</li><br>\n<li><b>502 잘못된 게이트웨이 / 503 서비스를 사용할 수 없음 / 504 게이트웨이 시간 초과:</b><br>\n이는 일반적으로 Kemono/Coomer의 일시적인 서버 측 문제를 나타냅니다. 사이트가 과부하되었거나 유지 보수 중이거나 문제가 있을 수 있습니다.<br>\n<b>해결책:</b> 잠시 기다렸다가(예: 30분에서 몇 시간) 나중에 다시 시도하십시오. 브라우저에서 직접 사이트를 확인하십시오.</li><br>\n<li><b>연결 끊김 / 연결 거부 / 시간 초과 (파일 다운로드 중):</b><br>\n이는 인터넷 연결, 서버 불안정 또는 서버가 대용량 파일에 대한 연결을 끊는 경우 발생할 수 있습니다.<br>\n<b>해결책:</b> 인터넷을 확인하십시오. '스레드' 수가 많으면 줄여 보십시오. 앱은 세션이 끝날 때 일부 실패한 파일을 다시 시도하라는 메시지를 표시할 수 있습니다.</li><br>\n<li><b>IncompleteRead 오류:</b><br>\n서버가 예상보다 적은 데이터를 보냈습니다. 종종 일시적인 네트워크 문제 또는 서버 문제입니다.<br>\n<b>해결책:</b> 앱은 종종 다운로드 세션이 끝날 때 다시 시도하도록 이러한 파일을 표시합니다.</li><br>\n<li><b>403 금지됨 / 401 인증되지 않음 (공개 게시물에는 덜 일반적):</b><br>\n콘텐츠에 액세스할 권한이 없을 수 있습니다. 일부 유료 또는 비공개 콘텐츠의 경우 브라우저 세션의 유효한 쿠키와 함께 '쿠키 사용' 옵션을 사용하면 도움이 될 수 있습니다. 쿠키가 최신 상태인지 확인하십시오.</li><br>\n<li><b>404 찾을 수 없음:</b><br>\n게시물 또는 파일 URL이 잘못되었거나 콘텐츠가 사이트에서 제거되었습니다. URL을 다시 확인하십시오.</li><br>\n<li><b>'게시물을 찾을 수 없음' / '대상 게시물을 찾을 수 없음':</b><br>\nURL이 올바르고 작성자/게시물이 존재하는지 확인하십시오. 페이지 범위를 사용하는 경우 작성자에게 유효한지 확인하십시오. 매우 새로운 게시물의 경우 API에 나타나기까지 약간의 지연이 있을 수 있습니다.</li><br>\n<li><b>일반적인 느림 / 앱 '(응답 없음)':</b><br>\n1단계에서 언급했듯이 앱이 시작 후 중단된 것처럼 보이면, 특히 대규모 작성자 피드나 많은 스레드가 있는 경우 시간을 주십시오. 백그라운드에서 데이터를 처리하고 있을 가능성이 높습니다. 스레드 수를 줄이면 이러한 현상이 자주 발생하는 경우 응답성이 향상될 수 있습니다.</li>\n</ul>",
    "tour_dialog_step8_title": "⑦ 로그 및 최종 제어",
    "tour_dialog_step8_content": "모니터링 및 제어:\n<ul>\n<li><b>📜 진행률 로그 / 추출된 링크 로그:</b> 자세한 다운로드 메시지를 표시합니다. '🔗 링크만' 모드가 활성화된 경우 이 영역에 추출된 링크가 표시됩니다.</li><br>\n<li><b>로그에 외부 링크 표시:</b> 선택하면 주 로그 패널 아래에 보조 로그 패널이 나타나 게시물 설명에서 찾은 외부 링크를 표시합니다. <i>('🔗 링크만' 또는 '📦 아카이브만' 모드가 활성화된 경우 비활성화됨).</i></li><br>\n<li><b>로그 보기 전환 (👁️ / 🙈 버튼):</b><br>\n이 버튼(로그 영역 오른쪽 상단)은 주 로그 보기를 전환합니다:\n<ul><li><b>👁️ 진행률 로그 (기본값):</b> 모든 다운로드 활동, 오류 및 요약을 표시합니다.</li><br>\n<li><b>🙈 누락된 캐릭터 로그:</b> '캐릭터로 필터링' 설정으로 인해 건너뛴 게시물 제목의 주요 용어 목록을 표시합니다. 의도치 않게 놓치고 있는 콘텐츠를 식별하는 데 유용합니다.</li></ul></li><br>\n<li><b>🔄 재설정:</b> 모든 입력 필드, 로그를 지우고 임시 설정을 기본값으로 재설정합니다. 다운로드가 활성화되어 있지 않을 때만 사용할 수 있습니다.</li><br>\n<li><b>⬇️ 다운로드 시작 / 🔗 링크 추출 / ⏸️ 일시 중지 / ❌ 취소:</b> 이러한 버튼은 프로세스를 제어합니다. '취소 및 UI 재설정'은 현재 작업을 중지하고 URL 및 디렉토리 입력을 보존하면서 소프트 UI 재설정을 수행합니다. '일시 중지/재개'를 사용하면 일시적으로 중단하고 계속할 수 있습니다.</li><br>\n<li>일부 파일이 복구 가능한 오류('IncompleteRead' 등)로 실패하면 세션이 끝날 때 다시 시도하라는 메시지가 표시될 수 있습니다.</li>\n</ul>\n<br>모두 준비되었습니다! 둘러보기를 닫고 다운로더 사용을 시작하려면 <b>'완료'</b>를 클릭하십시오.",
    "help_guide_dialog_title": "Kemono Downloader - 기능 가이드",
    "help_guide_github_tooltip": "프로젝트의 GitHub 페이지 방문 (브라우저에서 열림)",
    "help_guide_instagram_tooltip": "인스타그램 페이지 방문 (브라우저에서 열림)",
    "help_guide_discord_tooltip": "Discord 커뮤니티 방문 (브라우저에서 열림)",
    "help_guide_step1_title": "① 소개 및 주요 입력",
    "help_guide_step1_content": "<html><head/><body>\n<p>이 가이드는 Kemono Downloader의 기능, 필드 및 버튼에 대한 개요를 제공합니다.</p>\n<h3>주요 입력 영역 (왼쪽 상단)</h3>\n<ul>\n<li><b>🔗 Kemono 작성자/게시물 URL:</b>\n<ul>\n<li>작성자 페이지의 전체 웹 주소(예: <i>https://kemono.su/patreon/user/12345</i>) 또는 특정 게시물(예: <i>.../post/98765</i>)을 입력하십시오.</li>\n<li>Kemono(kemono.su, kemono.party) 및 Coomer(coomer.su, coomer.party) URL을 지원합니다.</li>\n</ul>\n</li>\n<li><b>페이지 범위 (시작부터 끝까지):</b>\n<ul>\n<li>작성자 URL의 경우: 가져올 페이지 범위(예: 2-5페이지)를 지정하십시오. 모든 페이지에 대해 비워두십시오.</li>\n<li>단일 게시물 URL 또는 <b>만화/코믹 모드</b>가 활성화된 경우 비활성화됩니다.</li>\n</ul>\n</li>\n<li><b>📁 다운로드 위치:</b>\n<ul>\n<li><b>'찾아보기...'</b>를 클릭하여 다운로드한 모든 파일이 저장될 컴퓨터의 기본 폴더를 선택하십시오.</li>\n<li>'<b>🔗 링크만</b>' 모드를 사용하지 않는 한 이 필드는 필수입니다.</li>\n</ul>\n</li>\n<li><b>🎨 작성자 선택 버튼 (URL 입력 옆):</b>\n<ul>\n<li>팔레트 아이콘(🎨)을 클릭하여 '작성자 선택' 대화 상자를 엽니다.</li>\n<li>이 대화 상자는 <code>creators.json</code> 파일(애플리케이션 디렉토리에 있어야 함)에서 작성자를 로드합니다.</li>\n<li><b>대화 상자 내부:</b>\n<ul>\n<li><b>검색 창:</b> 이름이나 서비스로 작성자 목록을 필터링하려면 입력하십시오.</li>\n<li><b>작성자 목록:</b> <code>creators.json</code>의 작성자를 표시합니다. '즐겨찾기'에 추가한 작성자(JSON 데이터)가 맨 위에 표시됩니다.</li>\n<li><b>확인란:</b> 이름 옆에 있는 상자를 선택하여 한 명 이상의 작성자를 선택하십시오.</li>\n<li><b>'범위' 버튼 (예: '범위: 캐릭터'):</b> 이 버튼은 이 팝업에서 다운로드를 시작할 때 다운로드 구성을 전환합니다:\n<ul><li><i>범위: 캐릭터:</i> 다운로드는 기본 '다운로드 위치' 내에서 직접 캐릭터 이름의 폴더로 구성됩니다. 동일한 캐릭터에 대한 다른 작성자의 작품이 함께 그룹화됩니다.</li>\n<li><i>범위: 작성자:</i> 다운로드는 먼저 기본 '다운로드 위치' 내에 작성자 이름의 폴더를 만듭니다. 그런 다음 각 작성자의 폴더 내에 캐릭터 이름의 하위 폴더가 생성됩니다.</li></ul>\n</li>\n<li><b>'선택 항목 추가' 버튼:</b> 이 버튼을 클릭하면 선택한 모든 작성자의 이름을 가져와 쉼표로 구분하여 기본 '🔗 Kemono 작성자/게시물 URL' 입력 필드에 추가합니다. 그런 다음 대화 상자가 닫힙니다.</li>\n</ul>\n</li>\n<li>이 기능은 각 URL을 수동으로 입력하거나 붙여넣지 않고도 여러 작성자에 대한 URL 필드를 빠르게 채울 수 있는 방법을 제공합니다.</li>\n</ul>\n</li>\n</ul></body></html>",
    "help_guide_step2_title": "② 다운로드 필터링",
    "help_guide_step2_content": "<html><head/><body>\n<h3>다운로드 필터링 (왼쪽 패널)</h3>\n<ul>\n<li><b>🎯 캐릭터로 필터링:</b>\n<ul>\n<li>이름을 쉼표로 구분하여 입력하십시오(예: <code>Tifa, Aerith</code>).</li>\n<li><b>공유 폴더에 대한 그룹화된 별칭 (별도의 Known.txt 항목):</b> <code>(Vivi, Ulti, Uta)</code>.\n<ul><li>'Vivi', 'Ulti' 또는 'Uta'와 일치하는 콘텐츠는 'Vivi Ulti Uta'라는 공유 폴더로 이동합니다(정리 후).</li>\n<li>이 이름이 새 이름이면 'Vivi', 'Ulti' 및 'Uta'를 <code>Known.txt</code>에 <i>별도의 개별 항목</i>으로 추가하라는 메시지가 표시됩니다.</li>\n</ul>\n</li>\n<li><b>공유 폴더에 대한 그룹화된 별칭 (단일 Known.txt 항목):</b> <code>(Yuffie, Sonon)~</code> (물결표 <code>~</code> 참고).\n<ul><li>'Yuffie' 또는 'Sonon'과 일치하는 콘텐츠는 'Yuffie Sonon'이라는 공유 폴더로 이동합니다.</li>\n<li>새로운 경우 'Yuffie Sonon'(별칭 Yuffie, Sonon 포함)을 <code>Known.txt</code>에 <i>단일 그룹 항목</i>으로 추가하라는 메시지가 표시됩니다.</li>\n</ul>\n</li>\n<li>이 필터는 '이름/제목별로 폴더 분리'가 활성화된 경우 폴더 이름 지정에 영향을 줍니다.</li>\n</ul>\n</li>\n<li><b>필터: [유형] 버튼 (캐릭터 필터 범위):</b> '캐릭터로 필터링'이 적용되는 방식을 순환합니다:\n<ul>\n<li><code>필터: 파일</code>: 개별 파일 이름을 확인합니다. 파일이 하나라도 일치하면 게시물이 유지됩니다. 일치하는 파일만 다운로드됩니다. 폴더 이름 지정은 일치하는 파일 이름의 캐릭터를 사용합니다.</li>\n<li><code>필터: 제목</code>: 게시물 제목을 확인합니다. 일치하는 게시물의 모든 파일이 다운로드됩니다. 폴더 이름 지정은 일치하는 게시물 제목의 캐릭터를 사용합니다.</li>\n<li><code>필터: 둘 다</code>: 먼저 게시물 제목을 확인합니다. 일치하면 모든 파일이 다운로드됩니다. 일치하지 않으면 파일 이름을 확인하고 일치하는 파일만 다운로드됩니다. 폴더 이름 지정은 제목 일치를 우선으로 하고 그 다음 파일 일치를 따릅니다.</li>\n<li><code>필터: 댓글 (베타)</code>: 먼저 파일 이름을 확인합니다. 파일이 일치하면 게시물의 모든 파일이 다운로드됩니다. 파일이 일치하지 않으면 게시물 댓글을 확인합니다. 댓글이 일치하면 모든 파일이 다운로드됩니다. (더 많은 API 요청을 사용합니다). 폴더 이름 지정은 파일 일치를 우선으로 하고 그 다음 댓글 일치를 따릅니다.</li>\n</ul>\n</li>\n<li><b>🗄️ 사용자 지정 폴더 이름 (단일 게시물만):</b>\n<ul>\n<li>단일 특정 게시물 URL을 다운로드하고 '이름/제목별로 폴더 분리'가 활성화된 경우에만 표시되고 사용할 수 있습니다.</li>\n<li>해당 단일 게시물의 다운로드 폴더에 대한 사용자 지정 이름을 지정할 수 있습니다.</li>\n</ul>\n</li>\n<li><b>🚫 단어로 건너뛰기:</b>\n<ul><li>특정 콘텐츠를 건너뛰려면 쉼표로 구분된 단어(예: <code>WIP, 스케치, 미리보기</code>)를 입력하십시오.</li></ul>\n</li>\n<li><b>범위: [유형] 버튼 (단어 건너뛰기 범위):</b> '단어로 건너뛰기'가 적용되는 방식을 순환합니다:\n<ul>\n<li><code>범위: 파일</code>: 파일 이름에 이 단어 중 하나라도 포함되어 있으면 개별 파일을 건너뜁니다.</li>\n<li><code>범위: 게시물</code>: 게시물 제목에 이 단어 중 하나라도 포함되어 있으면 전체 게시물을 건너뜁니다.</li>\n<li><code>범위: 둘 다</code>: 둘 다 적용합니다 (게시물 제목이 먼저, 그 다음 개별 파일).</li>\n</ul>\n</li>\n<li><b>✂️ 이름에서 단어 제거:</b>\n<ul><li>다운로드한 파일 이름에서 제거할 단어를 쉼표로 구분하여 입력하십시오(대소문자 구분 없음).</li></ul>\n</li>\n<li><b>파일 필터링 (라디오 버튼):</b> 다운로드할 항목을 선택하십시오:\n<ul>\n<li><code>전체</code>: 찾은 모든 파일 유형을 다운로드합니다.</li>\n<li><code>이미지/GIF</code>: 일반적인 이미지 형식(JPG, PNG, GIF, WEBP 등) 및 GIF만.</li>\n<li><code>비디오</code>: 일반적인 비디오 형식(MP4, MKV, WEBM, MOV 등)만.</li>\n<li><code>📦 아카이브만</code>: <b>.zip</b> 및 <b>.rar</b> 파일만 독점적으로 다운로드합니다. 이 옵션을 선택하면 '.zip 건너뛰기' 및 '.rar 건너뛰기' 확인란이 자동으로 비활성화되고 선택 취소됩니다. '외부 링크 표시'도 비활성화됩니다.</li>\n<li><code>🎧 오디오만</code>: 일반적인 오디오 형식(MP3, WAV, FLAC, M4A, OGG 등)만 다운로드합니다. 다른 파일 관련 옵션은 '이미지' 또는 '비디오' 모드와 동일하게 작동합니다.</li>\n<li><code>🔗 링크만</code>: 파일을 다운로드하는 대신 게시물 설명에서 외부 링크를 추출하여 표시합니다. 다운로드 관련 옵션 및 '외부 링크 표시'는 비활성화됩니다. 기본 다운로드 버튼이 '🔗 링크 추출'로 변경됩니다.</li>\n</ul>\n</li>\n</ul></body></html>",
    "help_guide_step3_title": "③ 다운로드 옵션 및 설정",
    "help_guide_step3_content": "<html><head/><body>\n<h3>다운로드 옵션 및 설정 (왼쪽 패널)</h3>\n<ul>\n<li><b>.zip 건너뛰기 / .rar 건너뛰기:</b> 이러한 아카이브 파일 유형의 다운로드를 피하기 위한 확인란. ('📦 아카이브만' 필터 모드를 선택하면 비활성화되고 무시됨).</li>\n<li><b>썸네일만 다운로드:</b> 전체 크기 파일 대신 작은 미리보기 이미지를 다운로드합니다(사용 가능한 경우).</li>\n<li><b>대용량 이미지 압축 (WebP로):</b> 'Pillow'(PIL) 라이브러리가 설치된 경우 WebP 버전이 훨씬 작으면 1.5MB보다 큰 이미지가 WebP 형식으로 변환됩니다.</li>\n<li><b>⚙️ 고급 설정:</b>\n<ul>\n<li><b>이름/제목별로 폴더 분리:</b> '캐릭터로 필터링' 입력 또는 게시물 제목을 기반으로 하위 폴더를 만듭니다. <b>Known.txt</b> 목록을 폴더 이름의 대체 수단으로 사용할 수 있습니다.</li></ul></li></ul></body></html>",
    "help_guide_step4_title": "④ 고급 설정 (1부)",
    "help_guide_step4_content": "<html><head/><body><h3>⚙️ 고급 설정 (계속)</h3><ul><ul>\n<li><b>게시물당 하위 폴더:</b> '폴더 분리'가 켜져 있으면 기본 캐릭터/제목 폴더 내에 <i>각 개별 게시물</i>에 대한 추가 하위 폴더가 생성됩니다.</li>\n<li><b>쿠키 사용:</b> 요청에 쿠키를 사용하려면 이 확인란을 선택하십시오.\n<ul>\n<li><b>텍스트 필드:</b> 쿠키 문자열을 직접 입력하십시오(예: <code>name1=value1; name2=value2</code>).</li>\n<li><b>찾아보기...:</b> <code>cookies.txt</code> 파일(Netscape 형식)을 선택하십시오. 경로가 텍스트 필드에 나타납니다.</li>\n<li><b>우선 순위:</b> 텍스트 필드(채워진 경우)가 찾아본 파일보다 우선합니다. '쿠키 사용'이 선택되어 있지만 둘 다 비어 있으면 앱 디렉토리에서 <code>cookies.txt</code>를 로드하려고 시도합니다.</li>\n</ul>\n</li>\n<li><b>멀티스레딩 사용 및 스레드 입력:</b>\n<ul>\n<li>더 빠른 작업을 활성화합니다. '스레드' 입력의 숫자는 다음을 의미합니다:\n<ul>\n<li><b>작성자 피드:</b> 동시에 처리할 게시물 수. 각 게시물 내의 파일은 해당 작업자에 의해 순차적으로 다운로드됩니다('날짜 기반' 만화 이름 지정이 켜져 있지 않은 한, 이 경우 1개의 게시물 작업자가 강제됨).</li>\n<li><b>단일 게시물 URL:</b> 해당 단일 게시물에서 동시에 다운로드할 파일 수.</li>\n</ul>\n</li>\n<li>선택하지 않으면 1개의 스레드가 사용됩니다. 스레드 수가 많으면(예: >40) 권장 사항이 표시될 수 있습니다.</li>\n</ul>\n</li></ul></ul></body></html>",
    "help_guide_step5_title": "⑤ 고급 설정 (2부) 및 작업",
    "help_guide_step5_content": "<html><head/><body><h3>⚙️ 고급 설정 (계속)</h3><ul><ul>\n<li><b>로그에 외부 링크 표시:</b> 선택하면 주 로그 패널 아래에 보조 로그 패널이 나타나 게시물 설명에서 찾은 외부 링크를 표시합니다. ('🔗 링크만' 또는 '📦 아카이브만' 모드가 활성화된 경우 비활성화됨).</li>\n<li><b>📖 만화/코믹 모드 (작성자 URL만):</b> 순차적 콘텐츠에 맞게 조정되었습니다.\n<ul>\n<li>게시물을 <b>가장 오래된 것부터 최신 것까지</b> 다운로드합니다.</li>\n<li>모든 게시물이 가져오므로 '페이지 범위' 입력은 비활성화됩니다.</li>\n<li>작성자 피드에 이 모드가 활성화되면 로그 영역의 오른쪽 상단에 <b>파일 이름 스타일 전환 버튼</b>(예: '이름: 게시물 제목')이 나타납니다. 클릭하여 이름 지정 스타일을 순환하십시오:\n<ul>\n<li><code>이름: 게시물 제목 (기본값)</code>: 게시물의 첫 번째 파일은 게시물의 정리된 제목(예: '내 1장.jpg')으로 이름이 지정됩니다. *동일한 게시물* 내의 후속 파일은 원래 파일 이름(예: 'page_02.png', 'bonus_art.jpg')을 유지하려고 시도합니다. 게시물에 파일이 하나만 있으면 게시물 제목으로 이름이 지정됩니다. 이는 대부분의 만화/코믹에 일반적으로 권장됩니다.</li>\n<li><code>이름: 원본 파일</code>: 모든 파일은 원래 파일 이름을 유지하려고 시도합니다.</li>\n<li><code>이름: 원본 파일</code>: 모든 파일은 원래 파일 이름을 유지하려고 시도합니다. 이 스타일이 활성화되면 이 스타일 버튼 옆에 <b>선택적 파일 이름 접두사</b>(예: '내 시리즈_')에 대한 입력 필드가 나타납니다. 예: '내 시리즈_원본 파일.jpg'.</li>\n<li><code>이름: 제목+전역 번호 (게시물 제목 + 전역 번호 매기기)</code>: 현재 다운로드 세션의 모든 게시물에 있는 모든 파일은 게시물의 정리된 제목을 접두사로 사용하고 전역 카운터를 사용하여 순차적으로 이름이 지정됩니다. 예: 게시물 '1장' (파일 2개) -> '1장 001.jpg', '1장 002.png'. 다음 게시물 '2장' (파일 1개) -> '2장 003.jpg'. 올바른 전역 번호 매기기를 보장하기 위해 이 스타일에 대한 게시물 처리 멀티스레딩은 자동으로 비활성화됩니다.</li>\n<li><code>이름: 날짜 기반</code>: 파일은 게시물 게시 순서에 따라 순차적으로 이름이 지정됩니다(001.ext, 002.ext, ...). 이 스타일이 활성화되면 이 스타일 버튼 옆에 <b>선택적 파일 이름 접두사</b>(예: '내 시리즈_')에 대한 입력 필드가 나타납니다. 예: '내 시리즈_001.jpg'. 이 스타일에 대한 게시물 처리 멀티스레딩은 자동으로 비활성화됩니다.</li>\n</ul>\n</li>\n<li>'이름: 게시물 제목', '이름: 제목+전역 번호' 또는 '이름: 날짜 기반' 스타일로 최상의 결과를 얻으려면 폴더 구성을 위해 '캐릭터로 필터링' 필드를 만화/시리즈 제목과 함께 사용하십시오.</li>\n</ul>\n</li>\n</ul></li></ul>\n<h3>주요 작업 버튼 (왼쪽 패널)</h3>\n<ul>\n<li><b>⬇️ 다운로드 시작 / 🔗 링크 추출:</b> 이 버튼의 텍스트와 기능은 '파일 필터링' 라디오 버튼 선택에 따라 변경됩니다. 주요 작업을 시작합니다.</li>\n<li><b>⏸️ 다운로드 일시 중지 / ▶️ 다운로드 재개:</b> 현재 다운로드/추출 프로세스를 일시적으로 중단하고 나중에 재개할 수 있습니다. 일시 중지된 동안 일부 UI 설정을 변경할 수 있습니다.</li>\n<li><b>❌ 취소 및 UI 재설정:</b> 현재 작업을 중지하고 소프트 UI 재설정을 수행합니다. URL 및 다운로드 디렉토리 입력은 보존되지만 다른 설정 및 로그는 지워집니다.</li>\n</ul></body></html>",
    "help_guide_step6_title": "⑥ 알려진 프로그램/캐릭터 목록",
    "help_guide_step6_content": "<html><head/><body>\n<h3>알려진 프로그램/캐릭터 목록 관리 (왼쪽 하단)</h3>\n<p>이 섹션은 '이름/제목별로 폴더 분리'가 활성화된 경우 스마트 폴더 구성을 위해 사용되는 <code>Known.txt</code> 파일을 관리하는 데 도움이 됩니다. 특히 게시물이 활성 '캐릭터로 필터링' 입력과 일치하지 않는 경우 대체 수단으로 사용됩니다.</p>\n<ul>\n<li><b>Known.txt 열기:</b> 기본 텍스트 편집기에서 <code>Known.txt</code> 파일(앱 디렉토리에 있음)을 열어 고급 편집(예: 복잡한 그룹화된 별칭 생성)을 수행합니다.</li>\n<li><b>캐릭터 검색...:</b> 아래에 표시된 알려진 이름 목록을 필터링합니다.</li>\n<li><b>목록 위젯:</b> <code>Known.txt</code>의 기본 이름을 표시합니다. 여기에서 항목을 선택하여 삭제하십시오.</li>\n<li><b>새 프로그램/캐릭터 이름 추가 (입력 필드):</b> 추가할 이름이나 그룹을 입력하십시오.\n<ul>\n<li><b>간단한 이름:</b> 예: <code>내 멋진 시리즈</code>. 단일 항목으로 추가됩니다.</li>\n<li><b>별도의 Known.txt 항목에 대한 그룹:</b> 예: <code>(Vivi, Ulti, Uta)</code>. 'Vivi', 'Ulti' 및 'Uta'를 <code>Known.txt</code>에 세 개의 별도 개별 항목으로 추가합니다.</li>\n<li><b>공유 폴더 및 단일 Known.txt 항목에 대한 그룹 (물결표 <code>~</code>):</b> 예: <code>(캐릭터 A, 캐릭 A)~</code>. <code>Known.txt</code>에 '캐릭터 A 캐릭 A'라는 하나의 항목을 추가합니다. '캐릭터 A'와 '캐릭 A'는 이 단일 폴더/항목의 별칭이 됩니다.</li>\n</ul>\n</li>\n<li><b>➕ 추가 버튼:</b> 위 입력 필드의 이름/그룹을 목록과 <code>Known.txt</code>에 추가합니다.</li>\n<li><b>⤵️ 필터에 추가 버튼:</b>\n<ul>\n<li>'알려진 프로그램/캐릭터' 목록의 '➕ 추가' 버튼 옆에 있습니다.</li>\n<li>이 버튼을 클릭하면 <code>Known.txt</code> 파일의 모든 이름이 각각 확인란과 함께 표시되는 팝업 창이 열립니다.</li>\n<li>팝업에는 이름 목록을 빠르게 필터링하기 위한 검색 창이 포함되어 있습니다.</li>\n<li>확인란을 사용하여 하나 이상의 이름을 선택할 수 있습니다.</li>\n<li>'선택 항목 추가'를 클릭하여 선택한 이름을 기본 창의 '캐릭터로 필터링' 입력 필드에 삽입하십시오.</li>\n<li><code>Known.txt</code>에서 선택한 이름이 원래 그룹인 경우(예: Known.txt에서 <code>(Boa, Hancock)</code>으로 정의됨), <code>(Boa, Hancock)~</code>로 필터 필드에 추가됩니다. 간단한 이름은 그대로 추가됩니다.</li>\n<li>편의를 위해 팝업에서 '모두 선택' 및 '모두 선택 해제' 버튼을 사용할 수 있습니다.</li>\n<li>변경 없이 팝업을 닫으려면 '취소'를 클릭하십시오.</li>\n</ul>\n</li>\n<li><b>🗑️ 선택 항목 삭제 버튼:</b> 목록과 <code>Known.txt</code>에서 선택한 이름을 삭제합니다.</li>\n<li><b>❓ 버튼 (바로 이것!):</b> 이 포괄적인 도움말 가이드를 표시합니다.</li>\n</ul></body></html>",
    "help_guide_step7_title": "⑦ 로그 영역 및 제어",
    "help_guide_step7_content": "<html><head/><body>\n<h3>로그 영역 및 제어 (오른쪽 패널)</h3>\n<ul>\n<li><b>📜 진행률 로그 / 추출된 링크 로그 (레이블):</b> 기본 로그 영역의 제목, '🔗 링크만' 모드가 활성화된 경우 변경됩니다.</li>\n<li><b>링크 검색... / 🔍 버튼 (링크 검색):</b>\n<ul><li>'🔗 링크만' 모드가 활성화된 경우에만 표시됩니다. 기본 로그에 표시된 추출된 링크를 텍스트, URL 또는 플랫폼으로 실시간 필터링할 수 있습니다.</li></ul>\n</li>\n<li><b>이름: [스타일] 버튼 (만화 파일 이름 스타일):</b>\n<ul><li>작성자 피드에 대해 <b>만화/코믹 모드</b>가 활성화되어 있고 '링크만' 또는 '아카이브만' 모드가 아닌 경우에만 표시됩니다.</li>\n<li>파일 이름 스타일을 순환합니다: <code>게시물 제목</code>, <code>원본 파일</code>, <code>날짜 기반</code>. (자세한 내용은 만화/코믹 모드 섹션 참조).</li>\n<li>'원본 파일' 또는 '날짜 기반' 스타일이 활성화되면 이 버튼 옆에 <b>선택적 파일 이름 접두사</b>에 대한 입력 필드가 나타납니다.</li>\n</ul>\n</li>\n<li><b>다중 파트: [켜기/끄기] 버튼:</b>\n<ul><li>개별 대용량 파일에 대한 다중 세그먼트 다운로드를 전환합니다.\n<ul><li><b>켜기:</b> 대용량 파일(예: 비디오)의 다운로드 속도를 높일 수 있지만 작은 파일이 많은 경우 UI 끊김이나 로그 스팸이 증가할 수 있습니다. 활성화하면 권장 사항이 나타납니다. 다중 파트 다운로드가 실패하면 단일 스트림으로 다시 시도합니다.</li>\n<li><b>끄기 (기본값):</b> 파일은 단일 스트림으로 다운로드됩니다.</li>\n</ul>\n<li>'🔗 링크만' 또는 '📦 아카이브만' 모드가 활성화된 경우 비활성화됩니다.</li>\n</ul>\n</li>\n<li><b>👁️ / 🙈 버튼 (로그 보기 전환):</b> 기본 로그 보기를 전환합니다:\n<ul>\n<li><b>👁️ 진행률 로그 (기본값):</b> 모든 다운로드 활동, 오류 및 요약을 표시합니다.</li>\n<li><b>🙈 누락된 캐릭터 로그:</b> '캐릭터로 필터링' 설정으로 인해 건너뛴 게시물 제목/콘텐츠의 주요 용어 목록을 표시합니다. 의도치 않게 놓치고 있는 콘텐츠를 식별하는 데 유용합니다.</li>\n</ul>\n</li>\n<li><b>🔄 재설정 버튼:</b> 모든 입력 필드, 로그를 지우고 임시 설정을 기본값으로 재설정합니다. 다운로드가 활성화되어 있지 않을 때만 사용할 수 있습니다.</li>\n<li><b>기본 로그 출력 (텍스트 영역):</b> 자세한 진행률 메시지, 오류 및 요약을 표시합니다. '🔗 링크만' 모드가 활성화된 경우 이 영역에 추출된 링크가 표시됩니다.</li>\n<li><b>누락된 캐릭터 로그 출력 (텍스트 영역):</b> (👁️ / 🙈 토글을 통해 볼 수 있음) 캐릭터 필터로 인해 건너뛴 게시물/파일을 표시합니다.</li>\n<li><b>외부 로그 출력 (텍스트 영역):</b> '로그에 외부 링크 표시'가 선택된 경우 기본 로그 아래에 나타납니다. 게시물 설명에서 찾은 외부 링크를 표시합니다.</li>\n<li><b>링크 내보내기 버튼:</b>\n<ul><li>'🔗 링크만' 모드가 활성화되어 있고 링크가 추출된 경우에만 표시되고 활성화됩니다.</li>\n<li>추출된 모든 링크를 <code>.txt</code> 파일에 저장할 수 있습니다.</li>\n</ul>\n</li>\n<li><b>진행률: [상태] 레이블:</b> 다운로드 또는 링크 추출 프로세스의 전체 진행률(예: 처리된 게시물)을 표시합니다.</li>\n<li><b>파일 진행률 레이블:</b> 속도 및 크기 또는 다중 파트 다운로드 상태를 포함하여 개별 파일 다운로드의 진행률을 표시합니다.</li>\n</ul></body></html>",
    "help_guide_step8_title": "⑧ 즐겨찾기 모드 및 향후 기능",
    "help_guide_step8_content": "<html><head/><body>\n<h3>즐겨찾기 모드 (Kemono.su 즐겨찾기에서 다운로드)</h3>\n<p>이 모드를 사용하면 Kemono.su에서 즐겨찾기에 추가한 아티스트의 콘텐츠를 직접 다운로드할 수 있습니다.</p>\n<ul>\n<li><b>⭐ 활성화 방법:</b>\n<ul>\n<li>'🔗 링크만' 라디오 버튼 옆에 있는 <b>'⭐ 즐겨찾기 모드'</b> 확인란을 선택하십시오.</li>\n</ul>\n</li>\n<li><b>즐겨찾기 모드의 UI 변경 사항:</b>\n<ul>\n<li>'🔗 Kemono 작성자/게시물 URL' 입력 영역이 즐겨찾기 모드가 활성화되었음을 나타내는 메시지로 바뀝니다.</li>\n<li>표준 '다운로드 시작', '일시 중지', '취소' 버튼이 다음으로 바뀝니다:\n<ul>\n<li><b>'🖼️ 즐겨찾는 아티스트'</b> 버튼</li>\n<li><b>'📄 즐겨찾는 게시물'</b> 버튼</li>\n</ul>\n</li>\n<li>'🍪 쿠키 사용' 옵션은 즐겨찾기를 가져오는 데 쿠키가 필요하므로 자동으로 활성화되고 잠깁니다.</li>\n</ul>\n</li>\n<li><b>🖼️ 즐겨찾는 아티스트 버튼:</b>\n<ul>\n<li>이 버튼을 클릭하면 Kemono.su에서 즐겨찾기에 추가한 모든 아티스트 목록이 있는 대화 상자가 열립니다.</li>\n<li>이 목록에서 한 명 이상의 아티스트를 선택하여 콘텐츠를 다운로드할 수 있습니다.</li>\n</ul>\n</li>\n<li><b>📄 즐겨찾는 게시물 버튼 (향후 기능):</b>\n<ul>\n<li>특정 즐겨찾기 <i>게시물</i>(특히 시리즈의 일부인 경우 만화와 같은 순차적 순서)을 다운로드하는 것은 현재 개발 중인 기능입니다.</li>\n<li>즐겨찾는 게시물, 특히 만화와 같은 순차적 읽기를 처리하는 가장 좋은 방법은 아직 탐색 중입니다.</li>\n<li>즐겨찾는 게시물을 다운로드하고 구성하는 방법에 대한 구체적인 아이디어나 사용 사례가 있는 경우(예: 즐겨찾기에서 '만화 스타일'), 프로젝트의 GitHub 페이지에서 문제를 제기하거나 토론에 참여하는 것을 고려해 보십시오. 여러분의 의견은 소중합니다!</li>\n</ul>\n</li>\n<li><b>즐겨찾기 다운로드 범위 (버튼):</b>\n<ul>\n<li>이 버튼('즐겨찾는 게시물' 옆)은 선택한 즐겨찾는 아티스트의 콘텐츠가 다운로드되는 위치를 제어합니다:\n<ul>\n<li><b><i>범위: 선택한 위치:</i></b> 선택한 모든 아티스트가 UI에서 설정한 기본 '다운로드 위치'에 다운로드됩니다. 필터는 모든 콘텐츠에 전역적으로 적용됩니다.</li>\n<li><b><i>범위: 아티스트 폴더:</i></b> 선택한 각 아티스트에 대해 기본 '다운로드 위치' 내에 하위 폴더(아티스트 이름)가 자동으로 생성됩니다. 해당 아티스트의 콘텐츠는 특정 하위 폴더로 이동합니다. 필터는 각 아티스트의 전용 폴더 내에서 적용됩니다.</li>\n</ul>\n</li>\n</ul>\n</li>\n<li><b>즐겨찾기 모드의 필터:</b>\n<ul>\n<li>UI에서 설정한 '🎯 캐릭터로 필터링', '🚫 단어로 건너뛰기' 및 '파일 필터링' 옵션은 선택한 즐겨찾는 아티스트에서 다운로드한 콘텐츠에 계속 적용됩니다.</li>\n</ul>\n</li>\n</ul></body></html>",
    "help_guide_step9_title": "⑨ 주요 파일 및 둘러보기",
    "help_guide_step9_content": "<html><head/><body>\n<h3>애플리케이션에서 사용하는 주요 파일</h3>\n<ul>\n<li><b><code>Known.txt</code>:</b>\n<ul>\n<li>애플리케이션 디렉토리(<code>.exe</code> 또는 <code>main.py</code>가 있는 위치)에 있습니다.</li>\n<li>'이름/제목별로 폴더 분리'가 활성화된 경우 자동 폴더 구성을 위해 알려진 프로그램, 캐릭터 또는 시리즈 제목 목록을 저장합니다.</li>\n<li><b>형식:</b>\n<ul>\n<li>각 줄은 항목입니다.</li>\n<li><b>간단한 이름:</b> 예: <code>내 멋진 시리즈</code>. 이와 일치하는 콘텐츠는 '내 멋진 시리즈'라는 폴더로 이동합니다.</li>\n<li><b>그룹화된 별칭:</b> 예: <code>(캐릭터 A, 캐릭 A, 대체 이름 A)</code>. '캐릭터 A', '캐릭 A' 또는 '대체 이름 A'와 일치하는 콘텐츠는 모두 '캐릭터 A 캐릭 A 대체 이름 A'라는 단일 폴더(정리 후)로 이동합니다. 괄호 안의 모든 용어는 해당 폴더의 별칭이 됩니다.</li>\n</ul>\n</li>\n<li><b>사용법:</b> 게시물이 활성 '캐릭터로 필터링' 입력과 일치하지 않는 경우 폴더 이름 지정의 대체 수단으로 사용됩니다. UI를 통해 간단한 항목을 관리하거나 복잡한 별칭에 대해 파일을 직접 편집할 수 있습니다. 앱은 시작하거나 다음에 사용할 때 다시 로드합니다.</li>\n</ul>\n</li>\n<li><b><code>cookies.txt</code> (선택 사항):</b>\n<ul>\n<li>'쿠키 사용' 기능을 사용하고 직접 쿠키 문자열을 제공하거나 특정 파일을 찾지 않으면 애플리케이션은 해당 디렉토리에서 <code>cookies.txt</code>라는 파일을 찾습니다.</li>\n<li><b>형식:</b> Netscape 쿠키 파일 형식이어야 합니다.</li>\n<li><b>사용법:</b> 다운로더가 브라우저의 로그인 세션을 사용하여 Kemono/Coomer에서 로그인해야 할 수 있는 콘텐츠에 액세스할 수 있도록 합니다.</li>\n</ul>\n</li>\n</ul>\n<h3>처음 사용자 둘러보기</h3>\n<ul>\n<li>처음 실행 시(또는 재설정된 경우) 주요 기능을 안내하는 환영 둘러보기 대화 상자가 나타납니다. 건너뛰거나 '다시는 이 둘러보기를 표시하지 않음'을 선택할 수 있습니다.</li>\n</ul>\n<p><em>많은 UI 요소에는 마우스를 가져가면 나타나는 도구 설명도 있어 빠른 힌트를 제공합니다.</em></p>\n</body></html>"
})

def get_translation(language_code, key, default_text=""):
    """
    Retrieves a translation for a given key and language.
    Falls back to English if the key is not found in the specified language.
    Falls back to default_text if not found in English either or if the language_code itself is not found.
    """
    # Try to get the translation for the specified language
    lang_translations = translations.get(language_code)
    if lang_translations and key in lang_translations:
        return lang_translations[key]

    # Fallback to English if the key or language is not found
    en_translations = translations.get("en")
    if en_translations and key in en_translations:
        print(f"Warning: Translation key '{key}' not found for language '{language_code}'. Falling back to English.")
        return en_translations[key]

    # Fallback to default_text if not found in English either
    print(f"Warning: Translation key '{key}' not found for language '{language_code}' or English. Using default: '{default_text}'.")
    return default_text
