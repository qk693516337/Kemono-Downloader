# Kemono Downloader v3.4.0

A powerful, feature-rich GUI application for downloading content from **[Kemono.su](https://kemono.su)** and **[Coomer.party](https://coomer.party)**.  
Built with **PyQt5**, this tool is ideal for users who want deep filtering, customizable folder structures, efficient downloads, and intelligent automation — all within a modern, user-friendly graphical interface.

---

## ✨ What's New in v3.4.0?

This version brings significant enhancements to manga/comic downloading, filtering capabilities, and user experience:

---

### 📖 Enhanced Manga/Comic Mode

- **New "Date Based" Filename Style:**

  - Perfect for truly sequential content! Files are named numerically (e.g., `001.jpg`, `002.jpg`, `003.ext`...) across an *entire creator's feed*, strictly following post publication order.

  - **Smart Numbering:** Automatically resumes from the highest existing number found in the series folder (and subfolders, if "Subfolder per Post" is enabled).

  - **Guaranteed Order:** Disables multi-threading for post processing to ensure sequential accuracy.

  - Works alongside the existing "Post Title" and "Original File Name" styles.

---

### ✂️ "Remove Words from Filename" Feature

- Specify comma-separated words or phrases (case-insensitive) that will be automatically removed from filenames.

- Example: `patreon, [HD], _final` transforms `AwesomeArt_patreon_[HD]_final.jpg` into `AwesomeArt.jpg`.

---

### 📦 New "Only Archives" File Filter Mode

- Exclusively downloads `.zip` and `.rar` files.

- Automatically disables conflicting options like "Skip .zip/.rar" and external link logging.

---

### 🗣️ Improved Character Filter Scope - "Comments (Beta)"

- **File-First Check:** Prioritizes matching filenames before checking post comments for character names.

- **Comment Fallback:** Only checks comments if no filename match is found, reducing unnecessary API calls.

---

### 🧐 Refined "Missed Character Log"

- Displays a capitalized, alphabetized list of key terms from skipped post titles.

- Makes it easier to spot patterns or characters that might be unintentionally excluded.

---

### 🚀 Enhanced Multi-part Download Progress

- Granular visibility into active chunk downloads and combined speed for large files.

---

### 🗺️ Updated Onboarding Tour

- Improved guide for new users, covering v3.4.0 features and existing core functions.

---

### 🛡️ Robust Configuration Path

- Settings and `Known.txt` are now stored in the system-standard application data folder (e.g., `AppData`, `~/.local/share`).

---

## 🖥️ Core Features

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

### 🧠 Smart Filtering

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

### 📚 Manga/Comic Mode (Creator Feeds Only)

- **Chronological Processing** — Oldest posts first

- **Filename Style Options:**
  - `Name: Post Title (Default)`
  - `Name: Original File`
  - `Name: Date Based (New)`

- **Best With:** Character filters set to manga/series title

---

### 📁 Folder Structure & Naming

- **Subfolders:**
  - Auto-created based on character name, post title, or `Known.txt`

  - "Subfolder per Post" option for further nesting

- **Smart Naming:** Cleans invalid characters and structures logically

---

### 🖼️ Thumbnail & Compression Tools

- **Download Thumbnails Only**

- **Compress to WebP** (via Pillow)
  - Converts large images to smaller WebP versions

---

### ⚙️ Performance Features

- **Multithreading:**
  - For both post processing and file downloading

- **Multi-part Downloads:**
  - Toggleable in GUI
  - Splits large files into chunks
  - Granular chunk-level progress display

---

### 📋 Logging & Progress

- **Real-time Logs:** Activity, errors, skipped posts

- **Missed Character Log:** Shows skipped keywords in easy-to-read list

- **External Links Log:** Shows links (unless disabled in some modes)

- **Export Links:** Save `.txt` of links (Only Links mode)

---

### 🗃️ Config System

- **Known.txt:**
  - Stores names for smart folder suggestions
  - Supports aliases via `(alias1, alias2)`

- **Stored in Standard App Data Path**

- **Editable Within GUI**

---

## 💻 Installation

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

## **🛠️ Build a Standalone Executable (Optional)**

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

## **🗂 Config Files**

- `Known.txt` — character/show names used for folder organization
- Supports grouped names in format: `(Name1, Name2)`

***

## **💬 Feedback & Support**

Issues? Suggestions?  
Open an issue on the [GitHub repository](https://github.com/Yuvi9587/kemono-downloader) or join our community.
