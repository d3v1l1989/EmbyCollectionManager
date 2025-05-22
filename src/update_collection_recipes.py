import os
import sys
import logging
from typing import List, Dict, Any
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def backup_existing_recipes(file_path: str) -> None:
    """Create a backup of the existing recipes file."""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.bak"
        try:
            with open(file_path, 'r', encoding='utf-8') as original_file:
                with open(backup_path, 'w', encoding='utf-8') as backup_file:
                    backup_file.write(original_file.read())
            logger.info(f"Created backup at {backup_path}")
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            sys.exit(1)

def merge_recipes(existing_recipes: List[Dict[str, Any]], 
                  new_recipes: List[Dict[str, Any]], 
                  overwrite: bool = False) -> List[Dict[str, Any]]:
    """Merge existing recipes with new recipes, avoiding duplicates by name."""
    if overwrite:
        return new_recipes
    
    # Create a set of existing recipe names for quick lookup
    existing_names = {recipe["name"] for recipe in existing_recipes}
    
    # Add only new recipes that don't have the same name as existing ones
    merged_recipes = existing_recipes.copy()
    added_count = 0
    
    for recipe in new_recipes:
        if recipe["name"] not in existing_names:
            merged_recipes.append(recipe)
            existing_names.add(recipe["name"])
            added_count += 1
    
    logger.info(f"Added {added_count} new recipes")
    return merged_recipes

def write_recipes_to_file(recipes: List[Dict[str, Any]], file_path: str) -> None:
    """Write recipes to a Python file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("from typing import List, Dict, Any\n\n")
            f.write("COLLECTION_RECIPES: List[Dict[str, Any]] = [\n")
            
            # First write hand-crafted recipes (assuming first 20 are hand-crafted)
            for i, recipe in enumerate(recipes[:20]):
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
                    f.write("    # === AUTO-GENERATED GENRE RECIPES ===\n")
            
            # Then write auto-generated recipes in a more compact format
            for recipe in recipes[20:]:
                f.write(f"    {repr(recipe)},\n")
            
            f.write("]\n\n")
            f.write("# Alias for compatibility with orchestration logic\n")
            f.write("RECIPES = COLLECTION_RECIPES\n")
        
        logger.info(f"Successfully wrote {len(recipes)} recipes to {file_path}")
    except Exception as e:
        logger.error(f"Failed to write recipes to file: {str(e)}")
        sys.exit(1)

def main():
    """Main function to update collection recipes."""
    parser = argparse.ArgumentParser(description="Update collection recipes with enhanced recipes")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing recipes instead of merging")
    args = parser.parse_args()
    
    # Import modules here to avoid circular imports
    from src.collection_recipes import COLLECTION_RECIPES
    from src.enhanced_recipe_generator import generate_all_recipes
    
    # File paths
    recipes_file = os.path.join(os.path.dirname(__file__), "collection_recipes.py")
    
    # Backup existing recipes
    backup_existing_recipes(recipes_file)
    
    # Generate new recipes
    logger.info("Generating new recipes...")
    new_recipes = generate_all_recipes()
    
    if not new_recipes:
        logger.error("Failed to generate new recipes")
        sys.exit(1)
    
    # Merge recipes
    merged_recipes = merge_recipes(COLLECTION_RECIPES, new_recipes, args.overwrite)
    
    # Write merged recipes back to file
    write_recipes_to_file(merged_recipes, recipes_file)
    
    logger.info(f"Collection recipes updated successfully! Total recipes: {len(merged_recipes)}")

if __name__ == "__main__":
    main()
