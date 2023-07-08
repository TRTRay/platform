import json
import copy
import math

import numpy as np
from flask import Blueprint, request
from backend.mqttServer import client
from backend.config import *
from backend.utils.utils import *
from backend.utils.jsonResult import *

datas_bp = Blueprint('datas', __name__)


# 回显实时数据
@datas_bp.route('/api/datas/start', methods=['GET', 'POST'])
def start_sample():
    # topic = '/broker/{devType}/{deviceId}/start, payload = None
    print(request.data)
    req_params = json.loads(request.data)
    [result, index] = find_device(req_params['deviceId'])
    deviceInform = device_list[index]

    # 每次调用都要清空缓存
    # data_slice.clear()
    data_key = deviceInform['deviceId'] + '_' + 'wav'
    if data_key in data_slice:
        data_slice[data_key].clear()
    pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/start'
    load = json.dumps({
        'timestamp': get_timestamp(),
        'message': 'Broker request for data',
        'data': []
    })
    client.publish(pub_topic, payload=load)
    # broker通过start和stop接口来控制设备采样与否，用showdata接口来获取数据
    return req_success('SUCCESS', '')


@datas_bp.route('/api/datas/showdata', methods=['GET', 'POST'])
def show_data():
    req_params = json.loads(request.data)
    [result, index] = find_device(req_params['deviceId'])
    deviceInform = device_list[index]

    # 实际上不需要设备知道前端读走了数据，设备只管发就行
    # 保留topic
    pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/showdata'
    recorderChannels = deviceInform['params']['recorderChannals']
    # 一秒25帧
    seg_len = int(deviceInform['params']['sampleRate'] / 25)
    # wifi remain!!!!!!!!
    data_key = deviceInform['deviceId'] + '_' + 'wav'
    run_data_len = math.floor(len(data_slice[data_key]) / seg_len / recorderChannels) * seg_len * recorderChannels
    # 取出数据
    # runtime_list = copy.copy(data_slice[data_key])
    # data_slice[data_key].clear()
    runtime_list = copy.copy(data_slice[data_key][0:run_data_len])
    del data_slice[data_key][0:run_data_len]
    # 简单处理
    # np_list = np.array(runtime_list)
    # runtime_data = np_list.reshape(-1, recorderChannels).T
    np_list = np.abs(np.array(runtime_list))
    runtime_data = np_list.reshape(-1, recorderChannels).T
    result_list = []
    for channel in runtime_data:
        re_channel = channel.reshape(-1, seg_len)
        result_list.append(np.round(np.mean(np.abs(re_channel), axis=1)))
    # inform = {'runtime_data': runtime_data.tolist()}
    # return req_success('SUCCESS', inform)
    inform = {'runtime_data': np.array(result_list).tolist()}
    return req_success('SUCCESS', inform)


@datas_bp.route('/api/datas/stop', methods=['GET', 'POST'])
def stop_sample():
    # topic = '/broker/{devType}/{deviceId}/stop, payload = None
    print(request.data)
    req_params = json.loads(request.data)
    [result, index] = find_device(req_params['deviceId'])
    deviceInform = device_list[index]

    pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/stop'
    load = json.dumps({
        'timestamp': get_timestamp(),
        'message': 'Broker request for stop',
        'data': []
    })
    client.publish(pub_topic, payload=load)
    return req_success('SUCCESS', '')
