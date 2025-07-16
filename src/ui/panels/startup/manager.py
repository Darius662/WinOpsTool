"""Windows Startup management."""
import os
import winreg
from typing import List, Dict, Any
import win32api
import win32service
from src.core.logger import setup_logger

class StartupManager:
    """Manager for Windows Startup items."""
    
    # Registry paths for startup entries
    STARTUP_PATHS = {
        'HKLM_RUN': (winreg.HKEY_LOCAL_MACHINE, r'Software\Microsoft\Windows\CurrentVersion\Run'),
        'HKLM_RUNONCE': (winreg.HKEY_LOCAL_MACHINE, r'Software\Microsoft\Windows\CurrentVersion\RunOnce'),
        'HKCU_RUN': (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run'),
        'HKCU_RUNONCE': (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\RunOnce')
    }
    
    def __init__(self):
        """Initialize startup manager."""
        self.logger = setup_logger(self.__class__.__name__)
        
    def get_registry_startups(self) -> List[Dict[str, Any]]:
        """Get startup entries from registry.
        
        Returns:
            list: List of startup entry dictionaries
        """
        entries = []
        
        for location, (root, path) in self.STARTUP_PATHS.items():
            try:
                key = winreg.OpenKey(root, path, 0, winreg.KEY_READ)
                
                try:
                    index = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, index)
                            entries.append({
                                'name': name,
                                'command': value,
                                'location': location,
                                'type': 'Registry',
                                'enabled': True  # Registry entries are always enabled
                            })
                            index += 1
                        except WindowsError:
                            break
                            
                finally:
                    winreg.CloseKey(key)
                    
            except WindowsError as e:
                self.logger.warning(f"Failed to read startup key {location}: {str(e)}")
                
        return entries
        
    def get_folder_startups(self) -> List[Dict[str, Any]]:
        """Get startup entries from startup folders.
        
        Returns:
            list: List of startup entry dictionaries
        """
        entries = []
        
        # Get startup folder paths
        try:
            common_startup = os.path.join(
                os.environ['ProgramData'],
                r'Microsoft\Windows\Start Menu\Programs\Startup'
            )
            user_startup = os.path.join(
                os.environ['APPDATA'],
                r'Microsoft\Windows\Start Menu\Programs\Startup'
            )
            
            # Scan common startup folder
            if os.path.exists(common_startup):
                for item in os.listdir(common_startup):
                    full_path = os.path.join(common_startup, item)
                    if os.path.isfile(full_path):
                        entries.append({
                            'name': item,
                            'command': full_path,
                            'location': 'Common Startup Folder',
                            'type': 'Shortcut',
                            'enabled': True  # Folder items are always enabled
                        })
                        
            # Scan user startup folder
            if os.path.exists(user_startup):
                for item in os.listdir(user_startup):
                    full_path = os.path.join(user_startup, item)
                    if os.path.isfile(full_path):
                        entries.append({
                            'name': item,
                            'command': full_path,
                            'location': 'User Startup Folder',
                            'type': 'Shortcut',
                            'enabled': True  # Folder items are always enabled
                        })
                        
        except Exception as e:
            self.logger.error(f"Failed to scan startup folders: {str(e)}")
            
        return entries
        
    def get_service_startups(self) -> List[Dict[str, Any]]:
        """Get automatic startup services.
        
        Returns:
            list: List of startup entry dictionaries
        """
        entries = []
        
        try:
            # Get service control manager
            sc_handle = win32service.OpenSCManager(
                None,
                None,
                win32service.SC_MANAGER_ENUMERATE_SERVICE
            )
            
            try:
                # Enumerate services
                services = win32service.EnumServicesStatus(
                    sc_handle,
                    win32service.SERVICE_WIN32,
                    win32service.SERVICE_STATE_ALL
                )
                
                for svc in services:
                    try:
                        # Get detailed service info
                        svc_handle = win32service.OpenService(
                            sc_handle,
                            svc[0],
                            win32service.SERVICE_QUERY_CONFIG
                        )
                        
                        try:
                            config = win32service.QueryServiceConfig(svc_handle)
                            
                            # Only include automatic startup services
                            if config[1] == win32service.SERVICE_AUTO_START:
                                entries.append({
                                    'name': svc[0],
                                    'command': config[3],  # Binary path
                                    'location': 'Services',
                                    'type': 'Service',
                                    'enabled': True,  # Service is set to auto-start
                                    'display_name': svc[1],
                                    'description': config[7]  # Service description
                                })
                                
                        finally:
                            win32service.CloseServiceHandle(svc_handle)
                            
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to query service {svc[0]}: {str(e)}"
                        )
                        
            finally:
                win32service.CloseServiceHandle(sc_handle)
                
        except Exception as e:
            self.logger.error(f"Failed to enumerate services: {str(e)}")
            
        return entries
        
    def add_registry_startup(self, name: str, command: str, user_specific: bool = True) -> bool:
        """Add a startup entry to the registry.
        
        Args:
            name: Entry name
            command: Command to run
            user_specific: True to add to HKCU, False for HKLM
            
        Returns:
            bool: True if successful
        """
        try:
            # Choose appropriate registry key
            if user_specific:
                root = winreg.HKEY_CURRENT_USER
                path = r'Software\Microsoft\Windows\CurrentVersion\Run'
            else:
                root = winreg.HKEY_LOCAL_MACHINE
                path = r'Software\Microsoft\Windows\CurrentVersion\Run'
                
            # Create/open key
            key = winreg.CreateKey(root, path)
            
            # Set value
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            
            self.logger.info(f"Added startup entry: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add startup entry: {str(e)}")
            return False
            
    def remove_registry_startup(self, name: str, location: str) -> bool:
        """Remove a startup entry from the registry.
        
        Args:
            name: Entry name
            location: Registry location (e.g. 'HKLM_RUN')
            
        Returns:
            bool: True if successful
        """
        try:
            if location not in self.STARTUP_PATHS:
                raise ValueError(f"Invalid location: {location}")
                
            root, path = self.STARTUP_PATHS[location]
            key = winreg.OpenKey(root, path, 0, winreg.KEY_SET_VALUE)
            
            winreg.DeleteValue(key, name)
            winreg.CloseKey(key)
            
            self.logger.info(f"Removed startup entry: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove startup entry: {str(e)}")
            return False
            
    def remove_folder_startup(self, name: str, location: str) -> bool:
        """Remove a startup entry from startup folder.
        
        Args:
            name: Entry name (filename)
            location: Folder location ('Common Startup Folder' or 'User Startup Folder')
            
        Returns:
            bool: True if successful
        """
        try:
            # Get appropriate folder path
            if location == 'Common Startup Folder':
                folder = os.path.join(
                    os.environ['ProgramData'],
                    r'Microsoft\Windows\Start Menu\Programs\Startup'
                )
            elif location == 'User Startup Folder':
                folder = os.path.join(
                    os.environ['APPDATA'],
                    r'Microsoft\Windows\Start Menu\Programs\Startup'
                )
            else:
                raise ValueError(f"Invalid location: {location}")
                
            # Remove file
            path = os.path.join(folder, name)
            if os.path.exists(path):
                os.remove(path)
                self.logger.info(f"Removed startup file: {path}")
                return True
            else:
                self.logger.warning(f"Startup file not found: {path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to remove startup file: {str(e)}")
            return False
