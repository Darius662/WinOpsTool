"""Configuration management main class."""
import os
import yaml
import logging
from .validation import validate_config
from .defaults import get_default_config

class ConfigManager:
    """Handles configuration loading and saving."""
    
    def __init__(self):
        """Initialize WinOpsInit configuration manager."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = get_default_config()
        self.observers = []
        
    def load_config(self, file_path):
        """Load configuration from file.
        
        Args:
            file_path: Path to configuration file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If configuration is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Config file not found: {file_path}")
            
        try:
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)
                
            # Validate configuration
            validate_config(config)
            
            self.config = config
            self.notify_observers()
            self.logger.info(f"Loaded configuration from {file_path}")
            
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to parse config file: {str(e)}")
            raise ValueError(f"Invalid YAML format: {str(e)}")
            
        except ValueError as e:
            self.logger.error(f"Invalid configuration: {str(e)}")
            raise
            
    def save_config(self, file_path):
        """Save configuration to file.
        
        Args:
            file_path: Path to save configuration to
            
        Raises:
            OSError: If save fails
        """
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                yaml.safe_dump(
                    self.config,
                    f,
                    default_flow_style=False,
                    sort_keys=False
                )
                
            self.logger.info(f"Saved configuration to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save config file: {str(e)}")
            raise OSError(f"Failed to save configuration: {str(e)}")
            
    def get_config(self):
        """Get current configuration.
        
        Returns:
            dict: Current configuration
        """
        return self.config
        
    def set_config(self, config):
        """Set new configuration.
        
        Args:
            config: New configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate configuration
        validate_config(config)
        
        self.config = config
        self.notify_observers()
        self.logger.info("Configuration updated")
        
    def clear_config(self):
        """Reset configuration to defaults."""
        self.config = get_default_config()
        self.notify_observers()
        self.logger.info("Configuration reset to defaults")
        
    def add_observer(self, observer):
        """Add configuration change observer.
        
        Args:
            observer: Observer object with update() method
        """
        if observer not in self.observers:
            self.observers.append(observer)
            
    def remove_observer(self, observer):
        """Remove configuration change observer.
        
        Args:
            observer: Observer to remove
        """
        if observer in self.observers:
            self.observers.remove(observer)
            
    def notify_observers(self):
        """Notify all observers of configuration change."""
        for observer in self.observers:
            observer.update(self.config)
