import copy
import os
from backend.utils.jsonResult import *

from flask import Blueprint, request, send_file
from backend.utils.staticData import StaticData
from backend.utils.utils import Utils
from backend.mqttServer import MqttServer

temp_bp = Blueprint('temp', __name__)


@temp_bp.route('/api/temp/cv/showdata', methods=['GET', 'POST'])
def get_png():
    req_params = json.loads(request.data)
    deviceId = req_params['deviceId']
    data_key = deviceId + '_' + 'png'
    png_bits = StaticData.png_for_real_camera

    png_data = []
    if png_bits:
        png_data = copy.copy(png_bits)
        png_bits.clear()

    if png_data:
        png_data = png_data[0].tolist()

    inform = {
        'png_bits': png_data
    }
    return req_success('SUCCESS', inform)


@temp_bp.route('/api/temp/cv/datalist', methods=['GET'])
def get_filelist():
    # cv datas
    dir_path = os.path.join(Utils.get_proj_path(), 'static', 'datas', 'vision')
    return req_success('SUCCESS', Utils.filelist_in_dir(dir_path))


@temp_bp.route('/api/temp/cv/download', methods=['GET', 'POST'])
def download_data():
    # 不带路径的文件名
    req_params = json.loads(request.data)
    filename = req_params['filename']

    filepath = os.path.join(Utils.get_proj_path(), 'static', 'datas', 'vision', filename)
    return send_file(filepath, as_attachment=True)
    pass


@temp_bp.route('/api/temp/mmv/showdata', methods=['GET', 'POST'])
def test_mmv():
    req_params = json.loads(request.data)
    [result, index] = Utils.find_device(req_params["deviceId"])
    deviceInform = StaticData.device_list[index]
    # 直接取就行了
    mmv_data = copy.copy(StaticData.mmv_buff)
    StaticData.mmv_buff.clear()

    return req_success('SUCCESS', mmv_data)
