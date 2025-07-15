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
