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
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False

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

def download_mega_file(mega_url, download_path, logger_func=print):
    """
    Downloads a file from a Mega.nz URL.
    Handles both public links and links that include a decryption key.
    """
    if not MEGA_AVAILABLE:
        logger_func("❌ Mega download failed: 'mega.py' library is not installed.")
        return

    logger_func(f"   [Mega] Initializing Mega client...")
    try:
        mega = Mega()
        # Anonymous login is sufficient for public links
        m = mega.login()

        # --- MODIFIED PART: Added error handling for invalid links ---
        try:
            file_details = m.find(mega_url)
            if file_details is None:
                logger_func(f"   [Mega] ❌ Download failed. The link appears to be invalid or has been taken down: {mega_url}")
                return
        except (ValueError, json.JSONDecodeError) as e:
            # This block catches the "Expecting value" error
            logger_func(f"   [Mega] ❌ Download failed. The link is likely invalid or expired. Error: {e}")
            return
        except Exception as e:
            # Catch other potential errors from the mega.py library
            logger_func(f"   [Mega] ❌ An unexpected error occurred trying to access the link: {e}")
            return
        # --- END OF MODIFIED PART ---

        filename = file_details[1]['a']['n']
        logger_func(f"   [Mega] File found: '{filename}'. Starting download...")

        # Sanitize filename before saving
        safe_filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_', '-')]).rstrip()
        final_path = os.path.join(download_path, safe_filename)

        # Check if file already exists
        if os.path.exists(final_path):
            logger_func(f"   [Mega] ℹ️ File '{safe_filename}' already exists. Skipping download.")
            return

        # Start the download
        m.download_url(mega_url, dest_path=download_path, dest_filename=safe_filename)
        logger_func(f"   [Mega] ✅ Successfully downloaded '{safe_filename}' to '{download_path}'")

    except Exception as e:
        logger_func(f"   [Mega] ❌ An unexpected error occurred during the Mega download process: {e}")

def download_gdrive_file(url, download_path, logger_func=print):
    """Downloads a file from a Google Drive link."""
    if not GDRIVE_AVAILABLE:
        logger_func("❌ Google Drive download failed: 'gdown' library is not installed.")
        return
    try:
        logger_func(f"   [G-Drive] Starting download for: {url}")
        # --- MODIFIED PART: Added a message and set quiet=True ---
        logger_func("   [G-Drive] Download in progress... This may take some time. Please wait.")
        
        # By setting quiet=True, the progress bar will no longer be printed to the terminal.
        output_path = gdown.download(url, output=download_path, quiet=True, fuzzy=True)
        # --- END OF MODIFIED PART ---
        
        if output_path and os.path.exists(output_path):
            logger_func(f"   [G-Drive] ✅ Successfully downloaded to '{output_path}'")
        else:
            logger_func(f"   [G-Drive] ❌ Download failed. The file may have been moved, deleted, or is otherwise inaccessible.")
    except Exception as e:
        logger_func(f"   [G-Drive] ❌ An unexpected error occurred: {e}")

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
