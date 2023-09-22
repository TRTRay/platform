import os
import time
import wave
import datetime

import numpy as np
from scipy import io

from backend.utils.staticData import StaticData


class Utils:
    @staticmethod
    def get_timestamp():
        now = time.time()
        date = datetime.datetime.fromtimestamp(now)
        data_string = date.strftime('%Y/%m/%d %H:%M:%S')
        return data_string

    @staticmethod
    def find_device(deviceid):
        device_list = StaticData.device_list
        for index, device in enumerate(device_list):
            if device['deviceId'] == deviceid:
                return [True, index]
        return [False, len(device_list)]

    @staticmethod
    def is_file_updated_within_seconds(filename, seconds):
        if os.path.exists(filename):
            modification_time = os.path.getmtime(filename)
            current_time = time.time()
            return (current_time - modification_time) <= seconds
        else:
            return False

    @staticmethod
    def save_data_as_audio(deviceInform):
        data_key = deviceInform['deviceId'] + '_' + 'wav'
        audio_bits = StaticData.audio_buff[data_key]

        current_dir = os.path.dirname(__file__)
        filepath = os.path.join(current_dir, '..', '..',  'static', data_key + '.wav')
        with wave.open(filepath, 'w') as audio_file:
            audio_file.setparams((deviceInform['params']['recorderChannals'], 2, deviceInform['params']['sampleRate'], 0, 'NONE', 'not compressed'))
            audio_file.writeframes(audio_bits)

    @staticmethod
    def save_data_as_mat(deviceInform):
        data_key1 = deviceInform['deviceId'] + '_' + "csi"
        data_key2 = deviceInform['deviceId'] + '_' + 'plcr'
        csi_arr = StaticData.csi_buff[data_key1]
        plcr_arr = StaticData.plcr_buff[data_key2]

        if len(csi_arr) == 0:
            return
        current_dir = os.path.dirname(__file__)
        filepath1 = os.path.join(current_dir, '..', '..', 'static', data_key1 + '.mat')

        # size of matrix: timeframes × 180
        matrix = np.array(csi_arr).reshape(len(csi_arr), len(csi_arr[0])).T
        matrix = matrix.astype(np.complex128)

        matrix[0::2, :] = np.complex128(matrix[0::2, :] + matrix[1::2, :] * 1j)
        csi_matrix = matrix[0::2, :]
        csi_matrix_split = np.split(csi_matrix, 3, axis=0)
        csi_matrix_stack = np.stack(csi_matrix_split, axis=0)

        io.savemat(filepath1, {'csi': csi_matrix_stack})

        if len(plcr_arr) == 0:
            return
        filepath2 = os.path.join(current_dir, '..', '..', 'static', data_key2 + '.mat')
        matrix_plcr = np.array(plcr_arr)
        matrix_plcr = matrix_plcr.astype(np.float64)
        io.savemat(filepath2, {'plcr': matrix_plcr})
