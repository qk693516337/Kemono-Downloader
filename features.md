<div>
  <h1>Kemono Downloader - Comprehensive Feature Guide</h1>
  <p>This guide provides a detailed overview of all user interface elements, input fields, buttons, popups, and functionalities available in the application.</p>
  <hr>

  <h2><strong>1. URL Input (🔗)</strong></h2>
  <p>This is the primary input field where you specify the content you want to download.</p>

  <p><strong>Functionality:</strong></p>
  <ul>
    <li><strong>Creator URL:</strong> A link to a creator's main page (e.g., https://kemono.su/patreon/user/12345). Downloads all posts from the creator.</li>
    <li><strong>Post URL:</strong> A direct link to a specific post (e.g., .../post/98765). Downloads only the specified post.</li>
  </ul>

  <p><strong>Interaction with Other Features:</strong> The content of this field influences "Manga Mode" and "Page Range". "Page Range" is enabled only with a creator URL.</p>

  <hr>

  <h2><strong>2. Creator Selection & Update (🎨)</strong></h2>
  <p>The color palette emoji button opens the Creator Selection & Update dialog. This allows managing and downloading from a local creator database.</p>

  <p><strong>Functionality:</strong></p>
  <ul>
    <li><strong>Creator Browser:</strong> Loads a list from <code>creators.json</code>. Search by name, service, or paste a URL to find creators.</li>
    <li><strong>Batch Selection:</strong> Select multiple creators and click "Add Selected" to add them to the batch download session.</li>
    <li><strong>Update Checker:</strong> Use a saved profile (.json) to download only new content based on previously fetched posts.</li>
    <li><strong>Post Fetching & Filtering:</strong> "Fetch Posts" loads post titles, allowing you to choose specific posts for download.</li>
  </ul>

  <hr>

  <h2><strong>3. Download Location Input (📁)</strong></h2>
  <p>This input defines the destination directory for downloaded files.</p>

  <p><strong>Functionality:</strong></p>
  <ul>
    <li><strong>Manual Entry:</strong> Enter or paste the folder path.</li>
    <li><strong>Browse Button:</strong> Opens a system dialog to choose a folder.</li>
    <li><strong>Directory Creation:</strong> If the folder doesn't exist, the app can create it after user confirmation.</li>
  </ul>

  <hr>

  <h2><strong>4. Filter by Character(s) & Scope Button</strong></h2>
  <p>Used to download content for specific characters or series and organize them into subfolders.</p>

  <p><strong>Input Field (Filter by Character(s)):</strong></p>
  <ul>
    <li>Enter comma-separated names (e.g., <code>Tifa, Aerith</code>).</li>
    <li>Group aliases using parentheses (e.g., <code>(Cloud, Zack)</code>).</li>
    <li>Names are matched against titles, filenames, or comments.</li>
    <li>If "Separate Folders by Known.txt" is enabled, the name becomes the subfolder name.</li>
  </ul>

  <p><strong>Scope Button Modes:</strong></p>
  <ul>
    <li><strong>Filter: Title</strong> (default) – Match names in post titles only.</li>
    <li><strong>Filter: Files</strong> – Match names in filenames only.</li>
    <li><strong>Filter: Both</strong> – Try title match first, then filenames.</li>
    <li><strong>Filter: Comments</strong> – Try filenames first, then post comments if no match.</li>
  </ul>

  <hr>

  <h2><strong>5. Skip with Words & Scope Button</strong></h2>
  <p>Prevents downloading content based on keywords.</p>

  <p><strong>Input Field (Skip with Words):</strong></p>
  <ul>
    <li>Enter comma-separated keywords (e.g., <code>WIP, sketch, preview</code>).</li>
    <li>Matching is case-insensitive.</li>
    <li>If a keyword matches, the file or post is skipped.</li>
  </ul>

  <p><strong>Scope Button Modes:</strong></p>
  <ul>
    <li><strong>Scope: Posts</strong> (default) – Skips post if title contains a keyword.</li>
    <li><strong>Scope: Files</strong> – Skips individual files with keyword matches.</li>
    <li><strong>Scope: Both</strong> – Skips entire post if title matches, otherwise filters individual files.</li>
  </ul>
