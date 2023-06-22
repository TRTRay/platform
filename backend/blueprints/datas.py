import json

from flask import Blueprint, request
from backend.mqttServer import client
from backend.config import *

datas_bp = Blueprint('datas', __name__)


# 回显实时数据
@datas_bp.route('/api/datas')
def show_data():
    # topic = '/broker/showdata/{devType}/{deviceId}, payload = None
    temp = json.loads(request.data)
    # 这一步查找可以由前端来完成
    deviceInform = []
    for device in device_list:
        if device['deviceId'] == temp['deviceId']:
            deviceInform = device
            break

    pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/showdata'
    client.publish(pub_topic, payload=json.dumps({'message': 'Broker request for data'}))
    # 发送报文通知端设备向服务器传输，如果端设备在一段时间内没有收到该publish就停止发送，停止发送的时候向服务器发一个特殊报文来清空数据队列
    # 实际情况应该是：在这个页面下前端每秒请求一次数据，后端将队列中的数据取出，然后清空队列
    runtime_data = data_slice
    data_slice.clear()
    return json.dumps(runtime_data)
