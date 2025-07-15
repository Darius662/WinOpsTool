"""File Transfer Dialog for remote operations."""
import os
import shutil
import win32wnet
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget,
                          QTreeWidgetItem, QPushButton, QProgressBar,
                          QLabel, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from src.core.logger import setup_logger
from src.core.remote_manager import RemotePC

class FileTransferWorker(QThread):
    """Worker thread for file transfer operations."""
    
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, source_path, dest_path, remote_pc=None):
        super().__init__()
        self.source_path = source_path
        self.dest_path = dest_path
        self.remote_pc = remote_pc
        self.logger = setup_logger(self.__class__.__name__)
        
    def run(self):
        """Execute the file transfer."""
        try:
            if self.remote_pc:
                # Connect to remote share
                try:
                    win32wnet.WNetAddConnection2(
                        0,  # Type: disk
                        None,  # Local device
                        f"\\\\{self.remote_pc.hostname}\\admin$",  # Remote path
                        None,  # Provider
                        self.remote_pc.username,
                        self.remote_pc.password
                    )
                except Exception as e:
                    self.logger.error(f"Failed to connect to remote share: {str(e)}")
                    self.finished.emit(False, str(e))
                    return
                    
            # Get total size for progress
            total_size = 0
            current_size = 0
            
            if os.path.isfile(self.source_path):
                total_size = os.path.getsize(self.source_path)
            else:
                for root, dirs, files in os.walk(self.source_path):
                    for file in files:
                        total_size += os.path.getsize(os.path.join(root, file))
                        
            # Copy files with progress
            if os.path.isfile(self.source_path):
                # Create destination directory if needed
                os.makedirs(os.path.dirname(self.dest_path), exist_ok=True)
                
                # Copy file with progress
                with open(self.source_path, 'rb') as src, open(self.dest_path, 'wb') as dst:
                    while True:
                        chunk = src.read(8192)
                        if not chunk:
                            break
                        dst.write(chunk)
                        current_size += len(chunk)
                        self.progress.emit(int(current_size * 100 / total_size))
            else:
                # Copy directory with progress
                for root, dirs, files in os.walk(self.source_path):
                    # Create directories
                    for dir in dirs:
                        src_dir = os.path.join(root, dir)
                        dst_dir = os.path.join(
                            self.dest_path,
                            os.path.relpath(src_dir, self.source_path)
                        )
                        os.makedirs(dst_dir, exist_ok=True)
                        
                    # Copy files
                    for file in files:
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(
                            self.dest_path,
                            os.path.relpath(src_file, self.source_path)
                        )
                        
                        # Create destination directory if needed
                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                        
                        # Copy file
                        shutil.copy2(src_file, dst_file)
                        current_size += os.path.getsize(src_file)
                        self.progress.emit(int(current_size * 100 / total_size))
                        
            self.progress.emit(100)
            self.finished.emit(True, "")
            
            if self.remote_pc:
                try:
                    win32wnet.WNetCancelConnection2(f"\\\\{self.remote_pc.hostname}\\admin$", 0, 0)
                except:
                    pass
                    
        except Exception as e:
            self.logger.error(f"File transfer failed: {str(e)}")
            self.finished.emit(False, str(e))

