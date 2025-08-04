"""
Remote Process Manager for WinOpsTool

This module provides a process manager that uses the REST API client
for remote process operations.
"""

import logging
from typing import Dict, List, Optional, Any, Union

from src.core.logger import setup_logger
from src.core.remote.rest_manager import RestManager

class RemoteProcessManager:
    """
    Process manager for remote operations using REST API.
    Maintains the same interface as the local ProcessManager.
    """
    
    def __init__(self, rest_manager: RestManager):
        """
        Initialize the remote process manager.
        
        Args:
            rest_manager: REST manager instance for remote operations
        """
        self.logger = setup_logger(self.__class__.__name__)
        self.rest_manager = rest_manager
    
    def get_processes(self) -> List[Dict]:
        """
        Get list of all processes on the remote machine.
        
        Returns:
            List of process dictionaries with details
        """
        if not self.rest_manager.is_connected():
            self.logger.error("Not connected to a remote PC")
            return []
            
        try:
            response = self.rest_manager.get_client().get_processes()
            if response.get("success", False):
                return response.get("data", [])
            else:
                self.logger.error(f"Failed to get processes: {response.get('message', 'Unknown error')}")
                return []
        except Exception as e:
            self.logger.error(f"Failed to get processes: {str(e)}")
            return []
    
    def get_process(self, pid: int) -> Optional[Dict]:
        """
        Get information about a specific process.
        
        Args:
            pid: Process ID
            
        Returns:
            Process information dictionary or None if not found
        """
        if not self.rest_manager.is_connected():
            self.logger.error("Not connected to a remote PC")
            return None
            
        try:
            response = self.rest_manager.get_client().get_process(pid)
            if response.get("success", False):
                return response.get("data")
            else:
                self.logger.error(f"Failed to get process {pid}: {response.get('message', 'Unknown error')}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to get process {pid}: {str(e)}")
            return None
    
    def terminate_process(self, pid: int) -> bool:
        """
        Terminate a process.
        
        Args:
            pid: Process ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.rest_manager.is_connected():
            self.logger.error("Not connected to a remote PC")
            return False
            
        try:
            response = self.rest_manager.get_client().terminate_process(pid)
            if response.get("success", False):
                return True
            else:
                self.logger.error(f"Failed to terminate process {pid}: {response.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to terminate process {pid}: {str(e)}")
            return False
