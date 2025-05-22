import os
import requests
from datetime import datetime
import yaml
import logging
from typing import List, Dict, Any, Optional
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
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request to {endpoint}: {str(e)}")
        return {}

def generate_genre_recipes(api_key: str) -> List[Dict[str, Any]]:
    """Generate basic genre-based collection recipes."""
    logger.info("Generating genre-based recipes")
    
    genres_data = tmdb_request("genre/movie/list", api_key)
    genres = genres_data.get("genres", [])
    
    if not genres:
        logger.warning("No genres found from TMDb API")
        return []
    
    recipes = []
    for genre in genres:
        recipes.append({
            "name": f"{genre['name']} Movies",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {"with_genres": str(genre['id']), "sort_by": "popularity.desc", "vote_count.gte": 50},
            "item_limit": 30,
            "target_servers": ["emby"]
        })
    
    logger.info(f"Generated {len(recipes)} genre recipes")
    return recipes

def generate_genre_combination_recipes(api_key: str, max_combinations: int = 20) -> List[Dict[str, Any]]:
    """Generate collections based on combinations of two genres."""
    logger.info("Generating genre combination recipes")
    
    genres_data = tmdb_request("genre/movie/list", api_key)
    genres = genres_data.get("genres", [])
    
    if not genres:
        logger.warning("No genres found from TMDb API")
        return []
    
    # Popular genre combinations that work well together
    good_combinations = [
        ("Action", "Adventure"),
        ("Action", "Science Fiction"),
        ("Adventure", "Fantasy"),
        ("Drama", "Romance"),
        ("Comedy", "Romance"),
        ("Crime", "Thriller"),
        ("Horror", "Mystery"),
        ("Drama", "History"),
        ("Animation", "Family"),
        ("Documentary", "History")
    ]
    
    # Create a mapping of genre names to IDs
    genre_map = {genre["name"]: genre["id"] for genre in genres}
    
    recipes = []
    combination_count = 0
    
    # First add the predefined good combinations
    for genre1_name, genre2_name in good_combinations:
        if genre1_name in genre_map and genre2_name in genre_map:
            genre1_id = genre_map[genre1_name]
            genre2_id = genre_map[genre2_name]
            
            recipes.append({
                "name": f"{genre1_name} & {genre2_name} Movies",
                "source_type": "tmdb_discover_individual_movies",
                "tmdb_discover_params": {
                    "with_genres": f"{genre1_id},{genre2_id}", 
                    "sort_by": "popularity.desc", 
                    "vote_count.gte": 75
                },
                "item_limit": 25,
                "target_servers": ["emby"]
            })
            combination_count += 1
    
    # Then add additional combinations if needed to reach max_combinations
    if combination_count < max_combinations:
        # Select most popular genres for additional combinations
        popular_genres = ["Action", "Adventure", "Comedy", "Drama", "Science Fiction", "Fantasy", "Horror", "Thriller"]
        popular_genres = [g for g in popular_genres if g in genre_map]
        
        for i, genre1_name in enumerate(popular_genres):
            for genre2_name in popular_genres[i+1:]:
                if combination_count >= max_combinations:
                    break
                
                # Skip if this combination is already in our predefined list
                if (genre1_name, genre2_name) in good_combinations or (genre2_name, genre1_name) in good_combinations:
                    continue
                
                genre1_id = genre_map[genre1_name]
                genre2_id = genre_map[genre2_name]
                
                recipes.append({
                    "name": f"{genre1_name} & {genre2_name} Movies",
                    "source_type": "tmdb_discover_individual_movies",
                    "tmdb_discover_params": {
                        "with_genres": f"{genre1_id},{genre2_id}", 
                        "sort_by": "popularity.desc", 
                        "vote_count.gte": 75
                    },
                    "item_limit": 25,
                    "target_servers": ["emby"]
                })
                combination_count += 1
    
    logger.info(f"Generated {len(recipes)} genre combination recipes")
    return recipes

