import json

from flask import Blueprint, request
from backend.mqttServer import client, device_list
from backend.config import *

map_bp = Blueprint('map', __name__)


# 添加、删除设备、生成地图，对应有一个算法
@map_bp.route('/api/map', methods=['GET', 'POST'])
def map_ctrl():
    # 生成设备分布图，需要搭配感知算法，用端设备上传的数据计算出位置
    # topic = '/broker/request/map', payload = ''
    if request.method == 'GET':
        pass
    # 添加或删除设备
    # topic = '/broker/{operation}/{devType}/{deviceId}, payload = {position}
    else:
        temp = json.loads(request.data)
        # 这一步查找可以由前端来完成
        deviceInform = []
        for device in device_list:
            if device['deviceId'] == temp['deviceId']:
                deviceInform = device
                break

        pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/' + temp['operation']
        client.publish(pub_topic, payload=temp['position'])
        # 做一个假的response
        deviceInform['position'] = temp['position']
        return json.dumps(deviceInform)
