"""Drivers configuration tab."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox, QComboBox, QCheckBox)
from .base_tab import BaseConfigTab

class DriversTab(BaseConfigTab):
    """Tab for configuring driver management settings."""
    
    def __init__(self, config_handler):
        super().__init__(config_handler, "drivers")
        
    def setup_ui(self):
        """Set up the tab's user interface."""
        # Drivers configuration tree
        tree_label = QLabel("Driver Management Configuration")
        self.layout.addWidget(tree_label)
        
        self.drivers_tree = QTreeWidget()
        self.drivers_tree.setHeaderLabels([
            "Driver Name",
            "Action",
            "Path/Version",
            "Description"
        ])
        self.drivers_tree.setColumnWidth(0, 200)
        self.drivers_tree.setColumnWidth(1, 100)
        self.drivers_tree.setColumnWidth(2, 200)
        self.layout.addWidget(self.drivers_tree)
        
        # Add configuration buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Driver Config")
        self.add_button.clicked.connect(self.add_driver_config)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Config")
        self.edit_button.clicked.connect(self.edit_driver_config)
        button_layout.addWidget(self.edit_button)
        
        self.remove_button = QPushButton("Remove Config")
        self.remove_button.clicked.connect(self.remove_driver_config)
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        
        # Load existing configuration
        self.load_config()
        
    def add_driver_config(self):
        """Add a new driver configuration."""
        # This would open a dialog to configure driver settings
        # like driver installation, updates, rollbacks, etc.
        QMessageBox.information(self, "Add Driver Config", "Driver configuration dialog would open here")
        
    def edit_driver_config(self):
        """Edit selected driver configuration."""
        current_item = self.drivers_tree.currentItem()
        if current_item:
            QMessageBox.information(self, "Edit Config", "Edit driver configuration dialog would open here")
        
    def remove_driver_config(self):
        """Remove selected driver configuration."""
        current_item = self.drivers_tree.currentItem()
        if current_item:
            reply = QMessageBox.question(
                self,
                "Remove Config",
                "Are you sure you want to remove this driver configuration?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.drivers_tree.takeTopLevelItem(
                    self.drivers_tree.indexOfTopLevelItem(current_item)
                )
                self.save_config()
        
    def load_config(self):
        """Load drivers configuration from config handler."""
        config = self.get_config()
        self.drivers_tree.clear()
        
        if config:
            for driver_name, driver_data in config.items():
                item = QTreeWidgetItem([
                    driver_name,
                    driver_data.get('action', ''),
                    driver_data.get('path_version', ''),
                    driver_data.get('description', '')
                ])
                self.drivers_tree.addTopLevelItem(item)
        
    def save_config(self):
        """Save current drivers configuration."""
        config = {}
        for i in range(self.drivers_tree.topLevelItemCount()):
            item = self.drivers_tree.topLevelItem(i)
            driver_name = item.text(0)
            config[driver_name] = {
                'action': item.text(1),
                'path_version': item.text(2),
                'description': item.text(3)
            }
        self.update_config(config)
        
    def on_config_changed(self):
        """Handle configuration changes."""
        self.load_config()
