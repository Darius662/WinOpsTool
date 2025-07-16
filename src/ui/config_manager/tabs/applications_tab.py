"""Applications configuration tab."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox, QComboBox, QTabWidget)
from .base_tab import BaseConfigTab

class ApplicationsTab(BaseConfigTab):
    """Tab for configuring application settings."""
    def __init__(self, config_handler):
        super().__init__(config_handler, "applications")
        
    def setup_ui(self):
        """Set up the tab's user interface."""
        # Create tabs for Startup and Processes
        tabs = QTabWidget()
        
        # Startup tab
        startup_widget = QWidget()
        startup_layout = QVBoxLayout(startup_widget)
        
        startup_label = QLabel("Startup Applications")
        startup_layout.addWidget(startup_label)
        
        self.startup_tree = QTreeWidget()
        self.startup_tree.setHeaderLabels([
            "Path",
            "Arguments",
            "Run As",
            "Wait"
        ])
        self.startup_tree.setColumnWidth(0, 300)
        self.startup_tree.setColumnWidth(1, 200)
        startup_layout.addWidget(self.startup_tree)
        
        # Startup input fields
        startup_input = QWidget()
        startup_input_layout = QVBoxLayout(startup_input)
        
        # Path
        path_layout = QHBoxLayout()
        path_label = QLabel("Path:")
        path_layout.addWidget(path_label)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Full path to application")
        path_layout.addWidget(self.path_edit)
        startup_input_layout.addLayout(path_layout)
        
        # Arguments
        args_layout = QHBoxLayout()
        args_label = QLabel("Arguments:")
        args_layout.addWidget(args_label)
        self.args_edit = QLineEdit()
        self.args_edit.setPlaceholderText("Command line arguments (optional)")
        args_layout.addWidget(self.args_edit)
        startup_input_layout.addLayout(args_layout)
        
        # Run As
        runas_layout = QHBoxLayout()
        runas_label = QLabel("Run As:")
        runas_layout.addWidget(runas_label)
        self.runas_edit = QLineEdit()
        self.runas_edit.setPlaceholderText("Username (optional)")
        runas_layout.addWidget(self.runas_edit)
        startup_input_layout.addLayout(runas_layout)
        
        # Wait
        wait_layout = QHBoxLayout()
        wait_label = QLabel("Wait:")
        wait_layout.addWidget(wait_label)
        self.wait_combo = QComboBox()
        self.wait_combo.addItems(["Yes", "No"])
        wait_layout.addWidget(self.wait_combo)
        startup_input_layout.addLayout(wait_layout)
        
        startup_layout.addWidget(startup_input)
        
        # Startup buttons
        startup_buttons = QHBoxLayout()
        add_startup = QPushButton("Add Startup")
        add_startup.clicked.connect(self.add_startup)
        startup_buttons.addWidget(add_startup)
        
        delete_startup = QPushButton("Delete Startup")
        delete_startup.clicked.connect(self.delete_startup)
        startup_buttons.addWidget(delete_startup)
        
        startup_layout.addLayout(startup_buttons)
        tabs.addTab(startup_widget, "Startup")
        
        # Processes tab
        processes_widget = QWidget()
        processes_layout = QVBoxLayout(processes_widget)
        
        # Stop processes section
        stop_label = QLabel("Stop Processes")
        processes_layout.addWidget(stop_label)
        
        self.stop_tree = QTreeWidget()
        self.stop_tree.setHeaderLabels([
            "Name/Path",
            "Force",
            "Timeout"
        ])
        self.stop_tree.setColumnWidth(0, 300)
        processes_layout.addWidget(self.stop_tree)
        
        # Stop process input
        stop_input = QWidget()
        stop_input_layout = QVBoxLayout(stop_input)
        
        # Process name/path
        stop_name_layout = QHBoxLayout()
        stop_name_label = QLabel("Name/Path:")
        stop_name_layout.addWidget(stop_name_label)
        self.stop_name_edit = QLineEdit()
        self.stop_name_edit.setPlaceholderText("Process name or full path")
        stop_name_layout.addWidget(self.stop_name_edit)
        stop_input_layout.addLayout(stop_name_layout)
        
        # Force
        force_layout = QHBoxLayout()
        force_label = QLabel("Force:")
        force_layout.addWidget(force_label)
        self.force_combo = QComboBox()
        self.force_combo.addItems(["Yes", "No"])
        force_layout.addWidget(self.force_combo)
        stop_input_layout.addLayout(force_layout)
        
        # Timeout
        timeout_layout = QHBoxLayout()
        timeout_label = QLabel("Timeout (s):")
        timeout_layout.addWidget(timeout_label)
        self.timeout_edit = QLineEdit()
        self.timeout_edit.setPlaceholderText("30")
        timeout_layout.addWidget(self.timeout_edit)
        stop_input_layout.addLayout(timeout_layout)
        
        processes_layout.addWidget(stop_input)
        
        # Stop process buttons
        stop_buttons = QHBoxLayout()
        add_stop = QPushButton("Add Stop Process")
        add_stop.clicked.connect(self.add_stop_process)
        stop_buttons.addWidget(add_stop)
        
        delete_stop = QPushButton("Delete Stop Process")
        delete_stop.clicked.connect(self.delete_stop_process)
        stop_buttons.addWidget(delete_stop)
        
        processes_layout.addLayout(stop_buttons)
        
        # Start processes section
        start_label = QLabel("Start Processes")
        processes_layout.addWidget(start_label)
        
        self.start_tree = QTreeWidget()
        self.start_tree.setHeaderLabels([
            "Path",
            "Arguments",
            "Run As",
            "Wait"
        ])
        self.start_tree.setColumnWidth(0, 300)
        self.start_tree.setColumnWidth(1, 200)
        processes_layout.addWidget(self.start_tree)
        
        # Start process input
        start_input = QWidget()
        start_input_layout = QVBoxLayout(start_input)
        
        # Process path
        start_path_layout = QHBoxLayout()
        start_path_label = QLabel("Path:")
        start_path_layout.addWidget(start_path_label)
        self.start_path_edit = QLineEdit()
        self.start_path_edit.setPlaceholderText("Full path to process")
        start_path_layout.addWidget(self.start_path_edit)
        start_input_layout.addLayout(start_path_layout)
        
        # Process arguments
        start_args_layout = QHBoxLayout()
        start_args_label = QLabel("Arguments:")
        start_args_layout.addWidget(start_args_label)
        self.start_args_edit = QLineEdit()
        self.start_args_edit.setPlaceholderText("Command line arguments (optional)")
        start_args_layout.addWidget(self.start_args_edit)
        start_input_layout.addLayout(start_args_layout)
        
        # Run As
        start_runas_layout = QHBoxLayout()
        start_runas_label = QLabel("Run As:")
        start_runas_layout.addWidget(start_runas_label)
        self.start_runas_edit = QLineEdit()
        self.start_runas_edit.setPlaceholderText("Username (optional)")
        start_runas_layout.addWidget(self.start_runas_edit)
        start_input_layout.addLayout(start_runas_layout)
        
        # Wait
        start_wait_layout = QHBoxLayout()
        start_wait_label = QLabel("Wait:")
        start_wait_layout.addWidget(start_wait_label)
        self.start_wait_combo = QComboBox()
        self.start_wait_combo.addItems(["Yes", "No"])
        start_wait_layout.addWidget(self.start_wait_combo)
        start_input_layout.addLayout(start_wait_layout)
        
        processes_layout.addWidget(start_input)
        
        # Start process buttons
        start_buttons = QHBoxLayout()
        add_start = QPushButton("Add Start Process")
        add_start.clicked.connect(self.add_start_process)
        start_buttons.addWidget(add_start)
        
        delete_start = QPushButton("Delete Start Process")
        delete_start.clicked.connect(self.delete_start_process)
        start_buttons.addWidget(delete_start)
        
        processes_layout.addLayout(start_buttons)
        
        tabs.addTab(processes_widget, "Processes")
        
        self.layout.addWidget(tabs)
        
    def add_startup(self):
        """Add startup application entry."""
        path = self.path_edit.text().strip()
        args = self.args_edit.text().strip()
        runas = self.runas_edit.text().strip()
        wait = self.wait_combo.currentText()
        
        if not path:
            QMessageBox.warning(self, "Warning", "Path is required.")
            return
            
        item = QTreeWidgetItem([
            path,
            args,
            runas,
            wait
        ])
        self.startup_tree.addTopLevelItem(item)
        
        # Clear input fields
        self.path_edit.clear()
        self.args_edit.clear()
        self.runas_edit.clear()
        
        self.update_config_from_ui()
        
    def delete_startup(self):
        """Delete selected startup entry."""
        item = self.startup_tree.currentItem()
        if item:
            self.startup_tree.takeTopLevelItem(
                self.startup_tree.indexOfTopLevelItem(item)
            )
            self.update_config_from_ui()
            
    def add_stop_process(self):
        """Add stop process entry."""
        name = self.stop_name_edit.text().strip()
        force = self.force_combo.currentText()
        timeout = self.timeout_edit.text().strip() or "30"
        
        if not name:
            QMessageBox.warning(self, "Warning", "Name/Path is required.")
            return
            
        try:
            timeout = int(timeout)
        except ValueError:
            QMessageBox.warning(self, "Warning", "Timeout must be a number.")
            return
            
        item = QTreeWidgetItem([
            name,
            force,
            str(timeout)
        ])
        self.stop_tree.addTopLevelItem(item)
        
        # Clear input fields
        self.stop_name_edit.clear()
        self.timeout_edit.clear()
        
        self.update_config_from_ui()
        
    def delete_stop_process(self):
        """Delete selected stop process entry."""
        item = self.stop_tree.currentItem()
        if item:
            self.stop_tree.takeTopLevelItem(
                self.stop_tree.indexOfTopLevelItem(item)
            )
            self.update_config_from_ui()
            
    def add_start_process(self):
        """Add start process entry."""
        path = self.start_path_edit.text().strip()
        args = self.start_args_edit.text().strip()
        runas = self.start_runas_edit.text().strip()
        wait = self.start_wait_combo.currentText()
        
        if not path:
            QMessageBox.warning(self, "Warning", "Path is required.")
            return
            
        item = QTreeWidgetItem([
            path,
            args,
            runas,
            wait
        ])
        self.start_tree.addTopLevelItem(item)
        
        # Clear input fields
        self.start_path_edit.clear()
        self.start_args_edit.clear()
        self.start_runas_edit.clear()
        
        self.update_config_from_ui()
        
    def delete_start_process(self):
        """Delete selected start process entry."""
        item = self.start_tree.currentItem()
        if item:
            self.start_tree.takeTopLevelItem(
                self.start_tree.indexOfTopLevelItem(item)
            )
            self.update_config_from_ui()
            
    def update_config_from_ui(self):
        """Update configuration from UI elements."""
        config = {
            "startup": [],
            "processes": {
                "stop": [],
                "start": []
            }
        }
        
        # Get startup entries
        for i in range(self.startup_tree.topLevelItemCount()):
            item = self.startup_tree.topLevelItem(i)
            config["startup"].append({
                "path": item.text(0),
                "arguments": item.text(1),
                "run_as": item.text(2),
                "wait": item.text(3) == "Yes"
            })
            
        # Get stop process entries
        for i in range(self.stop_tree.topLevelItemCount()):
            item = self.stop_tree.topLevelItem(i)
            config["processes"]["stop"].append({
                "name": item.text(0),
                "force": item.text(1) == "Yes",
                "timeout": int(item.text(2))
            })
            
        # Get start process entries
        for i in range(self.start_tree.topLevelItemCount()):
            item = self.start_tree.topLevelItem(i)
            config["processes"]["start"].append({
                "path": item.text(0),
                "arguments": item.text(1),
                "run_as": item.text(2),
                "wait": item.text(3) == "Yes"
            })
            
        self.update_config(config)
        
    def on_config_changed(self):
        """Handle configuration changes."""
        config = self.get_config()
        
        # Clear existing items
        self.startup_tree.clear()
        self.stop_tree.clear()
        self.start_tree.clear()
        
        # Add startup entries
        for entry in config.get("startup", []):
            item = QTreeWidgetItem([
                entry["path"],
                entry.get("arguments", ""),
                entry.get("run_as", ""),
                "Yes" if entry.get("wait", False) else "No"
            ])
            self.startup_tree.addTopLevelItem(item)
            
        # Add stop process entries
        for entry in config.get("processes", {}).get("stop", []):
            item = QTreeWidgetItem([
                entry["name"],
                "Yes" if entry.get("force", False) else "No",
                str(entry.get("timeout", 30))
            ])
            self.stop_tree.addTopLevelItem(item)
            
        # Add start process entries
        for entry in config.get("processes", {}).get("start", []):
            item = QTreeWidgetItem([
                entry["path"],
                entry.get("arguments", ""),
                entry.get("run_as", ""),
                "Yes" if entry.get("wait", False) else "No"
            ])
            self.start_tree.addTopLevelItem(item)
