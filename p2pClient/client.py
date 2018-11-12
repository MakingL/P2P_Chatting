# -*- coding: utf-8 -*-
# @Time    : 2018/11/5 15:21
# @Author  : MLee
# @File    : client.py
import json
import threading
import time
import tkinter as tk
from socketserver import StreamRequestHandler, ThreadingTCPServer
from tkinter import messagebox

from PeerManager.Chatting import Chatting
from PeerManager.LoginAndSignUp import LoginAndSignUp
from PeerManager.ServerConnection import ServerConnection
from PeerManager.ServerInfo import ServerInfo
from PeerManager.UserInfo import UserInfo
from PeerManager.WindowManager import WindowManager

user_info = UserInfo()
server_info = ServerInfo()
server_connection = ServerConnection()
window_manager = WindowManager()
active_peer_info_list = list()


def update_peer_info():
    global user_info, \
        server_info, server_connection, \
        active_peer_info_list

    while True:
        peer_name = user_info.user_name
        peer_port = user_info.local_port
        # 向服务器发送节点自身的信息
        peer_list_new = server_connection.send_heart_beat(
            peer_name, peer_port)
        active_peer_info_list = peer_list_new
        # 向各窗口发送联系人列表信息
        for window_obj in window_manager.get_all_window():
            window_obj.refresh_contact_list_info(peer_list_new)

        # 每隔 15s 向服务器登记一次节点信息
        time.sleep(15)


class LocalKnownServerHandler(StreamRequestHandler):
    """docstring for ServerHandler"""

    def handle(self):
        global user_info, \
            server_info, server_connection
        global window_manager, active_peer_info_list

        print("Got connection from {}".format(self.client_address))
        for line_data in self.rfile:
            message_data = json.loads(line_data, encoding="UTF-8")

            # 用户还未登录
            if not user_info.is_set_user_info:
                print("user_name is None")
                continue

            peer_name = message_data["peer_name"]

            if not window_manager.has_chatting_window(peer_name):
                # 弹出窗口提示有新用户的消息到达
                new_chatting = tk.messagebox.askyesno(title="A new peer message arrived",
                                                      message="A new peer message arrived from:"
                                                              " {}, are you want chat with"
                                                              " him?".format(peer_name))
                if new_chatting:
                    if window_manager.has_unused_window():
                        chatting_peer_obj = window_manager.get_unused_window()
                        chatting_peer_obj.set_info(user_info, server_info,
                                                   server_connection,
                                                   chatting_peer_name=peer_name)
                        window_manager.set_window_connection(chatting_peer_obj, peer_name)
                    else:
                        # 创建聊天界面管理对象
                        chatting_peer_obj = Chatting(user_info, server_info,
                                                     server_connection, window_manager,
                                                     chatting_peer_name=peer_name)
                        chatting_peer_obj.create_chatting_thread()
                        chatting_peer_obj.refresh_contact_list_info(active_peer_info_list)
                        window_manager.add_chatting_window(peer_name, chatting_peer_obj)

                    chatting_peer_obj.put_message(message_data)
            else:
                # 存在聊天界面
                chatting_peer_obj = window_manager.get_chatting_obj(peer_name)

                chatting_peer_obj.put_message(message_data)


def main():
    global user_info, server_info, server_connection
    global window_manager

    # 登录界面
    login_obj = LoginAndSignUp(user_info, server_info,
                               server_connection)

    login_obj.load_window()
    # 登录成功

    if user_info.is_set_user_info() and \
            server_info.is_set_server_info():
        # 启动心跳线程
        heartbeat_thread = threading.Thread(target=update_peer_info,
                                            args=())
        heartbeat_thread.start()

        # 登录成功,  开启界面
        chatting_obj = Chatting(user_info, server_info,
                                server_connection, window_manager)
        # 此窗口没有聊天对象
        window_manager.add_unused_window(chatting_obj)
        chatting_obj.refresh_contact_list_info(active_peer_info_list)
        chatting_obj.create_chatting_thread()

        # 监听自己的端口
        peer_address = ("", user_info.local_port)
        local_server = ThreadingTCPServer(peer_address,
                                          LocalKnownServerHandler)
        # 启动本地服务器线程，阻塞在这里
        local_server.serve_forever()

        # 此处需要添加关闭线程的部分
    else:
        print("False")


if __name__ == '__main__':
    main()
