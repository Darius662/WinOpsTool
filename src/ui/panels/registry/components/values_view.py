"""Registry values view component."""
import winreg
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class ValuesView(QTreeWidget):
    """Tree widget for displaying registry values."""
    
    def __init__(self, parent=None):
        """Initialize values view.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the tree widget UI."""
        self.setHeaderLabels(["Name", "Type", "Value"])
        
        # Set column widths
        self.setColumnWidth(0, 200)  # Name
        self.setColumnWidth(1, 100)  # Type
        self.setColumnWidth(2, 400)  # Value
        
        # Configure header
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        # Enable selection of items
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        
    def clear_values(self):
        """Clear all values from the view."""
        self.clear()
        
    def load_values(self, path):
        """Load registry values for a given key.
        
        Args:
            path: Registry path to load values from
        """
        self.clear()
        
        if not path:
            return
            
        try:
            # Split path into root key and subkey
            parts = path.split('\\', 1)
            if len(parts) == 1:
                root_key_name = parts[0]
                subkey = ""
            else:
                root_key_name, subkey = parts
                
            # Map root key name to handle
            root_keys = {
                'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
                'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
                'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
                'HKEY_USERS': winreg.HKEY_USERS,
                'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG
            }
            
            if root_key_name not in root_keys:
                self.logger.error(f"Invalid root key: {root_key_name}")
                return
                
            root_key = root_keys[root_key_name]
            
            # Open the key
            key = winreg.OpenKey(root_key, subkey, 0, winreg.KEY_READ)
            
            # Enumerate values
            try:
                i = 0
                while True:
                    name, value, reg_type = winreg.EnumValue(key, i)
                    # Format value for display
                    value_str = self._format_registry_value(value, reg_type)
                    reg_type_str = self._get_reg_type_name(reg_type)
                    
                    # Create value item
                    value_item = QTreeWidgetItem([name if name else "(Default)", reg_type_str, value_str])
                    self.addTopLevelItem(value_item)
                    
                    i += 1
            except WindowsError:
                # No more values
                pass
                
            winreg.CloseKey(key)
            
        except Exception as e:
            self.logger.warning(f"Failed to load registry values for {path}: {str(e)}")
            error_item = QTreeWidgetItem([f"Error: {str(e)}", "", ""])
            self.addTopLevelItem(error_item)
            
    def _format_registry_value(self, value, reg_type):
        """Format registry value for display based on type.
        
        Args:
            value: Registry value
            reg_type: Registry value type
            
        Returns:
            Formatted string representation of value
        """
        if reg_type == winreg.REG_BINARY:
            return ' '.join(f'{b:02x}' for b in value)
        elif reg_type == winreg.REG_MULTI_SZ:
            return ';'.join(value)
        elif reg_type == winreg.REG_DWORD:
            return f"0x{value:08x}"
        elif reg_type == winreg.REG_QWORD:
            return f"0x{value:016x}"
        else:
            return str(value)
    
    def _get_reg_type_name(self, reg_type):
        """Get registry type name from type value.
        
        Args:
            reg_type: Registry type value
            
        Returns:
            Registry type name
        """
        type_map = {
            winreg.REG_SZ: 'REG_SZ',
            winreg.REG_EXPAND_SZ: 'REG_EXPAND_SZ',
            winreg.REG_BINARY: 'REG_BINARY',
            winreg.REG_DWORD: 'REG_DWORD',
            winreg.REG_QWORD: 'REG_QWORD',
            winreg.REG_MULTI_SZ: 'REG_MULTI_SZ',
            winreg.REG_NONE: 'REG_NONE'
        }
        return type_map.get(reg_type, f'Unknown ({reg_type})')
