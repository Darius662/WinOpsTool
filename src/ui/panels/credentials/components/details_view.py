"""Details view for displaying credential information in Windows Credential Manager style.

This module provides a widget for displaying detailed credential information,
including target name, username, password, type, persistence, comment, and last modified date.
It works with the tabbed credential manager interface to show details for credentials
selected in either the Web Credentials or Windows Credentials tabs.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from src.core.logger import setup_logger

class DetailsView(QWidget):
    """Widget for displaying credential details in Windows Credential Manager style.
    
    This widget displays detailed information about a selected credential, including:
    - Target name: The resource or service the credential is for
    - Username: The account username
    - Password: Hidden by default with show/hide functionality
    - Type: The credential type (Windows, Certificate-Based, or Generic)
    - Persistence: How the credential is stored
    - Comment: Additional information about the credential
    - Last Modified: When the credential was last updated
    
    The widget works with both Web Credentials and Windows Credentials tabs
    and updates its display when a credential is selected in either tab.
    """
    
    # Signal emitted when show password button is clicked
    show_password_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize the details view."""
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)
        
        # Create labels for credential details
        self.target_label = QLabel()
        self.username_label = QLabel()
        self.type_label = QLabel()
        self.persist_label = QLabel()
        self.comment_label = QLabel()
        self.last_written_label = QLabel()
        
        # Add labels to form layout
        self.form_layout.addRow("Target Name:", self.target_label)
        self.form_layout.addRow("Username:", self.username_label)
        self.form_layout.addRow("Type:", self.type_label)
        self.form_layout.addRow("Persistence:", self.persist_label)
        self.form_layout.addRow("Comment:", self.comment_label)
        self.form_layout.addRow("Last Modified:", self.last_written_label)
        
        # Add password section with show button
        password_layout = QHBoxLayout()
        self.password_label = QLabel("[Hidden]")
        self.show_password_button = QPushButton("Show")
        self.show_password_button.setFixedWidth(80)
        self.show_password_button.clicked.connect(self._on_show_password)
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.show_password_button)
        password_layout.addStretch()
        
        self.form_layout.addRow("Password:", password_layout)
        
        # Add stretch to push everything to the top
        self.layout.addStretch()
        
        # Store the target name for reference
        self.current_target = None
        
    def show_credential_details(self, credential_info):
        """Show credential details.
        
        Args:
            credential_info: Dictionary with credential information
        """
        self.target_label.setText(credential_info['target_name'])
        self.username_label.setText(credential_info['username'])
        self.type_label.setText(credential_info['type'])
        self.persist_label.setText(credential_info['persist'])
        self.comment_label.setText(credential_info['comment'])
        self.last_written_label.setText(str(credential_info['last_written']))
        self.password_label.setText("[Hidden]")
        
        # Store target name for password retrieval
        self.current_target = credential_info['target_name']
        
    def clear(self):
        """Clear all credential details."""
        self.target_label.clear()
        self.username_label.clear()
        self.type_label.clear()
        self.persist_label.clear()
        self.comment_label.clear()
        self.last_written_label.clear()
        self.password_label.setText("[Hidden]")
        self.current_target = None
        
    def _on_show_password(self):
        """Handle show password button click."""
        if self.current_target:
            self.show_password_clicked.emit(self.current_target)
            
    def show_password(self, password):
        """Show the password.
        
        Args:
            password: Password to show
        """
        self.password_label.setText(password)
        
        # Change button text
        self.show_password_button.setText("Hide")
        self.show_password_button.clicked.disconnect()
        self.show_password_button.clicked.connect(self._on_hide_password)
        
    def _on_hide_password(self):
        """Handle hide password button click."""
        self.password_label.setText("[Hidden]")
        
        # Change button text back
        self.show_password_button.setText("Show")
        self.show_password_button.clicked.disconnect()
        self.show_password_button.clicked.connect(self._on_show_password)
