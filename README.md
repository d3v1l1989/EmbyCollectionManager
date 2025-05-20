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

## Usage
Run the orchestration CLI from the project root:

```sh
python -m src.app_logic --sync_emby --sync_jellyfin
```
- Use `--sync_emby` and/or `--sync_jellyfin` to target one or both servers.
- Use `--config` to specify a custom config file path.


---

**Contributions welcome!**
