"""Main application window."""
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QMenuBar, QMenu, QFileDialog, QMessageBox, QApplication,
                             QTextEdit)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger
from src.core.remote_manager import RemoteManager
from src.core.config import APP_NAME
from .dialogs.connection_dialog import ConnectionDialog

logger = setup_logger(__name__)

class HelpWindow(QMainWindow):
    """Help window for System Management Tool."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Management Tool Help")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Overview tab
        overview = QWidget()
        overview_layout = QVBoxLayout(overview)
        overview_text = QTextEdit()
        overview_text.setReadOnly(True)
        overview_text.setHtml("""
        <h2>Windows System Management Tool</h2>
        <p>A powerful tool for managing Windows systems locally and remotely. This application allows you 
        to configure and manage multiple aspects of Windows systems through a modern graphical interface.</p>
        
        <h3>Key Features</h3>
        <ul>
            <li>Local system configuration</li>
            <li>Remote PC management</li>
            <li>Configuration import/export</li>
            <li>File transfer capabilities</li>
            <li>Multi-PC operations</li>
        </ul>
        
        <h3>Basic Usage</h3>
        <ol>
            <li>Use the tabs to access different management features</li>
            <li>Configure settings as needed</li>
            <li>Apply changes locally or to remote PCs</li>
            <li>Import/export configurations for reuse</li>
        </ol>
        
        <h3>Remote Management</h3>
        <p>To manage remote PCs:</p>
        <ol>
            <li>Use Remote -> Manage Connections to add PCs</li>
            <li>Configure settings in any tab</li>
            <li>Use Remote -> Apply to All Connected PCs</li>
        </ol>
        """)
        overview_layout.addWidget(overview_text)
        tabs.addTab(overview, "Overview")
        
        # Features tab
        features = QWidget()
        features_layout = QVBoxLayout(features)
        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setHtml("""
        <h2>Features Guide</h2>
        
        <h3>Environment Variables</h3>
        <p>Manage system and user environment variables:</p>
        <ul>
            <li>View current variables</li>
            <li>Add/modify/delete variables</li>
            <li>Apply to remote PCs</li>
        </ul>
        
        <h3>Registry Editor</h3>
        <p>Windows Registry management:</p>
        <ul>
            <li>Browse registry structure</li>
            <li>Add/modify/delete values</li>
            <li>Import/export registry settings</li>
        </ul>
        
        <h3>Users & Groups</h3>
        <p>User account and group management:</p>
        <ul>
            <li>Create/modify user accounts</li>
            <li>Manage group memberships</li>
            <li>Set account properties</li>
        </ul>
        
        <h3>Services</h3>
        <p>Windows services control:</p>
        <ul>
            <li>View service status</li>
            <li>Start/stop services</li>
            <li>Change startup type</li>
        </ul>
        
        <h3>Firewall</h3>
        <p>Windows Firewall configuration:</p>
        <ul>
            <li>View existing rules</li>
            <li>Create new rules</li>
            <li>Modify rule properties</li>
        </ul>
        
        <h3>Software</h3>
        <p>Software management:</p>
        <ul>
            <li>Install applications</li>
            <li>Uninstall software</li>
            <li>Silent installation support</li>
        </ul>
        
        <h3>Permissions</h3>
        <p>File system permissions:</p>
        <ul>
            <li>View current permissions</li>
            <li>Modify access rights</li>
            <li>Set ownership</li>
        </ul>
        
        <h3>Applications</h3>
        <p>Application management:</p>
        <ul>
            <li>Configure startup items</li>
            <li>Manage running processes</li>
            <li>Set application properties</li>
        </ul>
        """)
        features_layout.addWidget(features_text)
        tabs.addTab(features, "Features")
        
        # Remote Management tab
        remote = QWidget()
        remote_layout = QVBoxLayout(remote)
        remote_text = QTextEdit()
        remote_text.setReadOnly(True)
        remote_text.setHtml("""
        <h2>Remote Management Guide</h2>
        
        <h3>Managing Connections</h3>
        <p>To manage remote PCs:</p>
        <ol>
            <li>Open Remote -> Manage Connections</li>
            <li>Add remote PC details (hostname/IP)</li>
            <li>Test connection</li>
            <li>Save connection details</li>
        </ol>
        
        <h3>File Transfer</h3>
        <p>To transfer files to remote PCs:</p>
        <ol>
            <li>Open Remote -> Transfer Files</li>
            <li>Select source files</li>
            <li>Choose destination</li>
            <li>Start transfer</li>
        </ol>
        
        <h3>Applying Changes</h3>
        <p>To apply changes to remote PCs:</p>
        <ol>
            <li>Configure settings in any tab</li>
            <li>Use Remote -> Apply to All Connected PCs</li>
            <li>Confirm the action</li>
            <li>Review results</li>
        </ol>
        
        <h3>Best Practices</h3>
        <ul>
            <li>Always test connections before applying changes</li>
            <li>Use configuration files for consistent deployment</li>
            <li>Review logs for troubleshooting</li>
            <li>Back up settings before major changes</li>
        </ul>
        """)
        remote_layout.addWidget(remote_text)
        tabs.addTab(remote, "Remote Management")


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        # Initialize QApplication if not already done
        if not QApplication.instance():
            app = QApplication(sys.argv)
            
        super().__init__()
        self.logger = setup_logger(self.__class__.__name__)
        self.remote_manager = RemoteManager()
        self.setWindowTitle("Windows System Management Tool")
        
        # Store panel references
        self.panels = {}
        
        # Create menu bar
        self.menubar = QMenuBar()
        self.setMenuBar(self.menubar)
        
        # Set up UI
        self.setup_ui()
        
        # Set up menu
        self.setup_menu()
        
    def setup_ui(self):
        """Set up the main window UI components."""
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Import panels
        from .panels.environment_panel import EnvironmentPanel
        from .panels.registry_panel import RegistryPanel
        from .panels.users_panel import UsersPanel
        from .panels.services_panel import ServicesPanel
        from .panels.firewall_panel import FirewallPanel
        from .panels.software_panel import SoftwarePanel
        from .panels.permissions_panel import PermissionsPanel
        from .panels.applications_panel import ApplicationsPanel
        
        panels = [
            ("Environment Variables", EnvironmentPanel(self)),
            ("Registry Editor", RegistryPanel(self)),
            ("Users & Groups", UsersPanel(self)),
            ("Services", ServicesPanel(self)),
            ("Firewall", FirewallPanel(self)),
            ("Software", SoftwarePanel(self)),
            ("Permissions", PermissionsPanel(self)),
            ("Applications", ApplicationsPanel(self))
        ]
        
        for title, panel in panels:
            try:
                if isinstance(panel, QWidget):
                    self.tab_widget.addTab(panel, title)
                    self.panels[title] = panel
                    self.logger.info(f"Loaded panel: {title}")
            except Exception as e:
                self.logger.error(f"Failed to load panel {title}: {str(e)}")
                
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
        dialog = ConnectionDialog(self.remote_manager, self)
        dialog.exec()
        
    def show_file_transfer(self):
        """Show the file transfer dialog."""
        from .dialogs.file_transfer_dialog import FileTransferDialog
        dialog = FileTransferDialog(self.remote_manager, self)
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
                for key in config["registry"].get("keys", []):
                    panel.add_registry_key(key["path"], key["values"])
                    
            # Apply users and groups
            if "Users & Groups" in self.panels and "users_and_groups" in config:
                panel = self.panels["Users & Groups"]
                users_groups = config["users_and_groups"]
                
                # Create groups first
                for group in users_groups.get("groups", []):
                    panel.add_group(group["name"], group["comment"])
                    
                # Then create users and add to groups
                for user in users_groups.get("users", []):
                    panel.add_user(
                        user["name"],
                        user["password"],
                        user["groups"],
                        user.get("comment", "")
                    )
                    
            # Apply services configuration
            if "Services" in self.panels and "services" in config:
                panel = self.panels["Services"]
                for service in config["services"]:
                    panel.configure_service(
                        service["name"],
                        service["start_type"],
                        service["state"]
                    )
                    
            # Apply firewall rules
            if "Firewall" in self.panels and "firewall" in config:
                panel = self.panels["Firewall"]
                for rule in config["firewall"].get("rules", []):
                    panel.add_rule(
                        rule["name"],
                        rule["direction"],
                        rule["action"],
                        rule["protocol"],
                        rule["local_ports"],
                        rule["remote_ports"],
                        rule["enabled"]
                    )
                    
            # Apply software changes
            if "Software" in self.panels and "software" in config:
                panel = self.panels["Software"]
                
                # Install software
                for software in config["software"].get("install", []):
                    panel.install_software(
                        path=software["path"],
                        arguments=software.get("arguments", "")
                    )
                    
                # Uninstall software
                for name in config["software"].get("uninstall", []):
                    panel.uninstall_software(name)
                    
            # Apply permissions
            if "Permissions" in self.panels and "permissions" in config:
                panel = self.panels["Permissions"]
                for item in config["permissions"]:
                    panel.set_permissions(
                        item["path"],
                        item["permissions"]
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
                        item["enabled"]
                    )
                    
                # Handle processes
                for proc in apps.get("processes", {}).get("stop", []):
                    panel.stop_process(proc)
                    
                for proc in apps.get("processes", {}).get("start", []):
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
        self.help_window = HelpWindow()
        self.help_window.show()
        
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
        connected_pcs = [pc for pc in self.remote_manager.get_connections() if pc.is_connected]
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
                    results = self.remote_manager.execute_on_all(current_panel.apply_remote)
                    
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
