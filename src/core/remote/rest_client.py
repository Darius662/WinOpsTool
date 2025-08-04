"""
REST API Client for WinOpsTool

This module provides a client for interacting with the WinOpsTool REST API server.
It serves as a replacement for PowerShell Remoting.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin

class RestApiClient:
    """Client for interacting with the WinOpsTool REST API server."""
    
    def __init__(self, base_url: str, api_key: str = None):
        """
        Initialize the REST API client.
        
        Args:
            base_url: Base URL of the API server (e.g., http://localhost:8000)
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.logger = logging.getLogger("RestApiClient")
        
        # Set up session with default headers
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """
        Make a request to the API server.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., /services)
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    self.logger.error(f"API error: {error_data}")
                    return {
                        "success": False,
                        "message": error_data.get('detail', str(e)),
                        "data": None
                    }
                except:
                    pass
            
            return {
                "success": False,
                "message": str(e),
                "data": None
            }
    
    def test_connection(self) -> bool:
        """
        Test connection to the API server.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = self._make_request("GET", "/")
            return response.get("success", False)
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def get_system_info(self) -> Dict:
        """
        Get system information.
        
        Returns:
            System information
        """
        return self._make_request("GET", "/system")
    
    # Services methods
    def get_services(self) -> Dict:
        """
        Get list of all services.
        
        Returns:
            List of services
        """
        return self._make_request("GET", "/services")
    
    def get_service(self, service_name: str) -> Dict:
        """
        Get information about a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service information
        """
        return self._make_request("GET", f"/services/{service_name}")
    
    def service_action(self, service_name: str, action: str) -> Dict:
        """
        Perform an action on a service.
        
        Args:
            service_name: Name of the service
            action: Action to perform (start, stop, restart, pause, resume)
            
        Returns:
            Result of the action
        """
        data = {"action": action}
        return self._make_request("POST", f"/services/{service_name}/action", data=data)
    
    # Processes methods
    def get_processes(self) -> Dict:
        """
        Get list of all processes.
        
        Returns:
            List of processes
        """
        return self._make_request("GET", "/processes")
    
    def get_process(self, pid: int) -> Dict:
        """
        Get information about a specific process.
        
        Args:
            pid: Process ID
            
        Returns:
            Process information
        """
        return self._make_request("GET", f"/processes/{pid}")
    
    def terminate_process(self, pid: int) -> Dict:
        """
        Terminate a process.
        
        Args:
            pid: Process ID
            
        Returns:
            Result of the action
        """
        return self._make_request("DELETE", f"/processes/{pid}")
    
    # Environment variables methods
    def get_environment_variables(self) -> Dict:
        """
        Get all environment variables.
        
        Returns:
            List of environment variables
        """
        return self._make_request("GET", "/environment")
    
    def set_environment_variable(self, name: str, value: str, is_system: bool = True) -> Dict:
        """
        Set an environment variable.
        
        Args:
            name: Name of the environment variable
            value: Value of the environment variable
            is_system: Whether it's a system or user environment variable
            
        Returns:
            Result of the action
        """
        data = {
            "name": name,
            "value": value,
            "is_system": is_system
        }
        return self._make_request("POST", "/environment", data=data)
    
    def delete_environment_variable(self, name: str, is_system: bool = True) -> Dict:
        """
        Delete an environment variable.
        
        Args:
            name: Name of the environment variable
            is_system: Whether it's a system or user environment variable
            
        Returns:
            Result of the action
        """
        params = {"is_system": is_system}
        return self._make_request("DELETE", f"/environment/{name}", params=params)
