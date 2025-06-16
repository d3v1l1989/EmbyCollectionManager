from typing import List, Dict, Any

# This file contains categorized collection recipes for the Emby Collection Manager application
# Recipes are organized by category for easier maintenance and readability

# Configuration section mapping category numbers to their properties
CATEGORY_CONFIG = {
    1: {"name": "TMDb GENERAL COLLECTIONS", "poster": "tmdb.jpg"},
    2: {"name": "STREAMING PLATFORM COLLECTIONS", "poster": "streaming_platforms.jpg"},
    3: {"name": "FRANCHISE COLLECTIONS", "poster": "uses TMDB API for poster fetching"},
    4: {"name": "GENRE COLLECTIONS", "poster": "genres.jpg"},
    5: {"name": "DIRECTOR COLLECTIONS", "poster": "director.jpg"},
    6: {"name": "ACTOR COLLECTIONS", "poster": "actor.jpg"},
    7: {"name": "DECADE COLLECTIONS", "poster": "decade.jpg"},
    8: {"name": "CRITICALLY ACCLAIMED COLLECTIONS", "poster": "award.jpg"},
    9: {"name": "ADDITIONAL THEME & KEYWORD COLLECTIONS", "poster": "themes.jpg"},
    10: {"name": "STUDIO COLLECTIONS", "poster": "studio.jpg"},
    11: {"name": "LANGUAGE & REGIONAL CINEMA", "poster": "languages.jpg"},
    12: {"name": "TRAKT COLLECTIONS", "poster": "trakt.png"},
    13: {"name": "MDBLIST COLLECTIONS", "poster": "mdblist.png"}
}

