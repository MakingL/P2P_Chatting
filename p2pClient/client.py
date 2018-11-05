# -*- coding: utf-8 -*-
# @Time    : 2018/11/5 15:21
# @Author  : MLee
# @File    : client.py
import json
import threading
from socket import *
from socketserver import ThreadingTCPServer, StreamRequestHandler
from time import sleep

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 21569
BUFFERSIZE = 1024
ADDR = (SERVER_HOST, SERVER_PORT)

server_tcp_connection = socket(AF_INET, SOCK_STREAM)

PEER_HOST = ""
PEER_PORT = 0
PEER_NAME = ""
PEER_ADDR = (PEER_HOST, PEER_PORT)

peer_list = list()


def register_peer(peer_name, peer_port):
    peer_info = {"action": "register", "peer_name": peer_name, "peer_port": peer_port}
    peer_info_json = json.dumps(peer_info)
    peer_info_json = "{}\r\n".format(peer_info_json).encode("UTF-8")
    # print(peer_info_json)
    server_tcp_connection.send(peer_info_json)

    # 从服务器获取注册反馈
    register_feedback = server_tcp_connection.recv(BUFFERSIZE)
    print("register_feedback: {}".format(register_feedback))


def update_register_info(peer_name, peer_port):
    global peer_list
    while True:
        # 向服务器发送节点自身的信息
        peer_info = {"action": "update_info", "peer_name": peer_name, "peer_port": peer_port}
        peer_info_json = json.dumps(peer_info)
        peer_info_json = "{}\r\n".format(peer_info_json).encode("UTF-8")
        # print(peer_info_json)
        server_tcp_connection.send(peer_info_json)

        # 从服务器获取已登记的节点信息
        peer_list_new = server_tcp_connection.recv(BUFFERSIZE)
        # print("peer list: {}".format(peer_list_new))

        # 此处的 peer list 要出去自己
        peer_list = json.loads(peer_list_new)

        # 每隔 15s 向服务器登记一次节点信息
        sleep(15)


class ServerHandler(StreamRequestHandler):
    """docstring for ServerHandler"""

    def handle(self):
        print("Got connection from {}".format(self.client_address))
        for line_data in self.rfile:
            print(line_data)
            # data = json.loads(line_data, encoding="UTF-8")
            # print(data)


class Chatting(object):
    """docstring for Chatting"""

    def __init__(self, dest_name, dest_ip, dest_port):
        self.peer_name = PEER_NAME
        self.dest_name = dest_name
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.chatting_connection = socket(AF_INET, SOCK_STREAM)
        self.chatting_connection.connect((dest_ip, dest_port))

    def send_message(self, message):
        data = {"from": self.peer_name, "destination": self.dest_name,
                "message": message}
        data = json.dumps(data)
        data = "{}\r\n".format(data)
        data = data.encode("UTF-8")

        self.chatting_connection.send(data)


def main():
    # 节点信息
    global PEER_NAME
    global PEER_HOST
    global PEER_PORT
    global PEER_ADDR
    PEER_NAME = "micheal"
    PEER_PORT = 52021
    PEER_ADDR = (PEER_HOST, PEER_PORT)

    # 连接服务器
    server_tcp_connection.connect(ADDR)

    register_peer(PEER_NAME, PEER_PORT)

    # 建立登记线程
    heartbeat_thread = threading.Thread(target=update_register_info,
                                        args=(PEER_NAME, PEER_PORT))
    heartbeat_thread.start()

    # 监听自己的某个端口
    serv = ThreadingTCPServer(PEER_ADDR, ServerHandler)
    serv.serve_forever()


if __name__ == '__main__':
    main()
