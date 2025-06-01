<h1 align="center">Kemono Downloader v5.0.0</h1>

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

A powerful, feature-rich GUI application for downloading content from **[Kemono.su](https://kemono.su)** (and its mirrors like kemono.party) and **[Coomer.party](https://coomer.party)** (and its mirrors like coomer.su).
Built with PyQt5, this tool is designed for users who want deep filtering capabilities, customizable folder structures, efficient downloads, and intelligent automation, all within a modern and user-friendly graphical interface.

*This v5.0.0 release marks a significant feature milestone. Future updates are expected to be less frequent, focusing on maintenance and minor refinements.*

---

## What's New in v5.0.0?

Version 5.0.0 is a major update, introducing comprehensive new features and refining existing ones for a more powerful and streamlined experience:

### ⭐ Favorite Mode (Artists & Posts)
-   **Direct Downloads from Your Kemono.su Favorites:**
    -   Enable via the "**⭐ Favorite Mode**" checkbox.
    -   The UI adapts: URL input is replaced, and action buttons change to "**🖼️ Favorite Artists**" and "**📄 Favorite Posts**".
    -   "**🍪 Use Cookie**" is automatically enabled and required.
-   **Favorite Artists Dialog:** Fetches and lists your favorited artists. Select one or more to queue for download.
-   **Favorite Posts Dialog:** Fetches and lists your favorited posts, grouped by artist. Includes search, selection, and known name highlighting in post titles.
-   **Flexible Download Scopes for Favorites:**
    -   `Scope: Selected Location`: Downloads all selected favorites into the main "Download Location".
    -   `Scope: Artist Folders`: Creates a subfolder for each artist within the main "Download Location".
-   Standard filters (character, skip words, file type) apply to content downloaded via Favorite Mode.

### 🎨 Creator Selection Popup
-   Click the "**🎨**" button next to the URL input to open the "Creator Selection" dialog.
-   Loads creators from your `creators.json` file (expected in the app's directory).
-   Search, select multiple creators, and their names are added to the URL input, comma-separated.
-   Choose download scope (`Characters` or `Creators`) for items added via this popup, influencing folder structure.

### 🎯 Advanced Character Filtering & `Known.txt` Integration
-   **Enhanced Filter Syntax:**
    -   `Nami`: Simple character filter.
    -   `(Vivi, Ulti, Uta)`: Groups distinct characters into a shared folder for the session (e.g., "Vivi Ulti Uta"). Adds "Vivi", "Ulti", "Uta" as *separate* entries to `Known.txt` if new.
    -   `(Boa, Hancock)~`: Defines "Boa" and "Hancock" as aliases for the *same character/entity*. Creates a shared folder (e.g., "Boa Hancock"). Adds "Boa Hancock" as a *single group entry* to `Known.txt` if new, with "Boa" and "Hancock" as its aliases.
-   **"Add to Filter" Button (⤵️):** Opens a dialog to select names from your `Known.txt` (with search) and add them to the "Filter by Character(s)" field. Grouped names from `Known.txt` are added with the `~` syntax.
-   **New Name Confirmation:** When new, unrecognized names/groups are used in the filter, a dialog prompts to add them to `Known.txt` with appropriate formatting.

### 📖 Manga/Comic Mode Enhancements
-   **"Title+G.Num" Filename Style:** (Post Title + Global Numbering) All files across posts get the post title prefix + a global sequential number (e.g., `Chapter 1_001.jpg`, `Chapter 2_003.jpg`).
-   **Optional Filename Prefix:** For "Original File" and "Date Based" manga styles, an input field appears to add a custom prefix to filenames.

### 🖼️ Enhanced Image & Content Handling
-   **"Scan Content for Images":** A checkbox to scan post HTML for `<img>` tags and direct image links, resolving relative paths. Crucial for images embedded in descriptions but not in API attachments.
    -   When "Download Thumbnails Only" is active, "Scan Content for Images" is auto-enabled, and *only* content-scanned images are downloaded.
-   **"🎧 Only Audio" Filter Mode:** Dedicated mode to download only common audio formats (MP3, WAV, FLAC, etc.).
-   **"📦 Only Archives" Filter Mode:** Exclusively downloads `.zip` and `.rar` files.

### ⚙️ UI & Workflow Improvements
-   **Cookie Management:**
    -   Directly paste cookie strings.
    -   Browse and load `cookies.txt` files.
    -   Automatic fallback to `cookies.txt` in the app directory.
-   **Multi-part Download Toggle:** Button in the log area to easily switch multi-segment downloads ON/OFF for large files.
-   **Log View Toggle (👁️ / 🙈):** Switch between the detailed "Progress Log" and the "Missed Character Log" (which now shows intelligently extracted key terms from skipped titles).
-   **Retry Failed Downloads:** Prompts at the end of a session to retry files that failed with recoverable errors (e.g., IncompleteRead).
-   **Persistent UI Defaults:** Key filter scopes ("Skip with Words" -> Posts, "Filter by Character(s)" -> Title) now reset to defaults on launch for consistency.
-   **Refined Onboarding Tour & Help Guide:** Updated guides accessible via the "❓" button.

---

## Core Features

This section details the primary functionalities of the Kemono Downloader.

### User Interface & Workflow

-   **Main Inputs:**
    -   **🔗 Kemono Creator/Post URL:** Paste the full URL of a Kemono/Coomer creator's page or a specific post.
        -   *Example (Creator):* `https://kemono.su/patreon/user/12345`
        -   *Example (Post):* `https://kemono.su/patreon/user/12345/post/98765`
    -   **🎨 Creator Selection Button:** (Next to URL input) Opens a dialog to select creators from `creators.json` to populate the URL field.
    -   **Page Range (Start to End):** For creator URLs, specify a range of pages to fetch. Disabled for single posts or Manga Mode.
    -   **📁 Download Location:** Browse to select the main folder for all downloads. Required unless in "🔗 Only Links" mode.
-   **Action Buttons:**
    -   **⬇️ Start Download / 🔗 Extract Links:** Initiates the primary operation based on current settings.
    -   **⏸️ Pause / ▶️ Resume Download:** Temporarily halt and continue the process. Some UI settings can be changed while paused.
    -   **❌ Cancel & Reset UI:** Stops the current operation and performs a "soft" UI reset (preserves URL and Directory inputs).
    -   **🔄 Reset:** (In log area) Clears all inputs, logs, and resets settings to default when idle.

### Filtering & Content Selection

-   **🎯 Filter by Character(s):**
    -   Enter character names, comma-separated.
    -   **Syntax Examples:**
        -   `Tifa, Aerith`: Matches posts/files with "Tifa" OR "Aerith". If "Separate Folders" is on, creates folders "Tifa" and "Aerith". Adds "Tifa", "Aerith" to `Known.txt` separately if new.
        -   `(Vivi, Ulti, Uta)`: Matches "Vivi" OR "Ulti" OR "Uta". Session folder: "Vivi Ulti Uta". Adds "Vivi", "Ulti", "Uta" to `Known.txt` as separate entries if new.
        -   `(Boa, Hancock)~`: Matches "Boa" OR "Hancock". Session folder: "Boa Hancock". Adds "Boa Hancock" as a single group entry to `Known.txt` if new (aliases: Boa, Hancock).
    -   **Filter: [Type] Button (Scope):** Cycles how this filter applies:
        -   `Filter: Files`: Checks individual filenames. Only matching files from a post are downloaded.
        -   `Filter: Title`: Checks post titles. All files from a matching post are downloaded.
        -   `Filter: Both`: Checks post title first. If no match, then checks filenames.
        -   `Filter: Comments (Beta)`: Checks filenames first. If no file match, then checks post comments. (Uses more API requests).
-   **🚫 Skip with Words:**
    -   Enter words (comma-separated) to skip content (e.g., `WIP, sketch`).
    -   **Scope: [Type] Button:** Cycles how skipping applies:
        -   `Scope: Files`: Skips individual files by name.
        -   `Scope: Posts`: Skips entire posts by title.
        -   `Scope: Both`: Post title first, then filenames.
-   **✂️ Remove Words from name:**
    -   Enter words (comma-separated) to remove from downloaded filenames (e.g., `patreon, [HD]`).
-   **Filter Files (Radio Buttons):**
    -   `All`: All file types.
    -   `Images/GIFs`: Common image formats.
    -   `Videos`: Common video formats.
    -   `📦 Only Archives`: Exclusively `.zip` and `.rar` files. Disables archive skipping and external link log.
    -   `🎧 Only Audio`: Common audio formats (MP3, WAV, FLAC, etc.).
    -   `🔗 Only Links`: Extracts and displays external links from post descriptions. Disables download options.
-   **Skip .zip / Skip .rar Checkboxes:** Avoid downloading these archive types (disabled if "📦 Only Archives" is active).

### Download Customization

-   **Download Thumbnails Only:** Downloads small API preview images.
    -   If "Scan Content for Images" is also active, *only* images found by content scan are downloaded (API thumbnails ignored).
-   **Scan Content for Images:** Scans post HTML for `<img>` tags and direct image links, resolving relative paths.
-   **Compress to WebP:** If Pillow is installed, converts images > 1.5MB to WebP if significantly smaller.
-   **🗄️ Custom Folder Name (Single Post Only):**
    -   Visible if downloading a single post URL AND "Separate Folders by Name/Title" is enabled.
    -   Set a custom folder name for that specific post's downloads.

### 📖 Manga/Comic Mode (Creator Feeds Only)

-   **Chronological Processing:** Downloads posts from oldest to newest.
-   **Page Range Disabled:** All posts are fetched for sorting.
-   **Filename Style Toggle Button (in log area):**
    -   `Name: Post Title (Default)`: First file named after post title; subsequent files in the same post keep original names.
    -   `Name: Original File`: All files attempt to keep original names. Optional prefix input appears.
    -   `Name: Title+G.Num`: All files across posts get post title prefix + global sequential number (e.g., `Chapter 1_001.jpg`). Disables post-level multithreading.
    -   `Name: Date Based`: Files named sequentially (e.g., `001.jpg`) by post date. Optional prefix input appears. Disables post-level multithreading.

### Folder Organization

-   **Separate Folders by Name/Title:** Creates subfolders based on "Filter by Character(s)" or post titles. Uses `Known.txt` as a fallback.
-   **Subfolder per Post:** If "Separate Folders" is on, creates an additional subfolder for each post.
-   **`Known.txt` Management (Bottom Left UI):**
    -   **List:** Displays primary names from `Known.txt`.
    -   **Add New:** Input field to add new names/groups.
        -   Simple: `My Series`
        -   Group (Separate Known.txt): `(Vivi, Ulti, Uta)`
        -   Group (Single Known.txt with `~`): `(Character A, Char A)~`
    -   **➕ Add Button:** Adds the name/group to `Known.txt`.
    -   **⤵️ Add to Filter Button:** Opens a dialog to select names from `Known.txt` to add to the "Filter by Character(s)" field.
    -   **🗑️ Delete Selected Button:** Removes selected names from `Known.txt`.
    -   **Open Known.txt Button:** Opens `Known.txt` in your default text editor for advanced editing.
    -   **❓ Button:** Opens this feature guide.

### Advanced & Performance

-   **🍪 Cookie Management:**
    -   **Use Cookie Checkbox:** Enables cookie usage.
    -   **Text Field:** Paste cookie string (e.g., `name1=value1; name2=value2`).
    -   **Browse... Button:** Select a `cookies.txt` file (Netscape format).
    -   *Behavior:* Text field takes precedence. If "Use Cookie" is checked and both are empty, tries to load `cookies.txt` from the app directory.
-   **Use Multithreading Checkbox & Threads Input:**
    -   *Creator Feeds:* Number of posts to process simultaneously.
    -   *Single Post URLs:* Number of files to download concurrently.
-   **Multi-part Download Toggle Button (in log area):**
    -   `Multi-part: ON`: Enables multi-segment downloads for large files. Can speed up large file downloads but may increase UI choppiness or log spam with many small files.
    -   `Multi-part: OFF (Default)`: Files downloaded in a single stream.
    -   Disabled if "🔗 Only Links" or "📦 Only Archives" mode is active.

### Logging & Monitoring

-   **📜 Progress Log / Extracted Links Log:** Main text area for detailed messages or extracted links.
-   **👁️ / 🙈 Log View Toggle Button:** Switches main log between:
    -   `👁️ Progress Log`: All download activity, errors, summaries.
    -   `🙈 Missed Character Log`: Key terms from post titles/content skipped due to character filters.
-   **Show External Links in Log Checkbox & Panel:** If checked, a secondary log panel displays external links from post descriptions (disabled in "Only Links" / "Only Archives" modes).
-   **Export Links Button:** (In "Only Links" mode) Saves extracted links to a `.txt` file.
-   **Progress Labels:** Display overall post progress and individual file download status/speed.

### ⭐ Favorite Mode (Downloading from Your Kemono.su Favorites)

-   **Enable:** Check the "**⭐ Favorite Mode**" checkbox (next to "🔗 Only Links").
-   **UI Changes:**
    -   URL input is replaced with a "Favorite Mode active" message.
    -   Action buttons change to "**🖼️ Favorite Artists**" and "**📄 Favorite Posts**".
    -   "**🍪 Use Cookie**" is auto-enabled and locked (required for favorites).
-   **🖼️ Favorite Artists Dialog:**
    -   Fetches and lists artists you've favorited on Kemono.su.
    -   Includes search, select all/deselect all, and a "Download Selected" button.
    -   Selected artists are added to a download queue.
-   **📄 Favorite Posts Dialog:**
    -   Fetches and lists posts you've favorited, grouped by artist and sorted by date.
    -   Includes search (title, creator, ID, service), select all/deselect all.
    -   Highlights known names from your `Known.txt` in post titles for easier identification.
    -   Selected posts are added to a download queue.
-   **Favorite Download Scope Button:** (Next to "Favorite Posts" button)
    -   `Scope: Selected Location`: All selected favorites download into the main "Download Location". Filters apply globally.
    -   `Scope: Artist Folders`: A subfolder (named after the artist) is created in the main "Download Location" for each artist. Content goes into their specific subfolder. Filters apply within each artist's folder.
-   **Filters:** Standard "Filter by Character(s)", "Skip with Words", and "Filter Files" options apply to content downloaded from favorites.

---

## Key Files

-   **`Known.txt`:** (Located in the application's directory)
    -   Stores your list of known shows, characters, or series titles for automatic folder organization.
    -   **Format:** Each line is an entry.
        -   Simple: `My Awesome Series`
        -   Grouped (single `Known.txt` entry, shared folder): `(Boa, Hancock)` - creates folder "Boa Hancock", aliases "Boa", "Hancock".
    -   Used as a fallback for folder naming if "Separate Folders" is on and no active filter matches.
-   **`creators.json`:** (Expected in the application's directory)
    -   Used by the "🎨 Creator Selection Popup".
    -   A JSON file containing a list of creator objects. Expected structure: `[ [ {creator1_data}, {creator2_data}, ... ] ]` or a flat list `[ {creator1_data}, ... ]`.
    -   Each creator object should ideally have `name`, `service`, `id`, and optionally `favorited` (integer count for sorting in popup).
    -   *Example entry in the inner list:* `{"id": "12345", "name": "ArtistName", "service": "patreon", "favorited": 10}`
-   **`cookies.txt` (Optional):**
    -   If "Use Cookie" is enabled and no direct string/file is provided, the app looks for this in its directory.
    -   Must be in Netscape cookie file format.
-   **Application Settings:** UI preferences (like manga style, multipart preference) are saved by Qt's `QSettings` (location varies by OS). Cookie details and some filter scopes are session-based.

---

## Installation

### Requirements
-   Python 3.6 or higher
-   pip (Python package installer)

### Install Dependencies
Open your terminal or command prompt and run:

```bash
pip install PyQt5 requests Pillow
```

```bash
python main.py
```


### 2. Optional Setup

-   Place your `cookies.txt` in the root directory (if using cookies).
-   Prepare your `Known.txt` and `creators.json` in the same directory for advanced filtering and selection features.

---

## Tips & Best Practices

-   For best results, use **Favorite Mode** if you're a logged-in user with bookmarked artists/posts.
-   Use **Filter by Character(s)** and keep your `Known.txt` updated to reduce clutter and organize downloads.
-   Use the **multi-part toggle** for large video/audio files but disable it when downloading large batches of small images to reduce overhead.
-   Adjust **thread count** based on your internet speed and CPU; too many threads can result in API throttling.

---

## Troubleshooting

-   **Downloads not starting?**
    -   Ensure the download location is set.
    -   Check your filters aren't too strict.
    -   If in Favorite Mode, make sure cookie is set and valid.

-   **Missing characters/folders?**
    -   Review the Missed Character Log.
    -   Use the "Scan Content for Images" option if image links are embedded in descriptions.

-   **App crashes or logs errors?**
    -   Check the console/log area for stack traces.
    -   Run from terminal to capture more error output.
    -   Ensure `Known.txt` and `creators.json` are valid.

---

## Contribution

Feel free to fork this repo and submit pull requests for bug fixes, new features, or UI improvements!

---

## License

This project is released under the MIT License.

