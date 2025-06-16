"""
MDBList Processor for TMDbCollector

This module processes user-created text files in the mdblists directory
and converts them into collections with TMDb movie IDs.
"""

import os
import re
import logging
from typing import List, Dict, Any, Set
from pathlib import Path

logger = logging.getLogger(__name__)

class MDBListProcessor:
    """
    Processes text files containing MDBList URLs, TMDb IDs, and movie titles
    to create collections for media servers.
    """
    
    def __init__(self, tmdb_client, mdblist_client=None, config=None):
        """
        Initialize the processor with required clients.
        
        Args:
            tmdb_client: TMDb client for movie lookups
            mdblist_client: Optional MDBList client for list processing
            config: Configuration dictionary
        """
        self.tmdb_client = tmdb_client
        self.mdblist_client = mdblist_client
        self.config = config or {}
        
        # Configuration options
        mdblists_config = self.config.get('mdblists', {})
        self.enabled = mdblists_config.get('enabled', True)
        self.directory = mdblists_config.get('directory', 'mdblists')
        self.max_items = mdblists_config.get('max_items_per_collection', 0)
        
    def is_enabled(self) -> bool:
        """Check if MDBList processing is enabled."""
        return self.enabled
    
    def get_mdblists_directory(self) -> Path:
        """Get the path to the mdblists directory."""
        return Path(self.directory)
    
    def scan_mdblists_directory(self) -> List[Dict[str, Any]]:
        """
        Scan the mdblists directory for .txt files and process them.
        
        Returns:
            List of collection dictionaries ready for processing
        """
        if not self.is_enabled():
            logger.info("MDBList processing is disabled")
            return []
            
        mdblists_dir = self.get_mdblists_directory()
        
        if not mdblists_dir.exists():
            logger.info(f"MDBList directory '{mdblists_dir}' does not exist")
            return []
            
        logger.info(f"Scanning MDBList directory: {mdblists_dir}")
        collections = []
        
        # Find all .txt files in the directory
        txt_files = list(mdblists_dir.glob("*.txt"))
        
        if not txt_files:
            logger.info("No .txt files found in mdblists directory")
            return []
            
        logger.info(f"Found {len(txt_files)} MDBList files to process")
        
        for txt_file in txt_files:
            try:
                collection = self.process_mdblist_file(txt_file)
                if collection:
                    collections.append(collection)
            except Exception as e:
                logger.error(f"Error processing file '{txt_file.name}': {e}")
                
        return collections
    
    def process_mdblist_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single mdblist file and extract movie IDs.
        
        Args:
            file_path: Path to the .txt file
            
        Returns:
            Dictionary containing collection info and TMDb IDs
        """
        collection_name = file_path.stem  # Filename without extension
        logger.info(f"Processing MDBList file: {file_path.name} -> Collection: '{collection_name}'")
        
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
            'source_type': 'mdblist_file',
            'tmdb_ids': tmdb_ids,
            'target_servers': ['emby'],
            'category_id': 13,  # MDBList category
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
            
        # 1. Check for MDBList URL
        mdblist_url_match = re.match(r'https://mdblist\.com/lists/([^/?]+)(?:/([^/?]+))?', line)
        if mdblist_url_match:
            return self.process_mdblist_url(line, collection_name)
            
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
    
    def process_mdblist_url(self, url: str, collection_name: str) -> List[int]:
        """
        Process an MDBList URL and extract TMDb IDs.
        
        Args:
            url: MDBList URL
            collection_name: Collection name for logging
            
        Returns:
            List of TMDb IDs from the MDBList
        """
        if not self.mdblist_client:
            logger.error(f"MDBList client not available for processing URL in '{collection_name}'")
            return []
            
        try:
            logger.info(f"Fetching MDBList: {url}")
            mdblist_items = self.mdblist_client.get_list_items(url)
            tmdb_ids = self.mdblist_client.extract_tmdb_ids(mdblist_items, 'movie')
            logger.info(f"Found {len(tmdb_ids)} movies from MDBList: {url}")
            return tmdb_ids
        except Exception as e:
            logger.error(f"Failed to process MDBList URL {url}: {e}")
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