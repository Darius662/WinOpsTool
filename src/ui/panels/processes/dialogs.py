"""Dialogs for Windows Process management."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                          QComboBox, QDialogButtonBox)
from src.core.logger import setup_logger

class PriorityDialog(QDialog):
    """Dialog for changing process priority."""
    
    def __init__(self, parent=None, current_priority="Normal"):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
            current_priority: Current priority class
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.current_priority = current_priority
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Change Priority")
        layout = QVBoxLayout(self)
        
        # Priority combo
        priority_layout = QHBoxLayout()
        priority_label = QLabel("Priority:")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems([
            "Low",
            "Below Normal",
            "Normal",
            "Above Normal",
            "High",
            "Realtime"
        ])
        self.priority_combo.setCurrentText(self.current_priority)
        priority_layout.addWidget(priority_label)
        priority_layout.addWidget(self.priority_combo)
        layout.addLayout(priority_layout)
        
        # Warning for Realtime
        self.warning_label = QLabel(
            "Warning: Setting Realtime priority can make the system unresponsive!"
        )
        self.warning_label.setStyleSheet("color: red")
        self.warning_label.setVisible(False)
        layout.addWidget(self.warning_label)
        
        # Show warning when Realtime is selected
        self.priority_combo.currentTextChanged.connect(
            lambda text: self.warning_label.setVisible(text == "Realtime")
        )
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_priority(self):
        """Get selected priority.
        
        Returns:
            str: Selected priority class
        """
        return self.priority_combo.currentText()
