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
        """Perform cleanup before panel is destroyed."""
        raise NotImplementedError('Panels must implement cleanup')
        
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
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed.
        
        Override this method in derived classes.
        """
        pass  # Optional to override
