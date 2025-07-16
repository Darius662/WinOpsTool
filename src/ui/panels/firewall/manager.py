"""Windows Firewall management."""
import win32com.client
from src.core.logger import setup_logger

class FirewallManager:
    """Manager for Windows Firewall rules."""
    
    def __init__(self):
        """Initialize firewall manager."""
        self.logger = setup_logger(self.__class__.__name__)
        self.firewall = win32com.client.Dispatch("HNetCfg.FwPolicy2")
        
    def get_rules(self, filter_type=None):
        """Get list of firewall rules.
        
        Args:
            filter_type: Optional filter type ("inbound", "outbound", or None for all)
            
        Returns:
            list: List of rule dictionaries with properties
        """
        try:
            rules = []
            for rule in self.firewall.Rules:
                # Convert rule direction
                direction = "Inbound" if rule.Direction == 1 else "Outbound"
                
                # Skip if doesn't match filter
                if filter_type and direction.lower() != filter_type.lower():
                    continue
                    
                # Convert protocol number to string
                protocol = str(rule.Protocol)
                if protocol == "*" or protocol == "0":
                    protocol = "Any"
                elif protocol == "6":
                    protocol = "TCP"
                elif protocol == "17":
                    protocol = "UDP"
                elif protocol == "1":
                    protocol = "ICMP"
                
                rules.append({
                    'name': rule.Name,
                    'enabled': rule.Enabled,
                    'direction': direction,
                    'action': "Allow" if rule.Action == 1 else "Block",
                    'protocol': protocol,
                    'local_ports': rule.LocalPorts or "",
                    'remote_ports': rule.RemotePorts or "",
                    'program': rule.ApplicationName or ""
                })
            return rules
        except Exception as e:
            self.logger.error(f"Failed to get firewall rules: {str(e)}")
            return []
            
    def add_rule(self, name, direction, action, protocol, local_ports="",
                remote_ports="", program=""):
        """Add a new firewall rule.
        
        Args:
            name: Rule name
            direction: "Inbound" or "Outbound"
            action: "Allow" or "Block"
            protocol: Protocol ("TCP", "UDP", or "Any")
            local_ports: Local port(s) (optional)
            remote_ports: Remote port(s) (optional)
            program: Program path (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            rule = win32com.client.Dispatch("HNetCfg.FWRule")
            rule.Name = name
            rule.Direction = 1 if direction == "Inbound" else 2
            rule.Action = 1 if action == "Allow" else 0
            rule.Protocol = protocol if protocol != "Any" else "*"
            rule.LocalPorts = local_ports
            rule.RemotePorts = remote_ports
            rule.ApplicationName = program
            rule.Enabled = True
            
            self.firewall.Rules.Add(rule)
            self.logger.info(f"Added firewall rule: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add firewall rule: {str(e)}")
            return False
            
    def delete_rule(self, name):
        """Delete a firewall rule.
        
        Args:
            name: Name of rule to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.firewall.Rules.Remove(name)
            self.logger.info(f"Deleted firewall rule: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete firewall rule: {str(e)}")
            return False
            
    def set_rule_enabled(self, name, enabled):
        """Enable or disable a firewall rule.
        
        Args:
            name: Name of rule to modify
            enabled: True to enable, False to disable
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            rule = self.firewall.Rules.Item(name)
            rule.Enabled = enabled
            self.logger.info(f"{'Enabled' if enabled else 'Disabled'} firewall rule: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to {'enable' if enabled else 'disable'} firewall rule: {str(e)}")
            return False
