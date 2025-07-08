# Kemono Downloader - Feature Guide
This guide provides a comprehensive overview of all user interface elements, input fields, buttons, popups, and functionalities available in the Kemono Downloader.

## 1. Main Interface & Workflow
These are the primary controls you'll interact with to initiate and manage downloads.

### 1.1. Core Inputs
**🔗 Creator/Post URL Input Field**  
- **Purpose**: Paste the URL of the content you want to download.  
- **Supported Sites**: Kemono.su, Coomer.party, Simpcity.su.  
- **Supported URL Types**:  
  - Creator pages (e.g., `https://kemono.su/patreon/user/12345`).  
  - Individual posts (e.g., `https://kemono.su/patreon/user/12345/post/98765`).  
- **Note**: When ⭐ Favorite Mode is active, this field is disabled. For Simpcity.su URLs, the "Use Cookie" option is mandatory and auto-enabled.

**🎨 Creator Selection Button**  
- **Icon**: 🎨 (Artist Palette)  
- **Purpose**: Opens the "Creator Selection" dialog to browse and queue downloads from known creators.  
- **Dialog Features**:  
  - Loads creators from `creators.json`.  
  - **Search Bar**: Filter creators by name.  
  - **Creator List**: Displays creators with their service (e.g., Patreon, Fanbox).  
  - **Selection**: Checkboxes to select one or more creators.  
  - **Download Scope**: Organize downloads by Characters or Creators.  
  - **Add to Queue**: Adds selected creators or their posts to the download queue.

**Page Range (Start to End) Input Fields**  
- **Purpose**: Specify a range of pages to fetch for creator URLs.  
- **Usage**: Enter the starting and ending page numbers.  
- **Behavior**:  
  - If blank, all pages are processed.  
  - Disabled for single post URLs.

**📁 Download Location Input Field & Browse Button**  
- **Purpose**: Specify the main directory for downloaded files.  
- **Usage**: Type the path or click "Browse..." to select a folder.  
- **Requirement**: Mandatory for all download operations.

### 1.2. Action Buttons
**⬇️ Start Download / 🔗 Extract Links Button**  
- **Purpose**: Initiates downloading or link extraction.  
- **Behavior**:  
  - Shows "🔗 Extract Links" if "Only Links" is selected.  
  - Otherwise, shows "⬇️ Start Download".  
  - Supports single-threaded or multi-threaded downloads based on settings.

**🔄 Restore Download Button**  
- **Visibility**: Appears if an incomplete session is detected on startup.  
- **Purpose**: Resumes a previously interrupted download session.

**⏸️ Pause / ▶️ Resume Download Button**  
- **Purpose**: Pause or resume the ongoing download.  
- **Behavior**: Toggles between "Pause" and "Resume". Some UI settings can be changed while paused.

**❌ Cancel & Reset UI Button**  
- **Purpose**: Stops the current operation and performs a "soft" reset.  
- **Behavior**: Halts background threads, preserves URL and Download Location inputs, resets other settings.

**🔄 Reset Button (in the log area)**  
- **Purpose**: Performs a "hard" reset when no operation is active.  
- **Behavior**: Clears all inputs, resets options to default, and clears logs.

## 2. Filtering & Content Selection
These options allow precise control over downloaded content.

### 2.1. Content Filtering
**🎯 Filter by Character(s) Input Field**  
- **Purpose**: Download content related to specific characters or series.  
- **Usage**: Enter comma-separated character names.  
- **Advanced Syntax**:  
  - `Nami`: Simple filter.  
  - `(Vivi, Ulti)`: Grouped filter. Matches posts with "Vivi" OR "Ulti". Creates a shared folder like `Vivi Ulti` if subfolders are enabled.  
  - `(Boa, Hancock)~`: Aliased filter. Treats "Boa" and "Hancock" as the same entity.

**Filter: [Type] Button (Character Filter Scope)**  
- **Purpose**: Defines where the character filter is applied. Cycles on click.  
- **Options**:  
  - **Filter: Title** (Default): Matches post titles.  
  - **Filter: Files**: Matches filenames.  
  - **Filter: Both**: Checks title first, then filenames.  
  - **Filter: Comments (Beta)**: Checks filenames, then post comments.

**🚫 Skip with Words Input Field**  
- **Purpose**: Exclude posts/files with specified keywords (e.g., `WIP`, `sketch`).

**Scope: [Type] Button (Skip Words Scope)**  
- **Purpose**: Defines where skip words are applied. Cycles on click.  
- **Options**:  
  - **Scope: Posts** (Default): Skips posts if the title contains a skip word.  
  - **Scope: Files**: Skips files if the filename contains a skip word.  
  - **Scope: Both**: Applies both rules.

**✂️ Remove Words from Name Input Field**  
- **Purpose**: Remove unwanted text from filenames (e.g., `patreon`, `[HD]`).

