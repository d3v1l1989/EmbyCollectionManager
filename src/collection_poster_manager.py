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
    category_poster_map: Optional[Dict[int, Dict[str, str]]] = None,
    category_id: Optional[int] = None
) -> Optional[str]:
    """
    Generate a custom poster for a collection based on its category.
    
    Args:
        collection_name: Name of the collection
        recipes_file_path: Path to the collection_recipes.py file
        resources_dir: Path to the resources directory
        category_poster_map: Optional pre-extracted categories with poster mappings
        category_id: Optional direct category ID from the collection recipe
        
    Returns:
        Path to the generated poster file or None if generation failed/not applicable
    """
    # Extract categories if not provided
    if category_poster_map is None:
        category_poster_map = parse_collection_categories(recipes_file_path)
    
    # Use provided category_id if available, otherwise find from file
    if category_id is not None:
        category_number = category_id
        logger.info(f"Using provided category_id {category_id} for collection '{collection_name}'")
    else:
        category_number = find_collection_category(collection_name, recipes_file_path)
        logger.info(f"Collection '{collection_name}' belongs to category {category_number if category_number else 'unknown'}")
    
    # Skip poster generation for franchise collections (they use TMDb posters)
    if category_number and is_franchise_collection(category_number, category_poster_map):
        logger.info(f"Skipping poster generation for franchise collection '{collection_name}'")
        return None
    
    # Add logging for collection poster generation
    logger.info(f"Generating poster for collection: '{collection_name}'")
    logger.info(f"Resources directory: {resources_dir}")
    logger.info(f"Category map has {len(category_poster_map) if category_poster_map else 0} entries")
    
    # Log the category ID we're using
    logger.info(f"Using category_id: {category_id}")
    
    if category_id and category_id in category_poster_map:
        logger.info(f"Category {category_id} maps to: {category_poster_map[category_id]}")
    
    # Get the appropriate template for this collection
    template_name = get_poster_template_for_collection(
        collection_name=collection_name, 
        category_poster_map=category_poster_map, 
        recipes_file_path=recipes_file_path,
        category_id=category_number
    )
    
    # IMPORTANT FIX: Don't return None if no template found, let the poster generator use default
    if not template_name:
        logger.warning(f"No poster template found for collection '{collection_name}', will use default")
        # Instead of returning None, we'll pass None to the generator which will use default
    
    # Check if the template exists
    templates_dir = os.path.join(resources_dir, "templates")
    
    
    if template_name:
        template_path = os.path.join(templates_dir, template_name)
        template_exists = os.path.exists(template_path)
        
        if not template_exists:
            logger.warning(f"Template file not found: {template_path}, will use default")
            # Instead of returning None, we'll pass None to the generator which will use default
            template_name = None
    
    # Generate the poster with template_name (which might be None, in which case default will be used)
    poster_path = generate_custom_poster(
        collection_name=collection_name,
        template_name=template_name,  # This might be None, in which case poster_generator will use default
        resources_dir=resources_dir
    )
    
    if poster_path:
        template_used = template_name if template_name else "default.png"
        logger.info(f"Generated poster for collection '{collection_name}' using template '{template_used}'")
        return poster_path
    else:
        logger.error(f"Failed to generate poster for collection '{collection_name}'")
        return None

