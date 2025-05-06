# Kemono Downloader

A simple, multi-platform GUI application built with PyQt5 to download content from Kemono.su or Coomer.party creator pages or specific posts, with options for filtering and organizing downloads.

## Features

* **GUI Interface:** Easy-to-use graphical interface.
* **URL Support:** Download from a creator's main page (paginated) or a specific post URL from Kemono or Coomer sites.
* **Download Location:** Select your desired output directory.
* **Subfolder Organization:**
    * Organize downloads into folders based on character/artist names found in post titles (using your "Known Names" list).
    * Option to create a custom folder for single post downloads.
    * Automatic folder naming based on post title if no known names are matched.
* **Known Names List:** Manage a persistent list of known names (artists, characters, series) for improved folder organization and filtering.
* **Content Filtering:**
    * **Character/Name Filter:** Only download posts where the specified known name is found in the title.
    * **File Type Filter:** Download All Files, Images/GIFs Only, or Videos Only.
    * **Skip Words Filter:** Specify a list of comma-separated words to skip posts or files if these words appear in their titles or filenames.
* **Archive Skipping:** Options to skip `.zip` and `.rar` files (enabled by default).
* **Image Compression:** Optionally compress large images (larger than 1.5MB) to WebP format to save space (requires Pillow library).
* **Thumbnail Downloading:** Option to download thumbnails. (Note: The previous local API method for enhanced thumbnail fetching has been removed. Thumbnail availability might depend on the source.)
* **Duplicate Prevention:**
    * Avoids re-downloading files with the same content hash.
    * Checks for existing filenames in the target directory.
* **Multithreading:** Utilizes multithreading for faster downloads from full creator pages (single posts are processed in a single thread).
* **Progress Log:** View detailed download progress, status messages, and errors.
* **Dark Theme:** Built-in dark theme for comfortable use.
* **Download Management:**
    * Ability to cancel an ongoing download process.
    * Option to skip the specific file currently being downloaded (in single-thread mode).
* **Persistent Configuration:** Saves the "Known Names" list to a local file.

## Prerequisites

* Python 3.6 or higher
* `pip` package installer

## Installation

1.  Clone or download this repository/script to your local machine.
2.  Navigate to the script's directory in your terminal or command prompt.
3.  Install the required Python libraries:
    ```bash
    pip install PyQt5 requests Pillow
    ```
    *(Pillow is required for image compression and potentially for basic image handling.)*

## How to Run

1.  Make sure you have followed the installation steps.
2.  Open your terminal or command prompt and navigate to the script's directory.
3.  Run the script using Python:
    ```bash
    python main.py
    ```

## How to Use

1.  **URL Input:** Enter the URL of the Kemono/Coomer creator page (e.g., `https://kemono.su/patreon/user/12345`) or a specific post (e.g., `https://kemono.su/patreon/user/12345/post/67890`) into the "Kemono Creator/Post URL" field.
2.  **Download Location:** Use the "Browse" button to select the root directory where you want to save the downloaded content.
3.  **Custom Folder Name (Single Post Only):** If downloading a single post and "Separate Folders" is enabled, you can specify a custom folder name for that post's content.
4.  **Filter by Show/Character Name (Optional):** If "Separate Folders" is enabled, enter a name from your "Known Names" list. Only posts with titles matching this name will be downloaded into a folder named accordingly. If empty, the script will try to match any known name or derive a folder name from the post title.
5.  **Skip Posts/Files with Words:** Enter comma-separated words (e.g., `WIP, sketch, preview`). Posts or files containing these words in their title/filename will be skipped.
6.  **File Type Filter:**
    * **All:** Downloads all files.
    * **Images/GIFs:** Downloads common image formats and GIFs.
    * **Videos:** Downloads common video formats.
7.  **Options (Checkboxes):**
    * **Separate Folders by Name/Title:** Enables creation of subfolders based on known names or post titles. Controls visibility of "Filter by Show/Character Name" and "Custom Folder Name". (Default: On)
    * **Download Thumbnails Only:** Attempts to download only thumbnails for posts. (Default: Off)
    * **Skip .zip / Skip .rar:** Prevents downloading of these archive types. (Default: On)
    * **Compress Large Images (to WebP):** Compresses images larger than 1.5MB. (Default: Off)
    * **Use Multithreading:** Enables faster downloads for full creator pages. (Default: On)
8.  **Known Names List:**
    * The list on the left ("Known Shows/Characters") displays names used for folder organization and filtering. This list is saved in `Known.txt`.
    * Use the input field below the list and the "➕ Add" button to add new names.
    * Select names and click "🗑️ Delete Selected" to remove them.
    * A search bar above the list allows you to filter the displayed names.
9.  **Start Download:** Click "⬇️ Start Download" to begin.
10. **Cancel / Skip:**
    * **❌ Cancel:** Stops the entire download process.
    * **⏭️ Skip Current File:** (Only in single-thread mode during file download) Skips the currently downloading file and moves to the next.
11. **Progress Log:** The area on the right shows detailed logs of the download process, including fetched posts, saved files, skips, and errors.

## Building an Executable (Optional)

You can create a standalone `.exe` file for Windows using `PyInstaller`.

1.  Install PyInstaller: `pip install pyinstaller`
2.  Obtain an icon file (`.ico`). Place it in the same directory as `main.py`.
3.  Open your terminal in the script's directory and run:
    ```bash
    pyinstaller --name "YourAppName" --onefile --windowed --icon="your_icon.ico" main.py
    ```
    Replace `"YourAppName"` with your desired application name and `"your_icon.ico"` with the actual name of your icon file.
4.  The executable will be found in the `./dist` folder.

## Configuration

The application saves your list of known names (characters, artists, series, etc.) to a file named `Known.txt` in the same directory as the script (`main.py`). Each name is stored on a new line. You can manually edit this file if needed.

## Dark Theme

The application uses a built-in dark theme for the user interface.

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue on the GitHub repository (if applicable). If you want to contribute code, please fork the repository and create a pull request.