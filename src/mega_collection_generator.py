import os
import logging
import time
from typing import List, Dict, Any, Optional
import yaml

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import all the collection generators
from studio_collections import generate_studio_collections
from theme_collections import generate_theme_collections
from international_collections import (
    generate_country_collections, 
    generate_language_collections,
    generate_world_cinema_collections
)
from artist_collections import (
    generate_cinematographer_collections,
    generate_composer_collections,
    generate_more_franchise_collections
)
from enhanced_recipe_generator import (
    get_tmdb_api_key,
    generate_genre_recipes,
    generate_genre_combination_recipes,
    generate_director_recipes,
    generate_actor_recipes,
    generate_decade_recipes,
    generate_award_winning_recipes,
    get_popular_tmdb_collections,
    generate_custom_discover_recipes,
    generate_keyword_based_recipes
)

def save_recipes_to_file(recipes: List[Dict[str, Any]], filename: str = "mega_recipes.py") -> None:
    """Save generated recipes to a Python file."""
    output_path = os.path.join(os.path.dirname(__file__), filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("from typing import List, Dict, Any\n\n")
        f.write("# Auto-generated mega collection recipes\n")
        f.write("MEGA_COLLECTION_RECIPES: List[Dict[str, Any]] = [\n")
        
        for recipe in recipes:
            f.write(f"    {repr(recipe)},\n")
        
        f.write("]\n\n")
        f.write("# Alias for compatibility with orchestration logic\n")
        f.write("RECIPES = MEGA_COLLECTION_RECIPES\n")
    
    logger.info(f"Saved {len(recipes)} recipes to {output_path}")

def generate_all_mega_collections() -> List[Dict[str, Any]]:
    """Generate all types of collection recipes from all generators."""
    start_time = time.time()
    api_key = get_tmdb_api_key()
    if not api_key:
        logger.error("Cannot generate recipes without a valid TMDb API key")
        return []
    
    all_recipes = []
    
    # Original collections from enhanced_recipe_generator
    logger.info("Generating original enhanced collections...")
    all_recipes.extend(generate_genre_recipes(api_key))
    all_recipes.extend(generate_genre_combination_recipes(api_key))
    all_recipes.extend(generate_director_recipes(api_key))
    all_recipes.extend(generate_actor_recipes(api_key))
    all_recipes.extend(generate_decade_recipes(api_key))
    all_recipes.extend(generate_award_winning_recipes(api_key))
    all_recipes.extend(get_popular_tmdb_collections(api_key))
    all_recipes.extend(generate_custom_discover_recipes())
    all_recipes.extend(generate_keyword_based_recipes(api_key))
    
    # New collection types
    logger.info("Generating studio collections...")
    all_recipes.extend(generate_studio_collections())
    
    logger.info("Generating theme collections...")
    all_recipes.extend(generate_theme_collections())
    
    logger.info("Generating international collections...")
    all_recipes.extend(generate_country_collections())
    all_recipes.extend(generate_language_collections())
    all_recipes.extend(generate_world_cinema_collections())
    
    logger.info("Generating artist collections...")
    all_recipes.extend(generate_cinematographer_collections(api_key))
    all_recipes.extend(generate_composer_collections(api_key))
    
    logger.info("Generating additional franchise collections...")
    all_recipes.extend(generate_more_franchise_collections(api_key))
    
    # Remove duplicates by name
    unique_recipes = []
    recipe_names = set()
    
    for recipe in all_recipes:
        if recipe["name"] not in recipe_names:
            unique_recipes.append(recipe)
            recipe_names.add(recipe["name"])
    
    elapsed_time = time.time() - start_time
    logger.info(f"Generated a total of {len(unique_recipes)} unique recipes in {elapsed_time:.2f} seconds")
    
    return unique_recipes

def update_main_recipes_file(recipes: List[Dict[str, Any]]) -> None:
    """Update the main collection_recipes.py file with new recipes."""
    from collection_recipes import COLLECTION_RECIPES
    
    # Create a backup of the existing recipes file
    recipes_file = os.path.join(os.path.dirname(__file__), "collection_recipes.py")
    backup_path = f"{recipes_file}.bak"
    
    try:
        with open(recipes_file, 'r', encoding='utf-8') as original_file:
            with open(backup_path, 'w', encoding='utf-8') as backup_file:
                backup_file.write(original_file.read())
        logger.info(f"Created backup at {backup_path}")
    except Exception as e:
        logger.error(f"Failed to create backup: {str(e)}")
        return
    
    # Create a set of existing recipe names for quick lookup
    existing_names = {recipe["name"] for recipe in COLLECTION_RECIPES}
    
    # Add only new recipes that don't have the same name as existing ones
    merged_recipes = COLLECTION_RECIPES.copy()
    added_count = 0
    
    for recipe in recipes:
        if recipe["name"] not in existing_names:
            merged_recipes.append(recipe)
            existing_names.add(recipe["name"])
            added_count += 1
    
    logger.info(f"Added {added_count} new recipes to the main collection file")
    
    # Write merged recipes back to file
    try:
        with open(recipes_file, 'w', encoding='utf-8') as f:
            f.write("from typing import List, Dict, Any\n\n")
            f.write("COLLECTION_RECIPES: List[Dict[str, Any]] = [\n")
            
            # First write hand-crafted recipes (assuming first 20 are hand-crafted)
            for i, recipe in enumerate(merged_recipes[:20]):
                if i == 0:
                    f.write("    {\n")
                else:
                    f.write("    {\n")
                
                for j, (key, value) in enumerate(recipe.items()):
                    if isinstance(value, str):
                        f.write(f'        "{key}": "{value}"')
                    else:
                        f.write(f'        "{key}": {value}')
                    
                    if j < len(recipe.items()) - 1:
                        f.write(",\n")
                    else:
                        f.write("\n")
                
                if i < 19:  # Not the last hand-crafted recipe
                    f.write("    },\n")
                else:  # Last hand-crafted recipe
                    f.write("    },\n\n")
                    f.write("    # === AUTO-GENERATED RECIPES ===\n")
            
            # Then write auto-generated recipes in a more compact format
            for recipe in merged_recipes[20:]:
                f.write(f"    {repr(recipe)},\n")
            
            f.write("]\n\n")
            f.write("# Alias for compatibility with orchestration logic\n")
            f.write("RECIPES = COLLECTION_RECIPES\n")
        
        logger.info(f"Successfully wrote {len(merged_recipes)} recipes to {recipes_file}")
    except Exception as e:
        logger.error(f"Failed to write recipes to file: {str(e)}")

def main():
    """Main function to generate and save all collection recipes."""
    logger.info("Starting mega collection generator...")
    
    # Generate all collections
    all_recipes = generate_all_mega_collections()
    
    if all_recipes:
        # Save to a separate file
        save_recipes_to_file(all_recipes)
        
        # Update the main recipes file
        update_main_recipes_file(all_recipes)
        
        print(f"Successfully generated {len(all_recipes)} mega collection recipes")
        print("Collections by category:")
        
        # Count recipe types
        categories = {}
        for recipe in all_recipes:
            source_type = recipe.get("source_type", "unknown")
            categories[source_type] = categories.get(source_type, 0) + 1
        
        for category, count in categories.items():
            print(f"  - {category}: {count}")
    else:
        print("Failed to generate recipes. Check the logs for details.")

if __name__ == "__main__":
    main()
