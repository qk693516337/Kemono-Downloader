# Kemono Downloader v3.3.0

A powerful, feature-rich GUI application for downloading content from **[Kemono.su](https://kemono.su)** and **[Coomer.party](https://coomer.party)**.  
Built with **PyQt5**, this tool is ideal for users who want deep filtering, customizable folder structure, efficient downloads, and intelligent automation — all within a modern GUI.

---

## 🔄 Recent Updates (v3.3.0)

### Skipped Characters Review (Eye Toggle)
- After a download, you can toggle a log view to review characters or keywords that were skipped based on your filters.
- Helps catch overlooked content you might want to adjust filters for.

### Grouped Folder Naming
- You can group aliases together using parentheses.
- Example: `(Boa, Hancock), Robin` → Downloads for "Boa" and "Hancock" go into one folder: `Boa Hancock`.
- Great for creators who use inconsistent naming.

---

## 🖥 User Interface & Workflow

### Clean PyQt5 GUI
- Simple and responsive interface
- Dark theme for long usage comfort
- Persistent settings saved between sessions
- Introductory tour for first-time users

### Download Modes
- Download from:
  - **Single Post URL**
  - **Entire Creator Feed**
- Optional:
  - **Page Range** for creator feeds
  - **Custom folder name** for single-post downloads

---

## 🧠 Smart Filtering

### Character Name Filtering
- Input comma-separated names to only include relevant content.
- Filtering modes:
  - **Files**: Checks filenames
  - **Titles**: Checks post titles
  - **Both**: Hybrid mode
  - **Comments**: Also scans post comments for matches

### Skip Words
- Enter words to **exclude** files or posts.
- Modes: File-level, Post-level, or Both
- Helps exclude WIPs, previews, sketches, etc.

### File Type Filters
- Filter download targets by type:
  - All
  - Images/GIFs
  - Videos
  - Archives
  - External Links (no downloads)

### Filename Cleanup
- Auto-remove unwanted keywords from filenames (e.g., `[HD]`, `patreon`)

---

## 📚 Manga/Comic Mode

Special handling for serialized content:
- Automatically fetches posts **oldest to newest**
- File naming options:
  - Use **Post Title** (e.g., `MyChapter1.jpg`)
  - Use **Original Filename** (e.g., `page_001.png`)
- Ignores page ranges and applies full-feed scan
- Works best when paired with grouped name filters (e.g., series titles)

---

## 📁 Folder Structure & Naming

- Auto-foldering by:
  - Character name
  - Post title
  - Custom name (for post URLs)
- Optional:
  - Subfolder per post
- Auto-detection and fallback from `Known.txt` if needed
- Smart cleaning of folder/file names to remove illegal characters

---

## 🖼 Thumbnail & Compression Tools

- **Thumbnail Mode**: Downloads only the preview thumbnails
- **Image Compression** (via Pillow):
  - Large images auto-converted to WebP
  - Only saved if final size is significantly smaller

---

## ⚙️ Performance Features

- **Multithreading**: Set number of threads for concurrent file and post downloads
- **Multi-part Downloads**:
  - Large files split into multiple threads for faster retrieval
  - Detailed chunk-level progress tracking
  - Smart retries and fallback on failure

---

## 📋 Logging & Progress

- Real-time log output with two views:
  - **Progress Log**
  - **Missed Character Summary**
- Log filters external links and organizes them separately
- Export logs as `.txt` for backup/reference
- Auto-log failed/skipped files and links

---

## 🗃 Config System

- `Known.txt`: Add frequently used names for fallback filtering and folder naming
- Auto-loaded and saved in system AppData (or local fallback)
- GUI for editing known names inside the app

---

## 💻 Installation

### Requirements
- Python 3.6 or higher
- pip

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
