"""Help window implementation."""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget,
                           QTextBrowser)
from PyQt6.QtCore import Qt
from .content import OVERVIEW_CONTENT, FEATURES_CONTENT
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class HelpWindow(QMainWindow):
    """Help window showing application documentation."""
    
    def __init__(self, parent=None):
        """Initialize help window.
        
        Args:
            parent: Parent widget, if any
        """
        super().__init__(parent)
        self.logger = logger
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the help window UI."""
        self.setWindowTitle("Help - Windows System Management Tool")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Overview tab
        overview_browser = QTextBrowser()
        overview_browser.setHtml(OVERVIEW_CONTENT)
        overview_browser.setOpenExternalLinks(True)
        self.tab_widget.addTab(overview_browser, "Overview")
        
        # Features tab
        features_browser = QTextBrowser()
        features_browser.setHtml(FEATURES_CONTENT)
        features_browser.setOpenExternalLinks(True)
        self.tab_widget.addTab(features_browser, "Features")
        
    def showEvent(self, event):
        """Handle window show event.
        
        Args:
            event: Show event
        """
        # Center window on parent if we have one
        if self.parent():
            parent_geo = self.parent().geometry()
            self.move(
                parent_geo.center().x() - self.width() // 2,
                parent_geo.center().y() - self.height() // 2
            )
