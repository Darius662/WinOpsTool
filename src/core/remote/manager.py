"""Remote management main class."""
from src.core.logger import setup_logger
from .connection import RemoteConnection
from .file_transfer import FileTransfer
from .process import ProcessManager
from .ps_remote_manager import PSRemoteManager, PSRemoteConnection

class RemoteManager:
    """Main class for remote system management using PowerShell Remoting."""
    
    def __init__(self):
        """Initialize remote manager."""
        self.logger = setup_logger(self.__class__.__name__)
        self.ps_remote = PSRemoteManager()
        self.file_transfer = FileTransfer()
        self.process = ProcessManager()
        self.connection = None  # For compatibility with existing code
        
    def connect(self, host, username, password):
        """Connect to remote system using PowerShell Remoting.
        
        Args:
            host: Remote hostname or IP
            username: Username for authentication
            password: Password for authentication
            
        Raises:
            ConnectionError: If connection fails
        """
        # Generate a unique name for this connection
        name = f"{host}_{username}"
        
        # Add the connection if it doesn't exist
        if not self.ps_remote.get_connection(name):
            success = self.ps_remote.add_connection(name, host, username, password)
            if not success:
                raise ConnectionError(f"Failed to connect to {host}")
        
        # Connect to the remote system
        success = self.ps_remote.connect(name)
        if not success:
            raise ConnectionError(f"Failed to connect to {host}")
            
        # Set up the connection for other components
        self.connection = self.ps_remote.connection
        self.file_transfer.set_connection(self.connection)
        self.process.set_connection(self.connection)
        
    def disconnect(self):
        """Disconnect from remote system."""
        self.ps_remote.disconnect()
        self.file_transfer.clear_connection()
        self.process.clear_connection()
        self.connection = None
        
    def is_connected(self):
        """Check if connected to remote system.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.ps_remote.is_connected()
        
    def refresh_connections(self):
        """Refresh the list of saved connections."""
        self.ps_remote.refresh_connections()
        
    def get_connections(self):
        """Get list of saved connections.
        
        Returns:
            list: List of PSRemoteConnection objects
        """
        return self.ps_remote.get_connections()
        
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
        return self.ps_remote.add_connection(name, hostname, username, password)
            
    def remove_connection(self, name):
        """Remove a saved connection.
        
        Args:
            name: Name of connection to remove
            
        Returns:
            bool: True if connection was removed successfully
        """
        return self.ps_remote.remove_connection(name)
        
    def execute_command(self, command):
        """Execute a PowerShell command on the remote system.
        
        Args:
            command: PowerShell command to execute
            
        Returns:
            tuple: (return_code, stdout, stderr)
        """
        return self.ps_remote.execute_command(command)
        
    def execute_script(self, script_content):
        """Execute a PowerShell script on the remote system.
        
        Args:
            script_content: Content of the PowerShell script
            
        Returns:
            tuple: (return_code, stdout, stderr)
        """
        return self.ps_remote.execute_script(script_content)
        
    def copy_file_to_remote(self, local_path, remote_path):
        """Copy a file to the remote system.
        
        Args:
            local_path: Path to the local file
            remote_path: Destination path on the remote system
            
        Returns:
            bool: True if successful
        """
        return self.ps_remote.copy_file_to_remote(local_path, remote_path)
        
    def copy_file_from_remote(self, remote_path, local_path):
        """Copy a file from the remote system.
        
        Args:
            remote_path: Path to the file on the remote system
            local_path: Destination path on the local system
            
        Returns:
            bool: True if successful
        """
        return self.ps_remote.copy_file_from_remote(remote_path, local_path)
