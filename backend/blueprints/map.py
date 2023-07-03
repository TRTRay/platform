import json

from flask import Blueprint, request
from backend.mqttServer import client, device_list
from backend.config import *
from backend.utils.utils import *
from backend.utils.jsonResult import *

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
        req_params = json.loads(request.data)
        [result, index] = find_device(req_params['deviceId'])
        deviceInform = device_list[index]

        # 预留操作，端设备暂时不需要知道自己的位置
        pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/' + req_params['operation']
        client.publish(pub_topic, payload=json.dumps({'position': req_params['position']}))
        # 更改设备位置
        deviceInform['position'] = req_params['position']
        # 做一个假的response
        return req_success('SUCCESS', deviceInform)
