# on_message中对各个topic的响应函数
import json
import math
import numpy as np
from backend.config import *
from backend.utils.utils import *


# topic:'/client/{deviceType}/{deviceId}/online
def res_online(client, userdata, msg):
    # 收到单个设备传来的上线信息，更新列表
    load_data = json.loads(msg.payload)['data']

    # # 收到报文，存在message就打印一下
    # if 'message' in load_data:
    #     print('message: {0}'.format(load_data['message']))

    msg_topic = msg.topic
    # wifi设备在尝试完成初始化
    if load_data['stat'] == 'off':
        print('Device {0} is trying to setup.'.format(load_data['deviceId']))
        return
    [result, index] = find_device(load_data['deviceId'])
    if result:
        device_list[index]['stat'] = "on"
    else:
        if load_data['devType'] == 'WiFi-Tx' or load_data['devType'] == 'WiFi-Rx':
            if load_data['params']['rx_model'] == 'a':
                load_data['params']['rx_model'] = ['csi', 'plcr']
            if load_data['params']['rx_model'] == 'p':
                load_data['params']['rx_model'] = ['plcr']
            if load_data['params']['rx_model'] == 'c':
                load_data['params']['rx_model'] = ['csi']
        device_list.append(load_data)
    print(device_list)
    deviceInform = device_list[index]
    # 创建数据缓存
    if load_data['devType'] == 'Speaker':
        data_key = load_data['deviceId'] + '_' + 'wav'
        if data_key not in data_slice:
            # 这样操作是因为直接创建空list加不进data_slice
            data_slice[data_key] = [1]
            data_slice[data_key].clear()
    elif load_data['devType'] == 'WiFi-Rx':
        data_key1 = load_data['deviceId'] + '_' + 'csi'
        data_key2 = load_data['deviceId'] + '_' + 'plcr'
        if data_key1 not in data_slice:
            data_slice[data_key1] = [1]
            data_slice[data_key1].clear()
        if data_key2 not in data_slice:
            data_slice[data_key2] = [1]
            data_slice[data_key2].clear()


# topic:'/client/{deviceType}/{deviceId}/offline
def res_offline(client, userdata, msg):
    # 收到单个设备的下线信息，更新设备列表
    load_data = json.loads(msg.payload)['data']
    # # 收到报文，存在message就打印一下
    # if 'message' in load_data:
    #     print('message: {0}'.format(load_data['message']))
    msg_topic = msg.topic
    [result, index] = find_device(load_data['deviceId'])
    device_list[index]['stat'] = 'off'


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
    topic_split = msg.topic.split('/')
    devId = topic_split[3]
    [result, index] = find_device(devId)
    deviceInform = device_list[index]
    if deviceInform['stat'] == 'working':
        print('{0} restart sampling!'.format(deviceInform['deviceId']))
    if deviceInform['stat'] == 'on':
        device_list[index]['stat'] = 'working'
        print('{0} start sampling!'.format(deviceInform['deviceId']))


def res_showdata(client, userdata, msg):
    # 把接收数据存在一个地方供前端取
    topic_split = msg.topic.split('/')
    devId = topic_split[3]
    data_type = topic_split[5]
    data = np.array([])
    # 获取设备信息
    [result, index] = find_device(devId)
    deviceInform = device_list[index]
    data_key = deviceInform['deviceId'] + '_' + data_type
    # 对wav数据和csi数据分别做不同的处理
    if data_type == 'wav':
        data = np.fromstring(msg.payload, dtype=np.int16)
    elif data_type == 'csi':
        # csi用c语言publish过来，在格式转换上不如python流畅，以下是多次试验后的结果
        pyload_to_str = msg.payload.decode('utf-8')[1:-1]
        str_to_list = pyload_to_str.split(',')
        data_total = np.array(str_to_list, dtype=np.float64)
        # 简单处理，取第一个子载波
        # # 最后一个包只有一个数据，单独处理
        # if data_total.size != 180:
        #     return
        data = np.array([math.sqrt(data_total[0] * data_total[0] + data_total[1] * data_total[1])])
    elif data_type == 'plcr':
        pyload_to_str = msg.payload.decode('utf-8')[1:-1]
        str_to_list = pyload_to_str.split(',')
        data = np.array(str_to_list, dtype=np.float64)
        print(data)
    # 创建数据缓存队列
    # 转移指设备上线即创建缓存队列
    # if data_key not in data_slice:
    #     data_slice[data_key] = []
    # 添加数据
    data_slice[data_key].extend(data.tolist())


def res_stop(client, userdata, msg):
    topic_split = msg.topic.split('/')
    devId = topic_split[3]
    # 目前只有wav
    [result, index] = find_device(devId)
    deviceInform = device_list[index]
    deviceInform['stat'] = 'on'
    if deviceInform['devType'] == 'Speaker':
        data_slice[devId + '_wav'].clear()
    elif deviceInform['devType'] == 'WiFi-Rx':
        data_slice[devId + '_plcr'].clear()
        data_slice[devId + '_csi'].clear()


# 无匹配的topic
def res_default(client, userdata, msg):
    print("default res_function!")
    load_data = json.loads(msg.payload)
    # # 收到报文，存在message就打印一下
    # if 'message' in load_data:
    #     print('message: {0}'.format(load_data['message']))
    msg_topic = msg.topic
    if msg_topic.endswith('/start'):
        res_start(client, userdata, msg)
    if msg_topic.endswith('/stop'):
        res_stop(client, userdata, msg)
    if msg_topic.endswith('/showdata/wav') or msg_topic.endswith('/showdata/csi') or msg_topic.endswith('/showdata/plcr'):
        res_showdata(client, userdata, msg)

    # msg_payload = json.loads(msg.payload)
    # if 'message' in msg_payload:
    #     print('message:{0}'.format(msg_payload['message']))


topic_case = {
    '/client/respond/deviceInform': res_inform,
    '/client/online': res_online,
    '/client/offline': res_offline

}
