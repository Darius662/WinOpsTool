"""Help window for Configuration Manager."""
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QTextEdit

class HelpWindow(QMainWindow):
    """Help window for Configuration Manager."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuration Manager Help")
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
        <h2>Configuration Manager</h2>
        <p>The Configuration Manager is a tool for creating and managing system configuration files 
        that can be imported into the main System Management Tool.</p>
        
        <h3>Key Features</h3>
        <ul>
            <li>Create and edit configuration files in YAML format</li>
            <li>Configure multiple system aspects in one place</li>
            <li>Save and load configurations</li>
            <li>Import configurations into main System Management Tool</li>
        </ul>
        
        <h3>Basic Usage</h3>
        <ol>
            <li>Use the tabs to configure different aspects of the system</li>
            <li>Save your configuration using File -> Save Config</li>
            <li>Import the saved configuration file in the main System Management Tool</li>
        </ol>
        """)
        overview_layout.addWidget(overview_text)
        tabs.addTab(overview, "Overview")
        
        # Tabs help
        tabs_help = QWidget()
        tabs_layout = QVBoxLayout(tabs_help)
        tabs_text = QTextEdit()
        tabs_text.setReadOnly(True)
        tabs_text.setHtml("""
        <h2>Configuration Tabs</h2>
        
        <h3>Environment Variables</h3>
        <p>Configure system and user environment variables:</p>
        <ul>
            <li>Add/remove system-wide variables</li>
            <li>Add/remove user-specific variables</li>
        </ul>
        
        <h3>Registry Editor</h3>
        <p>Manage Windows Registry settings:</p>
        <ul>
            <li>Add registry values with different types</li>
            <li>Specify registry paths and values</li>
            <li>Support for REG_SZ, REG_DWORD, etc.</li>
        </ul>
        
        <h3>Users & Groups</h3>
        <p>Configure user accounts and group memberships:</p>
        <ul>
            <li>Create user accounts with passwords</li>
            <li>Define group memberships</li>
            <li>Add users to groups</li>
        </ul>
        
        <h3>Services</h3>
        <p>Manage Windows services configuration:</p>
        <ul>
            <li>Set service startup types</li>
            <li>Configure service states</li>
            <li>Add service descriptions</li>
        </ul>
        
        <h3>Firewall</h3>
        <p>Configure Windows Firewall rules:</p>
        <ul>
            <li>Create inbound/outbound rules</li>
            <li>Set protocols and ports</li>
            <li>Configure allow/block actions</li>
        </ul>
        
        <h3>Software</h3>
        <p>Manage software installation/uninstallation:</p>
        <ul>
            <li>Configure MSI/EXE installations</li>
            <li>Set installation arguments</li>
            <li>Specify software to remove</li>
        </ul>
        
        <h3>Permissions</h3>
        <p>Configure file and folder permissions:</p>
        <ul>
            <li>Set ownership and access rights</li>
            <li>Configure inheritance</li>
            <li>Add/remove permissions</li>
        </ul>
        
        <h3>Applications</h3>
        <p>Configure application settings:</p>
        <ul>
            <li>Configure startup applications</li>
            <li>Set up processes to run</li>
            <li>Configure run-as settings</li>
        </ul>
        """)
        tabs_layout.addWidget(tabs_text)
        tabs.addTab(tabs_help, "Tabs Guide")
