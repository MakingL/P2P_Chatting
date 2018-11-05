# -*- coding: utf-8 -*-
# @Time    : 2018/11/5 15:09
# @Author  : MLee
# @File    : server.py
import threading
from _datetime import datetime
import json
from socketserver import StreamRequestHandler, ThreadingTCPServer
from time import sleep

HOST = ""
PORT = 21569
ADDR = (HOST, PORT)

peer_heart_dict = dict(tuple())
peer_name_set = set()


class ServerHandler(StreamRequestHandler):
    """docstring for ServerHandler"""

    def handle(self):
        print("Got connection from {}".format(self.client_address))
        peer_ip = self.client_address
        for line_data in self.rfile:
            # print(line_data)
            data = json.loads(line_data, encoding="UTF-8")
            print(data)
            if "action" in data:
                action = data["action"]
                if action == "update_info":
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
                    peer_name = data["peer_name"]
                    if peer_name in peer_name_set:
                        result = {"status": "false"}
                    else:
                        peer_name_set.add(peer_name)
                        result = {"status": "success"}
                    result = json.dumps(result)
                    result = result.encode("UTF-8")
                    self.wfile.write(result)

                    peer_port = data["peer_port"]

                    time_now = datetime.now()
                    time_now = time_now.strftime("%Y-%m-%d-%X")

                    peer_data_new = (time_now, peer_ip, peer_port)
                    peer_heart_dict[data["peer_name"]] = peer_data_new


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
