"""Add Startup Item button component."""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal


class AddButton(QPushButton):
    """Button for adding a new startup item."""
    
    # Signal emitted when button is clicked
    clicked_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the add startup item button.
        
        Args:
            parent: Parent widget
        """
        super().__init__("Add Startup Item", parent)
        self.clicked.connect(self._on_clicked)
        
    def _on_clicked(self):
        """Handle button click and emit signal."""
        self.clicked_signal.emit()
