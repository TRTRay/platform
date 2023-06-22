import json
import time

from paho.mqtt import client as mqtt
from backend.config import *
from backend.utils.resMessage import *


# 成功和服务器建立连接时（收到CONNACK）进行回调
def __on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT successfully!")
    else:
        print("Failed to connect, return code :{0}".format(rc))


# 在收到服务器发布的消息时（收到PUBLISH）进行回调
def __on_message(client, userdata, msg):
    # 接收到消息后根据主题类型进行分类处理
    print("Received message, topic:" + msg.topic)
    topic_case.get(msg.topic, res_default)(client, userdata, msg)


# 断开连接
def __on_disconnect(client, userdata, rc):
    print("Connection returned result:" + str(rc))


# 在收到订阅回复时（收到SUBACK）进行回调
def __on_subscribe(client, userdata, mid, granted_qos):
    print('New subscribe!')


def mqtt_connect(ip, port, hold_for):
    # 创建客户端实例
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = __on_connect
    mqtt_client.on_disconnect = __on_disconnect
    mqtt_client.on_message = __on_message
    mqtt_client.on_subscribe = __on_subscribe

    # 连接MQTT服务器，IP地址，端口号，窗口期
    mqtt_client.connect(ip, port, hold_for)
    return mqtt_client


# 开启网络循环
def run_mqtt_service(mqtt_client):
    mqtt_client.subscribe('/client/#')
    mqtt_client.loop_forever()


# 返回连接好的客户端实例
client = mqtt_connect(broker_ip, broker_port, keep_alive)
