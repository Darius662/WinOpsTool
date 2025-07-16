"""Refresh button for Services Panel."""
from PyQt6.QtWidgets import QPushButton
from src.core.logger import setup_logger

class RefreshButton(QPushButton):
    """Button for refreshing services list."""
    
    def __init__(self, panel):
        """Initialize refresh button.
        
        Args:
            panel: Parent ServicesPanel instance
        """
        super().__init__("Refresh")
        self.panel = panel
        self.logger = setup_logger(self.__class__.__name__)
        self.clicked.connect(self.on_click)
        
    def on_click(self):
        """Handle button click event."""
        self.logger.info("Refresh button clicked")
        self.panel.refresh_services()
