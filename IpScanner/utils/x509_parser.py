#!/usr/bin/env python3
"""x509_parser.py — X.509 certificate parser (DER/PEM).

Parses ASN.1 DER-encoded X.509 certificates: extracts subject, issuer,
validity, serial number, public key info, extensions, and signature.
Also extracts Subject Alternative Names (DNS entries).

One file. Zero deps. Does one thing well.
"""

import base64
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


# ─── ASN.1 DER Parser ───

class DERParser:
    OID_NAMES = {
        '2.5.4.3': 'CN', '2.5.4.4': 'SN', '2.5.4.5': 'SERIALNUMBER',
        '2.5.4.6': 'C', '2.5.4.7': 'L', '2.5.4.8': 'ST',
        '2.5.4.9': 'STREET', '2.5.4.10': 'O', '2.5.4.11': 'OU',
        '2.5.4.12': 'T', '2.5.4.13': 'DESCRIPTION',
        '2.5.4.17': 'POSTALCODE', '2.5.4.41': 'NAME',
        '2.5.4.42': 'GIVENNAME', '2.5.4.43': 'INITIALS',
        '1.2.840.113549.1.1.1': 'RSA', 
        '1.2.840.113549.1.1.5': 'SHA1withRSA',
        '1.2.840.113549.1.1.11': 'SHA256withRSA',
        '1.2.840.113549.1.1.12': 'SHA384withRSA',
        '1.2.840.113549.1.1.13': 'SHA512withRSA',
        '1.2.840.10040.4.1': 'DSA',
        '1.2.840.10045.2.1': 'EC',
        '1.2.840.10045.4.3.2': 'SHA256withECDSA',
        '1.3.14.3.2.26': 'SHA1',
        '2.16.840.1.101.3.4.2.1': 'SHA256',
        '2.5.29.14': 'subjectKeyIdentifier',
        '2.5.29.15': 'keyUsage',
        '2.5.29.17': 'subjectAltName',
        '2.5.29.19': 'basicConstraints',
        '2.5.29.30': 'nameConstraints',
        '2.5.29.31': 'crlDistributionPoints',
        '2.5.29.32': 'certificatePolicies',
        '2.5.29.35': 'authorityKeyIdentifier',
        '2.5.29.37': 'extKeyUsage',
        '1.3.6.1.5.5.7.1.1': 'authorityInfoAccess',
        '1.3.6.1.5.5.7.3.1': 'serverAuth',
        '1.3.6.1.5.5.7.3.2': 'clientAuth',
    }

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def read_tag(self) -> tuple[int, int, bool]:
        """Read tag: (class, number, constructed)."""
        b = self.data[self.pos]
        self.pos += 1
        cls = (b >> 6) & 3
        constructed = bool(b & 0x20)
        num = b & 0x1F
        if num == 0x1F:
            num = 0
            while True:
                b = self.data[self.pos]
                self.pos += 1
                num = (num << 7) | (b & 0x7F)
                if not (b & 0x80):
                    break
        return cls, num, constructed

    def read_length(self) -> int:
        b = self.data[self.pos]
        self.pos += 1
        if b < 0x80:
            return b
        n_bytes = b & 0x7F
        length = 0
        for _ in range(n_bytes):
            length = (length << 8) | self.data[self.pos]
            self.pos += 1
        return length

    def read_tlv(self) -> tuple[int, int, bool, bytes]:
        """Read Tag-Length-Value: (class, number, constructed, value)."""
        start = self.pos
        cls, num, constructed = self.read_tag()
        length = self.read_length()
        value = self.data[self.pos:self.pos + length]
        self.pos += length
        return cls, num, constructed, value

    def read_oid(self, data: bytes) -> str:
        """Convert OID bytes to dot notation string."""
        components = []
        first = data[0]
        components.append(str(first // 40))
        components.append(str(first % 40))
        val = 0
        for b in data[1:]:
            val = (val << 7) | (b & 0x7F)
            if not (b & 0x80):
                components.append(str(val))
                val = 0
        return '.'.join(components)

    def parse_name(self, data: bytes) -> dict[str, str]:
        """Parse X.501 Name (RDNSequence) from DER."""
        p = DERParser(data)
        result = {}
        while p.pos < len(data):
            try:
                _, _, _, set_data = p.read_tlv()  # SET
                sp = DERParser(set_data)
                _, _, _, seq_data = sp.read_tlv()  # SEQUENCE
                sp2 = DERParser(seq_data)
                _, _, _, oid_data = sp2.read_tlv()  # OID
                _, _, _, val_data = sp2.read_tlv()  # value
                oid = self.read_oid(oid_data)
                name = self.OID_NAMES.get(oid, oid)
                # Value could be PrintableString, UTF8String, etc.
                try:
                    result[name] = val_data.decode('utf-8')
                except UnicodeDecodeError:
                    result[name] = val_data.decode('ascii', errors='replace')
            except Exception:
                break
        return result

    def parse_time(self, tag: int, data: bytes) -> str:
        """Parse UTCTime or GeneralizedTime."""
        s = data.decode('ascii')
        if tag == 23:  # UTCTime
            if len(s) == 13:  # YYMMDDHHMMSSZ
                yr = int(s[:2])
                yr = yr + 2000 if yr < 70 else yr + 1900
                return f"{yr}-{s[2:4]}-{s[4:6]} {s[6:8]}:{s[8:10]}:{s[10:12]}"
        elif tag == 24:  # GeneralizedTime
            if len(s) >= 14:
                return f"{s[:4]}-{s[4:6]}-{s[6:8]} {s[8:10]}:{s[10:12]}:{s[12:14]}"
        return s

    def parse_san_dns(self, data: bytes) -> List[str]:
        """Parse Subject Alternative Names and extract DNS entries."""
        dns_names = []
        p = DERParser(data)
        
        while p.pos < len(data):
            try:
                cls, num, con, val = p.read_tlv()
                # generalName: context-specific, tag 2 is DNS name
                if cls == 2 and num == 2:  # DNS name
                    try:
                        dns = val.decode('utf-8')
                        if dns and '*' not in dns:
                            dns_names.append(dns)
                    except:
                        pass
                elif cls == 2 and num == 0:  # otherName (skip)
                    pass
                elif cls == 2 and num == 1:  # rfc822Name (skip)
                    pass
                elif cls == 2 and num == 6:  # uniformResourceIdentifier (skip)
                    pass
                elif cls == 2 and num == 7:  # iPAddress (skip)
                    pass
            except Exception:
                break
        
        return dns_names


@dataclass
class Certificate:
    """Parsed X.509 certificate."""
    version: int
    serial: str
    issuer: dict[str, str]
    subject: dict[str, str]
    not_before: str
    not_after: str
    sig_algorithm: str
    pub_key_algorithm: str
    pub_key_bits: int
    extensions: list[tuple[str, bool, List[str]]]  # (name, critical, value)
    signature_hex: str
    san_domains: List[str] = field(default_factory=list)

    def __repr__(self):
        lines = [
            f"Version: v{self.version + 1}",
            f"Subject: {self._dn(self.subject)}",
            f"Issuer:  {self._dn(self.issuer)}",
            f"Serial:  {self.serial}",
            f"Valid:   {self.not_before} → {self.not_after}",
            f"SigAlg:  {self.sig_algorithm}",
            f"PubKey:  {self.pub_key_algorithm} ({self.pub_key_bits} bits)",
        ]
        if self.san_domains:
            lines.append(f"SAN DNS: {', '.join(self.san_domains[:5])}")
        if self.extensions:
            lines.append(f"Extensions: {len(self.extensions)}")
        return '\n'.join(lines)

    def _dn(self, d: dict) -> str:
        return ', '.join(f'{k}={v}' for k, v in d.items())

    def get_all_domains(self) -> List[str]:
        """Extract all domain names from certificate (CN + SAN)."""
        domains = []
        
        # Get CN from subject
        if 'CN' in self.subject:
            cn = self.subject['CN']
            if '.' in cn and len(cn) > 3 and '*' not in cn:
                domains.append(cn)
        
        # Add SAN DNS entries
        for dns in self.san_domains:
            if dns not in domains and '.' in dns and len(dns) > 3 and '*' not in dns:
                domains.append(dns)
        
        return domains


def parse_pem(pem: str) -> bytes:
    """Convert PEM certificate to DER bytes."""
    lines = [l for l in pem.strip().splitlines() if not l.startswith('-----')]
    return base64.b64decode(''.join(lines))


def parse_der_file(path: str) -> bytes:
    """Read DER certificate file."""
    with open(path, 'rb') as f:
        return f.read()


def parse_cert(data: bytes) -> Certificate:
    """Parse a DER-encoded X.509 certificate."""
    p = DERParser(data)
    _, _, _, cert_data = p.read_tlv()  # outer SEQUENCE

    cp = DERParser(cert_data)
    _, _, _, tbs_data = cp.read_tlv()  # tbsCertificate SEQUENCE
    _, _, _, sig_alg_data = cp.read_tlv()  # signatureAlgorithm
    _, _, _, sig_data = cp.read_tlv()  # signature BIT STRING

    # Parse TBS
    tp = DERParser(tbs_data)

    # Version (explicit tag [0])
    version = 0
    cls, num, con, ver_data = tp.read_tlv()
    if cls == 2 and num == 0:  # context-specific, explicit
        vp = DERParser(ver_data)
        _, _, _, ver_val = vp.read_tlv()
        version = int.from_bytes(ver_val, byteorder='big')
        # Serial number
        _, _, _, serial_data = tp.read_tlv()
    else:
        # No version field, this data IS serial
        serial_data = ver_data

    serial = serial_data.hex().upper().lstrip('0') or '0'

    # Signature algorithm (inside TBS)
    _, _, _, inner_sig_data = tp.read_tlv()
    sp = DERParser(inner_sig_data)
    _, _, _, oid_data = sp.read_tlv()
    sig_alg = DERParser.OID_NAMES.get(DERParser(b'').read_oid(oid_data), 'unknown')

    # Issuer
    _, _, _, issuer_data = tp.read_tlv()
    issuer = tp.parse_name(issuer_data) if issuer_data else {}

    # Validity
    _, _, _, validity_data = tp.read_tlv()
    vp = DERParser(validity_data)
    _, tag1, _, nb_data = vp.read_tlv()
    _, tag2, _, na_data = vp.read_tlv()
    not_before = tp.parse_time(tag1, nb_data)
    not_after = tp.parse_time(tag2, na_data)

    # Subject
    _, _, _, subject_data = tp.read_tlv()
    subject = tp.parse_name(subject_data) if subject_data else {}

    # SubjectPublicKeyInfo
    _, _, _, spki_data = tp.read_tlv()
    kp = DERParser(spki_data)
    _, _, _, key_alg_data = kp.read_tlv()  # algorithm
    _, _, _, key_bits_data = kp.read_tlv()  # subjectPublicKey BIT STRING
    
    # Parse key algorithm
    kap = DERParser(key_alg_data)
    _, _, _, kalg_oid_data = kap.read_tlv()
    pub_key_alg = DERParser.OID_NAMES.get(DERParser(b'').read_oid(kalg_oid_data), 'unknown')
    
    # Estimate key bits
    pub_key_bits = (len(key_bits_data) - 1) * 8  # subtract unused bits byte

    # Extensions (optional)
    extensions = []
    san_domains = []
    
    while tp.pos < len(tbs_data):
        cls, num, con, ext_container = tp.read_tlv()
        if cls == 2 and num == 3:  # extensions [3]
            ep = DERParser(ext_container)
            _, _, _, exts_seq = ep.read_tlv()
            exp = DERParser(exts_seq)
            while exp.pos < len(exts_seq):
                cls2, num2, con2, ext_data = exp.read_tlv()
                if cls2 != 0 or num2 != 16:  # SEQUENCE
                    continue
                    
                exp2 = DERParser(ext_data)
                _, _, _, oid_d = exp2.read_tlv()
                oid_str = DERParser(b'').read_oid(oid_d)
                ext_name = DERParser.OID_NAMES.get(oid_str, oid_str)
                
                # Check for critical flag
                critical = False
                ext_value = None
                if exp2.pos < len(ext_data):
                    cls3, num3, con3, val = exp2.read_tlv()
                    if cls3 == 0 and num3 == 1:  # BOOLEAN
                        critical = val[0] != 0
                        # Next is OCTET STRING with extension value
                        if exp2.pos < len(ext_data):
                            _, _, _, ext_value = exp2.read_tlv()
                    else:
                        ext_value = val
                
                # Parse SAN extension
                if ext_name == 'subjectAltName' and ext_value:
                    san_domains = tp.parse_san_dns(ext_value)
                
                extensions.append((ext_name, critical, san_domains if ext_name == 'subjectAltName' else []))

    # Signature (first 16 bytes only for readability)
    sig_hex = sig_data[1:17].hex() + '...' if len(sig_data) > 17 else sig_data[1:].hex()

    return Certificate(
        version=version,
        serial=serial,
        issuer=issuer,
        subject=subject,
        not_before=not_before,
        not_after=not_after,
        sig_algorithm=sig_alg,
        pub_key_algorithm=pub_key_alg,
        pub_key_bits=pub_key_bits,
        extensions=extensions,
        signature_hex=sig_hex,
        san_domains=san_domains
    )


def load_and_parse(pem_path: str) -> Certificate:
    """Load PEM file and parse certificate."""
    with open(pem_path, 'r') as f:
        pem = f.read()
    der = parse_pem(pem)
    return parse_cert(der)


def demo():
    print("=== X.509 Certificate Parser ===\n")
    print("Usage: python3 x509_parser.py cert.pem")
    print("       python3 x509_parser.py --test\n")
    
    print("Features:")
    print("  - Parses Subject and Issuer DN (CN, O, C, etc.)")
    print("  - Extracts Subject Alternative Names (DNS entries)")
    print("  - Shows validity period, serial number, signature algorithm")
    print("  - Detects extensions and critical flags")
    print("  - Pure Python, zero external dependencies")


if __name__ == '__main__':
    if '--test' in sys.argv:
        # Quick tests
        p = DERParser(b'')
        assert p.read_oid(bytes([0x55, 0x04, 0x03])) == '2.5.4.3'
        data = bytes([0x02, 0x01, 0x05])
        p2 = DERParser(data)
        cls, num, con, val = p2.read_tlv()
        assert cls == 0 and num == 2
        assert val == bytes([5])
        pem_test = "-----BEGIN CERTIFICATE-----\nAQID\n-----END CERTIFICATE-----"
        assert parse_pem(pem_test) == bytes([1, 2, 3])
        print("All tests passed ✓")
    elif len(sys.argv) > 1 and sys.argv[1] != '--test':
        try:
            cert = load_and_parse(sys.argv[1])
            print(cert)
            print(f"\nAll domains: {cert.get_all_domains()}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        demo()