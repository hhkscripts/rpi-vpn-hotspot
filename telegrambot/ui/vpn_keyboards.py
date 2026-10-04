"""VPN backend switcher inline keyboard builder."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegrambot.constants.emojis import (
    EMOJI_AMNEZIAWG,
    EMOJI_GLOBE,
    EMOJI_OPENVPN,
    EMOJI_REFRESH,
    EMOJI_VLESS,
)


def make_switch_vpn_keyboard() -> InlineKeyboardMarkup:
    """Build the inline keyboard for choosing a VPN backend."""
    keyboard = [
        [
            InlineKeyboardButton(
                "VLESS S1 (198.71)",
                callback_data="switch_reality_1",
                icon_custom_emoji_id=EMOJI_VLESS,
            ),
            InlineKeyboardButton(
                "VLESS S2 (5.183)",
                callback_data="switch_reality_2",
                icon_custom_emoji_id=EMOJI_VLESS,
            ),
        ],
        [
            InlineKeyboardButton(
                "AmneziaWG (awg0)",
                callback_data="switch_awg0",
                icon_custom_emoji_id=EMOJI_AMNEZIAWG,
            ),
            InlineKeyboardButton(
                "OpenVPN (tun0)",
                callback_data="switch_tun0",
                icon_custom_emoji_id=EMOJI_OPENVPN,
            ),
        ],
        [
            InlineKeyboardButton(
                "🌐 Exit Country (VPN Unlimited)",
                callback_data="menu_country",
                icon_custom_emoji_id=EMOJI_GLOBE,
            ),
        ],
        [
            InlineKeyboardButton(
                "Auto (Auto Select)",
                callback_data="switch_auto",
                icon_custom_emoji_id=EMOJI_REFRESH,
            ),
        ],
        [
            InlineKeyboardButton("🔙 Back to Status", callback_data="refresh_status"),
            InlineKeyboardButton(
                "Refresh",
                callback_data="refresh_status",
                icon_custom_emoji_id=EMOJI_REFRESH,
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
