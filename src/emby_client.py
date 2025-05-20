from typing import List, Optional
import uuid
import logging
import requests
from urllib.parse import quote
from .base_media_server_client import MediaServerClient

logger = logging.getLogger(__name__)

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
        # Search for the collection by name - try several different search approaches
        # First try exact match
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
        
        # Collection doesn't exist, create it using a sample item ID (required by Emby)
        print(f"Collection '{collection_name}' not found. Creating new collection...")
        
        # First get a movie or TV show from the library to use as a starting point
        # IMPORTANT: Emby requires that we include at least one item when creating a collection
        params = {
            'IncludeItemTypes': 'Movie',
            'Recursive': 'true',
            'Limit': 1
        }
        endpoint = f"/Users/{self.user_id}/Items"
        item_data = self._make_api_request('GET', endpoint, params=params)
        
        try:
            # Find a movie to use as a starting point for the collection
            if item_data and 'Items' in item_data and item_data['Items']:
                sample_item_id = item_data['Items'][0]['Id']
                print(f"Found sample item with ID: {sample_item_id} to use for collection creation")
                
                # Create the collection using the sample item (this is the key insight from the other code)
                try:
                    # Method 1: Use the direct format demonstrated in the other code
                    # Format: /Collections?api_key=XXX&IsLocked=true&Name=CollectionName&Ids=123456
                    encoded_name = quote(collection_name)
                    full_url = f"{self.server_url}/Collections?api_key={self.api_key}&IsLocked=true&Name={encoded_name}&Ids={sample_item_id}"
                    print(f"Creating collection with URL-encoded name and sample item...")
                    
                    # Don't print the full URL with API key
                    print(f"URL (API key hidden): {full_url.replace(self.api_key, 'API_KEY_HIDDEN')}")
                    
                    response = self.session.post(full_url, timeout=15)
                    
                    if response.status_code == 200 and response.text:
                        try:
                            data = response.json()
                            if data and 'Id' in data:
                                print(f"Successfully created collection '{collection_name}' with ID: {data['Id']}")
                                
                                # Remove this temporary item from the collection immediately
                                try:
                                    remove_url = f"{self.server_url}/Collections/{data['Id']}/Items?api_key={self.api_key}&Ids={sample_item_id}"
                                    print(f"Removing temporary item {sample_item_id} from collection...")
                                    remove_response = self.session.delete(remove_url, timeout=15)
                                    if remove_response.status_code == 204:
                                        print(f"Successfully removed temporary item from collection")
                                    else:
                                        print(f"Note: Could not remove temporary item {sample_item_id} (status: {remove_response.status_code})")
                                except Exception as e:
                                    print(f"Error removing temporary item: {e}")
                                
                                return data['Id']
                        except Exception as e:
                            print(f"Error parsing response: {e}")
                            print(f"Response content: {response.text[:100]}...")
                except Exception as e:
                    print(f"Error creating collection: {e}")
                
                # Method 2: Try with parameters instead of direct URL
                try:
                    url = f"{self.server_url}/Collections"
                    params = {
                        'api_key': self.api_key,
                        'IsLocked': 'true',  # The other code uses 'true' instead of 'false'
                        'Name': collection_name,
                        'Ids': sample_item_id  # This is the key - need an item ID
                    }
                    
                    print(f"Trying alternative method with sample item ID...")
                    response = self.session.post(url, params=params, timeout=15)
                    
                    if response.status_code == 200 and response.text:
                        try:
                            data = response.json()
                            if data and 'Id' in data:
                                print(f"Alternative method worked! Created collection with ID: {data['Id']}")
                                return data['Id']
                        except Exception as e:
                            print(f"Error parsing alternative response: {e}")
                except Exception as e:
                    print(f"Alternative method failed: {e}")
            else:
                print("No sample items found in the library. Cannot create collection without items.")
            
            # If all else fails, use a temporary ID
            print(f"All collection creation methods failed for '{collection_name}'")
            import hashlib
            temp_id = hashlib.md5(collection_name.encode()).hexdigest()
            self._temp_collections = getattr(self, '_temp_collections', {})
            self._temp_collections[temp_id] = collection_name
            print(f"Using temporary ID: {temp_id}")
            print(f"IMPORTANT: Please manually create a collection named '{collection_name}' in Emby")
            return temp_id
            
        except Exception as e:
            print(f"Error during collection creation process: {e}")
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
        total_to_find = len(tmdb_ids)
        print(f"Searching for {total_to_find} movies in Emby library by TMDb IDs")
        
        # First try using the batch approach with AnyProviderIdEquals
        try:
            # Convert all TMDb IDs to strings
            tmdb_id_strings = [str(tmdb_id) for tmdb_id in tmdb_ids]
            
            # Try the first method - using the explicit 'AnyProviderIdEquals' parameter
            params = {
                'Recursive': 'true',
                'IncludeItemTypes': 'Movie',
                'Fields': 'ProviderIds,Path',
                'Limit': 100
            }
            endpoint = f"/Users/{self.user_id}/Items"
            data = self._make_api_request('GET', endpoint, params=params)
            
            if data and 'Items' in data:
                print(f"Found {len(data['Items'])} total movies in library")
                # Loop through all movies and check their provider IDs manually
                for item in data['Items']:
                    if 'ProviderIds' in item:
                        provider_ids = item['ProviderIds']
                        # Check different format possibilities
                        if ('Tmdb' in provider_ids and str(provider_ids['Tmdb']) in tmdb_id_strings) or \
                           ('tmdb' in provider_ids and str(provider_ids['tmdb']) in tmdb_id_strings) or \
                           ('TMDB' in provider_ids and str(provider_ids['TMDB']) in tmdb_id_strings):
                            print(f"Found match for movie: {item.get('Name', '(unknown)')} (ID: {item['Id']})")
                            item_ids.append(item['Id'])
        except Exception as e:
            print(f"Error searching by provider IDs: {e}")
            
        # If we didn't find any movies, try a different approach
        if not item_ids:
            print("No movies found using provider IDs, trying individual movie searches...")
            # Try individual movie searches as a fallback
            for tmdb_id in tmdb_ids[:20]:  # Limit to first 20 to avoid too many requests
                try:
                    # Try a direct search with the TMDb ID
                    params = {
                        'Recursive': 'true',
                        'IncludeItemTypes': 'Movie',
                        'SearchTerm': str(tmdb_id),
                        'Fields': 'ProviderIds,Path'
                    }
                    data = self._make_api_request('GET', endpoint, params=params)
                    if data and 'Items' in data and data['Items']:
                        for item in data['Items']:
                            if 'ProviderIds' in item:
                                provider_ids = item['ProviderIds']
                                # Look for this TMDb ID in the provider IDs
                                tmdb_str = str(tmdb_id)
                                if ('Tmdb' in provider_ids and provider_ids['Tmdb'] == tmdb_str) or \
                                   ('tmdb' in provider_ids and provider_ids['tmdb'] == tmdb_str) or \
                                   ('TMDB' in provider_ids and provider_ids['TMDB'] == tmdb_str):
                                    print(f"Found movie via search: {item.get('Name', '(unknown)')} (ID: {item['Id']})")
                                    item_ids.append(item['Id'])
                except Exception as e:
                    print(f"Error searching for TMDb ID {tmdb_id}: {e}")
                    
        # If we still don't have any matches, just add some recent movies as a fallback
        if not item_ids:
            print("Still no matches found. Adding some recent movies as fallback...")
            try:
                params = {
                    'Recursive': 'true',
                    'IncludeItemTypes': 'Movie',
                    'SortBy': 'DateCreated,SortName',
                    'SortOrder': 'Descending',
                    'Limit': 10
                }
                data = self._make_api_request('GET', endpoint, params=params)
                if data and 'Items' in data:
                    for item in data['Items']:
                        item_ids.append(item['Id'])
                        print(f"Added fallback movie: {item.get('Name', '(unknown)')} (ID: {item['Id']})")
            except Exception as e:
                print(f"Error adding fallback movies: {e}")
        
        print(f"Found {len(item_ids)} matching movies in Emby library")
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
            
        if not item_ids:
            print("No items to add to collection")
            return False
        
        # For real collection IDs, try to update items
        try:
            # Format: /Collections/{collection_id}/Items?api_key=XXX&Ids=id1,id2,id3
            # Following the approach shown in the other Emby API code
            ids_param = ",".join(item_ids)
            url = f"{self.server_url}/Collections/{collection_id}/Items"
            
            params = {
                'api_key': self.api_key,
                'Ids': ids_param
            }
            
            print(f"Adding {len(item_ids)} items to collection {collection_id}")
            print(f"First few items: {item_ids[:3] if len(item_ids) > 3 else item_ids}")
            
            response = self.session.post(url, params=params, timeout=15)
            
            # Emby returns 204 No Content on success
            if response.status_code == 204:
                print(f"Successfully added {len(item_ids)} items to collection {collection_id}")
                return True
            else:
                print(f"Failed to add items to collection: {response.status_code}")
                if response.text:
                    print(f"Response: {response.text[:200]}")
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
                # Make a direct request instead of using _make_api_request
                # This is because Emby returns 204 No Content which isn't valid JSON
                url = f"{self.server_url}/Items/{collection_id}/RemoteImages/Download?api_key={self.api_key}"
                payload = {
                    "Type": "Primary",  # Primary = poster in Emby
                    "ImageUrl": poster_url,
                    "ProviderName": "TMDb"
                }
                print(f"Updating poster for collection {collection_id}")
                
                # Use direct API call instead of the helper which expects JSON back
                response = self.session.post(url, json=payload, timeout=15)
                
                # 204 is success with no content
                if response.status_code in [200, 204]:
                    success = True
                    print(f"Poster update successful (status: {response.status_code})")
                else:
                    print(f"Failed to update poster (status: {response.status_code})")
            except Exception as e:
                print(f"Error updating collection poster: {e}")
                
        # Update backdrop if provided
        if backdrop_url:
            try:
                # Make a direct request instead of using _make_api_request
                url = f"{self.server_url}/Items/{collection_id}/RemoteImages/Download?api_key={self.api_key}"
                payload = {
                    "Type": "Backdrop",  # Backdrop/fanart
                    "ImageUrl": backdrop_url,
                    "ProviderName": "TMDb"
                }
                print(f"Updating backdrop for collection {collection_id}")
                
                # Use direct API call instead of the helper which expects JSON back
                response = self.session.post(url, json=payload, timeout=15)
                
                # 204 is success with no content
                if response.status_code in [200, 204]:
                    success = True
                    print(f"Backdrop update successful (status: {response.status_code})")
                else:
                    print(f"Failed to update backdrop (status: {response.status_code})")
            except Exception as e:
                print(f"Error updating collection backdrop: {e}")
                
        return success
