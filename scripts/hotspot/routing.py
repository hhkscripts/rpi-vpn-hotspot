#!/usr/bin/env python3
"""
IP policy routing rules and route update scripts.
"""

from typing import Optional

from .constants import (
    APPLY_ROUTE_SCRIPT,
    CONFIG,
    GITHUB_ROUTE_SCRIPT,
    POLICY_SCRIPT,
)
from .context import Context
from .runner import log, run_args


def apply_vpn_policy(interface: Optional[str] = None) -> bool:
    ctx = Context.get()
    runner = getattr(ctx, "run_args", run_args)
    logger = getattr(ctx, "log", log)
    cfg = getattr(ctx, "CONFIG", CONFIG)
    script = getattr(ctx, "POLICY_SCRIPT", POLICY_SCRIPT)
    get_iface = getattr(ctx, "get_active_vpn_interface")

    if not interface or interface == "auto":
        interface, _ = get_iface()
    target_iface = str(interface or "tun0")
    ok, out, err = runner(["sudo", script, target_iface, "apply"])
    if not ok:
        detail = err or out or "unknown error"
        logger(f"VPN policy apply failed: {detail}", "ERROR")
        return False

    route_ok, route_out, _ = runner(["ip", "route", "show", "table", "100"])
    rule_ok, rule_out, _ = runner(["ip", "rule", "show"])
    subnet = cfg.get("hotspot_subnet", "10.42.0.0/24")
    policy_ok = (
        route_ok
        and (f"default dev {interface}" in route_out or "default dev" in route_out)
        and rule_ok
        and (
            f"from {subnet} lookup 100" in rule_out
            or f"from {subnet} lookup github_vpn" in rule_out
            or "from 10.42.0.0/24 lookup 100" in rule_out
            or "from 10.42.0.0/24 lookup github_vpn" in rule_out
        )
    )
    if not policy_ok:
        logger("VPN policy apply did not install GoodWifi table 100 routing", "ERROR")
        return False
    return True


def refresh_github_routes() -> None:
    ctx = Context.get()
    runner = getattr(ctx, "run_args", run_args)
    logger = getattr(ctx, "log", log)
    gh_script = getattr(ctx, "GITHUB_ROUTE_SCRIPT", GITHUB_ROUTE_SCRIPT)
    ap_script = getattr(ctx, "APPLY_ROUTE_SCRIPT", APPLY_ROUTE_SCRIPT)

    ok, _, _ = runner(["test", "-x", gh_script])
    if ok:
        ok, _, err = runner(["sudo", gh_script], timeout=120)
        if not ok:
            detail = f": {err}" if err else ""
            logger(f"GitHub route refresh failed{detail}", "WARN")
        return

    ok, _, _ = runner(["test", "-x", ap_script])
    if ok:
        ok, _, err = runner(["sudo", ap_script], timeout=60)
        if not ok:
            detail = f": {err}" if err else ""
            logger(f"Route apply failed{detail}", "WARN")
