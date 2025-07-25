"""Dialog for adding network drives."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                          QLineEdit, QRadioButton, QGroupBox, QCheckBox,
                          QPushButton, QDialogButtonBox, QMessageBox,
                          QComboBox)
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class NetworkDriveDialog(QDialog):
    """Dialog for adding network drives."""
    
    def __init__(self, parent=None):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.parent = parent
        self.disk_manager = None
        
        # Get disk manager from parent if available
        if hasattr(parent, 'manager'):
            self.disk_manager = parent.manager
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Add Network Drive")
        self.resize(450, 300)
        layout = QVBoxLayout(self)
        
        # Network path
        path_layout = QHBoxLayout()
        path_label = QLabel("Network Path:")
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(r"\\server\share")
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_edit)
        layout.addLayout(path_layout)
        
        # Drive letter dropdown
        drive_layout = QHBoxLayout()
        drive_label = QLabel("Drive Letter:")
        self.drive_combo = QComboBox()
        self.populate_drive_letters()
        drive_layout.addWidget(drive_label)
        drive_layout.addWidget(self.drive_combo)
        layout.addLayout(drive_layout)
        
        # Credentials group
        cred_group = QGroupBox("Credentials")
        cred_layout = QVBoxLayout(cred_group)
        
        # Windows credentials
        self.windows_cred = QRadioButton("Use current Windows credentials")
        self.windows_cred.setChecked(True)
        cred_layout.addWidget(self.windows_cred)
        
        # Custom credentials
        self.custom_cred = QRadioButton("Use custom credentials")
        cred_layout.addWidget(self.custom_cred)
        
        # Custom credentials fields
        custom_fields = QVBoxLayout()
        
        # Username
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_edit = QLineEdit()
        self.username_edit.setEnabled(False)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        custom_fields.addLayout(username_layout)
        
        # Password
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setEnabled(False)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        custom_fields.addLayout(password_layout)
        
        cred_layout.addLayout(custom_fields)
        layout.addWidget(cred_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.reconnect = QCheckBox("Reconnect at sign-in")
        self.reconnect.setChecked(True)
        options_layout.addWidget(self.reconnect)
        
        layout.addWidget(options_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Connect signals
        self.windows_cred.toggled.connect(self.toggle_credentials)
        self.custom_cred.toggled.connect(self.toggle_credentials)
        
    def toggle_credentials(self, checked):
        """Toggle custom credentials fields based on radio button selection."""
        self.username_edit.setEnabled(self.custom_cred.isChecked())
        self.password_edit.setEnabled(self.custom_cred.isChecked())
        
    def populate_drive_letters(self):
        """Populate the drive letters dropdown with available and used drives."""
        try:
            # Clear the combo box
            self.drive_combo.clear()
            
            # Get drive letters information
            if self.disk_manager:
                drive_info = self.disk_manager.get_drive_letters_info()
            else:
                # Fallback if disk_manager is not available
                drive_info = {
                    'all_letters': [f"{chr(i)}:" for i in range(65, 91)],
                    'used_letters': [],
                    'available_letters': [f"{chr(i)}:" for i in range(67, 91)],  # C-Z
                    'reserved_letters': ["A:", "B:"]
                }
            
            # Add available drives first (with "Available" suffix)
            for letter in drive_info['available_letters']:
                self.drive_combo.addItem(f"{letter} (Available)", letter)
                
            # Add used drives (with their type or "In Use" suffix)
            if self.disk_manager:
                volumes = self.disk_manager.get_volumes()
                for vol in volumes:
                    if vol['device']:
                        drive_letter = vol['device'].rstrip('\\')
                        drive_type = vol['type']
                        self.drive_combo.addItem(f"{drive_letter} ({drive_type})", drive_letter)
            else:
                for letter in drive_info['used_letters']:
                    self.drive_combo.addItem(f"{letter} (In Use)", letter)
                    
            # Select first available drive by default
            if self.drive_combo.count() > 0:
                self.drive_combo.setCurrentIndex(0)
                
        except Exception as e:
            self.logger.error(f"Error populating drive letters: {str(e)}")
            # Add some default values in case of error
            for letter in [f"{chr(i)}:" for i in range(67, 91)]:  # C-Z
                self.drive_combo.addItem(letter, letter)
    
    def validate_and_accept(self):
        """Validate inputs before accepting."""
        # Check network path
        if not self.path_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Network path is required.")
            return
            
        # Check if a drive letter is selected
        if self.drive_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Validation Error", "Drive letter is required.")
            return
            
        # Check custom credentials if selected
        if self.custom_cred.isChecked():
            if not self.username_edit.text().strip():
                QMessageBox.warning(self, "Validation Error", "Username is required.")
                return
                
        # All validations passed
        self.accept()
        
    def get_values(self):
        """Get the dialog values.
        
        Returns:
            dict: Dictionary with dialog values
        """
        # Get the actual drive letter from the combo box's user data
        drive_letter = self.drive_combo.currentData()
        
        return {
            'network_path': self.path_edit.text().strip(),
            'drive_letter': drive_letter,
            'use_windows_credentials': self.windows_cred.isChecked(),
            'username': self.username_edit.text() if self.custom_cred.isChecked() else '',
            'password': self.password_edit.text() if self.custom_cred.isChecked() else '',
            'reconnect': self.reconnect.isChecked()
        }
