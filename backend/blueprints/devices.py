import json
import time

from flask import Blueprint, request
from backend.mqttServer import client, topic, device_list

devices_bp = Blueprint('devices', __name__)


@devices_bp.route('/api/devices', methods=['GET', 'POST'])
def device_ctl():
    # GET请求，获取设备列表
    # topic = '/broker/request/deviceInform', payload = ''
    if request.method == 'GET':
        # 先清空设备列表
        device_list.clear()
        # broker发布特殊主题的报文，由端设备做出回应，系统根据回应制作设备列表
        client.publish(topic + '/request/deviceInform', payload='')
        # 端设备给予回应，回调函数将设备信息处理好推进device_list中
        # 经测试，20个设备，1s绰绰有余
        time.sleep(1)
        # print('list fetch')
        # print(device_list)
        return json.dumps({'list': device_list})

    # POST请求，更改设备参数或者重启
    # topic = '/broker/{operation}/{deviceId}, payload = {param} or None
    else:
        temp = json.loads(request.data)
        # 这一步查找可以由前端来完成
        deviceInform = []
        for device in device_list:
            if device['deviceId'] == temp['deviceId']:
                deviceInform = device
                break

        pub_topic = topic + '/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/' + temp['operation']
        client.publish(pub_topic, payload=temp['param'])
        # 发送出去后自动刷新设备列表，重启的设备会断连，更改参数的设备会回应当前的工作参数，这样就不用进行错误处理
        # 做一个假的response
        deviceInform['param'] = temp['param']
        return json.dumps(deviceInform)
        # 在这一阶段都假设操作可靠，即一定能够执行成功，如果要验证可靠性的话，应该维护不同的消息队列，监测对应的消息队列来确定是否更改成功
        # json形式的，参数验证应该交给前端
