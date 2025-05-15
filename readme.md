# Kemono Downloader v3.2.0

A feature-rich GUI application built with PyQt5 to download content from **Kemono.su** or **Coomer.party**.  
Offers robust filtering, smart organization, manga-specific handling, and performance tuning.  

This version introduces:
- Multi-part downloads  
- Character filtering by comments  
- Filename word removal  
- Various UI/workflow enhancements

---

## 🚀 What's New in v3.2.0

### 🔹 Character Filter by Post Comments (Beta)

- New "Comments" scope for the 'Filter by Character(s)' feature.

**How it works:**
1. Checks if any **filenames** match your character filter. If yes → downloads the post (skips comment check).
2. If no filename matches → scans the **post's comments**. If matched → downloads the post.

- Prioritizes filename-matched character name for folder naming, otherwise uses comment match.
- Cycle through filter scopes with the `Filter: [Scope]` button next to the character input.

---

### ✂️ Remove Specific Words from Filenames

- Input field: `"✂️ Remove Words from name"`
- Enter comma-separated words (e.g., `patreon, kemono, [HD], _final`)
- These are removed from filenames (case-insensitive) to improve organization.

---

### 🧩 Multi-part Downloads for Large Files

- Toggle multi-part downloads (OFF by default).
- Improves speed on large files (e.g., >10MB videos, zips).
- Falls back to single-stream on failure.
- Toggle via `Multi-part: ON/OFF` in the log header.

---

### 🧠 UI and Workflow Enhancements

- **Updated Welcome Tour**  
  Shows on first launch, covers all new and core features.

- **Smarter Cancel/Reset**  
  Cancels active tasks and resets UI — but retains URL and Download Directory fields.

- **Simplified Interface**  
  - Removed "Skip Current File" and local API server for a cleaner experience.

---

### 📁 Refined File & Duplicate Handling

- **Duplicate Filenames**  
  Adds numeric suffix (`file.jpg`, `file_1.jpg`, etc.).  
  Removed the "Duplicate" subfolder system.

- **Efficient Hash Check**  
  Detects and skips duplicate files within the same session (before writing to disk).

- **Better Temp File Cleanup**  
  Cleans up `.part` files — especially if duplicate or compressed post-download.

---

## 🧩 Core Features

### 🎛 Simple GUI
- Built with **PyQt5**  
- Dark theme, responsive layout

### 📥 Supports Post and Creator URLs
- Download a single post or an entire creator’s feed.

### 🔢 Page Range Support
- Choose page range when downloading creator feeds (except in Manga Mode).

---

### 🗂 Smart Folder System

- Organize by character names, post titles, or custom labels.
- Option to create a separate folder for each post.
- Uses `Known.txt` for fallback names.

---

### 📚 Known Names Manager

- Add/edit/delete known characters/shows
- Saves entries in `Known.txt` for automatic folder naming.

---

### 🔍 Advanced Filtering

- **Filter by Character(s)**  
  Scope: `Files`, `Post Titles`, `Both`, or `Post Comments (Beta)`

- **Skip with Words**  
  Skip posts or files based on keywords. Toggle scope.

- **Media Type Filters**  
  Choose: `All`, `Images/GIFs`, `Videos`, `📦 Only Archives (.zip/.rar)`

- **🔗 Only Links Mode**  
  Extracts links from post descriptions.

- **Skip Archives**  
  Ignore `.zip`/`.rar` unless in "Only Archives" mode.

---

### 📖 Manga/Comic Mode (Creator URLs Only)

- Downloads posts oldest-to-newest.

**Filename Style Toggle:**
- `Post Title` (default): Names first file in post after title.
- `Original File`: Uses original file names.

- Uses manga/series title for filtering and folder naming.

---

### 🖼️ Image Compression

- Converts large images to **WebP** if it significantly reduces size.
- Requires `Pillow` library.

---

### 🖼 Download Thumbnails Only

- Option to fetch only small preview images.

---

### ⚙️ Multithreaded Downloads

- Adjustable threads for:
  - Multiple post processing (creator feeds)
  - File-level concurrency (within a post)

---

### ⏯ Download Controls

- Start and cancel active operations.

---

### 🌙 Dark Mode Interface

- Modern, dark-themed GUI for comfort and clarity.

---

## 🔧 Backend Enhancements

### ♻️ Retry Logic

- Retries failed file and chunk downloads before skipping.

---

### 🧬 Session-wide Deduplication

- Uses **MD5 hashes** to avoid saving identical files during a session.

---

### 🧹 Smart Naming & Cleanup

- Cleans special characters in names.
- Applies numeric suffixes on collision.
- Removes specified unwanted words.

---

### 📋 Efficient Logging

- Toggle verbosity: `Basic` (important) or `Full` (everything).
- Separate panel for extracted external links.
- Real-time feedback with clear statuses.

---

## 📦 Installation

### Requirements
- Python 3.6+
- Pip (Python package manager)

### Install Libraries
```bash
pip install PyQt5 requests Pillow
