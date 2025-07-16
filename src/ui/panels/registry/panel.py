"""Registry management panel."""
import winreg
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QMessageBox)
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import RegistryTree
from .dialogs import AddRegistryDialog

class RegistryPanel(BasePanel):
    """Panel for managing registry entries."""
    
    # Registry root keys
    ROOT_KEYS = {
        'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
        'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
        'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
        'HKEY_USERS': winreg.HKEY_USERS,
        'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG
    }
    
    def __init__(self, main_window):
        """Initialize registry panel.
        
        Args:
            main_window: MainWindow instance
        """
        super().__init__(main_window)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Create tree widget
        self.tree = RegistryTree()
        self.add_widget(self.tree)
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add")
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit")
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete")
        button_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("Refresh")
        button_layout.addWidget(self.refresh_button)
        
        self.add_layout(button_layout)
        
    def setup_connections(self):
        """Set up signal/slot connections."""
        self.add_button.clicked.connect(self.add_entry)
        self.edit_button.clicked.connect(self.edit_entry)
        self.delete_button.clicked.connect(self.delete_entry)
        self.refresh_button.clicked.connect(self.refresh_entries)
        
    def add_entry(self):
        """Add a new registry entry."""
        dialog = AddRegistryDialog(self)
        if dialog.exec():
            path, name, reg_type, value = dialog.get_entry()
            try:
                # Split path into root key and subkey
                root_key_name, subkey = self._split_path(path)
                root_key = self.ROOT_KEYS[root_key_name]
                
                # Create/open the key
                key = winreg.CreateKey(root_key, subkey)
                
                # Set the value
                self._set_registry_value(key, name, reg_type, value)
                winreg.CloseKey(key)
                
                # Add to tree
                self.tree.add_entry(path, name, reg_type, value)
                self.logger.info(f"Added registry entry: {path}\\{name}")
                
            except Exception as e:
                self.logger.error(f"Failed to add registry entry: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to add registry entry: {str(e)}"
                )
                
    def edit_entry(self):
        """Edit selected registry entry."""
        item = self.tree.currentItem()
        if not item:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select an entry to edit."
            )
            return
            
        path, name, reg_type, value = self.tree.get_entry(item)
        dialog = AddRegistryDialog(self, path, name, reg_type, value)
        
        if dialog.exec():
            new_path, new_name, new_type, new_value = dialog.get_entry()
            try:
                # Handle path change
                if path != new_path or name != new_name:
                    # Delete old value
                    self._delete_registry_value(path, name)
                    
                # Create/update new value
                root_key_name, subkey = self._split_path(new_path)
                root_key = self.ROOT_KEYS[root_key_name]
                key = winreg.CreateKey(root_key, subkey)
                self._set_registry_value(key, new_name, new_type, new_value)
                winreg.CloseKey(key)
                
                # Update tree
                self.tree.update_entry(
                    item,
                    new_path,
                    new_name,
                    new_type,
                    new_value
                )
                self.logger.info(
                    f"Updated registry entry: {new_path}\\{new_name}"
                )
                
            except Exception as e:
                self.logger.error(f"Failed to update registry entry: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to update registry entry: {str(e)}"
                )
                
    def delete_entry(self):
        """Delete selected registry entry."""
        item = self.tree.currentItem()
        if not item:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select an entry to delete."
            )
            return
            
        path, name, _, _ = self.tree.get_entry(item)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{path}\\{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self._delete_registry_value(path, name)
                self.tree.takeTopLevelItem(
                    self.tree.indexOfTopLevelItem(item)
                )
                self.logger.info(f"Deleted registry entry: {path}\\{name}")
                
            except Exception as e:
                self.logger.error(f"Failed to delete registry entry: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete registry entry: {str(e)}"
                )
                
    def refresh_entries(self):
        """Refresh registry entries list."""
        # TODO: Implement registry enumeration
        pass
        
    def _split_path(self, path):
        """Split registry path into root key and subkey.
        
        Args:
            path: Full registry path
            
        Returns:
            tuple: (root_key_name, subkey)
            
        Raises:
            ValueError: If path format is invalid
        """
        parts = path.split('\\', 1)
        if len(parts) != 2 or parts[0] not in self.ROOT_KEYS:
            raise ValueError(
                f"Invalid registry path. Must start with one of: "
                f"{', '.join(self.ROOT_KEYS.keys())}"
            )
        return parts[0], parts[1]
        
    def _set_registry_value(self, key, name, reg_type, value):
        """Set registry value with proper type conversion.
        
        Args:
            key: Registry key handle
            name: Value name
            reg_type: Registry value type
            value: String value to convert and set
        """
        if reg_type == 'REG_DWORD':
            value = int(value, 0)
            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            
        elif reg_type == 'REG_QWORD':
            value = int(value, 0)
            winreg.SetValueEx(key, name, 0, winreg.REG_QWORD, value)
            
        elif reg_type == 'REG_BINARY':
            value = bytes.fromhex(value.replace(' ', ''))
            winreg.SetValueEx(key, name, 0, winreg.REG_BINARY, value)
            
        elif reg_type == 'REG_MULTI_SZ':
            value = value.split(';')
            winreg.SetValueEx(key, name, 0, winreg.REG_MULTI_SZ, value)
            
        elif reg_type == 'REG_EXPAND_SZ':
            winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
            
        else:  # REG_SZ
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            
    def _delete_registry_value(self, path, name):
        """Delete registry value.
        
        Args:
            path: Registry path
            name: Value name to delete
        """
        root_key_name, subkey = self._split_path(path)
        root_key = self.ROOT_KEYS[root_key_name]
        
        key = winreg.OpenKey(
            root_key,
            subkey,
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
        
    def update_remote_state(self, connected):
        """Update UI based on remote connection state.
        
        Args:
            connected: True if connected to remote system, False otherwise
        """
        # Enable/disable controls based on connection state
        self.setEnabled(not connected)  # Disable local registry when remote
