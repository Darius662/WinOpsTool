"""Startup list component."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QInputDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal
import os

from src.ui.panels.applications.tree_widget import StartupTree
from src.ui.panels.applications.manager import StartupManager
from .button_bar import ButtonBar


class StartupList(QWidget):
    """Component combining startup tree and action buttons."""
    
    # Signals for startup operations
    startup_item_selected = pyqtSignal(dict)
    startup_item_added = pyqtSignal(dict)
    startup_item_removed = pyqtSignal(str)  # Name of removed item
    startup_items_refreshed = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize the startup list component.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.manager = StartupManager()
        self._setup_ui()
        self._connect_signals()
        
        # Initial load
        self.refresh_startup()
        
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Startup tree
        self.startup_tree = StartupTree()
        layout.addWidget(self.startup_tree)
        
        # Button bar
        self.button_bar = ButtonBar()
        layout.addWidget(self.button_bar)
        
    def _connect_signals(self):
        """Connect signals between components."""
        # Tree signals
        self.startup_tree.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Button bar signals
        self.button_bar.add_clicked.connect(self.add_startup)
        self.button_bar.remove_clicked.connect(self.remove_startup)
        self.button_bar.refresh_clicked.connect(self.refresh_startup)
        
    def _on_selection_changed(self):
        """Handle selection change in the startup tree."""
        has_selection = bool(self.startup_tree.selectedItems())
        self.button_bar.update_button_states(has_selection)
        
        if has_selection:
            item = self.get_selected_startup_item()
            if item:
                self.startup_item_selected.emit(item)
                
    def get_selected_startup_item(self):
        """Get the currently selected startup item.
        
        Returns:
            dict: Selected startup item data or None if no selection
        """
        current_item = self.startup_tree.currentItem()
        if current_item:
            return self.startup_tree.get_startup_item(current_item)
        return None
        
    def refresh_startup(self):
        """Refresh the startup items list."""
        try:
            self.startup_tree.clear_startup_items()
            startup_items = self.manager.get_startup_items()
            
            for item in startup_items:
                self.startup_tree.add_startup_item(
                    item['name'],
                    item['command'],
                    item['location'],
                    item['type'],
                    item['status']
                )
                
            self.startup_items_refreshed.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to refresh startup items: {str(e)}")
            
    def add_startup(self):
        """Add a new startup item."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Program",
                "",
                "Programs (*.exe);;All Files (*.*)"
            )
            
            if file_path:
                name = QInputDialog.getText(
                    self,
                    "Add Startup Item",
                    "Enter name for startup item:",
                    text=os.path.splitext(os.path.basename(file_path))[0]
                )[0]
                
                if name:
                    location = QInputDialog.getItem(
                        self,
                        "Add Startup Item",
                        "Select startup location:",
                        ["Current User", "All Users"],
                        0,
                        False
                    )[0]
                    
                    if self.manager.add_startup_item(name, file_path, location):
                        new_item = {
                            'name': name,
                            'command': file_path,
                            'location': location,
                            'type': 'Registry',  # Default type
                            'status': 'Enabled'  # Default status
                        }
                        self.startup_item_added.emit(new_item)
                        self.refresh_startup()
                    else:
                        self.error_occurred.emit("Failed to add startup item")
                        
        except Exception as e:
            self.error_occurred.emit(f"Failed to add startup item: {str(e)}")
            
    def remove_startup(self):
        """Remove selected startup item."""
        item = self.get_selected_startup_item()
        if item:
            if self.manager.remove_startup_item(
                item['name'],
                item['location'],
                item['type']
            ):
                self.startup_item_removed.emit(item['name'])
                self.refresh_startup()
            else:
                self.error_occurred.emit(f"Failed to remove startup item {item['name']}")
