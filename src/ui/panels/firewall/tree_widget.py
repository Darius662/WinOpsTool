"""Tree widget for firewall rules."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class RulesTree(QTreeWidget):
    """Tree widget for displaying firewall rules."""
    
    def __init__(self, parent=None):
        """Initialize rules tree.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the tree widget UI."""
        # Set up columns
        self.setHeaderLabels([
            "Name",
            "Enabled",
            "Direction",
            "Action",
            "Protocol",
            "Local Ports",
            "Remote Ports",
            "Program"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 200)  # Name
        self.setColumnWidth(1, 70)   # Enabled
        self.setColumnWidth(2, 80)   # Direction
        self.setColumnWidth(3, 70)   # Action
        self.setColumnWidth(4, 70)   # Protocol
        self.setColumnWidth(5, 100)  # Local Ports
        self.setColumnWidth(6, 100)  # Remote Ports
        self.setColumnWidth(7, 300)  # Program
        
        # Enable sorting and alternating row colors
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def add_rule(self, name, enabled, direction, action, protocol,
                local_ports="", remote_ports="", program=""):
        """Add a firewall rule to the tree.
        
        Args:
            name: Rule name
            enabled: Whether rule is enabled
            direction: "Inbound" or "Outbound"
            action: "Allow" or "Block"
            protocol: Protocol
            local_ports: Local port(s)
            remote_ports: Remote port(s)
            program: Program path
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        item = QTreeWidgetItem([
            name,
            "Yes" if enabled else "No",
            direction,
            action,
            protocol,
            local_ports,
            remote_ports,
            program
        ])
        self.addTopLevelItem(item)
        return item
        
    def update_rule(self, item, enabled=None):
        """Update a firewall rule in the tree.
        
        Args:
            item: QTreeWidgetItem to update
            enabled: New enabled state (optional)
        """
        if enabled is not None:
            item.setText(1, "Yes" if enabled else "No")
            
    def get_rule(self, item):
        """Get rule details from tree item.
        
        Args:
            item: QTreeWidgetItem to get details from
            
        Returns:
            dict: Rule properties
        """
        return {
            'name': item.text(0),
            'enabled': item.text(1) == "Yes",
            'direction': item.text(2),
            'action': item.text(3),
            'protocol': item.text(4),
            'local_ports': item.text(5),
            'remote_ports': item.text(6),
            'program': item.text(7)
        }
        
    def clear_rules(self):
        """Clear all rules from the tree."""
        self.clear()
