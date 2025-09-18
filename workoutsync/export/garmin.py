import logging
import datetime
import os.path
import redis
from garminconnect import Garmin
from workoutsync.utils import Cache


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--redis', default='127.0.0.1:6379')
    parser.add_argument('--login', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--days', type=int, default=3)
    parser.add_argument('--storage', default='./.workouts')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    host, port = list(map(lambda x: int(x) if x.isdigit() else x, args.redis.split(':')))
    cache = Cache(redis.Redis(host, port))

    api = Garmin(args.login, args.password)
    api.login()

    now = datetime.datetime.now()
    start = now - datetime.timedelta(days=args.days)

    activities = api.get_activities_by_date(start.isoformat(), now.isoformat(), None)
    exported = 0
    for activity in activities:
        activity_id = activity['activityId']
        if cache.get(str(activity_id)) is not None:
            continue

        logging.info(f"{activity_id}: {activity['startTimeLocal']} - {activity['activityName']}")
        try:
            gpx_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.ORIGINAL)
            filename = os.path.join(args.storage, f"{str(activity_id)}.fit")
            with open(filename, "wb") as fp:
                fp.write(gpx_data)
            cache.set(str(activity_id),
                      {
                          "id": activity_id,
                          "date:": activity['startTimeGMT'],
                          "name": activity['activityName'],
                          "file": filename,
                          "type": activity["activityType"]["typeKey"]
                      })
            exported = exported + 1
        except RuntimeError:
            logging.exception(f"Unable to download activity {activity_id}")
    cache.store()
    exit(1 if exported == 0 else 0)


if __name__ == '__main__':
    main()
