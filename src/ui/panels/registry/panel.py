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
