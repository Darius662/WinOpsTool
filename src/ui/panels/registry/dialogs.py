"""Dialogs for registry management."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                          QLineEdit, QComboBox, QPushButton, QMessageBox)
from src.core.logger import setup_logger

class AddRegistryValueDialog(QDialog):
    """Dialog for adding/editing registry values."""
    
    # Registry value types
    REG_TYPES = [
        'REG_SZ',
        'REG_EXPAND_SZ',
        'REG_MULTI_SZ',
        'REG_DWORD',
        'REG_QWORD',
        'REG_BINARY'
    ]
    
    def __init__(self, parent=None, name="", value="", reg_type="REG_SZ"):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
            name: Initial value name
            value: Initial value
            reg_type: Initial value type
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.name = name
        self.value = value
        self.reg_type = reg_type
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Registry Value")
        layout = QVBoxLayout(self)
        
        # Name field
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_edit = QLineEdit(self.name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Type selector
        type_layout = QHBoxLayout()
        type_label = QLabel("Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.REG_TYPES)
        self.type_combo.setCurrentText(self.reg_type)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Value field
        value_layout = QHBoxLayout()
        value_label = QLabel("Value:")
        self.value_edit = QLineEdit(self.value)
        value_layout.addWidget(value_label)
        value_layout.addWidget(self.value_edit)
        layout.addLayout(value_layout)
        
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
                "Value name cannot be empty."
            )
            return
            
        # Validate value based on type
        reg_type = self.type_combo.currentText()
        try:
            self._validate_value(value, reg_type)
        except ValueError as e:
            QMessageBox.warning(
                self,
                "Invalid Input",
                str(e)
            )
            return
            
        self.accept()
        
    def get_value(self):
        """Get the registry value details.
        
        Returns:
            tuple: (name, value, type)
        """
        return (
            self.name_edit.text().strip(),
            self.value_edit.text().strip(),
            self.type_combo.currentText()
        )
        
    def _validate_value(self, value, reg_type):
        """Validate registry value based on type.
        
        Args:
            value: Value to validate
            reg_type: Registry value type
            
        Raises:
            ValueError: If value is invalid for type
        """
        if not value:
            raise ValueError("Value cannot be empty.")
            
        try:
            if reg_type == 'REG_DWORD':
                # Validate DWORD (32-bit integer)
                int_val = int(value, 0)  # Base 0 allows hex with 0x prefix
                if not (0 <= int_val <= 0xFFFFFFFF):
                    raise ValueError
                    
            elif reg_type == 'REG_QWORD':
                # Validate QWORD (64-bit integer)
                int_val = int(value, 0)
                if not (0 <= int_val <= 0xFFFFFFFFFFFFFFFF):
                    raise ValueError
                    
            elif reg_type == 'REG_BINARY':
                # Validate binary string (hex pairs)
                value = value.replace(' ', '')
                if not all(c in '0123456789ABCDEFabcdef' for c in value):
                    raise ValueError
                if len(value) % 2 != 0:
                    raise ValueError
                    
            elif reg_type == 'REG_MULTI_SZ':
                # Validate multi-string (semicolon separated)
                if ';' not in value:
                    raise ValueError("Multi-string values must be semicolon-separated.")
                    
        except ValueError:
            raise ValueError(
                f"Invalid value format for type {reg_type}."
            )


class AddRegistryDialog(QDialog):
    """Dialog for adding/editing registry entries."""
    
    # Registry value types
    REG_TYPES = [
        'REG_SZ',
        'REG_EXPAND_SZ',
        'REG_MULTI_SZ',
        'REG_DWORD',
        'REG_QWORD',
        'REG_BINARY'
    ]
    
    def __init__(self, parent=None, path="", name="", reg_type="REG_SZ", value=""):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
            path: Initial registry path
            name: Initial value name
            reg_type: Initial value type
            value: Initial value
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.path = path
        self.name = name
        self.reg_type = reg_type
        self.value = value
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Add Registry Entry")
        layout = QVBoxLayout(self)
        
        # Path field
        path_layout = QHBoxLayout()
        path_label = QLabel("Path:")
        self.path_edit = QLineEdit(self.path)
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_edit)
        layout.addLayout(path_layout)
        
        # Name field
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_edit = QLineEdit(self.name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Type selector
        type_layout = QHBoxLayout()
        type_label = QLabel("Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.REG_TYPES)
        self.type_combo.setCurrentText(self.reg_type)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Value field
        value_layout = QHBoxLayout()
        value_label = QLabel("Value:")
        self.value_edit = QLineEdit(self.value)
        value_layout.addWidget(value_label)
        value_layout.addWidget(self.value_edit)
        layout.addLayout(value_layout)
        
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
        path = self.path_edit.text().strip()
        name = self.name_edit.text().strip()
        value = self.value_edit.text().strip()
        
        if not path:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Registry path cannot be empty."
            )
            return
            
        if not name:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Value name cannot be empty."
            )
            return
            
        # Validate value based on type
        reg_type = self.type_combo.currentText()
        try:
            self._validate_value(value, reg_type)
        except ValueError as e:
            QMessageBox.warning(
                self,
                "Invalid Input",
                str(e)
            )
            return
            
        self.accept()
        
    def get_entry(self):
        """Get the registry entry details.
        
        Returns:
            tuple: (path, name, type, value)
        """
        return (
            self.path_edit.text().strip(),
            self.name_edit.text().strip(),
            self.type_combo.currentText(),
            self.value_edit.text().strip()
        )
        
    def _validate_value(self, value, reg_type):
        """Validate registry value based on type.
        
        Args:
            value: Value to validate
            reg_type: Registry value type
            
        Raises:
            ValueError: If value is invalid for type
        """
        if not value:
            raise ValueError("Value cannot be empty.")
            
        try:
            if reg_type == 'REG_DWORD':
                # Validate DWORD (32-bit integer)
                int_val = int(value, 0)  # Base 0 allows hex with 0x prefix
                if not (0 <= int_val <= 0xFFFFFFFF):
                    raise ValueError
                    
            elif reg_type == 'REG_QWORD':
                # Validate QWORD (64-bit integer)
                int_val = int(value, 0)
                if not (0 <= int_val <= 0xFFFFFFFFFFFFFFFF):
                    raise ValueError
                    
            elif reg_type == 'REG_BINARY':
                # Validate binary string (hex pairs)
                value = value.replace(' ', '')
                if not all(c in '0123456789ABCDEFabcdef' for c in value):
                    raise ValueError
                if len(value) % 2 != 0:
                    raise ValueError
                    
            elif reg_type == 'REG_MULTI_SZ':
                # Validate multi-string (semicolon separated)
                if ';' not in value:
                    raise ValueError("Multi-string values must be semicolon-separated.")
                    
        except ValueError:
            raise ValueError(
                f"Invalid value format for type {reg_type}."
            )
