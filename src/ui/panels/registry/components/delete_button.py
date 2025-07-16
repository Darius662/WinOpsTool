"""Delete registry entry button component."""
import winreg
from PyQt6.QtWidgets import QPushButton, QMessageBox, QTreeWidgetItem
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class DeleteButton(QPushButton):
    """Button for deleting registry entries."""
    
    def __init__(self, parent=None):
        """Initialize delete button.
        
        Args:
            parent: Parent widget (RegistryPanel)
        """
        super().__init__("Delete", parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.panel = parent
        
    def connect_signals(self):
        """Connect button signals."""
        self.clicked.connect(self.on_clicked)
        
    def on_clicked(self):
        """Handle button click event."""
        # First check if a value is selected in the values view
        selected_values = self.panel.values_view.selectedItems()
        if selected_values:
            # Delete a value
            item = selected_values[0]
            name = item.text(0)  # Name column
            path = self.panel.tree.get_selected_key_path()
            is_value = True
        else:
            # Check if a key is selected in the tree
            path = self.panel.tree.get_selected_key_path()
            if not path:
                QMessageBox.warning(self.panel, "No Selection", "Please select a registry value or key to delete.")
                return
            name = ""
            is_value = False
        
        # Prepare confirmation message
        if is_value:
            message = f"Are you sure you want to delete the value '{name}' from '{path}'?"
        else:
            message = f"Are you sure you want to delete the key '{path}' and ALL its contents?"
            
        reply = QMessageBox.question(
            self.panel,
            "Confirm Delete",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if is_value:
                    # Delete a value
                    self._delete_registry_value(path, name)
                    self.logger.info(f"Deleted registry value: {path}\\{name}")
                    # Refresh the values view
                    self.panel.values_view.load_values(path)
                else:
                    # Delete a key
                    self._delete_registry_key(path)
                    self.logger.info(f"Deleted registry key: {path}")
                    
                    # Refresh the tree
                    parent_path = self._get_parent_path(path)
                    if parent_path:
                        # Select the parent key
                        for i in range(self.panel.tree.topLevelItemCount()):
                            self._find_and_select_key(self.panel.tree.topLevelItem(i), parent_path)
                    else:
                        # This was a root key, just refresh everything
                        self.panel.refresh_entries()
                
            except Exception as e:
                self.logger.error(f"Failed to delete registry entry: {str(e)}")
                QMessageBox.critical(
                    self.panel,
                    "Error",
                    f"Failed to delete registry entry: {str(e)}"
                )
                
    def _delete_registry_value(self, path, name):
        """Delete a registry value.
        
        Args:
            path: Registry key path
            name: Value name to delete
        """
        # Split path into root key and subkey
        root_key_name, subkey = self.panel._split_path(path)
        root_key = self.panel.ROOT_KEYS[root_key_name]
        
        # Open the key
        key = winreg.OpenKey(root_key, subkey, 0, winreg.KEY_WRITE)
        
        # Delete the value
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
    
    def _delete_registry_key(self, path):
        """Delete a registry key.
        
        Args:
            path: Registry key path to delete
        """
        # Split path into root key and subkey
        root_key_name, subkey = self.panel._split_path(path)
        root_key = self.panel.ROOT_KEYS[root_key_name]
        
        # Get parent key path and child key name
        last_backslash = subkey.rfind('\\')
        if last_backslash == -1:
            # Direct child of root key
            parent_subkey = ""
            child_key = subkey
        else:
            # Nested key
            parent_subkey = subkey[:last_backslash]
            child_key = subkey[last_backslash+1:]
        
        # Open the parent key
        parent_key = winreg.OpenKey(root_key, parent_subkey, 0, winreg.KEY_WRITE)
        
        # Delete the key
        winreg.DeleteKey(parent_key, child_key)
        winreg.CloseKey(parent_key)
    
    def _get_parent_path(self, path):
        """Get the parent path of a registry key path.
        
        Args:
            path: Registry key path
            
        Returns:
            str: Parent path or None if root key
        """
        # Split path into root key and subkey
        root_key_name, subkey = self.panel._split_path(path)
        
        if not subkey:
            # This is a root key, no parent
            return None
            
        last_backslash = subkey.rfind('\\')
        if last_backslash == -1:
            # Direct child of root key
            return root_key_name
        else:
            # Nested key
            return f"{root_key_name}\\{subkey[:last_backslash]}"
    
    def _find_and_select_key(self, item, path):
        """Find a registry key item by path and select it.
        
        Args:
            item: QTreeWidgetItem to start search from
            path: Registry path to find
            
        Returns:
            bool: True if found and selected, False otherwise
        """
        # Check if this is the item we're looking for
        item_path = item.data(0, Qt.ItemDataRole.UserRole)
        if item_path == path:
            # Found it, select it
            self.panel.tree.setCurrentItem(item)
            return True
            
        # Check children recursively
        for i in range(item.childCount()):
            child = item.child(i)
            if self._find_and_select_key(child, path):
                return True
                    
        return False
