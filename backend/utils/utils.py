import time
import datetime

from backend.config import *


# 获取字符串格式的时间戳
def get_timestamp():
    now = time.time()
    date = datetime.datetime.fromtimestamp(now)
    data_string = date.strftime('%Y/%m/%d %H:%M:%S')
    return data_string


# 从设备列表中查询某个设备id
def find_device(deviceid):
    for index, device in enumerate(device_list):
        if device['deviceId'] == deviceid:
            return [True, index]
    return [False, 0]
