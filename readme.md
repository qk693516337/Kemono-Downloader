# **Kemono Downloader v3.3.0**

A feature-rich GUI application built with PyQt5 to download content from **Kemono.su** or **Coomer.party**.  
Offers powerful filtering, smart organization, manga-specific tools, link extraction, and performance tuning.

This version introduces:  
- Skipped Character Review via Eye Toggle  
- Grouped Folder Naming (e.g., `(Boa, Hancock)`)  
- Refined UI behavior and bug fixes

***

## **🚀 What's New in v3.3.0**

### **👁 Skipped Characters Review (Eye Toggle)**

A new toggle button (👁) above the progress bar reveals a list of characters that appeared in the creator's feed but were skipped due to missing filters.  
Helps users avoid missed content by showing what they might have excluded unknowingly.

- Only available after download.  
- Hidden by default and toggled manually.

---

### **📁 Grouped Folder Naming via Parentheses**

Users can now group multiple aliases for a character under one folder by using parentheses.  
Example:  
`(Boa, Hancock), Robin` → Both "Boa" and "Hancock" content will be saved to a folder named `Boa Hancock`.

Useful for creators who name the same character inconsistently.

***

## **🧩 Core Features**

### **🎛 Simple GUI**
- PyQt5-based interface
- Dark theme, responsive layout

---

### **📥 Supports Post and Creator URLs**
- Download a single post or an entire creator feed

---

### **🔢 Page Range Support**
- Optional range for creator feed pagination (disabled in Manga Mode)

---

### **🗂 Smart Folder System**
- Organizes by character name, post title, or custom folder
- Per-post subfolder option
- Uses fallback from `Known.txt`

---

### **📚 Known Names Manager**
- Add/edit/delete known characters or show names
- Names stored persistently in `Known.txt`

---

### **🔍 Advanced Filtering**
- **Filter by Character(s)**: Scope options — `Files`, `Titles`, `Both`, `Comments`
- **Skip with Words**: Filter by keywords in post/file names
- **Remove Words from Filename**: Clean filenames with unwanted terms
- **File Type Filtering**: All, Images/GIFs, Videos, Archives, or Only Links
- **Only Archives**: Filters `.zip` and `.rar` downloads
- **Only Links Mode**: Extracts links from post descriptions without downloading

---

### **📖 Manga/Comic Mode (Creator URLs Only)**
- Sorts posts from oldest to newest
- Auto naming by `Post Title` (default) or `Original Filename`
- Best used with grouped filter names (e.g., series titles)

---

### **🖼️ Image Compression**
- Large images converted to WebP (requires Pillow)
- Only compresses if size is reduced significantly

---

### **🖼 Download Thumbnails Only**
- Download post thumbnails instead of full content

---

### **⚙️ Multithreaded Downloads**
- Configurable thread count
- Speeds up creator feed downloads and parallel file saving

---

### **⏯ Download Controls**
- Start, cancel, and safely reset without clearing paths or URLs

---

### **📋 Logging System**
- Real-time logs for downloads and status messages
- Toggle Basic or Full verbosity
- Separate external links panel with `.txt` export support

***

## **🔧 Backend Enhancements**

- Improved retry logic for failed chunks
- Session-wide deduplication via MD5
- Better temp file cleanup
- Smart filename suffixing on conflicts
- Unwanted word removal in filenames

***

## **📦 Installation**

### **Requirements**
- Python 3.6+
- pip

### **Install Dependencies**
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
