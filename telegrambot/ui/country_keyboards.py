"""Region and Country selection inline keyboard builders."""

from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegrambot.constants.emojis import EMOJI_GLOBE, EMOJI_REFRESH
from telegrambot.constants.flags import FLAG_MAP
from telegrambot.constants.profiles import get_bot_country_profiles


def make_region_keyboard() -> InlineKeyboardMarkup:
    """Build keyboard for browsing country profile regions."""
    profiles = get_bot_country_profiles()
    counts = {"asia": 0, "europe": 0, "americas": 0, "oceania-africa": 0}
    for p in profiles.values():
        reg = p.get("region", "other")
        if reg in counts:
            counts[reg] += 1

    keyboard = [
        [
            InlineKeyboardButton(
                f"🌏 Asia & Mideast ({counts['asia']})", callback_data="region_asia"
            ),
            InlineKeyboardButton(
                f"🏰 Europe ({counts['europe']})", callback_data="region_europe"
            ),
        ],
        [
            InlineKeyboardButton(
                f"🌎 Americas ({counts['americas']})",
                callback_data="region_americas",
            ),
            InlineKeyboardButton(
                f"🌍 Oceania & Africa ({counts['oceania-africa']})",
                callback_data="region_oceania-africa",
            ),
        ],
        [
            InlineKeyboardButton(
                f"📋 Show All ({len(profiles)} Countries)",
                callback_data="region_all",
            )
        ],
        [
            InlineKeyboardButton(
                "🌐 Direct VPS (No Detour)",
                callback_data="country_direct",
                icon_custom_emoji_id=EMOJI_GLOBE,
            )
        ],
        [
            InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_switch"),
            InlineKeyboardButton(
                "Refresh",
                callback_data="refresh_status",
                icon_custom_emoji_id=EMOJI_REFRESH,
            ),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def make_country_keyboard(
    selected_region: Optional[str] = None,
) -> InlineKeyboardMarkup:
    """Build grid keyboard of countries in a selected region."""
    profiles = get_bot_country_profiles()
    if selected_region and selected_region != "all":
        filtered = {
            cc: p for cc, p in profiles.items() if p.get("region") == selected_region
        }
    else:
        filtered = profiles

    keyboard = []
    row = []
    for cc, p in sorted(filtered.items()):
        flag = p.get("flag", FLAG_MAP.get(cc.split("-")[0], "🌐"))
        if "-" in cc:
            sub = cc.split("-")[1].upper()
            label = f"{flag} {sub}"
        else:
            label = flag
        btn = InlineKeyboardButton(label, callback_data=f"country_{cc}")
        row.append(btn)
        if len(row) == 4:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append(
        [
            InlineKeyboardButton(
                "🌐 Direct VPS (No Detour)",
                callback_data="country_direct",
                icon_custom_emoji_id=EMOJI_GLOBE,
            )
        ]
    )
    keyboard.append(
        [
            InlineKeyboardButton("⬅️ Back to Regions", callback_data="menu_country"),
            InlineKeyboardButton(
                "Refresh",
                callback_data="refresh_status",
                icon_custom_emoji_id=EMOJI_REFRESH,
            ),
        ]
    )
    return InlineKeyboardMarkup(keyboard)