def generate_director_recipes(api_key: str) -> List[Dict[str, Any]]:
    """Generate collections for famous directors."""
    logger.info("Generating director-based recipes")
    
    # List of famous directors (expanded)
    directors = [
        # Elite directors with distinctive styles
        "Steven Spielberg",
        "Christopher Nolan",
        "Martin Scorsese",
        "Quentin Tarantino",
        "James Cameron",
        "Peter Jackson",
        "Ridley Scott",
        "Alfred Hitchcock",
        "Stanley Kubrick",
        "David Fincher",
        "Denis Villeneuve",
        "Hayao Miyazaki",
        "Francis Ford Coppola",
        "Wes Anderson",
        "Akira Kurosawa",
        
        # Additional critically acclaimed directors
        "Guillermo del Toro",
        "Spike Lee",
        "Tim Burton",
        "Joel Coen",
        "Ethan Coen",
        "Clint Eastwood",
        "Ang Lee",
        "Ron Howard",
        "Alfonso Cuarón",
        "Darren Aronofsky",
        "David Lynch",
        "Sofia Coppola",
        "Alejandro González Iñárritu",
        "Greta Gerwig",
        "Kathryn Bigelow",
        
        # Influential directors from various eras
        "Ingmar Bergman",
        "Federico Fellini",
        "Orson Welles",
        "John Ford",
        "Woody Allen",
        "Billy Wilder",
        "Werner Herzog",
        "John Carpenter",
        "Sam Raimi",
        "Danny Boyle",
        "Paul Thomas Anderson",
        "Robert Zemeckis",
        "Bong Joon-ho",
        "Andrei Tarkovsky",
        "Sergio Leone"
    ]
    
    recipes = []
    for director in directors:
        # Search for the director's ID
        search_response = tmdb_request("search/person", api_key, {"query": director})
        results = search_response.get("results", [])
        
        if not results:
            logger.warning(f"No results found for director: {director}")
            continue
        
        director_id = results[0]["id"]
        
        recipes.append({
            "name": f"{director} Collection",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "with_people": str(director_id), 
                "sort_by": "vote_average.desc",
                "vote_count.gte": 50
            },
            "item_limit": 15,
            "target_servers": ["emby"]
        })
    
    logger.info(f"Generated {len(recipes)} director recipes")
    return recipes

def generate_actor_recipes(api_key: str) -> List[Dict[str, Any]]:
    """Generate collections for popular actors."""
    logger.info("Generating actor-based recipes")
    
    # List of popular actors (expanded)
    actors = [
        # A-list actors known for blockbusters
        "Tom Hanks",
        "Leonardo DiCaprio",
        "Meryl Streep",
        "Denzel Washington",
        "Jennifer Lawrence",
        "Brad Pitt",
        "Scarlett Johansson",
        "Robert Downey Jr.",
        "Tom Cruise",
        "Viola Davis",
        "Cate Blanchett",
        "Morgan Freeman",
        "Emma Stone",
        "Samuel L. Jackson",
        "Anthony Hopkins",
        
        # Additional acclaimed actors
        "Christian Bale",
        "Joaquin Phoenix",
        "Ryan Gosling",
        "Matt Damon",
        "Hugh Jackman",
        "Natalie Portman",
        "Kate Winslet",
        "Daniel Day-Lewis",
        "Frances McDormand",
        "Amy Adams",
        "Jake Gyllenhaal",
        "Nicole Kidman",
        "Johnny Depp",
        "Charlize Theron",
        "Gary Oldman",
        
        # Icons and legends
        "Harrison Ford",
        "Al Pacino",
        "Robert De Niro",
        "Jack Nicholson",
        "Clint Eastwood",
        "Audrey Hepburn",
        "Marilyn Monroe",
        "Sidney Poitier",
        "James Stewart",
        "Humphrey Bogart",
        
        # Current generation stars
        "Timothée Chalamet",
        "Margot Robbie",
        "Adam Driver",
        "Florence Pugh",
        "Zendaya",
        "Chris Hemsworth",
        "Saoirse Ronan",
        "Mahershala Ali",
        "Michelle Yeoh",
        "Lupita Nyong'o"
    ]
    
    recipes = []
    for actor in actors:
        # Search for the actor's ID
        search_response = tmdb_request("search/person", api_key, {"query": actor})
        results = search_response.get("results", [])
        
        if not results:
            logger.warning(f"No results found for actor: {actor}")
            continue
        
        actor_id = results[0]["id"]
        
        recipes.append({
            "name": f"{actor} Movies",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "with_cast": str(actor_id), 
                "sort_by": "vote_average.desc",
                "vote_count.gte": 50
            },
            "item_limit": 20,
            "target_servers": ["emby"]
        })
    
    logger.info(f"Generated {len(recipes)} actor recipes")
    return recipes

