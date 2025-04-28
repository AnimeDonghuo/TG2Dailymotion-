import requests
from config import Config
from urllib.parse import urlencode

class DailymotionAPI:
    def __init__(self):
        self.base_url = "https://api.dailymotion.com"
        self.token = self._get_access_token()
        
    def _get_access_token(self):
        auth_url = f"{self.base_url}/oauth/token"
        payload = {
            'grant_type': 'password',
            'client_id': Config.DAILYMOTION_KEY,
            'client_secret': Config.DAILYMOTION_SECRET,
            'username': Config.DAILYMOTION_USERNAME,
            'password': Config.DAILYMOTION_PASSWORD,
            'scope': 'manage_videos'
        }
        
        response = requests.post(auth_url, data=payload)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            raise Exception(f"Authentication failed: {response.text}")
    
    def upload_video(self, file_path, title, channel_id=None, description=None, tags=None):
        try:
            upload_url = f"{self.base_url}/me/videos"
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            
            params = {
                'title': title,
                'published': True
            }
            
            if channel_id:
                params['channel'] = channel_id
            if description:
                params['description'] = description
            if tags:
                params['tags'] = tags
                
            with open(file_path, 'rb') as video_file:
                files = {'file': video_file}
                response = requests.post(upload_url, headers=headers, data=params, files=files)
                
            if response.status_code == 200:
                return response.json().get('id'), None
            else:
                return None, response.text
        except Exception as e:
            return None, str(e)
    
    def get_channel_info(self, channel_id):
        try:
            url = f"{self.base_url}/channel/{channel_id}"
            params = {
                'fields': 'id,name,description,avatar_120_url'
            }
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json(), None
            else:
                return None, response.text
        except Exception as e:
            return None, str(e)
