"""Configuration management package."""
from .manager import ConfigManager

# Application constants
APP_NAME = "Windows System Management Tool"
APP_VERSION = "1.0.0"
CONFIG_FILE = "config.yaml"

# Required packages for the application
REQUIRED_PACKAGES = [
    'PyQt6',
    'pywin32',
    'pyyaml',
    'psutil',
    'wmi'
]

__all__ = [
    'ConfigManager',
    'APP_NAME',
    'APP_VERSION',
    'CONFIG_FILE',
    'REQUIRED_PACKAGES'
]
