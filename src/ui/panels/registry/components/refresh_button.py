"""Refresh registry entries button component."""
from PyQt6.QtWidgets import QPushButton
from src.core.logger import setup_logger

class RefreshButton(QPushButton):
    """Button for refreshing registry entries."""
    
    def __init__(self, parent=None):
        """Initialize refresh button.
        
        Args:
            parent: Parent widget (RegistryPanel)
        """
        super().__init__("Refresh", parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.panel = parent
        
    def connect_signals(self):
        """Connect button signals."""
        self.clicked.connect(self.on_clicked)
        
    def on_clicked(self):
        """Handle button click event."""
        # Refresh the tree view
        self.panel.refresh_entries()
        
        # Also refresh the values view if a key is selected
        path = self.panel.tree.get_selected_key_path()
        if path:
            self.panel.values_view.load_values(path)
