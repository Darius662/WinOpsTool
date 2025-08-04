"""Button bar for credential management."""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal
from src.core.logger import setup_logger

class CredentialButtonBar(QWidget):
    """Button bar for credential management."""
    
    # Signals
    add_clicked = pyqtSignal()
    edit_clicked = pyqtSignal()
    delete_clicked = pyqtSignal()
    refresh_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the button bar."""
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
        # Set up layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create buttons
        self.add_button = QPushButton("Add Credential")
        self.edit_button = QPushButton("Edit Credential")
        self.delete_button = QPushButton("Delete Credential")
        self.refresh_button = QPushButton("Refresh")
        
        # Add buttons to layout
        layout.addWidget(self.add_button)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.refresh_button)
        
        # Add stretch to push buttons to the left
        layout.addStretch()
        
        # Connect signals
        self.add_button.clicked.connect(self.add_clicked)
        self.edit_button.clicked.connect(self.edit_clicked)
        self.delete_button.clicked.connect(self.delete_clicked)
        self.refresh_button.clicked.connect(self.refresh_clicked)
        
        # Disable edit and delete buttons initially
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        
    def enable_item_buttons(self, enabled=True):
        """Enable or disable buttons that require an item selection.
        
        Args:
            enabled: Whether to enable the buttons
        """
        self.edit_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)
