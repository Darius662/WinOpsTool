"""Tree widget for registry keys."""
import winreg
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from src.core.logger import setup_logger

class RegistryTree(QTreeWidget):
    """Hierarchical tree widget for displaying registry keys."""
    
    # Signal emitted when a registry key is selected
    keySelected = pyqtSignal(str)
    
    # Registry root keys
    ROOT_KEYS = {
        'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
        'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
        'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
        'HKEY_USERS': winreg.HKEY_USERS,
        'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG
    }
    
    def __init__(self, parent=None):
        """Initialize registry tree.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the tree widget UI."""
        self.setHeaderLabels(["Registry Keys"])
        
        # Configure header
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        # Connect selection signal
        self.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Enable selection of items
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        
        # Create root key items
        self._create_root_keys()
        
    def _create_root_keys(self):
        """Create root key items in the tree."""
        for key_name in self.ROOT_KEYS.keys():
            item = QTreeWidgetItem([key_name, "", ""])
            item.setData(0, Qt.ItemDataRole.UserRole, key_name)  # Store full path
            self.addTopLevelItem(item)
            
            # Add a placeholder child to show the expand arrow
            placeholder = QTreeWidgetItem(["Loading...", "", ""])
            item.addChild(placeholder)
            
        # Connect item expansion signal
        self.itemExpanded.connect(self._on_item_expanded)
        
    def _on_item_expanded(self, item):
        """Handle item expansion to load subkeys and values.
        
        Args:
            item: The expanded QTreeWidgetItem
        """
        # Check if this is a placeholder item (first expansion)
        if item.childCount() == 1 and item.child(0).text(0) == "Loading...":
            # Remove placeholder
            item.removeChild(item.child(0))
            
            # Get the full path for this item
            path = self._get_item_path(item)
            
            # Load subkeys and values
            self._load_registry_key(item, path)
        
    def _load_registry_key(self, parent_item, path):
        """Load registry subkeys and values for a given key.
        
        Args:
            parent_item: Parent QTreeWidgetItem
            path: Registry path to load
        """
        try:
            # Split path into root key and subkey
            root_key_name, subkey = self._split_path(path)
            root_key = self.ROOT_KEYS[root_key_name]
            
            # Open the key
            key = winreg.OpenKey(root_key, subkey if subkey else None, 0, winreg.KEY_READ)
            
            # First, enumerate subkeys
            try:
                i = 0
                while True:
                    subkey_name = winreg.EnumKey(key, i)
                    # Create subkey item
                    subkey_item = QTreeWidgetItem([subkey_name])
                    subkey_item.setData(0, Qt.ItemDataRole.UserRole, f"{path}\\{subkey_name}")
                    parent_item.addChild(subkey_item)
                    
                    # Add placeholder for expandability
                    placeholder = QTreeWidgetItem(["Loading...", "", ""])
                    subkey_item.addChild(placeholder)
                    
                    i += 1
            except WindowsError:
                # No more subkeys
                pass
                
            # We don't enumerate values here anymore - they will be shown in the ValuesView
                
            winreg.CloseKey(key)
            
        except Exception as e:
            self.logger.warning(f"Failed to load registry key {path}: {str(e)}")
            error_item = QTreeWidgetItem([f"Error: {str(e)}", "", ""])
            parent_item.addChild(error_item)
            
    def _get_item_path(self, item):
        """Get the full registry path for an item.
        
        Args:
            item: QTreeWidgetItem to get path for
            
        Returns:
            str: Full registry path
        """
        # Check if item has stored path
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path:
            return path
            
        # If not, it's a value item, get path from parent
        parent = item.parent()
        if parent:
            return parent.data(0, Qt.ItemDataRole.UserRole)
            
        # Fallback for root items
        return item.text(0)
        
    def _on_selection_changed(self):
        """Handle selection change to emit keySelected signal."""
        items = self.selectedItems()
        if not items:
            return
            
        item = items[0]
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path:
            self.keySelected.emit(path)
    
    def get_selected_key_path(self):
        """Get the path of the currently selected registry key.
        
        Returns:
            str: Registry key path or None if no selection
        """
        items = self.selectedItems()
        if not items:
            return None
            
        item = items[0]
        return item.data(0, Qt.ItemDataRole.UserRole)
        
    def clear_entries(self):
        """Clear all registry entries from the tree."""
        self.clear()
        self._create_root_keys()
        
    def _split_path(self, path):
        """Split registry path into root key and subkey.
        
        Args:
            path: Full registry path
            
        Returns:
            tuple: (root_key_name, subkey)
            
        Raises:
            ValueError: If path format is invalid
        """
        if path in self.ROOT_KEYS:
            return path, ""
            
        parts = path.split('\\', 1)
        if len(parts) != 2 or parts[0] not in self.ROOT_KEYS:
            raise ValueError(
                f"Invalid registry path. Must start with one of: "
                f"{', '.join(self.ROOT_KEYS.keys())}"
            )
        return parts[0], parts[1]
        
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
