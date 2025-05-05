# Kemono Downloader

A simple, multi-platform GUI application built with PyQt5 to download content from Kemono.su creator pages or specific posts, with options for filtering and organizing downloads.

## Features

* **GUI Interface:** Easy-to-use graphical interface.
* **URL Support:** Download from a creator's main page (paginated) or a specific post URL.
* **Download Location:** Select your desired output directory.
* **Character Filtering:** Optionally filter posts and organize downloads into folders based on character names detected in post titles.
* **Known Characters List:** Manage a persistent list of known characters for better folder organization.
* **File Type Filtering:** Download All Files, Images Only (PNG, JPG, JPEG, WEBP, excluding GIFs), or Videos Only (MP4, MOV, MKV, WEBM, including GIFs).
* **Archive Skipping:** Options to skip `.zip` and `.rar` files.
* **Folder Organization:** Choose to download files into separate folders (based on character/title) or all into a single selected folder.
* **Progress Log:** View download progress and status messages.
* **Dark Theme:** Built-in dark theme for comfortable use.
* **Download Cancellation:** Ability to cancel an ongoing download.
* **Skip Current File:** Option to skip the specific file currently being downloaded within a larger batch.

## Prerequisites

* Python 3.6 or higher
* `pip` package installer

## Installation

1.  Clone or download this repository to your local machine.
2.  Navigate to the script's directory in your terminal or command prompt.
3.  Install the required Python libraries:
    ```bash
    pip install PyQt5 requests
    ```

## How to Run

1.  Make sure you have followed the installation steps.
2.  Open your terminal or command prompt and navigate to the script's directory.
3.  Run the script using Python:
    ```bash
    python main.py
    ```

## How to Use

1.  **URL Input:** Enter the URL of the Kemono creator page (e.g., `https://kemono.su/patreon/user/12345`) or a specific post (e.g., `https://kemono.su/api/v1/patreon/user/12345/post/67890`) into the "Kemono Creator Page or Post URL" field. Note that while the API URL format is shown, the GUI can usually handle the standard web page URL format as well (`https://kemono.su/patreon/user/12345` or `https://kemono.su/patreon/user/12345/post/67890`).
2.  **Download Location:** Use the "Browse" button to select the root directory where you want to save the downloaded content.
3.  **Filter by Character (optional):** Enter a character name from your "Known Characters" list to only download posts tagged with that character. If left empty, it will try to find any known character in the title or default to a name derived from the title.
4.  **File Type Filter:** Select the type of files you want to download (All Files, Images Only, or Videos Only).
5.  **Skip Archives:** Check "Skip Zip Files" and/or "Skip RAR Files" to prevent downloading these archive formats. These are checked by default.
6.  **Folder Organization:** Check "Download to Separate Folders" to create subfolders within your download location based on character names or derived titles. Uncheck it to download all files directly into the selected Download Location folder. This is checked by default.
7.  **Known Characters:** The list on the right shows characters the application knows about (saved in `kemono_downloader_config.txt`). You can manually add or delete characters here. If a new character is detected in a post title while "Download to Separate Folders" is enabled and is not in your list, the application may prompt you to add it.
8.  **Start Download:** Click the "Start Download" button to begin fetching and processing content.
9.  **Cancel Download:** Click "Cancel Download" to stop the process. Note that the current file download might finish before the cancellation takes effect.
10. **Skip Current File:** Click "Skip Current File" to immediately stop downloading the file currently in progress and move to the next one. This button is only enabled when a file is actively being downloaded.
11. **Progress Log:** Monitor the download status, file saves, and any errors in the "Progress Log" area.

## Building an Executable (Optional)

You can create a standalone `.exe` file for Windows using `PyInstaller`.

1.  Install PyInstaller: `pip install pyinstaller`
2.  Obtain an icon file (`.ico`). Place it in the same directory as `main.py`.
3.  Open your terminal in the script's directory and run:
    ```bash
    pyinstaller --onefile --windowed --icon="your_icon_name.ico" --name="Kemono Downloader" main.py
    ```
    Replace `"your_icon_name.ico"` with the actual name of your icon file.
4.  The executable will be found in the `./dist` folder.

## Configuration

The application saves your list of known characters to a file named `kemono_downloader_config.txt` in the same directory as the script (`main.py`). Each character name is stored on a new line. You can manually edit this file if needed, but be mindful of the format (one name per line).

## Dark Theme

The application comes with a simple dark theme applied via stylesheets.

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue on the GitHub repository. If you want to contribute code, please fork the repository and create a pull request.