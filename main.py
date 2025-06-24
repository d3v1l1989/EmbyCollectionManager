# Entry point for Emby Collection Manager

from src.config_loader import ConfigLoader
from src.logging_setup import setup_logging
import logging
import sys
import os
import time
from datetime import datetime, timedelta
from src.app_logic import main as app_main

def main():
    # Setup logging and verify config
    setup_logging()
    logger = logging.getLogger("EmbyCollectionManager")
    
    # Get the RUN_ONCE flag from environment
    run_once = os.getenv('RUN_ONCE', 'false').lower() == 'true'
    
    # Define the interval (24 hours in seconds)
    interval_seconds = 24 * 60 * 60  # 24 hours
    
    logger.info(f"Starting Emby Collection Manager {'in one-time mode' if run_once else 'in continuous mode with 24-hour interval'}")
    
    while True:
        try:
            # Load configuration each run to pick up any changes
            config = ConfigLoader(yaml_path="config/config.yaml")
            config_dict = config.as_dict()
            
            # Check for API key in both new nested format and legacy flat format for backward compatibility
            tmdb_api_key = None
            if 'tmdb' in config_dict and isinstance(config_dict['tmdb'], dict) and 'api_key' in config_dict['tmdb']:
                tmdb_api_key = config_dict['tmdb']['api_key']
            else:
                # Fallback to legacy format
                tmdb_api_key = config.get("TMDB_API_KEY")
            
            if tmdb_api_key and tmdb_api_key != "YOUR_TMDB_API_KEY":
                logger.info(f"TMDb API key loaded: {tmdb_api_key[:4]}... (hidden)")
            else:
                logger.error("TMDb API key not set. Please update config/config.yaml.")
                sys.exit(1)
                
            # Get the SYNC_TARGET from config or environment
            sync_target = config.get('SYNC_TARGET', 'auto')
            logger.info(f"Using sync target: {sync_target}")
            
            # Run the main application logic with the sync target
            # Modify sys.argv to include the targets parameter
            # Clear any previous args to avoid duplication in subsequent runs
            if len(sys.argv) > 1:
                sys.argv = sys.argv[:1]
            sys.argv.extend(['--targets', sync_target])
            
            # Run the application logic
            start_time = datetime.now()
            logger.info(f"Starting collection sync at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            app_main()
            logger.info(f"Collection sync completed successfully")
            
            # If run_once is True, exit after the first run
            if run_once:
                logger.info("Exiting after one-time execution as requested")
                break
                
            # Calculate next run time and sleep duration
            next_run = start_time + timedelta(seconds=interval_seconds)
            current_time = datetime.now()
            sleep_duration = (next_run - current_time).total_seconds()
            
            # Ensure we don't have negative sleep duration
            if sleep_duration < 0:
                logger.warning(f"Sync took longer than expected. Next run will start immediately.")
                sleep_duration = 0
            
            logger.info(f"Next sync scheduled for {next_run.strftime('%Y-%m-%d %H:%M:%S')} (in {sleep_duration/3600:.1f} hours)")
            
            # Sleep until next run time
            time.sleep(sleep_duration)
            
        except KeyboardInterrupt:
            logger.info("Emby Collection Manager stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            # Still wait before trying again
            logger.info(f"Waiting {interval_seconds} seconds before next attempt...")
            time.sleep(interval_seconds)

if __name__ == "__main__":
    main()
