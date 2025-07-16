"""Remote connection management."""
from src.core.logger import setup_logger
from .connection import RemoteConnection

logger = setup_logger(__name__)

class ConnectionManager:
    """Manages saved remote connections."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.logger = setup_logger(self.__class__.__name__)
        self.connections = []
        self.active_connection = None
        
    def refresh_connections(self):
        """Refresh the list of saved connections."""
        # For now, just ensure connection state is updated
        pass
        
    def get_connections(self):
        """Get list of saved connections.
        
        Returns:
            list: List of RemoteConnection objects
        """
        # For now, just return current connection if connected
        if self.active_connection and self.active_connection.is_connected():
            return [self.active_connection]
        return []
        
    def add_connection(self, name, hostname, username, password):
        """Add a new remote connection.
        
        Args:
            name: Display name for the connection
            hostname: Remote hostname or IP
            username: Username for authentication
            password: Password for authentication
            
        Returns:
            bool: True if connection was added successfully
        """
        try:
            connection = RemoteConnection()
            connection.connect(hostname, username, password)
            connection.name = name
            self.active_connection = connection
            return True
        except Exception as e:
            self.logger.error(f"Failed to add connection: {str(e)}")
            return False
            
    def remove_connection(self, name):
        """Remove a saved connection.
        
        Args:
            name: Name of connection to remove
            
        Returns:
            bool: True if connection was removed successfully
        """
        if (self.active_connection and 
            self.active_connection.is_connected() and 
            self.active_connection.name == name):
            self.active_connection.disconnect()
            self.active_connection = None
        return True
