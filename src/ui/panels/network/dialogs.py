"""Dialogs for network interface details."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                          QDialogButtonBox, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class InterfaceStatsDialog(QDialog):
    """Dialog for showing detailed network interface statistics."""
    
    def __init__(self, parent=None, name="", stats=None):
        """Initialize dialog.
        
        Args:
            parent: Parent widget
            name: Interface name
            stats: Interface statistics dictionary
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.name = name
        self.stats = stats or {}
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle(f"Interface Statistics - {self.name}")
        self.resize(400, 400)
        layout = QVBoxLayout(self)
        
        # Stats table
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Statistic", "Value"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        
        # Add stats rows
        self._add_stat("Speed", f"{self.stats.get('speed', 0)} Mbps")
        self._add_stat("MTU", str(self.stats.get('mtu', 0)))
        self._add_stat("Status", "Up" if self.stats.get('up', False) else "Down")
        
        # Traffic
        bytes_sent = self.stats.get('bytes_sent', 0)
        bytes_recv = self.stats.get('bytes_recv', 0)
        mb_sent = bytes_sent / (1024 * 1024)
        mb_recv = bytes_recv / (1024 * 1024)
        self._add_stat("Bytes Sent", f"{bytes_sent:,} ({mb_sent:.1f} MB)")
        self._add_stat("Bytes Received", f"{bytes_recv:,} ({mb_recv:.1f} MB)")
        
        # Packets
        self._add_stat("Packets Sent", f"{self.stats.get('packets_sent', 0):,}")
        self._add_stat("Packets Received", f"{self.stats.get('packets_recv', 0):,}")
        
        # Errors
        self._add_stat("Input Errors", f"{self.stats.get('errin', 0):,}")
        self._add_stat("Output Errors", f"{self.stats.get('errout', 0):,}")
        self._add_stat("Input Drops", f"{self.stats.get('dropin', 0):,}")
        self._add_stat("Output Drops", f"{self.stats.get('dropout', 0):,}")
        
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
