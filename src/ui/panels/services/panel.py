"""Windows Services management panel."""
from PyQt6.QtWidgets import QLineEdit, QLabel, QHBoxLayout
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
        self.service_ops.refresh_services()
            
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
