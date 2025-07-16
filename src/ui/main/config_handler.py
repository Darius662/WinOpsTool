"""Configuration import/export handler."""
import yaml
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class ConfigHandler:
    """Handles configuration import/export operations."""
    
    def __init__(self, main_window):
        """Initialize with reference to main window."""
        self.main_window = main_window
        self.logger = logger
        
    def import_configuration(self):
        """Import and apply configuration from a YAML file."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self.main_window,
                "Import Configuration",
                "",
                "YAML Files (*.yaml *.yml);;All Files (*.*)"
            )
            
            if not file_path:
                return
                
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f)
                
            # Apply environment variables
            if "Environment Variables" in self.main_window.panels and "environment_variables" in config:
                panel = self.main_window.panels["Environment Variables"]
                env_vars = config["environment_variables"]
                
                # System variables
                for name, value in env_vars.get("system", {}).items():
                    panel.add_variable(name, value, "System Variables")
                    
                # User variables
                for name, value in env_vars.get("user", {}).items():
                    panel.add_variable(name, value, "User Variables")
                    
            # Apply registry settings
            if "Registry Editor" in self.main_window.panels and "registry" in config:
                panel = self.main_window.panels["Registry Editor"]
                for entry in config["registry"]:
                    panel.add_registry_key(entry["path"], entry["value"])
                    
            # Apply users and groups
            if "Users & Groups" in self.main_window.panels and "users" in config:
                panel = self.main_window.panels["Users & Groups"]
                users = config["users"]
                
                # Create users
                for user in users.get("create", []):
                    panel.add_user(
                        user["username"],
                        user["password"],
                        user.get("groups", []),
                        user.get("comment", "")
                    )
                    
                # Create groups
                for group in users.get("groups", []):
                    panel.add_group(
                        group["name"],
                        group.get("comment", ""),
                        group.get("members", [])
                    )
                    
            # Apply services configuration
            if "Services" in self.main_window.panels and "services" in config:
                panel = self.main_window.panels["Services"]
                for service in config["services"]:
                    panel.configure_service(
                        service["name"],
                        service.get("start_type", "auto"),
                        service.get("state", "running"),
                        service.get("description", "")
                    )
                    
            # Apply firewall rules
            if "Firewall" in self.main_window.panels and "firewall" in config:
                panel = self.main_window.panels["Firewall"]
                firewall = config["firewall"]
                
                # Inbound rules
                for rule in firewall.get("inbound", []):
                    panel.add_rule(
                        rule["name"],
                        "in",
                        rule["action"],
                        rule["protocol"],
                        rule.get("local_port", ""),
                        rule.get("remote_port", ""),
                        rule.get("enabled", True)
                    )
                    
                # Outbound rules
                for rule in firewall.get("outbound", []):
                    panel.add_rule(
                        rule["name"],
                        "out",
                        rule["action"],
                        rule["protocol"],
                        rule.get("local_port", ""),
                        rule.get("remote_port", ""),
                        rule.get("enabled", True)
                    )
                    
            # Apply software changes
            if "Software" in self.main_window.panels and "software" in config:
                panel = self.main_window.panels["Software"]
                software = config["software"]
                
                # Install software
                for item in software.get("install", []):
                    panel.install_software(
                        path=item["path"],
                        arguments=item.get("arguments", "")
                    )
                    
                # Uninstall software
                for item in software.get("uninstall", []):
                    panel.uninstall_software(item["name"])
                    
            # Apply permissions
            if "Permissions" in self.main_window.panels and "permissions" in config:
                panel = self.main_window.panels["Permissions"]
                for perm in config["permissions"]:
                    panel.set_permissions(
                        perm["path"],
                        perm["permissions"]
                    )
                    
            # Apply applications settings
            if "Applications" in self.main_window.panels and "applications" in config:
                panel = self.main_window.panels["Applications"]
                apps = config["applications"]
                
                # Configure startup items
                for item in apps.get("startup", []):
                    panel.add_startup_item(
                        item["name"],
                        item["command"],
                        item.get("enabled", True)
                    )
                    
                # Handle processes
                processes = apps.get("processes", {})
                
                # Stop processes
                for proc in processes.get("stop", []):
                    panel.stop_process(proc)
                    
                # Start processes
                for proc in processes.get("start", []):
                    panel.start_process(
                        proc["path"],
                        proc.get("arguments", "")
                    )
                    
            QMessageBox.information(
                self.main_window,
                "Import Complete",
                "Configuration has been imported and applied successfully."
            )
            
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {str(e)}")
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"Failed to import configuration: {str(e)}"
            )
