# 参数
# test模式下，做一些假数据
test_mode = True
test_param = {
    'random_generate_fre': 1
}

# mqtt服务器地址、端口、窗口期
broker_ip = '182.92.152.209'
broker_port = 1883
keep_alive = 3600

# 用作存储的全局变量
# 存储设备信息
device_list = []
if test_mode:
    device_list = [
        {'deviceId': 'Acoustic1', 'devType': 'Acoustic', 'stat': 'working', 'param': 48000, 'position': None},
        {'deviceId': 'Acoustic8', 'devType': 'Acoustic', 'stat': 'working', 'param': 48000, 'position': None},
        {'deviceId': 'Wifi2', 'devType': 'WiFi', 'stat': 'working', 'param': 48000, 'position': None},
        {'deviceId': 'Wifi9', 'devType': 'WiFi', 'stat': 'working', 'param': 48000, 'position': None}
    ]

data_slice = []
