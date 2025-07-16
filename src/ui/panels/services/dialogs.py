"""Dialogs for Windows Services management."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                          QComboBox, QDialogButtonBox)
from src.core.logger import setup_logger

class StartupTypeDialog(QDialog):
    """Dialog for changing service startup type."""
    
    def __init__(self, parent=None, current_type="Manual"):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
            current_type: Current startup type
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.current_type = current_type
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Change Startup Type")
        layout = QVBoxLayout(self)
        
        # Startup type combo
        type_layout = QHBoxLayout()
        type_label = QLabel("Startup Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Automatic", "Manual", "Disabled"])
        self.type_combo.setCurrentText(self.current_type)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_startup_type(self):
        """Get selected startup type.
        
        Returns:
            str: Selected startup type
        """
        return self.type_combo.currentText()
