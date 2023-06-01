import json

from flask import Blueprint, request
from backend.mqttServer import client, topic, device_list, data_for_show

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

    pub_topic = topic + '/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/showdata'
    client.publish(pub_topic, payload='')
    # 做一个假的response
    return json.dumps(data_for_show.pop(0))
