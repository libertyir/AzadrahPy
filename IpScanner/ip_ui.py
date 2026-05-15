#!/usr/bin/env python3
"""
IP Scanner UI - Complete User Interface for IP Scanner
"""

import sys
import platform
import os
import threading
import time
from typing import List, Optional

from ip_scanner_core import IPScanner
from ip_storage import IPStorageManager
from geoip_parser import GeoIPManager

# Import UI components
from ui_components.menu_manager import MenuManager
from ui_components.paginated_view import PaginatedView
from ui_components.scan_controller import ScanController


class IPUIManager:
    """Handle user interface for IP scanner"""
    
    def __init__(self):
        self.storage = IPStorageManager()
        self.scanner = None
        self.geoip = GeoIPManager("geoip.dat")
        self.menu_manager = MenuManager()      # تغییر نام به menu_manager
        self.paginator = PaginatedView()
        self.scan_controller = ScanController()
        self.scan_thread = None
        self.scan_in_progress = False
    
    # ========== Core UI Methods ==========
    
    def add_from_geoip(self):
        """Add IP ranges from geoip.dat using a country tag"""
        self.menu_manager.show_add_from_geoip_header()   # تغییر به menu_manager
        
        # Check and show geoip status
        if not os.path.exists("geoip.dat"):
            print("\n[NOTE] geoip.dat not found in current directory!")
            print("Using built-in IP range lists for common countries.\n")
        else:
            print("\n[OK] geoip.dat found. Loading...\n")
            countries = self.geoip.get_all_countries()
            if countries:
                print(f"Found {len(countries)} countries in geoip.dat")
                print(f"Sample: {', '.join(countries[:15])}\n")
        
        # Show common country codes
        self.menu_manager.show_common_country_codes()
        
        tag = input("Enter country code (e.g., 'US', 'CN', 'JP'): ").strip().upper()
        if not tag:
            print("No tag entered!")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n[INFO] Extracting IP ranges for {tag}...")
        ip_ranges = self.geoip.get_ip_ranges_by_country(tag)
        
        if not ip_ranges:
            print(f"[ERROR] No IP ranges found for '{tag}'")
            input("\nPress Enter to continue...")
            return
        
        # Show preview
        self.menu_manager.show_ip_ranges_preview(tag, ip_ranges)
        
        # Get user choice
        choice = self.menu_manager.get_add_options_choice()
        
        if choice == '1':
            added = self.storage.add_ips_batch(ip_ranges)
            print(f"\n[OK] Added {added} IP ranges to ips.txt")
        elif choice == '2':
            added = self.storage.add_ips_batch(ip_ranges[:100])
            print(f"\n[OK] Added {added} IP ranges to ips.txt")
        else:
            print("Cancelled.")
        
        input("\nPress Enter to continue...")
    
    def show_extracted_domains(self):
        """Show domains extracted from SSL certificates"""
        domains = self.storage.get_extracted_domains()
        self.paginator.show(domains, "EXTRACTED DOMAINS FROM SSL")
    
    def show_help(self):
        """Show help information"""
        self.menu_manager.show_help_screen()
        input("\nPress Enter to continue...")
    
    def select_scan_method(self, force: bool = False):
        """Show scan method selection menu"""
        scan_type = self.menu_manager.show_scan_method_menu(force)
        
        if scan_type == '0':
            return
        elif scan_type in ['1', '2', '3']:
            self.run_scan(scan_type, force)
        else:
            print("\n[ERROR] Invalid choice!")
            input("\nPress Enter to continue...")
    
    def run_scan(self, scan_type: str, force: bool = False):
        """Run IP scan with selected method"""
        items = self.storage.load_ips()
        if not items:
            print("\n[ERROR] No IPs/CIDRs found in ips.txt!")
            input("\nPress Enter to continue...")
            return
        
        # Get configuration
        config = self.scan_controller.get_scan_configuration(scan_type, force)
        if not config:
            return
        
        # Initialize scanner
        self.scanner = IPScanner(timeout=config['timeout'], max_workers=config['workers'])
        
        # Load previously scanned IPs
        previous_scanned = self.storage.load_previous_results() if not force else None
        
        # Start scan with control
        self.scan_controller.run_with_control(
            scanner=self.scanner,
            items=items,
            scan_method=config['scan_method'],
            fake_sni=config['fake_sni'],
            previous_scanned=previous_scanned,
            force=force,
            storage=self.storage
        )
    
    def show_stats(self):
        """Show statistics in menu"""
        ips_count = len(self.storage.load_ips())
        live_count = len(self.storage.read_live_ips())
        domains_count = len(self.storage.get_extracted_domains())
        print(f"\nStats: {ips_count} IPs/CIDRs | {live_count} Live | {domains_count} Domains extracted")
    
    def menu(self):
        """Display main menu and handle user input"""
        while True:
            self.menu_manager.show_main_menu()
            self.show_stats()
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self.select_scan_method(force=False)
            elif choice == '2':
                self.select_scan_method(force=True)
            elif choice == '3':
                self._add_single_ip()
            elif choice == '4':
                live_ips = self.storage.read_live_ips()
                self.paginator.show(live_ips, "LIVE IPs LIST")
            elif choice == '5':
                self._show_archive()
            elif choice == '6':
                self._search_archive()
            elif choice == '7':
                self.show_extracted_domains()
            elif choice == '8':
                self.storage.sort_ips_file()
                print("\n[OK] ips.txt sorted successfully!")
                input("\nPress Enter to continue...")
            elif choice == '9':
                self.storage.sort_live_ips()
                print("\n[OK] LiveIPs.txt sorted successfully!")
                input("\nPress Enter to continue...")
            elif choice == '10':
                self.storage.sort_archive()
                print("\n[OK] Archive sorted successfully!")
                input("\nPress Enter to continue...")
            elif choice == '11':
                self.add_from_geoip()
            elif choice == '12':
                self.show_help()
            elif choice == '0':
                print("\nGoodbye!")
                sys.exit(0)
            else:
                print("\n[ERROR] Invalid choice!")
                input("\nPress Enter to continue...")
    
    # ========== Private Helper Methods ==========
    
    def _add_single_ip(self):
        """Add single IP or CIDR manually"""
        self.menu_manager.show_add_single_ip_header()
        
        ip_input = input("Enter IP or CIDR: ").strip()
        if ip_input:
            if ',' in ip_input:
                ips = [i.strip() for i in ip_input.split(',')]
                added = self.storage.add_ips_batch(ips)
                print(f"\n[OK] Added {added} new entries")
            else:
                if self.storage.add_ip(ip_input):
                    print(f"\n[OK] '{ip_input}' added successfully!")
                else:
                    print(f"\n[ERROR] Invalid or duplicate: {ip_input}")
        else:
            print("\nNo entry provided.")
        input("\nPress Enter to continue...")
    
    def _show_archive(self):
        """Show archive with pagination"""
        entries = self.storage.read_archive()
        if not entries:
            self.paginator.show([], "ARCHIVE DATA")
        else:
            formatted = [f"{e[0]} | {e[1]} | Ports:{e[3]} | Domains:{e[4][:30]}" 
                        for e in entries]
            self.paginator.show(formatted, "ARCHIVE DATA")
    
    def _search_archive(self):
        """Search for specific IP in archive"""
        self.menu_manager.show_archive_search_header()
        ip = input("\nEnter IP address to search: ").strip()
        if ip:
            res = self.storage.search_archive(ip)
            self.menu_manager.show_search_results(ip, res)
        input("\n\nPress Enter to continue...")


# For testing
if __name__ == "__main__":
    ui = IPUIManager()
    ui.menu()