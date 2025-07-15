"""Dialogs for environment variables management."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                          QLineEdit, QComboBox, QPushButton, QMessageBox)
from src.core.logger import setup_logger

class AddVariableDialog(QDialog):
    """Dialog for adding/editing environment variables."""
    
    def __init__(self, parent=None, name="", value="", var_type="User"):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
            name: Initial variable name
            value: Initial variable value
            var_type: Initial variable type
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.name = name
        self.value = value
        self.var_type = var_type
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Add Environment Variable")
        layout = QVBoxLayout(self)
        
        # Name field
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_edit = QLineEdit(self.name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Value field
        value_layout = QHBoxLayout()
        value_label = QLabel("Value:")
        self.value_edit = QLineEdit(self.value)
        value_layout.addWidget(value_label)
        value_layout.addWidget(self.value_edit)
        layout.addLayout(value_layout)
        
        # Type selector
        type_layout = QHBoxLayout()
        type_label = QLabel("Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["User", "System"])
        self.type_combo.setCurrentText(self.var_type)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
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
        value = self.value_edit.text().strip()
        
        if not name:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Variable name cannot be empty."
            )
            return
            
        if not value:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Variable value cannot be empty."
            )
            return
            
        self.accept()
        
    def get_variable(self):
        """Get the variable details.
        
        Returns:
            Tuple of (name, value, type)
        """
        return (
            self.name_edit.text().strip(),
            self.value_edit.text().strip(),
            self.type_combo.currentText()
        )
