#!/usr/bin/env python3
"""
Hotspot Manager Constants, Types, and Configurations.
"""

from typing import Optional, TypedDict


class Config(TypedDict, total=False):
    services: list[str]
    vpn_name: str
    default_hotspot_ssid: str
    hostapd_conf: str
    hotspot_ip: str
    interface_wlan: str
    log_file: str
    ping_target: str
    hotspot_subnet: str
    adguard_container: str
    telegram_container: str
    adguard_enabled: bool


class PingStatus(TypedDict):
    ok: bool
    target: str
    summary: str
    rtt: str
    loss: str
    avg_ms: str


class VpnStatus(TypedDict):
    connected: bool
    interface: str
    backend: str
    ip: Optional[str]
    external_ip: Optional[str]
    external_ok: bool


class HotspotInfo(TypedDict):
    broadcasting: bool
    clients: int


class HotspotStatus(TypedDict):
    services: dict[str, bool]
    vpn: VpnStatus
    hotspot: HotspotInfo
    dns_working: bool
    internet: bool
    ping: PingStatus
    ipv6_protection: str


CONFIG: Config = {
    "services": ["hostapd", "dnsmasq"],
    "vpn_name": "",
    "default_hotspot_ssid": "GoodWifi",
    "hostapd_conf": "/etc/hostapd/hostapd.conf",
    "hotspot_ip": "10.42.0.1",
    "interface_wlan": "wlan0",
    "log_file": "/var/log/hotspot-manager.log",
    "ping_target": "8.8.8.8",
    "hotspot_subnet": "10.42.0.0/24",
    "adguard_container": "adguardhome",
    "telegram_container": "mpxraspberrypibot",
    "adguard_enabled": True,
}

GITHUB_ROUTE_SCRIPT = "/usr/local/bin/github-vpn-routes.sh"
APPLY_ROUTE_SCRIPT = "/usr/local/bin/apply-routes.sh"
POLICY_SCRIPT = "/etc/NetworkManager/dispatcher.d/90-hotspot-vpn-policy"
GOODWIFI_CONF = "/etc/goodwifi/goodwifi.conf"

CUSTOM_EMOJIS = {
    "signal": '<tg-emoji emoji-id="6127157759872868272">📡</tg-emoji>',
    "tools": '<tg-emoji emoji-id="6141134446742478627">🔧</tg-emoji>',
    "check": '<tg-emoji emoji-id="6114156013399579882">✅</tg-emoji>',
    "lock": '<tg-emoji emoji-id="6059947491695008618">🔒</tg-emoji>',
    "stats": '<tg-emoji emoji-id="6143449494244563627">📶</tg-emoji>',
    "globe": '<tg-emoji emoji-id="6057443049020071219">🌐</tg-emoji>',
    "cross": '<tg-emoji emoji-id="6111658378247806635">❌</tg-emoji>',
    "ping": '<tg-emoji emoji-id="6060045064762039982">⏲</tg-emoji>',
    "wireguard": '<tg-emoji emoji-id="6165512058344318397">🐉</tg-emoji>',
    "openvpn": '<tg-emoji emoji-id="6165724869678866601">🔐</tg-emoji>',
    "amneziawg": '<tg-emoji emoji-id="6165519909544534378">🛡</tg-emoji>',
    "vless": '<tg-emoji emoji-id="6197318808022032017">🛡</tg-emoji>',
    "singbox": '<tg-emoji emoji-id="6197318808022032017">🛡</tg-emoji>',
    "raspberrypi": '<tg-emoji emoji-id="6165792622787961093">🍓</tg-emoji>',
    "adguard": '<tg-emoji emoji-id="6165657271188594962">🛡</tg-emoji>',
    "ipv6": '<tg-emoji emoji-id="6165466570345686935">🔒</tg-emoji>',
}

EMOJI_SIGNAL = CUSTOM_EMOJIS["signal"]
EMOJI_TOOLS = CUSTOM_EMOJIS["tools"]
EMOJI_CHECK = CUSTOM_EMOJIS["check"]
EMOJI_LOCK = CUSTOM_EMOJIS["lock"]
EMOJI_STATS = CUSTOM_EMOJIS["stats"]
EMOJI_GLOBE = CUSTOM_EMOJIS["globe"]
EMOJI_CROSS = CUSTOM_EMOJIS["cross"]
EMOJI_PING = CUSTOM_EMOJIS["ping"]
EMOJI_WIREGUARD = CUSTOM_EMOJIS["wireguard"]
EMOJI_OPENVPN = CUSTOM_EMOJIS["openvpn"]
EMOJI_AMNEZIAWG = CUSTOM_EMOJIS["amneziawg"]
EMOJI_VLESS = CUSTOM_EMOJIS["vless"]
EMOJI_SINGBOX = CUSTOM_EMOJIS["singbox"]
EMOJI_RPI = CUSTOM_EMOJIS["raspberrypi"]
EMOJI_ADGUARD = CUSTOM_EMOJIS["adguard"]
EMOJI_IPV6 = CUSTOM_EMOJIS["ipv6"]

FLAG_MAP = {
    "sg": "🇸🇬",
    "jp": "🇯🇵",
    "us": "🇺🇸",
    "uk": "🇬🇧",
    "gb": "🇬🇧",
    "de": "🇩🇪",
    "fr": "🇫🇷",
    "ca": "🇨🇦",
    "au": "🇦🇺",
    "nl": "🇳🇱",
    "hk": "🇭🇰",
    "in": "🇮🇳",
    "kr": "🇰🇷",
    "th": "🇹🇭",
    "at": "🇦🇹",
    "ba": "🇧🇦",
    "br": "🇧🇷",
    "ch": "🇨🇭",
    "se": "🇸🇪",
    "no": "🇳🇴",
    "fi": "🇫🇮",
    "es": "🇪🇸",
    "it": "🇮🇹",
    "pl": "🇵🇱",
    "ie": "🇮🇪",
    "nz": "🇳🇿",
    "mx": "🇲🇽",
    "za": "🇿🇦",
    "my": "🇲🇾",
    "vn": "🇻🇳",
    "id": "🇮🇩",
    "ph": "🇵🇭",
    "tw": "🇹🇼",
    "cl": "🇨🇱",
    "cz": "🇨🇿",
    "dk": "🇩🇰",
    "gr": "🇬🇷",
    "hr": "🇭🇷",
    "il": "🇮🇱",
    "lt": "🇱🇹",
    "lux": "🇱🇺",
    "lu": "🇱🇺",
    "ae": "🇦🇪",
    "ng": "🇳🇬",
    "ua": "🇺🇦",
}


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
