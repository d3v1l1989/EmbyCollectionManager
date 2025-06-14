import requests
import logging

class TmdbClient:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p"

    def __init__(self, api_key):
        self.api_key = api_key
        self.logger = logging.getLogger("TmdbClient")
        self.session = requests.Session()

    def discover_movies(self, params, page_limit=1):
        """
        Fetch movies from TMDb /discover/movie with given params. Handles pagination up to page_limit.
        If page_limit is None, fetch all available pages.
        Returns a list of movie dicts.
        """
        url = f"{self.BASE_URL}/discover/movie"
        all_results = []
        seen_ids = set()  # Track already seen movie IDs to prevent duplicates
        
        # Start with page 1
        current_page = 1
        total_pages = 1  # Will be updated from the first response
        
        # Continue fetching until we reach the limit or get all pages
        while True:
            if page_limit is not None and current_page > page_limit:
                break
                
            req_params = dict(params)
            req_params["page"] = current_page
            req_params["api_key"] = self.api_key # Add API key per-request
            
            try:
                resp = self.session.get(url, params=req_params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                
                # Get total pages from first response
                if current_page == 1:
                    total_pages = data.get("total_pages", 1)
                    self.logger.info(f"TMDb discover found {total_pages} total pages of results")
                
                # Add new unique results
                results = data.get("results", [])
                for movie in results:
                    if movie["id"] not in seen_ids:
                        seen_ids.add(movie["id"])
                        all_results.append(movie)
                
                # Log progress for large fetches
                if page_limit is None and current_page % 5 == 0:
                    self.logger.info(f"Fetched {current_page}/{total_pages} pages, found {len(all_results)} unique movies")
                
                # Break if we've reached the last page
                if current_page >= total_pages:
                    break
                    
                # Go to next page
                current_page += 1
                
            except requests.RequestException as e:
                self.logger.error(f"TMDb discover_movies failed on page {current_page}: {e}")
                break
                
        self.logger.info(f"Completed TMDb discovery with {len(all_results)} unique movies from {current_page} pages")
        return all_results

    def get_tmdb_series_collection_details(self, collection_id):
        """
        Fetch details for a TMDb collection (movie series). Returns the collection dict, or None on error.
        """
        url = f"{self.BASE_URL}/collection/{collection_id}"
        try:
            # Add API key per-request
            resp = self.session.get(url, params={"api_key": self.api_key}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            self.logger.error(f"TMDb get_tmdb_series_collection_details failed: {e}")
            return None
            
    def get_collection_images(self, collection_id):
        """
        Fetch images specifically for a TMDb collection.
        
        Args:
            collection_id: TMDb collection ID
            
        Returns:
            Dictionary containing images data with 'backdrops' and 'posters' lists,
            or None if there was an error
        """
        url = f"{self.BASE_URL}/collection/{collection_id}/images"
        try:
            # For collections, language should be set to 'en' or null to get all images
            # The 'en-US' sometimes doesn't work for collections
            resp = self.session.get(url, params={"api_key": self.api_key, "language": "en"}, timeout=10)
            resp.raise_for_status()
            self.logger.info(f"Successfully fetched images for TMDb collection {collection_id}")
            return resp.json()
        except requests.RequestException as e:
            self.logger.error(f"TMDb get_collection_images failed: {e}")
            return None

    def get_movie_details(self, movie_id):
        """
        Fetch details for a single TMDb movie. Returns the movie dict, or None on error.
        """
        url = f"{self.BASE_URL}/movie/{movie_id}"
        try:
            # Add API key per-request
            resp = self.session.get(url, params={"api_key": self.api_key}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            self.logger.error(f"TMDb get_movie_details failed: {e}")
            return None
            
    def get_image_url(self, path, size="original"):
        """
        Convert a TMDb image path to a full URL.
        
        Args:
            path: Image path from TMDb API (e.g., '/abc123.jpg')
            size: Image size ('original', 'w500', etc). Default is 'original'
            
        Returns:
            Full image URL or None if path is None/empty
        """
        if not path:
            return None
        return f"{self.IMAGE_BASE_URL}/{size}{path}"

    def get_collection_movies(self, collection_id, limit=None, sort_by='release_date'):
        """
        Fetch the list of movies in a TMDb collection with sorting options.
        
        Args:
            collection_id: TMDb collection ID
            limit: Maximum number of movies to return (None for all)
            sort_by: How to sort the movies ('release_date', 'title', or 'popularity')
            
        Returns:
            List of movie dicts from the collection
        """
        collection_data = self.get_tmdb_series_collection_details(collection_id)
        if not collection_data or 'parts' not in collection_data:
            self.logger.error(f"Failed to get movies for collection {collection_id}")
            return []
            
        # Get all movies from the collection
        movies = collection_data.get('parts', [])
        
        # Sort the movies based on the requested sort method
        if sort_by == 'release_date':
            # Sort by release date (chronological order)
            # Handle cases where release_date might be missing
            movies.sort(key=lambda x: x.get('release_date', '0000-00-00'))
        elif sort_by == 'title':
            # Sort by title
            movies.sort(key=lambda x: x.get('title', '').lower())
        elif sort_by == 'popularity':
            # Sort by popularity (descending)
            movies.sort(key=lambda x: x.get('popularity', 0), reverse=True)
        # If 'order' or 'episode_number' exists in data for ordered collections, use that
        if all('order' in movie for movie in movies):
            movies.sort(key=lambda x: x.get('order', 0))
        
        # Limit the number of movies if requested
        if limit and len(movies) > limit:
            movies = movies[:limit]
            
        self.logger.info(f"Found {len(movies)} movies in collection {collection_id}, sorted by {sort_by}")
        return movies

    def get_artwork_for_collection(self, collection_data):
        """
        Extract poster and backdrop URLs from collection data.
        
        Args:
            collection_data: Collection data from TMDb API
            
        Returns:
            Dict with 'poster' and 'backdrop' URLs (may be None)
        """
        result = {
            'poster': None,
            'backdrop': None
        }
        if not collection_data:
            return result
            
        if 'poster_path' in collection_data and collection_data['poster_path']:
            result['poster'] = self.get_image_url(collection_data['poster_path'])
            
        if 'backdrop_path' in collection_data and collection_data['backdrop_path']:
            result['backdrop'] = self.get_image_url(collection_data['backdrop_path'])
            
        return result

    def search_movies(self, query, page_limit=1):
        """
        Search for movies by title using TMDb search API.
        
        Args:
            query: Movie title to search for
            page_limit: Maximum number of pages to fetch (default 1)
            
        Returns:
            List of movie dictionaries from search results
        """
        url = f"{self.BASE_URL}/search/movie"
        all_results = []
        seen_ids = set()
        
        current_page = 1
        total_pages = 1
        
        while True:
            if page_limit is not None and current_page > page_limit:
                break
                
            params = {
                "api_key": self.api_key,
                "query": query,
                "page": current_page,
                "include_adult": False  # Filter out adult content
            }
            
            try:
                resp = self.session.get(url, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                
                if current_page == 1:
                    total_pages = data.get("total_pages", 1)
                    
                results = data.get("results", [])
                for movie in results:
                    if movie["id"] not in seen_ids:
                        seen_ids.add(movie["id"])
                        all_results.append(movie)
                        
                if current_page >= total_pages:
                    break
                    
                current_page += 1
                
            except requests.RequestException as e:
                self.logger.error(f"TMDb search_movies failed: {e}")
                break
                
        self.logger.debug(f"TMDb search for '{query}' returned {len(all_results)} results")
        return all_results
