import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from handlers.command_handlers import (
    start_handler,
    help_handler,
    limit_status_handler,
    channel_status_handler,
    full_guide_handler
)
from handlers.message_handlers import video_handler, text_handler
from handlers.channel_handlers import (
    add_channel_handler,
    my_channels_handler,
    remove_channel_handler
)
from handlers.premium_handlers import premium_help_handler, pricing_handler
from handlers.admin_handlers import (
    add_premium_handler,
    remove_premium_handler,
    reset_limit_handler,
    broadcast_handler
)
from config import Config
from telegram.error import TelegramError

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the telegram bot."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    if update and hasattr(update, 'effective_message'):
        try:
            await update.effective_message.reply_text(
                "❌ An error occurred. The developer has been notified.\n"
                "Please try again later."
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()

    # Add error handler first
    application.add_error_handler(error_handler)

    # Command handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("limitstatus", limit_status_handler))
    application.add_handler(CommandHandler("channelstatus", channel_status_handler))
    application.add_handler(CommandHandler("fullguide", full_guide_handler))
    application.add_handler(CommandHandler("pricing", pricing_handler))
    application.add_handler(CommandHandler("ping", lambda update, context: update.message.reply_text("🏓 Pong!")))

    # Admin commands
    application.add_handler(CommandHandler("addpremium", add_premium_handler))
    application.add_handler(CommandHandler("removepremium", remove_premium_handler))
    application.add_handler(CommandHandler("resetlimit", reset_limit_handler))
    application.add_handler(CommandHandler("broadcast", broadcast_handler))

    # Message handlers with proper filtering
    application.add_handler(MessageHandler(
        filters.VIDEO | (filters.Document.VIDEO & ~filters.COMMAND),
        video_handler
    ))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        text_handler
    ))

    # Button handlers
    application.add_handler(CallbackQueryHandler(add_channel_handler, pattern="^add_channel$"))
    application.add_handler(CallbackQueryHandler(my_channels_handler, pattern="^my_channels$"))
    application.add_handler(CallbackQueryHandler(remove_channel_handler, pattern="^remove_channel$"))
    application.add_handler(CallbackQueryHandler(premium_help_handler, pattern="^premium_help$"))

    # Run the bot until Ctrl-C is pressed
    application.run_polling()

if __name__ == '__main__':
    main()
