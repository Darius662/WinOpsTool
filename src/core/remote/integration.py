"""
Remote Integration for WinOpsTool

This module provides integration between the main application and the remote
management functionality using the REST API.
"""

import logging
from typing import Dict, List, Optional, Any, Union

from src.core.logger import setup_logger
from src.core.manager_factory import ManagerFactory, OperationMode
from src.core.remote.rest_manager import RestManager

class RemoteIntegration:
    """
    Handles integration between the main application and remote management.
    """
    
    def __init__(self):
        """Initialize the remote integration."""
        self.logger = setup_logger(self.__class__.__name__)
        self.manager_factory = ManagerFactory()
        self.rest_manager = self.manager_factory.get_rest_manager()
    
    def connect_to_remote(self, name: str, hostname: str, api_key: str, port: int = 8000) -> bool:
        """
        Connect to a remote PC using REST API.
        
        Args:
            name: Friendly name for the connection
            hostname: Hostname or IP address of the remote PC
            api_key: API key for authentication
            port: Port number (default: 8000)
            
        Returns:
            True if connection was successful, False otherwise
        """
        try:
            # Add the connection to the REST manager
            if not self.rest_manager.add_connection(name, hostname, api_key, port):
                return False
            
            # Connect to the remote PC
            if not self.rest_manager.connect(name):
                return False
            
            # Switch to remote mode
            self.manager_factory.set_mode(OperationMode.REMOTE)
            
            self.logger.info(f"Connected to remote PC: {name}")
            return True
                
        except Exception as e:
            self.logger.error(f"Failed to connect to remote PC {name}: {str(e)}")
            return False
    
    def disconnect_from_remote(self) -> bool:
        """
        Disconnect from the current remote PC.
        
        Returns:
            True if disconnection was successful, False otherwise
        """
        try:
            # Disconnect from the remote PC
            if not self.rest_manager.disconnect():
                return False
            
            # Switch to local mode
            self.manager_factory.set_mode(OperationMode.LOCAL)
            
            self.logger.info("Disconnected from remote PC")
            return True
                
        except Exception as e:
            self.logger.error(f"Failed to disconnect from remote PC: {str(e)}")
            return False
    
    def is_connected_to_remote(self) -> bool:
        """
        Check if connected to a remote PC.
        
        Returns:
            True if connected to a remote PC, False otherwise
        """
        return self.rest_manager.is_connected()
    
    def get_remote_connections(self) -> List[Dict]:
        """
        Get list of all remote connections.
        
        Returns:
            List of connection dictionaries
        """
        connections = []
        for connection in self.rest_manager.get_connections():
            connections.append({
                "name": connection.name,
                "hostname": connection.hostname,
                "port": connection.port,
                "is_connected": connection.is_connected
            })
        return connections
    
    def get_active_remote_connection(self) -> Optional[Dict]:
        """
        Get the active remote connection.
        
        Returns:
            Active connection dictionary or None if not connected
        """
        connection = self.rest_manager.get_active_connection()
        if connection:
            return {
                "name": connection.name,
                "hostname": connection.hostname,
                "port": connection.port,
                "is_connected": connection.is_connected
            }
        return None
    
    def get_manager_factory(self) -> ManagerFactory:
        """
        Get the manager factory instance.
        
        Returns:
            Manager factory instance
        """
        return self.manager_factory
