<h1 align="center">Kemono Downloader v5.5.0</h1>

<table align="center">
  <tr>
    <td align="center">
      <img src="Read/Read.png" alt="Default Mode" width="400"/><br>
      <strong>Default</strong>
    </td>
    <td align="center">
      <img src="Read/Read1.png" alt="Favorite Mode" width="400"/><br>
      <strong>Favorite mode</strong>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="Read/Read2.png" alt="Single Post" width="400"/><br>
      <strong>Single Post</strong>
    </td>
    <td align="center">
      <img src="Read/Read3.png" alt="Manga/Comic Mode" width="400"/><br>
      <strong>Manga/Comic Mode</strong>
    </td>
  </tr>
</table>
---

A powerful, feature-rich GUI application for downloading content from **[Kemono.su](https://kemono.su)** (and its mirrors like kemono.party) and **[Coomer.party](https://coomer.party)** (and its mirrors like coomer.su).
Built with PyQt5, this tool is designed for users who want deep filtering capabilities, customizable folder structures, efficient downloads, and intelligent automation, all within a modern and user-friendly graphical interface.

*This v5.0.0 release marks a significant feature milestone. Future updates are expected to be less frequent, focusing on maintenance and minor refinements.*
*Update v5.2.0 introduces multi-language support, theme selection, and further UI refinements.*

<p align="center">
  <a href="features.md">
    <img alt="Features" src="https://img.shields.io/badge/📚%20Full%20Feature%20List-FFD700?style=for-the-badge&logoColor=black&color=FFD700">
  </a>
  <a href="LICENSE">
    <img alt="License" src="https://img.shields.io/badge/📝%20License-90EE90?style=for-the-badge&logoColor=black&color=90EE90">
  </a>
  <a href="note.md">
    <img alt="Note" src="https://img.shields.io/badge/⚠️%20Important%20Note-FFCCCB?style=for-the-badge&logoColor=black&color=FFCCCB">
  </a>
</p>

---

## Feature Overview

Kemono Downloader offers a range of features to streamline your content downloading experience:

-   **User-Friendly Interface:** A modern PyQt5 GUI for easy navigation and operation.
-   **Flexible Downloading:**
    -   Download content from Kemono.su (and mirrors) and Coomer.party (and mirrors).
    -   Supports creator pages (with page range selection) and individual post URLs.
    -   Standard download controls: Start, Pause, Resume, and Cancel.
-   **Powerful Filtering:**
    -   **Character Filtering:** Filter content by character names. Supports simple comma-separated names and grouped names for shared folders.
    -   **Keyword Skipping:** Skip posts or files based on specified keywords.
    -   **Filename Cleaning:** Remove unwanted words or phrases from downloaded filenames.
    -   **File Type Selection:** Choose to download all files, or limit to images/GIFs, videos, audio, or archives. Can also extract external links only.
-   **Customizable Downloads:**
    -   **Thumbnails Only:** Option to download only small preview images.
    -   **Content Scanning:** Scan post HTML for `<img>` tags and direct image links, useful for images embedded in descriptions.
    -   **WebP Conversion:** Convert images to WebP format for smaller file sizes (requires Pillow library).
-   **Organized Output:**
    -   **Automatic Subfolders:** Create subfolders based on character names (from filters or `Known.txt`) or post titles.
    -   **Per-Post Subfolders:** Option to create an additional subfolder for each individual post.
-   **Manga/Comic Mode:**
    -   Downloads posts from a creator's feed in chronological order (oldest to newest).
    -   Offers various filename styling options for sequential reading (e.g., post title, original name, global numbering).
-   **⭐ Favorite Mode:**
    -   Directly download from your favorited artists and posts on Kemono.su.
    -   Requires a valid cookie and adapts the UI for easy selection from your favorites.
    -   Supports downloading into a single location or artist-specific subfolders. 
-   **Performance & Advanced Options:**
    -   **Cookie Support:** Use cookies (paste string or load from `cookies.txt`) to access restricted content.
    -   **Multithreading:** Configure the number of simultaneous downloads/post processing threads for improved speed.
-   **Logging:**
    -   A detailed progress log displays download activity, errors, and summaries.
-   **Multi-language Interface:** Choose from several languages for the UI (English, Japanese, French, Spanish, German, Russian, Korean, Chinese Simplified).
-   **Theme Customization:** Selectable Light and Dark themes for user comfort.

---

## ✨ What's New in v5.3.0
-   **Multi-Creator Post Fetching & Queuing:**
    -   The **Creator Selection popup** (🎨 icon) has been significantly enhanced.
    -   After selecting multiple creators, you can now click a new "**Fetch Posts**" button.
    -   This will retrieve and display posts from all selected creators in a new view within the popup.
    -   You can then browse these fetched posts (with search functionality) and select individual posts.
    -   A new "**Add Selected Posts to Queue**" button allows you to add your chosen posts directly to the main download queue, streamlining the process of gathering content from multiple artists.
    -   The traditional "**Add Selected to URL**" button is still available if you prefer to populate the main URL field with creator names.
-   **Improved Favorite Download Queue Handling:**
    -   When items are added to the download queue from the Creator Selection popup, the main URL input field will now display a placeholder message (e.g., "{count} items in queue from popup").
    -   The queue is now more robustly managed, especially when interacting with the main URL input field after items have been queued from the popup.

---

## ✨ What's New in v5.1.0
-   **Enhanced Error File Management**: The "Error" button now opens a dialog listing files that failed to download. This dialog includes:
    -   An option to **retry selected** failed downloads.
    -   A new **"Export URLs to .txt"** button, allowing users to save links of failed downloads either as "URL only" or "URL with details" (including post title, ID, and original filename).
    -   Fixed a bug where files skipped during retry (due to existing hash match) were not correctly removed from the error list.
-   **Improved UI Stability**: Addressed issues with UI state management to more accurately reflect ongoing download activities (including retries and external link downloads). This prevents the "Cancel" button from becoming inactive prematurely while operations are still running.

## ✨ What's New in v5.2.0
-   **Multi-language Support:** The interface now supports multiple languages: English, Japanese, French, Spanish, German, Russian, Korean, and Chinese (Simplified). Select your preferred language in the new Settings dialog.
-   **Theme Selection:** Choose between Light and Dark application themes via the Settings dialog for a personalized viewing experience.
-   **Centralized Settings:** A new Settings dialog (accessible via a settings button, often with a gear icon) provides a dedicated space for language and appearance customizations.
-   **Internal Localization:** Introduced `languages.py` for managing UI translations, streamlining the addition of new languages by contributors.

---

## Installation

### Requirements
-   Python 3.6 or higher
-   pip (Python package installer)

### Install Dependencies
Open your terminal or command prompt and run:

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
