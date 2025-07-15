"""Remote PC Connection Manager."""
import winreg
import win32net
import win32netcon
import win32security
import win32api
from typing import Dict, List, Optional
import socket
from dataclasses import dataclass
from src.core.logger import setup_logger

@dataclass
class RemotePC:
    """Remote PC connection details."""
    name: str
    hostname: str
    username: str
    password: str
    is_connected: bool = False

class RemoteManager:
    """Manages connections to remote PCs."""
    
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)
        self.connections: Dict[str, RemotePC] = {}
        
    def add_connection(self, name: str, hostname: str, username: str, password: str) -> bool:
        """Add a new remote PC connection."""
        try:
            # Test connection
            handle = win32net.NetUseAdd(None, 2, {
                'remote': f'\\\\{hostname}\\IPC$',
                'username': username,
                'password': password
            })
            
            # If connection successful, store it
            self.connections[name] = RemotePC(
                name=name,
                hostname=hostname,
                username=username,
                password=password,
                is_connected=True
            )
            
            self.logger.info(f"Successfully connected to remote PC: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to remote PC {name}: {str(e)}")
            return False
            
    def remove_connection(self, name: str) -> bool:
        """Remove a remote PC connection."""
        try:
            if name in self.connections:
                pc = self.connections[name]
                win32net.NetUseDel(None, f'\\\\{pc.hostname}\\IPC$')
                del self.connections[name]
                self.logger.info(f"Removed connection to remote PC: {name}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove connection to remote PC {name}: {str(e)}")
            return False
            
    def get_connections(self) -> List[RemotePC]:
        """Get list of all connections."""
        return list(self.connections.values())
        
    def get_connection(self, name: str) -> Optional[RemotePC]:
        """Get a specific connection by name."""
        return self.connections.get(name)
        
    def test_connection(self, name: str) -> bool:
        """Test if a connection is still active."""
        try:
            if name not in self.connections:
                return False
                
            pc = self.connections[name]
            socket.create_connection((pc.hostname, 445), timeout=2)
            return True
            
        except Exception:
            return False
            
    def refresh_connections(self):
        """Refresh all connections and update their status."""
        for name, pc in list(self.connections.items()):
            if not self.test_connection(name):
                pc.is_connected = False
                try:
                    # Try to reconnect
                    handle = win32net.NetUseAdd(None, 2, {
                        'remote': f'\\\\{pc.hostname}\\IPC$',
                        'username': pc.username,
                        'password': pc.password
                    })
                    pc.is_connected = True
                except:
                    self.logger.warning(f"Lost connection to remote PC: {name}")
                    
    def execute_on_all(self, func, *args, **kwargs):
        """Execute a function on all connected PCs."""
        results = {}
        for name, pc in self.connections.items():
            if pc.is_connected:
                try:
                    results[name] = func(pc, *args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Failed to execute on {name}: {str(e)}")
                    results[name] = None
        return results
