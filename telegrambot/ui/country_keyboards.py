"""Region and Country selection inline keyboard builders."""

from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegrambot.constants.emojis import EMOJI_GLOBE, EMOJI_REFRESH
from telegrambot.constants.flags import FLAG_MAP
from telegrambot.constants.profiles import get_bot_country_profiles
from telegrambot.core.dynamic_emojis import (
    get_country_emoji_id,
    get_region_emoji_id,
)


def make_region_keyboard() -> InlineKeyboardMarkup:
    """Build keyboard for browsing country profile regions."""
    profiles = get_bot_country_profiles()
    counts = {"asia": 0, "europe": 0, "americas": 0, "oceania-africa": 0}
    for p in profiles.values():
        reg = p.get("region", "other")
        if reg in counts:
            counts[reg] += 1

    asia_id = get_region_emoji_id("asia")
    europe_id = get_region_emoji_id("europe")
    americas_id = get_region_emoji_id("americas")
    oceania_id = get_region_emoji_id("oceania-africa")
    all_id = get_region_emoji_id("all")
    direct_id = get_region_emoji_id("direct") or EMOJI_GLOBE

    asia_label = (
        f"Asia & Mideast ({counts['asia']})"
        if asia_id
        else f"🌏 Asia & Mideast ({counts['asia']})"
    )
    europe_label = (
        f"Europe ({counts['europe']})"
        if europe_id
        else f"🏰 Europe ({counts['europe']})"
    )
    americas_label = (
        f"Americas ({counts['americas']})"
        if americas_id
        else f"🌎 Americas ({counts['americas']})"
    )
    oceania_label = (
        f"Oceania & Africa ({counts['oceania-africa']})"
        if oceania_id
        else f"🌍 Oceania & Africa ({counts['oceania-africa']})"
    )
    all_label = (
        f"Show All ({len(profiles)} Countries)"
        if all_id
        else f"📋 Show All ({len(profiles)} Countries)"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                asia_label,
                callback_data="region_asia",
                icon_custom_emoji_id=asia_id,
            ),
            InlineKeyboardButton(
                europe_label,
                callback_data="region_europe",
                icon_custom_emoji_id=europe_id,
            ),
        ],
        [
            InlineKeyboardButton(
                americas_label,
                callback_data="region_americas",
                icon_custom_emoji_id=americas_id,
            ),
            InlineKeyboardButton(
                oceania_label,
                callback_data="region_oceania-africa",
                icon_custom_emoji_id=oceania_id,
            ),
        ],
        [
            InlineKeyboardButton(
                all_label,
                callback_data="region_all",
                icon_custom_emoji_id=all_id,
            )
        ],
        [
            InlineKeyboardButton(
                "Direct VPS (No Detour)" if direct_id else "🌐 Direct VPS (No Detour)",
                callback_data="country_direct",
                icon_custom_emoji_id=direct_id,
            )
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


REGION_ORDER = ["asia", "europe", "americas", "oceania-africa", "all"]

REGION_INFO = {
    "asia": {"name": "Asia & Mideast", "symbol": "🌏"},
    "europe": {"name": "Europe", "symbol": "🏰"},
    "americas": {"name": "Americas", "symbol": "🌎"},
    "oceania-africa": {"name": "Oceania & Africa", "symbol": "🌍"},
    "all": {"name": "All Countries", "symbol": "📋"},
}


def make_country_keyboard(
    selected_region: Optional[str] = None,
) -> InlineKeyboardMarkup:
    """Build grid keyboard of countries in a selected region with pagination bar."""
    profiles = get_bot_country_profiles()
    curr_reg = selected_region if selected_region in REGION_ORDER else "all"

    if curr_reg != "all":
        filtered = {cc: p for cc, p in profiles.items() if p.get("region") == curr_reg}
    else:
        filtered = profiles

    counts = {"asia": 0, "europe": 0, "americas": 0, "oceania-africa": 0}
    for p in profiles.values():
        reg = p.get("region", "other")
        if reg in counts:
            counts[reg] += 1
    counts["all"] = len(profiles)

    idx = REGION_ORDER.index(curr_reg)
    prev_reg = REGION_ORDER[(idx - 1) % len(REGION_ORDER)]
    next_reg = REGION_ORDER[(idx + 1) % len(REGION_ORDER)]

    info = REGION_INFO.get(curr_reg, {"name": curr_reg.capitalize(), "symbol": "🌐"})
    count = counts.get(curr_reg, len(filtered))
    custom_icon = get_region_emoji_id(curr_reg)

    if custom_icon:
        title_btn = InlineKeyboardButton(
            f"{info['name']} ({count})",
            callback_data="noop",
            icon_custom_emoji_id=custom_icon,
        )
    else:
        title_btn = InlineKeyboardButton(
            f"{info['symbol']} {info['name']} ({count})",
            callback_data="noop",
        )

    keyboard = [
        [
            InlineKeyboardButton("◀️", callback_data=f"region_{prev_reg}"),
            title_btn,
            InlineKeyboardButton("▶️", callback_data=f"region_{next_reg}"),
        ]
    ]

    row = []
    for cc, p in sorted(filtered.items()):
        flag = p.get("flag", FLAG_MAP.get(cc.split("-")[0], "🌐"))
        custom_id = get_country_emoji_id(cc)
        if "-" in cc:
            sub = cc.split("-")[1].upper()
        else:
            sub = cc.upper()

        if custom_id:
            btn = InlineKeyboardButton(
                sub,
                callback_data=f"country_{cc}",
                icon_custom_emoji_id=custom_id,
            )
        else:
            btn = InlineKeyboardButton(
                f"{flag} {sub}",
                callback_data=f"country_{cc}",
            )
        row.append(btn)
        if len(row) == 4:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    direct_id = get_region_emoji_id("direct") or EMOJI_GLOBE
    keyboard.append(
        [
            InlineKeyboardButton(
                "Direct VPS (No Detour)" if direct_id else "🌐 Direct VPS (No Detour)",
                callback_data="country_direct",
                icon_custom_emoji_id=direct_id,
            )
        ]
    )
    keyboard.append(
        [
            InlineKeyboardButton("📋 All Regions", callback_data="menu_country"),
            InlineKeyboardButton(
                "Refresh",
                callback_data="refresh_status",
                icon_custom_emoji_id=EMOJI_REFRESH,
            ),
        ]
    )
    return InlineKeyboardMarkup(keyboard)
