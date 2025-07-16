"""Windows Network management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLineEdit, QLabel, QTabWidget)
from PyQt6.QtCore import QTimer
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import InterfacesTree, ConnectionsTree
from .dialogs import InterfaceStatsDialog
from .manager import NetworkManager

class NetworkPanel(BasePanel):
    """Panel for managing Windows Network interfaces and connections."""
    
    def __init__(self, parent=None):
        """Initialize network panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = NetworkManager()
        self.setup_ui()
        
        # Set up refresh timer (2 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_all)
        self.refresh_timer.start(2000)
        
        # Initial refresh
        self.refresh_all()
        
    def setup_ui(self):
        """Set up the panel UI."""
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Interfaces tab
        interfaces_widget = QWidget()
        interfaces_layout = QVBoxLayout(interfaces_widget)
        
        # Interface controls
        interface_controls = QHBoxLayout()
        
        interface_search_label = QLabel("Search:")
        self.interface_search = QLineEdit()
        self.interface_search.textChanged.connect(self.filter_interfaces)
        interface_controls.addWidget(interface_search_label)
        interface_controls.addWidget(self.interface_search)
        
        self.stats_button = QPushButton("View Statistics")
        self.stats_button.clicked.connect(self.view_interface_stats)
        interface_controls.addWidget(self.stats_button)
        
        self.interface_refresh = QPushButton("Refresh")
        self.interface_refresh.clicked.connect(self.refresh_interfaces)
        interface_controls.addWidget(self.interface_refresh)
        
        interfaces_layout.addLayout(interface_controls)
        
        # Interfaces tree
        self.interfaces_tree = InterfacesTree()
        self.interfaces_tree.itemSelectionChanged.connect(self.update_interface_buttons)
        interfaces_layout.addWidget(self.interfaces_tree)
        
        self.tab_widget.addTab(interfaces_widget, "Network Interfaces")
        
        # Connections tab
        connections_widget = QWidget()
        connections_layout = QVBoxLayout(connections_widget)
        
        # Connection controls
        connection_controls = QHBoxLayout()
        
        connection_search_label = QLabel("Search:")
        self.connection_search = QLineEdit()
        self.connection_search.textChanged.connect(self.filter_connections)
        connection_controls.addWidget(connection_search_label)
        connection_controls.addWidget(self.connection_search)
        
        self.connection_refresh = QPushButton("Refresh")
        self.connection_refresh.clicked.connect(self.refresh_connections)
        connection_controls.addWidget(self.connection_refresh)
        
        connections_layout.addLayout(connection_controls)
        
        # Connections tree
        self.connections_tree = ConnectionsTree()
        connections_layout.addWidget(self.connections_tree)
        
        self.tab_widget.addTab(connections_widget, "Network Connections")
        
        # Initial button state
        self.update_interface_buttons()
        
    def update_interface_buttons(self):
        """Update button enabled states based on interface selection."""
        has_selection = bool(self.interfaces_tree.selectedItems())
        self.stats_button.setEnabled(has_selection)
        
    def refresh_all(self):
        """Refresh both interfaces and connections."""
        self.refresh_interfaces()
        self.refresh_connections()
        
    def refresh_interfaces(self):
        """Refresh the network interfaces list."""
        try:
            # Get current selection
            selected_name = None
            if self.interfaces_tree.selectedItems():
                selected_name = self.interfaces_tree.selectedItems()[0].text(0)
                
            # Clear and repopulate tree
            self.interfaces_tree.clear_interfaces()
            interfaces = self.manager.get_interfaces()
            
            for iface in interfaces:
                self.interfaces_tree.add_interface(
                    iface['name'],
                    iface['type'],
                    iface['manufacturer'],
                    iface['mac'],
                    iface['ipv4'],
                    iface['ipv6'],
                    iface['speed'],
                    iface['mtu'],
                    iface['up'],
                    iface['bytes_sent'],
                    iface['bytes_recv']
                )
                
            # Reapply filter if search text exists
            if self.interface_search.text():
                self.filter_interfaces(self.interface_search.text())
                
            # Restore selection if interface still exists
            if selected_name:
                item = self.interfaces_tree.find_interface(selected_name)
                if item:
                    item.setSelected(True)
                    
            self.logger.debug("Refreshed network interfaces")
        except Exception as e:
            self.logger.error(f"Failed to refresh interfaces: {str(e)}")
            
    def refresh_connections(self):
        """Refresh the network connections list."""
        try:
            # Clear and repopulate tree
            self.connections_tree.clear_connections()
            connections = self.manager.get_connections()
            
            for conn in connections:
                self.connections_tree.add_connection(
                    conn['protocol'],
                    conn['local_address'],
                    conn['remote_address'],
                    conn['status'],
                    conn['pid'],
                    conn['process']
                )
                
            # Reapply filter if search text exists
            if self.connection_search.text():
                self.filter_connections(self.connection_search.text())
                
            self.logger.debug("Refreshed network connections")
        except Exception as e:
            self.logger.error(f"Failed to refresh connections: {str(e)}")
            
    def filter_interfaces(self, text):
        """Filter interfaces by name.
        
        Args:
            text: Search text
        """
        for i in range(self.interfaces_tree.topLevelItemCount()):
            item = self.interfaces_tree.topLevelItem(i)
            name = item.text(0).lower()
            search = text.lower()
            item.setHidden(search not in name)
            
    def filter_connections(self, text):
        """Filter connections by local address, remote address, or process.
        
        Args:
            text: Search text
        """
        for i in range(self.connections_tree.topLevelItemCount()):
            item = self.connections_tree.topLevelItem(i)
            local = item.text(1).lower()
            remote = item.text(2).lower()
            process = item.text(5).lower()
            search = text.lower()
            item.setHidden(
                search not in local and
                search not in remote and
                search not in process
            )
            
    def view_interface_stats(self):
        """View detailed statistics for selected interface."""
        item = self.interfaces_tree.selectedItems()[0]
        name = item.text(0)
        
        stats = self.manager.get_interface_stats(name)
        if stats:
            dialog = InterfaceStatsDialog(self, name, stats)
            dialog.exec()
