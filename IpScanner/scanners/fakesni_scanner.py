#!/usr/bin/env python3
"""Fake SNI Scanner - Scan with custom Server Name Indication"""

import ssl
import socket
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


class FakeSNIScanner:
    """Fake SNI scan: Use custom SNI to connect"""
    
    def __init__(self, timeout: int = 3, fake_sni: str = "www.google.com"):
        self.timeout = timeout
        self.fake_sni = fake_sni
        self.ports_to_check = [80, 443, 8080, 8443]
    
    def scan(self, ip: str) -> ScanResult:
        result = ScanResult(
            ip=ip, hostname=None, ping_response=False, open_ports=[],
            ssl_domains=[], http_headers={},
            scan_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            method_used=f"fakesni_{self.fake_sni}"
        )
        
        # Step 1: Ping
        result.ping_response = NetworkUtils.ping_host(ip, self.timeout)
        
        # Step 2: Check ports
        for port in self.ports_to_check:
            if NetworkUtils.check_port(ip, port, self.timeout):
                result.open_ports.append(port)
        
        # Step 3: SSL with fake SNI
        for port in [443, 8443]:
            if port in result.open_ports:
                try:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    
                    with socket.create_connection((ip, port), timeout=self.timeout) as sock:
                        with context.wrap_socket(sock, server_hostname=self.fake_sni) as ssock:
                            cert_binary = ssock.getpeercert(binary_form=True)
                            if cert_binary:
                                cert_pem = ssl.DER_cert_to_PEM_cert(cert_binary)
                                result.ssl_domains = SSLUtils.parse_certificate_pem(cert_pem)
                except:
                    pass
        
        # Step 4: HTTP with fake Host header
        for port in [80, 8080, 8443]:
            if port in result.open_ports:
                http_result = NetworkUtils.check_http_response(ip, port, self.timeout, sni=self.fake_sni)
                if http_result.get('status_code'):
                    result.http_headers = http_result
        
        result.ssl_domains = list(set(result.ssl_domains))
        result.hostname = NetworkUtils.get_hostname(ip)
        return result