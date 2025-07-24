"""Network configuration tab."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox, QComboBox, QCheckBox)
from .base_tab import BaseConfigTab

class NetworkTab(BaseConfigTab):
    """Tab for configuring network management settings."""
    
    def __init__(self, config_handler):
        super().__init__(config_handler, "network")
        
    def setup_ui(self):
        """Set up the tab's user interface."""
        # Network configuration tree
        tree_label = QLabel("Network Management Configuration")
        self.layout.addWidget(tree_label)
        
        self.network_tree = QTreeWidget()
        self.network_tree.setHeaderLabels([
            "Interface/Setting",
            "Configuration Type",
            "Value",
            "Description"
        ])
        self.network_tree.setColumnWidth(0, 180)
        self.network_tree.setColumnWidth(1, 120)
        self.network_tree.setColumnWidth(2, 150)
        self.layout.addWidget(self.network_tree)
        
        # Add configuration buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Network Config")
        self.add_button.clicked.connect(self.add_network_config)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Config")
        self.edit_button.clicked.connect(self.edit_network_config)
        button_layout.addWidget(self.edit_button)
        
        self.remove_button = QPushButton("Remove Config")
        self.remove_button.clicked.connect(self.remove_network_config)
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        
        # Load existing configuration
        self.load_config()
        
    def add_network_config(self):
        """Add a new network configuration."""
        # This would open a dialog to configure network settings
        # like IP settings, DNS, proxy, network profiles, etc.
        QMessageBox.information(self, "Add Network Config", "Network configuration dialog would open here")
        
    def edit_network_config(self):
        """Edit selected network configuration."""
        current_item = self.network_tree.currentItem()
        if current_item:
            QMessageBox.information(self, "Edit Config", "Edit network configuration dialog would open here")
        
    def remove_network_config(self):
        """Remove selected network configuration."""
        current_item = self.network_tree.currentItem()
        if current_item:
            reply = QMessageBox.question(
                self,
                "Remove Config",
                "Are you sure you want to remove this network configuration?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.network_tree.takeTopLevelItem(
                    self.network_tree.indexOfTopLevelItem(current_item)
                )
                self.save_config()
        
    def load_config(self):
        """Load network configuration from config handler."""
        config = self.get_config()
        self.network_tree.clear()
        
        if config:
            for config_name, config_data in config.items():
                item = QTreeWidgetItem([
                    config_name,
                    config_data.get('type', ''),
                    config_data.get('value', ''),
                    config_data.get('description', '')
                ])
                self.network_tree.addTopLevelItem(item)
        
    def save_config(self):
        """Save current network configuration."""
        config = {}
        for i in range(self.network_tree.topLevelItemCount()):
            item = self.network_tree.topLevelItem(i)
            config_name = item.text(0)
            config[config_name] = {
                'type': item.text(1),
                'value': item.text(2),
                'description': item.text(3)
            }
        self.update_config(config)
        
    def on_config_changed(self):
        """Handle configuration changes."""
        self.load_config()
