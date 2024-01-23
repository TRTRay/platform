import copy
import os
import base64

from flask import Blueprint, request
import scipy.io as sio

from backend.algos.breath import breathe, plot_and_save_pic
from backend.algos.nneTracking import make_input, nne
from backend.algos.classify import classify
from backend.utils.staticData import StaticData
from backend.utils.utils import Utils
from backend.utils.jsonResult import *

algos_wifi_bp = Blueprint('algos_wifi', __name__)


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
    inform = {
        'runtime_data_csi': [],
        'runtime_data_plcr': [],
        'filtbreath': [],
        'respiration_rate': 0,
        'PAR_value': []
    }
    if len(StaticData.csi_for_breath[data_key]) < StaticData.win_len_for_breath:
        return req_success('SUCCESS', inform)

    runtime_list_csi = copy.copy(StaticData.csi_for_breath[data_key][-1000:])
    runtime_list_plcr = copy.copy(StaticData.data_slice[req_params['deviceId'] + '_' + 'plcr'])
    # 现在需要保存之前的数据作为下一个窗的一部分，所以别清掉了
    # StaticData.csi_for_breath[data_key].clear()
    # 用来可视化的数据队列
    csi_view = copy.copy(StaticData.data_slice[data_key])
    StaticData.data_slice[data_key].clear()

    csi = Utils.csi_reshape(runtime_list_csi)
    # 感觉不需要，后续再看
    # if csi.size == 0:
    #     return req_success('SUCCESS', inform)

    # 呼吸检测主体
    respiration_rate, auto_shifted, filtbreath, PAR_value = breathe(csi)
    result = filtbreath.tolist()[2530 - 1: 2530 + auto_shifted]
    inform = {
        'runtime_data_csi': csi_view,
        'runtime_data_plcr': runtime_list_plcr,
        'filtbreath': result[-StaticData.step_len_for_breath:],
        'respiration_rate': respiration_rate,
        'PAR_value': PAR_value
    }
    return req_success('SUCCESS', inform)


@algos_wifi_bp.route('/api/algos/wifi/NNE-Tracking', methods=['GET', 'POST'])
def nne_tracking():
    req_params = json.loads(request.data)
    files = req_params['files']
    if len(files) < 2:
        return req_failed('Lack of Input!', '')
    for index in range(0, len(files)):
        filename = files[index]
        files[index] = os.path.join(Utils.get_proj_path(), 'static', 'datas', 'wifi', filename)
    init_pos = req_params['position']

    data_input = make_input(files, init_pos)
    result = nne(data_input)
    return req_success('SUCCESS', result.tolist())


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
