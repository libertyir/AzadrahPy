#!/usr/bin/env python3
"""
geosite_parser.py - Geosite.dat parser using dat-editor parser
Lazy loading with caching - loads once, caches results
"""

import os
import sys
import time
from typing import List, Dict, Set, Optional

# Add parent directory to path for geoparser imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_geoparser_path = os.path.join(_current_dir, 'geoparser')
if _geoparser_path not in sys.path:
    sys.path.insert(0, _geoparser_path)

# Import from geoparser modules - مسیر درست
from geoparser.models import GeoSiteList, GeoSite, Domain
from geoparser.parser import load_geosite
from geoparser.storage import load as load_dat_file


class GeositeParser:
    """Parse geosite.dat using dat-editor parser"""
    
    def __init__(self, filepath: str = "geosite.dat"):
        self.filepath = filepath
        self.domains_by_tag: Dict[str, Set[str]] = {}
        self.all_domains: Set[str] = set()
        self.is_loaded = False
        self.geosite_list: Optional[GeoSiteList] = None
        self.load_time = 0
    
    def load(self, silent: bool = False) -> bool:
        """Load and extract domains from geosite.dat"""
        if self.is_loaded:
            return True
            
        if not os.path.exists(self.filepath):
            if not silent:
                print(f"geosite.dat not found at {self.filepath}")
            return False
        
        start_time = time.time()
        
        try:
            ftype, data = load_dat_file(self.filepath)
            
            if ftype == "geosite" and isinstance(data, GeoSiteList):
                self.geosite_list = data
            else:
                self.geosite_list = load_geosite(self.filepath)
            
            self._parse_geosite_data()
            
            self.is_loaded = True
            self.load_time = time.time() - start_time
            
            if not silent:
                print(f"Loaded geosite.dat in {self.load_time:.2f}s")
                print(f"  - {len(self.geosite_list.entries)} site entries")
                print(f"  - {len(self.all_domains)} total domains")
                print(f"  - {len(self.domains_by_tag)} tagged categories")
            
            return True
            
        except Exception as e:
            if not silent:
                print(f"Error loading geosite.dat: {e}")
            return False
    
    def _parse_geosite_data(self):
        """Parse GeoSiteList into domains_by_tag dictionary"""
        if not self.geosite_list:
            return
        
        for entry in self.geosite_list.entries:
            tag = entry.code or entry.country_code
            if not tag:
                continue
            
            if tag not in self.domains_by_tag:
                self.domains_by_tag[tag] = set()
            
            for domain in entry.domains:
                domain_str = domain.value
                self.domains_by_tag[tag].add(domain_str)
                self.all_domains.add(domain_str)
    
    def get_domains_by_tag(self, tag: str) -> List[str]:
        """Get domains for a specific tag"""
        if not self.is_loaded:
            return []
        
        tag_lower = tag.lower()
        
        for t in self.domains_by_tag:
            if t.lower() == tag_lower:
                return sorted(self.domains_by_tag[t])
        
        for t in self.domains_by_tag:
            if tag_lower in t.lower():
                return sorted(self.domains_by_tag[t])
        
        return []
    
    def search_domains(self, keyword: str) -> List[str]:
        """Search domains containing keyword"""
        if not self.is_loaded:
            return []
        
        keyword_lower = keyword.lower()
        results = []
        
        for domain in self.all_domains:
            if keyword_lower in domain.lower():
                results.append(domain)
        
        return sorted(results)[:10000]
    
    def get_all_tags(self) -> List[str]:
        """Get all available tags"""
        if not self.is_loaded:
            return []
        return sorted(self.domains_by_tag.keys())
    
    def get_stats(self) -> dict:
        """Get statistics"""
        if not self.is_loaded:
            return {'total_domains': 0, 'total_tags': 0, 'tags': []}
        
        return {
            'total_domains': len(self.all_domains),
            'total_tags': len(self.domains_by_tag),
            'tags': list(self.domains_by_tag.keys())[:2000],
            'load_time': self.load_time
        }


