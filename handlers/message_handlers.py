import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext
from utils.mongodb import db
from utils.dailymotion_api import DailymotionAPI
from config import Config
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Check if we have a valid message and user
        if not update.message or not update.effective_user:
            logger.warning("Received video update without message or user")
            return

        user = update.effective_user
        message = update.message
        
        logger.info(f"Received video from user {user.id}")

        # Check if user exists in database or create new
        db_user = db.get_user(user.id)
        if not db_user:
            logger.info(f"Creating new user record for {user.id}")
            db.create_user({
                "telegram_id": user.id,
                "username": user.username,
                "is_premium": False
            })
            db_user = db.get_user(user.id)

        # Check daily upload limit
        today_uploads = db.get_today_uploads(user.id)
        if not db_user.get('is_premium', False) and today_uploads >= Config.DAILY_LIMIT:
            await message.reply_text(
                f"You've reached your daily upload limit ({Config.DAILY_LIMIT}). "
                "Upgrade to premium for unlimited uploads."
            )
            return

        # Get the video file
        video_file = await message.video.get_file()
        file_path = f"temp_{user.id}_{message.message_id}.mp4"
        await video_file.download_to_drive(file_path)
        logger.info(f"Video downloaded to {file_path}")

        # Get user's channels
        channels = db.get_user_channels(user.id)
        if not channels:
            await message.reply_text("You haven't added any channels yet. Please add a channel first.")
            os.remove(file_path)
            return

        # Prepare channel selection keyboard
        keyboard = [
            [InlineKeyboardButton(ch['channel_name'], callback_data=f"upload_channel_{str(ch['_id'])}")]
            for ch in channels
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text("Please select a channel for upload:", reply_markup=reply_markup)
        
        # Store file path in context for later use
        context.user_data['temp_video_path'] = file_path
        logger.info("Channel selection requested")

    except Exception as e:
        logger.error(f"Error in video_handler: {str(e)}", exc_info=True)
        if update.message:
            await update.message.reply_text("An error occurred while processing your video. Please try again.")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.effective_user:
            return

        text = update.message.text
        user = update.effective_user
        logger.info(f"Received text message from {user.id}: {text}")

        # Check if this is channel information
        if "Channel Name:" in text and "Username:" in text and "Client ID:" in text:
            try:
                parts = [p.strip() for p in text.split('\n') if p.strip()]
                channel_data = {
                    "user_id": user.id,
                    "channel_name": parts[0].replace("Channel Name:", "").strip(),
                    "username": parts[1].replace("Username:", "").strip(),
                    "client_id": parts[2].replace("Client ID:", "").strip()
                }
                
                channel_id = db.add_channel(channel_data)
                logger.info(f"Channel added: {channel_data['channel_name']}")
                await update.message.reply_text(f"Channel '{channel_data['channel_name']}' added successfully!")
            except Exception as e:
                logger.error(f"Error adding channel: {str(e)}")
                await update.message.reply_text(f"Error adding channel: {str(e)}")
        else:
            await update.message.reply_text("I didn't understand that message. Use /help to see available commands.")
    except Exception as e:
        logger.error(f"Error in text_handler: {str(e)}")
        if update.message:
            await update.message.reply_text("An error occurred while processing your message.")
