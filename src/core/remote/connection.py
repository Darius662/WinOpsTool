"""Remote connection handling."""
import win32net
import win32wnet
from src.core.logger import setup_logger

class RemoteConnection:
    """Handles remote system connection."""
    
    def __init__(self):
        """Initialize remote connection."""
        self.logger = setup_logger(self.__class__.__name__)
        self.name = None
        self.host = None
        self.username = None
        self._connected = False
        
    def connect(self, host, username, password):
        """Connect to remote system.
        
        Args:
            host: Remote hostname or IP
            username: Username for authentication
            password: Password for authentication
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            # Add backslashes if domain not specified
            if '\\' not in username and '@' not in username:
                username = f'\\{username}'
                
            # Attempt to establish network connection
            win32wnet.WNetAddConnection2(
                win32net.RESOURCETYPE_DISK,
                None,
                f'\\{host}',
                None,
                username,
                password,
                0
            )
            
            self.host = host
            self.username = username
            self._connected = True
            self.logger.info(f"Connected to {host} as {username}")
            
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            raise ConnectionError(f"Failed to connect to {host}: {str(e)}")
            
    def disconnect(self):
        """Disconnect from remote system."""
        if self._connected:
            try:
                win32wnet.WNetCancelConnection2(
                    f'\\{self.host}',
                    0,
                    True
                )
                self.logger.info(f"Disconnected from {self.host}")
            except Exception as e:
                self.logger.error(f"Disconnect error: {str(e)}")
            finally:
                self.name = None
                self.host = None
                self.username = None
                self._connected = False
                
    def is_connected(self):
        """Check if connected to remote system.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self._connected
        
    def get_host(self):
        """Get connected host.
        
        Returns:
            str: Hostname or None if not connected
        """
        return self.host
        
    def get_username(self):
        """Get connected username.
        
        Returns:
            str: Username or None if not connected
        """
        return self.username
