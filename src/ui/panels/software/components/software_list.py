"""Software list component for software panel."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox
from PyQt6.QtCore import pyqtSignal

from src.core.logger import setup_logger
from ..tree_widget import SoftwareTree
from .button_bar import ButtonBar


class SoftwareList(QWidget):
    """Widget for displaying and managing software list."""
    
    # Signals emitted when actions are performed
    install_software = pyqtSignal(str)
    uninstall_software = pyqtSignal(str)
    repair_software = pyqtSignal(str)
    refresh_software = pyqtSignal(str)
    filter_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize software list.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.filter_type = "All"
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All Software",
            "System Software",
            "User Software"
        ])
        filter_layout.addWidget(self.filter_combo)
        
        # Add filter layout to main layout
        layout.addLayout(filter_layout)
        
        # Create button bar
        self.button_bar = ButtonBar(self.filter_type, self)
        layout.addWidget(self.button_bar)
        
        # Create software tree
        self.software_tree = SoftwareTree()
        layout.addWidget(self.software_tree)
        
    def setup_connections(self):
        """Set up signal connections."""
        # Connect filter combo
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        
        # Connect button bar signals
        self.button_bar.install_software.connect(self.install_software)
        self.button_bar.uninstall_software.connect(self.uninstall_software)
        self.button_bar.repair_software.connect(self.repair_software)
        self.button_bar.refresh_software.connect(self.refresh_software)
        
        # Connect tree selection change
        self.software_tree.itemSelectionChanged.connect(self._on_selection_changed)
        
    def _on_filter_changed(self, text):
        """Handle filter combo change.
        
        Args:
            text: New filter text
        """
        # Map combo text to filter type
        filter_map = {
            "All Software": "All",
            "System Software": "System",
            "User Software": "User"
        }
        self.filter_type = filter_map[text]
        
        # Update button bar filter
        self.button_bar.update_filter(self.filter_type)
        
        # Emit signal
        self.filter_changed.emit(self.filter_type)
        
    def _on_selection_changed(self):
        """Handle tree selection change."""
        has_selection = bool(self.software_tree.selectedItems())
        self.button_bar.update_button_states(has_selection)
        
    def add_software(self, software_list):
        """Add software to the tree.
        
        Args:
            software_list: List of software dictionaries
        """
        self.software_tree.clear_software()
        
        for software in software_list:
            self.software_tree.add_software(
                software['name'],
                software['version'],
                software['publisher'],
                software['install_date'],
                software['size'],
                software['location']
            )
            
    def get_selected_software(self):
        """Get the currently selected software.
        
        Returns:
            dict: Selected software properties or None if nothing selected
        """
        current_item = self.software_tree.currentItem()
        if current_item:
            return self.software_tree.get_software(current_item)
        return None
