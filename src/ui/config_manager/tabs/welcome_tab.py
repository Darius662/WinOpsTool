"""Welcome tab for the WinOpsInit application."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QSizePolicy, QHBoxLayout
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
import os.path
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class WelcomeTab(QWidget):
    """Welcome tab showing the application logo and description."""
    
    def __init__(self, config_handler=None, parent=None):
        """Initialize the welcome tab."""
        super().__init__(parent)
        self.config_handler = config_handler
        self.logger = logger
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the welcome tab UI."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        main_layout.addWidget(scroll_area)
        
        # Content widget for the scroll area
        content_widget = self.create_content_widget()
        scroll_area.setWidget(content_widget)
        
    def create_content_widget(self):
        """Create the content widget with logo and description."""
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
        logo_path = os.path.join('assets', 'WinOpsInit.png')
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
        title_label = QLabel("Welcome to WinOpsInit")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title_label)
        
        # Description
        description = """
        <p>WinOpsInit is a configuration management tool for Windows systems, designed to simplify 
        the setup and maintenance of system configurations.</p>
        
        <p>With WinOpsInit, you can:</p>
        <ul>
            <li>Configure environment variables for your system</li>
            <li>Manage registry settings and keys</li>
            <li>Configure user accounts and permissions</li>
            <li>Manage Windows services</li>
            <li>Configure firewall rules</li>
            <li>Manage software installations</li>
            <li>Set up application permissions</li>
        </ul>
        
        <p>This tool is designed to help system administrators and IT professionals quickly 
        configure Windows systems according to organizational requirements and best practices.</p>
        
        <p>Select a tab above to begin configuring specific aspects of your system.</p>
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
