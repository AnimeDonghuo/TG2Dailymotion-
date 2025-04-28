from telegram import Update
from telegram.ext import ContextTypes
from config import Config

async def premium_help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    premium_text = """
What is Premium?
Premium users enjoy the following benefits:
- Unlimited daily uploads: No restrictions on the number of videos you can upload each day.
- Priority support: Get faster responses and assistance from the bot owner.

How to Become Premium?
Contact the bot owner to upgrade to premium.
Use the command /pricing to view the premium pricing.

Contact the Bot Owner:
Telegram: @OwnerUsername

Premium Commands:
- /addpremium <user_id>: (Owner only) Add a user as a premium user.
- /removepremium <user_id>: (Owner only) Remove a user from premium.
"""
    await query.edit_message_text(premium_text)

async def pricing_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pricing_text = """
Premium Pricing Plans:

1. Monthly Plan: $5/month
   - Unlimited uploads
   - Priority support

2. Yearly Plan: $50/year (Save $10)
   - All monthly features
   - Early access to new features

Contact @OwnerUsername to subscribe.
"""
    await update.message.reply_text(pricing_text)