def generate_decade_recipes(api_key: str) -> List[Dict[str, Any]]:
    """Generate collections for movies from different decades."""
    logger.info("Generating decade-based recipes")
    
    decades = [
        {"name": "1950s", "start": "1950-01-01", "end": "1959-12-31"},
        {"name": "1960s", "start": "1960-01-01", "end": "1969-12-31"},
        {"name": "1970s", "start": "1970-01-01", "end": "1979-12-31"},
        {"name": "1980s", "start": "1980-01-01", "end": "1989-12-31"},
        {"name": "1990s", "start": "1990-01-01", "end": "1999-12-31"},
        {"name": "2000s", "start": "2000-01-01", "end": "2009-12-31"},
        {"name": "2010s", "start": "2010-01-01", "end": "2019-12-31"},
        {"name": "2020s", "start": "2020-01-01", "end": "2029-12-31"}
    ]
    
    recipes = []
    for decade in decades:
        recipes.append({
            "name": f"{decade['name']} Classics",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "primary_release_date.gte": decade["start"],
                "primary_release_date.lte": decade["end"],
                "sort_by": "vote_average.desc",
                "vote_count.gte": 100
            },
            "item_limit": 25,
            "target_servers": ["emby"]
        })
    
    logger.info(f"Generated {len(recipes)} decade recipes")
    return recipes

