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
        
    def update_remote_state(self, connected):
        """Update UI based on remote connection state.
        
        Args:
            connected: True if connected to remote system, False otherwise
        """
        # Enable/disable controls based on connection state
        self.setEnabled(not connected)  # Disable local env vars when remote
        
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
            current_user_vars = {var['name']: var for var in self.manager.get_user_variables()}
            current_system_vars = {var['name']: var for var in self.manager.get_system_variables()}
            
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
