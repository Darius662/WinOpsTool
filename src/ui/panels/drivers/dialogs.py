"""Dialogs for driver management."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                          QComboBox, QPushButton, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class StartupTypeDialog(QDialog):
    """Dialog for changing driver startup type."""
    
    # Available startup types
    STARTUP_TYPES = [
        'Auto',
        'Manual',
        'Disabled',
        'Boot',
        'System'
    ]
    
    def __init__(self, parent=None, name="", current_type=""):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
            name: Driver name
            current_type: Current startup type
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.name = name
        self.current_type = current_type
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle(f"Change Startup Type - {self.name}")
        layout = QVBoxLayout(self)
        
        # Type selector
        type_layout = QHBoxLayout()
        type_label = QLabel("Startup Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.STARTUP_TYPES)
        
        # Set current type if valid
        if self.current_type in self.STARTUP_TYPES:
            self.type_combo.setCurrentText(self.current_type)
            
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def get_startup_type(self):
        """Get the selected startup type.
        
        Returns:
            str: Selected startup type
        """
        return self.type_combo.currentText()


class DriverDetailsDialog(QDialog):
    """Dialog for showing detailed driver information."""
    
    def __init__(self, parent=None, details=None):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
            details: Driver details dictionary
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.details = details or {}
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle(f"Driver Details - {self.details.get('name', '')}")
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        
        # Details table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Property", "Value"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        
        # Add properties
        self._add_property("Name", self.details.get('name', ''))
        self._add_property("Display Name", self.details.get('display_name', ''))
        self._add_property("Description", self.details.get('description', ''))
        self._add_property("Manufacturer", self.details.get('manufacturer', ''))
        self._add_property("Start Type", self.details.get('start_type', ''))
        self._add_property("State", self.details.get('state', ''))
        self._add_property("Path", self.details.get('path', ''))
        self._add_property("Service Type", self.details.get('service_type', ''))
        self._add_property("Error Control", self.details.get('error_control', ''))
        self._add_property("Start Name", self.details.get('start_name', ''))
        self._add_property("System Name", self.details.get('system_name', ''))
        self._add_property("Tag ID", str(self.details.get('tag_id', '')))
        
        # Add dependencies
        deps = self.details.get('dependencies', [])
        if deps:
            self._add_property("Dependencies", '\n'.join(deps))
            
        # Adjust table size
        self.table.resizeColumnsToContents()
        
        # Buttons
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
    def _add_property(self, name, value):
        """Add a property row to the table.
        
        Args:
            name: Property name
            value: Property value
        """
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        name_item = QTableWidgetItem(name)
        value_item = QTableWidgetItem(str(value))
        
        # Make items read-only
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        
        self.table.setItem(row, 0, name_item)
        self.table.setItem(row, 1, value_item)
