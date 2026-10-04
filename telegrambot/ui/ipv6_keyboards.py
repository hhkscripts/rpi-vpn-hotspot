"""IPv6 leak protection inline keyboard builder."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegrambot.constants.emojis import EMOJI_REFRESH


def make_ipv6_keyboard() -> InlineKeyboardMarkup:
    """Build inline keyboard for selecting IPv6 protection mode."""
    keyboard = [
        [
            InlineKeyboardButton("🔴 Drop (Default)", callback_data="ipv6_drop"),
            InlineKeyboardButton("🟡 Reject (Fast)", callback_data="ipv6_reject"),
        ],
        [
            InlineKeyboardButton("⚪ Off (Allow IPv6)", callback_data="ipv6_off"),
        ],
        [
            InlineKeyboardButton(
                "🔄 Refresh Status",
                callback_data="refresh_status",
                icon_custom_emoji_id=EMOJI_REFRESH,
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
