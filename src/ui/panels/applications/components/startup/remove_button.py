"""Remove Startup Item button component."""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal


class RemoveButton(QPushButton):
    """Button for removing a selected startup item."""
    
    # Signal emitted when button is clicked
    clicked_with_selection = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the remove startup item button.
        
        Args:
            parent: Parent widget
        """
        super().__init__("Remove Startup Item", parent)
        self.setEnabled(False)
        self.clicked.connect(self._on_clicked)
        
    def _on_clicked(self):
        """Handle button click and emit signal."""
        self.clicked_with_selection.emit()
        
    def update_state(self, has_selection):
        """Update button enabled state based on selection.
        
        Args:
            has_selection: Whether a startup item is selected
        """
        self.setEnabled(has_selection)
