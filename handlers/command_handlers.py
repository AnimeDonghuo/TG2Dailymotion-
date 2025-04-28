from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.mongodb import db
from config import Config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
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
    except Exception as e:
        logger.error(f"Error in start_handler: {str(e)}")
        await update.message.reply_text("An error occurred. Please try again.")

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
    try:
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
    except Exception as e:
        logger.error(f"Error in limit_status_handler: {str(e)}")
        await update.message.reply_text("Could not check your upload status. Please try again.")

async def channel_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        channels = db.get_user_channels(user.id)
        
        if not channels:
            await update.message.reply_text("You haven't added any channels yet.")
            return
        
        response = "📺 Your Channels Status:\n\n"
        for channel in channels:
            today_uploads = db.db.uploads.count_documents({
                "user_id": user.id,
                "channel_id": channel['_id'],
                "upload_date": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
            })
            
            response += f"🔹 {channel['channel_name']}\n"
            response += f"   - Today's uploads: {today_uploads}\n"
            response += f"   - Username: {channel['username']}\n\n"
        
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error in channel_status_handler: {str(e)}")
        await update.message.reply_text("Could not retrieve channel status. Please try again.")

async def full_guide_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    guide_text = """
📖 Full User Guide:

1. Adding Channels:
   - Use the "Add Channel" button
   - Provide your Dailymotion channel details in this format:
     Channel Name: Your Channel Name
     Username: your_dailymotion_username
     Client ID: your_client_id

2. Uploading Videos:
   - Simply send a video file to the bot
   - Select your channel
   - Choose a title option
   - The bot will handle the upload

3. Managing Channels:
   - View your channels with "My Channels"
   - Remove channels with "Remove Channel"

4. Premium Features:
   - Unlimited daily uploads
   - Priority support
   - Use /pricing to see subscription options

For additional help, contact the bot owner.
"""
    await update.message.reply_text(guide_text)
