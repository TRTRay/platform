
class StaticData:
    device_list = []
    data_slice = {}

    def __init__(self):
        pass

    @staticmethod
    def new_data_queue(deviceInform):
        data_slice = StaticData.data_slice
        if deviceInform['devType'] == 'Speaker':
            data_key = deviceInform['deviceId'] + '_' + 'wav'
            # 之前出现过这样加空list加不上去，多留意一下
            data_slice[data_key] = []
            # data_slice[data_key] = [1]
            # data_slice[data_key].clear()
        elif deviceInform['devType'].startswith('WiFi'):
            data_key1 = deviceInform['deviceId'] + '_' + 'plcr'
            data_key2 = deviceInform['deviceId'] + '_' + 'csi'
            data_slice[data_key1] = []
            data_slice[data_key2] = []

    @staticmethod
    def empty_data_queue(deviceInform):
        data_slice = StaticData.data_slice
        if deviceInform['devType'] == 'Speaker':
            data_key = deviceInform['deviceId'] + '_' + 'wav'
            data_slice[data_key].clear()
        elif deviceInform['devType'].startswith('WiFi'):
            data_key1 = deviceInform['deviceId'] + '_' + 'plcr'
            data_key2 = deviceInform['deviceId'] + '_' + 'csi'
            data_slice[data_key1].clear()
            data_slice[data_key2].clear()
