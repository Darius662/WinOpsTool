"""Windows Software management."""
import winreg
import subprocess
import os
from typing import List, Dict, Any, Tuple
from src.core.logger import setup_logger

class SoftwareManager:
    """Manager for Windows installed software."""
    
    # Registry paths for installed software
    UNINSTALL_KEYS = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    
    def __init__(self):
        """Initialize software manager."""
        self.logger = setup_logger(self.__class__.__name__)
        
    def get_installed_software(self, filter_type: str = "All") -> List[Dict[str, str]]:
        """Get list of installed software.
        
        Args:
            filter_type: Filter type ("All", "System", "User")
            
        Returns:
            list: List of software dictionaries with properties
        """
        software = []
        
        for root_key, subkey in self.UNINSTALL_KEYS:
            # Apply filters
            if filter_type == "System" and root_key == winreg.HKEY_CURRENT_USER:
                continue
            if filter_type == "User" and root_key == winreg.HKEY_LOCAL_MACHINE:
                continue
                
            try:
                with winreg.OpenKey(root_key, subkey) as key:
                    index = 0
                    while True:
                        try:
                            app_key = winreg.EnumKey(key, index)
                            with winreg.OpenKey(key, app_key) as app:
                                try:
                                    name = self._get_value(app, "DisplayName")
                                    if not name:  # Skip entries without display name
                                        index += 1
                                        continue
                                        
                                    software.append({
                                        'name': name,
                                        'version': self._get_value(app, "DisplayVersion"),
                                        'publisher': self._get_value(app, "Publisher"),
                                        'install_date': self._get_value(app, "InstallDate"),
                                        'size': self._get_value(app, "EstimatedSize"),
                                        'location': self._get_value(app, "InstallLocation"),
                                        'uninstall_string': self._get_value(app, "UninstallString"),
                                        'modify_path': self._get_value(app, "ModifyPath"),
                                        'windows_installer': self._get_value(app, "WindowsInstaller"),
                                        'registry_key': app_key
                                    })
                                    
                                except WindowsError:
                                    pass
                                    
                            index += 1
                            
                        except WindowsError:
                            break
                            
            except WindowsError as e:
                self.logger.warning(f"Failed to read registry key {subkey}: {str(e)}")
                
        return sorted(software, key=lambda s: s['name'].lower())
        
    def _get_value(self, key, name: str) -> str:
        """Get registry value safely.
        
        Args:
            key: Registry key handle
            name: Value name
            
        Returns:
            str: Value data or empty string if not found
        """
        try:
            value, _ = winreg.QueryValueEx(key, name)
            return str(value)
        except WindowsError:
            return ""
            
    def uninstall_software(self, uninstall_string: str) -> bool:
        """Uninstall software.
        
        Args:
            uninstall_string: Uninstall command string
            
        Returns:
            bool: True if started successfully
        """
        try:
            # Add silent flags if possible
            if uninstall_string.lower().startswith("msiexec"):
                if "/i" in uninstall_string:
                    uninstall_string = uninstall_string.replace("/i", "/x")
                uninstall_string += " /quiet"
            elif "/S" not in uninstall_string.upper():
                uninstall_string += " /S"
                
            subprocess.Popen(uninstall_string, shell=True)
            self.logger.info(f"Started uninstallation: {uninstall_string}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start uninstallation: {str(e)}")
            return False
            
    def repair_software(self, name: str) -> Tuple[bool, str]:
        """Get repair command for software.
        
        Args:
            name: Software name
            
        Returns:
            tuple: (success, repair_string or error message)
        """
        try:
            for root_key, subkey in self.UNINSTALL_KEYS:
                try:
                    with winreg.OpenKey(root_key, subkey) as key:
                        index = 0
                        while True:
                            try:
                                app_key = winreg.EnumKey(key, index)
                                with winreg.OpenKey(key, app_key) as app:
                                    try:
                                        if winreg.QueryValueEx(app, "DisplayName")[0] == name:
                                            # Try ModifyPath first
                                            try:
                                                repair_string = winreg.QueryValueEx(app, "ModifyPath")[0]
                                                return True, repair_string
                                            except WindowsError:
                                                # Try Windows Installer repair
                                                try:
                                                    product_code = winreg.QueryValueEx(app, "WindowsInstaller")[0]
                                                    if product_code:
                                                        repair_string = f"msiexec /f {{{product_code}}}"
                                                        return True, repair_string
                                                except WindowsError:
                                                    pass
                                    except WindowsError:
                                        pass
                                index += 1
                            except WindowsError:
                                break
                except WindowsError:
                    continue
                    
            return False, "Could not find repair information"
            
        except Exception as e:
            self.logger.error(f"Failed to get repair command: {str(e)}")
            return False, str(e)
            
    def install_software(self, file_path: str, silent: bool = True) -> bool:
        """Install software from file.
        
        Args:
            file_path: Path to installer
            silent: Whether to use silent install flags
            
        Returns:
            bool: True if started successfully
        """
        try:
            if not os.path.exists(file_path):
                return False
                
            cmd = file_path
            if silent:
                if file_path.lower().endswith('.msi'):
                    cmd = f'msiexec /i "{file_path}" /quiet'
                else:
                    cmd += ' /S'
                    
            subprocess.Popen(cmd, shell=True)
            self.logger.info(f"Started installation: {cmd}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start installation: {str(e)}")
            return False
