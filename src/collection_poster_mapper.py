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
            return module.CATEGORY_CONFIG
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
    
    # Explicitly map category numbers to template files for clarity
    # This serves as the primary source of truth for category-to-template mapping
    category_to_template_map = {
        1: "tmdb.png",          # TMDb GENERAL COLLECTIONS
        2: None,                # FRANCHISE COLLECTIONS (use TMDb posters)
        3: "genres.jpg",        # GENRE COLLECTIONS
        4: "genres.jpg",        # MIXED GENRE COLLECTIONS
        5: "director.jpg",      # DIRECTOR COLLECTIONS
        6: "actor.jpg",         # ACTOR COLLECTIONS
        7: "decade.jpg",        # DECADE COLLECTIONS
        8: None,                # POPULAR & CURATED COLLECTIONS (may use TMDb posters)
        9: "award.jpg",         # AWARD-WINNING COLLECTIONS
        10: "studio.jpg",       # STUDIO COLLECTIONS
        11: "themes.jpg",       # THEME & KEYWORD COLLECTIONS
        12: "languages.jpg",    # LANGUAGE & REGIONAL CINEMA
        13: "languages.jpg",    # REGIONAL CINEMA GROUPS
        14: "director.jpg",     # CINEMATOGRAPHER COLLECTIONS (use director template)
        15: "director.jpg"      # COMPOSER COLLECTIONS (use director template)
    }
    
    # First check our explicit map
    if category_number in category_to_template_map:
        template = category_to_template_map[category_number]
        if template:
            logger.info(f"Using template '{template}' for category {category_number}")
            return template
        elif template is None and category_number in [2, 8]:  # Franchise collections
            logger.info(f"Using TMDb API poster for franchise collection in category {category_number}")
            return None
    
    # If not in our map, try the category_poster_map as backup
    category_info = category_poster_map.get(category_number)
    if not category_info:
        # Fallback to default poster if no template assigned to category
        logger.warning(f"Using default poster for category {category_number} - no template assigned")
        return "default.png"
    
    # Special case for franchise collections which use TMDb posters
    if category_info.get('name') == "FRANCHISE COLLECTIONS" or \
       (isinstance(category_info.get('poster'), str) and "uses TMDB API" in category_info['poster'].lower()):
        logger.info(f"Category {category_number} is a franchise collection, using TMDb API poster")
        return None
    
    logger.info(f"Using template '{category_info['poster']}' from category_info")
    return category_info['poster']

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
    # First check the hardcoded franchise categories
    if category_number in [2, 8]:
        return True
        
    # Then check the category_poster_map
    category_info = category_poster_map.get(category_number)
    if not category_info:
        return False
    
    # Check if this is the franchise category or if it uses TMDb API for posters
    return (category_info.get('name') == "FRANCHISE COLLECTIONS" or 
            (isinstance(category_info.get('poster'), str) and "uses TMDB API" in category_info['poster'].lower()))