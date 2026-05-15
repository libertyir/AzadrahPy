#!/usr/bin/env python3
"""Menu Manager for Domain Scanner"""

import platform
import os


def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')


class MenuManager:
    """Manages menu displays and user prompts for Domain Scanner"""
    
    def show_main_menu(self):
        """Display main menu"""
        clear_screen()
        print("="*60)
        print("DOMAIN SCANNER - MAIN MENU")
        print("="*60)
        print("1. Normal Start")
        print("2. Force Update")
        print("3. Add Domain")
        print("4. Live List")
        print("5. Archive View")
        print("6. Archive Search")
        print("7. Sort Live List")
        print("8. Sort Domains")
        print("9. Sort Archive")
        print("10. Add from Geosite")
        print("11. Download Geo Files")
        print("12. Help")
        print("0. Exit")
        print("="*60)
    
    def show_add_domain_header(self):
        """Show add domain header"""
        clear_screen()
        print("\n" + "="*60)
        print("ADD DOMAIN")
        print("="*60)
        print("\nExamples:")
        print("  - Single domain: example.com")
        print("  - Multiple domains: google.com, github.com")
        print("  - Geosite tag: geosite:google\n")
    
    def show_add_from_geosite_header(self):
        """Show add from geosite header"""
        clear_screen()
        print("\n" + "="*60)
        print("ADD FROM GEOSITE")
        print("="*60)
    
    def show_common_tags(self):
        """Show common geosite tags"""
        print("\nCommon tags you can use:")
        common_tags = ['google', 'facebook', 'twitter', 'github', 'cloudflare', 
                       'microsoft', 'apple', 'netflix', 'amazon', 'telegram', 
                       'whatsapp', 'instagram', 'reddit', 'youtube', 'gfw', 'cn']
        for i, tag in enumerate(common_tags):
            print(f"  {tag}", end="  ")
            if (i + 1) % 6 == 0:
                print()
        print("\n")
    
    def show_domains_preview(self, tag: str, domains: list):
        """Show preview of extracted domains"""
        print(f"\n[SUCCESS] Found {len(domains)} domains for '{tag}':")
        print("-" * 40)
        for i, d in enumerate(domains[:15]):
            print(f"  {i+1}. {d}")
        if len(domains) > 15:
            print(f"  ... and {len(domains)-15} more")
    
    def get_add_options_choice(self) -> str:
        """Get user choice for add options"""
        print("\n" + "="*40)
        print("Options:")
        print("  1. Add all domains to list")
        print("  2. Add only .com domains")
        print("  3. Add only .net domains")
        print("  4. Add only .org domains")
        print("  5. Filter by keyword")
        print("  6. Cancel")
        print("="*40)
        return input("\nChoice (1-6): ").strip()
    
    def show_download_menu(self):
        """Show download menu"""
        clear_screen()
        print("\n" + "="*60)
        print("📥 DOWNLOAD GEO FILES")
        print("="*60)
        print("1. Download geosite.dat (Domain lists)")
        print("2. Download geoip.dat (IP ranges)")
        print("3. Download ALL (both files)")
        print("4. Check existing files status")
        print("0. Back to Main Menu")
        print("="*60)
    
    def show_geo_status_header(self):
        """Show geo files status header"""
        clear_screen()
        print("\n" + "="*60)
        print("GEO FILES STATUS")
        print("="*60)
    
    def show_archive_search_header(self):
        """Show archive search header"""
        clear_screen()
        print("\n" + "="*60)
        print("ARCHIVE SEARCH")
        print("="*60)
    
    def show_search_results(self, domain: str, results):
        """Show search results"""
        clear_screen()
        print(f"\n{'='*60}")
        print(f"SEARCH RESULTS FOR: {domain}")
        print(f"{'='*60}")
        if results:
            for r in results:
                print(f"\nDomain: {r[0]}")
                print(f"IP: {r[1] if len(r)>1 else 'N/A'}")
                print(f"Status: {r[2] if len(r)>2 else 'N/A'}")
                print(f"Accessible: {r[3] if len(r)>3 else 'N/A'}")
                print(f"Checked At: {r[4] if len(r)>4 else 'N/A'}")
        else:
            print(f"\nNo results found for '{domain}'")
    
    def show_help_screen(self):
        """Show help information"""
        clear_screen()
        print("\n" + "="*60)
        print("HELP - Domain Scanner User Guide")
        print("="*60)
        print("\n1. Normal Start")
        print("   - Scans only NEW domains (not previously checked)")
        print("   - Checks archive.csv to avoid duplicates")
        print("\n2. Force Update")
        print("   - Scans ALL domains regardless of previous checks")
        print("\n3. Add Domain")
        print("   - Manually add a single domain to domains.txt")
        print("\n4. Live List")
        print("   - Shows all domains that responded successfully")
        print("\n5. Archive View")
        print("   - Shows complete scan history")
        print("\n6. Archive Search")
        print("   - Search for specific domain in archive")
        print("\n7-9. Sort Options")
        print("   - Alphabetically sort various lists")
        print("\n10. Add from Geosite")
        print("   - Extract domains from geosite.dat by tag")
        print("   - Example: 'google' extracts all Google domains")
        print("\n11. Download Geo Files")
        print("   - Download/Update geosite.dat and geoip.dat")
        print("\n12. Help")
        print("\nScan Controls:")
        print("   P - Pause scanning")
        print("   R - Resume scanning")
        print("   S - Stop scanning (save partial results)")
        print("\nNavigation Controls:")
        print("   ← → Arrows - Navigate pages")
        print("   Home/End - First/Last page")
        print("   Esc - Exit current view")
        print("\n" + "="*60)
    
    def show_scan_config_header(self, domains_count: int, force: bool):
        """Show scan configuration header"""
        clear_screen()
        print("\n" + "="*60)
        print("SCAN CONFIGURATION")
        print("="*60)
        print(f"Total domains in list: {domains_count}")
        print(f"Force update mode: {'ON' if force else 'OFF'}")
        print("-" * 40)
    
    def show_scan_progress_header(self, workers: int, timeout: int, force: bool, total_domains: int, to_scan: int):
        """Show scan progress header"""
        clear_screen()
        print("\n" + "="*60)
        print("SCANNING IN PROGRESS")
        print("="*60)
        print(f"Threads: {workers}")
        print(f"Timeout: {timeout}s")
        print(f"Force Update: {force}")
        print(f"Total domains: {total_domains}")
        print(f"Domains to scan: {to_scan}")
        print("\nControls:")
        print("  P - Pause")
        print("  R - Resume")
        print("  S - Stop (save results)")
        print("-" * 40)
        print()