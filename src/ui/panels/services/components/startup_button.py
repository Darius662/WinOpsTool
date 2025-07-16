"""Startup button for Services Panel."""
from PyQt6.QtWidgets import QPushButton
from src.core.logger import setup_logger

class StartupButton(QPushButton):
    """Button for changing service startup type."""
    
    def __init__(self, panel):
        """Initialize startup button.
        
        Args:
            panel: Parent ServicesPanel instance
        """
        super().__init__("Startup Type")
        self.panel = panel
        self.logger = setup_logger(self.__class__.__name__)
        self.clicked.connect(self.on_click)
        self.setEnabled(False)  # Initially disabled until a service is selected
        
    def on_click(self):
        """Handle button click event."""
        self.logger.info("Startup Type button clicked")
        self.panel.change_startup()
