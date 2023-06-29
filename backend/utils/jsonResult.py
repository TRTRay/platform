# 用于生成json response的工具类
import json

# 定义返回状态的枚举
response_status_enum = {
    'SUCCESS': {'status': 200, 'message': 'success!', 'success': True},
    'FAILED': {'status': 500, 'message': 'fail!', 'success': False}

    # 预留给后面做扩展
    # 50x   登陆相关的错误返回

    # 自定义的错误返回
}


def req_success(stat, data: list):
    res = response_status_enum[stat]
    jsonResult = json.dumps({
        'status': res['status'],
        'message': res['message'],
        'success': res['success'],
        'data': data
    })
    return jsonResult
