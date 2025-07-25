"""Dialogs for the Events panel."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                          QPushButton, QTextEdit, QMessageBox, QTabWidget,
                          QWidget, QFormLayout, QLineEdit, QComboBox,
                          QCheckBox, QSpinBox, QGroupBox, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.core.logger import setup_logger

class EventDetailsDialog(QDialog):
    """Dialog for viewing detailed event information."""
    
    def __init__(self, event_data, parent=None):
        super().__init__(parent)
        self.event_data = event_data
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle(f"Event Details - ID {self.event_data.get('event_id', 'Unknown')}")
        self.setModal(True)
        self.resize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        
        # General tab
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        # Event information
        general_layout.addRow("Event ID:", QLabel(self.event_data.get('event_id', 'N/A')))
        general_layout.addRow("Level:", QLabel(self.event_data.get('level', 'N/A')))
        general_layout.addRow("Date and Time:", QLabel(self.event_data.get('time_created', 'N/A')))
        general_layout.addRow("Source:", QLabel(self.event_data.get('provider', 'N/A')))
        general_layout.addRow("Computer:", QLabel(self.event_data.get('computer', 'N/A')))
        general_layout.addRow("Task Category:", QLabel(self.event_data.get('task', 'N/A')))
        general_layout.addRow("Keywords:", QLabel(self.event_data.get('keywords', 'N/A')))
        
        tab_widget.addTab(general_tab, "General")
        
        # Details tab
        details_tab = QWidget()
        details_layout = QVBoxLayout(details_tab)
        
        details_layout.addWidget(QLabel("Event Data:"))
        
        # Event data text area
        event_data_text = QTextEdit()
        event_data_text.setPlainText(self.event_data.get('event_data', 'No additional data available'))
        event_data_text.setReadOnly(True)
        event_data_text.setFont(QFont("Consolas", 9))
        details_layout.addWidget(event_data_text)
        
        tab_widget.addTab(details_tab, "Details")
        
        # Raw XML tab (if available)
        if 'xml_content' in self.event_data:
            xml_tab = QWidget()
            xml_layout = QVBoxLayout(xml_tab)
            
            xml_layout.addWidget(QLabel("Raw XML:"))
            
            xml_text = QTextEdit()
            xml_text.setPlainText(self.event_data.get('xml_content', ''))
            xml_text.setReadOnly(True)
            xml_text.setFont(QFont("Consolas", 8))
            xml_layout.addWidget(xml_text)
            
            tab_widget.addTab(xml_tab, "XML")
        
        layout.addWidget(tab_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        copy_button = QPushButton("Copy Details")
        copy_button.clicked.connect(self.copy_details)
        button_layout.addWidget(copy_button)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
    def copy_details(self):
        """Copy event details to clipboard."""
        try:
            from PyQt6.QtWidgets import QApplication
            
            details = f"Event ID: {self.event_data.get('event_id', 'N/A')}\n"
            details += f"Level: {self.event_data.get('level', 'N/A')}\n"
            details += f"Date and Time: {self.event_data.get('time_created', 'N/A')}\n"
            details += f"Source: {self.event_data.get('provider', 'N/A')}\n"
            details += f"Computer: {self.event_data.get('computer', 'N/A')}\n"
            details += f"Task Category: {self.event_data.get('task', 'N/A')}\n"
            details += f"Keywords: {self.event_data.get('keywords', 'N/A')}\n\n"
            details += f"Event Data:\n{self.event_data.get('event_data', 'No additional data available')}"
            
            clipboard = QApplication.clipboard()
            clipboard.setText(details)
            
            QMessageBox.information(self, "Copied", "Event details copied to clipboard.")
            
        except Exception as e:
            self.logger.error(f"Error copying details: {e}")
            QMessageBox.warning(self, "Error", "Failed to copy details to clipboard.")

class EventFilterDialog(QDialog):
    """Dialog for filtering events."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Filter Events")
        self.setModal(True)
        self.resize(400, 350)
        
        layout = QVBoxLayout(self)
        
        # Time range group
        time_group = QGroupBox("Time Range")
        time_layout = QFormLayout(time_group)
        
        self.hours_back = QSpinBox()
        self.hours_back.setRange(1, 8760)  # 1 hour to 1 year
        self.hours_back.setValue(24)
        self.hours_back.setSuffix(" hours")
        time_layout.addRow("Show events from last:", self.hours_back)
        
        layout.addWidget(time_group)
        
        # Level filter group
        level_group = QGroupBox("Event Levels")
        level_layout = QVBoxLayout(level_group)
        
        self.critical_check = QCheckBox("Critical")
        self.critical_check.setChecked(True)
        level_layout.addWidget(self.critical_check)
        
        self.error_check = QCheckBox("Error")
        self.error_check.setChecked(True)
        level_layout.addWidget(self.error_check)
        
        self.warning_check = QCheckBox("Warning")
        self.warning_check.setChecked(True)
        level_layout.addWidget(self.warning_check)
        
        self.information_check = QCheckBox("Information")
        self.information_check.setChecked(True)
        level_layout.addWidget(self.information_check)
        
        self.verbose_check = QCheckBox("Verbose")
        self.verbose_check.setChecked(False)
        level_layout.addWidget(self.verbose_check)
        
        layout.addWidget(level_group)
        
        # Maximum events
        max_events_group = QGroupBox("Limit")
        max_events_layout = QFormLayout(max_events_group)
        
        self.max_events = QSpinBox()
        self.max_events.setRange(10, 10000)
        self.max_events.setValue(100)
        max_events_layout.addRow("Maximum events:", self.max_events)
        
        layout.addWidget(max_events_group)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.reset_filters)
        button_layout.addWidget(reset_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.accept)
        apply_button.setDefault(True)
        button_layout.addWidget(apply_button)
        
        layout.addLayout(button_layout)
        
    def reset_filters(self):
        """Reset all filters to default values."""
        self.hours_back.setValue(24)
        self.critical_check.setChecked(True)
        self.error_check.setChecked(True)
        self.warning_check.setChecked(True)
        self.information_check.setChecked(True)
        self.verbose_check.setChecked(False)
        self.max_events.setValue(100)
        
    def get_filter_settings(self):
        """Get the current filter settings."""
        levels = []
        if self.critical_check.isChecked():
            levels.append(1)  # Critical
        if self.error_check.isChecked():
            levels.append(2)  # Error
        if self.warning_check.isChecked():
            levels.append(3)  # Warning
        if self.information_check.isChecked():
            levels.append(4)  # Information
        if self.verbose_check.isChecked():
            levels.append(5)  # Verbose
            
        return {
            'hours_back': self.hours_back.value(),
            'level_filter': levels if levels else None,
            'max_events': self.max_events.value()
        }

