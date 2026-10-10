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

# Optional: Replace with your actual ImgBB direct link or set to None
IMAGE_URL = "https://via.placeholder.com/600x300.png?text=Welcome+To+Our+Community"

# Professional & Attractive Message
CUSTOM_MESSAGE = (
    "🚀 **WELCOME TO THE COMMUNITY!**\n\n"
    "Your join request has been received. You are one step away from accessing exclusive insights, daily updates, and premium resources.\n\n"
    "✨ **Why Join Us?**\n"
    "🔹 **Daily Market Insights** – Stay ahead of the crowd\n"
    "🔹 **Exclusive Signals & Tips** – Proven, high-value content\n"
    "🔹 **24/7 Dedicated Support** – We are here to help you succeed\n\n"
    "👇 **TAP A BUTTON BELOW TO GET STARTED IMMEDIATELY**"
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler."""
    await update.message.reply_text("🤖 Bot is active and listening for channel join requests!")


async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Triggered automatically when someone clicks Request to Join."""
    chat_join_request = update.chat_join_request
    user = chat_join_request.from_user
    chat = chat_join_request.chat

    logger.info(f"Received join request from {user.id} ({user.first_name}) in {chat.title}")

    # Buttons that appear below the message (you can change the URLs later)
    keyboard = [
        [
            InlineKeyboardButton("🌐 Official Website", url="https://example.com"),
            InlineKeyboardButton("💬 Support Chat", url="https://t.me/example_support")
        ],
        [
            InlineKeyboardButton("🎁 Claim Exclusive Bonus", url="https://example.com/bonus")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Header with private channel title
    full_text = f"**{chat.title}**\n\n{CUSTOM_MESSAGE}"

    try:
        if IMAGE_URL:
            # Send photo with message caption & inline buttons
            await context.bot.send_photo(
                chat_id=chat_join_request.user_chat_id or user.id,
                photo=IMAGE_URL,
                caption=full_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            # Send text-only message
            await context.bot.send_message(
                chat_id=chat_join_request.user_chat_id or user.id,
                text=full_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        logger.info(f"Successfully sent direct promotional message to {user.id}")
    except Exception as e:
        logger.error(f"Failed to send direct message to {user.id}: {e}")


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable is missing on Railway!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(ChatJoinRequestHandler(handle_join_request))

    logger.info("Bot starting...")
    app.run_polling(allowed_updates=[Update.CHAT_JOIN_REQUEST, Update.MESSAGE])


if __name__ == "__main__":
    main()
