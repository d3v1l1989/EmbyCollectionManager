import argparse
import sys
import logging
from src.tmdb_fetcher import TmdbClient
from src.emby_client import EmbyClient
from src.jellyfin_client import JellyfinClient
from src.collection_recipes import RECIPES  # Assumes recipes are defined here
import yaml
import os
from typing import List, Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> dict:
    """
    Load YAML configuration file containing API keys and server details.
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load configuration file '{config_path}': {e}")
        raise
def main():
    parser = argparse.ArgumentParser(description="Sync TMDb collections to Emby/Jellyfin.")
    parser.add_argument('--config', type=str, default='config/config.yaml', help='Path to config YAML file')
    parser.add_argument('--targets', type=str, default='auto', 
                      choices=['auto', 'all', 'emby', 'jellyfin'],
                      help='Sync targets: "auto" (use all available configs), "all" (require both), "emby" or "jellyfin"')
    parser.add_argument('--custom_list', type=str, help='Path to a custom list file (JSON/YAML) for creating collections')
    
    # For backward compatibility
    parser.add_argument('--sync_emby', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--sync_jellyfin', action='store_true', help=argparse.SUPPRESS)
    
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except Exception as e:
        logger.critical("Exiting due to configuration load failure.")
        sys.exit(1)

    try:
        tmdb = TmdbClient(api_key=config['tmdb']['api_key'])
    except Exception as e:
        logger.critical(f"Failed to initialize TMDb client: {e}")
        sys.exit(1)

    # Determine which servers to sync based on args and available config
    sync_emby = False
    sync_jellyfin = False
    
    # Legacy argument handling (for backward compatibility)
    if args.sync_emby or args.sync_jellyfin:
        sync_emby = args.sync_emby
        sync_jellyfin = args.sync_jellyfin
        logger.warning("Using deprecated --sync_emby/--sync_jellyfin flags. Please use --targets instead.")
    else:
        # New approach using --targets
        emby_configured = 'emby' in config
        jellyfin_configured = 'jellyfin' in config
        
        if args.targets == 'auto':
            # Auto: use all available configured servers
            sync_emby = emby_configured
            sync_jellyfin = jellyfin_configured
            logger.info(f"Auto-detected servers: Emby={'Yes' if sync_emby else 'No'}, Jellyfin={'Yes' if sync_jellyfin else 'No'}")
        elif args.targets == 'all':
            # All: require both servers to be configured
            sync_emby = True
            sync_jellyfin = True
        elif args.targets == 'emby':
            sync_emby = True
        elif args.targets == 'jellyfin':
            sync_jellyfin = True
    
    # Initialize selected clients
    emby = None
    jellyfin = None
    
    if sync_emby and 'emby' in config:
        try:
            emby = EmbyClient(
                server_url=config['emby']['server_url'],
                api_key=config['emby']['api_key'],
                user_id=config['emby']['user_id']
            )
            logger.info("Emby client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Emby client: {e}")
            
    if sync_jellyfin and 'jellyfin' in config:
        try:
            jellyfin = JellyfinClient(
                server_url=config['jellyfin']['server_url'],
                api_key=config['jellyfin']['api_key'],
                user_id=config['jellyfin']['user_id']
            )
            logger.info("Jellyfin client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Jellyfin client: {e}")
            
    if not (emby or jellyfin):
        logger.error("No media server available for sync. Check your configuration and target selection.")
        sys.exit(1)

    # Handle custom list if provided
    if args.custom_list and os.path.exists(args.custom_list):
        try:
            custom_lists = load_custom_lists(args.custom_list)
            if custom_lists and jellyfin:
                logger.info(f"Processing {len(custom_lists)} custom lists from: {args.custom_list}")
                
                for custom_list in custom_lists:
                    process_custom_list(custom_list, tmdb, jellyfin)
            elif not jellyfin:
                logger.warning("Cannot process custom lists: Jellyfin client not initialized")
            elif not custom_lists:
                logger.warning(f"No valid custom lists found in {args.custom_list}")
        except Exception as e:
            logger.error(f"Error processing custom list {args.custom_list}: {e}")

    # Process standard TMDb collections from recipes
    for recipe in RECIPES:
        logger.info(f"Processing recipe: {recipe['name']}")
        # Fetch TMDb IDs based on recipe type
        tmdb_ids = []
        try:
            if recipe['source_type'] == 'tmdb_discover_individual_movies':
                # Set a reasonable limit of 1000 movies (50 pages × 20 movies per page)
                tmdb_ids = [movie['id'] for movie in tmdb.discover_movies(recipe['tmdb_discover_params'], 50)]
            elif recipe['source_type'] == 'tmdb_series_collection':
                collection = tmdb.get_tmdb_series_collection_details(recipe['tmdb_collection_id'])
                tmdb_ids = [part['id'] for part in collection.get('parts', [])]
            else:
                logger.warning(f"Unknown recipe source_type: {recipe['source_type']}")
                continue
            
            # Ensure tmdb_ids are unique to avoid duplicates
            tmdb_ids = list(dict.fromkeys(tmdb_ids))  # Preserves order while removing duplicates
        except Exception as e:
            logger.error(f"Failed to fetch TMDb IDs for recipe '{recipe['name']}': {e}")
            continue
            
        # Check if we got any movies in this collection
        if not tmdb_ids:
            logger.warning(f"No movies found for recipe '{recipe['name']}'. Skipping...")
            continue
            
        logger.info(f"Found {len(tmdb_ids)} movies for '{recipe['name']}'")

        
        # Get artwork URLs for TMDb collections
        poster_url = None
        backdrop_url = None
        collection_data = None
        
        if recipe['source_type'] == 'tmdb_series_collection' and 'collection' in locals():
            # We already fetched the collection data above
            collection_data = collection
        elif recipe['source_type'] == 'tmdb_discover_individual_movies' and len(tmdb_ids) > 0:
            # For custom collections, try to get artwork from the first movie
            try:
                first_movie = tmdb.get_movie_details(tmdb_ids[0])
                if first_movie:
                    # Use the first movie's poster/backdrop as the collection artwork
                    if 'poster_path' in first_movie and first_movie['poster_path']:
                        poster_url = tmdb.get_image_url(first_movie['poster_path'])
                    if 'backdrop_path' in first_movie and first_movie['backdrop_path']:
                        backdrop_url = tmdb.get_image_url(first_movie['backdrop_path'])
            except Exception as e:
                logger.warning(f"Could not fetch artwork for first movie in collection '{recipe['name']}': {e}")
        
        # If we have collection data, extract artwork URLs
        if collection_data:
            artwork = tmdb.get_artwork_for_collection(collection_data)
            poster_url = artwork['poster']
            backdrop_url = artwork['backdrop']
            
        if poster_url or backdrop_url:
            logger.info(f"Found artwork for collection '{recipe['name']}'")
        
        # For each target server based on configured targets, sync collection
        recipe_targets = recipe.get('target_servers', ['emby', 'jellyfin'])
        
        # If Emby is enabled and the recipe targets Emby, sync to Emby
        if emby and ('emby' in recipe_targets):
            try:
                collection_id = _sync_collection(emby, recipe['name'], tmdb_ids)
                if collection_id and (poster_url or backdrop_url):
                    logger.info(f"Updating artwork for Emby collection '{recipe['name']}'")
                    if emby.update_collection_artwork(collection_id, poster_url, backdrop_url):
                        logger.info(f"Successfully updated artwork for Emby collection '{recipe['name']}'")
                    else:
                        logger.warning(f"Failed to update artwork for Emby collection '{recipe['name']}'")
            except Exception as e:
                logger.error(f"Error syncing '{recipe['name']}' to Emby: {e}")
                
        # If Jellyfin is enabled and the recipe targets Jellyfin, sync to Jellyfin
        if jellyfin and ('jellyfin' in recipe_targets):
            try:
                collection_id = _sync_collection(jellyfin, recipe['name'], tmdb_ids)
                if collection_id and (poster_url or backdrop_url):
                    logger.info(f"Updating artwork for Jellyfin collection '{recipe['name']}'")
                    if jellyfin.update_collection_artwork(collection_id, poster_url, backdrop_url):
                        logger.info(f"Successfully updated artwork for Jellyfin collection '{recipe['name']}'")
                    else:
                        logger.warning(f"Failed to update artwork for Jellyfin collection '{recipe['name']}'")
            except Exception as e:
                logger.error(f"Error syncing '{recipe['name']}' to Jellyfin: {e}")

def _sync_collection(server_client, collection_name, tmdb_ids):
    """
    Sync a collection to a media server. Creates the collection if it doesn't exist,
    and adds the matching library items to it.
    
    Args:
        server_client: The media server client (Emby/Jellyfin)
        collection_name: Name of the collection
        tmdb_ids: List of TMDb movie IDs to add to the collection
        
    Returns:
        The collection ID if successful, None otherwise
    """
    logger.info(f"  Syncing collection '{collection_name}' on {server_client.__class__.__name__}")
    try:
        collection_id = server_client.get_or_create_collection(collection_name)
        if not collection_id:
            logger.error(f"    Failed to get or create collection '{collection_name}'")
            return None
            
        owned_item_ids = server_client.get_library_item_ids_by_tmdb_ids(tmdb_ids)
        if not owned_item_ids:
            logger.warning(f"    No owned items found for collection '{collection_name}'")
            return collection_id  # Still return the ID for artwork updates
        
        # Ensure no duplicate item IDs
        unique_item_ids = list(dict.fromkeys(owned_item_ids))
        if len(unique_item_ids) < len(owned_item_ids):
            logger.info(f"    Removed {len(owned_item_ids) - len(unique_item_ids)} duplicate items from collection '{collection_name}'")
            
        success = server_client.update_collection_items(collection_id, unique_item_ids)
        if success:
            logger.info(f"    Updated collection '{collection_name}' with {len(unique_item_ids)} unique items")
        else:
            logger.error(f"    Failed to update collection '{collection_name}'.")            
        return collection_id
    except Exception as e:
        logger.error(f"    Exception during syncing collection '{collection_name}': {e}")
        return None

def load_custom_lists(file_path: str) -> List[Dict[str, Any]]:
    """
    Load custom lists from a YAML or JSON file.
    
    Args:
        file_path: Path to the list file
        
    Returns:
        List of custom list definitions
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                return yaml.safe_load(f)
            elif file_path.endswith('.json'):
                import json
                return json.load(f)
            else:
                logger.error(f"Unsupported file format: {file_path}. Use .yaml, .yml, or .json")
                return []
    except Exception as e:
        logger.error(f"Failed to load custom lists from '{file_path}': {e}")
        return []

