# -*- coding: utf-8 -*-
# @Time    : 2018/11/5 15:09
# @Author  : MLee
# @File    : server.py
import json
import os
import pickle
import threading
from _datetime import datetime
from socketserver import StreamRequestHandler, ThreadingTCPServer
from time import sleep

HOST = ""
PORT = 51569
ADDR = (HOST, PORT)

# 当前活跃的用户信息
peer_heart_dict = dict(tuple())
peer_name_set = set()

# 已注册的用户信息文件
USER_INFO_PATH = './user_information/usr_info.pickle'

if not os.path.exists(USER_INFO_PATH):
    os.makedirs(USER_INFO_PATH)
if not os.path.exists(USER_INFO_PATH):
    with open(USER_INFO_PATH, "wb+") as usr_file:
        usr_info = {'admin': 'admin123'}
        pickle.dump(usr_info, usr_file)


class ServerHandler(StreamRequestHandler):
    """docstring for ServerHandler"""

    def handle(self):

        print("Got connection from {}".format(self.client_address))
        peer_ip, request_port = self.client_address

        # 解析收到的数据
        for line_data in self.rfile:
            # print(line_data)
            data = json.loads(line_data, encoding="UTF-8")
            print(data)

            if "action" in data:
                action = data["action"]

                if action == "update_info":
                    # 更新节点信息
                    peer_port = data["peer_port"]

                    time_now = datetime.now()
                    time_now = time_now.strftime("%Y-%m-%d-%X")

                    peer_data_new = (time_now, peer_ip, peer_port)
                    peer_heart_dict[data["peer_name"]] = peer_data_new

                    # 返回已登记的 peer 信息
                    peer_list = list(dict())
                    for peer_name, peer_info in peer_heart_dict.items():
                        _, ip, port = peer_info
                        peer_node = {"name": peer_name, "ip": ip, "port": port}
                        peer_list.append(peer_node)

                    peers = json.dumps(peer_list)
                    peers = peers.encode("UTF-8")
                    self.wfile.write(peers)

                elif action == "register":
                    # 注册用户

                    peer_name = data["peer_name"]
                    password = data["password"]

                    # 读取已经注册了的用户信息
                    with open(USER_INFO_PATH, 'rb') as file_user_info:
                        existed_usr_info = pickle.load(file_user_info)

                    if peer_name in existed_usr_info:
                        # 该用户名已存在
                        result = {"status": "false"}
                    else:
                        # 添加用户信息
                        existed_usr_info[peer_name] = password

                        # 添加用户信息到文件
                        with open(USER_INFO_PATH, "wb") as f1:
                            pickle.dump(existed_usr_info, f1)

                        # # 登记心跳数据
                        # peer_port = data["peer_port"]
                        # time_now = datetime.now()
                        # time_now = time_now.strftime("%Y-%m-%d-%X")
                        # peer_data_new = (time_now, peer_ip, peer_port)
                        # peer_heart_dict[data["peer_name"]] = peer_data_new

                        # 注册成功
                        result = {"status": "true"}

                    # 返回反馈信息
                    result = json.dumps(result)
                    result = result.encode("UTF-8")
                    self.wfile.write(result)

                elif action == "login":
                    # 读取已经注册了的用户信息
                    with open(USER_INFO_PATH, 'rb') as file_usr_info:
                        existed_usr_info = pickle.load(file_usr_info)

                    print("existed_usr_info: {}".format(existed_usr_info))

                    peer_name = data["peer_name"]
                    password = data["password"]

                    if peer_name not in existed_usr_info:
                        # 用户名不存在
                        result = {"status": "false", "msg": "504"}
                    elif password == existed_usr_info[peer_name]:
                        # 登录成功
                        result = {"status": "true"}

                        # 添加当前活跃的用户
                        peer_name_set.add(peer_name)
                    else:
                        # 用户密码不正确
                        result = {"status": "false", "msg": "502"}

                    result = json.dumps(result)
                    result = result.encode("UTF-8")
                    self.wfile.write(result)


def update_peer_list():
    while True:
        delete_peer = list()
        delete_peer.clear()
        for peer_name, peer_data in peer_heart_dict.items():
            log_time, _, _ = peer_data

            print("Peer: {} {}".format(peer_name, peer_data))

            time_now = datetime.now()
            # log_time = datetime.strftime("%Y-%m-%d-%X")
            time_delta = time_now - datetime.strptime(log_time, "%Y-%m-%d-%X")
            if time_delta.seconds > 30:
                delete_peer.append(peer_name)

        for peer in delete_peer:
            peer_name_set.remove(peer)

            peer_heart_dict.pop(peer)
            print("{} has been delete".format(peer))

        # 定时 30s 刷新一次
        sleep(30)


if __name__ == '__main__':
    # 建立登记线程
    heartbeat_thread = threading.Thread(target=update_peer_list,
                                        args=())
    heartbeat_thread.start()

    serv = ThreadingTCPServer(ADDR, ServerHandler)
    serv.serve_forever()
