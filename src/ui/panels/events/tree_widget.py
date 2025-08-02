"""Tree widget for displaying Windows events."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QColor, QBrush
from src.core.logger import setup_logger

class EventsTreeWidget(QTreeWidget):
    """Tree widget for displaying Windows events."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
        # Track virtual items
        self.virtual_items = set()
        
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
        
    def add_virtual_event(self, event_data):
        """Add a virtual event to the tree (from imported config).
        
        Args:
            event_data: Dictionary containing event data
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        try:
            # Create a virtual event with provided data
            item = QTreeWidgetItem([
                event_data.get('level', 'Information'),
                event_data.get('time_created', 'N/A (Virtual)'),
                event_data.get('provider', 'Config Import'),
                event_data.get('event_id', event_data.get('id', 'N/A')),
                event_data.get('task', 'Virtual Event'),
                event_data.get('computer', event_data.get('computer', 'Local'))
            ])
            
            # Store full event data in the item
            event_data['is_virtual'] = True
            item.setData(0, Qt.ItemDataRole.UserRole, event_data)
            
            # Add to tree
            self.addTopLevelItem(item)
            
            # Mark as virtual
            self.virtual_items.add(item)
            
            # Highlight the item
            self.highlight_item(item, is_virtual=True)
            
            return item
            
        except Exception as e:
            self.logger.error(f"Error adding virtual event: {e}")
            return None
        
    def highlight_item(self, item, is_virtual=False):
        """Highlight an item to indicate it's from imported config or virtual.
        
        Args:
            item: QTreeWidgetItem to highlight
            is_virtual: Whether this is a virtual item
        """
        # Use cyan background with dark blue text for highlighting
        background_color = QColor(200, 255, 255)  # Light cyan
        text_color = QColor(0, 0, 128)  # Dark blue
        
        # Set background color for all columns
        for col in range(self.columnCount()):
            item.setBackground(col, QBrush(background_color))
            
            # Don't override the level column text color if it's already colored
            if col != 0 or is_virtual:
                item.setForeground(col, QBrush(text_color))
            
        # Set tooltip
        if is_virtual:
            tooltip = "Virtual event from imported configuration (does not exist in system)"
        else:
            tooltip = "Event from imported configuration"
            
        for col in range(self.columnCount()):
            item.setToolTip(col, tooltip)
            
    def is_virtual_item(self, item):
        """Check if an item is a virtual item.
        
        Args:
            item: QTreeWidgetItem to check
            
        Returns:
            bool: True if item is virtual, False otherwise
        """
        return item in self.virtual_items
        
    def get_all_items(self):
        """Get all items in the tree.
        
        Returns:
            list: List of all QTreeWidgetItems
        """
        items = []
        for i in range(self.topLevelItemCount()):
            items.append(self.topLevelItem(i))
        return items
        
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
