"""AdGuard Home DNS protection inline keyboard builder."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegrambot.constants.emojis import EMOJI_ADGUARD, EMOJI_REFRESH, EMOJI_TOOLS


def make_adguard_keyboard(adguard_on: bool) -> InlineKeyboardMarkup:
    """Build inline keyboard for toggling or restarting AdGuard Home."""
    if adguard_on:
        toggle_btn = InlineKeyboardButton(
            "Turn OFF (Bypass / Disable)",
            callback_data="adguard_off",
            icon_custom_emoji_id=EMOJI_TOOLS,
        )
    else:
        toggle_btn = InlineKeyboardButton(
            "Turn ON (Filter & Block Ads)",
            callback_data="adguard_on",
            icon_custom_emoji_id=EMOJI_ADGUARD,
        )
    restart_btn = InlineKeyboardButton(
        "Restart AdGuard",
        callback_data="adguard_restart",
        icon_custom_emoji_id=EMOJI_REFRESH,
    )
    refresh_btn = InlineKeyboardButton(
        "Refresh Status",
        callback_data="refresh_status",
        icon_custom_emoji_id=EMOJI_REFRESH,
    )
    return InlineKeyboardMarkup([[toggle_btn], [restart_btn], [refresh_btn]])
