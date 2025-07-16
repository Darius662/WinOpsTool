"""Add registry entry button component."""
import winreg
from PyQt6.QtWidgets import QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger
from ..dialogs import AddRegistryDialog

class AddButton(QPushButton):
    """Button for adding registry entries."""
    
    def __init__(self, parent=None):
        """Initialize add button.
        
        Args:
            parent: Parent widget (RegistryPanel)
        """
        super().__init__("Add", parent)
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
                "Warning",
                "Please select a registry key to add a value to."
            )
            return
        
        # Open dialog with pre-filled path
        dialog = AddRegistryDialog(self.panel, path)
        if dialog.exec():
            path, name, reg_type, value = dialog.get_entry()
            try:
                # Split path into root key and subkey
                root_key_name, subkey = self.panel._split_path(path)
                root_key = self.panel.ROOT_KEYS[root_key_name]
                
                # Create/open the key
                key = winreg.CreateKey(root_key, subkey)
                
                # Set the value
                self.panel._set_registry_value(key, name, reg_type, value)
                winreg.CloseKey(key)
                
                # Refresh the values view to show the new value
                self.panel.values_view.load_values(path)
                
                self.logger.info(f"Added registry entry: {path}\\{name}")
                
            except Exception as e:
                self.logger.error(f"Failed to add registry entry: {str(e)}")
                QMessageBox.critical(
                    self.panel,
                    "Error",
                    f"Failed to add registry entry: {str(e)}"
                )
                

