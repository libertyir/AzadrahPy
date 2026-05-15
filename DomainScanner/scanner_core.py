import socket
import queue
import threading
import requests
from typing import Dict, List, Optional

class DomainScanner:
    def __init__(self, timeout: int = 3, max_workers: int = 20, headers: Dict = None):
        self.timeout = timeout
        self.max_workers = max_workers
        self.headers = headers or {'User-Agent': 'Mozilla/5.0'}
        self.is_running = False
        self.is_paused = False
        self.pause_condition = threading.Condition()
        self.domain_queue = queue.Queue()
        self.results = []
        self.results_lock = threading.Lock()
        self.processed_count = 0
        self.total_count = 0
        self.progress_callback = None
        self.domain_callback = None
    
    def set_callbacks(self, progress_callback=None, domain_callback=None):
        self.progress_callback = progress_callback
        self.domain_callback = domain_callback
    
    @staticmethod
    def get_ip(domain: str) -> Optional[str]:
        try:
            return socket.gethostbyname(domain)
        except:
            return None
    
    def check_domain(self, domain: str) -> Dict:
        ip = None        
        for scheme in ['https', 'http']:
            try:
                url = f"{scheme}://{domain}"
                r = requests.head(url, timeout=(self.timeout, self.timeout), headers=self.headers, allow_redirects=True)
                
                # اگر پاسخ دریافت شد، IP را بگیر
                ip = self.get_ip(domain)
                
                return {
                    "domain": domain,
                    "status": "live",
                    "ip": ip,
                    "accessible": True,
                    "status_code": r.status_code
                }
            except:
                continue
        
        return {
            "domain": domain,
            "status": "dead",
            "ip": None,
            "accessible": False
        }
    
    def worker(self):
        while self.is_running:
            with self.pause_condition:
                while self.is_paused and self.is_running:
                    self.pause_condition.wait()
            try:
                domain = self.domain_queue.get(timeout=1)
            except:
                continue
            if domain is None:
                break            
            result = self.check_domain(domain)            
            with self.results_lock:
                self.results.append(result)
                self.processed_count += 1
                if self.progress_callback:
                    self.progress_callback(self.processed_count, self.total_count)
                if self.domain_callback:
                    self.domain_callback(result)         
            self.domain_queue.task_done()
    
    def start_scan(self, domains: List[str], force: bool = False, previous_checked: set = None) -> List[Dict]:
        domains_to_scan = domains.copy()
        if not force and previous_checked:
            domains_to_scan = [d for d in domains_to_scan if d not in previous_checked]
        
        if not domains_to_scan:
            return []
        
        self.total_count = len(domains_to_scan)
        self.processed_count = 0
        self.results = []
        self.is_running = True
        self.is_paused = False
        for d in domains_to_scan:
            self.domain_queue.put(d)        
        for _ in range(self.max_workers):
            self.domain_queue.put(None)        
        workers = []
        for _ in range(self.max_workers):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            workers.append(t)        
        for t in workers:
            t.join()        
        self.is_running = False
        return self.results
    
    def pause(self):
        with self.pause_condition:
            self.is_paused = True
    
    def resume(self):
        with self.pause_condition:
            self.is_paused = False
            self.pause_condition.notify_all()
    
    def stop(self):
        self.is_running = False
        with self.pause_condition:
            self.is_paused = False
            self.pause_condition.notify_all()