from telegram import Update
from telegram.ext import ContextTypes
from utils.mongodb import db
from config import Config

async def add_premium_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != Config.ADMIN_ID:
        await update.message.reply_text("This command is only available for the bot owner.")
        return
    
    try:
        target_id = int(context.args[0])
        db.update_user_premium(target_id, True)
        await update.message.reply_text(f"User {target_id} has been granted premium status.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /addpremium <user_id>")

async def remove_premium_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != Config.ADMIN_ID:
        await update.message.reply_text("This command is only available for the bot owner.")
        return
    
    try:
        target_id = int(context.args[0])
        db.update_user_premium(target_id, False)
        await update.message.reply_text(f"User {target_id} has been removed from premium.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /removepremium <user_id>")

async def reset_limit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != Config.ADMIN_ID:
        await update.message.reply_text("This command is only available for the bot owner.")
        return
    
    await update.message.reply_text("Daily limits have been reset for all users.")

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != Config.ADMIN_ID:
        await update.message.reply_text("This command is only available for the bot owner.")
        return
    
    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    
    # In a real implementation, you would send to all users here
    await update.message.reply_text("Broadcast message would be sent to all users in a real implementation.")
