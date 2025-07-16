"""Windows Management Instrumentation (WMI) operations."""
import wmi
from src.core.logger import setup_logger

class WmiManager:
    """Handles WMI operations on remote system."""
    
    def __init__(self):
        """Initialize WMI manager."""
        self.logger = setup_logger(self.__class__.__name__)
        self.connection = None
        self.wmi_connection = None
        
    def set_connection(self, connection):
        """Set remote connection.
        
        Args:
            connection: RemoteConnection instance
        """
        self.connection = connection
        self._connect_wmi()
        
    def clear_connection(self):
        """Clear remote connection."""
        self.connection = None
        self.wmi_connection = None
        
    def _connect_wmi(self):
        """Establish WMI connection to remote system.
        
        Raises:
            ConnectionError: If WMI connection fails
        """
        if not self.connection or not self.connection.is_connected():
            raise ConnectionError("Not connected to remote system")
            
        try:
            self.wmi_connection = wmi.WMI(
                self.connection.get_host(),
                user=self.connection.get_username()
            )
            self.logger.info("WMI connection established")
            
        except Exception as e:
            self.logger.error(f"WMI connection failed: {str(e)}")
            raise ConnectionError(f"WMI connection failed: {str(e)}")
            
    def query(self, wql):
        """Execute WMI query.
        
        Args:
            wql: WMI Query Language string
            
        Returns:
            list: Query results
            
        Raises:
            ConnectionError: If not connected
            RuntimeError: If query fails
        """
        if not self.wmi_connection:
            raise ConnectionError("WMI not connected")
            
        try:
            return self.wmi_connection.query(wql)
            
        except Exception as e:
            self.logger.error(f"WMI query failed: {str(e)}")
            raise RuntimeError(f"WMI query failed: {str(e)}")
            
    def get_service(self, name):
        """Get service by name.
        
        Args:
            name: Service name
            
        Returns:
            object: Service object or None if not found
            
        Raises:
            ConnectionError: If not connected
        """
        if not self.wmi_connection:
            raise ConnectionError("WMI not connected")
            
        try:
            services = self.wmi_connection.Win32_Service(Name=name)
            return services[0] if services else None
            
        except Exception as e:
            self.logger.error(f"Failed to get service: {str(e)}")
            return None
            
    def list_services(self):
        """List all services.
        
        Returns:
            list: Service objects
            
        Raises:
            ConnectionError: If not connected
        """
        if not self.wmi_connection:
            raise ConnectionError("WMI not connected")
            
        try:
            return self.wmi_connection.Win32_Service()
            
        except Exception as e:
            self.logger.error(f"Failed to list services: {str(e)}")
            return []
            
    def get_startup_command(self, name):
        """Get startup command by name.
        
        Args:
            name: Command name
            
        Returns:
            object: Startup command object or None if not found
            
        Raises:
            ConnectionError: If not connected
        """
        if not self.wmi_connection:
            raise ConnectionError("WMI not connected")
            
        try:
            commands = self.wmi_connection.Win32_StartupCommand(Name=name)
            return commands[0] if commands else None
            
        except Exception as e:
            self.logger.error(f"Failed to get startup command: {str(e)}")
            return None
            
    def list_startup_commands(self):
        """List all startup commands.
        
        Returns:
            list: Startup command objects
            
        Raises:
            ConnectionError: If not connected
        """
        if not self.wmi_connection:
            raise ConnectionError("WMI not connected")
            
        try:
            return self.wmi_connection.Win32_StartupCommand()
            
        except Exception as e:
            self.logger.error(f"Failed to list startup commands: {str(e)}")
            return []
