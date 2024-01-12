from ctypes import resize
from flask import Blueprint, request
from backend.mqttServer import MqttServer
from backend.utils.staticData import StaticData
from backend.utils.utils import Utils
from backend.utils.jsonResult import req_failed, req_success
from backend.log import logger

import time
import json

map_bp = Blueprint("map", __name__)

# @map_bp.route('/api/map/config', method=['GET'])
# def map_init():
#     # 初始化机器人
#     # 机器人上线前自带初始化，这个是手动接口
#     # topic = '/broker/{devType}/{deviceId}/config, payload = message
#     req_params = json.loads(request.data)
#     [result, index] = Utils.find_device(req_params['deviceId'])
#     deviceInform = StaticData.device_list[index]
#     if deviceInform['stat'] != 'waiting':
#         StaticData.device_list[index]['stat'] = 'waiting'
#     pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/config'
#     load = json.dumps({
#         'message': 'Broker request for init.'
#     })
#     client.publish(pub_topic, payload=load)
#     # 计时，等待StaticData.device_list中设备状态变化，否则返回超时
#     start_time = time.time()
#     while time.time() - start_time < 10:
#         if StaticData.device_list[index]['param'] == 'on':
#             return req_success('SUCCESS', StaticData.device_list[index])
#     return req_failed('Timeout', '')
#


@map_bp.route("/api/map/bye", methods=["GET"])
def map_bye():
    # 开启gmapping建图
    req_params = json.loads(request.data)
    [_, index] = Utils.find_device(req_params["deviceId"])
    deviceInform = StaticData.device_list[index]
    if deviceInform["stat"] != "on":
        # 设备状态不对
        print("Robot is not ready")
        return req_success("Timeout", "")

    pub_topic = (
        "/broker"
        + "/"
        + deviceInform["devType"]
        + "/"
        + deviceInform["deviceId"]
        + "/bye"
    )
    load = json.dumps({"message": "Broker request for gmapping"})
    MqttServer.publish(pub_topic, payload=load)
    logger.info(pub_topic)

    return req_success("SUCCESS", "")


@map_bp.route("/api/map/start", methods=["GET"])
def map_start():
    req_params = json.loads(request.data)
    [_, index] = Utils.find_device(req_params["deviceId"])
    deviceInform = StaticData.device_list[index]
    if deviceInform["stat"] != "on":
        # 设备状态不对
        print("Robot is not ready")
        return req_success("Timeout", "")

    pub_topic = (
        "/broker"
        + "/"
        + deviceInform["devType"]
        + "/"
        + deviceInform["deviceId"]
        + "/map"
        + "/start"
    )
    load = json.dumps({"message": "Broker request for gmapping"})
    MqttServer.publish(pub_topic, payload=load)

    # 计时，等待devicelist中设备状态变化，否则返回超时
    start_time = time.time()
    while time.time() - start_time < 10:
        if StaticData.device_list[index]["stat"] == "working":
            return req_success("SUCCESS", StaticData.device_list[index])
    return req_success("Timeout", "")


@map_bp.route("/api/map/image", methods=["GET"])
def fetch_image():
    req_params = json.loads(request.data)
    [_, index] = Utils.find_device(req_params["deviceId"])
    deviceInform = StaticData.device_list[index]
    pub_topic = (
        "/broker"
        + "/"
        + deviceInform["devType"]
        + "/"
        + deviceInform["deviceId"]
        + "/map"
        + "/fetch"
    )
    load = json.dumps({"message": "Fetch Image"})
    MqttServer.publish(pub_topic, payload=load)

    # TODO: Fetch Image from "broker/$DeviceType/$DeviceId/map/png"
    return req_success("SUCCESS", StaticData.device_list[index])


