"""Refresh environment variables button component."""
from PyQt6.QtWidgets import QPushButton
from src.core.logger import setup_logger

class RefreshButton(QPushButton):
    """Button for refreshing environment variables."""
    
    def __init__(self, parent=None):
        """Initialize refresh button.
        
        Args:
            parent: Parent widget
        """
        super().__init__("Refresh", parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.panel = parent
        
    def connect_signals(self):
        """Connect button signals."""
        self.clicked.connect(self.on_clicked)
        
    def on_clicked(self):
        """Handle button click event."""
        self.panel.refresh_variables()
