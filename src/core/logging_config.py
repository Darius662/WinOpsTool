"""Logging configuration."""
import os
from pathlib import Path

# Logging configuration
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "system_management.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "DEBUG"

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

#The available log levels in Python's logging module, from most to least verbose, are:

#DEBUG: Detailed information, typically only valuable when diagnosing problems
#INFO: Confirmation that things are working as expected
#WARNING: Indication that something unexpected happened, but the application is still working
#ERROR: Due to a more serious problem, the application has not been able to perform a function
#CRITICAL: A serious error indicating the application may be unable to continue running