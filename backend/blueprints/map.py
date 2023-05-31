from flask import Blueprint

map_bp = Blueprint('map', __name__)


# 添加、删除设备、生成地图，对应有一个算法
@map_bp.route('/api/map', methods=['GET', 'POST'])
def map_ctrl():

    return '<p>Hello! This is test1 for /map.</p>'
