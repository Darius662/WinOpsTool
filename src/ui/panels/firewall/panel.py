"""Firewall rules management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QComboBox, QMessageBox)
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import RulesTree
from .dialogs import AddRuleDialog
from .manager import FirewallManager

class FirewallPanel(BasePanel):
    """Panel for managing Windows Firewall rules."""
    
    def __init__(self, parent=None):
        """Initialize firewall panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = FirewallManager()
        self.refresh_rules()
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Filter controls
        filter_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Rules", "Inbound", "Outbound"])
        filter_layout.addWidget(self.filter_combo)
        
        # Action buttons
        self.add_button = QPushButton("Add Rule")
        filter_layout.addWidget(self.add_button)
        
        self.delete_button = QPushButton("Delete Rule")
        filter_layout.addWidget(self.delete_button)
        
        self.toggle_button = QPushButton("Enable/Disable")
        filter_layout.addWidget(self.toggle_button)
        
        self.refresh_button = QPushButton("Refresh")
        filter_layout.addWidget(self.refresh_button)
        
        self.add_layout(filter_layout)
        
        # Rules tree
        self.rules_tree = RulesTree()
        self.add_widget(self.rules_tree)
        
        # Initial button state
        self.update_buttons()
        
    def setup_connections(self):
        """Set up signal/slot connections."""
        self.filter_combo.currentTextChanged.connect(self.refresh_rules)
        self.add_button.clicked.connect(self.add_rule)
        self.delete_button.clicked.connect(self.delete_rule)
        self.toggle_button.clicked.connect(self.toggle_rule)
        self.refresh_button.clicked.connect(self.refresh_rules)
        self.rules_tree.itemSelectionChanged.connect(self.update_buttons)
        
    def update_buttons(self):
        """Update button enabled states based on selection."""
        has_selection = bool(self.rules_tree.selectedItems())
        self.delete_button.setEnabled(has_selection)
        self.toggle_button.setEnabled(has_selection)
        
    def refresh_rules(self):
        """Refresh the rules list."""
        try:
            # Get filter type
            filter_text = self.filter_combo.currentText()
            filter_type = filter_text.lower() if filter_text != "All Rules" else None
            
            # Clear and repopulate tree
            self.rules_tree.clear_rules()
            rules = self.manager.get_rules(filter_type)
            
            for rule in rules:
                self.rules_tree.add_rule(
                    rule['name'],
                    rule['enabled'],
                    rule['direction'],
                    rule['action'],
                    rule['protocol'],
                    rule['local_ports'],
                    rule['remote_ports'],
                    rule['program']
                )
                
            self.logger.info("Refreshed firewall rules")
        except Exception as e:
            self.logger.error(f"Failed to refresh rules: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to refresh firewall rules")
            
    def add_rule(self):
        """Add a new firewall rule."""
        dialog = AddRuleDialog(self)
        if dialog.exec():
            rule = dialog.get_rule()
            if self.manager.add_rule(**rule):
                self.refresh_rules()
            else:
                QMessageBox.critical(self, "Error", "Failed to add firewall rule")
                
    def delete_rule(self):
        """Delete selected firewall rule."""
        item = self.rules_tree.selectedItems()[0]
        name = item.text(0)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete rule '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.manager.delete_rule(name):
                self.refresh_rules()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete firewall rule")
                
    def toggle_rule(self):
        """Toggle enabled state of selected rule."""
        item = self.rules_tree.selectedItems()[0]
        rule = self.rules_tree.get_rule(item)
        
        if self.manager.set_rule_enabled(rule['name'], not rule['enabled']):
            self.rules_tree.update_rule(item, not rule['enabled'])
        else:
            QMessageBox.critical(self, "Error", "Failed to toggle firewall rule")
