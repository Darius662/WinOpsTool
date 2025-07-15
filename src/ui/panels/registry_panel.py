"""Registry Management Panel."""
import winreg
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
                          QTreeWidgetItem, QMessageBox, QInputDialog, QLineEdit,
                          QComboBox, QSplitter, QWidget)
from PyQt6.QtCore import Qt
from ..base.base_panel import BasePanel
from src.core.logger import setup_logger

class RegistryPanel(BasePanel):
    """Panel for managing Windows Registry."""
    
    HKEY_MAP = {
        "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
        "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
        "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
        "HKEY_USERS": winreg.HKEY_USERS,
        "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG
    }
    
    VALUE_TYPES = {
        "REG_SZ": winreg.REG_SZ,
        "REG_EXPAND_SZ": winreg.REG_EXPAND_SZ,
        "REG_BINARY": winreg.REG_BINARY,
        "REG_DWORD": winreg.REG_DWORD,
        "REG_MULTI_SZ": winreg.REG_MULTI_SZ
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
    def setup_ui(self):
        """Initialize the UI components."""
        # Create splitter for tree and values
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Registry tree
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        
        self.registry_tree = QTreeWidget()
        self.registry_tree.setHeaderLabels(["Registry Keys"])
        self.registry_tree.itemExpanded.connect(self.load_subkeys)
        tree_layout.addWidget(self.registry_tree)
        
        # Right side - Values
        values_widget = QWidget()
        values_layout = QVBoxLayout(values_widget)
        
        self.values_tree = QTreeWidget()
        self.values_tree.setHeaderLabels(["Name", "Type", "Value"])
        values_layout.addWidget(self.values_tree)
        
        splitter.addWidget(tree_widget)
        splitter.addWidget(values_widget)
        
        # Add splitter to main layout
        self.add_widget(splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_key_btn = QPushButton("Add Key")
        self.delete_key_btn = QPushButton("Delete Key")
        self.add_value_btn = QPushButton("Add Value")
        self.edit_value_btn = QPushButton("Edit Value")
        self.delete_value_btn = QPushButton("Delete Value")
        self.refresh_btn = QPushButton("Refresh")
        
        for btn in [self.add_key_btn, self.delete_key_btn, self.add_value_btn,
                   self.edit_value_btn, self.delete_value_btn, self.refresh_btn]:
            button_layout.addWidget(btn)
            
        self.add_layout(button_layout)
        
        # Connect signals
        self.add_key_btn.clicked.connect(self.add_key)
        self.delete_key_btn.clicked.connect(self.delete_key)
        self.add_value_btn.clicked.connect(self.add_value)
        self.edit_value_btn.clicked.connect(self.edit_value)
        self.delete_value_btn.clicked.connect(self.delete_value)
        self.refresh_btn.clicked.connect(self.refresh_view)
        self.registry_tree.currentItemChanged.connect(self.load_values)
        
        # Initial load
        self.load_root_keys()
        
    def load_root_keys(self):
        """Load root registry keys."""
        self.registry_tree.clear()
        for key_name in self.HKEY_MAP.keys():
            item = QTreeWidgetItem([key_name])
            item.addChild(QTreeWidgetItem(["..."]))  # Placeholder
            self.registry_tree.addTopLevelItem(item)
            
    def load_subkeys(self, item):
        """Load subkeys when a tree item is expanded."""
        try:
            if item.childCount() == 1 and item.child(0).text(0) == "...":
                # Get full path
                path = []
                current = item
                while current:
                    path.insert(0, current.text(0))
                    current = current.parent()
                    
                # Get registry key
                root_key = self.HKEY_MAP[path[0]]
                subkey_path = "\\".join(path[1:])
                
                # Clear placeholder
                item.removeChild(item.child(0))
                
                with winreg.OpenKey(root_key, subkey_path, 0, winreg.KEY_READ) as key:
                    index = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, index)
                            subitem = QTreeWidgetItem([subkey_name])
                            subitem.addChild(QTreeWidgetItem(["..."]))
                            item.addChild(subitem)
                            index += 1
                        except WindowsError:
                            break
                            
        except Exception as e:
            self.logger.error(f"Failed to load registry subkeys: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load registry subkeys: {str(e)}")
            
    def load_values(self, current, previous):
        """Load values for the selected registry key."""
        try:
            self.values_tree.clear()
            if not current:
                return
                
            # Get full path
            path = []
            item = current
            while item:
                path.insert(0, item.text(0))
                item = item.parent()
                
            if not path:
                return
                
            # Get registry key
            root_key = self.HKEY_MAP[path[0]]
            subkey_path = "\\".join(path[1:])
            
            with winreg.OpenKey(root_key, subkey_path, 0, winreg.KEY_READ) as key:
                index = 0
                while True:
                    try:
                        name, value, type_ = winreg.EnumValue(key, index)
                        item = QTreeWidgetItem([
                            name or "(Default)",
                            [k for k, v in self.VALUE_TYPES.items() if v == type_][0],
                            str(value)
                        ])
                        self.values_tree.addTopLevelItem(item)
                        index += 1
                    except WindowsError:
                        break
                        
        except Exception as e:
            self.logger.error(f"Failed to load registry values: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load registry values: {str(e)}")
            
    def get_current_path(self):
        """Get the full path of the currently selected registry key."""
        item = self.registry_tree.currentItem()
        if not item:
            return None, None
            
        path = []
        current = item
        while current:
            path.insert(0, current.text(0))
            current = current.parent()
            
        if not path:
            return None, None
            
        return self.HKEY_MAP[path[0]], "\\".join(path[1:])
        
    def add_key(self):
        """Add a new registry key."""
        try:
            root_key, subkey = self.get_current_path()
            if not root_key:
                return
                
            name, ok = QInputDialog.getText(self, "Add Key", "Key name:")
            if ok and name:
                new_key_path = f"{subkey}\\{name}" if subkey else name
                winreg.CreateKey(root_key, new_key_path)
                
                # Update tree
                item = QTreeWidgetItem([name])
                item.addChild(QTreeWidgetItem(["..."]))
                self.registry_tree.currentItem().addChild(item)
                
                self.logger.info(f"Added registry key: {new_key_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to add registry key: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add registry key: {str(e)}")
            
    def delete_key(self):
        """Delete the selected registry key."""
        try:
            root_key, subkey = self.get_current_path()
            if not root_key or not subkey:
                return
                
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete the registry key '{subkey}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                winreg.DeleteKey(root_key, subkey)
                self.registry_tree.currentItem().parent().removeChild(
                    self.registry_tree.currentItem()
                )
                self.logger.info(f"Deleted registry key: {subkey}")
                
        except Exception as e:
            self.logger.error(f"Failed to delete registry key: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to delete registry key: {str(e)}")
            
    def add_value(self):
        """Add a new registry value."""
        try:
            root_key, subkey = self.get_current_path()
            if not root_key:
                return
                
            name, ok = QInputDialog.getText(self, "Add Value", "Value name:")
            if ok:
                type_dialog = QInputDialog(self)
                type_dialog.setComboBoxItems(list(self.VALUE_TYPES.keys()))
                type_dialog.setWindowTitle("Select Value Type")
                type_dialog.setLabelText("Value type:")
                
                if type_dialog.exec() == QInputDialog.DialogCode.Accepted:
                    value_type = self.VALUE_TYPES[type_dialog.textValue()]
                    
                    value, ok = QInputDialog.getText(self, "Add Value", "Value data:")
                    if ok:
                        with winreg.OpenKey(root_key, subkey, 0, winreg.KEY_SET_VALUE) as key:
                            winreg.SetValueEx(key, name, 0, value_type, value)
                            
                        self.load_values(self.registry_tree.currentItem(), None)
                        self.logger.info(f"Added registry value: {name}")
                        
        except Exception as e:
            self.logger.error(f"Failed to add registry value: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add registry value: {str(e)}")
            
    def edit_value(self):
        """Edit the selected registry value."""
        try:
            current_item = self.values_tree.currentItem()
            if not current_item:
                return
                
            root_key, subkey = self.get_current_path()
            if not root_key:
                return
                
            name = current_item.text(0)
            if name == "(Default)":
                name = ""
                
            value, ok = QInputDialog.getText(
                self,
                "Edit Value",
                f"New value for {name or '(Default)'}:",
                QLineEdit.EchoMode.Normal,
                current_item.text(2)
            )
            
            if ok:
                value_type = self.VALUE_TYPES[current_item.text(1)]
                with winreg.OpenKey(root_key, subkey, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, name, 0, value_type, value)
                    
                self.load_values(self.registry_tree.currentItem(), None)
                self.logger.info(f"Updated registry value: {name}")
                
        except Exception as e:
            self.logger.error(f"Failed to edit registry value: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to edit registry value: {str(e)}")
            
    def delete_value(self):
        """Delete the selected registry value."""
        try:
            current_item = self.values_tree.currentItem()
            if not current_item:
                return
                
            root_key, subkey = self.get_current_path()
            if not root_key:
                return
                
            name = current_item.text(0)
            if name == "(Default)":
                name = ""
                
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete the value '{name or '(Default)'}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                with winreg.OpenKey(root_key, subkey, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, name)
                    
                self.load_values(self.registry_tree.currentItem(), None)
                self.logger.info(f"Deleted registry value: {name}")
                
        except Exception as e:
            self.logger.error(f"Failed to delete registry value: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to delete registry value: {str(e)}")
            
    def refresh_view(self):
        """Refresh the current view."""
        self.load_values(self.registry_tree.currentItem(), None)
        
    def setup_connections(self):
        """Set up signal/slot connections."""
        pass  # All connections are set up in setup_ui
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed."""
        pass  # No cleanup needed for this panel