def process_custom_list(list_info: Dict[str, Any], tmdb_client: TmdbClient, jellyfin_client: JellyfinClient) -> None:
    """
    Process a custom list definition and create/update a Jellyfin collection.
    
    Args:
        list_info: Dictionary containing list information
        tmdb_client: TMDb client instance
        jellyfin_client: Jellyfin client instance
    """
    try:
        list_name = list_info.get('name')
        list_id = list_info.get('list_id', str(hash(list_name)))  # Generate ID if not provided
        description = list_info.get('description')
        items = list_info.get('items', [])
        clear_collection = list_info.get('clear_collection', False)
        
        if not list_name or not items:
            logger.error("Custom list must have 'name' and 'items' properties")
            return
            
        logger.info(f"Processing custom list: {list_name} with {len(items)} items")
        
        # Find or create the collection
        collection_id = jellyfin_client.find_collection_with_name_or_create(
            list_name,
            list_id,
            description,
            'custom_list'
        )
        
        if not collection_id:
            logger.error(f"Failed to create collection for '{list_name}'")
            return
            
        # Optionally clear the collection first
        if clear_collection:
            jellyfin_client.clear_collection(collection_id)
            
        # Process each item
        matched_count = 0
        for item in items:
            # If item is just a TMDb ID (integer or string number)
            if isinstance(item, (int, str)) and str(item).isdigit():
                # Convert to a proper item dict with TMDb ID
                item_info = {'id': int(item)}
                # Try to get title and year from TMDb
                movie_details = tmdb_client.get_movie_details(item_info['id'])
                if movie_details:
                    item_info['title'] = movie_details.get('title')
                    if 'release_date' in movie_details and movie_details['release_date']:
                        item_info['year'] = int(movie_details['release_date'][:4])
            elif not isinstance(item, dict):
                logger.warning(f"Skipping invalid item format: {item}")
                continue
            else:
                # Item is already a dictionary
                item_info = item
                
            # Add the item to the collection
            if jellyfin_client.add_item_to_collection(collection_id, item_info):
                matched_count += 1
                
        logger.info(f"Added {matched_count} of {len(items)} items to collection '{list_name}'")
        
        # Add a poster if needed
        if not jellyfin_client.has_poster(collection_id):
            logger.info(f"Generating poster for collection '{list_name}'")
            if jellyfin_client.make_poster(collection_id, list_name):
                logger.info("Successfully created poster")
            else:
                logger.warning("Failed to create poster")
                
    except Exception as e:
        logger.error(f"Error processing custom list: {e}")

if __name__ == '__main__':
    main()
