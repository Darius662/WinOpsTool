"""Dialogs for Windows package management."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                          QLineEdit, QDialogButtonBox, QTableWidget,
                          QTableWidgetItem, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class WingetSearchDialog(QDialog):
    """Dialog for searching winget packages."""
    
    def __init__(self, parent=None):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.selected_package = None
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Search Winget Packages")
        self.resize(800, 500)
        layout = QVBoxLayout(self)
        
        # Search controls
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_packages)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)
        
        # Results table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Name",
            "Version",
            "Source",
            "Description"
        ])
        
        # Set column widths
        self.table.setColumnWidth(0, 200)  # ID
        self.table.setColumnWidth(1, 200)  # Name
        self.table.setColumnWidth(2, 100)  # Version
        self.table.setColumnWidth(3, 100)  # Source
        self.table.setColumnWidth(4, 300)  # Description
        
        # Enable sorting
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        
        # Enable selection
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        layout.addWidget(self.table)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept_selection)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def search_packages(self):
        """Search for winget packages."""
        # This will be implemented by the parent panel
        pass
        
    def set_packages(self, packages):
        """Set the packages to display.
        
        Args:
            packages: List of package dictionaries
        """
        self.table.setRowCount(0)
        
        for pkg in packages:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Add items
            for col, key in enumerate(['id', 'name', 'version', 'source', 'description']):
                item = QTableWidgetItem(pkg.get(key, ''))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, item)
                
    def accept_selection(self):
        """Accept the selected package."""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a package to install."
            )
            return
            
        # Get package ID from first column
        self.selected_package = self.table.item(
            selected_rows[0].row(),
            0
        ).text()
        self.accept()
        
    def get_selected_package(self):
        """Get the selected package ID.
        
        Returns:
            str: Selected package ID or None
        """
        return self.selected_package
