"""Details view for users and groups."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLabel, 
                           QGroupBox, QScrollArea)
from PyQt6.QtCore import pyqtSlot, Qt
from src.core.logger import setup_logger

class DetailsView(QWidget):
    """Widget for displaying details of selected user or group."""
    
    def __init__(self, parent=None):
        """Initialize details view.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the details view UI."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for details
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Container widget for scroll area
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)
        
        # User details section
        self.user_group = QGroupBox("User Details")
        self.user_group.setVisible(False)
        user_layout = QFormLayout(self.user_group)
        
        self.username_label = QLabel()
        user_layout.addRow("Username:", self.username_label)
        
        self.full_name_label = QLabel()
        user_layout.addRow("Full Name:", self.full_name_label)
        
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        user_layout.addRow("Description:", self.description_label)
        
        self.status_label = QLabel()
        user_layout.addRow("Status:", self.status_label)
        
        self.details_layout.addWidget(self.user_group)
        
        # Group details section
        self.group_group = QGroupBox("Group Details")
        self.group_group.setVisible(False)
        group_layout = QFormLayout(self.group_group)
        
        self.group_name_label = QLabel()
        group_layout.addRow("Name:", self.group_name_label)
        
        self.group_description_label = QLabel()
        self.group_description_label.setWordWrap(True)
        group_layout.addRow("Description:", self.group_description_label)
        
        self.members_label = QLabel()
        self.members_label.setWordWrap(True)
        group_layout.addRow("Members:", self.members_label)
        
        self.details_layout.addWidget(self.group_group)
        
        # Add empty space at the bottom
        self.details_layout.addStretch(1)
        
        # Set the widget for the scroll area
        scroll_area.setWidget(self.details_widget)
        self.main_layout.addWidget(scroll_area)
        
    def clear(self):
        """Clear all details."""
        self.user_group.setVisible(False)
        self.group_group.setVisible(False)
        
    @pyqtSlot(str, str, str, bool)
    def show_user_details(self, username, full_name, description, disabled):
        """Show details for a user.
        
        Args:
            username: Username
            full_name: Full name
            description: Account description
            disabled: Whether account is disabled
        """
        # Hide group details
        self.group_group.setVisible(False)
        
        # Update user details
        self.username_label.setText(username)
        self.full_name_label.setText(full_name)
        self.description_label.setText(description)
        self.status_label.setText("Disabled" if disabled else "Enabled")
        
        # Show user details
        self.user_group.setVisible(True)
        
    @pyqtSlot(str, str, list)
    def show_group_details(self, name, description, members):
        """Show details for a group.
        
        Args:
            name: Group name
            description: Group description
            members: List of member usernames
        """
        # Hide user details
        self.user_group.setVisible(False)
        
        # Update group details
        self.group_name_label.setText(name)
        self.group_description_label.setText(description)
        self.members_label.setText("\n".join(members) if members else "No members")
        
        # Show group details
        self.group_group.setVisible(True)