</div>
<div>
  <h2><strong>Filter File Section (Radio Buttons)</strong></h2>
  <p>This section uses a group of radio buttons to control the primary download mode, dictating which types of files are targeted. Only one of these modes can be active at a time.</p>

  <ul>
    <li>
      <strong>All:</strong> Default mode. Downloads every file and attachment provided by the API, regardless of type.
    </li>
    <li>
      <strong>Images/GIFs:</strong> Filters for common image formats (<code>.jpg</code>, <code>.png</code>, <code>.gif</code>, <code>.webp</code>), skipping non-image files.
    </li>
    <li>
      <strong>Videos:</strong> Filters for common video formats like <code>.mp4</code>, <code>.webm</code>, and <code>.mov</code>, skipping all others.
    </li>
    <li>
      <strong>Only Archives:</strong> Downloads only archive files (<code>.zip</code>, <code>.rar</code>). Disables "Compress to WebP" and unchecks "Skip Archives".
    </li>
    <li>
      <strong>Only Audio:</strong> Filters for common audio formats like <code>.mp3</code>, <code>.wav</code>, and <code>.flac</code>.
    </li>
    <li>
      <strong>Only Links:</strong> Extracts external hyperlinks from post descriptions (e.g., Mega, Google Drive) and displays them in the log. Disables all download options.
    </li>
    <li>
      <strong>More:</strong> Opens the "More Options" dialog to download text-based content instead of media files.
      <ul>
        <li><strong>Scope:</strong> Choose to extract from post description or comments.</li>
        <li><strong>Export Format:</strong> Save text as PDF, DOCX, or TXT.</li>
        <li><strong>Single PDF:</strong> Optionally compile all text into one PDF.</li>
      </ul>
    </li>
  </ul>

  <hr>

  <h2><strong>Check Box Buttons</strong></h2>
  <p>These checkboxes provide additional toggles to refine the download behavior and enable special features.</p>

  <ul>
    <li>
      <strong>⭐ Favorite Mode:</strong> Changes workflow to download from your personal favorites. Disables the URL input.
      <ul>
        <li><strong>Favorite Artists:</strong> Opens a dialog to select from your favorited creators.</li>
        <li><strong>Favorite Posts:</strong> Opens a dialog to select from your favorited posts on Kemono and Coomer.</li>
      </ul>
    </li>
    <li>
      <strong>Skip Archives:</strong> When checked, archive files (<code>.zip</code>, <code>.rar</code>) are ignored. Disabled in "Only Archives" mode.
    </li>
    <li>
      <strong>Download Thumbnail Only:</strong> Saves only thumbnail previews, not full-resolution files. Enables "Scan Content for Images".
    </li>
    <li>
      <strong>Scan Content for Images:</strong> Parses post HTML for embedded images not listed in the API. Looks for <code>&lt;img&gt;</code> tags and direct image links.
    </li>
    <li>
      <strong>Compress to WebP:</strong> Converts large images (over 1.5 MB) to WebP format using the Pillow library for space-saving.
    </li>
    <li>
      <strong>Keep Duplicates:</strong> Provides control over duplicate handling via the "Duplicate Handling Options" dialog.
      <ul>
        <li><strong>Skip by Hash:</strong> Default – skip identical files.</li>
        <li><strong>Keep Everything:</strong> Save all files regardless of duplication.</li>
        <li><strong>Limit:</strong> Set a limit on how many copies of the same file are saved. A limit of <code>0</code> means no limit.</li>
      </ul>
    </li>
  </ul>
