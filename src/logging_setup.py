import logging
import sys

def setup_logging(loglevel=logging.INFO, logfile=None):
    """Set up root logger for the application."""
    handlers = [logging.StreamHandler(sys.stdout)]
    if logfile:
        handlers.append(logging.FileHandler(logfile, encoding='utf-8'))
    logging.basicConfig(
        level=loglevel,
        format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
        handlers=handlers
    )

