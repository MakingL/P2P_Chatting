# -*- coding: utf-8 -*-
# @Time    : 2018/11/5 15:21
# @Author  : MLee
# @File    : client.py
from PeerManager.Chatting import Chatting
from PeerManager.LoginAndSignUp import LoginAndSignUp
from PeerManager.ServerConnection import ServerConnection
from PeerManager.ServerInfo import ServerInfo
from PeerManager.UserInfo import UserInfo


def main():
    user_info = UserInfo()
    server_info = ServerInfo()
    server_connection = ServerConnection()
    login_obj = LoginAndSignUp(user_info, server_info,
                               server_connection)

    login_obj.load_window()

    if user_info.is_set_user_info() and \
            server_info.is_set_server_info():
        # 登录成功
        chatting_obj = Chatting(user_info, server_info,
                                server_connection)
        chatting_obj.load_window()

        # 此处需要添加关闭线程的部分
    else:
        print("False")


if __name__ == '__main__':
    main()
