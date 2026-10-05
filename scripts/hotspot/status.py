#!/usr/bin/env python3
"""
Hotspot network diagnostics and status inspection.
"""

import os
import re
import time
from typing import Optional

from .constants import CONFIG, HotspotStatus, PingStatus
from .context import Context
from .runner import (
    check_docker_container,
    check_service,
    get_configured_ipv6_mode,
    log,
    run_args,
)


def check_internet() -> bool:
    ctx = Context.get()
    cfg = getattr(ctx, "CONFIG", CONFIG)
    runner = getattr(ctx, "run_args", run_args)
    get_iface = getattr(ctx, "get_active_vpn_interface")

    targets = [cfg.get("ping_target", "8.8.8.8"), "9.9.9.9", "8.8.4.4"]
    active_if, _ = get_iface()
    vpn_ok, _, _ = runner(["ip", "-4", "addr", "show", active_if])
    for target in targets:
        if vpn_ok:
            ok, _, _ = runner(["ping", "-c", "2", "-W", "3", "-I", active_if, target])
        else:
            ok, _, _ = runner(["ping", "-c", "2", "-W", "3", target])
        if ok:
            return True
    return False


def check_dns() -> bool:
    ctx = Context.get()
    cfg = getattr(ctx, "CONFIG", CONFIG)
    runner = getattr(ctx, "run_args", run_args)
    test_domains = [cfg.get("dns_test_domain", "google.com"), "cloudflare.com"]
    dns_ip = cfg.get("hotspot_ip", "10.42.0.1")
    for domain in dict.fromkeys(d for d in test_domains if d):
        ok, _, _ = runner(["nslookup", domain, dns_ip])
        if ok:
            return True
    return False


def check_ping(target: Optional[str] = None) -> PingStatus:
    ctx = Context.get()
    cfg = getattr(ctx, "CONFIG", CONFIG)
    runner = getattr(ctx, "run_args", run_args)
    get_iface = getattr(ctx, "get_active_vpn_interface")

    ping_target = str(target or cfg.get("ping_target", "8.8.8.8") or "8.8.8.8")
    active_if, _ = get_iface()
    vpn_ok, _, _ = runner(["ip", "-4", "addr", "show", active_if])
    out = ""
    ok = False
    if vpn_ok:
        ok, out, _ = runner(
            ["ping", "-c", "3", "-W", "2", "-I", active_if, ping_target]
        )
        if not ok:
            ok, out, _ = runner(["ping", "-c", "3", "-W", "2", ping_target])
    else:
        ok, out, _ = runner(["ping", "-c", "3", "-W", "2", ping_target])

    packet_line = "No ping result"
    rtt_line = ""
    for line in out.splitlines():
        if "packets transmitted" in line:
            packet_line = line.strip()
        elif line.startswith("rtt "):
            rtt_line = line.strip()

    loss_match = re.search(r"(\d+(?:\.\d+)?)% packet loss", packet_line)
    loss = loss_match.group(1) if loss_match else "?"
    avg_match = re.search(r"= ([0-9.]+)/([0-9.]+)/([0-9.]+)/([0-9.]+) ms", rtt_line)
    avg = avg_match.group(2) if avg_match else "?"
    return {
        "ok": ok,
        "target": ping_target,
        "summary": packet_line,
        "rtt": rtt_line,
        "loss": loss,
        "avg_ms": avg,
    }


def check_clients() -> int:
    ctx = Context.get()
    cfg = getattr(ctx, "CONFIG", CONFIG)
    runner = getattr(ctx, "run_args", run_args)
    wlan = cfg.get("interface_wlan", "wlan0")
    candidates = [wlan, "wlan1", "ap0"]
    for dev in dict.fromkeys(c for c in candidates if c):
        for cmd in [
            ["sudo", "iw", "dev", dev, "station", "dump"],
            ["/usr/sbin/iw", "dev", dev, "station", "dump"],
            ["iw", "dev", dev, "station", "dump"],
        ]:
            ok, out, _ = runner(cmd)
            if ok:
                return sum(
                    1 for line in out.splitlines() if line.startswith("Station ")
                )
    return 0


def check_hotspot() -> bool:
    ctx = Context.get()
    cfg = getattr(ctx, "CONFIG", CONFIG)
    runner = getattr(ctx, "run_args", run_args)
    wlan = cfg.get("interface_wlan", "wlan0")
    candidates = [wlan, "wlan1", "ap0"]
    for dev in dict.fromkeys(c for c in candidates if c):
        for cmd in [
            ["sudo", "iw", "dev", dev, "info"],
            ["/usr/sbin/iw", "dev", dev, "info"],
            ["iw", "dev", dev, "info"],
        ]:
            ok, out, _ = runner(cmd)
            if ok and any(line.strip() == "type AP" for line in out.splitlines()):
                return True
    ok, out, _ = runner(["systemctl", "is-active", "hostapd"])
    return ok and out.strip() == "active"


