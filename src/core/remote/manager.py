"""Remote management main class."""
from src.core.logger import setup_logger
from .connection import RemoteConnection
from .file_transfer import FileTransfer
from .process import ProcessManager
from .wmi import WmiManager

class RemoteManager:
    """Main class for remote system management."""
    
    def __init__(self):
        """Initialize remote manager."""
        self.logger = setup_logger(self.__class__.__name__)
        self.connection = RemoteConnection()
        self.file_transfer = FileTransfer()
        self.process = ProcessManager()
        self.wmi = WmiManager()
        
    def connect(self, host, username, password):
        """Connect to remote system.
        
        Args:
            host: Remote hostname or IP
            username: Username for authentication
            password: Password for authentication
            
        Raises:
            ConnectionError: If connection fails
        """
        self.connection.connect(host, username, password)
        self.file_transfer.set_connection(self.connection)
        self.process.set_connection(self.connection)
        self.wmi.set_connection(self.connection)
        
    def disconnect(self):
        """Disconnect from remote system."""
        self.connection.disconnect()
        self.file_transfer.clear_connection()
        self.process.clear_connection()
        self.wmi.clear_connection()
        
    def is_connected(self):
        """Check if connected to remote system.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.connection.is_connected()
