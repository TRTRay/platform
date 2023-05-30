from flask import Flask


def create_app():
    app = Flask('platform')
    # register_blueprint(app)
    return app
