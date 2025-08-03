"""Dialog components for credential management."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                           QLabel, QLineEdit, QComboBox, QPushButton,
                           QDialogButtonBox, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt
import win32cred
from src.core.logger import setup_logger

class CredentialDialog(QDialog):
    """Dialog for adding or editing credentials."""
    
    def __init__(self, parent=None, target_name="", username="", password="",
                credential_type=win32cred.CRED_TYPE_GENERIC,
                persistence=win32cred.CRED_PERSIST_LOCAL_MACHINE,
                comment="", edit_mode=False):
        """Initialize the credential dialog.
        
        Args:
            parent: Parent widget
            target_name: Target name for the credential
            username: Username
            password: Password
            credential_type: Credential type
            persistence: Persistence type
            comment: Comment
            edit_mode: Whether dialog is in edit mode
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.edit_mode = edit_mode
        
        # Set window properties
        self.setWindowTitle("Edit Credential" if edit_mode else "Add Credential")
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create form layout
        form_layout = QFormLayout()
        
        # Target name field
        self.target_name_edit = QLineEdit(target_name)
        if edit_mode:
            self.target_name_edit.setReadOnly(True)
        form_layout.addRow("Target Name:", self.target_name_edit)
        
        # Username field
        self.username_edit = QLineEdit(username)
        form_layout.addRow("Username:", self.username_edit)
        
        # Password field
        self.password_edit = QLineEdit(password)
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password:", self.password_edit)
        
        # Show password checkbox
        self.show_password_check = QCheckBox("Show Password")
        self.show_password_check.stateChanged.connect(self._toggle_password_visibility)
        form_layout.addRow("", self.show_password_check)
        
        # Credential type combo
        self.type_combo = QComboBox()
        self.type_combo.addItem("Generic", win32cred.CRED_TYPE_GENERIC)
        self.type_combo.addItem("Domain Password", win32cred.CRED_TYPE_DOMAIN_PASSWORD)
        self.type_combo.addItem("Domain Certificate", win32cred.CRED_TYPE_DOMAIN_CERTIFICATE)
        self.type_combo.addItem("Domain Visible Password", win32cred.CRED_TYPE_DOMAIN_VISIBLE_PASSWORD)
        self.type_combo.addItem("Generic Certificate", win32cred.CRED_TYPE_GENERIC_CERTIFICATE)
        self.type_combo.addItem("Domain Extended", win32cred.CRED_TYPE_DOMAIN_EXTENDED)
        
        # Set current type
        index = self.type_combo.findData(credential_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
            
        # In edit mode, credential type can't be changed
        if edit_mode:
            self.type_combo.setEnabled(False)
            
        form_layout.addRow("Credential Type:", self.type_combo)
        
        # Persistence combo
        self.persistence_combo = QComboBox()
        self.persistence_combo.addItem("Session", win32cred.CRED_PERSIST_SESSION)
        self.persistence_combo.addItem("Local Machine", win32cred.CRED_PERSIST_LOCAL_MACHINE)
        self.persistence_combo.addItem("Enterprise", win32cred.CRED_PERSIST_ENTERPRISE)
        
        # Set current persistence
        index = self.persistence_combo.findData(persistence)
        if index >= 0:
            self.persistence_combo.setCurrentIndex(index)
            
        form_layout.addRow("Persistence:", self.persistence_combo)
        
        # Comment field
        self.comment_edit = QLineEdit(comment)
        form_layout.addRow("Comment:", self.comment_edit)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def _toggle_password_visibility(self, state):
        """Toggle password visibility based on checkbox state."""
        if state == Qt.CheckState.Checked:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            
    def accept(self):
        """Handle dialog acceptance."""
        # Validate input
        if not self.target_name_edit.text():
            QMessageBox.warning(self, "Validation Error", "Target name is required.")
            return
            
        if not self.username_edit.text():
            QMessageBox.warning(self, "Validation Error", "Username is required.")
            return
            
        if not self.password_edit.text() and not self.edit_mode:
            QMessageBox.warning(self, "Validation Error", "Password is required.")
            return
            
        super().accept()
        
    def get_credential(self):
        """Get credential data from dialog.
        
        Returns:
            tuple: (target_name, username, password, credential_type, persistence, comment)
        """
        target_name = self.target_name_edit.text()
        username = self.username_edit.text()
        password = self.password_edit.text()
        credential_type = self.type_combo.currentData()
        persistence = self.persistence_combo.currentData()
        comment = self.comment_edit.text()
        
        return target_name, username, password, credential_type, persistence, comment
