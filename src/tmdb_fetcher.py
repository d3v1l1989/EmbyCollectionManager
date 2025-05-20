import requests
import logging

class TmdbClient:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key):
        self.api_key = api_key
        self.logger = logging.getLogger("TmdbClient")
        self.session = requests.Session()
        self.session.params = {"api_key": self.api_key}

    def discover_movies(self, params, page_limit=1):
        """
        Fetch movies from TMDb /discover/movie with given params. Handles pagination up to page_limit.
        Returns a list of movie dicts.
        """
        url = f"{self.BASE_URL}/discover/movie"
        all_results = []
        for page in range(1, page_limit+1):
            req_params = dict(params)
            req_params["page"] = page
            try:
                resp = self.session.get(url, params=req_params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                results = data.get("results", [])
                all_results.extend(results)
                if page >= data.get("total_pages", 1):
                    break
            except requests.RequestException as e:
                self.logger.error(f"TMDb discover_movies failed: {e}")
                break
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
