<div>
    <h1>Kemono Downloader - Comprehensive Feature Guide</h1>
    <p>This guide provides a detailed overview of all user interface elements, input fields, buttons, popups, and functionalities available in the application.</p>
    <hr>
    <h2><strong>Main Window: Core Functionality</strong></h2>
    <p>The application is divided into a configuration panel on the left and a status/log panel on the right.</p>
    <h3><strong>Primary Inputs (Top-Left)</strong></h3>
    <ul>
        <li><strong>URL Input Field</strong>: This is the starting point for most downloads. You can paste a URL for a specific post or for an entire creator's feed. The application's behavior adapts based on the URL type.</li>
        <li><strong>🎨 Creator Selection Popup</strong>: This button opens a powerful dialog listing all known creators. From here, you can:
            <ul>
                <li><strong>Search and Queue</strong>: Search for creators and check multiple names. Clicking "Add Selected" populates the main input field, preparing a batch download.</li>
                <li><strong>Check for Updates</strong>: Select a single creator's saved profile. This loads their information and switches the main download button to "Check for Updates" mode, allowing you to download only new content since your last session.</li>
            </ul>
        </li>
        <li><strong>Download Location</strong>: The primary folder where all content will be saved. The <strong>Browse...</strong> button lets you select this folder from your computer.</li>
        <li><strong>Page Range (Start/End)</strong>: These fields activate only for creator feed URLs. They allow you to download a specific slice of a creator's history (e.g., pages 5 through 10) instead of their entire feed.</li>
    </ul>
    <hr>
    <h2><strong>Filtering & Naming (Left Panel)</strong></h2>
    <p>These features give you precise control over what gets downloaded and how it's named and organized.</p>
    <ul>
        <li><strong>Filter by Character(s)</strong>: A powerful tool to download content featuring specific characters. You can enter multiple names separated by commas.
            <ul>
                <li><strong>Filter: [Scope] Button</strong>: This button changes how the character filter works:
                    <ul>
                        <li><strong>Title</strong>: Downloads posts only if a character's name is in the post title.</li>
                        <li><strong>Files</strong>: Downloads posts if a character's name is in any of the filenames within the post.</li>
                        <li><strong>Both</strong>: Combines the "Title" and "Files" logic.</li>
                        <li><strong>Comments (Beta)</strong>: Downloads a post if a character's name is mentioned in the comments section.</li>
                    </ul>
                </li>
            </ul>
        </li>
        <li><strong>Skip with Words</strong>: A keyword-based filter to avoid unwanted content (e.g., <code>WIP</code>, <code>sketch</code>).
            <ul>
                <li><strong>Scope: [Type] Button</strong>: This button changes how the skip filter works:
                    <ul>
                        <li><strong>Posts</strong>: Skips the entire post if a keyword is found in the title.</li>
                        <li><strong>Files</strong>: Skips only individual files if a keyword is found in the filename.</li>
                        <li><strong>Both</strong>: Applies both levels of skipping.</li>
                    </ul>
                </li>
            </ul>
        </li>
        <li><strong>Remove Words from name</strong>: Automatically cleans downloaded filenames by removing any specified words (e.g., "patreon," "HD").</li>
    </ul>
    <h3><strong>File Type Filter (Radio Buttons)</strong></h3>
    <p>This section lets you choose the kind of content you want:</p>
    <ul>
        <li><strong>All, Images/GIFs, Videos, 🎧 Only Audio, 📦 Only Archives</strong>: These options filter the downloads to only include the selected file types.</li>
        <li><strong>🔗 Only Links</strong>: This special mode doesn't download any files. Instead, it scans post descriptions and lists all external links (like Mega, Google Drive) in the log panel.</li>
        <li><strong>More</strong>: Opens a dialog for text-only downloads. You can choose to save post <strong>descriptions</strong> or <strong>comments</strong> as formatted <strong>PDF, DOCX, or TXT</strong> files. A key feature here is the <strong>"Single PDF"</strong> option, which compiles the text from all downloaded posts into one continuous, sorted PDF document.</li>
    </ul>
    <hr>
    <h2><strong>Download Options & Advanced Settings (Checkboxes)</strong></h2>
    <ul>
        <li><strong>Skip .zip</strong>: A simple toggle to ignore archive files during downloads.</li>
        <li><strong>Download Thumbnails Only</strong>: Downloads only the small preview images instead of the full-resolution files.</li>
        <li><strong>Scan Content for Images</strong>: A crucial feature that scans the post's text content for embedded images that may not be listed in the API, ensuring a more complete download.</li>
        <li><strong>Compress to WebP</strong>: Saves disk space by automatically converting large images into the efficient WebP format.</li>
        <li><strong>Keep Duplicates</strong>: Opens a dialog to control how files with identical content are handled. The default is to skip duplicates, but you can choose to keep all of them or set a specific limit (e.g., "keep up to 2 copies of the same file").</li>
        <li><strong>Subfolder per Post</strong>: Organizes downloads by creating a unique folder for each post, named after the post's title.</li>
        <li><strong>Date Prefix</strong>: When "Subfolder per Post" is on, this adds the post's date to the beginning of the folder name (e.g., <code>2025-07-25 Post Title</code>).</li>
        <li><strong>Separate Folders by Known.txt</strong>: This enables the automatic folder organization system based on your "Known Names" list.</li>
        <li><strong>Use Cookie</strong>: Allows the application to use browser cookies to access content that might be behind a paywall or login. You can paste a cookie string directly or use <strong>Browse...</strong> to select a <code>cookies.txt</code> file.</li>
        <li><strong>Use Multithreading</strong>: Greatly speeds up downloads of creator feeds by processing multiple posts at once. The number of <strong>Threads</strong> can be configured.</li>
        <li><strong>Show External Links in Log</strong>: When checked, a secondary log panel appears at the bottom of the right side, dedicated to listing any external links found.</li>
    </ul>
    <hr>
    <h2><strong>Known Names Management (Bottom-Left)</strong></h2>
    <p>This powerful feature automates the creation of organized, named folders.</p>
    <ul>
        <li><strong>Known Shows/Characters List</strong>: Displays all the names and groups you've saved.</li>
        <li><strong>Search...</strong>: Filters the list to quickly find a name.</li>
        <li><strong>Open Known.txt</strong>: Opens the source file in a text editor for advanced manual editing.</li>
        <li><strong>Add New Name</strong>:
            <ul>
                <li><strong>Single Name</strong>: Typing <code>Tifa Lockhart</code> and clicking <strong>➕ Add</strong> creates an entry that will match "Tifa Lockhart".</li>
                <li><strong>Group</strong>: Typing <code>(Boa, Hancock, Snake Princess)~</code> and clicking <strong>➕ Add</strong> creates a single entry named "Boa Hancock Snake Princess". The application will then look for "Boa," "Hancock," OR "Snake Princess" in titles/filenames and save any matches into that combined folder.</li>
            </ul>
        </li>
        <li><strong>⤵️ Add to Filter</strong>: Opens a dialog with your full Known Names list, allowing you to check multiple entries and add them all to the "Filter by Character(s)" field at once.</li>
        <li><strong>🗑️ Delete Selected</strong>: Removes highlighted names from your list.</li>
    </ul>
    <hr>
    <h2><strong>Action Buttons & Status Controls</strong></h2>
    <ul>
        <li><strong>⬇️ Start Download / 🔗 Extract Links</strong>: The main action button. Its function is dynamic:
            <ul>
                <li><strong>Normal Mode</strong>: Starts the download based on the current settings.</li>
                <li><strong>Update Mode</strong>: After selecting a creator profile, this button changes to <strong>🔄 Check for Updates</strong>.</li>
                <li><strong>Update Confirmation</strong>: After new posts are found, it changes to <strong>⬇️ Start Download (X new)</strong>.</li>
                <li><strong>Link Extraction Mode</strong>: The text changes to <strong>🔗 Extract Links</strong>.</li>
            </ul>
        </li>
        <li><strong>⏸️ Pause / ▶️ Resume Download</strong>: Pauses the ongoing download, allowing you to change certain settings (like filters) on the fly. Click again to resume.</li>
        <li><strong>❌ Cancel & Reset UI</strong>: Immediately stops all download activity and resets the UI to a clean state, preserving your URL and Download Location inputs.</li>
        <li><strong>Error Button</strong>: If files fail to download, they are logged. This button opens a dialog listing all failed files and will show a count of errors (e.g., <strong>(5) Error</strong>). From the dialog, you can:
            <ul>
                <li>Select specific files to <strong>Retry</strong> downloading.</li>
                <li><strong>Export</strong> the list of failed URLs to a <code>.txt</code> file.</li>
            </ul>
        </li>
        <li><strong>🔄 Reset (Top-Right)</strong>: A hard reset that clears all logs and returns every single UI element to its default state.</li>
        <li><strong>⚙️ (Settings)</strong>: Opens the main Settings dialog.</li>
        <li><strong>📜 (History)</strong>: Opens the Download History dialog.</li>
        <li><strong>? (Help)</strong>: Opens a helpful guide explaining the application's features.</li>
        <li><strong>❤️ Support</strong>: Opens a dialog with information on how to support the developer.</li>
    </ul>
    <hr>
    <h2><strong>Specialized Modes & Features</strong></h2>
    <h3><strong>⭐ Favorite Mode</strong></h3>
    <p>Activating this mode transforms the UI for managing saved collections:</p>
    <ul>
        <li>The URL input is disabled.</li>
        <li>The main action buttons are replaced with:
            <ul>
                <li><strong>🖼️ Favorite Artists</strong>: Opens a dialog to browse and queue downloads from your saved favorite creators.</li>
                <li><strong>📄 Favorite Posts</strong>: Opens a dialog to browse and queue downloads for specific saved favorite posts.</li>
            </ul>
        </li>
        <li><strong>Scope: [Location] Button</strong>: Toggles where the favorited content is saved:
            <ul>
                <li><strong>Selected Location</strong>: Saves all content directly into the main "Download Location".</li>
                <li><strong>Artist Folders</strong>: Creates a subfolder for each artist inside the main "Download Location".</li>
            </ul>
        </li>
    </ul>
    <h3><strong>📖 Manga/Comic Mode</strong></h3>
    <p>This mode is designed for sequential content and has several effects:</p>
    <ul>
        <li><strong>Reverses Download Order</strong>: It fetches and downloads posts from <strong>oldest to newest</strong>.</li>
        <li><strong>Enables Special Naming</strong>: A <strong><code>Name: [Style]</code></strong> button appears, allowing you to choose how files are named to maintain their correct order (e.g., by Post Title, by Date, or simple sequential numbering like <code>001, 002, 003...</code>).</li>
        <li><strong>Disables Multithreading (for certain styles)</strong>: To guarantee perfect sequential numbering, multithreading for posts is automatically disabled for certain naming styles.</li>
    </ul>
    <h3><strong>Session & Error Management</strong></h3>
    <ul>
        <li><strong>Session Restore</strong>: If the application is closed unexpectedly during a download, it will detect the incomplete session on the next launch. The UI will present a <strong>🔄 Restore Download</strong> button to resume exactly where you left off. You can also choose to discard the session.</li>
        <li><strong>Update Checking</strong>: By selecting a creator profile via the <strong>🎨 Creator Selection Popup</strong>, you can run an update check. The application compares the posts on the server with your download history for that creator and will prompt you to download only the new content.</li>
    </ul>
    <h3><strong>Logging & Monitoring</strong></h3>
    <ul>
        <li><strong>Progress Log</strong>: The main log provides real-time feedback on the download process, including status messages, file saves, skips, and errors.</li>
        <li><strong>👁️ Log View Toggle</strong>: Switches the log view between the standard <strong>Progress Log</strong> and a <strong>Missed Character Log</strong>, which shows potential character names from posts that were skipped by your filters, helping you discover new names to add to your list.</li>
    </ul>
</div>