def generate_award_winning_recipes(api_key: str) -> List[Dict[str, Any]]:
    """Generate collections for award-winning movies.
    
    Note: TMDb doesn't have direct filters for awards, 
    so we use a combination of keywords and high ratings to approximate award winners.
    """
    logger.info("Generating award-winning recipes")
    
    # Keyword IDs for awards and festivals
    keywords = {
        # Confirmed keyword IDs
        "Oscar Winner": 1498,
        "Golden Globe Winner": 10483,
        "BAFTA Winner": 207362,
        "Palme d'Or": 209537,
        "Cannes": 2243,
        "Sundance": 7994,
        "Emmy Winner": 212436,
        "Independent Spirit Award": 209676,
        "Venice Film Festival": 207868,
        "Berlin International Film Festival": 209863
    }
    
    recipes = []
    
    # Oscar winners and categories
    recipes.append({
        "name": "Oscar-Winning Movies",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {
            "with_keywords": str(keywords["Oscar Winner"]),
            "sort_by": "vote_average.desc",
            "vote_count.gte": 100
        },
        "item_limit": 40,
        "target_servers": ["emby"]
    })
    
    recipes.append({
        "name": "Oscar Best Picture Winners",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {
            "with_keywords": "207468", # Best Picture Oscar Winner
            "sort_by": "primary_release_date.desc"
        },
        "item_limit": 40,
        "target_servers": ["emby"]
    })
    
    recipes.append({
        "name": "Oscar Best Director Winners",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {
            "with_keywords": "209485", # Best Director Oscar Winner
            "sort_by": "primary_release_date.desc"
        },
        "item_limit": 40,
        "target_servers": ["emby"]
    })
    
    # Golden Globe winners
    recipes.append({
        "name": "Golden Globe-Winning Movies",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {
            "with_keywords": str(keywords["Golden Globe Winner"]),
            "sort_by": "vote_average.desc",
            "vote_count.gte": 100
        },
        "item_limit": 40,
        "target_servers": ["emby"]
    })
    
    # BAFTA winners
    recipes.append({
        "name": "BAFTA Award-Winning Movies",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {
            "with_keywords": str(keywords["BAFTA Winner"]),
            "sort_by": "vote_average.desc",
            "vote_count.gte": 100
        },
        "item_limit": 40,
        "target_servers": ["emby"]
    })
    
    # Cannes winners
    recipes.append({
        "name": "Cannes Film Festival Winners",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {
            "with_keywords": str(keywords["Cannes"]) + "," + str(keywords["Palme d'Or"]),
            "sort_by": "vote_average.desc",
            "vote_count.gte": 50
        },
        "item_limit": 40,
        "target_servers": ["emby"]
    })
    
    # Sundance winners
    recipes.append({
        "name": "Sundance Film Festival Favorites",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {
            "with_keywords": str(keywords["Sundance"]),
            "sort_by": "vote_average.desc",
            "vote_count.gte": 50
        },
        "item_limit": 40,
        "target_servers": ["emby"]
    })
    
    # Venice Film Festival
    recipes.append({
        "name": "Venice Film Festival Winners",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {
            "with_keywords": str(keywords["Venice Film Festival"]),
            "sort_by": "vote_average.desc",
            "vote_count.gte": 50
        },
        "item_limit": 40,
        "target_servers": ["emby"]
    })
    
    # Berlin Film Festival
    recipes.append({
        "name": "Berlin Film Festival Winners",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {
            "with_keywords": str(keywords["Berlin International Film Festival"]),
            "sort_by": "vote_average.desc",
            "vote_count.gte": 50
        },
        "item_limit": 40,
        "target_servers": ["emby"]
    })
    
    # Independent Spirit Awards
    recipes.append({
        "name": "Independent Spirit Award Winners",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {
            "with_keywords": str(keywords["Independent Spirit Award"]),
            "sort_by": "vote_average.desc",
            "vote_count.gte": 50
        },
        "item_limit": 40,
        "target_servers": ["emby"]
    })
    
    # Critically acclaimed (high rating + high vote count)
    recipes.append({
        "name": "Critically Acclaimed Movies",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {
            "vote_average.gte": 8,
            "vote_count.gte": 1000,
            "sort_by": "vote_average.desc"
        },
        "item_limit": 40,
        "target_servers": ["emby"]
    })
    
    # Hidden Masterpieces (high rating, low votes)
    recipes.append({
        "name": "Hidden Masterpieces",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {
            "vote_average.gte": 8.5,
            "vote_count.gte": 100,
            "vote_count.lte": 500,
            "sort_by": "vote_average.desc"
        },
        "item_limit": 40,
        "target_servers": ["emby"]
    })
    
    logger.info(f"Generated {len(recipes)} award-winning recipes")
    return recipes

