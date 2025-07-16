"""Dialogs for firewall rule management."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                          QLineEdit, QComboBox, QDialogButtonBox)
from src.core.logger import setup_logger

class AddRuleDialog(QDialog):
    """Dialog for adding/editing firewall rules."""
    
    def __init__(self, parent=None, direction="inbound", rule_data=None):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
            direction: Rule direction ("inbound" or "outbound")
            rule_data: Optional dictionary with existing rule data for editing
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
        # Store direction
        self.direction = direction.capitalize()  # Ensure first letter is capitalized
        
        # Initialize default values
        self.name = ""
        self.action = "Allow"
        self.protocol = "TCP"
        self.local_ports = ""
        self.remote_ports = ""
        self.program = ""
        
        # If editing an existing rule, use its values
        self.is_edit_mode = rule_data is not None
        if self.is_edit_mode:
            self.name = rule_data.get('name', "")
            self.action = rule_data.get('action', "Allow")
            self.protocol = rule_data.get('protocol', "TCP")
            self.local_ports = rule_data.get('local_ports', "")
            self.remote_ports = rule_data.get('remote_ports', "")
            self.program = rule_data.get('program', "")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        # Set window title based on mode
        if self.is_edit_mode:
            self.setWindowTitle(f"Edit {self.direction} Firewall Rule")
        else:
            self.setWindowTitle(f"Add {self.direction} Firewall Rule")
        layout = QVBoxLayout(self)
        
        # Rule name
        name_layout = QHBoxLayout()
        name_label = QLabel("Rule Name:")
        self.name_edit = QLineEdit(self.name)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Direction (read-only in this dialog)
        direction_layout = QHBoxLayout()
        direction_label = QLabel("Direction:")
        self.direction_label = QLabel(self.direction)
        direction_layout.addWidget(direction_label)
        direction_layout.addWidget(self.direction_label)
        layout.addLayout(direction_layout)
        
        # Action
        action_layout = QHBoxLayout()
        action_label = QLabel("Action:")
        self.action_combo = QComboBox()
        self.action_combo.addItems(["Allow", "Block"])
        self.action_combo.setCurrentText(self.action)
        action_layout.addWidget(action_label)
        action_layout.addWidget(self.action_combo)
        layout.addLayout(action_layout)
        
        # Protocol
        protocol_layout = QHBoxLayout()
        protocol_label = QLabel("Protocol:")
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["TCP", "UDP", "Any"])
        self.protocol_combo.setCurrentText(self.protocol)
        protocol_layout.addWidget(protocol_label)
        protocol_layout.addWidget(self.protocol_combo)
        layout.addLayout(protocol_layout)
        
        # Local ports
        local_ports_layout = QHBoxLayout()
        local_ports_label = QLabel("Local Ports:")
        self.local_ports_edit = QLineEdit(self.local_ports)
        self.local_ports_edit.setPlaceholderText("e.g., 80,443 or 1000-2000")
        local_ports_layout.addWidget(local_ports_label)
        local_ports_layout.addWidget(self.local_ports_edit)
        layout.addLayout(local_ports_layout)
        
        # Remote ports
        remote_ports_layout = QHBoxLayout()
        remote_ports_label = QLabel("Remote Ports:")
        self.remote_ports_edit = QLineEdit(self.remote_ports)
        self.remote_ports_edit.setPlaceholderText("e.g., 80,443 or 1000-2000")
        remote_ports_layout.addWidget(remote_ports_label)
        remote_ports_layout.addWidget(self.remote_ports_edit)
        layout.addLayout(remote_ports_layout)
        
        # Program
        program_layout = QHBoxLayout()
        program_label = QLabel("Program:")
        self.program_edit = QLineEdit(self.program)
        self.program_edit.setPlaceholderText("e.g., C:\\Program Files\\App\\app.exe")
        program_layout.addWidget(program_label)
        program_layout.addWidget(self.program_edit)
        layout.addLayout(program_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def validate_and_accept(self):
        """Validate input and accept dialog."""
        name = self.name_edit.text().strip()
        if not name:
            self.logger.warning("Rule name is required")
            return
            
        self.accept()
        
    def get_rule(self):
        """Get the rule data.
        
        Returns:
            dict: Rule properties
        """
        return {
            'name': self.name_edit.text().strip(),
            'direction': self.direction,
            'action': self.action_combo.currentText(),
            'protocol': self.protocol_combo.currentText(),
            'local_ports': self.local_ports_edit.text().strip(),
            'remote_ports': self.remote_ports_edit.text().strip(),
            'program': self.program_edit.text().strip()
        }
