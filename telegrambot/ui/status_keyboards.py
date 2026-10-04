"""Status menu inline keyboard builder."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegrambot.constants.emojis import (
    EMOJI_ADGUARD,
    EMOJI_AMNEZIAWG,
    EMOJI_GLOBE,
    EMOJI_IPV6,
    EMOJI_REFRESH,
    EMOJI_VLESS,
)
from telegrambot.core.runner import get_current_adguard_state


def make_status_keyboard(status_text: str) -> InlineKeyboardMarkup:
    """Build the inline keyboard displayed under the status output."""
    if "sing0" in status_text or "VLESS" in status_text:
        switch_btn = InlineKeyboardButton(
            "Switch to AmneziaWG (awg0)",
            callback_data="switch_awg0",
            icon_custom_emoji_id=EMOJI_AMNEZIAWG,
        )
    elif "awg0" in status_text or "AmneziaWG" in status_text:
        switch_btn = InlineKeyboardButton(
            "Switch to VLESS (sing0)",
            callback_data="switch_sing0",
            icon_custom_emoji_id=EMOJI_VLESS,
        )
    else:
        switch_btn = InlineKeyboardButton(
            "Switch to VLESS (sing0)",
            callback_data="switch_sing0",
            icon_custom_emoji_id=EMOJI_VLESS,
        )

    ipv6_btn = InlineKeyboardButton(
        "IPv6 Mode",
        callback_data="menu_ipv6",
        icon_custom_emoji_id=EMOJI_IPV6,
    )
    adguard_running = (
        "<code>adguard</code>: Running" in status_text
        or "adguard: Running" in status_text
        or "adguard      Running" in status_text
        or get_current_adguard_state()
    )
    adguard_btn = InlineKeyboardButton(
        f"AdGuard: {'ON' if adguard_running else 'OFF'}",
        callback_data="menu_adguard",
        icon_custom_emoji_id=EMOJI_ADGUARD,
    )
    refresh_btn = InlineKeyboardButton(
        "Refresh",
        callback_data="refresh_status",
        icon_custom_emoji_id=EMOJI_REFRESH,
    )
    country_btn = InlineKeyboardButton(
        "Exit Country",
        callback_data="menu_country",
        icon_custom_emoji_id=EMOJI_GLOBE,
    )
    return InlineKeyboardMarkup(
        [[switch_btn], [country_btn, ipv6_btn], [adguard_btn, refresh_btn]]
    )
