"""Events configuration tab."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox, QComboBox, QCheckBox, QSpinBox)
from .base_tab import BaseConfigTab

class EventsTab(BaseConfigTab):
    """Tab for configuring event log settings."""
    
    # Event levels
    EVENT_LEVELS = [
        "Critical",
        "Error",
        "Warning", 
        "Information",
        "Verbose"
    ]
    
    # Common event logs
    COMMON_LOGS = [
        "System",
        "Application",
        "Security",
        "Setup"
    ]
    
    def __init__(self, config_handler):
        super().__init__(config_handler, "events")
        
    def setup_ui(self):
        """Set up the tab's user interface."""
        # Events configuration tree
        tree_label = QLabel("Event Log Configuration")
        self.layout.addWidget(tree_label)
        
        self.events_tree = QTreeWidget()
        self.events_tree.setHeaderLabels([
            "Log Name",
            "Filter Level",
            "Max Events",
            "Export Path",
            "Description"
        ])
        self.events_tree.setColumnWidth(0, 150)
        self.events_tree.setColumnWidth(1, 100)
        self.events_tree.setColumnWidth(2, 80)
        self.events_tree.setColumnWidth(3, 200)
        self.layout.addWidget(self.events_tree)
        
        # Add configuration buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Log Config")
        self.add_button.clicked.connect(self.add_log_config)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Config")
        self.edit_button.clicked.connect(self.edit_log_config)
        button_layout.addWidget(self.edit_button)
        
        self.remove_button = QPushButton("Remove Config")
        self.remove_button.clicked.connect(self.remove_log_config)
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        
        # Load existing configuration
        self.load_config()
        
    def add_log_config(self):
        """Add a new event log configuration."""
        # This would open a dialog to configure event log settings
        # like log monitoring, filtering, export settings, etc.
        QMessageBox.information(self, "Add Log Config", "Event log configuration dialog would open here")
        
    def edit_log_config(self):
        """Edit selected event log configuration."""
        current_item = self.events_tree.currentItem()
        if current_item:
            QMessageBox.information(self, "Edit Config", "Edit event log configuration dialog would open here")
        
    def remove_log_config(self):
        """Remove selected event log configuration."""
        current_item = self.events_tree.currentItem()
        if current_item:
            reply = QMessageBox.question(
                self,
                "Remove Config",
                "Are you sure you want to remove this event log configuration?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.events_tree.takeTopLevelItem(
                    self.events_tree.indexOfTopLevelItem(current_item)
                )
                self.save_config()
        
    def load_config(self):
        """Load events configuration from config handler."""
        config = self.get_config()
        self.events_tree.clear()
        
        if config:
            for log_name, log_data in config.items():
                item = QTreeWidgetItem([
                    log_name,
                    log_data.get('filter_level', ''),
                    str(log_data.get('max_events', '')),
                    log_data.get('export_path', ''),
                    log_data.get('description', '')
                ])
                self.events_tree.addTopLevelItem(item)
        
    def save_config(self):
        """Save current events configuration."""
        config = {}
        for i in range(self.events_tree.topLevelItemCount()):
            item = self.events_tree.topLevelItem(i)
            log_name = item.text(0)
            config[log_name] = {
                'filter_level': item.text(1),
                'max_events': item.text(2),
                'export_path': item.text(3),
                'description': item.text(4)
            }
        self.update_config(config)
        
    def on_config_changed(self):
        """Handle configuration changes."""
        self.load_config()
