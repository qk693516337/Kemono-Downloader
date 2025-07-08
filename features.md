# Kemono Downloader - Feature Guide

This guide provides a comprehensive overview of all user interface elements, input fields, buttons, popups, and functionalities available in the Kemono Downloader.

---

## 1. Main Interface & Workflow
These are the primary controls you'll interact with to initiate and manage downloads.

### 1.1. Core Inputs

#### 🔗 Creator/Post URL Input Field
**Purpose:** This is where you paste the URL of the content you want to download.  
**Supported Sites:** Kemono.su, Coomer.party, Simpcity.su, and their mirrors.  
**Supported URL Types:**
* Creator pages (e.g., `https://kemono.su/patreon/user/12345`).
* Individual posts (e.g., `https://kemono.su/patreon/user/12345/post/98765`).  
**Note:** When ⭐ Favorite Mode is active, this field is disabled.

#### 🎨 Creator Selection Button
**Icon:** 🎨 (Artist Palette)  
**Purpose:** Opens the "Creator Selection" dialog to easily browse and queue downloads from a list of known creators.  
**Dialog Features:**
* Loads creators from the `creators.json` file.
* **Search Bar:** Filter the list of creators by name.
* **Creator List:** Displays creators with their service (e.g., Patreon, Fanbox).
* **Selection:** Checkboxes to select one or more creators.
* **Download Scope:** Choose to organize downloads by Characters or Creators.
* **Add to Queue:** Adds selected creators or their individual posts to the download queue.

#### Page Range (Start to End) Input Fields
**Purpose:** For creator URLs, you can specify a range of pages to fetch and process.  
**Usage:** Enter the starting page number in the first field and the ending page in the second.  
**Behavior:**
* If left blank, all pages for the creator are processed.
* Disabled for single post URLs.

#### 📁 Download Location Input Field & Browse Button
**Purpose:** Specify the main directory where all downloaded files and folders will be saved.  
**Usage:** Type the path directly or click "Browse..." to select a folder.  
**Requirement:** This field is mandatory for all download operations.

### 1.2. Action Buttons

#### ⬇️ Start Download / 🔗 Extract Links Button
**Purpose:** The primary button to begin the downloading or link extraction process.  
**Behavior:**
* If "🔗 Only Links" is selected, the button text changes to "🔗 Extract Links".
* Otherwise, it reads "⬇️ Start Download".

#### 🔄 Restore Download Button
**Visibility:** This button appears in place of the "Pause" button if an incomplete session is detected upon startup.  
**Purpose:** Allows you to resume a previously interrupted download session from where it left off.

#### ⏸️ Pause / ▶️ Resume Download Button
**Purpose:** Temporarily halt or continue the ongoing download.  
**Behavior:** Toggles between "Pause" and "Resume". Some UI settings can be changed while paused.

#### ❌ Cancel & Reset UI Button
**Purpose:** Immediately stops the current operation and performs a "soft" reset.  
**Behavior:** Halts all background threads and preserves the URL and Download Location inputs, resetting everything else.

#### 🔄 Reset Button (in the log area)
**Purpose:** Performs a "hard" reset of the UI when no operation is active.  
**Behavior:** Clears all input fields, resets all options to default, and clears logs.

---

## 2. Filtering & Content Selection
These options allow you to precisely control what content is downloaded.

### 2.1. Content Filtering

#### 🎯 Filter by Character(s) Input Field
**Purpose:** Download content related to specific characters or series.  
**Usage:** Enter character names, comma-separated.  
**Advanced Syntax:**
* `Nami`: Simple filter.
* `(Vivi, Ulti)`: Grouped filter. Matches posts with "Vivi" OR "Ulti". Creates a shared folder like "Vivi Ulti" if subfolders are enabled.
* `(Boa, Hancock)~`: Aliased filter. Treats "Boa" and "Hancock" as the same entity for matching and folder creation.

#### Filter: [Type] Button (Character Filter Scope)
**Purpose:** Defines where the character filter is applied. Cycles on click.  
**Options:**
* **Filter: Title (Default):** Matches against the post title.
* **Filter: Files:** Matches against individual filenames.
* **Filter: Both:** Checks the title first, then filenames.
* **Filter: Comments (Beta):** Checks filenames first, then post comments.

#### 🚫 Skip with Words Input Field
**Purpose:** Exclude posts or files containing specified keywords (e.g., WIP, sketch).

#### Scope: [Type] Button (Skip Words Scope)
**Purpose:** Defines where the skip words are applied. Cycles on click.  
**Options:**
* **Scope: Posts (Default):** Skips entire posts if the title contains a skip word.
* **Scope: Files:** Skips individual files if the filename contains a skip word.
* **Scope: Both:** Applies both rules.

#### ✂️ Remove Words from name Input Field
**Purpose:** Clean up filenames by removing unwanted text (e.g., patreon, [HD]).

### 2.2. File Type Filtering

#### Filter Files (Radio Buttons)
**Purpose:** Select the types of files to download.  
**Options:**
* **All:** Download all file types.
* **Images/GIFs:** Download only common image formats.
* **Videos:** Download only common video formats.
* **🎧 Only Audio:** Download only common audio formats.
* **📦 Only Archives:** Exclusively download `.zip` and `.rar` files.
* **🔗 Only Links:** Do not download any files. Instead, extracts and displays external links.

