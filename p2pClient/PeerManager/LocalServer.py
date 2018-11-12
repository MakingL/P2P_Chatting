# -*- coding: utf-8 -*-
# @Time    : 2018/11/10 17:10
# @Author  : MLee
# @File    : LocalServer.py
from socketserver import StreamRequestHandler, ThreadingTCPServer


connection_pairs = set()
chatting_peer_set = set()

class LocalKnownServerHandler(StreamRequestHandler):
    """docstring for ServerHandler"""

    def handle(self):
        print("Got connection from {}".format(self.client_address))
        for line_data in self.rfile:
            message_data = json.loads(line_data, encoding="UTF-8")
            if message_data["peer_name"] not in chatting_peer_set:
                chatting_peer_set.add(message_data["peer_name"])




class KnownServer(object):
    """docstring for KnownServer"""

    def __init__(self, user_info_obj, server_info_obj, server_connection_obj):
        self.user_info_obj = user_info_obj
        self.server_info_obj = server_info_obj
        self.server_connection_obj = server_connection_obj

    def create_local_server(self):
        # 监听自己的端口
        peer_address = ("", self.user_info_obj.local_port)
        local_server = ThreadingTCPServer(peer_address,
                                          LocalKnownServerHandler)
        # 启动本地服务器线程，阻塞在这里
        local_server.serve_forever()
