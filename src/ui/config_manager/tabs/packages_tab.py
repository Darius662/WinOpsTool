"""Packages configuration tab."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox, QComboBox, QCheckBox)
from .base_tab import BaseConfigTab

class PackagesTab(BaseConfigTab):
    """Tab for configuring package management settings."""
    
    # Package actions
    PACKAGE_ACTIONS = [
        "Install",
        "Uninstall",
        "Update",
        "Configure"
    ]
    
    def __init__(self, config_handler):
        super().__init__(config_handler, "packages")
        
    def setup_ui(self):
        """Set up the tab's user interface."""
        # Packages configuration tree
        tree_label = QLabel("Package Management Configuration")
        self.layout.addWidget(tree_label)
        
        self.packages_tree = QTreeWidget()
        self.packages_tree.setHeaderLabels([
            "Package Name",
            "Action",
            "Version/Source",
            "Description"
        ])
        self.packages_tree.setColumnWidth(0, 200)
        self.packages_tree.setColumnWidth(1, 100)
        self.packages_tree.setColumnWidth(2, 150)
        self.layout.addWidget(self.packages_tree)
        
        # Add configuration buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Package Config")
        self.add_button.clicked.connect(self.add_package_config)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Config")
        self.edit_button.clicked.connect(self.edit_package_config)
        button_layout.addWidget(self.edit_button)
        
        self.remove_button = QPushButton("Remove Config")
        self.remove_button.clicked.connect(self.remove_package_config)
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        
        # Load existing configuration
        self.load_config()
        
    def add_package_config(self):
        """Add a new package configuration."""
        # This would open a dialog to configure package settings
        # like installation, removal, updates, etc.
        QMessageBox.information(self, "Add Package Config", "Package configuration dialog would open here")
        
    def edit_package_config(self):
        """Edit selected package configuration."""
        current_item = self.packages_tree.currentItem()
        if current_item:
            QMessageBox.information(self, "Edit Config", "Edit package configuration dialog would open here")
        
    def remove_package_config(self):
        """Remove selected package configuration."""
        current_item = self.packages_tree.currentItem()
        if current_item:
            reply = QMessageBox.question(
                self,
                "Remove Config",
                "Are you sure you want to remove this package configuration?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.packages_tree.takeTopLevelItem(
                    self.packages_tree.indexOfTopLevelItem(current_item)
                )
                self.save_config()
        
    def load_config(self):
        """Load packages configuration from config handler."""
        config = self.get_config()
        self.packages_tree.clear()
        
        if config:
            for package_name, package_data in config.items():
                item = QTreeWidgetItem([
                    package_name,
                    package_data.get('action', ''),
                    package_data.get('version_source', ''),
                    package_data.get('description', '')
                ])
                self.packages_tree.addTopLevelItem(item)
        
    def save_config(self):
        """Save current packages configuration."""
        config = {}
        for i in range(self.packages_tree.topLevelItemCount()):
            item = self.packages_tree.topLevelItem(i)
            package_name = item.text(0)
            config[package_name] = {
                'action': item.text(1),
                'version_source': item.text(2),
                'description': item.text(3)
            }
        self.update_config(config)
        
    def on_config_changed(self):
        """Handle configuration changes."""
        self.load_config()
