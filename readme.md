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

[![](https://img.shields.io/badge/📚%20Full%20Feature%20List-FFD700?style=for-the-badge&logoColor=black&color=FFD700)](features.md)
[![](https://img.shields.io/badge/📝%20License-90EE90?style=for-the-badge&logoColor=black&color=90EE90)](LICENSE)
[![](https://img.shields.io/badge/⚠️%20Important%20Note-FFCCCB?style=for-the-badge&logoColor=black&color=FFCCCB)](note.md)

</div>


---

## Feature Overview

Kemono Downloader offers a range of features to streamline your content downloading experience:

- **User-Friendly Interface:** A modern PyQt5 GUI for easy navigation and operation.

- **Flexible Downloading:**
  - Download content from Kemono.su (and mirrors) and Coomer.party (and mirrors).
  - Supports creator pages (with page range selection) and individual post URLs.
  - Standard download controls: Start, Pause, Resume, and Cancel.

- **Powerful Filtering:**
  - **Character Filtering:** Filter content by character names. Supports simple comma-separated names and grouped names for shared folders.
  - **Keyword Skipping:** Skip posts or files based on specified keywords.
  - **Filename Cleaning:** Remove unwanted words or phrases from downloaded filenames.
  - **File Type Selection:** Choose to download all files, or limit to images/GIFs, videos, audio, or archives. Can also extract external links only.

- **Customizable Downloads:**
  - **Thumbnails Only:** Option to download only small preview images.
  - **Content Scanning:** Scan post HTML for `<img>` tags and direct image links, useful for images embedded in descriptions.
  - **WebP Conversion:** Convert images to WebP format for smaller file sizes (requires Pillow library).

- **Organized Output:**
  - **Automatic Subfolders:** Create subfolders based on character names (from filters or `Known.txt`) or post titles.
  - **Per-Post Subfolders:** Option to create an additional subfolder for each individual post.

- **Manga/Comic Mode:**
  - Downloads posts from a creator's feed in chronological order (oldest to newest).
  - Offers various filename styling options for sequential reading (e.g., post title, original name, global numbering).

- **⭐ Favorite Mode:**
  - Directly download from your favorited artists and posts on Kemono.su.
  - Requires a valid cookie and adapts the UI for easy selection from your favorites.
  - Supports downloading into a single location or artist-specific subfolders.

- **Performance & Advanced Options:**
  - **Cookie Support:** Use cookies (paste string or load from `cookies.txt`) to access restricted content.
  - **Multithreading:** Configure the number of simultaneous downloads/post processing threads for improved speed.

- **Logging:**
  - A detailed progress log displays download activity, errors, and summaries.

- **Multi-language Interface:** Choose from several languages for the UI (English, Japanese, French, Spanish, German, Russian, Korean, Chinese Simplified).

- **Theme Customization:** Selectable Light and Dark themes for user comfort.

---

## ✨ What's New in v6.0.0

This release focuses on providing more granular control over file organization and improving at-a-glance status monitoring.

### New Features

- **Live Error Count on Button**  
  The **"Error" button** now dynamically displays the number of failed files during a download. Instead of opening the dialog, you can quickly see a live count like `(3) Error`, helping you track issues at a glance.

- **Date Prefix for Post Subfolders**  
  A new checkbox labeled **"Date Prefix"** is now available in the advanced settings.  
  When enabled alongside **"Subfolder per Post"**, it prepends the post's upload date to the folder name (e.g., `2025-07-11 Post Title`).  
  This makes your downloads sortable and easier to browse chronologically.

- **Keep Duplicates Within a Post**  
  A **"Keep Duplicates"** option has been added to preserve all files from a post — even if some have the same name.  
  Instead of skipping or overwriting, the downloader will save duplicates with numbered suffixes (e.g., `image.jpg`, `image_1.jpg`, etc.), which is especially useful when the same file name points to different media.

### Bug Fixes

- The downloader now correctly renames large `.part` files when completed, avoiding leftover temp files.
- The list of failed files shown in the Error Dialog is now saved and restored with your session — so no errors get lost if you close the app.
- Your selected download location is remembered, even after pressing the **Reset** button.
- The **Cancel** button is now enabled when restoring a pending session, so you can abort stuck jobs more easily.
- Internal cleanup logs (like "Deleting post cache") are now excluded from the final download summary for clarity.

---

## 📅 Next Update Plans

### 🔖 Post Tag Filtering (Planned for v6.1.0)

A powerful new **"Filter by Post Tags"** feature is planned:

- Filter and download content based on specific post tags.
- Combine tag filtering with current filters (character, file type, etc.).
- Use tag presets to automate frequent downloads.

This will provide **much greater control** over what gets downloaded, especially for creators who use tags consistently.

### 📁 Creator Download History (.json Save)

To streamline incremental downloads, a new system will allow the app to:

- Save a `.json` file with metadata about already-downloaded posts.
- Compare that file on future runs, so only **new** posts are downloaded.
- Avoids duplication and makes regular syncs fast and efficient.

Ideal for users managing large collections or syncing favorites regularly.

---

## 💻 Installation

### Requirements

- Python 3.6 or higher
- pip (Python package installer)

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

<div align="center">

[![](https://img.shields.io/badge/📝%20Ko-fi000000?style=for-the-badge&logoColor=black&color=90EE90)](https://ko-fi.com/yuvi427183)
[![](https://img.shields.io/badge/🍺%20Buy%20Me%20a%20Coffee-FFCCCB?style=for-the-badge&logoColor=black&color=FFDD00)](https://buymeacoffee.com/yuvi9587)

</div>
