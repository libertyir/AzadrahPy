import csv
import os
from datetime import datetime
from typing import Dict, List, Set


class StorageManager:
    def __init__(self, batch_size: int = 100):
        self.archive_file = "archive.csv"
        self.live_file = "IsLive.txt"
        self.domains_file = "domains.txt"
        self._previous_cache = None
        self._batch_buffer = []
        self._batch_size = batch_size
        
        for f in [self.archive_file, self.live_file, self.domains_file]:
            if not os.path.exists(f):
                open(f, 'w').close()
    
    def load_previous(self, use_cache: bool = True) -> Set[str]:
        """Load previously checked domains with caching"""
        if use_cache and self._previous_cache is not None:
            return self._previous_cache
        
        checked = set()
        if os.path.exists(self.archive_file):
            with open(self.archive_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                try:
                    next(reader)
                    for row in reader:
                        if row:
                            checked.add(row[0].strip())
                except:
                    pass
        
        self._previous_cache = checked
        return checked
    
    def invalidate_cache(self):
        """Invalidate the previous scan cache"""
        self._previous_cache = None
    
    def load_domains_raw(self) -> List[str]:
        """Load raw lines from domains.txt"""
        if not os.path.exists(self.domains_file):
            return []
        
        with open(self.domains_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    
    def load_domains(self) -> List[str]:
        """Load domains from file - alias for load_domains_raw"""
        return self.load_domains_raw()
    
    def save_result(self, result: Dict):
        """Save result to buffer, auto-flush when buffer is full"""
        self._batch_buffer.append(result)
        
        if len(self._batch_buffer) >= self._batch_size:
            self.flush()
            self._previous_cache = None
    
    def flush(self):
        """Force flush buffer to disk"""
        if not self._batch_buffer:
            return
        
        # Write to archive
        file_exists = os.path.exists(self.archive_file)
        file_has_content = file_exists and os.path.getsize(self.archive_file) > 0
        
        with open(self.archive_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if not file_has_content:
                writer.writerow(["Domain", "IP", "Status", "Accessible", "CheckedAt"])
            
            for result in self._batch_buffer:
                writer.writerow([
                    result["domain"],
                    result.get("ip", ""),
                    result.get("status", "unknown"),
                    result.get("accessible", False),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])
        
        # Write to live file
        with open(self.live_file, 'a', encoding='utf-8') as f:
            for result in self._batch_buffer:
                if result.get("accessible"):
                    f.write(f"{result['domain']} => {result.get('ip', 'NO_IP')}\n")
        
        self._batch_buffer = []
    
    def add_domains_batch(self, domains: List[str]) -> int:
        """Add multiple domains to file (no duplicate check)"""
        existing = set(self.load_domains())
        added = 0
        
        with open(self.domains_file, 'a', encoding='utf-8') as f:
            for domain in domains:
                domain = domain.strip()
                if domain and domain not in existing:
                    f.write(f"{domain}\n")
                    existing.add(domain)
                    added += 1
        return added
    
    def add_domain(self, domain: str) -> bool:
        """Add single domain"""
        return self.add_domains_batch([domain]) > 0
    
    def read_live(self) -> List[str]:
        """Read live domains"""
        if not os.path.exists(self.live_file):
            return []
        with open(self.live_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    
    def read_archive(self) -> List[List[str]]:
        """Read archive entries"""
        entries = []
        if os.path.exists(self.archive_file):
            with open(self.archive_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                try:
                    next(reader)
                    for row in reader:
                        if row:
                            entries.append(row)
                except:
                    pass
        return entries
    
    def search_archive(self, domain: str) -> List[List[str]]:
        """Search for domain in archive"""
        return [e for e in self.read_archive() if e[0].lower() == domain.lower()]
    
    def sort_live(self):
        """Sort live domains"""
        if os.path.exists(self.live_file):
            with open(self.live_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            lines.sort(key=lambda x: x.split('=>')[0].strip().lower())
            with open(self.live_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
    
    def sort_domains(self):
        """Sort domains file"""
        domains = self.load_domains()
        unique = list(dict.fromkeys(domains))
        unique.sort(key=lambda x: x.lower())
        with open(self.domains_file, 'w', encoding='utf-8') as f:
            for d in unique:
                f.write(f"{d}\n")
    
    def sort_archive(self):
        """Sort archive by domain"""
        entries = self.read_archive()
        entries.sort(key=lambda x: x[0].lower())
        with open(self.archive_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Domain", "IP", "Status", "Accessible", "CheckedAt"])
            writer.writerows(entries)