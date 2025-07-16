"""Dialogs for Windows Services management."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                          QComboBox, QDialogButtonBox, QLineEdit, QTextEdit,
                          QGroupBox, QFormLayout, QTabWidget, QWidget, QCheckBox,
                          QRadioButton, QPushButton, QSpinBox, QScrollArea)
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


class EditServiceDialog(QDialog):
    """Dialog for editing service properties."""
    
    def __init__(self, parent=None, service=None):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
            service: Service data dictionary
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.service = service or {}
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle(f"Edit Service: {self.service.get('name', '')}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # General tab
        self.setup_general_tab()
        
        # Log On tab
        self.setup_logon_tab()
        
        # Recovery tab
        self.setup_recovery_tab()
        
        # Dependencies tab
        self.setup_dependencies_tab()
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def setup_general_tab(self):
        """Set up the General tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Service info form
        form_group = QGroupBox("Service Information")
        form_layout = QFormLayout(form_group)
        
        # Service name (read-only)
        self.name_edit = QLineEdit(self.service.get('name', ''))
        self.name_edit.setReadOnly(True)
        form_layout.addRow("Service Name:", self.name_edit)
        
        # Display name
        self.display_name_edit = QLineEdit(self.service.get('display_name', ''))
        form_layout.addRow("Display Name:", self.display_name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setText(self.service.get('description', ''))
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_edit)
        
        # Path
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(self.service.get('path', ''))
        path_layout.addWidget(self.path_edit)
        self.path_browse = QPushButton("Browse...")
        path_layout.addWidget(self.path_browse)
        form_layout.addRow("Path to executable:", path_layout)
        
        # Startup type group
        startup_group = QGroupBox("Startup Type")
        startup_layout = QVBoxLayout(startup_group)
        
        # Startup type
        self.startup_combo = QComboBox()
        self.startup_combo.addItems(["Automatic", "Manual", "Disabled"])
        self.startup_combo.setCurrentText(self.service.get('start_type', 'Manual'))
        startup_layout.addWidget(self.startup_combo)
        
        # Delayed start option
        self.delayed_start = QCheckBox("Delayed Start")
        self.delayed_start.setChecked(False)  # Default to unchecked
        startup_layout.addWidget(self.delayed_start)
        
        # Add startup group to form
        layout.addWidget(form_group)
        layout.addWidget(startup_group)
        
        # Service status group
        status_group = QGroupBox("Service Status")
        status_layout = QVBoxLayout(status_group)
        
        # Current status
        status_label = QLabel(f"Current Status: {self.service.get('state', 'Unknown')}")
        status_layout.addWidget(status_label)
        
        # Control buttons
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.pause_button = QPushButton("Pause")
        self.resume_button = QPushButton("Resume")
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.resume_button)
        status_layout.addLayout(control_layout)
        
        # Enable/disable buttons based on current state
        state = self.service.get('state', '').lower()
        self.start_button.setEnabled(state != 'running')
        self.stop_button.setEnabled(state == 'running')
        self.pause_button.setEnabled(state == 'running')
        self.resume_button.setEnabled(state == 'paused')
        
        layout.addWidget(status_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "General")
        
    def setup_logon_tab(self):
        """Set up the Log On tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Log on as group
        logon_group = QGroupBox("Log on as:")
        logon_layout = QVBoxLayout(logon_group)
        
        # Local System account
        self.local_system_radio = QRadioButton("Local System account")
        logon_layout.addWidget(self.local_system_radio)
        
        # Allow desktop interaction
        desktop_layout = QHBoxLayout()
        desktop_layout.addSpacing(20)  # Indent
        self.desktop_check = QCheckBox("Allow service to interact with desktop")
        desktop_layout.addWidget(self.desktop_check)
        logon_layout.addLayout(desktop_layout)
        
        # This account
        self.this_account_radio = QRadioButton("This account:")
        logon_layout.addWidget(self.this_account_radio)
        
        # Account name
        account_layout = QHBoxLayout()
        account_layout.addSpacing(20)  # Indent
        self.account_edit = QLineEdit(self.service.get('account', ''))
        account_layout.addWidget(self.account_edit)
        self.browse_button = QPushButton("Browse...")
        account_layout.addWidget(self.browse_button)
        logon_layout.addLayout(account_layout)
        
        # Password
        password_layout = QFormLayout()
        password_layout.setContentsMargins(20, 0, 0, 0)  # Indent
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addRow("Password:", self.password_edit)
        
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addRow("Confirm password:", self.confirm_password_edit)
        logon_layout.addLayout(password_layout)
        
        # Set initial radio button state based on account
        account = self.service.get('account', '').lower()
        if account == 'localsystem' or account == '':
            self.local_system_radio.setChecked(True)
            self.this_account_radio.setChecked(False)
            self.account_edit.setEnabled(False)
            self.password_edit.setEnabled(False)
            self.confirm_password_edit.setEnabled(False)
            self.browse_button.setEnabled(False)
        else:
            self.local_system_radio.setChecked(False)
            self.this_account_radio.setChecked(True)
            self.account_edit.setEnabled(True)
            self.password_edit.setEnabled(True)
            self.confirm_password_edit.setEnabled(True)
            self.browse_button.setEnabled(True)
        
        # Connect radio buttons
        self.local_system_radio.toggled.connect(self.on_logon_radio_toggled)
        self.this_account_radio.toggled.connect(self.on_logon_radio_toggled)
        
        layout.addWidget(logon_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Log On")
        
    def setup_recovery_tab(self):
        """Set up the Recovery tab."""
        tab = QScrollArea()
        tab.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # First failure
        first_group = QGroupBox("First failure:")
        first_layout = QVBoxLayout(first_group)
        self.first_action_combo = QComboBox()
        self.first_action_combo.addItems(["Take No Action", "Restart the Service", "Run a Program", "Restart the Computer"])
        first_layout.addWidget(self.first_action_combo)
        layout.addWidget(first_group)
        
        # Second failure
        second_group = QGroupBox("Second failure:")
        second_layout = QVBoxLayout(second_group)
        self.second_action_combo = QComboBox()
        self.second_action_combo.addItems(["Take No Action", "Restart the Service", "Run a Program", "Restart the Computer"])
        second_layout.addWidget(self.second_action_combo)
        layout.addWidget(second_group)
        
        # Subsequent failures
        subsequent_group = QGroupBox("Subsequent failures:")
        subsequent_layout = QVBoxLayout(subsequent_group)
        self.subsequent_action_combo = QComboBox()
        self.subsequent_action_combo.addItems(["Take No Action", "Restart the Service", "Run a Program", "Restart the Computer"])
        subsequent_layout.addWidget(self.subsequent_action_combo)
        layout.addWidget(subsequent_group)
        
        # Reset fail count
        reset_group = QGroupBox("Reset fail count after:")
        reset_layout = QHBoxLayout(reset_group)
        self.reset_days = QSpinBox()
        self.reset_days.setRange(1, 999)
        self.reset_days.setValue(1)
        reset_layout.addWidget(self.reset_days)
        reset_layout.addWidget(QLabel("days"))
        layout.addWidget(reset_group)
        
        # Restart service after
        restart_group = QGroupBox("Restart service after:")
        restart_layout = QHBoxLayout(restart_group)
        self.restart_minutes = QSpinBox()
        self.restart_minutes.setRange(1, 999)
        self.restart_minutes.setValue(1)
        restart_layout.addWidget(self.restart_minutes)
        restart_layout.addWidget(QLabel("minutes"))
        layout.addWidget(restart_group)
        
        # Run program
        run_group = QGroupBox("Run program:")
        run_layout = QVBoxLayout(run_group)
        
        # Program path
        path_layout = QHBoxLayout()
        self.program_path = QLineEdit()
        path_layout.addWidget(self.program_path)
        self.program_browse = QPushButton("Browse...")
        path_layout.addWidget(self.program_browse)
        run_layout.addLayout(path_layout)
        
        # Command line parameters
        self.program_params = QLineEdit()
        run_layout.addWidget(QLabel("Command line parameters:"))
        run_layout.addWidget(self.program_params)
        
        layout.addWidget(run_group)
        
        # Restart computer options
        restart_computer_group = QGroupBox("Restart computer options:")
        restart_computer_layout = QVBoxLayout(restart_computer_group)
        
        # Restart message
        restart_computer_layout.addWidget(QLabel("Message to show before restart:"))
        self.restart_message = QLineEdit()
        restart_computer_layout.addWidget(self.restart_message)
        
        layout.addWidget(restart_computer_group)
        layout.addStretch()
        
        tab.setWidget(content)
        self.tab_widget.addTab(tab, "Recovery")
        
    def setup_dependencies_tab(self):
        """Set up the Dependencies tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # This service depends on
        depends_group = QGroupBox("This service depends on the following system components:")
        depends_layout = QVBoxLayout(depends_group)
        
        # List of dependencies (read-only for now)
        self.depends_list = QTextEdit()
        self.depends_list.setReadOnly(True)
        depends_layout.addWidget(self.depends_list)
        
        layout.addWidget(depends_group)
        
        # Services that depend on this
        dependent_group = QGroupBox("The following system components depend on this service:")
        dependent_layout = QVBoxLayout(dependent_group)
        
        # List of dependent services (read-only for now)
        self.dependent_list = QTextEdit()
        self.dependent_list.setReadOnly(True)
        dependent_layout.addWidget(self.dependent_list)
        
        layout.addWidget(dependent_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Dependencies")
        
    def on_logon_radio_toggled(self, checked):
        """Handle logon radio button toggle."""
        if self.local_system_radio.isChecked():
            self.account_edit.setEnabled(False)
            self.password_edit.setEnabled(False)
            self.confirm_password_edit.setEnabled(False)
            self.browse_button.setEnabled(False)
            self.desktop_check.setEnabled(True)
        else:
            self.account_edit.setEnabled(True)
            self.password_edit.setEnabled(True)
            self.confirm_password_edit.setEnabled(True)
            self.browse_button.setEnabled(True)
            self.desktop_check.setEnabled(False)
        
    def get_service_data(self):
        """Get edited service data.
        
        Returns:
            dict: Updated service data
        """
        # Basic service data
        data = {
            'name': self.name_edit.text(),
            'display_name': self.display_name_edit.text(),
            'description': self.description_edit.toPlainText(),
            'path': self.path_edit.text(),
            'start_type': self.startup_combo.currentText(),
            'delayed_start': self.delayed_start.isChecked()
        }
        
        # Account information
        if self.local_system_radio.isChecked():
            data['account'] = 'LocalSystem'
            data['password'] = None
            data['desktop_interaction'] = self.desktop_check.isChecked()
        else:
            data['account'] = self.account_edit.text()
            # Only include password if both fields match and aren't empty
            if (self.password_edit.text() == self.confirm_password_edit.text() and 
                self.password_edit.text()):
                data['password'] = self.password_edit.text()
            else:
                data['password'] = None
            data['desktop_interaction'] = False
        
        # Recovery options
        action_map = {
            "Take No Action": "none",
            "Restart the Service": "restart",
            "Run a Program": "run_command",
            "Restart the Computer": "reboot"
        }
        
        data['recovery'] = {
            'first_action': action_map.get(self.first_action_combo.currentText(), "none"),
            'second_action': action_map.get(self.second_action_combo.currentText(), "none"),
            'subsequent_action': action_map.get(self.subsequent_action_combo.currentText(), "none"),
            'reset_period': self.reset_days.value() * 86400,  # Convert days to seconds
            'restart_delay': self.restart_minutes.value() * 60,  # Convert minutes to seconds
            'program_path': self.program_path.text(),
            'program_params': self.program_params.text(),
            'restart_message': self.restart_message.text()
        }
        
        return data
