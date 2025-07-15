"""Help window handler for the main window."""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget,
                          QTextEdit)
from src.core.logger import setup_logger

class HelpHandler:
    """Handles help window functionality."""
    
    def __init__(self, main_window):
        """Initialize help handler.
        
        Args:
            main_window: MainWindow instance
        """
        self.main_window = main_window
        self.logger = setup_logger(self.__class__.__name__)
        self.help_window = None
        
    def show_help(self):
        """Show help window."""
        if not self.help_window:
            self.help_window = HelpWindow(self.main_window)
        self.help_window.show()
        
class HelpWindow(QMainWindow):
    """Help window for the System Management Tool."""
    
    def __init__(self, parent=None):
        """Initialize help window."""
        super().__init__(parent)
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
        <p>The Windows System Management Tool is a comprehensive utility for managing
        Windows system settings and configurations both locally and remotely.</p>
        
        <h3>Key Features</h3>
        <ul>
            <li>Environment Variables Management</li>
            <li>Registry Editor</li>
            <li>User and Group Management</li>
            <li>Services Configuration</li>
            <li>Firewall Rules Management</li>
            <li>Software Installation</li>
            <li>File Permissions</li>
            <li>Application Management</li>
            <li>Remote System Management</li>
        </ul>
        
        <h3>Basic Usage</h3>
        <ol>
            <li>Use the tabs to access different system management features</li>
            <li>For remote management, connect to a remote system first</li>
            <li>Import configuration files to apply pre-defined settings</li>
            <li>Use the Configuration Manager to create new config files</li>
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
        <h2>Feature Guide</h2>
        
        <h3>Environment Variables</h3>
        <p>Manage system and user environment variables:</p>
        <ul>
            <li>View current variables</li>
            <li>Add/modify/delete variables</li>
            <li>Import/export configurations</li>
        </ul>
        
        <h3>Registry Editor</h3>
        <p>Manage Windows Registry settings:</p>
        <ul>
            <li>Browse registry structure</li>
            <li>Add/modify/delete keys and values</li>
            <li>Import/export registry settings</li>
        </ul>
        
        <h3>Users & Groups</h3>
        <p>Manage user accounts and group memberships:</p>
        <ul>
            <li>Create/modify user accounts</li>
            <li>Manage group memberships</li>
            <li>Set account properties</li>
        </ul>
        
        <h3>Services</h3>
        <p>Configure Windows services:</p>
        <ul>
            <li>View service status</li>
            <li>Start/stop services</li>
            <li>Change startup type</li>
        </ul>
        
        <h3>Firewall</h3>
        <p>Manage Windows Firewall rules:</p>
        <ul>
            <li>View existing rules</li>
            <li>Create new rules</li>
            <li>Modify rule properties</li>
        </ul>
        
        <h3>Software</h3>
        <p>Manage software installation:</p>
        <ul>
            <li>Install MSI/EXE packages</li>
            <li>Uninstall programs</li>
            <li>View installed software</li>
        </ul>
        
        <h3>Permissions</h3>
        <p>Manage file and folder permissions:</p>
        <ul>
            <li>View current permissions</li>
            <li>Modify access rights</li>
            <li>Set ownership</li>
        </ul>
        
        <h3>Applications</h3>
        <p>Manage running applications:</p>
        <ul>
            <li>View running processes</li>
            <li>Start/stop applications</li>
            <li>Configure startup items</li>
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
        <h2>Remote Management</h2>
        
        <h3>Connecting to Remote Systems</h3>
        <ol>
            <li>Click Connect in the Remote menu</li>
            <li>Enter hostname/IP and credentials</li>
            <li>Wait for connection to establish</li>
        </ol>
        
        <h3>File Transfer</h3>
        <p>Transfer files between local and remote systems:</p>
        <ul>
            <li>Use the File Transfer dialog</li>
            <li>Select source and destination</li>
            <li>Monitor transfer progress</li>
        </ul>
        
        <h3>Remote Operations</h3>
        <p>All system management features work remotely:</p>
        <ul>
            <li>View remote system settings</li>
            <li>Apply changes to remote system</li>
            <li>Import/export configurations</li>
        </ul>
        
        <h3>Security</h3>
        <p>Important security considerations:</p>
        <ul>
            <li>Use secure credentials</li>
            <li>Monitor remote changes</li>
            <li>Review audit logs</li>
            <li>Follow security policies</li>
        </ul>
        """)
        remote_layout.addWidget(remote_text)
        tabs.addTab(remote, "Remote Management")
