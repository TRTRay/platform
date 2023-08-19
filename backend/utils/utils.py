import time
import datetime

from backend.utils.staticData import StaticData


class Utils:
    @staticmethod
    def get_timestamp():
        now = time.time()
        date = datetime.datetime.fromtimestamp(now)
        data_string = date.strftime('%Y/%m/%d %H:%M:%S')
        return data_string

    @staticmethod
    def find_device(deviceid):
        device_list = StaticData.device_list
        for index, device in enumerate(device_list):
            if device['deviceId'] == deviceid:
                return [True, index]
        return [False, len(device_list)]
