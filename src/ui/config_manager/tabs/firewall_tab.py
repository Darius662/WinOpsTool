"""Firewall configuration tab."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox, QComboBox)
from .base_tab import BaseConfigTab

class FirewallTab(BaseConfigTab):
    """Tab for configuring Windows Firewall rules."""
    
    # Rule actions
    ACTIONS = ["Allow", "Block"]
    
    # Rule directions
    DIRECTIONS = ["Inbound", "Outbound"]
    
    # Rule protocols
    PROTOCOLS = ["TCP", "UDP", "Any"]
    
    def __init__(self, config_handler):
        super().__init__(config_handler, "firewall")
        
    def setup_ui(self):
        """Set up the tab's user interface."""
        # Rules tree
        tree_label = QLabel("Firewall Rules")
        self.layout.addWidget(tree_label)
        
        self.rules_tree = QTreeWidget()
        self.rules_tree.setHeaderLabels([
            "Name",
            "Direction",
            "Action",
            "Protocol",
            "Local Port",
            "Remote Port",
            "Program"
        ])
        self.rules_tree.setColumnWidth(0, 200)
        self.layout.addWidget(self.rules_tree)
        
        # Input fields
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        # Rule name
        name_layout = QHBoxLayout()
        name_label = QLabel("Rule Name:")
        name_layout.addWidget(name_label)
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        input_layout.addLayout(name_layout)
        
        # Direction
        direction_layout = QHBoxLayout()
        direction_label = QLabel("Direction:")
        direction_layout.addWidget(direction_label)
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(self.DIRECTIONS)
        direction_layout.addWidget(self.direction_combo)
        input_layout.addLayout(direction_layout)
        
        # Action
        action_layout = QHBoxLayout()
        action_label = QLabel("Action:")
        action_layout.addWidget(action_label)
        self.action_combo = QComboBox()
        self.action_combo.addItems(self.ACTIONS)
        action_layout.addWidget(self.action_combo)
        input_layout.addLayout(action_layout)
        
        # Protocol
        protocol_layout = QHBoxLayout()
        protocol_label = QLabel("Protocol:")
        protocol_layout.addWidget(protocol_label)
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(self.PROTOCOLS)
        protocol_layout.addWidget(self.protocol_combo)
        input_layout.addLayout(protocol_layout)
        
        # Local port
        local_port_layout = QHBoxLayout()
        local_port_label = QLabel("Local Port:")
        local_port_layout.addWidget(local_port_label)
        self.local_port_edit = QLineEdit()
        self.local_port_edit.setPlaceholderText("Port number or range (e.g., 80 or 80-90)")
        local_port_layout.addWidget(self.local_port_edit)
        input_layout.addLayout(local_port_layout)
        
        # Remote port
        remote_port_layout = QHBoxLayout()
        remote_port_label = QLabel("Remote Port:")
        remote_port_layout.addWidget(remote_port_label)
        self.remote_port_edit = QLineEdit()
        self.remote_port_edit.setPlaceholderText("Port number or range (e.g., 80 or 80-90)")
        remote_port_layout.addWidget(self.remote_port_edit)
        input_layout.addLayout(remote_port_layout)
        
        # Program
        program_layout = QHBoxLayout()
        program_label = QLabel("Program:")
        program_layout.addWidget(program_label)
        self.program_edit = QLineEdit()
        self.program_edit.setPlaceholderText("Full path to program (optional)")
        program_layout.addWidget(self.program_edit)
        input_layout.addLayout(program_layout)
        
        self.layout.addWidget(input_widget)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Rule")
        add_button.clicked.connect(self.add_rule)
        buttons_layout.addWidget(add_button)
        
        delete_button = QPushButton("Delete Rule")
        delete_button.clicked.connect(self.delete_rule)
        buttons_layout.addWidget(delete_button)
        
        self.layout.addLayout(buttons_layout)
        
    def add_rule(self):
        """Add a firewall rule to the tree."""
        name = self.name_edit.text().strip()
        direction = self.direction_combo.currentText()
        action = self.action_combo.currentText()
        protocol = self.protocol_combo.currentText()
        local_port = self.local_port_edit.text().strip()
        remote_port = self.remote_port_edit.text().strip()
        program = self.program_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Warning", "Rule name is required.")
            return
            
        # Validate ports if specified
        if local_port and not self._validate_port(local_port):
            QMessageBox.warning(self, "Warning", "Invalid local port specification.")
            return
            
        if remote_port and not self._validate_port(remote_port):
            QMessageBox.warning(self, "Warning", "Invalid remote port specification.")
            return
            
        item = QTreeWidgetItem([
            name,
            direction,
            action,
            protocol,
            local_port,
            remote_port,
            program
        ])
        self.rules_tree.addTopLevelItem(item)
        
        # Clear input fields
        self.name_edit.clear()
        self.local_port_edit.clear()
        self.remote_port_edit.clear()
        self.program_edit.clear()
        
        self.update_config_from_ui()
        
    def delete_rule(self):
        """Delete selected firewall rule."""
        item = self.rules_tree.currentItem()
        if item:
            self.rules_tree.takeTopLevelItem(
                self.rules_tree.indexOfTopLevelItem(item)
            )
            self.update_config_from_ui()
            
    def _validate_port(self, port_str):
        """Validate port number or range."""
        try:
            if "-" in port_str:
                start, end = map(int, port_str.split("-"))
                return 1 <= start <= 65535 and 1 <= end <= 65535 and start <= end
            else:
                port = int(port_str)
                return 1 <= port <= 65535
        except ValueError:
            return False
            
    def update_config_from_ui(self):
        """Update configuration from UI elements."""
        config = {
            "inbound": [],
            "outbound": []
        }
        
        for i in range(self.rules_tree.topLevelItemCount()):
            item = self.rules_tree.topLevelItem(i)
            rule = {
                "name": item.text(0),
                "action": item.text(2).lower(),
                "protocol": item.text(3).lower(),
                "local_port": item.text(4),
                "remote_port": item.text(5),
                "program": item.text(6)
            }
            
            # Add to appropriate direction list
            if item.text(1).lower() == "inbound":
                config["inbound"].append(rule)
            else:
                config["outbound"].append(rule)
                
        self.update_config(config)
        
    def on_config_changed(self):
        """Handle configuration changes."""
        config = self.get_config()
        
        # Clear existing items
        self.rules_tree.clear()
        
        # Add inbound rules
        for rule in config.get("inbound", []):
            item = QTreeWidgetItem([
                rule["name"],
                "Inbound",
                rule["action"].capitalize(),
                rule["protocol"].upper(),
                rule.get("local_port", ""),
                rule.get("remote_port", ""),
                rule.get("program", "")
            ])
            self.rules_tree.addTopLevelItem(item)
            
        # Add outbound rules
        for rule in config.get("outbound", []):
            item = QTreeWidgetItem([
                rule["name"],
                "Outbound",
                rule["action"].capitalize(),
                rule["protocol"].upper(),
                rule.get("local_port", ""),
                rule.get("remote_port", ""),
                rule.get("program", "")
            ])
            self.rules_tree.addTopLevelItem(item)
