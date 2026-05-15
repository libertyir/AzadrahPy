#!/usr/bin/env python3
"""Fast Scanner - Ping → nslookup → Port 443 SSL"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from utils import NetworkUtils, SSLUtils, CIDRUtils


@dataclass
class ScanResult:
    ip: str
    hostname: Optional[str]
    ping_response: bool
    open_ports: List[int]
    ssl_domains: List[str]
    http_headers: Dict
    scan_time: str
    method_used: str


class FastScanner:
    """Fast scan: Ping first, then port 443 SSL"""
    
    def __init__(self, timeout: int = 3):
        self.timeout = timeout
    
    def scan(self, ip: str) -> ScanResult:
        result = ScanResult(
            ip=ip, hostname=None, ping_response=False, open_ports=[],
            ssl_domains=[], http_headers={},
            scan_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            method_used="fast"
        )
        
        # Step 1: Ping
        result.ping_response = NetworkUtils.ping_host(ip, self.timeout)

        # Step 3: Get hostname (if ping succeeded)
        if result.ping_response:
            result.hostname = NetworkUtils.get_hostname(ip)
            if NetworkUtils.check_port(ip, 443, self.timeout):
                result.open_ports.append(443)
                result.ssl_domains = SSLUtils.extract_domains_from_ssl(ip, 443, self.timeout)
        
        return result