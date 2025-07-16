"""Windows environment variables management."""
import os
import winreg
from typing import Dict, List, Optional, Tuple
from src.core.logger import setup_logger

class EnvironmentManager:
    """Manager for Windows environment variables."""
    
    def __init__(self):
        """Initialize environment manager."""
        self.logger = setup_logger(self.__class__.__name__)
        
    def get_user_variables(self) -> Dict[str, str]:
        """Get user environment variables.
        
        Returns:
            dict: Dictionary of user variables {name: value}
        """
        return dict(os.environ)
        
    def get_system_variables(self) -> Dict[str, str]:
        """Get system environment variables.
        
        Returns:
            dict: Dictionary of system variables {name: value}
        """
        try:
            variables = {}
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
                0,
                winreg.KEY_READ
            )
            
            try:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        variables[name] = value
                        i += 1
                    except WindowsError:
                        break
            finally:
                winreg.CloseKey(key)
                
            return variables
            
        except WindowsError as e:
            self.logger.error(f"Failed to get system variables: {str(e)}")
            return {}
            
    def set_user_variable(self, name: str, value: str) -> bool:
        """Set a user environment variable.
        
        Args:
            name: Variable name
            value: Variable value
            
        Returns:
            bool: True if successful
        """
        try:
            os.environ[name] = value
            return True
        except Exception as e:
            self.logger.error(f"Failed to set user variable {name}: {str(e)}")
            return False
            
    def set_system_variable(self, name: str, value: str) -> bool:
        """Set a system environment variable.
        
        Args:
            name: Variable name
            value: Variable value
            
        Returns:
            bool: True if successful
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
                0,
                winreg.KEY_WRITE
            )
            
            try:
                winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
                return True
            finally:
                winreg.CloseKey(key)
                
        except WindowsError as e:
            self.logger.error(f"Failed to set system variable {name}: {str(e)}")
            return False
            
    def delete_user_variable(self, name: str) -> bool:
        """Delete a user environment variable.
        
        Args:
            name: Variable name to delete
            
        Returns:
            bool: True if successful
        """
        try:
            del os.environ[name]
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete user variable {name}: {str(e)}")
            return False
            
    def delete_system_variable(self, name: str) -> bool:
        """Delete a system environment variable.
        
        Args:
            name: Variable name to delete
            
        Returns:
            bool: True if successful
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
                0,
                winreg.KEY_WRITE
            )
            
            try:
                winreg.DeleteValue(key, name)
                return True
            finally:
                winreg.CloseKey(key)
                
        except WindowsError as e:
            self.logger.error(f"Failed to delete system variable {name}: {str(e)}")
            return False
