"""Dialog factory for Registry Panel."""
from PyQt6.QtWidgets import QMessageBox
from src.core.logger import setup_logger
from ..dialogs import AddRegistryValueDialog

class DialogFactory:
    """Factory for creating dialogs used in the Registry Panel."""
    
    def __init__(self, panel):
        """Initialize dialog factory.
        
        Args:
            panel: Parent RegistryPanel instance
        """
        self.panel = panel
        self.logger = setup_logger(self.__class__.__name__)
        
    def show_error(self, message):
        """Show error message.
        
        Args:
            message: Error message to display
        """
        QMessageBox.critical(self.panel, "Error", message)
        
    def show_warning(self, message):
        """Show warning message.
        
        Args:
            message: Warning message to display
        """
        QMessageBox.warning(self.panel, "Warning", message)
        
    def show_info(self, message):
        """Show information message.
        
        Args:
            message: Information message to display
        """
        QMessageBox.information(self.panel, "Information", message)
        
    def confirm_delete(self, name, value_type="Value"):
        """Show confirmation dialog for deletion.
        
        Args:
            name: Name of the registry value to delete
            value_type: Type of registry value (default: "Value")
            
        Returns:
            bool: True if user confirmed deletion, False otherwise
        """
        reply = QMessageBox.question(
            self.panel,
            "Confirm Delete",
            f"Are you sure you want to delete the registry {value_type.lower()} '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
        
    def create_add_value_dialog(self, name="", value="", reg_type="REG_SZ"):
        """Create dialog for adding/editing registry values.
        
        Args:
            name: Initial value name (default: "")
            value: Initial value (default: "")
            reg_type: Initial registry type (default: "REG_SZ")
            
        Returns:
            AddRegistryValueDialog: Dialog instance
        """
        return AddRegistryValueDialog(self.panel, name, value, reg_type)
