from mega import Mega 
import os 
import requests 
import traceback 
from urllib .parse import urlparse ,urlunparse ,parse_qs ,urlencode 

try :
    import gdown 
    GDOWN_AVAILABLE =True 
except ImportError :
    GDOWN_AVAILABLE =False 

def download_mega_file (mega_link ,download_path =".",logger_func =print ):
    """
    Downloads a file from a public Mega.nz link.

    Args:
        mega_link (str): The public Mega.nz link to the file.
        download_path (str, optional): The directory to save the downloaded file.
                                       Defaults to the current directory.
        logger_func (callable, optional): Function to use for logging. Defaults to print.
    """
    logger_func ("Initializing Mega client...")
    mega_client =Mega ()





    m =mega_client .login ()

    logger_func (f"Attempting to download from: {mega_link }")

    try :

        if not os .path .exists (download_path ):
            logger_func (f"Download path '{download_path }' does not exist. Creating it...")
            os .makedirs (download_path ,exist_ok =True )




        logger_func (f"Starting download to '{download_path }'...")



        file_handle =m .download_url (mega_link ,dest_path =download_path )

        if file_handle :




            logger_func (f"File downloaded successfully! (Handle: {file_handle })")










            try :
                info =m .get_public_url_info (mega_link )
                filename =info .get ('name','downloaded_file')
                full_download_path =os .path .join (download_path ,filename )
                logger_func (f"Downloaded file should be at: {full_download_path }")
                if not os .path .exists (full_download_path ):
                    logger_func (f"Warning: Expected file '{full_download_path }' not found. The library might have saved it with a different name or failed silently after appearing to succeed.")
            except Exception as e_info :
                logger_func (f"Could not retrieve file info to confirm filename: {e_info }")

        else :
            logger_func ("Download failed. The download_url method did not return a file handle.")

    except PermissionError :
        logger_func (f"Error: Permission denied to write to '{download_path }'. Please check permissions.")
    except FileNotFoundError :
        logger_func (f"Error: The specified download path '{download_path }' is invalid or a component was not found.")
    except ConnectionError as e :
        logger_func (f"Error: Connection problem. {e }")
    except requests .exceptions .RequestException as e :
        logger_func (f"Error during request to Mega: {e }")
    except Exception as e :
        logger_func (f"An error occurred during Mega download: {e }")
        traceback .print_exc ()

def download_gdrive_file (gdrive_link ,download_path =".",logger_func =print ):
    """
    Downloads a file from a public Google Drive link.

    Args:
        gdrive_link (str): The public Google Drive link to the file.
        download_path (str, optional): The directory to save the downloaded file.
                                       Defaults to the current directory.
        logger_func (callable, optional): Function to use for logging. Defaults to print.
    """
    if not GDOWN_AVAILABLE :
        logger_func ("❌ Error: gdown library is not installed. Cannot download from Google Drive.")
        logger_func ("Please install it: pip install gdown")
        raise ImportError ("gdown library not found. Please install it: pip install gdown")

    logger_func (f"Attempting to download from Google Drive: {gdrive_link }")
    try :
        if not os .path .exists (download_path ):
            logger_func (f"Download path '{download_path }' does not exist. Creating it...")
            os .makedirs (download_path ,exist_ok =True )

        logger_func (f"Starting Google Drive download to '{download_path }'...")

        output_file_path =gdown .download (gdrive_link ,output =download_path ,quiet =False ,fuzzy =True )

        if output_file_path and os .path .exists (os .path .join (download_path ,os .path .basename (output_file_path ))):
            logger_func (f"✅ Google Drive file downloaded successfully: {output_file_path }")
        elif output_file_path :
            full_path_check =os .path .join (download_path ,output_file_path )
            if os .path .exists (full_path_check ):
                 logger_func (f"✅ Google Drive file downloaded successfully: {full_path_check }")
            else :
                 logger_func (f"⚠️ Google Drive download finished, gdown returned '{output_file_path }', but file not found at expected location.")
                 logger_func (f"   Please check '{download_path }' for the downloaded file, it might have a different name than expected by gdown's return.")

                 files_in_dest =[f for f in os .listdir (download_path )if os .path .isfile (os .path .join (download_path ,f ))]
                 if len (files_in_dest )==1 :
                     logger_func (f"   Found one file in destination: {os .path .join (download_path ,files_in_dest [0 ])}. Assuming this is it.")
                 elif len (files_in_dest )>1 and output_file_path in files_in_dest :
                     logger_func (f"   Confirmed file '{output_file_path }' exists in '{download_path }'.")
                 else :
                     raise Exception (f"gdown download failed or file not found. Returned: {output_file_path }")
        else :
            logger_func ("❌ Google Drive download failed. gdown did not return an output path.")
            raise Exception ("gdown download failed.")

    except PermissionError :
        logger_func (f"❌ Error: Permission denied to write to '{download_path }'. Please check permissions.")
        raise 
    except Exception as e :
        logger_func (f"❌ An error occurred during Google Drive download: {e }")
        traceback .print_exc ()
        raise 

