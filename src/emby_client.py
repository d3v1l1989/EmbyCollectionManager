from typing import List, Optional, Dict, Any
import uuid
import logging
import requests
import os
from typing import List, Dict, Any, Optional
from urllib.parse import quote

from .base_media_server_client import MediaServerClient
from .poster_generator import generate_custom_poster, file_to_url

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
                logger.info(f"Attempting to set collection {collection_id} DisplayOrder to PremiereDate (SortOrder: Descending)...")
                
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
                    
                    # Set the DisplayOrder to PremiereDate in descending order
                    collection_metadata_payload["DisplayOrder"] = "PremiereDate"
                    collection_metadata_payload["SortOrder"] = "Descending"
                    collection_metadata_payload["SortBy"] = "PremiereDate"
                    
                    # Auxiliary sort fields (SortByPremiereDate, SortByPremiereFirst) removed 
                    # to rely on core DisplayOrder, SortOrder, and SortBy fields.
                    if "SortByPremiereDate" in collection_metadata_payload:
                        del collection_metadata_payload["SortByPremiereDate"]
                    if "SortByPremiereFirst" in collection_metadata_payload:
                        del collection_metadata_payload["SortByPremiereFirst"]
                    
                    # Ensure LockedFields allows DisplayOrder and SortBy to be changed
                    locked_fields = collection_metadata_payload.get('LockedFields') if isinstance(collection_metadata_payload.get('LockedFields'), list) else []
                    locked_fields = [field for field in locked_fields if field not in ['DisplayOrder', 'SortBy']]
                    collection_metadata_payload['LockedFields'] = locked_fields
                    
                    # Send the update to the collection
                    logger.info(f"Collection metadata update payload for {collection_id}: {collection_metadata_payload}")
                    collection_item_update_url = f"{self.server_url}/Items/{collection_id}?api_key={self.api_key}"
                    update_response = self.session.post(collection_item_update_url, json=collection_metadata_payload, timeout=30)
                    display_order_update_attempted = True
                
                # Only perform verification if we attempted the update
                if display_order_update_attempted and update_response and update_response.status_code in [200, 204]:
                    logger.info(f"Attempt to set collection DisplayOrder to PremiereDate (SortOrder: Descending) successful (HTTP {update_response.status_code}). Verifying...")
                    
                    # *** IMMEDIATE VERIFICATION ***
                    verification_url = f"{self.server_url}/Users/{self.user_id}/Items/{collection_id}?api_key={self.api_key}&Fields=DisplayOrder,SortOrder,Name"
                    verify_data = self._make_api_request('GET', f"/Users/{self.user_id}/Items/{collection_id}", params={'Fields': 'DisplayOrder,SortOrder,Name'})

                    if verify_data and 'DisplayOrder' in verify_data:
                        actual_display_order = verify_data['DisplayOrder']
                        actual_sort_order = verify_data.get('SortOrder', 'Unknown')
                        logger.info(f"VERIFIED: Collection '{verify_data.get('Name')}' (ID: {collection_id}) is using sorting by {actual_display_order} in {actual_sort_order} order")
                        if actual_display_order != "PremiereDate" or actual_sort_order != "Descending":
                            logger.critical(f"CRITICAL: Collection sort settings did NOT apply! Expected 'PremiereDate/Descending', got '{actual_display_order}/{actual_sort_order}'. This may affect collection sorting.")
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
                try:
                    refresh_url = f"{self.server_url}/Items/{collection_id}/Refresh?api_key={self.api_key}"
                    refresh_response = self.session.post(refresh_url, timeout=30)
                    if refresh_response.status_code in [200, 204]:
                        logger.info(f"Successfully sent refresh command for collection {collection_id}.")
                    else:
                        logger.warning(f"Failed to send refresh command for collection {collection_id}: {refresh_response.status_code}")
                except Exception as e_refresh:
                    logger.warning(f"Error sending refresh command: {e_refresh}")
                
                return True # Overall success if items were added, even if metadata tweaks had issues
            else:
                logger.error(f"Failed to set items in collection: {response.status_code} - {response.text[:200]}")
                return False
        except Exception as e:
            logger.error(f"Error updating collection items: {e}")
            return False

    # Removed methods related to custom sorting since we're now using year-based sorting
    
    def update_collection_artwork(self, collection_id: str, poster_url: Optional[str]=None, backdrop_url: Optional[str]=None) -> bool:
        """
        Update artwork for an Emby collection using external image URLs.
        Order of poster selection:
        1. Use provided poster_url if any
        2. Try to fetch collection poster from TMDb
        3. Generate custom poster if enabled
        4. Fall back to first movie's poster as last resort
        
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
            
            # For placeholder collections, try to generate a custom poster for future use
            if hasattr(self, 'config') and self.config.get('poster_settings', {}).get('enable_custom_posters', True):
                try:
                    # Get poster settings from config
                    poster_settings = self.config.get('poster_settings', {})
                    template_name = poster_settings.get('template_name')
                    text_color = poster_settings.get('text_color')
                    text_position = poster_settings.get('text_position')
                    
                    logger.info(f"Generating custom poster for future use with collection '{collection_name}'")
                    custom_poster_path = generate_custom_poster(
                        collection_name,
                        template_name=template_name,
                        text_color=text_color,
                        text_position=text_position
                    )
                    
                    if custom_poster_path:
                        logger.info(f"Generated custom poster for '{collection_name}' at: {custom_poster_path}")
                        logger.info(f"This poster will be available for manual assignment after creating the collection.")
                    else:
                        logger.warning(f"Failed to generate custom poster for '{collection_name}'")
                except Exception as e:
                    logger.error(f"Error generating custom poster for placeholder collection: {e}")
            
            # We'll pretend it succeeded since we can't do anything about it
            return True
            
        success = False
        collection_data = None
        
        if not collection_id:
            return False
        
        # If no poster_url is provided, try to get one using our priority order
        if not poster_url:
            logger.info("No poster URL provided, attempting to find a suitable poster")
            
            # First, get the collection details (we'll need this in multiple steps)
            try:
                # Use uppercase /Items/ for getting item information
                collection_endpoint = f"/Items/{collection_id}?api_key={self.api_key}"
                collection_data = self._make_api_request('GET', collection_endpoint)
            except Exception as e:
                logger.error(f"Error fetching collection data: {e}")
                collection_data = None
                
            # STEP 1: Try to fetch TMDb collection poster if available
            if collection_data and 'ProviderIds' in collection_data:
                try:
                    tmdb_id = collection_data['ProviderIds'].get('Tmdb')
                    
                    if tmdb_id:
                        logger.info(f"Found TMDb collection ID: {tmdb_id}")
                        # Use uppercase /Items/ for remote images
                        remote_images_endpoint = f"/Items/{collection_id}/RemoteImages?api_key={self.api_key}"
                        remote_images_data = self._make_api_request('GET', remote_images_endpoint)
                        
                        # Look for collection poster in remote images
                        if remote_images_data and 'Images' in remote_images_data:
                            collection_posters = [img for img in remote_images_data['Images'] 
                                                if img.get('Type') == 'Primary' and 
                                                img.get('ProviderName') == 'TheMovieDb']
                            
                            if collection_posters:
                                # Sort by vote average to get the best poster
                                collection_posters.sort(key=lambda x: x.get('CommunityRating', 0), reverse=True)
                                poster_url = collection_posters[0].get('Url')
                                logger.info(f"Found collection poster from TMDb: {poster_url}")
                except Exception as e:
                    logger.error(f"Error fetching TMDb poster: {e}")
            
            # STEP 2: If no TMDb poster, try generating a custom poster if enabled
            if not poster_url and hasattr(self, 'config') and self.config.get('poster_settings', {}).get('enable_custom_posters', True):
                try:
                    # Make sure we have collection data with name
                    if not collection_data or 'Name' not in collection_data:
                        collection_endpoint = f"/Items/{collection_id}?api_key={self.api_key}"
                        collection_data = self._make_api_request('GET', collection_endpoint)
                    
                    if collection_data and 'Name' in collection_data:
                        collection_name = collection_data['Name']
                        
                        # Get poster settings from config
                        poster_settings = self.config.get('poster_settings', {})
                        template_name = poster_settings.get('template_name')
                        text_color = poster_settings.get('text_color')
                        text_position = poster_settings.get('text_position')
                        
                        # Generate custom poster with configured settings
                        logger.info(f"Attempting to generate custom poster for collection '{collection_name}'")
                        custom_poster_path = generate_custom_poster(
                            collection_name,
                            template_name=template_name,
                            text_color=text_color,
                            text_position=text_position
                        )
                        
                        if custom_poster_path:
                            # Convert file path to URL
                            poster_url = file_to_url(custom_poster_path)
                            logger.info(f"Generated custom poster at: {custom_poster_path}")
                        else:
                            logger.warning(f"Failed to generate custom poster for '{collection_name}'")
                    else:
                        logger.warning("Could not determine collection name for custom poster generation")
                except Exception as e:
                    logger.error(f"Error generating custom poster: {e}")
            elif not poster_url and not (hasattr(self, 'config') and self.config.get('poster_settings', {}).get('enable_custom_posters', True)):
                logger.info("Custom poster generation is disabled in config or config not available")
            
            # STEP 3: Last resort - If still no poster, try using first movie's poster as fallback
            if not poster_url:
                try:
                    logger.info("Falling back to first movie poster in the collection")
                    # Get items in the collection
                    collection_items_endpoint = f"/Items?ParentId={collection_id}&api_key={self.api_key}"
                    items_data = self._make_api_request('GET', collection_items_endpoint)
                    
                    if items_data and 'Items' in items_data and items_data['Items']:
                        first_item = items_data['Items'][0]
                        first_item_id = first_item.get('Id')
                        
                        if first_item_id:
                            # Get remote images for the first item
                            item_images_endpoint = f"/Items/{first_item_id}/RemoteImages?api_key={self.api_key}"
                            item_images_data = self._make_api_request('GET', item_images_endpoint)
                            
                            if item_images_data and 'Images' in item_images_data:
                                movie_posters = [img for img in item_images_data['Images'] 
                                                if img.get('Type') == 'Primary' and 
                                                img.get('ProviderName') == 'TheMovieDb']
                                
                                if movie_posters:
                                    # Sort by vote average to get the best poster
                                    movie_posters.sort(key=lambda x: x.get('CommunityRating', 0), reverse=True)
                                    poster_url = movie_posters[0].get('Url')
                                    logger.info(f"Using first movie's poster as fallback: {poster_url}")
                                else:
                                    logger.info("No movie poster found in TMDb remote images for first item")
                            else:
                                logger.info("No remote images data available for first item")
                        else:
                            logger.info("Could not get ID for the first item in collection")
                    else:
                        logger.info("No items found in collection")
                except Exception as e:
                    logger.error(f"Error trying to fetch first movie poster: {e}")
        
        # Update poster if available - using direct binary upload like Posterizarr
        if poster_url:
            logger.info(f"Attempting to set poster for {collection_id} with URL: {poster_url}")
            try:
                # Download image from URL first
                try:
                    # Download the image
                    image_response = requests.get(poster_url, timeout=15)
                    image_response.raise_for_status()
                    image_data = image_response.content
                    
                    # Determine content type based on URL
                    if poster_url.lower().endswith('.jpg') or poster_url.lower().endswith('.jpeg'):
                        content_type = 'image/jpeg'
                    elif poster_url.lower().endswith('.png'):
                        content_type = 'image/png'
                    else:
                        content_type = 'image/jpeg'  # Default to JPEG
                    
                    # Convert image data to Base64 string - THIS IS CRITICAL
                    import base64
                    image_data_base64 = base64.b64encode(image_data).decode('utf-8')
                    
                    # Use lowercase URL exactly as Posterizarr does
                    url = f"{self.server_url}/items/{collection_id}/images/Primary?api_key={self.api_key}"
                    logger.info(f"Updating poster for collection {collection_id} using content type: {content_type}")
                    
                    # No additional headers - just content type as parameter
                    # This exactly matches Posterizarr implementation
                    response = self.session.post(url, data=image_data_base64, headers={'Content-Type': content_type}, timeout=15)
                    if response.status_code in [200, 204]:
                        success = True
                        logger.info(f"Poster update successful (status: {response.status_code})")
                    else:
                        logger.error(f"Failed to update poster (status: {response.status_code}) - {response.text}")
                except requests.RequestException as e:
                    logger.error(f"Error downloading/uploading image from URL {poster_url}: {e}")
            except Exception as e:
                logger.error(f"Error updating collection poster: {e}")
            
        # Update backdrop if provided - using direct binary upload like Posterizarr
        if backdrop_url:
            logger.info(f"Attempting to set backdrop for {collection_id} with URL: {backdrop_url}")
            try:
                # Download image from URL first
                try:
                    # Download the image
                    image_response = requests.get(backdrop_url, timeout=15)
                    image_response.raise_for_status()
                    image_data = image_response.content
                    
                    # Determine content type based on URL
                    if backdrop_url.lower().endswith('.jpg') or backdrop_url.lower().endswith('.jpeg'):
                        content_type = 'image/jpeg'
                    elif backdrop_url.lower().endswith('.png'):
                        content_type = 'image/png'
                    else:
                        content_type = 'image/jpeg'  # Default to JPEG
                    
                    # Convert image data to Base64 string - THIS IS CRITICAL
                    import base64
                    image_data_base64 = base64.b64encode(image_data).decode('utf-8')
                    
                    # Use lowercase URL exactly as Posterizarr does
                    url = f"{self.server_url}/items/{collection_id}/images/Backdrop?api_key={self.api_key}"
                    logger.info(f"Updating backdrop for collection {collection_id} using content type: {content_type}")
                    
                    # No additional headers - just content type as parameter
                    # This exactly matches Posterizarr implementation
                    response = self.session.post(url, data=image_data_base64, headers={'Content-Type': content_type}, timeout=15)
                    if response.status_code in [200, 204]:
                        success = True
                        logger.info(f"Backdrop update successful (status: {response.status_code})")
                    else:
                        logger.error(f"Failed to update backdrop (status: {response.status_code}) - {response.text}")
                except requests.RequestException as e:
                    logger.error(f"Error downloading/uploading image from URL {backdrop_url}: {e}")
            except Exception as e:
                logger.error(f"Error updating collection backdrop: {e}")
            
        return success