import json

from flask import Blueprint, request
from backend.mqttServer import client, device_list
from backend.config import *
from backend.utils.utils import *
from backend.utils.jsonResult import *

map_bp = Blueprint('map', __name__)


# 添加、删除设备、生成地图，对应有一个算法
@map_bp.route('/api/map', methods=['GET'])
def map_ctrl():
    # 生成设备分布图，需要搭配感知算法，用端设备上传的数据计算出位置
    # topic = '/broker/request/map', payload = ''
    if request.method == 'GET':
        pass


# 接口变更，添加和删除操作拆开
@map_bp.route('/api/map/add', methods=['POST'])
def map_add_device():
    # 在地图上添加设备
    # topic = '/broker/{devType}/{deviceId}/add, payload = {position}
    req_params = json.loads(request.data)
    [result, index] = find_device(req_params['deviceId'])
    # # next version: 是不会出现的错误，检索一个没有加入列表的设备id
    # if not result:
    #     msg = 'Refuse: No matched device has been found!'
    #     return req_bad_request('Unauthorized', msg)
    deviceInform = device_list[index]
    # broker端更改设备位置
    deviceInform['position'] = req_params['position']
    # 预留操作，设备暂时不需要知道自己的位置
    pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/add'
    client.publish(pub_topic, payload=json.dumps({'position': req_params['position']}))
    # 一个假的Response
    return req_success('SUCCESS', deviceInform)
    # # final replace
    # return req_success('SUCCESS', '')


@map_bp.route('/api/map/delete', methods=['POST'])
def map_delete_device():
    # 在地图上删除设备
    # topic = '/broker/{devType}/{deviceId}/delete, payload = ''
    req_params = json.loads(request.data)
    [result, index] = find_device(req_params['deviceId'])
    # # next version: 是不会出现的错误，检索一个没有加入列表的设备id
    # if not result:
    #     msg = 'Refuse: No matched device has been found!'
    #     return req_bad_request('Unauthorized', msg)
    deviceInform = device_list[index]
    # broker端更改设备位置
    deviceInform['position'] = []
    # 预留操作，设备暂时不需要知道自己的位置
    pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/delete'
    client.publish(pub_topic, payload='')
    # 一个假的Response
    return req_success('SUCCESS', deviceInform)
    # # final replace
    # return req_success('SUCCESS', '')
