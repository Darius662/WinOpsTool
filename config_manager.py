"""Configuration Manager for Windows System Management Tool."""
import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget,
                          QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                          QLineEdit, QTextEdit, QFileDialog, QMessageBox,
                          QTreeWidget, QTreeWidgetItem, QComboBox, QSplitter)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
import yaml
from src.core.config_schema import CONFIG_SCHEMA
from src.core.logger import setup_logger

class HelpWindow(QMainWindow):
    """Help window for Configuration Manager."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuration Manager Help")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Overview tab
        overview = QWidget()
        overview_layout = QVBoxLayout(overview)
        overview_text = QTextEdit()
        overview_text.setReadOnly(True)
        overview_text.setHtml("""
        <h2>Configuration Manager</h2>
        <p>The Configuration Manager is a tool for creating and managing system configuration files 
        that can be imported into the main System Management Tool.</p>
        
        <h3>Key Features</h3>
        <ul>
            <li>Create and edit configuration files in YAML format</li>
            <li>Configure multiple system aspects in one place</li>
            <li>Save and load configurations</li>
            <li>Import configurations into main System Management Tool</li>
        </ul>
        
        <h3>Basic Usage</h3>
        <ol>
            <li>Use the tabs to configure different aspects of the system</li>
            <li>Save your configuration using File -> Save Config</li>
            <li>Import the saved configuration file in the main System Management Tool</li>
        </ol>
        """)
        overview_layout.addWidget(overview_text)
        tabs.addTab(overview, "Overview")
        
        # Tabs help
        tabs_help = QWidget()
        tabs_layout = QVBoxLayout(tabs_help)
        tabs_text = QTextEdit()
        tabs_text.setReadOnly(True)
        tabs_text.setHtml("""
        <h2>Configuration Tabs</h2>
        
        <h3>Environment Variables</h3>
        <p>Configure system and user environment variables:</p>
        <ul>
            <li>Add/remove system-wide variables</li>
            <li>Add/remove user-specific variables</li>
        </ul>
        
        <h3>Registry Editor</h3>
        <p>Manage Windows Registry settings:</p>
        <ul>
            <li>Add registry values with different types</li>
            <li>Specify registry paths and values</li>
            <li>Support for REG_SZ, REG_DWORD, etc.</li>
        </ul>
        
        <h3>Users & Groups</h3>
        <p>Configure user accounts and group memberships:</p>
        <ul>
            <li>Create user accounts with passwords</li>
            <li>Define group memberships</li>
            <li>Add users to groups</li>
        </ul>
        
        <h3>Services</h3>
        <p>Manage Windows services configuration:</p>
        <ul>
            <li>Set service startup types</li>
            <li>Configure service states</li>
            <li>Add service descriptions</li>
        </ul>
        
        <h3>Firewall</h3>
        <p>Configure Windows Firewall rules:</p>
        <ul>
            <li>Create inbound/outbound rules</li>
            <li>Set protocols and ports</li>
            <li>Configure allow/block actions</li>
        </ul>
        
        <h3>Software</h3>
        <p>Manage software installation/uninstallation:</p>
        <ul>
            <li>Configure MSI/EXE installations</li>
            <li>Set installation arguments</li>
            <li>Specify software to remove</li>
        </ul>
        
        <h3>Permissions</h3>
        <p>Set file and folder permissions:</p>
        <ul>
            <li>Configure access rights</li>
            <li>Set user/group permissions</li>
            <li>Allow/deny access</li>
        </ul>
        
        <h3>Applications</h3>
        <p>Manage applications and processes:</p>
        <ul>
            <li>Configure startup applications</li>
            <li>Set up processes to run</li>
            <li>Configure run-as settings</li>
        </ul>
        """)
        tabs_layout.addWidget(tabs_text)
        tabs.addTab(tabs_help, "Tabs Guide")


class ConfigManagerWindow(QMainWindow):
    """Main window for the Configuration Manager."""
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger(self.__class__.__name__)
        self.config = self.create_empty_config()
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Windows System Management Tool - Configuration Manager")
        self.setMinimumSize(800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Tabs for different sections
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Add configuration sections
        self.add_env_vars_tab()
        self.add_registry_tab()
        self.add_users_groups_tab()
        self.add_services_tab()
        self.add_firewall_tab()
        self.add_software_tab()
        self.add_permissions_tab()
        self.add_applications_tab()
        
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        save_action = QAction("Save Config", self)
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)
        
        load_action = QAction("Load Config", self)
        load_action.triggered.connect(self.load_config)
        file_menu.addAction(load_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        help_action = QAction("Help Contents", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        load_btn = QPushButton("Load Config")
        save_btn = QPushButton("Save Config")
        clear_btn = QPushButton("Clear All")
        
        load_btn.clicked.connect(self.load_config)
        save_btn.clicked.connect(self.save_config)
        clear_btn.clicked.connect(self.clear_config)
        
        button_layout.addWidget(load_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
    def add_env_vars_tab(self):
        """Add Environment Variables configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # System variables
        layout.addWidget(QLabel("System Variables:"))
        self.system_vars_tree = QTreeWidget()
        self.system_vars_tree.setHeaderLabels(["Name", "Value"])
        layout.addWidget(self.system_vars_tree)
        
        # Add system variable
        sys_add_layout = QHBoxLayout()
        self.sys_name_edit = QLineEdit()
        self.sys_value_edit = QLineEdit()
        add_sys_btn = QPushButton("Add System Variable")
        
        sys_add_layout.addWidget(QLabel("Name:"))
        sys_add_layout.addWidget(self.sys_name_edit)
        sys_add_layout.addWidget(QLabel("Value:"))
        sys_add_layout.addWidget(self.sys_value_edit)
        sys_add_layout.addWidget(add_sys_btn)
        
        layout.addLayout(sys_add_layout)
        
        # User variables
        layout.addWidget(QLabel("User Variables:"))
        self.user_vars_tree = QTreeWidget()
        self.user_vars_tree.setHeaderLabels(["Name", "Value"])
        layout.addWidget(self.user_vars_tree)
        
        # Add user variable
        user_add_layout = QHBoxLayout()
        self.user_name_edit = QLineEdit()
        self.user_value_edit = QLineEdit()
        add_user_btn = QPushButton("Add User Variable")
        
        user_add_layout.addWidget(QLabel("Name:"))
        user_add_layout.addWidget(self.user_name_edit)
        user_add_layout.addWidget(QLabel("Value:"))
        user_add_layout.addWidget(self.user_value_edit)
        user_add_layout.addWidget(add_user_btn)
        
        layout.addLayout(user_add_layout)
        
        # Connect signals
        add_sys_btn.clicked.connect(self.add_system_var)
        add_user_btn.clicked.connect(self.add_user_var)
        
        self.tabs.addTab(tab, "Environment Variables")
        
    def add_system_var(self):
        """Add a system environment variable."""
        name = self.sys_name_edit.text().strip()
        value = self.sys_value_edit.text().strip()
        
        if name and value:
            item = QTreeWidgetItem([name, value])
            self.system_vars_tree.addTopLevelItem(item)
            self.sys_name_edit.clear()
            self.sys_value_edit.clear()
            
    def add_user_var(self):
        """Add a user environment variable."""
        name = self.user_name_edit.text().strip()
        value = self.user_value_edit.text().strip()
        
        if name and value:
            item = QTreeWidgetItem([name, value])
            self.user_vars_tree.addTopLevelItem(item)
            self.user_name_edit.clear()
            self.user_value_edit.clear()
            
    def add_registry_tab(self):
        """Add Registry configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Registry tree
        self.registry_tree = QTreeWidget()
        self.registry_tree.setHeaderLabels(["Path", "Name", "Type", "Value"])
        self.registry_tree.setColumnWidth(0, 300)
        layout.addWidget(self.registry_tree)
        
        # Add registry key/value
        add_layout = QHBoxLayout()
        
        self.reg_path_edit = QLineEdit()
        self.reg_path_edit.setPlaceholderText("Registry Path (e.g. HKLM\Software\MyApp)")
        self.reg_name_edit = QLineEdit()
        self.reg_name_edit.setPlaceholderText("Value Name")
        
        self.reg_type_combo = QComboBox()
        self.reg_type_combo.addItems(["REG_SZ", "REG_DWORD", "REG_BINARY", "REG_MULTI_SZ"])
        
        self.reg_value_edit = QLineEdit()
        self.reg_value_edit.setPlaceholderText("Value Data")
        
        add_btn = QPushButton("Add Registry Value")
        add_btn.clicked.connect(self.add_registry_value)
        
        add_layout.addWidget(self.reg_path_edit)
        add_layout.addWidget(self.reg_name_edit)
        add_layout.addWidget(self.reg_type_combo)
        add_layout.addWidget(self.reg_value_edit)
        add_layout.addWidget(add_btn)
        
        layout.addLayout(add_layout)
        
        # Delete button
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_registry_value)
        layout.addWidget(delete_btn)
        
        self.tabs.addTab(tab, "Registry")
        
    def add_registry_value(self):
        """Add a registry value to the tree."""
        path = self.reg_path_edit.text().strip()
        name = self.reg_name_edit.text().strip()
        value_type = self.reg_type_combo.currentText()
        value = self.reg_value_edit.text().strip()
        
        if path and name:
            # Find or create path item
            path_items = self.registry_tree.findItems(path, Qt.MatchFlag.MatchExactly, 0)
            if path_items:
                path_item = path_items[0]
            else:
                path_item = QTreeWidgetItem([path])
                self.registry_tree.addTopLevelItem(path_item)
            
            # Add value item
            value_item = QTreeWidgetItem([path, name, value_type, value])
            path_item.addChild(value_item)
            
            # Clear inputs
            self.reg_name_edit.clear()
            self.reg_value_edit.clear()
            
    def delete_registry_value(self):
        """Delete selected registry value."""
        selected = self.registry_tree.selectedItems()
        if selected:
            item = selected[0]
            if item.parent():
                # This is a value item
                item.parent().removeChild(item)
            else:
                # This is a path item
                index = self.registry_tree.indexOfTopLevelItem(item)
                self.registry_tree.takeTopLevelItem(index)
        
    def add_users_groups_tab(self):
        """Add Users & Groups configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Split into users and groups sections
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Users section
        users_widget = QWidget()
        users_layout = QVBoxLayout(users_widget)
        
        users_layout.addWidget(QLabel("Users:"))
        self.users_tree = QTreeWidget()
        self.users_tree.setHeaderLabels(["Username", "Groups", "Comment"])
        users_layout.addWidget(self.users_tree)
        
        # Add user controls
        user_add_layout = QHBoxLayout()
        
        self.user_name_edit = QLineEdit()
        self.user_name_edit.setPlaceholderText("Username")
        self.user_password_edit = QLineEdit()
        self.user_password_edit.setPlaceholderText("Password")
        self.user_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.user_groups_edit = QLineEdit()
        self.user_groups_edit.setPlaceholderText("Groups (comma-separated)")
        self.user_comment_edit = QLineEdit()
        self.user_comment_edit.setPlaceholderText("Comment")
        
        add_user_btn = QPushButton("Add User")
        add_user_btn.clicked.connect(self.add_user)
        
        user_add_layout.addWidget(self.user_name_edit)
        user_add_layout.addWidget(self.user_password_edit)
        user_add_layout.addWidget(self.user_groups_edit)
        user_add_layout.addWidget(self.user_comment_edit)
        user_add_layout.addWidget(add_user_btn)
        
        users_layout.addLayout(user_add_layout)
        
        # Delete user button
        delete_user_btn = QPushButton("Delete Selected User")
        delete_user_btn.clicked.connect(self.delete_user)
        users_layout.addWidget(delete_user_btn)
        
        splitter.addWidget(users_widget)
        
        # Groups section
        groups_widget = QWidget()
        groups_layout = QVBoxLayout(groups_widget)
        
        groups_layout.addWidget(QLabel("Groups:"))
        self.groups_tree = QTreeWidget()
        self.groups_tree.setHeaderLabels(["Group Name", "Members", "Comment"])
        groups_layout.addWidget(self.groups_tree)
        
        # Add group controls
        group_add_layout = QHBoxLayout()
        
        self.group_name_edit = QLineEdit()
        self.group_name_edit.setPlaceholderText("Group Name")
        self.group_members_edit = QLineEdit()
        self.group_members_edit.setPlaceholderText("Members (comma-separated)")
        self.group_comment_edit = QLineEdit()
        self.group_comment_edit.setPlaceholderText("Comment")
        
        add_group_btn = QPushButton("Add Group")
        add_group_btn.clicked.connect(self.add_group)
        
        group_add_layout.addWidget(self.group_name_edit)
        group_add_layout.addWidget(self.group_members_edit)
        group_add_layout.addWidget(self.group_comment_edit)
        group_add_layout.addWidget(add_group_btn)
        
        groups_layout.addLayout(group_add_layout)
        
        # Delete group button
        delete_group_btn = QPushButton("Delete Selected Group")
        delete_group_btn.clicked.connect(self.delete_group)
        groups_layout.addWidget(delete_group_btn)
        
        splitter.addWidget(groups_widget)
        
        self.tabs.addTab(tab, "Users & Groups")
        
    def add_user(self):
        """Add a user to the tree."""
        name = self.user_name_edit.text().strip()
        password = self.user_password_edit.text()
        groups = [g.strip() for g in self.user_groups_edit.text().split(",") if g.strip()]
        comment = self.user_comment_edit.text().strip()
        
        if name and password:
            item = QTreeWidgetItem([name, ", ".join(groups), comment])
            self.users_tree.addTopLevelItem(item)
            
            # Clear inputs
            self.user_name_edit.clear()
            self.user_password_edit.clear()
            self.user_groups_edit.clear()
            self.user_comment_edit.clear()
            
    def delete_user(self):
        """Delete selected user."""
        selected = self.users_tree.selectedItems()
        if selected:
            index = self.users_tree.indexOfTopLevelItem(selected[0])
            self.users_tree.takeTopLevelItem(index)
            
    def add_group(self):
        """Add a group to the tree."""
        name = self.group_name_edit.text().strip()
        members = [m.strip() for m in self.group_members_edit.text().split(",") if m.strip()]
        comment = self.group_comment_edit.text().strip()
        
        if name:
            item = QTreeWidgetItem([name, ", ".join(members), comment])
            self.groups_tree.addTopLevelItem(item)
            
            # Clear inputs
            self.group_name_edit.clear()
            self.group_members_edit.clear()
            self.group_comment_edit.clear()
            
    def delete_group(self):
        """Delete selected group."""
        selected = self.groups_tree.selectedItems()
        if selected:
            index = self.groups_tree.indexOfTopLevelItem(selected[0])
            self.groups_tree.takeTopLevelItem(index)
        
    def add_services_tab(self):
        """Add Services configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Services list
        self.services_tree = QTreeWidget()
        self.services_tree.setHeaderLabels(["Service Name", "Start Type", "State", "Description"])
        self.services_tree.setColumnWidth(0, 200)
        self.services_tree.setColumnWidth(3, 300)
        layout.addWidget(self.services_tree)
        
        # Add service controls
        add_layout = QHBoxLayout()
        
        self.service_name_edit = QLineEdit()
        self.service_name_edit.setPlaceholderText("Service Name")
        
        self.service_start_combo = QComboBox()
        self.service_start_combo.addItems(["auto", "manual", "disabled"])
        
        self.service_state_combo = QComboBox()
        self.service_state_combo.addItems(["start", "stop", "restart"])
        
        self.service_desc_edit = QLineEdit()
        self.service_desc_edit.setPlaceholderText("Description")
        
        add_btn = QPushButton("Add Service")
        add_btn.clicked.connect(self.add_service)
        
        add_layout.addWidget(self.service_name_edit)
        add_layout.addWidget(QLabel("Start Type:"))
        add_layout.addWidget(self.service_start_combo)
        add_layout.addWidget(QLabel("State:"))
        add_layout.addWidget(self.service_state_combo)
        add_layout.addWidget(self.service_desc_edit)
        add_layout.addWidget(add_btn)
        
        layout.addLayout(add_layout)
        
        # Delete button
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_service)
        layout.addWidget(delete_btn)
        
        self.tabs.addTab(tab, "Services")
        
    def add_service(self):
        """Add a service to the tree."""
        name = self.service_name_edit.text().strip()
        start_type = self.service_start_combo.currentText()
        state = self.service_state_combo.currentText()
        description = self.service_desc_edit.text().strip()
        
        if name:
            item = QTreeWidgetItem([name, start_type, state, description])
            self.services_tree.addTopLevelItem(item)
            
            # Clear inputs
            self.service_name_edit.clear()
            self.service_desc_edit.clear()
            
    def delete_service(self):
        """Delete selected service."""
        selected = self.services_tree.selectedItems()
        if selected:
            index = self.services_tree.indexOfTopLevelItem(selected[0])
            self.services_tree.takeTopLevelItem(index)
        
    def add_firewall_tab(self):
        """Add Firewall configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Firewall rules list
        self.firewall_tree = QTreeWidget()
        self.firewall_tree.setHeaderLabels(["Rule Name", "Direction", "Action", "Protocol", "Local Ports", "Remote Ports", "Enabled"])
        self.firewall_tree.setColumnWidth(0, 200)
        layout.addWidget(self.firewall_tree)
        
        # Add rule controls
        add_layout = QHBoxLayout()
        
        self.rule_name_edit = QLineEdit()
        self.rule_name_edit.setPlaceholderText("Rule Name")
        
        self.rule_direction_combo = QComboBox()
        self.rule_direction_combo.addItems(["in", "out"])
        
        self.rule_action_combo = QComboBox()
        self.rule_action_combo.addItems(["allow", "block"])
        
        self.rule_protocol_edit = QLineEdit()
        self.rule_protocol_edit.setPlaceholderText("Protocol (e.g. TCP)")
        
        self.rule_local_ports_edit = QLineEdit()
        self.rule_local_ports_edit.setPlaceholderText("Local Ports (comma-separated)")
        
        self.rule_remote_ports_edit = QLineEdit()
        self.rule_remote_ports_edit.setPlaceholderText("Remote Ports (comma-separated)")
        
        self.rule_enabled_combo = QComboBox()
        self.rule_enabled_combo.addItems(["True", "False"])
        
        add_btn = QPushButton("Add Rule")
        add_btn.clicked.connect(self.add_firewall_rule)
        
        add_layout.addWidget(self.rule_name_edit)
        add_layout.addWidget(QLabel("Direction:"))
        add_layout.addWidget(self.rule_direction_combo)
        add_layout.addWidget(QLabel("Action:"))
        add_layout.addWidget(self.rule_action_combo)
        add_layout.addWidget(self.rule_protocol_edit)
        add_layout.addWidget(self.rule_local_ports_edit)
        add_layout.addWidget(self.rule_remote_ports_edit)
        add_layout.addWidget(QLabel("Enabled:"))
        add_layout.addWidget(self.rule_enabled_combo)
        add_layout.addWidget(add_btn)
        
        layout.addLayout(add_layout)
        
        # Delete button
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_firewall_rule)
        layout.addWidget(delete_btn)
        
        self.tabs.addTab(tab, "Firewall")
        
    def add_firewall_rule(self):
        """Add a firewall rule to the tree."""
        name = self.rule_name_edit.text().strip()
        direction = self.rule_direction_combo.currentText()
        action = self.rule_action_combo.currentText()
        protocol = self.rule_protocol_edit.text().strip()
        local_ports = self.rule_local_ports_edit.text().strip()
        remote_ports = self.rule_remote_ports_edit.text().strip()
        enabled = self.rule_enabled_combo.currentText()
        
        if name and protocol:
            item = QTreeWidgetItem([name, direction, action, protocol, local_ports, remote_ports, enabled])
            self.firewall_tree.addTopLevelItem(item)
            
            # Clear inputs
            self.rule_name_edit.clear()
            self.rule_protocol_edit.clear()
            self.rule_local_ports_edit.clear()
            self.rule_remote_ports_edit.clear()
            
    def delete_firewall_rule(self):
        """Delete selected firewall rule."""
        selected = self.firewall_tree.selectedItems()
        if selected:
            index = self.firewall_tree.indexOfTopLevelItem(selected[0])
            self.firewall_tree.takeTopLevelItem(index)
        
    def add_software_tab(self):
        """Add Software configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Split into install and uninstall sections
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Install section
        install_widget = QWidget()
        install_layout = QVBoxLayout(install_widget)
        
        install_layout.addWidget(QLabel("Software to Install:"))
        self.install_tree = QTreeWidget()
        self.install_tree.setHeaderLabels(["Name", "Path", "Arguments", "Type", "Verify Path"])
        self.install_tree.setColumnWidth(0, 150)
        self.install_tree.setColumnWidth(1, 300)
        install_layout.addWidget(self.install_tree)
        
        # Add install controls
        install_add_layout = QHBoxLayout()
        
        self.install_name_edit = QLineEdit()
        self.install_name_edit.setPlaceholderText("Software Name")
        
        self.install_path_edit = QLineEdit()
        self.install_path_edit.setPlaceholderText("Installation Path")
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_install_file)
        
        self.install_args_edit = QLineEdit()
        self.install_args_edit.setPlaceholderText("Install Arguments")
        
        self.install_type_combo = QComboBox()
        self.install_type_combo.addItems(["msi", "exe"])
        
        self.install_verify_edit = QLineEdit()
        self.install_verify_edit.setPlaceholderText("Verify Path (Registry key or file)")
        
        add_install_btn = QPushButton("Add Software")
        add_install_btn.clicked.connect(self.add_install_software)
        
        install_add_layout.addWidget(self.install_name_edit)
        install_add_layout.addWidget(self.install_path_edit)
        install_add_layout.addWidget(browse_btn)
        install_add_layout.addWidget(self.install_args_edit)
        install_add_layout.addWidget(QLabel("Type:"))
        install_add_layout.addWidget(self.install_type_combo)
        install_add_layout.addWidget(self.install_verify_edit)
        install_add_layout.addWidget(add_install_btn)
        
        install_layout.addLayout(install_add_layout)
        
        # Delete install button
        delete_install_btn = QPushButton("Delete Selected")
        delete_install_btn.clicked.connect(self.delete_install_software)
        install_layout.addWidget(delete_install_btn)
        
        splitter.addWidget(install_widget)
        
        # Uninstall section
        uninstall_widget = QWidget()
        uninstall_layout = QVBoxLayout(uninstall_widget)
        
        uninstall_layout.addWidget(QLabel("Software to Uninstall:"))
        self.uninstall_tree = QTreeWidget()
        self.uninstall_tree.setHeaderLabels(["Software Name"])
        uninstall_layout.addWidget(self.uninstall_tree)
        
        # Add uninstall controls
        uninstall_add_layout = QHBoxLayout()
        
        self.uninstall_name_edit = QLineEdit()
        self.uninstall_name_edit.setPlaceholderText("Software Name")
        
        add_uninstall_btn = QPushButton("Add to Uninstall")
        add_uninstall_btn.clicked.connect(self.add_uninstall_software)
        
        uninstall_add_layout.addWidget(self.uninstall_name_edit)
        uninstall_add_layout.addWidget(add_uninstall_btn)
        
        uninstall_layout.addLayout(uninstall_add_layout)
        
        # Delete uninstall button
        delete_uninstall_btn = QPushButton("Delete Selected")
        delete_uninstall_btn.clicked.connect(self.delete_uninstall_software)
        uninstall_layout.addWidget(delete_uninstall_btn)
        
        splitter.addWidget(uninstall_widget)
        
        self.tabs.addTab(tab, "Software")
        
    def browse_install_file(self):
        """Browse for an installation file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Installation File",
            "",
            "Installation Files (*.msi *.exe);;All Files (*.*)"
        )
        
        if file_path:
            self.install_path_edit.setText(file_path)
            
            # Auto-detect type
            if file_path.lower().endswith(".msi"):
                self.install_type_combo.setCurrentText("msi")
            elif file_path.lower().endswith(".exe"):
                self.install_type_combo.setCurrentText("exe")
            
    def add_install_software(self):
        """Add software to install to the tree."""
        name = self.install_name_edit.text().strip()
        path = self.install_path_edit.text().strip()
        args = self.install_args_edit.text().strip()
        install_type = self.install_type_combo.currentText()
        verify = self.install_verify_edit.text().strip()
        
        if name and path:
            item = QTreeWidgetItem([name, path, args, install_type, verify])
            self.install_tree.addTopLevelItem(item)
            
            # Clear inputs
            self.install_name_edit.clear()
            self.install_path_edit.clear()
            self.install_args_edit.clear()
            self.install_verify_edit.clear()
            
    def delete_install_software(self):
        """Delete selected software to install."""
        selected = self.install_tree.selectedItems()
        if selected:
            index = self.install_tree.indexOfTopLevelItem(selected[0])
            self.install_tree.takeTopLevelItem(index)
            
    def add_uninstall_software(self):
        """Add software to uninstall to the tree."""
        name = self.uninstall_name_edit.text().strip()
        
        if name:
            item = QTreeWidgetItem([name])
            self.uninstall_tree.addTopLevelItem(item)
            self.uninstall_name_edit.clear()
            
    def delete_uninstall_software(self):
        """Delete selected software to uninstall."""
        selected = self.uninstall_tree.selectedItems()
        if selected:
            index = self.uninstall_tree.indexOfTopLevelItem(selected[0])
            self.uninstall_tree.takeTopLevelItem(index)
        
    def add_permissions_tab(self):
        """Add Permissions configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Permissions list
        self.permissions_tree = QTreeWidget()
        self.permissions_tree.setHeaderLabels(["Path", "User/Group", "Rights", "Type"])
        self.permissions_tree.setColumnWidth(0, 300)
        layout.addWidget(self.permissions_tree)
        
        # Add permission controls
        add_layout = QHBoxLayout()
        
        self.perm_path_edit = QLineEdit()
        self.perm_path_edit.setPlaceholderText("File/Folder Path")
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_perm_path)
        
        self.perm_account_edit = QLineEdit()
        self.perm_account_edit.setPlaceholderText("User or Group Name")
        
        self.perm_rights_combo = QComboBox()
        self.perm_rights_combo.addItems(["Full Control", "Modify", "Read & Execute", "Read", "Write"])
        
        self.perm_type_combo = QComboBox()
        self.perm_type_combo.addItems(["Allow", "Deny"])
        
        add_btn = QPushButton("Add Permission")
        add_btn.clicked.connect(self.add_permission)
        
        add_layout.addWidget(self.perm_path_edit)
        add_layout.addWidget(browse_btn)
        add_layout.addWidget(self.perm_account_edit)
        add_layout.addWidget(QLabel("Rights:"))
        add_layout.addWidget(self.perm_rights_combo)
        add_layout.addWidget(QLabel("Type:"))
        add_layout.addWidget(self.perm_type_combo)
        add_layout.addWidget(add_btn)
        
        layout.addLayout(add_layout)
        
        # Delete button
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_permission)
        layout.addWidget(delete_btn)
        
        self.tabs.addTab(tab, "Permissions")
        
    def browse_perm_path(self):
        """Browse for a file or folder to set permissions on."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            ""
        )
        
        if path:
            self.perm_path_edit.setText(path)
            
    def add_permission(self):
        """Add a permission to the tree."""
        path = self.perm_path_edit.text().strip()
        account = self.perm_account_edit.text().strip()
        rights = self.perm_rights_combo.currentText()
        perm_type = self.perm_type_combo.currentText()
        
        if path and account:
            item = QTreeWidgetItem([path, account, rights, perm_type])
            self.permissions_tree.addTopLevelItem(item)
            
            # Clear inputs
            self.perm_path_edit.clear()
            self.perm_account_edit.clear()
            
    def delete_permission(self):
        """Delete selected permission."""
        selected = self.permissions_tree.selectedItems()
        if selected:
            index = self.permissions_tree.indexOfTopLevelItem(selected[0])
            self.permissions_tree.takeTopLevelItem(index)
        
    def add_applications_tab(self):
        """Add Applications configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Split into startup and processes sections
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Startup section
        startup_widget = QWidget()
        startup_layout = QVBoxLayout(startup_widget)
        
        startup_layout.addWidget(QLabel("Startup Applications:"))
        self.startup_tree = QTreeWidget()
        self.startup_tree.setHeaderLabels(["Name", "Path", "Arguments", "Run As"])
        self.startup_tree.setColumnWidth(0, 150)
        self.startup_tree.setColumnWidth(1, 300)
        startup_layout.addWidget(self.startup_tree)
        
        # Add startup controls
        startup_add_layout = QHBoxLayout()
        
        self.startup_name_edit = QLineEdit()
        self.startup_name_edit.setPlaceholderText("Application Name")
        
        self.startup_path_edit = QLineEdit()
        self.startup_path_edit.setPlaceholderText("Application Path")
        
        browse_startup_btn = QPushButton("Browse...")
        browse_startup_btn.clicked.connect(self.browse_startup_app)
        
        self.startup_args_edit = QLineEdit()
        self.startup_args_edit.setPlaceholderText("Arguments")
        
        self.startup_runas_edit = QLineEdit()
        self.startup_runas_edit.setPlaceholderText("Run As (username)")
        
        add_startup_btn = QPushButton("Add to Startup")
        add_startup_btn.clicked.connect(self.add_startup_app)
        
        startup_add_layout.addWidget(self.startup_name_edit)
        startup_add_layout.addWidget(self.startup_path_edit)
        startup_add_layout.addWidget(browse_startup_btn)
        startup_add_layout.addWidget(self.startup_args_edit)
        startup_add_layout.addWidget(self.startup_runas_edit)
        startup_add_layout.addWidget(add_startup_btn)
        
        startup_layout.addLayout(startup_add_layout)
        
        # Delete startup button
        delete_startup_btn = QPushButton("Delete Selected")
        delete_startup_btn.clicked.connect(self.delete_startup_app)
        startup_layout.addWidget(delete_startup_btn)
        
        splitter.addWidget(startup_widget)
        
        # Processes section
        processes_widget = QWidget()
        processes_layout = QVBoxLayout(processes_widget)
        
        processes_layout.addWidget(QLabel("Processes to Start:"))
        self.processes_tree = QTreeWidget()
        self.processes_tree.setHeaderLabels(["Name", "Path", "Arguments", "Run As"])
        self.processes_tree.setColumnWidth(0, 150)
        self.processes_tree.setColumnWidth(1, 300)
        processes_layout.addWidget(self.processes_tree)
        
        # Add process controls
        process_add_layout = QHBoxLayout()
        
        self.process_name_edit = QLineEdit()
        self.process_name_edit.setPlaceholderText("Process Name")
        
        self.process_path_edit = QLineEdit()
        self.process_path_edit.setPlaceholderText("Process Path")
        
        browse_process_btn = QPushButton("Browse...")
        browse_process_btn.clicked.connect(self.browse_process)
        
        self.process_args_edit = QLineEdit()
        self.process_args_edit.setPlaceholderText("Arguments")
        
        self.process_runas_edit = QLineEdit()
        self.process_runas_edit.setPlaceholderText("Run As (username)")
        
        add_process_btn = QPushButton("Add Process")
        add_process_btn.clicked.connect(self.add_process)
        
        process_add_layout.addWidget(self.process_name_edit)
        process_add_layout.addWidget(self.process_path_edit)
        process_add_layout.addWidget(browse_process_btn)
        process_add_layout.addWidget(self.process_args_edit)
        process_add_layout.addWidget(self.process_runas_edit)
        process_add_layout.addWidget(add_process_btn)
        
        processes_layout.addLayout(process_add_layout)
        
        # Delete process button
        delete_process_btn = QPushButton("Delete Selected")
        delete_process_btn.clicked.connect(self.delete_process)
        processes_layout.addWidget(delete_process_btn)
        
        splitter.addWidget(processes_widget)
        
        self.tabs.addTab(tab, "Applications")
        
    def browse_startup_app(self):
        """Browse for a startup application."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Application",
            "",
            "Executables (*.exe);;All Files (*.*)"
        )
        
        if file_path:
            self.startup_path_edit.setText(file_path)
            
    def browse_process(self):
        """Browse for a process executable."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Process",
            "",
            "Executables (*.exe);;All Files (*.*)"
        )
        
        if file_path:
            self.process_path_edit.setText(file_path)
            
    def add_startup_app(self):
        """Add a startup application to the tree."""
        name = self.startup_name_edit.text().strip()
        path = self.startup_path_edit.text().strip()
        args = self.startup_args_edit.text().strip()
        run_as = self.startup_runas_edit.text().strip()
        
        if name and path:
            item = QTreeWidgetItem([name, path, args, run_as])
            self.startup_tree.addTopLevelItem(item)
            
            # Clear inputs
            self.startup_name_edit.clear()
            self.startup_path_edit.clear()
            self.startup_args_edit.clear()
            self.startup_runas_edit.clear()
            
    def delete_startup_app(self):
        """Delete selected startup application."""
        selected = self.startup_tree.selectedItems()
        if selected:
            index = self.startup_tree.indexOfTopLevelItem(selected[0])
            self.startup_tree.takeTopLevelItem(index)
            
    def add_process(self):
        """Add a process to the tree."""
        name = self.process_name_edit.text().strip()
        path = self.process_path_edit.text().strip()
        args = self.process_args_edit.text().strip()
        run_as = self.process_runas_edit.text().strip()
        
        if name and path:
            item = QTreeWidgetItem([name, path, args, run_as])
            self.processes_tree.addTopLevelItem(item)
            
            # Clear inputs
            self.process_name_edit.clear()
            self.process_path_edit.clear()
            self.process_args_edit.clear()
            self.process_runas_edit.clear()
            
    def delete_process(self):
        """Delete selected process."""
        selected = self.processes_tree.selectedItems()
        if selected:
            index = self.processes_tree.indexOfTopLevelItem(selected[0])
            self.processes_tree.takeTopLevelItem(index)
        
    def show_help(self):
        """Show the help window."""
        self.help_window = HelpWindow()
        self.help_window.show()
        
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Configuration Manager",
            """<h3>Windows System Configuration Manager</h3>
            <p>Version 1.0</p>
            <p>A tool for creating and managing system configuration files.</p>
            <p>Part of the Windows System Management Suite.</p>"""
        )
        
    def create_empty_config(self):
        """Create an empty configuration based on schema."""
        config = {}
        for section in CONFIG_SCHEMA:
            if CONFIG_SCHEMA[section].get("type") == "list":
                config[section] = []
            elif CONFIG_SCHEMA[section].get("type") == "dict":
                config[section] = {}
            else:
                config[section] = {
                    "system": {},
                    "user": {}
                } if section == "environment_variables" else {}
        return config
        
    def load_config(self):
        """Load configuration from a YAML file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Configuration",
            "",
            "YAML Files (*.yaml *.yml);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                self.update_ui_from_config()
                self.logger.info(f"Loaded configuration from {file_path}")
            except Exception as e:
                self.logger.error(f"Failed to load configuration: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to load configuration: {str(e)}"
                )
                
    def save_config(self):
        """Save configuration to a YAML file."""
        self.update_config_from_ui()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            "",
            "YAML Files (*.yaml);;All Files (*.*)"
        )
        
        if file_path:
            if not file_path.endswith('.yaml'):
                file_path += '.yaml'
                
            try:
                with open(file_path, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False)
                self.logger.info(f"Saved configuration to {file_path}")
            except Exception as e:
                self.logger.error(f"Failed to save configuration: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save configuration: {str(e)}"
                )
                
    def clear_config(self):
        """Clear all configuration settings."""
        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            "Are you sure you want to clear all settings?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config = self.create_empty_config()
            self.update_ui_from_config()
            
    def update_ui_from_config(self):
        """Update UI elements from the current configuration."""
        # Clear existing items
        self.system_vars_tree.clear()
        self.user_vars_tree.clear()
        
        # Update environment variables
        for name, value in self.config["environment_variables"]["system"].items():
            item = QTreeWidgetItem([name, str(value)])
            self.system_vars_tree.addTopLevelItem(item)
            
        for name, value in self.config["environment_variables"]["user"].items():
            item = QTreeWidgetItem([name, str(value)])
            self.user_vars_tree.addTopLevelItem(item)
            
    def update_config_from_ui(self):
        """Update configuration from UI elements."""
        # Update environment variables
        system_vars = {}
        user_vars = {}
        
        for i in range(self.system_vars_tree.topLevelItemCount()):
            item = self.system_vars_tree.topLevelItem(i)
            system_vars[item.text(0)] = item.text(1)
            
        for i in range(self.user_vars_tree.topLevelItemCount()):
            item = self.user_vars_tree.topLevelItem(i)
            user_vars[item.text(0)] = item.text(1)
            
        self.config["environment_variables"]["system"] = system_vars
        self.config["environment_variables"]["user"] = user_vars

def main():
    """Main entry point."""
    try:
        app = QApplication(sys.argv)
        window = ConfigManagerWindow()
        window.show()
        return app.exec()
        
    except Exception as e:
        logger = setup_logger("ConfigManager")
        logger.exception("Unexpected error in config manager")
        QMessageBox.critical(
            None,
            "Error",
            f"Unexpected error: {str(e)}\n\n{str(sys.exc_info())}"
        )
        return 1

if __name__ == '__main__':
    sys.exit(main())
