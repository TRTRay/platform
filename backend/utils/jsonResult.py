# 用于生成json response的工具类
import json

# 定义返回状态的枚举
response_status_enum = {
    "SUCCESS": {"code": 200, "message": "success!", "success": True},
    # 40x
    "Unauthorized": {"code": 400, "message": "bad request", "success": False},
    # 预留给后面做扩展
    # 50x   错误返回
    "FAILED": {"code": 500, "message": "fail!", "success": False},
    # 自定义的错误返回
    "Warning": {"code": 208, "message": "warning", "success": True},
    "Timeout": {"code": 209, "message": "request time out", "success": False},
}


def req_success(stat, data) -> str:
    res = response_status_enum[stat]
    jsonResult = json.dumps(
        {
            "code": res["code"],
            "msg": res["message"],
            "success": res["success"],
            "data": data,
        }
    )
    return jsonResult


def req_failed(stat, data):
    res = response_status_enum[stat]
    jsonResult = json.dumps(
        {
            "code": res["code"],
            "msg": res["message"],
            "success": res["success"],
            "data": data,
        }
    )
    pass


# next version:请求成功，可能会有warning信息
# def req_success(stat, data, msg):
#     res = response_status_enum[stat]
#     jsonResult = json.dumps({
#         'code': res['code'],
#         'msg': msg,
#         'success': res['success'],
#         'data': data
#     })
#     return jsonResult


# next version:当请求参数不正确时的错误返回
def req_bad_request(stat, msg):
    res = response_status_enum[stat]
    json.dumps({"code": res["code"], "msg": msg, "success": res["success"]})
