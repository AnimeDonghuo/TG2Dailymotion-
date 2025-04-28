import dailymotion
from config import Config

class DailymotionAPI:
    def __init__(self):
        self.dm = dailymotion.Dailymotion()
        self.dm.set_grant_type('password', api_key=Config.DAILYMOTION_KEY, 
                             api_secret=Config.DAILYMOTION_SECRET)
    
    def upload_video(self, file_path, title, channel_id=None, description=None, tags=None):
        try:
            # Authenticate
            self.dm.set_grant_type('password', api_key=Config.DAILYMOTION_KEY,
                                 api_secret=Config.DAILYMOTION_SECRET)
            
            # Upload parameters
            params = {
                'url': file_path,
                'title': title,
                'published': True
            }
            
            if channel_id:
                params['channel'] = channel_id
            if description:
                params['description'] = description
            if tags:
                params['tags'] = tags
                
            # Upload video
            result = self.dm.post('/me/videos', params)
            return result.get('id'), None
        except Exception as e:
            return None, str(e)
    
    def get_channel_info(self, channel_id):
        try:
            fields = 'id,name,description,avatar_120_url'
            channel = self.dm.get(f'/channel/{channel_id}', fields=fields)
            return channel, None
        except Exception as e:
            return None, str(e)
