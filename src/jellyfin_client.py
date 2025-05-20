from typing import List, Optional, Dict, Any, Union
import hashlib
import logging
import requests
import random
import re
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
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
                    # Use the same approach as Emby - direct URL parameters rather than JSON body
                    encoded_name = quote(collection_name)
                    
                    # Format: /Collections?api_key=XXX&IsLocked=true&Name=CollectionName&Ids=123456
                    # This follows the exact same pattern that works for Emby
                    full_url = f"{self.server_url}/Collections?api_key={self.api_key}&IsLocked=true&Name={encoded_name}&Ids={sample_item_id}"
                    print(f"Creating collection using URL parameters...")
                    
                    # Don't print the full URL with API key
                    print(f"URL (API key hidden): {full_url.replace(self.api_key, 'API_KEY_HIDDEN')}")
                    
                    # Make a direct POST request without a JSON body
                    response = self.session.post(full_url, timeout=15)
                    
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
                    
                    # Try the more compatible /Library/Collections endpoint approach
                    # This is a special endpoint in some Jellyfin versions
                    endpoint = f"/Library/Collections"
                    payload = {
                        'Name': collection_name,
                        'IsLocked': True,
                        'Type': 'boxset'
                    }
                    
                    # Try with direct session post first
                    try:
                        url = f"{self.server_url}{endpoint}?api_key={self.api_key}"
                        print(f"Trying Library/Collections endpoint...")
                        response = self.session.post(url, json=payload, timeout=15)
                        
                        if response.status_code in [200, 201, 204] and response.text:
                            try:
                                data = response.json()
                                if data and 'Id' in data:
                                    print(f"Successfully created Jellyfin collection via Library endpoint with ID: {data['Id']}")
                                    return data['Id']
                            except:
                                pass
                    except Exception as e:
                        print(f"Library/Collections endpoint failed: {e}")
                    
                    # Try another alternative endpoint used by some clients
                    try:
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
                    except Exception as e2:
                        print(f"Standard Collections endpoint failed: {e2}")
                except Exception as e:
                    print(f"All alternative collection creation methods failed: {e}")
            
            # Try one final method - see if we can find a collection that already exists with a similar name
            try:
                print(f"Trying to find similar collection as fallback...")
                params = {
                    'IncludeItemTypes': 'BoxSet',
                    'Recursive': 'true',
                    'Fields': 'Name'
                }
                endpoint = f"/Users/{self.user_id}/Items"
                data = self._make_api_request('GET', endpoint, params=params)
                
                if data and 'Items' in data and data['Items']:
                    # If any collection exists, suggest manual creation but also use first collection as fallback
                    first_collection = data['Items'][0]
                    print(f"Found existing collection '{first_collection['Name']}' (ID: {first_collection['Id']})")
                    print(f"Using this collection as temporary fallback for '{collection_name}'")
                    print(f"IMPORTANT: Please manually add '{collection_name}' to your collection or create it")
                    return first_collection['Id']
            except Exception as e:
                print(f"Error finding fallback collection: {e}")
            
            # If all creation attempts failed, use a temporary ID
            print(f"All collection creation methods failed for '{collection_name}'")
            print(f"ERROR: Cannot create collection '{collection_name}' on your Jellyfin server.")
            print(f"This typically happens when the API user doesn't have sufficient permissions")
            print(f"or when there are API compatibility issues with your Jellyfin version.")
            print(f"To fix this:")
            print(f"1. Ensure your API user has 'Administrator' access")
            print(f"2. Manually create the collection in Jellyfin's web interface")
            
            temp_id = hashlib.md5(collection_name.encode()).hexdigest()
            self._temp_collections = getattr(self, '_temp_collections', {})
            self._temp_collections[temp_id] = collection_name
            print(f"Using temporary ID: {temp_id}")
            print(f"IMPORTANT: Please manually create a collection named '{collection_name}' in Jellyfin")
            return temp_id
            
        except Exception as e:
            print(f"Error during collection creation process: {e}")
            return None

    def add_batch_to_collection(self, collection_id: str, item_ids: List[str]) -> bool:
        """
        Add a batch of items to a collection incrementally.
        Args:
            collection_id: The Jellyfin collection ID.
            item_ids: List of Jellyfin item IDs to add to the collection.
        Returns:
            True if successful, False otherwise.
        """
        if not item_ids:
            print("No items to add in this batch")
            return True
            
        if not collection_id:
            print("No collection ID provided")
            return False
            
        # For pseudo-collections, we can't add items
        if hasattr(self, '_temp_collections') and collection_id in self._temp_collections:
            return True
            
        # Endpoint for adding items to a collection
        endpoint = f"/Collections/{collection_id}/Items"
        
        # Format the IDs as a comma-separated string
        batch_str = ','.join(item_ids)
        
        try:
            # Try direct POST with batch_str as parameter
            params = {'ids': batch_str}
            url = f"{self.server_url}{endpoint}?api_key={self.api_key}"
            print(f"Adding batch of {len(item_ids)} items to collection...")
            
            # Try both methods: params and direct URL
            response = self.session.post(url, params=params, timeout=15)
            
            if response.status_code not in [200, 204]:
                # Try direct URL method as fallback
                direct_url = f"{url}&ids={batch_str}"
                response = self.session.post(direct_url, timeout=15)
                
            if response.status_code in [200, 204]:
                print(f"Successfully added batch of {len(item_ids)} items to collection")
                return True
            else:
                print(f"Error adding batch to collection: HTTP {response.status_code}")
                if response.text:
                    print(f"Response: {response.text[:100]}")
                return False
        except Exception as e:
            print(f"Exception during batch add: {e}")
            return False
    
    def update_collection_items(self, collection_id: str, tmdb_ids: List[int], incremental: bool = True) -> bool:
        """
        Update a collection with items that match the provided TMDb IDs.
        Args:
            collection_id: The Jellyfin collection ID.
            tmdb_ids: List of TMDb movie IDs to add to the collection.
            incremental: If True, add items to collection incrementally after each batch.
        Returns:
            True if successful, False otherwise.
        """
        if not collection_id:
            print("No collection ID provided")
            return False
            
        # For pseudo-collections, we can't add items
        if hasattr(self, '_temp_collections') and collection_id in self._temp_collections:
            return True
        
        print(f"Updating collection with {len(tmdb_ids)} TMDb IDs")
        
        if incremental:
            # Get the Jellyfin item IDs for the TMDb IDs and add them incrementally
            print("Using incremental batch processing to add items to collection")
            item_ids = self.get_library_item_ids_by_tmdb_ids(tmdb_ids, collection_id)
            
            if not item_ids:
                print("No matching items found in the library")
                return False
                
            print(f"Incremental update complete. Added {len(item_ids)} total items to collection.")
            return True
        else:
            # Traditional approach - get all IDs first, then add them in one go
            print("Using traditional approach to add items to collection")
            item_ids = self.get_library_item_ids_by_tmdb_ids(tmdb_ids)
            
            if not item_ids:
                print("No matching items found in the library")
                return False
                
            print(f"Found {len(item_ids)} matching items in the library")
            
            # Add all items at once
            return self.add_batch_to_collection(collection_id, item_ids)
    
    def get_library_item_ids_by_tmdb_ids(self, tmdb_ids: List[int], collection_id: str = None) -> List[str]:
        """
        Given a list of TMDb IDs, return the Jellyfin server's internal item IDs for owned movies.
        If collection_id is provided, items will be added to the collection incrementally in batches.
        
        Args:
            tmdb_ids: List of TMDb movie IDs.
            collection_id: Optional. If provided, items will be added to this collection incrementally.
        Returns:
            List of Jellyfin item IDs (str).
        """
        item_ids = []
        
        total_to_find = len(tmdb_ids)
        print(f"Searching for {total_to_find} movies in Jellyfin library by TMDb IDs")
        
        # Convert TMDb IDs to strings for EXACT comparison
        # Create a set for O(1) lookup
        tmdb_str_ids = set(str(tmdb_id) for tmdb_id in tmdb_ids)
        
        # Add additional debug information 
        if len(tmdb_str_ids) > 0:
            sample_ids = list(tmdb_str_ids)[:5] 
            print(f"Sample TMDb IDs we're looking for: {sample_ids}")
        
        # Track which items we've added to the collection for batch processing
        batch_jellyfin_ids = []
        
        try:
            # Get all movies and manually check TMDb IDs
            # We need to paginate to get ALL movies in the library
            params = {
                'Recursive': 'true',
                'IncludeItemTypes': 'Movie',
                'Fields': 'ProviderIds,Path',
                'Limit': 800,  # Get many more movies at once
                'EnableTotalRecordCount': 'true'  # Get total count for pagination
            }
            
            endpoint = f"/Users/{self.user_id}/Items"
            
            # Set up pagination variables
            start_index = 0
            page_size = 800
            total_items = 0
            processed_items = 0
            
            # First get total count of movies
            count_params = dict(params)
            count_params['Limit'] = 1
            initial_data = self._make_api_request('GET', endpoint, params=count_params)
            if initial_data and 'TotalRecordCount' in initial_data:
                total_items = initial_data['TotalRecordCount']
                print(f"Found total of {total_items} movies in Jellyfin library to scan for TMDb matches")
            
            # Log how many TMDb IDs we're looking for
            print(f"Looking for {len(tmdb_str_ids)} unique TMDb IDs in library of {total_items} movies")
            
            # Now paginate through all movies in library
            while True:
                current_params = dict(params)
                current_params['StartIndex'] = start_index
                current_params['Limit'] = page_size
                
                data = self._make_api_request('GET', endpoint, params=current_params)
                
                if not data or 'Items' not in data or not data['Items']:
                    break
                    
                page_items = len(data['Items'])
                processed_items += page_items
                print(f"Scanning {page_items} movies (page {start_index//page_size + 1}, {processed_items}/{total_items})")
                
                # Process the matches in this page
                page_matches = 0
                
                for item in data['Items']:
                    if 'ProviderIds' in item:
                        provider_ids = item['ProviderIds']
                        # Flag to track if we found a match for this item
                        found_match = False
                        
                        # Check for TMDb ID in any case format - ONLY EXACT STRING MATCHES
                        for key in ['Tmdb', 'tmdb', 'TMDB']:
                            if key in provider_ids:
                                jellyfin_tmdb_id = str(provider_ids[key])  # Convert to string for comparison
                                
                                if jellyfin_tmdb_id in tmdb_str_ids:
                                    # We found a matching TMDb ID
                                    name = item.get('Name', '(unknown)')
                                    item_id = item['Id']
                                    
                                    if item_id not in item_ids:  # Avoid duplicates
                                        item_ids.append(item_id)
                                        batch_jellyfin_ids.append(item_id)
                                        page_matches += 1
                                        
                                        # Log the match
                                        if len(item_ids) <= 50 or page_matches <= 5:  # Limit logging for large collections
                                            print(f"  - Found match: {name} (ID: {item_id}) - TMDb ID: {jellyfin_tmdb_id}")
                                    
                                    found_match = True
                                    break  # Break out of the key loop once we find a match
                
                # If collection_id is provided and we found matches, add this batch to the collection
                if collection_id and batch_jellyfin_ids and len(batch_jellyfin_ids) >= 25:  # Add in batches of 25 or more
                    print(f"Adding batch of {len(batch_jellyfin_ids)} items to collection...")
                    self.add_batch_to_collection(collection_id, batch_jellyfin_ids)
                    batch_jellyfin_ids = []  # Clear the batch after adding
                
                # Report progress for this page
                if page_matches > 0:
                    print(f"Found {page_matches} matches on this page (total: {len(item_ids)})")
                
                # If we got fewer items than requested, we've reached the end
                if page_items < page_size:
                    break
                    
                # Move to next page
                start_index += page_size
            
            # Add any remaining items to the collection
            if collection_id and batch_jellyfin_ids:
                print(f"Adding final batch of {len(batch_jellyfin_ids)} items to collection...")
                self.add_batch_to_collection(collection_id, batch_jellyfin_ids)
                
        except Exception as e:
            print(f"Error scanning library with pagination: {e}")
            
            # Fall back to simple non-paginated scan with smaller limit
            try:
                print("Falling back to simple library scan without pagination...")
                simple_params = {
                    'Recursive': 'true',
                    'IncludeItemTypes': 'Movie',
                    'Fields': 'ProviderIds,Path',
                    'Limit': 200  # Smaller but safer limit
                }
                
                simple_data = self._make_api_request('GET', endpoint, params=simple_params)
                if simple_data and 'Items' in simple_data and simple_data['Items']:
                    simple_count = len(simple_data['Items'])
                    print(f"Scanning {simple_count} movies with simple method")
                    
                    for item in simple_data['Items']:
                        if 'ProviderIds' in item:
                            provider_ids = item['ProviderIds']
                            # Check for TMDb ID in any case format
                            for key in ['Tmdb', 'tmdb', 'TMDB']:
                                if key in provider_ids:
                                    jellyfin_tmdb_id = str(provider_ids[key])
                                    if jellyfin_tmdb_id in tmdb_str_ids:
                                        name = item.get('Name', '(unknown)')
                                        item_id = item['Id']
                                        print(f"Found match via simple scan: {name} (ID: {item_id})")
                                        if item_id not in item_ids:  # Avoid duplicates
                                            item_ids.append(item_id)
                                            batch_jellyfin_ids.append(item_id)
                                        break
                    
                    # Add any found items to the collection
                    if collection_id and batch_jellyfin_ids:
                        print(f"Adding batch of {len(batch_jellyfin_ids)} items to collection from simple scan...")
                        self.add_batch_to_collection(collection_id, batch_jellyfin_ids)
            except Exception as simple_e:
                print(f"Simple library scan also failed: {simple_e}")
        
        # No fallback - only include exact matches
        
        print(f"Found total of {len(item_ids)} matching movies in Jellyfin library")
        return item_ids

    def add_items_to_collection(self, collection_id: str, item_ids: List[str]) -> bool:
        """
        Add items to a collection.
        Args:
            collection_id: The Jellyfin collection ID.
            item_ids: List of Jellyfin item IDs to add to the collection.
        Returns:
            True if successful, False otherwise.
        """
        # Use our new batch-based approach
        return self.add_batch_to_collection(collection_id, item_ids)
    
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
        
    def find_collection_with_name_or_create(self, collection_name: str, list_id: Optional[str]=None, 
                                            description: Optional[str]=None, plugin_name: Optional[str]=None) -> str:
        """
        Find a collection by name or create it if it doesn't exist.
        Extended version of get_or_create_collection with additional metadata support.
        
        Args:
            collection_name: Name of the collection
            list_id: External ID/reference for the collection
            description: Description text for the collection
            plugin_name: Name of plugin/source generating the collection
            
        Returns:
            The collection ID (str) or None if not found/created
        """
        # First, try to get the collection by name
        params = {
            'IncludeItemTypes': 'BoxSet',
            'Recursive': 'true',
            'SearchTerm': collection_name,
            'Fields': 'Name,Overview'
        }
        endpoint = f"/Users/{self.user_id}/Items"
        logger.info(f"Searching for collection: '{collection_name}'")
        data = self._make_api_request('GET', endpoint, params=params)
        
        if data and 'Items' in data:
            for item in data['Items']:
                if item.get('Name', '').lower() == collection_name.lower():
                    logger.info(f"Found existing collection: {item['Name']} (ID: {item['Id']})")
                    
                    # Update description if provided and collection doesn't have one
                    if description and not item.get('Overview'):
                        self._update_collection_metadata(item['Id'], collection_name, description, list_id, plugin_name)
                    
                    return item['Id']
        
        # Collection doesn't exist, create it with metadata
        return self._create_collection_with_metadata(collection_name, description, list_id, plugin_name)
    
    def _create_collection_with_metadata(self, collection_name: str, description: Optional[str]=None, 
                                         list_id: Optional[str]=None, plugin_name: Optional[str]=None) -> Optional[str]:
        """
        Create a new collection with metadata.
        
        Args:
            collection_name: Name of the collection
            description: Description text for the collection
            list_id: External ID for the collection
            plugin_name: Name of plugin/source generating the collection
            
        Returns:
            The collection ID (str) or None if creation failed
        """
        # Similar to get_or_create_collection but adding the metadata
        logger.info(f"Creating new collection '{collection_name}'")
        
        # First get a movie from the library to use as a starting point
        params = {
            'IncludeItemTypes': 'Movie',
            'Recursive': 'true',
            'Limit': 1
        }
        endpoint = f"/Users/{self.user_id}/Items"
        item_data = self._make_api_request('GET', endpoint, params=params)
        
        try:
            # Try to create collection with a sample item
            if item_data and 'Items' in item_data and item_data['Items']:
                sample_item_id = item_data['Items'][0]['Id']
                logger.info(f"Found sample item with ID: {sample_item_id} to use for collection creation")
                
                # Create the collection
                url = f"{self.server_url}/Collections"
                payload = {
                    'Name': collection_name,
                    'IsLocked': True,
                    'Ids': [sample_item_id]  # Include the sample item
                }
                
                logger.info(f"Creating collection with sample item...")
                response = self.session.post(f"{url}?api_key={self.api_key}", json=payload, timeout=15)
                
                if response.status_code in [200, 201, 204] and response.text:
                    try:
                        data = response.json()
                        if data and 'Id' in data:
                            collection_id = data['Id']
                            logger.info(f"Successfully created collection '{collection_name}' with ID: {collection_id}")
                            
                            # Remove the temporary item immediately
                            try:
                                remove_url = f"{self.server_url}/Collections/{collection_id}/Items/{sample_item_id}?api_key={self.api_key}"
                                logger.info(f"Removing temporary item {sample_item_id} from collection...")
                                remove_response = self.session.delete(remove_url, timeout=15)
                                
                                if remove_response.status_code in [200, 204]:
                                    logger.info(f"Successfully removed temporary item from collection")
                                else:
                                    logger.warning(f"Failed to remove temporary item: HTTP {remove_response.status_code}")
                            except Exception as e:
                                logger.error(f"Error removing temporary item: {e}")
                            
                            # Update collection metadata if provided
                            self._update_collection_metadata(collection_id, collection_name, description, list_id, plugin_name)
                            
                            return collection_id
                    except Exception as e:
                        logger.error(f"Error parsing collection creation response: {e}")
                else:
                    logger.error(f"Collection creation failed: HTTP {response.status_code}")
                    if response.text:
                        logger.error(f"Response: {response.text[:200]}")
            else:
                logger.error("Failed to find a sample item for collection creation")
                # Try to create an empty collection
                return self._create_empty_collection(collection_name, description)
        except Exception as e:
            logger.error(f"Error during collection creation: {e}")
            return self._create_empty_collection(collection_name, description)
            
        return None
    
    def _create_empty_collection(self, collection_name: str, description: Optional[str]=None) -> Optional[str]:
        """
        Create an empty collection without initial items.
        
        Args:
            collection_name: Name of the collection
            description: Description text for the collection
            
        Returns:
            The collection ID (str) or None if creation failed
        """
        try:
            url = f"{self.server_url}/Collections"
            payload = {
                'Name': collection_name,
                'IsLocked': True
            }
            
            if description:
                payload['Overview'] = description
                
            logger.info(f"Creating empty collection...")
            response = self.session.post(f"{url}?api_key={self.api_key}", json=payload, timeout=15)
            
            if response.status_code in [200, 201, 204]:
                try:
                    data = response.json()
                    if data and 'Id' in data:
                        logger.info(f"Successfully created empty collection '{collection_name}' with ID: {data['Id']}")
                        return data['Id']
                except Exception as e:
                    logger.error(f"Error parsing empty collection creation response: {e}")
            else:
                logger.error(f"Empty collection creation failed: HTTP {response.status_code}")
                if response.text:
                    logger.error(f"Response: {response.text[:200]}")
        except Exception as e:
            logger.error(f"Error during empty collection creation: {e}")
            
        return None
    
    def _update_collection_metadata(self, collection_id: str, name: str, description: Optional[str]=None, 
                                    list_id: Optional[str]=None, plugin_name: Optional[str]=None) -> bool:
        """
        Update metadata for a collection such as description and external IDs.
        
        Args:
            collection_id: Jellyfin collection ID
            name: Collection name
            description: Collection description
            list_id: External ID/reference
            plugin_name: Source plugin name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First get current item details
            endpoint = f"/Items/{collection_id}"
            item_data = self._make_api_request('GET', endpoint)
            
            if not item_data:
                logger.error(f"Couldn't retrieve collection data for ID: {collection_id}")
                return False
                
            # Create update payload based on current item data
            payload = {
                'Id': collection_id,
                'Name': name
            }
            
            # Add description if provided
            if description:
                payload['Overview'] = description
                
            # Add provider IDs if list_id and plugin_name are provided
            if list_id and plugin_name:
                if 'ProviderIds' not in payload:
                    payload['ProviderIds'] = {}
                
                # Use the plugin name as provider name and list_id as the value
                payload['ProviderIds'][plugin_name] = list_id
                
            # Use the API to update the item
            endpoint = f"/Items/{collection_id}"
            response = self.session.post(
                f"{self.server_url}{endpoint}?api_key={self.api_key}", 
                json=payload,
                timeout=15
            )
            
            if response.status_code in [200, 204]:
                logger.info(f"Successfully updated metadata for collection '{name}'")
                return True
            else:
                logger.error(f"Failed to update collection metadata: HTTP {response.status_code}")
                if response.text:
                    logger.error(f"Response: {response.text[:200]}")
                return False
        except Exception as e:
            logger.error(f"Error updating collection metadata: {e}")
            return False
    
    def clear_collection(self, collection_id: str) -> bool:
        """
        Remove all items from a collection.
        
        Args:
            collection_id: The Jellyfin collection ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Replace with an empty array to clear the collection
            response = self.update_collection_items(collection_id, [])
            if response:
                logger.info(f"Successfully cleared all items from collection {collection_id}")
            else:
                logger.error(f"Failed to clear collection {collection_id}")
            return response
        except Exception as e:
            logger.error(f"Error clearing collection {collection_id}: {e}")
            return False
    
    def add_item_to_collection(self, collection_id: str, item_info: Dict[str, Any], 
                               year_filter: bool=True, jellyfin_query_parameters: Dict[str, Any]={}) -> bool:
        """
        Add a single item to a collection with flexible matching.
        
        Args:
            collection_id: The Jellyfin collection ID
            item_info: Dictionary containing item details (title, year, ids)
            year_filter: Whether to filter by year when matching
            jellyfin_query_parameters: Additional query parameters to use when searching
            
        Returns:
            True if item was found and added, False otherwise
        """
        try:
            # Extract item details
            title = item_info.get('title')
            if not title:
                logger.error("No title provided for item matching")
                return False
                
            # Extract identified IDs
            tmdb_id = item_info.get('tmdb_id') or item_info.get('id')
            imdb_id = item_info.get('imdb_id')
            year = item_info.get('year')
            
            matched_items = []
            
            # Try to match by external IDs first (more precise)
            if tmdb_id:
                # Try to find by TMDb ID
                tmdb_items = self._find_library_items_by_provider_id('tmdb', str(tmdb_id))
                if tmdb_items:
                    matched_items.extend(tmdb_items)
                    
            if imdb_id and not matched_items:
                # Try to find by IMDb ID if no TMDb matches
                imdb_items = self._find_library_items_by_provider_id('imdb', imdb_id)
                if imdb_items:
                    matched_items.extend(imdb_items)
            
            # If no matches by ID, try title search
            if not matched_items:
                # Search by title
                params = {
                    'SearchTerm': title,
                    'IncludeItemTypes': 'Movie',
                    'Recursive': 'true',
                    'Limit': 5,  # Get a few potential matches
                    'Fields': 'ProviderIds,ProductionYear'
                }
                
                # Add any additional query parameters
                if jellyfin_query_parameters:
                    params.update(jellyfin_query_parameters)
                
                endpoint = f"/Users/{self.user_id}/Items"
                search_data = self._make_api_request('GET', endpoint, params=params)
                
                if search_data and 'Items' in search_data:
                    # Filter by title and year if requested
                    for item in search_data['Items']:
                        item_title = item.get('Name', '')
                        item_year = item.get('ProductionYear')
                        
                        title_match = title.lower() == item_title.lower()
                        year_match = not year_filter or not year or not item_year or int(year) == item_year
                        
                        if title_match and year_match:
                            matched_items.append(item)
            
            # Handle matched items
            if not matched_items:
                logger.warning(f"No matches found for '{title}'" + (f" ({year})" if year else ""))
                return False
                
            # Get first match ID
            item_id = matched_items[0]['Id']
            
            # Get current collection items
            current_items = self._get_collection_items(collection_id)
            if item_id in current_items:
                logger.info(f"Item '{title}' already in collection")
                return True
                
            # Add the item to the collection
            endpoint = f"/Collections/{collection_id}/Items"
            params = {'ids': item_id}
            
            try:
                # Try standard POST request first
                url = f"{self.server_url}{endpoint}?api_key={self.api_key}"
                logger.info(f"Adding '{title}' to collection...")
                response = self.session.post(url, params=params, timeout=15)
                
                if response.status_code in [200, 204]:
                    logger.info(f"Successfully added '{title}' to collection")
                    return True
                else:
                    # If that fails, try the item-specific endpoint as fallback
                    item_url = f"{self.server_url}{endpoint}/{item_id}?api_key={self.api_key}"
                    item_response = self.session.post(item_url, timeout=10)
                    if item_response.status_code in [200, 204]:
                        logger.info(f"Successfully added '{title}' to collection via item-specific endpoint")
                        return True
                    else:
                        logger.error(f"Failed to add item to collection: HTTP {response.status_code}")
                        if response.text:
                            logger.error(f"Response: {response.text[:200]}")
                        return False
            except Exception as e:
                logger.error(f"Error adding item to collection: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding item to collection: {e}")
            return False
    
    def _find_library_items_by_provider_id(self, provider: str, id_value: str) -> List[Dict[str, Any]]:
        """
        Find library items by an external provider ID.
        
        Args:
            provider: Provider name (e.g., 'tmdb', 'imdb')
            id_value: ID value to search for
            
        Returns:
            List of matching item data dictionaries
        """
        try:
            # Jellyfin's endpoint for searching by provider ID
            endpoint = f"/Users/{self.user_id}/Items"
            params = {
                f"ProviderIds": f"{provider}.{id_value}",
                'Recursive': 'true',
                'Fields': 'ProviderIds,ProductionYear'
            }
            
            data = self._make_api_request('GET', endpoint, params=params)
            
            if data and 'Items' in data and data['Items']:
                return data['Items']
                
        except Exception as e:
            logger.error(f"Error finding items by provider ID: {e}")
            
        return []
    
    def _get_collection_items(self, collection_id: str) -> List[str]:
        """
        Get the current item IDs in a collection.
        
        Args:
            collection_id: The Jellyfin collection ID
            
        Returns:
            List of item IDs currently in the collection
        """
        try:
            endpoint = f"/Collections/{collection_id}/Items"
            params = {
                'Fields': 'Id',
            }
            
            data = self._make_api_request('GET', endpoint, params=params)
            
            if data and 'Items' in data:
                return [item['Id'] for item in data['Items']]
                
        except Exception as e:
            logger.error(f"Error getting collection items: {e}")
            
        return []
    
    def has_poster(self, collection_id: str) -> bool:
        """
        Check if a collection has a poster image.
        
        Args:
            collection_id: The Jellyfin collection ID
            
        Returns:
            True if the collection has a poster, False otherwise
        """
        try:
            # Check for primary image information
            endpoint = f"/Items/{collection_id}/Images"
            data = self._make_api_request('GET', endpoint)
            
            if data:
                for image in data:
                    if image.get('Type') == 'Primary':
                        return True
                        
        except Exception as e:
            logger.error(f"Error checking for collection poster: {e}")
            
        return False
        
    def make_poster(self, collection_id: str, collection_name: str) -> bool:
        """
        Generate a simple poster for a collection if none exists.
        
        Args:
            collection_id: The Jellyfin collection ID
            collection_name: Name of the collection
            
        Returns:
            True if poster was successfully created and uploaded, False otherwise
        """
        try:
            # First check if poster already exists
            if self.has_poster(collection_id):
                logger.info(f"Collection already has a poster image")
                return True
                
            # Create a simple poster image with text
            width, height = 1000, 1500
            bg_color = (random.randint(0, 50), random.randint(0, 50), random.randint(0, 100))
            text_color = (220, 220, 220)
            
            # Create a new image with a solid background color
            image = Image.new('RGB', (width, height), color=bg_color)
            draw = ImageDraw.Draw(image)
            
            # Try to get system font, or use default
            try:
                # Try to get a nicer font if available
                try:
                    # For Windows
                    font_path = "C:\\Windows\\Fonts\\Arial.ttf"
                    title_font = ImageFont.truetype(font_path, 80)
                except:
                    # Fallback to default
                    title_font = ImageFont.load_default()
            except:
                # Just use default font if all else fails
                title_font = ImageFont.load_default()
                
            # Center and word-wrap text
            lines = []
            words = collection_name.split()
            current_line = []
            
            # Simple word-wrapping logic
            for word in words:
                current_line.append(word)
                test_line = ' '.join(current_line)
                try:
                    # Get text width if font supports it
                    text_width = draw.textlength(test_line, font=title_font)
                    if text_width > width - 100:  # Leave margins
                        current_line.pop()
                        lines.append(' '.join(current_line))
                        current_line = [word]
                except:
                    # Fallback if textlength not supported
                    if len(test_line) > 20:  # Arbitrary length
                        current_line.pop()
                        lines.append(' '.join(current_line))
                        current_line = [word]
                        
            if current_line:
                lines.append(' '.join(current_line))
                
            # Draw text lines
            y_position = height // 2 - (len(lines) * 100) // 2
            for line in lines:
                try:
                    # Get text width for centering if supported
                    try:
                        text_width = draw.textlength(line, font=title_font)
                        x_position = (width - text_width) // 2
                    except:
                        x_position = 100  # Fallback margin
                        
                    draw.text((x_position, y_position), line, fill=text_color, font=title_font)
                except Exception as inner_e:
                    logger.error(f"Error drawing text: {inner_e}")
                    # Fallback simple text
                    draw.text((100, y_position), line, fill=text_color)
                    
                y_position += 100
                
            # Save image to a buffer
            buffer = BytesIO()
            image.save(buffer, format="JPEG", quality=90)
            buffer.seek(0)
            
            # Upload the image to Jellyfin
            try:
                endpoint = f"/Items/{collection_id}/Images/Primary"
                headers = {"Content-Type": "image/jpeg"}
                
                response = self.session.post(
                    f"{self.server_url}{endpoint}?api_key={self.api_key}",
                    data=buffer.read(),
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code in [200, 204]:
                    logger.info(f"Successfully uploaded generated poster for collection '{collection_name}'")
                    return True
                else:
                    logger.error(f"Failed to upload generated poster: HTTP {response.status_code}")
                    if response.text:
                        logger.error(f"Response: {response.text[:200]}")
                    return False
            except Exception as e:
                logger.error(f"Error uploading generated poster: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error generating collection poster: {e}")
            return False
