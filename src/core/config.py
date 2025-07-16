"""Global configuration and constants."""
from pathlib import Path
import os

# Root paths
ROOT_DIR = Path(__file__).parent.parent.parent
SRC_DIR = ROOT_DIR / 'src'
LOG_DIR = ROOT_DIR / 'logs'
CONFIG_DIR = ROOT_DIR / 'config'
BACKUP_DIR = ROOT_DIR / 'backups'

# Create necessary directories
for directory in [LOG_DIR, CONFIG_DIR, BACKUP_DIR]:
    directory.mkdir(exist_ok=True)

# Application settings
APP_NAME = "System Management Tool"
APP_VERSION = "1.0.0"

# Logging configuration
LOG_FILE = LOG_DIR / 'system_manager.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

# Required dependencies
REQUIRED_PACKAGES = [
    'PyQt6',
    'pywin32',
    'psutil',
    'pyuac',
    'winreg',
    'pyyaml'
]
