"""Button bar component for startup tab."""
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

from .add_button import AddButton
from .remove_button import RemoveButton
from .refresh_button import RefreshButton


class ButtonBar(QWidget):
    """Button bar for startup tab containing action buttons."""
    
    # Signals forwarded from buttons
    add_clicked = pyqtSignal()
    remove_clicked = pyqtSignal()
    refresh_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the button bar.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._create_buttons()
        self._setup_layout()
        self._connect_signals()
        
    def _create_buttons(self):
        """Create button components."""
        self.add_button = AddButton()
        self.remove_button = RemoveButton()
        self.refresh_button = RefreshButton()
        
    def _setup_layout(self):
        """Set up the horizontal layout for buttons."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)
        layout.addWidget(self.refresh_button)
        
    def _connect_signals(self):
        """Connect button signals to forwarding slots."""
        self.add_button.clicked_signal.connect(self.add_clicked)
        self.remove_button.clicked_with_selection.connect(self.remove_clicked)
        self.refresh_button.clicked_signal.connect(self.refresh_clicked)
        
    def update_button_states(self, has_selection):
        """Update button states based on selection.
        
        Args:
            has_selection: Whether a startup item is selected
        """
        self.remove_button.update_state(has_selection)
