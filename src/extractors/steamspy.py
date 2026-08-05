import requests
from typing import Optional, Dict, Any
from src.config import DEFAULT_TIMEOUT

def fetch_steamspy_page(page=0) -> Optional[Dict[str, Any]]:
    """Fetches a batch of game data from the SteamSpy API."""
    url = f"https://steamspy.com/api.php?request=all&page={page}"
    print(f"Requesting payload metadata from SteamSpy Page {page}...")
    try:
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        print(f"Unexpected status code received: {response.status_code}")
        return None
    except Exception as e:
        # Log network issues without stopping the program entirely
        print(f"Network request exception occurred: {e}")
        return None