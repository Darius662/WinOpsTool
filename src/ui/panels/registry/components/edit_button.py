"""Edit registry entry button component."""
import winreg
from PyQt6.QtWidgets import QPushButton, QMessageBox, QTreeWidgetItem
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger
from ..dialogs import AddRegistryDialog

class EditButton(QPushButton):
    """Button for editing registry entries."""
    
    def __init__(self, parent=None):
        """Initialize edit button.
        
        Args:
            parent: Parent widget (RegistryPanel)
        """
        super().__init__("Edit", parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.panel = parent
        
    def connect_signals(self):
        """Connect button signals."""
        self.clicked.connect(self.on_clicked)
        
    def on_clicked(self):
        """Handle button click event."""
        # Get selected key path
        path = self.panel.tree.get_selected_key_path()
        if not path:
            QMessageBox.warning(
                self.panel,
                "No Selection",
                "Please select a registry key first."
            )
            return
            
        # Get selected value from values view
        selected_items = self.panel.values_view.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self.panel,
                "No Selection",
                "Please select a registry value to edit."
            )
            return
            
        # Get the selected value item
        item = selected_items[0]
        
        # Get current value information
        name = item.text(0)  # Name column
        reg_type = item.text(1)  # Type column
        value = item.text(2)  # Value column
        
        # Open dialog with pre-filled values
        dialog = AddRegistryDialog(self.panel, path, name, reg_type, value)
        
        if dialog.exec():
            new_path, new_name, new_type, new_value = dialog.get_entry()
            try:
                # Handle path change
                if path != new_path or name != new_name:
                    # Delete old value
                    self.panel._delete_registry_value(path, name)
                    
                # Split path into root key and subkey
                root_key_name, subkey = self.panel._split_path(new_path)
                root_key = self.panel.ROOT_KEYS[root_key_name]
                
                # Create/open the key
                key = winreg.CreateKey(root_key, subkey)
                
                # Set the value
                self.panel._set_registry_value(key, new_name, new_type, new_value)
                winreg.CloseKey(key)
                
                # Refresh the values view to show the updated value
                if path != new_path:
                    # Path changed, need to refresh the new path
                    self.panel.values_view.load_values(new_path)
                else:
                    # Just refresh the current path
                    self.panel.values_view.load_values(path)
                
                self.logger.info(
                    f"Updated registry entry: {path}\\{name} -> {new_path}\\{new_name}"
                )
                
            except Exception as e:
                self.logger.error(f"Failed to update registry entry: {str(e)}")
                QMessageBox.critical(
                    self.panel,
                    "Error",
                    f"Failed to update registry entry: {str(e)}"
                )
                