</div>
<h2><strong>Folder Organization Checkboxes</strong></h2>
<ul>
  <li>
    <strong>Separate folders by Known.txt:</strong> Automatically organizes downloads into folders based on name matches.
    <ul>
      <li>Uses "Filter by Character(s)" input first, if available.</li>
      <li>Then checks names in <code>Known.txt</code>.</li>
      <li>Falls back to extracting from post title.</li>
    </ul>
  </li>
  <li>
    <strong>Subfolder per post:</strong> Creates a unique folder per post, using the post’s title.
    <ul>
      <li>Prevents mixing files from multiple posts.</li>
      <li>Can be combined with Known.txt-based folders.</li>
      <li>Ensures uniqueness (e.g., <code>My Post Title_1</code>).</li>
      <li>Automatically removes empty folders.</li>
    </ul>
  </li>
  <li>
    <strong>Date prefix:</strong> Enabled only with "Subfolder per post". Prepends the post date (e.g., <code>2025-08-03 My Post Title</code>) for chronological sorting.
  </li>
</ul>

<h2><strong>General Functionality Checkboxes</strong></h2>
<ul>
  <li>
    <strong>Use cookie:</strong> Enables login-based access via cookies.
    <ul>
      <li>Paste cookie string directly, or browse to select a <code>cookies.txt</code> file.</li>
      <li>Cookies are used in all authenticated API requests.</li>
    </ul>
  </li>
  <li>
    <strong>Use Multithreading:</strong> Enables parallel downloading of posts.
    <ul>
      <li>Specify the number of worker threads (e.g., 10).</li>
      <li>Disabled for Manga Mode and Only Links mode.</li>
    </ul>
  </li>
  <li>
    <strong>Show external links in log:</strong> Adds a secondary log that displays links (e.g., Mega, Dropbox) found in post text.
  </li>
  <li>
    <strong>Manga/Comic mode:</strong> Sorts posts chronologically before download.
    <ul>
      <li>Ensures correct page order for comics/manga.</li>
    </ul>
    <strong>Scope Button (Name: ...):</strong> Controls filename style:
    <ul>
      <li><strong>Name: Post Title</strong> — e.g., <code>Chapter-1.jpg</code></li>
      <li><strong>Name: Date + Original</strong> — e.g., <code>2025-08-03_filename.png</code></li>
      <li><strong>Name: Date + Title</strong> — e.g., <code>2025-08-03_Chapter-1.jpg</code></li>
      <li><strong>Name: Title+G.Num</strong> — e.g., <code>Page_001.jpg</code></li>
      <li><strong>Name: Date Based</strong> — e.g., <code>001.jpg</code>, with optional prefix</li>
      <li><strong>Name: Post ID</strong> — uses unique post ID as filename</li>
    </ul>
  </li>
</ul>
<h2><strong>Start Download</strong></h2>
<ul>
  <li>
    <strong>Default State ("⬇️ Start Download"):</strong> When idle, this button gathers all current settings (URL, filters, checkboxes, etc.) and begins the download process via the DownloadManager.
  </li>
  <li>
    <strong>Restore State:</strong> If an interrupted session is detected, the tooltip will indicate that starting a new download will discard previous session progress.
  </li>
  <li>
    <strong>Update Mode (Phase 1 - "🔄 Check For Updates"):</strong> If a creator profile is loaded, clicking this button will fetch the creator's posts and compare them against your saved profile to identify new content.
  </li>
  <li>
    <strong>Update Mode (Phase 2 - "⬇️ Start Download (X new)"):</strong> After new posts are found, the button text updates to reflect the number. Clicking it downloads only the new content.
  </li>
</ul>

