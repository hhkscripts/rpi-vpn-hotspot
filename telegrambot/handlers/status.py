"""Status command and refresh callback query handlers."""

from telegram import Update
from telegram.ext import ContextTypes

from telegrambot.core.config import check_authorization, logger
from telegrambot.core.runner import get_status_text
from telegrambot.ui.main_keyboard import MAIN_KEYBOARD
from telegrambot.ui.status_keyboards import make_status_keyboard


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command and show hotspot status with inline keyboard."""
    if update.effective_user is None or not check_authorization(
        update.effective_user.id
    ):
        return

    status_text = await get_status_text()
    reply_markup = make_status_keyboard(status_text)

    if update.message is not None:
        if context.user_data is not None and not context.user_data.get(
            "keyboard_v2_adguard"
        ):
            context.user_data["keyboard_v2_adguard"] = True
            await update.message.reply_text(
                "GoodWifi Hotspot Manager", reply_markup=MAIN_KEYBOARD
            )
        await update.message.reply_text(
            text=status_text, reply_markup=reply_markup, parse_mode="HTML"
        )


async def refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button click for refreshing status."""
    query = update.callback_query
    if query is None:
        return
    if update.effective_user is None or not check_authorization(
        update.effective_user.id
    ):
        try:
            await query.answer("Unauthorized", show_alert=True)
        except Exception:
            pass
        return

    try:
        await query.answer("Refreshing...")
    except Exception:
        pass

    status_text = await get_status_text()
    reply_markup = make_status_keyboard(status_text)

    try:
        await query.edit_message_text(
            text=status_text, reply_markup=reply_markup, parse_mode="HTML"
        )
    except Exception as e:
        if "not modified" not in str(e).lower():
            logger.warning(f"Could not edit message: {e}")
