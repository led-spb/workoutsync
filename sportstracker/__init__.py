import requests


class SportsTrackerError(BaseException):
    ...


class SportsTrackerUnauthorizedError(SportsTrackerError):
    ...


class SportsTrackerApi:
    BASE_URL = "https://api.sports-tracker.com/apiserver/v1"

    def __init__(self, session_data=None):
        self.session = requests.Session()
        self.session_data = session_data
        self.configure_session()

    def configure_session(self):
        session_key = self.session_data.get('userKey') if self.session_data is not None else None
        self.session.headers.update({'STTAuthorization': session_key})

    def validate_api_response(self, response):
        data = response.json()
        if data.get('error') is not None:
            error = data['error']
            if error.get('code') == '403':
                raise SportsTrackerUnauthorizedError(*error.values())
            raise SportsTrackerError(*error.values())
        return data

    def authorize(self, login, password):
        resp = self.session.request(
            'POST', self.BASE_URL+'/login', {'source': 'javascript'}, {'l': login, 'p': password}
        )
        self.session_data = self.validate_api_response(resp)
        self.configure_session()

    def get_user(self):
        resp = self.session.get(self.BASE_URL+'/user')
        data = self.validate_api_response(resp)
        return data.get('payload')

    def get_workouts(self, limit=10, offset=0):
        resp = self.session.request(
            'GET', self.BASE_URL + '/workouts', {'sortonst': 'true', 'offset': offset, 'limit': limit}
        )
        return self.validate_api_response(resp).get('payload')

    def import_workout(self, gpx_file):
        resp = self.session.request(
            'POST', self.BASE_URL+'/workout/importGpx',
            files=[('file', ('workout.gpx', gpx_file, 'application/octet-stream'))]
        )
        return self.validate_api_response(resp).get('payload')

    def update_workout(self, workout):
        resp = self.session.request(
            'POST', self.BASE_URL+'/workouts/header',
            json=[workout]
        )
        return self.validate_api_response(resp).get('payload')
