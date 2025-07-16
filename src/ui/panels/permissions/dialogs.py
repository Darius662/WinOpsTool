"""Dialogs for Windows permissions."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                          QCheckBox, QDialogButtonBox)
import ntsecuritycon
from src.core.logger import setup_logger

class PermissionDialog(QDialog):
    """Dialog for adding/editing a permission."""
    
    def __init__(self, parent=None, name=None, current_mask=None):
        """Initialize permission dialog.
        
        Args:
            parent: Parent widget
            name: Optional name to pre-fill
            current_mask: Optional current permission mask
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setWindowTitle("Add Permission" if name is None else "Edit Permission")
        self.current_mask = current_mask
        self.setup_ui(name)
        
    def setup_ui(self, name=None):
        """Initialize the dialog UI.
        
        Args:
            name: Optional name to pre-fill
        """
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # User/Group name
        self.name_edit = QLineEdit()
        if name:
            self.name_edit.setText(name)
            self.name_edit.setReadOnly(True)
        form_layout.addRow("User/Group Name:", self.name_edit)
        
        # Permissions
        self.permissions = {
            "Full Control": ntsecuritycon.FILE_ALL_ACCESS,
            "Modify": ntsecuritycon.FILE_GENERIC_WRITE | ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE,
            "Read & Execute": ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE,
            "List Folder Contents": ntsecuritycon.FILE_LIST_DIRECTORY,
            "Read": ntsecuritycon.FILE_GENERIC_READ,
            "Write": ntsecuritycon.FILE_GENERIC_WRITE
        }
        
        self.permission_checks = {}
        for perm_name in self.permissions:
            self.permission_checks[perm_name] = QCheckBox(perm_name)
            if self.current_mask:
                self.permission_checks[perm_name].setChecked(
                    self.current_mask & self.permissions[perm_name] == self.permissions[perm_name]
                )
            form_layout.addRow("", self.permission_checks[perm_name])
            
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_permission_data(self):
        """Get the permission data from the dialog.
        
        Returns:
            dict: Permission data with name and mask
        """
        mask = 0
        for perm_name, check in self.permission_checks.items():
            if check.isChecked():
                mask |= self.permissions[perm_name]
                
        return {
            "name": self.name_edit.text(),
            "mask": mask
        }
