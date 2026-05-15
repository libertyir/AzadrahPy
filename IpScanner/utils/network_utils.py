
#!/usr/bin/env python3
"""Network utilities - ping, port check, hostname resolution"""

import socket
import subprocess
import platform
from typing import Optional


class NetworkUtils:
    """Network-related utilities"""
    
    @staticmethod
    def ping_host(ip: str, timeout: int = 2) -> bool:
        """Ping a host (cross-platform)"""
        system = platform.system().lower()
        
        try:
            if system == "windows":
                timeout_ms = int(timeout * 1000)
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', str(timeout_ms), ip],
                    capture_output=True,
                    timeout=timeout + 1
                )
                if result.returncode == 0:
                    output = result.stdout.decode('utf-8', errors='ignore')
                    if "Reply from" in output or "TTL=" in output:
                        return True
                return False
            else:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', str(timeout), ip],
                    capture_output=True,
                    timeout=timeout + 1
                )
                return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def check_port(ip: str, port: int, timeout: int = 2) -> bool:
        """Check if a port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    @staticmethod
    def get_hostname(ip: str) -> Optional[str]:
        """Get hostname from IP using reverse DNS"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return None
    
    @staticmethod
    def check_http_response(ip: str, port: int, timeout: int = 3, sni: str = None) -> dict:
        """Check HTTP/HTTPS response"""
        import requests
        
        result = {
            'status_code': None,
            'server': None,
            'headers': {},
            'location': None
        }
        
        scheme = 'https' if port in [443, 8443] else 'http'
        url = f"{scheme}://{ip}:{port}"
        
        try:
            headers = {}
            if sni:
                headers['Host'] = sni
            
            response = requests.get(url, timeout=timeout, headers=headers, verify=False, allow_redirects=False)
            result['status_code'] = response.status_code
            result['server'] = response.headers.get('Server', '')
            result['headers'] = dict(response.headers)
            result['location'] = response.headers.get('Location', '')
        except:
            pass
        
        return result