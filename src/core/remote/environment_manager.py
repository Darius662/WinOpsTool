"""
Remote Environment Manager for WinOpsTool

This module provides an environment manager that uses the REST API client
for remote environment variable operations.
"""

import logging
from typing import Dict, List, Optional, Any, Union

from src.core.logger import setup_logger
from src.core.remote.rest_manager import RestManager

class RemoteEnvironmentManager:
    """
    Environment manager for remote operations using REST API.
    Maintains the same interface as the local EnvironmentManager.
    """
    
    def __init__(self, rest_manager: RestManager):
        """
        Initialize the remote environment manager.
        
        Args:
            rest_manager: REST manager instance for remote operations
        """
        self.logger = setup_logger(self.__class__.__name__)
        self.rest_manager = rest_manager
    
    def get_environment_variables(self) -> Dict[str, str]:
        """
        Get all environment variables from the remote machine.
        
        Returns:
            Dictionary of environment variables (name: value)
        """
        if not self.rest_manager.is_connected():
            self.logger.error("Not connected to a remote PC")
            return {}
            
        try:
            response = self.rest_manager.get_client().get_environment_variables()
            if response.get("success", False):
                return response.get("data", {})
            else:
                self.logger.error(f"Failed to get environment variables: {response.get('message', 'Unknown error')}")
                return {}
        except Exception as e:
            self.logger.error(f"Failed to get environment variables: {str(e)}")
            return {}
    
    def set_environment_variable(self, name: str, value: str, is_system: bool = True) -> bool:
        """
        Set an environment variable on the remote machine.
        
        Args:
            name: Name of the environment variable
            value: Value of the environment variable
            is_system: Whether it's a system or user environment variable
            
        Returns:
            True if successful, False otherwise
        """
        if not self.rest_manager.is_connected():
            self.logger.error("Not connected to a remote PC")
            return False
            
        try:
            response = self.rest_manager.get_client().set_environment_variable(name, value, is_system)
            if response.get("success", False):
                return True
            else:
                self.logger.error(f"Failed to set environment variable {name}: {response.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to set environment variable {name}: {str(e)}")
            return False
    
    def delete_environment_variable(self, name: str, is_system: bool = True) -> bool:
        """
        Delete an environment variable from the remote machine.
        
        Args:
            name: Name of the environment variable
            is_system: Whether it's a system or user environment variable
            
        Returns:
            True if successful, False otherwise
        """
        if not self.rest_manager.is_connected():
            self.logger.error("Not connected to a remote PC")
            return False
            
        try:
            response = self.rest_manager.get_client().delete_environment_variable(name, is_system)
            if response.get("success", False):
                return True
            else:
                self.logger.error(f"Failed to delete environment variable {name}: {response.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to delete environment variable {name}: {str(e)}")
            return False
