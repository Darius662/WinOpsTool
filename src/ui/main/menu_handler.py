"""Menu handler for the main window."""
from PyQt6.QtWidgets import QMenuBar, QMenu, QMessageBox
from PyQt6.QtGui import QAction
from src.core.logger import setup_logger

class MenuHandler:
    """Handles menu creation and actions for the main window."""
    
    def __init__(self, main_window):
        """Initialize menu handler.
        
        Args:
            main_window: MainWindow instance
        """
        self.main_window = main_window
        self.logger = setup_logger(self.__class__.__name__)
        self.menubar = main_window.menuBar()
        self.setup_menus()
        
    def setup_menus(self):
        """Set up all menus."""
        self.setup_file_menu()
        self.setup_remote_menu()
        self.setup_help_menu()
        
    def setup_file_menu(self):
        """Set up File menu."""
        file_menu = self.menubar.addMenu("File")
        
        # Import config
        import_action = QAction("Import Config...", self.main_window)
        import_action.triggered.connect(self.main_window.import_configuration)
        file_menu.addAction(import_action)
        
        # Apply config
        apply_action = QAction("Apply Config", self.main_window)
        apply_action.triggered.connect(self.main_window.apply_config)
        file_menu.addAction(apply_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("Exit", self.main_window)
        exit_action.triggered.connect(self.main_window.close)
        file_menu.addAction(exit_action)
        
    def setup_remote_menu(self):
        """Set up Remote menu."""
        remote_menu = self.menubar.addMenu("Remote")
        
        # Connect
        connect_action = QAction("Connect...", self.main_window)
        connect_action.triggered.connect(self.main_window.remote_handler.connect)
        remote_menu.addAction(connect_action)
        
        # Disconnect
        disconnect_action = QAction("Disconnect", self.main_window)
        disconnect_action.triggered.connect(self.main_window.remote_handler.disconnect)
        remote_menu.addAction(disconnect_action)
        
        remote_menu.addSeparator()
        
        # File transfer
        transfer_action = QAction("File Transfer...", self.main_window)
        transfer_action.triggered.connect(self.main_window.remote_handler.show_file_transfer)
        remote_menu.addAction(transfer_action)
        
    def setup_help_menu(self):
        """Set up Help menu."""
        help_menu = self.menubar.addMenu("Help")
        
        # Help contents
        help_action = QAction("Help Contents", self.main_window)
        help_action.triggered.connect(self.main_window.help_handler.show_help)
        help_menu.addAction(help_action)
        
        # About
        about_action = QAction("About", self.main_window)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self.main_window,
            "About System Management Tool",
            """<h3>Windows System Management Tool</h3>
            <p>Version 1.0</p>
            <p>A tool for managing Windows system settings and configurations.</p>
            <p>Features:</p>
            <ul>
                <li>Environment variables management</li>
                <li>Registry editor</li>
                <li>User and group management</li>
                <li>Services configuration</li>
                <li>Firewall rules</li>
                <li>Software installation</li>
                <li>File permissions</li>
                <li>Application management</li>
                <li>Remote system management</li>
            </ul>"""
        )
