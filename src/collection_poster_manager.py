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
    
    # Get the category number for this collection - will be used throughout the function
    category_number = find_collection_category(collection_name, recipes_file_path)
    logger.info(f"Collection '{collection_name}' belongs to category {category_number if category_number else 'unknown'}")
    
    # Skip poster generation for franchise collections (they use TMDb posters)
    if category_number and is_franchise_collection(category_number, category_poster_map):
        logger.info(f"Skipping poster generation for franchise collection '{collection_name}'")
        return None
    
    # Add Docker-specific debugging for collection category
    logger.info(f"[DOCKER DEBUG] Generate poster for collection: '{collection_name}'")
    logger.info(f"[DOCKER DEBUG] Recipes file path: {recipes_file_path}")
    logger.info(f"[DOCKER DEBUG] Resources directory: {resources_dir}")
    logger.info(f"[DOCKER DEBUG] Category map has {len(category_poster_map) if category_poster_map else 0} entries")
    
    # Get the category number for logging purposes
    category_number = find_collection_category(collection_name, recipes_file_path)
    logger.info(f"[DOCKER DEBUG] Found category number: {category_number}")
    
    if category_number and category_number in category_poster_map:
        logger.info(f"[DOCKER DEBUG] Category {category_number} maps to: {category_poster_map[category_number]}")
    
    # Get the appropriate template for this collection
    template_name = get_poster_template_for_collection(collection_name, category_poster_map, recipes_file_path)
    logger.info(f"[DOCKER DEBUG] Template name from mapper: {template_name}")
    
    # IMPORTANT FIX: Don't return None if no template found, let the poster generator use default
    if not template_name:
        logger.warning(f"No poster template found for collection '{collection_name}', will use default")
        # Instead of returning None, we'll pass None to the generator which will use default
    
    # Check if the template exists
    templates_dir = os.path.join(resources_dir, "templates")
    
    # Log available templates for debugging
    try:
        available_templates = os.listdir(templates_dir)
        logger.info(f"[DOCKER DEBUG] Available templates in {templates_dir}: {available_templates}")
    except Exception as e:
        logger.error(f"[DOCKER DEBUG] Error listing templates: {e}")
    
    if template_name:
        template_path = os.path.join(templates_dir, template_name)
        template_exists = os.path.exists(template_path)
        logger.info(f"[DOCKER DEBUG] Template path: {template_path}, exists: {template_exists}")
        
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