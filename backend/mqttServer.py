from paho.mqtt import client as mqtt
from backend.utils.resMessage import *


class MqttServer:
    mqtt_client = mqtt.Client()

    @staticmethod
    def run_mqtt_service(host, port, keepalive):
        MqttServer.mqtt_client.connect(host, port, keepalive)
        MqttServer.mqtt_client.subscribe('/client/#')
        MqttServer.mqtt_client.loop_forever()

    @staticmethod
    def publish(topic, payload, qos=0):
        MqttServer.mqtt_client.publish(topic, payload=payload, qos=qos)

    @staticmethod
    # 成功和服务器建立连接时（收到CONNACK）进行回调
    def __on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT successfully!")
        else:
            print("Failed to connect, return code :{0}".format(rc))

    @staticmethod
    # 在收到服务器发布的消息时（收到PUBLISH）进行回调
    def __on_message(client, userdata, msg):
        # 接收到消息后根据主题类型进行分类处理
        print("Received message, topic:" + msg.topic)
        res_case(client, userdata, msg)

    @staticmethod
    # 断开连接
    def __on_disconnect(client, userdata, rc):
        print("Connection returned result:" + str(rc))

    @staticmethod
    # 在收到订阅回复时（收到SUBACK）进行回调
    def __on_subscribe(client, userdata, mid, granted_qos):
        print('New subscribe!')

    mqtt_client.on_connect = __on_connect
    mqtt_client.on_disconnect = __on_disconnect
    mqtt_client.on_message = __on_message
    mqtt_client.on_subscribe = __on_subscribe
