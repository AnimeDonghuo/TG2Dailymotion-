from pymongo import MongoClient
from config import Config
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self):
        try:
            self.client = MongoClient(Config.DATABASE_URL)
            self.db = self.client.get_database('dailymotion_bot')
            
            # Create indexes
            self.db.users.create_index("telegram_id", unique=True)
            self.db.channels.create_index("user_id")
            self.db.uploads.create_index([("user_id", 1), ("upload_date", 1)])
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise
        
    def get_user(self, telegram_id):
        return self.db.users.find_one({"telegram_id": telegram_id})
    
    def create_user(self, user_data):
        user_data['join_date'] = datetime.utcnow()
        return self.db.users.insert_one(user_data).inserted_id
    
    def update_user_premium(self, telegram_id, is_premium):
        return self.db.users.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"is_premium": is_premium}}
        )
    
    def add_channel(self, channel_data):
        channel_data['added_date'] = datetime.utcnow()
        return self.db.channels.insert_one(channel_data).inserted_id
    
    def get_user_channels(self, user_id):
        return list(self.db.channels.find({"user_id": user_id}))
    
    def get_channel(self, channel_id):
        return self.db.channels.find_one({"_id": ObjectId(channel_id)})
    
    def remove_channel(self, channel_id):
        return self.db.channels.delete_one({"_id": ObjectId(channel_id)})
    
    def add_upload(self, upload_data):
        upload_data['upload_date'] = datetime.utcnow()
        return self.db.uploads.insert_one(upload_data).inserted_id
    
    def get_today_uploads(self, user_id):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return self.db.uploads.count_documents({
            "user_id": user_id,
            "upload_date": {"$gte": today}
        })

# Initialize MongoDB connection
db = MongoDB()
