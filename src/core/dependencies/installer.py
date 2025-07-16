"""Package dependency installer."""
import os
import sys
import subprocess
from typing import List
from ..logger import setup_logger

logger = setup_logger(__name__)

def install_dependencies(packages: List[str]) -> bool:
    """Attempt to install missing dependencies.
    
    Args:
        packages: List of package names to install
        
    Returns:
        Boolean indicating success of installation
    """
    try:
        for package in packages:
            logger.info(f'Attempting to install {package}')
            if package == 'pywin32':
                # Try installing pywin32 with post-install script
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', 'pywin32'])
                    # Run post-install script
                    try:
                        import win32com.client
                        logger.info('pywin32 post-install script completed successfully')
                    except ImportError:
                        logger.warning('pywin32 post-install script may be needed')
                        try:
                            python_scripts = os.path.join(os.path.dirname(sys.executable), 'Scripts')
                            post_install = os.path.join(python_scripts, 'pywin32_postinstall.py')
                            if os.path.exists(post_install):
                                subprocess.check_call([sys.executable, post_install, '-install'])
                                logger.info('pywin32 post-install script completed')
                        except Exception as e:
                            logger.error(f'Failed to run pywin32 post-install script: {str(e)}')
                            return False
                except Exception as e:
                    logger.error(f'Failed to install pywin32: {str(e)}')
                    return False
            else:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        return True
    except Exception as e:
        logger.error(f'Failed to install dependencies: {str(e)}')
        return False