def get_popular_tmdb_collections(api_key: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch popular TMDb collections directly."""
    logger.info("Fetching popular TMDb collections")
    
    # Known popular collection IDs (pre-populated to save API calls)
    known_collection_ids = [
        # Major franchises
        10, # Star Wars
        645, # James Bond
        1241, # Harry Potter
        86311, # Marvel Cinematic Universe
        9485, # Fast & Furious
        2980, # Pirates of the Caribbean
        263, # The Dark Knight Trilogy
        87359, # Mission: Impossible
        295, # Pirates of the Caribbean Collection
        528, # The Terminator Collection
        556, # The Godfather Collection
        131292, # DC Extended Universe
        87096, # Avengers
        531241, # Guardians of the Galaxy Collection
        328, # Jurassic Park Collection
        70068, # John Wick Collection
        113575, # DCEU
        284, # The Matrix Collection
        2344, # The Lord of the Rings Collection
        121938, # The Hobbit Collection
        33514, # Transformers Collection
        313086, # Hotel Transylvania Collection
        1570, # Die Hard Collection
        8945, # The Hunger Games Collection
        8091, # Alien Collection
        531859, # Deadpool Collection
        1006268, # Ant-Man Collection
        10194, # Toy Story Collection
    ]
    
    # Additional collections to search for
    collection_ids = set(known_collection_ids)
    
    # Only search for more if we need more than our known list
    if limit > len(collection_ids):
        # Get collections from popular movies
        for page in range(1, 4):  # Check 3 pages of popular movies
            popular_movies = tmdb_request("movie/popular", api_key, {"page": page})
            
            for movie in popular_movies.get("results", []):
                movie_details = tmdb_request(f"movie/{movie['id']}", api_key)
                if movie_details.get("belongs_to_collection"):
                    collection_ids.add(movie_details["belongs_to_collection"]["id"])
                
                if len(collection_ids) >= limit:
                    break
                    
            if len(collection_ids) >= limit:
                break
        
        # If we still need more, get top rated movies
        if len(collection_ids) < limit:
            for page in range(1, 4):  # Check 3 pages of top rated movies
                top_rated_movies = tmdb_request("movie/top_rated", api_key, {"page": page})
                
                for movie in top_rated_movies.get("results", []):
                    movie_details = tmdb_request(f"movie/{movie['id']}", api_key)
                    if movie_details.get("belongs_to_collection"):
                        collection_ids.add(movie_details["belongs_to_collection"]["id"])
                    
                    if len(collection_ids) >= limit:
                        break
                        
                if len(collection_ids) >= limit:
                    break
    
    # Get collection details
    recipes = []
    for collection_id in collection_ids:
        collection_details = tmdb_request(f"collection/{collection_id}", api_key)
        
        if not collection_details.get("name"):
            continue
        
        recipes.append({
            "name": collection_details["name"],
            "source_type": "tmdb_series_collection",
            "tmdb_collection_id": collection_id,
            "target_servers": ["emby"],
            "sort_by": "release_date"
        })
    
    logger.info(f"Generated {len(recipes)} TMDb collection recipes")
    return recipes

def generate_custom_discover_recipes() -> List[Dict[str, Any]]:
    """Generate recipes using TMDb's discover API with custom parameters."""
    logger.info("Generating custom discover recipes")
    
    current_year = datetime.now().year
    
    recipes = [
        # Audience Favorites
        {
            "name": "Audience Favorites",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "sort_by": "vote_average.desc", 
                "vote_count.gte": 1000,
                "vote_average.gte": 8
            },
            "item_limit": 30,
            "target_servers": ["emby"]
        },
        
        # Recent Box Office Hits
        {
            "name": "Recent Box Office Hits",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "sort_by": "revenue.desc", 
                "primary_release_date.gte": f"{current_year-1}-01-01"
            },
            "item_limit": 30,
            "target_servers": ["emby"]
        },
        
        # Hidden Gems (high rated but less known)
        {
            "name": "Hidden Gems",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "sort_by": "vote_average.desc", 
                "vote_count.gte": 100,
                "vote_count.lte": 500,
                "vote_average.gte": 7.5
            },
            "item_limit": 30,
            "target_servers": ["emby"]
        },
        
        # Blockbusters of All Time
        {
            "name": "Blockbusters of All Time",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "sort_by": "revenue.desc", 
                "vote_count.gte": 500
            },
            "item_limit": 30,
            "target_servers": ["emby"]
        },
        
        # Recent Indie Films
        {
            "name": "Recent Indie Films",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "sort_by": "popularity.desc", 
                "primary_release_date.gte": f"{current_year-2}-01-01",
                "vote_average.gte": 6,
                "with_companies": "194" # A24 production company as an example
            },
            "item_limit": 30,
            "target_servers": ["emby"]
        },
        
        # Foreign Language Hits
        {
            "name": "Foreign Language Hits",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "sort_by": "vote_average.desc", 
                "vote_count.gte": 300,
                "with_original_language": "ko,fr,es,de,ja",  # Korean, French, Spanish, German, Japanese
                "vote_average.gte": 7
            },
            "item_limit": 30,
            "target_servers": ["emby"]
        },
        
        # Animated Features
        {
            "name": "Top Animated Features",
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "sort_by": "vote_average.desc", 
                "vote_count.gte": 300,
                "with_genres": "16",  # Animation genre
                "vote_average.gte": 7
            },
            "item_limit": 30,
            "target_servers": ["emby"]
        }
    ]
    
    logger.info(f"Generated {len(recipes)} custom discover recipes")
    return recipes

