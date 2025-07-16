"""Edit environment variable button component."""
from PyQt6.QtWidgets import QPushButton, QMessageBox
from src.core.logger import setup_logger
from ..dialogs import AddVariableDialog

class EditButton(QPushButton):
    """Button for editing environment variables."""
    
    def __init__(self, parent=None):
        """Initialize edit button.
        
        Args:
            parent: Parent widget
        """
        super().__init__("Edit", parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.panel = parent
        
    def connect_signals(self):
        """Connect button signals."""
        self.clicked.connect(self.on_clicked)
        
    def on_clicked(self):
        """Handle button click event."""
        # Use the panel's edit_variable method which now uses variable_ops
        self.panel.edit_variable()
        
        # The edit_variable method in the panel now handles all of this logic
        # through the variable_ops component
