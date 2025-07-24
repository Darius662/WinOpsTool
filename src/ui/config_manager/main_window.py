"""Main window for WinOpsInit."""
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget,
                          QVBoxLayout, QMenuBar, QMenu, QMessageBox)
from PyQt6.QtGui import QAction, QIcon
import os.path
from src.core.logger import setup_logger
from src.ui.config_manager.help_window import HelpWindow
from src.ui.config_manager.config_handler import ConfigHandler
from src.ui.config_manager.tabs.environment_tab import EnvironmentTab
from src.ui.config_manager.tabs.registry_tab import RegistryTab
from src.ui.config_manager.tabs.users_tab import UsersTab
from src.ui.config_manager.tabs.services_tab import ServicesTab
from src.ui.config_manager.tabs.firewall_tab import FirewallTab
from src.ui.config_manager.tabs.software_tab import SoftwareTab
from src.ui.config_manager.tabs.permissions_tab import PermissionsTab
from src.ui.config_manager.tabs.applications_tab import ApplicationsTab
from src.ui.config_manager.tabs.welcome_tab import WelcomeTab

class ConfigManagerWindow(QMainWindow):
    """Main window for the WinOpsInit."""
    def __init__(self):
        super().__init__()
        self.logger = setup_logger(self.__class__.__name__)
        self.config_handler = ConfigHandler()
        self.setup_ui()
        self.setup_menu()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("WinOpsInit")
        self.setMinimumSize(800, 600)
        
        # Set window icon
        icon_path = os.path.join('assets', 'WinOpsInit.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Create central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Add tabs
        # Welcome tab first
        self.welcome_tab = WelcomeTab(self.config_handler)
        self.tab_widget.addTab(self.welcome_tab, "Welcome")
        
        self.environment_tab = EnvironmentTab(self.config_handler)
        self.tab_widget.addTab(self.environment_tab, "Environment Variables")

        self.registry_tab = RegistryTab(self.config_handler)
        self.tab_widget.addTab(self.registry_tab, "Registry")

        self.users_tab = UsersTab(self.config_handler)
        self.tab_widget.addTab(self.users_tab, "Users & Groups")

        self.services_tab = ServicesTab(self.config_handler)
        self.tab_widget.addTab(self.services_tab, "Services")

        self.firewall_tab = FirewallTab(self.config_handler)
        self.tab_widget.addTab(self.firewall_tab, "Firewall")

        self.software_tab = SoftwareTab(self.config_handler)
        self.tab_widget.addTab(self.software_tab, "Software")

        self.permissions_tab = PermissionsTab(self.config_handler)
        self.tab_widget.addTab(self.permissions_tab, "Permissions")

        self.applications_tab = ApplicationsTab(self.config_handler)
        self.tab_widget.addTab(self.applications_tab, "Applications")

    def setup_menu(self):
        """Set up the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        
        load_action = QAction("Load Config...", self)
        load_action.triggered.connect(lambda: self.config_handler.load_config())
        file_menu.addAction(load_action)

        save_action = QAction("Save Config...", self)
        save_action.triggered.connect(lambda: self.config_handler.save_config())
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        clear_action = QAction("Clear All", self)
        clear_action.triggered.connect(lambda: self.config_handler.clear_config())
        file_menu.addAction(clear_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("Help")
        
        help_action = QAction("Help Contents", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_help(self):
        """Show the help window."""
        self.help_window = HelpWindow()
        self.help_window.show()

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About WinOpsInit",
            """<h3>WinOpsTool - WinOpsInit</h3>
            <p>Version 1.0</p>
            <p>A tool for creating and managing system configuration files.</p>
            <p>Part of the Windows System Management Suite.</p>"""
        )

def main():
    """Main entry point."""
    try:
        app = QApplication(sys.argv)
        window = ConfigManagerWindow()
        window.show()
        return app.exec()
    except Exception as e:
        logger = setup_logger("ConfigManager")
        logger.exception("Unexpected error in config manager")
        QMessageBox.critical(
            None,
            "Error",
            f"Unexpected error: {str(e)}\n\n{str(sys.exc_info())}"
        )
        return 1

if __name__ == '__main__':
    sys.exit(main())
