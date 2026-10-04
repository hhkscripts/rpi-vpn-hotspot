"""VPN backend switcher inline keyboard builder."""

from typing import Dict, List, Optional, Tuple

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegrambot.constants.emojis import (
    EMOJI_AMNEZIAWG,
    EMOJI_GLOBE,
    EMOJI_OPENVPN,
    EMOJI_REFRESH,
    EMOJI_VLESS,
    EMOJI_WIREGUARD,
)
from telegrambot.core.runner import (
    get_available_vpn_backends,
    get_vless_servers,
)


def make_switch_vpn_keyboard(
    available: Optional[Dict[str, bool]] = None,
    vless_servers: Optional[List[Tuple[str, str]]] = None,
) -> InlineKeyboardMarkup:
    """Build the inline keyboard dynamically for available VPN backends."""
    if available is None:
        available = get_available_vpn_backends()

    keyboard: List[List[InlineKeyboardButton]] = []

    # 1. Sing-box / VLESS Reality buttons (if available)
    if available.get("sing0", False):
        if vless_servers is None:
            vless_servers = get_vless_servers()

        if vless_servers:
            vless_row: List[InlineKeyboardButton] = []
            for s_num, label in vless_servers:
                vless_row.append(
                    InlineKeyboardButton(
                        label,
                        callback_data=f"switch_reality_{s_num}",
                        icon_custom_emoji_id=EMOJI_VLESS,
                    )
                )
                if len(vless_row) == 2:
                    keyboard.append(vless_row)
                    vless_row = []
            if vless_row:
                keyboard.append(vless_row)
        else:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "VLESS Reality (sing0)",
                        callback_data="switch_sing0",
                        icon_custom_emoji_id=EMOJI_VLESS,
                    )
                ]
            )

    # 2. Other VPN protocol buttons (AmneziaWG, OpenVPN, WireGuard)
    proto_buttons: List[InlineKeyboardButton] = []
    if available.get("awg0", False):
        proto_buttons.append(
            InlineKeyboardButton(
                "AmneziaWG (awg0)",
                callback_data="switch_awg0",
                icon_custom_emoji_id=EMOJI_AMNEZIAWG,
            )
        )
    if available.get("tun0", False):
        proto_buttons.append(
            InlineKeyboardButton(
                "OpenVPN (tun0)",
                callback_data="switch_tun0",
                icon_custom_emoji_id=EMOJI_OPENVPN,
            )
        )
    if available.get("wg0", False):
        proto_buttons.append(
            InlineKeyboardButton(
                "WireGuard (wg0)",
                callback_data="switch_wg0",
                icon_custom_emoji_id=EMOJI_WIREGUARD,
            )
        )

    for i in range(0, len(proto_buttons), 2):
        keyboard.append(proto_buttons[i : i + 2])

    # 3. Exit Country (only if Sing-box is available)
    if available.get("sing0", False):
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Exit Country",
                    callback_data="menu_country",
                    icon_custom_emoji_id=EMOJI_GLOBE,
                )
            ]
        )

    # 4. Auto (Auto Select)
    keyboard.append(
        [
            InlineKeyboardButton(
                "Auto (Auto Select)",
                callback_data="switch_auto",
                icon_custom_emoji_id=EMOJI_REFRESH,
            )
        ]
    )

    # 5. Navigation: Back to Status
    keyboard.append(
        [
            InlineKeyboardButton("🔙 Back to Status", callback_data="refresh_status"),
        ]
    )

    return InlineKeyboardMarkup(keyboard)
