import requests
import logging
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode

class TraktClient:
    """
    Client for interacting with the Trakt.tv API.
    Supports OAuth2 authentication and list/watchlist fetching.
    """
    
    BASE_URL = "https://api.trakt.tv"
    API_VERSION = "2"
    
    def __init__(self, client_id: str, client_secret: str = None, access_token: str = None):
        """
        Initialize Trakt client.
        
        Args:
            client_id: Trakt application client ID
            client_secret: Trakt application client secret (required for OAuth)
            access_token: User access token (if already obtained)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.logger = logging.getLogger("TraktClient")
        self.session = requests.Session()
        
        # Set required headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'trakt-api-version': self.API_VERSION,
            'trakt-api-key': self.client_id
        })
        
        # Add authorization header if access token is available
        if self.access_token:
            self.session.headers['Authorization'] = f'Bearer {self.access_token}'
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """
        Make an API request with error handling and rate limiting.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON data or None on error
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            # Rate limiting - Trakt allows 1000 requests per 5 minutes
            time.sleep(0.31)  # ~300ms between requests to stay under limit
            
            response = self.session.request(method, url, timeout=15, **kwargs)
            response.raise_for_status()
            
            # Handle empty responses (some endpoints return 204 No Content)
            if response.status_code == 204 or not response.content:
                return {}
                
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                self.logger.error("Trakt API authentication failed. Check your credentials.")
            elif e.response.status_code == 403:
                self.logger.error("Trakt API access forbidden. Check your app permissions.")
            elif e.response.status_code == 404:
                self.logger.error(f"Trakt API endpoint not found: {endpoint}")
            elif e.response.status_code == 429:
                self.logger.error("Trakt API rate limit exceeded. Please wait before retrying.")
            else:
                self.logger.error(f"Trakt API HTTP error {e.response.status_code}: {e}")
            return None
            
        except requests.RequestException as e:
            self.logger.error(f"Trakt API request failed: {e}")
            return None
    
    def get_oauth_url(self, redirect_uri: str, state: str = None) -> str:
        """
        Generate OAuth2 authorization URL.
        
        Args:
            redirect_uri: OAuth redirect URI
            state: Optional state parameter for security
            
        Returns:
            Authorization URL
        """
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': redirect_uri
        }
        
        if state:
            params['state'] = state
            
        return f"https://trakt.tv/oauth/authorize?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Optional[Dict]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            redirect_uri: OAuth redirect URI (must match)
            
        Returns:
            Token response or None on error
        """
        if not self.client_secret:
            self.logger.error("Client secret required for token exchange")
            return None
            
        data = {
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = self._make_request('POST', '/oauth/token', json=data)
        
        if response and 'access_token' in response:
            self.access_token = response['access_token']
            self.session.headers['Authorization'] = f'Bearer {self.access_token}'
            self.logger.info("Successfully obtained access token")
            
        return response
    
    def get_user_lists(self, username: str, list_type: str = 'personal') -> List[Dict]:
        """
        Get user's lists.
        
        Args:
            username: Trakt username or 'me' for authenticated user
            list_type: Type of lists ('personal', 'official', 'watchlists', 'all')
            
        Returns:
            List of list objects
        """
        if list_type == 'all':
            endpoint = f"/users/{username}/lists"
        else:
            endpoint = f"/users/{username}/lists/{list_type}"
            
        response = self._make_request('GET', endpoint)
        return response if response else []
    
    def get_list_items(self, username: str, list_slug: str, item_type: str = 'movies') -> List[Dict]:
        """
        Get items from a specific user list.
        
        Args:
            username: Trakt username or 'me' for authenticated user
            list_slug: List slug/ID
            item_type: Type of items to fetch ('movies', 'shows', 'all')
            
        Returns:
            List of items with metadata
        """
        endpoint = f"/users/{username}/lists/{list_slug}/items"
        
        # Add type filter if specified
        params = {}
        if item_type != 'all':
            params['type'] = item_type
            
        response = self._make_request('GET', endpoint, params=params)
        return response if response else []
    
    def get_watchlist(self, username: str = 'me', item_type: str = 'movies') -> List[Dict]:
        """
        Get user's watchlist.
        
        Args:
            username: Trakt username or 'me' for authenticated user
            item_type: Type of items ('movies', 'shows', 'all')
            
        Returns:
            List of watchlist items
        """
        endpoint = f"/users/{username}/watchlist"
        
        params = {}
        if item_type != 'all':
            params['type'] = item_type
            
        response = self._make_request('GET', endpoint, params=params)
        return response if response else []
    
    def get_collection(self, username: str = 'me', item_type: str = 'movies') -> List[Dict]:
        """
        Get user's collection.
        
        Args:
            username: Trakt username or 'me' for authenticated user
            item_type: Type of items ('movies', 'shows', 'all')
            
        Returns:
            List of collection items
        """
        endpoint = f"/users/{username}/collection/{item_type}"
        
        response = self._make_request('GET', endpoint)
        return response if response else []
    
    def extract_tmdb_ids(self, trakt_items: List[Dict], content_type: str = 'movie') -> List[int]:
        """
        Extract TMDb IDs from Trakt API response items.
        
        Args:
            trakt_items: List of items from Trakt API
            content_type: Content type ('movie' or 'show')
            
        Returns:
            List of TMDb IDs
        """
        tmdb_ids = []
        
        for item in trakt_items:
            # Handle different response formats (list items vs watchlist vs collection)
            content_data = None
            
            if content_type in item:
                content_data = item[content_type]
            elif 'movie' in item:
                content_data = item['movie']
            elif 'show' in item:
                content_data = item['show']
            
            if content_data and 'ids' in content_data:
                tmdb_id = content_data['ids'].get('tmdb')
                if tmdb_id:
                    tmdb_ids.append(int(tmdb_id))
                else:
                    title = content_data.get('title', 'Unknown')
                    self.logger.warning(f"No TMDb ID found for '{title}'")
        
        self.logger.info(f"Extracted {len(tmdb_ids)} TMDb IDs from {len(trakt_items)} Trakt items")
        return tmdb_ids
    
    def get_popular_lists(self, limit: int = 20) -> List[Dict]:
        """
        Get popular public lists.
        
        Args:
            limit: Maximum number of lists to return
            
        Returns:
            List of popular lists
        """
        params = {'limit': limit}
        response = self._make_request('GET', '/lists/popular', params=params)
        return response if response else []
    
    def get_trending_lists(self, limit: int = 20) -> List[Dict]:
        """
        Get trending public lists.
        
        Args:
            limit: Maximum number of lists to return
            
        Returns:
            List of trending lists
        """
        params = {'limit': limit}
        response = self._make_request('GET', '/lists/trending', params=params)
        return response if response else []
    
    def search_lists(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search for public lists.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching lists
        """
        params = {'query': query, 'type': 'list', 'limit': limit}
        response = self._make_request('GET', '/search/list', params=params)
        return response if response else []