from backend import create_app
from flask_cors import CORS
from gevent import pywsgi


app = create_app()
# 用来解决跨域问题
CORS(app, resources=r'/*')

# if __name__ == '__main__':
#     app.run(debug=True, host='127.0.0.1')

server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
server.serve_forever()
