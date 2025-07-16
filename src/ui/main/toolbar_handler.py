"""Toolbar handler for the main window."""
from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QAction, QIcon
from src.core.logger import setup_logger

class ToolbarHandler:
    """Handles toolbar creation and actions for the main window."""
    
    def __init__(self, main_window):
        """Initialize toolbar handler.
        
        Args:
            main_window: MainWindow instance
        """
        self.main_window = main_window
        self.logger = setup_logger(self.__class__.__name__)
        self.toolbar = QToolBar()
        self.main_window.addToolBar(self.toolbar)
        self.setup_toolbar()
        
    def setup_toolbar(self):
        """Set up toolbar actions."""
        # Import config
        import_action = QAction(QIcon("assets/import.png"), "Import Config", self.main_window)
        import_action.setStatusTip("Import configuration file")
        import_action.triggered.connect(self.main_window.import_configuration)
        self.toolbar.addAction(import_action)
        
        # Apply config
        apply_action = QAction(QIcon("assets/apply.png"), "Apply Config", self.main_window)
        apply_action.setStatusTip("Apply current configuration")
        apply_action.triggered.connect(self.main_window.apply_config)
        self.toolbar.addAction(apply_action)
        
        self.toolbar.addSeparator()
        
        # Connect
        connect_action = QAction(QIcon("assets/connect.png"), "Connect", self.main_window)
        connect_action.setStatusTip("Connect to remote system")
        connect_action.triggered.connect(self.main_window.remote_handler.connect)
        self.toolbar.addAction(connect_action)
        
        # Disconnect
        disconnect_action = QAction(QIcon("assets/disconnect.png"), "Disconnect", self.main_window)
        disconnect_action.setStatusTip("Disconnect from remote system")
        disconnect_action.triggered.connect(self.main_window.remote_handler.disconnect)
        self.toolbar.addAction(disconnect_action)
        
        # File transfer
        transfer_action = QAction(QIcon("assets/transfer.png"), "File Transfer", self.main_window)
        transfer_action.setStatusTip("Transfer files to/from remote system")
        transfer_action.triggered.connect(self.main_window.remote_handler.show_file_transfer)
        self.toolbar.addAction(transfer_action)
        
        self.toolbar.addSeparator()
        
        # Help
        help_action = QAction(QIcon("assets/help.png"), "Help", self.main_window)
        help_action.setStatusTip("Show help contents")
        help_action.triggered.connect(self.main_window.help_handler.show_help)
        self.toolbar.addAction(help_action)
