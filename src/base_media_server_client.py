import requests
from typing import List, Optional

class MediaServerClient:
    """
    Base class for media server clients (Emby, Jellyfin).
    Provides shared request logic and interface.
    """
    def __init__(self, server_url: str, api_key: str, user_id: str, config=None):
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.user_id = user_id
        self.config = config
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
        except requests.exceptions.JSONDecodeError as e:
            print(f"API response is not valid JSON: {e}")
            print(f"Response text: {response.text[:200]}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"API request failed with HTTP error: {e}")
            print(f"Request URL: {url}")
            print(f"Request method: {method}")
            print(f"Request params: {kwargs.get('params')}")
            print(f"Request JSON: {kwargs.get('json')}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text[:200]}")
            return None
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None

    def get_or_create_collection(self, collection_name: str) -> Optional[str]:
        raise NotImplementedError

    def get_library_item_ids_by_tmdb_ids(self, tmdb_ids: List[int]) -> List[str]:
        raise NotImplementedError

    def update_collection_items(self, collection_id: str, item_ids: List[str]) -> bool:
        raise NotImplementedError
        
    def update_collection_artwork(self, collection_id: str, poster_url: Optional[str]=None, backdrop_url: Optional[str]=None) -> bool:
        """
        Update artwork for a collection.
        
        Args:
            collection_id: Media server collection ID
            poster_url: URL to collection poster image
            backdrop_url: URL to collection backdrop/fanart image
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError
