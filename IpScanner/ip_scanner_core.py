#!/usr/bin/env python3
"""
IP Scanner Core - Main orchestrator for multi-threaded IP scanning
"""

import threading
import queue
import time
from typing import List, Optional
from dataclasses import dataclass

from utils import CIDRUtils
from scanners import FastScanner, DeepScanner, FakeSNIScanner
from scanners.fast_scanner import ScanResult


class IPScanner:
    """Multi-threaded IP scanner orchestrator"""
    
    def __init__(self, timeout: int = 3, max_workers: int = 20):
        self.timeout = timeout
        self.max_workers = max_workers
        self.is_running = False
        self.is_paused = False
        self.pause_condition = threading.Condition()
        self.ip_queue = queue.Queue()
        self.results = []
        self.results_lock = threading.Lock()
        self.processed_count = 0
        self.total_count = 0
        self.progress_callback = None
        self.result_callback = None
        self.workers = []
        self.scanner = None
    
    def set_callbacks(self, progress_callback=None, result_callback=None):
        self.progress_callback = progress_callback
        self.result_callback = result_callback
    
    def _create_scanner(self, scan_method: str, fake_sni: str = None):
        """Create appropriate scanner instance"""
        if scan_method == "fast":
            return FastScanner(self.timeout)
        elif scan_method == "deep":
            return DeepScanner(self.timeout)
        elif scan_method == "fakesni":
            return FakeSNIScanner(self.timeout, fake_sni)
        else:
            raise ValueError(f"Unknown scan method: {scan_method}")
    
    def _prepare_ips(self, items: List[str], previous_scanned: set = None, force: bool = False) -> List[str]:
        """Expand CIDRs and filter previously scanned IPs"""
        all_ips = []
        cidr_count = 0
        single_count = 0
        invalid_count = 0
        
        print("\n[PREPARE] Expanding CIDR ranges...")
        for item in items:
            item = item.strip()
            if '/' in item:
                if CIDRUtils.is_valid_cidr(item):
                    cidr_count += 1
                    ips = CIDRUtils.expand_cidr(item)
                    all_ips.extend(ips)
                else:
                    invalid_count += 1
                    print(f"  Invalid CIDR skipped: {item}")
            else:
                if CIDRUtils.is_valid_ip(item):
                    single_count += 1
                    all_ips.append(item)
                else:
                    invalid_count += 1
                    print(f"  Invalid IP skipped: {item}")
        
        # Remove duplicates
        all_ips = list(set(all_ips))
        
        # Filter out previously scanned IPs if not force mode
        if not force and previous_scanned:
            original_count = len(all_ips)
            all_ips = [ip for ip in all_ips if ip not in previous_scanned]
            skipped = original_count - len(all_ips)
            if skipped > 0:
                print(f"\n  Skipping {skipped} previously scanned IPs")
        
        print(f"\n[SUMMARY] {len(items)} entries total")
        print(f"  - CIDR ranges: {cidr_count}")
        print(f"  - Single IPs: {single_count}")
        print(f"  - Invalid entries: {invalid_count}")
        print(f"  - Total IPs to scan: {len(all_ips)}")
        
        return [ip for ip in all_ips if CIDRUtils.is_valid_ip(ip)]
    
    def _worker(self):
        """Worker thread for scanning"""
        while self.is_running:
            # Check pause state
            with self.pause_condition:
                while self.is_paused and self.is_running:
                    self.pause_condition.wait()
            
            if not self.is_running:
                break
            
            try:
                task = self.ip_queue.get(timeout=0.5)
                if task is None:
                    break
                
                ip = task
                result = self.scanner.scan(ip)
                
                with self.results_lock:
                    self.results.append(result)
                    self.processed_count += 1
                    if self.progress_callback:
                        self.progress_callback(self.processed_count, self.total_count)
                    if self.result_callback:
                        self.result_callback(result)
                
                self.ip_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                continue
    
    def start_scan(self, items: List[str], scan_method: str, fake_sni: str = None,
                   previous_scanned: set = None, force: bool = False) -> List[ScanResult]:
        """Start scanning IPs or CIDR ranges"""
        if self.is_running:
            raise Exception("Scanner is already running")
        
        # Prepare IPs
        valid_ips = self._prepare_ips(items, previous_scanned, force)
        
        if not valid_ips:
            print("\n[ERROR] No valid IPs to scan!")
            return []
        
        # Create scanner
        self.scanner = self._create_scanner(scan_method, fake_sni)
        
        self.total_count = len(valid_ips)
        self.processed_count = 0
        self.results = []
        self.is_running = True
        self.is_paused = False
        
        # Clear and fill queue
        while not self.ip_queue.empty():
            try:
                self.ip_queue.get_nowait()
            except:
                break
        
        for ip in valid_ips:
            self.ip_queue.put(ip)
        
        # Add poison pills
        for _ in range(self.max_workers):
            self.ip_queue.put(None)
        
        # Start workers
        self.workers = []
        for _ in range(self.max_workers):
            t = threading.Thread(target=self._worker)
            t.daemon = True
            t.start()
            self.workers.append(t)
        
        # Wait for all workers
        for t in self.workers:
            t.join()
        
        self.is_running = False
        return self.results
    
    def pause(self):
        """Pause scanning"""
        with self.pause_condition:
            if self.is_running and not self.is_paused:
                self.is_paused = True
                print("\n[PAUSED]")
    
    def resume(self):
        """Resume scanning"""
        with self.pause_condition:
            if self.is_running and self.is_paused:
                self.is_paused = False
                self.pause_condition.notify_all()
                print("\n[RESUMED]")
    
    def stop(self):
        """Stop scanning"""
        self.is_running = False
        with self.pause_condition:
            self.is_paused = False
            self.pause_condition.notify_all()
        print("\n[STOPPING] Please wait...")