"""Windows Driver management."""
import wmi
import win32api
import win32service
from typing import List, Dict, Any, Optional
from src.core.logger import setup_logger

class DriverManager:
    """Manager for Windows Device Drivers."""
    
    # Driver start type mapping
    START_TYPES = {
        0: 'Boot',
        1: 'System',
        2: 'Auto',
        3: 'Manual',
        4: 'Disabled'
    }
    
    # Driver state mapping
    STATES = {
        1: 'Stopped',
        4: 'Running',
        5: 'Starting',
        6: 'Stopping',
        7: 'Error'
    }
    
    def __init__(self):
        """Initialize driver manager."""
        self.logger = setup_logger(self.__class__.__name__)
        self.wmi = wmi.WMI()
        
    def get_drivers(self) -> List[Dict[str, Any]]:
        """Get list of installed drivers.
        
        Returns:
            list: List of driver dictionaries with properties
        """
        try:
            drivers = []
            
            # Get drivers from WMI
            for driver in self.wmi.Win32_SystemDriver():
                try:
                    drivers.append({
                        'name': driver.Name,
                        'display_name': driver.DisplayName,
                        'description': driver.Description or "",
                        'start_type': self.START_TYPES.get(driver.StartMode, 'Unknown'),
                        'state': self.STATES.get(driver.State, 'Unknown'),
                        'path': driver.PathName,
                        'service_type': driver.ServiceType,
                        'manufacturer': driver.Manufacturer or "Unknown",
                        'error_control': driver.ErrorControl
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to get details for driver {driver.Name}: {str(e)}")
                    continue
                    
            return sorted(drivers, key=lambda d: d['name'])
            
        except Exception as e:
            self.logger.error(f"Failed to enumerate drivers: {str(e)}")
            return []
            
    def get_driver_details(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific driver.
        
        Args:
            name: Driver name
            
        Returns:
            dict: Driver details or None if not found
        """
        try:
            # Get driver from WMI
            drivers = self.wmi.Win32_SystemDriver(Name=name)
            if not drivers:
                return None
                
            driver = drivers[0]
            
            # Get dependencies
            dependencies = []
            try:
                sc_handle = win32service.OpenSCManager(
                    None,
                    None,
                    win32service.SC_MANAGER_ENUMERATE_SERVICE
                )
                
                try:
                    svc_handle = win32service.OpenService(
                        sc_handle,
                        name,
                        win32service.SERVICE_QUERY_CONFIG
                    )
                    
                    try:
                        config = win32service.QueryServiceConfig(svc_handle)
                        if config[8]:  # Dependencies
                            dependencies = config[8]
                    finally:
                        win32service.CloseServiceHandle(svc_handle)
                        
                finally:
                    win32service.CloseServiceHandle(sc_handle)
                    
            except Exception as e:
                self.logger.warning(f"Failed to get dependencies for {name}: {str(e)}")
                
            return {
                'name': driver.Name,
                'display_name': driver.DisplayName,
                'description': driver.Description or "",
                'start_type': self.START_TYPES.get(driver.StartMode, 'Unknown'),
                'state': self.STATES.get(driver.State, 'Unknown'),
                'path': driver.PathName,
                'service_type': driver.ServiceType,
                'manufacturer': driver.Manufacturer or "Unknown",
                'error_control': driver.ErrorControl,
                'dependencies': dependencies,
                'caption': driver.Caption,
                'started': driver.Started,
                'start_name': driver.StartName,
                'system_name': driver.SystemName,
                'tag_id': driver.TagId
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get driver details: {str(e)}")
            return None
            
    def start_driver(self, name: str) -> bool:
        """Start a driver.
        
        Args:
            name: Driver name
            
        Returns:
            bool: True if successful
        """
        try:
            sc_handle = win32service.OpenSCManager(
                None,
                None,
                win32service.SC_MANAGER_ALL_ACCESS
            )
            
            try:
                svc_handle = win32service.OpenService(
                    sc_handle,
                    name,
                    win32service.SERVICE_ALL_ACCESS
                )
                
                try:
                    win32service.StartService(svc_handle, None)
                    return True
                    
                finally:
                    win32service.CloseServiceHandle(svc_handle)
                    
            finally:
                win32service.CloseServiceHandle(sc_handle)
                
        except Exception as e:
            self.logger.error(f"Failed to start driver {name}: {str(e)}")
            return False
            
    def stop_driver(self, name: str) -> bool:
        """Stop a driver.
        
        Args:
            name: Driver name
            
        Returns:
            bool: True if successful
        """
        try:
            sc_handle = win32service.OpenSCManager(
                None,
                None,
                win32service.SC_MANAGER_ALL_ACCESS
            )
            
            try:
                svc_handle = win32service.OpenService(
                    sc_handle,
                    name,
                    win32service.SERVICE_ALL_ACCESS
                )
                
                try:
                    status = win32service.ControlService(
                        svc_handle,
                        win32service.SERVICE_CONTROL_STOP
                    )
                    return True
                    
                finally:
                    win32service.CloseServiceHandle(svc_handle)
                    
            finally:
                win32service.CloseServiceHandle(sc_handle)
                
        except Exception as e:
            self.logger.error(f"Failed to stop driver {name}: {str(e)}")
            return False
            
    def set_startup_type(self, name: str, start_type: str) -> bool:
        """Set driver startup type.
        
        Args:
            name: Driver name
            start_type: Startup type ('Boot', 'System', 'Auto', 'Manual', 'Disabled')
            
        Returns:
            bool: True if successful
        """
        try:
            # Convert start type string to value
            start_values = {v: k for k, v in self.START_TYPES.items()}
            start_value = start_values.get(start_type)
            if start_value is None:
                raise ValueError(f"Invalid start type: {start_type}")
                
            sc_handle = win32service.OpenSCManager(
                None,
                None,
                win32service.SC_MANAGER_ALL_ACCESS
            )
            
            try:
                svc_handle = win32service.OpenService(
                    sc_handle,
                    name,
                    win32service.SERVICE_ALL_ACCESS
                )
                
                try:
                    win32service.ChangeServiceConfig(
                        svc_handle,
                        win32service.SERVICE_NO_CHANGE,  # Service type
                        start_value,  # Start type
                        win32service.SERVICE_NO_CHANGE,  # Error control
                        None,  # Binary path
                        None,  # Load order group
                        None,  # Tag ID
                        None,  # Dependencies
                        None,  # Account name
                        None,  # Password
                        None   # Display name
                    )
                    return True
                    
                finally:
                    win32service.CloseServiceHandle(svc_handle)
                    
            finally:
                win32service.CloseServiceHandle(sc_handle)
                
        except Exception as e:
            self.logger.error(f"Failed to set startup type for {name}: {str(e)}")
            return False
