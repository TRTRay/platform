from flask import Flask
from threading import Thread
from loguru import logger

import sys

from backend.mqttServer import MqttServer
from backend.config import *
from backend.blueprints.devices import devices_bp
from backend.blueprints.map import map_bp
from backend.blueprints.datas import datas_bp
from backend.blueprints.algos_wifi import algos_wifi_bp
from backend.blueprints.test import test_api

from backend.blueprints.temp import temp_bp
import backend.resources.LSTM_Net


def register_blueprint(app):
    app.register_blueprint(devices_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(datas_bp)
    app.register_blueprint(algos_wifi_bp)
    app.register_blueprint(temp_bp)
    app.register_blueprint(test_api)


# 重命名模块LSTM_Net的路径
sys.modules['LSTM_Net'] = backend.resources.LSTM_Net


def create_app():
    app = Flask("platform")
    register_blueprint(app)
    return app


mqtt_server_thread = Thread(
    name="mqtt_server",
    target=MqttServer.run_mqtt_service,
    args=(broker_ip, broker_port, keep_alive),
)
mqtt_server_thread.start()
