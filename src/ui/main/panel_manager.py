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
