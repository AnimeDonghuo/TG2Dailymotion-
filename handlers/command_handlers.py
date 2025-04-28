from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.mongodb import db
from config import Config
from datetime import datetime

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Check if user exists in database
    db_user = db.get_user(user.id)
    if not db_user:
        db.create_user({
            "telegram_id": user.id,
            "username": user.username,
            "is_premium": False
        })
        db_user = db.get_user(user.id)
    
    premium_status = "🍀 Premium" if db_user.get('is_premium', False) else "✘ Not Premium"
    
    welcome_message = f"""
Welcome to the Dailymotion Uploader Bot, {user.first_name}!

✔ Premium Status: {premium_status}

What can this bot do?
- Upload videos to your Dailymotion channels.
- Manage multiple Dailymotion channels.
- Enjoy unlimited uploads with premium status.
"""
    
    keyboard = [
        [InlineKeyboardButton("Help", callback_data="help"),
         InlineKeyboardButton("+ Add Channel", callback_data="add_channel")],
        [InlineKeyboardButton("My Channels", callback_data="my_channels"),
         InlineKeyboardButton("Premium Help", callback_data="premium_help")],
        [InlineKeyboardButton("Remove Channel", callback_data="remove_channel"),
         InlineKeyboardButton("Full Guide", callback_data="full_guide")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Here are the commands and features available:

- /start - Start the bot and view your premium status
- /help - Show this help message
- /limitstatus - Check your upload status and daily limits
- /channelstatus - Check upload status for your channels
- /fullguide - Get detailed usage guide
- /pricing - View premium pricing details
- /ping - Check bot response time

Channel Management:
- Add Channel - Add a new Dailymotion channel
- My Channels - List your added channels
- Remove Channel - Remove a channel

Premium Features:
- Unlimited daily uploads
- Priority support
"""
    await update.message.reply_text(help_text)

async def limit_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = db.get_user(user.id)
    
    today_uploads = db.get_today_uploads(user.id)
    limit = "∞" if db_user.get('is_premium', False) else Config.DAILY_LIMIT
    
    status_message = f"""
📊 Your Upload Status:

Today's uploads: {today_uploads}
Daily limit: {limit}

"""
    if not db_user.get('is_premium', False) and today_uploads >= Config.DAILY_LIMIT:
        status_message += "⚠️ You've reached your daily limit. Consider upgrading to premium."
    
    await update.message.reply_text(status_message)
