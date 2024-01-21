import socket
import threading


# 用来接收Phone的数据
class AirMouseSocket:
    def __init__(self, name, meassage_handler) -> None:
        self.APP = name
        self.host = "192.168.137.1"
        self.port = 9999
        self.queue_size = 20
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.meassage_handler = meassage_handler

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.queue_size)  # 设置监听队列的大小
        print(self.APP, "socket服务启动")

    def listen(self, deviceId):
        # 创建新线程处理客户端连接
        client_thread = threading.Thread(target=self.listen_thread, args=(deviceId,))
        client_thread.start()

    def listen_thread(self, deviceId):
        # 接受客户端连接
        client_socket, client_address = self.server_socket.accept()
        print(f"New connection from {client_address[0]}:{client_address[1]}@{deviceId}")
        self.meassage_handler(client_socket, client_address, deviceId)
