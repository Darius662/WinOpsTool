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
