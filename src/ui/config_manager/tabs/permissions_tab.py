"""Permissions configuration tab."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox, QComboBox, QCheckBox)
from .base_tab import BaseConfigTab

class PermissionsTab(BaseConfigTab):
    """Tab for configuring file and folder permissions."""
    
    # Permission types
    PERMISSIONS = [
        "Read",
        "Write",
        "Execute",
        "Full Control"
    ]
    
    def __init__(self, config_handler):
        super().__init__(config_handler, "permissions")
        
    def setup_ui(self):
        """Set up the tab's user interface."""
        # Permissions tree
        tree_label = QLabel("File and Folder Permissions")
        self.layout.addWidget(tree_label)
        
        self.permissions_tree = QTreeWidget()
        self.permissions_tree.setHeaderLabels([
            "Path",
            "User/Group",
            "Permissions",
            "Inherit",
            "Owner"
        ])
        self.permissions_tree.setColumnWidth(0, 300)
        self.permissions_tree.setColumnWidth(1, 150)
        self.permissions_tree.setColumnWidth(2, 200)
        self.layout.addWidget(self.permissions_tree)
        
        # Input fields
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        # Path
        path_layout = QHBoxLayout()
        path_label = QLabel("Path:")
        path_layout.addWidget(path_label)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Full path to file or folder")
        path_layout.addWidget(self.path_edit)
        input_layout.addLayout(path_layout)
        
        # User/Group
        user_layout = QHBoxLayout()
        user_label = QLabel("User/Group:")
        user_layout.addWidget(user_label)
        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("Username or group name")
        user_layout.addWidget(self.user_edit)
        input_layout.addLayout(user_layout)
        
        # Permissions
        perm_layout = QHBoxLayout()
        perm_label = QLabel("Permissions:")
        perm_layout.addWidget(perm_label)
        
        perm_widget = QWidget()
        perm_checks_layout = QHBoxLayout(perm_widget)
        self.perm_checks = []
        for perm in self.PERMISSIONS:
            check = QCheckBox(perm)
            self.perm_checks.append(check)
            perm_checks_layout.addWidget(check)
        perm_layout.addWidget(perm_widget)
        input_layout.addLayout(perm_layout)
        
        # Inherit
        inherit_layout = QHBoxLayout()
        inherit_label = QLabel("Inherit:")
        inherit_layout.addWidget(inherit_label)
        self.inherit_check = QCheckBox()
        inherit_layout.addWidget(self.inherit_check)
        input_layout.addLayout(inherit_layout)
        
        # Owner
        owner_layout = QHBoxLayout()
        owner_label = QLabel("Set Owner:")
        owner_layout.addWidget(owner_label)
        self.owner_check = QCheckBox()
        owner_layout.addWidget(self.owner_check)
        input_layout.addLayout(owner_layout)
        
        self.layout.addWidget(input_widget)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Permission")
        add_button.clicked.connect(self.add_permission)
        buttons_layout.addWidget(add_button)
        
        delete_button = QPushButton("Delete Permission")
        delete_button.clicked.connect(self.delete_permission)
        buttons_layout.addWidget(delete_button)
        
        self.layout.addLayout(buttons_layout)
        
    def add_permission(self):
        """Add a permission entry to the tree."""
        path = self.path_edit.text().strip()
        user = self.user_edit.text().strip()
        
        if not path:
            QMessageBox.warning(self, "Warning", "Path is required.")
            return
            
        if not user:
            QMessageBox.warning(self, "Warning", "User/Group is required.")
            return
            
        # Get selected permissions
        perms = []
        for check in self.perm_checks:
            if check.isChecked():
                perms.append(check.text())
                
        if not perms:
            QMessageBox.warning(self, "Warning", "At least one permission must be selected.")
            return
            
        item = QTreeWidgetItem([
            path,
            user,
            ", ".join(perms),
            "Yes" if self.inherit_check.isChecked() else "No",
            "Yes" if self.owner_check.isChecked() else "No"
        ])
        self.permissions_tree.addTopLevelItem(item)
        
        # Clear input fields
        self.path_edit.clear()
        self.user_edit.clear()
        for check in self.perm_checks:
            check.setChecked(False)
        self.inherit_check.setChecked(False)
        self.owner_check.setChecked(False)
        
        self.update_config_from_ui()
        
    def delete_permission(self):
        """Delete selected permission entry."""
        item = self.permissions_tree.currentItem()
        if item:
            self.permissions_tree.takeTopLevelItem(
                self.permissions_tree.indexOfTopLevelItem(item)
            )
            self.update_config_from_ui()
            
    def update_config_from_ui(self):
        """Update configuration from UI elements."""
        config = []
        
        for i in range(self.permissions_tree.topLevelItemCount()):
            item = self.permissions_tree.topLevelItem(i)
            config.append({
                "path": item.text(0),
                "user": item.text(1),
                "permissions": [p.strip() for p in item.text(2).split(",")],
                "inherit": item.text(3) == "Yes",
                "owner": item.text(4) == "Yes"
            })
            
        self.update_config(config)
        
    def on_config_changed(self):
        """Handle configuration changes."""
        config = self.get_config()
        
        # Clear existing items
        self.permissions_tree.clear()
        
        # Add items from config
        for entry in config:
            item = QTreeWidgetItem([
                entry["path"],
                entry["user"],
                ", ".join(entry["permissions"]),
                "Yes" if entry.get("inherit", False) else "No",
                "Yes" if entry.get("owner", False) else "No"
            ])
            self.permissions_tree.addTopLevelItem(item)
