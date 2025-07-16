"""Permissions list component for permissions panel."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QFileDialog
from PyQt6.QtCore import pyqtSignal

from src.core.logger import setup_logger
from ..tree_widget import PermissionsTree
from .button_bar import ButtonBar


class PermissionsList(QWidget):
    """Widget for displaying and managing permissions list."""
    
    # Signals emitted when actions are performed
    add_permission = pyqtSignal(str)
    edit_permission = pyqtSignal(str)
    remove_permission = pyqtSignal(str)
    refresh_permissions = pyqtSignal(str)
    path_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize permissions list.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.current_path = None
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Path selection
        path_layout = QHBoxLayout()
        self.path_combo = QComboBox()
        self.path_combo.setEditable(True)
        self.path_combo.setMaxCount(10)
        path_layout.addWidget(self.path_combo)
        
        # Browse button
        self.browse_btn = QPushButton("Browse...")
        path_layout.addWidget(self.browse_btn)
        
        # Add path layout to main layout
        layout.addLayout(path_layout)
        
        # Create button bar
        self.button_bar = ButtonBar(self.current_path, self)
        layout.addWidget(self.button_bar)
        
        # Create permissions tree
        self.permissions_tree = PermissionsTree()
        layout.addWidget(self.permissions_tree)
        
    def setup_connections(self):
        """Set up signal connections."""
        # Connect path combo and browse button
        self.path_combo.currentTextChanged.connect(self._on_path_changed)
        self.browse_btn.clicked.connect(self._on_browse)
        
        # Connect button bar signals
        self.button_bar.add_permission.connect(self.add_permission)
        self.button_bar.edit_permission.connect(self.edit_permission)
        self.button_bar.remove_permission.connect(self.remove_permission)
        self.button_bar.refresh_permissions.connect(self.refresh_permissions)
        
        # Connect tree selection change
        self.permissions_tree.itemSelectionChanged.connect(self._on_selection_changed)
        
    def _on_path_changed(self, path):
        """Handle path combo change.
        
        Args:
            path: New path
        """
        self.current_path = path
        self.button_bar.update_path(path)
        self.path_changed.emit(path)
        
    def _on_browse(self):
        """Handle browse button click."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            self.current_path or ""
        )
        
        if path:
            self.path_combo.setCurrentText(path)
            
    def _on_selection_changed(self):
        """Handle tree selection change."""
        has_selection = bool(self.permissions_tree.selectedItems())
        self.button_bar.update_button_states(has_selection)
        
    def add_path_to_history(self, path):
        """Add path to combo history if not present.
        
        Args:
            path: Path to add
        """
        if path and self.path_combo.findText(path) == -1:
            self.path_combo.addItem(path)
            
    def add_permissions(self, permissions_list):
        """Add permissions to the tree.
        
        Args:
            permissions_list: List of permission dictionaries
        """
        self.permissions_tree.clear_permissions()
        
        for perm in permissions_list:
            self.permissions_tree.add_permission(
                perm['name'],
                perm['type'],
                perm['permissions']
            )
            
    def get_selected_permission(self):
        """Get the currently selected permission.
        
        Returns:
            str: Selected permission name or None if nothing selected
        """
        current_item = self.permissions_tree.currentItem()
        if current_item:
            return current_item.text(0)
        return None
