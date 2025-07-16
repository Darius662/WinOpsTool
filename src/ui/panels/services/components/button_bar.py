"""Button bar for Services Panel."""
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from src.core.logger import setup_logger
from .start_button import StartButton
from .stop_button import StopButton
from .restart_button import RestartButton
from .startup_button import StartupButton
from .refresh_button import RefreshButton
from .edit_button import EditButton

class ButtonBar(QWidget):
    """Button bar for Services Panel."""
    
    def __init__(self, panel):
        """Initialize button bar.
        
        Args:
            panel: Parent ServicesPanel instance
        """
        super().__init__()
        self.panel = panel
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the button bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create buttons
        self.start_button = StartButton(self.panel)
        self.stop_button = StopButton(self.panel)
        self.restart_button = RestartButton(self.panel)
        self.edit_button = EditButton(self.panel)
        self.startup_button = StartupButton(self.panel)
        self.refresh_button = RefreshButton(self.panel)
        
        # Add buttons to layout
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.restart_button)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.startup_button)
        layout.addWidget(self.refresh_button)
        
        # Add stretch to push buttons to the left
        layout.addStretch()
        
    def update_button_states(self, has_selection):
        """Update button enabled states based on selection.
        
        Args:
            has_selection: Whether a service is selected
        """
        self.start_button.setEnabled(has_selection)
        self.stop_button.setEnabled(has_selection)
        self.restart_button.setEnabled(has_selection)
        self.edit_button.setEnabled(has_selection)
        self.startup_button.setEnabled(has_selection)
