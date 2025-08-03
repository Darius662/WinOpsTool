"""Windows Applications management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QMessageBox, QFileDialog, QTabWidget, QInputDialog)
from PyQt6.QtCore import Qt, QTimer
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import ProcessesTree, StartupTree
from .manager import ProcessManager, StartupManager

class ProcessesTab(QWidget):
    """Tab for managing running processes."""
    
    def __init__(self, parent=None):
        """Initialize processes tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = ProcessManager()
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Processes tree
        self.processes_tree = ProcessesTree()
        layout.addWidget(self.processes_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.end_btn = QPushButton("End Process")
        self.end_tree_btn = QPushButton("End Process Tree")
        self.refresh_btn = QPushButton("Refresh")
        
        for btn in [self.end_btn, self.end_tree_btn, self.refresh_btn]:
            button_layout.addWidget(btn)
            
        layout.addLayout(button_layout)
        
        # Connect signals
        self.end_btn.clicked.connect(self.end_process)
        self.end_tree_btn.clicked.connect(self.end_process_tree)
        self.refresh_btn.clicked.connect(self.refresh_processes)
        
        # Auto-refresh timer removed - refresh only happens manually via button
        # self.refresh_timer = QTimer()
        # self.refresh_timer.timeout.connect(self.refresh_processes)
        # Timer not started - refresh only on manual button click
        
        # Initial load
        self.refresh_processes()
        
    def refresh_processes(self):
        """Refresh the processes list."""
        try:
            self.processes_tree.clear_processes()
            processes = self.manager.get_processes()
            
            for proc in processes:
                self.processes_tree.add_process(
                    proc['name'],
                    proc['pid'],
                    proc['status'],
                    proc['cpu_percent'],
                    proc['memory'],
                    proc['username'],
                    proc['create_time']
                )
                
            self.logger.info("Refreshed processes list")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh processes: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to refresh processes list")
            
    def end_process(self):
        """End selected process."""
        try:
            current_item = self.processes_tree.currentItem()
            if not current_item:
                return
                
            process = self.processes_tree.get_process(current_item)
            
            reply = QMessageBox.question(
                self,
                "Confirm End Process",
                f"Are you sure you want to end process '{process['name']}' (PID {process['pid']})?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.manager.end_process(process['pid']):
                    self.refresh_processes()
                else:
                    QMessageBox.critical(self, "Error", f"Failed to end process {process['pid']}")
                    
        except Exception as e:
            self.logger.error(f"Failed to end process: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to end process: {str(e)}")
            
    def end_process_tree(self):
        """End selected process and its children."""
        try:
            current_item = self.processes_tree.currentItem()
            if not current_item:
                return
                
            process = self.processes_tree.get_process(current_item)
            
            reply = QMessageBox.question(
                self,
                "Confirm End Process Tree",
                f"Are you sure you want to end process '{process['name']}' (PID {process['pid']}) and all its children?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.manager.end_process_tree(process['pid']):
                    self.refresh_processes()
                else:
                    QMessageBox.critical(self, "Error", f"Failed to end process tree {process['pid']}")
                    
        except Exception as e:
            self.logger.error(f"Failed to end process tree: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to end process tree: {str(e)}")

class StartupTab(QWidget):
    """Tab for managing startup applications."""
    
    def __init__(self, parent=None):
        """Initialize startup tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = StartupManager()
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Startup tree
        self.startup_tree = StartupTree()
        layout.addWidget(self.startup_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add")
        self.remove_btn = QPushButton("Remove")
        self.refresh_btn = QPushButton("Refresh")
        
        for btn in [self.add_btn, self.remove_btn, self.refresh_btn]:
            button_layout.addWidget(btn)
            
        layout.addLayout(button_layout)
        
        # Connect signals
        self.add_btn.clicked.connect(self.add_startup)
        self.remove_btn.clicked.connect(self.remove_startup)
        self.refresh_btn.clicked.connect(self.refresh_startup)
        
        # Initial load
        self.refresh_startup()
        
    def refresh_startup(self):
        """Refresh the startup items list."""
        try:
            # Store current selection
            current_item = self.startup_tree.currentItem()
            current_name = current_item.text(0) if current_item else None
            
            # Clear tree
            self.startup_tree.clear_startup_items()
            
            # Get startup items
            startup_items = self.manager.get_startup_items()
            
            # Add items to tree
            for item in startup_items:
                tree_item = self.startup_tree.add_startup_item(
                    item['name'],
                    item['command'],
                    item['location'],
                    item['type']
                )
                
                # Check if this item is marked as imported config in the parent panel
                if hasattr(self.parent(), 'is_imported_config_item') and self.parent().is_imported_config_item(f"applications:startup_item:{item['name']}"):
                    self.startup_tree.highlight_item(tree_item)
            
            # Add virtual startup items from imported config
            if hasattr(self.parent(), 'imported_config_items'):
                self.add_virtual_startup_items()
                
            # Restore selection
            if current_name:
                items = self.startup_tree.findItems(current_name, Qt.MatchFlag.MatchExactly, 0)
                if items:
                    self.startup_tree.setCurrentItem(items[0])
                    
            self.logger.info("Refreshed startup items list")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh startup items: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to refresh startup items list")
            
    def add_virtual_startup_items(self):
        """Add virtual startup items from imported configuration."""
        try:
            # Get parent panel (ApplicationsPanel)
            parent_panel = self.parent()
            if not hasattr(parent_panel, 'imported_config_items'):
                return
                
            # Get existing startup items for comparison
            existing_items = {item['name']: item for item in self.manager.get_startup_items()}
            
            # Check for virtual startup items to add
            for item_id in parent_panel.imported_config_items:
                # Only process startup items
                if not item_id.startswith('applications:startup_item:'):
                    continue
                    
                # Extract name from item_id
                name = item_id.replace('applications:startup_item:', '')
                
                # Skip if item already exists in system
                if name in existing_items:
                    continue
                    
                # Get config data for this virtual item
                if not hasattr(parent_panel, 'current_config') or not parent_panel.current_config:
                    continue
                    
                config = parent_panel.current_config
                if 'applications' not in config or 'startup_items' not in config['applications']:
                    continue
                    
                # Find matching item in config
                for item_config in config['applications']['startup_items']:
                    if item_config.get('name') == name:
                        # Add virtual startup item
                        self.startup_tree.add_virtual_startup_item(
                            name,
                            item_config.get('path', 'Unknown'),
                            item_config.get('location', 'Current User'),
                            'Startup'  # Default type
                        )
                        break
                        
            self.logger.info("Added virtual startup items from imported configuration")
            
        except Exception as e:
            self.logger.error(f"Failed to add virtual startup items: {str(e)}")
            # Don't show error message to user, just log it
            
    def add_startup(self):
        """Add a new startup item."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Program",
                "",
                "Programs (*.exe);;All Files (*.*)"
            )
            
            if file_path:
                name = QInputDialog.getText(
                    self,
                    "Add Startup Item",
                    "Enter name for startup item:",
                    text=os.path.splitext(os.path.basename(file_path))[0]
                )[0]
                
                if name:
                    location = QInputDialog.getItem(
                        self,
                        "Add Startup Item",
                        "Select startup location:",
                        ["Current User", "All Users"],
                        0,
                        False
                    )[0]
                    
                    if self.manager.add_startup_item(name, file_path, location):
                        self.refresh_startup()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to add startup item")
                        
        except Exception as e:
            self.logger.error(f"Failed to add startup item: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add startup item: {str(e)}")
            
    def remove_startup(self):
        """Remove selected startup item."""
        try:
            current_item = self.startup_tree.currentItem()
            if not current_item:
                return
                
            item = self.startup_tree.get_startup_item(current_item)
            
            reply = QMessageBox.question(
                self,
                "Confirm Remove",
                f"Are you sure you want to remove startup item '{item['name']}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.manager.remove_startup_item(
                    item['name'],
                    item['location'],
                    item['type']
                ):
                    self.refresh_startup()
                else:
                    QMessageBox.critical(self, "Error", f"Failed to remove startup item {item['name']}")
                    
        except Exception as e:
            self.logger.error(f"Failed to remove startup item: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to remove startup item: {str(e)}")

class ApplicationsPanel(BasePanel):
    """Panel for managing running processes and startup applications."""
    
    def __init__(self, parent=None):
        """Initialize applications panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
        # Initialize imported config items
        self.imported_config_items = set()
        
    def setup_ui(self):
        """Initialize the UI components."""
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.processes_tab = ProcessesTab()
        self.startup_tab = StartupTab()
        
        # Add tabs
        self.tab_widget.addTab(self.processes_tab, "Processes")
        self.tab_widget.addTab(self.startup_tab, "Startup")
        
        # Add tab widget to main layout
        self.add_widget(self.tab_widget)
        
    def setup_connections(self):
        """Set up signal/slot connections."""
        pass  # All connections are set up in the tabs
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed."""
        if hasattr(self, 'processes_tab'):
            self.processes_tab.refresh_timer.stop()
            
    def apply_config(self, config):
        """Apply configuration to the panel.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if configuration was applied successfully, False otherwise
        """
        self.logger.info("Applying applications panel configuration")
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Process configuration
            if 'applications' not in config:
                self.logger.warning("No applications panel configuration found")
                return False
                
            applications_config = config['applications']
            success = True
            
            # Apply startup items configuration if available
            if 'startup_items' in applications_config and isinstance(applications_config['startup_items'], list):
                self.logger.info(f"Found {len(applications_config['startup_items'])} startup items in configuration")
                
                # Process each startup item
                for item_config in applications_config['startup_items']:
                    if not isinstance(item_config, dict):
                        self.logger.warning("Skipping invalid startup item configuration")
                        continue
                        
                    # Check required fields
                    if 'name' not in item_config or 'path' not in item_config:
                        self.logger.warning("Skipping startup item without required fields")
                        continue
                        
                    name = item_config['name']
                    path = item_config['path']
                    location = item_config.get('location', 'Current User')
                    
                    # Add startup item
                    if not self.startup_tab.manager.add_startup_item(name, path, location):
                        self.logger.warning(f"Failed to add startup item: {name}")
                        success = False
                
                # Refresh startup items list
                self.startup_tab.refresh_startup()
                
                # Clear imported config items since they've been applied
                self.imported_config_items.clear()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error applying applications panel configuration: {str(e)}")
            return False
            
    def export_config(self):
        """Export panel configuration.
        
        Returns:
            dict: Dictionary containing panel configuration
        """
        self.logger.info("Exporting applications panel configuration")
        
        try:
            # Get startup items
            startup_items = []
            
            # Get startup items from manager
            for item in self.startup_tab.manager.get_startup_items():
                startup_items.append({
                    'name': item['name'],
                    'path': item['command'],
                    'location': item['location']
                })
            
            # Create configuration dictionary
            config = {
                'applications': {
                    'startup_items': startup_items
                }
            }
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error exporting applications panel configuration: {str(e)}")
            return {'applications': {}}
            
    def mark_config_items(self, config):
        """Mark items from configuration for highlighting without applying changes.
        
        This method identifies and marks startup items from the configuration
        that would be modified by apply_config(), but does not actually
        apply any changes to the system. Items will be visually highlighted in the UI.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if items were marked successfully, False otherwise
        """
        self.logger.info("Marking applications panel configuration items")
        
        # Clear previous imported items
        self.imported_config_items.clear()
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Check if applications section exists
            if 'applications' not in config:
                self.logger.warning("No applications panel configuration found")
                return False
                
            # Store the current configuration for use in virtual startup items
            self.current_config = config
                
            applications_config = config['applications']
            
            # Process startup items configuration if available
            if 'startup_items' in applications_config and isinstance(applications_config['startup_items'], list):
                self.logger.info(f"Found {len(applications_config['startup_items'])} startup items in configuration")
                
                # Get existing startup items for comparison
                existing_items = {item['name']: item for item in self.startup_tab.manager.get_startup_items()}
                
                # Process each startup item
                for item_config in applications_config['startup_items']:
                    if not isinstance(item_config, dict):
                        self.logger.warning("Skipping invalid startup item configuration")
                        continue
                        
                    # Check required fields
                    if 'name' not in item_config or 'path' not in item_config:
                        self.logger.warning("Skipping startup item without required fields")
                        continue
                        
                    name = item_config['name']
                    
                    # Mark this startup item as imported from config for highlighting
                    self.mark_as_imported_config(f"applications:startup_item:{name}")
                    
                # Refresh startup items list to show highlighting
                self.startup_tab.refresh_startup()
                
                return True
                
            # If no specific configurations were found, return False
            self.logger.warning("No startup items configuration found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error marking applications panel configuration items: {str(e)}")
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
