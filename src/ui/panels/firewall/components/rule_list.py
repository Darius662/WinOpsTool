"""Rule list component for firewall panel."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal

from ..tree_widget import RulesTree
from .button_bar import ButtonBar

class RuleList(QWidget):
    """Widget for displaying and managing firewall rules for a specific direction."""
    
    add_rule = pyqtSignal(str)
    edit_rule = pyqtSignal(str, dict)  # direction, rule_data
    delete_rule = pyqtSignal(str, str)  # direction, rule_name
    toggle_rule = pyqtSignal(str, str, bool)  # direction, rule_name, new_state
    refresh_rules = pyqtSignal(str)  # direction
    
    def __init__(self, direction, parent=None):
        """Initialize rule list.
        
        Args:
            direction: "inbound" or "outbound"
            parent: Parent widget
        """
        super().__init__(parent)
        self.direction = direction
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Set up the rule list UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create button bar
        self.button_bar = ButtonBar(self.direction, self)
        layout.addWidget(self.button_bar)
        
        # Create rules tree
        self.rules_tree = RulesTree(self)
        layout.addWidget(self.rules_tree)
        
    def setup_connections(self):
        """Set up signal/slot connections."""
        # Connect button bar signals
        self.button_bar.add_clicked.connect(self.add_rule)
        self.button_bar.edit_clicked.connect(self._on_edit_clicked)
        self.button_bar.delete_clicked.connect(self._on_delete_clicked)
        self.button_bar.toggle_clicked.connect(self._on_toggle_clicked)
        self.button_bar.refresh_clicked.connect(self.refresh_rules)
        
        # Connect tree selection signal
        self.rules_tree.itemSelectionChanged.connect(self._on_selection_changed)
        
    def _on_selection_changed(self):
        """Handle selection change in the rules tree."""
        has_selection = bool(self.rules_tree.selectedItems())
        self.button_bar.update_button_states(has_selection)
        
    def _on_edit_clicked(self, direction):
        """Handle edit button click.
        
        Args:
            direction: Rule direction
        """
        if self.rules_tree.selectedItems():
            item = self.rules_tree.selectedItems()[0]
            rule_data = self.rules_tree.get_rule(item)
            self.edit_rule.emit(direction, rule_data)
            
    def _on_delete_clicked(self, direction):
        """Handle delete button click.
        
        Args:
            direction: Rule direction
        """
        if self.rules_tree.selectedItems():
            item = self.rules_tree.selectedItems()[0]
            rule_name = item.text(0)
            self.delete_rule.emit(direction, rule_name)
            
    def _on_toggle_clicked(self, direction):
        """Handle toggle button click.
        
        Args:
            direction: Rule direction
        """
        if self.rules_tree.selectedItems():
            item = self.rules_tree.selectedItems()[0]
            rule = self.rules_tree.get_rule(item)
            self.toggle_rule.emit(direction, rule['name'], not rule['enabled'])
            
    def add_rules(self, rules):
        """Add rules to the tree.
        
        Args:
            rules: List of rule dictionaries
        """
        self.rules_tree.clear_rules()
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
            
    def update_rule_state(self, rule_name, enabled):
        """Update a rule's enabled state in the tree.
        
        Args:
            rule_name: Name of the rule to update
            enabled: New enabled state
        """
        # Find the item with the matching rule name
        for i in range(self.rules_tree.topLevelItemCount()):
            item = self.rules_tree.topLevelItem(i)
            if item.text(0) == rule_name:
                self.rules_tree.update_rule(item, enabled)
                break
