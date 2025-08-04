"""
REST API Manager for WinOpsTool

This module provides a manager for remote operations using the REST API client.
It serves as a replacement for PowerShell Remoting.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from src.core.logger import setup_logger
from src.core.remote.rest_client import RestApiClient

@dataclass
class RemoteConnection:
    """Remote connection details."""
    name: str
    hostname: str
    api_key: str
    port: int = 8000
    is_connected: bool = False

class RestManager:
    """Manages connections to remote PCs using REST API."""
    
    def __init__(self):
        """Initialize the REST manager."""
        self.logger = setup_logger(self.__class__.__name__)
        self.connections: Dict[str, RemoteConnection] = {}
        self.active_connection: Optional[RemoteConnection] = None
        self.client: Optional[RestApiClient] = None
    
    def add_connection(self, name: str, hostname: str, api_key: str, port: int = 8000) -> bool:
        """
        Add a new remote PC connection.
        
        Args:
            name: Friendly name for the connection
            hostname: Hostname or IP address of the remote PC
            api_key: API key for authentication
            port: Port number (default: 8000)
            
        Returns:
            True if connection was added successfully, False otherwise
        """
        try:
            # Create a new client to test the connection
            base_url = f"http://{hostname}:{port}"
            test_client = RestApiClient(base_url, api_key)
            
            # Test the connection
            if test_client.test_connection():
                # If successful, store the connection
                self.connections[name] = RemoteConnection(
                    name=name,
                    hostname=hostname,
                    api_key=api_key,
                    port=port,
                    is_connected=True
                )
                
                self.logger.info(f"Successfully connected to remote PC: {name}")
                return True
            else:
                self.logger.error(f"Failed to connect to remote PC {name}: Connection test failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to connect to remote PC {name}: {str(e)}")
            return False
    
    def remove_connection(self, name: str) -> bool:
        """
        Remove a remote PC connection.
        
        Args:
            name: Name of the connection to remove
            
        Returns:
            True if connection was removed successfully, False otherwise
        """
        try:
            if name in self.connections:
                # If this is the active connection, disconnect first
                if self.active_connection and self.active_connection.name == name:
                    self.disconnect()
                
                # Remove the connection
                del self.connections[name]
                self.logger.info(f"Removed connection to remote PC: {name}")
                return True
            return False
                
        except Exception as e:
            self.logger.error(f"Failed to remove connection to remote PC {name}: {str(e)}")
            return False
    
    def get_connections(self) -> List[RemoteConnection]:
        """
        Get list of all connections.
        
        Returns:
            List of connections
        """
        return list(self.connections.values())
    
    def get_connection(self, name: str) -> Optional[RemoteConnection]:
        """
        Get a specific connection by name.
        
        Args:
            name: Name of the connection
            
        Returns:
            Connection details or None if not found
        """
        return self.connections.get(name)
    
    def connect(self, name: str) -> bool:
        """
        Connect to a remote PC.
        
        Args:
            name: Name of the connection
            
        Returns:
            True if connection was successful, False otherwise
        """
        try:
            if name not in self.connections:
                self.logger.error(f"Connection '{name}' not found")
                return False
            
            # Disconnect from any existing connection
            if self.active_connection:
                self.disconnect()
            
            # Set the active connection
            connection = self.connections[name]
            base_url = f"http://{connection.hostname}:{connection.port}"
            self.client = RestApiClient(base_url, connection.api_key)
            
            # Test the connection
            if self.client.test_connection():
                self.active_connection = connection
                self.logger.info(f"Connected to remote PC: {name}")
                return True
            else:
                self.client = None
                self.logger.error(f"Failed to connect to remote PC {name}: Connection test failed")
                return False
                
        except Exception as e:
            self.client = None
            self.logger.error(f"Failed to connect to remote PC {name}: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from the current remote PC.
        
        Returns:
            True if disconnection was successful, False otherwise
        """
        try:
            if not self.active_connection:
                return True
            
            self.client = None
            self.active_connection = None
            self.logger.info("Disconnected from remote PC")
            return True
                
        except Exception as e:
            self.logger.error(f"Failed to disconnect from remote PC: {str(e)}")
            return False
    
    def test_connection(self, name: str) -> bool:
        """
        Test if a connection is still active.
        
        Args:
            name: Name of the connection
            
        Returns:
            True if connection is active, False otherwise
        """
        try:
            if name not in self.connections:
                return False
            
            connection = self.connections[name]
            base_url = f"http://{connection.hostname}:{connection.port}"
            test_client = RestApiClient(base_url, connection.api_key)
            
            return test_client.test_connection()
                
        except Exception:
            return False
    
    def refresh_connections(self):
        """Refresh all connections and update their status."""
        for name, connection in list(self.connections.items()):
            is_connected = self.test_connection(name)
            connection.is_connected = is_connected
            
            if not is_connected:
                self.logger.warning(f"Lost connection to remote PC: {name}")
    
    def is_connected(self) -> bool:
        """
        Check if there is an active connection.
        
        Returns:
            True if there is an active connection, False otherwise
        """
        return self.active_connection is not None and self.client is not None
    
    def get_active_connection(self) -> Optional[RemoteConnection]:
        """
        Get the active connection.
        
        Returns:
            Active connection or None if not connected
        """
        return self.active_connection
    
    def get_client(self) -> Optional[RestApiClient]:
        """
        Get the REST API client for the active connection.
        
        Returns:
            REST API client or None if not connected
        """
        return self.client
