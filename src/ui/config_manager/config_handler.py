"""Configuration handler for Configuration Manager."""
import yaml
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from src.core.logger import setup_logger
from src.core.config_schema import CONFIG_SCHEMA

class ConfigHandler:
    """Handles configuration loading, saving, and management."""
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)
        self.config = self.create_empty_config()
        self.observers = []  # List of tabs to notify of config changes

    def create_empty_config(self):
        """Create an empty configuration dictionary."""
        return {
            "environment_variables": {
                "system": {},
                "user": {}
            },
            "registry": [],
            "users": {
                "create": [],
                "groups": []
            },
            "services": [],
            "firewall": {
                "inbound": [],
                "outbound": []
            },
            "software": {
                "install": [],
                "uninstall": []
            },
            "permissions": [],
            "applications": {
                "startup": [],
                "processes": {
                    "stop": [],
                    "start": []
                }
            }
        }

    def add_observer(self, observer):
        """Add a tab to notify of configuration changes."""
        self.observers.append(observer)

    def notify_observers(self):
        """Notify all tabs of configuration changes."""
        for observer in self.observers:
            observer.on_config_changed()

    def load_config(self):
        """Load configuration from a YAML file."""
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Load Configuration",
            "",
            "YAML Files (*.yaml *.yml);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                self.notify_observers()
                self.logger.info(f"Loaded configuration from {file_path}")
            except Exception as e:
                self.logger.error(f"Failed to load configuration: {str(e)}")
                QMessageBox.critical(
                    None,
                    "Error",
                    f"Failed to load configuration: {str(e)}"
                )

    def save_config(self):
        """Save configuration to a YAML file."""
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Save Configuration",
            "",
            "YAML Files (*.yaml);;All Files (*.*)"
        )
        
        if file_path:
            if not file_path.endswith('.yaml'):
                file_path += '.yaml'
                
            try:
                with open(file_path, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False)
                self.logger.info(f"Saved configuration to {file_path}")
            except Exception as e:
                self.logger.error(f"Failed to save configuration: {str(e)}")
                QMessageBox.critical(
                    None,
                    "Error",
                    f"Failed to save configuration: {str(e)}"
                )

    def clear_config(self):
        """Clear all configuration settings."""
        reply = QMessageBox.question(
            None,
            "Confirm Clear",
            "Are you sure you want to clear all settings?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config = self.create_empty_config()
            self.notify_observers()

    def get_config(self, section=None):
        """Get the current configuration or a specific section."""
        if section:
            return self.config.get(section, {})
        return self.config

    def update_config(self, section, data):
        """Update a section of the configuration."""
        self.config[section] = data
        self.notify_observers()
