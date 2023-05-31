from flask import Flask
from threading import Thread

from backend.mqttServer import run_mqtt_service, client
from backend.blueprints.devices import devices_bp
from backend.blueprints.map import map_bp
from backend.blueprints.datas import datas_bp


def register_blueprint(app):
    app.register_blueprint(devices_bp)
    app.register_blueprint(map_bp)


def create_app():
    app = Flask('platform')
    register_blueprint(app)
    return app


mqtt_server = Thread(name='mqtt_server', target=run_mqtt_service, args=(client,))
mqtt_server.start()
