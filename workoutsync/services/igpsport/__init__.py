import logging
import requests
import base64
import json
import time


class IgpSportApi:
    API_URL = "https://prod.en.igpsport.com/service"

    def __init__(self, username, password, token):
        self.username = username
        self.password = password
        self.token = token
        self.session = requests.Session()

    def _validate_token(self):
        if self.token is None:
            logging.warning('Access token is empty')
            return False
        parts = self.token.split('.')
        if len(parts) != 3:
            return False
        try:
            payload = parts[1]
            data = base64.b64decode(payload+'=' * (-len(payload) % 4), validate=False)
            payload = json.loads(data)
            if time.time() > payload.get('exp', 0):
                logging.warning('Access token is expired')
                return False
        except:
            logging.exception('Access token is invalid')
            return False
        return True

    def login(self):
        if not self._validate_token():
            logging.info(f'Get access_token usign username {self.username}')
            resp = self.session.post(IgpSportApi.API_URL+'/auth/account/login',
                                    json={'username': self.username, 'password': self.password, 'appId': 'igpsport-web'})
            resp.raise_for_status()
            self.token = resp.json()['data']['access_token']

    def find_activities(self, count, page):
        resp = self.session.get(IgpSportApi.API_URL+f'/web-gateway/web-analyze/activity/queryMyActivity?pageNo={page}&pageSize={count}&reqType=0&sort=1',
                                headers={'Authorization': f'Bearer {self.token}'})
        resp.raise_for_status()
        return resp.json().get('data', {}).get('rows', [])
    
    def get_activity_info(self, ride_id):
        resp = self.session.get(IgpSportApi.API_URL+f'/web-gateway/web-analyze/activity/queryActivityDetail/{ride_id}',
                                headers={'Authorization': f'Bearer {self.token}'})
        resp.raise_for_status()
        return resp.json().get('data', {})
    
    def download_activity(self, activity):
        resp = self.session.get(activity['fitUrl'])
        resp.raise_for_status()
        return resp.content
