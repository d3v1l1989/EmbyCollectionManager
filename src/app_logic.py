import argparse
import sys
import logging
from src.tmdb_fetcher import TmdbClient
from src.emby_client import EmbyClient
from src.jellyfin_client import JellyfinClient
from src.collection_recipes import RECIPES  # Assumes recipes are defined here
import yaml
import os

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
    parser.add_argument('--sync_emby', action='store_true', help='Sync Emby server')
    parser.add_argument('--sync_jellyfin', action='store_true', help='Sync Jellyfin server')
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

    emby = None
    jellyfin = None
    if args.sync_emby and 'emby' in config:
        try:
            emby = EmbyClient(
                server_url=config['emby']['server_url'],
                api_key=config['emby']['api_key'],
                user_id=config['emby']['user_id']
            )
        except Exception as e:
            logger.error(f"Failed to initialize Emby client: {e}")
    if args.sync_jellyfin and 'jellyfin' in config:
        try:
            jellyfin = JellyfinClient(
                server_url=config['jellyfin']['server_url'],
                api_key=config['jellyfin']['api_key'],
                user_id=config['jellyfin']['user_id']
            )
        except Exception as e:
            logger.error(f"Failed to initialize Jellyfin client: {e}")
    if not (emby or jellyfin):
        logger.error("No media server selected for sync. Use --sync_emby and/or --sync_jellyfin.")
        sys.exit(1)

    for recipe in RECIPES:
        logger.info(f"Processing recipe: {recipe['name']}")
        # Fetch TMDb IDs based on recipe type
        tmdb_ids = []
        try:
            if recipe['source_type'] == 'tmdb_discover_individual_movies':
                tmdb_ids = [movie['id'] for movie in tmdb.discover_movies(recipe['tmdb_discover_params'], recipe.get('item_limit'))]
            elif recipe['source_type'] == 'tmdb_series_collection':
                collection = tmdb.get_tmdb_series_collection_details(recipe['tmdb_collection_id'])
                tmdb_ids = [part['id'] for part in collection.get('parts', [])]
            else:
                logger.warning(f"Unknown recipe source_type: {recipe['source_type']}")
                continue
        except Exception as e:
            logger.error(f"Failed to fetch TMDb IDs for recipe '{recipe['name']}': {e}")
            continue
        # For each target server, sync collection
        for target in recipe.get('target_servers', ['emby', 'jellyfin']):
            if target == 'emby' and emby:
                try:
                    _sync_collection(emby, recipe['name'], tmdb_ids)
                except Exception as e:
                    logger.error(f"Error syncing '{recipe['name']}' to Emby: {e}")
            if target == 'jellyfin' and jellyfin:
                try:
                    _sync_collection(jellyfin, recipe['name'], tmdb_ids)
                except Exception as e:
                    logger.error(f"Error syncing '{recipe['name']}' to Jellyfin: {e}")

def _sync_collection(server_client, collection_name, tmdb_ids):
    logger.info(f"  Syncing collection '{collection_name}' on {server_client.__class__.__name__}")
    try:
        collection_id = server_client.get_or_create_collection(collection_name)
        if not collection_id:
            logger.error(f"    Failed to get or create collection '{collection_name}'")
            return
        owned_item_ids = server_client.get_library_item_ids_by_tmdb_ids(tmdb_ids)
        if not owned_item_ids:
            logger.warning(f"    No owned items found for collection '{collection_name}'")
            return
        success = server_client.update_collection_items(collection_id, owned_item_ids)
        if success:
            logger.info(f"    Updated collection '{collection_name}' with {len(owned_item_ids)} items.")
        else:
            logger.error(f"    Failed to update collection '{collection_name}'.")
    except Exception as e:
        logger.error(f"    Exception during syncing collection '{collection_name}': {e}")

if __name__ == '__main__':
    main()
