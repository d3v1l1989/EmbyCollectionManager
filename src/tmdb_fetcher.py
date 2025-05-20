import requests
import logging

class TmdbClient:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p"

    def __init__(self, api_key):
        self.api_key = api_key
        self.logger = logging.getLogger("TmdbClient")
        self.session = requests.Session()
        self.session.params = {"api_key": self.api_key}

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
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            self.logger.error(f"TMDb get_tmdb_series_collection_details failed: {e}")
            return None

    def get_movie_details(self, movie_id):
        """
        Fetch details for a single TMDb movie. Returns the movie dict, or None on error.
        """
        url = f"{self.BASE_URL}/movie/{movie_id}"
        try:
            resp = self.session.get(url, timeout=10)
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
