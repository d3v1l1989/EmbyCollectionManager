"""
MDBList Client for Emby Collection Manager

This module provides a client for interacting with the MDBList API
to retrieve movie and TV show lists from various sources.
"""

import requests
import time
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class MDBListClient:
    """
    Client for interacting with the MDBList API.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the MDBList client.
        
        Args:
            api_key: MDBList API key
        """
        self.api_key = api_key
        self.base_url = "https://api.mdblist.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Emby Collection Manager/1.0'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Make a request to the MDBList API with rate limiting.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response or None if error
        """
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
            
        if params is None:
            params = {}
            
        params['apikey'] = self.api_key
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.debug(f"Making MDBList API request: {url}")
            response = self.session.get(url, params=params)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.error("MDBList API authentication failed. Check your API key.")
                return None
            elif response.status_code == 429:
                logger.warning("MDBList API rate limit exceeded. Waiting 60 seconds...")
                time.sleep(60)
                return self._make_request(endpoint, params)
            else:
                logger.error(f"MDBList API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error making MDBList API request: {e}")
            return None
            
    def get_list_items(self, list_id: str, limit: int = 0) -> List[Dict[str, Any]]:
        """
        Get items from an MDBList list.
        
        Args:
            list_id: MDBList list ID or URL
            limit: Maximum number of items to return (0 = no limit)
            
        Returns:
            List of movie/TV show items
        """
        # Extract list ID from URL if needed
        if list_id.startswith('http'):
            list_id = self._extract_list_id_from_url(list_id)
            
        if not list_id:
            logger.error("Invalid MDBList list ID or URL")
            return []
            
        logger.info(f"Fetching MDBList items for list: {list_id} (limit: {'unlimited' if limit == 0 else limit})")
        
        all_items = []
        offset = 0
        batch_size = 1000  # MDBList API limit per request
        page_num = 1
        
        while True:
            # Calculate how many items to request in this batch
            if limit > 0:
                remaining_items = limit - len(all_items)
                if remaining_items <= 0:
                    break
                current_batch_size = min(batch_size, remaining_items)
            else:
                current_batch_size = batch_size
            
            params = {
                'limit': current_batch_size,
                'offset': offset
            }
            
            logger.debug(f"Fetching page {page_num} (offset: {offset}, limit: {current_batch_size}) for MDBList list: {list_id}")
            
            # Use the correct MDBList API endpoint format
            response = self._make_request(f"lists/{list_id}/items", params)
            
            if not response:
                logger.error(f"Failed to fetch page {page_num} for MDBList list: {list_id}")
                break
            
            # Debug: Log the actual response structure
            if page_num == 1:  # Only log for first page to avoid spam
                logger.info(f"MDBList API response type: {type(response)}")
                if isinstance(response, dict):
                    logger.info(f"MDBList API response keys: {list(response.keys())}")
                logger.info(f"MDBList API response (first 200 chars): {str(response)[:200]}...")
            
            # Handle MDBList API response format: {'movies': [...], 'shows': [...]}
            if isinstance(response, list):
                items = response
            elif isinstance(response, dict):
                # MDBList API returns movies in 'movies' key and shows in 'shows' key
                movies = response.get('movies', [])
                shows = response.get('shows', [])
                
                # For now, we focus on movies (could extend to shows later)
                items = movies
                
                if page_num == 1 and movies:
                    logger.info(f"Found {len(movies)} movies and {len(shows)} shows in MDBList response")
            else:
                logger.error(f"Unexpected response format for MDBList list {list_id}: {type(response)}")
                break
                
            if not items:
                logger.info(f"No more items found for MDBList list: {list_id} (reached end at page {page_num})")
                break
                
            all_items.extend(items)
            
            # Log progress for large lists
            if len(all_items) % 1000 == 0 or len(items) < batch_size:
                logger.info(f"Fetched {len(all_items)} items so far from MDBList list: {list_id}")
            
            # Check if we've reached the user-specified limit
            if limit > 0 and len(all_items) >= limit:
                all_items = all_items[:limit]
                logger.info(f"Reached specified limit of {limit} items for MDBList list: {list_id}")
                break
                
            # Check if we got fewer items than requested (end of list)
            if len(items) < current_batch_size:
                logger.info(f"Reached end of MDBList list: {list_id} (got {len(items)} items in final page)")
                break
                
            offset += len(items)
            page_num += 1
            
        logger.info(f"Total items fetched from MDBList list '{list_id}': {len(all_items)}")
        return all_items
        
    def _extract_list_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract list ID from MDBList URL.
        
        Args:
            url: MDBList URL (e.g., https://mdblist.com/lists/username/list-name)
            
        Returns:
            List ID or None if invalid
        """
        try:
            parsed = urlparse(url)
            
            # Handle different URL formats
            if 'mdblist.com' in parsed.netloc:
                path_parts = parsed.path.strip('/').split('/')
                
                # Format: /lists/username/list-name
                if len(path_parts) >= 3 and path_parts[0] == 'lists':
                    username = path_parts[1]
                    list_name = path_parts[2]
                    return f"{username}/{list_name}"
                    
                # Format: /lists/list-id (direct ID)
                elif len(path_parts) >= 2 and path_parts[0] == 'lists':
                    return path_parts[1]
                    
            logger.error(f"Unable to extract list ID from MDBList URL: {url}")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing MDBList URL '{url}': {e}")
            return None
            
    def extract_tmdb_ids(self, mdblist_items: List[Dict[str, Any]], media_type: str = 'movie') -> List[int]:
        """
        Extract TMDb IDs from MDBList items.
        
        Args:
            mdblist_items: List of items from MDBList API
            media_type: Type of media ('movie' or 'show')
            
        Returns:
            List of TMDb IDs
        """
        tmdb_ids = []
        
        for i, item in enumerate(mdblist_items):
            try:
                # Debug: Log the item structure for the first few items
                if i < 3:
                    logger.info(f"MDBList item {i+1} structure: {item}")
                
                # MDBList items should have TMDb ID directly
                tmdb_id = None
                
                # MDBList API format: {'id': 524635, 'title': '...', 'imdb_id': 'tt...', ...}
                # The 'id' field appears to be the TMDb ID based on the API response structure
                if 'id' in item:
                    tmdb_id = item['id']
                # Also try other possible field names for compatibility
                elif 'tmdb_id' in item:
                    tmdb_id = item['tmdb_id']
                elif 'tmdb' in item:
                    tmdb_id = item['tmdb']
                elif 'tmdb_id' in item.get('ids', {}):
                    tmdb_id = item['ids']['tmdb_id']
                elif 'tmdb' in item.get('ids', {}):
                    tmdb_id = item['ids']['tmdb']
                    
                # Validate and add TMDb ID
                if tmdb_id and isinstance(tmdb_id, (int, str)):
                    try:
                        tmdb_id = int(tmdb_id)
                        if tmdb_id > 0:
                            tmdb_ids.append(tmdb_id)
                    except ValueError:
                        logger.warning(f"Invalid TMDb ID format in MDBList item: {tmdb_id}")
                        
            except Exception as e:
                logger.warning(f"Error processing MDBList item: {e}")
                
        logger.info(f"Extracted {len(tmdb_ids)} TMDb IDs from {len(mdblist_items)} MDBList items")
        return tmdb_ids
        
    def search_lists(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for MDBList lists.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        params = {
            'q': query,
            'limit': limit
        }
        
        response = self._make_request("search/lists", params)
        
        if response:
            return response.get('results', [])
        else:
            return []
            
    def get_list_details(self, list_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details about an MDBList list.
        
        Args:
            list_id: MDBList list ID
            
        Returns:
            List details or None if error
        """
        if list_id.startswith('http'):
            list_id = self._extract_list_id_from_url(list_id)
            
        if not list_id:
            return None
            
        return self._make_request(f"lists/{list_id}/info")