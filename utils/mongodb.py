from pymongo import MongoClient
from config import Config
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self):
        self.client = MongoClient(Config.DATABASE_URL)
        self.db = self.client.get_database('dailymotion_bot')
        
        # Create indexes
        self.db.users.create_index("telegram_id", unique=True)
        self.db.channels.create_index("user_id")
        self.db.uploads.create_index([("user_id", 1), ("upload_date", 1)])
        
    def get_user(self, telegram_id: int) -> dict:
        return self.db.users.find_one({"telegram_id": telegram_id})
    
    def create_user(self, user_data: dict) -> ObjectId:
        user_data['join_date'] = datetime.utcnow()
        return self.db.users.insert_one(user_data).inserted_id
    
    def add_channel(self, channel_data: dict) -> ObjectId:
        channel_data['added_date'] = datetime.utcnow()
        return self.db.channels.insert_one(channel_data).inserted_id
    
    def get_user_channels(self, user_id: int) -> list:
        return list(self.db.channels.find({"user_id": user_id}))
    
    def remove_channel(self, channel_id: str) -> bool:
        result = self.db.channels.delete_one({"_id": ObjectId(channel_id)})
        return result.deleted_count > 0

# Initialize MongoDB connection
db = MongoDB()
