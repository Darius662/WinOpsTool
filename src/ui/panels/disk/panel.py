"""Windows Disk management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLineEdit, QLabel, QTabWidget)
from PyQt6.QtCore import QTimer
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import DisksTree, VolumesTree
from .dialogs import DiskPerformanceDialog, VolumeInfoDialog
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
            
            for vol in volumes:
                self.volumes_tree.add_volume(
                    vol['mountpoint'],
                    vol['label'],
                    vol['type'],
                    vol['fstype'],
                    vol['total'],
                    vol['used'],
                    vol['free']
                )
                
            # Reapply filter if search text exists
            if self.volume_search.text():
                self.filter_volumes(self.volume_search.text())
                
            # Restore selection if volume still exists
            if selected_mountpoint:
                item = self.volumes_tree.find_volume(selected_mountpoint)
                if item:
                    item.setSelected(True)
                    
            self.logger.debug("Refreshed volumes")
        except Exception as e:
            self.logger.error(f"Failed to refresh volumes: {str(e)}")
            
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
