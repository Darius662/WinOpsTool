"""Windows Firewall Management Panel."""
import win32com.client
from PyQt6.QtWidgets import (QTreeWidget, QTreeWidgetItem, QPushButton, QHBoxLayout,
                          QMessageBox, QInputDialog, QLineEdit, QComboBox, QSpinBox,
                          QFormLayout, QDialog, QDialogButtonBox, QWidget, QVBoxLayout)
from PyQt6.QtCore import Qt
from ..base.base_panel import BasePanel
from src.core.logger import setup_logger

class AddRuleDialog(QDialog):
    """Dialog for adding a new firewall rule."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Firewall Rule")
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Rule name
        self.name_edit = QLineEdit()
        form_layout.addRow("Rule Name:", self.name_edit)
        
        # Direction
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["Inbound", "Outbound"])
        form_layout.addRow("Direction:", self.direction_combo)
        
        # Action
        self.action_combo = QComboBox()
        self.action_combo.addItems(["Allow", "Block"])
        form_layout.addRow("Action:", self.action_combo)
        
        # Protocol
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["TCP", "UDP", "Any"])
        form_layout.addRow("Protocol:", self.protocol_combo)
        
        # Local port
        self.local_port_edit = QLineEdit()
        self.local_port_edit.setPlaceholderText("e.g., 80,443 or 1000-2000")
        form_layout.addRow("Local Ports:", self.local_port_edit)
        
        # Remote port
        self.remote_port_edit = QLineEdit()
        self.remote_port_edit.setPlaceholderText("e.g., 80,443 or 1000-2000")
        form_layout.addRow("Remote Ports:", self.remote_port_edit)
        
        # Program
        self.program_edit = QLineEdit()
        self.program_edit.setPlaceholderText("e.g., C:\\Program Files\\App\\app.exe")
        form_layout.addRow("Program:", self.program_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_rule_data(self):
        """Get the rule data from the dialog."""
        return {
            "name": self.name_edit.text(),
            "direction": self.direction_combo.currentText(),
            "action": self.action_combo.currentText(),
            "protocol": self.protocol_combo.currentText(),
            "local_ports": self.local_port_edit.text(),
            "remote_ports": self.remote_port_edit.text(),
            "program": self.program_edit.text()
        }

class FirewallPanel(BasePanel):
    """Panel for managing Windows Firewall rules."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
    def setup_ui(self):
        """Initialize the UI components."""
        # Initialize firewall
        self.firewall = win32com.client.Dispatch("HNetCfg.FwPolicy2")
        
        # Rules tree
        self.rules_tree = QTreeWidget()
        self.rules_tree.setHeaderLabels([
            "Name",
            "Enabled",
            "Direction",
            "Action",
            "Protocol",
            "Local Ports",
            "Remote Ports",
            "Program"
        ])
        self.rules_tree.setAlternatingRowColors(True)
        for i, width in enumerate([200, 70, 80, 70, 70, 100, 100, 300]):
            self.rules_tree.setColumnWidth(i, width)
            
        self.add_widget(self.rules_tree)
        
        # Filter
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All Rules",
            "Inbound Only",
            "Outbound Only",
            "Enabled Only",
            "Disabled Only"
        ])
        self.filter_combo.currentTextChanged.connect(self.refresh_rules)
        self.add_widget(self.filter_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Rule")
        self.delete_btn = QPushButton("Delete Rule")
        self.enable_btn = QPushButton("Enable Rule")
        self.disable_btn = QPushButton("Disable Rule")
        self.refresh_btn = QPushButton("Refresh")
        
        for btn in [self.add_btn, self.delete_btn, self.enable_btn,
                   self.disable_btn, self.refresh_btn]:
            button_layout.addWidget(btn)
            
        self.add_layout(button_layout)
        
        # Connect signals
        self.add_btn.clicked.connect(self.add_rule)
        self.delete_btn.clicked.connect(self.delete_rule)
        self.enable_btn.clicked.connect(self.enable_rule)
        self.disable_btn.clicked.connect(self.disable_rule)
        self.refresh_btn.clicked.connect(self.refresh_rules)
        
        # Initial load
        self.refresh_rules()
        
    def refresh_rules(self):
        """Refresh the firewall rules list."""
        try:
            self.rules_tree.clear()
            
            rules = self.firewall.Rules
            filter_text = self.filter_combo.currentText()
            
            for rule in rules:
                try:
                    # Apply filter
                    if filter_text == "Inbound Only" and rule.Direction != 1:  # NET_FW_RULE_DIRECTION_IN
                        continue
                    elif filter_text == "Outbound Only" and rule.Direction != 2:  # NET_FW_RULE_DIRECTION_OUT
                        continue
                    elif filter_text == "Enabled Only" and not rule.Enabled:
                        continue
                    elif filter_text == "Disabled Only" and rule.Enabled:
                        continue
                        
                    # Convert protocol number to string
                    protocol = str(rule.Protocol)
                    if protocol == "6":
                        protocol = "TCP"
                    elif protocol == "17":
                        protocol = "UDP"
                    elif protocol == "256":
                        protocol = "Any"
                    
                    item = QTreeWidgetItem([
                        rule.Name,
                        "Yes" if rule.Enabled else "No",
                        "Inbound" if rule.Direction == 1 else "Outbound",
                        "Allow" if rule.Action == 1 else "Block",
                        protocol,
                        rule.LocalPorts if rule.LocalPorts else "*",
                        rule.RemotePorts if rule.RemotePorts else "*",
                        rule.ApplicationName if rule.ApplicationName else "*"
                    ])
                    self.rules_tree.addTopLevelItem(item)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to get info for rule {rule.Name}: {str(e)}")
                    
            self.rules_tree.sortItems(0, Qt.SortOrder.AscendingOrder)
            
        except Exception as e:
            self.logger.error(f"Failed to refresh firewall rules: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to refresh firewall rules: {str(e)}")
            
    def add_rule(self):
        """Add a new firewall rule."""
        try:
            dialog = AddRuleDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_rule_data()
                
                rule = win32com.client.Dispatch("HNetCfg.FWRule")
                rule.Name = data["name"]
                rule.Direction = 1 if data["direction"] == "Inbound" else 2
                rule.Action = 1 if data["action"] == "Allow" else 0
                rule.Protocol = data["protocol"] if data["protocol"] != "Any" else "*"
                rule.LocalPorts = data["local_ports"]
                rule.RemotePorts = data["remote_ports"]
                rule.ApplicationName = data["program"]
                rule.Enabled = True
                
                self.firewall.Rules.Add(rule)
                self.logger.info(f"Added firewall rule: {data['name']}")
                self.refresh_rules()
                
        except Exception as e:
            self.logger.error(f"Failed to add firewall rule: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add firewall rule: {str(e)}")
            
    def delete_rule(self):
        """Delete the selected firewall rule."""
        try:
            current_item = self.rules_tree.currentItem()
            if not current_item:
                return
                
            rule_name = current_item.text(0)
            
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete the firewall rule '{rule_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.firewall.Rules.Remove(rule_name)
                self.logger.info(f"Deleted firewall rule: {rule_name}")
                self.refresh_rules()
                
        except Exception as e:
            self.logger.error(f"Failed to delete firewall rule: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to delete firewall rule: {str(e)}")
            
    def enable_rule(self):
        """Enable the selected firewall rule."""
        try:
            current_item = self.rules_tree.currentItem()
            if not current_item:
                return
                
            rule_name = current_item.text(0)
            rule = self.firewall.Rules.Item(rule_name)
            rule.Enabled = True
            
            self.logger.info(f"Enabled firewall rule: {rule_name}")
            self.refresh_rules()
            
        except Exception as e:
            self.logger.error(f"Failed to enable firewall rule: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to enable firewall rule: {str(e)}")
            
    def disable_rule(self):
        """Disable the selected firewall rule."""
        try:
            current_item = self.rules_tree.currentItem()
            if not current_item:
                return
                
            rule_name = current_item.text(0)
            rule = self.firewall.Rules.Item(rule_name)
            rule.Enabled = False
            
            self.logger.info(f"Disabled firewall rule: {rule_name}")
            self.refresh_rules()
            
        except Exception as e:
            self.logger.error(f"Failed to disable firewall rule: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to disable firewall rule: {str(e)}")
            
    def setup_connections(self):
        """Set up signal/slot connections."""
        pass  # All connections are set up in setup_ui
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed."""
        pass  # No cleanup needed for this panel
