from typing import List, Optional
from .base_media_server_client import MediaServerClient

class EmbyClient(MediaServerClient):
    """
    Client for interacting with the Emby server API.
    Inherits from MediaServerClient.
    """
    def get_or_create_collection(self, collection_name: str) -> Optional[str]:
        """
        Get the Emby collection ID by name, or create it if it does not exist.
        Args:
            collection_name: Name of the collection.
        Returns:
            The collection ID (str) or None if not found/created.
        """
        # Search for the collection by name
        params = {
            'IncludeItemTypes': 'BoxSet',
            'Recursive': 'true',
            'SearchTerm': collection_name,
            'Fields': 'Name'
        }
        endpoint = f"/Users/{self.user_id}/Items"
        data = self._make_api_request('GET', endpoint, params=params)
        if data and 'Items' in data:
            for item in data['Items']:
                if item.get('Name', '').lower() == collection_name.lower():
                    return item['Id']
        # Not found, create collection
        endpoint = f"/Collections"
        payload = {
            'Name': collection_name,
            'UserId': self.user_id
        }
        data = self._make_api_request('POST', endpoint, json=payload)
        if data and 'Id' in data:
            return data['Id']
        return None

    def get_library_item_ids_by_tmdb_ids(self, tmdb_ids: List[int]) -> List[str]:
        """
        Given a list of TMDb IDs, return the Emby server's internal item IDs for owned movies.
        Args:
            tmdb_ids: List of TMDb movie IDs.
        Returns:
            List of Emby item IDs (str).
        """
        item_ids = []
        for tmdb_id in tmdb_ids:
            params = {
                'Recursive': 'true',
                'IncludeItemTypes': 'Movie',
                'Filters': '',
                'AnyProviderIdEquals': f'tmdb:{tmdb_id}',
                'Fields': 'ProviderIds'
            }
            endpoint = f"/Users/{self.user_id}/Items"
            data = self._make_api_request('GET', endpoint, params=params)
            if data and 'Items' in data:
                for item in data['Items']:
                    item_ids.append(item['Id'])
        return item_ids

    def update_collection_items(self, collection_id: str, item_ids: List[str]) -> bool:
        """
        Set the items for a given Emby collection.
        Args:
            collection_id: The Emby collection ID.
            item_ids: List of Emby item IDs to include in the collection.
        Returns:
            True if successful, False otherwise.
        """
        endpoint = f"/Collections/{collection_id}/Items"
        payload = item_ids
        data = self._make_api_request('POST', endpoint, json=payload)
        if data is not None:
            return True
        return False
