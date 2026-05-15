#!/usr/bin/env python3
"""Deep Scanner - Multiple ports (80,443,8080,8443)"""

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


class DeepScanner:
    """Deep scan: Check multiple ports even if ping fails"""
    
    def __init__(self, timeout: int = 3):
        self.timeout = timeout
        self.ports_to_check = [80, 443, 8080, 8443]
    
    def scan(self, ip: str) -> ScanResult:
        result = ScanResult(
            ip=ip, hostname=None, ping_response=False, open_ports=[],
            ssl_domains=[], http_headers={},
            scan_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            method_used="deep"
        )
        
        # Step 1: Ping (don't stop if fails)
        result.ping_response = NetworkUtils.ping_host(ip, self.timeout)
        
        # Step 2: Check multiple ports
        for port in self.ports_to_check:
            if NetworkUtils.check_port(ip, port, self.timeout):
                result.open_ports.append(port)
        
        # Step 3: If any port is open, get additional info
        if result.open_ports:
            result.hostname = NetworkUtils.get_hostname(ip)
            
            # SSL extraction on ports 443 and 8443
            for port in [443, 8443]:
                if port in result.open_ports:
                    ssl_domains = SSLUtils.extract_domains_from_ssl(ip, port, self.timeout)
                    result.ssl_domains.extend(ssl_domains)
            result.ssl_domains = list(set(result.ssl_domains))
            
            # HTTP header check on port 80
            if 80 in result.open_ports:
                result.http_headers = NetworkUtils.check_http_response(ip, 80, self.timeout)
        
        return result
