# TMDbCollector

TMDbCollector is a Python application that automatically generates and syncs movie collections in Emby and/or Jellyfin servers, using dynamic lists and franchise data fetched from The Movie Database (TMDb). Inspired by the Stremio TMDb collections addon, it keeps your media server collections fresh and relevant—no manual curation required.

## Features
- **Auto-generate collections**: Popular, Top Rated, New Releases, Genres, and major Franchises (e.g., Star Wars, James Bond, Harry Potter)
- **Sync to Emby and/or Jellyfin**: Works with both servers, or just one
- **Customizable recipes**: Easily edit or extend collection logic in `src/collection_recipes.py`
- **Robust error handling & logging**
- **Configurable via YAML and/or .env files**

## Requirements
- Python 3.8+
- Emby or Jellyfin server (with API key and user ID)
- TMDb API key

## Setup
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Copy `config/config.yaml` and fill in your TMDb, Emby, and/or Jellyfin details. See `.env.example` for environment variable options.

## Configuration
- **YAML**: Edit `config/config.yaml` with your API keys and server info.
- **.env**: Optionally use a `.env` file for secrets (see `.env.example`).

### Example .env file
Copy `.env.example` to `.env` and fill in your values:

```env
TMDB_API_KEY=your_tmdb_api_key
EMBY_API_KEY=your_emby_api_key
EMBY_URL=http://localhost:8096
EMBY_USER_ID=your_emby_user_id
JELLYFIN_API_KEY=your_jellyfin_api_key
JELLYFIN_URL=http://localhost:8096
JELLYFIN_USER_ID=your_jellyfin_user_id
```

## Docker Compose (Recommended)

The easiest way to run TMDbCollector is with Docker Compose. This will automatically pull the latest image from GitHub Container Registry and run it with your configuration.

1. Copy `docker-compose.yml` to your project directory (already included in this repo).
2. Edit `config/config.yaml` and `.env` with your API keys and server details.
3. Start the service:
   ```sh
   docker compose up -d
   ```

**Example `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  tmdbcollector:
    build: .
    environment:
      - SYNC_EMBY=1
      - SYNC_JELLYFIN=1
      # ...other env vars (TMDB_API_KEY, etc)
    volumes:
      - ./config:/app/config
    # No need to override command or entrypoint
```
  tmdbcollector:
    image: ghcr.io/d3v1l1989/tmdbcollector:latest
    container_name: tmdbcollector
    volumes:
      - ./config:/app/config:ro
    env_file:
      - .env
    # The sync targets are now configured via the SYNC_TARGETS variable in your .env file
    command: ["/bin/sh", "-c", "python main.py $SYNC_TARGETS"]
    restart: unless-stopped
```

Logs can be viewed with:
```sh
docker compose logs -f tmdbcollector
```

---

**Example `.env` file for Docker Compose:**
```env
TMDB_API_KEY=your_tmdb_api_key
EMBY_API_KEY=your_emby_api_key
EMBY_URL=http://localhost:8096
EMBY_USER_ID=your_emby_user_id
JELLYFIN_API_KEY=your_jellyfin_api_key
JELLYFIN_URL=http://localhost:8096
JELLYFIN_USER_ID=your_jellyfin_user_id
# Choose which server(s) to sync
SYNC_TARGET=auto  # Options: auto, emby, jellyfin, all
```

- Set the `SYNC_TARGET` environment variable to control which server(s) to sync to:
  - `SYNC_TARGET=auto` - Auto-detect and use all configured servers (default)
  - `SYNC_TARGET=emby` - Sync only to Emby 
  - `SYNC_TARGET=jellyfin` - Sync only to Jellyfin
  - `SYNC_TARGET=all` - Sync to both servers (both must be configured)

- Legacy approach (still supported): You can also use `SYNC_EMBY=1` and/or `SYNC_JELLYFIN=1`

## Docker (Standalone)

You can also run TMDbCollector directly with Docker (without Compose):

1. Make sure you have `config/config.yaml` and `.env` files in your project directory.
2. Pull/build the latest image:
   ```sh
   docker pull ghcr.io/d3v1l1989/tmdbcollector:latest
   # or build locally:
   docker build -t tmdbcollector .
   ```
3. Run the container (set env vars as needed):
   ```sh
   docker run -d \
     --name tmdbcollector \
     -e SYNC_TARGET=auto \
     -v $(pwd)/config:/app/config \
     tmdbcollector
   ```
   - Set SYNC_TARGET to: `auto`, `emby`, `jellyfin`, or `all` as needed
   - On Windows, replace `$(pwd)` with the full path to your project directory.
     -v $(pwd)/config:/app/config:ro \
     --env-file .env \
     ghcr.io/d3v1l1989/tmdbcollector:latest \
     --sync_emby --sync_jellyfin
   ```
   - Adjust the command-line arguments (`--sync_emby`, `--sync_jellyfin`) as needed.
   - On Windows, replace `$(pwd)` with the full path to your project directory.

Logs can be viewed with:
```sh
docker logs -f tmdbcollector
```

---

## Usage
Run the orchestration CLI from the project root (for manual/advanced use):

```sh
python -m src.app_logic --targets auto
```
- Use `--targets [auto|emby|jellyfin|all]` to control which servers to sync:
  - `auto`: Auto-detect and use all configured servers (default)
  - `emby`: Sync only to Emby
  - `jellyfin`: Sync only to Jellyfin
  - `all`: Sync to both Emby and Jellyfin (both must be configured)
- Legacy: You can still use `--sync_emby` and/or `--sync_jellyfin` flags for backward compatibility
- Use `--config` to specify a custom config file path.

---

**Contributions welcome!**
