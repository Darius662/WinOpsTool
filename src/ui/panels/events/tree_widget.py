"""Tree widget for displaying Windows events."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QColor
from src.core.logger import setup_logger

class EventsTreeWidget(QTreeWidget):
    """Tree widget for displaying Windows events."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the tree widget."""
        # Set headers
        self.setHeaderLabels([
            "Level",
            "Date and Time",
            "Source",
            "Event ID",
            "Task Category",
            "Computer"
        ])
        
        # Configure columns
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Level
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Date and Time
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Source
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Event ID
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Task Category
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)           # Computer
        
        # Set selection behavior
        self.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        
        # Enable sorting
        self.setSortingEnabled(True)
        self.sortByColumn(1, Qt.SortOrder.DescendingOrder)  # Sort by date, newest first
        
        # Set alternating row colors
        self.setAlternatingRowColors(True)
        
    def populate_events(self, events):
        """Populate the tree with events."""
        self.clear()
        
        if not events:
            self.logger.debug("No events to display")
            return
            
        for event in events:
            try:
                item = QTreeWidgetItem([
                    event.get('level', ''),
                    event.get('time_created', ''),
                    event.get('provider', ''),
                    event.get('event_id', ''),
                    event.get('task', ''),
                    event.get('computer', '')
                ])
                
                # Store full event data in the item
                item.setData(0, Qt.ItemDataRole.UserRole, event)
                
                # Set level-based styling
                level = event.get('level', '').lower()
                if level == 'critical':
                    item.setForeground(0, QColor(139, 0, 0))  # Dark red
                    item.setBackground(0, QColor(255, 240, 240))  # Light red background
                elif level == 'error':
                    item.setForeground(0, QColor(255, 0, 0))  # Red
                elif level == 'warning':
                    item.setForeground(0, QColor(255, 140, 0))  # Orange
                elif level == 'information':
                    item.setForeground(0, QColor(0, 100, 0))  # Dark green
                elif level == 'verbose':
                    item.setForeground(0, QColor(128, 128, 128))  # Gray
                
                self.addTopLevelItem(item)
                
            except Exception as e:
                self.logger.error(f"Error adding event item: {e}")
                continue
        
        self.logger.debug(f"Populated tree with {len(events)} events")
        
    def get_selected_event(self):
        """Get the currently selected event data."""
        current_item = self.currentItem()
        if current_item:
            return current_item.data(0, Qt.ItemDataRole.UserRole)
        return None
        
    def get_selected_event_id(self):
        """Get the ID of the currently selected event."""
        event = self.get_selected_event()
        if event:
            return event.get('event_id', '')
        return None
        
    def filter_by_level(self, levels):
        """Filter events by level."""
        if not levels:
            # Show all items
            for i in range(self.topLevelItemCount()):
                item = self.topLevelItem(i)
                if item:
                    item.setHidden(False)
            return
            
        # Hide/show items based on level filter
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item:
                event_data = item.data(0, Qt.ItemDataRole.UserRole)
                if event_data:
                    event_level = event_data.get('level', '').lower()
                    should_show = any(level.lower() in event_level for level in levels)
                    item.setHidden(not should_show)
                    
    def filter_by_source(self, sources):
        """Filter events by source/provider."""
        if not sources:
            # Show all items
            for i in range(self.topLevelItemCount()):
                item = self.topLevelItem(i)
                if item:
                    item.setHidden(False)
            return
            
        # Hide/show items based on source filter
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item:
                event_data = item.data(0, Qt.ItemDataRole.UserRole)
                if event_data:
                    event_source = event_data.get('provider', '').lower()
                    should_show = any(source.lower() in event_source for source in sources)
                    item.setHidden(not should_show)
                    
    def clear_filters(self):
        """Clear all filters and show all events."""
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item:
                item.setHidden(False)
