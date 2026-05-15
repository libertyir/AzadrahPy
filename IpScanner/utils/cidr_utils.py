#!/usr/bin/env python3
"""CIDR utilities - IP validation and CIDR expansion"""

import re
from typing import List


class CIDRUtils:
    """CIDR and IP address utilities"""
    
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """Validate IP address (not CIDR)"""
        ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        if not ip_pattern.match(ip):
            return False
        parts = ip.split('.')
        for part in parts:
            if int(part) > 255:
                return False
        return True
    
    @staticmethod
    def is_valid_cidr(cidr: str) -> bool:
        """Validate CIDR notation"""
        try:
            import ipaddress
            if ':' in cidr:
                return False

            ipaddress.ip_network(cidr, strict=False)
            return True
        except:
            return False
    
    @staticmethod
    def expand_cidr(cidr: str) -> List[str]:
        """Expand a CIDR range to ALL individual IPs (no limit)"""
        ips = []
        try:
            import ipaddress
            network = ipaddress.ip_network(cidr, strict=False)
            total = network.num_addresses - 2
            print(f"  {cidr} -> {total} IPs")
            
            for ip in network.hosts():
                ips.append(str(ip))
        except Exception as e:
            print(f"  Error expanding {cidr}: {e}")
        
        return ips