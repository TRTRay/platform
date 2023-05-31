import json
import time

from paho.mqtt import client as mqtt


topic = '/broker'
sub_topic = '/client/#'

# mqtt服务器地址、端口、窗口期
broker_ip = '8.130.124.186'
broker_port = 1883
keep_alive = 3600

# 存储设备信息
# device_list = []
# for test
device_list = [
    {'deviceId': 'Acoustic1', 'type': 'Acoustic', 'stat': 'working', 'param': 48000},
    {'deviceId': 'Acoustic8', 'type': 'Acoustic', 'stat': 'working', 'param': 48000},
    {'deviceId': 'Wifi2', 'type': 'WiFi', 'stat': 'working', 'param': 48000},
    {'deviceId': 'Wifi9', 'type': 'WiFi', 'stat': 'working', 'param': 48000}
]


# 成功和服务器建立连接时（收到CONNACK）进行回调
def __on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT successfully!")
    else:
        print("Failed to connect, return code :{0}".format(rc))
    # 可以添加一个订阅的调用，表示如果客户端和服务器断连，在重连后可以恢复


# 在收到服务器发布的消息时（收到PUBLISH）进行回调
def __on_message(client, userdata, msg):
    # 接收到消息后根据主题类型进行分类处理
    print("Received message, topic:" + msg.topic + " payload:" + str(msg.payload))
    # '/client/response/deviceInform'   端设备回应的设备信息
    if msg.topic == '/client/respond/deviceInform':
        # 对设备信息的预想是json格式返回的一系列信息
        deviceInform = json.loads(msg.payload)
        device_list.append(deviceInform)
        # print('list append')
        # print(device_list)
        # pass


# 断开连接
def __on_disconnect(client, userdata, rc):
    print("Connection returned result:" + str(rc))


# 在收到订阅回复时（收到SUBACK）进行回调
def __on_subscribe(client, userdata, mid, granted_qos):
    print('New subscribe!')


def mqtt_connect(broker_ip, broker_port, keep_alive):
    # 创建客户端实例
    client = mqtt.Client()
    client.on_connect = __on_connect
    client.on_disconnect = __on_disconnect
    client.on_message = __on_message
    client.on_subscribe = __on_subscribe

    # 连接MQTT服务器，IP地址，端口号，窗口期
    client.connect(broker_ip, broker_port, keep_alive)

    return client


client = mqtt_connect(broker_ip, broker_port, keep_alive)


def run_mqtt_service(client):
    client.subscribe(sub_topic)
    client.loop_forever()
