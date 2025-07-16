"""Status bar handler for the main window."""
from PyQt6.QtWidgets import QStatusBar, QLabel
from src.core.logger import setup_logger

class StatusHandler:
    """Handles status bar for the main window."""
    
    def __init__(self, main_window):
        """Initialize status handler.
        
        Args:
            main_window: MainWindow instance
        """
        self.main_window = main_window
        self.logger = setup_logger(self.__class__.__name__)
        self.statusbar = QStatusBar()
        self.main_window.setStatusBar(self.statusbar)
        self.setup_statusbar()
        
    def setup_statusbar(self):
        """Set up status bar widgets."""
        # Main status label
        self.status_label = QLabel("Ready")
        self.statusbar.addWidget(self.status_label)
        
        # Connection status
        self.connection_label = QLabel("Not Connected")
        self.statusbar.addPermanentWidget(self.connection_label)
        
    def set_status(self, message):
        """Set main status message.
        
        Args:
            message: Status message to display
        """
        self.status_label.setText(message)
        self.logger.debug(f"Status: {message}")
        
    def set_connection_status(self, connected, host=None):
        """Set connection status.
        
        Args:
            connected: True if connected, False otherwise
            host: Optional host name when connected
        """
        if connected and host:
            self.connection_label.setText(f"Connected to {host}")
        else:
            self.connection_label.setText("Not Connected")
            
    def clear_status(self):
        """Clear main status message."""
        self.status_label.setText("Ready")
