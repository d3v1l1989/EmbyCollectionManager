import requests
from typing import List, Optional

class MediaServerClient:
    """
    Base class for media server clients (Emby, Jellyfin).
    Provides shared request logic and interface.
    """
    def __init__(self, server_url: str, api_key: str, user_id: str):
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.user_id = user_id
        self.session = requests.Session()
        self.session.headers.update({
            'X-Emby-Token': self.api_key,
            'Accept': 'application/json'
        })

    def _make_api_request(self, method: str, endpoint: str, **kwargs):
        """
        Helper for making API requests with error handling.
        """
        url = f"{self.server_url}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=15, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None

    def get_or_create_collection(self, collection_name: str) -> Optional[str]:
        raise NotImplementedError

    def get_library_item_ids_by_tmdb_ids(self, tmdb_ids: List[int]) -> List[str]:
        raise NotImplementedError

    def update_collection_items(self, collection_id: str, item_ids: List[str]) -> bool:
        raise NotImplementedError
