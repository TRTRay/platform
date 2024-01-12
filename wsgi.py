from backend import create_app, log
from flask_cors import CORS
from gevent import pywsgi


def main():
    app = create_app()
    # 用来解决跨域问题
    CORS(app, resources=r"/*")

    server = pywsgi.WSGIServer(
        ("0.0.0.0", 5000),
        app,
        log=log.InterceptHandler(),
        error_log=log.InterceptHandler(),
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
