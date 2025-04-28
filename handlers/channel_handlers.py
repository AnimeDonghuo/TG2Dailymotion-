from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.mongodb import db
from config import Config
from datetime import datetime
from bson import ObjectId

async def add_channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("""
To add a Dailymotion channel, please send the following details in this format:

Channel Name: Your Channel Name
Username: your_dailymotion_username
Client ID: your_client_id

Example:
Channel Name: Anime Donghua
Username: animefan123
Client ID: 4b8ebba0a67b86ead065
""")

async def my_channels_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    channels = db.get_user_channels(user.id)
    
    if not channels:
        await query.edit_message_text("You haven't added any channels yet.")
        return
    
    response = "### Your Channels:\n\n"
    for idx, channel in enumerate(channels, 1):
        response += f"{idx}. {channel['channel_name']}\n"
        response += f"   - Username: {channel['username']}\n"
        response += f"   - Client ID: {channel['client_id']}\n"
        response += f"   - Added on: {channel['added_date'].strftime('%Y-%m-%d')}\n\n"
    
    await query.edit_message_text(response)

async def remove_channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    channels = db.get_user_channels(user.id)
    
    if not channels:
        await query.edit_message_text("You don't have any channels to remove.")
        return
    
    keyboard = [[InlineKeyboardButton(ch['channel_name'], callback_data=f"remove_{str(ch['_id'])}")] for ch in channels]
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel_remove")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("Select a channel to remove:", reply_markup=reply_markup)
