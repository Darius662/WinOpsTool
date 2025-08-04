"""
Manager Factory for WinOpsTool

This module provides a factory for creating manager instances based on
whether the application is operating in local or remote mode.
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional, Type, Union

# Import local managers
from src.managers.service_manager import ServiceManager
from src.managers.process_manager import ProcessManager
from src.managers.environment_manager import EnvironmentManager
from src.managers.system_manager import SystemManager

# Import remote managers
from src.core.remote.rest_manager import RestManager
from src.core.remote.service_manager import RemoteServiceManager
from src.core.remote.process_manager import RemoteProcessManager
from src.core.remote.environment_manager import RemoteEnvironmentManager
from src.core.remote.system_manager import RemoteSystemManager

from src.core.logger import setup_logger

class OperationMode(Enum):
    """Enum for operation modes."""
    LOCAL = "local"
    REMOTE = "remote"

class ManagerFactory:
    """Factory for creating manager instances based on operation mode."""
    
    def __init__(self):
        """Initialize the manager factory."""
        self.logger = setup_logger(self.__class__.__name__)
        self.mode = OperationMode.LOCAL
        self.rest_manager = RestManager()
        
        # Cache for manager instances
        self._managers = {
            OperationMode.LOCAL: {},
            OperationMode.REMOTE: {}
        }
    
    def set_mode(self, mode: OperationMode):
        """
        Set the operation mode.
        
        Args:
            mode: Operation mode (LOCAL or REMOTE)
        """
        if self.mode != mode:
            self.logger.info(f"Switching operation mode from {self.mode.value} to {mode.value}")
            self.mode = mode
    
    def get_mode(self) -> OperationMode:
        """
        Get the current operation mode.
        
        Returns:
            Current operation mode
        """
        return self.mode
    
    def get_rest_manager(self) -> RestManager:
        """
        Get the REST manager instance.
        
        Returns:
            REST manager instance
        """
        return self.rest_manager
    
    def get_service_manager(self) -> Union[ServiceManager, RemoteServiceManager]:
        """
        Get a service manager instance based on the current operation mode.
        
        Returns:
            Service manager instance
        """
        return self._get_manager(
            ServiceManager,
            RemoteServiceManager,
            lambda: RemoteServiceManager(self.rest_manager)
        )
    
    def get_process_manager(self) -> Union[ProcessManager, RemoteProcessManager]:
        """
        Get a process manager instance based on the current operation mode.
        
        Returns:
            Process manager instance
        """
        return self._get_manager(
            ProcessManager,
            RemoteProcessManager,
            lambda: RemoteProcessManager(self.rest_manager)
        )
    
    def get_environment_manager(self) -> Union[EnvironmentManager, RemoteEnvironmentManager]:
        """
        Get an environment manager instance based on the current operation mode.
        
        Returns:
            Environment manager instance
        """
        return self._get_manager(
            EnvironmentManager,
            RemoteEnvironmentManager,
            lambda: RemoteEnvironmentManager(self.rest_manager)
        )
    
    def get_system_manager(self) -> Union[SystemManager, RemoteSystemManager]:
        """
        Get a system manager instance based on the current operation mode.
        
        Returns:
            System manager instance
        """
        return self._get_manager(
            SystemManager,
            RemoteSystemManager,
            lambda: RemoteSystemManager(self.rest_manager)
        )
    
    def _get_manager(self, local_class: Type, remote_class: Type, remote_factory):
        """
        Get a manager instance based on the current operation mode.
        
        Args:
            local_class: Class for local manager
            remote_class: Class for remote manager
            remote_factory: Factory function for creating remote manager
            
        Returns:
            Manager instance
        """
        mode = self.mode
        manager_type = local_class.__name__ if mode == OperationMode.LOCAL else remote_class.__name__
        
        # Check if we already have an instance
        if manager_type in self._managers[mode]:
            return self._managers[mode][manager_type]
        
        # Create a new instance
        if mode == OperationMode.LOCAL:
            manager = local_class()
        else:
            manager = remote_factory()
        
        # Cache the instance
        self._managers[mode][manager_type] = manager
        
        return manager
