"""Refresh button component for startup tab."""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal


class RefreshButton(QPushButton):
    """Button for refreshing the startup items list."""
    
    # Signal emitted when button is clicked
    clicked_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the refresh button.
        
        Args:
            parent: Parent widget
        """
        super().__init__("Refresh", parent)
        self.clicked.connect(self._on_clicked)
        
    def _on_clicked(self):
        """Handle button click and emit signal."""
        self.clicked_signal.emit()
