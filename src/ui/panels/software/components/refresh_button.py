"""Refresh button component for software panel."""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal


class RefreshButton(QPushButton):
    """Button for refreshing software list."""
    
    # Signal emitted when button is clicked
    clicked_with_filter = pyqtSignal(str)
    
    def __init__(self, filter_type="All", parent=None):
        """Initialize refresh button.
        
        Args:
            filter_type: Current filter type
            parent: Parent widget
        """
        super().__init__("Refresh", parent)
        self.filter_type = filter_type
        self.setup_connections()
        
    def setup_connections(self):
        """Set up signal connections."""
        self.clicked.connect(self._on_clicked)
        
    def _on_clicked(self):
        """Handle button click."""
        self.clicked_with_filter.emit(self.filter_type)
        
    def update_filter(self, filter_type):
        """Update the current filter type.
        
        Args:
            filter_type: New filter type
        """
        self.filter_type = filter_type
