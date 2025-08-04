"""
Remote System Manager for WinOpsTool

This module provides a system manager that uses the REST API client
for remote system information operations.
"""

import logging
from typing import Dict, List, Optional, Any, Union

from src.core.logger import setup_logger
from src.core.remote.rest_manager import RestManager

class RemoteSystemManager:
    """
    System manager for remote operations using REST API.
    Maintains the same interface as the local SystemManager.
    """
    
    def __init__(self, rest_manager: RestManager):
        """
        Initialize the remote system manager.
        
        Args:
            rest_manager: REST manager instance for remote operations
        """
        self.logger = setup_logger(self.__class__.__name__)
        self.rest_manager = rest_manager
        self._system_info = None
    
    def get_system_info(self, refresh: bool = False) -> Dict:
        """
        Get system information from the remote machine.
        
        Args:
            refresh: Whether to refresh the cached information
            
        Returns:
            Dictionary with system information
        """
        if not self.rest_manager.is_connected():
            self.logger.error("Not connected to a remote PC")
            return {}
            
        try:
            if refresh or self._system_info is None:
                response = self.rest_manager.get_client().get_system_info()
                if response.get("success", False):
                    self._system_info = response.get("data", {})
                else:
                    self.logger.error(f"Failed to get system info: {response.get('message', 'Unknown error')}")
                    return {}
            
            return self._system_info
        except Exception as e:
            self.logger.error(f"Failed to get system info: {str(e)}")
            return {}
    
    def get_hostname(self) -> str:
        """
        Get the hostname of the remote machine.
        
        Returns:
            Hostname
        """
        system_info = self.get_system_info()
        return system_info.get("hostname", "")
    
    def get_os_version(self) -> str:
        """
        Get the OS version of the remote machine.
        
        Returns:
            OS version
        """
        system_info = self.get_system_info()
        return system_info.get("os_version", "")
    
    def get_cpu_info(self) -> Dict:
        """
        Get CPU information of the remote machine.
        
        Returns:
            CPU information
        """
        system_info = self.get_system_info()
        return system_info.get("cpu_info", {})
    
    def get_memory_info(self) -> Dict:
        """
        Get memory information of the remote machine.
        
        Returns:
            Memory information
        """
        system_info = self.get_system_info()
        return system_info.get("memory_info", {})
    
    def get_disk_info(self) -> List[Dict]:
        """
        Get disk information of the remote machine.
        
        Returns:
            List of disk information dictionaries
        """
        system_info = self.get_system_info()
        return system_info.get("disk_info", [])
