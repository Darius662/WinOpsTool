"""Dialogs for user and group management."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                          QLineEdit, QCheckBox, QListWidget, QPushButton,
                          QMessageBox)
from src.core.logger import setup_logger

class AddUserDialog(QDialog):
    """Dialog for adding/editing user accounts."""
    
    def __init__(self, parent=None, username="", full_name="",
                description="", disabled=False):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
            username: Initial username
            full_name: Initial full name
            description: Initial description
            disabled: Initial disabled state
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.username = username
        self.full_name = full_name
        self.description = description
        self.disabled = disabled
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Add User Account")
        layout = QVBoxLayout(self)
        
        # Username field
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_edit = QLineEdit(self.username)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)
        
        # Password fields
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        layout.addLayout(password_layout)
        
        confirm_layout = QHBoxLayout()
        confirm_label = QLabel("Confirm Password:")
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_edit)
        layout.addLayout(confirm_layout)
        
        # Full name field
        full_name_layout = QHBoxLayout()
        full_name_label = QLabel("Full Name:")
        self.full_name_edit = QLineEdit(self.full_name)
        full_name_layout.addWidget(full_name_label)
        full_name_layout.addWidget(self.full_name_edit)
        layout.addLayout(full_name_layout)
        
        # Description field
        description_layout = QHBoxLayout()
        description_label = QLabel("Description:")
        self.description_edit = QLineEdit(self.description)
        description_layout.addWidget(description_label)
        description_layout.addWidget(self.description_edit)
        layout.addLayout(description_layout)
        
        # Disabled checkbox
        self.disabled_check = QCheckBox("Account is disabled")
        self.disabled_check.setChecked(self.disabled)
        layout.addWidget(self.disabled_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.validate_and_accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def validate_and_accept(self):
        """Validate input and accept dialog."""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        confirm = self.confirm_edit.text()
        full_name = self.full_name_edit.text().strip()
        
        if not username:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Username cannot be empty."
            )
            return
            
        if not self.username and not password:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Password is required for new accounts."
            )
            return
            
        if password and password != confirm:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Passwords do not match."
            )
            return
            
        self.accept()
        
    def get_user(self):
        """Get the user account details.
        
        Returns:
            tuple: (username, password, full_name, description, disabled)
        """
        return (
            self.username_edit.text().strip(),
            self.password_edit.text(),
            self.full_name_edit.text().strip(),
            self.description_edit.text().strip(),
            self.disabled_check.isChecked()
        )

class AddGroupDialog(QDialog):
    """Dialog for adding/editing user groups."""
    
    def __init__(self, parent=None, name="", description="", members=None,
                available_users=None):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
            name: Initial group name
            description: Initial description
            members: Initial list of member usernames
            available_users: List of available usernames
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.name = name
        self.description = description
        self.members = members or []
        self.available_users = available_users or []
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Add User Group")
        layout = QVBoxLayout(self)
        
        # Name field
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_edit = QLineEdit(self.name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Description field
        description_layout = QHBoxLayout()
        description_label = QLabel("Description:")
        self.description_edit = QLineEdit(self.description)
        description_layout.addWidget(description_label)
        description_layout.addWidget(self.description_edit)
        layout.addLayout(description_layout)
        
        # Members list
        members_label = QLabel("Members:")
        layout.addWidget(members_label)
        
        self.members_list = QListWidget()
        self.members_list.addItems(self.members)
        layout.addWidget(self.members_list)
        
        # Available users list
        available_label = QLabel("Available Users:")
        layout.addWidget(available_label)
        
        self.available_list = QListWidget()
        for user in self.available_users:
            if user not in self.members:
                self.available_list.addItem(user)
        layout.addWidget(self.available_list)
        
        # Add/Remove buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add >>")
        add_button.clicked.connect(self.add_member)
        button_layout.addWidget(add_button)
        
        remove_button = QPushButton("<< Remove")
        remove_button.clicked.connect(self.remove_member)
        button_layout.addWidget(remove_button)
        
        layout.addLayout(button_layout)
        
        # OK/Cancel buttons
        dialog_buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.validate_and_accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        dialog_buttons.addWidget(ok_button)
        dialog_buttons.addWidget(cancel_button)
        layout.addLayout(dialog_buttons)
        
    def add_member(self):
        """Add selected user to members list."""
        item = self.available_list.currentItem()
        if item:
            self.members_list.addItem(item.text())
            self.available_list.takeItem(
                self.available_list.row(item)
            )
            
    def remove_member(self):
        """Remove selected user from members list."""
        item = self.members_list.currentItem()
        if item:
            self.available_list.addItem(item.text())
            self.members_list.takeItem(
                self.members_list.row(item)
            )
            
    def validate_and_accept(self):
        """Validate input and accept dialog."""
        name = self.name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Group name cannot be empty."
            )
            return
            
        self.accept()
        
    def get_group(self):
        """Get the group details.
        
        Returns:
            tuple: (name, description, members)
        """
        members = []
        for i in range(self.members_list.count()):
            members.append(self.members_list.item(i).text())
            
        return (
            self.name_edit.text().strip(),
            self.description_edit.text().strip(),
            members
        )
