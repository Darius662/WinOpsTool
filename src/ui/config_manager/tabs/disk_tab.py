"""Disk configuration tab."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox, QComboBox, QSpinBox, QCheckBox)
from .base_tab import BaseConfigTab

class DiskTab(BaseConfigTab):
    """Tab for configuring disk management settings."""
    
    def __init__(self, config_handler):
        super().__init__(config_handler, "disk")
        
    def setup_ui(self):
        """Set up the tab's user interface."""
        # Disk configuration tree
        tree_label = QLabel("Disk Management Configuration")
        self.layout.addWidget(tree_label)
        
        self.disk_tree = QTreeWidget()
        self.disk_tree.setHeaderLabels([
            "Setting",
            "Value",
            "Description"
        ])
        self.disk_tree.setColumnWidth(0, 200)
        self.disk_tree.setColumnWidth(1, 150)
        self.layout.addWidget(self.disk_tree)
        
        # Add configuration buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Setting")
        self.add_button.clicked.connect(self.add_setting)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Setting")
        self.edit_button.clicked.connect(self.edit_setting)
        button_layout.addWidget(self.edit_button)
        
        self.remove_button = QPushButton("Remove Setting")
        self.remove_button.clicked.connect(self.remove_setting)
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        
        # Load existing configuration
        self.load_config()
        
    def add_setting(self):
        """Add a new disk configuration setting."""
        # This would open a dialog to add disk-related settings
        # like cleanup policies, disk quotas, etc.
        QMessageBox.information(self, "Add Setting", "Disk configuration dialog would open here")
        
    def edit_setting(self):
        """Edit selected disk configuration setting."""
        current_item = self.disk_tree.currentItem()
        if current_item:
            QMessageBox.information(self, "Edit Setting", "Edit disk configuration dialog would open here")
        
    def remove_setting(self):
        """Remove selected disk configuration setting."""
        current_item = self.disk_tree.currentItem()
        if current_item:
            reply = QMessageBox.question(
                self,
                "Remove Setting",
                "Are you sure you want to remove this disk setting?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.disk_tree.takeTopLevelItem(
                    self.disk_tree.indexOfTopLevelItem(current_item)
                )
                self.save_config()
        
    def load_config(self):
        """Load disk configuration from config handler."""
        config = self.get_config()
        self.disk_tree.clear()
        
        if config:
            for setting_name, setting_data in config.items():
                item = QTreeWidgetItem([
                    setting_name,
                    str(setting_data.get('value', '')),
                    setting_data.get('description', '')
                ])
                self.disk_tree.addTopLevelItem(item)
        
    def save_config(self):
        """Save current disk configuration."""
        config = {}
        for i in range(self.disk_tree.topLevelItemCount()):
            item = self.disk_tree.topLevelItem(i)
            setting_name = item.text(0)
            config[setting_name] = {
                'value': item.text(1),
                'description': item.text(2)
            }
        self.update_config(config)
        
    def on_config_changed(self):
        """Handle configuration changes."""
        self.load_config()