#### Skip .zip / Skip .rar Checkboxes
**Purpose:** Individually choose to skip downloading `.zip` or `.rar` files.  
**Behavior:** Disabled when "📦 Only Archives" is active.

---

## 3. Download Customization
Options to further refine the download process and output.

#### Download Thumbnails Only
Downloads only the small preview images instead of full-resolution files.

#### Scan Content for Images
Scans the HTML of posts for `<img>` tags. Crucial for sites where images are embedded in descriptions but not listed as attachments.

#### Compress to WebP
Converts large images to the space-saving WebP format (requires the Pillow library).

#### 🗄️ Custom Folder Name (Single Post Only)
When downloading a single post, this field appears (if subfolders are on) to let you specify a custom folder name for that post's content.

---

## 4. 📖 Manga/Comic Mode
A specialized mode for downloading creator feeds in chronological order, ideal for sequential content.

**Activation:** This mode is active when downloading a creator's entire feed (not a single post).  
**Core Behavior:** Fetches all posts from the creator and processes them from oldest to newest.

#### Filename Style Toggle Button (in the log area)
**Purpose:** Controls how files are named in Manga Mode. Cycles on click.  
**Options:**
* **Name: Post Title:** Names the first file after the post title; subsequent files in the same post keep their original names.
* **Name: Original File:** All files keep their original server-provided names. An optional prefix can be added.
* **Name: Title+G.Num:** (Global Numbering) All files across all posts get a prefix from their post's title, followed by a global sequential number (e.g., `Chapter 1_001.jpg`, `Chapter 2_003.jpg`).
* **Name: Date Based:** Files are named sequentially (e.g., `001.jpg`, `002.jpg`) based on post date. An optional prefix can be added.
* **Name: Post ID:** Files are named after the post's unique ID, ensuring no name clashes.

---

## 5. Folder Organization & Known.txt
Controls for how downloaded content is structured into folders.

#### Separate Folders by Name/Title Checkbox
The master switch for enabling automatic subfolder creation.

#### Subfolder per Post Checkbox
Creates an additional layer of subfolders, where each post's content goes into its own folder named after the post title.

#### Known.txt Management UI (Bottom Left)
**Purpose:** Manages a local list (`Known.txt`) of series, characters, or terms used for automatic folder creation.
* **List Display:** Shows the primary names from your `Known.txt` file.
* **➕ Add Button:** Adds a new name or group (e.g., `(Character A, Alias B)~`) to `Known.txt`.
* **⤵️ Add to Filter Button:** Opens a dialog to select names from `Known.txt` and add them to the character filter input.
* **🗑️ Delete Selected Button:** Removes selected names from the list and the file.
* **Open Known.txt Button:** Opens the file in your default text editor.
* **❓ Help Button:** Opens the application's feature guide.

---

## 6. ⭐ Favorite Mode (Kemono.su Only)
Download directly from your favorited artists and posts on Kemono.su.

#### Enable Checkbox ("⭐ Favorite Mode")
Switches the downloader to Favorite Mode.
* Disables the main URL input.
* Changes action buttons to "Favorite Artists" and "Favorite Posts".
* Requires cookies to be enabled.

#### 🖼️ Favorite Artists Button
Opens a dialog to select and download from your favorited artists.

#### 📄 Favorite Posts Button
Opens a dialog to select and download specific favorited posts.

#### Favorite Download Scope Button
* **Scope: Selected Location:** Downloads all selected favorites into the main download directory.
* **Scope: Artist Folders:** Creates a subfolder for each artist and downloads their content into it.

---

## 7. Advanced Settings & Performance

### 🍪 Cookie Management
**Use Cookie Checkbox:** Enables the use of browser cookies to access restricted content.  
**Cookie Text Field:** Paste your cookie string directly.  
**Browse... Button:** Select a `cookies.txt` file (Netscape format).

### Use Multithreading Checkbox & Threads Input
**Purpose:** Enable and configure the number of simultaneous operations.  
**Behavior:** For creator feeds, this sets the number of posts processed concurrently. For single posts, it sets the number of files downloaded concurrently.

### Multi-part Download Toggle Button
**Purpose:** Enables/disables multi-segment downloading for individual large files to improve speed.  
**Note:** Best for large files; can be less efficient for many small files.

---

## 8. Logging, Monitoring & Error Handling

#### 📜 Progress Log Area
The main text area displaying detailed messages, progress, and errors.

#### 👁️ / 🙈 Log View Toggle Button
Switches the main log view between the Progress Log and the Missed Character Log (which shows posts that were skipped by your character filters).

#### Show External Links in Log
When enabled, a secondary panel appears to display external links (Mega, Google Drive) found in post descriptions.

#### Export Links Button
Appears in "Only Links" mode to save all extracted links to a `.txt` file.

#### 🆘 Error Button & Dialog
**Purpose:** Becomes active if files failed to download.  
**Dialog Features:**
* Lists all failed files.
* Allows you to select and **Retry** failed downloads.
* Allows you to **Export** the list of failed URLs to a text file for manual handling.

---

## 9. Application Settings (⚙️)

#### Appearance
Switch between a Light and Dark theme for the application.

#### Language
Change the display language of the UI. A restart is required for changes to take full effect.
