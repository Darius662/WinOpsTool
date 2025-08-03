"""Windows Process management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLineEdit, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import ProcessesTree
from .dialogs import PriorityDialog
from .manager import ProcessManager

class ProcessesPanel(BasePanel):
    """Panel for managing Windows Processes."""
    
    def __init__(self, parent=None):
        """Initialize processes panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = ProcessManager()
        
        # Set up refresh timer (2 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_processes)
        
        # Initialize imported config items
        self.imported_config_items = set()
        
        # Defer initial refresh and timer start
        # This will prevent blocking the UI during startup
        QTimer.singleShot(1000, self.delayed_start)
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Use the main_layout from BasePanel instead of creating a new layout
        layout = self.main_layout
        
        # Search controls
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.filter_processes)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        
        # Action buttons
        self.terminate_button = QPushButton("Terminate")
        self.terminate_button.clicked.connect(self.terminate_process)
        search_layout.addWidget(self.terminate_button)
        
        self.priority_button = QPushButton("Set Priority")
        self.priority_button.clicked.connect(self.change_priority)
        search_layout.addWidget(self.priority_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_processes)
        search_layout.addWidget(self.refresh_button)
        
        layout.addLayout(search_layout)
        
        # Processes tree
        self.processes_tree = ProcessesTree()
        self.processes_tree.itemSelectionChanged.connect(self.update_buttons)
        layout.addWidget(self.processes_tree)
        
        # Initial button state
        self.update_buttons()
        
    def update_buttons(self):
        """Update button enabled states based on selection."""
        has_selection = bool(self.processes_tree.selectedItems())
        self.terminate_button.setEnabled(has_selection)
        self.priority_button.setEnabled(has_selection)
        
    def refresh_processes(self):
        """Refresh the processes list."""
        try:
            # Get current selection
            selected_pid = None
            if self.processes_tree.selectedItems():
                selected_pid = int(self.processes_tree.selectedItems()[0].text(0))
                
            # Clear and repopulate tree
            self.processes_tree.clear_processes()
            processes = self.manager.get_processes()
            
            # Track process names we've seen to add virtual entries later
            seen_process_names = set()
            
            for proc in processes:
                # Check if this process is in the imported config
                is_imported = self.is_imported_config_item(f"process:{proc['pid']}:{proc['priority']}")
                
                # Add to seen process names
                seen_process_names.add(proc['name'])
                
                self.processes_tree.add_process(
                    proc['pid'],
                    proc['name'],
                    proc['cpu_percent'],
                    proc['memory_percent'],
                    proc['status'],
                    proc['threads'],
                    proc['username'],
                    proc['priority'],
                    highlight=is_imported
                )
                
            # Add virtual entries for processes in config but not running
            self.add_virtual_processes(seen_process_names)
                
            # Reapply filter if search text exists
            if self.search_edit.text():
                self.filter_processes(self.search_edit.text())
                
            # Restore selection if process still exists
            if selected_pid:
                item = self.processes_tree.find_process(selected_pid)
                if item:
                    self.processes_tree.setCurrentItem(item)
                    
        except Exception as e:
            self.logger.error(f"Failed to refresh processes: {str(e)}")
            
    def add_virtual_processes(self, seen_process_names):
        """Add virtual entries for processes in config but not running.
        
        Args:
            seen_process_names: Set of process names that are currently running
        """
        try:
            # Check for process priority settings in imported config
            for item_id in self.imported_config_items:
                if item_id.startswith("process:priority:"):
                    # Extract process name and priority from the item ID
                    # Format is "process:priority:name:priority_value"
                    parts = item_id.split(":", 3)
                    if len(parts) == 4:
                        process_name = parts[2]
                        priority = parts[3]
                        
                        # Only add virtual entry if process is not running
                        if process_name not in seen_process_names:
                            self.processes_tree.add_virtual_process(process_name, priority)
                            self.logger.debug(f"Added virtual process entry: {process_name} with priority {priority}")
                            
        except Exception as e:
            self.logger.error(f"Error adding virtual processes: {str(e)}")
    
    def filter_processes(self, text):
        """Filter processes by PID or name.
        
        Args:
            text: Search text
        """
        for i in range(self.processes_tree.topLevelItemCount()):
            item = self.processes_tree.topLevelItem(i)
            pid = item.text(0)
            name = item.text(1).lower()
            search = text.lower()
            item.setHidden(search not in pid and search not in name)
            
    def terminate_process(self):
        """Terminate selected process."""
        item = self.processes_tree.selectedItems()[0]
        process = self.processes_tree.get_process(item)
        
        reply = QMessageBox.question(
            self,
            "Confirm Terminate",
            f"Are you sure you want to terminate process '{process['name']}' (PID: {process['pid']})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.manager.terminate_process(process['pid']):
                self.refresh_processes()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to terminate process '{process['name']}' (PID: {process['pid']})"
                )
                
    def change_priority(self):
        """Change priority of selected process."""
        item = self.processes_tree.selectedItems()[0]
        process = self.processes_tree.get_process(item)
        
        dialog = PriorityDialog(self, process['priority'])
        if dialog.exec():
            priority = dialog.get_priority()
            if priority == "Realtime":
                # Extra confirmation for Realtime
                reply = QMessageBox.warning(
                    self,
                    "Warning",
                    "Setting Realtime priority can make the system unresponsive!\n\n"
                    "Are you absolutely sure?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
                    
            if self.manager.set_priority(process['pid'], priority):
                self.refresh_processes()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to change priority for process '{process['name']}' (PID: {process['pid']})"
                )
                
    def delayed_start(self):
        """Delayed initialization to prevent blocking the UI during startup."""
        self.logger.info('Starting delayed initialization of ProcessesPanel')
        self.refresh_processes()
        # Auto-refresh timer removed - refresh only happens manually via button
        self.logger.info('ProcessesPanel initialization complete')
        
    def setup_connections(self):
        """Set up signal-slot connections."""
        # Connections already set up in setup_ui method
        # This method is required by BasePanel but implementation is kept here
        # for consistency with the BasePanel interface
        pass
        
    def apply_config(self, config):
        """Apply configuration to the panel.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if configuration was applied successfully, False otherwise
        """
        self.logger.info("Applying processes configuration")
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Process configuration
            if 'processes' not in config:
                self.logger.warning("No processes configuration found")
                return False
                
            processes_config = config['processes']
            
            # Apply monitored processes configuration if available
            if 'monitored_processes' in processes_config and isinstance(processes_config['monitored_processes'], list):
                self.logger.info(f"Found {len(processes_config['monitored_processes'])} monitored processes in config")
                # Note: Currently the processes panel doesn't support persistent monitoring of specific processes
                # This is a placeholder for future implementation
                # We'll return True to indicate successful processing of the configuration
                return True
                
            # Apply process priority settings if available
            if 'priority_settings' in processes_config and isinstance(processes_config['priority_settings'], list):
                self.logger.info(f"Applying {len(processes_config['priority_settings'])} process priority settings")
                
                success = False
                for setting in processes_config['priority_settings']:
                    if not isinstance(setting, dict) or 'name' not in setting or 'priority' not in setting:
                        self.logger.warning("Skipping invalid priority setting")
                        continue
                        
                    process_name = setting['name']
                    priority = setting['priority']
                    
                    # Find processes by name and set priority
                    processes = self.manager.find_processes_by_name(process_name)
                    if not processes:
                        self.logger.warning(f"Process '{process_name}' not found")
                        continue
                        
                    for proc in processes:
                        result = self.manager.set_priority(proc['pid'], priority)
                        if result:
                            self.logger.info(f"Set priority of '{process_name}' (PID: {proc['pid']}) to {priority}")
                            success = True
                        else:
                            self.logger.warning(f"Failed to set priority of '{process_name}' (PID: {proc['pid']})")
                
                # Refresh the process list to show updated priorities
                self.refresh_processes()
                return success
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying processes configuration: {str(e)}")
            return False
            
    def mark_config_items(self, config):
        """Mark items from configuration for highlighting without applying changes.
        
        This method identifies and marks process settings from the configuration
        that would be modified by apply_config(), but does not actually
        apply any changes to the system. Items will be visually highlighted in the UI.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if items were marked successfully, False otherwise
        """
        self.logger.info("Marking process settings from configuration for highlighting")
        
        # Clear previous imported items
        self.imported_config_items.clear()
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Check if processes section exists
            if 'processes' not in config:
                self.logger.warning("No process settings in configuration")
                return False
                
            processes_config = config['processes']
            
            # Process priority settings
            if 'priority_settings' in processes_config and isinstance(processes_config['priority_settings'], list):
                self.logger.info(f"Marking {len(processes_config['priority_settings'])} process priority settings for highlighting")
                
                for setting in processes_config['priority_settings']:
                    if not isinstance(setting, dict) or 'name' not in setting or 'priority' not in setting:
                        self.logger.warning("Skipping invalid priority setting")
                        continue
                        
                    process_name = setting['name']
                    priority = setting['priority']
                    
                    # Mark this process priority setting as imported from config for highlighting
                    self.mark_as_imported_config(f"process:priority:{process_name}:{priority}")
                    self.logger.debug(f"Marked process priority setting for highlighting: {process_name} -> {priority}")
                    
                    # Find processes by name to highlight them
                    processes = self.manager.find_processes_by_name(process_name)
                    if processes:
                        for proc in processes:
                            # Add to imported config items for highlighting
                            self.mark_as_imported_config(f"process:{proc['pid']}:{priority}")
                    else:
                        # Process not currently running, will be highlighted when it appears
                        self.logger.debug(f"Process '{process_name}' not currently running")
            
            # Process monitored processes (placeholder for future implementation)
            if 'monitored_processes' in processes_config and isinstance(processes_config['monitored_processes'], list):
                self.logger.info(f"Marking {len(processes_config['monitored_processes'])} monitored processes for highlighting")
                
                for process_name in processes_config['monitored_processes']:
                    if not isinstance(process_name, str):
                        self.logger.warning("Skipping invalid monitored process")
                        continue
                        
                    # Mark this monitored process as imported from config for highlighting
                    self.mark_as_imported_config(f"process:monitored:{process_name}")
                    self.logger.debug(f"Marked monitored process for highlighting: {process_name}")
            
            # Refresh the processes to show updated state with highlighting
            self.refresh_processes()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error marking process settings from configuration: {str(e)}")
            return False
            
    def export_config(self):
        """Export panel configuration.
        
        Returns:
            dict: Dictionary containing panel configuration
        """
        self.logger.info("Exporting processes configuration")
        
        try:
            # Get current processes
            processes = self.manager.get_processes()
            
            # Filter out system processes and create a list of processes with their priorities
            priority_settings = []
            for proc in processes:
                # Skip system processes
                if proc['name'].lower() in ['system', 'system idle process', 'registry', 'smss.exe']:
                    continue
                    
                # Only include processes with non-normal priority
                if proc['priority'] != "Normal":
                    priority_settings.append({
                        'name': proc['name'],
                        'priority': proc['priority']
                    })
            
            # Create configuration dictionary
            config = {
                'processes': {
                    'priority_settings': priority_settings,
                    # Placeholder for future monitored processes feature
                    'monitored_processes': []
                }
            }
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error exporting processes configuration: {str(e)}")
            return {'processes': {'priority_settings': [], 'monitored_processes': []}}
