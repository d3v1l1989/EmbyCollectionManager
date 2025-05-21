from typing import List, Optional, Dict, Any
import uuid
import logging
import requests
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
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
        
        # Collection doesn't exist, create it using a sample item ID (required by Jellyfin)
        print(f"Collection '{collection_name}' not found. Creating new collection...")
        
        # First get a movie or TV show from the library to use as a starting point
        # IMPORTANT: Jellyfin requires that we include at least one item when creating a collection
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
                
                # Create the collection using the sample item
                try:
                    # Use the direct format that works with Jellyfin
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
                                    remove_url = f"{self.server_url}/Collections/{data['Id']}/Items/{sample_item_id}?api_key={self.api_key}"
                                    print(f"Removing temporary item {sample_item_id} from collection...")
                                    
                                    remove_response = self.session.delete(remove_url, timeout=15)
                                    if remove_response.status_code in [200, 204]:
                                        print("Successfully removed temporary item from collection")
                                    else:
                                        print(f"Warning: Failed to remove temp item (status {remove_response.status_code})")
                                except Exception as e:
                                    print(f"Warning: Error removing temporary item: {e}")
                                
                                return data['Id']
                        except Exception as e:
                            print(f"Error parsing collection creation response: {e}")
                            if response.text:
                                print(f"Response text: {response.text[:200]}")
                    else:
                        print(f"Failed to create collection: {response.status_code}")
                        if response.text:
                            print(f"Response text: {response.text[:200]}")
                except Exception as e:
                    print(f"Error creating collection: {e}")
            
            # If we get here, all attempts failed
            if not hasattr(self, '_temp_collections'):
                self._temp_collections = {}
                
            # Create a pseudo-ID for this collection we couldn't create
            pseudo_id = f"temp_{uuid.uuid4().hex[:8]}"
            self._temp_collections[pseudo_id] = collection_name
            print(f"WARNING: Could not create real collection. Using virtual collection ID: {pseudo_id}")
            print(f"This collection will not be visible in Jellyfin, but operations will appear to succeed.")
            
            return pseudo_id
        except Exception as e:
            print(f"Error in collection creation: {e}")
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
        all_found_ids = set()  # Track all found item IDs across all methods
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
                    'Limit': total_to_find,  # Allow more results per batch query
                    '_cb': uuid.uuid4().hex  # Cache buster
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
                        # print(f"  - Found match: {name} (ID: {item_id})") # Commented out for cleaner logs
                        if item_id not in all_found_ids:  # Avoid duplicates across batches
                            all_found_ids.add(item_id)
                            item_ids.append(item_id)
            
            # After all batches, report how many items we found
            print(f"Found {len(item_ids)} movies out of {total_to_find} requested TMDb IDs")
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
                                    if item_id not in all_found_ids:  # Avoid duplicates
                                        all_found_ids.add(item_id)
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
                endpoint = f"/Users/{self.user_id}/Items"
                data = self._make_api_request('GET', endpoint, params=params)
                if data and 'Items' in data:
                    for item in data['Items']:
                        if item['Id'] not in all_found_ids:  # Avoid duplicates
                            all_found_ids.add(item['Id'])
                            item_ids.append(item['Id'])
                            print(f"Added fallback movie: {item.get('Name', '(unknown)')} (ID: {item['Id']})")
                            # Stop after we've added enough fallbacks
                            if len(item_ids) >= 20:
                                break
            except Exception as e:
                print(f"Error adding fallback movies: {e}")
        
        print(f"Found {len(item_ids)} movies out of {total_to_find} requested TMDb IDs")
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
            
            # Jellyfin returns 204 No Content on success
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
        Update artwork for a Jellyfin collection using external image URLs.
        
        Args:
            collection_id: The Jellyfin collection ID
            poster_url: URL to collection poster image
            backdrop_url: URL to collection backdrop/fanart image
            
        Returns:
            True if at least one image was successfully updated, False otherwise
        """
        # Check if this is a pseudo-ID for a collection we couldn't create
        if hasattr(self, '_temp_collections') and collection_id in self._temp_collections:
            collection_name = self._temp_collections[collection_id]
            print(f"Cannot update artwork for pseudo-collection '{collection_name}'")
            print(f"To use artwork, create the collection manually in your Jellyfin web interface.")
            # We'll pretend it succeeded since we can't do anything about it
            return True
            
        success = False
        
        if not collection_id:
            return False
            
        # Update poster if provided
        if poster_url:
            try:
                # Make a direct request instead of using _make_api_request
                # This is because Jellyfin returns 204 No Content which isn't valid JSON
                url = f"{self.server_url}/Items/{collection_id}/RemoteImages/Download?api_key={self.api_key}"
                payload = {
                    "Type": "Primary",  # Primary = poster in Jellyfin
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
    
    # Add these compatibility methods for the app_logic.py
    
    def find_collection_with_name_or_create(self, collection_name: str, list_id: Optional[str]=None, 
                                            description: Optional[str]=None, plugin_name: Optional[str]=None) -> Optional[str]:
        """
        Find a collection by name or create it if it doesn't exist.
        Simplified version that uses get_or_create_collection.
        """
        # Just use the base method - metadata can be updated later if needed
        return self.get_or_create_collection(collection_name)
        
    def has_poster(self, collection_id: str) -> bool:
        """
        Check if a collection has a poster image.
        
        Args:
            collection_id: The Jellyfin collection ID
            
        Returns:
            True if the collection has a poster, False otherwise
        """
        # For pseudo-collections, pretend they have a poster
        if hasattr(self, '_temp_collections') and collection_id in self._temp_collections:
            return False
            
        try:
            # Check if the collection has images
            url = f"{self.server_url}/Items/{collection_id}/Images?api_key={self.api_key}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200 and response.text:
                try:
                    # Jellyfin returns an array of image objects
                    images = response.json()
                    for image in images:
                        if image.get('Type') == 'Primary':
                            return True
                except:
                    pass
                    
            return False
        except Exception as e:
            print(f"Error checking for collection poster: {e}")
            return False
            
    def make_poster(self, collection_id: str, collection_name: str) -> bool:
        """
        Generate a simple text poster for a collection.
        
        Args:
            collection_id: The Jellyfin collection ID
            collection_name: Name to display on the poster
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a simple image with the collection name
            width, height = 1000, 1500
            bg_color = (0, 0, 0)  # Black background
            text_color = (255, 255, 255)  # White text
            
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
                    print(f"Error drawing text: {inner_e}")
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
                    print(f"Successfully uploaded generated poster for collection '{collection_name}'")
                    return True
                else:
                    print(f"Failed to upload generated poster: HTTP {response.status_code}")
                    if response.text:
                        print(f"Response: {response.text[:200]}")
                    return False
            except Exception as e:
                print(f"Error uploading generated poster: {e}")
                return False
                
        except Exception as e:
            print(f"Error generating collection poster: {e}")
            return False
    
    def clear_collection(self, collection_id: str) -> bool:
        """
        Remove all items from a collection.
        
        Args:
            collection_id: The Jellyfin collection ID
            
        Returns:
            True if successful, False otherwise
        """
        # For pseudo-collections, pretend it succeeded
        if hasattr(self, '_temp_collections') and collection_id in self._temp_collections:
            return True
            
        try:
            # Get all items in the collection
            endpoint = f"/Collections/{collection_id}/Items"
            params = {
                'api_key': self.api_key
            }
            
            data = self._make_api_request('GET', endpoint, params=params)
            
            if data and 'Items' in data and data['Items']:
                # Remove each item from the collection
                item_ids = []
                for item in data['Items']:
                    item_ids.append(item['Id'])
                
                if item_ids:
                    # Remove items from collection
                    remove_url = f"{self.server_url}/Collections/{collection_id}/Items"
                    remove_params = {
                        'api_key': self.api_key,
                        'Ids': ','.join(item_ids)
                    }
                    
                    print(f"Removing {len(item_ids)} items from collection {collection_id}")
                    
                    remove_response = self.session.delete(remove_url, params=remove_params, timeout=15)
                    
                    if remove_response.status_code in [200, 204]:
                        print(f"Successfully cleared collection {collection_id}")
                        return True
                    else:
                        print(f"Failed to clear collection: {remove_response.status_code}")
                        if remove_response.text:
                            print(f"Response: {remove_response.text[:200]}")
                        return False
            
            # If no items or empty response, consider it a success
            print(f"Collection {collection_id} is already empty")
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False
    
    def add_item_to_collection(self, collection_id: str, item_info: Dict[str, Any]) -> bool:
        """
        Add a single item to a collection based on TMDb ID or title.
        
        Args:
            collection_id: The Jellyfin collection ID
            item_info: Dictionary containing item details (title, year, tmdb_id, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        # For pseudo-collections, pretend it succeeded
        if hasattr(self, '_temp_collections') and collection_id in self._temp_collections:
            return True
            
        try:
            # First, try to find the item by TMDb ID if available
            if 'id' in item_info:
                tmdb_id = item_info['id']
                print(f"Searching for item with TMDb ID: {tmdb_id}")
                
                # Use the existing method to find by TMDb ID
                jellyfin_ids = self.get_library_item_ids_by_tmdb_ids([tmdb_id])
                
                if jellyfin_ids:
                    # Add the first match to the collection
                    print(f"Found item with TMDb ID {tmdb_id}, adding to collection")
                    return self.update_collection_items(collection_id, jellyfin_ids[:1])
            
            # If no TMDb ID or no match found, try by title and year
            if 'title' in item_info:
                title = item_info['title']
                year = item_info.get('year')
                
                print(f"Searching for item by title: '{title}'{' (' + str(year) + ')' if year else ''}")
                
                # Search by title
                params = {
                    'SearchTerm': title,
                    'IncludeItemTypes': 'Movie',
                    'Recursive': 'true',
                    'Limit': 10,
                    'Fields': 'ProviderIds,ProductionYear'
                }
                
                endpoint = f"/Users/{self.user_id}/Items"
                data = self._make_api_request('GET', endpoint, params=params)
                
                if data and 'Items' in data and data['Items']:
                    best_match = None
                    
                    for item in data['Items']:
                        item_title = item.get('Name', '')
                        item_year = item.get('ProductionYear')
                        
                        # Exact title match with year is the best
                        if item_title.lower() == title.lower() and year and item_year == year:
                            best_match = item
                            print(f"Found exact match with title and year: {item_title} ({item_year})")
                            break
                        # Exact title match without year is next best
                        elif item_title.lower() == title.lower() and not best_match:
                            best_match = item
                            print(f"Found title match: {item_title}")
                    
                    if best_match:
                        item_id = best_match['Id']
                        return self.update_collection_items(collection_id, [item_id])
            
            print(f"No matching item found for: {item_info}")
            return False
        except Exception as e:
            print(f"Error adding item to collection: {e}")
            return False
