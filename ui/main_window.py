from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QTabWidget, QStatusBar)
from PyQt6.QtCore import Qt
from .panels.software_panel import SoftwarePanel
from .panels.environment_panel import EnvironmentPanel
from .panels.registry_panel import RegistryPanel
from .panels.users_panel import UsersPanel
from .panels.services_panel import ServicesPanel
from .panels.permissions_panel import PermissionsPanel
from .panels.firewall_panel import FirewallPanel
from .panels.apps_panel import ApplicationsPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Management Tool")
        self.setMinimumSize(1024, 768)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Add panels
        tabs.addTab(SoftwarePanel(), "Software Management")
        tabs.addTab(EnvironmentPanel(), "Environment Variables")
        tabs.addTab(RegistryPanel(), "Registry")
        tabs.addTab(UsersPanel(), "Users & Groups")
        tabs.addTab(ServicesPanel(), "Services")
        tabs.addTab(PermissionsPanel(), "Permissions")
        tabs.addTab(FirewallPanel(), "Firewall")
        tabs.addTab(ApplicationsPanel(), "Applications")
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
    def show_status(self, message, timeout=5000):
        self.status_bar.showMessage(message, timeout)
