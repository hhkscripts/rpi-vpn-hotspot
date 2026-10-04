"""Execution wrapper for hotspot-manager.py and config state inspection."""

import asyncio
import os
import subprocess
from typing import List, Tuple

from telegrambot.constants.emojis import (
    TG_EMOJI_AMNEZIAWG,
    TG_EMOJI_OPENVPN,
    TG_EMOJI_VLESS,
    TG_EMOJI_WIREGUARD,
)
from telegrambot.constants.flags import FLAG_MAP


def run_hotspot_command(args: List[str]) -> Tuple[str, str, int]:
    """Run hotspot-manager.py in the host namespaces."""
    try:
        script_path = os.environ.get(
            "HOTSPOT_MANAGER_HOST_PATH", "/usr/local/bin/hotspot-manager.py"
        )
        cmd = [
            "nsenter",
            "--target",
            "1",
            "--mount",
            "--uts",
            "--ipc",
            "--net",
            "--pid",
            "--",
            "python3",
            script_path,
        ] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), -1


async def get_status_text() -> str:
    """Fetch current hotspot and VPN status output formatted as HTML."""
    loop = asyncio.get_running_loop()
    stdout, stderr, code = await loop.run_in_executor(
        None, run_hotspot_command, ["--status", "--html"]
    )
    if code != 0 and not stdout:
        return f"Error getting status:\n{stderr}"
    return stdout if stdout else "No output from hotspot manager."


def get_current_unlimited_country() -> str:
    """Read the configured UNLIMITED_COUNTRY from goodwifi.conf."""
    conf_path = "/host/etc/goodwifi/goodwifi.conf"
    if not os.path.exists(conf_path):
        conf_path = "/etc/goodwifi/goodwifi.conf"
    if os.path.exists(conf_path):
        try:
            with open(conf_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("UNLIMITED_COUNTRY="):
                        return (
                            line.split("=", 1)[1].strip().strip('"').strip("'").lower()
                        )
        except Exception:
            pass
    return "direct"


def get_current_backend_name() -> str:
    """Resolve and format the currently active VPN backend name."""
    conf_path = "/host/etc/goodwifi/goodwifi.conf"
    if not os.path.exists(conf_path):
        conf_path = "/etc/goodwifi/goodwifi.conf"
    backend = "auto"
    if os.path.exists(conf_path):
        try:
            with open(conf_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("VPN_BACKEND="):
                        backend = line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    unlimited_c = get_current_unlimited_country()
    vless_label = f"{TG_EMOJI_VLESS} VLESS Reality (sing0)"
    if unlimited_c and unlimited_c not in ["direct", "off", "none"]:
        flag = FLAG_MAP.get(unlimited_c, "🌐")
        vless_label += f" [{flag} {unlimited_c.upper()}]"

    names = {
        "sing0": vless_label,
        "awg0": f"{TG_EMOJI_AMNEZIAWG} AmneziaWG (awg0)",
        "tun0": f"{TG_EMOJI_OPENVPN} OpenVPN (tun0)",
        "wg0": f"{TG_EMOJI_WIREGUARD} WireGuard (wg0)",
        "auto": "Auto",
    }
    return names.get(backend, backend)


def get_current_ipv6_mode() -> str:
    """Read the configured IPV6_LEAK_PROTECTION mode."""
    conf_path = "/host/etc/goodwifi/goodwifi.conf"
    if not os.path.exists(conf_path):
        conf_path = "/etc/goodwifi/goodwifi.conf"

    if os.path.exists(conf_path):
        try:
            with open(conf_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("IPV6_LEAK_PROTECTION="):
                        val = (
                            line.split("=", 1)[1].strip().strip('"').strip("'").lower()
                        )
                        if val in ["drop", "reject", "off"]:
                            return val
        except Exception:
            pass
    return "drop"


def get_current_adguard_state() -> bool:
    """Check whether AdGuard Home DNS protection is enabled."""
    conf_path = "/host/etc/goodwifi/goodwifi.conf"
    if not os.path.exists(conf_path):
        conf_path = "/etc/goodwifi/goodwifi.conf"

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
    return True
