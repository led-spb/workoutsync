import time
import requests


class StravaError(BaseException):
    ...


class StravaUnauthorizedError(StravaError):
    ...


class StravaApi:
    TOKEN_URL = "https://www.strava.com/oauth/token"
    API_URL = "https://www.strava.com/api/v3"

    def __init__(self, client_id, client_secret, token_data):
        self.client_id = client_id
        self.token = token_data
        self.client_secret = client_secret
        pass

    def make_request(self, method, uri, data=None):
        return requests.request(method, self.API_URL+uri,
                                headers={'Authorization': f'Bearer {self.token["access_token"]}'})

    def validate_api_response(self, response):
        data = response.json()
        if data.get('errors') is not None:
            error = data['errors'][0]
            if error.get('code') == '403':
                raise StravaUnauthorizedError(*error.values())
            raise StravaError(*(data['message'], *error.values()))
        return data

    def refresh_token(self, force=False):
        if self.token['expires_at'] < time.time() or force:
            self.token = self.validate_api_response(
                requests.post(self.TOKEN_URL,
                              {'client_id': self.client_id,
                               'client_secret': self.client_secret,
                               'grant_type': 'refresh_token',
                               'refresh_token': self.token['refresh_token']}))
        pass

    def get_athlete_info(self):
        return self.validate_api_response(self.make_request('GET', '/athlete'))

    def get_athlete_stats(self, athlete_id):
        return self.validate_api_response(self.make_request('GET', f'/athletes/{athlete_id}/stats'))

    def upload(self, workout_file):
        resp = requests.request(
            'POST', self.API_URL + '/uploads',
            data={'data_type': 'gpx'},
            headers={'Authorization': f'Bearer {self.token["access_token"]}'},
            files=[('file', ('workout.gpx', workout_file, 'application/octet-stream'))]
        )
        return self.validate_api_response(resp)
