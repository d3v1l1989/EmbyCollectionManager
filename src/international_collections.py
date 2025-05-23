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

def generate_country_collections() -> List[Dict[str, Any]]:
    """Generate collections based on countries with strong film traditions."""
    logger.info("Generating country-based collections")
    
    # Dictionary of countries and their ISO 3166-1 codes
    countries = {
        "French Cinema": "FR",
        "Italian Cinema": "IT",
        "Japanese Cinema": "JP",
        "Korean Cinema": "KR",
        "Spanish Cinema": "ES",
        "Indian Cinema": "IN",
        "Chinese Cinema": "CN",
        "German Cinema": "DE",
        "British Cinema": "GB",
        "Swedish Cinema": "SE",
        "Danish Cinema": "DK",
        "Norwegian Cinema": "NO",
        "Mexican Cinema": "MX",
        "Brazilian Cinema": "BR",
        "Australian Cinema": "AU",
        "Russian Cinema": "RU",
        "Canadian Cinema": "CA",
        "Hong Kong Cinema": "HK",
        "Thai Cinema": "TH",
        "Turkish Cinema": "TR",
        "Iranian Cinema": "IR",
        "Polish Cinema": "PL",
        "Argentine Cinema": "AR",
        "Czech Cinema": "CZ",
        "Israeli Cinema": "IL"
    }
    
    recipes = []
    
    for country_name, country_code in countries.items():
        recipes.append({
            "name": country_name,
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "with_original_language": country_code.lower(),
                "sort_by": "vote_average.desc",
                "vote_count.gte": 50
            },
            "item_limit": 30,
            "target_servers": ["emby"]
        })
    
    logger.info(f"Generated {len(recipes)} country-based collections")
    return recipes

def generate_language_collections() -> List[Dict[str, Any]]:
    """Generate collections based on languages (independent of country)."""
    logger.info("Generating language-based collections")
    
    # Dictionary of languages and their ISO 639-1 codes
    languages = {
        "Films in Arabic": "ar",
        "Films in Bengali": "bn",
        "Films in Dutch": "nl",
        "Films in Finnish": "fi",
        "Films in Greek": "el",
        "Films in Hebrew": "he",
        "Films in Hindi": "hi",
        "Films in Hungarian": "hu",
        "Films in Indonesian": "id",
        "Films in Mandarin": "zh",
        "Films in Persian": "fa",
        "Films in Portuguese": "pt",
        "Films in Romanian": "ro",
        "Films in Tamil": "ta",
        "Films in Ukrainian": "uk",
        "Films in Vietnamese": "vi"
    }
    
    recipes = []
    
    for language_name, language_code in languages.items():
        recipes.append({
            "name": language_name,
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "with_original_language": language_code,
                "sort_by": "popularity.desc",
                "vote_count.gte": 20
            },
            "item_limit": 25,
            "target_servers": ["emby"]
        })
    
    logger.info(f"Generated {len(recipes)} language-based collections")
    return recipes

def generate_world_cinema_collections() -> List[Dict[str, Any]]:
    """Generate collections for regional cinema groups."""
    logger.info("Generating world cinema collections")
    
    recipes = [
        {
            "name": "Nordic Cinema",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "with_original_language": "sv,da,no,fi,is",  # Swedish, Danish, Norwegian, Finnish, Icelandic
                "sort_by": "vote_average.desc",
                "vote_count.gte": 50
            },
            "item_limit": 40,
            "target_servers": ["emby"]
        },
        {
            "name": "Eastern European Cinema",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "with_original_language": "ru,pl,cs,hu,ro,bg,uk,sr,hr,sk",  # Russian, Polish, Czech, Hungarian, Romanian, Bulgarian, Ukrainian, Serbian, Croatian, Slovak
                "sort_by": "vote_average.desc",
                "vote_count.gte": 30
            },
            "item_limit": 40,
            "target_servers": ["emby"]
        },
        {
            "name": "Latin American Cinema",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "with_original_language": "es,pt",  # Spanish, Portuguese
                "region": "AR,BR,MX,CL,CO,PE,VE",  # Argentina, Brazil, Mexico, Chile, Colombia, Peru, Venezuela
                "sort_by": "vote_average.desc",
                "vote_count.gte": 30
            },
            "item_limit": 40,
            "target_servers": ["emby"]
        },
        {
            "name": "East Asian Cinema",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "with_original_language": "zh,ja,ko",  # Chinese, Japanese, Korean
                "sort_by": "vote_average.desc",
                "vote_count.gte": 100
            },
            "item_limit": 40,
            "target_servers": ["emby"]
        },
        {
            "name": "South Asian Cinema",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "with_original_language": "hi,bn,ta,te,ml,kn",  # Hindi, Bengali, Tamil, Telugu, Malayalam, Kannada
                "sort_by": "vote_average.desc",
                "vote_count.gte": 30
            },
            "item_limit": 40,
            "target_servers": ["emby"]
        },
        {
            "name": "Middle Eastern Cinema",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "with_original_language": "ar,fa,he,tr",  # Arabic, Farsi, Hebrew, Turkish
                "sort_by": "vote_average.desc",
                "vote_count.gte": 20
            },
            "item_limit": 40,
            "target_servers": ["emby"]
        }
    ]
    
    logger.info(f"Generated {len(recipes)} world cinema collections")
    return recipes

def main():
    """Main function to generate all international collections."""
    api_key = get_tmdb_api_key()
    if not api_key:
        logger.error("Cannot generate recipes without a valid TMDb API key")
        return
    
    country_collections = generate_country_collections()
    language_collections = generate_language_collections()
    world_cinema_collections = generate_world_cinema_collections()
    
    all_collections = country_collections + language_collections + world_cinema_collections
    
    print(f"Generated {len(all_collections)} international collections")
    
    # Print sample collections
    for i, recipe in enumerate(all_collections[:5]):
        print(f"Sample {i+1}: {recipe['name']}")

if __name__ == "__main__":
    main()
