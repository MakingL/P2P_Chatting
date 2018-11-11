# -*- coding: utf-8 -*-
# @Time    : 2018/11/11 13:03
# @Author  : MLee
# @File    : PeerInfo.py


class PeerInfo(object):
    """docstring for PeerInfo"""

    def __init__(self, peer_name=None, peer_ip=None, peer_port=None):
        self.peer_name = peer_name
        self.peer_ip = peer_ip
        self.peer_port = peer_port

    def set_peer_info(self, peer_name, peer_ip, peer_port):
        self.peer_name = peer_name
        self.peer_ip = peer_ip
        self.peer_port = peer_port

    def set_peer_name(self, peer_name):
        self.peer_name = peer_name

    def set_peer_password(self, peer_ip):
        self.peer_ip = peer_ip

    def set_peer_port(self, peer_port):
        self.peer_port = peer_port

    def is_set_peer_info(self):
        if self.peer_name is None or self.peer_ip is None \
                or self.peer_port is None:
            return False
        else:
            return True
