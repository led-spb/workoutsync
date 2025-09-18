import argparse
import glob
import logging
import json
import redis
from ..services.strava import StravaApi
from ..utils import Cache


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--redis', default='127.0.0.1:6379')
    parser.add_argument('--client_id', type=int, required=True)
    parser.add_argument('--client_secret', required=True)
    parser.add_argument('--athlete_id', type=int, required=True)
    args = parser.parse_args()

    host, port = list(map(lambda x: int(x) if x.isdigit() else x, args.redis.split(':')))
    redis_client = redis.Redis(host, port)
    cache = Cache(redis_client)

    activities = []
    for key in cache.keys():
        activity = cache.get(key)
        if activity.get('imported') is None or 'strava' not in activity.get('imported'):
            activities.append(activity)

    if len(activities) == 0:
        logging.info('No workouts for import')
        return

    token_data = json.loads(redis_client.get(f'strava:{args.athlete_id}'))
    strava = StravaApi(client_id=args.client_id, client_secret=args.client_secret, token_data=token_data)
    strava.refresh_token(False)
    redis_client.set(f'strava:{args.athlete_id}', json.dumps(strava.token))

    for activity in activities:
        logging.info(f"{activity['file']}")
        try:
            with open(activity['file']) as fp:
                strava.upload(fp)

            if activity.get('imported') is None:
                activity['imported'] = []
            activity['imported'].append('strava')

            cache.set(activity['id'], activity)
        except:
            pass
    cache.store()


if __name__ == '__main__':
    main()
