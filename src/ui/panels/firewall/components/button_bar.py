"""Button bar component for firewall panel."""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal

from .add_button import AddButton
from .edit_button import EditButton
from .delete_button import DeleteButton
from .refresh_button import RefreshButton

class ButtonBar(QWidget):
    """Button bar for firewall rule operations."""
    
    add_clicked = pyqtSignal(str)
    edit_clicked = pyqtSignal(str)
    delete_clicked = pyqtSignal(str)
    refresh_clicked = pyqtSignal(str)
    toggle_clicked = pyqtSignal(str)
    
    def __init__(self, direction, parent=None):
        """Initialize button bar.
        
        Args:
            direction: "inbound" or "outbound"
            parent: Parent widget
        """
        super().__init__(parent)
        self.direction = direction
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Set up the button bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create buttons
        self.add_button = AddButton(self.direction, self)
        self.edit_button = EditButton(self.direction, self)
        self.delete_button = DeleteButton(self.direction, self)
        self.toggle_button = QPushButton("Enable/Disable", self)
        self.toggle_button.setEnabled(False)  # Disabled by default until selection
        self.refresh_button = RefreshButton(self.direction, self)
        
        # Add buttons to layout
        layout.addWidget(self.add_button)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.refresh_button)
        
        # Add stretch to push buttons to the left
        layout.addStretch()
        
    def setup_connections(self):
        """Set up signal/slot connections."""
        self.add_button.clicked_with_direction.connect(self.add_clicked)
        self.edit_button.clicked_with_direction.connect(self.edit_clicked)
        self.delete_button.clicked_with_direction.connect(self.delete_clicked)
        self.refresh_button.clicked_with_direction.connect(self.refresh_clicked)
        self.toggle_button.clicked.connect(lambda: self.toggle_clicked.emit(self.direction))
        
    def update_button_states(self, has_selection):
        """Update button enabled states based on selection.
        
        Args:
            has_selection: Whether a rule is selected
        """
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self.toggle_button.setEnabled(has_selection)
