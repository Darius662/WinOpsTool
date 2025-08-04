"""Firewall rules management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QTabWidget, QMessageBox)
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import RulesTree
from .dialogs import AddRuleDialog
from .manager import FirewallManager
from .components.rule_list import RuleList

class FirewallPanel(BasePanel):
    """Panel for managing Windows Firewall rules."""
    
    def __init__(self, parent=None):
        """Initialize firewall panel.
        
        Args:
            parent: Parent widget
        """
        # Initialize manager before calling super().__init__ which will call setup_ui
        self.manager = FirewallManager()
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
        # Initialize imported config items
        self.imported_config_items = set()
        
        # Refresh rules initially after setup is complete
        self.refresh_rules("inbound")
        self.refresh_rules("outbound")
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create inbound and outbound rule lists
        self.inbound_rules = RuleList("inbound")
        self.outbound_rules = RuleList("outbound")
        
        # Add tabs
        self.tab_widget.addTab(self.inbound_rules, "Inbound Rules")
        self.tab_widget.addTab(self.outbound_rules, "Outbound Rules")
        
        # Add tab widget to panel
        self.add_widget(self.tab_widget)
        
    def setup_connections(self):
        """Set up signal/slot connections."""
        # Connect inbound rule list signals
        self.inbound_rules.add_rule.connect(self.add_rule)
        self.inbound_rules.edit_rule.connect(self.edit_rule)
        self.inbound_rules.delete_rule.connect(self.delete_rule)
        self.inbound_rules.toggle_rule.connect(self.toggle_rule)
        self.inbound_rules.refresh_rules.connect(self.refresh_rules)
        
        # Connect outbound rule list signals
        self.outbound_rules.add_rule.connect(self.add_rule)
        self.outbound_rules.edit_rule.connect(self.edit_rule)
        self.outbound_rules.delete_rule.connect(self.delete_rule)
        self.outbound_rules.toggle_rule.connect(self.toggle_rule)
        self.outbound_rules.refresh_rules.connect(self.refresh_rules)
        
        # Connect tab changed signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
    def _on_tab_changed(self, index):
        """Handle tab change event.
        
        Args:
            index: New tab index
        """
        # Refresh the rules in the newly selected tab
        direction = "inbound" if index == 0 else "outbound"
        self.refresh_rules(direction)
        
    def refresh_rules(self, direction):
        """Refresh the rules list for the specified direction.
        
        Args:
            direction: "inbound" or "outbound"
        """
        try:
            # Get rules for the specified direction
            rules = self.manager.get_rules(direction)
            
            # Update the appropriate rule list
            if direction == "inbound":
                self.inbound_rules.add_rules(rules)
            else:
                self.outbound_rules.add_rules(rules)
                
            self.logger.info(f"Refreshed {direction} firewall rules")
        except Exception as e:
            self.logger.error(f"Failed to refresh {direction} rules: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to refresh {direction} firewall rules")
            
    def add_rule(self, direction):
        """Add a new firewall rule.
        
        Args:
            direction: "inbound" or "outbound"
        """
        dialog = AddRuleDialog(self, direction)
        if dialog.exec():
            rule = dialog.get_rule()
            if self.manager.add_rule(**rule):
                self.refresh_rules(direction)
            else:
                QMessageBox.critical(self, "Error", "Failed to add firewall rule")
                
    def edit_rule(self, direction, rule_data):
        """Edit an existing firewall rule.
        
        Args:
            direction: "inbound" or "outbound"
            rule_data: Dictionary with rule properties
        """
        dialog = AddRuleDialog(self, direction, rule_data)
        if dialog.exec():
            # First delete the old rule
            if self.manager.delete_rule(rule_data['name']):
                # Then add the new rule with updated properties
                new_rule = dialog.get_rule()
                if self.manager.add_rule(**new_rule):
                    self.refresh_rules(direction)
                else:
                    QMessageBox.critical(self, "Error", "Failed to update firewall rule")
            else:
                QMessageBox.critical(self, "Error", "Failed to update firewall rule")
                
    def delete_rule(self, direction, rule_name):
        """Delete a firewall rule.
        
        Args:
            direction: "inbound" or "outbound"
            rule_name: Name of the rule to delete
        """
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete rule '{rule_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.manager.delete_rule(rule_name):
                self.refresh_rules(direction)
            else:
                QMessageBox.critical(self, "Error", "Failed to delete firewall rule")
                
    def toggle_rule(self, direction, rule_name, new_state):
        """Toggle enabled state of a rule.
        
        Args:
            direction: "inbound" or "outbound"
            rule_name: Name of the rule to toggle
            new_state: New enabled state
        """
        if self.manager.set_rule_enabled(rule_name, new_state):
            # Update the rule in the appropriate list
            if direction == "inbound":
                self.inbound_rules.update_rule_state(rule_name, new_state)
            else:
                self.outbound_rules.update_rule_state(rule_name, new_state)
        else:
            QMessageBox.critical(self, "Error", "Failed to toggle firewall rule")
            
    def mark_config_items(self, config):
        """Mark items from configuration for highlighting without applying changes.
        
        This method identifies and marks firewall rules from the configuration
        that would be modified by apply_config(), but does not actually
        apply any changes to the system. Items will be visually highlighted in the UI.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if items were marked successfully, False otherwise
        """
        self.logger.info("Marking firewall rules from configuration for highlighting")
        
        # Clear previous imported items
        self.imported_config_items.clear()
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Check if firewall_rules section exists
            if 'firewall_rules' not in config:
                self.logger.warning("No firewall rules in configuration")
                return False
                
            firewall_config = config['firewall_rules']
            
            # Process inbound rules
            if 'inbound' in firewall_config and isinstance(firewall_config['inbound'], list):
                self.logger.info(f"Marking {len(firewall_config['inbound'])} inbound rules for highlighting")
                
                for rule in firewall_config['inbound']:
                    if not isinstance(rule, dict) or 'name' not in rule:
                        self.logger.warning("Skipping invalid rule")
                        continue
                        
                    # Mark this rule as imported from config for highlighting
                    self.mark_as_imported_config(f"firewall:inbound:{rule['name']}")
                    self.logger.debug(f"Marked inbound rule for highlighting: {rule['name']}")
                    
                    # Add virtual entry for this rule if it doesn't exist
                    self.add_virtual_rule("inbound", rule)
            
            # Process outbound rules
            if 'outbound' in firewall_config and isinstance(firewall_config['outbound'], list):
                self.logger.info(f"Marking {len(firewall_config['outbound'])} outbound rules for highlighting")
                
                for rule in firewall_config['outbound']:
                    if not isinstance(rule, dict) or 'name' not in rule:
                        self.logger.warning("Skipping invalid rule")
                        continue
                        
                    # Mark this rule as imported from config for highlighting
                    self.mark_as_imported_config(f"firewall:outbound:{rule['name']}")
                    self.logger.debug(f"Marked outbound rule for highlighting: {rule['name']}")
                    
                    # Add virtual entry for this rule if it doesn't exist
                    self.add_virtual_rule("outbound", rule)
            
            # Refresh the rules to show updated state with highlighting
            self.refresh_rules("inbound")
            self.refresh_rules("outbound")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error marking firewall rules from configuration: {str(e)}")
            return False
    
    def add_virtual_rule(self, direction, rule):
        """Add a virtual firewall rule that doesn't exist in the system yet.
        
        Args:
            direction: "inbound" or "outbound"
            rule: Dictionary containing rule properties
        """
        try:
            # Get existing rules
            existing_rules = self.manager.get_rules(direction)
            rule_exists = any(r['name'] == rule['name'] for r in existing_rules)
            
            # Only add virtual entry if rule doesn't exist
            if not rule_exists:
                self.logger.debug(f"Adding virtual entry for {direction} rule: {rule['name']}")
                
                # Add virtual entry to the appropriate rule list
                if direction == "inbound":
                    self.inbound_rules.add_virtual_rule(rule)
                else:
                    self.outbound_rules.add_virtual_rule(rule)
                    
        except Exception as e:
            self.logger.error(f"Error adding virtual firewall rule: {str(e)}")
    
    def apply_config(self, config):
        """Apply configuration to the panel.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if configuration was applied successfully, False otherwise
        """
        self.logger.info("Applying firewall rules configuration")
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            success = False
            
            # Process firewall rules configuration
            if 'firewall_rules' not in config:
                self.logger.warning("No firewall rules in configuration")
                return False
                
            firewall_config = config['firewall_rules']
            
            # Process inbound rules
            if 'inbound' in firewall_config and isinstance(firewall_config['inbound'], list):
                self.logger.info(f"Applying {len(firewall_config['inbound'])} inbound rules")
                
                for rule in firewall_config['inbound']:
                    if not isinstance(rule, dict) or 'name' not in rule:
                        self.logger.warning("Skipping invalid rule")
                        continue
                        
                    # Check if rule exists
                    existing_rules = self.manager.get_rules("inbound")
                    rule_exists = any(r['name'] == rule['name'] for r in existing_rules)
                    
                    if rule_exists:
                        # Delete existing rule first
                        self.logger.info(f"Updating existing rule: {rule['name']}")
                        self.manager.delete_rule(rule['name'])
                    else:
                        self.logger.info(f"Adding new rule: {rule['name']}")
                        
                    # Add rule with configuration
                    result = self.manager.add_rule(**rule)
                    if not result:
                        self.logger.warning(f"Failed to add rule: {rule['name']}")
                    
                    success = success or result
            
            # Process outbound rules
            if 'outbound' in firewall_config and isinstance(firewall_config['outbound'], list):
                self.logger.info(f"Applying {len(firewall_config['outbound'])} outbound rules")
                
                for rule in firewall_config['outbound']:
                    if not isinstance(rule, dict) or 'name' not in rule:
                        self.logger.warning("Skipping invalid rule")
                        continue
                        
                    # Check if rule exists
                    existing_rules = self.manager.get_rules("outbound")
                    rule_exists = any(r['name'] == rule['name'] for r in existing_rules)
                    
                    if rule_exists:
                        # Delete existing rule first
                        self.logger.info(f"Updating existing rule: {rule['name']}")
                        self.manager.delete_rule(rule['name'])
                    else:
                        self.logger.info(f"Adding new rule: {rule['name']}")
                        
                    # Add rule with configuration
                    result = self.manager.add_rule(**rule)
                    if not result:
                        self.logger.warning(f"Failed to add rule: {rule['name']}")
                    
                    success = success or result
            
            # Refresh the rules to show updated state
            self.refresh_rules("inbound")
            self.refresh_rules("outbound")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error applying firewall configuration: {str(e)}")
            return False
            
    def export_config(self):
        """Export panel configuration.
        
        Returns:
            dict: Dictionary containing panel configuration
        """
        self.logger.info("Exporting firewall rules configuration")
        
        try:
            # Get current firewall rules
            inbound_rules = self.manager.get_rules("inbound")
            outbound_rules = self.manager.get_rules("outbound")
            
            # Create configuration dictionary
            config = {
                'firewall_rules': {
                    'inbound': inbound_rules,
                    'outbound': outbound_rules
                }
            }
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error exporting firewall configuration: {str(e)}")
            return {'firewall_rules': {'inbound': [], 'outbound': []}}
