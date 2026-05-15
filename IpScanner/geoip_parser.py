#!/usr/bin/env python3
"""
GeoIP Manager - Using dat-editor parser
"""

import os
import sys
from typing import List, Optional

# Add current directory to path to ensure geoparser is found
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Now import from geoparser
try:
    from geoparser.parser import load_geoip
    from geoparser.models import GeoIPList, GeoIP, CIDR
    from geoparser.storage import load as load_dat_file
    GEOPARSER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import geoparser: {e}")
    print("Falling back to built-in parser...")
    GEOPARSER_AVAILABLE = False


class GeoIPManager:
    """Manager for geoip operations"""
    
    def __init__(self, dat_path: str = "geoip.dat"):
        self.dat_path = dat_path
        self.geoip_list = None
        self.is_loaded = False
    
    def load(self) -> bool:
        """Load geoip.dat file"""
        if not os.path.exists(self.dat_path):
            print(f"geoip.dat not found at {self.dat_path}")
            return False
        
        if not GEOPARSER_AVAILABLE:
            print("Geoparser not available, using fallback mode")
            return False
        
        try:
            # Use storage.load() which auto-detects file type
            from geoparser.storage import load as load_dat
            ftype, data = load_dat(self.dat_path)
            
            if ftype == "geoip":
                self.geoip_list = data
                self.is_loaded = True
                
                total_cidrs = sum(len(entry.cidrs) for entry in self.geoip_list.entries)
                print(f"Loaded {len(self.geoip_list.entries)} country records from geoip.dat")
                print(f"Total IP ranges: {total_cidrs}")
                
                return True
            else:
                print(f"File type mismatch: expected geoip, got {ftype}")
                return False
                
        except Exception as e:
            print(f"Error loading geoip.dat: {e}")
            return False
    
    def get_ip_ranges_by_country(self, country_code: str) -> List[str]:
        """Get IP ranges for a country code"""
        if not self.is_loaded:
            if not self.load():
                return self._get_builtin_fallback(country_code)
        
        if not self.geoip_list:
            return self._get_builtin_fallback(country_code)
        
        country_upper = country_code.upper()
        
        # Search in loaded data
        for entry in self.geoip_list.entries:
            if entry.code.upper() == country_upper:
                return [cidr.to_string() for cidr in entry.cidrs]
        
        # Try partial match
        for entry in self.geoip_list.entries:
            if country_upper in entry.code.upper() or entry.code.upper() in country_upper:
                return [cidr.to_string() for cidr in entry.cidrs]
        
        return self._get_builtin_fallback(country_code)
    
    def get_all_countries(self) -> List[str]:
        """Get all available country codes"""
        if not self.is_loaded:
            self.load()
        
        if self.geoip_list:
            return sorted([entry.code for entry in self.geoip_list.entries])
        return []
    
    def _get_builtin_fallback(self, country_code: str) -> List[str]:
        """Fallback built-in IP ranges"""
        builtin_ranges = {
            'US': ['8.8.8.0/24', '8.8.4.0/24', '4.4.4.0/24', '13.32.0.0/15'],
            'CN': ['1.0.0.0/8', '14.0.0.0/8', '27.0.0.0/8', '36.0.0.0/8', '39.0.0.0/8'],
            'RU': ['5.0.0.0/8', '31.0.0.0/8', '46.0.0.0/8', '77.0.0.0/8', '80.0.0.0/8'],
            'DE': ['2.200.0.0/13', '5.144.128.0/19', '13.224.0.0/14'],
            'GB': ['2.96.0.0/11', '2.120.0.0/13', '5.64.0.0/13'],
            'JP': ['1.0.16.0/20', '1.0.64.0/18', '1.1.0.0/16', '1.21.0.0/16'],
            'KR': ['1.11.0.0/16', '1.96.0.0/13', '1.208.0.0/12', '3.32.0.0/14'],
            'FR': ['2.0.0.0/12', '2.16.0.0/13', '2.24.0.0/14', '5.48.0.0/13'],
        }
        
        country_upper = country_code.upper()
        if country_upper in builtin_ranges:
            print(f"Using built-in IP ranges for '{country_upper}'")
            return builtin_ranges[country_upper]
        
        return []


# Quick test
if __name__ == "__main__":
    manager = GeoIPManager("geoip.dat")
    
    print("="*50)
    print("Testing GeoIP Manager")
    print("="*50)
    
    if os.path.exists("geoip.dat"):
        manager.load()
        countries = manager.get_all_countries()
        print(f"\nCountries found: {len(countries)}")
        if countries:
            print(f"Sample: {', '.join(countries[:20])}")
    else:
        print("geoip.dat not found, using built-in fallback")
    
    # Test extraction
    print("\n" + "="*50)
    print("IP Range Extraction Test:")
    print("="*50)
    
    for test_code in ['US', 'CN', 'DE', 'JP']:
        ranges = manager.get_ip_ranges_by_country(test_code)
        print(f"\n{test_code}: {len(ranges)} IP ranges")
        if ranges:
            print(f"  Sample: {ranges[:3]}")