"""Windows Package management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLineEdit, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import PackagesTree
from .dialogs import WingetSearchDialog
from .manager import PackageManager

class ProgramsWorker(QThread):
    """Background worker for loading programs."""
    programs_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
    def run(self):
        """Load programs in background thread."""
        try:
            programs = self.manager.get_installed_programs()
            self.programs_loaded.emit(programs)
        except Exception as e:
            self.error_occurred.emit(str(e))

class PackagesPanel(BasePanel):
    """Panel for managing Windows installed programs and packages."""
    
    def __init__(self, parent=None):
        """Initialize packages panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = PackageManager()
        self.worker = None
        
        # Initialize imported config items tracking
        self.imported_config_items = set()
        self.current_config = None
        
        # Defer initial refresh with longer delay to reduce resource contention
        # This will prevent blocking the UI during startup
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(5000, self.delayed_start)
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Use the main_layout from BasePanel instead of creating a new layout
        layout = self.main_layout
        
        # Search controls
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.filter_programs)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        
        # Action buttons
        self.uninstall_button = QPushButton("Uninstall")
        self.uninstall_button.clicked.connect(self.uninstall_program)
        search_layout.addWidget(self.uninstall_button)
        
        self.install_button = QPushButton("Install (Winget)")
        self.install_button.clicked.connect(self.install_package)
        search_layout.addWidget(self.install_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_programs)
        search_layout.addWidget(self.refresh_button)
        
        layout.addLayout(search_layout)
        
        # Programs tree
        self.programs_tree = PackagesTree()
        self.programs_tree.itemSelectionChanged.connect(self.update_buttons)
        layout.addWidget(self.programs_tree)
        
        # Initial button state
        self.update_buttons()
        
    def update_buttons(self):
        """Update button enabled states based on selection."""
        has_selection = bool(self.programs_tree.selectedItems())
        self.uninstall_button.setEnabled(has_selection)
        
    def refresh_programs(self):
        """Refresh the programs list using background thread."""
        try:
            # Don't start new worker if one is already running
            if self.worker and self.worker.isRunning():
                return
                
            # Clear tree and show loading state
            self.programs_tree.clear_programs()
            
            # Create and start worker thread
            self.worker = ProgramsWorker(self.manager)
            self.worker.programs_loaded.connect(self.on_programs_loaded)
            self.worker.error_occurred.connect(self.on_programs_error)
            self.worker.start()
            
            self.logger.info("Started loading programs in background")
        except Exception as e:
            self.logger.error(f"Failed to start programs refresh: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to start programs refresh")
            
    def on_programs_loaded(self, programs):
        """Handle programs loaded from background thread."""
        try:
            for program in programs:
                self.programs_tree.add_program(
                    program['name'],
                    program['version'],
                    program['publisher'],
                    program['install_date'],
                    program['install_location'],
                    program['registry_key']
                )
                
            # Reapply filter if search text exists
            if self.search_edit.text():
                self.filter_programs(self.search_edit.text())
                
            self.logger.info(f"Loaded {len(programs)} programs successfully")
        except Exception as e:
            self.logger.error(f"Failed to populate programs tree: {str(e)}")
            
    def on_programs_error(self, error_msg):
        """Handle error from background thread."""
        self.logger.error(f"Failed to load programs: {error_msg}")
        QMessageBox.critical(self, "Error", f"Failed to load programs: {error_msg}")
            
    def filter_programs(self, text):
        """Filter programs by name or publisher.
        
        Args:
            text: Search text
        """
        for i in range(self.programs_tree.topLevelItemCount()):
            item = self.programs_tree.topLevelItem(i)
            name = item.text(0).lower()
            publisher = item.text(2).lower()
            search = text.lower()
            item.setHidden(search not in name and search not in publisher)
            
    def uninstall_program(self):
        """Uninstall selected program."""
        item = self.programs_tree.selectedItems()[0]
        program = self.programs_tree.get_program(item)
        
        reply = QMessageBox.question(
            self,
            "Confirm Uninstall",
            f"Are you sure you want to uninstall '{program['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Get uninstall string from registry
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    f'Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{program["registry_key"]}'
                )
                uninstall_string = winreg.QueryValueEx(key, 'UninstallString')[0]
                winreg.CloseKey(key)
                
                if self.manager.uninstall_program(uninstall_string):
                    self.refresh_programs()
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to uninstall '{program['name']}'"
                    )
                    
            except WindowsError as e:
                self.logger.error(f"Failed to get uninstall string: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to get uninstall information for '{program['name']}'"
                )
                
    def install_package(self):
        """Install a winget package."""
        dialog = WingetSearchDialog(self)
        
        # Override search function
        def search():
            try:
                packages = self.manager.get_winget_packages()
                dialog.set_packages(packages)
            except Exception as e:
                self.logger.error(f"Failed to search winget packages: {str(e)}")
                QMessageBox.critical(
                    dialog,
                    "Error",
                    "Failed to search winget packages"
                )
                
        dialog.search_packages = search
        
        if dialog.exec():
            package_id = dialog.get_selected_package()
            if package_id:
                try:
                    if self.manager.install_winget_package(package_id):
                        self.refresh_programs()
                    else:
                        QMessageBox.critical(
                            self,
                            "Error",
                            f"Failed to install package '{package_id}'"
                        )
                except Exception as e:
                    self.logger.error(f"Failed to install package: {str(e)}")
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to install package: {str(e)}"
                    )
                    
    def delayed_start(self):
        """Delayed initialization to prevent blocking the UI during startup."""
        self.logger.info('Starting delayed initialization of PackagesPanel')
        self.refresh_programs()
        self.logger.info('PackagesPanel initialization complete')
        
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
        self.logger.info("Applying packages panel configuration")
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Process configuration
            if 'packages' not in config:
                self.logger.warning("No packages panel configuration found")
                return False
                
            packages_config = config['packages']
            success = True
            
            # Apply package entries if available
            if 'entries' in packages_config and isinstance(packages_config['entries'], list):
                self.logger.info(f"Found {len(packages_config['entries'])} package entries in configuration")
                
                # Process each package entry
                for pkg_entry in packages_config['entries']:
                    if not isinstance(pkg_entry, dict):
                        self.logger.warning("Skipping invalid package entry")
                        continue
                        
                    # Check required fields
                    if 'name' not in pkg_entry or 'id' not in pkg_entry:
                        self.logger.warning("Skipping package entry without name or id")
                        continue
                        
                    package_id = pkg_entry['id']
                    
                    # Install package using winget
                    try:
                        if not self.manager.install_winget_package(package_id):
                            self.logger.warning(f"Failed to install package {package_id}")
                            success = False
                    except Exception as e:
                        self.logger.error(f"Error installing package {package_id}: {str(e)}")
                        success = False
                
                # Refresh programs list to reflect changes
                self.refresh_programs()
            
            # Clear imported config items since they've been applied
            self.imported_config_items.clear()
            self.current_config = None
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error applying packages panel configuration: {str(e)}")
            return False
            
    def export_config(self):
        """Export panel configuration.
        
        Returns:
            dict: Dictionary containing panel configuration
        """
        self.logger.info("Exporting packages panel configuration")
        
        try:
            # Get installed programs
            entries = []
            
            # Get all programs from the tree
            for i in range(self.programs_tree.topLevelItemCount()):
                item = self.programs_tree.topLevelItem(i)
                
                # Skip virtual items
                if self.programs_tree.is_virtual_item(item):
                    continue
                    
                program = self.programs_tree.get_program(item)
                
                # Add to entries
                entries.append({
                    'name': program['name'],
                    'version': program['version'],
                    'publisher': program['publisher'],
                    # Use registry key as ID for reinstallation
                    'id': program['registry_key']
                })
            
            # Create configuration dictionary
            config = {
                'packages': {
                    'entries': entries
                }
            }
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error exporting packages panel configuration: {str(e)}")
            return {'packages': {}}
            
    def mark_config_items(self, config):
        """Mark items from configuration for highlighting without applying changes.
        
        This method identifies and marks package entries from the configuration
        that would be modified by apply_config(), but does not actually
        apply any changes to the system. Items will be visually highlighted in the UI.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if items were marked successfully, False otherwise
        """
        self.logger.info("Marking packages panel configuration items")
        
        # Clear previous imported items
        self.imported_config_items.clear()
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Check if packages section exists
            if 'packages' not in config:
                self.logger.warning("No packages panel configuration found")
                return False
                
            # Store the current configuration for use in virtual package entries
            self.current_config = config
                
            packages_config = config['packages']
            
            # Process package entries if available
            if 'entries' in packages_config and isinstance(packages_config['entries'], list):
                self.logger.info(f"Found {len(packages_config['entries'])} package entries in configuration")
                
                # Get existing programs for comparison
                existing_programs = {}
                for i in range(self.programs_tree.topLevelItemCount()):
                    item = self.programs_tree.topLevelItem(i)
                    program = self.programs_tree.get_program(item)
                    # Use name as key for comparison
                    existing_programs[program['name'].lower()] = {
                        'item': item,
                        'program': program
                    }
                
                # Process each package entry
                for pkg_entry in packages_config['entries']:
                    if not isinstance(pkg_entry, dict):
                        self.logger.warning("Skipping invalid package entry")
                        continue
                        
                    # Check required fields
                    if 'name' not in pkg_entry:
                        self.logger.warning("Skipping package entry without name")
                        continue
                        
                    name = pkg_entry['name']
                    
                    # Mark this package as imported from config for highlighting
                    self.mark_as_imported_config(f"packages:entry:{name}")
                    
                    # If package exists, highlight it
                    if name.lower() in existing_programs:
                        item = existing_programs[name.lower()]['item']
                        self.programs_tree.highlight_item(item)
                    else:
                        # Add virtual package if it doesn't exist in the system
                        self.add_virtual_package(pkg_entry)
                
                return True
                
            # If no specific configurations were found, return False
            self.logger.warning("No package entries configuration found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error marking packages panel configuration items: {str(e)}")
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
        
    def add_virtual_package(self, pkg_entry):
        """Add a virtual package from imported configuration.
        
        Args:
            pkg_entry: Dictionary containing package configuration
            
        Returns:
            QTreeWidgetItem: Created tree item or None if failed
        """
        try:
            name = pkg_entry['name']
            
            # Use provided values or defaults
            version = pkg_entry.get('version', 'Unknown')
            publisher = pkg_entry.get('publisher', 'Unknown')
            
            # Add virtual package to tree
            item = self.programs_tree.add_virtual_program(
                name,
                version,
                publisher
            )
            
            self.logger.info(f"Added virtual package: {name}")
            return item
            
        except Exception as e:
            self.logger.error(f"Failed to add virtual package: {str(e)}")
            return None
