"""End Process button component."""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal


class EndProcessButton(QPushButton):
    """Button for ending a selected process."""
    
    # Signal emitted when button is clicked
    clicked_with_selection = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the end process button.
        
        Args:
            parent: Parent widget
        """
        super().__init__("End Process", parent)
        self.setEnabled(False)
        self.clicked.connect(self._on_clicked)
        
    def _on_clicked(self):
        """Handle button click and emit signal."""
        self.clicked_with_selection.emit()
        
    def update_state(self, has_selection):
        """Update button enabled state based on selection.
        
        Args:
            has_selection: Whether a process is selected
        """
        self.setEnabled(has_selection)
