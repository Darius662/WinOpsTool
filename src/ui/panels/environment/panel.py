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
