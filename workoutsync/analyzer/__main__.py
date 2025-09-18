from . import FITDataExctractor
import matplotlib.pyplot as plt
from statistics import mean


def moving_agv(data, window_sec):
    point = 0
    acc = 0
    acc_points = 0

    total_points = len(data)

    for i in range(total_points):
        acc = acc + data[i][1]
        acc_points = acc_points + 1

        ela = data[i][0] - data[point][0] + 1
        if ela >= window_sec:
            yield acc/acc_points if acc_points > 0 else 0
            acc = acc - data[point][1]
            acc_points = acc_points - 1
            point = point + 1
            if point == total_points:
                return

    yield acc / acc_points if acc_points > 0 else 0


def power_curve(stream, buckets):
    for bucket in buckets:
        average_power = max(moving_agv(stream, bucket))
        yield bucket, average_power


def interval_label(s):
    if s < 60:
        return f'{s}s'
    if s < 3600:
        return f'{s//60}m'
    return f'{s//3600}h'


if __name__ == '__main__':
    extractor = FITDataExctractor()
    extractor.dump('.workouts/66703413.fit')
    exit()
    data = list(extractor.extract_stream('.workouts/66703413.fit', ['power']))
    start_time = min([item[0] for item in data])
    data = list(map(lambda x: ((x[0]-start_time).total_seconds(), x[1],), data))

    # average
    avg = mean([x[1] for x in data])
    print('avg_power', avg)

    # normalized power
    np = pow(mean(map(lambda x: pow(x, 4), moving_agv(data, 30))), 0.25)
    print('np', np)

    # power curve
    buckets = (1, 2, 3, 5, 10, 20, 30, 1 * 60, 2 * 60, 5 * 60, 10 * 60, 20 * 60, 30 * 60, 60 * 60)
    pc = list(power_curve(data, buckets))
    plt.figure()
    #plt.subplot(2, 1, 1)
    plt.plot(
        [interval_label(x[0]) for x in pc],
        [x[1] for x in pc]
    )
    plt.grid(True)

    plt.show()
