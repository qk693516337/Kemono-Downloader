<h1 align="center">Kemono Downloader </h1>

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

<h2><strong>Core Capabilities Overview</strong></h2>

<h3><strong>High-Performance Downloading</strong></h3>
<ul>
  <li><strong>Multi-threading:</strong> Processes multiple posts simultaneously to greatly accelerate downloads from large creator profiles.</li>
  <li><strong>Multi-part Downloading:</strong> Splits large files into chunks and downloads them in parallel to maximize speed.</li>
  <li><strong>Resilience:</strong> Supports pausing, resuming, and restoring downloads after crashes or interruptions.</li>
</ul>

<h3><strong>Advanced Filtering & Content Control</strong></h3>
<ul>
  <li><strong>Content Type Filtering:</strong> Select whether to download all files or limit to images, videos, audio, or archives only.</li>
  <li><strong>Keyword Skipping:</strong> Automatically skips posts or files containing certain keywords (e.g., "WIP", "sketch").</li>
  <li><strong>Character Filtering:</strong> Restricts downloads to posts that match specific character or series names.</li>
</ul>

<h3><strong>File Organization & Renaming</strong></h3>
<ul>
  <li><strong>Automated Subfolders:</strong> Automatically organizes downloaded files into subdirectories based on character names or per post.</li>
  <li><strong>Advanced File Renaming:</strong> Flexible renaming options, especially in Manga Mode, including:
    <ul>
      <li><strong>Post Title:</strong> Uses the post's title (e.g., <code>Chapter-One.jpg</code>).</li>
      <li><strong>Date + Original Name:</strong> Prepends the publication date to the original filename.</li>
      <li><strong>Date + Title:</strong> Combines the date with the post title.</li>
      <li><strong>Sequential Numbering (Date Based):</strong> Simple sequence numbers (e.g., <code>001.jpg</code>, <code>002.jpg</code>).</li>
      <li><strong>Title + Global Numbering:</strong> Uses post title with a globally incrementing number across the session.</li>
      <li><strong>Post ID:</strong> Names files using the post’s unique ID.</li>
    </ul>
  </li>
</ul>

<h3><strong>Specialized Modes</strong></h3>
<ul>
  <li><strong>Manga/Comic Mode:</strong> Sorts posts chronologically before downloading to ensure pages appear in the correct sequence.</li>
  <li><strong>Favorite Mode:</strong> Connects to your account and downloads from your favorites list (artists or posts).</li>
  <li><strong>Link Extraction Mode:</strong> Extracts external links from posts for export or targeted downloading.</li>
  <li><strong>Text Extraction Mode:</strong> Saves post descriptions or comment sections as <code>PDF</code>, <code>DOCX</code>, or <code>TXT</code> files.</li>
</ul>

<h3><strong>Utility & Advanced Features</strong></h3>
<ul>
  <li><strong>Cookie Support:</strong> Enables access to subscriber-only content via browser session cookies.</li>
  <li><strong>Duplicate Detection:</strong> Prevents saving duplicate files using content-based comparison, with configurable limits.</li>
  <li><strong>Image Compression:</strong> Automatically converts large images to <code>.webp</code> to reduce disk usage.</li>
  <li><strong>Creator Management:</strong> Built-in creator browser and update checker for downloading only new posts from saved profiles.</li>
  <li><strong>Error Handling:</strong> Tracks failed downloads and provides a retry dialog with options to export or redownload missing files.</li>
</ul>

## 💻 Installation

### Requirements

- Python 3.6 or higher
- pip (Python package installer)

### Install Dependencies

```bash
pip install PyQt5 requests Pillow mega.py fpdf python-docx
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

This project is under the MIT Licence

## Star History

<table align="center" style="border-collapse: collapse; border: none; margin-left: auto; margin-right: auto;">
  <tr>
    <td align="center" valign="middle" style="padding: 10px; border: none;">
      <a href="https://www.star-history.com/#Yuvi9587/Kemono-Downloader&Date">
        <img src="https://api.star-history.com/svg?repos=Yuvi9587/Kemono-Downloader&type=Date" alt="Star History Chart" width="650">
      </a>
</table>

<p align="center">
  <a href="https://buymeacoffee.com/yuvi9587">
    <img src="https://img.shields.io/badge/🍺%20Buy%20Me%20a%20Coffee-FFCCCB?style=for-the-badge&logoColor=black&color=FFDD00" alt="Buy Me a Coffee">
  </a>
</p>

