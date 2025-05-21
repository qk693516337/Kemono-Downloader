import os
import time
import requests
import hashlib
import http.client
import traceback
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

CHUNK_DOWNLOAD_RETRY_DELAY = 2 # Slightly reduced for faster retries if needed
MAX_CHUNK_DOWNLOAD_RETRIES = 1 # Further reduced for quicker fallback if a chunk is problematic
DOWNLOAD_CHUNK_SIZE_ITER = 1024 * 256  # 256KB for iter_content within a chunk download


def _download_individual_chunk(chunk_url, temp_file_path, start_byte, end_byte, headers,
                               part_num, total_parts, progress_data, cancellation_event, skip_event, pause_event, global_emit_time_ref, # Added global_emit_time_ref
                               logger_func, emitter=None, api_original_filename=None): # Renamed logger, signals to emitter
    """Downloads a single chunk of a file and writes it to the temp file."""
    if cancellation_event and cancellation_event.is_set():
        logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Download cancelled before start.")
        return 0, False  # bytes_downloaded, success
    if skip_event and skip_event.is_set():
        logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Skip event triggered before start.")
        return 0, False

    if pause_event and pause_event.is_set():
        logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Download paused before start...")
        while pause_event.is_set():
            if cancellation_event and cancellation_event.is_set():
                logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Download cancelled while paused.")
                return 0, False
            time.sleep(0.2) # Shorter sleep for responsive resume
        logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Download resumed.")

    chunk_headers = headers.copy()
    # end_byte can be -1 for 0-byte files, meaning download from start_byte to end of file (which is start_byte itself)
    if end_byte != -1 : # For 0-byte files, end_byte might be -1, Range header should not be set or be 0-0
        chunk_headers['Range'] = f"bytes={start_byte}-{end_byte}"
    elif start_byte == 0 and end_byte == -1: # Specifically for 0-byte files
        # Some servers might not like Range: bytes=0--1.
        # For a 0-byte file, we might not even need a range header, or Range: bytes=0-0
        # Let's try without for 0-byte, or rely on server to handle 0-0 if Content-Length was 0.
        # If Content-Length was 0, the main function might handle it directly.
        # This chunking logic is primarily for files > 0 bytes.
        # For now, if end_byte is -1, it implies a 0-byte file, so we expect 0 bytes.
        pass


    bytes_this_chunk = 0
    # last_progress_emit_time_for_chunk = time.time() # Replaced by global_emit_time_ref logic
    last_speed_calc_time = time.time()
    bytes_at_last_speed_calc = 0

    for attempt in range(MAX_CHUNK_DOWNLOAD_RETRIES + 1):
        if cancellation_event and cancellation_event.is_set():
            logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Cancelled during retry loop.")
            return bytes_this_chunk, False
        if skip_event and skip_event.is_set():
            logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Skip event during retry loop.")
            return bytes_this_chunk, False
        if pause_event and pause_event.is_set():
            logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Paused during retry loop...")
            while pause_event.is_set():
                if cancellation_event and cancellation_event.is_set():
                    logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Cancelled while paused in retry loop.")
                    return bytes_this_chunk, False
                time.sleep(0.2)
            logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Resumed from retry loop pause.")

        try:
            if attempt > 0:
                logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Retrying download (Attempt {attempt}/{MAX_CHUNK_DOWNLOAD_RETRIES})...")
                time.sleep(CHUNK_DOWNLOAD_RETRY_DELAY * (2 ** (attempt - 1)))
                # Reset speed calculation on retry
                last_speed_calc_time = time.time()
                bytes_at_last_speed_calc = bytes_this_chunk # Current progress of this chunk
            
            # Enhanced log message for chunk start
            log_msg = f"   🚀 [Chunk {part_num + 1}/{total_parts}] Starting download: bytes {start_byte}-{end_byte if end_byte != -1 else 'EOF'}"
            logger_func(log_msg)
            print(f"DEBUG_MULTIPART: {log_msg}") # Direct console print for debugging
            response = requests.get(chunk_url, headers=chunk_headers, timeout=(10, 120), stream=True)
            response.raise_for_status()

            # For 0-byte files, if end_byte was -1, we expect 0 content.
            if start_byte == 0 and end_byte == -1 and int(response.headers.get('Content-Length', 0)) == 0:
                logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Confirmed 0-byte file.")
                with progress_data['lock']:
                    progress_data['chunks_status'][part_num]['active'] = False
                    progress_data['chunks_status'][part_num]['speed_bps'] = 0
                return 0, True

            with open(temp_file_path, 'r+b') as f:  # Open in read-write binary
                f.seek(start_byte)
                for data_segment in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE_ITER):
                    if cancellation_event and cancellation_event.is_set():
                        logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Cancelled during data iteration.")
                        return bytes_this_chunk, False
                    if skip_event and skip_event.is_set():
                        logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Skip event during data iteration.")
                        return bytes_this_chunk, False
                    if pause_event and pause_event.is_set():
                        logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Paused during data iteration...")
                        while pause_event.is_set():
                            if cancellation_event and cancellation_event.is_set():
                                logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Cancelled while paused in data iteration.")
                                return bytes_this_chunk, False
                            time.sleep(0.2)
                        logger_func(f"   [Chunk {part_num + 1}/{total_parts}] Resumed from data iteration pause.")
                    if data_segment:
                        f.write(data_segment)
                        bytes_this_chunk += len(data_segment)
                        
                        with progress_data['lock']:
                            # Increment both the chunk's downloaded and the overall downloaded
                            progress_data['total_downloaded_so_far'] += len(data_segment)
                            progress_data['chunks_status'][part_num]['downloaded'] = bytes_this_chunk
                            progress_data['chunks_status'][part_num]['active'] = True

                            current_time = time.time()
                            time_delta_speed = current_time - last_speed_calc_time
                            if time_delta_speed > 0.5: # Calculate speed every 0.5 seconds
                                bytes_delta = bytes_this_chunk - bytes_at_last_speed_calc
                                current_speed_bps = (bytes_delta * 8) / time_delta_speed if time_delta_speed > 0 else 0
                                progress_data['chunks_status'][part_num]['speed_bps'] = current_speed_bps
                                last_speed_calc_time = current_time
                                bytes_at_last_speed_calc = bytes_this_chunk                            

                            # Throttle emissions globally for this file download
                            if emitter and (current_time - global_emit_time_ref[0] > 0.25): # Max ~4Hz for the whole file
                                global_emit_time_ref[0] = current_time # Update shared last emit time
                                
                                # Prepare and emit the status_list_copy
                                status_list_copy = [dict(s) for s in progress_data['chunks_status']] # Make a deep enough copy
                                if isinstance(emitter, queue.Queue):
                                    emitter.put({'type': 'file_progress', 'payload': (api_original_filename, status_list_copy)})
                                elif hasattr(emitter, 'file_progress_signal'): # PostProcessorSignals-like
                                    # Ensure we read the latest total downloaded from progress_data
                                    emitter.file_progress_signal.emit(api_original_filename, status_list_copy)
            return bytes_this_chunk, True

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, http.client.IncompleteRead) as e:
            logger_func(f"   ❌ [Chunk {part_num + 1}/{total_parts}] Retryable error: {e}")
            if attempt == MAX_CHUNK_DOWNLOAD_RETRIES:
                logger_func(f"   ❌ [Chunk {part_num + 1}/{total_parts}] Failed after {MAX_CHUNK_DOWNLOAD_RETRIES} retries.")
                return bytes_this_chunk, False
        except requests.exceptions.RequestException as e: # Includes 4xx/5xx errors after raise_for_status
            logger_func(f"   ❌ [Chunk {part_num + 1}/{total_parts}] Non-retryable error: {e}")
            return bytes_this_chunk, False
        except Exception as e:
            logger_func(f"   ❌ [Chunk {part_num + 1}/{total_parts}] Unexpected error: {e}\n{traceback.format_exc(limit=1)}")
            return bytes_this_chunk, False

    # Ensure final status is marked as inactive if loop finishes due to retries
    with progress_data['lock']:
        progress_data['chunks_status'][part_num]['active'] = False
        progress_data['chunks_status'][part_num]['speed_bps'] = 0
    return bytes_this_chunk, False # Should be unreachable


