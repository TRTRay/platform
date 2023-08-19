from flask import Blueprint, request
from backend.mqttServer import MqttServer
from backend.utils.staticData import StaticData
from backend.utils.utils import Utils
from backend.utils.jsonResult import *

devices_bp = Blueprint('devices', __name__)


@devices_bp.route('/api/devices', methods=['GET'])
def get_device_list():
    # GET请求，获取设备列表
    # 直接读取设备列表
    # next：检查设备列表中的设备状态，没有在线设备报warning
    return req_success('SUCCESS', {'list': StaticData.device_list})


@devices_bp.route('/api/devices/update', methods=['POST'])
def device_update():
    # POST请求，更改设备参数
    # pub_topic = '/broker/{devType}/{deviceId}/update, payload = msg,{params}
    req_params = json.loads(request.data)
    [result, index] = Utils.find_device(req_params['deviceId'])
    deviceInform = StaticData.device_list[index]

    pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/' + 'update'
    # next：先检查设备状态，下线设备和正在工作的设备给错误反馈，只有闲置设备可以更改设备状态
    params = req_params['params']
    # 为了方便对wifi设备的参数进行的映射，可以优化
    if deviceInform['devType'] == 'WiFi-Tx' or deviceInform['devType'] == 'WiFi-Rx':
        if params['rx_model'] == ['csi', 'plcr']:
            params['rx_model'] = 'a'
        if params['rx_model'] == ['plcr']:
            params['rx_model'] = 'p'
        if params['rx_model'] == ['csi']:
            params['rx_model'] = 'c'
    load = json.dumps({
        'timestamp': Utils.get_timestamp(),
        'message': 'Broker request for changing device params',
        'data': params
    })
    MqttServer.publish(pub_topic, load)
    # next0818:这部分可以删掉，设备重新上线后会自动更新参数
    # 暂时在本地更改
    deviceInform['params'] = params
    # next0818：不需要关注结果，不要设备信息
    return req_success('SUCCESS', deviceInform)


@devices_bp.route('/api/devices/reboot', methods=['POST'])
def device_reboot():
    # POST请求，重启设备
    # pub_topic = '/broker/{devType}/{deviceId}/reboot, payload = msg
    req_params = json.loads(request.data)
    [result, index] = Utils.find_device(req_params['deviceId'])
    deviceInform = StaticData.device_list[index]

    pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/' + 'reboot'
    load = json.dumps({
        'timestamp': Utils.get_timestamp(),
        'message': 'Broker request for rebooting',
        'data': []
    })
    MqttServer.publish(pub_topic, load)
    # next0818：不需要关注结果，不要设备信息
    return req_success('SUCCESS', deviceInform)
