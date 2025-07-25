"""Windows Package management."""
import winreg
import subprocess
from typing import List, Dict, Any
from src.core.logger import setup_logger

class PackageManager:
    """Manager for Windows installed programs and packages."""
    
    # Registry paths for installed programs
    UNINSTALL_PATHS = [
        (winreg.HKEY_LOCAL_MACHINE, r'Software\Microsoft\Windows\CurrentVersion\Uninstall'),
        (winreg.HKEY_LOCAL_MACHINE, r'Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall'),
        (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Uninstall')
    ]
    
    def __init__(self):
        """Initialize package manager."""
        self.logger = setup_logger(self.__class__.__name__)
        
    def get_installed_programs(self) -> List[Dict[str, Any]]:
        """Get list of installed programs.
        
        Returns:
            list: List of program dictionaries with properties
        """
        programs = []
        max_programs_per_hive = 500  # Limit to prevent excessive loading
        
        for root, path in self.UNINSTALL_PATHS:
            try:
                key = winreg.OpenKey(root, path, 0, winreg.KEY_READ)
                
                try:
                    index = 0
                    hive_programs = 0
                    while hive_programs < max_programs_per_hive:
                        try:
                            # Get subkey name
                            subkey_name = winreg.EnumKey(key, index)
                            
                            try:
                                subkey = winreg.OpenKey(key, subkey_name)
                                
                                try:
                                    # Get program details with timeout protection
                                    name = self._get_value(subkey, 'DisplayName')
                                    if not name or len(name.strip()) == 0:  # Skip entries without display name
                                        continue
                                    
                                    # Skip system components and updates
                                    if any(skip in name.lower() for skip in ['hotfix', 'security update', 'kb', 'microsoft visual c++']):
                                        continue
                                        
                                    # Get other properties
                                    version = self._get_value(subkey, 'DisplayVersion')
                                    publisher = self._get_value(subkey, 'Publisher')
                                    install_date = self._get_value(subkey, 'InstallDate')
                                    install_location = self._get_value(subkey, 'InstallLocation')
                                    uninstall_string = self._get_value(subkey, 'UninstallString')
                                    
                                    programs.append({
                                        'name': name,
                                        'version': version,
                                        'publisher': publisher,
                                        'install_date': install_date,
                                        'install_location': install_location,
                                        'uninstall_string': uninstall_string,
                                        'registry_key': subkey_name
                                    })
                                    
                                    hive_programs += 1
                                    
                                finally:
                                    winreg.CloseKey(subkey)
                                    
                            except WindowsError:
                                # Skip problematic entries
                                pass
                                
                            index += 1
                            
                        except WindowsError:
                            # No more entries
                            break
                            
                finally:
                    winreg.CloseKey(key)
                    
            except WindowsError as e:
                self.logger.debug(f"Failed to read registry key {path}: {str(e)}")
                
        self.logger.info(f"Found {len(programs)} installed programs")
        return sorted(programs, key=lambda p: p['name'].lower())
        
    def _get_value(self, key, name):
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
            
    def uninstall_program(self, uninstall_string: str) -> bool:
        """Uninstall a program.
        
        Args:
            uninstall_string: Program uninstall command
            
        Returns:
            bool: True if successful
        """
        try:
            # Run uninstaller silently if possible
            if '/S' not in uninstall_string.upper():
                uninstall_string += ' /S'
                
            subprocess.run(
                uninstall_string,
                shell=True,
                check=True
            )
            
            self.logger.info(f"Uninstalled program: {uninstall_string}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to uninstall program: {str(e)}")
            return False
            
    def get_winget_packages(self) -> List[Dict[str, Any]]:
        """Get list of available winget packages.
        
        Returns:
            list: List of package dictionaries with properties
        """
        try:
            # Run winget search
            result = subprocess.run(
                ['winget', 'search', '--format', 'json'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse JSON output
            import json
            data = json.loads(result.stdout)
            
            packages = []
            for pkg in data.get('data', []):
                packages.append({
                    'id': pkg.get('Id', ''),
                    'name': pkg.get('Name', ''),
                    'version': pkg.get('Version', ''),
                    'source': pkg.get('Source', ''),
                    'description': pkg.get('Description', '')
                })
                
            return packages
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to get winget packages: {str(e)}")
            return []
            
    def install_winget_package(self, package_id: str) -> bool:
        """Install a winget package.
        
        Args:
            package_id: Package ID
            
        Returns:
            bool: True if successful
        """
        try:
            # Run winget install
            subprocess.run(
                ['winget', 'install', '--id', package_id, '--silent'],
                check=True
            )
            
            self.logger.info(f"Installed winget package: {package_id}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install winget package: {str(e)}")
            return False
