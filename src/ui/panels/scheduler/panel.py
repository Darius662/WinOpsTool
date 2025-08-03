"""Scheduler panel for Windows Task Scheduler management."""
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                          QMessageBox, QSplitter, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from src.ui.base.base_panel import BasePanel
from .manager import SchedulerManager
from .tree_widget import SchedulerTreeWidget
from .dialogs import TaskDetailsDialog, CreateTaskDialog, ConfirmTaskActionDialog
from src.core.logger import setup_logger

class SchedulerPanel(BasePanel):
    """Panel for managing Windows scheduled tasks."""
    
    def __init__(self, parent=None):
        self.manager = SchedulerManager()
        
        # Initialize imported config items
        self.imported_config_items = set()
        
        super().__init__(parent)
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Create splitter for main layout
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top section - Task list and controls
        top_widget = self.create_top_section()
        splitter.addWidget(top_widget)
        
        # Bottom section - Task details
        bottom_widget = self.create_bottom_section()
        splitter.addWidget(bottom_widget)
        
        # Set splitter proportions
        splitter.setSizes([400, 200])
        
        self.main_layout.addWidget(splitter)
        
        # Load initial data with deferred initialization
        QTimer.singleShot(1000, self.deferred_initialization)
        
    def create_top_section(self):
        """Create the top section with task list and controls."""
        top_widget = QGroupBox("Scheduled Tasks")
        layout = QVBoxLayout(top_widget)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_tasks)
        button_layout.addWidget(self.refresh_button)
        
        self.run_button = QPushButton("Run Task")
        self.run_button.clicked.connect(self.run_selected_task)
        self.run_button.setEnabled(False)
        button_layout.addWidget(self.run_button)
        
        self.enable_button = QPushButton("Enable")
        self.enable_button.clicked.connect(self.enable_selected_task)
        self.enable_button.setEnabled(False)
        button_layout.addWidget(self.enable_button)
        
        self.disable_button = QPushButton("Disable")
        self.disable_button.clicked.connect(self.disable_selected_task)
        self.disable_button.setEnabled(False)
        button_layout.addWidget(self.disable_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_selected_task)
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; }")
        button_layout.addWidget(self.delete_button)
        
        self.details_button = QPushButton("Details")
        self.details_button.clicked.connect(self.show_task_details)
        self.details_button.setEnabled(False)
        button_layout.addWidget(self.details_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Task tree
        self.task_tree = SchedulerTreeWidget()
        self.task_tree.itemSelectionChanged.connect(self.on_task_selection_changed)
        self.task_tree.itemDoubleClicked.connect(self.show_task_details)
        layout.addWidget(self.task_tree)
        
        return top_widget
        
    def create_bottom_section(self):
        """Create the bottom section with task details."""
        bottom_widget = QGroupBox("Task Information")
        layout = QVBoxLayout(bottom_widget)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        self.info_text.setPlainText("Select a task to view details...")
        layout.addWidget(self.info_text)
        
        return bottom_widget
        
    def setup_connections(self):
        """Set up signal connections."""
        # This method is required by BasePanel
        pass
        
    def deferred_initialization(self):
        """Perform deferred initialization to improve startup responsiveness."""
        self.logger.info("Starting delayed initialization of SchedulerPanel")
        try:
            self.refresh_tasks()
            self.logger.info("SchedulerPanel initialization complete")
        except Exception as e:
            self.logger.error(f"Error during SchedulerPanel initialization: {e}")
            
    def refresh_tasks(self):
        """Refresh the list of scheduled tasks."""
        try:
            tasks = self.manager.get_scheduled_tasks()
            self.task_tree.populate_tasks(tasks)
            
            # Highlight imported config items
            self.highlight_imported_tasks()
            
            self.info_text.setPlainText(f"Loaded {len(tasks)} scheduled tasks.")
            self.logger.info(f"Refreshed {len(tasks)} scheduled tasks")
        except Exception as e:
            self.logger.error(f"Failed to refresh tasks: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to refresh tasks:\n{str(e)}")
            
    def highlight_imported_tasks(self):
        """Highlight tasks that are marked as imported from configuration."""
        try:
            # Iterate through all items in the tree
            for item in self.task_tree.get_all_items():
                task_data = item.data(0, Qt.ItemDataRole.UserRole)
                if task_data and task_data.get('name'):
                    task_name = task_data.get('name')
                    
                    # Check if this task is in the imported config
                    if f"scheduler:task:{task_name}" in self.imported_config_items:
                        self.task_tree.highlight_item(item)
                        
        except Exception as e:
            self.logger.error(f"Error highlighting imported tasks: {str(e)}")
            
    def on_task_selection_changed(self):
        """Handle task selection changes."""
        selected_task = self.task_tree.get_selected_task()
        has_selection = selected_task is not None
        
        # Enable/disable buttons based on selection
        self.run_button.setEnabled(has_selection)
        self.enable_button.setEnabled(has_selection)
        self.disable_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self.details_button.setEnabled(has_selection)
        
        if selected_task:
            # Update info text with basic task information
            info_text = f"Task: {selected_task.get('name', 'N/A')}\n"
            info_text += f"Status: {selected_task.get('status', 'N/A')}\n"
            info_text += f"Next Run: {selected_task.get('next_run', 'N/A')}\n"
            info_text += f"Last Run: {selected_task.get('last_run', 'N/A')}\n"
            info_text += f"Last Result: {selected_task.get('last_result', 'N/A')}\n"
            info_text += f"Command: {selected_task.get('task_to_run', 'N/A')}"
            self.info_text.setPlainText(info_text)
        else:
            self.info_text.setPlainText("Select a task to view details...")
            
    def run_selected_task(self):
        """Run the selected task immediately."""
        task_name = self.task_tree.get_selected_task_name()
        if not task_name:
            return
            
        try:
            if self.manager.run_task(task_name):
                QMessageBox.information(self, "Success", f"Task '{task_name}' has been started.")
                # Refresh to show updated status
                QTimer.singleShot(1000, self.refresh_tasks)
            else:
                QMessageBox.warning(self, "Failed", f"Failed to run task '{task_name}'.")
        except Exception as e:
            self.logger.error(f"Error running task: {e}")
            QMessageBox.critical(self, "Error", f"Error running task:\n{str(e)}")
            
    def enable_selected_task(self):
        """Enable the selected task."""
        task_name = self.task_tree.get_selected_task_name()
        if not task_name:
            return
            
        try:
            if self.manager.enable_task(task_name):
                QMessageBox.information(self, "Success", f"Task '{task_name}' has been enabled.")
                self.refresh_tasks()
            else:
                QMessageBox.warning(self, "Failed", f"Failed to enable task '{task_name}'.")
        except Exception as e:
            self.logger.error(f"Error enabling task: {e}")
            QMessageBox.critical(self, "Error", f"Error enabling task:\n{str(e)}")
            
    def disable_selected_task(self):
        """Disable the selected task."""
        task_name = self.task_tree.get_selected_task_name()
        if not task_name:
            return
            
        dialog = ConfirmTaskActionDialog("disable", task_name, self)
        if dialog.exec() == QMessageBox.StandardButton.Yes:
            try:
                if self.manager.disable_task(task_name):
                    QMessageBox.information(self, "Success", f"Task '{task_name}' has been disabled.")
                    self.refresh_tasks()
                else:
                    QMessageBox.warning(self, "Failed", f"Failed to disable task '{task_name}'.")
            except Exception as e:
                self.logger.error(f"Error disabling task: {e}")
                QMessageBox.critical(self, "Error", f"Error disabling task:\n{str(e)}")
                
    def delete_selected_task(self):
        """Delete the selected task."""
        task_name = self.task_tree.get_selected_task_name()
        if not task_name:
            return
            
        dialog = ConfirmTaskActionDialog("delete", task_name, self)
        if dialog.exec() == QMessageBox.StandardButton.Yes:
            try:
                if self.manager.delete_task(task_name):
                    QMessageBox.information(self, "Success", f"Task '{task_name}' has been deleted.")
                    self.refresh_tasks()
                else:
                    QMessageBox.warning(self, "Failed", f"Failed to delete task '{task_name}'.")
            except Exception as e:
                self.logger.error(f"Error deleting task: {e}")
                QMessageBox.critical(self, "Error", f"Error deleting task:\n{str(e)}")
                
    def show_task_details(self):
        """Show detailed information about the selected task."""
        selected_task = self.task_tree.get_selected_task()
        if not selected_task:
            return
            
        try:
            # Get additional details from the manager
            task_name = selected_task.get('name', '')
            detailed_info = self.manager.get_task_details(task_name)
            
            if detailed_info:
                # Merge the basic task info with detailed info
                combined_data = {**selected_task, **detailed_info}
            else:
                combined_data = selected_task
                
            dialog = TaskDetailsDialog(combined_data, self)
            dialog.exec()
            
        except Exception as e:
            self.logger.error(f"Error showing task details: {e}")
            QMessageBox.critical(self, "Error", f"Error showing task details:\n{str(e)}")
            
    def cleanup(self):
        """Clean up resources when the panel is destroyed."""
        try:
            # Stop any running operations
            pass
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            
    def apply_config(self, config):
        """Apply configuration to the panel.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if configuration was applied successfully, False otherwise
        """
        self.logger.info("Applying scheduler configuration")
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Process configuration
            if 'scheduled_tasks' not in config:
                self.logger.warning("No scheduled tasks configuration found")
                return False
                
            tasks_config = config['scheduled_tasks']
            
            if not isinstance(tasks_config, list):
                self.logger.warning("Invalid scheduled tasks configuration format")
                return False
                
            success = False
            
            # Process each task in the configuration
            for task_config in tasks_config:
                if not isinstance(task_config, dict):
                    self.logger.warning("Skipping invalid task configuration")
                    continue
                    
                # Check required fields
                if 'name' not in task_config or 'command' not in task_config:
                    self.logger.warning("Skipping task without required fields")
                    continue
                    
                task_name = task_config['name']
                command = task_config['command']
                
                # Optional fields with defaults
                description = task_config.get('description', '')
                schedule_type = task_config.get('schedule_type', 'ONCE')
                start_time = task_config.get('start_time', None)
                enabled = task_config.get('enabled', True)
                
                # Create task dialog would normally be used here, but we're applying directly
                try:
                    # Check if task already exists
                    existing_tasks = self.manager.get_scheduled_tasks()
                    task_exists = any(task['name'] == task_name for task in existing_tasks)
                    
                    if task_exists:
                        # Delete existing task first
                        self.logger.info(f"Replacing existing task: {task_name}")
                        self.manager.delete_task(task_name)
                    
                    # Create the task with configuration
                    result = self.manager.create_task(
                        name=task_name,
                        command=command,
                        description=description,
                        schedule_type=schedule_type,
                        start_time=start_time
                    )
                    
                    if result:
                        self.logger.info(f"Created scheduled task: {task_name}")
                        
                        # Set enabled state if needed
                        if not enabled:
                            self.manager.disable_task(task_name)
                            self.logger.info(f"Disabled task: {task_name}")
                            
                        success = True
                    else:
                        self.logger.warning(f"Failed to create scheduled task: {task_name}")
                        
                except Exception as e:
                    self.logger.error(f"Error creating scheduled task '{task_name}': {str(e)}")
            
            # Refresh the task list to show updated state
            self.refresh_tasks()
            return success
            
        except Exception as e:
            self.logger.error(f"Error applying scheduler configuration: {str(e)}")
            return False
            
    def export_config(self):
        """Export panel configuration.
        
        Returns:
            dict: Dictionary containing panel configuration
        """
        self.logger.info("Exporting scheduler configuration")
        
        try:
            # Get current scheduled tasks
            tasks = self.manager.get_scheduled_tasks()
            
            # Filter out system tasks and create exportable task configurations
            exportable_tasks = []
            
            for task in tasks:
                # Skip Microsoft and Windows system tasks
                if task['name'].startswith('\\Microsoft\\') or task['name'].startswith('\\Windows\\'):
                    continue
                    
                # Get detailed task information
                task_details = self.manager.get_task_details(task['name'])
                
                if not task_details:
                    continue
                    
                # Create task configuration
                task_config = {
                    'name': task['name'],
                    'command': task.get('task_to_run', ''),
                    'description': task_details.get('description', ''),
                    'schedule_type': task_details.get('trigger_type', 'ONCE'),
                    'enabled': task.get('status', '') == 'Ready'
                }
                
                exportable_tasks.append(task_config)
            
            # Create configuration dictionary
            config = {
                'scheduled_tasks': exportable_tasks
            }
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error exporting scheduler configuration: {str(e)}")
            return {'scheduled_tasks': []}

    def mark_config_items(self, config):
        """Mark items from configuration for highlighting without applying changes.
        
        This method identifies and marks scheduled tasks from the configuration
        that would be modified by apply_config(), but does not actually
        apply any changes to the system. Items will be visually highlighted in the UI.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if items were marked successfully, False otherwise
        """
        self.logger.info("Marking scheduled tasks from configuration for highlighting")
        
        # Clear previous imported items
        self.imported_config_items.clear()
        
        if not isinstance(config, dict):
            self.logger.error("Invalid configuration format")
            return False
            
        try:
            # Check if scheduler section exists
            if 'scheduled_tasks' not in config:
                self.logger.warning("No scheduled tasks configuration found")
                return False
                
            scheduled_tasks = config['scheduled_tasks']
            
            if not isinstance(scheduled_tasks, list):
                self.logger.warning("Invalid scheduled tasks configuration format")
                return False
                
            # Get existing tasks for comparison
            existing_tasks = {task['name']: task for task in self.manager.get_scheduled_tasks()}
            
            # Process scheduled tasks
            for task_config in scheduled_tasks:
                if not isinstance(task_config, dict):
                    continue
                    
                # Check required fields
                if 'name' not in task_config:
                    self.logger.warning("Skipping invalid task configuration (missing name)")
                    continue
                    
                task_name = task_config['name']
                
                # Mark this task as imported from config for highlighting
                self.mark_as_imported_config(f"scheduler:task:{task_name}")
                self.logger.debug(f"Marked scheduled task for highlighting: {task_name}")
                
                # Check if task exists
                if task_name in existing_tasks:
                    # Task exists, it will be highlighted during refresh
                    pass
                else:
                    # Task doesn't exist, add virtual entry
                    self.add_virtual_task(task_config)
            
            # Refresh the tasks to show updated state with highlighting
            self.refresh_tasks()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error marking scheduled tasks from configuration: {str(e)}")
            return False
    
    def add_virtual_task(self, task_config):
        """Add a virtual task entry that doesn't exist in the system yet.
        
        Args:
            task_config: Dictionary containing task configuration
        """
        try:
            # Create a task dictionary in the format expected by the tree widget
            virtual_task = {
                'name': task_config.get('name', ''),
                'command': task_config.get('command', ''),
                'description': task_config.get('description', ''),
                'schedule_type': task_config.get('schedule_type', 'ONCE'),
                'status': 'Virtual (Not Applied)',
                'task_to_run': task_config.get('command', '')
            }
            
            # Add virtual entry to the tree
            self.task_tree.add_virtual_task(virtual_task)
            
            self.logger.debug(f"Added virtual scheduled task: {task_config.get('name', '')}")
            
        except Exception as e:
            self.logger.error(f"Error adding virtual scheduled task: {str(e)}")
    
    def mark_as_imported_config(self, item):
        """Mark an item as imported from config for highlighting.
        
        Args:
            item: Item to mark
        """
        self.imported_config_items.add(item)
