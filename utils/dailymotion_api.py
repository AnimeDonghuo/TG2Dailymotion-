import dailymotion
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def verify_dailymotion_credentials(api_key: str, api_secret: str, email: str, password: str) -> Dict[str, Any]:
    try:
        dm = dailymotion.Dailymotion()
        dm.set_grant_type(
            'password',
            api_key=api_key,
            api_secret=api_secret,
            username=email,
            password=password,
            scope=['manage_videos']
        )
        
        # Get user info to verify credentials
        user_info = dm.get('/me')
        
        return {
            'success': True,
            'username': user_info.get('username'),
            'user_id': user_info.get('id')
        }
        
    except Exception as e:
        logger.error(f"DM verification failed: {e}")
        return {'success': False}

async def upload_to_dailymotion(channel_data: Dict[str, Any], file_path: str, title: str) -> Dict[str, Any]:
    try:
        dm = dailymotion.Dailymotion()
        dm.set_grant_type(
            'password',
            api_key=channel_data['api_key'],
            api_secret=channel_data['api_secret'],
            username=channel_data['email'],
            password=channel_data['password'],
            scope=['manage_videos']
        )
        
        # Upload the video with progress
        url = dm.upload(file_path)
        result = dm.post('/me/videos', {
            'url': url,
            'title': title,
            'published': True
        })
        
        return {
            'success': True,
            'video_id': result.get('id'),
            'url': f"https://dailymotion.com/video/{result.get('id')}"
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return {'success': False}
