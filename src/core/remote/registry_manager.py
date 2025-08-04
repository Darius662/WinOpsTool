"""
Remote Registry Manager for WinOpsTool

This module provides a registry manager that uses the REST API client
for remote registry operations.
"""

import logging
from typing import Dict, List, Optional, Any, Union

from src.core.logger import setup_logger
from src.core.remote.rest_manager import RestManager

class RemoteRegistryManager:
    """
    Registry manager for remote operations using REST API.
    Maintains the same interface as the local RegistryManager.
    """
    
    def __init__(self, rest_manager: RestManager):
        """
        Initialize the remote registry manager.
        
        Args:
            rest_manager: REST manager instance for remote operations
        """
        self.logger = setup_logger(self.__class__.__name__)
        self.rest_manager = rest_manager
    
    def get_key_values(self, hkey: str, key_path: str) -> Dict[str, Any]:
        """
        Get values from a registry key on the remote machine.
        
        Args:
            hkey: Root key (HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, etc.)
            key_path: Path to the registry key
            
        Returns:
            Dictionary of values (name: value)
        """
        if not self.rest_manager.is_connected():
            self.logger.error("Not connected to a remote PC")
            return {}
            
        try:
            response = self._make_request("GET", "/registry", params={
                "hkey": hkey,
                "key_path": key_path
            })
            
            if response.get("success", False):
                return response.get("data", {})
            else:
                self.logger.error(f"Failed to get registry values: {response.get('message', 'Unknown error')}")
                return {}
        except Exception as e:
            self.logger.error(f"Failed to get registry values: {str(e)}")
            return {}
    
    def set_key_value(self, hkey: str, key_path: str, value_name: str, value_data: Any, value_type: str) -> bool:
        """
        Set a registry value on the remote machine.
        
        Args:
            hkey: Root key (HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, etc.)
            key_path: Path to the registry key
            value_name: Name of the value
            value_data: Value data
            value_type: Value type (REG_SZ, REG_DWORD, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.rest_manager.is_connected():
            self.logger.error("Not connected to a remote PC")
            return False
            
        try:
            data = {
                "hkey": hkey,
                "key_path": key_path,
                "value_name": value_name,
                "value_data": value_data,
                "value_type": value_type
            }
            
            response = self._make_request("POST", "/registry", data=data)
            
            if response.get("success", False):
                return True
            else:
                self.logger.error(f"Failed to set registry value: {response.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to set registry value: {str(e)}")
            return False
    
    def delete_key_value(self, hkey: str, key_path: str, value_name: str) -> bool:
        """
        Delete a registry value on the remote machine.
        
        Args:
            hkey: Root key (HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, etc.)
            key_path: Path to the registry key
            value_name: Name of the value
            
        Returns:
            True if successful, False otherwise
        """
        if not self.rest_manager.is_connected():
            self.logger.error("Not connected to a remote PC")
            return False
            
        try:
            params = {
                "hkey": hkey,
                "key_path": key_path,
                "value_name": value_name
            }
            
            response = self._make_request("DELETE", "/registry", params=params)
            
            if response.get("success", False):
                return True
            else:
                self.logger.error(f"Failed to delete registry value: {response.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to delete registry value: {str(e)}")
            return False
    
    def create_key(self, hkey: str, key_path: str) -> bool:
        """
        Create a registry key on the remote machine.
        
        Args:
            hkey: Root key (HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, etc.)
            key_path: Path to the registry key
            
        Returns:
            True if successful, False otherwise
        """
        if not self.rest_manager.is_connected():
            self.logger.error("Not connected to a remote PC")
            return False
            
        try:
            data = {
                "hkey": hkey,
                "key_path": key_path
            }
            
            response = self._make_request("PUT", "/registry/key", data=data)
            
            if response.get("success", False):
                return True
            else:
                self.logger.error(f"Failed to create registry key: {response.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to create registry key: {str(e)}")
            return False
    
    def delete_key(self, hkey: str, key_path: str) -> bool:
        """
        Delete a registry key on the remote machine.
        
        Args:
            hkey: Root key (HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, etc.)
            key_path: Path to the registry key
            
        Returns:
            True if successful, False otherwise
        """
        if not self.rest_manager.is_connected():
            self.logger.error("Not connected to a remote PC")
            return False
            
        try:
            params = {
                "hkey": hkey,
                "key_path": key_path
            }
            
            response = self._make_request("DELETE", "/registry/key", params=params)
            
            if response.get("success", False):
                return True
            else:
                self.logger.error(f"Failed to delete registry key: {response.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to delete registry key: {str(e)}")
            return False
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """
        Make a request to the API server.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data
        """
        client = self.rest_manager.get_client()
        if not client:
            return {"success": False, "message": "No API client available"}
        
        return client._make_request(method, endpoint, data, params)
