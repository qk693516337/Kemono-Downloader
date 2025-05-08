# Kemono Downloader v3.0.0

A feature-rich GUI application built with PyQt5 to download content from [Kemono.su](https://kemono.su) or [Coomer.party](https://coomer.party) pages. It offers a wide array of filtering, organizing, and performance-tuning options including manga-specific handling, content deduplication, thread control, and smart folder creation.

---

## 🚀 What's New in v3.0.0

* **Manga Mode**: Smart file renaming based on post titles and upload sequence; handles single-image-per-post manga.
* **Enhanced Logging**:

  * Toggle between **Basic** and **Advanced** views.
  * Live log resizing and improved readability.
* **Dynamic Thread Control**:

  * Adjustable worker thread count.
  * Warnings and auto-caps on high thread values to prevent system slowdown or site rate-limiting.
* **Advanced Skip Filters**:

  * Skip posts/files based on title/filename keywords.
  * Visual cues in logs when posts are skipped.
* **External Link Detection**: Option to show extracted cloud/drive links in the log.
* **Cleaner UI**:

  * Redesigned layout.
  * Collapsible advanced settings.
  * Real-time feedback with improved progress indicators.

---

## 🧩 Core Features

* **GUI Interface**: User-friendly PyQt5-based design.
* **Supports Post and Creator URLs**: Handles individual post downloads or full creator feeds.
* **Smart Folder System**:

  * Organizes downloads using post title, known character/show names, or a custom folder per post.
  * Automatically detects and names folders based on matching keywords.
* **Known Names Manager**:

  * Add, search, and delete known characters/shows for smarter file organization.
  * Persistently saved to `Known.txt`.
* **Advanced Filters**:

  * Filter posts by known names in titles.
  * Skip posts or files containing words like `WIP`, `sketch`, etc.
  * Filter by media type: images, GIFs, or videos only.
* **Archive Control**:

  * Skip `.zip` and `.rar` files.
* **Image Compression**:

  * Convert large images (>1.5MB) to WebP (requires Pillow).
* **Thumbnails Only**:

  * Uses a local API to fetch and download thumbnail previews instead of full files.
* **Multithreaded Downloads**:

  * Adjustable thread count with warnings at unsafe values.
  * Full threading support for creators, single-threaded fallback for single posts.
* **Download Management**:

  * Cancel in-progress downloads.
  * Skip current file in single-thread mode.
* **Dark Mode**: Clean and modern dark UI theme.

---

## 🔧 Backend Logic Enhancements

* **Post Order Management**:

  * Manga Mode reverses post fetch order to preserve original upload sequence.
* **Hash-based Deduplication**:

  * Avoids re-downloading content already present.
* **Smart File Naming**:

  * Handles inconsistent naming in multi-language manga posts.
  * Applies cleaned post titles with page indices.
* **Efficient Progress Tracking**:

  * Shows percentage, active download status, and current file.
  * Summarizes per-post download outcomes.
* **Error Handling**:

  * Catches broken links, HTTP issues, and content skips with clear log feedback.

---

## 📦 Installation

### Requirements:

* Python 3.6+
* Pip packages:

```bash
pip install PyQt5 requests Pillow
```

### Run it:

```bash
python main.py
```

---

## 🖥️ Build as .EXE

Use `PyInstaller` for a single-file Windows executable:

1. Convert `.png` icon to `.ico` format (if needed).
2. Run:

```bash
pyinstaller --noconsole --onefile --name "Kemono Downloader" --icon=Kemono.ico main.py
```

3. Your `.exe` will be inside the `dist/` folder.

---

## 💡 Usage Tips

1. **Enter a Creator/Post URL**.
2. **Set your Download Location**.
3. (Optional) Choose known characters to filter or organize.
4. Apply filters (skip keywords, file types).
5. Tweak thread settings or enable Manga Mode if needed.
6. Hit **Start Download** and monitor progress!

---

## 🗃️ Configuration File

* `Known.txt` stores known character/show names.
* Each name should be on a new line.

---

## 🤝 Contributing

Contributions are welcome! Open an issue or submit a pull request if you have improvements, bug reports, or feature ideas.

---


