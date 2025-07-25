"""Tree widget for displaying scheduled tasks."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class SchedulerTreeWidget(QTreeWidget):
    """Tree widget for displaying Windows scheduled tasks."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the tree widget."""
        # Set headers
        self.setHeaderLabels([
            "Task Name",
            "Status",
            "Next Run",
            "Last Run",
            "Last Result",
            "Author",
            "Task To Run"
        ])
        
        # Configure columns
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Task Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Next Run
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Last Run
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Last Result
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Author
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)           # Task To Run
        
        # Set selection behavior
        self.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        
        # Enable sorting
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
        # Set alternating row colors
        self.setAlternatingRowColors(True)
        
    def populate_tasks(self, tasks):
        """Populate the tree with scheduled tasks."""
        self.clear()
        
        if not tasks:
            self.logger.debug("No scheduled tasks to display")
            return
            
        for task in tasks:
            try:
                item = QTreeWidgetItem([
                    task.get('name', ''),
                    task.get('status', ''),
                    task.get('next_run', ''),
                    task.get('last_run', ''),
                    task.get('last_result', ''),
                    task.get('author', ''),
                    task.get('task_to_run', '')
                ])
                
                # Store full task data in the item
                item.setData(0, Qt.ItemDataRole.UserRole, task)
                
                # Set status-based styling
                status = task.get('status', '').lower()
                if status == 'ready':
                    item.setForeground(1, Qt.GlobalColor.darkGreen)
                elif status == 'running':
                    item.setForeground(1, Qt.GlobalColor.blue)
                elif status == 'disabled':
                    item.setForeground(1, Qt.GlobalColor.red)
                elif 'error' in status or 'failed' in status:
                    item.setForeground(1, Qt.GlobalColor.darkRed)
                
                self.addTopLevelItem(item)
                
            except Exception as e:
                self.logger.error(f"Error adding task item: {e}")
                continue
        
        self.logger.debug(f"Populated tree with {len(tasks)} scheduled tasks")
        
    def get_selected_task(self):
        """Get the currently selected task data."""
        current_item = self.currentItem()
        if current_item:
            return current_item.data(0, Qt.ItemDataRole.UserRole)
        return None
        
    def get_selected_task_name(self):
        """Get the name of the currently selected task."""
        task = self.get_selected_task()
        if task:
            return task.get('name', '')
        return None
        
    def refresh_task_item(self, task_name, updated_task):
        """Refresh a specific task item with updated data."""
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item and item.text(0) == task_name:
                # Update the item with new data
                item.setText(0, updated_task.get('name', ''))
                item.setText(1, updated_task.get('status', ''))
                item.setText(2, updated_task.get('next_run', ''))
                item.setText(3, updated_task.get('last_run', ''))
                item.setText(4, updated_task.get('last_result', ''))
                item.setText(5, updated_task.get('author', ''))
                item.setText(6, updated_task.get('task_to_run', ''))
                
                # Update stored data
                item.setData(0, Qt.ItemDataRole.UserRole, updated_task)
                
                # Update status styling
                status = updated_task.get('status', '').lower()
                if status == 'ready':
                    item.setForeground(1, Qt.GlobalColor.darkGreen)
                elif status == 'running':
                    item.setForeground(1, Qt.GlobalColor.blue)
                elif status == 'disabled':
                    item.setForeground(1, Qt.GlobalColor.red)
                elif 'error' in status or 'failed' in status:
                    item.setForeground(1, Qt.GlobalColor.darkRed)
                
                break
