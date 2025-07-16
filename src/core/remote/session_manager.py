"""Remote session management."""
from src.core.logger import setup_logger
from .file_transfer import FileTransfer
from .process import ProcessManager
from .wmi import WmiManager
from .connection_manager import ConnectionManager

logger = setup_logger(__name__)

class SessionManager:
    """Manages active remote sessions and services."""
    
    def __init__(self):
        """Initialize session manager."""
        self.logger = setup_logger(self.__class__.__name__)
        self.connection_manager = ConnectionManager()
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
        # Add connection through connection manager
        if not self.connection_manager.add_connection("Active Session", host, username, password):
            raise ConnectionError("Failed to establish connection")
            
        # Initialize services with active connection
        active_conn = self.connection_manager.active_connection
        self.file_transfer.set_connection(active_conn)
        self.process.set_connection(active_conn)
        self.wmi.set_connection(active_conn)
        
    def disconnect(self):
        """Disconnect from remote system."""
        if self.connection_manager.active_connection:
            self.connection_manager.remove_connection(
                self.connection_manager.active_connection.name
            )
        self.file_transfer.clear_connection()
        self.process.clear_connection()
        self.wmi.clear_connection()
        
    def is_connected(self):
        """Check if connected to remote system.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return (self.connection_manager.active_connection and 
                self.connection_manager.active_connection.is_connected())
