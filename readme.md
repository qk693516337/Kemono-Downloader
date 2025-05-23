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

- **Fine-Grained Control:** Take your automatic folder organization to the next level with a personalized list of names, series titles, and keywords in `Known.txt`.
- **Primary Names & Aliases:** Define a main folder name and link multiple aliases to it. For example, `([Power], powwr, pwr, Blood devil)` ensures any post matching "Power" or "powwr" (in title or filename, depending on settings) gets saved into a "Power" folder. Simple entries like `My Series` are also supported.
- **Intelligent Fallback:** When "Separate Folders by Name/Title" is active, and if a post doesn't match any specific "Filter by Character(s)" input, the downloader consults `Known.txt` to find a matching primary name for folder creation.
- **User-Friendly Management:** Add or remove primary names directly through the UI, or click "Open Known.txt" for advanced editing (e.g., setting up aliases).

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

- **`Known.txt` for Smart Folder Naming:**
  - A user-editable file (`Known.txt`) stores a list of preferred names, series titles, or keywords.
  - Used as a fallback for folder creation when "Separate Folders by Name/Title" is enabled, helping to group content logically even without explicit character filters.
  - **Supports primary names and aliases:**
    - Simple entries: `My Favorite Series`
    - Grouped entries with a primary name for the folder: `([Primary Name], alias1, alias2)`

- **Stored in Standard App Data Path**

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

- `Known.txt` — character/show names used for folder organization
- Supports simple names (e.g., `My Series`) and grouped names with a primary folder name and aliases (e.g., `([Primary Folder Name], alias1, alias2)`).

***

## ** Feedback & Support**

Issues? Suggestions?  
Open an issue on the [GitHub repository](https://github.com/Yuvi9587/kemono-downloader) or join our community.
