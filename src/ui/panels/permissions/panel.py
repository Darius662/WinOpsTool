"""Windows Permissions management panel."""
from PyQt6.QtWidgets import QMessageBox
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .manager import PermissionsManager
from .components.permissions_list import PermissionsList
from .dialogs import PermissionDialog

class PermissionsPanel(BasePanel):
    """Panel for managing file and folder permissions."""
    
    def __init__(self, parent=None):
        """Initialize permissions panel.
        
        Args:
            parent: Parent widget
        """
        # Initialize manager before calling super().__init__ which will call setup_ui
        self.manager = PermissionsManager()
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
    def setup_ui(self):
        """Initialize the UI components."""
        # Create permissions list component
        self.permissions_list = PermissionsList()
        self.add_widget(self.permissions_list)
        
        # Initialize current path
        self.current_path = None
        
    def update_buttons(self):
        """Update button enabled states based on selection."""
        # This is now handled by the PermissionsList component
        pass
        
    def browse_path(self):
        """Browse for a file or folder."""
        # This is now handled by the PermissionsList component
        pass
            
    def path_changed(self, path):
        """Handle path change.
        
        Args:
            path: New path
        """
        self.current_path = path
        self.refresh_permissions()
        
    def refresh_permissions(self):
        """Refresh the permissions list."""
        try:
            if not self.current_path:
                return
                
            # Add path to combo history
            self.permissions_list.add_path_to_history(self.current_path)
                
            # Get permissions from manager
            permissions = self.manager.get_permissions(self.current_path)
            
            # Update permissions list component
            self.permissions_list.add_permissions(permissions)
                
            self.logger.info(f"Refreshed permissions for {self.current_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh permissions: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to refresh permissions list")
            
    def add_permission(self, path):
        """Add a new permission.
        
        Args:
            path: Current path
        """
        try:
            if not path:
                return
                
            dialog = PermissionDialog(self)
            if dialog.exec() == PermissionDialog.DialogCode.Accepted:
                data = dialog.get_permission_data()
                
                if self.manager.add_permission(
                    path,
                    data["name"],
                    data["mask"]
                ):
                    self.refresh_permissions()
                else:
                    QMessageBox.critical(self, "Error", "Failed to add permission")
                    
        except Exception as e:
            self.logger.error(f"Failed to add permission: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add permission: {str(e)}")
            
    def edit_permission(self, path):
        """Edit selected permission.
        
        Args:
            path: Current path
        """
        try:
            if not path:
                return
                
            # Get selected permission from component
            name = self.permissions_list.get_selected_permission()
            if not name:
                return
                
            # Get current permissions
            permissions = self.manager.get_permissions(path)
            current_perm = next((p for p in permissions if p['name'] == name), None)
            if not current_perm:
                return
                
            dialog = PermissionDialog(self, name, current_perm['mask'])
            if dialog.exec() == PermissionDialog.DialogCode.Accepted:
                data = dialog.get_permission_data()
                
                if self.manager.edit_permission(
                    path,
                    data["name"],
                    data["mask"]
                ):
                    self.refresh_permissions()
                else:
                    QMessageBox.critical(self, "Error", "Failed to edit permission")
                    
        except Exception as e:
            self.logger.error(f"Failed to edit permission: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to edit permission: {str(e)}")
            
    def remove_permission(self, path):
        """Remove selected permission.
        
        Args:
            path: Current path
        """
        try:
            if not path:
                return
                
            # Get selected permission from component
            name = self.permissions_list.get_selected_permission()
            if not name:
                return
                
            reply = QMessageBox.question(
                self,
                "Confirm Remove",
                f"Are you sure you want to remove permissions for '{name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.manager.remove_permission(path, name):
                    self.refresh_permissions()
                else:
                    QMessageBox.critical(self, "Error", f"Failed to remove permission for {name}")
                    
        except Exception as e:
            self.logger.error(f"Failed to remove permission: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to remove permission: {str(e)}")
            
    def setup_connections(self):
        """Set up signal/slot connections."""
        # Connect permissions list signals
        self.permissions_list.path_changed.connect(self.path_changed)
        self.permissions_list.add_permission.connect(self.add_permission)
        self.permissions_list.edit_permission.connect(self.edit_permission)
        self.permissions_list.remove_permission.connect(self.remove_permission)
        self.permissions_list.refresh_permissions.connect(self.refresh_permissions)
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed."""
        pass  # No cleanup needed for this panel
