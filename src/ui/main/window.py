"""Main application window."""
import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import os.path
from src.core.logger import setup_logger
from src.core.privileges import is_admin
from .panel_manager import PanelManager
from .menu_handler import MenuHandler
from .remote_handler import RemoteHandler
from .config_handler import ConfigHandler
from .help_handler import HelpHandler
from .dialog_handler import DialogHandler

logger = setup_logger(__name__)

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, config=None):
        """Initialize main window.
        
        Args:
            config: Optional configuration dictionary loaded from YAML file
        """
        # Check for admin privileges
        if not is_admin():
            raise PermissionError("This tool requires administrator privileges.")
            
        # Initialize QApplication if not already done
        if not QApplication.instance():
            app = QApplication(sys.argv)
            
        super().__init__()
        
        self.logger = logger
        
        # Store configuration
        self.config = config or {}
        self.logger.info(f"MainWindow initialized with configuration: {len(self.config)} sections")
        
        # Create handlers in dependency order
        self.remote_handler = RemoteHandler(self)
        self.config_handler = ConfigHandler(self)
        self.help_handler = HelpHandler(self)
        self.dialog_handler = DialogHandler(self)
        self.panel_manager = PanelManager(self)
        # MenuHandler must be created last as it depends on other handlers
        self.menu_handler = MenuHandler(self)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the main window UI."""
        self.setWindowTitle("WinOpsTool")
        
        # Set proper window size and make it resizable
        self.setMinimumSize(1024, 768)
        self.resize(1200, 900)  # Set default size larger than minimum
        
        # Enable window resizing and improve performance
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowMinimizeButtonHint)
        
        # Set window icon
        icon_path = os.path.join('assets', 'WinOpsTool.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Create central widget and layout with proper margins
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins for better space usage
        layout.setSpacing(2)  # Reduce spacing for better performance
        
        # Add panel manager's tab widget
        layout.addWidget(self.panel_manager.tab_widget)
        
        # Set up menu
        self.menubar = self.menu_handler.create_menu_bar()
        self.setMenuBar(self.menubar)
        
    def show_connections(self):
        """Show the connections management dialog."""
        self.dialog_handler.show_connections()
        
    def show_file_transfer(self):
        """Show the file transfer dialog."""
        self.dialog_handler.show_file_transfer()
        
    def show_help(self):
        """Show the help window."""
        self.help_handler.show_help()
        
    def show_about(self):
        """Show about dialog."""
        self.dialog_handler.show_about()
        
    def apply_to_all(self):
        """Apply current panel's changes to all connected PCs."""
        current_panel = self.panel_manager.get_current_panel()
        if not current_panel:
            return
            
        panel_name = self.panel_manager.get_current_panel_name()
        
        # Get list of connected PCs
        connected_pcs = [pc for pc in self.remote_handler.get_connections() if pc.is_connected]
        if not connected_pcs:
            self.dialog_handler.show_error("Warning", "No connected PCs available")
            return
            
        # Confirm action
        if not self.dialog_handler.confirm_apply_all(panel_name, len(connected_pcs)):
            return
            
        try:
            # Each panel should implement an apply_remote method
            if hasattr(current_panel, 'apply_remote'):
                results = self.remote_handler.execute_on_all(current_panel.apply_remote)
                
                # Show results
                success = sum(1 for r in results.values() if r)
                failed = sum(1 for r in results.values() if not r)
                
                self.dialog_handler.show_apply_results(success, failed)
            else:
                self.dialog_handler.show_error(
                    "Warning",
                    f"The {panel_name} panel does not support remote operations"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to apply changes to remote PCs: {str(e)}")
            self.dialog_handler.show_error(
                "Error",
                f"Failed to apply changes to remote PCs: {str(e)}"
            )
            
    def update_remote_state(self, connected):
        """Update UI elements based on remote connection state.
        
        Args:
            connected: True if connected to remote system, False otherwise
        """
        self.panel_manager.update_remote_state(connected)
    
    def set_config(self, config):
        """Set the current configuration.
        
        Args:
            config: Dictionary containing configuration data
        """
        self.config = config or {}
        self.logger.info(f"Configuration set with {len(self.config)} sections")
        
        # Update panels to show imported items but don't apply changes
        self.panel_manager.update_panels_with_config(self.config)
        
    def apply_config(self):
        """Apply current configuration to the system."""
        try:
            if not self.config:
                self.logger.warning("No configuration loaded to apply")
                self.dialog_handler.show_error(
                    "Warning",
                    "No configuration loaded. Please import a configuration file first."
                )
                return
                
            # Confirm action
            if not self.dialog_handler.confirm_action(
                "Apply Configuration",
                "Are you sure you want to apply the loaded configuration to the system?"
            ):
                return
                
            # Apply configuration to all panels
            success = self.panel_manager.apply_config_to_panels(self.config)
            
            if success:
                self.logger.info("Configuration applied successfully")
                self.dialog_handler.show_info(
                    "Success",
                    "Configuration applied successfully"
                )
            else:
                self.logger.warning("Some panels failed to apply configuration")
                self.dialog_handler.show_warning(
                    "Warning",
                    "Some panels failed to apply configuration. Check logs for details."
                )
                
        except Exception as e:
            self.logger.error(f"Failed to apply configuration: {str(e)}")
            self.dialog_handler.show_error(
                "Error",
                f"Failed to apply configuration: {str(e)}"
            )
