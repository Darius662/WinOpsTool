#!/usr/bin/env python3
"""Entry point for the System Management Tool."""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from src.core.logger import setup_logger
from src.core.dependencies import check_dependencies, install_dependencies
from src.core.privileges import is_admin, request_admin_privileges
from src.ui.dialogs.error_dialog import show_error
from src.ui.main.window import MainWindow
from src.core.config import APP_NAME

logger = setup_logger(__name__)

def main():
    """Main entry point."""
    try:
        # Initialize Qt application first
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        app.setApplicationName(APP_NAME)
        
        # Check for admin privileges
        if not is_admin():
            logger.info('Requesting admin privileges')
            request_admin_privileges()
            return 1

        # Check dependencies
        deps_ok, missing_deps = check_dependencies()
        if not deps_ok:
            msg = f'Missing required packages: {", ".join(missing_deps)}\nWould you like to install them now?'
            
            reply = QMessageBox.question(
                None, 
                'Missing Dependencies',
                msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if not install_dependencies(missing_deps):
                    show_error('Failed to install dependencies. Please install them manually.')
                    return 1
            else:
                return 1

        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Start event loop
        return app.exec()

    except Exception as e:
        logger.exception('Unexpected error in main')
        show_error(
            message=str(e),
            detailed_text=str(sys.exc_info())
        )
        return 1

if __name__ == '__main__':
    sys.exit(main())
