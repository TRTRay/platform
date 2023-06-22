# on_message中对各个topic的响应函数
import json
import time
import random
from threading import Thread
from backend.config import *


# topic:'/client/respond/deviceInform'
def res_inform(client, userdata, msg):
    if test_mode:
        device_list.extend(json.loads(msg.payload))
    else:
        deviceInform = json.loads(msg.payload)
        device_list.append(deviceInform)


# topic:'/client/showdata/#'
def res_showdata(client, userdata, msg):
    data_slice.append(int(msg.payload))
    print(data_slice)
    # print(int(msg.payload))


# 无匹配的topic
def res_default(client, userdata, msg):
    print(json.loads(msg.payload)['message'])
    pass


topic_case = {
    '/client/respond/deviceInform': res_inform,
    '/client/showdata/': res_showdata

}
