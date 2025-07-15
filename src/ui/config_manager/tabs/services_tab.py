"""Services configuration tab."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox, QComboBox)
from .base_tab import BaseConfigTab

class ServicesTab(BaseConfigTab):
    """Tab for configuring Windows services."""
    
    # Service startup types
    STARTUP_TYPES = [
        "Automatic",
        "Manual",
        "Disabled"
    ]
    
    # Service states
    SERVICE_STATES = [
        "Running",
        "Stopped"
    ]
    
    def __init__(self, config_handler):
        super().__init__(config_handler, "services")
        
    def setup_ui(self):
        """Set up the tab's user interface."""
        # Services tree
        tree_label = QLabel("Services Configuration")
        self.layout.addWidget(tree_label)
        
        self.services_tree = QTreeWidget()
        self.services_tree.setHeaderLabels([
            "Service Name",
            "Display Name",
            "Startup Type",
            "State",
            "Description"
        ])
        self.services_tree.setColumnWidth(0, 150)
        self.services_tree.setColumnWidth(1, 200)
        self.services_tree.setColumnWidth(4, 250)
        self.layout.addWidget(self.services_tree)
        
        # Input fields
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        # Service name
        name_layout = QHBoxLayout()
        name_label = QLabel("Service Name:")
        name_layout.addWidget(name_label)
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        input_layout.addLayout(name_layout)
        
        # Display name
        display_layout = QHBoxLayout()
        display_label = QLabel("Display Name:")
        display_layout.addWidget(display_label)
        self.display_edit = QLineEdit()
        display_layout.addWidget(self.display_edit)
        input_layout.addLayout(display_layout)
        
        # Startup type
        startup_layout = QHBoxLayout()
        startup_label = QLabel("Startup Type:")
        startup_layout.addWidget(startup_label)
        self.startup_combo = QComboBox()
        self.startup_combo.addItems(self.STARTUP_TYPES)
        startup_layout.addWidget(self.startup_combo)
        input_layout.addLayout(startup_layout)
        
        # State
        state_layout = QHBoxLayout()
        state_label = QLabel("State:")
        state_layout.addWidget(state_label)
        self.state_combo = QComboBox()
        self.state_combo.addItems(self.SERVICE_STATES)
        state_layout.addWidget(self.state_combo)
        input_layout.addLayout(state_layout)
        
        # Description
        desc_layout = QHBoxLayout()
        desc_label = QLabel("Description:")
        desc_layout.addWidget(desc_label)
        self.desc_edit = QLineEdit()
        desc_layout.addWidget(self.desc_edit)
        input_layout.addLayout(desc_layout)
        
        self.layout.addWidget(input_widget)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Service")
        add_button.clicked.connect(self.add_service)
        buttons_layout.addWidget(add_button)
        
        delete_button = QPushButton("Delete Service")
        delete_button.clicked.connect(self.delete_service)
        buttons_layout.addWidget(delete_button)
        
        self.layout.addLayout(buttons_layout)
        
    def add_service(self):
        """Add a service to the tree."""
        name = self.name_edit.text().strip()
        display = self.display_edit.text().strip()
        startup = self.startup_combo.currentText()
        state = self.state_combo.currentText()
        description = self.desc_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Warning", "Service name is required.")
            return
            
        item = QTreeWidgetItem([
            name,
            display,
            startup,
            state,
            description
        ])
        self.services_tree.addTopLevelItem(item)
        
        # Clear input fields
        self.name_edit.clear()
        self.display_edit.clear()
        self.desc_edit.clear()
        
        self.update_config_from_ui()
        
    def delete_service(self):
        """Delete selected service."""
        item = self.services_tree.currentItem()
        if item:
            self.services_tree.takeTopLevelItem(
                self.services_tree.indexOfTopLevelItem(item)
            )
            self.update_config_from_ui()
            
    def update_config_from_ui(self):
        """Update configuration from UI elements."""
        config = []
        
        for i in range(self.services_tree.topLevelItemCount()):
            item = self.services_tree.topLevelItem(i)
            config.append({
                "name": item.text(0),
                "display_name": item.text(1),
                "startup": item.text(2).lower(),
                "state": item.text(3).lower(),
                "description": item.text(4)
            })
            
        self.update_config(config)
        
    def on_config_changed(self):
        """Handle configuration changes."""
        config = self.get_config()
        
        # Clear existing items
        self.services_tree.clear()
        
        # Add items from config
        for service in config:
            item = QTreeWidgetItem([
                service["name"],
                service.get("display_name", ""),
                service["startup"].capitalize(),
                service["state"].capitalize(),
                service.get("description", "")
            ])
            self.services_tree.addTopLevelItem(item)
