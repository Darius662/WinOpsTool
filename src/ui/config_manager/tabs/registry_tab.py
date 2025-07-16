"""Registry configuration tab."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox, QComboBox)
from .base_tab import BaseConfigTab

class RegistryTab(BaseConfigTab):
    """Tab for configuring registry settings."""
    
    # Registry value types
    REG_TYPES = [
        "REG_SZ",
        "REG_DWORD",
        "REG_BINARY",
        "REG_EXPAND_SZ",
        "REG_MULTI_SZ"
    ]
    
    def __init__(self, config_handler):
        super().__init__(config_handler, "registry")
        
    def setup_ui(self):
        """Set up the tab's user interface."""
        # Registry entries tree
        tree_label = QLabel("Registry Entries")
        self.layout.addWidget(tree_label)
        
        self.reg_tree = QTreeWidget()
        self.reg_tree.setHeaderLabels(["Path", "Name", "Type", "Value"])
        self.reg_tree.setColumnWidth(0, 300)  # Path column wider
        self.layout.addWidget(self.reg_tree)
        
        # Input fields
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        # Path input
        path_layout = QHBoxLayout()
        path_label = QLabel("Path:")
        path_layout.addWidget(path_label)
        
        self.reg_path_edit = QLineEdit()
        self.reg_path_edit.setPlaceholderText("Registry Path (e.g. HKLM\\Software\\MyApp)")
        path_layout.addWidget(self.reg_path_edit)
        input_layout.addLayout(path_layout)
        
        # Name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_layout.addWidget(name_label)
        
        self.reg_name_edit = QLineEdit()
        self.reg_name_edit.setPlaceholderText("Value Name")
        name_layout.addWidget(self.reg_name_edit)
        input_layout.addLayout(name_layout)
        
        # Type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("Type:")
        type_layout.addWidget(type_label)
        
        self.reg_type_combo = QComboBox()
        self.reg_type_combo.addItems(self.REG_TYPES)
        type_layout.addWidget(self.reg_type_combo)
        input_layout.addLayout(type_layout)
        
        # Value input
        value_layout = QHBoxLayout()
        value_label = QLabel("Value:")
        value_layout.addWidget(value_label)
        
        self.reg_value_edit = QLineEdit()
        self.reg_value_edit.setPlaceholderText("Value Data")
        value_layout.addWidget(self.reg_value_edit)
        input_layout.addLayout(value_layout)
        
        self.layout.addWidget(input_widget)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_registry_value)
        buttons_layout.addWidget(add_button)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_registry_value)
        buttons_layout.addWidget(delete_button)
        
        self.layout.addLayout(buttons_layout)
        
    def add_registry_value(self):
        """Add a registry value to the tree."""
        path = self.reg_path_edit.text().strip()
        name = self.reg_name_edit.text().strip()
        reg_type = self.reg_type_combo.currentText()
        value = self.reg_value_edit.text().strip()
        
        if not path or not name:
            QMessageBox.warning(self, "Warning", "Path and Name are required.")
            return
            
        try:
            # Validate value based on type
            if reg_type == "REG_DWORD":
                # Convert to integer and back to string to validate
                value = str(int(value, 0))  # Base 0 allows hex with 0x prefix
            elif reg_type == "REG_BINARY":
                # Validate hex string
                value = value.replace(" ", "")
                int(value, 16)  # Will raise ValueError if invalid hex
                
            item = QTreeWidgetItem([path, name, reg_type, value])
            self.reg_tree.addTopLevelItem(item)
            
            # Clear input fields
            self.reg_path_edit.clear()
            self.reg_name_edit.clear()
            self.reg_value_edit.clear()
            
            self.update_config_from_ui()
            
        except ValueError as e:
            QMessageBox.warning(
                self,
                "Invalid Value",
                f"The value is not valid for type {reg_type}."
            )
            
    def delete_registry_value(self):
        """Delete selected registry value."""
        item = self.reg_tree.currentItem()
        if item:
            self.reg_tree.takeTopLevelItem(
                self.reg_tree.indexOfTopLevelItem(item)
            )
            self.update_config_from_ui()
            
    def update_config_from_ui(self):
        """Update configuration from UI elements."""
        config = []
        
        for i in range(self.reg_tree.topLevelItemCount()):
            item = self.reg_tree.topLevelItem(i)
            config.append({
                "path": item.text(0),
                "name": item.text(1),
                "type": item.text(2),
                "value": item.text(3)
            })
            
        self.update_config(config)
        
    def on_config_changed(self):
        """Handle configuration changes."""
        config = self.get_config()
        
        # Clear existing items
        self.reg_tree.clear()
        
        # Add items from config
        for entry in config:
            item = QTreeWidgetItem([
                entry["path"],
                entry["name"],
                entry["type"],
                str(entry["value"])
            ])
            self.reg_tree.addTopLevelItem(item)
