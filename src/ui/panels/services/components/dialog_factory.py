"""Dialog factory for Services Panel."""
from PyQt6.QtWidgets import QMessageBox
from src.core.logger import setup_logger
from ..dialogs import StartupTypeDialog, EditServiceDialog

class DialogFactory:
    """Factory for creating dialogs used in the Services Panel."""
    
    def __init__(self, panel):
        """Initialize dialog factory.
        
        Args:
            panel: Parent ServicesPanel instance
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
        
    def confirm_action(self, title, message):
        """Show confirmation dialog for an action.
        
        Args:
            title: Dialog title
            message: Confirmation message to display
            
        Returns:
            bool: True if user confirmed action, False otherwise
        """
        reply = QMessageBox.question(
            self.panel,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
        
    def create_startup_type_dialog(self, current_type):
        """Create a dialog for changing service startup type.
        
        Args:
            current_type: Current startup type
            
        Returns:
            StartupTypeDialog: Dialog for changing startup type
        """
        return StartupTypeDialog(self.panel, current_type)
        
    def create_edit_service_dialog(self, service):
        """Create a dialog for editing service properties.
        
        Args:
            service: Service data dictionary
            
        Returns:
            EditServiceDialog: Dialog for editing service properties
        """
        return EditServiceDialog(self.panel, service)
