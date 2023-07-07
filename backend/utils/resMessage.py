# on_message中对各个topic的响应函数
import json
import numpy as np
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
    load_data = json.loads(msg.payload)['data']
    [result, index] = find_device(load_data['deviceId'])
    device_list[index]['stat'] = 'offline'


# topic:'/client/respond/deviceInform'
def res_inform(client, userdata, msg):
    # deprecate
    load_data = json.loads(msg.payload)['data']
    [result, index] = find_device(load_data['deviceId'])
    if result:
        pass
    else:
        pass


# topic:'/client/{devType}/{deviceId}/start'
def res_start(client, userdata, msg):
    # 把接收数据存在一个地方供前端取
    # 现在仅支持单设备，还需要继续完善
    topic_split = msg.topic.split('/')
    devId = topic_split[3]
    [result, index] = find_device(devId)
    deviceInform = device_list[index]
    recorderChannels = deviceInform['params']['recorderChannals']
    data = np.fromstring(msg.payload, dtype=np.int16)
    data.reshape(-1, recorderChannels)
    for dataframe in data:
        # print(dataframe)
        data_slice.append(dataframe.tolist())


def res_stop(client, userdata, msg):
    pass


# 无匹配的topic
def res_default(client, userdata, msg):
    print("default res_function!")
    msg_topic = msg.topic
    if msg_topic.endswith('/start'):
        res_start(client, userdata, msg)
    pass


topic_case = {
    '/client/respond/deviceInform': res_inform,
    '/client/online': res_online,
    '/client/offline': res_offline,
    '/client/stop': res_stop

}
