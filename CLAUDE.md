# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
- **Install dependencies**: `pip install -r requirements.txt`
- **Run directly**: `python main.py` or `python -m src.app_logic --targets auto`
- **Run with specific config**: `python -m src.app_logic --targets auto --config /path/to/config.yaml`
- **Test configuration**: `python docker_test_resources.py` (validates resource files)
- **Test Trakt lists**: `python test_traktlists.py` (validates Trakt list processing)

### Docker Development
- **Build image**: `docker build -t tmdbcollector .`
- **Run with Docker**: `docker run -d --name tmdbcollector -e SYNC_TARGET=auto -v $(pwd)/config:/app/config:ro ghcr.io/d3v1l1989/tmdbcollector:latest`
- **View logs**: `docker compose logs -f tmdbcollector`
- **Start with compose**: `docker compose up -d`

### Configuration Commands
- **Target auto-detection**: `--targets auto` (default, uses available configured servers)
- **Target Emby specifically**: `--targets emby`

## Architecture Overview

### Core Application Flow
1. **Entry Point**: `main.py` - Orchestrates the entire application with 24-hour scheduling loop
2. **App Logic**: `src/app_logic.py` - Main business logic, processes collection recipes and syncs to media servers
3. **Configuration**: Loaded via `src/config_loader.py` with YAML config precedence over environment variables

### Key Components

#### Media Server Integration
- **Base Client**: `src/base_media_server_client.py` - Abstract base class defining media server interface
- **Emby Client**: `src/emby_client.py` - Concrete implementation for Emby server API integration
- **Server Detection**: Automatic server detection based on configuration availability

#### TMDb Integration
- **TMDb Client**: `src/tmdb_fetcher.py` - Handles all TMDb API interactions including:
  - Movie discovery with pagination support
  - Collection details and artwork fetching
  - Search and filtering capabilities
  - Movie search by title for Trakt list processing

#### Trakt Integration
- **Trakt Client**: `src/trakt_client.py` - Handles Trakt.tv API interactions with OAuth2 support
- **Trakt List Processor**: `src/trakt_list_processor.py` - Processes user-created text files from `traktlists/` directory
- **Supported Formats**: TMDb IDs, movie titles, Trakt list URLs in simple text files
- **Random Artwork**: Automatically selects poster from random movie in each collection

#### Collection Management
- **Recipes**: `src/collection_recipes.py` - Contains 11 categories of pre-configured collections:
  1. TMDb General Collections (Popular, Top Rated, New Releases)
  2. Streaming Platform Collections (Netflix, Disney+, Amazon Prime, etc.)
  3. Franchise Collections (Star Wars, James Bond, Marvel, etc.)
  4. Genre Collections (Action, Drama, Comedy, etc.)
  5. Director Collections
  6. Actor Collections  
  7. Decade Collections
  8. Critically Acclaimed Collections
  9. Theme & Keyword Collections
  10. Studio Collections
  11. Language & Regional Cinema

#### Artwork System
- **Poster Generator**: `src/poster_generator.py` - Creates custom collection posters when TMDb artwork unavailable
- **Poster Mapper**: `src/collection_poster_mapper.py` - Maps collections to appropriate poster templates
- **Collection Poster Manager**: `src/collection_poster_manager.py` - Orchestrates poster generation and application
- **Templates**: Located in `resources/templates/` with category-specific poster designs

### Configuration System
- **Primary**: `config/config.yaml` - Nested YAML structure with service-specific sections
- **Fallback**: Environment variables for backward compatibility
- **Config Structure**:
  ```yaml
  tmdb:
    api_key: "..."
  emby:
    api_key: "..."
    server_url: "..."  
    user_id: "..."
  trakt:
    client_id: "..."
    client_secret: "..."
    access_token: "..."
  traktlists:
    enabled: true
    directory: "traktlists"
    random_poster: true
    max_items_per_collection: 100
  poster_settings:
    enable_custom_posters: true
    template_name: "default.png"
    text_color: [255, 255, 255]
    bg_color: [0, 0, 0, 128]
    text_position: 0.5
  ```

### Collection Processing Logic
1. **Recipe Processing**: Each recipe defines source type (TMDb collection, discover, etc.)
2. **TMDb Data Fetching**: Based on recipe parameters (discover params, collection IDs, limits)
3. **Trakt List Processing**: Scans `traktlists/` directory for user-created collections
4. **Server Sync**: Creates/updates collections and adds matching library items
5. **Artwork Application**: 
   - Recipe collections: TMDb collection poster → custom generated poster → movie artwork
   - Trakt collections: Random movie poster from collection → custom generated poster

### Docker Architecture
- **Multi-stage Build**: Python 3.11-slim base with optimized dependency installation
- **Volume Mounting**: Config directory mounted read-only for security
- **Environment Control**: `SYNC_TARGET` environment variable controls server selection
- **Entrypoint**: `entrypoint.sh` handles command-line argument construction and legacy compatibility

## Development Notes

### Extending Collections
- Modify `COLLECTION_RECIPES` list in `src/collection_recipes.py`
- Each recipe requires: `name`, `source_type`, `target_servers`, `category_id`
- Source types: `tmdb_collection`, `tmdb_series_collection`, `tmdb_discover`, `tmdb_discover_individual_movies`

### Adding Media Server Support
- Extend `MediaServerClient` base class in `src/base_media_server_client.py`
- Implement required methods: `get_or_create_collection`, `get_library_item_ids_by_tmdb_ids`, `update_collection_items`
- Update `app_logic.py` to handle new server type

### Custom Poster Generation
- Templates stored in `resources/templates/` 
- Font resources in `resources/fonts/`
- Poster generation controlled via `poster_settings` in config
- Category-specific poster templates mapped in `CATEGORY_CONFIG`

### Trakt Lists Feature
- **Directory**: `traktlists/` - Place `.txt` files here to create collections
- **File Format**: Each `.txt` file becomes a collection (filename = collection name)
- **Supported Content**:
  - TMDb IDs: `550` (Fight Club)
  - Movie titles: `The Matrix` (searched on TMDb)
  - Trakt URLs: `https://trakt.tv/users/username/lists/list-name`
  - Comments: Lines starting with `#`
- **Artwork**: Automatically uses poster from randomly selected movie in collection
- **Configuration**: Enable/disable via `traktlists.enabled` in config
- **Testing**: Use `python test_traktlists.py` to validate processing