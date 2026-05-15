#!/usr/bin/env python3
"""Scan Controller for Domain Scanner"""

import platform
import sys
import time


class ScanController:
    """Controls scan execution with pause/resume/stop capabilities"""
    
    def __init__(self):
        self.scan_thread = None
        self.is_running = False
    
    def get_scan_config(self) -> tuple:
        """Get timeout and workers from user"""
        try:
            timeout_input = input("Timeout in seconds (default 5): ").strip()
            timeout = int(timeout_input) if timeout_input else 5
        except ValueError:
            timeout = 5
        
        try:
            workers_input = input("Number of worker threads (default 10): ").strip()
            workers = int(workers_input) if workers_input else 10
        except ValueError:
            workers = 10
        
        return timeout, workers
    
    def handle_scan_control(self, scanner, key: str):
        """Handle control keys (P, R, S)"""
        if key == 'p':
            if scanner and scanner.is_running and not scanner.is_paused:
                scanner.pause()
                print("\n[PAUSED] Scan paused. Press 'R' to resume.")
        elif key == 'r':
            if scanner and scanner.is_running and scanner.is_paused:
                scanner.resume()
                print("\n[RESUMED] Scan continuing...")
        elif key == 's':
            if scanner and scanner.is_running:
                scanner.stop()
                print("\n[STOPPED] Scan stopped. Results saved so far.")
                return True
        return False
    
    def get_key(self):
        """Get keyboard input (cross-platform)"""
        if platform.system() == "Windows":
            import msvcrt
            if msvcrt.kbhit():
                try:
                    return msvcrt.getch().decode('utf-8', errors='ignore').lower()
                except:
                    return None
        else:
            import select
            if select.select([sys.stdin], [], [], 0)[0]:
                return sys.stdin.read(1).lower()
        return None