class FileTransferDialog(QDialog):
    """Dialog for transferring files to remote PCs."""
    
    def __init__(self, remote_manager, parent=None):
        super().__init__(parent)
        self.remote_manager = remote_manager
        self.logger = setup_logger(self.__class__.__name__)
        self.setWindowTitle("File Transfer")
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Remote PC list
        self.remote_tree = QTreeWidget()
        self.remote_tree.setHeaderLabels([
            "Name",
            "Hostname",
            "Status"
        ])
        self.remote_tree.setAlternatingRowColors(True)
        
        layout.addWidget(QLabel("Select Target PCs:"))
        layout.addWidget(self.remote_tree)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.browse_btn = QPushButton("Browse...")
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.browse_btn)
        layout.addLayout(file_layout)
        
        # Progress
        self.progress_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.transfer_btn = QPushButton("Transfer")
        self.refresh_btn = QPushButton("Refresh")
        self.close_btn = QPushButton("Close")
        
        for btn in [self.transfer_btn, self.refresh_btn, self.close_btn]:
            button_layout.addWidget(btn)
            
        layout.addLayout(button_layout)
        
        # Connect signals
        self.browse_btn.clicked.connect(self.browse_file)
        self.transfer_btn.clicked.connect(self.transfer_files)
        self.refresh_btn.clicked.connect(self.refresh_pcs)
        self.close_btn.clicked.connect(self.accept)
        
        # Initial load
        self.refresh_pcs()
        self.selected_path = None
        
    def browse_file(self):
        """Browse for a file or folder to transfer."""
        path = QFileDialog.getOpenFileName(
            self,
            "Select File to Transfer",
            "",
            "All Files (*.*)"
        )[0]
        
        if path:
            self.selected_path = path
            self.file_label.setText(os.path.basename(path))
            
    def refresh_pcs(self):
        """Refresh the remote PC list."""
        self.remote_tree.clear()
        
        for pc in self.remote_manager.get_connections():
            item = QTreeWidgetItem([
                pc.name,
                pc.hostname,
                "Connected" if pc.is_connected else "Disconnected"
            ])
            item.setCheckState(0, Qt.CheckState.Unchecked)
            self.remote_tree.addTopLevelItem(item)
            
    def transfer_files(self):
        """Transfer files to selected remote PCs."""
        if not self.selected_path:
            QMessageBox.warning(self, "Warning", "Please select a file to transfer")
            return
            
        # Get selected PCs
        selected_pcs = []
        for i in range(self.remote_tree.topLevelItemCount()):
            item = self.remote_tree.topLevelItem(i)
            if item.checkState(0) == Qt.CheckState.Checked:
                pc = self.remote_manager.get_connection(item.text(0))
                if pc and pc.is_connected:
                    selected_pcs.append(pc)
                    
        if not selected_pcs:
            QMessageBox.warning(self, "Warning", "Please select at least one connected PC")
            return
            
        # Confirm transfer
        reply = QMessageBox.question(
            self,
            "Confirm Transfer",
            f"Transfer {os.path.basename(self.selected_path)} to {len(selected_pcs)} PCs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.transfer_to_pcs(selected_pcs)
            
    def transfer_to_pcs(self, pcs):
        """Transfer files to the specified PCs."""
        total_pcs = len(pcs)
        completed = 0
        failed = 0
        
        for pc in pcs:
            try:
                # Update progress
                self.progress_label.setText(f"Transferring to {pc.name}...")
                self.progress_bar.setValue(0)
                
                # Create remote path
                filename = os.path.basename(self.selected_path)
                remote_path = f"C:\\Windows\\Temp\\{filename}"
                
                # Create and start worker
                self.worker = FileTransferWorker(self.selected_path, remote_path, pc)
                self.worker.progress.connect(self.progress_bar.setValue)
                self.worker.finished.connect(
                    lambda success, error, pc=pc: self.transfer_completed(success, error, pc)
                )
                self.worker.start()
                
                # Wait for completion
                self.worker.wait()
                
                if hasattr(self, 'last_transfer_success'):
                    if self.last_transfer_success:
                        completed += 1
                    else:
                        failed += 1
                        
            except Exception as e:
                self.logger.error(f"Failed to transfer to {pc.name}: {str(e)}")
                failed += 1
                
        # Show final results
        QMessageBox.information(
            self,
            "Transfer Complete",
            f"Successfully transferred to {completed} PCs\nFailed on {failed} PCs"
        )
        
        self.progress_label.setText("Ready")
        self.progress_bar.setValue(0)
        
    def transfer_completed(self, success, error, pc):
        """Handle transfer completion."""
        self.last_transfer_success = success
        if not success:
            self.logger.error(f"Failed to transfer to {pc.name}: {error}")
            QMessageBox.warning(
                self,
                "Transfer Failed",
                f"Failed to transfer to {pc.name}: {error}"
            )
