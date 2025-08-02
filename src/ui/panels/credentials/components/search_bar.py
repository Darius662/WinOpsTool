"""Search bar for filtering credentials in the Windows Credential Manager panel.

This module provides a search bar component that allows users to filter credentials
by target name, username, or credential type. It integrates with the tabbed interface
and works independently in both the Web Credentials and Windows Credentials tabs.
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon
from src.core.logger import setup_logger

class SearchBar(QWidget):
    """Search bar for filtering credentials in the Windows Credential Manager panel.
    
    This widget provides a search field that allows users to filter credentials
    by target name, username, or credential type. It emits a signal whenever the
    search text changes, which is connected to the filtering method of the
    corresponding CredentialsTree widget in each tab.
    
    Each tab (Web Credentials and Windows Credentials) has its own independent
    SearchBar instance, allowing for separate filtering in each tab.
    """
    
    # Signal emitted when search text changes
    search_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize the search bar."""
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
        # Set up layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create search field
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search credentials...")
        self.search_field.setClearButtonEnabled(True)
        self.search_field.textChanged.connect(self.on_search_text_changed)
        
        # Add to layout
        layout.addWidget(self.search_field)
        
    def on_search_text_changed(self, text):
        """Handle search text changes.
        
        Args:
            text: New search text
        """
        self.search_changed.emit(text)
        
    def clear(self):
        """Clear the search field."""
        self.search_field.clear()