def _get_filename_from_headers (headers ):
    cd =headers .get ('content-disposition')
    if not cd :
        return None 
    fname_match =re .findall ('filename="?([^"]+)"?',cd )
    if fname_match :
        return fname_match [0 ].strip ()
    return None 

def download_dropbox_file (dropbox_link ,download_path =".",logger_func =print ):
    """
    Downloads a file from a public Dropbox link.

    Args:
        dropbox_link (str): The public Dropbox link to the file.
        download_path (str, optional): The directory to save the downloaded file.
                                       Defaults to the current directory.
        logger_func (callable, optional): Function to use for logging. Defaults to print.
    """
    logger_func (f"Attempting to download from Dropbox: {dropbox_link }")


    parsed_url =urlparse (dropbox_link )
    query_params =parse_qs (parsed_url .query )
    query_params ['dl']=['1']
    new_query =urlencode (query_params ,doseq =True )
    direct_download_url =urlunparse (parsed_url ._replace (query =new_query ))

    logger_func (f"   Using direct download URL: {direct_download_url }")

    try :
        if not os .path .exists (download_path ):
            logger_func (f"Download path '{download_path }' does not exist. Creating it...")
            os .makedirs (download_path ,exist_ok =True )

        with requests .get (direct_download_url ,stream =True ,allow_redirects =True ,timeout =(10 ,300 ))as r :
            r .raise_for_status ()
            filename =_get_filename_from_headers (r .headers )or os .path .basename (urlparse (dropbox_link ).path )or "dropbox_downloaded_file"

            filename =re .sub (r'[<>:"/\\|?*]','_',filename )
            full_save_path =os .path .join (download_path ,filename )
            logger_func (f"Starting Dropbox download of '{filename }' to '{full_save_path }'...")
            with open (full_save_path ,'wb')as f :
                for chunk in r .iter_content (chunk_size =8192 ):
                    f .write (chunk )
            logger_func (f"✅ Dropbox file downloaded successfully: {full_save_path }")
    except Exception as e :
        logger_func (f"❌ An error occurred during Dropbox download: {e }")
        traceback .print_exc ()
        raise 

if __name__ =="__main__":



    mega_file_link ="https://mega.nz/file/03oRjBQT#Tcbp5sQVIyPbdmv8sLgbb9Lf9AZvZLdKRSQiuXkNW0k"

    if not mega_file_link .startswith ("https://mega.nz/file/"):
        print ("Invalid Mega file link format. It should start with 'https://mega.nz/file/'.")
    else :


        script_dir =os .path .dirname (os .path .abspath (__file__ ))
        download_directory =os .path .join (script_dir ,"mega_downloads")

        print (f"Files will be downloaded to: {download_directory }")
        download_mega_file (mega_file_link ,download_directory ,logger_func =print )

