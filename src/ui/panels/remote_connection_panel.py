"""
Remote Connection Panel for WinOpsTool

This panel allows users to manage remote connections using the REST API.
"""

import os
import sys
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QSpinBox, QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.core.logger import setup_logger
from src.core.remote.integration import RemoteIntegration

class RemoteConnectionPanel(QWidget):
    """Panel for managing remote connections using REST API."""
    
    # Signal emitted when connection state changes
    connection_changed = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        """Initialize the remote connection panel."""
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.remote_integration = RemoteIntegration()
        
        self.init_ui()
        self.refresh_connections()
    
    def init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Connection form
        connection_group = QGroupBox("Add New Connection")
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.hostname_edit = QLineEdit()
        self.api_key_edit = QLineEdit()
        self.port_spin = QSpinBox()
        self.port_spin.setMinimum(1)
        self.port_spin.setMaximum(65535)
        self.port_spin.setValue(8000)
        
        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Hostname/IP:", self.hostname_edit)
        form_layout.addRow("API Key:", self.api_key_edit)
        form_layout.addRow("Port:", self.port_spin)
        
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Connection")
        self.add_button.clicked.connect(self.add_connection)
        button_layout.addWidget(self.add_button)
        
        connection_layout = QVBoxLayout()
        connection_layout.addLayout(form_layout)
        connection_layout.addLayout(button_layout)
        connection_group.setLayout(connection_layout)
        
        main_layout.addWidget(connection_group)
        
        # Connections table
        connections_group = QGroupBox("Saved Connections")
        connections_layout = QVBoxLayout()
        
        self.connections_table = QTableWidget(0, 4)
        self.connections_table.setHorizontalHeaderLabels(["Name", "Hostname", "Port", "Status"])
        self.connections_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.connections_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.connections_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.connections_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        connections_layout.addWidget(self.connections_table)
        
        # Table buttons
        table_buttons_layout = QHBoxLayout()
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_selected)
        
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect)
        self.disconnect_button.setEnabled(False)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_selected)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_connections)
        
        table_buttons_layout.addWidget(self.connect_button)
        table_buttons_layout.addWidget(self.disconnect_button)
        table_buttons_layout.addWidget(self.remove_button)
        table_buttons_layout.addWidget(self.refresh_button)
        
        connections_layout.addLayout(table_buttons_layout)
        connections_group.setLayout(connections_layout)
        
        main_layout.addWidget(connections_group)
        
        # Status label
        self.status_label = QLabel("Not connected to any remote PC")
        main_layout.addWidget(self.status_label)
    
    def add_connection(self):
        """Add a new remote connection."""
        name = self.name_edit.text().strip()
        hostname = self.hostname_edit.text().strip()
        api_key = self.api_key_edit.text().strip()
        port = self.port_spin.value()
        
        if not name or not hostname or not api_key:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields")
            return
        
        # Add the connection
        if self.remote_integration.rest_manager.add_connection(name, hostname, api_key, port):
            self.logger.info(f"Added connection to remote PC: {name}")
            self.refresh_connections()
            
            # Clear the form
            self.name_edit.clear()
            self.hostname_edit.clear()
            self.api_key_edit.clear()
            self.port_spin.setValue(8000)
        else:
            QMessageBox.critical(self, "Connection Error", f"Failed to add connection to {hostname}")
    
    def refresh_connections(self):
        """Refresh the connections table."""
        connections = self.remote_integration.get_remote_connections()
        
        self.connections_table.setRowCount(len(connections))
        
        for i, connection in enumerate(connections):
            self.connections_table.setItem(i, 0, QTableWidgetItem(connection["name"]))
            self.connections_table.setItem(i, 1, QTableWidgetItem(connection["hostname"]))
            self.connections_table.setItem(i, 2, QTableWidgetItem(str(connection["port"])))
            
            status = "Connected" if connection["is_connected"] else "Disconnected"
            status_item = QTableWidgetItem(status)
            if connection["is_connected"]:
                status_item.setForeground(Qt.GlobalColor.green)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            
            self.connections_table.setItem(i, 3, status_item)
        
        # Update the status label and buttons
        active_connection = self.remote_integration.get_active_remote_connection()
        if active_connection:
            self.status_label.setText(f"Connected to {active_connection['name']} ({active_connection['hostname']})")
            self.disconnect_button.setEnabled(True)
        else:
            self.status_label.setText("Not connected to any remote PC")
            self.disconnect_button.setEnabled(False)
    
    def connect_to_selected(self):
        """Connect to the selected remote PC."""
        selected_rows = self.connections_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a connection")
            return
        
        row = selected_rows[0].row()
        name = self.connections_table.item(row, 0).text()
        
        # Connect to the remote PC
        if self.remote_integration.connect_to_remote(name):
            self.logger.info(f"Connected to remote PC: {name}")
            self.refresh_connections()
            
            # Emit the connection changed signal
            self.connection_changed.emit(True)
        else:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to {name}")
    
    def disconnect(self):
        """Disconnect from the current remote PC."""
        if self.remote_integration.disconnect_from_remote():
            self.logger.info("Disconnected from remote PC")
            self.refresh_connections()
            
            # Emit the connection changed signal
            self.connection_changed.emit(False)
        else:
            QMessageBox.critical(self, "Disconnection Error", "Failed to disconnect from remote PC")
    
    def remove_selected(self):
        """Remove the selected remote connection."""
        selected_rows = self.connections_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a connection")
            return
        
        row = selected_rows[0].row()
        name = self.connections_table.item(row, 0).text()
        
        # Confirm removal
        reply = QMessageBox.question(
            self, 
            "Confirm Removal", 
            f"Are you sure you want to remove the connection to {name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove the connection
            if self.remote_integration.rest_manager.remove_connection(name):
                self.logger.info(f"Removed connection to remote PC: {name}")
                self.refresh_connections()
            else:
                QMessageBox.critical(self, "Removal Error", f"Failed to remove connection to {name}")
    
    def connect_to_remote(self, name: str, hostname: str, api_key: str, port: int = 8000) -> bool:
        """
        Connect to a remote PC using REST API.
        
        Args:
            name: Friendly name for the connection
            hostname: Hostname or IP address of the remote PC
            api_key: API key for authentication
            port: Port number (default: 8000)
            
        Returns:
            True if connection was successful, False otherwise
        """
        return self.remote_integration.connect_to_remote(name, hostname, api_key, port)
    
    def disconnect_from_remote(self) -> bool:
        """
        Disconnect from the current remote PC.
        
        Returns:
            True if disconnection was successful, False otherwise
        """
        return self.remote_integration.disconnect_from_remote()
    
    def is_connected_to_remote(self) -> bool:
        """
        Check if connected to a remote PC.
        
        Returns:
            True if connected to a remote PC, False otherwise
        """
        return self.remote_integration.is_connected_to_remote()
    
    def get_manager_factory(self):
        """
        Get the manager factory instance.
        
        Returns:
            Manager factory instance
        """
        return self.remote_integration.get_manager_factory()
