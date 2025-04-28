from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.dailymotion_api import upload_to_dailymotion
from utils.mongodb import db
import os
import logging
import asyncio

logger = logging.getLogger(__name__)

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Validate update structure
        if not update.message or not update.effective_user:
            logger.warning("Invalid update structure - skipping")
            return

        user = update.effective_user
        message = update.message
        
        # Check if user has channels
        channels = db.get_user_channels(user.id)
        if not channels:
            await message.reply_text("❌ You haven't added any channels yet. Use /addchannel first.")
            return

        # Download the video with progress updates
        status_msg = await message.reply_text("⬇️ Downloading your video...")
        
        try:
            video_file = await (message.video or message.document).get_file()
            file_path = f"temp_{user.id}_{message.message_id}.mp4"
            await video_file.download_to_drive(file_path)
            await status_msg.edit_text("✅ Download complete!\n🔼 Preparing to upload...")
        except Exception as e:
            logger.error(f"Download failed: {e}")
            await status_msg.edit_text("❌ Failed to download video. Please try again.")
            return

        # Channel selection keyboard
        keyboard = [
            [InlineKeyboardButton(ch['channel_name'], callback_data=f"upload_{ch['_id']}")]
            for ch in channels
        ]
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_upload")])
        
        await status_msg.edit_text(
            "📤 Select a channel for upload:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        # Store file path in context
        context.user_data['file_path'] = file_path
        context.user_data['status_msg'] = status_msg

    except Exception as e:
        logger.error(f"Video handler error: {e}")
        if update.message:
            await update.message.reply_text("❌ An error occurred. Please try again.")
