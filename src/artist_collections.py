import os
import logging
from typing import List, Dict, Any, Optional
import yaml
import requests
import time

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
        
        # Basic rate limiting - TMDb allows 40 requests per 10 seconds
        time.sleep(0.25)  # 250ms pause between requests
        
        return response.json()
    except Exception as e:
        logger.error(f"Error making request to {endpoint}: {str(e)}")
        return {}

def generate_cinematographer_collections(api_key: str) -> List[Dict[str, Any]]:
    """Generate collections based on renowned cinematographers."""
    logger.info("Generating cinematographer collections")
    
    # List of famous cinematographers
    cinematographers = [
        "Roger Deakins",
        "Emmanuel Lubezki",
        "Janusz Kamiński",
        "Robert Richardson",
        "Conrad L. Hall",
        "Vittorio Storaro",
        "Hoyte van Hoytema",
        "Gordon Willis",
        "Darius Khondji",
        "Sven Nykvist",
        "Greig Fraser",
        "Bradford Young",
        "Rodrigo Prieto",
        "Linus Sandgren",
        "Rachel Morrison"
    ]
    
    recipes = []
    for cinematographer in cinematographers:
        # Search for the cinematographer's ID
        search_response = tmdb_request("search/person", api_key, {"query": cinematographer})
        results = search_response.get("results", [])
        
        if not results:
            logger.warning(f"No results found for cinematographer: {cinematographer}")
            continue
        
        person_id = results[0]["id"]
        
        # Get person details to confirm they're a cinematographer
        person_details = tmdb_request(f"person/{person_id}", api_key)
        if "cinematographer" not in person_details.get("known_for_department", "").lower():
            logger.info(f"Skipping {cinematographer} as they're not primarily a cinematographer")
        
        recipes.append({
            "name": f"Films Shot by {cinematographer}",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "with_crew": str(person_id),
                "sort_by": "vote_average.desc",
                "vote_count.gte": 30
            },
            "item_limit": 25,
            "target_servers": ["emby"]
        })
    
    logger.info(f"Generated {len(recipes)} cinematographer collections")
    return recipes

def generate_composer_collections(api_key: str) -> List[Dict[str, Any]]:
    """Generate collections based on film composers."""
    logger.info("Generating composer collections")
    
    # List of famous film composers
    composers = [
        "John Williams",
        "Hans Zimmer",
        "Ennio Morricone",
        "Howard Shore",
        "James Horner",
        "Danny Elfman",
        "Bernard Herrmann",
        "Thomas Newman",
        "Alexandre Desplat",
        "Max Steiner",
        "Jerry Goldsmith",
        "John Barry",
        "Trent Reznor",
        "Atticus Ross",
        "Jóhann Jóhannsson",
        "Ryuichi Sakamoto",
        "Toru Takemitsu",
        "Michael Giacchino",
        "Jonny Greenwood",
        "Hildur Guðnadóttir"
    ]
    
    recipes = []
    for composer in composers:
        # Search for the composer's ID
        search_response = tmdb_request("search/person", api_key, {"query": composer})
        results = search_response.get("results", [])
        
        if not results:
            logger.warning(f"No results found for composer: {composer}")
            continue
        
        person_id = results[0]["id"]
        
        # Get person details to confirm they're a composer
        person_details = tmdb_request(f"person/{person_id}", api_key)
        if "composer" not in person_details.get("known_for_department", "").lower() and "music" not in person_details.get("known_for_department", "").lower():
            logger.info(f"Skipping {composer} as they're not primarily a composer")
        
        recipes.append({
            "name": f"Films Scored by {composer}",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "with_crew": str(person_id),
                "sort_by": "vote_average.desc",
                "vote_count.gte": 30
            },
            "item_limit": 25,
            "target_servers": ["emby"]
        })
    
    logger.info(f"Generated {len(recipes)} composer collections")
    return recipes