<h2><strong>Pause / Resume Download</strong></h2>
<ul>
  <li>
    <strong>While Downloading:</strong> The button toggles between:
    <ul>
      <li><strong>"⏸️ Pause Download":</strong> Sets a <code>pause_event</code>, which tells all worker threads to halt their current task and wait.</li>
      <li><strong>"▶️ Resume Download":</strong> Clears the <code>pause_event</code>, allowing threads to resume their work.</li>
    </ul>
  </li>
  <li>
    <strong>While Idle:</strong> The button is disabled.
  </li>
  <li>
    <strong>Restore State:</strong> Changes to "🔄 Restore Download", which resumes the last session from saved data.
  </li>
</ul>

<h2><strong>Cancel & Reset UI</strong></h2>
<ul>
  <li>
    <strong>Functionality:</strong> Stops downloads gracefully using a <code>cancellation_event</code>. Threads finish current tasks before shutting down.
  </li>
  <li>
    <strong>The Soft Reset:</strong> After cancellation is confirmed by background threads, the UI resets via the <code>download_finished</code> function. Input fields (URL and Download Location) are preserved for convenience.
  </li>
  <li>
    <strong>Restore State:</strong> Changes to "🗑️ Discard Session", which deletes <code>session.json</code> and resets the UI.
  </li>
  <li>
    <strong>Update State:</strong> Changes to "🗑️ Clear Selection", unloading the selected creator profile and returning to normal UI state.
  </li>
</ul>

<h2><strong>Error Button</strong></h2>
<ul>
  <li>
    <strong>Error Counter:</strong> Shows how many files failed to download (e.g., <code>(3) Error</code>). Disabled if there are no errors.
  </li>
  <li>
    <strong>Error Dialog:</strong> Clicking opens the "Files Skipped Due to Errors" dialog (defined in <code>ErrorFilesDialog.py</code>), listing all failed files.
  </li>
  <li>
    <strong>Dialog Features:</strong>
    <ul>
      <li><strong>View Failed Files:</strong> Shows filenames and related post info.</li>
      <li><strong>Select and Retry:</strong> Retry selected failed files in a focused download session.</li>
      <li><strong>Export URLs:</strong> Save a <code>.txt</code> file of direct download links. Optionally include post metadata with each URL.</li>
    </ul>
  </li>
</ul>
<h2><strong>"Known Area" and its Controls</strong></h2>
<p>This section, located on the right side of the main window, manages your personal name database (<code>Known.txt</code>), which the app uses to organize downloads into subfolders.</p>

<ul>
  <li>
    <strong>Open Known.txt:</strong> Opens the <code>Known.txt</code> file in your system's default text editor for manual editing, such as bulk changes or cleanup.
  </li>
  <li>
    <strong>Search character input:</strong> A live search filter that hides any list items not matching your input text. Useful for quickly locating specific names in large lists.
  </li>
  <li>
    <strong>Known Series/Characters Area:</strong> Displays all names currently stored in your <code>Known.txt</code>. These names are used when "Separate folders by Known.txt" is enabled.
  </li>
  <li>
    <strong>Input at bottom & Add button:</strong> Type a new character or series name into the input field, then click "➕ Add". The app checks for duplicates, updates the list, and saves to <code>Known.txt</code>.
  </li>
  <li>
    <strong>Add to Filter:</strong> Opens a dialog showing all entries from <code>Known.txt</code> with checkboxes. You can select one or more to auto-fill the "Filter by Character(s)" field at the top of the app.
  </li>
  <li>
    <strong>Delete Selected:</strong> Select one or more entries from the list and click "🗑️ Delete Selected" to remove them from the app and update <code>Known.txt</code> accordingly.
  </li>
</ul>

<h2><strong>Other Buttons</strong></h2>
<ul>
  <li>
    <strong>(?_?) mark button (Help Guide):</strong> Opens a multi-page help dialog with step-by-step instructions and explanations for all app features. Useful for new users.
  </li>
  <li>
    <strong>History Button:</strong> Opens the Download History dialog (from <code>DownloadHistoryDialog.py</code>), showing:
    <ul>
      <li>Recently downloaded files</li>
      <li>The first few posts processed in the last session</li>
    </ul>
    This allows for a quick review of recent activity.
  </li>
  <li>
    <strong>Settings Button:</strong> Opens the Settings dialog (from <code>FutureSettingsDialog.py</code>), where you can change app-wide settings such as theme (light/dark) and language.
  </li>
  <li>
    <strong>Support Button:</strong> Opens the Support dialog (from <code>SupportDialog.py</code>), which includes developer info, source links, and donation platforms like Ko-fi or Patreon.
  </li>
