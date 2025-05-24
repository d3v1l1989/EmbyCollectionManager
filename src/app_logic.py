import argparse
import sys
import logging
from src.tmdb_fetcher import TmdbClient
from src.emby_client import EmbyClient
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
                      choices=['auto', 'emby'],
                      help='Sync targets: "auto" (use available config) or "emby"')
    parser.add_argument('--custom_list', type=str, help='Path to a custom list file (JSON/YAML) for creating collections')
    
    # For backward compatibility
    parser.add_argument('--sync_emby', action='store_true', help=argparse.SUPPRESS)
    
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

    # Determine if we should sync to Emby based on args and available config
    sync_emby = False
    
    # Legacy argument handling (for backward compatibility)
    if args.sync_emby:
        sync_emby = True
        logger.warning("Using deprecated --sync_emby flag. Please use --targets instead.")
    else:
        # New approach using --targets
        emby_configured = 'emby' in config
        
        if args.targets == 'auto':
            # Auto: use if available
            sync_emby = emby_configured
            logger.info(f"Auto-detected servers: Emby={'Yes' if sync_emby else 'No'}")
        elif args.targets == 'emby':
            sync_emby = True
    
    # Initialize Emby client
    emby = None
    
    if sync_emby and 'emby' in config:
        try:
            emby = EmbyClient(
                server_url=config['emby']['server_url'],
                api_key=config['emby']['api_key'],
                user_id=config['emby']['user_id'],
                config=config
            )
            logger.info("Emby client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Emby client: {e}")
            
    if not emby:
        logger.error("No media server available for sync. Check your configuration and target selection.")
        sys.exit(1)

    # Process standard TMDb collections from recipes
    for recipe in RECIPES:
        # Check if this recipe's targets include our active server
        targets = recipe.get('target_servers', ['emby'])
        
        if 'emby' in targets and emby:
            # Get recipe info
            collection_name = recipe.get('name')
            source_type = recipe.get('source_type')
            tmdb_collection_id = recipe.get('tmdb_collection_id')
            tmdb_discover_params = recipe.get('tmdb_discover_params')
            item_limit = recipe.get('item_limit', 50)  # Default to 50 items
            
            if not collection_name:
                logger.warning(f"Skipping recipe without a name: {recipe}")
                continue
                
            logger.info(f"Processing collection: {collection_name}")
            tmdb_ids = []
            
            # Get movie IDs based on source type
            if source_type == 'tmdb_collection' or source_type == 'tmdb_series_collection':
                if not tmdb_collection_id:
                    logger.warning(f"Recipe {collection_name} is missing tmdb_collection_id")
                    continue
                
                # For franchise/series collections, sort by release date by default,
                # but allow recipe to override with specific sort order
                sort_by = recipe.get('sort_by', 'release_date')
                logger.info(f"Fetching movies for TMDb collection {tmdb_collection_id} (sorting by {sort_by})")
                collection_movies = tmdb.get_collection_movies(tmdb_collection_id, item_limit, sort_by)
                tmdb_ids = [movie['id'] for movie in collection_movies]
            
            elif source_type == 'tmdb_discover' or source_type == 'tmdb_discover_individual_movies':
                if not tmdb_discover_params:
                    logger.warning(f"Recipe {collection_name} is missing tmdb_discover_params")
                    continue
                    
                logger.info(f"Discovering movies using: {tmdb_discover_params}")
                discovered_movies = tmdb.discover_movies(tmdb_discover_params, item_limit)
                tmdb_ids = [movie['id'] for movie in discovered_movies]
            
            else:
                logger.warning(f"Unsupported source_type '{source_type}' for {collection_name}")
                continue
                
            logger.info(f"Found {len(tmdb_ids)} movies for collection \"{collection_name}\"")
            
            # Prepare artwork URLs
            poster_url = None
            backdrop_url = None
            
            try:
                collection_id = _sync_collection(emby, collection_name, tmdb_ids)

                if collection_id: # Proceed only if collection sync was successful
                    # --- BEGIN IMPROVED ARTWORK FETCHING LOGIC ---
                    # Determine if this is a TMDB collection or discover-based collection
                    if source_type == 'tmdb_series_collection' and 'tmdb_collection_id' in recipe:
                        # For TMDB collections, fetch proper collection artwork
                        tmdb_collection_id = recipe['tmdb_collection_id']
                        logger.info(f"Fetching dedicated collection artwork for TMDb collection ID {tmdb_collection_id}")
                        
                        # Get collection details first (includes basic artwork)
                        collection_details = tmdb.get_tmdb_series_collection_details(tmdb_collection_id)
                        if collection_details:
                            # Try to get basic poster/backdrop from collection details
                            if collection_details.get('poster_path'):
                                poster_url = tmdb.get_image_url(collection_details['poster_path'])
                                logger.info(f"Found collection poster for '{collection_name}': {poster_url}")
                            if collection_details.get('backdrop_path'):
                                backdrop_url = tmdb.get_image_url(collection_details['backdrop_path'])
                                logger.info(f"Found collection backdrop for '{collection_name}': {backdrop_url}")
                                
                            # If still no poster, try the dedicated images endpoint for more options
                            if not poster_url or not backdrop_url:
                                collection_images = tmdb.get_collection_images(tmdb_collection_id)
                                if collection_images:
                                    if not poster_url and collection_images.get('posters') and len(collection_images['posters']) > 0:
                                        # Get highest voted poster
                                        sorted_posters = sorted(collection_images['posters'], 
                                                             key=lambda x: x.get('vote_average', 0), reverse=True)
                                        poster_path = sorted_posters[0].get('file_path')
                                        if poster_path:
                                            poster_url = tmdb.get_image_url(poster_path)
                                            logger.info(f"Found collection poster from images API for '{collection_name}': {poster_url}")
                                    
                                    if not backdrop_url and collection_images.get('backdrops') and len(collection_images['backdrops']) > 0:
                                        # Get highest voted backdrop
                                        sorted_backdrops = sorted(collection_images['backdrops'], 
                                                               key=lambda x: x.get('vote_average', 0), reverse=True)
                                        backdrop_path = sorted_backdrops[0].get('file_path')
                                        if backdrop_path:
                                            backdrop_url = tmdb.get_image_url(backdrop_path)
                                            logger.info(f"Found collection backdrop from images API for '{collection_name}': {backdrop_url}")
                        else:
                            logger.warning(f"Could not fetch collection details for TMDb collection ID {tmdb_collection_id}")
                    
                    # NOTE: We're no longer falling back to movie artwork here automatically.  
                    # Instead, we'll let the EmbyClient.update_collection_artwork method handle
                    # poster generation and fallbacks in the right priority order:
                    # 1. Use TMDb collection poster if available (which we've attempted to get above)
                    # 2. Generate custom poster if enabled in config
                    # 3. Only then fall back to movie artwork as last resort
                    
                    # Get backdrop from first movie as it's usually a good choice regardless
                    if not backdrop_url and tmdb_ids:
                        try:
                            # Only fetch the backdrop, not the poster
                            representative_movie_id = tmdb_ids[0]
                            logger.debug(f"Fetching details for movie ID {representative_movie_id} to get backdrop for collection '{collection_name}'.")
                            movie_details = tmdb.get_movie_details(representative_movie_id)
                            if movie_details and movie_details.get('backdrop_path'):
                                backdrop_url = tmdb.get_image_url(movie_details['backdrop_path'])
                                logger.info(f"Using backdrop from movie ID {representative_movie_id} for collection '{collection_name}': {backdrop_url}")
                        except Exception as e_art:
                            logger.error(f"Error fetching movie backdrop for collection '{collection_name}': {e_art}")
                    elif not tmdb_ids:
                        logger.info(f"No movies in collection '{collection_name}', skipping artwork update attempt.")
                    else:
                        logger.info(f"Successfully found collection artwork for '{collection_name}'")
                    # --- END IMPROVED ARTWORK FETCHING LOGIC ---

                    if poster_url or backdrop_url: # Condition now checks the fetched URLs
                        logger.info(f"Attempting to update artwork for Emby collection '{collection_name}' (ID: {collection_id})")
                        if emby.update_collection_artwork(collection_id, poster_url, backdrop_url):
                            logger.info(f"Successfully initiated artwork update for Emby collection '{collection_name}'")
                        else:
                            logger.warning(f"Call to update_collection_artwork for '{collection_name}' returned false or failed.")
                    else:
                        logger.info(f"No artwork URLs found or specified for collection '{collection_name}', skipping artwork update.")
            except Exception as e:
                logger.error(f"Error processing collection '{collection_name}' for Emby: {e}")

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

def process_custom_list(list_info: Dict[str, Any], tmdb_client: TmdbClient, emby_client=None) -> None:
    """
    Process a custom list definition and create/update a collection.
    
    Args:
        list_info: Dictionary containing list information
        tmdb_client: TMDb client instance
        emby_client: Emby client instance (for future implementation)
    """
    logger.error("Custom lists feature is not currently supported for Emby")

if __name__ == '__main__':
    main()
