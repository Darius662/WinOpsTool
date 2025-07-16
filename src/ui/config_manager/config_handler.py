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

    def load_config(self, file_path=None):
        """Load configuration from a YAML file.
        
        Args:
            file_path: Optional path to config file. If None, shows file dialog.
        """
        if file_path is None:
            file_path, _ = QFileDialog.getOpenFileName(
                None,
                "Load Configuration",
                "",
                "YAML Files (*.yaml *.yml);;All Files (*.*)"
            )
            
            # If user cancelled dialog, keep current config
            if not file_path:
                return
            
        try:
            with open(file_path, 'r') as f:
                content = yaml.safe_load(f)
                if content is None:
                    # Empty file, use default empty config
                    content = self.create_empty_config()
                elif not isinstance(content, dict):
                    raise ValueError("Configuration must be a dictionary")
                    
                # Validate against schema
                self._validate_config(content)
                    
                self.config = content
                self.notify_observers()
                self.logger.info(f"Loaded configuration from {file_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            QMessageBox.critical(
                None,
                "Error",
                f"Failed to load configuration: {str(e)}"
            )
            
    def _validate_config(self, config):
        """Validate configuration against schema.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Basic structure validation
        required_sections = [
            "environment_variables",
            "registry",
            "users",
            "services",
            "firewall",
            "software",
            "permissions",
            "applications"
        ]
        
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required section: {section}")
                
        # Environment variables validation
        env_vars = config["environment_variables"]
        if not isinstance(env_vars, dict):
            raise ValueError("environment_variables must be a dictionary")
        if "system" not in env_vars or "user" not in env_vars:
            raise ValueError("environment_variables must have system and user sections")
            
        # Registry validation
        if not isinstance(config["registry"], list):
            raise ValueError("registry must be a list")
            
        # Users validation
        users = config["users"]
        if not isinstance(users, dict):
            raise ValueError("users must be a dictionary")
        if "create" not in users or "groups" not in users:
            raise ValueError("users must have create and groups sections")
            
        # Services validation
        if not isinstance(config["services"], list):
            raise ValueError("services must be a list")
            
        # Firewall validation
        firewall = config["firewall"]
        if not isinstance(firewall, dict):
            raise ValueError("firewall must be a dictionary")
        if "inbound" not in firewall or "outbound" not in firewall:
            raise ValueError("firewall must have inbound and outbound sections")
            
        # Software validation
        software = config["software"]
        if not isinstance(software, dict):
            raise ValueError("software must be a dictionary")
        if "install" not in software or "uninstall" not in software:
            raise ValueError("software must have install and uninstall sections")
            
        # Permissions validation
        if not isinstance(config["permissions"], list):
            raise ValueError("permissions must be a list")
            
        # Applications validation
        apps = config["applications"]
        if not isinstance(apps, dict):
            raise ValueError("applications must be a dictionary")
        if "startup" not in apps or "processes" not in apps:
            raise ValueError("applications must have startup and processes sections")
            
        processes = apps["processes"]
        if not isinstance(processes, dict):
            raise ValueError("processes must be a dictionary")
        if "stop" not in processes or "start" not in processes:
            raise ValueError("processes must have stop and start sections")

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
