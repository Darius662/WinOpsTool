"""Button bar component for software panel."""
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

from .install_button import InstallButton
from .uninstall_button import UninstallButton
from .repair_button import RepairButton
from .refresh_button import RefreshButton


class ButtonBar(QWidget):
    """Button bar for software panel."""
    
    # Signals emitted when buttons are clicked
    install_software = pyqtSignal(str)
    uninstall_software = pyqtSignal(str)
    repair_software = pyqtSignal(str)
    refresh_software = pyqtSignal(str)
    
    def __init__(self, filter_type="All", parent=None):
        """Initialize button bar.
        
        Args:
            filter_type: Current filter type
            parent: Parent widget
        """
        super().__init__(parent)
        self.filter_type = filter_type
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Set up the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create buttons
        self.install_button = InstallButton(self.filter_type, self)
        self.uninstall_button = UninstallButton(self.filter_type, self)
        self.repair_button = RepairButton(self.filter_type, self)
        self.refresh_button = RefreshButton(self.filter_type, self)
        
        # Add buttons to layout
        layout.addWidget(self.install_button)
        layout.addWidget(self.uninstall_button)
        layout.addWidget(self.repair_button)
        layout.addWidget(self.refresh_button)
        
        # Add stretch to push buttons to the left
        layout.addStretch()
        
    def setup_connections(self):
        """Set up signal connections."""
        self.install_button.clicked_with_filter.connect(self.install_software)
        self.uninstall_button.clicked_with_filter.connect(self.uninstall_software)
        self.repair_button.clicked_with_filter.connect(self.repair_software)
        self.refresh_button.clicked_with_filter.connect(self.refresh_software)
        
    def update_filter(self, filter_type):
        """Update the filter type for all buttons.
        
        Args:
            filter_type: New filter type
        """
        self.filter_type = filter_type
        self.install_button.update_filter(filter_type)
        self.uninstall_button.update_filter(filter_type)
        self.repair_button.update_filter(filter_type)
        self.refresh_button.update_filter(filter_type)
        
    def update_button_states(self, has_selection):
        """Update button enabled states based on selection.
        
        Args:
            has_selection: Whether an item is selected
        """
        self.uninstall_button.setEnabled(has_selection)
        self.repair_button.setEnabled(has_selection)
