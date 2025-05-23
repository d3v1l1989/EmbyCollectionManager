#!/usr/bin/env python3
"""
Test script to check what SortName values are actually stored in Emby for items in a collection.
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
import requests
import argparse

# Import ConfigLoader
from src.config_loader import ConfigLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_sort_names(server_url: str, api_key: str, user_id: str, collection_id: str, limit: int = 5) -> None:
    """
    Debug utility to check what SortName values are actually stored in Emby for items in a collection.
    Args:
        server_url: The Emby server URL
        api_key: The Emby API key
        user_id: The Emby user ID
        collection_id: The Emby collection ID to check items for
        limit: Maximum number of items to check (default 5)
    """
    # Create a session with proper headers
    session = requests.Session()
    session.headers.update({
        'X-Emby-Token': api_key,
        'Accept': 'application/json'
    })
    
    def make_api_request(method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Helper to make API requests"""
        try:
            current_params = params or {}
            if 'api_key' not in current_params:
                current_params['api_key'] = api_key
                
            url = f"{server_url}{endpoint}" if not endpoint.lower().startswith('http') else endpoint
            response = session.request(method, url, params=current_params, timeout=30, **kwargs)
            response.raise_for_status()
            
            if response.status_code == 204:  # No Content
                return None
            
            return response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None

    logger.info(f"==== DEBUG: Checking SortName values for collection {collection_id} =====")
    
    # 1. First check the collection itself
    collection_data = make_api_request('GET', f"/Users/{user_id}/Items/{collection_id}")
    if collection_data:
        logger.info(f"Collection: {collection_data.get('Name')} (ID: {collection_id})")
        logger.info(f"  - DisplayOrder: {collection_data.get('DisplayOrder', 'NOT SET')}")
        logger.info(f"  - SortName: {collection_data.get('SortName', 'NOT SET')}")
        logger.info(f"  - LockedFields: {collection_data.get('LockedFields', [])}")
    else:
        logger.error(f"Could not retrieve collection {collection_id}")
        return
        
    # 2. Get the collection items
    collection_items_url = f"/Users/{user_id}/Items?ParentId={collection_id}&Limit={limit}&Fields=SortName"
    items_data = make_api_request('GET', collection_items_url)
    
    if not items_data or 'Items' not in items_data or not items_data['Items']:
        logger.info(f"No items found in collection {collection_id}")
        return
    
    # 3. Check each item's SortName in various places
    for item in items_data['Items']:
        item_id = item.get('Id')
        item_name = item.get('Name', 'Unknown')
        
        # Check direct item data from the collection listing
        logger.info(f"Item: {item_name} (ID: {item_id})")
        logger.info(f"  - SortName in collection response: {item.get('SortName', 'NOT SET')}")
        
        # Get full item details
        item_details = make_api_request('GET', f"/Users/{user_id}/Items/{item_id}")
        if item_details:
            logger.info(f"  - SortName in full item data: {item_details.get('SortName', 'NOT SET')}")
            logger.info(f"  - ForcedSortName in item data: {item_details.get('ForcedSortName', 'NOT SET')}")
            logger.info(f"  - LockedFields: {item_details.get('LockedFields', [])}")
        
        # Check display preferences
        pref_url = f"{server_url}/DisplayPreferences/items/{item_id}?api_key={api_key}&userId={user_id}"
        pref_resp = session.get(pref_url, timeout=15)
        
        if pref_resp.status_code == 200:
            try:
                pref_data = pref_resp.json()
                custom_prefs = pref_data.get('CustomPrefs', {})
                logger.info(f"  - Display preferences SortName: {custom_prefs.get('SortName', 'NOT SET')}")
                logger.info(f"  - Display preferences ForcedSortName: {custom_prefs.get('ForcedSortName', 'NOT SET')}")
            except Exception as e:
                logger.info(f"  - Error parsing display preferences: {e}")
        else:
            logger.info(f"  - No display preferences found (status: {pref_resp.status_code})")
            
        logger.info("-----------------------------------")
    
    logger.info(f"==== END DEBUG: Checked {min(limit, len(items_data['Items']))} items =====")


def main():
    """Main entry point with command line arguments"""
    parser = argparse.ArgumentParser(description="Check SortName values in Emby for a collection")
    parser.add_argument("--collection", "-c", dest="collection_id", required=True, 
                        help="Emby collection ID to check")
    parser.add_argument("--limit", "-l", dest="limit", type=int, default=5,
                        help="Number of items to check (default: 5)")
    parser.add_argument("--server", "-s", dest="server_url", 
                        help="Emby server URL (default: from config.yaml)")
    parser.add_argument("--apikey", "-a", dest="api_key",
                        help="Emby API key (default: from config.yaml)")
    parser.add_argument("--userid", "-u", dest="user_id",
                        help="Emby user ID (default: from config.yaml)")
    
    args = parser.parse_args()
    
    # Load config.yaml
    config = ConfigLoader(yaml_path="config/config.yaml")
    
    # Get credentials from config.yaml or command line
    server_url = args.server_url or config.get("EMBY_URL")
    api_key = args.api_key or config.get("EMBY_API_KEY")
    user_id = args.user_id or config.get("EMBY_USER_ID")
    
    if not server_url or not api_key or not user_id:
        logger.error("Missing credentials. Please set EMBY_URL, EMBY_API_KEY, and EMBY_USER_ID in config/config.yaml file or provide via command line")
        sys.exit(1)
    
    check_sort_names(server_url, api_key, user_id, args.collection_id, args.limit)


if __name__ == "__main__":
    main()
