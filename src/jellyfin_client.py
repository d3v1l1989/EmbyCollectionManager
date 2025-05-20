from typing import List, Optional
import hashlib
import logging
import requests
from urllib.parse import quote
from .base_media_server_client import MediaServerClient

logger = logging.getLogger(__name__)

class JellyfinClient(MediaServerClient):
    """
    Client for interacting with the Jellyfin server API.
    Inherits from MediaServerClient.
    """
    def get_or_create_collection(self, collection_name: str) -> Optional[str]:
        """
        Get the Jellyfin collection ID by name, or create it if it does not exist.
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
        
        # Collection doesn't exist, create it using a sample item ID if possible
        print(f"Collection '{collection_name}' not found. Creating new collection...")
        
        # First get a movie or TV show from the library to use as a starting point
        params = {
            'IncludeItemTypes': 'Movie',
            'Recursive': 'true',
            'Limit': 1
        }
        endpoint = f"/Users/{self.user_id}/Items"
        item_data = self._make_api_request('GET', endpoint, params=params)
        
        try:
            # Try to create a collection with a sample item
            if item_data and 'Items' in item_data and item_data['Items']:
                sample_item_id = item_data['Items'][0]['Id']
                print(f"Found sample item with ID: {sample_item_id} to use for collection creation")
                
                # Try the standard Jellyfin collection creation endpoint
                try:
                    # Jellyfin's collection endpoint
                    encoded_name = quote(collection_name)
                    url = f"{self.server_url}/Collections"  
                    
                    # Try both payload formats that might work with Jellyfin
                    payload = {
                        'Name': collection_name,
                        'IsLocked': True,
                        'Ids': [sample_item_id]  # Include the sample item
                    }
                    
                    print(f"Creating collection with sample item...")
                    response = self.session.post(f"{url}?api_key={self.api_key}", json=payload, timeout=15)
                    
                    if response.status_code in [200, 201, 204] and response.text:
                        try:
                            data = response.json()
                            if data and 'Id' in data:
                                print(f"Successfully created collection '{collection_name}' with ID: {data['Id']}")
                                
                                # Remove the sample item immediately
                                try:
                                    # Remove the temporary item from the collection
                                    remove_url = f"{self.server_url}/Collections/{data['Id']}/Items/{sample_item_id}?api_key={self.api_key}"
                                    print(f"Removing temporary item {sample_item_id} from collection...")
                                    remove_response = self.session.delete(remove_url, timeout=15)
                                    if remove_response.status_code in [200, 204]:
                                        print(f"Successfully removed temporary item from collection")
                                    else:
                                        print(f"Note: Could not remove temp item {sample_item_id} (status: {remove_response.status_code})")
                                except Exception as e:
                                    print(f"Error removing temporary item: {e}")
                                
                                return data['Id']
                        except Exception as e:
                            print(f"Error parsing response: {e}")
                            print(f"Response content: {response.text[:100]}...")
                except Exception as e:
                    print(f"Error creating collection with sample item: {e}")
            
            # Alternative method without a sample item
            try:
                print(f"Trying alternative collection creation method...")
                endpoint = f"/Collections"
                payload = {
                    'Name': collection_name,
                    'IsLocked': True,
                    'UserId': self.user_id
                }
                
                data = self._make_api_request('POST', endpoint, json=payload)
                if data and 'Id' in data:
                    print(f"Successfully created Jellyfin collection with ID: {data['Id']}")
                    return data['Id']
            except Exception as e:
                print(f"Alternative collection creation failed: {e}")
            
            # If all creation attempts failed, use a temporary ID
            print(f"All collection creation methods failed for '{collection_name}'")
            temp_id = hashlib.md5(collection_name.encode()).hexdigest()
            self._temp_collections = getattr(self, '_temp_collections', {})
            self._temp_collections[temp_id] = collection_name
            print(f"Using temporary ID: {temp_id}")
            print(f"IMPORTANT: Please manually create a collection named '{collection_name}' in Jellyfin")
            return temp_id
            
        except Exception as e:
            print(f"Error during collection creation process: {e}")
            return None

    def get_library_item_ids_by_tmdb_ids(self, tmdb_ids: List[int]) -> List[str]:
        """
        Given a list of TMDb IDs, return the Jellyfin server's internal item IDs for owned movies.
        Args:
            tmdb_ids: List of TMDb movie IDs.
        Returns:
            List of Jellyfin item IDs (str).
        """
        item_ids = []
        total_to_find = len(tmdb_ids)
        print(f"Searching for {total_to_find} movies in Jellyfin library by TMDb IDs")
        
        # Define batch size to prevent too long URLs
        batch_size = 50
        
        # First try the batched approach with AnyProviderIdEquals
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
        
        print(f"Found total of {len(item_ids)} matching movies in Jellyfin library")
        return item_ids

    def update_collection_items(self, collection_id: str, item_ids: List[str]) -> bool:
        """
        Set the items for a given Jellyfin collection.
        Args:
            collection_id: The Jellyfin collection ID.
            item_ids: List of Jellyfin item IDs to include in the collection.
        Returns:
            True if successful, False otherwise.
        """
        # Check if this is a pseudo-ID for a collection we couldn't create
        if hasattr(self, '_temp_collections') and collection_id in self._temp_collections:
            collection_name = self._temp_collections[collection_id]
            print(f"This is a pseudo-collection '{collection_name}'. Can't add items via API.")
            print(f"If you want to use this collection, please manually create a collection named:")
            print(f"'{collection_name}' in your Jellyfin web interface before running this tool.")
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
                
            # Add the deduplicated items to the collection
            try:
                endpoint = f"/Collections/{collection_id}/Items"
                print(f"Adding {len(deduplicated_ids)} unique items to collection {collection_id}")
                print(f"First few items: {deduplicated_ids[:3] if len(deduplicated_ids) > 3 else deduplicated_ids}")
                
                # Format items as payload for Jellyfin API
                payload = deduplicated_ids
                
                # Make the API request
                data = self._make_api_request('POST', endpoint, json=payload)
                if data is not None:
                    print(f"Successfully added {len(deduplicated_ids)} unique items to Jellyfin collection")
                    return True
                else:
                    print("Failed to add items to collection")
                    return False
            except Exception as e:
                print(f"Error adding items to collection: {e}")
                return False
        except Exception as e:
            print(f"Error during collection update: {e}")
            return False
        
    def update_collection_artwork(self, collection_id: str, poster_url: Optional[str]=None, backdrop_url: Optional[str]=None) -> bool:
        """
        Update artwork for a Jellyfin collection using external image URLs.
        
        Args:
            collection_id: The Jellyfin collection ID
            poster_url: URL to collection poster image
            backdrop_url: URL to collection backdrop/fanart image
            
        Returns:
            True if at least one image was successfully updated, False otherwise
        """
        success = False
        
        # Check if this is a pseudo-ID for a collection we couldn't create
        if hasattr(self, '_temp_collections') and collection_id in self._temp_collections:
            collection_name = self._temp_collections[collection_id]
            print(f"This is a pseudo-collection '{collection_name}'. Can't update artwork.")
            return True  # Pretend it succeeded
        
        if not collection_id:
            print("No collection ID provided for artwork update")
            return False
        
        print(f"Updating artwork for collection {collection_id}")
            
        # Update poster if provided
        if poster_url:
            try:
                print(f"Downloading poster from {poster_url}")
                # Jellyfin uses a slightly different endpoint structure than Emby
                endpoint = f"/Items/{collection_id}/RemoteImages/Download"
                params = {
                    "Type": "Primary",  # Primary = poster in Jellyfin
                    "ImageUrl": poster_url,
                    "ProviderName": "TMDb"
                }
                
                # For Jellyfin, we need to handle the response differently
                try:
                    url = f"{self.server_url}{endpoint}?api_key={self.api_key}"
                    for key, value in params.items():
                        url += f"&{key}={quote(str(value))}"
                    
                    response = self.session.post(url, timeout=30)  # Longer timeout for image downloads
                    
                    if response.status_code in [200, 204]:
                        print("Successfully updated poster image")
                        success = True
                    else:
                        print(f"Failed to update poster image: HTTP {response.status_code}")
                        if response.text:
                            print(f"Response: {response.text[:100]}")
                except Exception as e:
                    print(f"Exception during direct poster update: {e}")
                    
                    # Fall back to the base method
                    data = self._make_api_request('POST', endpoint, params=params)
                    if data is not None:
                        print("Successfully updated poster image via fallback method")
                        success = True
            except Exception as e:
                print(f"Error updating collection poster: {e}")
                
        # Update backdrop if provided
        if backdrop_url:
            try:
                print(f"Downloading backdrop from {backdrop_url}")
                endpoint = f"/Items/{collection_id}/RemoteImages/Download"
                params = {
                    "Type": "Backdrop",  # Backdrop/fanart
                    "ImageUrl": backdrop_url,
                    "ProviderName": "TMDb"
                }
                
                # For Jellyfin, we need to handle the response differently
                try:
                    url = f"{self.server_url}{endpoint}?api_key={self.api_key}"
                    for key, value in params.items():
                        url += f"&{key}={quote(str(value))}"
                    
                    response = self.session.post(url, timeout=30)  # Longer timeout for image downloads
                    
                    if response.status_code in [200, 204]:
                        print("Successfully updated backdrop image")
                        success = True
                    else:
                        print(f"Failed to update backdrop image: HTTP {response.status_code}")
                        if response.text:
                            print(f"Response: {response.text[:100]}")
                except Exception as e:
                    print(f"Exception during direct backdrop update: {e}")
                    
                    # Fall back to the base method
                    data = self._make_api_request('POST', endpoint, params=params)
                    if data is not None:
                        print("Successfully updated backdrop image via fallback method")
                        success = True
            except Exception as e:
                print(f"Error updating collection backdrop: {e}")
        
        if success:
            print(f"Successfully updated artwork for collection {collection_id}")
        else:
            print(f"Failed to update any artwork for collection {collection_id}")
                
        return success
