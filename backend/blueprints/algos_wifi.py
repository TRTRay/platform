import copy
import os
import base64

from flask import Blueprint, request
import scipy.io as sio

from backend.algos.breath import breathe, plot_and_save_pic
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

    csi = Utils.csi_reshape(runtime_list_csi)
    respiration_rate, auto_shifted, filtbreath = breathe(csi)
    inform = {
        'runtime_data_csi': runtime_list_csi,
        'runtime_data_plcr': runtime_list_plcr,
        'filtbreath': filtbreath.tolist(),
        'respiration_rate': respiration_rate
    }
    # save_path = os.path.join(Utils.get_proj_path(), 'static', 'results', 'wifi', 'real_test')
    # plot_and_save_pic("结果图", filtbreath, 2530 - 1, 2530 + auto_shifted, 'Breath',
    #                   'Breath_Wave(Filtered Respiration Waveform)', 'Time', 'Amplitude', save_path)
    return req_success('SUCCESS', inform)


@algos_wifi_bp.route('/api/algos/wifi/feature', methods=['GET'])
def classify_feature():
    return req_success('SUCCESS', '')
