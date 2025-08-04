"""Base class for all management panels."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from src.core.logger import setup_logger

class BasePanel(QWidget):
    """Base class for all management panels."""
    
    def __init__(self, parent=None):
        """Initialize the panel."""
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
        # Set up layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # Track imported configuration items for highlighting
        self.imported_config_items = set()
        
        # Initialize UI
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Set up the UI components."""
        raise NotImplementedError('Panels must implement setup_ui')
        
    def setup_connections(self):
        """Set up signal/slot connections."""
        raise NotImplementedError('Panels must implement setup_connections')
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed.
        
        This method clears the main layout of all widgets.
        Derived classes should override this method if additional cleanup is needed.
        """
        # Remove all widgets from the layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                # Recursively clear sublayouts
                while item.layout().count():
                    subitem = item.layout().takeAt(0)
                    if subitem.widget():
                        subitem.widget().setParent(None)
        
    def add_widget(self, widget):
        """Add a widget to the main layout."""
        self.main_layout.addWidget(widget)
        
    def add_layout(self, layout):
        """Add a layout to the main layout."""
        self.main_layout.addLayout(layout)
        
    def load_data(self):
        """Load or refresh panel data.
        
        Override this method in derived classes.
        """
        pass  # Optional to override
        
    def save_data(self):
        """Save panel data.
        
        Override this method in derived classes.
        """
        pass  # Optional to override
        
    def mark_config_items(self, config):
        """Mark items from configuration for highlighting without applying changes.
        
        This method identifies and marks items from the configuration that would be
        applied by apply_config(), but does not actually apply any changes to the system.
        Items will be visually highlighted in the UI to show what would be changed.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if items were marked successfully, False otherwise
        """
        self.logger.info("BasePanel mark_config_items called")
        
        # Clear previous imported items
        self.imported_config_items.clear()
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        # This is a base implementation that should be overridden by derived classes
        # Panels should implement this to mark items that would be changed by apply_config()
        # without actually applying the changes
        
        # After marking items, panels should refresh their UI to show the highlighting
        
        return True
        
    def apply_config(self, config):
        """Apply configuration to the panel.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if configuration was applied successfully, False otherwise
        """
        self.logger.info("BasePanel apply_config called")
        # Store the keys of imported config items for highlighting
        if isinstance(config, dict):
            # Clear previous imported items
            self.imported_config_items.clear()
            # This is a base implementation that should be overridden by derived classes
            return True
        return False
        
    def export_config(self):
        """Export panel configuration.
        
        Returns:
            dict: Dictionary containing panel configuration
        """
        self.logger.info("BasePanel export_config called")
        # This is a base implementation that should be overridden by derived classes
        return {}
        
    def is_imported_config_item(self, item_id):
        """Check if an item was imported from configuration.
        
        Args:
            item_id: Identifier for the item (e.g., name, path, etc.)
            
        Returns:
            bool: True if the item was imported from configuration
        """
        return item_id in self.imported_config_items
        
    def mark_as_imported_config(self, item_id):
        """Mark an item as imported from configuration.
        
        Args:
            item_id: Identifier for the item (e.g., name, path, etc.)
        """
        self.imported_config_items.add(item_id)
        
    def get_imported_config_style(self):
        """Get the style for imported configuration items.
        
        Returns:
            str: CSS style string for imported configuration items
        """
        return "background-color: #E6F7FF; border: 2px solid #1890FF; font-weight: bold;"
