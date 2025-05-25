"""
Collection Poster Mapper Module for TMDbCollector

This module provides functionality to map collections to their appropriate poster templates
based on their category IDs and CATEGORY_CONFIG in collection_recipes.py.
"""

import os
import logging
import importlib.util
import sys
from typing import Dict, Optional

# Configure logger
logger = logging.getLogger(__name__)

def load_category_config(recipes_file_path: str) -> Dict[int, Dict[str, str]]:
    """
    Load the CATEGORY_CONFIG dictionary from collection_recipes.py.
    
    Args:
        recipes_file_path: Path to the collection_recipes.py file
        
    Returns:
        The CATEGORY_CONFIG dictionary mapping category numbers to their properties
    """
    try:
        # Get the directory containing the recipes file
        recipes_dir = os.path.dirname(recipes_file_path)
        
        # Make sure the directory is in the Python path
        if recipes_dir not in sys.path:
            sys.path.append(recipes_dir)
        
        # Get the module name (filename without extension)
        module_name = os.path.basename(recipes_file_path).split('.')[0]
        
        # Import the module dynamically
        spec = importlib.util.spec_from_file_location(module_name, recipes_file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Get the CATEGORY_CONFIG dictionary
        if hasattr(module, 'CATEGORY_CONFIG'):
            category_config = module.CATEGORY_CONFIG
            logger.info(f"Successfully loaded CATEGORY_CONFIG with {len(category_config)} categories")
            
            # Fix any tmdb.jpg references to use tmdb.png instead
            for cat_id, cat_info in category_config.items():
                if cat_info.get('poster') == 'tmdb.jpg':
                    cat_info['poster'] = 'tmdb.png'
                    logger.info(f"Updated template for category {cat_id} from 'tmdb.jpg' to 'tmdb.png'")
                    
            # Log loaded categories for debugging
            for cat_id, cat_info in category_config.items():
                logger.info(f"Category {cat_id}: '{cat_info.get('name')}' uses template '{cat_info.get('poster')}'")    
                
            return category_config
        else:
            logger.warning(f"CATEGORY_CONFIG not found in {recipes_file_path}")
            return {}
            
    except Exception as e:
        logger.error(f"Error loading CATEGORY_CONFIG from {recipes_file_path}: {e}")
        return {}

# Alias for backward compatibility
parse_collection_categories = load_category_config

def get_poster_template_for_collection(
    collection_name: str, 
    category_poster_map: Dict[int, Dict[str, str]], 
    recipes_file_path: str,
    category_id: Optional[int] = None
) -> Optional[str]:
    """
    Get the appropriate poster template filename for a collection based on its category ID.
    
    Args:
        collection_name: Name of the collection
        category_poster_map: Dictionary mapping category numbers to poster information
        recipes_file_path: Path to the collection_recipes.py file (not used if category_id is provided)
        category_id: Category ID from the collection recipe
        
    Returns:
        Poster template filename or None if not applicable/found
    """
    # Add debug logging
    logger.info(f"Finding poster template for collection: '{collection_name}'")
    logger.info(f"Category map has {len(category_poster_map)} categories: {list(category_poster_map.keys())}")
    
    # Check if we have a valid category ID
    if category_id is None:
        logger.warning(f"No category ID provided for collection '{collection_name}', using default template")
        return "default.png"
    
    category_number = category_id
    logger.info(f"Using category ID {category_id} for collection '{collection_name}'")
    
    # Get the template directly from the category_poster_map which contains the CATEGORY_CONFIG from collection_recipes.py
    # This ensures we're using the official mapping from the config file
    category_info = category_poster_map.get(category_number)
    
    if not category_info:
        # Fallback to default poster if no template assigned to category
        logger.warning(f"Using default poster for category {category_number} - no template assigned")
        return "default.png"
    
    # Get the poster template from the category info
    poster_template = category_info.get('poster')
    
    # Special case for franchise collections which use TMDb posters
    if category_info.get('name') == "FRANCHISE COLLECTIONS" or \
       (isinstance(poster_template, str) and "uses TMDB API" in poster_template.lower()):
        logger.info(f"Category {category_number} is a franchise collection, using TMDb API poster")
        return None
    
    # Fix the tmdb.jpg to tmdb.png issue
    if poster_template == "tmdb.jpg":
        poster_template = "tmdb.png"
        logger.info(f"Converted tmdb.jpg to tmdb.png for category {category_number}")
    
    logger.info(f"Using template '{poster_template}' from CATEGORY_CONFIG for category {category_number}")
    return poster_template

def check_poster_template_exists(template_name: str, templates_dir: str) -> bool:
    """
    Check if a poster template exists in the templates directory.
    
    Args:
        template_name: Name of the template file
        templates_dir: Path to the templates directory
        
    Returns:
        True if the template exists, False otherwise
    """
    template_path = os.path.join(templates_dir, template_name)
    return os.path.exists(template_path)

def is_franchise_collection(category_number: int, category_poster_map: Dict[int, Dict[str, str]]) -> bool:
    """
    Determine if a category is for franchise collections (which use TMDb posters).
    
    Args:
        category_number: The category number to check
        category_poster_map: Dictionary mapping category numbers to poster information
        
    Returns:
        True if it's a franchise category, False otherwise
    """
    # Check the category in the category_poster_map
    category_info = category_poster_map.get(category_number)
    if not category_info:
        return False
    
    # Check if this is the franchise category by name
    if category_info.get('name') == "FRANCHISE COLLECTIONS":
        return True
        
    # Check if the poster description indicates it uses TMDb API
    poster_info = category_info.get('poster')
    if isinstance(poster_info, str) and "uses TMDB API" in poster_info.lower():
        return True
        
    return False