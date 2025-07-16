"""Registry operations component."""
import winreg
from src.core.logger import setup_logger

class RegistryOperations:
    """Encapsulates registry operations for the Registry Panel."""
    
    # Registry root keys
    ROOT_KEYS = {
        'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
        'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
        'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
        'HKEY_USERS': winreg.HKEY_USERS,
        'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG
    }
    
    def __init__(self, panel):
        """Initialize registry operations.
        
        Args:
            panel: Parent RegistryPanel instance
        """
        self.panel = panel
        self.logger = setup_logger(self.__class__.__name__)
        
    @property
    def tree(self):
        """Get registry tree widget."""
        return self.panel.tree if hasattr(self.panel, 'tree') else None
        
    @property
    def values_view(self):
        """Get values view widget."""
        return self.panel.values_view if hasattr(self.panel, 'values_view') else None
        
    @property
    def dialog_factory(self):
        """Get dialog factory."""
        return self.panel.dialog_factory if hasattr(self.panel, 'dialog_factory') else None
    
    def add_entry(self):
        """Add a new registry entry."""
        # Get the currently selected key path
        if not self.tree or not self.tree.currentItem():
            self.dialog_factory.show_warning("Please select a registry key first")
            return
            
        path = self.tree.get_selected_path()
        if not path:
            self.dialog_factory.show_warning("Please select a registry key first")
            return
            
        # Create and show dialog
        dialog = self.dialog_factory.create_add_value_dialog()
        if dialog.exec():
            name, value, reg_type = dialog.get_value()
            try:
                # Add registry value
                root_key_name, subkey = self._split_path(path)
                root_key = self.ROOT_KEYS[root_key_name]
                
                key = winreg.OpenKey(
                    root_key,
                    subkey,
                    0,
                    winreg.KEY_SET_VALUE
                )
                
                self._set_registry_value(key, name, reg_type, value)
                winreg.CloseKey(key)
                
                # Refresh values view
                self.refresh_values(path)
                self.logger.info(f"Added registry value: {name} to {path}")
            except Exception as e:
                self.logger.error(f"Error adding registry value: {str(e)}")
                self.dialog_factory.show_error(f"Error adding registry value: {str(e)}")
    
    def edit_entry(self):
        """Edit selected registry entry."""
        # Get the currently selected value
        if not self.values_view or not self.values_view.currentItem():
            self.dialog_factory.show_warning("Please select a registry value to edit")
            return
            
        item = self.values_view.currentItem()
        name = item.text(0)
        value = item.text(1)
        reg_type = item.text(2)
        path = self.tree.get_selected_path()
        
        # Create and show dialog
        dialog = self.dialog_factory.create_add_value_dialog(name, value, reg_type)
        if dialog.exec():
            new_name, new_value, new_reg_type = dialog.get_value()
            try:
                # Update registry value
                root_key_name, subkey = self._split_path(path)
                root_key = self.ROOT_KEYS[root_key_name]
                
                key = winreg.OpenKey(
                    root_key,
                    subkey,
                    0,
                    winreg.KEY_SET_VALUE
                )
                
                # If name changed, delete old value and create new one
                if name != new_name:
                    self._delete_registry_value(path, name)
                
                self._set_registry_value(key, new_name, new_reg_type, new_value)
                winreg.CloseKey(key)
                
                # Refresh values view
                self.refresh_values(path)
                self.logger.info(f"Updated registry value: {new_name} in {path}")
            except Exception as e:
                self.logger.error(f"Error updating registry value: {str(e)}")
                self.dialog_factory.show_error(f"Error updating registry value: {str(e)}")
    
    def delete_entry(self):
        """Delete selected registry entry."""
        # Get the currently selected value
        if not self.values_view or not self.values_view.currentItem():
            self.dialog_factory.show_warning("Please select a registry value to delete")
            return
            
        item = self.values_view.currentItem()
        name = item.text(0)
        path = self.tree.get_selected_path()
        
        # Confirm deletion
        if self.dialog_factory.confirm_delete(name, "Registry Value"):
            try:
                # Delete registry value
                self._delete_registry_value(path, name)
                
                # Refresh values view
                self.refresh_values(path)
                self.logger.info(f"Deleted registry value: {name} from {path}")
            except Exception as e:
                self.logger.error(f"Error deleting registry value: {str(e)}")
                self.dialog_factory.show_error(f"Error deleting registry value: {str(e)}")
    
    def refresh_entries(self):
        """Refresh registry entries list."""
        if self.tree:
            self.tree.clear_entries()
            self.logger.info("Registry entries refreshed successfully")
    
    def refresh_values(self, path):
        """Refresh registry values for the selected key.
        
        Args:
            path: Registry key path
        """
        if self.values_view:
            self.values_view.load_values(path)
    
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