def generate_more_franchise_collections(api_key: str) -> List[Dict[str, Any]]:
    """Generate additional franchise collections beyond what's in the main generator."""
    logger.info("Generating additional franchise collections")
    
    # Additional known franchise collection IDs
    additional_franchise_ids = [
        115575, # Dragon Ball
        435259, # Demon Slayer
        11249,  # Men in Black Collection
        2344,   # The Lord of the Rings Collection
        86066,  # The Incredibles Collection
        91361,  # Halloween Collection
        9485,   # The Fast and the Furious Collection
        158,    # Halloween Collection (Original)
        645,    # James Bond Collection
        2602,   # Back to the Future Collection
        2806,   # American Pie Collection
        295,    # Pirates of the Caribbean Collection
        387,    # Police Academy Collection
        84,     # Scream Collection
        87359,  # Mission: Impossible Collection
        1241,   # Harry Potter Collection
        264,    # Rocky Collection
        33514,  # Transformers Collection
        2467,   # Friday the 13th Collection
        3186,   # A Nightmare on Elm Street Collection
        2833,   # Final Destination Collection
        7180,   # Despicable Me Collection
        8764,   # Narnia Collection
        10194,  # Toy Story Collection
        10455,  # Die Hard Collection
        119050, # Mean Girls Collection
        86066,  # The Incredibles Collection
        86825,  # Wonder Woman Collection
        34055,  # Cloudy with a Chance of Meatballs Collection
        404609, # Joker Collection
        531241, # Guardians of the Galaxy Collection
        9387,   # The Texas Chainsaw Massacre Collection
        86825,  # Wonder Woman Collection
        87096,  # Avengers Collection
        86066,  # The Incredibles Collection
        9485,   # The Fast and the Furious Collection
        2980,   # Pirates of the Caribbean Collection
        86311,  # Marvel Cinematic Universe
        131296, # DC Extended Universe
        173710, # Indiana Jones Collection
        86825,  # Wonder Woman Collection
        9485,   # Fast & Furious Collection
        295,    # Pirates of the Caribbean Collection
        2150,   # The Godfather Collection
        86067,  # Finding Nemo Collection
        8091,   # Alien Collection
        87359,  # Mission: Impossible Collection
        8580,   # Predator Collection
        5039,   # Saw Collection
        528,    # The Terminator Collection
        1570,   # Die Hard Collection
        111502, # Top Gun Collection
        748,    # The Exorcist Collection
        9398,   # Planet of the Apes Collection
        87359,  # Mission: Impossible Collection
        8091,   # Alien Collection
        2150,   # The Godfather Collection
        1570,   # Die Hard Collection
        9398,   # Planet of the Apes Collection
        1241,   # Harry Potter Collection
        86311,  # Marvel Cinematic Universe
        131296, # DC Extended Universe
        645,    # James Bond Collection
        1570,   # Die Hard Collection
        10195,  # Twilight Collection
        4246,   # Mad Max Collection
        531840, # Knives Out Collection
    ]
    
    # Remove duplicates
    franchise_ids = list(set(additional_franchise_ids))
    
    recipes = []
    for collection_id in franchise_ids:
        try:
            collection_details = tmdb_request(f"collection/{collection_id}", api_key)
            
            if not collection_details.get("name"):
                logger.warning(f"No collection found for ID: {collection_id}")
                continue
            
            recipes.append({
                "name": collection_details["name"],
                "source_type": "tmdb_series_collection",
                "tmdb_collection_id": collection_id,
                "target_servers": ["emby"],
                "sort_by": "release_date"
            })
        except Exception as e:
            logger.error(f"Error processing collection ID {collection_id}: {str(e)}")
    
    logger.info(f"Generated {len(recipes)} additional franchise collections")
    return recipes

def main():
    """Main function to generate all artist-related collections."""
    api_key = get_tmdb_api_key()
    if not api_key:
        logger.error("Cannot generate recipes without a valid TMDb API key")
        return
    
    cinematographer_collections = generate_cinematographer_collections(api_key)
    composer_collections = generate_composer_collections(api_key)
    franchise_collections = generate_more_franchise_collections(api_key)
    
    all_collections = cinematographer_collections + composer_collections + franchise_collections
    
    print(f"Generated {len(all_collections)} artist and franchise collections")
    
    # Print sample collections
    for i, recipe in enumerate(all_collections[:5]):
        print(f"Sample {i+1}: {recipe['name']}")

if __name__ == "__main__":
    main()
