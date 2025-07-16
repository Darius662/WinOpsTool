"""Help window handler for the main window."""
from src.core.logger import setup_logger
from src.ui.help.help_window import HelpWindow

class HelpHandler:
    """Handles help window functionality."""
    
    def __init__(self, main_window):
        """Initialize help handler.
        
        Args:
            main_window: MainWindow instance
        """
        self.main_window = main_window
        self.logger = setup_logger(self.__class__.__name__)
        self.help_window = None
        
    def show_help(self):
        """Show help window."""
        if not self.help_window:
            self.help_window = HelpWindow(self.main_window)
        self.help_window.show()
        

