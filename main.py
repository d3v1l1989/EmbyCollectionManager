# Entry point for TMDbCollector

from src.config_loader import ConfigLoader
from src.logging_setup import setup_logging
import logging

def main():
    setup_logging()
    logger = logging.getLogger("TMDbCollector")
    config = ConfigLoader(yaml_path="config/config.yaml", dotenv_path=".env")
    tmdb_api_key = config.get("TMDB_API_KEY")
    if tmdb_api_key and tmdb_api_key != "YOUR_TMDB_API_KEY":
        logger.info(f"TMDb API key loaded: {tmdb_api_key[:4]}... (hidden)")
    else:
        logger.warning("TMDb API key not set. Please update config/config.yaml or your .env file.")

if __name__ == "__main__":
    main()
