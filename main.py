# Entry point for TMDbCollector

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
    logger = logging.getLogger("TMDbCollector")
    
    # Get the RUN_ONCE flag from environment
    run_once = os.getenv('RUN_ONCE', 'false').lower() == 'true'
    
    # Define the interval (24 hours in seconds)
    interval_seconds = 24 * 60 * 60  # 24 hours
    
    logger.info(f"Starting TMDbCollector {'in one-time mode' if run_once else 'in continuous mode with 24-hour interval'}")
    
    while True:
        try:
            # Load configuration each run to pick up any changes
            config = ConfigLoader(yaml_path="config/config.yaml")
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
            import sys
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
                
            # Calculate next run time
            next_run = start_time + timedelta(seconds=interval_seconds)
            logger.info(f"Next sync scheduled for {next_run.strftime('%Y-%m-%d %H:%M:%S')} (in 24 hours)")
            
            # Sleep until next run time
            time.sleep(interval_seconds)
            
        except KeyboardInterrupt:
            logger.info("TMDbCollector stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            # Still wait before trying again
            logger.info(f"Waiting {interval_seconds} seconds before next attempt...")
            time.sleep(interval_seconds)

if __name__ == "__main__":
    main()
