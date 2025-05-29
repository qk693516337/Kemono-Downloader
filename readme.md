<h1 align="center">Kemono Downloader v4.2.0</h1>

<table align="center">
  <tr>
    <td align="center">
      <img src="Read/Read.png" alt="Post Downloader Tab" width="400"/>
      <br>
      <strong>Default</strong>
    </td>
    <td align="center">
      <img src="Read/Read1.png" alt="Creator Downloader Tab" width="400"/>
      <br>
      <strong>Favorite mode</strong>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="Read/Read2.png" alt="Settings Tab" width="400"/>
      <br>
      <strong>Single Post</strong>
    </td>
    <td align="center">
      <img src="Read/Read3.png" alt="Settings Tab" width="400"/>
      <br>
      <strong>Manga/Comic Mode</strong>
    </td>
    <td align="center">
    </td>
  </tr>
</table>
---

A powerful, feature-rich GUI application for downloading content from **[Kemono.su](https://kemono.su)** and **[Coomer.party](https://coomer.party)**.  
Built with **PyQt5**, this tool is ideal for users who want deep filtering, customizable folder structures, efficient downloads, and intelligent automation — all within a modern, user-friendly graphical interface.

---

## 🚀 What's New in v4.2.0? - Favorite Mode & UI Enhancements!

Version 4.2.0 introduces the highly anticipated **Favorite Mode**, allowing you to directly download content from artists you've favorited on Kemono.su. This update also includes several UI tweaks for a smoother experience.

### ⭐ Favorite Mode: Download Your Kemono Favorites

-   **Easy Access to Your Favorites:** A new "**⭐ Favorite Mode**" checkbox (located next to the "🔗 Only Links" radio button) activates this feature.
-   **Dedicated Workflow:**
    -   When enabled, the standard URL input is replaced with a message indicating Favorite Mode is active.
    -   The main action buttons change to "**🖼️ Favorite Artists**" and "**📄 Favorite Posts**" (Note: "Favorite Posts" functionality is planned for a future release).
    -   The "**🍪 Use Cookie**" option is automatically enabled and locked, as cookies are essential for fetching your favorites from Kemono.su.
-   **🖼️ Favorite Artists Dialog:**
    -   Clicking the "**🖼️ Favorite Artists**" button opens a new dialog.
    -   This dialog fetches and displays a list of all artists you have favorited on Kemono.su.
    -   You can search, select one or multiple artists, and then initiate downloads for their content.
-   **🎯 Flexible Download Scopes:** A new toggle button, "**Scope: [Selected Location/Artist Folders]**", appears in Favorite Mode, allowing you to choose how the selected artists' content is organized:
    -   **`Scope: Selected Location` (Default):** All content from the selected favorite artists will be downloaded into the main "Download Location" you've set in the UI. Filters (character, skip words, file type) will apply globally to all downloaded content.
    -   **`Scope: Artist Folders`:** For each selected favorite artist, a new subfolder (named after the artist, e.g., "ArtistName") will be automatically created inside your main "Download Location". All content for that specific artist will be downloaded into their dedicated subfolder. Filters will apply *within* each artist's folder.
-   **Filters Still Apply:** Your existing "Filter by Character(s)", "Skip with Words", and "Filter Files" settings will be applied to the content downloaded from your selected favorite artists, respecting the chosen download scope.

### ⚙️ UI Defaults & Filter Cycling Order

-   **Persistent Filter Defaults:**
    -   The "Skip with Words" filter now always defaults to scoping by "**Posts**" on application startup.
    -   The "Filter by Character(s)" filter now always defaults to scoping by "**Title**" on application startup.
    -   *Note: Any changes made to these two scope settings during a session will not be saved, ensuring they revert to these defaults on the next launch.*
-   **Updated Filter Cycling Order:**
    -   **Filter by Character(s) Scope:** Cycles as `Title` -> `Files` -> `Both` -> `Comments (Beta)` -> `Title`.
    -   **Skip with Words Scope:** Cycles as `Posts` -> `Files` -> `Both` -> `Posts`.

---

## 📜 Previous Update: What's New in v4.1.1? - Enhanced Image Discovery & Audio Filtering
Version 4.1.1 brings significant enhancements, including smarter image capture from post content and a dedicated filter mode for audio files.

###  "Scan Content for Images" Feature

- **Enhanced Image Discovery:** A new checkbox, "**Scan Content for Images**," has been added to the UI (grouped with "Download Thumbnails Only" and "Compress Large Images").
- **How it Works:**
    - When enabled, the downloader meticulously scans the HTML content of each post's description or body.
    - It searches for images in two main ways:
        - **Directly linked absolute URLs** (e.g., `https://externalsite.com/image.png`) that end with a common image extension (jpg, png, gif, etc.).
        - **Images embedded using HTML `<img>` tags.** The downloader extracts the `src` attribute from these tags and can resolve various path types:
            - Absolute URLs (e.g., `http://...` or `https://...`)
            - Protocol-relative URLs (e.g., `//cdn.example.com/image.jpg`)
            - Root-relative paths (e.g., `/data/user_content/image.gif`), which are resolved against the site's base URL (like `https://kemono.su/data/user_content/image.gif`).
    - This is particularly useful for capturing images that are part of the post's narrative but not formally listed in the API's file or attachment sections.
- **Default State:** This option is **unchecked by default**.
- **Key Interaction with "Download Thumbnails Only":** This new feature works closely with the existing "Download Thumbnails Only" option:
    - If you enable "Download Thumbnails Only":
        - The "Scan Content for Images" checkbox will **automatically become checked and disabled** (locked).
        - The downloader then **exclusively downloads images discovered through the content scan**. Any API-listed thumbnails are bypassed, giving priority to images embedded directly in the post.
    - If you disable "Download Thumbnails Only":
        - The "Scan Content for Images" checkbox will become **enabled again and revert to being unchecked**. You can then manually enable it if you wish to scan content without being in thumbnail-only mode.

This feature ensures a more comprehensive download experience, especially for posts where images are integrated directly into the text.

### New "🎧 Only Audio" Filter Mode

Alongside image discovery, v4.1.1 also introduces/enhances a dedicated filter mode for audio enthusiasts:

-   **Focused Audio Downloads:** The "🎧 Only Audio" option in the "Filter Files" radio button group allows you to download exclusively common audio file types. This includes formats like MP3, WAV, FLAC, M4A, OGG, and more.
-   **Streamlined UI:** When "🎧 Only Audio" mode is active:
    -   Irrelevant UI options such as the "Skip Scope" button (for word-based post/file skipping) and the "Multi-part Download" toggle are hidden to simplify the interface.
    -   The "Show External Links in Log" checkbox is automatically disabled, as link extraction is not the focus of this mode.
-   **Archive Handling:** Unlike the "📦 Only Archives" mode (which disables archive skipping), the "Skip .zip" and "Skip .rar" checkboxes remain enabled and configurable when "🎧 Only Audio" is selected. This gives you the flexibility to also exclude any archives encountered while in audio-only mode if desired.
-   **Purpose:** This mode is perfect for users who primarily want to collect audio tracks, podcasts, or sound effects from posts without downloading other media types.


---

## 📜 Previous Update: What's New in v4.0.1? - Cookie Management & Advanced Known.txt

Version 4.0.1 focuses on enhancing access to content and providing even smarter organization:

###  Cookie Management

- **Access Content:** Seamlessly download from Kemono/Coomer as if you were logged in by using your browser's cookies.
- **Flexible Input:**
  - Directly paste your cookie string (e.g., `name1=value1; name2=value2`).
  - Browse and load cookies from a `cookies.txt` file (Netscape format).
  - Automatic fallback to a `cookies.txt` file in the application directory if "Use Cookie" is enabled and no other source is specified.
- **Easy Activation:** A simple "Use Cookie" checkbox in the UI controls this feature.
- *Important Note: Cookie settings (text, file path, and enabled state) are configured per session and are not saved when the application is closed. You will need to re-apply them on each launch if needed.*

---

###  Advanced `Known.txt` and Character Filtering

The `Known.txt` system has been revamped for improved performance and stability. The previous method of handling known names could become resource-intensive with large lists, potentially leading to application slowdowns or crashes. This new, streamlined system offers more direct control and robust organization.
The `Known.txt` file and the "Filter by Character(s)" input field work together to provide powerful and flexible content organization. The `Known.txt` file itself has a straightforward syntax, while the UI input allows for more complex session-specific grouping and alias definitions that can then be added to `Known.txt`.

**1. `Known.txt` File Syntax (Located in App Directory):**

`Known.txt` stores your persistent list of characters, series, or keywords for folder organization. Each line is an entry:

- **Simple Entries:**
  - A line like `My Awesome Series` or `Nami`.
  - **Behavior:** Content matching this term will be saved into a folder named "My Awesome Series" or "Nami" respectively (if "Separate Folders" is enabled).

**2. "Filter by Character(s)" UI Input Field:**

This field allows for dynamic filtering for the current download session and provides options for how new entries are added to `Known.txt`.

- **Standard Names:**
  - Input: `Nami, Robin`
  - Session Behavior: Filters for "Nami" OR "Robin". If "Separate Folders" is on, creates folders "Nami" and "Robin".
  - `Known.txt` Addition: If "Nami" is new and selected for addition in the confirmation dialog, it's added as `Nami` on a new line in `Known.txt`.

- **Grouped Aliases for a Single Character (using `(...)~` syntax):**
  - Input: `(Boa, Hancock)~`
  - Meaning: "Boa" and "Hancock" are different names/aliases for the *same character*. The names are listed within parentheses separated by commas (e.g., `name1, alias1, alias2`), and the entire group is followed by a `~` symbol. This is useful when a creator uses different names for the same character.
  - Session Behavior: Filters for "Boa" OR "Hancock". If "Separate Folders" is on, creates a single folder named "Boa Hancock".
  - `Known.txt` Addition: If this group is new and selected for addition, it's added to `Known.txt` as a grouped alias entry, typically `(Boa Hancock)`. The first name in the `Known.txt` entry (e.g., "Boa Hancock") becomes the primary folder name.

- **Combined Folder for Distinct Characters (using `(...)` syntax):**
  - Input: `(Vivi, Uta)`
  - Meaning: "Vivi" and "Uta" are *distinct characters*, but for this download session, their content should be grouped into a single folder. The names are listed within parentheses separated by commas. This is useful for grouping art of less frequent characters without creating many small individual folders.
  - Session Behavior: Filters for "Vivi" OR "Uta". If "Separate Folders" is on, creates a single folder named "Vivi Uta".
  - `Known.txt` Addition: If this "combined group" is new and selected for addition, "Vivi" and "Uta" are added to `Known.txt` as *separate, individual simple entries* on new lines:
    ```
    Vivi
    Uta
    ```
    The combined folder "Vivi Uta" is a session-only convenience; `Known.txt` stores them as distinct entities for future individual use.

**3. Interaction with `Known.txt`:**

- **Adding New Names from Filters:** When you use the "Filter by Character(s)" input, if any names or groups are new (not already in `Known.txt`), a dialog will appear after you start the download. This dialog allows you to select which of these new names/groups should be added to `Known.txt`, formatted according to the rules described above.
- **Intelligent Fallback:** If "Separate Folders by Name/Title" is active, and content doesn't match the "Filter by Character(s)" UI input, the downloader consults your `Known.txt` file for folder naming.
- **Direct Management:** You can add simple entries directly to `Known.txt` using the list and "Add" button in the UI's `Known.txt` management section. For creating or modifying complex grouped alias entries directly in the file, or for bulk edits, click the "Open Known.txt" button. The application reloads `Known.txt` on startup or before a download process begins.
- **Using Known Names to Populate Filters (via "Add to Filter" Button):**
  - Next to the "Add" button in the `Known.txt` management section, a "⤵️ Add to Filter" button provides a quick way to use your existing known names.
  - Clicking this opens a popup window displaying all entries from your `Known.txt` file, each with a checkbox.
  - The popup includes:
    - A search bar to quickly filter the list of names.
    - "Select All" and "Deselect All" buttons for convenience.
  - After selecting the desired names, click "Add Selected".
  - The chosen names will be inserted into the "Filter by Character(s)" input field.
  - **Important Formatting:** If a selected entry from `Known.txt` is a group (e.g., originally `(Boa Hancock)` in `Known.txt`, which implies aliases "Boa" and "Hancock"), it will be added to the filter field as `(Boa, Hancock)~`. Simple names are added as-is.


---
##  What's in v3.5.0? (Previous Update)
This version brought significant enhancements to manga/comic downloading, filtering capabilities, and user experience:

###  Enhanced Manga/Comic Mode

- **Optional Filename Prefix:**
  - When using the "Date Based" or "Original File Name" manga styles, an optional prefix can be specified in the UI.
  - This prefix will be prepended to each filename generated by these styles.
  - **Example (Date Based):** If prefix is `MySeries_`, files become `MySeries_001.jpg`, `MySeries_002.png`, etc.
  - **Example (Original File Name):** If prefix is `Comic_Vol1_`, an original file `page_01.jpg` becomes `Comic_Vol1_page_01.jpg`.
  - This input field appears automatically when either of these two manga naming styles is selected.

- **New "Date Based" Filename Style:**

  - Perfect for truly sequential content! Files are named numerically (e.g., `001.jpg`, `002.jpg`, `003.ext`...) across an *entire creator's feed*, strictly following post publication order.

  - **Smart Numbering:** Automatically resumes from the highest existing number found in the series folder (and subfolders, if "Subfolder per Post" is enabled).

  - **Guaranteed Order:** Disables multi-threading for post processing to ensure sequential accuracy.

  - Works alongside the existing "Post Title" and "Original File Name" styles.
- **New "Title+G.Num (Post Title + Global Numbering)" Filename Style:**
  - Ideal for series where you want each file to be prefixed by its post title but still maintain a global sequential number across all posts from a single download session.
  - **Naming Convention:** Files are named using the cleaned post title as a prefix, followed by an underscore and a globally incrementing number (e.g., `Post Title_001.ext`, `Post Title_002.ext`).
  - **Example:**
    - Post "Chapter 1: The Adventure Begins" (contains 2 files: `imageA.jpg`, `imageB.png`) -> `Chapter 1 The Adventure Begins_001.jpg`, `Chapter 1 The Adventure Begins_002.png`
    - Next Post "Chapter 2: New Friends" (contains 1 file: `cover.jpg`) -> `Chapter 2 New Friends_003.jpg`
  - **Sequential Integrity:** Multithreading for post processing is automatically disabled when this style is selected to ensure the global numbering is strictly sequential.

---

###  "Remove Words from Filename" Feature

- Specify comma-separated words or phrases (case-insensitive) that will be automatically removed from filenames.

- Example: `patreon, [HD], _final` transforms `AwesomeArt_patreon` `Hinata_Hd` into `AwesomeArt.jpg` `Hinata.jpg`.

---

###  New "Only Archives" File Filter Mode

- Exclusively downloads `.zip` and `.rar` files.

- Automatically disables conflicting options like "Skip .zip/.rar" and external link logging.

---

###  Improved Character Filter Scope - "Comments (Beta)"

- **File-First Check:** Prioritizes matching filenames before checking post comments for character names.

- **Comment Fallback:** Only checks comments if no filename match is found, reducing unnecessary API calls.

---

###  Refined "Missed Character Log"

- Displays a capitalized, alphabetized list of key terms from skipped post titles.

- Makes it easier to spot patterns or characters that might be unintentionally excluded.

---

###  Enhanced Multi-part Download Progress

- Granular visibility into active chunk downloads and combined speed for large files.

---

###  Updated Onboarding Tour

- Improved guide for new users, covering v4.0.0 features and existing core functions.

---

###  Robust Configuration Path

- Settings and `Known.txt` are now stored in the same folder as app.

---

##  Core Features

---

### User Interface & Workflow

- **Clean PyQt5 GUI** — Simple, modern, and dark-themed.

- **Persistent Settings** — Saves preferences between sessions.

- **Download Modes:**
  - Single Post URL
  - Entire Creator Feed
  - **Favorite Mode:**
    - Download directly from your Kemono.su favorited artists.
    - Choose to download to a central location or into individual artist-named subfolders.

- **Flexible Options:**
  - Specify Page Range (disabled in Manga Mode)
  - Custom Folder Name for single posts

---

###  Smart Filtering

- **Character Name Filtering:**
  - Use `Tifa, Aerith` or group `(Boa, Hancock)` → folder `Boa Hancock`
  - Flexible input for current session and for adding to `Known.txt`.
  - Examples:
    - `Nami` (simple character)
    - `(Boa Hancock)~` (aliases for one character, session folder "Boa Hancock", adds `(Boa Hancock)` to `Known.txt`)
    - `(Vivi, Uta)` (distinct characters, session folder "Vivi Uta", adds `Vivi` and `Uta` separately to `Known.txt`)
  - A "⤵️ Add to Filter" button (near the `Known.txt` management UI) allows you to quickly populate this field by selecting from your existing `Known.txt` entries via a popup with search and checkbox selection.
  - See "Advanced `Known.txt` and Character Filtering" for full details.
  - **Filter Scopes:**
    - `Files`
    - `Title`
    - `Both (Title then Files)`
    - `Comments (Beta - Files first)`

- **Skip with Words:**
  - Exclude with `WIP, sketch, preview`

  - **Skip Scopes:**
    - `Files`
    - `Posts`
    - `Both (Posts then Files)`

- **File Type Filters:**
  - `All`, `Images/GIFs`, `Videos`, `📦 Only Archives`, `🔗 Only Links`

- **Filename Cleanup:**
  - Remove illegal and unwanted characters or phrases

---

### Manga/Comic Mode (Creator Feeds Only)

- **Chronological Processing** — Oldest posts first

- **Filename Style Options:**
  - `Name: Post Title (Default)`
  - `Name: Original File`
  - `Name: Date Based (New)`
  - `Name: Title+G.Num (Post Title + Global Numbering)`

- **Best With:** Character filters set to manga/series title

---

### Folder Structure & Naming

- **Subfolders:**
  - Auto-created based on character name, post title, or `Known.txt`

  - "Subfolder per Post" option for further nesting

- **Smart Naming:** Cleans invalid characters and structures logically

---

### Thumbnail & Compression Tools
- **Download Thumbnails Only:**
  - Downloads small preview images from the API instead of full-sized files (if available).
  - **Interaction with "Scan Content for Images" (New in v4.1.1):** When "Download Thumbnails Only" is active, "Scan Content for Images" is auto-enabled, and only images found by the content scan are downloaded. See "What's New in v4.1.1" for details.
- **Scan Content for Images (New in v4.1.1):**
  - A UI option to scan the HTML content of posts for embedded image URLs (from `<img>` tags or direct links).
  - Resolves relative paths and helps capture images not listed in the API's formal attachments.
  - See the "What's New in v4.1.1?" section for a comprehensive explanation.
- **Compress to WebP** (via Pillow)
  - Converts large images to smaller WebP versions


---

###  Performance Features

- **Multithreading:**
  - For both post processing and file downloading

- **Multi-part Downloads:**
  - Toggleable in GUI
  - Splits large files into chunks
  - Granular chunk-level progress display

---

### Logging & Progress

- **Real-time Logs:** Activity, errors, skipped posts

- **Missed Character Log:** Shows skipped keywords in easy-to-read list

- **External Links Log:** Shows links (unless disabled in some modes)

- **Export Links:** Save `.txt` of links (Only Links mode)

---

### Configuration & Settings

- **`Known.txt` for Smart Folder Naming:** (Located in the application's directory)
  - User-editable file for preferred names, series titles, or keywords.
  - Used as an intelligent fallback for folder creation when "Separate Folders by Name/Title" is enabled.
  - Supports simple entries (e.g., `My Series`) and grouped entries for aliases (e.g., `(Folder Name, alias1, alias2)`).
- **Application Settings:** UI preferences and some operational settings are saved by the application (e.g., manga filename style, multi-part download preference). Some settings, like cookie details or specific filter scopes, are session-based.
- **Editable Within GUI:** Many settings and the `Known.txt` list (for simple entries) can be managed directly through the application interface.

---

## Installation

---

### Requirements

- Python 3.6 or higher  
- pip

---

### Install Dependencies

```bash
pip install PyQt5 requests Pillow

```

***

## ** Build a Standalone Executable (Optional)**

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Run:
```bash
pyinstaller --name "Kemono Downloader" --onefile --windowed --icon="Kemono.ico" main.py
```

3. Output will be in the `dist/` folder.

***

## **Key Files**
- **`Known.txt`:** (Located in the application's directory) Stores character names, series titles, or keywords for organizing downloaded content into specific folders.
  
  - Supports simple entries (e.g., `My Series`) and grouped entries for aliases (e.g., `(Folder Name, alias1, alias2)` where "Folder Name" is the name of the created folder, and all terms are used for matching).

- **Application Settings:** The application uses `QSettings` to store UI preferences and some operational settings. The actual storage location and format (e.g., .ini file, registry entry) depend on your operating system.
- **`cookies.txt` (Optional):** If using the "Use Cookie" feature without specifying a direct string or file, the app looks for `cookies.txt` in its directory. Must be Netscape format.

***

## ** Feedback & Support**

Issues? Suggestions?  
Open an issue on the [GitHub repository](https://github.com/Yuvi9587/kemono-downloader) or join our community.