COLLECTION_RECIPES: List[Dict[str, Any]] = [
    #############################################
    # CATEGORY 1: TMDb GENERAL COLLECTIONS POSTER:tmdb.jpg
    #############################################
    {
        "name": "Popular Movies on TMDb",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {'sort_by': 'popularity.desc', 'vote_count.gte': 100},
        "item_limit": 40,
        "target_servers": ['emby'],
        "category_id": 1
    },
    {
        "name": "Top Rated Movies on TMDb",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {'sort_by': 'vote_average.desc', 'vote_count.gte': 500},
        "item_limit": 40,
        "target_servers": ['emby'],
        "category_id": 1
    },
    {
        "name": "New Releases (Last Year)",
        "source_type": "tmdb_discover_individual_movies",
        "tmdb_discover_params": {'sort_by': 'release_date.desc', 'primary_release_date.gte': '2024-01-01', 'vote_count.gte': 50},
        "item_limit": 30,
        "target_servers": ['emby'],
        "category_id": 1
    },

    {'name': 'Audience Favorites', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'sort_by': 'vote_average.desc', 'vote_count.gte': 1000, 'vote_average.gte': 8}, 'item_limit': 30, 'target_servers': ['emby'], "category_id": 1},
    {'name': 'Recent Box Office Hits', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'sort_by': 'revenue.desc', 'primary_release_date.gte': '2024-01-01'}, 'item_limit': 30, 'target_servers': ['emby'], "category_id": 1},
    {'name': 'Hidden Gems', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'sort_by': 'vote_average.desc', 'vote_count.gte': 100, 'vote_count.lte': 500, 'vote_average.gte': 7.5}, 'item_limit': 30, 'target_servers': ['emby'], "category_id": 1},
    {'name': 'Blockbusters of All Time', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'sort_by': 'revenue.desc', 'vote_count.gte': 500}, 'item_limit': 30, 'target_servers': ['emby'], "category_id": 1},
    {'name': 'Recent Indie Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'primary_release_date.gte': '2023-01-01', 'vote_average.gte': 6, 'with_companies': '194'}, 'item_limit': 30, 'target_servers': ['emby'], "category_id": 1},
    {'name': 'Foreign Language Hits', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'sort_by': 'vote_average.desc', 'vote_count.gte': 300, 'with_original_language': 'ko,fr,es,de,ja', 'vote_average.gte': 7}, 'item_limit': 30, 'target_servers': ['emby'], "category_id": 1},
    
    #############################################
    # CATEGORY 2: STREAMING PLATFORM COLLECTIONS POSTER:streaming_platforms.jpg
    #############################################
    # Netflix Collections
    {'name': 'Popular on Netflix', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '8', 'watch_region': 'US', 'sort_by': 'popularity.desc', 'vote_count.gte': 100}, 'item_limit': 40, 'target_servers': ['emby'], "category_id": 2},
    {'name': 'Top Rated on Netflix', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '8', 'watch_region': 'US', 'sort_by': 'vote_average.desc', 'vote_count.gte': 200}, 'item_limit': 40, 'target_servers': ['emby'], "category_id": 2},
    {'name': 'Netflix Originals', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '213', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 40, 'target_servers': ['emby'], "category_id": 2},
    
    # Disney+ Collections
    {'name': 'Popular on Disney+', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '337', 'watch_region': 'US', 'sort_by': 'popularity.desc', 'vote_count.gte': 100}, 'item_limit': 40, 'target_servers': ['emby'], "category_id": 2},
    {'name': 'Top Rated on Disney+', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '337', 'watch_region': 'US', 'sort_by': 'vote_average.desc', 'vote_count.gte': 200}, 'item_limit': 40, 'target_servers': ['emby'], "category_id": 2},
    {'name': 'Disney+ Originals', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '2', 'with_watch_providers': '337', 'watch_region': 'US', 'sort_by': 'popularity.desc'}, 'item_limit': 40, 'target_servers': ['emby'], "category_id": 2},
    
    # Amazon Prime Video Collections
    {'name': 'Popular on Amazon Prime', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '9', 'watch_region': 'US', 'sort_by': 'popularity.desc', 'vote_count.gte': 100}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'Top Rated on Amazon Prime', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '9', 'watch_region': 'US', 'sort_by': 'vote_average.desc', 'vote_count.gte': 200}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'Amazon Prime Originals', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '20580', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    
    # HBO Max Collections
    {'name': 'Popular on HBO Max', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '384', 'watch_region': 'US', 'sort_by': 'popularity.desc', 'vote_count.gte': 100}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'Top Rated on HBO Max', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '384', 'watch_region': 'US', 'sort_by': 'vote_average.desc', 'vote_count.gte': 200}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'HBO Max Originals', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '174', 'with_watch_providers': '384', 'watch_region': 'US', 'sort_by': 'popularity.desc'}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    
    # Apple TV+ Collections
    {'name': 'Popular on Apple TV+', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '350', 'watch_region': 'US', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'Top Rated on Apple TV+', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '350', 'watch_region': 'US', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'Apple TV+ Originals', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '152952', 'sort_by': 'popularity.desc'}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    
    # Hulu Collections
    {'name': 'Popular on Hulu', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '15', 'watch_region': 'US', 'sort_by': 'popularity.desc', 'vote_count.gte': 100}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'Top Rated on Hulu', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '15', 'watch_region': 'US', 'sort_by': 'vote_average.desc', 'vote_count.gte': 200}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'Hulu Originals', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '3364', 'sort_by': 'popularity.desc'}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    
    # Paramount+ Collections
    {'name': 'Popular on Paramount+', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '531', 'watch_region': 'US', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'Top Rated on Paramount+', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '531', 'watch_region': 'US', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'Paramount+ Originals', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '4', 'with_watch_providers': '531', 'watch_region': 'US', 'sort_by': 'popularity.desc'}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    
    # Peacock Collections
    {'name': 'Popular on Peacock', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '386', 'watch_region': 'US', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'Top Rated on Peacock', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '386', 'watch_region': 'US', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'Peacock Originals', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '33', 'with_watch_providers': '386', 'watch_region': 'US', 'sort_by': 'popularity.desc'}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    
    # Crunchyroll Collections
    {'name': 'Popular on Crunchyroll', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '283', 'watch_region': 'US', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'Top Rated on Crunchyroll', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '283', 'watch_region': 'US', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'Anime Movies on Crunchyroll', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '283', 'watch_region': 'US', 'with_genres': '16', 'sort_by': 'popularity.desc'}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    
    # Discovery+ Collections
    {'name': 'Popular on Discovery+', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '520', 'watch_region': 'US', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'Documentaries on Discovery+', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '520', 'watch_region': 'US', 'with_genres': '99', 'sort_by': 'popularity.desc'}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    
    # Shudder Collections
    {'name': 'Popular on Shudder', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '99', 'watch_region': 'US', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    {'name': 'Horror Movies on Shudder', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_watch_providers': '99', 'watch_region': 'US', 'with_genres': '27', 'sort_by': 'popularity.desc'}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 2},
    
    #############################################
    # CATEGORY 3: FRANCHISE COLLECTIONS POSTER:uses TMDB API for poster fetching
    #############################################
    {
        "name": "Star Wars Collection",
        "source_type": "tmdb_series_collection",
        "tmdb_collection_id": 10,
        "target_servers": ['emby'],
        "sort_by": "title",
        "category_id": 3
    },
    {
        "name": "James Bond Collection",
        "source_type": "tmdb_series_collection",
        "tmdb_collection_id": 645,
        "target_servers": ['emby'],
        "sort_by": "release_date",
        "category_id": 3
    },
    {
        "name": "Harry Potter Collection",
        "source_type": "tmdb_series_collection",
        "tmdb_collection_id": 1241,
        "target_servers": ['emby'],
        "sort_by": "release_date",
        "category_id": 3
    },
    {
        "name": "Marvel Cinematic Universe Collection",
        "source_type": "tmdb_series_collection",
        "tmdb_collection_id": 86311,
        "target_servers": ['emby'],
        "sort_by": "release_date",
        "category_id": 3
    },
    {
        "name": "Fast & Furious Collection",
        "source_type": "tmdb_series_collection",
        "tmdb_collection_id": 9485,
        "target_servers": ['emby'],
        "sort_by": "release_date",
        "category_id": 3
    },

    {'name': 'The Lord of the Rings Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 119, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Hobbit Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 121938, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Jurassic Park Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 328, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Matrix Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 2344, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Terminator Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 528, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Alien Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 8091, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Pirates of the Caribbean Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 295, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Hunger Games Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 131635, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Transformers Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 8650, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Die Hard Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 1570, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Mission: Impossible Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 87359, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Toy Story Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 10194, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Godfather Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 230, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Rocky Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 1575, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Blade Runner Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 422837, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Dark Knight Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 263, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Ghostbusters Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 2980, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Ice Age Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 8354, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Kung Fu Panda Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 77816, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Mummy Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 1733, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Ocean\'s Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 304, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Planet of the Apes (Original) Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 19995, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Predator Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 399, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Men in Black Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 86055, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Conjuring Universe', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 313086, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Avengers Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 86311, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Guardians of the Galaxy Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 284433, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Captain America Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 131292, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Iron Man Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 131294, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Incredibles Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 468222, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Finding Nemo Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 137697, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Lion King Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 94032, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Monsters, Inc. Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 137696, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Cars Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 87118, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Hangover Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 86033, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Madagascar Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 18652, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'How to Train Your Dragon Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 89137, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Bourne Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 31562, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Night at the Museum Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 85299, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Twilight Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 33514, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Princess Diaries Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 107674, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Austin Powers Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 1006, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Expendables Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 126125, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Saw Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 656, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Final Destination Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 8864, 'target_servers': ['emby'], 'sort_by': 'release_date'},
    {'name': 'Underworld Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 2326, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Resident Evil Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 17255, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Chronicles of Narnia Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 420, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Insidious Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 238163, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'John Wick Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 404609, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Pokémon Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 34055, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Back to the Future Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 264, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Grumpy Old Men Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 119050, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Planet of the Apes (Reboot) Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 173710, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Scary Movie Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 4246, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Tomb Raider Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 2467, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Scream Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 2602, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Rambo Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 5039, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Despicable Me Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 86066, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Fantastic Beasts Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 435259, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Indiana Jones Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 84, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': "Child's Play Collection", 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 10455, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Thor Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 131296, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Halloween Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 91361, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Shrek Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 2150, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'X-Men Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 748, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'American Pie Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 2806, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Star Trek: Alternate Reality Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 115575, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Moana Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 1241984, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Karate Kid Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 8580, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Fast and the Furious Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 9485, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Hannibal Lecter Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 9743, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Terminator Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 528, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Lion King (Reboot) Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 762512, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Devara Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 1187990, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Alien Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 8091, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Die Hard Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 1570, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Ghostbusters Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 2980, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Bullet Train Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 1471524, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Pirates of the Caribbean Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 295, 'target_servers': ['emby'], 'sort_by': 'release_date'},
    {'name': 'Spider-Man (MCU) Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 531241, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Matrix Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 2344, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Spider-Man Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 556, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Quintessential Quintuplets Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 1287339, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'xXx Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 52785, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Ip Man Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 70068, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Avatar Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 87096, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Fault Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 1156666, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Jurassic Park Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 328, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Hobbit Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 121938, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Toy Story Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 10194, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Iron Man Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 131292, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Legend of Hei Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 1444577, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'O Auto da Compadecida: Coleção', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 1219938, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Wild Robot Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 1370345, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Twilight Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 33514, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': "Gabriel's Inferno Collection", 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 729322, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Sonic the Hedgehog Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 720879, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Mad Max Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 8945, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Psycho Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 119674, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Spider-Man: Spider-Verse Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 573436, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Conjuring Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 313086, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Final Destination Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 8864, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Mission: Impossible Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 87359, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Godfather Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 230, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Dark Knight Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 263, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Lord of the Rings Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 119, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Lost Bullet Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 1002775, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'The Minecraft Movie Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 1461530, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},
    {'name': 'Captain America Collection', 'source_type': 'tmdb_series_collection', 'tmdb_collection_id': 131295, 'target_servers': ['emby'], 'sort_by': 'release_date', 'category_id': 3},

    #############################################
    # CATEGORY 4: GENRE COLLECTIONS POSTER:genres.jpg
    #############################################
    {
        "item_limit": 30,
        "name": "Adventure Movies",
        "source_type": "tmdb_discover_individual_movies",
        "target_servers": ['emby'],
        "tmdb_discover_params": {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '12'},
        "category_id": 4
    },
    {
        "item_limit": 30,
        "name": "Animation Movies",
        "source_type": "tmdb_discover_individual_movies",
        "target_servers": ['emby'],
        "tmdb_discover_params": {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '16'},
        "category_id": 4
    },
    {
        "item_limit": 30,
        "name": "Crime Movies",
        "source_type": "tmdb_discover_individual_movies",
        "target_servers": ['emby'],
        "tmdb_discover_params": {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '80'},
        "category_id": 4
    },
    {
        "item_limit": 30,
        "name": "Documentary Movies",
        "source_type": "tmdb_discover_individual_movies",
        "target_servers": ['emby'],
        "tmdb_discover_params": {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '99'},
        "category_id": 4
    },
    {
        "item_limit": 30,
        "name": "Drama Movies",
        "source_type": "tmdb_discover_individual_movies",
        "target_servers": ['emby'],
        "tmdb_discover_params": {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '18'},
        "category_id": 4
    },
    {
        "item_limit": 30,
        "name": "Family Movies",
        "source_type": "tmdb_discover_individual_movies",
        "target_servers": ['emby'],
        "tmdb_discover_params": {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '10751'},
        "category_id": 4
    },
    {
        "item_limit": 30,
        "name": "Fantasy Movies",
        "source_type": "tmdb_discover_individual_movies",
        "target_servers": ['emby'],
        "tmdb_discover_params": {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '14'},
        "category_id": 4
    },
    {
        "item_limit": 30,
        "name": "History Movies",
        "source_type": "tmdb_discover_individual_movies",
        "target_servers": ['emby'],
        "tmdb_discover_params": {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '36'},
        "category_id": 4
    },
    {
        "item_limit": 30,
        "name": "Horror Movies",
        "source_type": "tmdb_discover_individual_movies",
        "target_servers": ['emby'],
        "tmdb_discover_params": {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '27'},
        "category_id": 4
    },
    {
        "item_limit": 30,
        "name": "Music Movies",
        "source_type": "tmdb_discover_individual_movies",
        "target_servers": ['emby'],
        "tmdb_discover_params": {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '10402'},
        "category_id": 4
    },
    {
        "item_limit": 30,
        "name": "Mystery Movies",
        "source_type": "tmdb_discover_individual_movies",
        "target_servers": ['emby'],
        "tmdb_discover_params": {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '9648'},
        "category_id": 4
    },
    {
        "item_limit": 30,
        "name": "Romance Movies",
        "source_type": "tmdb_discover_individual_movies",
        "target_servers": ['emby'],
        "tmdb_discover_params": {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '10749'},
        "category_id": 4
    },

    {'name': 'Drama & Romance Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '18,10749', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Comedy & Romance Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '35,10749', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Crime & Thriller Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '80,53', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Horror & Mystery Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '27,9648', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Drama & History Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '18,36', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Animation & Family Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '16,10751', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Documentary & History Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '99,36', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Action & Comedy Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '28,35', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Action & Drama Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '28,18', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Action & Fantasy Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '28,14', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Action & Horror Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '28,27', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Action & Thriller Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '28,53', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Adventure & Comedy Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '12,35', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Adventure & Drama Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '12,18', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Adventure & Science Fiction Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '12,878', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Action & Adventure Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '28,12', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Action & Science Fiction Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '28,878', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Adventure & Horror Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '12,27', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Adventure & Thriller Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '12,53', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'name': 'Adventure & Fantasy Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '12,14', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    {'item_limit': 30, 'name': 'Science Fiction Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '878'}, 'category_id': 4},
    {'item_limit': 30, 'name': 'Thriller Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '53'}, 'category_id': 4},
    {'item_limit': 30, 'name': 'War Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '10752'}, 'category_id': 4},
    {'item_limit': 30, 'name': 'Western Movies', 'source_type': 'tmdb_discover_individual_movies', 'target_servers': ['emby'], 'tmdb_discover_params': {'sort_by': 'popularity.desc', 'vote_count.gte': 50, 'with_genres': '37'}, 'category_id': 4},
    {'name': 'Adventure & Fantasy Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_genres': '12,14', 'sort_by': 'popularity.desc', 'vote_count.gte': 75}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 4},
    
    
    #############################################
    # CATEGORY 5: DIRECTOR COLLECTIONS POSTER:director.jpg
    #############################################
    {'name': 'Christopher Nolan Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '525', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Martin Scorsese Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '1032', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Quentin Tarantino Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '138', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'James Cameron Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '2710', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Peter Jackson Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '108', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Ridley Scott Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '578', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Alfred Hitchcock Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '2636', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Stanley Kubrick Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '240', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'David Fincher Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '7467', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Denis Villeneuve Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '137427', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Hayao Miyazaki Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '608', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Francis Ford Coppola Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '1776', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Wes Anderson Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '5655', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Akira Kurosawa Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '5026', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Guillermo del Toro Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '10828', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Spike Lee Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '5281', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Tim Burton Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '510', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Joel Coen Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '1223', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Ethan Coen Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '1224', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Clint Eastwood Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '190', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    {'name': 'Ang Lee Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '1614', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 5},
    
    #############################################
    # CATEGORY 6: ACTOR COLLECTIONS POSTER:actor.jpg
    #############################################
    {'name': 'Jennifer Lawrence Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '72129', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Brad Pitt Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '287', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Scarlett Johansson Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '1245', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Robert Downey Jr. Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '3223', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Tom Cruise Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '500', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Viola Davis Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '19492', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Cate Blanchett Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '112', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Morgan Freeman Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '192', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Emma Stone Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '54693', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Samuel L. Jackson Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '2231', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Anthony Hopkins Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '4173', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Ron Howard Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '6159', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Alfonso Cuarón Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '11218', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Darren Aronofsky Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '6431', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'David Lynch Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '5602', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Sofia Coppola Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '1769', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Alejandro González Iñárritu Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '223', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Greta Gerwig Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '45400', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Kathryn Bigelow Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '14392', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Ingmar Bergman Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '6648', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Federico Fellini Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '4415', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Orson Welles Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '40', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'John Ford Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '1090553', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Woody Allen Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '1243', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Billy Wilder Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '3146', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Werner Herzog Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '6818', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'John Carpenter Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '11770', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Sam Raimi Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '7623', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Danny Boyle Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '2034', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Paul Thomas Anderson Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '4762', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Sofia Coppola Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '1769', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Alejandro González Iñárritu Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '223', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Greta Gerwig Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '45400', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Kathryn Bigelow Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '14392', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Ingmar Bergman Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '6648', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Federico Fellini Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '4415', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Orson Welles Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '40', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'John Ford Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '1090553', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Woody Allen Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '1243', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Billy Wilder Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '3146', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Werner Herzog Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '6818', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'John Carpenter Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '11770', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Sam Raimi Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '7623', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Danny Boyle Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '2034', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Robert Zemeckis Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '24', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Bong Joon-ho Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '21684', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Andrei Tarkovsky Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '8452', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Sergio Leone Collection', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_people': '4385', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 15, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Christian Bale Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '3894', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Joaquin Phoenix Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '73421', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Ryan Gosling Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '30614', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Matt Damon Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '1892', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Hugh Jackman Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '6968', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Natalie Portman Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '524', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Kate Winslet Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '204', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Daniel Day-Lewis Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '11856', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Frances McDormand Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '3910', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Amy Adams Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '9273', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Jake Gyllenhaal Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '131', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Nicole Kidman Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '2227', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Johnny Depp Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '85', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Charlize Theron Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '6885', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Gary Oldman Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '64', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Harrison Ford Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '3', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Al Pacino Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '1158', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Robert De Niro Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '380', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Jack Nicholson Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '514', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Clint Eastwood Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '190', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Audrey Hepburn Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '1932', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Marilyn Monroe Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '3149', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Sidney Poitier Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '16897', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'James Stewart Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '854', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Humphrey Bogart Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '4110', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Timothée Chalamet Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '1190668', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Margot Robbie Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '234352', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Adam Driver Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '1023139', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Florence Pugh Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '1373737', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Zendaya Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '505710', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Chris Hemsworth Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '74568', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Saoirse Ronan Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '36592', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Mahershala Ali Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '932967', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': 'Michelle Yeoh Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '1620', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    {'name': "Lupita Nyong'o Movies", 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_cast': '1267329', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 20, 'target_servers': ['emby'], 'category_id': 6},
    
    #############################################
    # CATEGORY 7: DECADE COLLECTIONS   POSTER:decade.jpg
    #############################################
    {'name': '1950s Classics', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'primary_release_date.gte': '1950-01-01', 'primary_release_date.lte': '1959-12-31', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 7},
    {'name': '1960s Classics', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'primary_release_date.gte': '1960-01-01', 'primary_release_date.lte': '1969-12-31', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 7},
    {'name': '1970s Classics', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'primary_release_date.gte': '1970-01-01', 'primary_release_date.lte': '1979-12-31', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 7},
    {'name': '1980s Classics', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'primary_release_date.gte': '1980-01-01', 'primary_release_date.lte': '1989-12-31', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 7},
    {'name': '1990s Classics', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'primary_release_date.gte': '1990-01-01', 'primary_release_date.lte': '1999-12-31', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 7},
    {'name': '2000s Classics', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'primary_release_date.gte': '2000-01-01', 'primary_release_date.lte': '2009-12-31', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 7},
    {'name': '2010s Classics', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'primary_release_date.gte': '2010-01-01', 'primary_release_date.lte': '2019-12-31', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 7},
    {'name': '2020s Classics', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'primary_release_date.gte': '2020-01-01', 'primary_release_date.lte': '2029-12-31', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 7},
    
    #############################################
    # CATEGORY 8: CRITICALLY ACCLAIMED COLLECTIONS POSTER:award.jpg
    #############################################
    {'name': 'Oscar-Winning Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '1498', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 8},
    {'name': 'Golden Globe-Winning Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '10483', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 8},
    {'name': 'Critically Acclaimed Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'vote_average.gte': 8, 'vote_count.gte': 1000, 'sort_by': 'vote_average.desc'}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 8},
    {'name': 'Oscar Best Picture Winners', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '207468', 'sort_by': 'primary_release_date.desc'}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 8},
    {'name': 'Oscar Best Director Winners', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '209485', 'sort_by': 'primary_release_date.desc'}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 8},
    {'name': 'BAFTA Award-Winning Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '207362', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 8},
    {'name': 'Cannes Film Festival Winners', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '2243,209537', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 8},
    {'name': 'Sundance Film Festival Favorites', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '7994', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 8},
    {'name': 'Venice Film Festival Winners', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '207868', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 8},
    {'name': 'Berlin Film Festival Winners', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '209863', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 8},
    {'name': 'Independent Spirit Award Winners', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '209676', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 8},
    {'name': 'Hidden Masterpieces', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'vote_average.gte': 8.5, 'vote_count.gte': 100, 'vote_count.lte': 500, 'sort_by': 'vote_average.desc'}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 8},

    
    
    #############################################
    # CATEGORY 9: ADDITIONAL THEME & KEYWORD COLLECTIONS POSTER:themes.jpg
    #############################################
    {'name': 'Time Travel Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '4565', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Dystopian Future Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '12565', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Post-Apocalyptic Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '2964', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Artificial Intelligence Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '9643', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Zombie Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '1692', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Superhero Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '9715', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Spy Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '10161', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Heist Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '9882', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Space Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '11844', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Coming of Age Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '10683', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Road Trip Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '2236', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Revenge Movies', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '256227', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Coming of Age', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '10683', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Dystopian', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '12565', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Post-Apocalyptic', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '2964', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Time Travel', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '4565', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Parallel Universe', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '3801', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Alternate History', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '10868', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Conspiracy', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '10292', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Virtual Reality', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '14643', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Spy', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '10161', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Cyberpunk', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '11099', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Fantasy World', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '4344', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Underdog Story', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '162740', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Space', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '11844', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Underwater', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '10954', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Prison', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '2181', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Jungle', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '1903', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Desert', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '10232', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Arctic/Antarctic', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '8391', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Island', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '2482', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'High School', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '6270', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Hospital', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '10306', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Courtroom', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '3684', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Sports', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '156792', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Boxing', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '6437', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Martial Arts', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '4251', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'War', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '2454', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Political', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '6454', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Survival', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '9882', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Art', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '9748', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Music', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '4344', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Dance', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '1879', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Food', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '1055', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Fashion', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '7046', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Chess', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '158655', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'True Story', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '9672', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Biopic', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '1347', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Based on Novel', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '818', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Based on Comic', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '9717', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Christmas', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '207317', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Halloween', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '3335', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': "New Year's Eve", 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '13090', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': "Valentine's Day", 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '160404', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Thanksgiving', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '206554', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Summer Vacation', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '2026', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Winter', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '3272', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Romance', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '9840', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Friendship', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '4472', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Family', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '10751', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Father Son Relationship', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '18015', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Mother Daughter Relationship', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '195444', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Sibling Relationship', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '11071', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Twist Ending', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '3626', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Mental Illness', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '9673', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Amnesia', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '594', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Double Life', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '12560', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Found Footage', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '7103', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Mockumentary', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '21182', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Noir', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '9803', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Anthology', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '7062', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},
    {'name': 'Unreliable Narrator', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_keywords': '278069', 'sort_by': 'popularity.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 9},



    #############################################
    # CATEGORY 10: STUDIO COLLECTIONS POSTER:studio.jpg
    #############################################
    {'name': 'Pixar Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '3', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Lucasfilm Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '1', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Marvel Studios Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '420', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Warner Bros. Pictures Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '174', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Universal Pictures Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '33', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': '20th Century Studios Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '25', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Paramount Pictures Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '4', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Columbia Pictures Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '5', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Walt Disney Pictures Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '2', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'DreamWorks Animation Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '521', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Studio Ghibli Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '10342', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'A24 Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '41077', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Lionsgate Films Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '1632', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'New Line Cinema Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '12', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Focus Features Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '10146', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Sony Pictures Animation Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '2251', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'BBC Films Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '146', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Miramax Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '14', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Amblin Entertainment Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '56', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Legendary Pictures Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '923', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Blumhouse Productions Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '3172', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Metro-Goldwyn-Mayer Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '8411', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Working Title Films Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '10163', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Bad Robot Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '11461', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'NEON Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '124052', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'FilmNation Entertainment Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '27551', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'StudioCanal Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '694', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Netflix Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '12177', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Amazon Studios Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '34982', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    {'name': 'Apple Studios Films', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_companies': '152952', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 10},
    
    
    #############################################
    # CATEGORY 11: LANGUAGE & REGIONAL CINEMA POSTER:languages.jpg
    #############################################
    {'name': 'French Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'fr', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Italian Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'it', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Japanese Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'jp', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Korean Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'kr', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Spanish Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'es', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Indian Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'in', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Chinese Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'cn', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'German Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'de', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'British Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'gb', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Swedish Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'se', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Danish Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'dk', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Norwegian Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'no', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Mexican Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'mx', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Brazilian Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'br', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Australian Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'au', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Russian Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'ru', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Canadian Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'ca', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Hong Kong Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'hk', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Thai Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'th', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Turkish Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'tr', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Iranian Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'ir', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Polish Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'pl', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Argentine Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'ar', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Czech Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'cz', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Israeli Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'il', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 30, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Arabic', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'ar', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Bengali', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'bn', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Dutch', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'nl', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Finnish', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'fi', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Greek', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'el', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Hebrew', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'he', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Hindi', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'hi', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Hungarian', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'hu', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Indonesian', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'id', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Mandarin', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'zh', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Persian', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'fa', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Portuguese', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'pt', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Romanian', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'ro', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Tamil', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'ta', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Ukrainian', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'uk', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Films in Vietnamese', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'vi', 'sort_by': 'popularity.desc', 'vote_count.gte': 20}, 'item_limit': 25, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Nordic Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'sv,da,no,fi,is', 'sort_by': 'vote_average.desc', 'vote_count.gte': 50}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Eastern European Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'ru,pl,cs,hu,ro,bg,uk,sr,hr,sk', 'sort_by': 'vote_average.desc', 'vote_count.gte': 30}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Latin American Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'es,pt', 'region': 'AR,BR,MX,CL,CO,PE,VE', 'sort_by': 'vote_average.desc', 'vote_count.gte': 30}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'East Asian Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'zh,ja,ko', 'sort_by': 'vote_average.desc', 'vote_count.gte': 100}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'South Asian Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'hi,bn,ta,te,ml,kn', 'sort_by': 'vote_average.desc', 'vote_count.gte': 30}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 11},
    {'name': 'Middle Eastern Cinema', 'source_type': 'tmdb_discover_individual_movies', 'tmdb_discover_params': {'with_original_language': 'ar,fa,he,tr', 'sort_by': 'vote_average.desc', 'vote_count.gte': 20}, 'item_limit': 40, 'target_servers': ['emby'], 'category_id': 11},
    
    #############################################
    # CATEGORY 12: TRAKT COLLECTIONS POSTER:default.png
    #############################################
    
    # Example Trakt watchlist collection
    {
        "name": "My Trakt Watchlist",
        "source_type": "trakt_watchlist",
        "target_servers": ['emby'],
        "category_id": 12,
        "description": "Movies from your Trakt watchlist"
    },
    
    # Example Trakt collection
    {
        "name": "My Trakt Collection",
        "source_type": "trakt_collection",
        "target_servers": ['emby'],
        "category_id": 12,
        "description": "Movies from your Trakt collection"
    },
    
    # Example custom Trakt list
    {
        "name": "Top 250 Movies",
        "source_type": "trakt_list",
        "trakt_list_params": {
            "username": "lish408",
            "list_slug": "top-250-movies"
        },
        "target_servers": ['emby'],
        "category_id": 12,
        "description": "Popular Trakt list of top-rated movies"
    },
    
    # Example trending lists
    {
        "name": "Trakt Trending Movies",
        "source_type": "trakt_trending_list",
        "item_limit": 50,
        "target_servers": ['emby'],
        "category_id": 12,
        "description": "Currently trending movies on Trakt"
    },
    
    # Example popular lists
    {
        "name": "Trakt Popular Movies",
        "source_type": "trakt_popular_list",
        "item_limit": 50,
        "target_servers": ['emby'],
        "category_id": 12,
        "description": "Popular movies on Trakt"
    }

]

# Alias for compatibility with orchestration logic
RECIPES = COLLECTION_RECIPES

