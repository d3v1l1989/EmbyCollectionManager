from typing import List, Dict, Any

COLLECTION_RECIPES: List[Dict[str, Any]] = [
    {
        "name": "Popular Movies on TMDb",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {"sort_by": "popularity.desc", "vote_count.gte": 100},
        "item_limit": 40,
        "target_servers": ["emby", "jellyfin"]
    },
    {
        "name": "Top Rated Movies on TMDb",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {"sort_by": "vote_average.desc", "vote_count.gte": 500},
        "item_limit": 40,
        "target_servers": ["emby", "jellyfin"]
    },
    {
        "name": "New Releases (Last Year)",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {"sort_by": "release_date.desc", "primary_release_date.gte": "2024-01-01", "vote_count.gte": 50},
        "item_limit": 30,
        "target_servers": ["emby", "jellyfin"]
    },

    # Example series/franchise collections (real TMDb collection IDs should be looked up)
    {
        "name": "Star Wars Collection",
        "source_type": "tmdb_series_collection",
        "tmdb_collection_id": 10,
        "target_servers": ["emby", "jellyfin"]
    },
    {
        "name": "James Bond Collection",
        "source_type": "tmdb_series_collection",
        "tmdb_collection_id": 645,
        "target_servers": ["emby", "jellyfin"]
    },
    {
        "name": "Harry Potter Collection",
        "source_type": "tmdb_series_collection",
        "tmdb_collection_id": 1241,
        "target_servers": ["emby", "jellyfin"]
    },
    # === AUTO-GENERATED GENRE RECIPES ===
    {'item_limit': 30, 'name': 'Adventure Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '12'}},
    {'item_limit': 30, 'name': 'Animation Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '16'}},
    {'item_limit': 30, 'name': 'Crime Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '80'}},
    {'item_limit': 30, 'name': 'Documentary Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '99'}},
    {'item_limit': 30, 'name': 'Drama Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '18'}},
    {'item_limit': 30, 'name': 'Family Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '10751'}},
    {'item_limit': 30, 'name': 'Fantasy Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '14'}},
    {'item_limit': 30, 'name': 'History Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '36'}},
    {'item_limit': 30, 'name': 'Horror Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '27'}},
    {'item_limit': 30, 'name': 'Music Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '10402'}},
    {'item_limit': 30, 'name': 'Mystery Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '9648'}},
    {'item_limit': 30, 'name': 'Romance Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '10749'}},
    {'item_limit': 30, 'name': 'Science Fiction Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '878'}},
    {'item_limit': 30, 'name': 'TV Movie Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '10770'}},
    {'item_limit': 30, 'name': 'Thriller Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '53'}},
    {'item_limit': 30, 'name': 'War Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '10752'}},
    {'item_limit': 30, 'name': 'Western Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby', 'jellyfin'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '37'}},
]

# Alias for compatibility with orchestration logic
RECIPES = COLLECTION_RECIPES

