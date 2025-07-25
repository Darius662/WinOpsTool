"""Dialogs for the Scheduler panel."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QTextEdit, QMessageBox, QTabWidget,
                          QWidget, QFormLayout, QLineEdit, QComboBox,
                          QCheckBox, QSpinBox, QDateTimeEdit, QGroupBox)
from PyQt6.QtCore import Qt, QDateTime
from src.core.logger import setup_logger

class TaskDetailsDialog(QDialog):
    """Dialog for viewing detailed task information."""
    
    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle(f"Task Details - {self.task_data.get('name', 'Unknown')}")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        
        # General tab
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        general_layout.addRow("Name:", QLabel(self.task_data.get('name', 'N/A')))
        general_layout.addRow("Status:", QLabel(self.task_data.get('status', 'N/A')))
        general_layout.addRow("Author:", QLabel(self.task_data.get('author', 'N/A')))
        general_layout.addRow("Description:", QLabel(self.task_data.get('comment', 'N/A')))
        general_layout.addRow("Last Run:", QLabel(self.task_data.get('last_run', 'N/A')))
        general_layout.addRow("Next Run:", QLabel(self.task_data.get('next_run', 'N/A')))
        general_layout.addRow("Last Result:", QLabel(self.task_data.get('last_result', 'N/A')))
        
        tab_widget.addTab(general_tab, "General")
        
        # Actions tab
        actions_tab = QWidget()
        actions_layout = QVBoxLayout(actions_tab)
        
        actions_layout.addWidget(QLabel("Task to Run:"))
        task_command = QTextEdit()
        task_command.setPlainText(self.task_data.get('task_to_run', 'N/A'))
        task_command.setReadOnly(True)
        task_command.setMaximumHeight(100)
        actions_layout.addWidget(task_command)
        
        actions_layout.addWidget(QLabel("Start In:"))
        start_in_label = QLabel(self.task_data.get('start_in', 'N/A'))
        actions_layout.addWidget(start_in_label)
        
        actions_layout.addStretch()
        tab_widget.addTab(actions_tab, "Actions")
        
        # Schedule tab
        schedule_tab = QWidget()
        schedule_layout = QFormLayout(schedule_tab)
        
        schedule_layout.addRow("Schedule Type:", QLabel(self.task_data.get('schedule_type', 'N/A')))
        schedule_layout.addRow("Schedule:", QLabel(self.task_data.get('schedule', 'N/A')))
        schedule_layout.addRow("Start Time:", QLabel(self.task_data.get('start_time', 'N/A')))
        schedule_layout.addRow("Start Date:", QLabel(self.task_data.get('start_date', 'N/A')))
        schedule_layout.addRow("End Date:", QLabel(self.task_data.get('end_date', 'N/A')))
        schedule_layout.addRow("Days:", QLabel(self.task_data.get('days', 'N/A')))
        schedule_layout.addRow("Months:", QLabel(self.task_data.get('months', 'N/A')))
        
        tab_widget.addTab(schedule_tab, "Schedule")
        
        # Settings tab
        settings_tab = QWidget()
        settings_layout = QFormLayout(settings_tab)
        
        settings_layout.addRow("Run As User:", QLabel(self.task_data.get('run_as_user', 'N/A')))
        settings_layout.addRow("Task State:", QLabel(self.task_data.get('scheduled_task_state', 'N/A')))
        settings_layout.addRow("Power Management:", QLabel(self.task_data.get('power_management', 'N/A')))
        settings_layout.addRow("Idle Time:", QLabel(self.task_data.get('idle_time', 'N/A')))
        settings_layout.addRow("Delete if not rescheduled:", QLabel(self.task_data.get('delete_task_if_not_rescheduled', 'N/A')))
        settings_layout.addRow("Stop if runs too long:", QLabel(self.task_data.get('stop_task_if_runs_x_hours_and_x_mins', 'N/A')))
        
        tab_widget.addTab(settings_tab, "Settings")
        
        layout.addWidget(tab_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)

class CreateTaskDialog(QDialog):
    """Dialog for creating a new scheduled task."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Create New Scheduled Task")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Basic information
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit()
        basic_layout.addRow("Task Name:", self.name_edit)
        
        self.description_edit = QLineEdit()
        basic_layout.addRow("Description:", self.description_edit)
        
        layout.addWidget(basic_group)
        
        # Action information
        action_group = QGroupBox("Action")
        action_layout = QFormLayout(action_group)
        
        self.program_edit = QLineEdit()
        action_layout.addRow("Program/Script:", self.program_edit)
        
        self.arguments_edit = QLineEdit()
        action_layout.addRow("Arguments:", self.arguments_edit)
        
        self.start_in_edit = QLineEdit()
        action_layout.addRow("Start In:", self.start_in_edit)
        
        layout.addWidget(action_group)
        
        # Trigger information
        trigger_group = QGroupBox("Trigger")
        trigger_layout = QFormLayout(trigger_group)
        
        self.trigger_type = QComboBox()
        self.trigger_type.addItems([
            "Daily",
            "Weekly", 
            "Monthly",
            "Once",
            "At startup",
            "At logon",
            "When idle"
        ])
        trigger_layout.addRow("Trigger Type:", self.trigger_type)
        
        self.start_time = QDateTimeEdit(QDateTime.currentDateTime())
        trigger_layout.addRow("Start Time:", self.start_time)
        
        layout.addWidget(trigger_group)
        
        # Settings
        settings_group = QGroupBox("Settings")
        settings_layout = QFormLayout(settings_group)
        
        self.enabled_check = QCheckBox()
        self.enabled_check.setChecked(True)
        settings_layout.addRow("Enabled:", self.enabled_check)
        
        self.run_with_highest_privileges = QCheckBox()
        settings_layout.addRow("Run with highest privileges:", self.run_with_highest_privileges)
        
        layout.addWidget(settings_group)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        create_button = QPushButton("Create")
        create_button.clicked.connect(self.accept)
        create_button.setDefault(True)
        button_layout.addWidget(create_button)
        
        layout.addLayout(button_layout)
        
    def get_task_data(self):
        """Get the task data from the dialog."""
        return {
            'name': self.name_edit.text(),
            'description': self.description_edit.text(),
            'program': self.program_edit.text(),
            'arguments': self.arguments_edit.text(),
            'start_in': self.start_in_edit.text(),
            'trigger_type': self.trigger_type.currentText(),
            'start_time': self.start_time.dateTime(),
            'enabled': self.enabled_check.isChecked(),
            'highest_privileges': self.run_with_highest_privileges.isChecked()
        }

class ConfirmTaskActionDialog(QDialog):
    """Dialog for confirming task actions like delete, disable, etc."""
    
    def __init__(self, action, task_name, parent=None):
        super().__init__(parent)
        self.action = action
        self.task_name = task_name
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle(f"Confirm {self.action.title()}")
        self.setModal(True)
        self.resize(350, 150)
        
        layout = QVBoxLayout(self)
        
        # Message
        message = QLabel(f"Are you sure you want to {self.action} the task:\n\n{self.task_name}")
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        confirm_button = QPushButton(self.action.title())
        confirm_button.clicked.connect(self.accept)
        confirm_button.setDefault(True)
        
        # Set button color based on action
        if self.action.lower() in ['delete', 'remove']:
            confirm_button.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; }")
        elif self.action.lower() in ['disable', 'stop']:
            confirm_button.setStyleSheet("QPushButton { background-color: #f57c00; color: white; }")
        else:
            confirm_button.setStyleSheet("QPushButton { background-color: #388e3c; color: white; }")
            
        button_layout.addWidget(confirm_button)
        
        layout.addLayout(button_layout)
