from mega import Mega # Correctly import the Mega class
import os
import requests # Added import for requests.exceptions
import traceback
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

try:
    import gdown
    GDOWN_AVAILABLE = True
except ImportError:
    GDOWN_AVAILABLE = False

def download_mega_file(mega_link, download_path=".", logger_func=print):
    """
    Downloads a file from a public Mega.nz link.

    Args:
        mega_link (str): The public Mega.nz link to the file.
        download_path (str, optional): The directory to save the downloaded file.
                                       Defaults to the current directory.
        logger_func (callable, optional): Function to use for logging. Defaults to print.
    """
    logger_func("Initializing Mega client...")
    mega_client = Mega() # Instantiate the imported Mega class

    # For public links, login is usually not required.
    # If you needed to log in for private files:
    # m = mega.login("your_email@example.com", "your_password")
    # Or anonymous login for some operations:
    m = mega_client.login() # Call login on the instance

    logger_func(f"Attempting to download from: {mega_link}")

    try:
        # Ensure the download path exists
        if not os.path.exists(download_path):
            logger_func(f"Download path '{download_path}' does not exist. Creating it...")
            os.makedirs(download_path, exist_ok=True)
        
        # It's often better to let mega.py handle finding the file from the URL
        # and then downloading it.
        # The `download_url` method is convenient for public links.
        logger_func(f"Starting download to '{download_path}'...")
        
        # mega.py's download_url will download the file to the specified path
        # and name it appropriately.
        file_handle = m.download_url(mega_link, dest_path=download_path) # m is the logged-in client
        
        if file_handle:
            # The download_url method itself handles the file saving.
            # The return value 'file_handle' might be the filename or a handle,
            # depending on the library version and specifics.
            # For modern mega.py, it often returns the local path to the downloaded file.
            logger_func(f"File downloaded successfully! (Handle: {file_handle})")
            # If you need the exact filename it was saved as:
            # You might need to inspect what `download_url` returns or list dir contents
            # if the filename isn't directly returned in a usable way.
            # Often, the library names it based on the Mega file name.
            # For this example, we'll assume it's handled and saved in download_path.
            
            # To get the actual filename (as mega.py might rename it)
            # We can list the directory and find the newest file if only one download happened
            # Or, more robustly, use the information from `m.get_public_url_info(mega_link)`
            # to get the expected filename.
            try:
                info = m.get_public_url_info(mega_link)
                filename = info.get('name', 'downloaded_file') # Default if name not found
                full_download_path = os.path.join(download_path, filename)
                logger_func(f"Downloaded file should be at: {full_download_path}")
                if not os.path.exists(full_download_path):
                    logger_func(f"Warning: Expected file '{full_download_path}' not found. The library might have saved it with a different name or failed silently after appearing to succeed.")
            except Exception as e_info:
                logger_func(f"Could not retrieve file info to confirm filename: {e_info}")

        else:
            logger_func("Download failed. The download_url method did not return a file handle.")

    except PermissionError:
        logger_func(f"Error: Permission denied to write to '{download_path}'. Please check permissions.")
    except FileNotFoundError:
        logger_func(f"Error: The specified download path '{download_path}' is invalid or a component was not found.")
    except ConnectionError as e: # More specific requests exception
        logger_func(f"Error: Connection problem. {e}")
    except requests.exceptions.RequestException as e: # Catch other requests-related errors
        logger_func(f"Error during request to Mega: {e}")
    except Exception as e:
        logger_func(f"An error occurred during Mega download: {e}")
        traceback.print_exc()

def download_gdrive_file(gdrive_link, download_path=".", logger_func=print):
    """
    Downloads a file from a public Google Drive link.

    Args:
        gdrive_link (str): The public Google Drive link to the file.
        download_path (str, optional): The directory to save the downloaded file.
                                       Defaults to the current directory.
        logger_func (callable, optional): Function to use for logging. Defaults to print.
    """
    if not GDOWN_AVAILABLE:
        logger_func("❌ Error: gdown library is not installed. Cannot download from Google Drive.")
        logger_func("Please install it: pip install gdown")
        raise ImportError("gdown library not found. Please install it: pip install gdown")

    logger_func(f"Attempting to download from Google Drive: {gdrive_link}")
    try:
        if not os.path.exists(download_path):
            logger_func(f"Download path '{download_path}' does not exist. Creating it...")
            os.makedirs(download_path, exist_ok=True)

        logger_func(f"Starting Google Drive download to '{download_path}'...")
        # gdown.download returns the path to the downloaded file
        output_file_path = gdown.download(gdrive_link, output=download_path, quiet=False, fuzzy=True)

        if output_file_path and os.path.exists(os.path.join(download_path, os.path.basename(output_file_path))):
            logger_func(f"✅ Google Drive file downloaded successfully: {output_file_path}")
        elif output_file_path: # gdown might return a path but if download_path was a dir, it might be just the filename
            full_path_check = os.path.join(download_path, output_file_path)
            if os.path.exists(full_path_check):
                 logger_func(f"✅ Google Drive file downloaded successfully: {full_path_check}")
            else:
                 logger_func(f"⚠️ Google Drive download finished, gdown returned '{output_file_path}', but file not found at expected location.")
                 logger_func(f"   Please check '{download_path}' for the downloaded file, it might have a different name than expected by gdown's return.")
                 # As a fallback, list files in dir if only one was expected
                 files_in_dest = [f for f in os.listdir(download_path) if os.path.isfile(os.path.join(download_path, f))]
                 if len(files_in_dest) == 1:
                     logger_func(f"   Found one file in destination: {os.path.join(download_path, files_in_dest[0])}. Assuming this is it.")
                 elif len(files_in_dest) > 1 and output_file_path in files_in_dest: # if gdown returned just filename
                     logger_func(f"   Confirmed file '{output_file_path}' exists in '{download_path}'.")
                 else:
                     raise Exception(f"gdown download failed or file not found. Returned: {output_file_path}")
        else:
            logger_func("❌ Google Drive download failed. gdown did not return an output path.")
            raise Exception("gdown download failed.")

    except PermissionError:
        logger_func(f"❌ Error: Permission denied to write to '{download_path}'. Please check permissions.")
        raise
    except Exception as e:
        logger_func(f"❌ An error occurred during Google Drive download: {e}")
        traceback.print_exc()
        raise

