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

    pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/start'
    load = json.dumps({
        'timestamp': get_timestamp(),
        'message': 'Broker request for data',
        'data': []
    })
    client.publish(pub_topic, payload=load)
    # 发送报文通知端设备向服务器传输，如果端设备在一段时间内没有收到该publish就停止发送，停止发送的时候向服务器发一个特殊报文来清空数据队列(还没完成)
    # 实际情况应该是：在这个页面下前端每秒请求一次数据，后端将队列中的数据取出，然后清空队列
    runtime_data = copy.copy(data_slice)
    inform = {'runtime_data': runtime_data}
    data_slice.clear()
    return req_success('SUCCESS', inform)


# @datas_bp.route('/api/datas/stop', methods=['GET'])
# def stop_sample():
#     # topic = '/broker/{devType}/{deviceId}/stop, payload = None
#     req_params = json.loads(request.data)
#     [result, index] = find_device(req_params['deviceId'])
#     deviceInform = device_list[index]
#
#     pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/stop'
#     load = json.dumps({
#         'timestamp': get_timestamp(),
#         'message': 'Broker request for stop',
#         'data': []
#     })
#     client.publish(pub_topic, payload=load)
#     return req_success('SUCCESS', '')
