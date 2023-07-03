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
# if test_mode:
#     device_list = [
#         {
#             "deviceId": "Speaker8",
#             "devType": "Speaker",
#             "stat": "on",
#             "params": {
#                 "signal": {
#                     "chirp": {
#                         "startFrequency": 18000,
#                         "bandWidth": 4000,
#                         "chirpT": 0.04
#                     },
#                     "Tchirp": {
#                         "startFrequency": 18000,
#                         "bandWidth": 4000,
#                         "chirpT": 0.04
#                     },
#                     "singleTone": {
#                         "frequency": 16000
#                     }
#                 },
#                 "sampleRate": 48000,
#                 "playerIndex": 1,
#                 "recorderIndex": 1,
#                 "recorderChannals": 1
#             },
#             "position": [],
#             "ip": "172.168.1.137"
#         },
#         {
#             "deviceId": "WiFi9",
#             "devType": "WiFi",
#             "stat": "on",
#             "params": [48000],
#             "position": None,
#             "ip": "172.168.1.138"
#         },
#         {
#             "deviceId": "Speaker1",
#             "devType": "Speaker",
#             "stat": "working",
#             "params": {
#                 "signal": {
#                     "chirp": {
#                         "startFrequency": 18000,
#                         "bandWidth": 4000,
#                         "chirpT": 0.04
#                     },
#                     "Tchirp": {
#                         "startFrequency": 18000,
#                         "bandWidth": 4000,
#                         "chirpT": 0.04
#                     },
#                     "singleTone": {
#                         "frequency": 16000
#                     }
#                 },
#                 "sampleRate": 48000,
#                 "playerIndex": 1,
#                 "recorderIndex": 1,
#                 "recorderChannals": 1
#             },
#             "position": [],
#             "ip": "172.168.1.137"
#         },
#         {
#             "deviceId": "WiFi2",
#             "devType": "WiFi",
#             "stat": "on",
#             "params": [48000],
#             "position": None,
#             "ip": "172.168.1.138"
#         },
#         {
#             "deviceId": "Speaker3",
#             "devType": "Speaker",
#             "stat": "on",
#             "params": {
#                 "signal": {
#                     "chirp": {
#                         "startFrequency": 18000,
#                         "bandWidth": 4000,
#                         "chirpT": 0.04
#                     },
#                     "Tchirp": {
#                         "startFrequency": 18000,
#                         "bandWidth": 4000,
#                         "chirpT": 0.04
#                     },
#                     "singleTone": {
#                         "frequency": 16000
#                     }
#                 },
#                 "sampleRate": 48000,
#                 "playerIndex": 1,
#                 "recorderIndex": 1,
#                 "recorderChannals": 1
#             },
#             "position": [],
#             "ip": "172.168.1.137"
#         },
#         {
#             "deviceId": "WiFi4",
#             "devType": "WiFi",
#             "stat": "on",
#             "params": [48000],
#             "position": None,
#             "ip": "172.168.1.138"
#         }
#     ]

data_slice = []
