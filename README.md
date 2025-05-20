# TMDbCollector

TMDbCollector is a Python application that automatically generates and syncs movie collections in Emby and/or Jellyfin servers, using dynamic lists and franchise data fetched from The Movie Database (TMDb). Inspired by the Stremio TMDb collections addon, it keeps your media server collections fresh and relevant—no manual curation required.

## Features
- **Auto-generate collections**: Popular, Top Rated, New Releases, Genres, and major Franchises (e.g., Star Wars, James Bond, Harry Potter)
- **Beautiful collection artwork**: Automatically fetches and applies posters and backdrops from TMDb
- **Sync to Emby and/or Jellyfin**: Works with both servers, or just one
- **Smart server detection**: Auto-detects configured servers by default
- **Customizable recipes**: Easily edit or extend collection logic in `src/collection_recipes.py`
- **Robust error handling & logging**
- **Configurable via YAML and/or .env files**

## Requirements
- Python 3.8+ (for direct installation)
- Docker (for containerized installation - recommended)
- Emby or Jellyfin server (with API key and user ID)
- TMDb API key (free from [themoviedb.org](https://www.themoviedb.org/settings/api))

## Quick Start (Docker)

1. Create a directory for the project and navigate into it
2. Create a `config` subdirectory
3. Create a `config/config.yaml` file with your API keys (see example below)
4. Create a `.env` file (optional, can be used instead of config.yaml)
5. Run with Docker Compose:
   ```sh
   docker compose up -d
   ```

## Configuration

You can configure TMDbCollector using either:

1. A **config.yaml** file in the config directory (example below)
2. Environment variables or a **.env** file

### Example config.yaml

```yaml
tmdb:
  api_key: your_tmdb_api_key

emby:
  server_url: http://emby:8096
  api_key: your_emby_api_key
  user_id: your_emby_user_id

jellyfin:
  server_url: http://jellyfin:8096
  api_key: your_jellyfin_api_key
  user_id: your_jellyfin_user_id
```

### Example .env file

```env
TMDB_API_KEY=your_tmdb_api_key
EMBY_API_KEY=your_emby_api_key
EMBY_URL=http://localhost:8096  # Use your actual server address
EMBY_USER_ID=your_emby_user_id
JELLYFIN_API_KEY=your_jellyfin_api_key
JELLYFIN_URL=http://localhost:8096  # Use your actual server address
JELLYFIN_USER_ID=your_jellyfin_user_id

# Choose which server(s) to sync
SYNC_TARGET=auto  # Options: auto, emby, jellyfin, all
```

## Installation & Usage

### Option 1: Docker Compose (Recommended)

The easiest way to run TMDbCollector is with Docker Compose:

1. Create a `docker-compose.yml` file with the following content:

```yaml
version: '3.8'

services:
  tmdbcollector:
    image: ghcr.io/d3v1l1989/tmdbcollector:latest
    container_name: tmdbcollector
    volumes:
      - ./config:/app/config:ro
    environment:
      - SYNC_TARGET=auto  # Options: auto, emby, jellyfin, all
      # Uncomment and fill in if not using config.yaml:
      # - TMDB_API_KEY=your_tmdb_api_key
      # - EMBY_API_KEY=your_emby_api_key
      # - EMBY_URL=http://emby:8096
      # - EMBY_USER_ID=your_emby_user_id
      # - JELLYFIN_API_KEY=your_jellyfin_api_key
      # - JELLYFIN_URL=http://jellyfin:8096
      # - JELLYFIN_USER_ID=your_jellyfin_user_id
    # Alternative: use .env file instead of environment section above
    # env_file:
    #   - .env
    restart: unless-stopped
```

2. Create a `config` directory and add your `config.yaml` file
3. Start the service:

```sh
docker compose up -d
```

4. View logs:

```sh
docker compose logs -f tmdbcollector
```

### Option 2: Standalone Docker

You can also run TMDbCollector directly with Docker:

```sh
docker run -d \
  --name tmdbcollector \
  -e SYNC_TARGET=auto \
  -v $(pwd)/config:/app/config:ro \
  ghcr.io/d3v1l1989/tmdbcollector:latest
```

On Windows PowerShell, use:

```powershell
docker run -d `
  --name tmdbcollector `
  -e SYNC_TARGET=auto `
  -v ${PWD}/config:/app/config:ro `
  ghcr.io/d3v1l1989/tmdbcollector:latest
```

### Option 3: Direct Python Installation

If you prefer to run without Docker:

1. Clone the repository:
   ```sh
   git clone https://github.com/d3v1l1989/TMDbCollector.git
   cd TMDbCollector
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Run the application:
   ```sh
   python -m src.app_logic --targets auto
   ```

## Controlling Which Servers to Sync

Use the `SYNC_TARGET` environment variable (for Docker) or the `--targets` command-line flag (for direct Python usage):

- **`auto`**: Auto-detect and use all configured servers (default)
- **`emby`**: Sync only to Emby
- **`jellyfin`**: Sync only to Jellyfin
- **`all`**: Sync to both servers (both must be configured)

Legacy approach (still supported): You can also use `SYNC_EMBY=1` and/or `SYNC_JELLYFIN=1` environment variables.

## Advanced Usage

### Command-Line Options

When running directly with Python, you have these options:

```sh
python -m src.app_logic --targets auto --config /path/to/config.yaml
```

Arguments:
- `--targets [auto|emby|jellyfin|all]`: Which server(s) to sync with
- `--config PATH`: Path to config YAML file (default: config/config.yaml)

### Building from Source

To build the Docker image locally:

```sh
git clone https://github.com/d3v1l1989/TMDbCollector.git
cd TMDbCollector
docker build -t tmdbcollector .
```

### Collection Recipes

TMDbCollector comes with pre-configured collections like:

- Popular Movies on TMDb
- Top Rated Movies on TMDb
- New Releases (Last Year)
- Franchise Collections (Star Wars, James Bond, Harry Potter)
- Genre Collections (Action, Drama, Comedy, etc.)

You can customize these in `src/collection_recipes.py`.

### Automatic Artwork

TMDbCollector automatically adds artwork to your collections:

- For franchise collections: Uses official TMDb collection artwork
- For dynamic collections (Popular, Genres): Uses artwork from the first movie

## Troubleshooting

### Common Issues

1. **The container exits immediately**
   - Check that your TMDb API key is valid
   - Check that your config file or environment variables are correctly set
   - Look at the logs: `docker logs tmdbcollector`

2. **Collections don't appear in server**
   - Ensure your Emby/Jellyfin API keys and user IDs are correct
   - Check server URLs (make sure they're reachable from the container)
   - Verify your media server has movies that match the TMDb IDs

3. **No collections are synced**
   - Set `SYNC_TARGET=auto` to let the app auto-detect available servers
   - Check the `/config` volume mapping in your Docker setup

## Getting API Keys

- **TMDb**: Register at [themoviedb.org](https://www.themoviedb.org/settings/api) to get a free API key
- **Emby**: Get your API key from Emby Dashboard → Advanced → Security
- **Jellyfin**: Get your API key from Jellyfin Dashboard → Administration → API Keys

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

MIT License

