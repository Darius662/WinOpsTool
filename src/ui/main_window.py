"""Main application window."""
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
    QApplication, QMenuBar, QMessageBox, QMenu, QFileDialog)
from src.core.logger import setup_logger
from src.core.privileges import is_admin
from src.ui.help.help_window import HelpWindow
from src.ui.main.menu_handler import MenuHandler
from src.ui.main.remote_handler import RemoteHandler
from src.ui.main.config_handler import ConfigHandler
from src.ui.main.help_handler import HelpHandler
from src.ui.dialogs.connection_dialog import ConnectionDialog

logger = setup_logger(__name__)

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        # Check for admin privileges
        if not is_admin():
            raise PermissionError("This tool requires administrator privileges.")
            
        # Initialize QApplication if not already done
        if not QApplication.instance():
            app = QApplication(sys.argv)
            
        super().__init__()
        
        self.logger = logger
        
        # Create handlers in dependency order
        self.remote_handler = RemoteHandler(self)
        self.config_handler = ConfigHandler(self)
        self.help_handler = HelpHandler(self)
        self.menu_handler = MenuHandler(self)  # MenuHandler depends on other handlers
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the main window UI components."""
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
        self.panels = {}
        
        # Environment Variables panel
        from .panels.environment_panel import EnvironmentPanel
        env_panel = EnvironmentPanel(self)
        self.tab_widget.addTab(env_panel, "Environment Variables")
        self.panels["Environment Variables"] = env_panel
        
        # Registry Editor panel
        from .panels.registry import RegistryPanel
        reg_panel = RegistryPanel(self)
        self.tab_widget.addTab(reg_panel, "Registry Editor")
        self.panels["Registry Editor"] = reg_panel
        
        # Users & Groups panel
        from .panels.users_panel import UsersPanel
        users_panel = UsersPanel(self)
        self.tab_widget.addTab(users_panel, "Users & Groups")
        self.panels["Users & Groups"] = users_panel
        
        # Services panel
        from .panels.services_panel import ServicesPanel
        services_panel = ServicesPanel(self)
        self.tab_widget.addTab(services_panel, "Services")
        self.panels["Services"] = services_panel
        
        # Firewall panel
        from .panels.firewall_panel import FirewallPanel
        firewall_panel = FirewallPanel(self)
        self.tab_widget.addTab(firewall_panel, "Firewall")
        self.panels["Firewall"] = firewall_panel
        
        # Software panel
        from .panels.software_panel import SoftwarePanel
        software_panel = SoftwarePanel(self)
        self.tab_widget.addTab(software_panel, "Software")
        self.panels["Software"] = software_panel
        
        # Permissions panel
        from .panels.permissions_panel import PermissionsPanel
        perms_panel = PermissionsPanel(self)
        self.tab_widget.addTab(perms_panel, "Permissions")
        self.panels["Permissions"] = perms_panel
        
        # Applications panel
        from .panels.applications_panel import ApplicationsPanel
        apps_panel = ApplicationsPanel(self)
        self.tab_widget.addTab(apps_panel, "Applications")
        self.panels["Applications"] = apps_panel
        
        # Create menu bar
        self.menubar = QMenuBar()
        self.setMenuBar(self.menubar)
        
        # Set up menu
        self.setup_menu()
        
    def setup_menu(self):
        """Set up the menu bar."""
        # File menu
        file_menu = QMenu("File", self)
        self.menubar.addMenu(file_menu)
        
        # File actions
        import_config = file_menu.addAction("Import Configuration...")
        import_config.triggered.connect(self.import_configuration)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Remote menu
        remote_menu = QMenu("Remote", self)
        self.menubar.addMenu(remote_menu)
        
        # Remote actions
        manage_connections = remote_menu.addAction("Manage Connections...")
        manage_connections.triggered.connect(self.show_connections)
        
        transfer_files = remote_menu.addAction("Transfer Files...")
        transfer_files.triggered.connect(self.show_file_transfer)
        
        remote_menu.addSeparator()
        
        apply_all = remote_menu.addAction("Apply to All Connected PCs")
        apply_all.triggered.connect(self.apply_to_all)
        
        # Help menu
        help_menu = QMenu("Help", self)
        self.menubar.addMenu(help_menu)
        
        help_action = help_menu.addAction("Help Contents")
        help_action.triggered.connect(self.show_help)
        
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)
        
    def show_connections(self):
        """Show the connections management dialog."""
        dialog = ConnectionDialog(self.remote_handler, self)
        dialog.exec()
        
    def show_file_transfer(self):
        """Show the file transfer dialog."""
        from .dialogs.file_transfer_dialog import FileTransferDialog
        dialog = FileTransferDialog(self.remote_handler, self)
        dialog.exec()
        
    def import_configuration(self):
        """Import and apply configuration from a YAML file."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import Configuration",
                "",
                "YAML Files (*.yaml *.yml);;All Files (*.*)"
            )
            
            if not file_path:
                return
                
            with open(file_path, 'r') as f:
                import yaml
                config = yaml.safe_load(f)
                
            # Apply environment variables
            if "Environment Variables" in self.panels and "environment_variables" in config:
                panel = self.panels["Environment Variables"]
                env_vars = config["environment_variables"]
                
                # System variables
                for name, value in env_vars.get("system", {}).items():
                    panel.add_variable(name, value, "System Variables")
                    
                # User variables
                for name, value in env_vars.get("user", {}).items():
                    panel.add_variable(name, value, "User Variables")
                    
            # Apply registry settings
            if "Registry Editor" in self.panels and "registry" in config:
                panel = self.panels["Registry Editor"]
                for entry in config["registry"]:
                    panel.add_registry_key(entry["path"], entry["value"])
                    
            # Apply users and groups
            if "Users & Groups" in self.panels and "users" in config:
                panel = self.panels["Users & Groups"]
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
            if "Services" in self.panels and "services" in config:
                panel = self.panels["Services"]
                for service in config["services"]:
                    panel.configure_service(
                        service["name"],
                        service.get("start_type", "auto"),
                        service.get("state", "running"),
                        service.get("description", "")
                    )
                    
            # Apply firewall rules
            if "Firewall" in self.panels and "firewall" in config:
                panel = self.panels["Firewall"]
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
            if "Software" in self.panels and "software" in config:
                panel = self.panels["Software"]
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
            if "Permissions" in self.panels and "permissions" in config:
                panel = self.panels["Permissions"]
                for perm in config["permissions"]:
                    panel.set_permissions(
                        perm["path"],
                        perm["permissions"]
                    )
                    
            # Apply applications settings
            if "Applications" in self.panels and "applications" in config:
                panel = self.panels["Applications"]
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
                self,
                "Import Complete",
                "Configuration has been imported and applied successfully."
            )
            
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to import configuration: {str(e)}"
            )
        
    def show_help(self):
        """Show the help window."""
        self.help_handler.show_help()
        
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About System Management Tool",
            """<h3>Windows System Management Tool</h3>
            <p>Version 1.0</p>
            <p>A powerful tool for managing Windows systems locally and remotely.</p>
            <p>Part of the Windows System Management Suite.</p>"""
        )
        
    def apply_to_all(self):
        """Apply current panel's changes to all connected PCs."""
        current_panel = self.tab_widget.currentWidget()
        if not current_panel:
            return
            
        panel_name = self.tab_widget.tabText(self.tab_widget.currentIndex())
        
        # Get list of connected PCs
        connected_pcs = [pc for pc in self.remote_handler.get_connections() if pc.is_connected]
        if not connected_pcs:
            QMessageBox.warning(self, "Warning", "No connected PCs available")
            return
            
        # Confirm action
        reply = QMessageBox.question(
            self,
            "Confirm Apply",
            f"Are you sure you want to apply {panel_name} changes to {len(connected_pcs)} connected PCs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Each panel should implement an apply_remote method
                if hasattr(current_panel, 'apply_remote'):
                    results = self.remote_handler.execute_on_all(current_panel.apply_remote)
                    
                    # Show results
                    success = sum(1 for r in results.values() if r)
                    failed = sum(1 for r in results.values() if not r)
                    
                    QMessageBox.information(
                        self,
                        "Apply Complete",
                        f"Changes applied to {success} PCs\nFailed on {failed} PCs"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Warning",
                        f"The {panel_name} panel does not support remote operations"
                    )
                    
            except Exception as e:
                self.logger.error(f"Failed to apply changes to remote PCs: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to apply changes to remote PCs: {str(e)}"
                )

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
                
    def apply_config(self):
        """Apply current configuration to the system."""
        try:
            current_panel = self.tab_widget.currentWidget()
            if not current_panel:
                return
                
            # Each panel should implement an apply_config method
            if hasattr(current_panel, 'apply_config'):
                current_panel.apply_config()
                self.logger.info(f"Configuration applied for {self.tab_widget.tabText(self.tab_widget.currentIndex())}")
            else:
                self.logger.warning(f"Panel {self.tab_widget.tabText(self.tab_widget.currentIndex())} does not support configuration application")
                
        except Exception as e:
            self.logger.error(f"Failed to apply configuration: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to apply configuration: {str(e)}"
            )
