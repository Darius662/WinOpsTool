"""Software installation configuration tab."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox, QComboBox)
from .base_tab import BaseConfigTab

class SoftwareTab(BaseConfigTab):
    """Tab for configuring software installation and uninstallation."""
    
    def __init__(self, config_handler):
        super().__init__(config_handler, "software")
        
    def setup_ui(self):
        """Set up the tab's user interface."""
        # Create tabs for Install and Uninstall
        install_widget = QWidget()
        install_layout = QVBoxLayout(install_widget)
        
        # Install section
        install_label = QLabel("Software to Install")
        install_layout.addWidget(install_label)
        
        self.install_tree = QTreeWidget()
        self.install_tree.setHeaderLabels([
            "Path",
            "Arguments",
            "Wait",
            "Expected Return Code"
        ])
        self.install_tree.setColumnWidth(0, 300)
        self.install_tree.setColumnWidth(1, 200)
        install_layout.addWidget(self.install_tree)
        
        # Install input fields
        install_input = QWidget()
        install_input_layout = QVBoxLayout(install_input)
        
        # Install path
        path_layout = QHBoxLayout()
        path_label = QLabel("Install Path:")
        path_layout.addWidget(path_label)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Full path to installer (MSI/EXE)")
        path_layout.addWidget(self.path_edit)
        install_input_layout.addLayout(path_layout)
        
        # Install arguments
        args_layout = QHBoxLayout()
        args_label = QLabel("Arguments:")
        args_layout.addWidget(args_label)
        self.args_edit = QLineEdit()
        self.args_edit.setPlaceholderText("Installation arguments (optional)")
        args_layout.addWidget(self.args_edit)
        install_input_layout.addLayout(args_layout)
        
        # Wait for completion
        wait_layout = QHBoxLayout()
        wait_label = QLabel("Wait:")
        wait_layout.addWidget(wait_label)
        self.wait_combo = QComboBox()
        self.wait_combo.addItems(["Yes", "No"])
        wait_layout.addWidget(self.wait_combo)
        install_input_layout.addLayout(wait_layout)
        
        # Expected return code
        return_layout = QHBoxLayout()
        return_label = QLabel("Expected Return Code:")
        return_layout.addWidget(return_label)
        self.return_edit = QLineEdit()
        self.return_edit.setPlaceholderText("0")
        return_layout.addWidget(self.return_edit)
        install_input_layout.addLayout(return_layout)
        
        install_layout.addWidget(install_input)
        
        # Install buttons
        install_buttons = QHBoxLayout()
        add_install = QPushButton("Add Install")
        add_install.clicked.connect(self.add_install)
        install_buttons.addWidget(add_install)
        
        delete_install = QPushButton("Delete Install")
        delete_install.clicked.connect(self.delete_install)
        install_buttons.addWidget(delete_install)
        
        install_layout.addLayout(install_buttons)
        
        # Uninstall section
        uninstall_widget = QWidget()
        uninstall_layout = QVBoxLayout(uninstall_widget)
        
        uninstall_label = QLabel("Software to Uninstall")
        uninstall_layout.addWidget(uninstall_label)
        
        self.uninstall_tree = QTreeWidget()
        self.uninstall_tree.setHeaderLabels([
            "Name/ID",
            "Method",
            "Arguments"
        ])
        self.uninstall_tree.setColumnWidth(0, 300)
        self.uninstall_tree.setColumnWidth(1, 100)
        uninstall_layout.addWidget(self.uninstall_tree)
        
        # Uninstall input fields
        uninstall_input = QWidget()
        uninstall_input_layout = QVBoxLayout(uninstall_input)
        
        # Uninstall name/ID
        name_layout = QHBoxLayout()
        name_label = QLabel("Name/ID:")
        name_layout.addWidget(name_label)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Program name or Product ID")
        name_layout.addWidget(self.name_edit)
        uninstall_input_layout.addLayout(name_layout)
        
        # Uninstall method
        method_layout = QHBoxLayout()
        method_label = QLabel("Method:")
        method_layout.addWidget(method_label)
        self.method_combo = QComboBox()
        self.method_combo.addItems(["MSI", "EXE", "Registry"])
        method_layout.addWidget(self.method_combo)
        uninstall_input_layout.addLayout(method_layout)
        
        # Uninstall arguments
        uninstall_args_layout = QHBoxLayout()
        uninstall_args_label = QLabel("Arguments:")
        uninstall_args_layout.addWidget(uninstall_args_label)
        self.uninstall_args_edit = QLineEdit()
        self.uninstall_args_edit.setPlaceholderText("Uninstall arguments (optional)")
        uninstall_args_layout.addWidget(self.uninstall_args_edit)
        uninstall_input_layout.addLayout(uninstall_args_layout)
        
        uninstall_layout.addWidget(uninstall_input)
        
        # Uninstall buttons
        uninstall_buttons = QHBoxLayout()
        add_uninstall = QPushButton("Add Uninstall")
        add_uninstall.clicked.connect(self.add_uninstall)
        uninstall_buttons.addWidget(add_uninstall)
        
        delete_uninstall = QPushButton("Delete Uninstall")
        delete_uninstall.clicked.connect(self.delete_uninstall)
        uninstall_buttons.addWidget(delete_uninstall)
        
        uninstall_layout.addLayout(uninstall_buttons)
        
        # Add both sections to main layout
        self.layout.addWidget(install_widget)
        self.layout.addWidget(uninstall_widget)
        
    def add_install(self):
        """Add software installation entry."""
        path = self.path_edit.text().strip()
        args = self.args_edit.text().strip()
        wait = self.wait_combo.currentText() == "Yes"
        return_code = self.return_edit.text().strip() or "0"
        
        if not path:
            QMessageBox.warning(self, "Warning", "Install path is required.")
            return
            
        try:
            return_code = int(return_code)
        except ValueError:
            QMessageBox.warning(self, "Warning", "Return code must be a number.")
            return
            
        item = QTreeWidgetItem([
            path,
            args,
            "Yes" if wait else "No",
            str(return_code)
        ])
        self.install_tree.addTopLevelItem(item)
        
        # Clear input fields
        self.path_edit.clear()
        self.args_edit.clear()
        self.return_edit.clear()
        
        self.update_config_from_ui()
        
    def delete_install(self):
        """Delete selected installation entry."""
        item = self.install_tree.currentItem()
        if item:
            self.install_tree.takeTopLevelItem(
                self.install_tree.indexOfTopLevelItem(item)
            )
            self.update_config_from_ui()
            
    def add_uninstall(self):
        """Add software uninstallation entry."""
        name = self.name_edit.text().strip()
        method = self.method_combo.currentText()
        args = self.uninstall_args_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Warning", "Name/ID is required.")
            return
            
        item = QTreeWidgetItem([
            name,
            method,
            args
        ])
        self.uninstall_tree.addTopLevelItem(item)
        
        # Clear input fields
        self.name_edit.clear()
        self.uninstall_args_edit.clear()
        
        self.update_config_from_ui()
        
    def delete_uninstall(self):
        """Delete selected uninstallation entry."""
        item = self.uninstall_tree.currentItem()
        if item:
            self.uninstall_tree.takeTopLevelItem(
                self.uninstall_tree.indexOfTopLevelItem(item)
            )
            self.update_config_from_ui()
            
    def update_config_from_ui(self):
        """Update configuration from UI elements."""
        config = {
            "install": [],
            "uninstall": []
        }
        
        # Get install entries
        for i in range(self.install_tree.topLevelItemCount()):
            item = self.install_tree.topLevelItem(i)
            config["install"].append({
                "path": item.text(0),
                "arguments": item.text(1),
                "wait": item.text(2) == "Yes",
                "return_code": int(item.text(3))
            })
            
        # Get uninstall entries
        for i in range(self.uninstall_tree.topLevelItemCount()):
            item = self.uninstall_tree.topLevelItem(i)
            config["uninstall"].append({
                "name": item.text(0),
                "method": item.text(1).lower(),
                "arguments": item.text(2)
            })
            
        self.update_config(config)
        
    def on_config_changed(self):
        """Handle configuration changes."""
        config = self.get_config()
        
        # Clear existing items
        self.install_tree.clear()
        self.uninstall_tree.clear()
        
        # Add install entries
        for entry in config.get("install", []):
            item = QTreeWidgetItem([
                entry["path"],
                entry.get("arguments", ""),
                "Yes" if entry.get("wait", True) else "No",
                str(entry.get("return_code", 0))
            ])
            self.install_tree.addTopLevelItem(item)
            
        # Add uninstall entries
        for entry in config.get("uninstall", []):
            item = QTreeWidgetItem([
                entry["name"],
                entry["method"].upper(),
                entry.get("arguments", "")
            ])
            self.uninstall_tree.addTopLevelItem(item)
