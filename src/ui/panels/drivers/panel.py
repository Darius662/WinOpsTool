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
        
        # Initialize imported config items
        self.imported_config_items = set()
        self.current_config = None
        
        # Defer initial refresh
        # This will prevent blocking the UI during startup
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(3000, self.delayed_start)
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Use the main_layout from BasePanel instead of creating a new layout
        layout = self.main_layout
        
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
    
    def delayed_start(self):
        """Delayed initialization to prevent blocking the UI during startup."""
        self.logger.info('Starting delayed initialization of DriversPanel')
        self.refresh_drivers()
        self.logger.info('DriversPanel initialization complete')
        
    def setup_connections(self):
        """Set up signal-slot connections."""
        # Connections already set up in setup_ui method
        # This method is required by BasePanel but implementation is kept here
        # for consistency with the BasePanel interface
        pass
        
    def apply_config(self, config):
        """Apply configuration to the panel.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if configuration was applied successfully, False otherwise
        """
        self.logger.info("Applying drivers panel configuration")
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Process configuration
            if 'drivers' not in config:
                self.logger.warning("No drivers panel configuration found")
                return False
                
            drivers_config = config['drivers']
            success = True
            
            # Apply driver startup type configuration if available
            if 'driver_settings' in drivers_config and isinstance(drivers_config['driver_settings'], list):
                self.logger.info(f"Found {len(drivers_config['driver_settings'])} driver settings in configuration")
                
                # Process each driver setting
                for driver_config in drivers_config['driver_settings']:
                    if not isinstance(driver_config, dict):
                        self.logger.warning("Skipping invalid driver configuration")
                        continue
                        
                    # Check required fields
                    if 'name' not in driver_config:
                        self.logger.warning("Skipping driver setting without name")
                        continue
                        
                    name = driver_config['name']
                    
                    # Apply startup type if specified
                    if 'start_type' in driver_config:
                        start_type = driver_config['start_type']
                        if not self.manager.set_startup_type(name, start_type):
                            self.logger.warning(f"Failed to set startup type for driver: {name}")
                            success = False
                    
                    # Apply state if specified (start/stop)
                    if 'state' in driver_config:
                        state = driver_config['state']
                        if state.lower() == 'running':
                            if not self.manager.start_driver(name):
                                self.logger.warning(f"Failed to start driver: {name}")
                                success = False
                        elif state.lower() == 'stopped':
                            if not self.manager.stop_driver(name):
                                self.logger.warning(f"Failed to stop driver: {name}")
                                success = False
                
                # Refresh drivers list to reflect changes
                self.refresh_drivers()
                
                # Clear imported config items since they've been applied
                self.imported_config_items.clear()
                self.current_config = None
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error applying drivers panel configuration: {str(e)}")
            return False
            
    def export_config(self):
        """Export panel configuration.
        
        Returns:
            dict: Dictionary containing panel configuration
        """
        self.logger.info("Exporting drivers panel configuration")
        
        try:
            # Get driver settings
            driver_settings = []
            
            # Get all drivers from the tree
            for i in range(self.tree.topLevelItemCount()):
                item = self.tree.topLevelItem(i)
                name, _, _, start_type, state = self.tree.get_driver(item)
                
                # Only export non-virtual drivers
                if not self.tree.is_virtual_item(item):
                    driver_settings.append({
                        'name': name,
                        'start_type': start_type,
                        'state': state
                    })
            
            # Create configuration dictionary
            config = {
                'drivers': {
                    'driver_settings': driver_settings
                }
            }
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error exporting drivers panel configuration: {str(e)}")
            return {'drivers': {}}
            
    def mark_config_items(self, config):
        """Mark items from configuration for highlighting without applying changes.
        
        This method identifies and marks driver settings from the configuration
        that would be modified by apply_config(), but does not actually
        apply any changes to the system. Items will be visually highlighted in the UI.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if items were marked successfully, False otherwise
        """
        self.logger.info("Marking drivers panel configuration items")
        
        # Clear previous imported items
        self.imported_config_items.clear()
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Check if drivers section exists
            if 'drivers' not in config:
                self.logger.warning("No drivers panel configuration found")
                return False
                
            # Store the current configuration for use in virtual driver items
            self.current_config = config
                
            drivers_config = config['drivers']
            
            # Process driver settings configuration if available
            if 'driver_settings' in drivers_config and isinstance(drivers_config['driver_settings'], list):
                self.logger.info(f"Found {len(drivers_config['driver_settings'])} driver settings in configuration")
                
                # Get existing drivers for comparison
                existing_drivers = {}
                for i in range(self.tree.topLevelItemCount()):
                    item = self.tree.topLevelItem(i)
                    name, display_name, manufacturer, start_type, state = self.tree.get_driver(item)
                    existing_drivers[name] = {
                        'item': item,
                        'display_name': display_name,
                        'manufacturer': manufacturer,
                        'start_type': start_type,
                        'state': state
                    }
                
                # Process each driver setting
                for driver_config in drivers_config['driver_settings']:
                    if not isinstance(driver_config, dict):
                        self.logger.warning("Skipping invalid driver configuration")
                        continue
                        
                    # Check required fields
                    if 'name' not in driver_config:
                        self.logger.warning("Skipping driver setting without name")
                        continue
                        
                    name = driver_config['name']
                    
                    # Mark this driver as imported from config for highlighting
                    self.mark_as_imported_config(f"drivers:driver:{name}")
                    
                    # If driver exists, highlight it
                    if name in existing_drivers:
                        item = existing_drivers[name]['item']
                        self.tree.highlight_item(item)
                    else:
                        # Add virtual driver if it doesn't exist in the system
                        self.add_virtual_driver(driver_config)
                
                return True
                
            # If no specific configurations were found, return False
            self.logger.warning("No driver settings configuration found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error marking drivers panel configuration items: {str(e)}")
            return False
    
    def mark_as_imported_config(self, item):
        """Mark an item as imported from config for highlighting.
        
        Args:
            item: Item to mark
        """
        self.imported_config_items.add(item)
        
    def is_imported_config_item(self, item):
        """Check if an item is marked as imported from config.
        
        Args:
            item: Item to check
            
        Returns:
            bool: True if item is marked as imported, False otherwise
        """
        return item in self.imported_config_items
        
    def add_virtual_driver(self, driver_config):
        """Add a virtual driver from imported configuration.
        
        Args:
            driver_config: Dictionary containing driver configuration
            
        Returns:
            QTreeWidgetItem: Created tree item or None if failed
        """
        try:
            name = driver_config['name']
            
            # Use provided values or defaults
            display_name = driver_config.get('display_name', name)
            manufacturer = driver_config.get('manufacturer', 'Unknown')
            start_type = driver_config.get('start_type', 'Auto')
            
            # Add virtual driver to tree
            item = self.tree.add_virtual_driver(
                name,
                display_name,
                manufacturer,
                start_type
            )
            
            self.logger.info(f"Added virtual driver: {name}")
            return item
            
        except Exception as e:
            self.logger.error(f"Failed to add virtual driver: {str(e)}")
            return None
