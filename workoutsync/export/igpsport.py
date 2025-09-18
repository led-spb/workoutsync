import logging
import os.path
import os

from igpsport import IgpSportApi


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--login', default=os.environ.get('API_USERNAME'))
    parser.add_argument('--password', default=os.environ.get('API_PASSWORD'))
    parser.add_argument('--api-key-path', default='.token')
    parser.add_argument('--page', type=int, default=1)
    parser.add_argument('--count', type=int, default=10)
    parser.add_argument('--storage', default='./.workouts')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    token = None
    try:
        with open(args.api_key_path, 'rt') as fp:
            token = fp.read()
    except:
        pass    

    api = IgpSportApi(args.login, args.password, token)
    api.login()

    try:
        with open(args.api_key_path, 'wt') as fp:
            fp.write(api.token)
    except:
        pass

    activities = api.find_activities(args.count, args.page)
    exported = 0
    for activity in activities:
        activity_id = activity['rideId']

        try:
            filename = os.path.join(args.storage, f"{str(activity_id)}.fit")
            if os.path.exists(filename):
                continue

            logging.info(f"{activity_id}: {activity['startTime']} - {activity['title']}")
            activity = api.get_activity_info(activity_id)
            
            activity_data = api.download_activity(activity)
            with open(filename, "wb") as fp:
                fp.write(activity_data)
                exported = exported + 1

        except RuntimeError:
            logging.exception(f"Unable to download activity {activity_id}")
    exit(1 if exported == 0 else 0)


if __name__ == '__main__':
    main()
