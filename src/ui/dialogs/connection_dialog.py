"""Remote PC Connection Dialog."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                          QPushButton, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox)
from PyQt6.QtCore import Qt
from src.core.remote.manager import RemoteManager

class ConnectionDialog(QDialog):
    """Dialog for managing remote PC connections."""
    
    def __init__(self, remote_manager: RemoteManager, parent=None):
        super().__init__(parent)
        self.remote_manager = remote_manager
        self.setWindowTitle("Remote PC Connections")
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Connection list
        self.connections_tree = QTreeWidget()
        self.connections_tree.setHeaderLabels([
            "Name",
            "Hostname",
            "Username",
            "Status"
        ])
        self.connections_tree.setAlternatingRowColors(True)
        for i, width in enumerate([150, 150, 150, 100]):
            self.connections_tree.setColumnWidth(i, width)
            
        layout.addWidget(self.connections_tree)
        
        # Add connection form
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.hostname_edit = QLineEdit()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Hostname:", self.hostname_edit)
        form_layout.addRow("Username:", self.username_edit)
        form_layout.addRow("Password:", self.password_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Connection")
        self.remove_btn = QPushButton("Remove Connection")
        self.refresh_btn = QPushButton("Refresh")
        self.close_btn = QPushButton("Close")
        
        for btn in [self.add_btn, self.remove_btn, self.refresh_btn, self.close_btn]:
            button_layout.addWidget(btn)
            
        layout.addLayout(button_layout)
        
        # Connect signals
        self.add_btn.clicked.connect(self.add_connection)
        self.remove_btn.clicked.connect(self.remove_connection)
        self.refresh_btn.clicked.connect(self.refresh_connections)
        self.close_btn.clicked.connect(self.accept)
        
        # Initial load
        self.refresh_connections()
        
    def add_connection(self):
        """Add a new remote PC connection."""
        name = self.name_edit.text().strip()
        hostname = self.hostname_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not all([name, hostname, username, password]):
            QMessageBox.warning(self, "Warning", "Please fill in all fields")
            return
            
        if self.remote_manager.add_connection(name, hostname, username, password):
            self.name_edit.clear()
            self.hostname_edit.clear()
            self.username_edit.clear()
            self.password_edit.clear()
            self.refresh_connections()
        else:
            QMessageBox.critical(self, "Error", f"Failed to connect to {hostname}")
            
    def remove_connection(self):
        """Remove the selected connection."""
        current_item = self.connections_tree.currentItem()
        if not current_item:
            return
            
        name = current_item.text(0)
        
        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Are you sure you want to remove the connection to '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.remote_manager.remove_connection(name):
                self.refresh_connections()
            else:
                QMessageBox.critical(self, "Error", f"Failed to remove connection to {name}")
                
    def refresh_connections(self):
        """Refresh the connections list."""
        self.connections_tree.clear()
        self.remote_manager.refresh_connections()
        
        for pc in self.remote_manager.get_connections():
            item = QTreeWidgetItem([
                pc.name,
                pc.hostname,
                pc.username,
                "Connected" if pc.is_connected else "Disconnected"
            ])
            self.connections_tree.addTopLevelItem(item)
