# on_message中对各个topic的响应函数
import json
import math
import cv2
import numpy as np
from backend.utils.utils import Utils
from backend.utils.staticData import StaticData


# topic:'/client/{deviceType}/{deviceId}/online
def res_online(client, userdata, msg):
    # 收到单个设备传来的上线信息，更新列表
    payload = json.loads(msg.payload)
    # wifi设备、robot在尝试完成初始化
    if 'data' not in payload:
        print('Device is trying to setup.')
        return
    load_data = payload['data']
    [result, index] = Utils.find_device(load_data['deviceId'])
    if result:
        StaticData.device_list[index]['stat'] = "on"
    else:
        # 将WiFi设备的工作参数进行简单映射，可以优化
        if load_data['devType'] == 'WiFi-Tx' or load_data['devType'] == 'WiFi-Rx':
            if load_data['params']['rx_model'] == 'a':
                load_data['params']['rx_model'] = ['csi', 'plcr']
            if load_data['params']['rx_model'] == 'p':
                load_data['params']['rx_model'] = ['plcr']
            if load_data['params']['rx_model'] == 'c':
                load_data['params']['rx_model'] = ['csi']
        StaticData.device_list.append(load_data)
    print(StaticData.device_list)
    # 创建数据缓存
    StaticData.empty_data_queue(load_data)


# topic:'/client/{deviceType}/{deviceId}/offline
def res_offline(client, userdata, msg):
    # 收到单个设备的下线信息，更新设备列表
    load_data = json.loads(msg.payload)['data']
    [result, index] = Utils.find_device(load_data['deviceId'])
    if result:
        StaticData.device_list[index]['stat'] = 'off'


# topic:'/client/{devType}/{deviceId}/start'
def res_start(client, userdata, msg):
    # 收到设备对start报文的回应
    topic_split = msg.topic.split('/')
    devId = topic_split[3]
    [result, index] = Utils.find_device(devId)
    deviceInform = StaticData.device_list[index]
    # 更改设备的工作状态
    # if deviceInform['stat'] == 'working':
    #     print('{0} restart sampling!'.format(deviceInform['deviceId']))
    if deviceInform['stat'] == 'on':
        StaticData.device_list[index]['stat'] = 'working'
        print('{0} start sampling!'.format(deviceInform['deviceId']))


def res_showdata(client, userdata, msg):
    # 设备在收到start报文后使用该信道传输数据
    # 把接收数据存在一个地方供前端取
    topic_split = msg.topic.split('/')
    devId = topic_split[3]
    data_type = topic_split[5]
    data = np.array([])
    # 获取设备信息
    [result, index] = Utils.find_device(devId)
    deviceInform = StaticData.device_list[index]
    data_key = deviceInform['deviceId'] + '_' + data_type
    # 对wav数据和csi数据分别做不同的处理
    if data_type == 'wav':
        StaticData.audio_buff[data_key] += msg.payload
        data = np.fromstring(msg.payload, dtype=np.int16)
    elif data_type == 'csi':
        # csi用c语言publish过来，在格式转换上不如python流畅，以下是多次试验后的结果
        pyload_to_str = msg.payload.decode('utf-8')[1:-1]
        str_to_list = pyload_to_str.split(',')
        data_total = np.array(str_to_list, dtype=np.float64)
        StaticData.csi_buff[data_key].append(data_total.tolist())
        # 简单处理，取第一个子载波
        data = np.array([math.sqrt(data_total[0] * data_total[0] + data_total[1] * data_total[1])])
    elif data_type == 'plcr':
        pyload_to_str = msg.payload.decode('utf-8')[1:-1]
        str_to_list = pyload_to_str.split(',')
        data = np.array(str_to_list, dtype=np.float64)
        StaticData.plcr_buff[data_key].append(data)
    elif data_type == 'png':
        # 只做存储，没做别的
        img_b = np.frombuffer(msg.payload, np.uint8)
        StaticData.camera_buff.append(img_b)
        # cv2.imshow(msg.topic, )
        # if cv2.waitKey(100) == 27:
        #     exit()
        pass
    # 添加数据
    # 对camera不适用，所以不要使用camera的data_slice
    StaticData.data_slice[data_key].extend(data.tolist())


def res_stop(client, userdata, msg):
    # 设备接收到停止工作的请求
    topic_split = msg.topic.split('/')
    devId = topic_split[3]
    [result, index] = Utils.find_device(devId)
    deviceInform = StaticData.device_list[index]
    deviceInform['stat'] = 'on'
    # 不做处理也可以
    if deviceInform['devType'] == 'Speaker':
        StaticData.data_slice[devId + '_wav'].clear()
    elif deviceInform['devType'] == 'WiFi-Rx':
        StaticData.data_slice[devId + '_plcr'].clear()
        StaticData.data_slice[devId + '_csi'].clear()
    elif deviceInform['devType'] == 'Camera':
        Utils.save_as_video(deviceInform)


def res_download(client, userdata, msg):

    return


def res_update(client, userdata, msg):
    topic_split = msg.topic.split('/')
    devId = topic_split[3]
    [result, index] = Utils.find_device(devId)
    deviceInform = StaticData.device_list[index]

    load_data = json.loads(msg.payload)['params']
    if deviceInform['devType'].startswith('WiFi'):
        if load_data['rx_model'] == 'a':
            load_data['rx_model'] = ['csi', 'plcr']
        if load_data['rx_model'] == 'p':
            load_data['rx_model'] = ['plcr']
        if load_data['rx_model'] == 'c':
            load_data['rx_model'] = ['csi']
    deviceInform['params'] = load_data


res_dict = {
    'online': res_online,
    'offline': res_offline,
    'update': res_update,
    'start': res_start,
    'stop': res_stop,
    'download': res_download,
    'csi': res_showdata,
    'plcr': res_showdata,
    'wav': res_showdata,
    'png': res_showdata
}


def res_case(client, userdata, msg):
    msg_topic = msg.topic
    topic_split = msg_topic.split('/')
    ends = topic_split[-1]
    if ends in res_dict:
        res_function = res_dict[ends]
        res_function(client, userdata, msg)
    else:
        print('No matched funtion!')