def get_hotspot_ssid() -> str:
    ctx = Context.get()
    cfg = getattr(ctx, "CONFIG", CONFIG)
    try:
        with open(cfg.get("hostapd_conf", "/etc/hostapd/hostapd.conf")) as conf:
            for line in conf:
                if line.startswith("ssid="):
                    return line.split("=", 1)[1].strip()
    except OSError:
        pass
    return cfg.get("default_hotspot_ssid", "GoodWifi")


def fix_hotspot() -> bool:
    ctx = Context.get()
    logger = getattr(ctx, "log", log)
    runner = getattr(ctx, "run_args", run_args)
    rst_vpn = getattr(ctx, "restart_vpn")
    apply_pol = getattr(ctx, "apply_vpn_policy")

    # Only restart hostapd if it is inactive/dead to avoid dropping Wi-Fi for clients
    ok, out, _ = runner(["systemctl", "is-active", "hostapd"])
    if not ok or out.strip() != "active":
        logger("Hostapd AP inactive; restarting hostapd...")
        runner(["sudo", "systemctl", "restart", "hostapd"])
    else:
        logger("Hostapd AP is active and healthy.")

    logger("Restarting dnsmasq and ensuring DNS resilience...")
    runner(["sudo", "systemctl", "restart", "dnsmasq"])
    time.sleep(1)
    ensure_dns = getattr(ctx, "ensure_adguard_resilience", None)
    if ensure_dns:
        ensure_dns()
    vpn_ok = rst_vpn()
    policy_ok = apply_pol() if vpn_ok else False
    return vpn_ok and policy_ok


def get_status() -> HotspotStatus:
    ctx = Context.get()
    cfg = getattr(ctx, "CONFIG", CONFIG)
    chk_cli = getattr(ctx, "check_clients", check_clients)
    chk_vpn = getattr(ctx, "check_vpn")
    get_iface = getattr(ctx, "get_active_vpn_interface")
    chk_vpn_ip = getattr(ctx, "check_vpn_ip")
    chk_ext_ip = getattr(ctx, "check_vpn_external_ip")
    chk_svc = getattr(ctx, "check_service", check_service)
    chk_container = getattr(ctx, "check_docker_container", check_docker_container)
    chk_hotspot = getattr(ctx, "check_hotspot", check_hotspot)
    chk_dns = getattr(ctx, "check_dns", check_dns)
    chk_net = getattr(ctx, "check_internet", check_internet)
    chk_ping = getattr(ctx, "check_ping", check_ping)
    get_ipv6 = getattr(ctx, "get_configured_ipv6_mode", get_configured_ipv6_mode)

    clients = chk_cli()
    vpn_connected = chk_vpn()
    active_if, backend_name = get_iface()
    _vpn_ip_ok, vpn_ip = chk_vpn_ip() if vpn_connected else (False, None)
    external_ok, external_ip = chk_ext_ip() if vpn_connected else (False, None)

    services_status = {s: chk_svc(s) for s in cfg.get("services", [])}

    adguard_candidates = [
        cfg.get("adguard_container", "adguardhome"),
        "adguardhome",
        "adguard",
    ]
    for name in dict.fromkeys(adguard_candidates):
        st = chk_container(name)
        if st is not None:
            services_status["adguard"] = st
            break

    bot_candidates = [
        os.getenv("TELEGRAM_CONTAINER"),
        cfg.get("telegram_container"),
        "mpxraspberrypibot",
        "telegrambot",
        "vpn-telegrambot-1",
        "vpn_telegrambot_1",
    ]
    for name in dict.fromkeys(c for c in bot_candidates if c):
        st = chk_container(name)
        if st is not None:
            services_status["telegrambot"] = st
            break

    return {
        "services": services_status,
        "vpn": {
            "connected": vpn_connected,
            "interface": active_if,
            "backend": backend_name,
            "ip": vpn_ip,
            "external_ip": external_ip,
            "external_ok": external_ok,
        },
        "hotspot": {"broadcasting": chk_hotspot(), "clients": clients},
        "dns_working": chk_dns(),
        "internet": chk_net(),
        "ping": chk_ping(),
        "ipv6_protection": get_ipv6(),
    }
