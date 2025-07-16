"""Add environment variable button component."""
from PyQt6.QtWidgets import QPushButton
from src.core.logger import setup_logger
from ..dialogs import AddVariableDialog

class AddButton(QPushButton):
    """Button for adding environment variables."""
    
    def __init__(self, parent=None):
        """Initialize add button.
        
        Args:
            parent: Parent widget
        """
        super().__init__("Add", parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.panel = parent
        
    def connect_signals(self):
        """Connect button signals."""
        self.clicked.connect(self.on_clicked)
        
    def on_clicked(self):
        """Handle button click event."""
        # Use the panel's add_variable method which now uses variable_ops
        self.panel.add_variable()
