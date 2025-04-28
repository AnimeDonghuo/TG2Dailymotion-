import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    DAILYMOTION_KEY = os.getenv('DAILYMOTION_API_KEY')
    DAILYMOTION_SECRET = os.getenv('DAILYMOTION_API_SECRET')
    ADMIN_ID = int(os.getenv('ADMIN_USER_ID'))
    DATABASE_URL = os.getenv('DATABASE_URL')
    DAILY_LIMIT = int(os.getenv('DAILY_UPLOAD_LIMIT'))
    
    PREMIUM_FEATURES = {
        'unlimited_uploads': True,
        'priority_support': True
    }
