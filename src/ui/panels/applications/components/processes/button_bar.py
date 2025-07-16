"""Button bar component for processes tab."""
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

from .end_process_button import EndProcessButton
from .end_process_tree_button import EndProcessTreeButton
from .refresh_button import RefreshButton


class ButtonBar(QWidget):
    """Button bar for processes tab containing action buttons."""
    
    # Signals forwarded from buttons
    end_process_clicked = pyqtSignal()
    end_process_tree_clicked = pyqtSignal()
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
        self.end_process_button = EndProcessButton()
        self.end_process_tree_button = EndProcessTreeButton()
        self.refresh_button = RefreshButton()
        
    def _setup_layout(self):
        """Set up the horizontal layout for buttons."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(self.end_process_button)
        layout.addWidget(self.end_process_tree_button)
        layout.addWidget(self.refresh_button)
        
    def _connect_signals(self):
        """Connect button signals to forwarding slots."""
        self.end_process_button.clicked_with_selection.connect(self.end_process_clicked)
        self.end_process_tree_button.clicked_with_selection.connect(self.end_process_tree_clicked)
        self.refresh_button.clicked_signal.connect(self.refresh_clicked)
        
    def update_button_states(self, has_selection):
        """Update button states based on selection.
        
        Args:
            has_selection: Whether a process is selected
        """
        self.end_process_button.update_state(has_selection)
        self.end_process_tree_button.update_state(has_selection)
