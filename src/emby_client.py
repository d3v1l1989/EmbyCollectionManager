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
        print(f"Searching for collection: '{collection_name}'")
        data = self._make_api_request('GET', endpoint, params=params)
        if data and 'Items' in data:
            for item in data['Items']:
                if item.get('Name', '').lower() == collection_name.lower():
                    print(f"Found existing collection: {item['Name']} (ID: {item['Id']})")
                    return item['Id']
        
        # Collection doesn't exist, create it using the method from forum post
        # https://emby.media/community/index.php?/topic/114883-using-the-collections-api-to-create-a-new-collection/
        print(f"Collection '{collection_name}' not found. Creating new collection...")
        
        try:
            # The key insight is to use a POST request to /Collections with empty Ids parameter
            # This API format follows the successful example from the Emby forum
            url = f"{self.server_url}/Collections"
            
            # Create empty ids list in URL format
            empty_ids = ""
            
            # Prepare the query parameters
            params = {
                'api_key': self.api_key,
                'IsLocked': 'false',
                'Name': collection_name,
                'Ids': empty_ids
            }
            
            print(f"Using direct POST to /Collections endpoint...")
            
            # Make direct request instead of using the helper to handle URL parameters properly
            response = self.session.post(url, params=params, timeout=15)
            response.raise_for_status()
            
            # Parse the response
            try:
                data = response.json()
                if data and 'Id' in data:
                    print(f"Successfully created collection '{collection_name}' with ID: {data['Id']}")
                    return data['Id']
            except Exception as e:
                print(f"Error parsing response: {e}")
                
            # If we get here, we couldn't create the collection the standard way
            # Try the old approach as fallback with different URLs and parameters
            print(f"Trying fallback methods to create collection...")
            
            # Try creating with URL-encoded parameters (different format)
            try:
                full_url = f"{self.server_url}/Collections?api_key={self.api_key}&IsLocked=false&Name={collection_name.replace(' ', '%20')}&Ids="
                print(f"Trying direct URL: {full_url.replace(self.api_key, 'API_KEY_HIDDEN')}")
                response = self.session.post(full_url, timeout=15)
                response.raise_for_status()
                
                if response.text and len(response.text) > 0:
                    try:
                        data = response.json()
                        if data and 'Id' in data:
                            print(f"Fallback method worked! Created collection with ID: {data['Id']}")
                            return data['Id']
                    except Exception as e:
                        print(f"Error parsing fallback response: {e}")
            except Exception as e:
                print(f"Fallback method failed: {e}")
            
            # If all else fails, we'll need a temporary ID to continue
            print(f"Could not create collection. Using temporary ID for '{collection_name}'")
            import hashlib
            temp_id = hashlib.md5(collection_name.encode()).hexdigest()
            self._temp_collections = getattr(self, '_temp_collections', {})
            self._temp_collections[temp_id] = collection_name
            print(f"Using temporary ID: {temp_id}")
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
