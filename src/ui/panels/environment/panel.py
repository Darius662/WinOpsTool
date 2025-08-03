"""Environment variables management panel."""
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .manager import EnvironmentManager
from .components import ButtonBar, VariablesView
from .components.dialog_factory import DialogFactory
from .components.variable_operations import VariableOperations

class EnvironmentPanel(BasePanel):
    """Panel for managing environment variables."""
    
    def __init__(self, main_window):
        """Initialize environment panel.
        
        Args:
            main_window: MainWindow instance
        """
        # Initialize component references first
        self.variables_view = None
        self.button_bar = None
        self.dialog_factory = None
        self.variable_ops = None
        
        # Initialize logger and manager
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = EnvironmentManager()
        
        # Initialize remote mode attributes
        self.remote_mode = False
        self.remote_manager = None
        
        # Initialize base class (this will call setup_ui)
        super().__init__(main_window)
        
        # Now that UI is set up, we can connect signals
        self.setup_connections()
        
        # Initialize data
        self.refresh_variables()
        
        # Initialize imported config items
        self.imported_config_items = set()
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Create variables view component with separate trees for user and system variables
        self.variables_view = VariablesView(self)
        self.add_widget(self.variables_view)
        
        # Create button bar component
        self.button_bar = ButtonBar(self)
        self.add_widget(self.button_bar)
        
        # Create helper components
        self.dialog_factory = DialogFactory(self)
        self.variable_ops = VariableOperations(self)
        
        # Update button states
        self.update_button_states()
        
    def setup_connections(self):
        """Set up signal/slot connections."""
        # Make sure variables_view exists before connecting signals
        if self.variables_view:
            self.variables_view.connect_signals()
        
    def update_button_states(self):
        """Update button enabled states based on selection."""
        has_selection = self.variables_view.has_selection()
        self.button_bar.update_button_states(has_selection)
        
    def show_error(self, message):
        """Show error message.
        
        Args:
            message: Error message to display
        """
        self.dialog_factory.show_error(message)
        
    def add_variable(self):
        """Add new environment variable."""
        self.variable_ops.add_variable()
                
    def edit_variable(self):
        """Edit selected environment variable."""
        self.variable_ops.edit_variable()
                
    def delete_variable(self):
        """Delete selected environment variable."""
        self.variable_ops.delete_variable()
                
    def refresh_variables(self):
        """Refresh environment variables list."""
        self.variable_ops.refresh_variables()
        
    def set_remote_mode(self, remote_mode, remote_manager=None):
        """Set remote mode and update data accordingly.
        
        Args:
            remote_mode: True if in remote mode, False for local mode
            remote_manager: RemoteManager instance for remote operations
        """
        self.logger.debug(f"Setting remote mode to {remote_mode}")
        self.logger.debug(f"Remote manager: {remote_manager}")
        if remote_manager:
            self.logger.debug(f"Remote manager is_connected: {remote_manager.is_connected()}")
        
        # Set remote mode and manager
        self.remote_mode = remote_mode
        self.remote_manager = remote_manager
        
        # Clear current data
        self.clear_data()
        
        # Load data for the new mode
        self.load_data()
    
    def load_data(self):
        """Load environment variables data."""
        self.logger.debug(f"Loading data (remote mode: {self.remote_mode})")
        if self.remote_mode and self.remote_manager:
            self.load_remote_data()
        else:
            self.load_local_data()
    
    def clear_data(self):
        """Clear all data in the panel."""
        self.logger.debug("Clearing environment variables data")
        if self.variables_view:
            self.variables_view.clear()
        
    def load_local_data(self):
        """Load environment variables from the local system."""
        self.logger.debug("Loading local environment variables")
        try:
            # Get environment variables from local system
            user_vars_dict = self.manager.get_user_variables()
            system_vars_dict = self.manager.get_system_variables()
            
            # Convert dictionaries to lists of dictionaries with 'name' and 'value' keys
            user_vars = [{'name': name, 'value': value} for name, value in user_vars_dict.items()]
            system_vars = [{'name': name, 'value': value} for name, value in system_vars_dict.items()]
            
            # Update the view
            self.variables_view.update_variables(user_vars, system_vars)
            self.update_button_states()
        except Exception as e:
            self.logger.error(f"Error loading local environment variables: {str(e)}")
            self.show_error(f"Failed to load environment variables: {str(e)}")
    
    def load_remote_data(self):
        """Load environment variables from the remote system."""
        self.logger.debug("Loading remote environment variables")
        if not self.remote_manager:
            self.logger.error("No remote manager available")
            self.show_error("No remote connection available")
            return
            
        # Check if remote manager is connected
        # This works with both RemoteManager and PSRemoteManager
        try:
            if not self.remote_manager.is_connected():
                self.logger.error("Remote manager is not connected")
                self.show_error("No remote connection available")
                return
        except Exception as e:
            self.logger.error(f"Error checking remote connection: {str(e)}")
            self.show_error("Error checking remote connection")
            return
            
        try:
            # Get user variables from remote system
            user_vars = []
            system_vars = []
            
            # Execute PowerShell to get environment variables remotely
            ps_script = """
            $userVars = [Environment]::GetEnvironmentVariables('User') | ConvertTo-Json
            $systemVars = [Environment]::GetEnvironmentVariables('Machine') | ConvertTo-Json
            $result = @{
                'UserVars' = $userVars
                'SystemVars' = $systemVars
            } | ConvertTo-Json
            return $result
            """
            
            result = self.remote_manager.process_manager.execute_powershell(ps_script)
            if result and result.get('success', False):
                import json
                data = json.loads(result.get('output', '{}'))
                
                # Parse user variables
                if 'UserVars' in data:
                    user_vars_dict = json.loads(data['UserVars'])
                    user_vars = [{'name': name, 'value': value} for name, value in user_vars_dict.items()]
                
                # Parse system variables
                if 'SystemVars' in data:
                    system_vars_dict = json.loads(data['SystemVars'])
                    system_vars = [{'name': name, 'value': value} for name, value in system_vars_dict.items()]
                
                # Update the view
                self.variables_view.update_variables(user_vars, system_vars)
                self.update_button_states()
            else:
                error = result.get('error', 'Unknown error') if result else 'No result returned'
                self.logger.error(f"Error getting remote environment variables: {error}")
                self.show_error(f"Failed to get remote environment variables: {error}")
        except Exception as e:
            self.logger.error(f"Error loading remote environment variables: {str(e)}")
            self.show_error(f"Failed to load remote environment variables: {str(e)}")
    
    def save_local_data(self):
        """Save environment variables to the local system."""
        # This is handled by individual operations (add, edit, delete)
        pass
    
    def save_remote_data(self):
        """Save environment variables to the remote system."""
        # This is handled by individual operations (add, edit, delete)
        pass
    
    def apply_remote(self, remote_connection):
        """Apply environment variable changes to a remote system.
        
        Args:
            remote_connection: RemoteConnection instance
            
        Returns:
            bool: True if changes were applied successfully, False otherwise
        """
        self.logger.info(f"Applying environment variables to remote system: {remote_connection.host}")
        
        try:
            # Get current configuration
            config = self.export_config()
            
            # Apply configuration to remote system using PowerShell
            ps_script = """
            param($ConfigJson)
            
            $config = ConvertFrom-Json $ConfigJson
            
            # Apply user variables
            if ($config.environment_variables.user) {
                foreach ($var in $config.environment_variables.user.PSObject.Properties) {
                    [Environment]::SetEnvironmentVariable($var.Name, $var.Value, 'User')
                }
            }
            
            # Apply system variables
            if ($config.environment_variables.system) {
                foreach ($var in $config.environment_variables.system.PSObject.Properties) {
                    [Environment]::SetEnvironmentVariable($var.Name, $var.Value, 'Machine')
                }
            }
            
            return $true
            """
            
            import json
            config_json = json.dumps(config)
            
            result = remote_connection.process_manager.execute_powershell(
                ps_script, 
                parameters=[config_json]
            )
            
            if result and result.get('success', False):
                return True
            else:
                error = result.get('error', 'Unknown error') if result else 'No result returned'
                self.logger.error(f"Error applying environment variables to remote system: {error}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error applying environment variables to remote system: {str(e)}")
            return False
        
    def apply_config(self, config):
        """Apply configuration to the panel.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if configuration was applied successfully, False otherwise
        """
        self.logger.info("Applying environment variables configuration")
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Check if environment variables section exists
            if 'environment_variables' not in config:
                self.logger.warning("No environment variables in configuration")
                return False
                
            env_vars = config['environment_variables']
            
            # Process user variables
            if 'user' in env_vars and isinstance(env_vars['user'], dict):
                for name, value in env_vars['user'].items():
                    self.logger.debug(f"Setting user variable: {name}={value}")
                    success = self.manager.set_user_variable(name, value)
                    if not success:
                        self.logger.warning(f"Failed to set user variable: {name}")
            
            # Process system variables
            if 'system' in env_vars and isinstance(env_vars['system'], dict):
                for name, value in env_vars['system'].items():
                    self.logger.debug(f"Setting system variable: {name}={value}")
                    success = self.manager.set_system_variable(name, value)
                    if not success:
                        self.logger.warning(f"Failed to set system variable: {name}")
            
            # Refresh the view to show updated variables
            self.refresh_variables()
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying environment configuration: {str(e)}")
            return False
            
    def export_config(self):
        """Export panel configuration.
        
        Returns:
            dict: Dictionary containing panel configuration
        """
        self.logger.info("Exporting environment variables configuration")
        
        try:
            # Get current environment variables
            user_vars = self.manager.get_user_variables()
            system_vars = self.manager.get_system_variables()
            
            # Create configuration dictionary
            config = {
                'environment_variables': {
                    'user': {},
                    'system': {}
                }
            }
            
            # Add user variables to configuration
            for var in user_vars:
                config['environment_variables']['user'][var['name']] = var['value']
                
            # Add system variables to configuration
            for var in system_vars:
                config['environment_variables']['system'][var['name']] = var['value']
                
            return config
            
        except Exception as e:
            self.logger.error(f"Error exporting environment configuration: {str(e)}")
            return {}
            
    def mark_config_items(self, config):
        """Mark items from configuration for highlighting without applying changes.
        
        This method identifies and marks environment variables from the configuration
        that would be modified by apply_config(), but does not actually
        apply any changes to the system. Items will be visually highlighted in the UI.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if items were marked successfully, False otherwise
        """
        self.logger.info("Marking environment variables from configuration for highlighting")
        
        # Clear previous imported items
        self.imported_config_items.clear()
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Check if environment variables section exists
            if 'environment_variables' not in config:
                self.logger.warning("No environment variables in configuration")
                return False
                
            env_vars = config['environment_variables']
            
            # Mark user variables
            if 'user' in env_vars and isinstance(env_vars['user'], dict):
                for name, value in env_vars['user'].items():
                    self.mark_as_imported_config(f"user_var:{name}")
                    self.logger.debug(f"Marked user variable: {name}")
            
            # Mark system variables
            if 'system' in env_vars and isinstance(env_vars['system'], dict):
                for name, value in env_vars['system'].items():
                    self.mark_as_imported_config(f"system_var:{name}")
                    self.logger.debug(f"Marked system variable: {name}")
            
            # Add virtual entries for variables that don't exist yet
            self.add_virtual_entries_for_config(env_vars)
            
            # Refresh the view to show highlighted variables
            self.refresh_variables()
            return True
            
        except Exception as e:
            self.logger.error(f"Error marking environment variables from configuration: {str(e)}")
            return False
    
    def add_virtual_entries_for_config(self, env_vars):
        """Add virtual entries for environment variables that don't exist yet.
        
        This method adds visual entries for environment variables that are in the
        configuration but don't exist in the system yet.
        
        Args:
            env_vars: Dictionary containing environment variables configuration
        """
        try:
            # Get current environment variables
            current_user_vars = self.manager.get_user_variables()
            current_system_vars = self.manager.get_system_variables()
            
            # Add virtual entries for user variables
            if 'user' in env_vars and isinstance(env_vars['user'], dict):
                for name, value in env_vars['user'].items():
                    if name not in current_user_vars:
                        # Add virtual entry for user variable
                        self.variables_view.add_virtual_user_variable(name, value)
                        self.logger.debug(f"Added virtual entry for user variable: {name}")
            
            # Add virtual entries for system variables
            if 'system' in env_vars and isinstance(env_vars['system'], dict):
                for name, value in env_vars['system'].items():
                    if name not in current_system_vars:
                        # Add virtual entry for system variable
                        self.variables_view.add_virtual_system_variable(name, value)
                        self.logger.debug(f"Added virtual entry for system variable: {name}")
                        
        except Exception as e:
            self.logger.error(f"Error adding virtual entries for environment variables: {str(e)}")

    def mark_as_imported_config(self, item):
        """Mark an item as imported from configuration.
        
        Args:
            item: Item to mark as imported
        """
        self.imported_config_items.add(item)
