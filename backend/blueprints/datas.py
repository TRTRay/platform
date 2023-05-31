from flask import Blueprint

datas_bp = Blueprint('datas', __name__)


# 回显实时数据
@datas_bp.route('/api/datas/', methond=['GET'])
def show_data():
    pass
