"""Dialogs for startup management."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                          QLineEdit, QComboBox, QPushButton, QMessageBox,
                          QCheckBox)
from src.core.logger import setup_logger

class AddStartupDialog(QDialog):
    """Dialog for adding startup entries."""
    
    def __init__(self, parent=None, name="", command="", user_specific=True):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
            name: Initial name
            command: Initial command
            user_specific: Initial user-specific setting
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.name = name
        self.command = command
        self.user_specific = user_specific
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Add Startup Entry")
        layout = QVBoxLayout(self)
        
        # Name field
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_edit = QLineEdit(self.name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Command field
        command_layout = QHBoxLayout()
        command_label = QLabel("Command:")
        self.command_edit = QLineEdit(self.command)
        command_layout.addWidget(command_label)
        command_layout.addWidget(self.command_edit)
        layout.addLayout(command_layout)
        
        # User-specific checkbox
        self.user_check = QCheckBox("User-specific (HKCU)")
        self.user_check.setChecked(self.user_specific)
        layout.addWidget(self.user_check)
        
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
        name = self.name_edit.text().strip()
        command = self.command_edit.text().strip()
        
        if not name:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Name cannot be empty."
            )
            return
            
        if not command:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Command cannot be empty."
            )
            return
            
        self.accept()
        
    def get_entry(self):
        """Get the startup entry details.
        
        Returns:
            tuple: (name, command, user_specific)
        """
        return (
            self.name_edit.text().strip(),
            self.command_edit.text().strip(),
            self.user_check.isChecked()
        )
