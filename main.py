import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ChatJoinRequestHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Fetch bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Store admin ID and custom message in memory
# (You can expand this with a database like SQLite or PostgreSQL if needed)
ADMIN_ID = None  # Will be set when the admin runs /start
CUSTOM_MESSAGE = "Welcome! Thank you for requesting to join our private channel. Check out our special offers here!"
CUSTOM_IMAGE_URL = ""  # Optional photo URL
CUSTOM_BUTTON_TEXT = "Visit Website"
CUSTOM_BUTTON_URL = "https://example.com"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler for the bot owner to configure messages."""
    global ADMIN_ID
    user_id = update.effective_user.id
    ADMIN_ID = user_id

    welcome_text = (
        "🤖 **Join Request Bot active!**\n\n"
        "Commands for Owner:\n"
        "• `/setmsg <your message>` - Set the auto-reply message text.\n"
        "• `/setlink <Button Text> | <URL>` - Add an inline button link.\n"
        "• `/viewmsg` - View the current auto-reply message."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def set_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows the bot owner to update the custom message text."""
    global CUSTOM_MESSAGE
    if not context.args:
        await update.message.reply_text("Usage: `/setmsg Your custom message here`", parse_mode="Markdown")
        return

    CUSTOM_MESSAGE = " ".join(context.args)
    await update.message.reply_text("✅ Auto-reply message updated successfully!")


async def set_link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows setting an inline button. Format: /setlink Text | https://url.com"""
    global CUSTOM_BUTTON_TEXT, CUSTOM_BUTTON_URL
    text = " ".join(context.args)
    if "|" not in text:
        await update.message.reply_text("Usage: `/setlink Button Text | https://yourlink.com`", parse_mode="Markdown")
        return

    parts = text.split("|")
    CUSTOM_BUTTON_TEXT = parts[0].strip()
    CUSTOM_BUTTON_URL = parts[1].strip()
    await update.message.reply_text("✅ Button link updated successfully!")


async def view_message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Preview the current active welcome message."""
    keyboard = [[InlineKeyboardButton(CUSTOM_BUTTON_TEXT, url=CUSTOM_BUTTON_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"**Current Auto-Reply Message:**\n\n{CUSTOM_MESSAGE}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Triggered automatically whenever a user requests to join the channel."""
    chat_join_request = update.chat_join_request
    user = chat_join_request.from_user
    chat = chat_join_request.chat

    logger.info(f"Received join request from User ID: {user.id} ({user.full_name}) for Chat: {chat.title}")

    # Build button keyboard if URL is provided
    reply_markup = None
    if CUSTOM_BUTTON_URL and CUSTOM_BUTTON_TEXT:
        keyboard = [[InlineKeyboardButton(CUSTOM_BUTTON_TEXT, url=CUSTOM_BUTTON_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

    # Message header identifying the channel
    full_message = f"**{chat.title}**\n\n{CUSTOM_MESSAGE}"

    try:
        # Send private message directly to the requester
        await context.bot.send_message(
            chat_id=user.id,
            text=full_message,
            reply_markup=reply_markup,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
        logger.info(f"Successfully sent join request message to {user.id}")
    except Exception as e:
        logger.error(f"Failed to send private message to {user.id}: {e}")


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable is not set!")

    # Build the Application
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("setmsg", set_message_command))
    app.add_handler(CommandHandler("setlink", set_link_command))
    app.add_handler(CommandHandler("viewmsg", view_message_command))
    
    # Core handler for join requests
    app.add_handler(ChatJoinRequestHandler(handle_join_request))

    # Run bot
    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
