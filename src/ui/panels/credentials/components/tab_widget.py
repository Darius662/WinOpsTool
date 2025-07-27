"""Tab widget for credential categories in Windows Credential Manager style.

This module provides a tabbed interface for the Credential Manager panel,
separating credentials into Web Credentials and Windows Credentials tabs.
Each tab contains its own search bar and credentials tree, allowing for
independent filtering and display of credentials in each category.
"""
from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger
from ..tree_widget import CredentialsTree
from .search_bar import SearchBar

class CredentialTabWidget(QTabWidget):
    """Tab widget for credential categories in Windows Credential Manager style.
    
    This class provides a tabbed interface with two main tabs:
    - Web Credentials: For storing website login credentials
    - Windows Credentials: For storing system and application credentials
    
    Each tab contains its own search bar for filtering credentials and a
    CredentialsTree widget that displays credentials in a categorized view.
    The Windows Credentials tab further categorizes credentials into Windows,
    Certificate-Based, and Generic credential types.
    """
    
    def __init__(self, parent=None):
        """Initialize the credential tab widget."""
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
        # Create tabs
        self.web_credentials_tab = self._create_credentials_tab("Web Credentials")
        self.windows_credentials_tab = self._create_credentials_tab("Windows Credentials")
        
        # Add tabs to widget
        self.addTab(self.web_credentials_tab["container"], "Web Credentials")
        self.addTab(self.windows_credentials_tab["container"], "Windows Credentials")
        
    def _create_credentials_tab(self, title):
        """Create a tab for credentials.
        
        Args:
            title: Tab title
            
        Returns:
            dict: Dictionary with tab components
        """
        # Create container
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add search bar
        search_bar = SearchBar()
        layout.addWidget(search_bar)
        
        # Add tree widget
        tree = CredentialsTree()
        layout.addWidget(tree)
        
        # Connect search bar to tree
        search_bar.search_changed.connect(tree.filter_credentials)
        
        return {
            "container": container,
            "search_bar": search_bar,
            "tree": tree
        }
        
    def get_web_credentials_tree(self):
        """Get the web credentials tree widget.
        
        Returns:
            CredentialsTree: Web credentials tree widget
        """
        return self.web_credentials_tab["tree"]
        
    def get_windows_credentials_tree(self):
        """Get the windows credentials tree widget.
        
        Returns:
            CredentialsTree: Windows credentials tree widget
        """
        return self.windows_credentials_tab["tree"]
        
    def clear_all(self):
        """Clear all trees."""
        self.web_credentials_tab["tree"].clear_credentials()
        self.windows_credentials_tab["tree"].clear_credentials()
        
    def get_current_tree(self):
        """Get the currently visible tree widget.
        
        Returns:
            CredentialsTree: Currently visible tree widget
        """
        current_index = self.currentIndex()
        if current_index == 0:
            return self.web_credentials_tab["tree"]
        else:
            return self.windows_credentials_tab["tree"]
