# Kemono Downloader - Detailed Feature Guide

This guide provides a comprehensive overview of all user interface elements, input fields, buttons, popups, and functionalities available in the Kemono Downloader.

---

## Main Interface & Workflow

These are the primary controls you'll interact with to initiate and manage downloads.

### 1. Main Inputs

-   **🔗 Kemono Creator/Post URL Input Field:**
    -   **Purpose:** This is where you paste the URL of the content you want to download.
    -   **Usage:** Supports full URLs for:
        -   Kemono.su (and mirrors like kemono.party) creator pages (e.g., `https://kemono.su/patreon/user/12345`).
        -   Kemono.su (and mirrors) individual posts (e.g., `https://kemono.su/patreon/user/12345/post/98765`).
        -   Coomer.party (and mirrors like coomer.su) creator pages.
        -   Coomer.party (and mirrors) individual posts.
    -   **Note:** When **⭐ Favorite Mode** is active, this field is disabled and shows a "Favorite Mode active" message.

-   **🎨 Creator Selection Button:**
    -   **Icon:** 🎨 (Artist Palette)
    -   **Location:** Next to the URL input field.
    -   **Purpose:** Opens the "Creator Selection" dialog to easily add multiple creators to the URL field.
    -   **Dialog Features:**
        -   Loads creators from your `creators.json` file (expected in the app's directory).
        -   **Search Bar:** Filter the list of creators by name.
        -   **Creator List:** Displays creators with their service (e.g., Patreon, Fanbox) and ID.
        -   **Selection:** Checkboxes to select one or more creators.
        -   **"Add Selected to URL" Button:** Adds the names of selected creators to the URL input field, comma-separated.
        -   **"Download Scope" Radio Buttons (`Characters` / `Creators`):** Determines the folder structure for items added via this popup.
            -   `Characters`: Assumes creator names are character names for folder organization.
            -   `Creators`: Uses the actual creator names for folder organization.

-   **Page Range (Start to End) Input Fields:**
    -   **Purpose:** For creator URLs, specify a range of pages to fetch and process.
    -   **Usage:** Enter the starting page number in the first field and the ending page number in the second.
    -   **Behavior:**
        -   If left blank, all pages for the creator are typically processed (or up to a reasonable limit).
        -   Disabled for single post URLs or when **📖 Manga/Comic Mode** is active (as manga mode fetches all posts for chronological sorting).

-   **📁 Download Location Input Field & Browse Button:**
    -   **Purpose:** Specify the main directory where all downloaded files and folders will be saved.
    -   **Usage:**
        -   Type or paste the path directly into the field.
        -   Click the **"Browse..."** button to open a system dialog to select a folder.
    -   **Requirement:** This field must be filled unless you are using the "🔗 Only Links" filter mode.

### 2. Action Buttons

-   **⬇️ Start Download / 🔗 Extract Links Button:**
    -   **Purpose:** The primary action button to begin the downloading or link extraction process based on current settings.
    -   **Behavior:**
        -   If "🔗 Only Links" filter is selected, the button text changes to **"🔗 Extract Links"** and it will only gather external links from posts.
        -   Otherwise, it reads **"⬇️ Start Download"** and initiates the content download.

-   **⏸️ Pause / ▶️ Resume Download Button:**
    -   **Purpose:** Temporarily halt or continue the ongoing download/extraction process.
    -   **Behavior:**
        -   When active, the button shows **"⏸️ Pause Download"**. Clicking it pauses the operation.
        -   When paused, the button shows **"▶️ Resume Download"**. Clicking it resumes from where it left off.
        -   Some UI settings can be changed while paused (e.g., filter adjustments), which will apply upon resuming.

-   **❌ Cancel & Reset UI Button:**
    -   **Purpose:** Immediately stops the current download/extraction operation and performs a "soft" reset of the UI.
    -   **Behavior:**
        -   Halts all active threads and processes.
        -   Clears progress information and logs.
        -   Preserves the content of the "🔗 Kemono Creator/Post URL" and "📁 Download Location" input fields. Other settings are reset to their defaults.

-   **🔄 Reset Button (located in the log area):**
    -   **Purpose:** Performs a "hard" reset of the UI when no operation is active.
    -   **Behavior:**
        -   Clears all input fields (including URL and Download Location).
        -   Resets all filter settings and options to their default values.
        -   Clears the log area.

---

## Filtering & Content Selection

These options allow you to precisely control what content is downloaded or skipped.

-   **🎯 Filter by Character(s) Input Field:**
    -   **Purpose:** Download content related to specific characters.
    -   **Usage:** Enter character names, comma-separated.
    -   **Advanced Syntax:**
        -   `Nami`: Simple character filter. Matches "Nami".
        -   `(Vivi, Ulti, Uta)`: Grouped characters. Matches "Vivi" OR "Ulti" OR "Uta". If "Separate Folders" is on, creates a shared folder for the session (e.g., "Vivi Ulti Uta"). Adds "Vivi", "Ulti", "Uta" as *separate* entries to `Known.txt` if new.
        -   `(Boa, Hancock)~`: Aliased characters. Matches "Boa" OR "Hancock" but treats them as the same entity. If "Separate Folders" is on, creates a shared folder (e.g., "Boa Hancock"). Adds "Boa Hancock" as a *single group entry* to `Known.txt` if new, with "Boa" and "Hancock" as its aliases.

-   **Filter: [Type] Button (Scope for Character Filter):**
    -   **Location:** Next to the "Filter by Character(s)" input.
    -   **Purpose:** Defines how the character filter is applied. Cycles through options on click.
    -   **Options:**
        -   `Filter: Files`: Checks individual filenames against the character filter. Only matching files from a post are downloaded.
        -   `Filter: Title` (Default): Checks post titles against the character filter. If the title matches, all files from that post are downloaded.
        -   `Filter: Both`: Checks the post title first. If no match, then checks individual filenames within that post.
        -   `Filter: Comments (Beta)`: Checks filenames first. If no file match, then checks post comments/description. (Note: This may use more API requests).

-   **🚫 Skip with Words Input Field:**
    -   **Purpose:** Exclude posts or files containing specified keywords.
    -   **Usage:** Enter words or phrases, comma-separated (e.g., `WIP, sketch, preview`).

-   **Scope: [Type] Button (Scope for Skip with Words):**
    -   **Location:** Next to the "Skip with Words" input.
    -   **Purpose:** Defines how the skip words are applied. Cycles through options on click.
    -   **Options:**
        -   `Scope: Files`: Skips individual files if their names contain any of the skip words.
        -   `Scope: Posts` (Default): Skips entire posts if their titles contain any of the skip words.
        -   `Scope: Both`: Checks the post title first. If no skip words match, then checks individual filenames.

-   **✂️ Remove Words from name Input Field:**
    -   **Purpose:** Clean up downloaded filenames by removing specified unwanted words or phrases.
    -   **Usage:** Enter words or phrases, comma-separated (e.g., `patreon, [HD], kemono`).

-   **Filter Files (Radio Buttons):**
    -   **Purpose:** Select the types of files to download.
    -   **Options:**
        -   `All`: Download all file types attached to posts.
        -   `Images/GIFs`: Download only common image formats (JPG, PNG, GIF, WebP, etc.).
        -   `Videos`: Download only common video formats (MP4, MOV, MKV, WebM, etc.).
        -   `📦 Only Archives`: Exclusively download `.zip` and `.rar` files. This mode disables the "Skip .zip/.rar" checkboxes and the "Show External Links in Log" feature.
        -   `🎧 Only Audio`: Download only common audio formats (MP3, WAV, FLAC, OGG, etc.).
        -   `🔗 Only Links`: Do not download any files. Instead, extract and display external links found in post descriptions in the log area. The main action button changes to "🔗 Extract Links".

-   **Skip .zip / Skip .rar Checkboxes:**
    -   **Purpose:** Individually choose to skip downloading `.zip` files or `.rar` files.
    -   **Behavior:** Disabled if the "📦 Only Archives" filter is active.

---

## Download Customization

Options to further refine the download process and output.

-   **Download Thumbnails Only Checkbox:**
    -   **Purpose:** Download only the small preview images (thumbnails) provided by the API, instead of full-resolution files.
    -   **Behavior:** If "**Scan Content for Images**" is also active, this option's behavior changes: *only* images found by the content scan (embedded `<img>` tags) are downloaded as thumbnails (API thumbnails are ignored).

-   **Scan Content for Images Checkbox:**
    -   **Purpose:** Actively scan the HTML content of posts for `<img>` tags and direct image links. This is crucial for downloading images embedded in post descriptions that are not listed as direct attachments in the API response.
    -   **Behavior:** Resolves relative image paths to absolute URLs for downloading.

-   **Compress to WebP Checkbox:**
    -   **Purpose:** Convert downloaded images to WebP format to potentially save disk space.
    -   **Requirement:** Requires the `Pillow` library to be installed.
    -   **Behavior:** Attempts to convert images larger than a certain threshold (e.g., 1.5MB) to WebP if the WebP version is significantly smaller. Original files are not kept if conversion is successful.

-   **🗄️ Custom Folder Name (Single Post Only) Input Field:**
    -   **Purpose:** When downloading a single post URL, allows you to specify a custom name for the folder where its contents will be saved.
    -   **Visibility:** Only appears if:
        1.  A single post URL is entered in the main URL field.
        2.  The "**Separate Folders by Name/Title**" option is enabled.

---

## 📖 Manga/Comic Mode

Specialized mode for downloading creator feeds in a way suitable for sequential reading, like manga or comics. This mode is implicitly active when downloading from a creator URL and certain filename styles are chosen.

-   **Activation:** Primarily by downloading a creator's feed (not a single post) and selecting a relevant "Filename Style".
-   **Core Behavior:** Processes and downloads posts from the creator's feed in chronological order (oldest to newest). The "Page Range" input is typically disabled as all posts are fetched for correct sorting.

-   **Filename Style Toggle Button (located in the log area):**
    -   **Purpose:** Controls how files are named when downloading in a manga/comic-like fashion. Cycles through options on click.
    -   **Options:**
        -   `Name: Post Title` (Default for non-manga): The first file in a post is named after the post title; subsequent files in the *same post* keep their original names.
        -   `Name: Original File`: All downloaded files attempt to keep their original filenames as provided by the server. An optional "Filename Prefix" input field appears.
        -   `Name: Title+G.Num`: (Global Numbering) All files across all downloaded posts for the creator get a prefix from their respective post's title, followed by a global sequential number (e.g., `Chapter 1_001.jpg`, `Chapter 1_002.jpg`, `Chapter 2_003.jpg`). This ensures strict order across posts. Disables post-level multithreading for sequential numbering.
        -   `Name: Date Based`: Files are named sequentially (e.g., `001.jpg`, `002.jpg`) based on the post's publication date. An optional "Filename Prefix" input field appears. Disables post-level multithreading.

-   **Optional Filename Prefix Input Field (Manga Mode):**
    -   **Visibility:** Appears when "Filename Style" is set to `Name: Original File` or `Name: Date Based`.
    -   **Purpose:** Allows you to add a custom prefix to all filenames generated using these styles (e.g., `MySeries_001.jpg`).

---

## Folder Organization

Controls for how downloaded content is structured into folders.

-   **Separate Folders by Name/Title Checkbox:**
    -   **Purpose:** Creates subfolders within the main "Download Location" based on matching criteria.
    -   **Behavior:**
        -   If "**Filter by Character(s)**" is used, folders are named after the matched character(s)/group(s).
        -   If no character filter matches (or no filter is active), but the post title matches an entry in `Known.txt`, a folder named after the `Known.txt` entry is created.
        -   If neither of the above, and this option is checked, folders might be created based on post titles directly (behavior can vary).

-   **Subfolder per Post Checkbox:**
    -   **Purpose:** Creates an additional layer of subfolders, where each individual post's content goes into its own subfolder.
    -   **Behavior:** Only active if "**Separate Folders by Name/Title**" is also checked. The post subfolder will be created *inside* the character/title folder. Folder names are typically derived from sanitized post titles or IDs.

-   **`Known.txt` Management UI (Bottom Left of UI):**
    -   **Purpose:** Manages a local list (`Known.txt` file in the app directory) of series, characters, or general terms used for automatic folder organization and character filter suggestions.
    -   **Elements:**
        -   **List Display:** Shows the primary names from your `Known.txt` file.
        -   **Add New Input Field:** Enter a new name or group to add to `Known.txt`.
            -   Simple Name: e.g., `My Series`
            -   Group (creates separate entries in `Known.txt`): e.g., `(Vivi, Ulti, Uta)`
            -   Group with Aliases (single entry in `Known.txt` with `~`): e.g., `(Boa, Hancock)~`
        -   **➕ Add Button:** Adds the entry from the "Add New" field to `Known.txt` and refreshes the list.
        -   **⤵️ Add to Filter Button:** Opens a dialog displaying all entries from `Known.txt` (with a search bar). Select one or more entries to add them to the "**🎯 Filter by Character(s)**" input field. Grouped names from `Known.txt` are added with the `~` syntax if applicable.
        -   **🗑️ Delete Selected Button:** Removes the currently selected name(s) from the list display and from the `Known.txt` file.
        -   **Open Known.txt Button:** Opens your `Known.txt` file in the system's default text editor for manual editing.
        -   **❓ Help Button (Known.txt):** Opens a guide or tooltip explaining the `Known.txt` feature and syntax.

---

## ⭐ Favorite Mode (Kemono.su Only)

Download directly from your favorited artists and posts on Kemono.su.

-   **Enable Checkbox ("⭐ Favorite Mode"):**
    -   **Location:** Usually near the "🔗 Only Links" filter option.
    -   **Purpose:** Switches the downloader to operate on your Kemono.su favorites.
    -   **UI Changes upon Enabling:**
        -   The "🔗 Kemono Creator/Post URL" input field is disabled/replaced with a "Favorite Mode active" message.
        -   The main action buttons change to "**🖼️ Favorite Artists**" and "**📄 Favorite Posts**".
        -   The "**🍪 Use Cookie**" option is automatically enabled and locked, as cookies are required to access your favorites.

-   **🖼️ Favorite Artists Button & Dialog:**
    -   **Purpose:** Fetches and allows you to download content from artists you have favorited on Kemono.su.
    -   **Dialog Features:**
        -   Fetches the list of your favorited artists.
        -   **Search Bar:** Filter artists by name.
        -   **Artist List:** Displays favorited artists.
        -   **Select All / Deselect All:** Convenience buttons for selection.
        -   **"Download Selected" Button:** Queues all posts from the selected artists for download, respecting current filter settings.

-   **📄 Favorite Posts Button & Dialog:**
    -   **Purpose:** Fetches and allows you to download specific posts you have favorited on Kemono.su.
    -   **Dialog Features:**
        -   Fetches the list of your favorited posts, usually grouped by artist and sorted by date.
        -   **Search Bar:** Filter posts by title, creator name, ID, or service.
        -   **Post List:** Displays favorited posts. Known names from your `Known.txt` may be highlighted in post titles for easier identification.
        -   **Select All / Deselect All:** Convenience buttons for selection.
        -   **"Download Selected" Button:** Queues the selected individual posts for download, respecting current filter settings.

-   **Favorite Download Scope Button (Location may vary, often near Favorite Posts button):**
    -   **Purpose:** Determines the folder structure for downloads initiated via Favorite Mode.
    -   **Options:**
        -   `Scope: Selected Location`: All selected favorites (artists or posts) are downloaded directly into the main "📁 Download Location". Global filters apply.
        -   `Scope: Artist Folders`: A subfolder is created for each artist within the main "📁 Download Location" (e.g., `DownloadLocation/ArtistName/`). Content from that artist (whether a full artist download or specific favorited posts from them) goes into their respective subfolder. Filters apply within each artist's context.

---

## Advanced & Performance

-   **🍪 Cookie Management:**
    -   **Use Cookie Checkbox:** Enables the use of browser cookies for accessing content that might be restricted or require login (e.g., certain posts, Favorite Mode).
    -   **Cookie Text Field:**
        -   **Purpose:** Directly paste your cookie string.
        -   **Format:** Standard HTTP cookie string format (e.g., `name1=value1; name2=value2`).
    -   **Browse... Button (for Cookies):**
        -   **Purpose:** Select a `cookies.txt` file from your system.
        -   **Format:** Must be in Netscape cookie file format.
    -   **Behavior:**
        -   The text field takes precedence if filled.
        -   If "Use Cookie" is checked and both the text field and browsed file path are empty, the application will attempt to automatically load a `cookies.txt` file from its root directory.

-   **Use Multithreading Checkbox & Threads Input Field:**
    -   **Purpose:** Enable and configure the number of simultaneous operations to potentially speed up downloads.
    -   **Behavior:**
        -   **Creator Feeds:** The "Threads" input controls how many posts are processed concurrently.
        -   **Single Post URLs:** The "Threads" input controls how many files from that single post are downloaded concurrently.
    -   **Note:** Setting too high a number might lead to API rate-limiting or instability.

-   **Multi-part Download Toggle Button (located in the log area):**
    -   **Purpose:** Enables/disables multi-segment downloading for individual large files.
    -   **Options:**
        -   `Multi-part: ON`: Large files are split into multiple parts that are downloaded simultaneously and then reassembled. Can significantly speed up downloads for single large files but may increase UI choppiness or log spam with many small files.
        -   `Multi-part: OFF` (Default): Files are downloaded as a single stream.
    -   **Behavior:** Disabled if "🔗 Only Links" or "📦 Only Archives" mode is active.

---

## Logging & Monitoring

-   **📜 Progress Log / Extracted Links Log Area:**
    -   **Purpose:** The main text area displaying detailed messages about the ongoing process.
    -   **Content:** Shows download progress for each file, errors encountered, skipped items, summary information, or extracted links (if in "🔗 Only Links" mode).

-   **👁️ / 🙈 Log View Toggle Button:**
    -   **Purpose:** Switches the content displayed in the main log area.
    -   **Views:**
        -   `👁️ Progress Log` (Default): Shows all download activity, errors, and general progress messages.
        -   `🙈 Missed Character Log`: Shows a list of key terms intelligently extracted from post titles or content that were skipped due to the "**🎯 Filter by Character(s)**" not matching. Useful for identifying characters you might want to add to your filter or `Known.txt`.

-   **Show External Links in Log Checkbox & Panel:**
    -   **Purpose:** If checked, a secondary, smaller log panel appears (usually below the main log) that specifically displays any external links (e.g., to Mega, Google Drive) found in post descriptions.
    -   **Behavior:** Disabled if "🔗 Only Links" or "📦 Only Archives" mode is active (as "Only Links" uses the main log, and archives typically don't have such external links processed).

-   **Export Links Button:**
    -   **Visibility:** Appears when the "**🔗 Only Links**" filter mode is active.
    -   **Purpose:** Saves all the links extracted and displayed in the main log area to a `.txt` file.

-   **Progress Labels/Bars:**
    -   **Purpose:** Provide a visual and textual representation of the download progress.
    -   **Typically Includes:**
        -   Overall post progress (e.g., "Post 5 of 20").
        -   Individual file download status (e.g., "Downloading file.zip... 50% at 1.2 MB/s").
        -   Summary statistics at the end of a session (total downloaded, skipped, failed).

---
## Error Handling & Retries

-   **🆘 Error Button (Main UI):**
    -   **Location:** Typically near the main action buttons (e.g., Start, Pause, Cancel).
    -   **Purpose:** Becomes active if files failed to download during the last session (and were not successfully retried). Clicking it opens the "Files Skipped Due to Errors" dialog.
    -   **"Files Skipped Due to Errors" Dialog:**
        -   **File List:** Displays a list of files that encountered download errors. Each entry shows the filename, the post it was from (title and ID).
        -   **Checkboxes:** Allows selection of individual files from the list.
        -   **"Select All" Button:** Checks all files in the list.
        -   **"Retry Selected" Button:** Attempts to re-download all checked files.
        -   **"Export URLs to .txt" Button:**
            -   Opens an "Export Options" dialog.
            -   **"Link per line (URL only)":** Exports only the direct download URL for each failed file, one URL per line.
            -   **"Export with details (URL [Post, File info])":** Exports the URL followed by details like Post Title, Post ID, and Original Filename in brackets.
            -   Prompts the user to save the generated `.txt` file.
        -   **"OK" Button:** Closes the dialog.
    -   **Note:** Files successfully retried or skipped due to hash match during a retry attempt are removed from this error list.
---

## ⚙️ Application Settings

These settings allow you to customize the application's appearance and language.

-   **⚙️ Settings Button (Icon may vary, e.g., a gear ⚙️):**
    -   **Location:** Typically located in a persistent area of the UI, possibly near other global controls or in a menu.
    -   **Purpose:** Opens the "Settings" dialog.
    -   **Tooltip Example:** "Open application settings (Theme, Language, etc.)"

-   **"Settings" Dialog:**
    -   **Title:** "Settings"
    -   **Purpose:** Provides options to configure application-wide preferences.
    -   **Sections:**
        -   **Appearance Group (`Appearance`):**
            -   **Theme Toggle Buttons/Options:**
                -   `Switch to Light Mode`
                -   `Switch to Dark Mode`
                -   **Purpose:** Allows users to switch between a light and dark visual theme for the application.
                -   **Tooltips:** Provide guidance on switching themes.
        -   **Language Settings Group (`Language Settings`):**
            -   **Language Selection Dropdown/List:**
                -   **Label:** "Language:"
                -   **Options:** Includes, but not limited to:
                    -   English (`English`)
                    -   日本語 (`日本語 (Japanese)`)
                    -   Français (French)
                    -   Español (Spanish)
                    -   Deutsch (German)
                    -   Русский (Russian)
                    -   한국어 (Korean)
                    -   简体中文 (Chinese Simplified)
                -   **Purpose:** Allows users to change the display language of the application interface.
            -   **Restart Prompt:** After changing the language, a dialog may appear:
                -   **Title:** "Language Changed"
                -   **Message:** "The language has been changed. A restart is required for all changes to take full effect."
                -   **Informative Text:** "Would you like to restart the application now?"
                -   **Buttons:** "Restart Now", "OK" (or similar to defer restart).
    -   **"OK" Button:** Saves the changes made in the Settings dialog and closes it.
---

## Other UI Elements

-   **Retry Failed Downloads Prompt:**
    -   **Trigger:** Appears at the end of a download session if there were files that failed to download due to recoverable errors (e.g., network interruption, IncompleteRead).
    -   **Action:** Prompts the user if they want to attempt downloading the failed files again.

-   **New Name Confirmation Dialog (for Character Filter & `Known.txt`):**
    -   **Trigger:** When new, unrecognized names or groups are used in the "**🎯 Filter by Character(s)**" field that are not present in `Known.txt`.
    -   **Action:** Prompts the user to confirm if they want to add these new names/groups to `Known.txt` with the appropriate formatting (simple, grouped, or aliased).

-   **Onboarding Tour / Help Guide Button (❓):**
    -   **Purpose:** Opens a built-in help guide or an onboarding tour that explains the basic functionalities and UI elements of the application. Often linked to this detailed feature guide.

---

This guide should cover all interactive elements of the Kemono Downloader. If you have further questions or discover elements not covered, please refer to the main `readme.md` or consider opening an issue on the project's repository.