"""
Collection Poster Mapper Module for TMDbCollector

This module provides functionality to map collections to their appropriate poster templates
based on their categories in the collection_recipes.py file.
"""

import os
import re
import logging
import importlib.util
import sys
from typing import Dict, List, Optional, Tuple

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
            logger.warning(f"CATEGORY_CONFIG not found in {recipes_file_path}, falling back to parsing comments")
            return {}
            
    except Exception as e:
        logger.error(f"Error loading CATEGORY_CONFIG from {recipes_file_path}: {e}")
        return {}

def parse_collection_categories(recipes_file_path: str) -> Dict[int, Dict[str, str]]:
    """
    Parse the collection_recipes.py file to extract category to poster mappings.
    First tries to load the CATEGORY_CONFIG dictionary, then falls back to parsing comments if needed.
    
    Args:
        recipes_file_path: Path to the collection_recipes.py file
        
    Returns:
        Dictionary mapping category numbers to a dict with 'name' and 'poster' keys
    """
    # First try to load the CATEGORY_CONFIG dictionary
    category_config = load_category_config(recipes_file_path)
    
    if category_config:
        logger.info(f"Using CATEGORY_CONFIG from {recipes_file_path} with {len(category_config)} categories")
        return category_config
    
    # If that fails, fall back to parsing comments
    logger.info("Falling back to parsing category comments from recipes file")
    category_poster_map = {}
    
    # Regular expression to match category headers with poster information
    # Format: # CATEGORY X: CATEGORY_NAME POSTER:filename.jpg
    category_pattern = re.compile(r'#\s*CATEGORY\s+(\d+):\s*(.+?)\s+POSTER:([a-zA-Z0-9_.-]+)')
    
    try:
        with open(recipes_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Check if this line contains a category header with poster info
                match = category_pattern.search(line)
                if match:
                    category_number = int(match.group(1))
                    category_name = match.group(2).strip()
                    poster_filename = match.group(3).strip()
                    
                    category_poster_map[category_number] = {
                        'name': category_name,
                        'poster': poster_filename
                    }
                    
                    logger.debug(f"Found category {category_number}: '{category_name}' with poster '{poster_filename}'")
    
    except Exception as e:
        logger.error(f"Error parsing collection categories: {e}")
    
    return category_poster_map

def find_collection_category(collection_name: str, recipes_file_path: str) -> Optional[int]:
    """
    Find the category number a collection belongs to based on its position in the recipes file.
    
    Args:
        collection_name: Name of the collection
        recipes_file_path: Path to the collection_recipes.py file
        
    Returns:
        Category number or None if not found
    """
    # Special case for specific collections we know the category for
    collection_to_category_map = {
        "Popular Movies on TMDb": 1,  # TMDb GENERAL COLLECTIONS
        "Trending Movies on TMDb": 1,
        "Top Rated Movies on TMDb": 1,
        "Now Playing in Theaters": 1,
        "Upcoming Movies": 1
    }
    
    # Check if this is a known collection with a predefined category
    if collection_name in collection_to_category_map:
        category = collection_to_category_map[collection_name]
        logger.info(f"[DOCKER DEBUG] Using hardcoded category {category} for collection '{collection_name}'")
        return category
    logger.info(f"[DOCKER DEBUG] Finding category for collection: '{collection_name}'")
    logger.info(f"[DOCKER DEBUG] Using recipes file: {recipes_file_path}")
    
    # First try to load category directly from CATEGORY_CONFIG
    try:
        category_config = load_category_config(recipes_file_path)
        if category_config:
            logger.info(f"[DOCKER DEBUG] Loaded {len(category_config)} categories from CATEGORY_CONFIG")
            
            # Try a direct import of collection_recipes to check collections
            try:
                from src.collection_recipes import COLLECTION_RECIPES
                
                # Log collections we're looking for
                collection_names = [recipe.get("name") for recipe in COLLECTION_RECIPES if recipe.get("name")]
                logger.info(f"[DOCKER DEBUG] Found {len(collection_names)} collection names in COLLECTION_RECIPES")
                logger.info(f"[DOCKER DEBUG] Is our collection in the list? {collection_name in collection_names}")
                
                if collection_name in collection_names:
                    # Try to find it manually by checking adjacent collections
                    for i, recipe in enumerate(COLLECTION_RECIPES):
                        if recipe.get("name") == collection_name:
                            # Look at recipes before this one to find the last category header
                            for j in range(i, 0, -1):
                                prev_recipe = COLLECTION_RECIPES[j-1]
                                logger.info(f"[DOCKER DEBUG] Checking previous recipe: {prev_recipe.get('name')}")
            except Exception as e:
                logger.error(f"[DOCKER DEBUG] Error directly importing COLLECTION_RECIPES: {e}")
    except Exception as e:
        logger.error(f"[DOCKER DEBUG] Error loading CATEGORY_CONFIG: {e}")
    try:
        with open(recipes_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Find the collection in the file
            # Handle both formats: {'name': 'Collection Name', ...} and {"name": "Collection Name", ...}
            collection_pattern = re.compile(r'{\s*[\'"]name[\'"]\s*:\s*[\'"]' + re.escape(collection_name) + r'[\'"]')
            collection_match = collection_pattern.search(content)
            
            if not collection_match:
                logger.warning(f"Collection '{collection_name}' not found in recipes file")
                return None
            
            # Find the last category header before this collection
            collection_position = collection_match.start()
            content_before_collection = content[:collection_position]
            
            # Regular expression to match category headers
            # Format: # CATEGORY X: CATEGORY_NAME POSTER:filename.jpg
            category_pattern = re.compile(r'#\s*CATEGORY\s+(\d+):\s*(.*?)\s+POSTER:([a-zA-Z0-9_.-]+)')
            category_matches = list(category_pattern.finditer(content_before_collection))
            
            if not category_matches:
                logger.warning(f"No category found for collection '{collection_name}'")
                return None
            
            # Get the last category before this collection
            last_match = category_matches[-1]
            category_number = int(last_match.group(1))
            
            return category_number
            
    except Exception as e:
        logger.error(f"Error finding collection category: {e}")
        return None

def get_poster_template_for_collection(
    collection_name: str, 
    category_poster_map: Dict[int, Dict[str, str]], 
    recipes_file_path: str
) -> Optional[str]:
    """
    Get the appropriate poster template filename for a collection.
    
    Args:
        collection_name: Name of the collection
        category_poster_map: Dictionary mapping category numbers to poster information
        recipes_file_path: Path to the collection_recipes.py file
        
    Returns:
        Poster template filename or None if not applicable/found
    """
    # Add Docker-specific debug logging
    logger.info(f"[DOCKER DEBUG] Finding poster template for collection: '{collection_name}'")
    logger.info(f"[DOCKER DEBUG] Category map has {len(category_poster_map)} categories: {list(category_poster_map.keys())}")
    logger.info(f"[DOCKER DEBUG] Recipes file path: {recipes_file_path}")
    logger.info(f"[DOCKER DEBUG] Current working directory: {os.getcwd()}")
    # Find which category this collection belongs to
    category_number = find_collection_category(collection_name, recipes_file_path)
    if not category_number:
        # Fallback to default poster if category not found
        logger.warning(f"Using default poster for collection '{collection_name}' - category not found")
        return "default.png"
    
    # Explicitly map category numbers to template files for clarity
    category_to_template_map = {
        1: "tmdb.jpg",          # TMDb GENERAL COLLECTIONS
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
    
    # Log the mapping for debugging
    logger.info(f"[DOCKER DEBUG] Category number {category_number} for collection '{collection_name}'")
    
    # First check our explicit map
    if category_number in category_to_template_map:
        template = category_to_template_map[category_number]
        if template:
            logger.info(f"[DOCKER DEBUG] Using explicitly mapped template '{template}' for category {category_number}")
            return template
        elif template is None and category_number in [2, 8]:  # Franchise collections
            logger.info(f"[DOCKER DEBUG] Using None for franchise collection in category {category_number}")
            return None
    
    # If not in our map, try the category_poster_map as backup
    category_info = category_poster_map.get(category_number)
    if not category_info:
        # Fallback to default poster if no template assigned to category
        logger.warning(f"Using default poster for category {category_number} - no template assigned")
        return "default.png"
    
    # Special case for franchise collections which use TMDb posters
    if category_info['name'] == "FRANCHISE COLLECTIONS" or "uses TMDB API" in category_info['poster'].lower():
        logger.info(f"[DOCKER DEBUG] Category {category_number} is a franchise collection, returning None")
        return None
    
    logger.info(f"[DOCKER DEBUG] Using template '{category_info['poster']}' from category_info")
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
    category_info = category_poster_map.get(category_number)
    if not category_info:
        return False
    
    # Check if this is the franchise category or if it uses TMDb API for posters
    return (category_info['name'] == "FRANCHISE COLLECTIONS" or 
            "uses TMDB API" in category_info['poster'].lower())