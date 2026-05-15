"""
Lightweight protobuf reader/writer specialized for v2ray geosite.dat / geoip.dat.
Keeps dependencies to the stdlib for offline usage.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from .models import (
    Attribute,
    CIDR,
    DOMAIN_TYPE_TO_NUM,
    Domain,
    GeoIP,
    GeoIPList,
    GeoSite,
    GeoSiteList,
    NUM_TO_DOMAIN_TYPE,
)


###############################################################################
# Varint helpers
###############################################################################
def _read_varint(buf: bytes, idx: int) -> Tuple[int, int]:
    shift = 0
    result = 0
    while True:
        if idx >= len(buf):
            raise ValueError("Unexpected EOF while reading varint")
        b = buf[idx]
        idx += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return result, idx


def _write_varint(value: int) -> bytes:
    out = bytearray()
    v = value
    while True:
        to_write = v & 0x7F
        v >>= 7
        if v:
            out.append(to_write | 0x80)
        else:
            out.append(to_write)
            break
    return bytes(out)


def _skip_value(buf: bytes, idx: int, wire_type: int) -> int:
    if wire_type == 0:
        _, idx = _read_varint(buf, idx)
        return idx
    if wire_type == 1:
        return idx + 8
    if wire_type == 2:
        length, idx = _read_varint(buf, idx)
        return idx + length
    if wire_type == 5:
        return idx + 4
    raise ValueError(f"Unsupported wire type: {wire_type}")


def _read_length_delimited(buf: bytes, idx: int) -> Tuple[bytes, int]:
    length, idx = _read_varint(buf, idx)
    end = idx + length
    return buf[idx:end], end


###############################################################################
# Parsers
###############################################################################
def _parse_attribute(buf: bytes, start: int, end: int) -> Attribute:
    idx = start
    key = ""
    bool_value = None
    int_value = None
    while idx < end:
        tag, idx = _read_varint(buf, idx)
        field_no, wire = tag >> 3, tag & 0x7
        if field_no == 1 and wire == 2:
            raw, idx = _read_length_delimited(buf, idx)
            key = raw.decode()
        elif field_no == 2 and wire == 0:
            val, idx = _read_varint(buf, idx)
            bool_value = bool(val)
        elif field_no == 3 and wire == 0:
            val, idx = _read_varint(buf, idx)
            int_value = val
        else:
            idx = _skip_value(buf, idx, wire)
    return Attribute(key=key, bool_value=bool_value, int_value=int_value)


def _parse_domain(buf: bytes, start: int, end: int) -> Domain:
    idx = start
    dtype_num = 0
    value = ""
    attrs: List[Attribute] = []
    while idx < end:
        tag, idx = _read_varint(buf, idx)
        field_no, wire = tag >> 3, tag & 0x7
        if field_no == 1 and wire == 0:
            dtype_num, idx = _read_varint(buf, idx)
        elif field_no == 2 and wire == 2:
            raw, idx = _read_length_delimited(buf, idx)
            value = raw.decode()
        elif field_no == 3 and wire == 2:
            raw, idx = _read_length_delimited(buf, idx)
            attrs.append(_parse_attribute(raw, 0, len(raw)))
        else:
            idx = _skip_value(buf, idx, wire)
    return Domain(value=value, dtype=NUM_TO_DOMAIN_TYPE.get(dtype_num, "plain"), attributes=attrs)


def _parse_cidr(buf: bytes, start: int, end: int) -> CIDR:
    idx = start
    ip = b""
    prefix = 0
    while idx < end:
        tag, idx = _read_varint(buf, idx)
        field_no, wire = tag >> 3, tag & 0x7
        if field_no == 1 and wire == 2:
            ip, idx = _read_length_delimited(buf, idx)
        elif field_no == 2 and wire == 0:
            prefix, idx = _read_varint(buf, idx)
        else:
            idx = _skip_value(buf, idx, wire)
    return CIDR(ip=ip, prefix=prefix)


def _parse_geosite(buf: bytes, start: int, end: int) -> GeoSite:
    idx = start
    code = ""
    country_code = ""
    domains: List[Domain] = []
    while idx < end:
        tag, idx = _read_varint(buf, idx)
        field_no, wire = tag >> 3, tag & 0x7
        if field_no == 1 and wire == 2:
            raw, idx = _read_length_delimited(buf, idx)
            country_code = raw.decode()
        elif field_no == 2 and wire == 2:
            raw, idx = _read_length_delimited(buf, idx)
            domains.append(_parse_domain(raw, 0, len(raw)))
        elif field_no == 4 and wire == 2:
            raw, idx = _read_length_delimited(buf, idx)
            code = raw.decode()
        else:
            idx = _skip_value(buf, idx, wire)
    return GeoSite(code=code or country_code, country_code=country_code, domains=domains)


def _parse_geoip(buf: bytes, start: int, end: int) -> GeoIP:
    idx = start
    code = ""
    country_code = ""
    cidrs: List[CIDR] = []
    inverse_match = False
    while idx < end:
        tag, idx = _read_varint(buf, idx)
        field_no, wire = tag >> 3, tag & 0x7
        if field_no == 1 and wire == 2:
            raw, idx = _read_length_delimited(buf, idx)
            country_code = raw.decode()
        elif field_no == 2 and wire == 2:
            raw, idx = _read_length_delimited(buf, idx)
            cidrs.append(_parse_cidr(raw, 0, len(raw)))
        elif field_no == 3 and wire == 0:
            val, idx = _read_varint(buf, idx)
            inverse_match = bool(val)
        elif field_no == 5 and wire == 2:
            raw, idx = _read_length_delimited(buf, idx)
            code = raw.decode()
        else:
            idx = _skip_value(buf, idx, wire)
    return GeoIP(code=code or country_code, country_code=country_code, cidrs=cidrs, inverse_match=inverse_match)


###############################################################################
# Serialization
###############################################################################
def _encode_field(tag: int, payload: bytes) -> bytes:
    return _write_varint(tag) + payload


def _ld(payload: bytes) -> bytes:
    return _write_varint(len(payload)) + payload


def _serialize_attribute(attr: Attribute) -> bytes:
    out = bytearray()
    out += _encode_field((1 << 3) | 2, _ld(attr.key.encode()))
    if attr.bool_value is not None:
        out += _encode_field((2 << 3) | 0, _write_varint(1 if attr.bool_value else 0))
    if attr.int_value is not None:
        out += _encode_field((3 << 3) | 0, _write_varint(attr.int_value))
    return bytes(out)


def _serialize_domain(dom: Domain) -> bytes:
    out = bytearray()
    out += _encode_field((1 << 3) | 0, _write_varint(DOMAIN_TYPE_TO_NUM.get(dom.dtype, 0)))
    out += _encode_field((2 << 3) | 2, _ld(dom.value.encode()))
    for attr in dom.attributes:
        payload = _serialize_attribute(attr)
        out += _encode_field((3 << 3) | 2, _ld(payload))
    return bytes(out)


def _serialize_cidr(cidr: CIDR) -> bytes:
    out = bytearray()
    out += _encode_field((1 << 3) | 2, _ld(cidr.ip))
    out += _encode_field((2 << 3) | 0, _write_varint(cidr.prefix))
    return bytes(out)


def _serialize_geosite(site: GeoSite) -> bytes:
    out = bytearray()
    if site.country_code:
        out += _encode_field((1 << 3) | 2, _ld(site.country_code.encode()))
    for dom in site.domains:
        payload = _serialize_domain(dom)
        out += _encode_field((2 << 3) | 2, _ld(payload))
    if site.code:
        out += _encode_field((4 << 3) | 2, _ld(site.code.encode()))
    return bytes(out)


def _serialize_geoip(entry: GeoIP) -> bytes:
    out = bytearray()
    if entry.country_code:
        out += _encode_field((1 << 3) | 2, _ld(entry.country_code.encode()))
    for cidr in entry.cidrs:
        payload = _serialize_cidr(cidr)
        out += _encode_field((2 << 3) | 2, _ld(payload))
    out += _encode_field((3 << 3) | 0, _write_varint(1 if entry.inverse_match else 0))
    if entry.code:
        out += _encode_field((5 << 3) | 2, _ld(entry.code.encode()))
    return bytes(out)


###############################################################################
# Public API
###############################################################################
def load_geosite(path: str) -> GeoSiteList:
    data = _safe_read(path)
    idx = 0
    entries: List[GeoSite] = []
    while idx < len(data):
        tag, idx = _read_varint(data, idx)
        field_no, wire = tag >> 3, tag & 0x7
        if field_no != 1 or wire != 2:
            idx = _skip_value(data, idx, wire)
            continue
        raw, idx = _read_length_delimited(data, idx)
        entries.append(_parse_geosite(raw, 0, len(raw)))
    return GeoSiteList(entries=entries)


def load_geoip(path: str) -> GeoIPList:
    data = _safe_read(path)
    idx = 0
    entries: List[GeoIP] = []
    while idx < len(data):
        tag, idx = _read_varint(data, idx)
        field_no, wire = tag >> 3, tag & 0x7
        if field_no != 1 or wire != 2:
            idx = _skip_value(data, idx, wire)
            continue
        raw, idx = _read_length_delimited(data, idx)
        entries.append(_parse_geoip(raw, 0, len(raw)))
    return GeoIPList(entries=entries)


def save_geosite(gs: GeoSiteList, path: str) -> None:
    out = bytearray()
    for entry in gs.entries:
        payload = _serialize_geosite(entry)
        out += _encode_field((1 << 3) | 2, _ld(payload))
    _write_all(path, bytes(out))


def save_geoip(gi: GeoIPList, path: str) -> None:
    out = bytearray()
    for entry in gi.entries:
        payload = _serialize_geoip(entry)
        out += _encode_field((1 << 3) | 2, _ld(payload))
    _write_all(path, bytes(out))


def _safe_read(path: str) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return b""


def _write_all(path: str, data: bytes) -> None:
    with open(path, "wb") as f:
        f.write(data)
