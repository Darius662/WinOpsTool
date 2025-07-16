"""Windows Permissions management panel."""
from PyQt6.QtWidgets import (QHBoxLayout, QPushButton, QMessageBox, QComboBox,
                          QFileDialog)
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import PermissionsTree
from .manager import PermissionsManager
from .dialogs import PermissionDialog

class PermissionsPanel(BasePanel):
    """Panel for managing file and folder permissions."""
    
    def __init__(self, parent=None):
        """Initialize permissions panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = PermissionsManager()
        self.current_path = None
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI components."""
        # Path selection
        self.path_combo = QComboBox()
        self.path_combo.setEditable(True)
        self.path_combo.setMaxCount(10)
        self.path_combo.currentTextChanged.connect(self.path_changed)
        self.add_widget(self.path_combo)
        
        # Browse button
        browse_layout = QHBoxLayout()
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_path)
        browse_layout.addWidget(self.browse_btn)
        self.add_layout(browse_layout)
        
        # Permissions tree
        self.permissions_tree = PermissionsTree()
        self.add_widget(self.permissions_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Permission")
        self.edit_btn = QPushButton("Edit Permission")
        self.remove_btn = QPushButton("Remove Permission")
        self.refresh_btn = QPushButton("Refresh")
        
        for btn in [self.add_btn, self.edit_btn, self.remove_btn, self.refresh_btn]:
            button_layout.addWidget(btn)
            
        self.add_layout(button_layout)
        
        # Connect signals
        self.add_btn.clicked.connect(self.add_permission)
        self.edit_btn.clicked.connect(self.edit_permission)
        self.remove_btn.clicked.connect(self.remove_permission)
        self.refresh_btn.clicked.connect(self.refresh_permissions)
        self.permissions_tree.itemSelectionChanged.connect(self.update_buttons)
        
        # Initial button state
        self.update_buttons()
        
    def update_buttons(self):
        """Update button enabled states based on selection."""
        has_path = bool(self.current_path)
        has_selection = bool(self.permissions_tree.selectedItems())
        
        self.add_btn.setEnabled(has_path)
        self.edit_btn.setEnabled(has_path and has_selection)
        self.remove_btn.setEnabled(has_path and has_selection)
        self.refresh_btn.setEnabled(has_path)
        
    def browse_path(self):
        """Browse for a file or folder."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            self.current_path or ""
        )
        
        if path:
            self.path_combo.setCurrentText(path)
            
    def path_changed(self, path):
        """Handle path change.
        
        Args:
            path: New path
        """
        self.current_path = path
        self.refresh_permissions()
        self.update_buttons()
        
    def refresh_permissions(self):
        """Refresh the permissions list."""
        try:
            if not self.current_path:
                self.permissions_tree.clear_permissions()
                return
                
            # Add path to combo if not present
            if self.path_combo.findText(self.current_path) == -1:
                self.path_combo.addItem(self.current_path)
                
            # Clear and repopulate tree
            self.permissions_tree.clear_permissions()
            permissions = self.manager.get_permissions(self.current_path)
            
            for perm in permissions:
                self.permissions_tree.add_permission(
                    perm['name'],
                    perm['type'],
                    perm['permissions']
                )
                
            self.logger.info(f"Refreshed permissions for {self.current_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh permissions: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to refresh permissions list")
            
    def add_permission(self):
        """Add a new permission."""
        try:
            if not self.current_path:
                return
                
            dialog = PermissionDialog(self)
            if dialog.exec() == PermissionDialog.DialogCode.Accepted:
                data = dialog.get_permission_data()
                
                if self.manager.add_permission(
                    self.current_path,
                    data["name"],
                    data["mask"]
                ):
                    self.refresh_permissions()
                else:
                    QMessageBox.critical(self, "Error", "Failed to add permission")
                    
        except Exception as e:
            self.logger.error(f"Failed to add permission: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add permission: {str(e)}")
            
    def edit_permission(self):
        """Edit selected permission."""
        try:
            current_item = self.permissions_tree.currentItem()
            if not current_item or not self.current_path:
                return
                
            name = current_item.text(0)
            
            # Get current permissions
            permissions = self.manager.get_permissions(self.current_path)
            current_perm = next((p for p in permissions if p['name'] == name), None)
            if not current_perm:
                return
                
            dialog = PermissionDialog(self, name, current_perm['mask'])
            if dialog.exec() == PermissionDialog.DialogCode.Accepted:
                data = dialog.get_permission_data()
                
                if self.manager.edit_permission(
                    self.current_path,
                    data["name"],
                    data["mask"]
                ):
                    self.refresh_permissions()
                else:
                    QMessageBox.critical(self, "Error", "Failed to edit permission")
                    
        except Exception as e:
            self.logger.error(f"Failed to edit permission: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to edit permission: {str(e)}")
            
    def remove_permission(self):
        """Remove selected permission."""
        try:
            current_item = self.permissions_tree.currentItem()
            if not current_item or not self.current_path:
                return
                
            name = current_item.text(0)
            
            reply = QMessageBox.question(
                self,
                "Confirm Remove",
                f"Are you sure you want to remove permissions for '{name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.manager.remove_permission(self.current_path, name):
                    self.refresh_permissions()
                else:
                    QMessageBox.critical(self, "Error", f"Failed to remove permission for {name}")
                    
        except Exception as e:
            self.logger.error(f"Failed to remove permission: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to remove permission: {str(e)}")
            
    def setup_connections(self):
        """Set up signal/slot connections."""
        pass  # All connections are set up in setup_ui
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed."""
        pass  # No cleanup needed for this panel
