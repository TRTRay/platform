from backend import create_app
from flask_cors import CORS


app = create_app()
# 用来解决跨域问题
CORS(app, resources=r'/*')

app.run()
