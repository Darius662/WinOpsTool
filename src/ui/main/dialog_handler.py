"""Dialog management for main window."""
import yaml
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from src.core.logger import setup_logger
from src.ui.dialogs.connection_dialog import ConnectionDialog

logger = setup_logger(__name__)

class DialogHandler:
    """Manages dialogs for the main window."""
    
    def __init__(self, parent):
        """Initialize dialog handler.
        
        Args:
            parent: Parent window
        """
        self.logger = logger
        self.parent = parent
        
    def show_connections(self):
        """Show the connections management dialog."""
        dialog = ConnectionDialog(self.parent.remote_handler, self.parent)
        dialog.exec()
        
    def show_file_transfer(self):
        """Show the file transfer dialog."""
        if self.parent.remote_handler.is_connected():
            from src.ui.dialogs.file_transfer_dialog import FileTransferDialog
            dialog = FileTransferDialog(self.parent.remote_handler, self.parent)
            dialog.exec()
            
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self.parent,
            "About System Management Tool",
            """<h3>Windows System Management Tool</h3>
            <p>Version 1.0</p>
            <p>A powerful tool for managing Windows systems locally and remotely.</p>
            <p>Part of the Windows System Management Suite.</p>"""
        )
        
    def confirm_apply_all(self, panel_name, pc_count):
        """Show confirmation dialog for applying to all PCs.
        
        Args:
            panel_name: Name of panel being applied
            pc_count: Number of connected PCs
            
        Returns:
            bool: True if user confirmed, False otherwise
        """
        reply = QMessageBox.question(
            self.parent,
            "Confirm Apply",
            f"Are you sure you want to apply {panel_name} changes to {pc_count} connected PCs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
        
    def show_apply_results(self, success_count, fail_count):
        """Show results of applying changes to multiple PCs.
        
        Args:
            success_count: Number of successful applications
            fail_count: Number of failed applications
        """
        QMessageBox.information(
            self.parent,
            "Apply Complete",
            f"Changes applied to {success_count} PCs\nFailed on {fail_count} PCs"
        )
        
    def show_error(self, title, message):
        """Show error dialog.
        
        Args:
            title: Dialog title
            message: Error message
        """
        QMessageBox.critical(self.parent, title, message)
        
    def get_open_filename(self, title, filter_str):
        """Show file open dialog.
        
        Args:
            title: Dialog title
            filter_str: File type filter string
            
        Returns:
            str: Selected filename or empty string
        """
        filename, _ = QFileDialog.getOpenFileName(
            self.parent,
            title,
            "",
            filter_str
        )
        return filename
        
    def import_configuration(self):
        """Import and apply configuration from a YAML file."""
        filename = self.get_open_filename(
            "Import Configuration",
            "YAML files (*.yaml *.yml);;All files (*.*)"
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'r') as f:
                config = yaml.safe_load(f)
                
            if not isinstance(config, dict):
                raise ValueError("Invalid configuration format")
                
            # Apply configuration to current panel
            current_panel = self.parent.panel_manager.get_current_panel()
            if not current_panel:
                return
                
            panel_name = self.parent.panel_manager.get_current_panel_name()
            
            if hasattr(current_panel, 'apply_config'):
                current_panel.apply_config(config)
                self.logger.info(f"Configuration imported for {panel_name}")
            else:
                self.logger.warning(f"Panel {panel_name} does not support configuration import")
                self.show_error(
                    "Warning",
                    f"The {panel_name} panel does not support configuration import"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {str(e)}")
            self.show_error(
                "Error",
                f"Failed to import configuration: {str(e)}"
            )
