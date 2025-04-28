import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext
from utils.mongodb import db
from config import Config
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Validate the update structure
        if not update.effective_message or not update.effective_user:
            logger.warning("Invalid update structure received")
            return

        message = update.effective_message
        user = update.effective_user
        
        # Verify we have a video
        if not message.video and not (message.document and message.document.mime_type.startswith('video/')):
            logger.warning("Received non-video message in video handler")
            return

        logger.info(f"Processing video from user {user.id}")

        # Ensure user exists in database
        db_user = db.get_user(user.id)
        if not db_user:
            logger.info(f"Creating new user record for {user.id}")
            db.create_user({
                "telegram_id": user.id,
                "username": user.username,
                "is_premium": False
            })
            db_user = db.get_user(user.id)

        # Check upload limits
        today_uploads = db.get_today_uploads(user.id)
        if not db_user.get('is_premium', False) and today_uploads >= Config.DAILY_LIMIT:
            await message.reply_text(
                f"⚠️ You've reached your daily upload limit ({Config.DAILY_LIMIT}).\n"
                "Upgrade to premium for unlimited uploads."
            )
            return

        # Download the video file
        video_file = await (message.video or message.document).get_file()
        file_path = f"temp_{user.id}_{message.message_id}.mp4"
        
        try:
            await video_file.download_to_drive(file_path)
            logger.info(f"Video saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to download video: {str(e)}")
            await message.reply_text("❌ Failed to download your video. Please try again.")
            return

        # Get user's channels
        channels = db.get_user_channels(user.id)
        if not channels:
            await message.reply_text("You haven't added any channels yet. Please add a channel first.")
            try:
                os.remove(file_path)
            except:
                pass
            return

        # Create channel selection keyboard
        keyboard = [
            [InlineKeyboardButton(ch['channel_name'], callback_data=f"upload_channel_{str(ch['_id'])}")]
            for ch in channels
        ]
        keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel_upload")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            "📤 Please select a channel for upload:",
            reply_markup=reply_markup
        )
        
        # Store file path in context
        context.user_data['temp_video_path'] = file_path
        context.user_data['upload_message_id'] = message.message_id

    except Exception as e:
        logger.error(f"Error in video_handler: {str(e)}", exc_info=True)
        if update.effective_message:
            await update.effective_message.reply_text("❌ An error occurred while processing your video. Please try again.")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.effective_user:
            return

        text = update.message.text
        user = update.effective_user
        
        # Handle channel addition
        if all(x in text for x in ["Channel Name:", "Username:", "Client ID:"]):
            try:
                parts = [p.strip() for p in text.split('\n') if p.strip()]
                channel_data = {
                    "user_id": user.id,
                    "channel_name": parts[0].replace("Channel Name:", "").strip(),
                    "username": parts[1].replace("Username:", "").strip(),
                    "client_id": parts[2].replace("Client ID:", "").strip()
                }
                
                channel_id = db.add_channel(channel_data)
                await update.message.reply_text(
                    f"✅ Channel '{channel_data['channel_name']}' added successfully!\n"
                    f"Client ID: {channel_data['client_id']}"
                )
            except Exception as e:
                await update.message.reply_text(
                    "❌ Failed to add channel. Please check the format:\n\n"
                    "Channel Name: Your Channel\n"
                    "Username: your_username\n"
                    "Client ID: your_client_id"
                )
        else:
            await update.message.reply_text(
                "I didn't understand that message. Here's what you can do:\n\n"
                "1. Send a video to upload it\n"
                "2. Add a channel with the format:\n"
                "Channel Name: Your Channel\n"
                "Username: your_username\n"
                "Client ID: your_client_id"
            )

    except Exception as e:
        logger.error(f"Error in text_handler: {str(e)}")
        if update.message:
            await update.message.reply_text("❌ An error occurred. Please try again.")
