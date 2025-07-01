# --- Standard Library Imports ---
import os
import re
import traceback
import json
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

# --- Third-Party Library Imports ---
import requests
try:
    from mega import Mega
    MEGA_AVAILABLE = True
except ImportError:
    MEGA_AVAILABLE = False

try:
    import gdown
    GDOWN_AVAILABLE = True
except ImportError:
    GDOWN_AVAILABLE = False

# --- Helper Functions ---

def _get_filename_from_headers(headers):
    """
    Extracts a filename from the Content-Disposition header.

    Args:
        headers (dict): A dictionary of HTTP response headers.

    Returns:
        str or None: The extracted filename, or None if not found.
    """
    cd = headers.get('content-disposition')
    if not cd:
        return None
    
    fname_match = re.findall('filename="?([^"]+)"?', cd)
    if fname_match:
        # Sanitize the filename to prevent directory traversal issues
        # and remove invalid characters for most filesystems.
        sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', fname_match[0].strip())
        return sanitized_name
        
    return None

# --- Main Service Downloader Functions ---

def download_mega_file(mega_link, download_path=".", logger_func=print):
    """
    Downloads a file from a public Mega.nz link.

    Args:
        mega_link (str): The public Mega.nz link to the file.
        download_path (str): The directory to save the downloaded file.
        logger_func (callable): Function to use for logging.
    """
    if not MEGA_AVAILABLE:
        logger_func("❌ Error: mega.py library is not installed. Cannot download from Mega.")
        logger_func("   Please install it: pip install mega.py")
        raise ImportError("mega.py library not found.")

    logger_func(f"   [Mega] Initializing Mega client...")
    try:
        mega_client = Mega()
        m = mega_client.login()
        logger_func(f"   [Mega] Attempting to download from: {mega_link}")
        
        if not os.path.exists(download_path):
            os.makedirs(download_path, exist_ok=True)
            logger_func(f"   [Mega] Created download directory: {download_path}")
            
        # The download_url method handles file info fetching and saving internally.
        downloaded_file_path = m.download_url(mega_link, dest_path=download_path)

        if downloaded_file_path and os.path.exists(downloaded_file_path):
            logger_func(f"   [Mega] ✅ File downloaded successfully! Saved as: {downloaded_file_path}")
        else:
            raise Exception(f"Mega download failed or file not found. Returned: {downloaded_file_path}")

    except Exception as e:
        logger_func(f"   [Mega] ❌ An unexpected error occurred during Mega download: {e}")
        traceback.print_exc(limit=2)
        raise  # Re-raise the exception to be handled by the calling worker

def download_gdrive_file(gdrive_link, download_path=".", logger_func=print):
    """
    Downloads a file from a public Google Drive link using the gdown library.

    Args:
        gdrive_link (str): The public Google Drive link to the file.
        download_path (str): The directory to save the downloaded file.
        logger_func (callable): Function to use for logging.
    """
    if not GDOWN_AVAILABLE:
        logger_func("❌ Error: gdown library is not installed. Cannot download from Google Drive.")
        logger_func("   Please install it: pip install gdown")
        raise ImportError("gdown library not found.")

    logger_func(f"   [GDrive] Attempting to download: {gdrive_link}")
    try:
        if not os.path.exists(download_path):
            os.makedirs(download_path, exist_ok=True)
            logger_func(f"   [GDrive] Created download directory: {download_path}")

        # gdown handles finding the file ID and downloading. 'fuzzy=True' helps with various URL formats.
        output_file_path = gdown.download(gdrive_link, output=download_path, quiet=False, fuzzy=True)

        if output_file_path and os.path.exists(output_file_path):
            logger_func(f"   [GDrive] ✅ Google Drive file downloaded successfully: {output_file_path}")
        else:
            raise Exception(f"gdown download failed or file not found. Returned: {output_file_path}")

    except Exception as e:
        logger_func(f"   [GDrive] ❌ An error occurred during Google Drive download: {e}")
        traceback.print_exc(limit=2)
        raise

def download_dropbox_file(dropbox_link, download_path=".", logger_func=print):
    """
    Downloads a file from a public Dropbox link by modifying the URL for direct download.

    Args:
        dropbox_link (str): The public Dropbox link to the file.
        download_path (str): The directory to save the downloaded file.
        logger_func (callable): Function to use for logging.
    """
    logger_func(f"   [Dropbox] Attempting to download: {dropbox_link}")
    
    # Modify the Dropbox URL to force a direct download instead of showing the preview page.
    parsed_url = urlparse(dropbox_link)
    query_params = parse_qs(parsed_url.query)
    query_params['dl'] = ['1']
    new_query = urlencode(query_params, doseq=True)
    direct_download_url = urlunparse(parsed_url._replace(query=new_query))

    logger_func(f"   [Dropbox] Using direct download URL: {direct_download_url}")

    try:
        if not os.path.exists(download_path):
            os.makedirs(download_path, exist_ok=True)
            logger_func(f"   [Dropbox] Created download directory: {download_path}")

        with requests.get(direct_download_url, stream=True, allow_redirects=True, timeout=(10, 300)) as r:
            r.raise_for_status()
            
            # Determine filename from headers or URL
            filename = _get_filename_from_headers(r.headers) or os.path.basename(parsed_url.path) or "dropbox_file"
            full_save_path = os.path.join(download_path, filename)
            
            logger_func(f"   [Dropbox] Starting download of '{filename}'...")
            
            # Write file to disk in chunks
            with open(full_save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger_func(f"   [Dropbox] ✅ Dropbox file downloaded successfully: {full_save_path}")

    except Exception as e:
        logger_func(f"   [Dropbox] ❌ An error occurred during Dropbox download: {e}")
        traceback.print_exc(limit=2)
        raise