class ExportEventsDialog(QDialog):
    """Dialog for exporting events."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Export Events")
        self.setModal(True)
        self.resize(450, 300)
        
        layout = QVBoxLayout(self)
        
        # Export format
        format_group = QGroupBox("Export Format")
        format_layout = QVBoxLayout(format_group)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "Event Log (.evtx)",
            "XML (.xml)",
            "CSV (.csv)",
            "Text (.txt)"
        ])
        format_layout.addWidget(self.format_combo)
        
        layout.addWidget(format_group)
        
        # File path
        path_group = QGroupBox("Export Location")
        path_layout = QHBoxLayout(path_group)
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select export file path...")
        path_layout.addWidget(self.path_edit)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_file)
        path_layout.addWidget(browse_button)
        
        layout.addWidget(path_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.include_details = QCheckBox("Include detailed event data")
        self.include_details.setChecked(True)
        options_layout.addWidget(self.include_details)
        
        self.compress_file = QCheckBox("Compress exported file")
        self.compress_file.setChecked(False)
        options_layout.addWidget(self.compress_file)
        
        layout.addWidget(options_group)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        export_button = QPushButton("Export")
        export_button.clicked.connect(self.accept)
        export_button.setDefault(True)
        button_layout.addWidget(export_button)
        
        layout.addLayout(button_layout)
        
    def browse_file(self):
        """Browse for export file location."""
        from PyQt6.QtWidgets import QFileDialog
        
        format_text = self.format_combo.currentText()
        if "Event Log" in format_text:
            filter_str = "Event Log Files (*.evtx)"
            default_ext = ".evtx"
        elif "XML" in format_text:
            filter_str = "XML Files (*.xml)"
            default_ext = ".xml"
        elif "CSV" in format_text:
            filter_str = "CSV Files (*.csv)"
            default_ext = ".csv"
        else:
            filter_str = "Text Files (*.txt)"
            default_ext = ".txt"
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Events",
            f"events{default_ext}",
            filter_str
        )
        
        if file_path:
            self.path_edit.setText(file_path)
            
    def get_export_settings(self):
        """Get the export settings."""
        return {
            'format': self.format_combo.currentText(),
            'file_path': self.path_edit.text(),
            'include_details': self.include_details.isChecked(),
            'compress': self.compress_file.isChecked()
        }
