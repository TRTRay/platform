import multiprocessing
from backend.algos.AirMouse import AirMouseProcess
from backend.utils.AirMouseSocket import AirMouseSocket


def message_handler(client_socket, client_address, deviceId):
    while True:
        data = client_socket.recv(1024)  # 接收数据
        if data:  # 处理接收到的数据
            if deviceId in list(StaticData.AIRMOUSELIST.keys()):
                StaticData.AIRMOUSELIST[deviceId]["audiodata"].put(data)
        else:
            print(f"客户端 {client_address[0]}:{client_address[1]}@{deviceId} 断开连接")
            break
    client_socket.close()


class StaticData:
    # 设备列表
    device_list = []
    # 分段数据，Speaker和WiFi在使用
    data_slice = {}

    audio_buff = {}
    csi_buff = {}
    plcr_buff = {}
    camera_buff = []
    robot_buff = []
    mmv_buff = []
    rfid_buff = []

    AIRMOUSELIST = {}
    airmouse_socket = AirMouseSocket('AirMouse', message_handler)

    # Speaker在使用
    begin_index = {}

    # 呼吸监测相关
    csi_for_breath = {}
    # 应该是用不上
    win_len_for_breath = 1000
    # 需要和前端的接口调用频率同步
    step_len_for_breath = 300

    # 中台相关参数
    # Camera
    png_for_real_camera = []

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
        elif deviceInform['devType'] == 'MMV':
            # 实际上用不上，防止报错，先写在这
            data_key = deviceInform['deviceId'] + '_' + 'mmv'
            data_slice[data_key] = []
        elif deviceInform['devType'] == 'Phone':
            # 准备数据队列
            # 这里会调用两次，上线一次，start一次
            data_key = deviceInform['deviceId']
            data_manager = multiprocessing.Manager()
            audio_data = data_manager.Queue()
            motion_data = data_manager.list()
            airmouse_process = AirMouseProcess(audio_data, motion_data)
            StaticData.AIRMOUSELIST[data_key] = {
                'process': airmouse_process,
                'audiodata': audio_data,
                'motiondata': motion_data
            }
        elif deviceInform['devType'] == 'RFID':
            # 估计也用不上，防止报错，先写在这
            data_key = deviceInform['deviceId'] + '_' + 'rfid'
            data_slice[data_key] = []

    @staticmethod
    def update_index(deviceInform, index):
        # 目前只有声学设备
        begin_index = StaticData.begin_index
        if deviceInform['devType'] == 'Speaker':
            data_key = deviceInform['deviceId'] + '_' + 'wav'
            begin_index[data_key] = index
