"""Scheduler configuration tab."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox, QComboBox, QCheckBox, QDateTimeEdit)
from PyQt6.QtCore import QDateTime
from .base_tab import BaseConfigTab

class SchedulerTab(BaseConfigTab):
    """Tab for configuring scheduled task settings."""
    
    # Task trigger types
    TRIGGER_TYPES = [
        "Daily",
        "Weekly", 
        "Monthly",
        "Once",
        "At startup",
        "At logon",
        "When idle"
    ]
    
    def __init__(self, config_handler):
        super().__init__(config_handler, "scheduler")
        
    def setup_ui(self):
        """Set up the tab's user interface."""
        # Scheduler configuration tree
        tree_label = QLabel("Task Scheduler Configuration")
        self.layout.addWidget(tree_label)
        
        self.scheduler_tree = QTreeWidget()
        self.scheduler_tree.setHeaderLabels([
            "Task Name",
            "Trigger Type",
            "Program/Script",
            "Status",
            "Description"
        ])
        self.scheduler_tree.setColumnWidth(0, 200)
        self.scheduler_tree.setColumnWidth(1, 120)
        self.scheduler_tree.setColumnWidth(2, 200)
        self.scheduler_tree.setColumnWidth(3, 80)
        self.layout.addWidget(self.scheduler_tree)
        
        # Add configuration buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Task Config")
        self.add_button.clicked.connect(self.add_task_config)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Config")
        self.edit_button.clicked.connect(self.edit_task_config)
        button_layout.addWidget(self.edit_button)
        
        self.remove_button = QPushButton("Remove Config")
        self.remove_button.clicked.connect(self.remove_task_config)
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch()
        self.layout.addLayout(button_layout)
        
        # Load existing configuration
        self.load_config()
        
    def add_task_config(self):
        """Add a new scheduled task configuration."""
        # This would open a dialog to configure scheduled task settings
        # like task creation, triggers, actions, conditions, etc.
        QMessageBox.information(self, "Add Task Config", "Scheduled task configuration dialog would open here")
        
    def edit_task_config(self):
        """Edit selected scheduled task configuration."""
        current_item = self.scheduler_tree.currentItem()
        if current_item:
            QMessageBox.information(self, "Edit Config", "Edit scheduled task configuration dialog would open here")
        
    def remove_task_config(self):
        """Remove selected scheduled task configuration."""
        current_item = self.scheduler_tree.currentItem()
        if current_item:
            reply = QMessageBox.question(
                self,
                "Remove Config",
                "Are you sure you want to remove this scheduled task configuration?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.scheduler_tree.takeTopLevelItem(
                    self.scheduler_tree.indexOfTopLevelItem(current_item)
                )
                self.save_config()
        
    def load_config(self):
        """Load scheduler configuration from config handler."""
        config = self.get_config()
        self.scheduler_tree.clear()
        
        if config:
            for task_name, task_data in config.items():
                item = QTreeWidgetItem([
                    task_name,
                    task_data.get('trigger_type', ''),
                    task_data.get('program', ''),
                    task_data.get('status', ''),
                    task_data.get('description', '')
                ])
                self.scheduler_tree.addTopLevelItem(item)
        
    def save_config(self):
        """Save current scheduler configuration."""
        config = {}
        for i in range(self.scheduler_tree.topLevelItemCount()):
            item = self.scheduler_tree.topLevelItem(i)
            task_name = item.text(0)
            config[task_name] = {
                'trigger_type': item.text(1),
                'program': item.text(2),
                'status': item.text(3),
                'description': item.text(4)
            }
        self.update_config(config)
        
    def on_config_changed(self):
        """Handle configuration changes."""
        self.load_config()
