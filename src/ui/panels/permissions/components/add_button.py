"""Add button component for permissions panel."""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal


class AddButton(QPushButton):
    """Button for adding a new permission."""
    
    # Signal emitted when button is clicked
    clicked_with_path = pyqtSignal(str)
    
    def __init__(self, path=None, parent=None):
        """Initialize add button.
        
        Args:
            path: Current path
            parent: Parent widget
        """
        super().__init__("Add Permission", parent)
        self.path = path
        self.setEnabled(bool(path))  # Enabled only when path is set
        self.setup_connections()
        
    def setup_connections(self):
        """Set up signal connections."""
        self.clicked.connect(self._on_clicked)
        
    def _on_clicked(self):
        """Handle button click."""
        if self.path:
            self.clicked_with_path.emit(self.path)
        
    def update_path(self, path):
        """Update the current path.
        
        Args:
            path: New path
        """
        self.path = path
        self.setEnabled(bool(path))
