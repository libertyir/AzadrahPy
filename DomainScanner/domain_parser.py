#!/usr/bin/env python3
"""
Domain Parser - Parses domain entries with support for geosite: tags
All domain validation happens here - no duplication in scanner
"""

import re
import os
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass


@dataclass
class ParsedDomain:
    """Result of parsing a domain entry"""
    original: str
    is_geosite: bool
    tag: Optional[str]
    domains: List[str]
    is_valid: bool = True
    error: Optional[str] = None


class DomainValidator:
    """Single source of truth for domain validation"""
    
    DOMAIN_PATTERN = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    )
    WILDCARD_PATTERN = re.compile(r'^\*\.(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$')
    REGEX_PATTERN = re.compile(r'^/.*/$')
    
    @classmethod
    def is_valid(cls, domain: str) -> bool:
        """Check if a domain is valid for scanning"""
        domain = domain.strip().lower()
        if not domain or len(domain) > 253:
            return False
        
        if cls.REGEX_PATTERN.match(domain):
            return False
        
        if cls.WILDCARD_PATTERN.match(domain):
            return True
        
        parts = domain.split('.')
        if len(parts) < 2:
            return False
        
        part_pattern = re.compile(r'^[a-z0-9-]+$')
        for part in parts:
            if not part_pattern.match(part):
                return False
        
        return True
    
    @classmethod
    def extract_scan_domains(cls, domain: str) -> List[str]:
        """Extract actual domains to scan from a pattern"""
        domain = domain.strip().lower()
        
        if cls.REGEX_PATTERN.match(domain):
            return []
        
        if cls.WILDCARD_PATTERN.match(domain):
            return [domain[2:]]
        
        if cls.is_valid(domain):
            return [domain]
        
        return []


class DomainParser:
    """Parse domain entries and expand geosite: tags"""
    
    GEOSITE_PATTERN = re.compile(r'^geosite:([a-zA-Z0-9_\-]+)$', re.IGNORECASE)
    
    def __init__(self, geosite_manager=None):
        self.geosite_manager = geosite_manager
        self.validator = DomainValidator()
    
    def is_geosite_tag(self, entry: str) -> bool:
        return bool(self.GEOSITE_PATTERN.match(entry.strip()))
    
    def extract_tag(self, entry: str) -> Optional[str]:
        match = self.GEOSITE_PATTERN.match(entry.strip())
        return match.group(1) if match else None
    
    def parse_line(self, line: str) -> ParsedDomain:
        """Parse a single line from domains.txt"""
        line = line.strip()
        if not line:
            return ParsedDomain(
                original=line, is_geosite=False, tag=None,
                domains=[], is_valid=False, error="Empty line"
            )
        
        if self.is_geosite_tag(line):
            tag = self.extract_tag(line)
            if not tag:
                return ParsedDomain(
                    original=line, is_geosite=True, tag=None,
                    domains=[], is_valid=False,
                    error=f"Invalid geosite format: {line}"
                )
            
            domains = self._resolve_geosite_tag(tag)
            valid_domains = [d for d in domains if self.validator.is_valid(d)]
            
            return ParsedDomain(
                original=line, is_geosite=True, tag=tag,
                domains=valid_domains,
                is_valid=bool(valid_domains),
                error=None if valid_domains else f"No valid domains for geosite:{tag}"
            )
        
        # Regular domain
        is_valid = self.validator.is_valid(line)
        return ParsedDomain(
            original=line, is_geosite=False, tag=None,
            domains=[line] if is_valid else [],
            is_valid=is_valid,
            error=None if is_valid else f"Invalid domain: {line}"
        )
    
    def _resolve_geosite_tag(self, tag: str) -> List[str]:
        """Resolve geosite tag - always fresh read, no cache"""
        if not self.geosite_manager:
            print(f"[WARNING] No GeositeManager for geosite:{tag}")
            return []
        
        try:
            return self.geosite_manager.extract_domains_by_geosite(tag)
        except Exception as e:
            print(f"[ERROR] Failed to resolve geosite:{tag}: {e}")
            return []
    
    def expand_all(self, lines: List[str], previous_scanned: Set[str] = None) -> List[str]:
        """
        Expand all entries to flat list of domains
        previous_scanned: domains already scanned (will be filtered out)
        """
        all_domains = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if self.is_geosite_tag(line):
                domains = self._resolve_geosite_tag(self.extract_tag(line))
                for d in domains:
                    if self.validator.is_valid(d):
                        if previous_scanned and d in previous_scanned:
                            print(f"[SKIP] Already scanned: {d}")
                            continue
                        all_domains.append(d)
            else:
                if self.validator.is_valid(line):
                    if previous_scanned and line in previous_scanned:
                        print(f"[SKIP] Already scanned: {line}")
                        continue
                    all_domains.append(line)
                else:
                    print(f"[WARNING] Invalid domain skipped: {line}")
        
        # Remove duplicates
        seen = set()
        unique = []
        for d in all_domains:
            if d not in seen:
                seen.add(d)
                unique.append(d)
        
        return unique
    
    def preview(self, filepath: str) -> None:
        """Preview how domains.txt will be expanded"""
        if not os.path.exists(filepath):
            print(f"[ERROR] File not found: {filepath}")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("\n" + "="*60)
        print("DOMAIN FILE PREVIEW")
        print("="*60)
        
        total_domains = 0
        invalid_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if self.is_geosite_tag(line):
                tag = self.extract_tag(line)
                domains = self._resolve_geosite_tag(tag) if tag else []
                valid = [d for d in domains if self.validator.is_valid(d)]
                total_domains += len(valid)
                print(f"\n{line}")
                print(f"  └─ {len(valid)} valid domains")
                for d in valid[:5]:
                    print(f"       {d}")
                if len(valid) > 5:
                    print(f"       ... and {len(valid)-5} more")
            else:
                if self.validator.is_valid(line):
                    total_domains += 1
                    print(f"\n{line} -> {line} [VALID]")
                else:
                    invalid_count += 1
                    print(f"\n{line} -> [INVALID] {line}")
        
        print("\n" + "="*60)
        print(f"SUMMARY: {total_domains} domains to scan, {invalid_count} invalid skipped")
        print("="*60)