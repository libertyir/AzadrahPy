#!/usr/bin/env python3
"""
Domain Scanner - Main Entry Point
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from domain_ui.domain_ui import UIManager


def main():
    try:
        ui = UIManager()
        ui.menu()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()