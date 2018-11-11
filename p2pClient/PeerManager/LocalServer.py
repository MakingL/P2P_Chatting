# -*- coding: utf-8 -*-
# @Time    : 2018/11/10 17:10
# @Author  : MLee
# @File    : LocalServer.py
from socketserver import StreamRequestHandler


class LocalServerHandler(StreamRequestHandler):
    """docstring for ServerHandler"""

    def handle(self):
        print("Got connection from {}".format(self.client_address))
        for line_data in self.rfile:
            print(line_data)

