"""Settings dialog for application preferences."""
import os
import logging
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QPushButton, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt

from src.core.logger import setup_logger
import src.core.logging_config as logging_config

class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""
    
    def __init__(self, parent=None):
        """Initialize the settings dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setWindowTitle("Application Settings")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_current_settings()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Logging settings group
        logging_group = QGroupBox("Logging Settings")
        logging_layout = QFormLayout(logging_group)
        
        # Log level selector
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems([
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
        ])
        logging_layout.addRow("Log Level:", self.log_level_combo)
        
        # Log file path (display only)
        log_file_path = os.path.abspath(logging_config.LOG_FILE)
        log_file_label = QLabel(log_file_path)
        log_file_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        logging_layout.addRow("Log File:", log_file_label)
        
        layout.addWidget(logging_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_settings)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def load_current_settings(self):
        """Load current settings into the UI."""
        # Set current log level
        current_log_level = logging_config.LOG_LEVEL
        index = self.log_level_combo.findText(current_log_level)
        if index >= 0:
            self.log_level_combo.setCurrentIndex(index)
            
    def apply_settings(self):
        """Apply the current settings."""
        try:
            # Get selected log level
            new_log_level = self.log_level_combo.currentText()
            
            # Update logging_config.py
            self._update_logging_config(new_log_level)
            
            # Update current loggers
            self._update_active_loggers(new_log_level)
            
            self.logger.info(f"Log level changed to {new_log_level}")
            
        except Exception as e:
            self.logger.error(f"Error applying settings: {str(e)}")
            
    def accept_settings(self):
        """Apply settings and close dialog."""
        self.apply_settings()
        self.accept()
        
    def _update_logging_config(self, log_level):
        """Update the logging_config.py file with new log level.
        
        Args:
            log_level: New log level to set
        """
        config_path = os.path.abspath(logging_config.__file__)
        
        with open(config_path, 'r') as f:
            lines = f.readlines()
            
        # Find and replace the LOG_LEVEL line
        for i, line in enumerate(lines):
            if line.strip().startswith('LOG_LEVEL ='):
                lines[i] = f'LOG_LEVEL = "{log_level}"\n'
                break
                
        # Write updated content back to file
        with open(config_path, 'w') as f:
            f.writelines(lines)
            
    def _update_active_loggers(self, log_level):
        """Update all active loggers with the new log level.
        
        Args:
            log_level: New log level to set
        """
        # Get the numeric log level
        numeric_level = getattr(logging, log_level)
        
        # Update the root logger
        logging.getLogger().setLevel(numeric_level)
        
        # Update all existing loggers
        for name in logging.root.manager.loggerDict:
            if isinstance(logging.root.manager.loggerDict[name], logging.Logger):
                logging.getLogger(name).setLevel(numeric_level)
