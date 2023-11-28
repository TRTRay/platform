class StaticData:
    device_list = []
    data_slice = {}
    audio_buff = {}
    csi_buff = {}
    plcr_buff = {}
    camera_buff = []
    begin_index = {}

    csi_for_breath = {}

    def __init__(self):
        pass

    @staticmethod
    def empty_data_queue(deviceInform):
        data_slice = StaticData.data_slice
        if deviceInform['devType'] == 'Speaker':
            data_key = deviceInform['deviceId'] + '_' + 'wav'
            # 之前出现过这样加空list加不上去，多留意一下
            data_slice[data_key] = []
            StaticData.begin_index[data_key] = 0
            StaticData.audio_buff[data_key] = b''
        elif deviceInform['devType'].startswith('WiFi'):
            data_key1 = deviceInform['deviceId'] + '_' + 'plcr'
            data_key2 = deviceInform['deviceId'] + '_' + 'csi'
            data_slice[data_key1] = []
            data_slice[data_key2] = []
            StaticData.begin_index[data_key1] = 0
            StaticData.begin_index[data_key2] = 0
            StaticData.csi_buff[data_key2] = []
            StaticData.plcr_buff[data_key1] = []
            StaticData.csi_for_breath[data_key2] = []
        elif deviceInform['devType'] == 'Camera':
            data_key = deviceInform['deviceId'] + '_' + 'png'
            data_slice[data_key] = []

    @staticmethod
    def update_index(deviceInform, index):
        # 目前只有声学设备
        begin_index = StaticData.begin_index
        if deviceInform['devType'] == 'Speaker':
            data_key = deviceInform['deviceId'] + '_' + 'wav'
            begin_index[data_key] = index
