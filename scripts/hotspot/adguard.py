#!/usr/bin/env python3
"""
AdGuard Home and DNS security management.
"""

import os
import tempfile
import time

from .constants import CONFIG, GOODWIFI_CONF
from .context import Context
from .runner import (
    check_docker_container,
    get_host_path,
    log,
    run_args,
    update_goodwifi_conf,
)


def get_adguard_enabled() -> bool:
    ctx = Context.get()
    get_path = getattr(ctx, "get_host_path", get_host_path)
    chk_container = getattr(ctx, "check_docker_container", check_docker_container)
    cfg = getattr(ctx, "CONFIG", CONFIG)

    conf_path = get_path(GOODWIFI_CONF)
    if os.path.exists(conf_path):
        try:
            with open(conf_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("ADGUARD_ENABLED="):
                        val = (
                            line.split("=", 1)[1].strip().strip('"').strip("'").lower()
                        )
                        if val in ["false", "0", "off", "no", "disable", "disabled"]:
                            return False
                        elif val in ["true", "1", "on", "yes", "enable", "enabled"]:
                            return True
        except Exception:
            pass
    st = chk_container(cfg.get("adguard_container", "adguardhome"))
    if st is False:
        return False
    return True


def configure_dnsmasq_fallback(enable_fallback: bool) -> bool:
    ctx = Context.get()
    get_path = getattr(ctx, "get_host_path", get_host_path)
    runner = getattr(ctx, "run_args", run_args)
    logger = getattr(ctx, "log", log)

    conf_path = get_path("/etc/dnsmasq.conf")
    if not os.path.exists(conf_path):
        return False
    try:
        with open(conf_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.splitlines()
        new_lines = []
        if enable_fallback:
            has_fallback_server = False
            for line in lines:
                stripped = line.strip()
                if stripped == "port=0":
                    new_lines.append("#port=0")
                    new_lines.append("server=8.8.8.8")
                    new_lines.append("server=9.9.9.9")
                    has_fallback_server = True
                elif (
                    stripped.startswith("server=8.8.8.8")
                    or stripped.startswith("server=9.9.9.9")
                    or stripped.startswith("server=1.1.1.1")
                ):
                    has_fallback_server = True
                    new_lines.append(line)
                else:
                    new_lines.append(line)
            if not has_fallback_server:
                new_lines.append("server=8.8.8.8")
                new_lines.append("server=9.9.9.9")
        else:
            has_port_zero = False
            for line in lines:
                stripped = line.strip()
                if (
                    stripped.startswith("server=1.1.1.1")
                    or stripped.startswith("server=8.8.8.8")
                    or stripped.startswith("server=9.9.9.9")
                ):
                    continue
                if stripped == "#port=0":
                    new_lines.append("port=0")
                    has_port_zero = True
                else:
                    if stripped == "port=0":
                        has_port_zero = True
                    new_lines.append(line)
            if not has_port_zero:
                new_lines.insert(0, "port=0")

        new_content = "\n".join(new_lines) + "\n"
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
            tf.write(new_content)
            temp_path = tf.name
        runner(["sudo", "cp", temp_path, conf_path])
        runner(["sudo", "chmod", "0644", conf_path])
        os.unlink(temp_path)
        return True
    except Exception as e:
        logger(f"Could not update dnsmasq config: {e}", "WARN")
        return False


def set_adguard_state(enable: bool) -> bool:
    ctx = Context.get()
    logger = getattr(ctx, "log", log)
    runner = getattr(ctx, "run_args", run_args)
    upd_conf = getattr(ctx, "update_goodwifi_conf", update_goodwifi_conf)
    cfg_dnsmasq = getattr(ctx, "configure_dnsmasq_fallback", configure_dnsmasq_fallback)
    chk_container = getattr(ctx, "check_docker_container", check_docker_container)
    cfg = getattr(ctx, "CONFIG", CONFIG)

    container_name = cfg.get("adguard_container", "adguardhome")
    if enable:
        logger("Enabling AdGuard Home DNS service...")
        upd_conf("ADGUARD_ENABLED", "true")
        cfg_dnsmasq(enable_fallback=False)
        runner(["sudo", "systemctl", "restart", "dnsmasq"], timeout=30)
        ok, _, _ = runner(["docker", "start", container_name], timeout=30)
        if not ok:
            project_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            adguard_dir = os.path.join(project_dir, "adguard")
            compose_file = os.path.join(adguard_dir, "docker-compose.yml")
            if os.path.exists(compose_file):
                runner(
                    [
                        "docker",
                        "compose",
                        "-f",
                        compose_file,
                        "up",
                        "-d",
                    ],
                    timeout=60,
                )
        time.sleep(2)
        running = chk_container(container_name)
        if running:
            logger("AdGuard Home is now running and handling DNS.")
            return True
        else:
            logger("Could not start AdGuard Home container.", "WARN")
            return False
    else:
        logger("Disabling AdGuard Home DNS service (switching to fallback DNS)...")
        upd_conf("ADGUARD_ENABLED", "false")
        runner(["docker", "stop", container_name], timeout=30)
        cfg_dnsmasq(enable_fallback=True)
        runner(["sudo", "systemctl", "restart", "dnsmasq"], timeout=30)
        time.sleep(1)
        chk_dns = getattr(ctx, "check_dns")
        dns_ok = chk_dns()
        if dns_ok:
            logger("AdGuard Home disabled. Fallback DNS is active and working.")
        else:
            logger("AdGuard Home disabled, but fallback DNS check failed.", "WARN")
        return True


def set_ipv6_mode(mode: str) -> bool:
    ctx = Context.get()
    logger = getattr(ctx, "log", log)
    upd_conf = getattr(ctx, "update_goodwifi_conf", update_goodwifi_conf)
    apply_pol = getattr(ctx, "apply_vpn_policy")

    mode = mode.lower()
    if mode not in ["drop", "reject", "off"]:
        logger(f"Invalid mode: {mode}. Choose from: drop, reject, off", "ERROR")
        return False
    upd_conf("IPV6_LEAK_PROTECTION", mode)
    logger(f"Set IPV6_LEAK_PROTECTION to {mode}")
    return apply_pol()


def ensure_adguard_resilience() -> tuple[bool, str]:
    """Check AdGuard status and automatically failover to dnsmasq if unhealthy.

    Returns (success, state_description).
    """
    ctx = Context.get()
    logger = getattr(ctx, "log", log)
    runner = getattr(ctx, "run_args", run_args)
    chk_container = getattr(ctx, "check_docker_container", check_docker_container)
    cfg_dnsmasq = getattr(ctx, "configure_dnsmasq_fallback", configure_dnsmasq_fallback)
    get_enabled = getattr(ctx, "get_adguard_enabled", get_adguard_enabled)
    cfg = getattr(ctx, "CONFIG", CONFIG)

    is_enabled = get_enabled()
    container_name = cfg.get("adguard_container", "adguardhome")

    if not is_enabled:
        cfg_dnsmasq(enable_fallback=True)
        return True, "fallback_active"

    running = chk_container(container_name)
    if running:
        cfg_dnsmasq(enable_fallback=False)
        return True, "adguard_healthy"

    logger(
        f"AdGuard Home ({container_name}) is stopped. Attempting recovery...",
        "WARN",
    )
    cfg_dnsmasq(enable_fallback=False)
    runner(["sudo", "systemctl", "restart", "dnsmasq"], timeout=15)
    runner(["docker", "start", container_name], timeout=20)
    time.sleep(1)
    if chk_container(container_name):
        logger(f"AdGuard Home ({container_name}) recovered and active.", "SUCCESS")
        return True, "adguard_recovered"

    logger(
        f"AdGuard Home ({container_name}) could not be started! "
        "Activating emergency DNS fallback via dnsmasq...",
        "WARN",
    )
    cfg_dnsmasq(enable_fallback=True)
    runner(["sudo", "systemctl", "restart", "dnsmasq"], timeout=30)
    return True, "fallback_activated"