#
#
# @map_bp.route('/api/map/stop', method=['GET'])
# def map_init():
#     # 停止gmapping建图
#     req_params = json.loads(request.data)
#     [result, index] = Utils.find_device(req_params['deviceId'])
#     deviceInform = StaticData.device_list[index]
#     # 应该不会触发
#     if deviceInform['stat'] != 'working':
#         # 设备状态不对
#         return req_failed('WrongStat', '')
#     pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/stop'
#     load = json.dumps({
#         'message': 'Broker request for stop.'
#     })
#     MqttServer.publish(pub_topic, payload=load)
#     start_time = time.time()
#     while time.time() - start_time < 10:
#         if StaticData.device_list[index]['param'] == 'on':
#             return req_success('SUCCESS', StaticData.device_list[index])
#     return req_failed('Timeout', '')
#
#
# @map_bp.route('/api/map/showmap', method=['GET'])
# def map_init():
#     # 请求slam地图
#     req_params = json.loads(request.data)
#     [result, index] = Utils.find_device(req_params['deviceId'])
#     deviceInform = StaticData.device_list[index]
#     # 应该不会触发
#     if deviceInform['stat'] != 'mapping':
#         # 设备状态不对
#         return req_failed('WrongStat')
#     pub_topic = '/broker/' + deviceInform['devType'] + deviceInform['deviceId'] + '/showmap'
#     load = json.dumps({
#         'message': 'Broker request for map.'
#     })
#     MqttServer.publish(pub_topic, payload=load)
#     # 从数据队列中取出地图并返回
#     time.sleep(0.5)
#     png_data = copy.copy(StaticData.robot_buff[0])
#     StaticData.robot_buff.clear()
#     inform = {
#         "png": png_data
#     }
#     req_success('SUCCESS', inform)
#
#
# # 添加、删除设备、生成地图，对应有一个算法
# @map_bp.route('/api/map/generate', methods=['GET'])
# def map_ctrl():
#     # 生成设备分布图，需要搭配感知算法，用端设备上传的数据计算出位置
#     # topic = '/broker/request/map', payload = ''
#     if request.method == 'GET':
#         pass
#
#
# # 接口变更，添加和删除操作拆开
# @map_bp.route('/api/map/add', methods=['POST'])
# def map_add_device():
#     # 在地图上添加设备
#     # topic = '/broker/{devType}/{deviceId}/add, payload = {position}
#     req_params = json.loads(request.data)
#     [result, index] = Utils.find_device(req_params['deviceId'])
#     # # next version: 是不会出现的错误，检索一个没有加入列表的设备id
#     # if not result:
#     #     msg = 'Refuse: No matched device has been found!'
#     #     return req_bad_request('Unauthorized', msg)
#     deviceInform = StaticData.device_list[index]
#     # broker端更改设备位置
#     deviceInform['position'] = req_params['position']
#     # 预留操作，设备暂时不需要知道自己的位置
#     pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/add'
#     client.publish(pub_topic, payload=json.dumps({'position': req_params['position']}))
#     # 一个假的Response
#     return req_success('SUCCESS', deviceInform)
#     # # final replace
#     # return req_success('SUCCESS', '')
#
#
# @map_bp.route('/api/map/delete', methods=['POST'])
# def map_delete_device():
#     # 在地图上删除设备
#     # topic = '/broker/{devType}/{deviceId}/delete, payload = ''
#     req_params = json.loads(request.data)
#     [result, index] = Utils.find_device(req_params['deviceId'])
#     # # next version: 是不会出现的错误，检索一个没有加入列表的设备id
#     # if not result:
#     #     msg = 'Refuse: No matched device has been found!'
#     #     return req_bad_request('Unauthorized', msg)
#     deviceInform = StaticData.device_list[index]
#     # broker端更改设备位置
#     deviceInform['position'] = []
#     # 预留操作，设备暂时不需要知道自己的位置
#     pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/delete'
#     client.publish(pub_topic, payload='')
#     # 一个假的Response
#     return req_success('SUCCESS', deviceInform)
#     # # final replace
#     # return req_success('SUCCESS', '')
