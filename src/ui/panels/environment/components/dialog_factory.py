"""Dialog factory for environment panel."""
from PyQt6.QtWidgets import QMessageBox
from src.core.logger import setup_logger
from ..dialogs import AddVariableDialog

class DialogFactory:
    """Factory for creating and managing dialogs in the environment panel."""
    
    def __init__(self, panel):
        """Initialize dialog factory.
        
        Args:
            panel: Parent panel (EnvironmentPanel)
        """
        self.panel = panel
        self.logger = setup_logger(self.__class__.__name__)
        
    def create_add_dialog(self, name=None, value=None, var_type=None):
        """Create a dialog for adding or editing a variable.
        
        Args:
            name: Variable name for editing (None for new variable)
            value: Variable value for editing (None for new variable)
            var_type: Variable type for editing (None for new variable)
            
        Returns:
            AddVariableDialog instance
        """
        return AddVariableDialog(self.panel, name, value, var_type)
        
    def show_error(self, message):
        """Show error message.
        
        Args:
            message: Error message to display
            
        Returns:
            QMessageBox.StandardButton value
        """
        return QMessageBox.critical(self.panel, "Error", message)
        
    def show_warning(self, title, message):
        """Show warning message.
        
        Args:
            title: Warning title
            message: Warning message to display
            
        Returns:
            QMessageBox.StandardButton value
        """
        return QMessageBox.warning(self.panel, title, message)
        
    def confirm_delete(self, var_type, name):
        """Show confirmation dialog for deletion.
        
        Args:
            var_type: Variable type (User or System)
            name: Variable name
            
        Returns:
            True if user confirmed deletion, False otherwise
        """
        reply = QMessageBox.question(
            self.panel,
            "Confirm Delete",
            f"Are you sure you want to delete {var_type} variable '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
