# -*- coding: utf-8 -*-
# @Time    : 2018/11/10 13:24
# @Author  : MLee
# @File    : ServerInfo.py


class ServerInfo(object):
    """docstring for ServerInfo"""

    def __init__(self, server_ip=None, server_port=None):
        self.server_ip = server_ip
        self.server_port = server_port

    def set_server_info(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port

    def set_server_ip(self, server_ip):
        self.server_ip = server_ip

    def set_server_port(self, server_port):
        self.server_port = server_port

    def is_set_server_info(self):
        if self.server_ip is None or self.server_port is None:
            return False
        else:
            return True
