"""Windows Startup management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QMessageBox)
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import StartupTree
from .dialogs import AddStartupDialog
from .manager import StartupManager

class StartupPanel(BasePanel):
    """Panel for managing Windows startup entries."""
    
    def __init__(self, parent=None):
        """Initialize startup panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = StartupManager()
        
        # Initialize imported config items
        self.imported_config_items = set()
        
        self.setup_ui()
        
        # Initial refresh
        self.refresh_entries()
        
    def setup_ui(self):
        """Set up the panel UI."""
        layout = QVBoxLayout(self)
        
        # Create tree widget
        self.tree = StartupTree()
        layout.addWidget(self.tree)
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_entry)
        button_layout.addWidget(add_button)
        
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self.remove_entry)
        button_layout.addWidget(remove_button)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_entries)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)
        
    def add_entry(self):
        """Add a new startup entry."""
        dialog = AddStartupDialog(self)
        if dialog.exec():
            name, command, user_specific = dialog.get_entry()
            
            try:
                if self.manager.add_registry_startup(name, command, user_specific):
                    location = 'HKCU_RUN' if user_specific else 'HKLM_RUN'
                    self.tree.add_entry(
                        name,
                        command,
                        location,
                        'Registry',
                        True
                    )
                    self.logger.info(f"Added startup entry: {name}")
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to add startup entry."
                    )
                    
            except Exception as e:
                self.logger.error(f"Failed to add startup entry: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to add startup entry: {str(e)}"
                )
                
    def remove_entry(self):
        """Remove selected startup entry."""
        item = self.tree.currentItem()
        if not item:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select an entry to remove."
            )
            return
            
        name, _, location, entry_type, _ = self.tree.get_entry(item)
        
        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Are you sure you want to remove '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = False
                
                if entry_type == 'Registry':
                    success = self.manager.remove_registry_startup(name, location)
                elif entry_type == 'Shortcut':
                    success = self.manager.remove_folder_startup(name, location)
                else:
                    QMessageBox.warning(
                        self,
                        "Cannot Remove",
                        f"Cannot remove entries of type: {entry_type}"
                    )
                    return
                    
                if success:
                    self.tree.takeTopLevelItem(
                        self.tree.indexOfTopLevelItem(item)
                    )
                    self.logger.info(f"Removed startup entry: {name}")
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to remove startup entry."
                    )
                    
            except Exception as e:
                self.logger.error(f"Failed to remove startup entry: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to remove startup entry: {str(e)}"
                )
                
    def refresh_entries(self):
        """Refresh startup entries list."""
        try:
            # Clear existing entries
            self.tree.clear_entries()
            
            # Add registry entries
            for entry in self.manager.get_registry_startups():
                self.tree.add_entry(
                    entry['name'],
                    entry['command'],
                    entry['location'],
                    entry['type'],
                    entry['enabled']
                )
                
            # Add folder entries
            for entry in self.manager.get_folder_startups():
                self.tree.add_entry(
                    entry['name'],
                    entry['command'],
                    entry['location'],
                    entry['type'],
                    entry['enabled']
                )
                
            # Add service entries
            for entry in self.manager.get_service_startups():
                self.tree.add_entry(
                    entry['name'],
                    entry['command'],
                    entry['location'],
                    entry['type'],
                    entry['enabled']
                )
                
            # Highlight imported config items
            for item in self.tree.get_all_items():
                name, _, location, entry_type, _ = self.tree.get_entry(item)
                if f"startup:{entry_type.lower()}:{name}" in self.imported_config_items:
                    self.tree.highlight_item(item)
                    
            self.logger.debug("Refreshed startup entries")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh startup entries: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to refresh startup entries: {str(e)}"
            )
            
    def apply_config(self, config):
        """Apply configuration to the panel.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if configuration was applied successfully, False otherwise
        """
        self.logger.info("Applying startup entries configuration")
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Process configuration
            if 'startup' not in config:
                self.logger.warning("No startup configuration found")
                return False
                
            startup_config = config['startup']
            
            # Apply registry startup entries if available
            success = False
            
            if 'registry_entries' in startup_config and isinstance(startup_config['registry_entries'], list):
                self.logger.info(f"Applying {len(startup_config['registry_entries'])} registry startup entries")
                
                for entry in startup_config['registry_entries']:
                    if not isinstance(entry, dict):
                        continue
                        
                    # Check required fields
                    if 'name' not in entry or 'command' not in entry:
                        self.logger.warning("Skipping invalid startup entry")
                        continue
                        
                    name = entry['name']
                    command = entry['command']
                    user_specific = entry.get('user_specific', True)  # Default to user-specific (HKCU)
                    
                    # Add the registry startup entry
                    result = self.manager.add_registry_startup(name, command, user_specific)
                    
                    if result:
                        self.logger.info(f"Added registry startup entry: {name}")
                        success = True
                    else:
                        self.logger.warning(f"Failed to add registry startup entry: {name}")
            
            # Refresh the entries to show updated state
            self.refresh_entries()
            return success
            
        except Exception as e:
            self.logger.error(f"Error applying startup configuration: {str(e)}")
            return False
            
    def export_config(self):
        """Export panel configuration.
        
        Returns:
            dict: Dictionary containing panel configuration
        """
        self.logger.info("Exporting startup entries configuration")
        
        try:
            # Create configuration dictionary
            config = {
                'startup': {
                    'registry_entries': [],
                    'folder_entries': []
                }
            }
            
            # Export registry startup entries
            for entry in self.manager.get_registry_startups():
                # Skip Windows default entries
                if entry['name'] in ['OneDrive', 'WindowsDefender', 'SecurityHealth']:
                    continue
                    
                registry_entry = {
                    'name': entry['name'],
                    'command': entry['command'],
                    'user_specific': entry['location'] == 'HKCU_RUN'
                }
                
                config['startup']['registry_entries'].append(registry_entry)
                
            # Export folder startup entries
            # Note: We don't export folder entries as they are typically managed by the system
            # or installed applications, and we don't want to duplicate them
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error exporting startup configuration: {str(e)}")
            return {'startup': {'registry_entries': [], 'folder_entries': []}}

    def mark_config_items(self, config):
        """Mark items from configuration for highlighting without applying changes.
        
        This method identifies and marks startup entries from the configuration
        that would be modified by apply_config(), but does not actually
        apply any changes to the system. Items will be visually highlighted in the UI.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if items were marked successfully, False otherwise
        """
        self.logger.info("Marking startup entries from configuration for highlighting")
        
        # Clear previous imported items
        self.imported_config_items.clear()
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Check if startup section exists
            if 'startup' not in config:
                self.logger.warning("No startup configuration found")
                return False
                
            startup_config = config['startup']
            
            # Get existing entries for comparison
            existing_registry_entries = {entry['name']: entry for entry in self.manager.get_registry_startups()}
            
            # Process registry startup entries
            if 'registry_entries' in startup_config and isinstance(startup_config['registry_entries'], list):
                self.logger.info(f"Marking {len(startup_config['registry_entries'])} registry startup entries for highlighting")
                
                for entry in startup_config['registry_entries']:
                    if not isinstance(entry, dict):
                        continue
                        
                    # Check required fields
                    if 'name' not in entry or 'command' not in entry:
                        self.logger.warning("Skipping invalid startup entry")
                        continue
                        
                    name = entry['name']
                    command = entry['command']
                    user_specific = entry.get('user_specific', True)  # Default to user-specific (HKCU)
                    
                    # Mark this entry as imported from config for highlighting
                    self.mark_as_imported_config(f"startup:registry:{name}")
                    self.logger.debug(f"Marked registry startup entry for highlighting: {name}")
                    
                    # Check if entry exists
                    if name in existing_registry_entries:
                        # Entry exists, check if it matches
                        existing_entry = existing_registry_entries[name]
                        if existing_entry['command'] != command:
                            self.logger.debug(f"Existing entry '{name}' has different command")
                    else:
                        # Entry doesn't exist, add virtual entry
                        self.add_virtual_entry(name, command, user_specific)
            
            # Process folder startup entries if available
            if 'folder_entries' in startup_config and isinstance(startup_config['folder_entries'], list):
                self.logger.info(f"Marking {len(startup_config['folder_entries'])} folder startup entries for highlighting")
                
                for entry in startup_config['folder_entries']:
                    if not isinstance(entry, dict):
                        continue
                        
                    # Check required fields
                    if 'name' not in entry or 'path' not in entry:
                        self.logger.warning("Skipping invalid folder startup entry")
                        continue
                        
                    name = entry['name']
                    path = entry['path']
                    user_specific = entry.get('user_specific', True)  # Default to user-specific
                    
                    # Mark this entry as imported from config for highlighting
                    self.mark_as_imported_config(f"startup:folder:{name}")
                    self.logger.debug(f"Marked folder startup entry for highlighting: {name}")
            
            # Refresh the entries to show updated state with highlighting
            self.refresh_entries()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error marking startup entries from configuration: {str(e)}")
            return False
    
    def add_virtual_entry(self, name, command, user_specific):
        """Add a virtual startup entry that doesn't exist in the system yet.
        
        Args:
            name: Entry name
            command: Command to execute
            user_specific: Whether entry is user-specific (HKCU) or system-wide (HKLM)
        """
        try:
            location = 'HKCU_RUN' if user_specific else 'HKLM_RUN'
            
            # Add virtual entry to the tree
            self.tree.add_virtual_entry(
                name,
                command,
                location,
                'Registry'
            )
            
            self.logger.debug(f"Added virtual startup entry: {name}")
            
        except Exception as e:
            self.logger.error(f"Error adding virtual startup entry: {str(e)}")
    
    def mark_as_imported_config(self, item):
        """Mark an item as imported from config for highlighting.
        
        Args:
            item: Item to mark
        """
        self.imported_config_items.add(item)
