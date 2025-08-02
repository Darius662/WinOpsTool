"""Panel management for main window."""
from PyQt6.QtWidgets import QTabWidget
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class PanelManager:
    """Manages feature panels in the main window."""
    
    def __init__(self, parent):
        """Initialize panel manager.
        
        Args:
            parent: Parent window
        """
        self.logger = logger
        self.parent = parent
        self.tab_widget = QTabWidget(parent)
        self.panels = {}
        self.setup_panels()
        
        # Apply configuration if available
        if hasattr(parent, 'config') and parent.config:
            self.apply_config_to_panels(parent.config)
        
    def setup_panels(self):
        """Set up all feature panels."""
        # Welcome panel
        from ..panels.welcome import WelcomePanel
        welcome_panel = WelcomePanel(self.parent)
        self.tab_widget.addTab(welcome_panel, "Welcome")
        self.panels["Welcome"] = welcome_panel
        
        # Environment Variables panel
        from ..panels.environment import EnvironmentPanel
        env_panel = EnvironmentPanel(self.parent)
        self.tab_widget.addTab(env_panel, "Environment Variables")
        self.panels["Environment Variables"] = env_panel
        
        # Registry Editor panel
        from ..panels.registry import RegistryPanel
        reg_panel = RegistryPanel(self.parent)
        self.tab_widget.addTab(reg_panel, "Registry Editor")
        self.panels["Registry Editor"] = reg_panel
        
        # Users & Groups panel
        from ..panels.users import UsersPanel
        users_panel = UsersPanel(self.parent)
        self.tab_widget.addTab(users_panel, "Users & Groups")
        self.panels["Users & Groups"] = users_panel
        
        # Services panel
        from ..panels.services import ServicesPanel
        services_panel = ServicesPanel(self.parent)
        self.tab_widget.addTab(services_panel, "Services")
        self.panels["Services"] = services_panel
        
        # Firewall panel
        from ..panels.firewall import FirewallPanel
        firewall_panel = FirewallPanel(self.parent)
        self.tab_widget.addTab(firewall_panel, "Firewall")
        self.panels["Firewall"] = firewall_panel
        
        # Software panel
        from ..panels.software import SoftwarePanel
        software_panel = SoftwarePanel(self.parent)
        self.tab_widget.addTab(software_panel, "Software")
        self.panels["Software"] = software_panel
        
        # Permissions panel
        from ..panels.permissions import PermissionsPanel
        perms_panel = PermissionsPanel(self.parent)
        self.tab_widget.addTab(perms_panel, "Permissions")
        self.panels["Permissions"] = perms_panel
        
        # Applications panel
        from ..panels.applications import ApplicationsPanel
        apps_panel = ApplicationsPanel(self.parent)
        self.tab_widget.addTab(apps_panel, "Applications")
        self.panels["Applications"] = apps_panel
        
        # Disk panel
        from ..panels.disk import DiskPanel
        disk_panel = DiskPanel(self.parent)
        self.tab_widget.addTab(disk_panel, "Disk")
        self.panels["Disk"] = disk_panel
        
        # Drivers panel
        from ..panels.drivers import DriversPanel
        drivers_panel = DriversPanel(self.parent)
        self.tab_widget.addTab(drivers_panel, "Drivers")
        self.panels["Drivers"] = drivers_panel
        
        # Network panel
        from ..panels.network import NetworkPanel
        network_panel = NetworkPanel(self.parent)
        self.tab_widget.addTab(network_panel, "Network")
        self.panels["Network"] = network_panel
        
        # Packages panel
        from ..panels.packages import PackagesPanel
        packages_panel = PackagesPanel(self.parent)
        self.tab_widget.addTab(packages_panel, "Packages")
        self.panels["Packages"] = packages_panel
        
        # Processes panel
        from ..panels.processes import ProcessesPanel
        processes_panel = ProcessesPanel(self.parent)
        self.tab_widget.addTab(processes_panel, "Processes")
        self.panels["Processes"] = processes_panel
        
        # Scheduler panel
        from ..panels.scheduler import SchedulerPanel
        scheduler_panel = SchedulerPanel(self.parent)
        self.tab_widget.addTab(scheduler_panel, "Task Scheduler")
        self.panels["Task Scheduler"] = scheduler_panel
        
        # Events panel
        from ..panels.events import EventsPanel
        events_panel = EventsPanel(self.parent)
        self.tab_widget.addTab(events_panel, "Event Viewer")
        self.panels["Event Viewer"] = events_panel
        
        # Credentials panel
        from ..panels.credentials import CredentialsPanel
        credentials_panel = CredentialsPanel(self.parent)
        self.tab_widget.addTab(credentials_panel, "Credentials")
        self.panels["Credentials"] = credentials_panel
        
    def get_current_panel(self):
        """Get currently active panel.
        
        Returns:
            QWidget: Current panel widget or None
        """
        return self.tab_widget.currentWidget()
        
    def get_current_panel_name(self):
        """Get name of currently active panel.
        
        Returns:
            str: Current panel name
        """
        return self.tab_widget.tabText(self.tab_widget.currentIndex())
        
    def update_remote_state(self, connected):
        """Update all panels' remote state.
        
        Args:
            connected: True if connected to remote system
        """
        for i in range(self.tab_widget.count()):
            panel = self.tab_widget.widget(i)
            if hasattr(panel, 'update_remote_state'):
                panel.update_remote_state(connected)

    def update_panels_with_config(self, config):
        """Update panels to show imported configuration items without applying changes.
        
        This method marks items in the configuration as imported but does not
        apply any changes to the system. Items will be visually highlighted in the UI.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            bool: True if all panels were updated successfully, False otherwise
        """
        if not isinstance(config, dict):
            self.logger.warning("Invalid configuration format")
            return False
            
        self.logger.info(f"Updating panels with configuration: {list(config.keys())}")
        success = True
        
        # Update each panel based on its type
        for panel_name, panel in self.panels.items():
            try:
                # Determine which section of the config applies to this panel
                panel_config = {}
                
                # Map panel names to config sections
                if "Environment Variables" in panel_name and "environment_variables" in config:
                    panel_config = {"environment_variables": config["environment_variables"]}
                elif "Registry Editor" in panel_name and "registry" in config:
                    panel_config = {"registry": config["registry"]}
                elif "Users & Groups" in panel_name and "users" in config:
                    panel_config = {"users": config["users"]}
                elif "Services" in panel_name and "services" in config:
                    panel_config = {"services": config["services"]}
                elif "Firewall" in panel_name and "firewall" in config:
                    panel_config = {"firewall_rules": config["firewall"]}
                elif "Software" in panel_name and "software" in config:
                    panel_config = {"software": config["software"]}
                elif "Permissions" in panel_name and "permissions" in config:
                    panel_config = {"permissions": config["permissions"]}
                elif "Applications" in panel_name and "applications" in config:
                    panel_config = {"applications": config["applications"]}
                elif "Packages" in panel_name and "software" in config:
                    panel_config = {"software": config["software"]}
                
                # Update panel with configuration if available
                if panel_config and hasattr(panel, 'mark_config_items'):
                    self.logger.info(f"Updating {panel_name} panel with configuration")
                    if not panel.mark_config_items(panel_config):
                        success = False
                        
            except Exception as e:
                self.logger.error(f"Error updating {panel_name} panel with configuration: {str(e)}")
                success = False
                
        return success
        
    def apply_config_to_panels(self, config):
        """Apply configuration to all panels.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            bool: True if all panels were updated successfully, False otherwise
        """
        if not isinstance(config, dict):
            self.logger.warning("Invalid configuration format")
            return False
            
        self.logger.info(f"Applying configuration to panels: {list(config.keys())}")
        success = True
        
        # Apply configuration to each panel based on its type
        for panel_name, panel in self.panels.items():
            try:
                # Determine which section of the config applies to this panel
                panel_config = {}
                
                # Map panel names to config sections
                if "Environment Variables" in panel_name and "environment_variables" in config:
                    panel_config = {"environment_variables": config["environment_variables"]}
                elif "Registry Editor" in panel_name and "registry" in config:
                    panel_config = {"registry": config["registry"]}
                elif "Users & Groups" in panel_name and "users" in config:
                    panel_config = {"users": config["users"]}
                elif "Services" in panel_name and "services" in config:
                    panel_config = {"services": config["services"]}
                elif "Firewall" in panel_name and "firewall" in config:
                    panel_config = {"firewall_rules": config["firewall"]}
                elif "Software" in panel_name and "software" in config:
                    panel_config = {"software": config["software"]}
                elif "Permissions" in panel_name and "permissions" in config:
                    panel_config = {"permissions": config["permissions"]}
                elif "Applications" in panel_name and "applications" in config:
                    panel_config = {"applications": config["applications"]}
                elif "Packages" in panel_name and "software" in config:
                    panel_config = {"software": config["software"]}
                
                # Apply configuration if available for this panel
                if panel_config and hasattr(panel, 'apply_config'):
                    self.logger.info(f"Applying configuration to {panel_name} panel")
                    if not panel.apply_config(panel_config):
                        success = False
                    
            except Exception as e:
                self.logger.error(f"Error applying configuration to {panel_name} panel: {str(e)}")
                success = False
                
        return success
