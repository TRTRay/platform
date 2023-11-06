import os
import base64

from flask import Blueprint, request
import scipy.io as sio

from backend.algos.breath import breathe, plot_and_save_pic
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
    filepath = req_params['filepath']

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


@algos_wifi_bp.route('/api/algos/wifi/feature', methods=['GET'])
def classify_feature():
    return req_success('SUCCESS', '')
