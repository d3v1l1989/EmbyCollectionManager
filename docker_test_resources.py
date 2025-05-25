"""
Docker-specific resource testing script.

This script helps diagnose resource access issues in a Docker environment.
It checks if template files are accessible and logs detailed information
about resource paths and file existence.
"""

import os
import sys
import logging
import json
from typing import Dict, List, Any

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("docker_test_resources")

def scan_directory(path: str, max_depth: int = 3, current_depth: int = 0) -> Dict:
    """
    Recursively scan a directory and return its structure as a dictionary.
    
    Args:
        path: Directory path to scan
        max_depth: Maximum recursion depth
        current_depth: Current recursion depth
        
    Returns:
        Dictionary representing the directory structure
    """
    if current_depth > max_depth:
        return {"name": os.path.basename(path), "type": "dir", "note": "max depth reached"}
    
    result = {"name": os.path.basename(path), "path": path, "type": "dir", "children": []}
    
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            
            if os.path.isdir(item_path):
                result["children"].append(scan_directory(item_path, max_depth, current_depth + 1))
            else:
                # Get file details
                try:
                    size = os.path.getsize(item_path)
                    readable = os.access(item_path, os.R_OK)
                    result["children"].append({
                        "name": item,
                        "path": item_path,
                        "type": "file",
                        "size": size,
                        "readable": readable
                    })
                except Exception as e:
                    result["children"].append({
                        "name": item,
                        "path": item_path,
                        "type": "file",
                        "error": str(e)
                    })
    except Exception as e:
        result["error"] = str(e)
    
    return result

def check_resources():
    """
    Check if resource files are accessible in the current environment.
    """
    logger.info("Starting Docker environment resource check")
    
    # Log system information
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Current user: {os.environ.get('USER', 'unknown')}")
    
    # Check possible resource locations
    possible_locations = [
        # Standard location relative to script
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources"),
        # Docker container standard location
        "/app/resources",
        # Additional fallback locations
        os.path.join(os.path.dirname(__file__), "resources"),
        "/opt/tmdbcollector/resources"
    ]
    
    for location in possible_locations:
        logger.info(f"Checking resource location: {location}")
        
        if os.path.exists(location):
            logger.info(f"✅ Location exists: {location}")
            
            # Check if templates directory exists
            templates_dir = os.path.join(location, "templates")
            if os.path.exists(templates_dir):
                logger.info(f"✅ Templates directory exists: {templates_dir}")
                
                # List template files
                try:
                    template_files = os.listdir(templates_dir)
                    logger.info(f"Found {len(template_files)} template files:")
                    for file in template_files:
                        file_path = os.path.join(templates_dir, file)
                        size = os.path.getsize(file_path)
                        readable = os.access(file_path, os.R_OK)
                        logger.info(f"  - {file} (Size: {size} bytes, Readable: {readable})")
                except Exception as e:
                    logger.error(f"❌ Error listing template files: {e}")
            else:
                logger.error(f"❌ Templates directory does not exist: {templates_dir}")
            
            # Check if fonts directory exists
            fonts_dir = os.path.join(location, "fonts")
            if os.path.exists(fonts_dir):
                logger.info(f"✅ Fonts directory exists: {fonts_dir}")
                
                # List font files
                try:
                    font_files = os.listdir(fonts_dir)
                    logger.info(f"Found {len(font_files)} font files:")
                    for file in font_files:
                        file_path = os.path.join(fonts_dir, file)
                        size = os.path.getsize(file_path)
                        readable = os.access(file_path, os.R_OK)
                        logger.info(f"  - {file} (Size: {size} bytes, Readable: {readable})")
                except Exception as e:
                    logger.error(f"❌ Error listing font files: {e}")
            else:
                logger.error(f"❌ Fonts directory does not exist: {fonts_dir}")
            
            # Scan the resource directory structure
            logger.info(f"Scanning directory structure for: {location}")
            structure = scan_directory(location)
            
            # Save the structure to a file for reference
            try:
                output_path = os.path.join(os.path.dirname(__file__), "docker_resources_scan.json")
                with open(output_path, 'w') as f:
                    json.dump(structure, f, indent=2)
                logger.info(f"Saved directory structure to: {output_path}")
            except Exception as e:
                logger.error(f"Error saving directory structure: {e}")
                
        else:
            logger.warning(f"❌ Location does not exist: {location}")
    
    # Test creating a temporary file
    import tempfile
    import uuid
    
    try:
        temp_dir = tempfile.gettempdir()
        logger.info(f"Temporary directory: {temp_dir}")
        
        # Check if temp directory exists and is writable
        if os.path.exists(temp_dir):
            logger.info(f"✅ Temporary directory exists: {temp_dir}")
            if os.access(temp_dir, os.W_OK):
                logger.info(f"✅ Temporary directory is writable: {temp_dir}")
                
                # Try to create a test file
                test_filename = f"docker_test_{uuid.uuid4().hex}.txt"
                test_path = os.path.join(temp_dir, test_filename)
                
                with open(test_path, 'w') as f:
                    f.write("Docker resource test file")
                
                logger.info(f"✅ Successfully created test file: {test_path}")
                
                # Clean up
                try:
                    os.remove(test_path)
                    logger.info(f"✅ Successfully removed test file: {test_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not remove test file: {e}")
            else:
                logger.error(f"❌ Temporary directory is not writable: {temp_dir}")
        else:
            logger.error(f"❌ Temporary directory does not exist: {temp_dir}")
            
    except Exception as e:
        logger.error(f"❌ Error testing temporary file creation: {e}")
    
    # Log any environment variables that might be relevant
    try:
        env_vars = {
            'PYTHONPATH': os.environ.get('PYTHONPATH', 'Not set'),
            'PATH': os.environ.get('PATH', 'Not set'),
            'HOME': os.environ.get('HOME', 'Not set'),
            'USER': os.environ.get('USER', 'Not set'),
            'TEMP': os.environ.get('TEMP', 'Not set'),
            'TMP': os.environ.get('TMP', 'Not set')
        }
        
        logger.info("Environment variables:")
        for var, value in env_vars.items():
            logger.info(f"  {var}: {value}")
    except Exception as e:
        logger.error(f"Error getting environment variables: {e}")

if __name__ == "__main__":
    check_resources()
