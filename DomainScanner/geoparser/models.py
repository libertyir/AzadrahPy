"""
Data models for geosite.dat and geoip.dat entries.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


DOMAIN_TYPE_TO_NUM = {
    "plain": 0,  # substring match
    "regex": 1,
    "root": 2,   # root domain match
    "full": 3,   # exact match
}
NUM_TO_DOMAIN_TYPE = {v: k for k, v in DOMAIN_TYPE_TO_NUM.items()}


@dataclass
class Attribute:
    key: str
    bool_value: Optional[bool] = None
    int_value: Optional[int] = None

    def render(self) -> str:
        if self.int_value is not None:
            return f"{self.key}={self.int_value}"
        if self.bool_value in (True, None):
            return self.key
        if self.bool_value is False:
            return f"{self.key}=false"
        return self.key


@dataclass
class Domain:
    value: str
    dtype: str = "plain"
    attributes: List[Attribute] = field(default_factory=list)

    def render(self) -> str:
        attr = "" if not self.attributes else " @" + ",".join(a.render() for a in self.attributes)
        return f"{self.dtype}: {self.value}{attr}"


@dataclass
class CIDR:
    ip: bytes
    prefix: int

    def to_string(self) -> str:
        import ipaddress

        addr = ipaddress.ip_address(self.ip)
        return f"{addr}/{self.prefix}"


@dataclass
class GeoSite:
    code: str
    country_code: str = ""
    domains: List[Domain] = field(default_factory=list)


@dataclass
class GeoIP:
    code: str
    country_code: str = ""
    cidrs: List[CIDR] = field(default_factory=list)
    inverse_match: bool = False


@dataclass
class GeoSiteList:
    entries: List[GeoSite] = field(default_factory=list)


@dataclass
class GeoIPList:
    entries: List[GeoIP] = field(default_factory=list)
