import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ChatJoinRequestHandler,
    CommandHandler,
    ContextTypes,
)

# Enable detailed logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Environment variable from Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Custom configuration variables
CUSTOM_MESSAGE = "Welcome! Thank you for requesting to join our private channel!"
CUSTOM_BUTTON_TEXT = "Visit Website"
CUSTOM_BUTTON_URL = "https://example.com"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler."""
    await update.message.reply_text("🤖 Bot is active and listening for channel join requests!")


async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Triggered automatically when someone clicks Request to Join."""
    chat_join_request = update.chat_join_request
    user = chat_join_request.from_user
    chat = chat_join_request.chat

    logger.info(f"Received join request from {user.id} ({user.first_name}) in {chat.title}")

    # Build inline URL button
    keyboard = [[InlineKeyboardButton(CUSTOM_BUTTON_TEXT, url=CUSTOM_BUTTON_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        # Send direct promotional message to user
        await context.bot.send_message(
            chat_id=chat_join_request.user_chat_id or user.id,
            text=f"**{chat.title}**\n\n{CUSTOM_MESSAGE}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        logger.info(f"Successfully sent direct message to {user.id}")
    except Exception as e:
        logger.error(f"Failed to send direct message to {user.id}: {e}")


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable is missing on Railway!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(ChatJoinRequestHandler(handle_join_request))

    # Listen specifically for CHAT_JOIN_REQUEST updates
    logger.info("Bot starting...")
    app.run_polling(allowed_updates=[Update.CHAT_JOIN_REQUEST, Update.MESSAGE])


if __name__ == "__main__":
    main()
