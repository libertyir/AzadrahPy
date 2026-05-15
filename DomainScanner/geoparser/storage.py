"""
Storage façade: picks correct parser based on file type, handles inference.
"""
from __future__ import annotations

import os
from typing import Literal, Tuple

from .models import GeoIPList, GeoSiteList
from . import parser


FileType = Literal["geosite", "geoip"]


def infer_type(path: str, explicit: FileType | None = None) -> FileType:
    if explicit:
        return explicit
    name = os.path.basename(path).lower()
    return "geoip" if "geoip" in name else "geosite"


def load(path: str, explicit: FileType | None = None) -> Tuple[FileType, GeoSiteList | GeoIPList]:
    ftype = infer_type(path, explicit)
    if ftype == "geosite":
        return ftype, parser.load_geosite(path)
    return ftype, parser.load_geoip(path)


def save(path: str, data: GeoSiteList | GeoIPList, ftype: FileType) -> None:
    if ftype == "geosite":
        parser.save_geosite(data, path)
    else:
        parser.save_geoip(data, path)
