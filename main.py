import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from handlers.command_handlers import start_handler, help_handler
from handlers.channel_handlers import (
    start_add_channel, process_channel_name,
    process_api_key, process_api_secret,
    process_email, process_password,
    cancel_channel_setup
)
from handlers.video_handlers import video_handler
from config import Config
from telegram.error import TelegramError

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
CHANNEL_NAME, API_KEY, API_SECRET, EMAIL, PASSWORD = range(5)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)
    if update and hasattr(update, 'effective_message'):
        try:
            await update.effective_message.reply_text("❌ An error occurred. Please try again.")
        except:
            pass

def main() -> None:
    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Conversation handler for channel setup
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('addchannel', start_add_channel)],
        states={
            CHANNEL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_channel_name)],
            API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_api_key)],
            API_SECRET: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_api_secret)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_email)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_password)]
        },
        fallbacks=[CommandHandler('cancel', cancel_channel_setup)],
        allow_reentry=True
    )

    # Command handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(conv_handler)

    # Video handler with strict filtering
    application.add_handler(MessageHandler(
        (filters.VIDEO | (filters.Document.VIDEO)) & ~filters.COMMAND,
        video_handler
    ))

    # Run the bot with cleanup
    application.run_polling(
        poll_interval=1.0,
        drop_pending_updates=True,
        close_loop=False
    )

if __name__ == '__main__':
    main()
