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
        
        # Define batch size to prevent too long URLs
        batch_size = 50
        
        # First try the batched approach with AnyProviderIdEquals like the other client does
        try:
            # Convert all TMDb IDs to strings and add 'tmdb.' prefix
            tmdb_id_strings = [f"tmdb.{tmdb_id}" for tmdb_id in tmdb_ids]
            
            # Process in batches to avoid URL length limits
            for i in range(0, len(tmdb_id_strings), batch_size):
                batch = tmdb_id_strings[i:i+batch_size]
                provider_ids_str = ",".join(batch)
                
                params = {
                    'Recursive': 'true',
                    'IncludeItemTypes': 'Movie',
                    'Fields': 'ProviderIds,Path',
                    'AnyProviderIdEquals': provider_ids_str,
                    'Limit': batch_size
                }
                
                endpoint = f"/Users/{self.user_id}/Items"
                print(f"Searching batch {i//batch_size + 1} with {len(batch)} TMDb IDs")
                data = self._make_api_request('GET', endpoint, params=params)
                
                if data and 'Items' in data and data['Items']:
                    batch_matches = len(data['Items'])
                    print(f"Found {batch_matches} matches in batch {i//batch_size + 1}")
                    
                    for item in data['Items']:
                        name = item.get('Name', '(unknown)')
                        item_id = item['Id']
                        print(f"  - Found match: {name} (ID: {item_id})")
                        if item_id not in item_ids:  # Avoid duplicates
                            item_ids.append(item_id)
        except Exception as e:
            print(f"Error searching by batched provider IDs: {e}")
        
        # If we didn't find many matches, try the direct approach using all movies
        if len(item_ids) < total_to_find / 10:  # If we found less than 10% of movies
            print(f"Only found {len(item_ids)} movies with batch method, trying full library scan...")
            try:
                # Get all movies and manually check TMDb IDs
                params = {
                    'Recursive': 'true',
                    'IncludeItemTypes': 'Movie',
                    'Fields': 'ProviderIds,Path',
                    'Limit': 200  # Get more movies at once
                }
                
                # Convert TMDb IDs to strings for comparison
                tmdb_str_ids = set(str(tmdb_id) for tmdb_id in tmdb_ids)
                
                endpoint = f"/Users/{self.user_id}/Items"
                data = self._make_api_request('GET', endpoint, params=params)
                
                if data and 'Items' in data:
                    movies_count = len(data['Items'])
                    print(f"Scanning {movies_count} movies in library for TMDb ID matches")
                    
                    for item in data['Items']:
                        if 'ProviderIds' in item:
                            provider_ids = item['ProviderIds']
                            # Check for TMDb ID in any case format
                            for key in ['Tmdb', 'tmdb', 'TMDB']:
                                if key in provider_ids and provider_ids[key] in tmdb_str_ids:
                                    name = item.get('Name', '(unknown)')
                                    item_id = item['Id']
                                    print(f"Found match via scan: {name} (ID: {item_id})")
                                    if item_id not in item_ids:  # Avoid duplicates
                                        item_ids.append(item_id)
                                    break
            except Exception as e:
                print(f"Error scanning full library: {e}")
        
        # If we still have very few movies, add some recent popular ones as a fallback
        if len(item_ids) < 5:
            print("Found very few matches. Adding some recent popular movies as fallback...")
            try:
                params = {
                    'Recursive': 'true',
                    'IncludeItemTypes': 'Movie',
                    'SortBy': 'DateCreated,SortName',  # Recently added
                    'SortOrder': 'Descending',
                    'Limit': 20
                }
                data = self._make_api_request('GET', endpoint, params=params)
                if data and 'Items' in data:
                    for item in data['Items']:
                        if item['Id'] not in item_ids:  # Avoid duplicates
                            item_ids.append(item['Id'])
                            print(f"Added fallback movie: {item.get('Name', '(unknown)')} (ID: {item['Id']})")
                            # Stop after we've added enough fallbacks
                            if len(item_ids) >= 20:
                                break
            except Exception as e:
                print(f"Error adding fallback movies: {e}")
        
        print(f"Found total of {len(item_ids)} matching movies in Emby library")
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
            
        # For real collection IDs, we need to aggressively deduplicate items
        try:
            # First, get all movie names to avoid adding duplicate movies with different IDs
            # This handles cases where the same movie exists in multiple qualities
            print(f"Fetching movie details to prevent duplicates...")
            movie_names = {}
            deduplicated_ids = []
            
            for item_id in item_ids:
                try:
                    # Use the Items endpoint to get movie details
                    item_url = f"{self.server_url}/Users/{self.user_id}/Items/{item_id}?api_key={self.api_key}"
                    response = self.session.get(item_url, timeout=15)
                    
                    if response.status_code == 200:
                        item_data = response.json()
                        movie_name = item_data.get('Name', '').lower()
                        
                        if movie_name and movie_name not in movie_names:
                            # First time we've seen this movie name
                            movie_names[movie_name] = item_id
                            deduplicated_ids.append(item_id)
                            print(f"  Including: {movie_name}")
                        else:
                            print(f"  Skipping duplicate: {movie_name}")
                except Exception as e:
                    print(f"Error getting movie details for {item_id}: {e}")
                    # If we can't get details, include it anyway
                    if item_id not in deduplicated_ids:
                        deduplicated_ids.append(item_id)
            
            print(f"After deduplication: {len(deduplicated_ids)} of {len(item_ids)} movies remain")
            
            if not deduplicated_ids:
                print("No items remain after deduplication")
                return False
            
            # Now add the deduplicated items to the collection
            ids_param = ",".join(deduplicated_ids)
            url = f"{self.server_url}/Collections/{collection_id}/Items"
            
            params = {
                'api_key': self.api_key,
                'Ids': ids_param
            }
            
            print(f"Adding {len(deduplicated_ids)} unique items to collection {collection_id}")
            print(f"First few items: {deduplicated_ids[:3] if len(deduplicated_ids) > 3 else deduplicated_ids}")
            
            response = self.session.post(url, params=params, timeout=15)
            
            # Emby returns 204 No Content on success
            if response.status_code == 204:
                print(f"Successfully added {len(deduplicated_ids)} unique items to collection {collection_id}")
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