def download_file_in_parts(file_url, save_path, total_size, num_parts, headers, api_original_filename,
                           emitter_for_multipart, cancellation_event, skip_event, logger_func, pause_event): # Added pause_event
    """
    Downloads a file in multiple parts concurrently.
    Returns: (download_successful_flag, downloaded_bytes, calculated_file_hash, temp_file_handle_or_None)
    The temp_file_handle will be an open read-binary file handle to the .part file if successful, otherwise None.
    It is the responsibility of the caller to close this handle and rename/delete the .part file.
    """
    logger_func(f"⬇️ Initializing Multi-part Download ({num_parts} parts) for: '{api_original_filename}' (Size: {total_size / (1024*1024):.2f} MB)")
    temp_file_path = save_path + ".part"

    try:
        with open(temp_file_path, 'wb') as f_temp:
            if total_size > 0:
                f_temp.truncate(total_size) # Pre-allocate space
    except IOError as e:
        logger_func(f"   ❌ Error creating/truncating temp file '{temp_file_path}': {e}")
        return False, 0, None, None

    chunk_size_calc = total_size // num_parts
    chunks_ranges = []
    for i in range(num_parts):
        start = i * chunk_size_calc
        end = start + chunk_size_calc - 1 if i < num_parts - 1 else total_size - 1
        if start <= end: # Valid range
            chunks_ranges.append((start, end))
        elif total_size == 0 and i == 0: # Special case for 0-byte file
            chunks_ranges.append((0, -1)) # Indicates 0-byte file, download 0 bytes from offset 0

    chunk_actual_sizes = [] 
    for start, end in chunks_ranges:
        if end == -1 and start == 0: # 0-byte file
            chunk_actual_sizes.append(0)
        else:
            chunk_actual_sizes.append(end - start + 1)

    if not chunks_ranges and total_size > 0:
        logger_func(f"   ⚠️ No valid chunk ranges for multipart download of '{api_original_filename}'. Aborting multipart.")
        if os.path.exists(temp_file_path): os.remove(temp_file_path)
        return False, 0, None, None

    progress_data = {
        'total_file_size': total_size, # Overall file size for reference
        'total_downloaded_so_far': 0,  # New key for overall progress
        'chunks_status': [ # Status for each chunk
            {'id': i, 'downloaded': 0, 'total': chunk_actual_sizes[i] if i < len(chunk_actual_sizes) else 0, 'active': False, 'speed_bps': 0.0}
            for i in range(num_parts)
        ],
        'lock': threading.Lock(),
        'last_global_emit_time': [time.time()] # Shared mutable for global throttling timestamp
    }

    chunk_futures = []
    all_chunks_successful = True
    total_bytes_from_chunks = 0 # Still useful to verify total downloaded against file size

    with ThreadPoolExecutor(max_workers=num_parts, thread_name_prefix=f"MPChunk_{api_original_filename[:10]}_") as chunk_pool:
        for i, (start, end) in enumerate(chunks_ranges):
            if cancellation_event and cancellation_event.is_set(): all_chunks_successful = False; break
            chunk_futures.append(chunk_pool.submit(
                _download_individual_chunk, chunk_url=file_url, temp_file_path=temp_file_path,
                start_byte=start, end_byte=end, headers=headers, part_num=i, total_parts=num_parts,
                progress_data=progress_data, cancellation_event=cancellation_event, skip_event=skip_event, global_emit_time_ref=progress_data['last_global_emit_time'],
                pause_event=pause_event, logger_func=logger_func, emitter=emitter_for_multipart, # Pass pause_event and emitter
                api_original_filename=api_original_filename
            ))

        for future in as_completed(chunk_futures):
            if cancellation_event and cancellation_event.is_set(): all_chunks_successful = False; break
            bytes_downloaded_this_chunk, success_this_chunk = future.result()
            total_bytes_from_chunks += bytes_downloaded_this_chunk
            if not success_this_chunk:
                all_chunks_successful = False

    if cancellation_event and cancellation_event.is_set():
        logger_func(f"   Multi-part download for '{api_original_filename}' cancelled by main event.")
        all_chunks_successful = False

    # Ensure a final progress update is sent with all chunks marked inactive (unless still active due to error)
    if emitter_for_multipart:
        with progress_data['lock']:
            # Ensure all chunks are marked inactive for the final signal if download didn't fully succeed or was cancelled
            status_list_copy = [dict(s) for s in progress_data['chunks_status']]
            if isinstance(emitter_for_multipart, queue.Queue):
                emitter_for_multipart.put({'type': 'file_progress', 'payload': (api_original_filename, status_list_copy)})
            elif hasattr(emitter_for_multipart, 'file_progress_signal'): # PostProcessorSignals-like
                emitter_for_multipart.file_progress_signal.emit(api_original_filename, status_list_copy)

    if all_chunks_successful and (total_bytes_from_chunks == total_size or total_size == 0):
        logger_func(f"   ✅ Multi-part download successful for '{api_original_filename}'. Total bytes: {total_bytes_from_chunks}")
        md5_hasher = hashlib.md5()
        with open(temp_file_path, 'rb') as f_hash:
            for buf in iter(lambda: f_hash.read(4096*10), b''): # Read in larger buffers for hashing
                md5_hasher.update(buf)
        calculated_hash = md5_hasher.hexdigest()
        # Return an open file handle for the caller to manage (e.g., for compression)
        # The caller is responsible for closing this handle and renaming/deleting the .part file.
        return True, total_bytes_from_chunks, calculated_hash, open(temp_file_path, 'rb')
    else:
        logger_func(f"   ❌ Multi-part download failed for '{api_original_filename}'. Success: {all_chunks_successful}, Bytes: {total_bytes_from_chunks}/{total_size}. Cleaning up.")
        if os.path.exists(temp_file_path):
            try: os.remove(temp_file_path)
            except OSError as e: logger_func(f"    Failed to remove temp part file '{temp_file_path}': {e}")
        return False, total_bytes_from_chunks, None, None