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
            self.logger.debug("Refreshing scheduled tasks")
            tasks = self.manager.get_scheduled_tasks()
            self.task_tree.populate_tasks(tasks)
            self.info_text.setPlainText(f"Loaded {len(tasks)} scheduled tasks.")
            self.logger.debug("Refreshed scheduled tasks list")
        except Exception as e:
            self.logger.error(f"Error refreshing tasks: {e}")
            QMessageBox.critical(self, "Error", f"Failed to refresh tasks:\n{str(e)}")
            
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