def generate_keyword_based_recipes(api_key: str) -> List[Dict[str, Any]]:
    """Generate collections based on specific TMDb keywords."""
    logger.info("Generating keyword-based recipes")
    
    # Predefined keywords with their TMDb IDs (these IDs should be verified with TMDb's API)
    keyword_collections = [
        {"name": "Time Travel Movies", "keyword_id": 4565},
        {"name": "Dystopian Future Movies", "keyword_id": 12565},
        {"name": "Post-Apocalyptic Movies", "keyword_id": 2964},
        {"name": "Artificial Intelligence Movies", "keyword_id": 9643},
        {"name": "Zombie Movies", "keyword_id": 1692},
        {"name": "Superhero Movies", "keyword_id": 9715},
        {"name": "Spy Movies", "keyword_id": 10161},
        {"name": "Heist Movies", "keyword_id": 9882},
        {"name": "Space Movies", "keyword_id": 11844},
        {"name": "Coming of Age Movies", "keyword_id": 10683}
    ]
    
    recipes = []
    for collection in keyword_collections:
        recipes.append({
            "name": collection["name"],
            "source_type": "tmdb_discover_individual_movies",
            "tmdb_discover_params": {
                "with_keywords": str(collection["keyword_id"]),
                "sort_by": "vote_average.desc",
                "vote_count.gte": 50
            },
            "item_limit": 25,
            "target_servers": ["emby"]
        })
    
    logger.info(f"Generated {len(recipes)} keyword-based recipes")
    return recipes

def generate_all_recipes() -> List[Dict[str, Any]]:
    """Generate all types of collection recipes."""
    api_key = get_tmdb_api_key()
    if not api_key:
        logger.error("Cannot generate recipes without a valid TMDb API key")
        return []
    
    all_recipes = []
    
    # Generate all recipe types
    all_recipes.extend(generate_genre_recipes(api_key))
    all_recipes.extend(generate_genre_combination_recipes(api_key))
    all_recipes.extend(generate_director_recipes(api_key))
    all_recipes.extend(generate_actor_recipes(api_key))
    all_recipes.extend(generate_decade_recipes(api_key))
    all_recipes.extend(generate_award_winning_recipes(api_key))
    all_recipes.extend(get_popular_tmdb_collections(api_key))
    all_recipes.extend(generate_custom_discover_recipes())
    all_recipes.extend(generate_keyword_based_recipes(api_key))
    
    logger.info(f"Generated a total of {len(all_recipes)} recipes")
    return all_recipes

def save_recipes_to_file(recipes: List[Dict[str, Any]], filename: str = "enhanced_recipes.py") -> None:
    """Save generated recipes to a Python file."""
    output_path = os.path.join(os.path.dirname(__file__), filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("from typing import List, Dict, Any\n\n")
        f.write("# Auto-generated collection recipes\n")
        f.write("ENHANCED_COLLECTION_RECIPES: List[Dict[str, Any]] = [\n")
        
        for recipe in recipes:
            f.write(f"    {repr(recipe)},\n")
        
        f.write("]\n\n")
        f.write("# Alias for compatibility with orchestration logic\n")
        f.write("RECIPES = ENHANCED_COLLECTION_RECIPES\n")
    
    logger.info(f"Saved {len(recipes)} recipes to {output_path}")

def main():
    """Main function to generate and save all recipes."""
    recipes = generate_all_recipes()
    if recipes:
        save_recipes_to_file(recipes)
        print(f"Successfully generated {len(recipes)} collection recipes")
    else:
        print("Failed to generate recipes. Check the logs for details.")

if __name__ == "__main__":
    main()
