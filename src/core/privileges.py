"""Handle application privileges and security."""
import ctypes
import sys
from typing import Optional
from .logger import setup_logger

logger = setup_logger(__name__)

def is_admin() -> bool:
    """Check if the current process has admin privileges.
    
    Returns:
        Boolean indicating if process has admin rights
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logger.error(f'Failed to check admin status: {str(e)}')
        return False

def request_admin_privileges(executable: Optional[str] = None) -> None:
    """Request elevation to admin privileges.
    
    Args:
        executable: Path to executable to run with admin rights.
                   If None, uses current Python executable.
    """
    try:
        if executable is None:
            executable = sys.executable
            
        logger.info('Requesting admin privileges')
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            'runas',
            executable,
            ' '.join(sys.argv),
            None,
            1
        )
    except Exception as e:
        logger.error(f'Failed to request admin privileges: {str(e)}')
        raise
