#!/usr/bin/env python3
"""
IP Storage Manager - Handle file operations for IP scanner
"""

import csv
import os
import json
import re
from datetime import datetime
from typing import List, Dict, Set, Optional
from ip_scanner_core import ScanResult


class IPStorageManager:
    """Handle file operations for IP scanner"""
    
    def __init__(self):
        self.ips_file = "ips.txt"
        self.archive_file = "ip_archive.csv"
        self.live_file = "LiveIPs.txt"
        self.domains_extracted_file = "extracted_domains.txt"
        
        # Create files if not exist
        for f in [self.ips_file, self.archive_file, self.live_file, self.domains_extracted_file]:
            if not os.path.exists(f):
                with open(f, 'w', encoding='utf-8') as file:
                    pass
    
    def load_ips(self) -> List[str]:
        """Load IPs/CIDRs from file"""
        if not os.path.exists(self.ips_file):
            return []
        
        with open(self.ips_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    
    def load_previous_results(self) -> Set[str]:
        """Load previously scanned IPs from archive"""
        scanned = set()
        if not os.path.exists(self.archive_file):
            return scanned
        
        with open(self.archive_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                next(reader)  # Skip header
                for row in reader:
                    if row:
                        scanned.add(row[0].strip())
            except StopIteration:
                pass
        
        return scanned
    
    def save_result(self, result: ScanResult):
        """Save scan result to archive"""
        file_exists = os.path.exists(self.archive_file)
        
        with open(self.archive_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if not file_exists or os.path.getsize(self.archive_file) == 0:
                writer.writerow([
                    "IP", "Hostname", "PingResponse", "OpenPorts", 
                    "SSL_Domains", "HTTP_StatusCode", "HTTP_Server",
                    "ScanMethod", "ScanTime"
                ])
            
            writer.writerow([
                result.ip,
                result.hostname or "",
                result.ping_response,
                ",".join(map(str, result.open_ports)),
                ",".join(result.ssl_domains),
                result.http_headers.get('status_code', ''),
                result.http_headers.get('server', ''),
                result.method_used,
                result.scan_time
            ])
        
        # Save to live file if ports are open
        if result.open_ports:
            self._add_to_live_file(result)
        
        # Extract and save domains from SSL
        if result.ssl_domains:
            self._save_extracted_domains(result.ssl_domains)
    
    def _add_to_live_file(self, result: ScanResult):
        """Add live IP to LiveIPs.txt"""
        existing = set()
        if os.path.exists(self.live_file):
            with open(self.live_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        existing.add(line.split('|')[0].strip())
        
        if result.ip not in existing:
            with open(self.live_file, 'a', encoding='utf-8') as f:
                ports = ",".join(map(str, result.open_ports))
                domains = ",".join(result.ssl_domains[:3]) if result.ssl_domains else ""
                f.write(f"{result.ip} | {ports} | {domains}\n")
    
    def _save_extracted_domains(self, domains: List[str]):
        """Save extracted domains to file (no duplicates)"""
        existing = set()
        if os.path.exists(self.domains_extracted_file):
            with open(self.domains_extracted_file, 'r', encoding='utf-8') as f:
                for line in f:
                    domain = line.strip()
                    if domain:
                        existing.add(domain)
        
        with open(self.domains_extracted_file, 'a', encoding='utf-8') as f:
            for domain in domains:
                if domain not in existing:
                    f.write(f"{domain}\n")
                    existing.add(domain)
    
    def read_live_ips(self) -> List[str]:
        """Read live IPs from file"""
        if not os.path.exists(self.live_file):
            return []
        
        with open(self.live_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    
    def read_archive(self) -> List[List[str]]:
        """Read all archive entries"""
        entries = []
        if not os.path.exists(self.archive_file):
            return entries
        
        with open(self.archive_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                next(reader)
                for row in reader:
                    if row:
                        entries.append(row)
            except StopIteration:
                pass
        
        return entries
    
    def search_archive(self, ip: str) -> List[List[str]]:
        """Search for IP in archive"""
        entries = self.read_archive()
        return [e for e in entries if e[0].strip() == ip.strip()]
    
    def add_ip(self, ip: str) -> bool:
        """Add IP to ips.txt if not exists"""
        from utils import CIDRUtils
        
        # Accept both IP and CIDR
        is_valid = CIDRUtils.is_valid_ip(ip) or CIDRUtils.is_valid_cidr(ip)
        
        if not is_valid:
            return False
        
        ips = self.load_ips()
        if ip in ips:
            return False
        
        with open(self.ips_file, 'a', encoding='utf-8') as f:
            f.write(f"{ip}\n")
        
        return True
    
    def add_ips_batch(self, ips: List[str]) -> int:
        """Add multiple IPs/CIDRs, skip duplicates and invalid"""
        from utils import CIDRUtils
        
        existing = set(self.load_ips())
        added = 0
        
        print(f"Processing {len(ips)} IP ranges...")
        
        with open(self.ips_file, 'a', encoding='utf-8') as f:
            for ip in ips:
                ip = ip.strip()
                # Check if it's valid (IP or CIDR)
                is_valid =  CIDRUtils.is_valid_ip(ip) or CIDRUtils.is_valid_cidr(ip)
                
                if is_valid and ip not in existing:
                    f.write(f"{ip}\n")
                    existing.add(ip)
                    added += 1
                    
                    # Progress indicator
                    if added % 100 == 0:
                        print(f"  Added {added} so far...")
        
        print(f"Successfully added {added} new IP ranges")
        return added
    
    def sort_ips_file(self):
        """Sort ips.txt file (IPv4 only for now)"""
        ips = self.load_ips()
        
        # Custom sort function for IPs
        def ip_key(ip_str):
            try:
                if '/' in ip_str:
                    ip_str = ip_str.split('/')[0]
                return [int(i) for i in ip_str.split('.')]
            except:
                return [0, 0, 0, 0]
        
        unique = list(dict.fromkeys(ips))
        unique.sort(key=ip_key)
        
        with open(self.ips_file, 'w', encoding='utf-8') as f:
            for ip in unique:
                f.write(f"{ip}\n")
    
    def sort_live_ips(self):
        """Sort LiveIPs.txt file"""
        if os.path.exists(self.live_file):
            with open(self.live_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            def ip_key(line):
                try:
                    ip = line.split('|')[0].strip()
                    if '/' in ip:
                        ip = ip.split('/')[0]
                    return [int(i) for i in ip.split('.')]
                except:
                    return [0, 0, 0, 0]
            
            lines.sort(key=ip_key)
            
            with open(self.live_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
    
    def sort_archive(self):
        """Sort archive by IP"""
        entries = self.read_archive()
        if not entries:
            return
        
        def ip_key(entry):
            try:
                ip = entry[0].strip()
                if '/' in ip:
                    ip = ip.split('/')[0]
                return [int(i) for i in ip.split('.')]
            except:
                return [0, 0, 0, 0]
        
        entries.sort(key=ip_key)
        
        with open(self.archive_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "IP", "Hostname", "PingResponse", "OpenPorts", 
                "SSL_Domains", "HTTP_StatusCode", "HTTP_Server",
                "ScanMethod", "ScanTime"
            ])
            writer.writerows(entries)
    
    def get_extracted_domains(self) -> List[str]:
        """Get all extracted domains from SSL certificates"""
        if not os.path.exists(self.domains_extracted_file):
            return []
        
        with open(self.domains_extracted_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]