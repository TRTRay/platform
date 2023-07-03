import json
import time

from flask import Blueprint, request
from backend.mqttServer import client, device_list
from backend.config import *
from backend.utils.utils import *
from backend.utils.jsonResult import *

devices_bp = Blueprint('devices', __name__)


@devices_bp.route('/api/devices', methods=['GET', 'POST'])
def device_ctl():
    # GET请求，获取设备列表
    # pub_topic = '/broker/request/deviceInform', payload = ''
    if request.method == 'GET':
        # 先清空设备列表
        # if ~test_mode:
        #     device_list.clear()
        # broker发布特殊主题的报文，由端设备做出回应，系统根据回应制作设备列表
        load = json.dumps({
            'timestamp': get_timestamp(),
            'message': 'Broker request for device information',
            'data': []
        })
        client.publish('/broker/request/deviceInform', payload=load)
        # 端设备给予回应，回调函数将设备信息处理好推进device_list中
        # 经测试，20个设备，1s绰绰有余
        time.sleep(0.2)
        return req_success('SUCCESS', device_list)

    # POST请求，更改设备参数或者重启
    # pub_topic = '/broker/{devType}/{deviceId}/update, payload = {params}
    # pub_topic = '/broker/{devType}/{deviceId}/reboot, payload = None
    else:
        req_params = json.loads(request.data)
        [result, index] = find_device(req_params['deviceId'])
        deviceInform = device_list[index]

        operation = req_params['operation']
        pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/' + operation
        if operation == 'update':
            load = json.dumps({
                'timestamp': get_timestamp(),
                'message': 'Broker request for changing device params',
                'data': req_params['params']
            })
            client.publish(pub_topic, payload=load)
            # 本地更改，还有和设备之间的通信
            deviceInform['params'] = req_params['params']
        else:
            load = json.dumps({
                'timestamp': get_timestamp(),
                'message': 'Broker request for rebooting',
                'data': []
            })
            client.publish(pub_topic, payload=load)
        # 发送出去后自动刷新设备列表，重启的设备会断连，更改参数的设备会回应当前的工作参数，这样就不用进行错误处理
        # 做一个假的response
        return req_success('SUCCESS', deviceInform)
        # 在这一阶段都假设操作可靠，即一定能够执行成功，如果要验证可靠性的话，应该维护不同的消息队列，监测对应的消息队列来确定是否更改成功
        # json形式的，参数验证应该交给前端
