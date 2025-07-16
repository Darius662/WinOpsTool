"""Delete button component for permissions panel."""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal


class DeleteButton(QPushButton):
    """Button for deleting a permission."""
    
    # Signal emitted when button is clicked
    clicked_with_path = pyqtSignal(str)
    
    def __init__(self, path=None, parent=None):
        """Initialize delete button.
        
        Args:
            path: Current path
            parent: Parent widget
        """
        super().__init__("Remove Permission", parent)
        self.path = path
        self.setEnabled(False)  # Disabled by default until selection
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
        
    def update_state(self, has_path, has_selection):
        """Update button enabled state.
        
        Args:
            has_path: Whether a path is selected
            has_selection: Whether an item is selected
        """
        self.setEnabled(has_path and has_selection)
