"""Windows Services management."""
import win32service
import win32serviceutil
import pywintypes
import win32security
import winreg
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
            
    def is_driver(self, name):
        """Check if a service is a driver.
        
        Args:
            name: Service name
            
        Returns:
            bool: True if the service is a driver, False otherwise
        """
        try:
            sc_handle = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
            try:
                handle = win32service.OpenService(sc_handle, name, win32service.SERVICE_QUERY_CONFIG)
                try:
                    config = win32service.QueryServiceConfig(handle)
                    # Check if service type is a driver
                    service_type = config[0]  # First element is service type
                    return bool(service_type & win32service.SERVICE_DRIVER)
                finally:
                    win32service.CloseServiceHandle(handle)
            finally:
                win32service.CloseServiceHandle(sc_handle)
        except Exception as e:
            self.logger.error(f"Error checking if {name} is a driver: {str(e)}")
            return False
            
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
                
            # Open service manager and service
            handle_scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
            try:
                handle_svc = win32service.OpenService(handle_scm, name, win32service.SERVICE_CHANGE_CONFIG)
                try:
                    # Change service config
                    win32service.ChangeServiceConfig(
                        handle_svc,
                        win32service.SERVICE_NO_CHANGE,  # service type
                        type_map[start_type],            # start type
                        win32service.SERVICE_NO_CHANGE,  # error control
                        None,                           # binary path
                        None,                           # load order group
                        0,                              # tag id
                        None,                           # dependencies
                        None,                           # service start name
                        None,                           # password
                        None                            # display name
                    )
                    self.logger.info(f"Changed startup type for {name} to {start_type}")
                    return True
                finally:
                    win32service.CloseServiceHandle(handle_svc)
            finally:
                win32service.CloseServiceHandle(handle_scm)
            
        except Exception as e:
            self.logger.error(f"Failed to change startup type for {name}: {str(e)}")
            return False
            
    def set_display_name(self, name, display_name):
        """Set service display name.
        
        Args:
            name: Service name
            display_name: New display name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Open service manager and service
            handle_scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
            try:
                handle_svc = win32service.OpenService(handle_scm, name, win32service.SERVICE_CHANGE_CONFIG)
                try:
                    # Change service config
                    win32service.ChangeServiceConfig(
                        handle_svc,
                        win32service.SERVICE_NO_CHANGE,  # service type
                        win32service.SERVICE_NO_CHANGE,  # start type
                        win32service.SERVICE_NO_CHANGE,  # error control
                        None,                           # binary path
                        None,                           # load order group
                        0,                              # tag id
                        None,                           # dependencies
                        None,                           # service start name
                        None,                           # password
                        display_name                    # display name
                    )
                    self.logger.info(f"Changed display name for {name} to {display_name}")
                    return True
                finally:
                    win32service.CloseServiceHandle(handle_svc)
            finally:
                win32service.CloseServiceHandle(handle_scm)
            
        except Exception as e:
            self.logger.error(f"Failed to change display name for {name}: {str(e)}")
            return False
            
    def set_description(self, name, description):
        """Set service description.
        
        Args:
            name: Service name
            description: New description
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            sc_handle = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
            try:
                service_handle = win32service.OpenService(sc_handle, name, win32service.SERVICE_CHANGE_CONFIG)
                try:
                    # Create description structure
                    desc_info = win32service.SERVICE_DESCRIPTION(description)
                    win32service.ChangeServiceConfig2(service_handle, win32service.SERVICE_CONFIG_DESCRIPTION, desc_info)
                    
                    self.logger.info(f"Changed description for {name}")
                    return True
                finally:
                    win32service.CloseServiceHandle(service_handle)
            finally:
                win32service.CloseServiceHandle(sc_handle)
                
        except Exception as e:
            self.logger.error(f"Failed to change description for {name}: {str(e)}")
            return False
            
    def set_path(self, name, path):
        """Set service binary path.
        
        Args:
            name: Service name
            path: New binary path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Open service manager and service
            handle_scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
            try:
                handle_svc = win32service.OpenService(handle_scm, name, win32service.SERVICE_CHANGE_CONFIG)
                try:
                    # Change service config
                    win32service.ChangeServiceConfig(
                        handle_svc,
                        win32service.SERVICE_NO_CHANGE,  # service type
                        win32service.SERVICE_NO_CHANGE,  # start type
                        win32service.SERVICE_NO_CHANGE,  # error control
                        path,                           # binary path
                        None,                           # load order group
                        0,                              # tag id
                        None,                           # dependencies
                        None,                           # service start name
                        None,                           # password
                        None                            # display name
                    )
                    self.logger.info(f"Changed binary path for {name} to {path}")
                    return True
                finally:
                    win32service.CloseServiceHandle(handle_svc)
            finally:
                win32service.CloseServiceHandle(handle_scm)
            
        except Exception as e:
            self.logger.error(f"Failed to change binary path for {name}: {str(e)}")
            return False
            
    def set_account(self, name, account, password=None):
        """Set service logon account.
        
        Args:
            name: Service name
            account: New logon account (e.g., "LocalSystem", "NT AUTHORITY\\NetworkService", etc.)
            password: Account password (None for system accounts)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Open service manager and service
            handle_scm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
            try:
                handle_svc = win32service.OpenService(handle_scm, name, win32service.SERVICE_CHANGE_CONFIG)
                try:
                    # Change service config
                    win32service.ChangeServiceConfig(
                        handle_svc,
                        win32service.SERVICE_NO_CHANGE,  # service type
                        win32service.SERVICE_NO_CHANGE,  # start type
                        win32service.SERVICE_NO_CHANGE,  # error control
                        None,                           # binary path
                        None,                           # load order group
                        0,                              # tag id
                        None,                           # dependencies
                        account,                        # service start name
                        password,                       # password
                        None                            # display name
                    )
                    self.logger.info(f"Changed logon account for {name} to {account}")
                    return True
                finally:
                    win32service.CloseServiceHandle(handle_svc)
            finally:
                win32service.CloseServiceHandle(handle_scm)
            
        except Exception as e:
            self.logger.error(f"Failed to change logon account for {name}: {str(e)}")
            return False
            
    def set_recovery_options(self, name, first_action="restart", second_action="restart", 
                           third_action="none", reset_period=86400):
        """Set service recovery options.
        
        Args:
            name: Service name
            first_action: Action on first failure ("restart", "reboot", "run_command", "none")
            second_action: Action on second failure
            third_action: Action on subsequent failures
            reset_period: Time in seconds after which to reset failure count (default 1 day)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Recovery options can only be set for Win32 services, not for drivers
            if self.is_driver(name):
                self.logger.warning(f"Cannot set recovery options for driver {name}")
                return False
                
            sc_handle = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
            try:
                service_handle = win32service.OpenService(sc_handle, name, win32service.SERVICE_ALL_ACCESS)
                try:
                    # Map action strings to constants
                    action_map = {
                        "none": win32service.SC_ACTION_NONE,
                        "restart": win32service.SC_ACTION_RESTART,
                        "reboot": win32service.SC_ACTION_REBOOT,
                        "run_command": win32service.SC_ACTION_RUN_COMMAND
                    }
                    
                    # Create actions array
                    actions = [
                        (action_map.get(first_action, win32service.SC_ACTION_NONE), 30000),  # 30 sec delay
                        (action_map.get(second_action, win32service.SC_ACTION_NONE), 30000), # 30 sec delay
                        (action_map.get(third_action, win32service.SC_ACTION_NONE), 30000)   # 30 sec delay
                    ]
                    
                    # Set recovery options
                    win32service.ChangeServiceConfig2(
                        service_handle,
                        win32service.SERVICE_CONFIG_FAILURE_ACTIONS,
                        {
                            'ResetPeriod': reset_period,
                            'RebootMsg': '',
                            'Command': '',
                            'Actions': actions
                        }
                    )
                    
                    self.logger.info(f"Set recovery options for {name}")
                    return True
                    
                finally:
                    win32service.CloseServiceHandle(service_handle)
            finally:
                win32service.CloseServiceHandle(sc_handle)
                
        except Exception as e:
            self.logger.error(f"Failed to set recovery options for {name}: {str(e)}")
            return False
            
    def set_delayed_auto_start(self, name, delayed=True):
        """Set delayed auto-start option.
        
        Args:
            name: Service name
            delayed: Whether to enable delayed auto-start
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            sc_handle = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
            try:
                service_handle = win32service.OpenService(sc_handle, name, win32service.SERVICE_CHANGE_CONFIG)
                try:
                    # Set delayed auto-start info
                    win32service.ChangeServiceConfig2(
                        service_handle,
                        win32service.SERVICE_CONFIG_DELAYED_AUTO_START_INFO,
                        delayed
                    )
                    
                    status = "enabled" if delayed else "disabled"
                    self.logger.info(f"Delayed auto-start {status} for {name}")
                    return True
                    
                finally:
                    win32service.CloseServiceHandle(service_handle)
            finally:
                win32service.CloseServiceHandle(sc_handle)
                
        except Exception as e:
            self.logger.error(f"Failed to set delayed auto-start for {name}: {str(e)}")
            return False
