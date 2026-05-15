#!/usr/bin/env python3
"""
IP Scanner - Main Entry Point
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main function"""
    try:
        # Try to import from ip_ui
        from ip_ui import IPUIManager
        ui = IPUIManager()
        ui.menu()
    except ImportError as e:
        print(f"Import error: {e}")
        print("\nTrying fallback import...")
        
        try:
            # Fallback: direct import from ip_ui_backup
            from ip_ui_backup import IPUIManager
            ui = IPUIManager()
            ui.menu()
        except ImportError as e2:
            print(f"Fallback also failed: {e2}")
            print("\nPossible solutions:")
            print("1. Make sure all required files exist:")
            print("   - ip_ui.py")
            print("   - ip_scanner_core.py")
            print("   - ip_storage.py")
            print("   - geoip_parser.py")
            print("   - x509_parser.py")
            print("2. Check if ui_components folder exists with required files")
            print("3. Run: pip install requests")
            sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()