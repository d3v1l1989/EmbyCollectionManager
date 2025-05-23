import os
import requests
import logging
from typing import List, Dict, Any, Optional
import yaml

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_tmdb_api_key() -> Optional[str]:
    """Get TMDb API key from environment or config file."""
    # Try from environment
    api_key = os.getenv("TMDB_API_KEY")
    if api_key and api_key != "YOUR_TMDB_API_KEY":
        return api_key
    
    # Try from YAML config
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            api_key = config.get("TMDB_API_KEY")
            if api_key and api_key != "YOUR_TMDB_API_KEY":
                return api_key
    
    logger.error("No valid TMDb API key found in environment or config.")
    return None

def tmdb_request(endpoint: str, api_key: str, params: Dict = None) -> Dict:
    """Make a request to the TMDb API with error handling and rate limiting."""
    base_url = "https://api.themoviedb.org/3"
    url = f"{base_url}/{endpoint}"
    
    if params is None:
        params = {}
    
    params["api_key"] = api_key
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error making request to {endpoint}: {str(e)}")
        return {}

def generate_studio_collections() -> List[Dict[str, Any]]:
    """Generate collections based on major studios and production companies."""
    logger.info("Generating studio-based collections")
    
    # Dictionary of studio names and their TMDb IDs
    studios = {
        "Pixar": 3,
        "Lucasfilm": 1,
        "Marvel Studios": 420,
        "Warner Bros. Pictures": 174,
        "Universal Pictures": 33,
        "20th Century Studios": 25,
        "Paramount Pictures": 4,
        "Columbia Pictures": 5,
        "Walt Disney Pictures": 2,
        "DreamWorks Animation": 521,
        "Studio Ghibli": 10342,
        "A24": 41077,
        "Lionsgate Films": 1632,
        "New Line Cinema": 12,
        "Focus Features": 10146,
        "Sony Pictures Animation": 2251,
        "BBC Films": 146,
        "Miramax": 14,
        "Amblin Entertainment": 56,
        "Legendary Pictures": 923,
        "Blumhouse Productions": 3172,
        "Metro-Goldwyn-Mayer": 8411,
        "Working Title Films": 10163,
        "Bad Robot": 11461,
        "NEON": 124052,
        "FilmNation Entertainment": 27551,
        "StudioCanal": 694,
        "Netflix": 12177,
        "Amazon Studios": 34982,
        "Apple Studios": 152952
    }
    
    recipes = []
    
    for studio_name, studio_id in studios.items():
        recipes.append({
            "name": f"{studio_name} Films",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "with_companies": str(studio_id),
                "sort_by": "popularity.desc",
                "vote_count.gte": 20
            },
            "item_limit": 30,
            "target_servers": ["emby"]
        })
    
    logger.info(f"Generated {len(recipes)} studio collections")
    return recipes

def main():
    """Main function to generate and save studio collections."""
    api_key = get_tmdb_api_key()
    if not api_key:
        logger.error("Cannot generate recipes without a valid TMDb API key")
        return
    
    studio_collections = generate_studio_collections()
    print(f"Generated {len(studio_collections)} studio collections")
    
    # Print sample collections
    for i, recipe in enumerate(studio_collections[:3]):
        print(f"Sample {i+1}: {recipe['name']}")

if __name__ == "__main__":
    main()