</ul>
<h2><strong>Log Area Controls</strong></h2>
<p>These controls are located around the main log panel and offer tools for managing downloads, configuring advanced options, and resetting the application.</p>

<ul>
  <li>
    <strong>Multi-part: OFF</strong><br>
    This button acts as both a status indicator and a configuration panel for multi-part downloading (parallel downloading of large files).
    <ul>
      <li><strong>Function:</strong> Opens the <code>Multipart Download Options</code> dialog (defined in <code>MultipartScopeDialog.py</code>).</li>
      <li><strong>Scope Options:</strong> Choose between "Videos Only", "Archives Only", or "Both".</li>
      <li><strong>Number of parts:</strong> Set how many simultaneous connections to use (2–16).</li>
      <li><strong>Minimum file size:</strong> Set a threshold (MB) below which files are downloaded normally.</li>
      <li><strong>Status:</strong> After applying settings, the button's text updates (e.g., <code>Multi-part: Both</code>); otherwise, it resets to <code>Multi-part: OFF</code>.</li>
    </ul>
  </li>

  <li>
    <strong>👁️ Eye Emoji Button (Log View Toggle)</strong><br>
    Switches between two views in the log panel:
    <ul>
      <li><strong>👁️ Progress Log View:</strong> Shows real-time download progress, status messages, and errors.</li>
      <li><strong>🚫 Missed Character View:</strong> Displays names detected in posts that didn’t match the current filter — useful for updating <code>Known.txt</code>.</li>
    </ul>
  </li>

  <li>
    <strong>Reset Button</strong><br>
    Performs a full "soft reset" of the UI when the application is idle.
    <ul>
      <li>Clears all inputs (except saved Download Location)</li>
      <li>Resets checkboxes, buttons, and logs</li>
      <li>Clears counters, queues, and restores the UI to its default state</li>
      <li><strong>Note:</strong> This is different from <em>Cancel & Reset UI</em>, which halts active downloads</li>
    </ul>
  </li>
</ul>

<h3><strong>The Progress Log and "Only Links" Mode Controls</strong></h3>

<ul>
  <li>
    <strong>Standard Mode (Progress Log)</strong><br>
    This is the default behavior. The <code>main_log_output</code> field displays:
    <ul>
      <li>Post processing steps</li>
      <li>Download/skipped file notifications</li>
      <li>Error messages</li>
      <li>Session summaries</li>
    </ul>
  </li>

  <li>
    <strong>"Only Links" Mode</strong><br>
    When enabled, the log panel switches modes and reveals new controls.
    <ul>
      <li><strong>📜 Extracted Links Log:</strong> Replaces progress info with a list of found external links (e.g., Mega, Dropbox).</li>
      <li><strong>Export Links Button:</strong> Saves the extracted links to a <code>.txt</code> file.</li>
      <li><strong>Download Button:</strong> Opens the <code>Download Selected External Links</code> dialog (from <code>DownloadExtractedLinksDialog.py</code>), where you can:
        <ul>
          <li>View all supported external links</li>
          <li>Select which ones to download</li>
          <li>Begin download directly from cloud services</li>
        </ul>
      </li>
      <li><strong>Links View Button:</strong> Toggles log display between:
        <ul>
          <li><strong>🔗 Links View:</strong> Shows all extracted links</li>
          <li><strong>⬇️ Progress View:</strong> Shows download progress from external services (e.g., Mega)</li>
        </ul>
      </li>
    </ul>
  </li>
</ul>
