from flask import Blueprint

map_bp = Blueprint('map', __name__)


# 添加、删除设备
@map_bp.route('/api/map', methods=['GET', 'POST'])
def test1():
    return '<p>Hello! This is test1 for /map.</p>'


# 生成地图，对应有一个算法
@map_bp.route('/api/map/generate', methods=['GET'])
def test2():
    return '<p>Hello! This is test2 for /map.</p>'
