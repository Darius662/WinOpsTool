"""Main window for the System Management Tool."""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from src.core.logger import setup_logger
from src.core.privileges import is_admin
from .menu_handler import MenuHandler
from .toolbar_handler import ToolbarHandler
from .status_handler import StatusHandler
from .remote_handler import RemoteHandler
from .help_handler import HelpHandler

# Import panels
from src.ui.panels.environment import EnvironmentPanel
from src.ui.panels.registry import RegistryPanel
from src.ui.panels.users import UsersPanel
from src.ui.panels.services import ServicesPanel
from src.ui.panels.firewall import FirewallPanel
from src.ui.panels.software import SoftwarePanel
from src.ui.panels.permissions import PermissionsPanel
from src.ui.panels.applications import ApplicationsPanel

class MainWindow(QMainWindow):
    """Main window for the System Management Tool."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        # Check for admin privileges
        if not is_admin():
            raise PermissionError("This tool requires administrator privileges.")
            
        self.logger = setup_logger(self.__class__.__name__)
        
        # Create handlers
        self.menu_handler = MenuHandler(self)
        self.toolbar_handler = ToolbarHandler(self)
        self.status_handler = StatusHandler(self)
        self.remote_handler = RemoteHandler(self)
        self.help_handler = HelpHandler(self)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Windows System Management Tool")
        self.setMinimumSize(1024, 768)
        
        # Create central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add feature panels
        self.environment_panel = EnvironmentPanel(self)
        self.tab_widget.addTab(self.environment_panel, "Environment Variables")
        
        self.registry_panel = RegistryPanel(self)
        self.tab_widget.addTab(self.registry_panel, "Registry")
        
        self.users_panel = UsersPanel(self)
        self.tab_widget.addTab(self.users_panel, "Users & Groups")
        
        self.services_panel = ServicesPanel(self)
        self.tab_widget.addTab(self.services_panel, "Services")
        
        self.firewall_panel = FirewallPanel(self)
        self.tab_widget.addTab(self.firewall_panel, "Firewall")
        
        self.software_panel = SoftwarePanel(self)
        self.tab_widget.addTab(self.software_panel, "Software")
        
        self.permissions_panel = PermissionsPanel(self)
        self.tab_widget.addTab(self.permissions_panel, "Permissions")
        
        self.applications_panel = ApplicationsPanel(self)
        self.tab_widget.addTab(self.applications_panel, "Applications")
        
    def import_config(self):
        """Import configuration file."""
        # Implementation will be added when config system is ready
        self.logger.info("Import config requested")
        
    def apply_config(self):
        """Apply current configuration."""
        # Implementation will be added when config system is ready
        self.logger.info("Apply config requested")
        
    def update_remote_state(self, connected):
        """Update UI elements based on remote connection state.
        
        Args:
            connected: True if connected to remote system, False otherwise
        """
        # Update panel states
        for i in range(self.tab_widget.count()):
            panel = self.tab_widget.widget(i)
            if hasattr(panel, 'update_remote_state'):
                panel.update_remote_state(connected)

def main():
    """Main entry point."""
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        return app.exec()
    except Exception as e:
        logger = setup_logger("Main")
        logger.exception("Unexpected error")
        return 1

if __name__ == '__main__':
    sys.exit(main())
