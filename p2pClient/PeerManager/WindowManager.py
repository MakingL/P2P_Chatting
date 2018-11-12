# -*- coding: utf-8 -*-
# @Time    : 2018/11/12 9:10
# @Author  : MLee
# @File    : WindowManager.py
# 聊天节点名字到窗口对象的映射
from PeerManager.Chatting import Chatting

chatting_connection_pairs = dict()
# 窗口对象到聊天节点名字的映射
connection_names = dict()
unused_chatting_obj = set()


class WindowManager(object):
    """docstring for WindowManager"""

    def __init__(self):
        pass

    def add_unused_window(self, window_obj):
        unused_chatting_obj.add(window_obj)

    def get_unused_window(self):
        window_obj = unused_chatting_obj.pop()
        return window_obj

    def set_window_connection(self, window_obj, peer_name):
        if window_obj in connection_names:
            window_peer_name = connection_names[window_obj]
            chatting_connection_pairs.pop(window_peer_name)
        if window_obj in unused_chatting_obj:
            unused_chatting_obj.remove(window_obj)

        chatting_connection_pairs[peer_name] = window_obj
        connection_names[window_obj] = peer_name

    def has_chatting_window(self, peer_name):
        if peer_name in chatting_connection_pairs:
            return True
        else:
            return False

    def add_chatting_window(self, peer_name, window_obj):
        chatting_connection_pairs[peer_name] = window_obj
        connection_names[window_obj] = peer_name

    def has_unused_window(self):
        if len(unused_chatting_obj) == 0:
            return False
        else:
            return True

    def get_chatting_obj(self, peer_name):
        return chatting_connection_pairs[peer_name]

    def get_all_window(self):
        window_list = list()
        for window in unused_chatting_obj:
            window_list.append(window)

        for window, peer_name in connection_names.items():
            window_list.append(window)

        return window_list

    def create_new_chatting_window(self, user_info, server_info,
                                   server_connection, window_manager,
                                   peer_name, active_peer_info_list):
        chatting_peer_obj = Chatting(user_info, server_info,
                                     server_connection, window_manager,
                                     chatting_peer_name=peer_name)
        chatting_peer_obj.create_chatting_thread()
        chatting_peer_obj.refresh_contact_list_info(active_peer_info_list)
        self.add_chatting_window(peer_name, chatting_peer_obj)
