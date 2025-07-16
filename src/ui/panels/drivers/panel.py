"""Windows Driver management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QMessageBox)
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import DriversTree
from .dialogs import StartupTypeDialog, DriverDetailsDialog
from .manager import DriverManager

class DriversPanel(BasePanel):
    """Panel for managing Windows device drivers."""
    
    def __init__(self, parent=None):
        """Initialize drivers panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = DriverManager()
        self.setup_ui()
        
        # Initial refresh
        self.refresh_drivers()
        
    def setup_ui(self):
        """Set up the panel UI."""
        layout = QVBoxLayout(self)
        
        # Create tree widget
        self.tree = DriversTree()
        layout.addWidget(self.tree)
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_driver)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_driver)
        button_layout.addWidget(self.stop_button)
        
        self.startup_button = QPushButton("Change Startup")
        self.startup_button.clicked.connect(self.change_startup)
        button_layout.addWidget(self.startup_button)
        
        self.details_button = QPushButton("Details")
        self.details_button.clicked.connect(self.view_details)
        button_layout.addWidget(self.details_button)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_drivers)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)
        
        # Connect selection change
        self.tree.itemSelectionChanged.connect(self.update_buttons)
        
        # Initial button state
        self.update_buttons()
        
    def update_buttons(self):
        """Update button enabled states based on selection."""
        has_selection = bool(self.tree.selectedItems())
        self.start_button.setEnabled(has_selection)
        self.stop_button.setEnabled(has_selection)
        self.startup_button.setEnabled(has_selection)
        self.details_button.setEnabled(has_selection)
        
    def start_driver(self):
        """Start selected driver."""
        item = self.tree.currentItem()
        if not item:
            return
            
        name = item.text(0)
        
        try:
            if self.manager.start_driver(name):
                # Update state in tree
                details = self.manager.get_driver_details(name)
                if details:
                    self.tree.update_driver(
                        item,
                        state=details['state']
                    )
                self.logger.info(f"Started driver: {name}")
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to start driver: {name}"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to start driver: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to start driver: {str(e)}"
            )
            
    def stop_driver(self):
        """Stop selected driver."""
        item = self.tree.currentItem()
        if not item:
            return
            
        name = item.text(0)
        
        reply = QMessageBox.question(
            self,
            "Confirm Stop",
            f"Are you sure you want to stop '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.manager.stop_driver(name):
                    # Update state in tree
                    details = self.manager.get_driver_details(name)
                    if details:
                        self.tree.update_driver(
                            item,
                            state=details['state']
                        )
                    self.logger.info(f"Stopped driver: {name}")
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to stop driver: {name}"
                    )
                    
            except Exception as e:
                self.logger.error(f"Failed to stop driver: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to stop driver: {str(e)}"
                )
                
    def change_startup(self):
        """Change startup type of selected driver."""
        item = self.tree.currentItem()
        if not item:
            return
            
        name, _, _, start_type, _ = self.tree.get_driver(item)
        
        dialog = StartupTypeDialog(self, name, start_type)
        if dialog.exec():
            new_type = dialog.get_startup_type()
            
            try:
                if self.manager.set_startup_type(name, new_type):
                    self.tree.update_driver(
                        item,
                        start_type=new_type
                    )
                    self.logger.info(f"Changed startup type for {name} to {new_type}")
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to change startup type for: {name}"
                    )
                    
            except Exception as e:
                self.logger.error(f"Failed to change startup type: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to change startup type: {str(e)}"
                )
                
    def view_details(self):
        """View details of selected driver."""
        item = self.tree.currentItem()
        if not item:
            return
            
        name = item.text(0)
        details = self.manager.get_driver_details(name)
        
        if details:
            dialog = DriverDetailsDialog(self, details)
            dialog.exec()
        else:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to get details for: {name}"
            )
            
    def refresh_drivers(self):
        """Refresh drivers list."""
        try:
            # Get current selection
            selected_name = None
            if self.tree.selectedItems():
                selected_name = self.tree.selectedItems()[0].text(0)
                
            # Clear and repopulate tree
            self.tree.clear_drivers()
            drivers = self.manager.get_drivers()
            
            for driver in drivers:
                self.tree.add_driver(
                    driver['name'],
                    driver['display_name'],
                    driver['manufacturer'],
                    driver['start_type'],
                    driver['state']
                )
                
            # Restore selection if driver still exists
            if selected_name:
                item = self.tree.find_driver(selected_name)
                if item:
                    item.setSelected(True)
                    
            self.logger.debug("Refreshed drivers list")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh drivers: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to refresh drivers: {str(e)}"
            )
