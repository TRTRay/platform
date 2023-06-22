# 用于生成json response的工具类

# 定义返回状态的枚举
response_status_enum = {
    'SUCCESS': {'status': 200, 'message': 'success!', 'success': True},
    'FAILED': {'status': 500, 'message': 'fail!', 'success': False}

    # 预留给后面做扩展
    # 50x   登陆相关的错误返回

    # 自定义的错误返回
}
