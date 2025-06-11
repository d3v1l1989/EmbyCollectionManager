# 🎬 TMDbCollector

TMDbCollector is a Python application that automatically generates and syncs movie collections in your Emby server, using dynamic lists and franchise data fetched from The Movie Database (TMDb). Inspired by the Stremio TMDb collections addon, it keeps your media server collections fresh and relevant—no manual curation required.

## ✨ Features
- **🎭 Auto-generate collections**: Popular, Top Rated, New Releases, Genres, and major Franchises (e.g., Star Wars, James Bond, Harry Potter)
- **📋 User-defined Trakt lists**: Create collections by pasting movie lists in the `traktlists/` directory
- **🖼️ Beautiful collection artwork**: Automatically fetches and applies posters and backdrops from TMDb
- **🎲 Random movie posters**: Trakt list collections get posters from random movies in the collection
- **🔍 Smart server detection**: Auto-detects if Emby is configured
- **📝 Customizable recipes**: Easily edit or extend collection logic in `src/collection_recipes.py`
- **🛡️ Robust error handling & logging**
- **⚙️ Configurable via YAML config file**

## 📋 Requirements
- 🐍 Python 3.8+ (for direct installation)
- 🐳 Docker (for containerized installation - recommended)
- 🎬 Emby server (with API key and user ID)
- 🔑 TMDb API key (free from [themoviedb.org](https://www.themoviedb.org/settings/api))

## 🚀 Quick Start (Docker)

1. Create a directory for the project and navigate into it
2. Create a `config` subdirectory and add your `config/config.yaml` file (see example below)
3. Create a `traktlists` subdirectory for your custom movie lists (optional)
4. Run with Docker Compose:
   ```sh
   docker compose up -d
   ```

## ⚙️ Configuration

Configure TMDbCollector using a **config.yaml** file in the config directory (example below):

### Example config.yaml

```yaml
# Config file for TMDbCollector
# API keys and server details organized by service

# TMDb configuration
tmdb:
  api_key: "YOUR_TMDB_API_KEY"

# Emby configuration
emby:
  api_key: "YOUR_EMBY_API_KEY"
  server_url: "http://emby:8096"  # Use your actual server address
  user_id: "YOUR_EMBY_USER_ID"

# Trakt configuration (optional)
trakt:
  client_id: "YOUR_TRAKT_CLIENT_ID"
  client_secret: "YOUR_TRAKT_CLIENT_SECRET"
  access_token: "YOUR_TRAKT_ACCESS_TOKEN"  # Optional

# Trakt lists configuration
traktlists:
  enabled: true                          # Enable/disable Trakt list processing
  directory: "traktlists"                # Directory to scan for Trakt list files
  random_poster: true                    # Use random movie poster from collection
  max_items_per_collection: 100          # Maximum items per collection

# Custom poster generation settings
poster_settings:
  # Enable/disable custom poster generation when TMDb doesn't provide one
  enable_custom_posters: true
  
  # Template settings
  template_name: "default.png"  # Template file in resources/templates/
  
  # Text settings
  text_color: [255, 255, 255]  # RGB values for text color (white)
  bg_color: [0, 0, 0, 128]     # RGBA values for text background (semi-transparent black)
  text_position: 0.5           # Vertical position of text (0-1), 0.8 = 80% from top
```



## 🔧 Installation & Usage

### 🐳 Option 1: Docker Compose (Recommended)

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
      - ./traktlists:/app/traktlists:ro
    environment:
      - SYNC_TARGET=auto  # Options: auto, emby
    restart: unless-stopped
```

2. Create a `config` directory and add your `config.yaml` file
3. Optionally create a `traktlists` directory for your custom movie lists
4. Start the service:

```sh
docker compose up -d
```

4. View logs:

```sh
docker compose logs -f tmdbcollector
```

### 🐳 Option 2: Standalone Docker

You can also run TMDbCollector directly with Docker:

```sh
docker run -d \
  --name tmdbcollector \
  -e SYNC_TARGET=auto \
  -v $(pwd)/config:/app/config:ro \
  -v $(pwd)/traktlists:/app/traktlists:ro \
  ghcr.io/d3v1l1989/tmdbcollector:latest
```

On Windows PowerShell, use:

```powershell
docker run -d `
  --name tmdbcollector `
  -e SYNC_TARGET=auto `
  -v ${PWD}/config:/app/config:ro `
  -v ${PWD}/traktlists:/app/traktlists:ro `
  ghcr.io/d3v1l1989/tmdbcollector:latest
```

### 🐍 Option 3: Direct Python Installation

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

## 🎯 Controlling Sync Target

Use the `SYNC_TARGET` environment variable (for Docker) or the `--targets` command-line flag (for direct Python usage):

- **`auto`**: Auto-detect and use Emby if configured (default)
- **`emby`**: Sync to Emby

Legacy approach (still supported): You can also use `SYNC_EMBY=1` environment variable.

## 🔄 Advanced Usage

### 💻 Command-Line Options

When running directly with Python, you have these options:

```sh
python -m src.app_logic --targets auto --config /path/to/config.yaml
```

Arguments:
- `--targets [auto|emby]`: Which server to sync with
- `--config PATH`: Path to config YAML file (default: config/config.yaml)

### 🛠️ Building from Source

To build the Docker image locally:

```sh
git clone https://github.com/d3v1l1989/TMDbCollector.git
cd TMDbCollector
docker build -t tmdbcollector .
```

### 📚 Collection Recipes

TMDbCollector comes with pre-configured collections like:

- 🌟 Popular Movies on TMDb
- 🏆 Top Rated Movies on TMDb
- 🆕 New Releases (Last Year)
- 🎭 Franchise Collections (Star Wars, James Bond, Harry Potter)
- 📚 Genre Collections (Action, Drama, Comedy, etc.)

You can customize these in `src/collection_recipes.py`.

### 📋 User-Defined Trakt Lists

Create your own movie collections by simply placing text files in the `traktlists/` directory!

#### How to Use

1. **Create a text file** in the `traktlists/` directory
   - Example: `My Favorite Movies.txt` becomes a collection called "My Favorite Movies"

2. **Add your movies** using any of these formats:

```
# My Favorite Movies.txt

# Movies by TMDb ID
550        # Fight Club
13         # Forrest Gump
155        # The Dark Knight

# Movies by title (searched automatically)
The Matrix
Inception
Pulp Fiction

# Trakt list URLs
https://trakt.tv/users/username/lists/my-list
```

#### Supported Formats

- **TMDb IDs**: `550` (Fight Club)
- **Movie Titles**: `The Matrix` (automatically searched on TMDb)
- **Trakt List URLs**: `https://trakt.tv/users/username/lists/list-name`
- **Comments**: Lines starting with `#` for organization

#### Features

- **🎲 Random Posters**: Each collection gets a poster from a randomly selected movie
- **📁 Simple Organization**: One file = one collection (filename becomes collection name)
- **🔄 Automatic Processing**: Collections are created/updated every time the app runs
- **⚙️ Configurable**: Control via `traktlists` section in config.yaml

### 🖼️ Automatic Artwork

TMDbCollector automatically adds artwork to your collections:

- 🖼️ For franchise collections: Uses official TMDb collection artwork
- 🎨 For dynamic collections (Popular, Genres): Uses artwork from the first movie
- 🎲 For Trakt list collections: Uses artwork from a randomly selected movie in the collection

## 🔍 Troubleshooting

### ❓ Common Issues

1. **🛑 The container exits immediately**
   - Check that your TMDb API key is valid
   - Check that your config file or environment variables are correctly set
   - Look at the logs: `docker logs tmdbcollector`

2. **❓ Collections don't appear in server**
   - Ensure your Emby API key and user ID are correct
   - Check server URL (make sure it's reachable from the container)
   - Verify your media server has movies that match the TMDb IDs

3. **⚠️ No collections are synced**
   - Set `SYNC_TARGET=auto` to let the app auto-detect available servers
   - Check the `/config` volume mapping in your Docker setup

## Getting API Keys

- **TMDb**: Register at [themoviedb.org](https://www.themoviedb.org/settings/api) to get a free API key
- **Emby**: Get your API key from Emby Dashboard → Advanced → Security

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

MIT License

