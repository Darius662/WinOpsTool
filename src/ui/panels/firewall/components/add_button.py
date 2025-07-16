"""Add rule button component."""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal

class AddButton(QPushButton):
    """Button for adding a new firewall rule."""
    
    clicked_with_direction = pyqtSignal(str)  # Signal with direction parameter
    
    def __init__(self, direction, parent=None):
        """Initialize add button.
        
        Args:
            direction: "inbound" or "outbound"
            parent: Parent widget
        """
        super().__init__("Add Rule", parent)
        self.direction = direction
        self.setup_connections()
        
    def setup_connections(self):
        """Set up signal/slot connections."""
        self.clicked.connect(self._on_clicked)
        
    def _on_clicked(self):
        """Handle button click by emitting signal with direction."""
        self.clicked_with_direction.emit(self.direction)
