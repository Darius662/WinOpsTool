"""Windows Services management."""
import win32service
import win32serviceutil
import pywintypes
from src.core.logger import setup_logger

class ServiceManager:
    """Manager for Windows Services."""
    
    def __init__(self):
        """Initialize service manager."""
        self.logger = setup_logger(self.__class__.__name__)
        
    def get_services(self):
        """Get list of all services.
        
        Returns:
            list: List of service dictionaries with properties
        """
        try:
            services = []
            sc_handle = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
            
            try:
                # Enumerate services
                type_filter = win32service.SERVICE_WIN32 | win32service.SERVICE_DRIVER
                state_filter = win32service.SERVICE_STATE_ALL
                
                for svc in win32service.EnumServicesStatus(sc_handle, type_filter, state_filter):
                    name = svc[0]
                    try:
                        # First try with fewer permissions
                        access_level = win32service.SERVICE_QUERY_CONFIG | win32service.SERVICE_QUERY_STATUS
                        try:
                            handle = win32service.OpenService(sc_handle, name, access_level)
                            try:
                                config = win32service.QueryServiceConfig(handle)
                                status = win32service.QueryServiceStatus(handle)
                                description = self._get_service_description(handle)
                                
                                # Map status code to string
                                state = {
                                    win32service.SERVICE_STOPPED: "Stopped",
                                    win32service.SERVICE_START_PENDING: "Starting",
                                    win32service.SERVICE_STOP_PENDING: "Stopping",
                                    win32service.SERVICE_RUNNING: "Running",
                                    win32service.SERVICE_CONTINUE_PENDING: "Continuing",
                                    win32service.SERVICE_PAUSE_PENDING: "Pausing",
                                    win32service.SERVICE_PAUSED: "Paused"
                                }.get(status[1], "Unknown")
                                
                                # Map start type to string
                                start_type = {
                                    win32service.SERVICE_AUTO_START: "Automatic",
                                    win32service.SERVICE_DEMAND_START: "Manual",
                                    win32service.SERVICE_DISABLED: "Disabled",
                                    win32service.SERVICE_BOOT_START: "Boot",
                                    win32service.SERVICE_SYSTEM_START: "System"
                                }.get(config[2], "Unknown")
                                
                                services.append({
                                    'name': name,
                                    'display_name': svc[1],
                                    'description': description,
                                    'state': state,
                                    'start_type': start_type,
                                    'path': config[3],
                                    'account': config[7]
                                })
                                
                            finally:
                                win32service.CloseServiceHandle(handle)
                        except pywintypes.error as e:
                            if e.winerror == 5:  # Access denied error code
                                # Add service with limited info
                                services.append({
                                    'name': name,
                                    'display_name': svc[1],
                                    'description': "Access denied - run as administrator for full details",
                                    'state': "Unknown",
                                    'start_type': "Unknown",
                                    'path': "",
                                    'account': ""
                                })
                            else:
                                # Log non-access denied errors
                                self.logger.warning(f"Failed to get details for service {name}: {str(e)}")
                    except pywintypes.error as e:
                        if e.winerror == 5:  # Access denied error code
                            # Silently add service with limited info
                            services.append({
                                'name': name,
                                'display_name': svc[1],
                                'description': "Access denied - run as administrator for full details",
                                'state': "Unknown",
                                'start_type': "Unknown",
                                'path': "",
                                'account': ""
                            })
                        else:
                            self.logger.warning(f"Failed to get details for service {name}: {str(e)}")
                        continue
                        
            finally:
                win32service.CloseServiceHandle(sc_handle)
                
            return services
            
        except Exception as e:
            self.logger.error(f"Failed to enumerate services: {str(e)}")
            return []
            
    def _get_service_description(self, handle):
        """Get service description.
        
        Args:
            handle: Service handle
            
        Returns:
            str: Service description or empty string
        """
        try:
            return win32service.QueryServiceConfig2(handle, win32service.SERVICE_CONFIG_DESCRIPTION)[0]
        except:
            return ""
            
    def start_service(self, name):
        """Start a service.
        
        Args:
            name: Service name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            win32serviceutil.StartService(name)
            self.logger.info(f"Started service: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start service {name}: {str(e)}")
            return False
            
    def stop_service(self, name):
        """Stop a service.
        
        Args:
            name: Service name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            win32serviceutil.StopService(name)
            self.logger.info(f"Stopped service: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop service {name}: {str(e)}")
            return False
            
    def restart_service(self, name):
        """Restart a service.
        
        Args:
            name: Service name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            win32serviceutil.RestartService(name)
            self.logger.info(f"Restarted service: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to restart service {name}: {str(e)}")
            return False
            
    def set_startup_type(self, name, start_type):
        """Set service startup type.
        
        Args:
            name: Service name
            start_type: "Automatic", "Manual", or "Disabled"
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Map string to win32service constant
            type_map = {
                "Automatic": win32service.SERVICE_AUTO_START,
                "Manual": win32service.SERVICE_DEMAND_START,
                "Disabled": win32service.SERVICE_DISABLED
            }
            
            if start_type not in type_map:
                raise ValueError(f"Invalid start type: {start_type}")
                
            win32serviceutil.ChangeServiceConfig(
                name,
                startType=type_map[start_type]
            )
            
            self.logger.info(f"Changed startup type for {name} to {start_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to change startup type for {name}: {str(e)}")
            return False
