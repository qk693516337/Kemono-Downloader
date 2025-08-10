import time
import requests
import json
from urllib.parse import urlparse

def fetch_server_channels(server_id, logger, cookies=None, cancellation_event=None, pause_event=None):
    """
    Fetches the list of channels for a given Discord server ID from the Kemono API.
    UPDATED to be pausable and cancellable.
    """
    domains_to_try = ["kemono.cr", "kemono.su"]
    for domain in domains_to_try:
        if cancellation_event and cancellation_event.is_set():
            logger("   Channel fetching cancelled by user.")
            return None
        while pause_event and pause_event.is_set():
            if cancellation_event and cancellation_event.is_set(): break
            time.sleep(0.5)

        lookup_url = f"https://{domain}/api/v1/discord/channel/lookup/{server_id}"
        logger(f"   Attempting to fetch channel list from: {lookup_url}")
        try:
            response = requests.get(lookup_url, cookies=cookies, timeout=15)
            response.raise_for_status()
            channels = response.json()
            if isinstance(channels, list):
                logger(f"   ✅ Found {len(channels)} channels for server {server_id}.")
                return channels
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            # This is a silent failure, we'll just try the next domain
            pass
            
    logger(f"   ❌ Failed to fetch channel list for server {server_id} from all available domains.")
    return None

def fetch_channel_messages(channel_id, logger, cancellation_event, pause_event, cookies=None):
    """
    Fetches all messages from a Discord channel by looping through API pages (pagination).
    Uses a page size of 150 and handles the specific offset logic.
    """
    offset = 0
    page_size = 150 # Corrected page size based on your findings
    api_base_url = f"https://kemono.cr/api/v1/discord/channel/{channel_id}"
    
    while not (cancellation_event and cancellation_event.is_set()):
        if pause_event and pause_event.is_set():
            logger("   Message fetching paused...")
            while pause_event.is_set():
                if cancellation_event and cancellation_event.is_set(): break
                time.sleep(0.5)
            logger("   Message fetching resumed.")

        if cancellation_event and cancellation_event.is_set():
            break
            
        paginated_url = f"{api_base_url}?o={offset}"
        logger(f"   Fetching messages from API: page starting at offset {offset}")

        try:
            response = requests.get(paginated_url, cookies=cookies, timeout=20)
            response.raise_for_status()
            messages_batch = response.json()

            if not messages_batch:
                logger(f"   ✅ Reached end of messages for channel {channel_id}.")
                break
            
            logger(f"   Fetched {len(messages_batch)} messages...")
            yield messages_batch

            if len(messages_batch) < page_size:
                logger(f"   ✅ Last page of messages received for channel {channel_id}.")
                break

            offset += page_size
            time.sleep(0.5)

        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logger(f"   ❌ Error fetching messages at offset {offset}: {e}")
            break