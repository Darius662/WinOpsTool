"""
Remote Service Manager for WinOpsTool

This module provides a service manager that uses the REST API client
for remote service operations.
"""

import logging
from typing import Dict, List, Optional, Any, Union

from src.core.logger import setup_logger
from src.core.remote.rest_manager import RestManager

class RemoteServiceManager:
    """
    Service manager for remote operations using REST API.
    Maintains the same interface as the local ServiceManager.
    """
    
    def __init__(self, rest_manager: RestManager):
        """
        Initialize the remote service manager.
        
        Args:
            rest_manager: REST manager instance for remote operations
        """
        self.logger = setup_logger(self.__class__.__name__)
        self.rest_manager = rest_manager
    
    def get_services(self) -> List[Dict]:
        """
        Get list of all services on the remote machine.
        
        Returns:
            List of service dictionaries with details
        """
        if not self.rest_manager.is_connected():
            self.logger.error("Not connected to a remote PC")
            return []
            
        try:
            response = self.rest_manager.get_client().get_services()
            if response.get("success", False):
                return response.get("data", [])
            else:
                self.logger.error(f"Failed to get services: {response.get('message', 'Unknown error')}")
                return []
        except Exception as e:
            self.logger.error(f"Failed to get services: {str(e)}")
            return []
    
    def get_service(self, service_name: str) -> Optional[Dict]:
        """
        Get information about a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service information dictionary or None if not found
        """
        if not self.rest_manager.is_connected():
            self.logger.error("Not connected to a remote PC")
            return None
            
        try:
            response = self.rest_manager.get_client().get_service(service_name)
            if response.get("success", False):
                return response.get("data")
            else:
                self.logger.error(f"Failed to get service {service_name}: {response.get('message', 'Unknown error')}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to get service {service_name}: {str(e)}")
            return None
    
    def start_service(self, service_name: str) -> bool:
        """
        Start a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if successful, False otherwise
        """
        return self._service_action(service_name, "start")
    
    def stop_service(self, service_name: str) -> bool:
        """
        Stop a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if successful, False otherwise
        """
        return self._service_action(service_name, "stop")
    
    def restart_service(self, service_name: str) -> bool:
        """
        Restart a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if successful, False otherwise
        """
        return self._service_action(service_name, "restart")
    
    def pause_service(self, service_name: str) -> bool:
        """
        Pause a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if successful, False otherwise
        """
        return self._service_action(service_name, "pause")
    
    def resume_service(self, service_name: str) -> bool:
        """
        Resume a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            True if successful, False otherwise
        """
        return self._service_action(service_name, "resume")
    
    def _service_action(self, service_name: str, action: str) -> bool:
        """
        Perform an action on a service.
        
        Args:
            service_name: Name of the service
            action: Action to perform (start, stop, restart, pause, resume)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.rest_manager.is_connected():
            self.logger.error("Not connected to a remote PC")
            return False
            
        try:
            response = self.rest_manager.get_client().service_action(service_name, action)
            if response.get("success", False):
                return True
            else:
                self.logger.error(f"Failed to {action} service {service_name}: {response.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to {action} service {service_name}: {str(e)}")
            return False
