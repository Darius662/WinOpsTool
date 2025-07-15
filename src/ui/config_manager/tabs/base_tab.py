"""Base class for configuration tabs."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from src.core.logger import setup_logger

class BaseConfigTab(QWidget):
    """Base class for all configuration tabs."""
    def __init__(self, config_handler, config_section):
        """Initialize the tab.
        
        Args:
            config_handler: ConfigHandler instance
            config_section: Name of the configuration section this tab manages
        """
        super().__init__()
        self.logger = setup_logger(self.__class__.__name__)
        self.config_handler = config_handler
        self.config_section = config_section
        self.config_handler.add_observer(self)
        
        # Set up the base layout
        self.layout = QVBoxLayout(self)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the tab's user interface.
        
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement setup_ui")
        
    def on_config_changed(self):
        """Handle configuration changes.
        
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement on_config_changed")
        
    def get_config(self):
        """Get this tab's configuration section."""
        return self.config_handler.get_config(self.config_section)
        
    def update_config(self, data):
        """Update this tab's configuration section."""
        self.config_handler.update_config(self.config_section, data)
