"""IPv6 leak protection command and callback handlers."""

import asyncio
from telegram import Update
from telegram.ext import ContextTypes

from telegrambot.constants.emojis import TG_EMOJI_IPV6
from telegrambot.core.config import check_authorization, logger
from telegrambot.core.runner import (
    get_current_ipv6_mode,
    get_status_text,
    run_hotspot_command,
)
from telegrambot.ui.ipv6_keyboards import make_ipv6_keyboard
from telegrambot.ui.status_keyboards import make_status_keyboard


async def ipv6_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the IPv6 leak protection configuration menu."""
    if update.effective_user is None or not check_authorization(
        update.effective_user.id
    ):
        return

    current = get_current_ipv6_mode().upper()
    reply_markup = make_ipv6_keyboard()
    text = (
        f"<b>{TG_EMOJI_IPV6} IPv6 Leak Protection:</b>\n\n"
        f"Current Mode: <code>{current}</code>\n\n"
        f"• <b>Drop</b>: Silently drop client IPv6 packets (Recommended)\n"
        f"• <b>Reject</b>: Reject with ICMPv6 unreachable (Fail fast)\n"
        f"• <b>Off</b>: Disable IPv6 blocking (Allow IPv6)\n\n"
        f"Choose an option below to set:"
    )
    if update.message:
        await update.message.reply_text(
            text, reply_markup=reply_markup, parse_mode="HTML"
        )


async def ipv6_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle IPv6 protection mode button clicks."""
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

    if query.data == "menu_ipv6":
        current = get_current_ipv6_mode().upper()
        text = (
            f"<b>{TG_EMOJI_IPV6} IPv6 Leak Protection:</b>\n\n"
            f"Current Mode: <code>{current}</code>\n\n"
            f"• <b>Drop</b>: Silently drop client IPv6 packets (Recommended)\n"
            f"• <b>Reject</b>: Reject with ICMPv6 unreachable (Fail fast)\n"
            f"• <b>Off</b>: Disable IPv6 blocking (Allow IPv6)\n\n"
            f"Choose an option below to set:"
        )
        try:
            await query.edit_message_text(
                text, reply_markup=make_ipv6_keyboard(), parse_mode="HTML"
            )
        except Exception:
            pass
        return

    mode = query.data.replace("ipv6_", "")
    try:
        await query.answer(f"Setting IPv6 protection to {mode.upper()}...")
    except Exception:
        pass

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_hotspot_command, ["--set-ipv6", mode])
    await asyncio.sleep(1)
    status_text = await get_status_text()
    reply_markup = make_status_keyboard(status_text)

    try:
        msg_text = (
            f"<b>{TG_EMOJI_IPV6} IPv6 Protection updated to {mode.upper()}!</b>"
            f"\n\n{status_text}"
        )
        await query.edit_message_text(
            text=msg_text,
            reply_markup=reply_markup,
            parse_mode="HTML",
        )
    except Exception as e:
        if "not modified" not in str(e).lower():
            logger.warning(f"Could not edit message after ipv6 switch: {e}")


async def ipv6_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ipv6 command with mode argument."""
    if update.effective_user is None or not check_authorization(
        update.effective_user.id
    ):
        return

    target = context.args[0].lower() if context.args else None
    if not target or target not in ["drop", "reject", "off"]:
        await ipv6_menu_command(update, context)
        return

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_hotspot_command, ["--set-ipv6", target])
    await asyncio.sleep(1)
    status_text = await get_status_text()
    reply_markup = make_status_keyboard(status_text)
    if update.message:
        msg_text = (
            f"<b>{TG_EMOJI_IPV6} IPv6 Protection set to {target.upper()}!</b>"
            f"\n\n{status_text}"
        )
        await update.message.reply_text(
            msg_text,
            reply_markup=reply_markup,
            parse_mode="HTML",
        )
