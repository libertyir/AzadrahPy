#!/usr/bin/env python3
"""
Geoparser module - for reading geosite.dat and geoip.dat files
"""

from .models import (
    Attribute,
    CIDR,
    Domain,
    GeoIP,
    GeoIPList,
    GeoSite,
    GeoSiteList,
)

from .parser import (
    load_geoip,
    load_geosite,
    save_geoip,
    save_geosite,
)

from .storage import (
    load as load_dat,
    save as save_dat,
    infer_type,
)

__all__ = [
    'Attribute', 'CIDR', 'Domain', 'GeoIP', 'GeoIPList', 'GeoSite', 'GeoSiteList',
    'load_geoip', 'load_geosite', 'save_geoip', 'save_geosite',
    'load_dat', 'save_dat', 'infer_type'
]