"""Error dialog implementations."""
import sys
from typing import Optional
from src.core.logger import setup_logger

logger = setup_logger(__name__)

# Try to import PyQt6, but don't fail if it's not available
try:
    from PyQt6.QtWidgets import QMessageBox
    HAS_QT = True
except ImportError:
    HAS_QT = False
    logger.warning('PyQt6 not available, falling back to console output')

def show_error(
    message: str,
    title: str = "Error",
    detailed_text: Optional[str] = None
) -> None:
    """Display an error message to the user.
    
    Falls back to console output if GUI is not available.
    
    Args:
        message: Main error message to display
        title: Dialog title
        detailed_text: Optional technical details to show in expandable section
    """
    if HAS_QT:
        try:
            dialog = QMessageBox()
            dialog.setIcon(QMessageBox.Icon.Critical)
            dialog.setText(message)
            dialog.setWindowTitle(title)
            
            if detailed_text:
                dialog.setDetailedText(detailed_text)
                
            dialog.exec()
            return
        except Exception as e:
            logger.error(f'Failed to show error dialog: {str(e)}')
    
    # Fall back to console output
    print(f'Error: {title}', file=sys.stderr)
    print(f'Message: {message}', file=sys.stderr)
    if detailed_text:
        print(f'Details: {detailed_text}', file=sys.stderr)
