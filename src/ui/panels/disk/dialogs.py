"""Dialogs for disk and volume information."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                          QDialogButtonBox, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class DiskPerformanceDialog(QDialog):
    """Dialog for showing disk performance metrics."""
    
    def __init__(self, parent=None, name="", metrics=None):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
            name: Disk name
            metrics: Performance metrics dictionary
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.name = name
        self.metrics = metrics or {}
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle(f"Disk Performance - {self.name}")
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        
        # Stats table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        
        # Add metrics rows
        # Read operations
        read_count = self.metrics.get('read_count', 0)
        self._add_stat("Read Operations", f"{read_count:,}")
        
        # Write operations
        write_count = self.metrics.get('write_count', 0)
        self._add_stat("Write Operations", f"{write_count:,}")
        
        # Read bytes
        read_bytes = self.metrics.get('read_bytes', 0)
        read_mb = read_bytes / (1024 * 1024)
        self._add_stat("Data Read", f"{read_bytes:,} bytes ({read_mb:.1f} MB)")
        
        # Write bytes
        write_bytes = self.metrics.get('write_bytes', 0)
        write_mb = write_bytes / (1024 * 1024)
        self._add_stat("Data Written", f"{write_bytes:,} bytes ({write_mb:.1f} MB)")
        
        # Read time
        read_time = self.metrics.get('read_time', 0)
        self._add_stat("Read Time", f"{read_time:,} ms")
        
        # Write time
        write_time = self.metrics.get('write_time', 0)
        self._add_stat("Write Time", f"{write_time:,} ms")
        
        # Average read speed
        if read_time > 0:
            read_speed = (read_bytes / 1024 / 1024) / (read_time / 1000)  # MB/s
            self._add_stat("Average Read Speed", f"{read_speed:.1f} MB/s")
            
        # Average write speed
        if write_time > 0:
            write_speed = (write_bytes / 1024 / 1024) / (write_time / 1000)  # MB/s
            self._add_stat("Average Write Speed", f"{write_speed:.1f} MB/s")
            
        # Adjust table size
        self.table.resizeColumnsToContents()
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def _add_stat(self, name, value):
        """Add a statistic row to the table.
        
        Args:
            name: Statistic name
            value: Statistic value
        """
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        name_item = QTableWidgetItem(name)
        value_item = QTableWidgetItem(value)
        
        # Make items read-only
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        
        self.table.setItem(row, 0, name_item)
        self.table.setItem(row, 1, value_item)


class VolumeInfoDialog(QDialog):
    """Dialog for showing detailed volume information."""
    
    def __init__(self, parent=None, mountpoint="", info=None):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
            mountpoint: Volume mountpoint
            info: Volume information dictionary
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.mountpoint = mountpoint
        self.info = info or {}
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle(f"Volume Information - {self.mountpoint}")
        self.resize(400, 400)
        layout = QVBoxLayout(self)
        
        # Stats table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Property", "Value"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        
        # Add info rows
        self._add_stat("Volume Name", self.info.get('volume_name', ""))
        self._add_stat("Serial Number", f"{self.info.get('serial_number', 0):X}")
        
        # Space information
        total = self.info.get('total', 0)
        used = self.info.get('used', 0)
        free = self.info.get('free', 0)
        
        total_gb = total / (1024 * 1024 * 1024)
        used_gb = used / (1024 * 1024 * 1024)
        free_gb = free / (1024 * 1024 * 1024)
        
        self._add_stat("Total Space", f"{total:,} bytes ({total_gb:.1f} GB)")
        self._add_stat("Used Space", f"{used:,} bytes ({used_gb:.1f} GB)")
        self._add_stat("Free Space", f"{free:,} bytes ({free_gb:.1f} GB)")
        self._add_stat("Used Percentage", f"{self.info.get('percent', 0):.1f}%")
        
        # Filesystem information
        self._add_stat("Filesystem", self.info.get('filesystem', ""))
        self._add_stat("Max Path Length", str(self.info.get('max_path_length', 0)))
        
        # Flags
        flags = self.info.get('flags', 0)
        flag_list = []
        if flags & 0x00000001: flag_list.append("Case Preserved")
        if flags & 0x00000002: flag_list.append("Case Sensitive")
        if flags & 0x00000004: flag_list.append("Unicode")
        if flags & 0x00000008: flag_list.append("ACLs")
        if flags & 0x00000010: flag_list.append("File Compression")
        if flags & 0x00000020: flag_list.append("Quotas")
        if flags & 0x00000040: flag_list.append("Sparse Files")
        if flags & 0x00000080: flag_list.append("Reparse Points")
        if flags & 0x00000100: flag_list.append("Remote Storage")
        if flags & 0x00008000: flag_list.append("Volume is Compressed")
        if flags & 0x00010000: flag_list.append("Object IDs")
        if flags & 0x00020000: flag_list.append("Encryption")
        
        self._add_stat("Features", "\n".join(flag_list))
        
        # Adjust table size
        self.table.resizeColumnsToContents()
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def _add_stat(self, name, value):
        """Add a statistic row to the table.
        
        Args:
            name: Statistic name
            value: Statistic value
        """
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        name_item = QTableWidgetItem(name)
        value_item = QTableWidgetItem(value)
        
        # Make items read-only
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        
        self.table.setItem(row, 0, name_item)
        self.table.setItem(row, 1, value_item)
