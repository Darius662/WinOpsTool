"""Edit button for Services Panel."""
from PyQt6.QtWidgets import QPushButton
from src.core.logger import setup_logger

class EditButton(QPushButton):
    """Button for editing service properties."""
    
    def __init__(self, panel):
        """Initialize edit button.
        
        Args:
            panel: Parent ServicesPanel instance
        """
        super().__init__("Edit")
        self.panel = panel
        self.logger = setup_logger(self.__class__.__name__)
        self.clicked.connect(self.on_click)
        self.setEnabled(False)  # Initially disabled until a service is selected
        
    def on_click(self):
        """Handle button click event."""
        self.logger.info("Edit button clicked")
        self.panel.edit_service()
