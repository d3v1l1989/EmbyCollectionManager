"""
Trakt List Processor for TMDbCollector

This module processes user-created text files in the traktlists directory
and converts them into collections with TMDb movie IDs.
"""

import os
import re
import logging
from typing import List, Dict, Any, Set
from pathlib import Path

logger = logging.getLogger(__name__)

class TraktListProcessor:
    """
    Processes text files containing Trakt lists, TMDb IDs, and movie titles
    to create collections for media servers.
    """
    
    def __init__(self, tmdb_client, trakt_client=None, config=None):
        """
        Initialize the processor with required clients.
        
        Args:
            tmdb_client: TMDb client for movie lookups
            trakt_client: Optional Trakt client for list processing
            config: Configuration dictionary
        """
        self.tmdb_client = tmdb_client
        self.trakt_client = trakt_client
        self.config = config or {}
        
        # Configuration options
        traktlists_config = self.config.get('traktlists', {})
        self.enabled = traktlists_config.get('enabled', True)
        self.directory = traktlists_config.get('directory', 'traktlists')
        self.max_items = traktlists_config.get('max_items_per_collection', 100)
        
    def is_enabled(self) -> bool:
        """Check if Trakt list processing is enabled."""
        return self.enabled
    
    def get_traktlists_directory(self) -> Path:
        """Get the path to the traktlists directory."""
        return Path(self.directory)
    
    def scan_traktlists_directory(self) -> List[Dict[str, Any]]:
        """
        Scan the traktlists directory for .txt files and process them.
        
        Returns:
            List of collection dictionaries ready for processing
        """
        if not self.is_enabled():
            logger.info("Trakt lists processing is disabled")
            return []
            
        traktlists_dir = self.get_traktlists_directory()
        
        if not traktlists_dir.exists():
            logger.info(f"Trakt lists directory '{traktlists_dir}' does not exist")
            return []
            
        logger.info(f"Scanning Trakt lists directory: {traktlists_dir}")
        collections = []
        
        # Find all .txt files in the directory
        txt_files = list(traktlists_dir.glob("*.txt"))
        
        if not txt_files:
            logger.info("No .txt files found in traktlists directory")
            return []
            
        logger.info(f"Found {len(txt_files)} Trakt list files to process")
        
        for txt_file in txt_files:
            try:
                collection = self.process_traktlist_file(txt_file)
                if collection:
                    collections.append(collection)
            except Exception as e:
                logger.error(f"Error processing file '{txt_file.name}': {e}")
                
        return collections
    
    def process_traktlist_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single traktlist file and extract movie IDs.
        
        Args:
            file_path: Path to the .txt file
            
        Returns:
            Dictionary containing collection info and TMDb IDs
        """
        collection_name = file_path.stem  # Filename without extension
        logger.info(f"Processing Trakt list file: {file_path.name} -> Collection: '{collection_name}'")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read file '{file_path}': {e}")
            return None
            
        tmdb_ids = self.extract_tmdb_ids_from_content(content, collection_name)
        
        if not tmdb_ids:
            logger.warning(f"No valid movies found in '{file_path.name}'")
            return None
            
        # Apply max items limit
        if self.max_items and len(tmdb_ids) > self.max_items:
            logger.info(f"Limiting collection '{collection_name}' to {self.max_items} items (was {len(tmdb_ids)})")
            tmdb_ids = tmdb_ids[:self.max_items]
            
        logger.info(f"Found {len(tmdb_ids)} movies for collection '{collection_name}'")
        
        return {
            'name': collection_name,
            'source_type': 'traktlist_file',
            'tmdb_ids': tmdb_ids,
            'target_servers': ['emby'],
            'category_id': 12,  # Trakt category
            'file_path': str(file_path)
        }
    
    def extract_tmdb_ids_from_content(self, content: str, collection_name: str) -> List[int]:
        """
        Extract TMDb IDs from file content supporting multiple formats.
        
        Args:
            content: File content as string
            collection_name: Name for logging purposes
            
        Returns:
            List of TMDb movie IDs
        """
        lines = content.strip().split('\n')
        tmdb_ids = []
        seen_ids = set()  # Prevent duplicates
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
                
            try:
                # Try to extract TMDb IDs from this line
                extracted_ids = self.parse_line(line, collection_name, line_num)
                
                # Add unique IDs only
                for tmdb_id in extracted_ids:
                    if tmdb_id not in seen_ids:
                        tmdb_ids.append(tmdb_id)
                        seen_ids.add(tmdb_id)
                        
            except Exception as e:
                logger.warning(f"Error processing line {line_num} in '{collection_name}': {line[:50]}... - {e}")
                
        return tmdb_ids
    
    def parse_line(self, line: str, collection_name: str, line_num: int) -> List[int]:
        """
        Parse a single line and extract TMDb IDs.
        
        Args:
            line: Line content
            collection_name: Collection name for logging
            line_num: Line number for logging
            
        Returns:
            List of TMDb IDs found on this line
        """
        # Remove inline comments
        if '#' in line:
            line = line.split('#')[0].strip()
            
        if not line:
            return []
            
        # 1. Check for Trakt list URL
        trakt_url_match = re.match(r'https://trakt\.tv/users/([^/]+)/lists/([^/?]+)', line)
        if trakt_url_match:
            return self.process_trakt_list_url(trakt_url_match.group(1), trakt_url_match.group(2), collection_name)
            
        # 2. Check for direct TMDb ID (just a number)
        if line.isdigit():
            tmdb_id = int(line)
            if self.validate_tmdb_id(tmdb_id):
                return [tmdb_id]
            else:
                logger.warning(f"Invalid TMDb ID {tmdb_id} in '{collection_name}' line {line_num}")
                return []
                
        # 3. Treat as movie title - search TMDb
        return self.search_movie_by_title(line, collection_name, line_num)
    
    def process_trakt_list_url(self, username: str, list_slug: str, collection_name: str) -> List[int]:
        """
        Process a Trakt list URL and extract TMDb IDs.
        
        Args:
            username: Trakt username
            list_slug: Trakt list slug
            collection_name: Collection name for logging
            
        Returns:
            List of TMDb IDs from the Trakt list
        """
        if not self.trakt_client:
            logger.error(f"Trakt client not available for processing URL in '{collection_name}'")
            return []
            
        try:
            logger.info(f"Fetching Trakt list: {username}/{list_slug}")
            trakt_items = self.trakt_client.get_list_items(username, list_slug, 'movies')
            tmdb_ids = self.trakt_client.extract_tmdb_ids(trakt_items, 'movie')
            logger.info(f"Found {len(tmdb_ids)} movies from Trakt list {username}/{list_slug}")
            return tmdb_ids
        except Exception as e:
            logger.error(f"Failed to process Trakt list {username}/{list_slug}: {e}")
            return []
    
    def search_movie_by_title(self, title: str, collection_name: str, line_num: int) -> List[int]:
        """
        Search for a movie by title using TMDb.
        
        Args:
            title: Movie title to search
            collection_name: Collection name for logging
            line_num: Line number for logging
            
        Returns:
            List containing the TMDb ID if found, empty list otherwise
        """
        try:
            logger.debug(f"Searching TMDb for movie title: '{title}'")
            search_results = self.tmdb_client.search_movies(title)
            
            if search_results and len(search_results) > 0:
                # Take the first (most relevant) result
                movie = search_results[0]
                tmdb_id = movie['id']
                movie_title = movie.get('title', 'Unknown')
                year = movie.get('release_date', '')[:4] if movie.get('release_date') else ''
                logger.info(f"Found movie: '{title}' -> '{movie_title}' ({year}) [TMDb ID: {tmdb_id}]")
                return [tmdb_id]
            else:
                logger.warning(f"No TMDb results found for title: '{title}' in '{collection_name}' line {line_num}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching for movie '{title}': {e}")
            return []
    
    def validate_tmdb_id(self, tmdb_id: int) -> bool:
        """
        Validate that a TMDb ID exists by checking the movie details.
        
        Args:
            tmdb_id: TMDb movie ID
            
        Returns:
            True if the ID is valid, False otherwise
        """
        try:
            movie_details = self.tmdb_client.get_movie_details(tmdb_id)
            return movie_details is not None
        except Exception:
            return False