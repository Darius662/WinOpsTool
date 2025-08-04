"""Windows Services management panel."""
from PyQt6.QtWidgets import QLineEdit, QLabel, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import ServicesTree
from .components import ButtonBar, DialogFactory, ServiceOperations

class ServicesPanel(BasePanel):
    """Panel for managing Windows Services."""
    
    def __init__(self, parent=None):
        """Initialize services panel.
        
        Args:
            parent: Parent widget
        """
        # Initialize components to None first
        self.services_tree = None
        self.search_edit = None
        self.button_bar = None
        
        # Set up logger
        self.logger = setup_logger(self.__class__.__name__)
        
        # Initialize helper components
        self.dialog_factory = DialogFactory(self)
        self.service_ops = ServiceOperations(self)
        
        # Call base class constructor (which calls setup_ui)
        super().__init__(parent)
        
        # Connect signals after UI is set up
        self.setup_connections()
        
        # Refresh services list
        self.refresh_services()
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Search controls
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        
        # Add search layout
        self.add_layout(search_layout)
        
        # Services tree
        self.services_tree = ServicesTree()
        self.add_widget(self.services_tree)
        
        # Button bar
        self.button_bar = ButtonBar(self)
        self.add_widget(self.button_bar)
        
        # Initial button state
        self.update_buttons()
        
    def setup_connections(self):
        """Set up signal/slot connections."""
        if self.search_edit:
            self.search_edit.textChanged.connect(self.filter_services)
        
        if self.services_tree:
            self.services_tree.itemSelectionChanged.connect(self.update_buttons)
        
    def update_buttons(self):
        """Update button enabled states based on selection."""
        if self.services_tree and self.button_bar:
            has_selection = bool(self.services_tree.selectedItems())
            self.button_bar.update_button_states(has_selection)
        
    def refresh_services(self):
        """Refresh the services list."""
        self.logger.info("Refreshing services list")
        self.service_ops.refresh_services_with_highlighting()
            
    def filter_services(self, text):
        """Filter services by name or display name.
        
        Args:
            text: Search text
        """
        self.service_ops.filter_services(text)
            
    def start_service(self):
        """Start selected service."""
        self.service_ops.start_service()
            
    def stop_service(self):
        """Stop selected service."""
        self.service_ops.stop_service()
                
    def restart_service(self):
        """Restart selected service."""
        self.service_ops.restart_service()
                
    def change_startup(self):
        """Change startup type of selected service."""
        self.service_ops.change_startup()
        
    def edit_service(self):
        """Edit selected service properties."""
        self.service_ops.edit_service()
        
    def mark_config_items(self, config):
        """Mark items from configuration for highlighting without applying changes.
        
        This method identifies and marks services from the configuration
        that would be modified by apply_config(), but does not actually
        apply any changes to the system. Items will be visually highlighted in the UI.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if items were marked successfully, False otherwise
        """
        self.logger.info("Marking services from configuration for highlighting")
        
        # Clear previous imported items
        self.imported_config_items.clear()
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Process services configuration
            if 'services' in config and isinstance(config['services'], list):
                for service_config in config['services']:
                    if not isinstance(service_config, dict):
                        continue
                        
                    # Check required fields
                    if 'name' not in service_config:
                        self.logger.warning("Skipping service without name")
                        continue
                        
                    name = service_config['name']
                    
                    # Mark this service as imported from config for highlighting
                    self.mark_as_imported_config(f"service:{name}")
                    self.logger.info(f"Marked service for configuration: {name}")
            
            # Refresh the view to show highlighted services
            self.refresh_services()
            return True
            
        except Exception as e:
            self.logger.error(f"Error marking services from configuration: {str(e)}")
            return False
    
    def apply_config(self, config):
        """Apply configuration to the panel.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if configuration was applied successfully, False otherwise
        """
        self.logger.info("Applying services configuration")
        
        # Clear previous imported items
        self.imported_config_items.clear()
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            success = False
            
            # Process services configuration
            if 'services' in config and isinstance(config['services'], list):
                for service_config in config['services']:
                    if not isinstance(service_config, dict):
                        continue
                        
                    # Check required fields
                    if 'name' not in service_config:
                        self.logger.warning("Skipping service without name")
                        continue
                        
                    name = service_config['name']
                    
                    # Mark this service as imported from config for highlighting
                    self.mark_as_imported_config(f"service:{name}")
                    
                    # Configure service properties if specified
                    start_type = service_config.get('start_type')
                    if start_type:
                        self.service_ops.manager.set_startup_type(name, start_type)
                        success = True
                    
                    # Configure service state if specified
                    desired_state = service_config.get('state')
                    if desired_state:
                        current_state = self.service_ops.manager.get_service_state(name)
                        
                        if desired_state.lower() == 'running' and current_state != 'Running':
                            self.service_ops.manager.start_service(name)
                            success = True
                        elif desired_state.lower() == 'stopped' and current_state != 'Stopped':
                            self.service_ops.manager.stop_service(name)
                            success = True
            
            # Refresh the view to show updated services with highlighting
            self.refresh_services()
            return success
            
        except Exception as e:
            self.logger.error(f"Error applying services configuration: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error applying services configuration: {str(e)}"
            )
            return False
