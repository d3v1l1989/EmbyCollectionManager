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
        Uses direct provider ID lookup for enhanced performance.
        
        Args:
            tmdb_ids: List of TMDb movie IDs.
        Returns:
            List of Emby item IDs (str).
        """
        if not tmdb_ids:
            return []
        
        # Convert all IDs to strings for comparison and lookup
        tmdb_ids_str = [str(id) for id in tmdb_ids]
        found_item_ids = []
        
        # Use a set to track which TMDb IDs we've already found to avoid duplicates
        found_tmdb_ids = set()
        total_to_find = len(tmdb_ids_str)
        
        logger.info(f"Searching for {total_to_find} TMDb movies using optimized batch lookup...")
        
        try:
            # Use Emby's AnyProviderIdEquals parameter to directly search for TMDb IDs
            # Process in batches to avoid overloading the server with too many IDs at once
            batch_size = 50  # Size of each TMDb ID batch
            total_found = 0
            batch_counter = 0
            
            for i in range(0, len(tmdb_ids_str), batch_size):
                batch_counter += 1
                batch = tmdb_ids_str[i:i+batch_size]
                
                # Generate a string of TMDb IDs in the format needed by Emby's API
                # Format: "tmdb.12345,tmdb.67890,..." (each must be prefixed with tmdb.)
                tmdb_id_query = ','.join([f"tmdb.{tmdb_id}" for tmdb_id in batch])
                
                params = {
                    'IncludeItemTypes': 'Movie',
                    'Recursive': 'true',
                    'Fields': 'ProviderIds',
                    'AnyProviderIdEquals': tmdb_id_query,
                    # Critical: Set Limit to total_to_find to ensure we get all matches
                    # Setting it to batch_size would limit results per batch
                    'Limit': total_to_find,
                    # Add a cache-busting parameter to avoid stale results
                    '_cb': str(uuid.uuid4().hex),
                }
                
                endpoint = f"/Users/{self.user_id}/Items"
                
                # Only log every 5th batch to reduce log spam
                if batch_counter % 5 == 1:
                    logger.info(f"Fetching batch {batch_counter} ({len(batch)} TMDb IDs)...")
                
                data = self._make_api_request('GET', endpoint, params=params)
                if not data:
                    logger.warning(f"No data returned for batch {batch_counter}")
                    continue
                
                items = data.get('Items', [])
                if not items:
                    continue
                
                # Track items found in this batch
                batch_found = 0
                
                # Extract Emby item IDs and store matching TMDb IDs as found
                for item in items:
                    provider_ids = item.get('ProviderIds', {})
                    if not provider_ids:
                        continue
                    
                    # Check for any recognized TMDb ID format
                    tmdb_id = None
                    if 'Tmdb' in provider_ids:
                        tmdb_id = provider_ids['Tmdb']
                    elif 'TMDb' in provider_ids:
                        tmdb_id = provider_ids['TMDb']
                    elif 'tmdb' in provider_ids:
                        tmdb_id = provider_ids['tmdb']
                    
                    # Only add items that match our search criteria and haven't been found before
                    if tmdb_id and tmdb_id in tmdb_ids_str and tmdb_id not in found_tmdb_ids:
                        found_item_ids.append(item['Id'])
                        found_tmdb_ids.add(tmdb_id)
                        batch_found += 1
                
                total_found += batch_found
                
                # Log progress but only every 5th batch or if this batch had significant finds
                if batch_counter % 5 == 0 or batch_found > 0:
                    logger.info(f"Found {total_found} of {total_to_find} TMDb movies so far...")
                
                # If we found everything, we can stop
                if len(found_tmdb_ids) >= len(tmdb_ids_str):
                    logger.info("Found all requested TMDb movies!")
                    break
                    
            # Final summary
            logger.info(f"Completed optimized lookup. Found {len(found_item_ids)} of {total_to_find} TMDb movies in {batch_counter} batches.")
            
            # If we found less than 80% of the movies, log a warning about potential configuration issues
            if len(found_item_ids) < total_to_find * 0.8:
                logger.warning(f"Found only {len(found_item_ids)} of {total_to_find} TMDb movies.")
                logger.warning("If this is lower than expected, check that your TMDb IDs match those in Emby.")
                logger.warning("Some films may need to be refreshed in Emby to update their TMDb provider IDs.")
            
        except Exception as e:
            logger.error(f"Error searching library for TMDb IDs: {e}")
            
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
        # First, ensure we have no duplicate IDs which could cause issues
        unique_item_ids = list(dict.fromkeys(item_ids))  # Preserve order while removing duplicates
        
        if len(unique_item_ids) < len(item_ids):
            logger.info(f"Removed {len(item_ids) - len(unique_item_ids)} duplicate item IDs from collection update")
        
        # Emby's /Collections/{Id}/Items endpoint replaces all items with the provided list.
        # So, we just pass the full desired list.
        items_to_set_str = ",".join(unique_item_ids) if unique_item_ids else "" # Handle empty list to clear collection
        add_items_url = f"{self.server_url}/Collections/{collection_id}/Items?api_key={self.api_key}&Ids={items_to_set_str}"
        
        try:
            logger.info(f"Setting {len(unique_item_ids)} items for collection {collection_id}...")
            # This POST request replaces the collection's content with the given IDs
            response = self.session.post(add_items_url, timeout=30) 
            
            if response.status_code == 204: # 204 No Content is success
                logger.info(f"Successfully set items in collection {collection_id}.")

                # 2. Set and VERIFY the Collection's DisplayOrder to "SortName"
                logger.info(f"Attempting to set collection {collection_id} DisplayOrder to SortName...")
                
                # Initialize update_response to None to track if we attempted the update
                update_response = None
                display_order_update_attempted = False
                
                # First, get the current collection data to ensure we have all required fields
                # This is necessary because the API requires a 'source' parameter and other fields
                collection_data = self._make_api_request('GET', f"/Users/{self.user_id}/Items/{collection_id}")
                
                if not collection_data:
                    logger.error(f"Failed to fetch collection data for ID: {collection_id}")
                    # Continue anyway to try setting SortNames for items
                else:
                    # Start with all existing data and modify what we need
                    collection_metadata_payload = collection_data.copy()
                    
                    # Set the DisplayOrder to ProductionYear in descending order
                    # Make sure all relevant fields are included and formatted correctly
                    collection_metadata_payload["DisplayOrder"] = "ProductionYear"
                    collection_metadata_payload["SortOrder"] = "Descending"
                    
                    # Ensure other sorting-related fields are properly set
                    collection_metadata_payload["SortBy"] = "ProductionYear,SortName"  # Backup sort by name
                    collection_metadata_payload["SortByPremiereDate"] = False
                    collection_metadata_payload["SortByPremiereFirst"] = False
                    
                    # Ensure LockedFields allows DisplayOrder to be changed
                    locked_fields = collection_metadata_payload.get('LockedFields') if isinstance(collection_metadata_payload.get('LockedFields'), list) else []
                    locked_fields = [field for field in locked_fields if field != 'DisplayOrder']
                    collection_metadata_payload['LockedFields'] = locked_fields
                    
                    # Send the update to the collection
                    collection_item_update_url = f"{self.server_url}/Items/{collection_id}?api_key={self.api_key}"
                    update_response = self.session.post(collection_item_update_url, json=collection_metadata_payload, timeout=30)
                    display_order_update_attempted = True
                
                # Only perform verification if we attempted the update
                if display_order_update_attempted and update_response and update_response.status_code in [200, 204]:
                    logger.info(f"Attempt to set collection DisplayOrder to SortName successful (HTTP {update_response.status_code}). Verifying...")
                    
                    # *** IMMEDIATE VERIFICATION ***
                    verification_url = f"{self.server_url}/Users/{self.user_id}/Items/{collection_id}?api_key={self.api_key}&Fields=DisplayOrder,SortOrder,Name"
                    verify_data = self._make_api_request('GET', f"/Users/{self.user_id}/Items/{collection_id}", params={'Fields': 'DisplayOrder,SortOrder,Name'})

                    if verify_data and 'DisplayOrder' in verify_data:
                        actual_display_order = verify_data['DisplayOrder']
                        actual_sort_order = verify_data.get('SortOrder', 'Unknown')
                        logger.info(f"VERIFIED: Collection '{verify_data.get('Name')}' (ID: {collection_id}) is using sorting by {actual_display_order} in {actual_sort_order} order")
                        if actual_display_order != "ProductionYear" or actual_sort_order != "Descending":
                            logger.critical(f"CRITICAL: Collection sort settings did NOT apply! Expected 'ProductionYear/Descending', got '{actual_display_order}/{actual_sort_order}'. Year-based sorting may not work correctly.")
                    else:
                        logger.warning(f"Could not verify collection DisplayOrder. Response: {verify_data}")
                elif display_order_update_attempted and update_response:
                    logger.error(f"FAILED to set collection DisplayOrder to SortName. Status: {update_response.status_code} - {update_response.text[:200]}")
                elif display_order_update_attempted:
                    logger.error(f"FAILED to set collection DisplayOrder to SortName. No response received.")
                else:
                    logger.warning(f"Could not attempt to set collection DisplayOrder due to missing collection data.")
                    
                # No need to set individual item sort names as we're using year-based sorting now
                logger.info(f"Using year-based descending order for collection {collection_id} items.")
                
                # Optional: Trigger a refresh on the collection
                # try:
                #     refresh_url = f"{self.server_url}/Items/{collection_id}/Refresh?api_key={self.api_key}"
                #     refresh_response = self.session.post(refresh_url, timeout=30)
                #     if refresh_response.status_code in [200, 204]:
                #         logger.info(f"Successfully sent refresh command for collection {collection_id}.")
                #     else:
                #         logger.warning(f"Failed to send refresh command for collection {collection_id}: {refresh_response.status_code}")
                # except Exception as e_refresh:
                #     logger.warning(f"Error sending refresh command: {e_refresh}")
                
                return True # Overall success if items were added, even if metadata tweaks had issues
            else:
                logger.error(f"Failed to set items in collection: {response.status_code} - {response.text[:200]}")
                return False
        except Exception as e:
            logger.error(f"Error updating collection items: {e}")
            return False

    # Removed methods related to custom sorting since we're now using year-based sorting
    # - set_collection_display_order is handled by updating DisplayOrder on the collection item
    # - set_collection_items_sort_order is no longer needed
    # - _set_item_sort_names has been removed as we're using ProductionYear sorting
        
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
            
        # Import quote function for URL encoding
        from urllib.parse import quote
        
        # Update poster if provided
        if poster_url:
            try:
                # Ensure the URL is properly encoded
                encoded_url = quote(poster_url, safe='')
                
                # Build direct URL with all parameters included
                base_url = f"{self.server_url}/Items/{collection_id}/RemoteImages/Download"
                url_with_params = f"{base_url}?api_key={self.api_key}&Type=Primary&ImageUrl={encoded_url}&ProviderName=TMDb&EnableImageEnhancers=false"
                
                logger.info(f"Updating poster for collection {collection_id} using direct URL method")
                
                # Make direct request - no JSON payload needed
                response = self.session.post(url_with_params, timeout=30)
                
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
                # Ensure the URL is properly encoded
                encoded_url = quote(backdrop_url, safe='')
                
                # Build direct URL with all parameters included
                base_url = f"{self.server_url}/Items/{collection_id}/RemoteImages/Download"
                url_with_params = f"{base_url}?api_key={self.api_key}&Type=Backdrop&ImageUrl={encoded_url}&ProviderName=TMDb&EnableImageEnhancers=false"
                
                logger.info(f"Updating backdrop for collection {collection_id} using direct URL method")
                
                # Make direct request - no JSON payload needed
                response = self.session.post(url_with_params, timeout=30)
                
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