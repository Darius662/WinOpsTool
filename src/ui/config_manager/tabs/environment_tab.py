"""Environment Variables configuration tab."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox)
from .base_tab import BaseConfigTab

class EnvironmentTab(BaseConfigTab):
    """Tab for configuring environment variables."""
    def __init__(self, config_handler):
        super().__init__(config_handler, "environment_variables")
        
    def setup_ui(self):
        """Set up the tab's user interface."""
        # System Variables
        system_group = QWidget()
        system_layout = QVBoxLayout(system_group)
        
        system_label = QLabel("System Variables")
        system_layout.addWidget(system_label)
        
        self.system_vars_tree = QTreeWidget()
        self.system_vars_tree.setHeaderLabels(["Name", "Value"])
        system_layout.addWidget(self.system_vars_tree)
        
        system_buttons = QHBoxLayout()
        add_system = QPushButton("Add")
        add_system.clicked.connect(self.add_system_var)
        system_buttons.addWidget(add_system)
        
        del_system = QPushButton("Delete")
        del_system.clicked.connect(lambda: self.delete_var(self.system_vars_tree))
        system_buttons.addWidget(del_system)
        
        system_layout.addLayout(system_buttons)
        self.layout.addWidget(system_group)
        
        # User Variables
        user_group = QWidget()
        user_layout = QVBoxLayout(user_group)
        
        user_label = QLabel("User Variables")
        user_layout.addWidget(user_label)
        
        self.user_vars_tree = QTreeWidget()
        self.user_vars_tree.setHeaderLabels(["Name", "Value"])
        user_layout.addWidget(self.user_vars_tree)
        
        user_buttons = QHBoxLayout()
        add_user = QPushButton("Add")
        add_user.clicked.connect(self.add_user_var)
        user_buttons.addWidget(add_user)
        
        del_user = QPushButton("Delete")
        del_user.clicked.connect(lambda: self.delete_var(self.user_vars_tree))
        user_buttons.addWidget(del_user)
        
        user_layout.addLayout(user_buttons)
        self.layout.addWidget(user_group)
        
    def add_system_var(self):
        """Add a system environment variable."""
        dialog = EnvVarDialog(self)
        if dialog.exec():
            name, value = dialog.get_values()
            if name:
                item = QTreeWidgetItem([name, value])
                self.system_vars_tree.addTopLevelItem(item)
                self.update_config_from_ui()
                
    def add_user_var(self):
        """Add a user environment variable."""
        dialog = EnvVarDialog(self)
        if dialog.exec():
            name, value = dialog.get_values()
            if name:
                item = QTreeWidgetItem([name, value])
                self.user_vars_tree.addTopLevelItem(item)
                self.update_config_from_ui()
                
    def delete_var(self, tree):
        """Delete selected variable from tree."""
        item = tree.currentItem()
        if item:
            tree.takeTopLevelItem(tree.indexOfTopLevelItem(item))
            self.update_config_from_ui()
            
    def update_config_from_ui(self):
        """Update configuration from UI elements."""
        config = {
            "system": {},
            "user": {}
        }
        
        # Get system variables
        for i in range(self.system_vars_tree.topLevelItemCount()):
            item = self.system_vars_tree.topLevelItem(i)
            config["system"][item.text(0)] = item.text(1)
            
        # Get user variables
        for i in range(self.user_vars_tree.topLevelItemCount()):
            item = self.user_vars_tree.topLevelItem(i)
            config["user"][item.text(0)] = item.text(1)
            
        self.update_config(config)
        
    def on_config_changed(self):
        """Handle configuration changes."""
        config = self.get_config()
        
        # Clear existing items
        self.system_vars_tree.clear()
        self.user_vars_tree.clear()
        
        # Update system variables
        for name, value in config.get("system", {}).items():
            item = QTreeWidgetItem([name, str(value)])
            self.system_vars_tree.addTopLevelItem(item)
            
        # Update user variables
        for name, value in config.get("user", {}).items():
            item = QTreeWidgetItem([name, str(value)])
            self.user_vars_tree.addTopLevelItem(item)
            
class EnvVarDialog(QMessageBox):
    """Dialog for adding environment variables."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Environment Variable")
        self.setText("Enter variable name and value:")
        
        # Create input fields
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Variable Name")
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("Variable Value")
        
        # Add input fields to layout
        layout = self.layout()
        layout.addWidget(self.name_edit, 1, 0)
        layout.addWidget(self.value_edit, 2, 0)
        
        # Add standard buttons
        self.setStandardButtons(QMessageBox.StandardButton.Ok | 
                              QMessageBox.StandardButton.Cancel)
        
    def get_values(self):
        """Get the entered name and value."""
        return self.name_edit.text(), self.value_edit.text()
