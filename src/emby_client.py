from typing import List, Optional, Dict, Any
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
        logger.info(f"Searching for collection: '{collection_name}'")
        data = self._make_api_request('GET', endpoint, params=params)
        if data and 'Items' in data:
            for item in data['Items']:
                if item.get('Name', '').lower() == collection_name.lower():
                    logger.info(f"Found existing collection: {item['Name']} (ID: {item['Id']})")
                    return item['Id']
        
        # Collection doesn't exist, create it using a sample item ID (required by Emby)
        logger.info(f"Collection '{collection_name}' not found. Creating new collection...")
        
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
                logger.info(f"Found sample item with ID: {sample_item_id} to use for collection creation")
                
                # Create the collection using the sample item (this is the key insight from the other code)
                try:
                    # Method 1: Use the direct format demonstrated in the other code
                    # Format: /Collections?api_key=XXX&IsLocked=true&Name=CollectionName&Ids=123456
                    encoded_name = quote(collection_name)
                    # Ensure IsLocked=false if you want to edit it easily later, or true if you want to protect it.
                    # Let's default to false for easier management initially.
                    full_url = f"{self.server_url}/Collections?api_key={self.api_key}&IsLocked=false&Name={encoded_name}&Ids={sample_item_id}"
                    logger.info(f"Creating collection with URL-encoded name and sample item...")
                    
                    # Don't print the full URL with API key
                    logger.info(f"URL (API key hidden): {full_url.replace(self.api_key, 'API_KEY_HIDDEN')}")
                    
                    response = self.session.post(full_url, timeout=15)
                    
                    if response.status_code == 200 and response.text: # Emby usually returns 200 OK with collection details
                        try:
                            data = response.json()
                            if data and 'Id' in data:
                                new_collection_id = data['Id']
                                logger.info(f"Successfully created collection '{collection_name}' with ID: {new_collection_id}")
                                
                                # Remove this temporary item from the collection immediately
                                try:
                                    # The endpoint for removing items from a collection is /Collections/{CollectionId}/Items
                                    # The method is DELETE, not POST, and IDs are passed in query string.
                                    remove_url = f"{self.server_url}/Collections/{new_collection_id}/Items?api_key={self.api_key}&Ids={sample_item_id}"
                                    logger.info(f"Removing temporary item {sample_item_id} from collection {new_collection_id}...")
                                    # remove_response = self.session.post(remove_url, timeout=15) # Original was POST
                                    remove_response = self.session.delete(remove_url, timeout=15) # Correct method is DELETE

                                    # Successful deletion usually returns 204 No Content
                                    if remove_response.status_code == 204:
                                        logger.info(f"Successfully removed temporary item from collection")
                                    else:
                                        logger.warning(f"Failed to remove temporary item from collection: {remove_response.status_code} - {remove_response.text}")
                                except Exception as e:
                                    logger.error(f"Error removing temporary item from collection: {e}")
                                
                                return new_collection_id
                            else:
                                logger.error(f"Invalid response data when creating collection: {data}")
                        except Exception as e:
                            logger.error(f"Error parsing collection creation response: {e} - Response text: {response.text}")
                    else:
                        logger.error(f"Collection creation failed: {response.status_code}")
                        if response.text:
                            logger.error(f"Response: {response.text}")
                except Exception as e:
                    logger.error(f"Error creating collection: {e}")
            else:
                logger.warning("No sample item found to use for collection creation")
                
            # If we get here, collection creation failed
            # Create a fake ID and remember the collection name for later reporting
            # This is just to allow the process to continue for other collections
            if not hasattr(self, '_temp_collections'):
                self._temp_collections = {}
                
            fake_id = str(uuid.uuid4())
            self._temp_collections[fake_id] = collection_name
            logger.info(f"Created temporary placeholder ID for collection '{collection_name}': {fake_id}")
            logger.info(f"Please create this collection manually in your Emby web interface.")
            return fake_id
        except Exception as e:
            logger.error(f"Error during collection creation: {e}")
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
        logger.info(f"Scanning library for {len(tmdb_ids)} TMDb movies...")
        
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
                logger.info(f"Fetching movies batch {start_index//movie_batch_size + 1}...")
                
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
                logger.info(f"Found {len(found_tmdb_ids)} of {len(tmdb_ids)} TMDb movies so far...")
                
            logger.info(f"Completed library scan. Found {len(found_item_ids)} of {len(tmdb_ids)} TMDb movies.")
            
        except Exception as e:
            logger.error(f"Error scanning library for TMDb IDs: {e}")
            
        # Return the item IDs we found
        logger.info(f"Found total of {len(found_item_ids)} matching movies in Emby library")
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
        batch_size = 25 # Emby's Ids parameter can usually take more, but 25 is safe.
        for i in range(0, len(item_ids), batch_size):
            batch = item_ids[i:i+batch_size]
            
            try:
                # Use comma-separated list of IDs to get details for multiple items at once
                ids_param = ",".join(batch)
                # Fetching from /Items requires user_id to get full editable metadata
                endpoint = f"/Users/{self.user_id}/Items?Ids={ids_param}&Fields=Name,SortName" # Added SortName for debugging
                data = self._make_api_request('GET', endpoint) # _make_api_request should handle self.user_id if needed by endpoint
                
                if data and 'Items' in data:
                    for item in data['Items']:
                        if 'Id' in item and 'Name' in item:
                            result[item['Id']] = item['Name']
            except Exception as e:
                logger.error(f"Error fetching names for batch of items: {e}")
        
        return result

    def update_collection_items(self, collection_id: str, item_ids: List[str]) -> bool:
        """
        Set the items for a given Emby collection, applying custom sort order.
        The item_ids list should be in the desired final sort order.
        Args:
            collection_id: The Emby collection ID.
            item_ids: List of Emby item IDs to include in the collection, in the desired sort order.
        Returns:
            True if successful, False otherwise.
        """
        if not collection_id: # item_ids can be empty if we want to clear a collection
            logger.error("Error: Invalid collection_id")
            return False
        
        if hasattr(self, '_temp_collections') and collection_id in self._temp_collections:
            collection_name = self._temp_collections[collection_id]
            logger.info(f"Cannot update items for pseudo-collection '{collection_name}'")
            return True # Pretend success
        
        # 1. Add/Update items in the collection
        # Emby's /Collections/{Id}/Items endpoint replaces all items with the provided list.
        # So, we just pass the full desired list.
        
        items_to_set_str = ",".join(item_ids)
        add_items_url = f"{self.server_url}/Collections/{collection_id}/Items?api_key={self.api_key}&Ids={items_to_set_str}"
        
        try:
            logger.info(f"Setting {len(item_ids)} items for collection {collection_id}...")
            # This POST request replaces the collection's content with the given IDs
            response = self.session.post(add_items_url, timeout=30) 
            
            if response.status_code == 204: # 204 No Content is success
                logger.info(f"Successfully set items in collection {collection_id}.")

                # 2. Set the Collection's DisplayOrder to "SortName"
                logger.info(f"Attempting to set collection {collection_id} DisplayOrder to SortName...")
                collection_item_update_url = f"{self.server_url}/Items/{collection_id}?api_key={self.api_key}"
                collection_metadata_payload = {
                    "Id": collection_id, # Required by this endpoint
                    "DisplayOrder": "SortName",
                    # "LockedFields": [] # Optional: use if you suspect fields are locked. Clears all locks.
                                       # Or specify fields to unlock: ["DisplayOrder"]
                }
                
                update_response = self.session.post(collection_item_update_url, json=collection_metadata_payload, timeout=30)
                if update_response.status_code in [200, 204]: # 200 OK or 204 No Content
                    logger.info(f"Successfully set collection DisplayOrder to SortName.")
                else:
                    logger.warning(f"Failed to set collection DisplayOrder to SortName. Status: {update_response.status_code} - {update_response.text[:200]}")
                    # Continue anyway, as item sort names might still be useful if set manually later

                # 3. Set SortName for each item in the collection based on the desired order
                logger.info(f"Setting individual item SortNames for custom order in collection {collection_id}...")
                sort_names_success = self._set_item_sort_names(item_ids) # Pass only item_ids
                if sort_names_success:
                    logger.info("Successfully set all item SortNames for the collection.")
                else:
                    logger.warning("Warning: One or more item SortNames could not be set for the collection.")
                
                return True # Overall success if items were added, even if metadata tweaks had issues
            else:
                logger.error(f"Failed to set items in collection: {response.status_code} - {response.text[:200]}")
                return False
        except Exception as e:
            logger.error(f"Error updating collection items: {e}")
            return False

    # Removed set_collection_display_order as it's better handled by updating DisplayOrder on the collection item
    # Removed set_collection_items_sort_order as its logic is now in _set_item_sort_names

    def _set_item_sort_names(self, ordered_item_ids: List[str]) -> bool:
        """
        Set the SortName property for each item in the provided list based on its position.
        Args:
            ordered_item_ids: List of Emby item IDs in the desired final sort order.
        Returns:
            True if all items were successfully updated, False otherwise.
        """
        if not ordered_item_ids:
            return True # Nothing to do

        all_successful = True
        # Get names for logging purposes in a batch
        item_details = self.get_item_names_by_ids(ordered_item_ids)

        for index, item_id in enumerate(ordered_item_ids):
            item_name = item_details.get(item_id, f"Item {item_id}") # Fallback name
            
            # Create a sortable prefix (e.g., "001-", "002-")
            # Using a simple prefix that Emby's sorter will understand
            prefix = f"{index + 1:03d}_" # Using underscore as separator, can be a dash too
            
            # Payload to update the item's SortName
            # The /Items/{Id} endpoint for POST is used to update an item.
            # The payload should contain the fields to be updated.
            item_update_url = f"{self.server_url}/Items/{item_id}?api_key={self.api_key}"
            payload = {
                "Id": item_id, # Usually required in the payload for this endpoint
                "SortName": f"{prefix}{item_name}",
                # "LockedFields": [] # Optional: to ensure SortName can be updated if locked
                                       # Or specify fields to unlock: ["DisplayOrder"]
            }
            
            try:
                response = self.session.post(item_update_url, json=payload, timeout=15)
                if response.status_code not in [200, 204]: # 200 OK or 204 No Content
                    logger.error(f"Failed to set SortName for {item_name} (ID: {item_id}). Status: {response.status_code} - {response.text[:100]}")
                    all_successful = False
                else:
                    logger.info(f"Set SortName: {payload['SortName']} for {item_name} (ID: {item_id})")
            except Exception as e:
                logger.error(f"Error setting SortName for {item_name} (ID: {item_id}): {e}")
                all_successful = False
                
        return all_successful
    
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
            logger.info(f"Cannot update artwork for pseudo-collection '{collection_name}'")
            logger.info(f"To use artwork, create the collection manually in your Emby web interface.")
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
                    "ProviderName": "TMDb" # Or any other provider name, it's informational
                }
                logger.info(f"Updating poster for collection {collection_id}")
                
                # Use direct API call instead of the helper which expects JSON back
                response = self.session.post(url, json=payload, timeout=15)
                
                # 204 is success with no content
                if response.status_code in [200, 204]:
                    success = True
                    logger.info(f"Poster update successful (status: {response.status_code})")
                else:
                    logger.error(f"Failed to update poster (status: {response.status_code}) - {response.text}")
            except Exception as e:
                logger.error(f"Error updating collection poster: {e}")
                
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
                logger.info(f"Updating backdrop for collection {collection_id}")
                
                # Use direct API call instead of the helper which expects JSON back
                response = self.session.post(url, json=payload, timeout=15)
                
                # 204 is success with no content
                if response.status_code in [200, 204]:
                    success = True
                    logger.info(f"Backdrop update successful (status: {response.status_code})")
                else:
                    logger.error(f"Failed to update backdrop (status: {response.status_code}) - {response.text}")
            except Exception as e:
                logger.error(f"Error updating collection backdrop: {e}")
                
        return success

    def _make_api_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None,
                          json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Internal helper to make API requests.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/Users/{user_id}/Items")
            params: Optional query parameters
            json_data: Optional JSON payload for POST/PUT requests
            **kwargs: Additional keyword arguments to pass to the request
            
        Returns:
            JSON response data or None if error/no content
        """
        # Call the parent class implementation which handles common functionality
        # This implementation adds a few Emby-specific enhancements
        
        # Make sure we have a session with proper headers
        if not hasattr(self, 'session'):
            self.session = requests.Session()
            self.session.headers.update({
                'X-Emby-Token': self.api_key,
                'Accept': 'application/json'
            })
        
        # Ensure API key is included in requests
        current_params = params.copy() if params else {}
        if 'api_key' not in current_params and not endpoint.lower().startswith('http'):
            current_params['api_key'] = self.api_key
            
        try:
            url = f"{self.server_url}{endpoint}" if not endpoint.lower().startswith('http') else endpoint
            response = self.session.request(method, url, params=current_params, json=json_data, timeout=30, **kwargs)
            response.raise_for_status()
            
            # Handle 204 No Content responses (successful but no body)
            if response.status_code == 204:
                return None
                
            return response.json()
            
        except requests.exceptions.JSONDecodeError as e:
            logger.error(f"API response is not valid JSON: {e}")
            if 'response' in locals():
                logger.error(f"Response text: {response.text[:200]}")
            return None
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"API request failed with HTTP error: {e}")
            logger.error(f"Request URL: {endpoint}")
            logger.error(f"Request method: {method}")
            logger.error(f"Request params: {params}")
            logger.error(f"Request JSON: {json_data}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                logger.error(f"Response text: {e.response.text[:200]}")
            return None
            
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None