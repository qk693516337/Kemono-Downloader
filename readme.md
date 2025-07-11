<h1 align="center">Kemono Downloader v6.0.0</h1>

<div align="center">

<table>
  <tr>
    <td align="center">
      <img src="Read/Read.png" alt="Default Mode" width="400"><br>
      <strong>Default</strong>
    </td>
    <td align="center">
      <img src="Read/Read1.png" alt="Favorite Mode" width="400"><br>
      <strong>Favorite Mode</strong>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="Read/Read2.png" alt="Single Post" width="400"><br>
      <strong>Single Post</strong>
    </td>
    <td align="center">
      <img src="Read/Read3.png" alt="Manga/Comic Mode" width="400"><br>
      <strong>Manga/Comic Mode</strong>
    </td>
  </tr>
</table>

</div>

---

A powerful, feature-rich GUI application for downloading content from **[Kemono.su](https://kemono.su)** (and its mirrors like kemono.party) and **[Coomer.party](https://coomer.party)** (and its mirrors like coomer.su).

Built with PyQt5, this tool is designed for users who want deep filtering capabilities, customizable folder structures, efficient downloads, and intelligent automation — all within a modern and user-friendly graphical interface.

<div align="center">

[![](https://img.shields.io/badge/Full_Feature_List-FFD700?style=for-the-badge&logoColor=black&color=FFD700)](features.md)
[![](https://img.shields.io/badge/License-90EE90?style=for-the-badge&logoColor=black&color=90EE90)](LICENSE)
[![](https://img.shields.io/badge/Important_Note-FFCCCB?style=for-the-badge&logoColor=black&color=FFCCCB)](note.md)

</div>

---

## 🚀 Feature Overview

Kemono Downloader offers a wide range of features to streamline your content downloading experience:

### 🎛️ User-Friendly Interface
- Built with PyQt5 for a modern and intuitive experience.

### 📥 Flexible Downloading
- Download from Kemono.su and Coomer.party (and their mirrors).
- Supports full creator pages and individual post URLs.
- Standard download controls: Start, Pause, Resume, Cancel.

### 🔎 Powerful Filtering
- **Character Filtering**: Filter by comma-separated or grouped character names.
- **Keyword Skipping**: Skip posts/files by keywords.
- **Filename Cleaning**: Clean downloaded filenames.
- **File Type Selection**: Choose all, images, videos, audio, archives, or external links only.

### 📁 Customizable Downloads
- **Thumbnails Only**: Download preview images only.
- **Content Scanning**: Finds `<img>` tags and image links in HTML.
- **WebP Conversion**: Convert images to WebP (requires Pillow).

### 🗂 Organized Output
- **Subfolders by Character or Post Title**
- **Per-Post Subfolders**: Optional for better organization.

### 📚 Manga/Comic Mode
- Downloads posts chronologically.
- Various filename styles for reading convenience.

### ⭐ Favorite Mode
- Download from your favorited artists and posts.
- Requires a valid cookie.
- Supports global or per-artist subfolders.

### ⚙️ Performance & Advanced Options
- **Cookie Support**: Paste string or use `cookies.txt`.
- **Multithreading**: Configure threads for speed.

### 🧾 Logging
- Detailed logs of download activity, errors, and status.

### 🌐 Multi-language Support
- UI in English, Japanese, French, Spanish, German, Russian, Korean, Chinese (Simplified).

### 🎨 Theme Customization
- Light and Dark themes available.

---

## ✨ What's New in v6.0.0

### 🔔 New Features

- **Live Error Count**: Error button shows live count like `(3) Error`.
- **Date Prefix for Subfolders**: Adds upload date to subfolder names (e.g. `2025-07-11 Post Title`).
- **Keep Duplicates**: Save all files in a post, even with duplicate names (adds `_1`, `_2`, etc.).

### 🐞 Bug Fixes & Improvements

- `.part` files now correctly renamed after completion.
- Failed files list is saved/restored with sessions.
- Download location now remembered after clicking "Reset".
- "Cancel" is available on session restore.
- Cleaner final download log.

---

## 🛠️ Planned for v6.1.0

### 🔖 Tag Filtering
- Filter posts by **tags**.
- Combine with existing filters.
- Use tag presets for repeatable workflows.

### 📁 Creator Download History
- Save a `.json` with already-downloaded posts.
- Skip previously downloaded posts automatically.

---

## 📦 Installation

### Requirements

- Python 3.6 or newer
- `pip` (Python package installer)

### Install Dependencies

```bash
pip install PyQt5 requests Pillow mega.py
```

### Running the Application
Navigate to the application's directory in your terminal and run:
```bash
python main.py
```

### Optional Setup
-   **Main Inputs:**
-   Place your `cookies.txt` in the root directory (if using cookies).
-   Prepare your `Known.txt` and `creators.json` in the same directory for advanced filtering and selection features.

---

## Troubleshooting

### AttributeError: module 'asyncio' has no attribute 'coroutine'

If you encounter an error message similar to:
```
AttributeError: module 'asyncio' has no attribute 'coroutine'. Did you mean: 'coroutines'?
```
This usually means that a dependency, often `tenacity` (used by `mega.py`), is an older version that's incompatible with your Python version (typically Python 3.10+).

To fix this, activate your virtual environment and run the following commands to upgrade the libraries:

```bash
pip install --upgrade tenacity
pip install --upgrade mega.py
```

---

## Contribution

Feel free to fork this repo and submit pull requests for bug fixes, new features, or UI improvements!

---

## License

This project is under the Custom Licence

## Star History

<table align="center" style="border-collapse: collapse; border: none; margin-left: auto; margin-right: auto;">
  <tr>
    <td align="center" valign="middle" style="padding: 10px; border: none;">
      <a href="https://www.star-history.com/#Yuvi9587/Kemono-Downloader&Date">
        <img src="https://api.star-history.com/svg?repos=Yuvi9587/Kemono-Downloader&type=Date" alt="Star History Chart" width="650">
      </a>
</table>

👉 See [features.md](features.md) for the full feature list.
