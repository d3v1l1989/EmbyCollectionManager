"""
Collection Poster Manager Module for TMDbCollector

This module manages the creation of custom posters for collections based on their categories.
It identifies the appropriate template for each collection and generates a poster with text overlay.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple
import tempfile

from src.poster_generator import generate_custom_poster, cleanup_temp_posters, file_to_url
from src.collection_poster_mapper import (
    parse_collection_categories,
    find_collection_category,
    get_poster_template_for_collection,
    check_poster_template_exists,
    is_franchise_collection
)

# Configure logger
logger = logging.getLogger(__name__)

def generate_poster_for_collection(
    collection_name: str,
    recipes_file_path: str,
    resources_dir: str,
    category_poster_map: Optional[Dict[int, Dict[str, str]]] = None
) -> Optional[str]:
    """
    Generate a custom poster for a collection based on its category.
    
    Args:
        collection_name: Name of the collection
        recipes_file_path: Path to the collection_recipes.py file
        resources_dir: Path to the resources directory
        category_poster_map: Optional pre-extracted categories with poster mappings
        
    Returns:
        Path to the generated poster file or None if generation failed/not applicable
    """
    # Extract categories if not provided
    if category_poster_map is None:
        category_poster_map = parse_collection_categories(recipes_file_path)
    
    # Get the category number for this collection
    category_number = find_collection_category(collection_name, recipes_file_path)
    
    # Skip poster generation for franchise collections (they use TMDb posters)
    if category_number and is_franchise_collection(category_number, category_poster_map):
        logger.info(f"Skipping poster generation for franchise collection '{collection_name}'")
        return None
    
    # Get the appropriate template for this collection
    template_name = get_poster_template_for_collection(collection_name, category_poster_map, recipes_file_path)
    if not template_name:
        logger.warning(f"No poster template found for collection '{collection_name}'")
        return None
    
    # Check if the template exists
    templates_dir = os.path.join(resources_dir, "templates")
    template_path = os.path.join(templates_dir, template_name)
    if not os.path.exists(template_path):
        logger.error(f"Template file not found: {template_path}")
        return None
    
    # Generate the poster
    poster_path = generate_custom_poster(
        collection_name=collection_name,
        template_name=template_name,
        resources_dir=resources_dir
    )
    
    if poster_path:
        logger.info(f"Generated poster for collection '{collection_name}' using template '{template_name}'")
        return poster_path
    else:
        logger.error(f"Failed to generate poster for collection '{collection_name}'")
        return None

def generate_posters_for_all_collections(
    collection_recipes: List[Dict],
    recipes_file_path: str,
    resources_dir: str
) -> Dict[str, str]:
    """
    Generate posters for all collections in the recipes list.
    
    Args:
        collection_recipes: List of collection recipe dictionaries
        recipes_file_path: Path to the collection_recipes.py file
        resources_dir: Path to the resources directory
        
    Returns:
        Dictionary mapping collection names to poster file paths
    """
    # Clean up old temporary posters first
    cleanup_count = cleanup_temp_posters()
    if cleanup_count > 0:
        logger.info(f"Cleaned up {cleanup_count} old temporary poster files")
    
    # Extract categories once to avoid repeated parsing
    category_poster_map = parse_collection_categories(recipes_file_path)
    logger.info(f"Found {len(category_poster_map)} categories with poster assignments")
    
    # Generate posters for each collection
    poster_map = {}
    for recipe in collection_recipes:
        collection_name = recipe.get("name")
        if not collection_name:
            continue
        
        poster_path = generate_poster_for_collection(
            collection_name=collection_name,
            recipes_file_path=recipes_file_path,
            resources_dir=resources_dir,
            category_poster_map=category_poster_map
        )
        
        if poster_path:
            poster_map[collection_name] = poster_path
    
    logger.info(f"Generated {len(poster_map)} posters for collections")
    return poster_map