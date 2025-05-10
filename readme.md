# Kemono Downloader v3.1.0

A feature-rich GUI application built with PyQt5 to download content from [Kemono.su](https://kemono.su) or [Coomer.party](https://coomer.party). Offers robust filtering, smart organization, manga-specific handling, and performance tuning. Now with session resuming, better retry logic, and smarter file management.

---

## 🚀 What's New in v3.1.0

* **Session Resuming**  
  * Automatically saves and resumes incomplete downloads.  

* **Retry on Failure**  
  * Failed files auto-retry up to 3 times.  
  * Clear logging for each retry attempt.

* **Improved Manga Mode**  
  * Better post ordering and handling of missing or untitled posts.  
  * Optional numeric-only sorting for consistent naming.

* **UI Enhancements**  
  * Settings persist across sessions.  
  * Improved layout spacing, tooltips, and status indicators.

* **Stability & Speed**  
  * Faster post fetching with lower memory usage.  
  * Minor bug fixes (duplicate folders, empty post crashes).

---

## 🧩 Core Features

* **Simple GUI**  
  Built with PyQt5 for a clean, responsive experience.

* **Supports Both Post and Creator URLs**  
  Download a single post or an entire feed with one click.

* **Smart Folder System**  
  Organize files using post titles, known character/show names, or a folder per post.  
  Detects and auto-names folders based on custom keywords.

* **Known Names Manager**  
  Add, search, and delete tags for smarter organization.  
  Saved to `Known.txt` for reuse.

* **Advanced Filters**  
  * Skip posts or files with specific keywords (e.g. `WIP`, `sketch`).  
  * Filter by media type: images, videos, or GIFs.  
  * Skip `.zip` and `.rar` archives.  

* **Manga Mode**  
  Rename and sort manga posts by title and upload order.  
  Handles one-image-per-post formats cleanly.

* **Image Compression**  
  Auto-convert large images (>1.5MB) to WebP (requires Pillow).

* **Multithreaded Downloads**  
  Adjustable worker count with warnings at unsafe levels.  
  Full threading for creators, single-thread fallback for post mode.

* **Download Controls**  
  Cancel files mid-download.  
  Visual progress tracking with per-post summaries.

* **Dark Mode**  
  Clean and modern dark-themed interface.

---

## 🔧 Backend Enhancements

* **Retry Logic**  
  Auto-retries individual failed files before skipping.  
  Logs all failures with HTTP codes and reasons.

* **Hash-Based Deduplication**  
  Prevents redownloading of previously saved files.

* **Smart Naming**  
  Cleans and standardizes inconsistent post titles.  
  Adds page indices for manga.

* **Efficient Logging**  
  Toggle between basic and advanced views.  
  Live feedback with color-coded logs.

---

## 📦 Installation

### Requirements

* Python 3.6+
* Pip packages:

```bash
pip install PyQt5 requests Pillow

```

This How it work
📥 START DOWNLOAD
│
├── 🔍 Check Filter Settings
│   ├── Character Filter (if any)
│   └── Skip Words (posts/files)
│
├── 📂 Determine Folder Structure
│   ├── Is "Separate Folders by Name/Title" Enabled?
│   │   ├── YES:
│   │   │   ├── Check Known Character List
│   │   │   │   ├── If match in post title → use as folder name
│   │   │   │   └── If no match → use post title (cleaned)
│   │   │   └── Also check for fallback to creator name or "Misc"
│   │   └── NO:
│   │       └── Save all files to selected root folder
│   │
│   └── Is "Subfolder per Post" Enabled?
│       └── YES: Append post ID or cleaned post title under base folder
│
├── 📑 File Filtering & Pre-Checks
│   ├── Skip ZIP / RAR
│   ├── File type check: Image / Video / Link
│   └── Check for duplicates (hash or name)
│
├── 📘 Manga Mode Enabled?
│   ├── YES:
│   │   ├── Is Rename-to-Post-Title Toggle ON?
│   │   │   ├── YES:
│   │   │   │   ├── One image per post → Rename to: `<PostTitle>_001.jpg`
│   │   │   │   ├── Multi-image post → Attempt sort by number or keep original
│   │   │   │   └── Add log entry for files that kept original name
│   │   │   └── NO:
│   │   │       └── Keep all original filenames
│   │   └── Sequence posts by upload date (oldest = page 1)
│   │
│   └── NO:
│       └── Use default or filtered file name, skip renaming logic
│
├── ⏬ Download File(s)
│   ├── Apply multithreading (if enabled)
│   └── Retry logic for network failures
│
└── 📜 Log & Post Processing Summary
    ├── Save summary per post (Downloaded/Skipped)
    └── If Manga Mode: show renaming log for clarity