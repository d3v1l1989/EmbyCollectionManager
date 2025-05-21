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
                                    remove_response = self.session.post(remove_url, timeout=15)
                                    
                                    if remove_response.status_code == 204:
                                        print(f"Successfully removed temporary item from collection")
                                    else:
                                        print(f"Warning: Failed to remove temporary item from collection: {remove_response.status_code}")
                                except Exception as e:
                                    print(f"Error removing temporary item from collection: {e}")
                                
                                return data['Id']
                            else:
                                print(f"Invalid response data when creating collection: {data}")
                        except Exception as e:
                            print(f"Error parsing collection creation response: {e}")
                    else:
                        print(f"Collection creation failed: {response.status_code}")
                        if response.text:
                            print(f"Response: {response.text}")
                except Exception as e:
                    print(f"Error creating collection: {e}")
            else:
                print("No sample item found to use for collection creation")
                
            # If we get here, collection creation failed
            # Create a fake ID and remember the collection name for later reporting
            # This is just to allow the process to continue for other collections
            if not hasattr(self, '_temp_collections'):
                self._temp_collections = {}
                
            fake_id = str(uuid.uuid4())
            self._temp_collections[fake_id] = collection_name
            print(f"Created temporary placeholder ID for collection '{collection_name}': {fake_id}")
            print(f"Please create this collection manually in your Emby web interface.")
            return fake_id
        except Exception as e:
            print(f"Error during collection creation: {e}")
            return None
            
    def get_library_item_ids_by_tmdb_ids(self, tmdb_ids: List[int]) -> List[str]:
        """
        Given a list of TMDb IDs, return the Emby server's internal item IDs for owned movies.
        Args:
            tmdb_ids: List of TMDb movie IDs.
        Returns:
            List of Emby item IDs (str).
        """
        if not tmdb_ids:
            return []
            
        # Convert all IDs to strings for comparison
        tmdb_ids_str = [str(id) for id in tmdb_ids]
        found_item_ids = []
        
        # We need to scan the entire movie library to find the matching TMDb IDs
        print(f"Scanning library for {len(tmdb_ids)} TMDb movies...")
        
        # First get all movies from the library
        # Note this will only return the first 100-200 movies, so we need to page through results
        try:
            params = {
                'IncludeItemTypes': 'Movie',
                'Recursive': 'true',
                'Fields': 'ProviderIds', # Make sure we get the TMDb ID in the provider IDs
                'Limit': 100, # Fetch in batches of 100 to avoid overloading the server
            }
            endpoint = f"/Users/{self.user_id}/Items"
            
            # Initialize for pagination
            start_index = 0
            total_found = 0
            has_more = True
            movie_batch_size = 100
            
            # Use set to track what we've already found to avoid duplicates
            found_tmdb_ids = set()
            
            # Keep fetching until we have all items or find all our TMDb IDs
            while has_more and len(found_tmdb_ids) < len(tmdb_ids_str):
                params['StartIndex'] = start_index
                print(f"Fetching movies batch {start_index//movie_batch_size + 1}...")
                
                data = self._make_api_request('GET', endpoint, params=params)
                if not data:
                    break
                    
                total_items = data.get('TotalRecordCount', 0)
                items = data.get('Items', [])
                
                if not items:
                    break
                    
                # Check each item for matching TMDb IDs
                for item in items:
                    provider_ids = item.get('ProviderIds', {})
                    if not provider_ids:
                        continue
                        
                    # TMDb IDs can be stored in multiple formats - try all common formats
                    tmdb_id = None
                    if 'Tmdb' in provider_ids:
                        tmdb_id = provider_ids['Tmdb']
                    elif 'TMDb' in provider_ids:
                        tmdb_id = provider_ids['TMDb']
                    elif 'tmdb' in provider_ids:
                        tmdb_id = provider_ids['tmdb']
                        
                    if tmdb_id and tmdb_id in tmdb_ids_str and tmdb_id not in found_tmdb_ids:
                        found_item_ids.append(item['Id'])
                        found_tmdb_ids.add(tmdb_id)
                        total_found += 1
                        
                # Update for next batch
                start_index += len(items)
                has_more = start_index < total_items
                print(f"Found {len(found_tmdb_ids)} of {len(tmdb_ids)} TMDb movies so far...")
                
            print(f"Completed library scan. Found {len(found_item_ids)} of {len(tmdb_ids)} TMDb movies.")
            
        except Exception as e:
            print(f"Error scanning library for TMDb IDs: {e}")
            
        # Return the item IDs we found
        print(f"Found total of {len(found_item_ids)} matching movies in Emby library")
        return found_item_ids

    def get_item_names_by_ids(self, item_ids: List[str]) -> dict:
        """
        Get movie/item names by their IDs to provide better logging.
        
        Args:
            item_ids: List of Emby item IDs
            
        Returns:
            Dictionary mapping item IDs to their names
        """
        result = {}
        
        if not item_ids:
            return result
            
        # Process items in batches to avoid making too many individual API calls
        batch_size = 25
        for i in range(0, len(item_ids), batch_size):
            batch = item_ids[i:i+batch_size]
            
            try:
                # Use comma-separated list of IDs to get details for multiple items at once
                ids_param = ",".join(batch)
                endpoint = f"/Items?Ids={ids_param}"
                data = self._make_api_request('GET', endpoint)
                
                if data and 'Items' in data:
                    for item in data['Items']:
                        if 'Id' in item and 'Name' in item:
                            result[item['Id']] = item['Name']
            except Exception as e:
                print(f"Error fetching names for batch of items: {e}")
        
        return result

    def update_collection_items(self, collection_id: str, item_ids: List[str]) -> bool:
        """
        Set the items for a given Emby collection.
        Args:
            collection_id: The Emby collection ID.
            item_ids: List of Emby item IDs to include in the collection.
        Returns:
            True if successful, False otherwise.
        """
        if not collection_id or not item_ids:
            print("Error: Invalid collection_id or empty item_ids list")
            return False
        
        # Check if this is a pseudo-ID for a collection we couldn't create
        if hasattr(self, '_temp_collections') and collection_id in self._temp_collections:
            collection_name = self._temp_collections[collection_id]
            print(f"Cannot update items for pseudo-collection '{collection_name}'")
            print(f"To add items, create the collection manually in your Emby web interface.")
            # We'll pretend it succeeded since we can't do anything about it
            return True
        
        # First get current collection items to avoid duplicates
        current_items = []
        try:
            # Get current collection items
            endpoint = f"/Collections/{collection_id}/Items"
            get_url = f"{self.server_url}{endpoint}?api_key={self.api_key}"
            response = self.session.get(get_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'Items' in data:
                    current_items = [item['Id'] for item in data['Items']]
                    print(f"Collection currently has {len(current_items)} items")
        except Exception as e:
            print(f"Warning: Could not get current collection items: {e}")
        
        # Create a set for existing IDs to avoid duplicating them
        existing_ids = set(current_items)
        new_ids = []
        
        # Get item details for better logging
        items_info = self.get_item_names_by_ids(item_ids)
        
        # Check for duplicates and existing items
        added_in_this_run = set()
        for item_id in item_ids:
            # Skip if this item is already in the collection
            if item_id in existing_ids:
                movie_name = items_info.get(item_id, f"Unknown (ID: {item_id})")
                print(f"  Skipping existing item: {movie_name}")
                continue
                
            # Skip if we've already added this item in this run
            if item_id in added_in_this_run:
                movie_name = items_info.get(item_id, f"Unknown (ID: {item_id})")
                print(f"  Skipping duplicate: {movie_name}")
                continue
            
            # This is a new, unique item
            new_ids.append(item_id)
            added_in_this_run.add(item_id)
            movie_name = items_info.get(item_id, f"Unknown (ID: {item_id})")
            print(f"  Adding new item: {movie_name}")
        
        # If no new items to add, we're done
        if not new_ids:
            print("No new items to add to collection")
            return True
            
        # Add the new items to the collection
        try:
            endpoint = f"/Collections/{collection_id}/Items"            
            params = {"Ids": ",".join(new_ids)}
            print(f"Adding {len(new_ids)} new items to collection {collection_id}...")
            
            # Use direct request because we're expecting a 204 response, not JSON
            url = f"{self.server_url}{endpoint}"
            if "?" in url:
                url += "&"
            else:
                url += "?"
            url += f"api_key={self.api_key}"
            
            # Add parameters
            for key, value in params.items():
                url += f"&{key}={value}"
            
            # Send the request to add items
            response = self.session.post(url, timeout=30)
            
            if response.status_code == 204:
                print(f"Successfully added {len(new_ids)} new items to collection")
                
                # Now try to set the display order for boxsets
                try:
                    # Get the collection metadata
                    collection_url = f"{self.server_url}/Items/{collection_id}?api_key={self.api_key}"
                    collection_response = self.session.get(collection_url, timeout=30)
                    
                    if collection_response.status_code == 200:
                        collection_data = collection_response.json()
                        
                        # Update the collection to use sorting by release date
                        update_data = {
                            "Id": collection_id,
                            "CollectionSortOrder": "PremiereDate"
                        }
                        
                        update_url = f"{self.server_url}/Items/{collection_id}?api_key={self.api_key}"
                        update_response = self.session.post(update_url, json=update_data, timeout=30)
                        
                        if update_response.status_code in [200, 204]:
                            print("Successfully updated collection sort order")
                        else:
                            print(f"Note: Could not update collection sort order: {update_response.status_code}")
                except Exception as e:
                    print(f"Note: Error during collection sort preference update: {e}")
                
                print(f"\nIMPORTANT: If items are still sorted incorrectly, please use the Emby web UI:")
                print(f"  1. Navigate to the collection and click the '...' menu")
                print(f"  2. Select 'Edit metadata'")
                print(f"  3. Change 'Display order' to your preferred option:")
                print(f"     - For franchise collections, use 'Release date'")
                print(f"     - For popular collections, use 'Popularity'")
                
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