### 2.2. File Type Filtering
**Filter Files (Radio Buttons)**  
- **Purpose**: Select file types to download.  
- **Options**:  
  - **All**: All file types.  
  - **Images/GIFs**: Common image formats.  
  - **Videos**: Common video formats.  
  - **🎧 Only Audio**: Common audio formats.  
  - **📦 Only Archives**: Only `.zip` and `.rar` files.  
  - **🔗 Only Links**: Extracts external links without downloading files.

**Skip .zip / Skip .rar Checkboxes**  
- **Purpose**: Skip downloading `.zip` or `.rar` files.  
- **Behavior**: Disabled when "📦 Only Archives" is active.

## 3. Download Customization
Options to refine the download process and output.

- **Download Thumbnails Only**: Downloads small preview images instead of full-resolution files.  
- **Scan Content for Images**: Scans post HTML for `<img>` tags, crucial for images in descriptions.  
- **Compress to WebP**: Converts images to WebP format (requires Pillow library).  
- **🗄️ Custom Folder Name (Single Post Only)**: Specify a custom folder name for a single post's content (appears if subfolders are enabled).

## 4. 📖 Manga/Comic Mode
A mode for downloading creator feeds in chronological order, ideal for sequential content.

- **Activation**: Active when downloading a creator's entire feed (not a single post).  
- **Core Behavior**: Fetches all posts, processing from oldest to newest.  
- **Filename Style Toggle Button (in the log area)**:  
  - **Purpose**: Controls file naming in Manga Mode. Cycles on click.  
  - **Options**:  
    - **Name: Post Title**: First file named after post title; others keep original names.  
    - **Name: Original File**: Files keep server-provided names, with optional prefix.  
    - **Name: Title+G.Num**: Global numbering with post title prefix (e.g., `Chapter 1_001.jpg`).  
    - **Name: Date Based**: Sequential naming by post date (e.g., `001.jpg`), with optional prefix.  
    - **Name: Post ID**: Files named after post ID to avoid clashes.  
    - **Name: Date + Title**: Combines post date and title for filenames.

## 5. Folder Organization & Known.txt
Controls for structuring downloaded content.

- **Separate Folders by Name/Title Checkbox**: Enables automatic subfolder creation.  
- **Subfolder per Post Checkbox**: Creates subfolders for each post, named after the post title.  
- **Known.txt Management UI (Bottom Left)**:  
  - **Purpose**: Manages a local `Known.txt` file for series, characters, or terms used in folder creation.  
  - **List Display**: Shows primary names from `Known.txt`.  
  - **➕ Add Button**: Adds names or groups (e.g., `(Character A, Alias B)~`).  
  - **⤵️ Add to Filter Button**: Select names from `Known.txt` for the character filter.  
  - **🗑️ Delete Selected Button**: Removes selected names from `Known.txt`.  
  - **Open Known.txt Button**: Opens the file in the default text editor.  
  - **❓ Help Button**: Opens this feature guide.  
  - **📜 History Button**: Views recent download history.

## 6. ⭐ Favorite Mode (Kemono.su Only)
Download from favorited artists/posts on Kemono.su.

- **Enable Checkbox ("⭐ Favorite Mode")**:  
  - Switches to Favorite Mode.  
  - Disables the main URL input.  
  - Changes action buttons to "Favorite Artists" and "Favorite Posts".  
  - Requires cookies.  
- **🖼️ Favorite Artists Button**: Select and download from favorited artists.  
- **📄 Favorite Posts Button**: Select and download specific favorited posts.  
- **Favorite Download Scope Button**:  
  - **Scope: Selected Location**: Downloads favorites to the main directory.  
  - **Scope: Artist Folders**: Creates subfolders per artist.

## 7. Advanced Settings & Performance
- **🍪 Cookie Management**:  
  - **Use Cookie Checkbox**: Enables cookies for restricted content.  
  - **Cookie Text Field**: Paste cookie string.  
  - **Browse... Button**: Select a `cookies.txt` file (Netscape format).  
- **Use Multithreading Checkbox & Threads Input**:  
  - **Purpose**: Configures simultaneous operations.  
  - **Behavior**: Sets concurrent post processing (creator feeds) or file downloads (single posts).  
- **Multi-part Download Toggle Button**:  
  - **Purpose**: Enables/disables multi-segment downloading for large files.  
  - **Note**: Best for large files; less efficient for small files.

## 8. Logging, Monitoring & Error Handling
- **📜 Progress Log Area**: Displays messages, progress, and errors.  
- **👁️ / 🙈 Log View Toggle Button**: Switches between Progress Log and Missed Character Log (skipped posts).  
- **Show External Links in Log**: Displays external links (e.g., Mega, Google Drive) in a secondary panel.  
- **Export Links Button**: Saves extracted links to a `.txt` file in "Only Links" mode.  
- **Download Extracted Links Button**: Downloads files from supported external links in "Only Links" mode.  
- **🆘 Error Button & Dialog**:  
  - **Purpose**: Active if files fail to download.  
  - **Dialog Features**:  
    - Lists failed files.  
    - Retry failed downloads.  
    - Export failed URLs to a text file.

## 9. Application Settings (⚙️)
- **Appearance**: Switch between Light and Dark themes.  
- **Language**: Change UI language (restart required).
