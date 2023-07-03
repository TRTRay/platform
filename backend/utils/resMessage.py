# on_message中对各个topic的响应函数
import json
import time
import random
from threading import Thread
from backend.config import *
from backend.utils.utils import *


# topic:'/client/{deviceType}/{deviceId}/online
def res_online(client, userdata, msg):
    # 收到单个设备传来的上线信息，更新列表
    load_data = json.loads(msg.payload)['data']
    [result, index] = find_device(load_data['deviceId'])
    if result:
        device_list[index]['stat'] = "online"
    else:
        device_list.append(load_data)
    print(device_list)


# topic:'/client/{deviceType}/{deviceId}/offline
def res_offline(client, userdata, msg):
    # 收到单个设备的下线信息，更新设备列表
    load_data = json.loads(msg.payload)['data'][0]
    [result, index] = find_device(load_data['deviceId'])
    device_list[index]['stat'] = 'offline'


# (deprecated)
# topic:'/client/respond/deviceInform'
def res_inform(client, userdata, msg):
    # 收到单个设备传来的上线信息或下线信息，更新列表即可
    load = json.loads(msg.payload)
    device_list.append(load['data'])


# topic:'/client/showdata/#'
def res_showdata(client, userdata, msg):
    # 把接收数据存在一个地方供前端取
    data_slice.append(int(msg.payload))


def res_stop(client, userdata, msg):
    pass


# 无匹配的topic
def res_default(client, userdata, msg):
    print("default res_function!")
    pass


topic_case = {
    '/client/respond/deviceInform': res_inform,
    '/client/start': res_showdata,
    '/client/online': res_online,
    '/client/offline': res_offline,
    '/client/stop': res_stop

}
