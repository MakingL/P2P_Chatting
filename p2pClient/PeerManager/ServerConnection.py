# -*- coding: utf-8 -*-
# @Time    : 2018/11/10 13:31
# @Author  : MLee
# @File    : ServerConnection.py
import json
from socket import *


class ServerConnection(object):
    """docstring for ServerConnection"""

    def __init__(self, server_ip=None, server_port=None):
        self.server_ip = server_ip
        self.server_port = server_port
        self.server_tcp_connection = socket(AF_INET, SOCK_STREAM)
        self.BUFFER_SIZE = 1024
        self.is_connected = False

    # def __del__(self):
    #     if self.is_connected:
    #         self.server_tcp_connection.close()

    def set_server_info(self, server_ip, server_port):
        # print("Set server info: {} {}".format(server_ip, server_port))
        self.server_ip = server_ip
        self.server_port = server_port

    def is_connected_to_server(self):
        return self.is_connected

    def connect_server(self):
        # 连接服务器
        server_address = (self.server_ip, self.server_port)
        # print("Connection address: {}".format(server_address))
        try:
            self.server_tcp_connection.connect(server_address)
        except (Exception, Warning) as e:
            print("Connect server failed: {}".format(str(e)))
            return False
        else:
            self.is_connected = True
            # print("Connect success")
            return True

    def register_peer(self, peer_name, password):
        if not self.is_connected_to_server():
            self.connect_server()

        peer_info = {"action": "register",
                     "peer_name": peer_name, "password": password}
        peer_info_json = json.dumps(peer_info)
        peer_info_json = "{}\r\n".format(peer_info_json).encode("UTF-8")
        # print(peer_info_json)
        self.server_tcp_connection.send(peer_info_json)

        # 从服务器获取注册反馈
        register_feedback = self.server_tcp_connection.recv(self.BUFFER_SIZE)
        register_feedback = json.loads(register_feedback, encoding="UTF-8")
        # print("register_feedback: {}".format(register_feedback))

        if register_feedback["status"] == "true":
            feedback_info = True
        else:
            feedback_info = False

        return feedback_info

    def login_peer(self, peer_name, password):
        if not self.is_connected_to_server():
            self.connect_server()
        peer_info = {"action": "login",
                     "peer_name": peer_name, "password": password}
        peer_info_json = json.dumps(peer_info)
        peer_info_json = "{}\r\n".format(peer_info_json).encode("UTF-8")
        self.server_tcp_connection.send(peer_info_json)

        # 从服务器获取注册反馈
        login_feedback = self.server_tcp_connection.recv(self.BUFFER_SIZE)
        login_feedback = json.loads(login_feedback, encoding="UTF-8")

        if login_feedback["status"] == "true":
            feedback_info = {"status": True}
        else:
            if login_feedback["msg"] == "502":
                # 密码不正确
                feedback_info = {"status": False, "code": "402"}
            elif login_feedback["msg"] == "504":
                # 用户名未注册
                feedback_info = {"status": False, "code": "404"}
            else:
                # 未知错误
                feedback_info = {"status": False, "code": "401"}
        return feedback_info

    def send_heart_beat(self, peer_name, peer_port):
        if not self.is_connected_to_server():
            self.connect_server()

        # 向服务器发送节点自身的信息
        peer_info = {"action": "update_info",
                     "peer_name": peer_name, "peer_port": peer_port}
        peer_info_json = json.dumps(peer_info)
        peer_info_json = "{}\r\n".format(peer_info_json).encode("UTF-8")
        # print(peer_info_json)
        self.server_tcp_connection.send(peer_info_json)

        # 从服务器获取已登记的节点信息
        peer_list_new = self.server_tcp_connection.recv(self.BUFFER_SIZE)
        peer_list_new = json.loads(peer_list_new, encoding="UTF-8")

        return peer_list_new

    def send_chatting_message(self, message_data, sender):
        if not self.is_connected_to_server():
            self.connect_server()

        # 向服务器发送节点自身的信息
        data = {"action": "chat",
                "peer_name": sender, "data": message_data}
        mssg_info_json = json.dumps(data)
        mssg_info_json = "{}\r\n".format(mssg_info_json).encode("UTF-8")
        # print(peer_info_json)
        self.server_tcp_connection.send(mssg_info_json)


if __name__ == '__main__':
    server_connection = ServerConnection("127.0.0.1", 21569)
    print(server_connection.connect_server())
    server_connection.register_peer("Micheal", "123456")
    server_connection.login_peer("Micheal", "12356")
