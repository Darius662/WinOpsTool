"""Handle bundled dependencies when running as executable."""
import sys
import os

def is_bundled():
    """Check if running as a bundled executable."""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
