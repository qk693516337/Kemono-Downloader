# Kemono Downloader - Comprehensive Feature Guide

This guide provides a detailed overview of all user interface elements, input fields, buttons, popups, and functionalities available in the application.

---

## Main Window: Core Functionality

The application is divided into a **configuration panel on the left** and a **status/log panel on the right**.

### Primary Inputs (Top-Left)

- **URL Input Field**  
  Starting point for most downloads. Paste a URL for a specific post or an entire creator's feed. The app adapts based on the URL type.

- **🎨 Creator Selection Popup**  
  Opens a dialog with all known creators.
  - **Search and Queue:** Search and queue multiple creators for batch downloads.  
  - **Check for Updates:** Select a single creator to enable update-only mode, downloading only new content.

- **Download Location**  
  The folder where all content is saved.  
  - *Browse...* button to select from your computer.

- **Page Range (Start/End)**  
  *For creator feed URLs only.* Download a specific range of pages, e.g., pages 5–10 instead of the whole feed.

---

## Filtering & Naming (Left Panel)

Precise control over what gets downloaded and how it’s named/organized.

- **Filter by Character(s):**  
  Download content featuring specific characters; enter multiple names separated by commas.

- **Filter: [Scope] Button:**  
  Changes how the character filter works:
  - *Title:* Character name must be in post title.
  - *Files:* Character name must be in filenames.
  - *Both:* Combines Title and Files.
  - *Comments (Beta):* Character name mentioned in comments.

- **Skip with Words:**  
  Avoid unwanted content via keywords (e.g., WIP, sketch).

- **Scope: [Type] Button:**  
  Changes how the skip filter works:
  - *Posts:* Skip entire post if keyword is in title.
  - *Files:* Skip individual files if keyword is in filename.
  - *Both:* Both levels.

- **Remove Words from name:**  
  Cleans filenames by removing specified terms (e.g., "patreon", "HD").

---

## File Type Filter (Radio Buttons)

Choose what kind of content to download:

- **All**  
- **Images/GIFs**  
- **Videos**  
- **🎧 Only Audio**  
- **📦 Only Archives**  
- **🔗 Only Links:**  
  Scans descriptions for external links (Mega, Google Drive, etc.) and logs them—does *not* download files.

- **More...**  
  Opens a dialog for text-only downloads.  
  - Save post descriptions or comments as **PDF, DOCX, or TXT**.  
  - **Single PDF**: Combine all downloaded posts' text into one sorted PDF.

---

## Download Options & Advanced Settings (Checkboxes)

- **Skip .zip:** Ignore archive files (.zip) during downloads.
- **Download Thumbnails Only:** Fetch only preview images, not full-resolution files.
- **Scan Content for Images:** Ensures all embedded images in post text are downloaded.
- **Compress to WebP:** Converts large images to efficient WebP format to save space.
- **Keep Duplicates:**  
  Dialog to control handling of duplicate files:
  - Default: skip duplicates
  - Option: keep all duplicates
  - Limit: e.g., keep up to 2 copies
- **Subfolder per Post:** Organizes by making a folder per post, named after the post title.
- **Date Prefix:** Adds date to folder name (e.g., `2025-07-25 Post Title`) when *Subfolder per Post* is enabled.
- **Separate Folders by Known.txt:** Organizes based on your Known Names list.
- **Use Cookie:**  
  Access paywalled content using browser cookies. Paste a cookie string or select a `cookies.txt` file.
- **Use Multithreading:**  
  Speeds up feed downloads by processing posts in parallel. Set configurable thread count.
- **Show External Links in Log:**  
  Displays a secondary log panel for external links.

---

## Known Names Management (Bottom-Left)

Automates creation of organized, named folders.

- **Known Shows/Characters List:**  
  Displays all saved names/groups.
- **Search...:** Filter the list to find names quickly.
- **Open Known.txt:** Edit the source file directly.
- **Add New Name:**
  - *Single Name:*  
    Typing `Tifa Lockhart` + ➕ Add = entry matching "Tifa Lockhart"
  - *Group:*  
    Typing `(Boa, Hancock, Snake Princess)~` + ➕ Add = one entry matching "Boa", "Hancock", or "Snake Princess"... all saved in a combined folder.
- **⤵️ Add to Filter:**  
  Select multiple Known Names and add them all to "Filter by Character(s)" at once.
- **🗑️ Delete Selected:**  
  Remove highlighted entries from your list.

---

## Action Buttons & Status Controls

- **⬇️ Start Download / 🔗 Extract Links:**  
  Main action button:
  - *Normal Mode:* Starts downloads as per current settings.
  - *Update Mode:* After selecting a creator, changes to 🔄 *Check for Updates*.
  - *Update Confirmation:* After new posts are found, changes to ⬇️ *Start Download (X new)*.
  - *Link Extraction Mode:* Changes text to 🔗 *Extract Links*.
  
- **⏸️ Pause / ▶️ Resume Download:**  
  Temporarily halt/resume downloads. Some settings (like filters) can be changed during pause.

- **❌ Cancel & Reset UI:**  
  Stops downloads, resets UI to clean state. Retains URL & Download Location.

- **Error Button:**  
  Shows number of files that failed to download. Opens a dialog to:
    - Retry selected failed files
    - Export failed URLs as `.txt`

- **🔄 Reset (Top-Right):**  
  Hard reset; clears logs and returns UI to default.

- **⚙️ (Settings):**  
  Opens main settings.

- **📜 (History):**  
  Opens download history.

- **? (Help):**  
  Opens user guide.

- **❤️ Support:**  
  Info on how to support the developer.

---

## Specialized Modes & Features

### ⭐ Favorite Mode

Transforms the UI for collection management.

- URL input is **disabled**
- Main buttons replaced with:
  - **🖼️ Favorite Artists:** Browse/queue favorite creators.
  - **📄 Favorite Posts:** Browse/queue favorite posts.

- **Scope: [Location] Button:**  
  Toggle favorite content saving location:
  - *Selected Location*: All in main folder
  - *Artist Folders*: Creates subfolder for each artist

### 📖 Manga/Comic Mode

Designed for sequential content.

- **Reverse Download Order:**  
  Fetches/downloads oldest → newest.
- **Enables Special Naming:**  
  *Name: [Style]* button lets you pick naming conventions:
  - By Post Title
  - By Date
  - Sequential numbers (001, 002, 003...)
- **Disables Multithreading** (certain styles):  
  For perfect sequential order, multithreading is off for some naming modes.

---

## Session & Error Management

- **Session Restore:**  
  On abrupt closure, detects incomplete sessions. UI shows 🔄 *Restore Download* to resume or discard session.

- **Update Checking:**  
  Select creator via 🎨 Creator Selection Popup to compare server posts with local history. Prompts for new-only downloads.

---

## Logging & Monitoring

- **Progress Log:**  
  Real-time status of downloads, saves, skips, and errors.

- **👁️ Log View Toggle:**  
  Switch views:
    - *Progress Log:* Standard log
    - *Missed Character Log:* Shows possible new character names from skipped posts—useful for expanding your filters.

---

