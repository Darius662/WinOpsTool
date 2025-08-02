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
            "About WinOpsTool",
            """<h3>WinOpsTool</h3>
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
        """Import configuration from a YAML file without applying changes.
        
        This method loads the configuration from a YAML file and updates the UI
        to show what would be changed, but does not apply the changes to the system.
        The changes will only be applied when the user selects "Apply Config" from the menu.
        """
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
                
            # Store the configuration in the main window
            self.parent.set_config(config)
            
            self.logger.info(f"Configuration imported from {filename}")
            QMessageBox.information(
                self.parent,
                "Configuration Imported",
                f"Configuration has been imported from {filename}.\n\n"
                "Items that would be changed are now highlighted in each panel.\n"
                "To apply these changes, select 'Apply Config' from the File menu."
            )
                
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {str(e)}")
            self.show_error(
                "Error",
                f"Failed to import configuration: {str(e)}"
            )
            
    def export_configuration(self):
        """Export configuration to a YAML file."""
        filename, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Export Configuration",
            "",
            "YAML files (*.yaml);;All files (*.*)"
        )
        
        if not filename:
            return
            
        try:
            # Get configuration from all panels
            config = {}
            
            for panel_name, panel in self.parent.panel_manager.panels.items():
                if hasattr(panel, 'export_config'):
                    panel_config = panel.export_config()
                    if panel_config:
                        # Map panel names to config sections
                        if "Environment Variables" in panel_name:
                            config["environment_variables"] = panel_config.get("environment_variables", {})
                        elif "Registry Editor" in panel_name:
                            config["registry"] = panel_config.get("registry", {})
                        elif "Users & Groups" in panel_name:
                            config["users"] = panel_config.get("users", {})
                        elif "Services" in panel_name:
                            config["services"] = panel_config.get("services", {})
                        elif "Firewall" in panel_name:
                            config["firewall"] = panel_config.get("firewall_rules", {})
                        elif "Software" in panel_name:
                            config["software"] = panel_config.get("software", {})
                        elif "Permissions" in panel_name:
                            config["permissions"] = panel_config.get("permissions", {})
                        elif "Applications" in panel_name:
                            config["applications"] = panel_config.get("applications", {})
                        elif "Packages" in panel_name:
                            config["packages"] = panel_config.get("software", {})
            
            # Write configuration to file
            with open(filename, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
            self.logger.info(f"Configuration exported to {filename}")
            QMessageBox.information(
                self.parent,
                "Configuration Exported",
                f"Configuration has been exported to {filename}"
            )
                
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {str(e)}")
            self.show_error(
                "Error",
                f"Failed to export configuration: {str(e)}"
            )
            
    def confirm_action(self, title, message):
        """Show confirmation dialog for an action.
        
        Args:
            title: Dialog title
            message: Confirmation message
            
        Returns:
            bool: True if user confirmed, False otherwise
        """
        reply = QMessageBox.question(
            self.parent,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
        
    def show_info(self, title, message):
        """Show information dialog.
        
        Args:
            title: Dialog title
            message: Information message
        """
        QMessageBox.information(self.parent, title, message)
        
    def show_warning(self, title, message):
        """Show warning dialog.
        
        Args:
            title: Dialog title
            message: Warning message
        """
        QMessageBox.warning(self.parent, title, message)
