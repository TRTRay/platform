import copy
import math
import os.path
import time

import numpy as np
from flask import Blueprint, request, send_file
from backend.utils.staticData import StaticData
from backend.mqttServer import MqttServer
from backend.utils.utils import Utils
from backend.utils.jsonResult import *

datas_bp = Blueprint('datas', __name__)


# 回显实时数据
@datas_bp.route('/api/datas/start', methods=['GET', 'POST'])
def start_sample():
    # topic = '/broker/{devType}/{deviceId}/start, payload = None
    req_params = json.loads(request.data)
    [result, index] = Utils.find_device(req_params['deviceId'])
    deviceInform = StaticData.device_list[index]

    # 每次调用清空缓存
    StaticData.empty_data_queue(deviceInform)
    pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/start'
    load = json.dumps({
        'timestamp': Utils.get_timestamp(),
        'message': 'Broker request for data',
        'data': []
    })
    MqttServer.publish(pub_topic, load)
    return req_success('SUCCESS', '')


@datas_bp.route('/api/datas/showdata', methods=['GET', 'POST'])
def show_data():
    req_params = json.loads(request.data)
    [result, index] = Utils.find_device(req_params['deviceId'])
    deviceInform = StaticData.device_list[index]

    # 保留topic
    pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/showdata'
    if deviceInform['devType'] == 'Speaker':
        # 在数据缓存中的检索关键字
        data_key = deviceInform['deviceId'] + '_' + 'wav'
        data_slice = StaticData.data_slice[data_key]
        begin_index = StaticData.begin_index[data_key]
        # 一秒25帧，对声学数据做一个分割，完成预处理，减少前端的数据处理压力
        recorderChannels = deviceInform['params']['recorderChannals']
        seg_len = int(deviceInform['params']['sampleRate'] / 25)
        # 取出部分
        run_data_len = math.floor(len(data_slice[begin_index:]) / seg_len / recorderChannels) * seg_len * recorderChannels
        # 取出数据（防止清空缓存导致临时数据失效要进行拷贝）
        runtime_list = copy.copy(data_slice[begin_index:begin_index + run_data_len])
        StaticData.update_index(deviceInform, begin_index + run_data_len)
        # del StaticData.data_slice[data_key][0:run_data_len]
        # 简单处理（具体处理方法由wyy提供）
        np_list = np.abs(np.array(runtime_list))
        runtime_data = np_list.reshape(-1, recorderChannels).T
        result_list = []
        for channel in runtime_data:
            re_channel = channel.reshape(-1, seg_len)
            result_list.append(np.round(np.mean(np.abs(re_channel), axis=1)))
        # 返回数据
        inform = {'runtime_data': np.array(result_list).tolist()}
        return req_success('SUCCESS', inform)
    elif deviceInform['devType'].startswith('WiFi'):
        # wifi部分没有做数据下载
        # 将csi和plcr队列的数据打包在一起
        # 检索关键字
        data_key_csi = deviceInform['deviceId'] + '_' + 'csi'
        data_key_plcr = deviceInform['deviceId'] + '_' + 'plcr'
        # 已经完成处理，直接取出并清空
        runtime_list_csi = copy.copy(StaticData.data_slice[data_key_csi])
        runtime_list_plcr = copy.copy(StaticData.data_slice[data_key_plcr])
        StaticData.data_slice[data_key_csi].clear()
        StaticData.data_slice[data_key_plcr].clear()
        # 返回数据
        inform = {
            'runtime_data_csi': runtime_list_csi,
            'runtime_data_plcr': runtime_list_plcr
        }
        return req_success('SUCCESS', inform)


@datas_bp.route('/api/datas/stop', methods=['GET', 'POST'])
def stop_sample():
    # 不涉及到wif设备的暂停
    # topic = '/broker/{devType}/{deviceId}/stop, payload = None
    req_params = json.loads(request.data)
    [result, index] = Utils.find_device(req_params['deviceId'])
    deviceInform = StaticData.device_list[index]

    pub_topic = '/broker/' + deviceInform['devType'] + '/' + deviceInform['deviceId'] + '/stop'
    load = json.dumps({
        'timestamp': Utils.get_timestamp(),
        'message': 'Broker request for stop',
        'data': []
    })
    MqttServer.publish(pub_topic, load)
    # 目前只有声学设备
    time.sleep(1)
    Utils.save_data_as_audio(deviceInform)
    return req_success('SUCCESS', '')


@datas_bp.route('/api/datas/download', methods=['GET'])
def download_data():
    # topic = '/broker/{devType}/{deviceId}/download, payload = None
    req_params = json.loads(request.data)
    [result, index] = Utils.find_device(req_params['deviceId'])
    deviceInform = StaticData.device_list[index]

    # 目前只有音频文件
    data_key = deviceInform['deviceId'] + '_' + 'wav'
    current_dir = os.path.dirname(__file__)
    filepath = os.path.join(current_dir, '..', '..', 'static', data_key + '.wav')
    return send_file(filepath, as_attachment=True)
