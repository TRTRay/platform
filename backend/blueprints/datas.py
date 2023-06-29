import json
import threading

from flask import Blueprint, request
from backend.mqttServer import client
from backend.config import *
from backend.utils.utils import *

datas_bp = Blueprint('datas', __name__)


# 回显实时数据
@datas_bp.route('/api/datas')
def show_data():
    # topic = '/broker/{devType}/{deviceId}/showdata, payload = None
    req_params = json.loads(request.data)
    [result, index] = find_device(req_params['deviceId'])
    deviceInform = device_list[index]

    pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/showdata'
    load = json.dumps({
        'timestamp': get_timestamp(),
        'message': 'Broker request for data',
        'data': []
    })
    client.publish(pub_topic, payload=load)
    # 发送报文通知端设备向服务器传输，如果端设备在一段时间内没有收到该publish就停止发送，停止发送的时候向服务器发一个特殊报文来清空数据队列(还没完成)
    # 实际情况应该是：在这个页面下前端每秒请求一次数据，后端将队列中的数据取出，然后清空队列
    # 这个地方为了保证操作的原子性，不知道在48000的采样率下会不会出现失真
    with lock:
        runtime_data = data_slice
        print(runtime_data)
        data_slice.clear()
    return json.dumps({'data': runtime_data})


lock = threading.Lock()
