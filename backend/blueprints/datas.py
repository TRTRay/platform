import json
import copy

from flask import Blueprint, request
from backend.mqttServer import client
from backend.config import *
from backend.utils.utils import *
from backend.utils.jsonResult import *

datas_bp = Blueprint('datas', __name__)


# 回显实时数据
@datas_bp.route('/api/datas/start', methods=['GET'])
def start_sample():
    # topic = '/broker/{devType}/{deviceId}/start, payload = None
    req_params = json.loads(request.data)
    [result, index] = find_device(req_params['deviceId'])
    deviceInform = device_list[index]

    # 每次调用都要清空缓存
    data_slice.clear()
    pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/start'
    load = json.dumps({
        'timestamp': get_timestamp(),
        'message': 'Broker request for data',
        'data': []
    })
    client.publish(pub_topic, payload=load)
    # broker通过start和stop接口来控制设备采样与否，用showdata接口来获取数据
    return req_success('SUCCESS', '')


@datas_bp.route('/api/datas/showdata', methods=['GET'])
def show_data():
    req_params = json.loads(request.data)
    [result, index] = find_device(req_params['deviceId'])
    deviceInform = device_list[index]

    # 实际上不需要设备知道前端读走了数据，设备只管发就行
    # 保留topic
    pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/showdata'
    # 从缓存中读取数据并清空
    runtime_data = copy.copy(data_slice)
    inform = {'runtime_data': runtime_data}
    data_slice.clear()
    return req_success('SUCCESS', inform)


@datas_bp.route('/api/datas/stop', methods=['GET'])
def stop_sample():
    # topic = '/broker/{devType}/{deviceId}/stop, payload = None
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
