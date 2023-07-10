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
    # pub_topic = '/broker/request/deviceInform', payload = msg
    if request.method == 'GET':
        # 不要清空列表：不要删除已经下线设备；理论上设备状态不会发生更新，添加一个异常处理，设备状态不对的报warning
        # # 先清空设备列表
        # device_list.clear()
        # broker发布特殊主题的报文，由端设备做出回应，系统根据回应制作设备列表
        # 事实上不需要发送请求了
        load = json.dumps({
            'timestamp': get_timestamp(),
            'message': 'Broker request for device information',
            'data': []
        })
        client.publish('/broker/request/deviceInform', payload=load)
        # 端设备给予回应，回调函数将设备信息处理好推进device_list中
        # 时间足够
        time.sleep(0.2)
        # # next version:没有设备在线的时候，报warning，检查设备状态
        # flag_online = True
        # for device in device_list:
        #     if device['stat'] == 'on' or device['stat'] == 'working':
        #         flag_online = False
        #         break
        # if flag_online:
        #     msg = 'Warning: There are no online devices!'
        #     return req_success('Warning', device_list, msg)
        return req_success('SUCCESS', {'list': device_list})
    # POST请求，更改设备参数或者重启
    # pub_topic = '/broker/{devType}/{deviceId}/update, payload = msg,{params}
    # pub_topic = '/broker/{devType}/{deviceId}/reboot, payload = msg
    else:
        req_params = json.loads(request.data)
        [result, index] = find_device(req_params['deviceId'])
        deviceInform = device_list[index]

        operation = req_params['operation']
        pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/' + operation
        # # next version: 先检查设备状态
        # if deviceInform['stat'] == 'off':
        #     msg = 'Refuse: Device is not online!'
        #     return req_bad_request('Unauthorized', msg)
        # if deviceInform['stat'] == 'working':
        #     msg = 'Refuse: Device is working, please stop sampling first!'
        #     return req_bad_request('Unauthorized', msg)
        if operation == 'update':
            params = req_params['params']
            if deviceInform['devType'] == 'WiFi-Tx' or deviceInform['devType'] == 'WiFi-Rx':
                if params['rx_model'] == ['csi', 'plcr']:
                    params['rx_model'] = 'a'
                if params['rx_model'] == ['plcr']:
                    params['rx_model'] = 'p'
                if params['rx_model'] == ['csi']:
                    params['rx_model'] = 'c'
            load = json.dumps({
                'timestamp': get_timestamp(),
                'message': 'Broker request for changing device params',
                'data': params
            })
            client.publish(pub_topic, payload=load)
            # next version:这部分可以删掉，设备重新上线后会自动更新参数
            # 本地更改，还有和设备之间的通信
            deviceInform['params'] = params
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
        # # next version:真response，不需要返回设备信息了
        # return req_success('SUCCESS', '')
        # 在这一阶段都假设操作可靠，即一定能够执行成功，如果要验证可靠性的话，应该维护不同的消息队列，监测对应的消息队列来确定是否更改成功
        # json形式的，参数验证应该交给前端
