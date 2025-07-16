"""Test script to identify Registry Panel loading issues."""
import sys
from PyQt6.QtWidgets import QApplication
from src.ui.panels.registry import RegistryPanel

def main():
    """Run test to identify Registry Panel loading issues."""
    app = QApplication(sys.argv)
    
    # Create Registry Panel
    panel = RegistryPanel(None)
    
    # Print panel class details
    print(f"Panel class: {panel.__class__.__name__}")
    print(f"Panel module: {panel.__class__.__module__}")
    print(f"Panel file: {panel.__class__.__module__.__file__ if hasattr(panel.__class__.__module__, '__file__') else 'Unknown'}")
    
    # Print panel attributes
    print("\nPanel attributes:")
    for attr in dir(panel):
        if not attr.startswith('__'):
            print(f"- {attr}")
    
    # Print UI structure
    print("\nUI Structure:")
    for child in panel.children():
        print(f"- {child.__class__.__name__}")
        if hasattr(child, 'children'):
            for subchild in child.children():
                print(f"  - {subchild.__class__.__name__}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
