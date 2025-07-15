"""Dialog for handling environment variable conflicts during remote apply."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QTableWidget, QTableWidgetItem, QComboBox,
                          QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class EnvVarConflictDialog(QDialog):
    """Dialog for resolving environment variable conflicts."""
    
    def __init__(self, local_vars, remote_vars, remote_pc_name, parent=None):
        super().__init__(parent)
        self.local_vars = local_vars
        self.remote_vars = remote_vars
        self.remote_pc_name = remote_pc_name
        self.logger = setup_logger(self.__class__.__name__)
        self.resolution = {}  # Will store resolution choices
        self.setWindowTitle(f"Environment Variable Conflicts - {remote_pc_name}")
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Instructions
        layout.addWidget(QLabel(
            f"The following environment variables have different values on {self.remote_pc_name}. "
            "Please choose how to handle each conflict:"
        ))
        
        # Conflict table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Variable",
            "Local Value",
            "Remote Value",
            "Action"
        ])
        
        # Add conflicts to table
        conflicts = []
        for name, local_value in self.local_vars.items():
            if name in self.remote_vars and self.remote_vars[name] != local_value:
                conflicts.append((name, local_value, self.remote_vars[name]))
                
        self.table.setRowCount(len(conflicts))
        
        for row, (name, local_value, remote_value) in enumerate(conflicts):
            # Variable name
            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, name_item)
            
            # Local value
            local_item = QTableWidgetItem(local_value)
            local_item.setFlags(local_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, local_item)
            
            # Remote value
            remote_item = QTableWidgetItem(remote_value)
            remote_item.setFlags(remote_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, remote_item)
            
            # Action combo box
            action_combo = QComboBox()
            action_combo.addItems([
                "Keep Remote",
                "Use Local",
                "Skip"
            ])
            action_combo.setProperty("var_name", name)
            self.table.setCellWidget(row, 3, action_combo)
            
        self.table.resizeColumnsToContents()
        layout.addWidget(self.table)
        
        # Apply to all checkbox
        self.apply_all_check = QCheckBox("Apply same action to all conflicts")
        layout.addWidget(self.apply_all_check)
        self.apply_all_check.stateChanged.connect(self.apply_all_changed)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # Size
        self.resize(800, 400)
        
    def apply_all_changed(self, state):
        """Handle apply all checkbox state change."""
        if state == Qt.CheckState.Checked.value:
            # Get action from first row
            first_action = self.table.cellWidget(0, 3).currentText()
            
            # Apply to all other rows
            for row in range(1, self.table.rowCount()):
                self.table.cellWidget(row, 3).setCurrentText(first_action)
                
    def get_resolutions(self):
        """Get the resolution choices for each variable."""
        resolutions = {}
        
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()
            action = self.table.cellWidget(row, 3).currentText()
            
            if action == "Keep Remote":
                resolutions[name] = self.remote_vars[name]
            elif action == "Use Local":
                resolutions[name] = self.local_vars[name]
            # Skip means don't include in resolutions
            
        return resolutions
