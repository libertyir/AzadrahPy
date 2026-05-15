#!/usr/bin/env python3
"""Menu Manager - Handles all menu displays and user prompts"""

import os
import platform
from typing import List, Optional


def clear_screen():
    """Clear terminal screen"""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')


class MenuManager:
    """Manages menu displays and user prompts"""
    
    def show_main_menu(self):
        """Display main menu"""
        clear_screen()
        print("="*60)
        print("IP SCANNER - MAIN MENU")
        print("="*60)
        print("1. Normal IP Scan")
        print("2. Force Update IP Scan")
        print("3. Add Single IP")
        print("4. Live IPs List")
        print("5. Archive View")
        print("6. Archive Search")
        print("7. Extracted Domains (from SSL)")
        print("8. Sort IPs List")
        print("9. Sort Live IPs")
        print("10. Sort Archive")
        print("11. Add from GeoIP")
        print("12. Help")
        print("0. Exit")
        print("="*60)
    
    def show_scan_method_menu(self, force: bool = False) -> str:
        """Show scan method selection menu"""
        clear_screen()
        print("\n" + "="*60)
        if force:
            print("FORCE UPDATE IP SCAN - Select Scan Method")
        else:
            print("NORMAL IP SCAN - Select Scan Method")
        print("="*60)
        print("\n1. Fast Scan - Ping → nslookup → Port 443 SSL")
        print("2. Deep Scan - Multiple ports (80,443,8080,8443)")
        print("3. Fake SNI Scan - Scan with custom SNI")
        print("0. Back to Main Menu")
        print("="*60)
        
        return input("\nEnter your choice (0-3): ").strip()
    
    def show_add_single_ip_header(self):
        """Show add single IP header"""
        clear_screen()
        print("\n" + "="*60)
        print("ADD SINGLE IP / CIDR")
        print("="*60)
        print("\nExamples:")
        print("  - Single IP: 8.8.8.8")
        print("  - CIDR range: 45.115.42.0/23")
        print("  - Multiple: Separate with commas\n")
    
    def show_add_from_geoip_header(self):
        """Show add from geoip header"""
        clear_screen()
        print("\n" + "="*60)
        print("ADD IP RANGES FROM GEOIP")
        print("="*60)
    
    def show_common_country_codes(self):
        """Show common country codes"""
        print("\nCommon country codes you can use:")
        common_codes = ['US', 'CN', 'RU', 'DE', 'GB', 'FR', 'JP', 'KR', 'BR', 'IN', 'CA', 'AU']
        for i, code in enumerate(common_codes):
            print(f"  {code}", end="  ")
            if (i + 1) % 6 == 0:
                print()
        print("\n")
    
    def show_ip_ranges_preview(self, tag: str, ip_ranges: List[str]):
        """Show preview of IP ranges"""
        print(f"\n[SUCCESS] Found {len(ip_ranges)} IP ranges for '{tag}':")
        print("-" * 40)
        for i, r in enumerate(ip_ranges[:15]):
            print(f"  {i+1}. {r}")
        if len(ip_ranges) > 15:
            print(f"  ... and {len(ip_ranges)-15} more")
    
    def get_add_options_choice(self) -> str:
        """Get user choice for add options"""
        print("\n" + "="*40)
        print("Options:")
        print("  1. Add all IP ranges to list (as CIDR)")
        print("  2. Add only first 100 IP ranges")
        print("  3. Cancel")
        print("="*40)
        return input("\nChoice (1-3): ").strip()
    
    def show_archive_search_header(self):
        """Show archive search header"""
        clear_screen()
        print("\n" + "="*60)
        print("ARCHIVE SEARCH")
        print("="*60)
    
    def show_search_results(self, ip: str, results: List[List[str]]):
        """Show search results"""
        clear_screen()
        print(f"\n{'='*60}")
        print(f"SEARCH RESULTS FOR: {ip}")
        print(f"{'='*60}")
        if results:
            for r in results:
                print(f"\nIP: {r[0]}")
                print(f"Hostname: {r[1]}")
                print(f"Ping Response: {r[2]}")
                print(f"Open Ports: {r[3]}")
                print(f"SSL Domains: {r[4]}")
                print(f"Scan Method: {r[7]}")
                print(f"Scan Time: {r[8]}")
        else:
            print(f"\nNo results found for '{ip}'")
    
    def show_help_screen(self):
        """Show help information"""
        clear_screen()
        print("\n" + "="*60)
        print("IP SCANNER - User Guide")
        print("="*60)
        print("\n1. Normal IP Scan")
        print("   - Scans only NEW IPs (not previously checked)")
        print("   - Checks archive to avoid duplicates")
        print("\n2. Force Update IP Scan")
        print("   - Scans ALL IPs regardless of previous checks")
        print("\nScan Methods:")
        print("   1. Fast Scan - Ping → nslookup → Port 443 SSL")
        print("   2. Deep Scan - Checks ports 80,443,8080,8443")
        print("   3. Fake SNI Scan - Uses custom Server Name Indication")
        print("\n4. Add Single IP")
        print("5. Live IPs List")
        print("6. Archive View")
        print("7. Archive Search")
        print("8. Extracted Domains")
        print("9-11. Sort Options")
        print("12. Add from GeoIP")
        print("\nScan Controls:")
        print("   P - Pause scanning")
        print("   R - Resume scanning")
        print("   S - Stop scanning")
        print("\nNavigation Controls:")
        print("   ← → Arrows - Navigate pages")
        print("   Home/End - First/Last page")
        print("   Esc - Exit current view")
        print("\n" + "="*60)
