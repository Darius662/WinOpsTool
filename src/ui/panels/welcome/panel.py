"""Welcome panel for the WinOpsTool application."""
from PyQt6.QtWidgets import QLabel, QScrollArea, QSizePolicy, QHBoxLayout
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
import os.path
from src.ui.base.base_panel import BasePanel
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class WelcomePanel(BasePanel):
    """Welcome panel showing the application logo and description."""
    
    def __init__(self, parent=None):
        """Initialize the welcome panel."""
        self.logger = logger
        super().__init__(parent)
        
        # Initialize imported config items
        self.imported_config_items = set()
        
    def setup_ui(self):
        """Set up the welcome panel UI."""
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Add scroll area to the main layout
        self.add_widget(scroll_area)
        
        # Content widget for the scroll area
        content_widget = self.create_content_widget()
        scroll_area.setWidget(content_widget)
    
    def setup_connections(self):
        """Set up signal connections."""
        # No connections needed for this panel
        pass
        
    def create_content_widget(self):
        """Create the content widget with logo and description."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
        
        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        # Logo section
        logo_layout = QHBoxLayout()
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add logo if it exists
        logo_path = os.path.join('assets', 'WinOpsTool.png')
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            # Scale pixmap if it's too large
            if pixmap.width() > 400:
                pixmap = pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_layout.addWidget(logo_label)
        
        content_layout.addLayout(logo_layout)
        
        # Title
        title_label = QLabel("Welcome to WinOpsTool")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title_label)
        
        # Description
        description = """
        <p>WinOpsTool is a comprehensive Windows system management application designed to simplify 
        administrative tasks and system operations.</p>
        
        <p>With WinOpsTool, you can:</p>
        <ul>
            <li>Monitor system performance and resource usage</li>
            <li>Manage services, applications, and processes</li>
            <li>Configure system settings and policies</li>
            <li>Perform remote management of multiple systems</li>
            <li>Deploy configurations across your network</li>
            <li>Automate routine maintenance tasks</li>
        </ul>
        
        <p>This tool is designed for system administrators and IT professionals who need 
        powerful yet user-friendly tools to manage Windows environments efficiently.</p>
        
        <p>Select a tab above to get started with specific management tasks.</p>
        """
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setTextFormat(Qt.TextFormat.RichText)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        desc_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        content_layout.addWidget(desc_label)
        
        # Version info
        version_label = QLabel("Version 1.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(version_label)
        
        return content_widget
        
    def apply_config(self, config):
        """Apply configuration to the panel.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if configuration was applied successfully, False otherwise
        """
        self.logger.info("Applying welcome panel configuration")
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Process configuration
            if 'welcome' not in config:
                self.logger.warning("No welcome panel configuration found")
                return False
                
            # The welcome panel is primarily informational and doesn't have
            # configurable settings that need to be applied
            # This method exists to satisfy the BasePanel interface
            self.logger.info("Welcome panel configuration processed (no actions required)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying welcome panel configuration: {str(e)}")
            return False
            
    def export_config(self):
        """Export panel configuration.
        
        Returns:
            dict: Dictionary containing panel configuration
        """
        self.logger.info("Exporting welcome panel configuration")
        
        try:
            # The welcome panel doesn't have any configurable settings to export
            # Return an empty configuration dictionary with the panel key
            config = {
                'welcome': {}
            }
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error exporting welcome panel configuration: {str(e)}")
            return {'welcome': {}}

    def mark_config_items(self, config):
        """Mark items from configuration for highlighting without applying changes.
        
        This method identifies and marks items from the configuration
        that would be modified by apply_config(), but does not actually
        apply any changes to the system. Items will be visually highlighted in the UI.
        
        For the WelcomePanel, this is a placeholder implementation since there are no
        configurable items that need to be highlighted.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if items were marked successfully, False otherwise
        """
        self.logger.info("Marking welcome panel configuration items (no action required)")
        
        # Clear previous imported items
        self.imported_config_items.clear()
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Check if welcome section exists
            if 'welcome' not in config:
                self.logger.warning("No welcome panel configuration found")
                return False
                
            # The welcome panel is primarily informational and doesn't have
            # configurable settings that need to be highlighted
            self.logger.info("Welcome panel configuration processed (no highlighting required)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error marking welcome panel configuration items: {str(e)}")
            return False
    
    def mark_as_imported_config(self, item):
        """Mark an item as imported from config for highlighting.
        
        Args:
            item: Item to mark
        """
        self.imported_config_items.add(item)
        
    def is_imported_config_item(self, item):
        """Check if an item is marked as imported from config.
        
        Args:
            item: Item to check
            
        Returns:
            bool: True if item is marked as imported, False otherwise
        """
        return item in self.imported_config_items
