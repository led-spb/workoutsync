import logging
import redis
from sportstracker import SportsTrackerApi, SportsTrackerError
from workoutsync.utils import Cache


def main():
    import argparse
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--redis', default='127.0.0.1:6379')
    parser.add_argument('--apikey', required=True)
    args = parser.parse_args()

    host, port = list(map(lambda x: int(x) if x.isdigit() else x, args.redis.split(':')))
    cache = Cache(redis.Redis(host, port))

    activities = []
    for key in cache.keys():
        activity = cache.get(key)
        if activity.get('imported') is None or 'sportstracker' not in activity.get('imported'):
            activities.append(activity)

    if len(activities) == 0:
        logging.info('No workouts for import')
        return

    try:
        sportstracker = SportsTrackerApi({"userKey": args.apikey})
        sportstracker.get_user()

        for activity in activities:
            logging.info(f"{activity['file']}")
            try:
                with open(activity['file']) as fp:
                    workout = sportstracker.import_workout(fp)
                    sportstracker.update_workout({
                        "totalDistance": workout['totalDistance'],
                        "workoutKey":  workout['workoutKey'],
                        "activityId": 2,
                        "startTime": workout["startTime"],
                        "totalTime": workout["totalTime"],
                        "description": activity['name'],
                        "energyConsumption": workout["energyConsumption"],
                        "sharingFlags": 0
                    })
                if activity.get('imported') is None:
                    activity['imported'] = []
                activity['imported'].append('sportstracker')
                cache.set(activity['id'], activity)
            except SportsTrackerError:
                logging.exception('Unable to import workout')
    finally:
        cache.store()


if __name__ == '__main__':
    main()
