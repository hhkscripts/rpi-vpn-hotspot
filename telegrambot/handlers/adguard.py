"""AdGuard Home DNS protection command and callback handlers."""

import asyncio
import os
from telegram import Update
from telegram.ext import ContextTypes

from telegrambot.constants.emojis import TG_EMOJI_ADGUARD
from telegrambot.core.config import check_authorization
from telegrambot.core.runner import (
    get_current_adguard_state,
    get_status_text,
    run_hotspot_command,
)
from telegrambot.ui.adguard_keyboards import make_adguard_keyboard
from telegrambot.ui.main_keyboard import MAIN_KEYBOARD
from telegrambot.ui.status_keyboards import make_status_keyboard


async def adguard_menu_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Show the AdGuard Home management menu."""
    if update.effective_user is None or not check_authorization(
        update.effective_user.id
    ):
        return

    is_enabled = get_current_adguard_state()
    state_str = (
        "🟢 Active (Filtering & Blocking Ads)"
        if is_enabled
        else "🔴 Disabled (Fallback to dnsmasq)"
    )
    reply_markup = make_adguard_keyboard(is_enabled)
    dns_ip = os.getenv("HOTSPOT_IP", "10.42.0.1")

    text = (
        f"<b>{TG_EMOJI_ADGUARD} AdGuard Home DNS Protection</b>\n\n"
        f"Current Status: <b>{state_str}</b>\n\n"
        f"• <b>Turn ON</b>: AdGuard Home filters DNS and blocks ads.\n"
        f"• <b>Turn OFF</b>: AdGuard Home is stopped; dnsmasq resolves "
        f"upstream DNS directly on <code>{dns_ip}:53</code>.\n\n"
        f"Choose an action below:"
    )
    if update.message:
        await update.message.reply_text(
            text, reply_markup=reply_markup, parse_mode="HTML"
        )


async def adguard_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle AdGuard inline button toggles and restarts."""
    query = update.callback_query
    if query is None or query.data is None:
        return
    if update.effective_user is None or not check_authorization(
        update.effective_user.id
    ):
        try:
            await query.answer("Unauthorized", show_alert=True)
        except Exception:
            pass
        return

    data = query.data
    if data == "menu_adguard":
        is_enabled = get_current_adguard_state()
        state_str = (
            "🟢 Active (Filtering & Blocking Ads)"
            if is_enabled
            else "🔴 Disabled (Fallback to dnsmasq)"
        )
        reply_markup = make_adguard_keyboard(is_enabled)
        dns_ip = os.getenv("HOTSPOT_IP", "10.42.0.1")
        text = (
            f"<b>{TG_EMOJI_ADGUARD} AdGuard Home DNS Protection</b>\n\n"
            f"Current Status: <b>{state_str}</b>\n\n"
            f"• <b>Turn ON</b>: AdGuard Home filters DNS and blocks ads.\n"
            f"• <b>Turn OFF</b>: AdGuard Home is stopped; dnsmasq resolves "
            f"upstream DNS directly on <code>{dns_ip}:53</code>.\n\n"
            f"Choose an action below:"
        )
        try:
            await query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode="HTML"
            )
            await query.answer()
        except Exception:
            pass
        return

    action_map = {
        "adguard_on": ("on", "Enabling AdGuard Home..."),
        "adguard_off": ("off", "Disabling AdGuard Home (switching to dnsmasq)..."),
        "adguard_restart": ("restart", "Restarting AdGuard Home..."),
    }
    if data not in action_map:
        return

    arg, wait_msg = action_map[data]
    try:
        await query.answer(wait_msg)
    except Exception:
        pass

    try:
        await query.edit_message_text(f"⏳ <i>{wait_msg}</i>", parse_mode="HTML")
    except Exception:
        pass

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_hotspot_command, ["--adguard", arg])

    status_text = await get_status_text()
    reply_markup = make_status_keyboard(status_text)
    try:
        await query.edit_message_text(
            status_text, reply_markup=reply_markup, parse_mode="HTML"
        )
    except Exception:
        pass


async def adguard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /adguard command with arguments."""
    if update.effective_user is None or not check_authorization(
        update.effective_user.id
    ):
        return

    args = context.args if context.args else []
    if not args:
        await adguard_menu_command(update, context)
        return

    action = args[0].lower()
    if action not in ["on", "off", "enable", "disable", "restart", "status"]:
        if update.message:
            await update.message.reply_text(
                "Usage: <code>adguard &lt;on|off|restart|status&gt;</code>",
                parse_mode="HTML",
                reply_markup=MAIN_KEYBOARD,
            )
        return

    if action in ["on", "enable"]:
        arg = "on"
        wait_text = "Enabling AdGuard Home..."
    elif action in ["off", "disable"]:
        arg = "off"
        wait_text = "Disabling AdGuard Home (switching to fallback DNS)..."
    elif action == "restart":
        arg = "restart"
        wait_text = "Restarting AdGuard Home..."
    else:
        await adguard_menu_command(update, context)
        return

    if update.message:
        msg = await update.message.reply_text(
            f"⏳ <i>{wait_text}</i>", parse_mode="HTML"
        )
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, run_hotspot_command, ["--adguard", arg])
        status_text = await get_status_text()
        reply_markup = make_status_keyboard(status_text)
        await msg.edit_text(status_text, reply_markup=reply_markup, parse_mode="HTML")
