#!/usr/bin/env python3
"""Scan Controller - Handles scan execution and control (Pause/Resume/Stop)"""

import sys
import platform
import threading
import time
from typing import Optional


class ScanController:
    """Controls scan execution with pause/resume/stop capabilities"""
    
    def __init__(self):
        self.scan_thread = None
        self.is_running = False
    
    def get_scan_configuration(self, scan_type: str, force: bool = False) -> Optional[dict]:
        """Get scan configuration from user"""
        self._clear_screen()
        print("\n" + "="*60)
        print("SCAN CONFIGURATION")
        print("="*60)
        
        # Get timeout
        try:
            timeout_input = input("Timeout in seconds (default 3): ").strip()
            timeout = int(timeout_input) if timeout_input else 3
        except ValueError:
            timeout = 3
        
        # Get number of workers
        try:
            workers_input = input("Number of worker threads (default 20): ").strip()
            workers = int(workers_input) if workers_input else 20
        except ValueError:
            workers = 20
        
        # Setup scan method
        scan_method = ""
        fake_sni = None
        method_name = ""
        
        if scan_type == "1":
            scan_method = "fast"
            method_name = "FAST SCAN"
        elif scan_type == "2":
            scan_method = "deep"
            method_name = "DEEP SCAN"
        elif scan_type == "3":
            scan_method = "fakesni"
            fake_sni = input("\nEnter fake SNI (e.g., 'www.google.com'): ").strip()
            if not fake_sni:
                fake_sni = "www.google.com"
            method_name = f"FAKE SNI SCAN (SNI: {fake_sni})"
        else:
            return None
        
        return {
            'timeout': timeout,
            'workers': workers,
            'scan_method': scan_method,
            'fake_sni': fake_sni,
            'method_name': method_name
        }
    
    def run_with_control(self, scanner, items: list, scan_method: str, fake_sni: str,
                         previous_scanned: set, force: bool, storage):
        """Run scan with interactive controls (Pause/Resume/Stop)"""
        self._clear_screen()
        print("\n" + "="*60)
        print(f"SCANNING IN PROGRESS")
        print("="*60)
        print(f"Force mode: {'ON (re-scanning all)' if force else 'OFF (new IPs only)'}")
        print("\nControls:")
        print("  P - Pause")
        print("  R - Resume")
        print("  S - Stop")
        print("-" * 40)
        print()
        
        stats = {'live': 0, 'dead': 0}
        
        def update_progress(processed, total):
            if total > 0:
                percent = (processed / total) * 100
                print(f"\r[PROGRESS] {processed}/{total} ({percent:.1f}%) | Live: {stats['live']} | Dead: {stats['dead']}", end="", flush=True)
        
        def save_result(result):
            storage.save_result(result)
            if result.open_ports:
                stats['live'] += 1
                ports_str = ",".join(map(str, result.open_ports))
                print(f"\n✓ LIVE: {result.ip} | Ports: {ports_str} | Domains: {len(result.ssl_domains)}")
                if result.ssl_domains:
                    print(f"  └─ SSL Domains: {', '.join(result.ssl_domains[:3])}")
            else:
                stats['dead'] += 1
                print(f"\n✗ DEAD: {result.ip}")
        
        scanner.set_callbacks(progress_callback=update_progress, result_callback=save_result)
        
        # Run scan in separate thread
        scan_thread = threading.Thread(
            target=scanner.start_scan,
            args=(items, scan_method, fake_sni, previous_scanned, force)
        )
        scan_thread.daemon = True
        scan_thread.start()
        
        # Control loop
        while scan_thread.is_alive():
            try:
                if platform.system() == "Windows":
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                        self._handle_control_key(key, scanner)
                        if key == 's':
                            break
                else:
                    import select
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1).lower()
                        self._handle_control_key(key, scanner)
                        if key == 's':
                            break
            except:
                pass
            time.sleep(0.1)
        
        # Wait for thread to finish
        scan_thread.join(timeout=5)
        
        print("\n\n" + "="*60)
        print("SCAN COMPLETED!")
        print("="*60)
        print(f"Total scanned: {scanner.processed_count}")
        print(f"Live IPs: {stats['live']}")
        print(f"Dead IPs: {stats['dead']}")
        input("\nPress Enter to continue...")
    
    def _handle_control_key(self, key: str, scanner):
        """Handle control keys (P, R, S)"""
        if key == 'p':
            scanner.pause()
        elif key == 'r':
            scanner.resume()
        elif key == 's':
            scanner.stop()
    
    def _clear_screen(self):
        """Clear terminal screen"""
        if platform.system() == "Windows":
            import os
            os.system('cls')
        else:
            import os
            os.system('clear')