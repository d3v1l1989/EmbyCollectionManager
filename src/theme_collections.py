import os
import logging
from typing import List, Dict, Any, Optional
import yaml
import requests

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
    """Make a request to the TMDb API with error handling."""
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

def generate_theme_collections() -> List[Dict[str, Any]]:
    """Generate collections based on specific themes and topics."""
    logger.info("Generating theme-based collections")
    
    # Dictionary of theme names and their corresponding TMDb keyword IDs
    themes = {
        # Story types
        "Heist Movies": 4887,
        "Road Trip Movies": 2236,
        "Revenge Movies": 256227,
        "Coming of Age": 10683,
        "Dystopian": 12565,
        "Post-Apocalyptic": 2964,
        "Time Travel": 4565,
        "Parallel Universe": 3801,
        "Alternate History": 10868,
        "Conspiracy": 10292,
        "Virtual Reality": 14643,
        "Spy": 10161,
        "Cyberpunk": 11099,
        "Fantasy World": 4344,
        "Underdog Story": 162740,
        
        # Settings
        "Space": 11844,
        "Underwater": 10954,
        "Prison": 2181,
        "Jungle": 1903,
        "Desert": 10232,
        "Arctic/Antarctic": 8391,
        "Island": 2482,
        "High School": 6270,
        "Hospital": 10306,
        "Courtroom": 3684,
        
        # Subject matter
        "Sports": 156792,
        "Boxing": 6437,
        "Martial Arts": 4251,
        "War": 2454,
        "Political": 6454,
        "Survival": 9882,
        "Art": 9748,
        "Music": 4344,
        "Dance": 1879,
        "Food": 1055,
        "Fashion": 7046,
        "Chess": 158655,
        "True Story": 9672,
        "Biopic": 1347,
        "Based on Novel": 818,
        "Based on Comic": 9717,
        
        # Holidays and seasons
        "Christmas": 207317,
        "Halloween": 3335,
        "New Year's Eve": 13090,
        "Valentine's Day": 160404,
        "Thanksgiving": 206554,
        "Summer Vacation": 2026,
        "Winter": 3272,
        
        # Relationships
        "Romance": 9840,
        "Friendship": 4472,
        "Family": 10751,
        "Father Son Relationship": 18015,
        "Mother Daughter Relationship": 195444,
        "Sibling Relationship": 11071,
        
        # Other themes
        "Twist Ending": 3626,
        "Mental Illness": 9673,
        "Amnesia": 594,
        "Double Life": 12560,
        "Found Footage": 7103,
        "Mockumentary": 21182,
        "Noir": 9803,
        "Anthology": 7062,
        "Unreliable Narrator": 278069,
    }
    
    recipes = []
    
    for theme_name, keyword_id in themes.items():
        recipes.append({
            "name": f"{theme_name}",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "with_keywords": str(keyword_id),
                "sort_by": "popularity.desc",
                "vote_count.gte": 50
            },
            "item_limit": 30,
            "target_servers": ["emby"]
        })
    
    logger.info(f"Generated {len(recipes)} theme-based collections")
    return recipes

def main():
    """Main function to generate and save theme collections."""
    theme_collections = generate_theme_collections()
    print(f"Generated {len(theme_collections)} theme collections")
    
    # Print sample collections
    for i, recipe in enumerate(theme_collections[:5]):
        print(f"Sample {i+1}: {recipe['name']}")

if __name__ == "__main__":
    main()
