"""Package dependency checker."""
import sys
from typing import List, Tuple
from ..logger import setup_logger
from ..config import REQUIRED_PACKAGES
from ..bundled import is_bundled

logger = setup_logger(__name__)

def check_dependencies() -> Tuple[bool, List[str]]:
    """Check if all required packages are installed.
    
    Returns:
        Tuple containing:
        - Boolean indicating if all dependencies are met
        - List of missing package names
    """
    # If running as bundled executable, skip dependency check
    if is_bundled():
        logger.debug('Running as bundled executable, skipping dependency check')
        return True, []
    
    missing_packages = []
    
    for package in REQUIRED_PACKAGES:
        try:
            if package == 'pywin32':
                try:
                    import win32api
                    import win32net
                    import win32security
                    logger.debug('pywin32 modules are available')
                except ImportError:
                    missing_packages.append(package)
                    logger.warning('pywin32 modules are not available')
            elif package == 'pyyaml':
                try:
                    import yaml
                    logger.debug('Package PyYAML is installed')
                except ImportError:
                    missing_packages.append(package)
                    logger.warning('Missing required package: PyYAML')
            else:
                __import__(package)
                logger.debug(f'Package {package} is installed')
        except ImportError:
            missing_packages.append(package)
            logger.warning(f'Missing required package: {package}')
    
    return len(missing_packages) == 0, missing_packages
