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
