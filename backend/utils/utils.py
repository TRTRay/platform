import os
import time
import wave
import datetime

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
