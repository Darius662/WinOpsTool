"""Delete environment variable button component."""
from PyQt6.QtWidgets import QPushButton, QMessageBox
from src.core.logger import setup_logger

class DeleteButton(QPushButton):
    """Button for deleting environment variables."""
    
    def __init__(self, parent=None):
        """Initialize delete button.
        
        Args:
            parent: Parent widget
        """
        super().__init__("Delete", parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.panel = parent
        
    def connect_signals(self):
        """Connect button signals."""
        self.clicked.connect(self.on_clicked)
        
    def on_clicked(self):
        """Handle button click event."""
        # Use the panel's delete_variable method which now uses variable_ops
        self.panel.delete_variable()