class GeositeManager:
    """Manager for geosite operations with fallback to built-in lists"""
    
    def __init__(self, dat_path: str = "geosite.dat"):
        self.dat_path = dat_path
        self.parser: Optional[GeositeParser] = None
        self._load_attempted = False
        self._cache: Dict[str, List[str]] = {}
        
        self.builtin_domains = {
            'google': ['google.com', 'gstatic.com', 'googleapis.com', 'youtube.com'],
            'facebook': ['facebook.com', 'fbcdn.net', 'instagram.com'],
            'twitter': ['twitter.com', 'twimg.com', 'x.com'],
            'github': ['github.com', 'github.io', 'githubusercontent.com'],
            'cloudflare': ['cloudflare.com', 'cfassets.com'],
            'microsoft': ['microsoft.com', 'windows.com', 'office.com'],
            'apple': ['apple.com', 'icloud.com'],
            'netflix': ['netflix.com', 'nflxext.com'],
            'amazon': ['amazon.com', 'amazonaws.com'],
            'telegram': ['telegram.org', 't.me'],
            'whatsapp': ['whatsapp.com'],
            'instagram': ['instagram.com'],
            'reddit': ['reddit.com'],
            'youtube': ['youtube.com', 'youtu.be'],
            'cn': ['baidu.com', 'qq.com', 'taobao.com'],
            'ir': ['aparat.com', 'digikala.com', 'divar.ir'],
        }
    
    def _ensure_parser(self, silent: bool = False) -> bool:
        """Initialize parser only when needed"""
        if self.parser is not None and self.parser.is_loaded:
            return True
        
        if self._load_attempted:
            return False
        
        self._load_attempted = True
        self.parser = GeositeParser(self.dat_path)
        
        if self.parser.load(silent=silent):
            return True
        else:
            self.parser = None
            return False
    
    def extract_domains_by_geosite(self, tag: str, silent: bool = False) -> List[str]:
        """Extract domains from geosite.dat for a given tag"""
        tag_lower = tag.lower()
        
        if tag_lower in self._cache:
            return self._cache[tag_lower]
        
        if self._ensure_parser(silent=silent):
            domains = self.parser.get_domains_by_tag(tag)
            if domains:
                self._cache[tag_lower] = domains
                return domains
            
            domains = self.parser.search_domains(tag)
            if domains:
                self._cache[tag_lower] = domains
                return domains
        
        if tag_lower in self.builtin_domains:
            domains = self.builtin_domains[tag_lower]
            self._cache[tag_lower] = domains
            return domains
        
        for key, domains in self.builtin_domains.items():
            if tag_lower in key or key in tag_lower:
                self._cache[tag_lower] = domains
                return domains
        
        return []
    
    def list_available_tags(self) -> List[str]:
        """List all available tags"""
        tags = set(self.builtin_domains.keys())
        
        if self.parser and self.parser.is_loaded:
            tags.update(self.parser.get_all_tags())
        
        return sorted(tags)
    
    def search_tag(self, keyword: str, silent: bool = False) -> List[str]:
        """Search tags containing keyword"""
        return self.extract_domains_by_geosite(keyword, silent=silent)
    
    def is_available(self) -> bool:
        """Check if geosite.dat is available"""
        return os.path.exists(self.dat_path)
    
    def reload(self, silent: bool = False) -> bool:
        """Force reload geosite.dat"""
        self.parser = None
        self._load_attempted = False
        self._cache.clear()
        return self._ensure_parser(silent=silent)
    
    def clear_cache(self):
        """Clear resolved tags cache"""
        self._cache.clear()


# Test
if __name__ == "__main__":
    manager = GeositeManager("geosite.dat")
    
    print("="*60)
    print("GEOSITE MANAGER TEST")
    print("="*60)
    
    for tag in ['google', 'github', 'facebook']:
        domains = manager.extract_domains_by_geosite(tag)
        print(f"\n{tag}: {len(domains)} domains")
        if domains:
            print(f"  Sample: {domains[:3]}")