#!/usr/bin/env python3
"""SSL utilities - certificate extraction and domain parsing"""

import ssl
import socket
import sys
import os
from typing import List, Optional

# Add parent directory to path for x509_parser
# چون x509_parser در پوشه utils است، نیازی به مسیر پیچیده نیست
from .x509_parser import parse_pem, parse_cert


class SSLUtils:
    """SSL/TLS certificate utilities"""
    
    @staticmethod
    def get_certificate_pem(ip: str, port: int = 443, timeout: int = 3) -> Optional[str]:
        """Get certificate in PEM format from IP:port"""
        # Method 1: Try with SSL context
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((ip, port), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=ip) as ssock:
                    cert_binary = ssock.getpeercert(binary_form=True)
                    if cert_binary:
                        return ssl.DER_cert_to_PEM_cert(cert_binary)
        except:
            pass
        
        # Method 2: Use get_server_certificate
        try:
            cert_pem = ssl.get_server_certificate((ip, port), timeout=timeout)
            if cert_pem and "BEGIN CERTIFICATE" in cert_pem:
                return cert_pem
        except:
            pass
        
        return None
    
    @staticmethod
    def parse_certificate_pem(cert_pem: str) -> List[str]:
        """Parse PEM certificate and extract all domains (CN + SAN)"""
        domains = []
        
        if not cert_pem or "BEGIN CERTIFICATE" not in cert_pem:
            return domains
        
        try:
            der_data = parse_pem(cert_pem)
            cert = parse_cert(der_data)
            domains = cert.get_all_domains()
        except Exception as e:
            pass
        
        return list(set(domains))
    
    @staticmethod
    def extract_domains_from_ssl(ip: str, port: int = 443, timeout: int = 3) -> List[str]:
        """Extract domains from SSL certificate"""
        cert_pem = SSLUtils.get_certificate_pem(ip, port, timeout)
        if not cert_pem:
            return []
        
        domains = SSLUtils.parse_certificate_pem(cert_pem)
        
        # Filter domains
        unique_domains = []
        seen = set()
        for d in domains:
            d_lower = d.lower()
            if d_lower not in seen and '*' not in d and len(d) > 3 and '.' in d:
                seen.add(d_lower)
                unique_domains.append(d)
        
        return unique_domains[:20]