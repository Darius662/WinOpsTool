"""Processes configuration tab."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox, QComboBox, QCheckBox, QSpinBox)
from .base_tab import BaseConfigTab

class ProcessesTab(BaseConfigTab):
    """Tab for configuring process management settings."""
    
    # Process actions
    PROCESS_ACTIONS = [
        "Monitor",
        "Kill",
        "Set Priority",
        "Set Affinity",
        "Limit Resources"
    ]
    
    # Process priorities
    PROCESS_PRIORITIES = [
        "Low",
        "Below Normal",
        "Normal",
        "Above Normal",
        "High",
        "Real Time"
    ]
    
    def __init__(self, config_handler):
        super().__init__(config_handler, "processes")
        
    def setup_ui(self):
        """Set up the tab's user interface."""
        # Processes configuration tree
        tree_label = QLabel("Process Management Configuration")
        self.layout.addWidget(tree_label)
        
        self.processes_tree = QTreeWidget()
        self.processes_tree.setHeaderLabels([
            "Process Name/Pattern",
            "Action",
            "Parameters",
            "Description"
        ])
        self.processes_tree.setColumnWidth(0, 200)
        self.processes_tree.setColumnWidth(1, 120)
        self.processes_tree.setColumnWidth(2, 150)
        self.layout.addWidget(self.processes_tree)
        
        # Add configuration buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Process Config")
        self.add_button.clicked.connect(self.add_process_config)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Config")
        self.edit_button.clicked.connect(self.edit_process_config)
        button_layout.addWidget(self.edit_button)
        
        self.remove_button = QPushButton("Remove Config")
        self.remove_button.clicked.connect(self.remove_process_config)
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        
        # Load existing configuration
        self.load_config()
        
    def add_process_config(self):
        """Add a new process configuration."""
        # This would open a dialog to configure process settings
        # like monitoring rules, kill lists, priority settings, etc.
        QMessageBox.information(self, "Add Process Config", "Process configuration dialog would open here")
        
    def edit_process_config(self):
        """Edit selected process configuration."""
        current_item = self.processes_tree.currentItem()
        if current_item:
            QMessageBox.information(self, "Edit Config", "Edit process configuration dialog would open here")
        
    def remove_process_config(self):
        """Remove selected process configuration."""
        current_item = self.processes_tree.currentItem()
        if current_item:
            reply = QMessageBox.question(
                self,
                "Remove Config",
                "Are you sure you want to remove this process configuration?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.processes_tree.takeTopLevelItem(
                    self.processes_tree.indexOfTopLevelItem(current_item)
                )
                self.save_config()
        
    def load_config(self):
        """Load processes configuration from config handler."""
        config = self.get_config()
        self.processes_tree.clear()
        
        if config:
            for process_name, process_data in config.items():
                item = QTreeWidgetItem([
                    process_name,
                    process_data.get('action', ''),
                    process_data.get('parameters', ''),
                    process_data.get('description', '')
                ])
                self.processes_tree.addTopLevelItem(item)
        
    def save_config(self):
        """Save current processes configuration."""
        config = {}
        for i in range(self.processes_tree.topLevelItemCount()):
            item = self.processes_tree.topLevelItem(i)
            process_name = item.text(0)
            config[process_name] = {
                'action': item.text(1),
                'parameters': item.text(2),
                'description': item.text(3)
            }
        self.update_config(config)
        
    def on_config_changed(self):
        """Handle configuration changes."""
        self.load_config()
