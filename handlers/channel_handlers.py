from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from utils.dailymotion_api import verify_dailymotion_credentials
from utils.mongodb import db
import logging

logger = logging.getLogger(__name__)

async def start_add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📺 Let's connect your Dailymotion channel\n\n"
        "First, enter your channel name:",
        reply_markup=ReplyKeyboardRemove()
    )
    return CHANNEL_NAME

async def process_channel_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['channel_name'] = update.message.text
    await update.message.reply_text(
        "🔑 Enter your Dailymotion API Key:",
        reply_markup=ReplyKeyboardRemove()
    )
    return API_KEY

async def process_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['api_key'] = update.message.text
    await update.message.reply_text(
        "🔒 Enter your Dailymotion API Secret:",
        reply_markup=ReplyKeyboardRemove()
    )
    return API_SECRET

async def process_api_secret(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['api_secret'] = update.message.text
    await update.message.reply_text(
        "📧 Enter your Dailymotion account email:",
        reply_markup=ReplyKeyboardRemove()
    )
    return EMAIL

async def process_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text
    await update.message.reply_text(
        "🔐 Enter your Dailymotion account password:",
        reply_markup=ReplyKeyboardRemove()
    )
    return PASSWORD

async def process_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        password = update.message.text
        
        # Verify credentials with Dailymotion API
        verification = await verify_dailymotion_credentials(
            context.user_data['api_key'],
            context.user_data['api_secret'],
            context.user_data['email'],
            password
        )
        
        if verification['success']:
            # Save channel to database
            channel_data = {
                'user_id': user.id,
                'channel_name': context.user_data['channel_name'],
                'api_key': context.user_data['api_key'],
                'api_secret': context.user_data['api_secret'],
                'email': context.user_data['email'],
                'dm_user_id': verification['user_id'],
                'dm_username': verification['username']
            }
            db.add_channel(channel_data)
            
            await update.message.reply_text(
                f"✅ Channel '{context.user_data['channel_name']}' connected successfully!\n"
                f"Username: @{verification['username']}\n"
                "You can now upload videos to this channel.",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                "❌ Failed to verify credentials. Please check your details and try /addchannel again.",
                reply_markup=ReplyKeyboardRemove()
            )
        
    except Exception as e:
        logger.error(f"Error adding channel: {e}")
        await update.message.reply_text(
            "❌ An error occurred while connecting your channel. Please try /addchannel again.",
            reply_markup=ReplyKeyboardRemove()
        )
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_channel_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Channel setup cancelled.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END