def _get_filename_from_headers(headers):
    cd = headers.get('content-disposition')
    if not cd:
        return None
    fname_match = re.findall('filename="?([^"]+)"?', cd)
    if fname_match:
        return fname_match[0].strip()
    return None

def download_dropbox_file(dropbox_link, download_path=".", logger_func=print):
    """
    Downloads a file from a public Dropbox link.

    Args:
        dropbox_link (str): The public Dropbox link to the file.
        download_path (str, optional): The directory to save the downloaded file.
                                       Defaults to the current directory.
        logger_func (callable, optional): Function to use for logging. Defaults to print.
    """
    logger_func(f"Attempting to download from Dropbox: {dropbox_link}")
    
    # Modify URL for direct download
    parsed_url = urlparse(dropbox_link)
    query_params = parse_qs(parsed_url.query)
    query_params['dl'] = ['1'] # Set dl=1 for direct download
    new_query = urlencode(query_params, doseq=True)
    direct_download_url = urlunparse(parsed_url._replace(query=new_query))

    logger_func(f"   Using direct download URL: {direct_download_url}")

    try:
        if not os.path.exists(download_path):
            logger_func(f"Download path '{download_path}' does not exist. Creating it...")
            os.makedirs(download_path, exist_ok=True)

        with requests.get(direct_download_url, stream=True, allow_redirects=True, timeout=(10,300)) as r:
            r.raise_for_status()
            filename = _get_filename_from_headers(r.headers) or os.path.basename(urlparse(dropbox_link).path) or "dropbox_downloaded_file"
            # Sanitize filename (basic)
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            full_save_path = os.path.join(download_path, filename)
            logger_func(f"Starting Dropbox download of '{filename}' to '{full_save_path}'...")
            with open(full_save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger_func(f"✅ Dropbox file downloaded successfully: {full_save_path}")
    except Exception as e:
        logger_func(f"❌ An error occurred during Dropbox download: {e}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    # --- IMPORTANT ---
    # Replace this with an ACTUAL PUBLIC MEGA.NZ FILE LINK to test.
    # Using the specific link you provided:
    mega_file_link = "https://mega.nz/file/03oRjBQT#Tcbp5sQVIyPbdmv8sLgbb9Lf9AZvZLdKRSQiuXkNW0k"

    if not mega_file_link.startswith("https://mega.nz/file/"):
        print("Invalid Mega file link format. It should start with 'https://mega.nz/file/'.") # Or use logger_func if testing outside main
    else:
        # Specify your desired download directory
        # If you want to download to a specific folder, e.g., "MegaDownloads" in your user's Downloads folder:
        # user_downloads_path = os.path.expanduser("~/Downloads")
        # download_directory = os.path.join(user_downloads_path, "MegaDownloads")
        
        # For this example, we'll download to a "mega_downloads" subfolder in the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        download_directory = os.path.join(script_dir, "mega_downloads")
        
        print(f"Files will be downloaded to: {download_directory}") # Or use logger_func
        download_mega_file(mega_file_link, download_directory, logger_func=print)

    # Test Google Drive
    # gdrive_test_link = "YOUR_PUBLIC_GOOGLE_DRIVE_FILE_LINK_HERE" # Replace with a real link
    # if gdrive_test_link and gdrive_test_link != "YOUR_PUBLIC_GOOGLE_DRIVE_FILE_LINK_HERE":
    #     gdrive_download_dir = os.path.join(script_dir, "gdrive_downloads")
    #     print(f"\nGoogle Drive files will be downloaded to: {gdrive_download_dir}")
    #     download_gdrive_file(gdrive_test_link, gdrive_download_dir, logger_func=print)
    #
    # # Test Dropbox
    # dropbox_test_link = "YOUR_PUBLIC_DROPBOX_FILE_LINK_HERE"  # Replace with a real link
    # if dropbox_test_link and dropbox_test_link != "YOUR_PUBLIC_DROPBOX_FILE_LINK_HERE":
    #     dropbox_download_dir = os.path.join(script_dir, "dropbox_downloads")
    #     print(f"\nDropbox files will be downloaded to: {dropbox_download_dir}")
    #     download_dropbox_file(dropbox_test_link, dropbox_download_dir, logger_func=print)
