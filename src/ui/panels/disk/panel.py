"""Windows Disk management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLineEdit, QLabel, QTabWidget, QMessageBox)
from PyQt6.QtCore import QTimer
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import DisksTree, VolumesTree
from .dialogs import DiskPerformanceDialog, VolumeInfoDialog
from .network_drive_dialog import NetworkDriveDialog
from .manager import DiskManager

class DiskPanel(BasePanel):
    """Panel for managing Windows Disks and Volumes."""
    
    def __init__(self, parent=None):
        """Initialize disk panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = DiskManager()
        
        # Initialize imported config items
        self.imported_config_items = set()
        self.virtual_network_drives = {}
        
        # Set up refresh timer (5 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_all)
        
        # Defer initial refresh and timer start
        # This will prevent blocking the UI during startup
        QTimer.singleShot(1500, self.delayed_start)
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Use the main_layout from BasePanel instead of creating a new layout
        layout = self.main_layout
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Physical Disks tab
        disks_widget = QWidget()
        disks_layout = QVBoxLayout(disks_widget)
        
        # Disk controls
        disk_controls = QHBoxLayout()
        
        disk_search_label = QLabel("Search:")
        self.disk_search = QLineEdit()
        self.disk_search.textChanged.connect(self.filter_disks)
        disk_controls.addWidget(disk_search_label)
        disk_controls.addWidget(self.disk_search)
        
        self.performance_button = QPushButton("View Performance")
        self.performance_button.clicked.connect(self.view_disk_performance)
        disk_controls.addWidget(self.performance_button)
        
        self.disk_refresh = QPushButton("Refresh")
        self.disk_refresh.clicked.connect(self.refresh_disks)
        disk_controls.addWidget(self.disk_refresh)
        
        disks_layout.addLayout(disk_controls)
        
        # Disks tree
        self.disks_tree = DisksTree()
        self.disks_tree.itemSelectionChanged.connect(self.update_disk_buttons)
        disks_layout.addWidget(self.disks_tree)
        
        self.tab_widget.addTab(disks_widget, "Physical Disks")
        
        # Volumes tab
        volumes_widget = QWidget()
        volumes_layout = QVBoxLayout(volumes_widget)
        
        # Volume controls
        volume_controls = QHBoxLayout()
        
        volume_search_label = QLabel("Search:")
        self.volume_search = QLineEdit()
        self.volume_search.textChanged.connect(self.filter_volumes)
        volume_controls.addWidget(volume_search_label)
        volume_controls.addWidget(self.volume_search)
        
        self.info_button = QPushButton("View Details")
        self.info_button.clicked.connect(self.view_volume_info)
        volume_controls.addWidget(self.info_button)
        
        self.add_network_button = QPushButton("Add Network Drive")
        self.add_network_button.clicked.connect(self.add_network_drive)
        volume_controls.addWidget(self.add_network_button)
        
        self.disconnect_network_button = QPushButton("Disconnect Drive")
        self.disconnect_network_button.clicked.connect(self.disconnect_network_drive)
        self.disconnect_network_button.setEnabled(False)
        volume_controls.addWidget(self.disconnect_network_button)
        
        self.volume_refresh = QPushButton("Refresh")
        self.volume_refresh.clicked.connect(self.refresh_volumes)
        volume_controls.addWidget(self.volume_refresh)
        
        volumes_layout.addLayout(volume_controls)
        
        # Volumes tree
        self.volumes_tree = VolumesTree()
        self.volumes_tree.itemSelectionChanged.connect(self.update_volume_buttons)
        volumes_layout.addWidget(self.volumes_tree)
        
        self.tab_widget.addTab(volumes_widget, "Volumes")
        
        # Initial button state
        self.update_disk_buttons()
        self.update_volume_buttons()
        
    def update_disk_buttons(self):
        """Update button enabled states based on disk selection."""
        has_selection = bool(self.disks_tree.selectedItems())
        self.performance_button.setEnabled(has_selection)
        
    def update_volume_buttons(self):
        """Update button enabled states based on volume selection."""
        has_selection = bool(self.volumes_tree.selectedItems())
        self.info_button.setEnabled(has_selection)
        
        # Only enable disconnect button for network drives
        if has_selection:
            selected_item = self.volumes_tree.selectedItems()[0]
            drive_type = selected_item.text(2)  # Type column
            self.disconnect_network_button.setEnabled(drive_type == "Network Drive")
        else:
            self.disconnect_network_button.setEnabled(False)
        
    def refresh_all(self):
        """Refresh both disks and volumes."""
        self.refresh_disks()
        self.refresh_volumes()
        
    def refresh_disks(self):
        """Refresh the physical disks list."""
        try:
            # Get current selection
            selected_id = None
            if self.disks_tree.selectedItems():
                selected_id = self.disks_tree.selectedItems()[0].text(0)
                
            # Clear and repopulate tree
            self.disks_tree.clear_disks()
            disks = self.manager.get_disks()
            
            for disk in disks:
                self.disks_tree.add_disk(
                    disk['name'],
                    disk['model'],
                    disk['interface'],
                    disk['size'],
                    disk['partitions'],
                    disk['status'],
                    disk['serial'],
                    disk['firmware']
                )
                
            # Reapply filter if search text exists
            if self.disk_search.text():
                self.filter_disks(self.disk_search.text())
                
            # Restore selection if disk still exists
            if selected_id:
                item = self.disks_tree.find_disk(selected_id)
                if item:
                    item.setSelected(True)
                    
            self.logger.debug("Refreshed physical disks")
        except Exception as e:
            self.logger.error(f"Failed to refresh disks: {str(e)}")
            
    def refresh_volumes(self):
        """Refresh the volumes list."""
        try:
            # Get current selection
            selected_mountpoint = None
            if self.volumes_tree.selectedItems():
                selected_mountpoint = self.volumes_tree.selectedItems()[0].text(0)
                
            # Clear and repopulate tree
            self.volumes_tree.clear_volumes()
            volumes = self.manager.get_volumes()
            
            # Track volume drive letters we've seen to add virtual entries later
            seen_drive_letters = set()
            
            for vol in volumes:
                # Check if this volume is in the imported config
                drive_letter = vol['device'].rstrip('\\')
                is_imported = self.is_imported_config_item(f"disk:network_drive:{drive_letter}")
                
                # Add to seen drive letters
                seen_drive_letters.add(drive_letter)
                
                item = self.volumes_tree.add_volume(
                    vol['device'],
                    vol['label'],
                    vol['type'],
                    vol['fstype'],
                    vol['total'],
                    vol['used'],
                    vol['free']
                )
                
                # Highlight if this volume is in the imported config
                if is_imported:
                    self.volumes_tree.highlight_item(item)
            
            # Add virtual entries for network drives in config but not in system
            self.add_virtual_network_drives(seen_drive_letters)
                
            # Reapply filter if search text exists
            if self.volume_search.text():
                self.filter_volumes(self.volume_search.text())
                
            # Restore selection if volume still exists
            if selected_mountpoint:
                item = self.volumes_tree.find_volume(selected_mountpoint)
                if item:
                    item.setSelected(True)
                    
            # Update button states
            self.update_volume_buttons()
            
            self.logger.debug("Refreshed volumes")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh volumes: {str(e)}")
            
    def add_virtual_network_drives(self, seen_drive_letters):
        """Add virtual entries for network drives in config but not in system.
        
        Args:
            seen_drive_letters: Set of drive letters that are currently in the system
        """
        try:
            # Check for network drive configurations in imported config
            for drive_letter, drive_config in self.virtual_network_drives.items():
                # Only add virtual entry if drive letter is not in system
                if drive_letter not in seen_drive_letters:
                    network_path = drive_config.get('network_path', '')
                    
                    self.volumes_tree.add_virtual_volume(
                        device=drive_letter,
                        label=network_path,
                        type="Network Drive",
                        fstype="Network"
                    )
                    
                    self.logger.debug(f"Added virtual network drive entry: {drive_letter} -> {network_path}")
                    
        except Exception as e:
            self.logger.error(f"Error adding virtual network drives: {str(e)}")
            
    def filter_disks(self, text):
        """Filter disks by name or model.
        
        Args:
            text: Search text
        """
        for i in range(self.disks_tree.topLevelItemCount()):
            item = self.disks_tree.topLevelItem(i)
            name = item.text(0).lower()
            model = item.text(1).lower()
            search = text.lower()
            item.setHidden(search not in name and search not in model)
            
    def filter_volumes(self, text):
        """Filter volumes by drive letter or label.
        
        Args:
            text: Search text
        """
        for i in range(self.volumes_tree.topLevelItemCount()):
            item = self.volumes_tree.topLevelItem(i)
            drive = item.text(0).lower()
            label = item.text(1).lower()
            search = text.lower()
            item.setHidden(search not in drive and search not in label)
            
    def view_disk_performance(self):
        """View performance metrics for selected disk."""
        item = self.disks_tree.selectedItems()[0]
        name = item.text(0)
        
        metrics = self.manager.get_disk_performance(name)
        if metrics:
            dialog = DiskPerformanceDialog(self, name, metrics)
            dialog.exec()
            
    def view_volume_info(self):
        """View detailed information for selected volume."""
        item = self.volumes_tree.selectedItems()[0]
        mountpoint = item.text(0)
        
        info = self.manager.get_volume_info(mountpoint)
        if info:
            dialog = VolumeInfoDialog(self, mountpoint, info)
            dialog.exec()
            
    def delayed_start(self):
        """Delayed initialization to prevent blocking the UI during startup."""
        self.logger.info('Starting delayed initialization of DiskPanel')
        self.refresh_all()
        # Auto-refresh timer removed - refresh only happens manually via button
        self.logger.info('DiskPanel initialization complete')
        
    def setup_connections(self):
        """Set up signal-slot connections."""
        # Connections already set up in setup_ui method
        # This method is required by BasePanel but implementation is kept here
        # for consistency with the BasePanel interface
        pass
        
    def add_network_drive(self):
        """Open dialog to add a network drive."""
        dialog = NetworkDriveDialog(self)
        if dialog.exec():
            values = dialog.get_values()
            try:
                result = self.manager.map_network_drive(
                    values['network_path'],
                    values['drive_letter'],
                    values['use_windows_credentials'],
                    values['username'],
                    values['password'],
                    values['reconnect']
                )
                
                if result['success']:
                    QMessageBox.information(self, "Success", 
                                         f"Network drive {values['drive_letter']} mapped successfully.")
                    self.refresh_volumes()
                else:
                    QMessageBox.warning(self, "Error", 
                                      f"Failed to map network drive: {result['error']}")
            except Exception as e:
                self.logger.error(f"Error mapping network drive: {str(e)}")
                QMessageBox.critical(self, "Error", 
                                   f"Error mapping network drive: {str(e)}")
                                   
    def disconnect_network_drive(self):
        """Disconnect selected network drive."""
        if not self.volumes_tree.selectedItems():
            return
            
        selected_item = self.volumes_tree.selectedItems()[0]
        drive_letter = selected_item.text(0)  # Drive letter column
        drive_type = selected_item.text(2)    # Type column
        
        # Verify it's a network drive
        if drive_type != "Network Drive":
            QMessageBox.warning(self, "Error", 
                              f"{drive_letter} is not a network drive.")
            return
            
        # Confirm disconnection
        reply = QMessageBox.question(self, "Disconnect Network Drive",
                                   f"Are you sure you want to disconnect {drive_letter}?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                                   
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Call manager to disconnect
                result = self.manager.disconnect_network_drive(drive_letter)
                
                if result['success']:
                    # Check if there was a warning
                    if 'warning' in result:
                        QMessageBox.information(self, "Information", 
                                     f"{result['warning']}")
                    else:
                        QMessageBox.information(self, "Success", 
                                     f"Network drive {drive_letter} disconnected successfully.")
                    self.refresh_volumes()
                else:
                    QMessageBox.warning(self, "Error", 
                              f"Failed to disconnect network drive: {result['error']}")
            except Exception as e:
                self.logger.error(f"Error disconnecting network drive: {str(e)}")
                QMessageBox.critical(self, "Error", 
                           f"Error disconnecting network drive: {str(e)}")

    def apply_config(self, config):
        """Apply configuration to the panel.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if configuration was applied successfully, False otherwise
        """
        self.logger.info("Applying disk configuration")
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Check if disk section exists
            if 'disk' not in config:
                self.logger.warning("No disk configuration found")
                return False
                
            disk_config = config['disk']
            
            # Process network drive configurations
            if 'network_drives' in disk_config and isinstance(disk_config['network_drives'], list):
                self.logger.info(f"Found {len(disk_config['network_drives'])} network drive configurations")
                
                # Track success/failure
                success_count = 0
                total_count = 0
                
                # Get existing volumes for comparison
                existing_volumes = {vol['device'].rstrip('\\'): vol for vol in self.manager.get_volumes()}
                
                for drive_config in disk_config['network_drives']:
                    if not isinstance(drive_config, dict):
                        self.logger.warning("Skipping invalid network drive configuration")
                        continue
                        
                    # Check required fields
                    if 'network_path' not in drive_config or 'drive_letter' not in drive_config:
                        self.logger.warning("Skipping network drive without required fields")
                        continue
                        
                    total_count += 1
                    drive_letter = drive_config['drive_letter']
                    network_path = drive_config['network_path']
                    
                    # Optional fields with defaults
                    use_windows_creds = drive_config.get('use_windows_creds', True)
                    username = drive_config.get('username', '')
                    password = drive_config.get('password', '')
                    reconnect = drive_config.get('reconnect', True)
                    
                    # Check if drive letter exists
                    if drive_letter in existing_volumes:
                        # If it's already mapped to the same network path, skip
                        vol = existing_volumes[drive_letter]
                        if vol.get('is_network_drive', False) and vol.get('network_path') == network_path:
                            self.logger.info(f"Network drive {drive_letter} already mapped to {network_path}")
                            success_count += 1
                            continue
                        
                        # Otherwise, disconnect first
                        self.logger.info(f"Disconnecting existing drive {drive_letter} before remapping")
                        result = self.manager.disconnect_network_drive(drive_letter)
                        if not result.get('success', False):
                            self.logger.error(f"Failed to disconnect drive {drive_letter}: {result.get('error', 'Unknown error')}")
                            continue
                    
                    # Map the network drive
                    self.logger.info(f"Mapping network drive {drive_letter} to {network_path}")
                    result = self.manager.map_network_drive(
                        network_path=network_path,
                        drive_letter=drive_letter,
                        use_windows_creds=use_windows_creds,
                        username=username,
                        password=password,
                        reconnect=reconnect
                    )
                    
                    if result.get('success', False):
                        self.logger.info(f"Successfully mapped network drive {drive_letter} to {network_path}")
                        success_count += 1
                    else:
                        self.logger.error(f"Failed to map network drive {drive_letter}: {result.get('error', 'Unknown error')}")
                
                # Clear imported config items and virtual drives since they've been applied
                self.imported_config_items.clear()
                self.virtual_network_drives.clear()
                
                # Refresh volumes to show updated state
                self.refresh_volumes()
                
                return success_count > 0 and success_count == total_count
                
            # If no specific configurations were found, return False
            self.logger.warning("No network drive configurations found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error applying disk configuration: {str(e)}")
            return False

    def export_config(self):
        """Export panel configuration.
        
        Returns:
            dict: Dictionary containing panel configuration
        """
        self.logger.info("Exporting disk configuration")
        
        try:
            # Get current volumes
            volumes = self.manager.get_volumes()
            
            # Filter for network drives and create exportable configurations
            network_drives = []
            
            for volume in volumes:
                # Only include network drives
                if volume['type'] != "Network Drive":
                    continue
                    
                # Create network drive configuration
                drive_config = {
                    'drive_letter': volume['drive_letter'],
                    'network_path': volume['path'],
                    'reconnect': True  # Default to reconnect at logon
                }
                
                network_drives.append(drive_config)
            
            # Create configuration dictionary
            config = {
                'disk': {
                    'network_drives': network_drives
                }
            }
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error exporting disk configuration: {str(e)}")
            return {'disk': {'network_drives': []}}

    def mark_config_items(self, config):
        """Mark items from configuration for highlighting without applying changes.
        
        This method identifies and marks network drives from the configuration
        that would be modified by apply_config(), but does not actually
        apply any changes to the system. Items will be visually highlighted in the UI.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if items were marked successfully, False otherwise
        """
        self.logger.info("Marking network drives from configuration for highlighting")
        
        # Clear previous imported items
        self.imported_config_items.clear()
        
        # Clear virtual network drives dictionary
        self.virtual_network_drives = {}
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Check if disk section exists
            if 'disk' not in config:
                self.logger.warning("No disk configuration found")
                return False
                
            disk_config = config['disk']
            
            # Process network drive configurations
            if 'network_drives' in disk_config and isinstance(disk_config['network_drives'], list):
                self.logger.info(f"Found {len(disk_config['network_drives'])} network drive configurations")
                
                # Get existing volumes for comparison
                existing_volumes = {vol['device'].rstrip('\\'): vol for vol in self.manager.get_volumes()}
                
                for drive_config in disk_config['network_drives']:
                    if not isinstance(drive_config, dict):
                        self.logger.warning("Skipping invalid network drive configuration")
                        continue
                        
                    # Check required fields
                    if 'network_path' not in drive_config or 'drive_letter' not in drive_config:
                        self.logger.warning("Skipping network drive without required fields")
                        continue
                        
                    drive_letter = drive_config['drive_letter']
                    network_path = drive_config['network_path']
                    
                    # Mark this network drive as imported from config for highlighting
                    self.mark_as_imported_config(f"disk:network_drive:{drive_letter}")
                    self.logger.debug(f"Marked network drive for highlighting: {drive_letter} -> {network_path}")
                    
                    # Check if drive letter exists
                    if drive_letter in existing_volumes:
                        # Drive letter exists, it will be highlighted during refresh
                        pass
                    else:
                        # Drive letter doesn't exist, store for virtual entry
                        self.virtual_network_drives[drive_letter] = drive_config
                
                # Refresh volumes to show updated state with highlighting
                self.refresh_volumes()
                
                return True
                
            # If no specific configurations were found, return False
            self.logger.warning("No network drive configurations found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error marking network drives from configuration: {str(e)}")
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
