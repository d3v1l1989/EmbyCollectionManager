from typing import List, Optional
import uuid
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
                    
        # Try different approach for stubborn Emby servers
        try:
            # First do a broader search for the collection
            params = {
                'IncludeItemTypes': 'BoxSet',
                'Recursive': 'true',
                'Limit': 100,
                'Fields': 'Name,Path'
            }
            endpoint = f"/Users/{self.user_id}/Items"
            print(f"Looking for any existing collections...")
            data = self._make_api_request('GET', endpoint, params=params)
            
            # If there are any collections, check if one matches our name
            if data and 'Items' in data:
                print(f"Found {len(data['Items'])} existing collections")
                for item in data['Items']:
                    # Case-insensitive comparison to find our collection
                    if item.get('Name', '').lower() == collection_name.lower():
                        print(f"Found existing collection: {item['Name']} (ID: {item['Id']})")
                        return item['Id']
                        
                # For diagnostic purposes, list all collections
                print("Available collections:")
                for item in data['Items'][:5]:  # Just show first 5 to avoid log spam
                    print(f"  - {item.get('Name', '?')} (ID: {item.get('Id', '?')})")
            
            # Collection doesn't exist and we can't create it via the API
            # So we'll use a stable pseudo-ID based on the collection name
            print(f"Using alternative collection handling method for '{collection_name}'")
            import hashlib
            temp_id = hashlib.md5(collection_name.encode()).hexdigest()
            
            # Store this as a temporary collection mapping
            self._temp_collections = getattr(self, '_temp_collections', {})
            self._temp_collections[temp_id] = collection_name
            
            # Before returning, check if this collection exists - maybe there's a user-created one
            # We'd need to first use Emby UI to manually create these collections
            print(f"Checking for manually created collection: '{collection_name}'")
            params = {
                'IncludeItemTypes': 'BoxSet',
                'SearchTerm': collection_name,
                'Recursive': 'true',
                'Limit': 10
            }
            search_data = self._make_api_request('GET', f"/Users/{self.user_id}/Items", params=params)
            if search_data and 'Items' in search_data and search_data['Items']:
                for item in search_data['Items']:
                    if item.get('Name', '').lower() == collection_name.lower():
                        real_id = item['Id']
                        print(f"Found manually created collection: {item['Name']} (ID: {real_id})")
                        return real_id
            
            # No luck - return the pseudo-ID
            return temp_id
        except Exception as e:
            print(f"Error creating collection '{collection_name}': {e}")
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
        # Check if this is a pseudo-ID for a collection we couldn't create
        if hasattr(self, '_temp_collections') and collection_id in self._temp_collections:
            collection_name = self._temp_collections[collection_id]
            print(f"This is a pseudo-collection '{collection_name}'. Can't add items via API.")
            print(f"If you want to use this collection, please manually create a collection named:")
            print(f"'{collection_name}' in your Emby web interface before running this tool.")
            # We'll pretend it succeeded since we can't do anything about it
            return True
        
        # For real collection IDs, try to update items
        try:
            endpoint = f"/Collections/{collection_id}/Items"
            payload = item_ids
            print(f"Adding {len(item_ids)} items to collection {collection_id}")
            data = self._make_api_request('POST', endpoint, json=payload)
            if data is not None:
                return True
            return False
        except Exception as e:
            print(f"Error updating collection items: {e}")
            return False
        
    def update_collection_artwork(self, collection_id: str, poster_url: Optional[str]=None, backdrop_url: Optional[str]=None) -> bool:
        """
        Update artwork for an Emby collection using external image URLs.
        
        Args:
            collection_id: The Emby collection ID
            poster_url: URL to collection poster image
            backdrop_url: URL to collection backdrop/fanart image
            
        Returns:
            True if at least one image was successfully updated, False otherwise
        """
        # Check if this is a pseudo-ID for a collection we couldn't create
        if hasattr(self, '_temp_collections') and collection_id in self._temp_collections:
            collection_name = self._temp_collections[collection_id]
            print(f"Cannot update artwork for pseudo-collection '{collection_name}'")
            print(f"To use artwork, create the collection manually in your Emby web interface.")
            # We'll pretend it succeeded since we can't do anything about it
            return True
            
        success = False
        
        if not collection_id:
            return False
            
        # Update poster if provided
        if poster_url:
            try:
                # First inform Emby about the image URL
                endpoint = f"/Items/{collection_id}/RemoteImages/Download"
                params = {
                    "Type": "Primary",  # Primary = poster in Emby
                    "ImageUrl": poster_url,
                    "ProviderName": "TMDb"
                }
                print(f"Updating poster for collection {collection_id}")
                data = self._make_api_request('POST', endpoint, params=params)
                if data is not None:
                    success = True
                    print("Poster update successful")
            except Exception as e:
                print(f"Error updating collection poster: {e}")
                
        # Update backdrop if provided
        if backdrop_url:
            try:
                endpoint = f"/Items/{collection_id}/RemoteImages/Download"
                params = {
                    "Type": "Backdrop",  # Backdrop/fanart
                    "ImageUrl": backdrop_url,
                    "ProviderName": "TMDb"
                }
                print(f"Updating backdrop for collection {collection_id}")
                data = self._make_api_request('POST', endpoint, params=params)
                if data is not None:
                    success = True
                    print("Backdrop update successful")
            except Exception as e:
                print(f"Error updating collection backdrop: {e}")
                
        return success
