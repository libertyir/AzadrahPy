#!/usr/bin/env python3
"""
Domain UI Manager - Main orchestrator for Domain Scanner UI
"""

import sys
import os

from scanner_core import DomainScanner
from storage import StorageManager
from geosite_parser import GeositeManager
from .menu_manager import MenuManager

from .components import (
    GeoDownloader,
    GeositeAdder,
    ScanRunner,
    DomainManager,
    ViewHandlers
)


class UIManager:
    """Handle user interface and menu operations for Domain Scanner"""
    
    def __init__(self):
        self.storage = StorageManager(batch_size=100)
        self.geosite = GeositeManager("geosite.dat")
        self.menu_manager = MenuManager()
        
        # Initialize components
        self.geo_downloader = GeoDownloader(self.geosite)
        self.geosite_adder = GeositeAdder(self.geosite, self.storage)
        self.scan_runner = ScanRunner(self.storage, self.geosite, DomainScanner)
        self.domain_manager = DomainManager(self.storage)
        self.view_handlers = ViewHandlers(self.storage)
    
    def menu(self):
        """Display main menu and handle user input"""
        while True:
            self.menu_manager.show_main_menu()
            
            domains_count = len(self.storage.load_domains())
            live_count = len(self.storage.read_live())
            geosite_exists = os.path.exists("geosite.dat")
            print(f"\nStats: {domains_count} domains | {live_count} live | GeoFiles: {'✅' if geosite_exists else '❌'}")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self.scan_runner.run(force=False)
            elif choice == '2':
                self.scan_runner.run(force=True)
            elif choice == '3':
                self.domain_manager.add_domain()
            elif choice == '4':
                self.view_handlers.show_live_list()
            elif choice == '5':
                self.view_handlers.show_archive()
            elif choice == '6':
                self.view_handlers.search_archive()
            elif choice == '7':
                self.domain_manager.sort_live()
            elif choice == '8':
                self.domain_manager.sort_domains()
            elif choice == '9':
                self.domain_manager.sort_archive()
            elif choice == '10':
                self.geosite_adder.add()
            elif choice == '11':
                self.geo_downloader.download_menu()
            elif choice == '12':
                self.menu_manager.show_help_screen()
                input("\nPress Enter to continue...")
            elif choice == '0':
                print("\nGoodbye!")
                sys.exit(0)
            else:
                print("\n[ERROR] Invalid choice!")
                input("\nPress Enter to continue...")


if __name__ == "__main__":
    ui = UIManager()
    ui.menu()