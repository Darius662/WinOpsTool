"""Windows Services management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLineEdit, QLabel, QMessageBox)
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import ServicesTree
from .dialogs import StartupTypeDialog
from .manager import ServiceManager

class ServicesPanel(BasePanel):
    """Panel for managing Windows Services."""
    
    def __init__(self, parent=None):
        """Initialize services panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = ServiceManager()
        self.setup_ui()
        self.refresh_services()
        
    def setup_ui(self):
        """Set up the panel UI."""
        layout = QVBoxLayout(self)
        
        # Search controls
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.filter_services)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        
        # Action buttons
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_service)
        search_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_service)
        search_layout.addWidget(self.stop_button)
        
        self.restart_button = QPushButton("Restart")
        self.restart_button.clicked.connect(self.restart_service)
        search_layout.addWidget(self.restart_button)
        
        self.startup_button = QPushButton("Startup Type")
        self.startup_button.clicked.connect(self.change_startup)
        search_layout.addWidget(self.startup_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_services)
        search_layout.addWidget(self.refresh_button)
        
        layout.addLayout(search_layout)
        
        # Services tree
        self.services_tree = ServicesTree()
        self.services_tree.itemSelectionChanged.connect(self.update_buttons)
        layout.addWidget(self.services_tree)
        
        # Initial button state
        self.update_buttons()
        
    def update_buttons(self):
        """Update button enabled states based on selection."""
        has_selection = bool(self.services_tree.selectedItems())
        self.start_button.setEnabled(has_selection)
        self.stop_button.setEnabled(has_selection)
        self.restart_button.setEnabled(has_selection)
        self.startup_button.setEnabled(has_selection)
        
    def refresh_services(self):
        """Refresh the services list."""
        try:
            # Clear and repopulate tree
            self.services_tree.clear_services()
            services = self.manager.get_services()
            
            for service in services:
                self.services_tree.add_service(
                    service['name'],
                    service['display_name'],
                    service['description'],
                    service['state'],
                    service['start_type'],
                    service['path'],
                    service['account']
                )
                
            # Reapply filter if search text exists
            if self.search_edit.text():
                self.filter_services(self.search_edit.text())
                
            self.logger.info("Refreshed services list")
        except Exception as e:
            self.logger.error(f"Failed to refresh services: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to refresh services list")
            
    def filter_services(self, text):
        """Filter services by name or display name.
        
        Args:
            text: Search text
        """
        for i in range(self.services_tree.topLevelItemCount()):
            item = self.services_tree.topLevelItem(i)
            name = item.text(0).lower()
            display_name = item.text(1).lower()
            search = text.lower()
            item.setHidden(search not in name and search not in display_name)
            
    def start_service(self):
        """Start selected service."""
        item = self.services_tree.selectedItems()[0]
        name = item.text(0)
        
        if self.manager.start_service(name):
            self.refresh_services()
            # Find and select the service again
            item = self.services_tree.find_service(name)
            if item:
                item.setSelected(True)
        else:
            QMessageBox.critical(self, "Error", f"Failed to start service '{name}'")
            
    def stop_service(self):
        """Stop selected service."""
        item = self.services_tree.selectedItems()[0]
        name = item.text(0)
        
        reply = QMessageBox.question(
            self,
            "Confirm Stop",
            f"Are you sure you want to stop service '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.manager.stop_service(name):
                self.refresh_services()
                # Find and select the service again
                item = self.services_tree.find_service(name)
                if item:
                    item.setSelected(True)
            else:
                QMessageBox.critical(self, "Error", f"Failed to stop service '{name}'")
                
    def restart_service(self):
        """Restart selected service."""
        item = self.services_tree.selectedItems()[0]
        name = item.text(0)
        
        reply = QMessageBox.question(
            self,
            "Confirm Restart",
            f"Are you sure you want to restart service '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.manager.restart_service(name):
                self.refresh_services()
                # Find and select the service again
                item = self.services_tree.find_service(name)
                if item:
                    item.setSelected(True)
            else:
                QMessageBox.critical(self, "Error", f"Failed to restart service '{name}'")
                
    def change_startup(self):
        """Change startup type of selected service."""
        item = self.services_tree.selectedItems()[0]
        service = self.services_tree.get_service(item)
        
        dialog = StartupTypeDialog(self, service['start_type'])
        if dialog.exec():
            start_type = dialog.get_startup_type()
            if self.manager.set_startup_type(service['name'], start_type):
                self.refresh_services()
                # Find and select the service again
                item = self.services_tree.find_service(service['name'])
                if item:
                    item.setSelected(True)
            else:
                QMessageBox.critical(self, "Error", f"Failed to change startup type for '{service['name']}'")
