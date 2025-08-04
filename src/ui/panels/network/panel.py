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
        
        # Initialize imported config items
        self.imported_config_items = set()
        
        # Set up refresh timer (2 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_all)
        
        # Defer initial refresh and timer start
        # This will prevent blocking the UI during startup
        QTimer.singleShot(4000, self.delayed_start)
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Use the main_layout from BasePanel instead of creating a new layout
        layout = self.main_layout
        
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
            # Clear tree and get interfaces
            self.interfaces_tree.clear_interfaces()
            interfaces = self.manager.get_interfaces()
            
            # Track seen interface names for virtual entries
            seen_interface_names = set()
            
            for interface in interfaces:
                # Add interface to tree
                item = self.interfaces_tree.add_interface(
                    interface['name'],
                    interface['type'],
                    interface['manufacturer'],
                    interface['mac'],
                    interface['ipv4'],
                    interface['ipv6'],
                    interface['speed'],
                    interface['mtu'],
                    interface['up'],
                    interface['bytes_sent'],
                    interface['bytes_recv']
                )
                
                # Add to seen interfaces
                seen_interface_names.add(interface['name'])
                
                # Check if this interface is in imported config
                if self.is_imported_config_item(f"network:interface:{interface['name']}"):
                    self.interfaces_tree.highlight_item(item)
                    
            # Add virtual interfaces from config
            self.add_virtual_interfaces(seen_interface_names)
            
            self.logger.info("Network interfaces refreshed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh network interfaces: {str(e)}")
            
    def refresh_connections(self):
        """Refresh the network connections list."""
        try:
            # Clear tree and get connections
            self.connections_tree.clear_connections()
            connections = self.manager.get_connections()
            
            for connection in connections:
                # Add connection to tree
                self.connections_tree.add_connection(
                    connection['protocol'],
                    connection['local_address'],
                    connection['local_port'],
                    connection['remote_address'],
                    connection['remote_port'],
                    connection['state'],
                    connection['pid'],
                    connection['process_name']
                )
                
            self.logger.info("Network connections refreshed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh network connections: {str(e)}")
            
    def add_virtual_interfaces(self, seen_interface_names):
        """Add virtual entries for interfaces in config but not in system.
        
        Args:
            seen_interface_names: Set of interface names that are currently in the system
        """
        try:
            # Check for interface configurations in imported config
            for item_id in self.imported_config_items:
                if item_id.startswith("network:interface:"):
                    # Extract interface name from the item ID
                    # Format is "network:interface:name"
                    parts = item_id.split(":", 2)
                    if len(parts) == 3:
                        interface_name = parts[2]
                        
                        # Only add virtual entry if interface is not in system
                        if interface_name not in seen_interface_names:
                            # Get interface config from our stored virtual interfaces
                            if interface_name in self.virtual_interfaces:
                                iface_config = self.virtual_interfaces[interface_name]
                                
                                self.interfaces_tree.add_virtual_interface(
                                    name=interface_name,
                                    type=iface_config.get('type', 'Unknown'),
                                    manufacturer=iface_config.get('manufacturer', ''),
                                    mac=iface_config.get('mac', ''),
                                    ipv4=iface_config.get('ipv4', ''),
                                    ipv6=iface_config.get('ipv6', ''),
                                    speed=iface_config.get('speed', 0),
                                    mtu=iface_config.get('mtu', 0),
                                    up=iface_config.get('enabled', False)
                                )
                                
                                self.logger.debug(f"Added virtual interface entry: {interface_name}")
                            
        except Exception as e:
            self.logger.error(f"Error adding virtual interfaces: {str(e)}")
            
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
            
    def delayed_start(self):
        """Delayed initialization to prevent blocking the UI during startup."""
        self.logger.info('Starting delayed initialization of NetworkPanel')
        self.refresh_all()
        # Auto-refresh timer removed - refresh only happens manually via button
        self.logger.info('NetworkPanel initialization complete')
        
    def setup_connections(self):
        """Set up signal-slot connections."""
        # Connections already set up in setup_ui method
        # This method is required by BasePanel but implementation is kept here
        # for consistency with the BasePanel interface
        pass
        
    def apply_config(self, config):
        """Apply configuration to the panel.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if configuration was applied successfully, False otherwise
        """
        self.logger.info("Applying network configuration")
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Process configuration
            if 'network' not in config:
                self.logger.warning("No network configuration found")
                return False
                
            network_config = config['network']
            
            # Apply network interface configurations if available
            if 'interfaces' in network_config and isinstance(network_config['interfaces'], list):
                self.logger.info(f"Found {len(network_config['interfaces'])} interface configurations")
                
                success = False
                for interface_config in network_config['interfaces']:
                    if not isinstance(interface_config, dict) or 'name' not in interface_config:
                        self.logger.warning("Skipping invalid interface configuration")
                        continue
                        
                    interface_name = interface_config['name']
                    
                    # Check if we should enable/disable the interface
                    if 'enabled' in interface_config:
                        enabled = bool(interface_config['enabled'])
                        result = self.manager.set_interface_status(interface_name, enabled)
                        
                        if result:
                            status = "enabled" if enabled else "disabled"
                            self.logger.info(f"Interface {interface_name} {status}")
                            success = True
                        else:
                            self.logger.warning(f"Failed to set status for interface {interface_name}")
                
                # Refresh interfaces to show updated state
                self.refresh_interfaces()
                return success
                
            # If no specific configurations were applied, return True
            # This allows for future expansion of network configuration options
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying network configuration: {str(e)}")
            return False
            
    def export_config(self):
        """Export panel configuration.
        
        Returns:
            dict: Dictionary containing panel configuration
        """
        self.logger.info("Exporting network configuration")
        
        try:
            # Get current network interfaces
            interfaces = self.manager.get_interfaces()
            
            # Create exportable interface configurations
            interface_configs = []
            
            for iface in interfaces:
                # Skip loopback and virtual interfaces
                if iface['name'].lower() == 'loopback' or 'virtual' in iface['name'].lower():
                    continue
                    
                interface_config = {
                    'name': iface['name'],
                    'enabled': iface['up'],
                    'mac': iface['mac'],
                    'mtu': iface['mtu']
                }
                
                # Add IP configurations if available
                if iface['ipv4']:
                    interface_config['ipv4'] = iface['ipv4']
                    
                if iface['ipv6']:
                    interface_config['ipv6'] = iface['ipv6']
                
                interface_configs.append(interface_config)
            
            # Create configuration dictionary
            config = {
                'network': {
                    'interfaces': interface_configs
                }
            }
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error exporting network configuration: {str(e)}")
            return {'network': {'interfaces': []}}

    def mark_config_items(self, config):
        """Mark items from configuration for highlighting without applying changes.
        
        This method identifies and marks network interfaces from the configuration
        that would be modified by apply_config(), but does not actually
        apply any changes to the system. Items will be visually highlighted in the UI.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if items were marked successfully, False otherwise
        """
        self.logger.info("Marking network interfaces from configuration for highlighting")
        
        # Clear previous imported items
        self.imported_config_items.clear()
        
        # Initialize virtual interfaces dictionary
        self.virtual_interfaces = {}
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Check if network section exists
            if 'network' not in config:
                self.logger.warning("No network configuration found")
                return False
                
            network_config = config['network']
            
            # Process interface configurations
            if 'interfaces' in network_config and isinstance(network_config['interfaces'], list):
                self.logger.info(f"Found {len(network_config['interfaces'])} interface configurations")
                
                # Get existing interfaces for comparison
                existing_interfaces = {iface['name']: iface for iface in self.manager.get_interfaces()}
                
                for interface_config in network_config['interfaces']:
                    if not isinstance(interface_config, dict) or 'name' not in interface_config:
                        self.logger.warning("Skipping invalid interface configuration")
                        continue
                        
                    interface_name = interface_config['name']
                    
                    # Mark this interface as imported from config for highlighting
                    self.mark_as_imported_config(f"network:interface:{interface_name}")
                    self.logger.debug(f"Marked network interface for highlighting: {interface_name}")
                    
                    # Check if interface exists
                    if interface_name in existing_interfaces:
                        # Interface exists, it will be highlighted during refresh
                        pass
                    else:
                        # Interface doesn't exist or needs to be modified, store for virtual entry
                        self.virtual_interfaces[interface_name] = interface_config
                
                # Refresh interfaces to show updated state with highlighting
                self.refresh_interfaces()
                
                return True
                
            # If no specific configurations were found, return False
            self.logger.warning("No interface configurations found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error marking network interfaces from configuration: {str(e)}")
            return False
    
    def mark_as_imported_config(self, item):
        """Mark an item as imported from config for highlighting.
        
        Args:
            item: Item to mark
        """
        self.imported_config_items.add(item)
        
    def is_imported_config_item(self, item):
        """Check if an item is marked as imported from config.
        
        Args:
            item: Item to check
            
        Returns:
            bool: True if item is marked as imported, False otherwise
        """
        return item in self.imported_config_items
        
    def refresh_connecctions(self):
        """Alias for refresh_connections to handle typo in method name.
        
        This method exists to fix an AttributeError where code is trying to call
        'refresh_connecctions' (with an extra 'c') instead of 'refresh_connections'.
        """
        self.logger.warning("Called refresh_connecctions (typo) - using refresh_connections instead")
        return self.refresh_connections()
