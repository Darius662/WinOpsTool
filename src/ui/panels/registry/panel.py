"""Registry management panel."""
from PyQt6.QtWidgets import QSplitter, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import RegistryTree
from .components import ButtonBar, ValuesView, DialogFactory, RegistryOperations

class RegistryPanel(BasePanel):
    """Panel for managing registry entries."""
    
    def __init__(self, main_window):
        """Initialize registry panel.
        
        Args:
            main_window: MainWindow instance
        """
        # Initialize components to None first
        self.tree = None
        self.values_view = None
        self.button_bar = None
        self.splitter = None
        
        # Set up logger
        self.logger = setup_logger(self.__class__.__name__)
        
        # Initialize helper components
        self.dialog_factory = DialogFactory(self)
        self.registry_ops = RegistryOperations(self)
        
        # Call base class constructor (which calls setup_ui)
        super().__init__(main_window)
        
        # Connect signals after UI is set up
        self.setup_connections()
        
        # Initialize imported config items
        self.imported_config_items = set()
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed.
        
        Override of BasePanel.cleanup to handle specific cleanup tasks.
        """
        # Clear references to UI elements to avoid memory leaks
        if hasattr(self, 'tree') and self.tree is not None:
            try:
                self.tree.clear()
            except RuntimeError:
                # Widget might have been deleted already
                pass
        
        if hasattr(self, 'values_view') and self.values_view is not None:
            try:
                self.values_view.clear()
            except RuntimeError:
                # Widget might have been deleted already
                pass
                
        # Call the parent class cleanup to clear the main layout
        # This should be called after clearing individual widgets
        super().cleanup()
    
    def setup_ui(self):
        """Set up the panel UI."""
        # Clear any existing layout if this is not the initial setup
        if hasattr(self, 'splitter') and self.splitter is not None:
            self.cleanup()
        
        # Create main splitter (horizontal orientation for left/right split)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create left widget for tree view
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create label for keys tree
        self.keys_label = QLabel("Registry Keys")
        self.keys_label.setStyleSheet("font-weight: bold;")
        self.left_layout.addWidget(self.keys_label)
        
        # Create tree widget for keys
        self.tree = RegistryTree()
        self.left_layout.addWidget(self.tree)
        
        # Create right widget for values view
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create label for values view
        self.values_label = QLabel("Registry Values")
        self.values_label.setStyleSheet("font-weight: bold;")
        self.right_layout.addWidget(self.values_label)
        
        # Create values view
        self.values_view = ValuesView()
        self.right_layout.addWidget(self.values_view)
        
        # Add widgets to splitter
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        
        # Set initial sizes (40% for tree, 60% for values)
        self.splitter.setSizes([400, 600])
        
        # Create a main layout widget to contain splitter and buttons
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add splitter to main layout with stretch factor to fill available space
        main_layout.addWidget(self.splitter, 1)  # 1 = stretch factor
        
        # Create button bar component and add to bottom of main layout
        self.button_bar = ButtonBar(self)
        main_layout.addWidget(self.button_bar, 0)  # 0 = no stretch
        
        # Add the main widget to the panel
        self.add_widget(main_widget)
        
        # Update button states
        self.update_button_states()
        
        # Load registry entries automatically
        self.refresh_entries()
        
    def setup_connections(self):
        """Set up signal/slot connections."""
        # Connect tree signals
        self.tree.itemSelectionChanged.connect(self.update_button_states)
        self.tree.keySelected.connect(self.on_key_selected)
        
    def update_button_states(self):
        """Update button enabled states based on selection."""
        has_selection = bool(self.tree.selectedItems())
        self.button_bar.update_button_states(has_selection)
        
    def on_key_selected(self, path):
        """Handle registry key selection.
        
        Args:
            path: Selected registry key path
        """
        if self.values_view:
            self.registry_ops.refresh_values(path)
            self.update_button_states()
            self.logger.info(f"Selected registry key: {path}")
        
    def show_error(self, message):
        """Show error message.
        
        Args:
            message: Error message to display
        """
        self.dialog_factory.show_error(message)
        
    def add_entry(self):
        """Add a new registry entry.
        
        This method is called by the AddButton component.
        """
        self.registry_ops.add_entry()
                
    def edit_entry(self):
        """Edit selected registry entry.
        
        This method is called by the EditButton component.
        """
        self.registry_ops.edit_entry()
                
    def delete_entry(self):
        """Delete selected registry entry.
        
        This method is called by the DeleteButton component.
        """
        self.registry_ops.delete_entry()
                
    def refresh_entries(self):
        """Refresh registry entries list.
        
        This method is called by the RefreshButton component.
        """
        self.logger.info("Refreshing registry entries")
        self.registry_ops.refresh_entries()
        self.logger.info("Registry entries refreshed successfully")
        
    def update_remote_state(self, connected):
        """Update UI based on remote connection state.
        
        Args:
            connected: True if connected to remote system, False otherwise
        """
        # Enable/disable controls based on connection state
        self.setEnabled(not connected)  # Disable local registry when remote
        self.logger.info(f"Remote connection state changed: {connected}")
        
    def apply_config(self, config):
        """Apply configuration to the panel.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if configuration was applied successfully, False otherwise
        """
        self.logger.info("Applying registry configuration")
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Check if registry section exists
            if 'registry' not in config:
                self.logger.warning("No registry entries in configuration")
                return False
                
            registry_config = config['registry']
            
            # Process registry entries
            success_count = 0
            total_count = 0
            
            for entry in registry_config:
                total_count += 1
                
                # Check if entry has required fields
                if not all(k in entry for k in ['path', 'name', 'type', 'value']):
                    self.logger.warning(f"Skipping invalid registry entry: {entry}")
                    continue
                    
                path = entry['path']
                name = entry['name']
                value_type = entry['type']
                value = entry['value']
                
                self.logger.debug(f"Setting registry value: {path}\\{name} = {value} ({value_type})")
                
                # Use registry operations to set the value
                if self.registry_ops.set_registry_value(path, name, value_type, value):
                    success_count += 1
                else:
                    self.logger.warning(f"Failed to set registry value: {path}\\{name}")
            
            # Refresh the view to show updated entries
            self.refresh_entries()
            
            # Report success rate
            if total_count > 0:
                self.logger.info(f"Applied {success_count} of {total_count} registry entries")
                return success_count > 0
            else:
                self.logger.warning("No registry entries to apply")
                return False
                
        except Exception as e:
            self.logger.error(f"Error applying registry configuration: {str(e)}")
            return False
            
    def mark_config_items(self, config):
        """Mark items from configuration for highlighting without applying changes.
        
        This method identifies and marks registry entries from the configuration
        that would be modified by apply_config(), but does not actually
        apply any changes to the system. Items will be visually highlighted in the UI.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if items were marked successfully, False otherwise
        """
        self.logger.info("Marking registry entries from configuration for highlighting")
        
        # Clear previous imported items
        self.imported_config_items.clear()
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Check if registry section exists
            if 'registry' not in config:
                self.logger.warning("No registry entries in configuration")
                return False
                
            registry_config = config['registry']
            
            # Process registry entries
            for entry in registry_config:
                # Check if entry has required fields
                if not all(k in entry for k in ['path', 'name', 'type', 'value']):
                    self.logger.warning(f"Skipping invalid registry entry: {entry}")
                    continue
                    
                path = entry['path']
                name = entry['name']
                
                # Mark this registry entry as imported from config for highlighting
                self.mark_as_imported_config(f"registry:{path}\\{name}")
                self.logger.debug(f"Marked registry entry for highlighting: {path}\\{name}")
            
            # Add virtual entries for registry values that don't exist yet
            self.add_virtual_entries_for_config(registry_config)
            
            # Refresh the view to show highlighted entries
            self.refresh_entries()
            return True
            
        except Exception as e:
            self.logger.error(f"Error marking registry entries from configuration: {str(e)}")
            return False
    
    def add_virtual_entries_for_config(self, registry_config):
        """Add virtual entries for registry values that don't exist in the system yet.
        
        This method adds visual entries for registry values that are in the
        configuration but don't exist in the system yet.
        
        Args:
            registry_config: List of registry entries from configuration
        """
        try:
            # Group entries by path for efficient processing
            entries_by_path = {}
            for entry in registry_config:
                if not all(k in entry for k in ['path', 'name', 'type', 'value']):
                    continue
                    
                path = entry['path']
                if path not in entries_by_path:
                    entries_by_path[path] = []
                    
                entries_by_path[path].append(entry)
            
            # For each path, check if it exists and add virtual entries for values
            for path, entries in entries_by_path.items():
                # Check if the path exists in the registry
                if not self.registry_ops.key_exists(path):
                    self.logger.debug(f"Registry key does not exist: {path}")
                    continue
                
                # Get existing values for this path
                existing_values = {v['name']: v for v in self.registry_ops.get_registry_values(path)}
                
                # Add virtual entries for values that don't exist
                for entry in entries:
                    name = entry['name']
                    if name not in existing_values:
                        # Add virtual entry to values view if this is the currently selected path
                        if path == self.tree.get_selected_path():
                            self.values_view.add_virtual_value(
                                name,
                                entry['value'],
                                entry['type']
                            )
                            self.logger.debug(f"Added virtual entry for registry value: {path}\\{name}")
                        
        except Exception as e:
            self.logger.error(f"Error adding virtual entries for registry values: {str(e)}")
    
    def export_config(self):
        """Export panel configuration.
        
        Returns:
            dict: Dictionary containing panel configuration
        """
        self.logger.info("Exporting registry configuration")
        
        try:
            # Get current registry entries
            registry_entries = []
            
            # Get the currently selected key path
            selected_path = self.tree.get_selected_path()
            if not selected_path:
                self.logger.warning("No registry key selected for export")
                return {'registry': []}
                
            # Get values for the selected key
            values = self.registry_ops.get_registry_values(selected_path)
            
            # Add each value to the registry entries list
            for value in values:
                registry_entries.append({
                    'path': selected_path,
                    'name': value['name'],
                    'type': value['type'],
                    'value': value['value']
                })
                
            return {'registry': registry_entries}
            
        except Exception as e:
            self.logger.error(f"Error exporting registry configuration: {str(e)}")
            return {'registry': []}
