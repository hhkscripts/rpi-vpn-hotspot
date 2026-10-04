#!/usr/bin/env python3
"""
Country profiles scanning and metadata mapping for WireGuard and OpenVPN.
"""

import os
import re
from typing import Optional

from .constants import FLAG_MAP


def get_country_profiles(
    profiles_dir: Optional[str] = None,
) -> dict[str, dict[str, str]]:
    """Scan profiles folder for WireGuard (.conf) and OpenVPN (.ovpn) files."""
    if not profiles_dir:
        candidates = [
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "..", "profiles"
            ),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "profiles"),
            "/host/etc/goodwifi/profiles",
            "/etc/goodwifi/profiles",
            "/app/profiles",
            os.path.join(os.getcwd(), "profiles"),
            "profiles",
        ]
        for c in candidates:
            if os.path.exists(c) and os.path.isdir(c):
                profiles_dir = c
                break

    if not profiles_dir or not os.path.exists(profiles_dir):
        return {}

    profiles = {}
    name_map = {
        "sg": "Singapore",
        "jp": "Japan",
        "us": "United States",
        "uk": "United Kingdom",
        "gb": "United Kingdom",
        "de": "Germany",
        "fr": "France",
        "ca": "Canada",
        "au": "Australia",
        "nl": "Netherlands",
        "hk": "Hong Kong",
        "in": "India",
        "kr": "South Korea",
        "th": "Thailand",
        "at": "Austria",
        "ba": "Bosnia",
        "br": "Brazil",
        "ch": "Switzerland",
        "se": "Sweden",
        "no": "Norway",
        "fi": "Finland",
        "es": "Spain",
        "it": "Italy",
        "pl": "Poland",
        "ie": "Ireland",
        "nz": "New Zealand",
        "mx": "Mexico",
        "za": "South Africa",
        "my": "Malaysia",
        "vn": "Vietnam",
        "id": "Indonesia",
        "ph": "Philippines",
        "tw": "Taiwan",
        "cl": "Chile",
        "cz": "Czech Republic",
        "dk": "Denmark",
        "gr": "Greece",
        "hr": "Croatia",
        "il": "Israel",
        "lt": "Lithuania",
        "lux": "Luxembourg",
        "lu": "Luxembourg",
        "ae": "United Arab Emirates",
        "ng": "Nigeria",
        "ua": "Ukraine",
    }
    region_map = {
        "asia": [
            "ae",
            "il",
            "in",
            "jp",
            "kr",
            "sg",
            "hk",
            "th",
            "my",
            "vn",
            "id",
            "ph",
            "tw",
        ],
        "europe": [
            "at",
            "ba",
            "ch",
            "cz",
            "de",
            "dk",
            "es",
            "fr",
            "gr",
            "hr",
            "it",
            "lt",
            "lux",
            "lu",
            "nl",
            "no",
            "pl",
            "se",
            "ua",
            "uk",
            "gb",
            "fi",
            "ie",
        ],
        "americas": ["br", "ca", "cl", "mx", "us"],
        "oceania-africa": ["au", "nz", "ng", "za"],
    }
    found_files = []
    for root, _, fnames in os.walk(profiles_dir):
        for fname in fnames:
            if fname.endswith(".ovpn"):
                found_files.append((root, fname))

    for root, fname in sorted(found_files, key=lambda x: x[1]):
        m = re.match(r"^([a-z]{2,3}(?:-[a-z]{2,3})?)(?:[-_].*)?\.ovpn$", fname.lower())
        if m:
            cc = m.group(1)
        else:
            m2 = re.search(r"[-_]([a-z]{2,3}(?:-[a-z]{2,3})?)[-_.]", fname.lower())
            cc = m2.group(1) if m2 else fname.split(".")[0].lower()

        base_cc = cc.split("-")[0]
        flag = FLAG_MAP.get(base_cc, "🌐")
        cname = name_map.get(base_cc, base_cc.upper())
        if "-" in cc:
            cname += " (" + cc.split("-")[1].upper() + ")"

        rel_dir = os.path.basename(root).lower()
        if rel_dir in region_map:
            region = rel_dir
        else:
            region = "other"
            for r_name, r_ccs in region_map.items():
                if base_cc in r_ccs:
                    region = r_name
                    break

        profiles[cc] = {
            "filename": fname,
            "country_code": cc,
            "country_name": cname,
            "flag": flag,
            "region": region,
            "path": os.path.join(root, fname),
        }
    return profiles
