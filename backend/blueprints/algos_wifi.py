import copy
import os
import base64

from flask import Blueprint, request
import scipy.io as sio

from backend.algos.breath import breathe, plot_and_save_pic
from backend.algos.classify import classify
from backend.utils.staticData import StaticData
from backend.utils.utils import Utils
from backend.utils.jsonResult import *

algos_wifi_bp = Blueprint('algos_wifi', __name__)


@algos_wifi_bp.route('/api/algos/wifi/datalist', methods=['GET'])
def get_filelist():
    # wifi datas
    dir_path = os.path.join(Utils.get_proj_path(), 'static', 'datas', 'wifi')
    return req_success('SUCCESS', Utils.filelist_in_dir(dir_path))


@algos_wifi_bp.route('/api/algos/wifi/breath', methods=['GET', 'POST'])
def detect_breath():
    req_params = json.loads(request.data)
    filename = req_params['filename']
    filepath = os.path.join(Utils.get_proj_path(), 'static', 'datas', 'wifi', filename)

    mat_data = sio.loadmat(filepath)
    csi = mat_data['csi']
    respiration_rate, auto_shifted, filtbreath = breathe(csi)
    data_name, data_ext = os.path.splitext(os.path.basename(filepath))
    save_path = os.path.join(Utils.get_proj_path(), 'static', 'results', 'wifi', data_name)
    plot_and_save_pic("结果图", filtbreath, 2530 - 1, 2530 + auto_shifted, 'Breath',
                      'Breath_Wave(Filtered Respiration Waveform)', 'Time', 'Amplitude', save_path)
    re_content = {
        'breath_rate': respiration_rate,
        'breath_wave': None
    }
    with open(save_path + '.png', 'rb') as f:
        image = f.read()
        re_content['breath_wave'] = base64.b64encode(image).decode('utf-8')

    return req_success('SUCCESS', re_content)


@algos_wifi_bp.route('/api/algos/wifi/breath/realtime', methods=['GET', 'POST'])
def detect_breath_realtime():
    req_params = json.loads(request.data)

    data_key = req_params['deviceId'] + '_' + 'csi'
    runtime_list_csi = copy.copy(StaticData.csi_for_breath[data_key])
    runtime_list_plcr = copy.copy(StaticData.data_slice[req_params['deviceId'] + '_' + 'plcr'])
    StaticData.csi_for_breath[data_key].clear()
    csi_view = copy.copy(StaticData.data_slice[data_key])
    StaticData.data_slice[data_key].clear()
    inform = {
        'runtime_data_csi': [],
        'runtime_data_plcr': [],
        'filtbreath': [],
        'respiration_rate': 0
    }

    csi = Utils.csi_reshape(runtime_list_csi)
    if csi.size == 0:
        print(csi.size)
        return req_success('SUCCESS', inform)
    respiration_rate, auto_shifted, filtbreath = breathe(csi)
    inform = {
        'runtime_data_csi': csi_view,
        'runtime_data_plcr': runtime_list_plcr,
        'filtbreath': filtbreath.tolist()[2530 - 1: 2530 + auto_shifted],
        'respiration_rate': respiration_rate
    }
    # save_path = os.path.join(Utils.get_proj_path(), 'static', 'results', 'wifi', 'real_test')
    # plot_and_save_pic("结果图", filtbreath, 2530 - 1, 2530 + auto_shifted, 'Breath',
    #                   'Breath_Wave(Filtered Respiration Waveform)', 'Time', 'Amplitude', save_path)
    return req_success('SUCCESS', inform)


@algos_wifi_bp.route('/api/algos/wifi/feature', methods=['GET'])
def classify_feature():
    req_params = json.loads(request.data)
    filename = req_params['filename']
    filepath = os.path.join(Utils.get_proj_path(), 'static', 'datas', 'wifi', filename)

    mat_data = sio.loadmat(filepath)
    # 后续需要提醒他们统一一下命名格式
    csi = mat_data['get_csi']
    # 统一格式如下
    # csi = mat_data['csi']

    # 返回结果是一个一维数组记录了动作的类别
    motion = classify(csi)
    inform = {
        'motion': motion.tolist()
    }
    return req_success('SUCCESS', inform)
