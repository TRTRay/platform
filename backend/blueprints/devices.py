import json
import time

from flask import Flask, Blueprint, request
from backend.mqttServer import topic, device_list
from backend.mqttServer import client

devices_bp = Blueprint('devices', __name__)


@devices_bp.route('/api/devices', methods=['GET', 'POST'])
def device_ctl():
    # GET请求，获取设备列表
    if request.method == 'GET':
        # 先清空设备列表
        device_list.clear()
        # broker发布特殊主题的报文，由端设备做出回应，系统根据回应制作设备列表
        client.publish(topic + '/request/deviceInform', payload='')
        # 端设备给予回应，回调函数将设备信息处理好推进device_list中
        time.sleep(3)
        # print('list fetch')
        # print(device_list)
        return json.dumps(device_list)

    # POST请求，更改设备参数
    else:
        param = request.data
        # json形式的，验证一下参数是否合理


@devices_bp.route('/api/devices/test2', methods=['GET', 'POST'])
def test2():
    return '<p>Hello! This is test2 for /devices.</p>'
