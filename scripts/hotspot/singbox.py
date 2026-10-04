#!/usr/bin/env python3
"""
Sing-box configuration generator and server/country detour switcher.
"""

import configparser
import json
import os
import re
import subprocess
import tempfile
import time
from typing import Optional

from .context import Context
from .profiles import get_country_profiles
from .runner import get_host_path, log, run_args, update_goodwifi_conf


def _parse_ovpn_endpoint(content: str) -> dict:
    def _tag(t: str) -> str:
        m = re.search(rf"<{t}>\s*(.*?)\s*</{t}>", content, re.DOTALL)
        return m.group(1).strip() if m else ""

    def _opt(pat: str, default: str = "") -> str:
        m = re.search(pat, content, re.MULTILINE)
        return m.group(1).strip() if m else default

    ca, cert, key = _tag("ca"), _tag("cert"), _tag("key")
    remote_m = re.search(r"^\s*remote\s+([^\s]+)(?:\s+(\d+))?", content, re.MULTILINE)
    server_host = remote_m.group(1).strip() if remote_m else "127.0.0.1"
    server_port = (
        int(remote_m.group(2).strip())
        if (remote_m and remote_m.group(2))
        else int(_opt(r"^\s*port\s+(\d+)", "1194"))
    )

    cipher = _opt(r"^\s*cipher\s+([^\s]+)")
    c_list = [c for c in [cipher, "AES-256-GCM", "AES-256-CBC"] if c]
    data_ciphers = list(dict.fromkeys(c_list))
    auth_val = _opt(r"^\s*auth\s+([^\s]+)", "SHA512").upper()

    tls_name = (
        os.getenv("OPENVPN_TLS_SERVER_NAME")
        or os.getenv("OPENVPN_SERVER_NAME")
        or _opt(r'^\s*(?:verify-x509-name|tls-remote)\s+["\']?([^"\'\s]+)["\']?')
    )
    if not tls_name and re.search(r"[a-zA-Z]", server_host):
        tls_name = (
            "server.ironnodes.com"
            if "vpnunlimitedapp.com" in server_host.lower()
            else server_host
        )

    server_ip = server_host
    try:
        res = subprocess.run(
            ["dig", "@127.0.0.1", "-p", "53", server_host, "+short"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        ips = [
            line.strip()
            for line in res.stdout.splitlines()
            if line.strip() and not line.startswith(";")
        ]
        if ips:
            server_ip = ips[0]
    except Exception:
        pass

    tls_dict: dict = {
        "certificate": [ca] if ca else [],
        "client_certificate": [cert] if cert else [],
        "client_key": [key] if key else [],
    }
    if tls_name:
        tls_dict["server_name"] = tls_name

    return {
        "type": "openvpn-client",
        "tag": "ovpn-out",
        "server": server_ip,
        "server_port": server_port,
        "data_ciphers": data_ciphers,
        "auth": auth_val,
        "tls": tls_dict,
        "detour": "xray-socks",
    }


def _parse_wg_endpoint(profile_path: str) -> dict:
    cp = configparser.ConfigParser()
    cp.read(profile_path)
    iface, peer = cp["Interface"], cp["Peer"]
    endpoint = peer.get("endpoint", "")
    server_ip, port_val = (
        endpoint.rsplit(":", 1) if ":" in endpoint else (endpoint, "51820")
    )
    ep = {
        "type": "wireguard",
        "tag": "wg-out",
        "system": False,
        "address": [
            a.strip() for a in iface.get("address", "").split(",") if a.strip()
        ],
        "private_key": iface.get("privatekey", ""),
        "peers": [
            {
                "address": server_ip.strip().strip("[]"),
                "port": int(str(port_val).strip()),
                "public_key": peer.get("publickey", ""),
                "allowed_ips": ["0.0.0.0/0"],
            }
        ],
        "detour": "xray-socks",
    }
    psk = peer.get("presharedkey")
    if psk:
        ep["peers"][0]["pre_shared_key"] = psk.strip()
    return ep


def generate_singbox_config(profile_path: Optional[str] = None) -> dict:
    """Generate Sing-box config with WireGuard or OpenVPN endpoint detour via Xray."""
    ctx = Context.get()
    logger = getattr(ctx, "log", log)
    tun_addr = os.getenv("SINGBOX_TUN_ADDR", "10.99.0.1/30")
    socks_port, socks_host = int(os.getenv("XRAY_SOCKS_PORT", "10808")), os.getenv(
        "XRAY_SOCKS_HOST", "127.0.0.1"
    )
    cfg = {
        "log": {"level": "warn"},
        "inbounds": [
            {
                "type": "tun",
                "tag": "tun-in",
                "interface_name": "sing0",
                "address": [tun_addr],
                "auto_route": False,
                "strict_route": False,
                "stack": "system",
            }
        ],
        "outbounds": [
            {
                "type": "socks",
                "tag": "xray-socks",
                "server": socks_host,
                "server_port": socks_port,
            }
        ],
        "route": {"rules": [{"action": "sniff"}]},
    }

    if profile_path and os.path.exists(profile_path):
        try:
            if profile_path.endswith(".ovpn"):
                with open(profile_path, "r", encoding="utf-8") as f:
                    ep = _parse_ovpn_endpoint(f.read())
                cfg["endpoints"] = [ep]
                cfg["route"]["rules"].append(
                    {"inbound": ["tun-in"], "outbound": "ovpn-out"}
                )
            elif profile_path.endswith(".conf"):
                ep = _parse_wg_endpoint(profile_path)
                cfg["endpoints"] = [ep]
                cfg["route"]["rules"].append(
                    {"inbound": ["tun-in"], "outbound": "wg-out"}
                )
        except Exception as e:
            logger(f"Error parsing profile {profile_path}: {e}", "ERROR")
            cfg["route"]["rules"].append(
                {"inbound": ["tun-in"], "outbound": "xray-socks"}
            )
    else:
        cfg["route"]["rules"].append({"inbound": ["tun-in"], "outbound": "xray-socks"})

    return cfg


def switch_unlimited_country(country: str) -> bool:
    """Switch Sing-box exit country using KeepSolid profile detour."""
    ctx = Context.get()
    logger = getattr(ctx, "log", log)
    runner, get_path = getattr(ctx, "run_args", run_args), getattr(
        ctx, "get_host_path", get_host_path
    )
    upd_conf = getattr(ctx, "update_goodwifi_conf", update_goodwifi_conf)
    get_profiles = getattr(ctx, "get_country_profiles", get_country_profiles)
    gen_config = getattr(ctx, "generate_singbox_config", generate_singbox_config)

    country = country.lower().strip()
    profiles = get_profiles()

    profile_path = None
    if country not in ["direct", "off", "none"]:
        if country not in profiles:
            logger(f"Country profile '{country}' not found.", "ERROR")
            return False
        profile_path = profiles[country]["path"]

    cfg = gen_config(profile_path)
    config_path = get_path("/etc/sing-box/config.json")

    with tempfile.NamedTemporaryFile("w", delete=False) as tf:
        json.dump(cfg, tf, indent=2)
        tmp_name = tf.name

    runner(["sudo", "mkdir", "-p", os.path.dirname(config_path)])
    runner(["sudo", "cp", tmp_name, config_path])
    runner(["sudo", "chmod", "0644", config_path])
    os.unlink(tmp_name)

    upd_conf("UNLIMITED_COUNTRY", country)

    backend = getattr(ctx, "get_configured_backend")()
    if backend != "sing0":
        getattr(ctx, "switch_vpn")("sing0")
    else:
        runner(["sudo", "systemctl", "restart", "sing-box"], timeout=20)
        getattr(ctx, "wait_for_interface")("sing0", timeout=10)
        getattr(ctx, "apply_vpn_policy")("sing0")
        getattr(ctx, "refresh_routes", getattr(ctx, "refresh_github_routes"))()
        ensure_adg = getattr(ctx, "ensure_adguard_resilience", None)
        if ensure_adg:
            ensure_adg()

    if country not in ["direct", "off", "none"]:
        time.sleep(4)
        check_ext = getattr(ctx, "check_vpn_external_ip")
        ok_ext, _ = check_ext()
        if not ok_ext:
            time.sleep(3)
            ok_ext, _ = check_ext()
        if not ok_ext:
            logger(
                f"Country profile '{country.upper()}' did not handshake. "
                "Reverting to Direct VLESS...",
                "WARN",
            )
            switch_unlimited_country("direct")
            return False

    logger(f"Switched Multi-Country exit to {country.upper()}", "SUCCESS")
    return True


def switch_reality_server(server_num: str) -> bool:
    """Switch primary Xray Reality outbound between server-1 and server-2."""
    ctx = Context.get()
    logger = getattr(ctx, "log", log)
    runner, get_path = getattr(ctx, "run_args", run_args), getattr(
        ctx, "get_host_path", get_host_path
    )

    config_path = get_path("/etc/xray/config.json")
    if not os.path.exists(config_path):
        logger(f"Xray config not found at {config_path}", "ERROR")
        return False

    target_tag = (
        f"server-{server_num}" if not server_num.startswith("server-") else server_num
    )
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        target = next(
            (o for o in cfg.get("outbounds", []) if o.get("tag") == target_tag), None
        )
        if not target:
            logger(f"Reality server '{target_tag}' not found in config", "ERROR")
            return False

        other_outbounds = [
            o for o in cfg.get("outbounds", []) if o.get("tag") != target_tag
        ]
        cfg["outbounds"] = [target] + other_outbounds

        with tempfile.NamedTemporaryFile("w", delete=False) as tf:
            json.dump(cfg, tf, indent=2)
            tmp_name = tf.name

        runner(["sudo", "cp", tmp_name, config_path])
        runner(["sudo", "chmod", "0644", config_path])
        os.unlink(tmp_name)

        runner(["sudo", "systemctl", "restart", "xray"], timeout=15)
        logger(f"Switched Reality primary to {target_tag}", "SUCCESS")
        return True
    except Exception as e:
        logger(f"Failed to switch Reality server: {e}", "ERROR")
        return False
