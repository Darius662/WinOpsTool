"""Windows Applications management."""
import os
import psutil
import winreg
import win32api
import win32con
import win32process
import win32security
import win32com.client
from datetime import datetime
from typing import List, Dict, Any
from src.core.logger import setup_logger

class ProcessManager:
    """Manager for Windows processes."""
    
    def __init__(self):
        """Initialize process manager."""
        self.logger = setup_logger(self.__class__.__name__)
        
    def get_processes(self) -> List[Dict[str, Any]]:
        """Get list of running processes.
        
        Returns:
            list: List of process dictionaries with properties
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent',
                                     'memory_info', 'create_time', 'username']):
            try:
                info = proc.info
                processes.append({
                    'name': info['name'],
                    'pid': info['pid'],
                    'status': info['status'],
                    'cpu_percent': info['cpu_percent'],
                    'memory': info['memory_info'].rss,
                    'username': info['username'] or "N/A",
                    'create_time': datetime.fromtimestamp(info['create_time'])
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        return sorted(processes, key=lambda p: p['name'].lower())
        
    def end_process(self, pid: int) -> bool:
        """End a process.
        
        Args:
            pid: Process ID
            
        Returns:
            bool: True if successful
        """
        try:
            process = psutil.Process(pid)
            process.terminate()
            self.logger.info(f"Terminated process {pid}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to terminate process {pid}: {str(e)}")
            return False
            
    def end_process_tree(self, pid: int) -> bool:
        """End a process and all its children.
        
        Args:
            pid: Process ID
            
        Returns:
            bool: True if successful
        """
        try:
            process = psutil.Process(pid)
            process.terminate()
            for child in process.children(recursive=True):
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass
            self.logger.info(f"Terminated process tree {pid}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to terminate process tree {pid}: {str(e)}")
            return False

class StartupManager:
    """Manager for Windows startup applications."""
    
    # Registry paths for startup items
    STARTUP_LOCATIONS = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce")
    ]
    
    def __init__(self):
        """Initialize startup manager."""
        self.logger = setup_logger(self.__class__.__name__)
        
    def get_startup_items(self) -> List[Dict[str, str]]:
        """Get list of startup items.
        
        Returns:
            list: List of startup item dictionaries with properties
        """
        items = []
        
        # Check registry locations
        for root_key, subkey in self.STARTUP_LOCATIONS:
            try:
                with winreg.OpenKey(root_key, subkey) as key:
                    index = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, index)
                            items.append({
                                'name': name,
                                'command': value,
                                'location': "HKLM" if root_key == winreg.HKEY_LOCAL_MACHINE else "HKCU",
                                'type': "RunOnce" if "RunOnce" in subkey else "Run"
                            })
                            index += 1
                        except WindowsError:
                            break
            except WindowsError:
                continue
                
        # Check startup folders
        for env_var, location in [
            ("APPDATA", "Current User"),
            ("PROGRAMDATA", "All Users")
        ]:
            try:
                startup_folder = os.path.join(
                    os.environ[env_var],
                    r"Microsoft\Windows\Start Menu\Programs\Startup"
                )
                if os.path.exists(startup_folder):
                    for item in os.listdir(startup_folder):
                        path = os.path.join(startup_folder, item)
                        if os.path.isfile(path):
                            items.append({
                                'name': os.path.splitext(item)[0],
                                'command': path,
                                'location': location,
                                'type': "Startup Folder"
                            })
            except Exception as e:
                self.logger.warning(f"Failed to read startup folder {startup_folder}: {str(e)}")
                
        return sorted(items, key=lambda i: i['name'].lower())
        
    def add_startup_item(self, name: str, file_path: str, location: str) -> bool:
        """Add a startup item.
        
        Args:
            name: Item name
            file_path: Path to executable
            location: "Current User" or "All Users"
            
        Returns:
            bool: True if successful
        """
        try:
            if not os.path.exists(file_path):
                return False
                
            # Add to registry
            root_key = winreg.HKEY_CURRENT_USER if "Current User" in location else winreg.HKEY_LOCAL_MACHINE
            with winreg.OpenKey(root_key, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, f'"{file_path}"')
                
            self.logger.info(f"Added startup item: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add startup item: {str(e)}")
            return False
            
    def remove_startup_item(self, name: str, location: str, item_type: str) -> bool:
        """Remove a startup item.
        
        Args:
            name: Item name
            location: Registry hive or folder location
            item_type: "Run", "RunOnce", or "Startup Folder"
            
        Returns:
            bool: True if successful
        """
        try:
            if item_type == "Startup Folder":
                startup_folder = os.path.join(
                    os.environ["APPDATA" if location == "Current User" else "PROGRAMDATA"],
                    r"Microsoft\Windows\Start Menu\Programs\Startup"
                )
                path = os.path.join(startup_folder, f"{name}.lnk")
                if os.path.exists(path):
                    os.remove(path)
            else:
                root_key = winreg.HKEY_LOCAL_MACHINE if location == "HKLM" else winreg.HKEY_CURRENT_USER
                key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
                if item_type == "RunOnce":
                    key_path += "Once"
                    
                with winreg.OpenKey(root_key, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, name)
                    
            self.logger.info(f"Removed startup item: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove startup item: {str(e)}")
            return False
