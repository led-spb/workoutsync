import fitdecode
from functools import reduce


class FITDataExctractor:
    def init(self):
        pass

    def extract_stream(self, filename, streams):
        with fitdecode.FitReader(filename) as fit:
            for frame in fit:
                if frame.frame_type != fitdecode.FIT_FRAME_DATA:
                    continue
                if frame.has_field('timestamp'):
                    try:
                        data = reduce(lambda values, field: values + [frame.get_value(field)], streams, [])
                        yield frame.get_value('timestamp'), *data
                    except KeyError:
                        pass
        pass

    def dump(self, filename):
        with fitdecode.FitReader(filename) as fit:
            for frame in fit:
                if frame.frame_type == fitdecode.FIT_FRAME_DATA:
                    print(f'{frame.frame_type}:{frame.name}')
