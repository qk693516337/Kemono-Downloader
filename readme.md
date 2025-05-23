<h1 align="center">Kemono Downloader v3.5.0</h1>

<div align="center">
  <img src="https://github.com/Yuvi9587/Kemono-Downloader/blob/main/Read.png" alt="Kemono Downloader"/>
</div>

---

A powerful, feature-rich GUI application for downloading content from **[Kemono.su](https://kemono.su)** and **[Coomer.party](https://coomer.party)**.  
Built with **PyQt5**, this tool is ideal for users who want deep filtering, customizable folder structures, efficient downloads, and intelligent automation — all within a modern, user-friendly graphical interface.

---

##  What's New in v3.5.0?

Version 3.5.0 focuses on enhancing access to content and providing even smarter organization:

###  Cookie Management

- **Access Content:** Seamlessly download from Kemono/Coomer as if you were logged in by using your browser's cookies.
- **Flexible Input:**
  - Directly paste your cookie string (e.g., `name1=value1; name2=value2`).
  - Browse and load cookies from a `cookies.txt` file (Netscape format).
  - Automatic fallback to a `cookies.txt` file in the application directory if "Use Cookie" is enabled and no other source is specified.
- **Easy Activation:** A simple "Use Cookie" checkbox in the UI controls this feature.
- *Important Note: Cookie settings (text, file path, and enabled state) are configured per session and are not saved when the application is closed. You will need to re-apply them on each launch if needed.*

---

###  Advanced `Known.txt` for Smart Folder Organization

The `Known.txt` system has been revamped for improved performance and stability. The previous method of handling known names could become resource-intensive with large lists, potentially leading to application slowdowns or crashes. This new, streamlined system offers more direct control and robust organization.

- **Fine-Grained Control:** `Known.txt`, located in the application's directory, allows you to create a personalized list of names, series titles, and keywords for precise automatic folder organization when "Separate Folders by Name/Title" is enabled.

- **How It Works (Syntax and Behavior):**
  Each line in `Known.txt` represents an entry:
  - **Simple Entries:** A line like `My Awesome Series` defines both the term to match in content (post titles, filenames, etc., based on your filter scope) and the name of the folder where matching content will be saved ("My Awesome Series").
  - **Grouped Entries (Primary Folder Name & Aliases):** To group multiple search terms under a single, specific folder name, use parentheses. The format is `(FolderName, alias1, alias2, ...)`.
    - The **first item** inside the parentheses explicitly defines the name of the folder.
    - All items within the parentheses (including the first one) are used as aliases to match against content.
    - **Example:** An entry like `(Chainsaw Man, Denji, Pochita, Makima)` means:
      - Matching content (containing "Chainsaw Man", "Denji", "Pochita", or "Makima") will be saved into a folder named "Chainsaw Man".
    - **Another Example:** `(Power, powwr, pwr, Blood Devil)` will create a folder named "Power" for content matching any of those terms.

- **Intelligent Fallback:** If "Separate Folders by Name/Title" is active, and a post's content doesn't match any terms provided in the main "Filter by Character(s)" UI input, the downloader will then consult `Known.txt`. If a match is found in `Known.txt`, the content will be organized into the folder defined by that `Known.txt` entry.

- **User-Friendly Management:**
  - You can add new simple (non-grouped) entries to `Known.txt` directly using the list and "Add" button in the UI.
  - To create or modify grouped entries, or to make more complex changes, click the "Open Known.txt" button. This will open the file in your system's default text editor. The application reloads `Known.txt` on startup or when a download process begins.

---
##  What's in v3.4.0? (Previous Update)
This version brings significant enhancements to manga/comic downloading, filtering capabilities, and user experience:

###  Enhanced Manga/Comic Mode

- **New "Date Based" Filename Style:**

  - Perfect for truly sequential content! Files are named numerically (e.g., `001.jpg`, `002.jpg`, `003.ext`...) across an *entire creator's feed*, strictly following post publication order.

  - **Smart Numbering:** Automatically resumes from the highest existing number found in the series folder (and subfolders, if "Subfolder per Post" is enabled).

  - **Guaranteed Order:** Disables multi-threading for post processing to ensure sequential accuracy.

  - Works alongside the existing "Post Title" and "Original File Name" styles.

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

- Improved guide for new users, covering v3.4.0 features and existing core functions.

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

- **Flexible Options:**
  - Specify Page Range (disabled in Manga Mode)
  - Custom Folder Name for single posts

---

###  Smart Filtering

- **Character Name Filtering:**
  - Use `Tifa, Aerith` or group `(Boa, Hancock)` → folder `Boa Hancock`

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

- **Best With:** Character filters set to manga/series title

---

### Folder Structure & Naming

- **Subfolders:**
  - Auto-created based on character name, post title, or `Known.txt`

  - "Subfolder per Post" option for further nesting

- **Smart Naming:** Cleans invalid characters and structures logically

---

### Thumbnail & Compression Tools

- **Download Thumbnails Only**

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

###  Config System

- **`Known.txt` for Smart Folder Naming (Located in App Directory):**
  - A user-editable file that stores a list of preferred names, series titles, or keywords.
  - It's primarily used as an intelligent fallback for folder creation when "Separate Folders by Name/Title" is enabled.
  - **Syntax:**
    - Simple entries: `My Favorite Series` (creates folder "My Favorite Series", matches "My Favorite Series").
    - Grouped entries: `(Desired Folder Name, alias1, alias2)` (creates folder "Desired Folder Name"; matches "Desired Folder Name", "alias1", or "alias2").

- **Settings Stored in App Directory**

- **Editable Within GUI**

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

## ** Config Files**
- `settings.json` — Stores your UI preferences and settings.
- `Known.txt` — Stores character names, series titles, or keywords for organizing downloaded content into specific folders.
  - Supports simple entries (e.g., `My Series`) and grouped entries for aliases (e.g., `(Folder Name, alias1, alias2)` where "Folder Name" is the name of the created folder, and all terms are used for matching).

***

## ** Feedback & Support**

Issues? Suggestions?  
Open an issue on the [GitHub repository](https://github.com/Yuvi9587/kemono-downloader) or join our community.
