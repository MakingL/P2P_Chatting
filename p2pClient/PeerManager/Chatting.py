# -*- coding: utf-8 -*-
# @Time    : 2018/11/10 17:00
# @Author  : MLee
# @File    : Chatting.py
import json
import threading
import time
import tkinter as tk
from queue import Queue
from socketserver import ThreadingTCPServer, StreamRequestHandler
from tkinter import *
from tkinter import messagebox

from PeerManager.PeerInfo import PeerInfo
from PeerManager.ServerConnection import ServerConnection

user_message_queue = Queue()
widget_chatted_content_global = None


def create_new_chatting_obj(user_info_obj, server_info_obj,
                            server_connection_obj, chatting_peer_obj):
    """
    为新的聊天请求创建新的聊天窗口
    :param user_info_obj:
    :param server_info_obj:
    :param server_connection_obj:
    :param chatting_peer_obj:
    :return:
    """
    chatting_obj = NewChatting(user_info_obj, server_info_obj,
                               server_connection_obj, chatting_peer_obj)
    chatting_obj.load_window()


class LocalServerHandler(StreamRequestHandler):
    """docstring for ServerHandler"""

    def handle(self):
        global user_message_queue, widget_chatted_content_global
        print("Got connection from {}".format(self.client_address))
        for line_data in self.rfile:
            message_data = json.loads(line_data, encoding="UTF-8")
            user_message_queue.put(message_data)
            print("got message: {}".format(message_data))
            if widget_chatted_content_global is not None:
                widget_chatted_content_global.event_generate("<<get>>")
            else:
                print("widget_chatted_content_global is None when recv message")


class Chatting(object):
    """docstring for Chatting"""

    def __init__(self, user_info_obj, server_info_obj,
                 server_connection_obj):
        self.user_info_obj = user_info_obj
        self.server_info_obj = server_info_obj
        self.server_connection_obj = server_connection_obj
        self.peer_list = list()
        self.peer_name = user_info_obj.user_name
        self.peer_port = user_info_obj.local_port

        self.chatting_window = None
        self.var_chat_with = None
        self.var_peer_name = None
        self.var_peer_port = None
        self.var_recv_msg = None
        self.widget_list_contact = None
        self.widget_chatted_content = None
        self.widget_editing_msg = None

        # 正在聊天的对象信息
        self.chatting_peer_name = None
        self.chatting_peer_port = None
        self.chatting_peer_ip = None

        self.chatting_connection = None

        self.active_peer_node_info = dict()

    def create_heartbeat_thread(self):
        heartbeat_thread = threading.Thread(target=self.update_peer_info,
                                            args=())
        heartbeat_thread.start()

    def create_server_thread(self):
        create_thread = threading.Thread(target=self.create_local_server,
                                         args=())
        create_thread.start()

    def create_local_server(self):
        # 监听自己的端口
        peer_address = ("", self.user_info_obj.local_port)
        local_server = ThreadingTCPServer(peer_address,
                                          LocalServerHandler)
        # 启动本地服务器线程，阻塞在这里
        local_server.serve_forever()

    def create_new_chat_window(self, new_peer_obj):
        new_chatting_thread = threading.Thread(target=create_new_chatting_obj,
                                               args=(self.user_info_obj,
                                                     self.server_info_obj,
                                                     self.server_connection_obj,
                                                     new_peer_obj))
        new_chatting_thread.start()

    def set_chatting_peer(self, peer_name, peer_ip, peer_port):
        self.chatting_peer_name = peer_name
        self.chatting_peer_port = peer_port
        self.chatting_peer_ip = peer_ip

        # 聊天对象
        self.var_chat_with.set("Chat with: {}".format(peer_name))
        self.chatting_connection = ServerConnection(peer_ip, peer_port)
        self.chatting_connection.connect_server()
        # self.chatting_connection.send_chatting_message("Hello!", self.peer_name)
        # print("Connection peer OK")

    def has_chatting_chatting_peer(self):
        if self.chatting_peer_name is None or \
                self.chatting_peer_ip is None or \
                self.chatting_peer_port is None:
            return False
        else:
            return True

    def update_peer_info(self):
        while True:
            # 向服务器发送节点自身的信息
            peer_list_new = self.server_connection_obj.send_heart_beat(
                self.peer_name, self.peer_port)

            active_peer_name_set = set()
            self.active_peer_node_info.clear()
            for peer_node in peer_list_new:
                # 此处的 peer list 要除去自己
                if peer_node["name"] == self.user_info_obj.user_name:
                    continue

                # 将收到的节点添加到集合
                active_peer_name_set.add(peer_node["name"])
                node_info = (peer_node["ip"], peer_node["port"])

                self.active_peer_node_info[peer_node["name"]] = node_info

            self.update_peer_list(active_peer_name_set)

            # 每隔 15s 向服务器登记一次节点信息
            time.sleep(15)

    def update_peer_list(self, active_peer_name_set):
        if self.widget_list_contact is None:
            return False

        self.widget_list_contact.delete(first=0, last=END)
        for active_peer_name in active_peer_name_set:
            self.widget_list_contact.insert(END, "  {}".format(active_peer_name))

    def chatting_with_peer(self, event):
        curse_index = self.widget_list_contact.curselection()
        if curse_index == 0:
            return False

        value = self.widget_list_contact.get(curse_index)
        value = value.strip("\n ")
        tk.messagebox.showwarning(title="chatting with",
                                  message="chatting with: {}".format(value))

        peer_info = self.active_peer_node_info[value]
        peer_ip, peer_port = peer_info
        self.set_chatting_peer(value, peer_ip, peer_port)

    def send_message_to_peer(self, message):  # 发送消息
        print("self.chatting_connection: {}".format(self.chatting_connection))
        if self.chatting_connection is not None:
            self.chatting_connection.send_chatting_message(message,
                                                           self.peer_name)
            return True
        else:
            return False

    def cancel_edited_msg(self):  # 取消消息
        self.widget_editing_msg.delete('0.0', END)

    def send_msg_event(self, event=None):  # 发送消息事件

        if event is None or event.keysym == "Return":  # 按回车键可发送
            self_peer_info = "{} :  {}\n".format("you",
                                                 time.strftime("%Y-%m-%d %H:%M:%S",
                                                               time.localtime()))
            # 插入到tag: timestamp 位置
            self.widget_chatted_content.insert(END, self_peer_info, 'timestamp_self')
            message_edited = self.widget_editing_msg.get('0.0', END)
            message_edited = message_edited.strip("\n ")
            self.widget_chatted_content.insert(END, "{}\n".format(message_edited))
            self.widget_editing_msg.delete('0.0', END)

            # print("send message to peer: {}".format(message_edited))
            self.send_message_to_peer(message_edited)

    def receive_msg_event(self, event):
        global user_message_queue
        while not user_message_queue.empty():
            message_info = user_message_queue.get()
            if "action" in message_info and \
                    message_info["action"] == "chat":
                sender_name = message_info["peer_name"]
                sender_ip, sender_port = self.active_peer_node_info[sender_name]

                if self.chatting_peer_name is None:
                    self.set_chatting_peer(sender_name, sender_ip, sender_port)

                    is_chatting_peer_message = True
                elif self.chatting_peer_name == sender_name:
                    is_chatting_peer_message = True
                else:
                    is_chatting_peer_message = False
                    print("Receive chatting message from: {}".format(sender_name))
                    # 弹出窗口提示有新用户的消息到达
                    new_chatting = tk.messagebox.askyesno(title="A new peer message arrived",
                                                          message="A new peer message arrived from:"
                                                                  " {}, are you want chat with"
                                                                  " him?".format(sender_name))
                    if new_chatting:
                        # new_chatting_peer_obj = PeerInfo(sender_name, sender_ip, sender_port)
                        # self.create_new_chat_window(new_chatting_peer_obj)
                        self.set_chatting_peer(sender_name, sender_ip, sender_port)
                    # 如果用户同意与新用户建立连接，则创建线程，建立一个新的窗口对象

                if is_chatting_peer_message is True:
                    data = message_info["data"]
                    peer_info = "{} :  {}\n".format(sender_name,
                                                    time.strftime("%Y-%m-%d %H:%M:%S",
                                                                  time.localtime()))
                    # 插入到tag: timestamp 位置
                    self.widget_chatted_content.insert(END, peer_info, 'timestamp_peer')
                    # print("message_recv: {}".format(data))
                    data = "{}\n".format(data)
                    self.widget_chatted_content.insert(END, data)

    def load_window(self):
        # ========== 创建窗口 =============
        self.chatting_window = Tk()
        self.chatting_window.title('P2P 聊天软件')  # 窗口名称
        self.chatting_window.geometry("580x500")
        # self.chatting_window.resizable(0, 0)  # 禁止调整窗口大小

        # ========== 创建frame容器 =============
        # 第一列
        frm_a1 = Frame(master=self.chatting_window,
                       width=180, height=30)
        frm_a2 = Frame(master=self.chatting_window,
                       width=180, height=400)
        frm_a3 = Frame(master=self.chatting_window,
                       width=180, height=150)

        # 第二列
        frm_b1 = Frame(master=self.chatting_window,
                       width=350, height=30)
        frm_b2 = Frame(master=self.chatting_window,
                       width=350, height=400)
        frm_b3 = Frame(master=self.chatting_window,
                       width=350, height=120)
        frm_b4 = Frame(master=self.chatting_window,
                       width=350, height=30)

        # ========== 定义各控件 =============
        # Label 控件
        widget_list_title = Label(master=frm_a1, text="联系人列表",
                                  font="Helvetica 12 bold", padx=30)

        self.var_chat_with = tk.StringVar()
        if self.chatting_peer_name is None:
            self.var_chat_with.set("Has not body chatting with you")
        else:
            self.var_chat_with.set("Chatting with: ".format(self.chatting_peer_name))
        # 初始化聊天对象
        widget_chat_side_title = Label(master=frm_b1,
                                       textvariable=self.var_chat_with,
                                       font="Helvetica 12 bold", padx=30)

        # 联系人列表
        # 滚动条 滚动条的宽度（如果是水平，则为y尺寸，如果为垂直，则为x尺寸）
        widget_scro_contact = Scrollbar(master=frm_a2, orient=VERTICAL,
                                        troughcolor="blue",
                                        width=22)

        # Listbox控件 height: 行数 width: 每个字节的大小
        # 连接listbox 到 vertical scrollbar
        self.widget_list_contact = Listbox(master=frm_a2, width=20, height=20,
                                           yscrollcommand=widget_scro_contact.set)

        # 鼠标双击
        self.widget_list_contact.bind('<Double-1>', self.chatting_with_peer)
        # scrollbar滚动时listbox同时滚动
        widget_scro_contact.config(command=self.widget_list_contact.yview)

        self.var_peer_name = tk.StringVar()
        self.var_peer_port = tk.StringVar()
        self.var_peer_name.set("your name: {}".format(self.user_info_obj.user_name))
        self.var_peer_port.set("your port: {}".format(self.user_info_obj.local_port))
        # 初始化聊天对象
        # self.var_peer_name.set("your name: " + "Michael")
        # self.var_peer_port.set("your port:" + "8082")
        widget_name_label = Label(master=frm_a3, textvariable=self.var_peer_name,
                                  font="Helvetica 12 bold",
                                  width=20, height=2)
        widget_port_label = Label(master=frm_a3, textvariable=self.var_peer_port,
                                  font="Helvetica 12 bold",
                                  width=20, height=1)

        # 对方发送过来的消息
        self.var_recv_msg = tk.StringVar()

        widget_scroll_msg = Scrollbar(master=frm_b2, orient=VERTICAL, troughcolor="blue",
                                      width=22)
        # text控件  height: 行数
        global widget_chatted_content_global
        widget_chatted_content_global = Text(frm_b2, width=48, height=26,
                                             yscrollcommand=widget_scroll_msg.set)
        self.widget_chatted_content = widget_chatted_content_global
        # 创建并配置标签tag属性
        widget_chatted_content_global.tag_config('timestamp_peer',  # 标签tag名称
                                                 foreground='green')
        widget_chatted_content_global.tag_config('timestamp_self',  # 标签tag名称
                                                 foreground='blue')
        widget_scroll_msg.config(command=widget_chatted_content_global.yview)
        widget_chatted_content_global.bind('<<get>>', self.receive_msg_event)

        # 消息编辑区
        widget_scroll_msg_edit = Scrollbar(master=frm_b3, orient=VERTICAL, troughcolor="blue",
                                           width=22)
        self.widget_editing_msg = Text(frm_b3, width=50, height=5,
                                       yscrollcommand=widget_scroll_msg_edit.set)
        # 事件绑定，定义快捷键
        self.widget_editing_msg.bind("<KeyPress-Return>", self.send_msg_event)
        widget_scroll_msg_edit.config(command=self.widget_editing_msg.yview)

        # Button 控件
        widget_btn_send = Button(frm_b4, text='发 送', width=8, height=1,
                                 font="Helvetica 9 bold",
                                 padx=2, command=self.send_msg_event)
        widget_btn_ancel = Button(frm_b4, text='取 消', width=8, height=1,
                                  font="Helvetica 9 bold",
                                  padx=2, command=self.cancel_edited_msg)
        widget_btn_exit = Button(frm_b4, text='退 出', width=8, height=1,
                                 font="Helvetica 9 bold",
                                 padx=2, command=self.chatting_window.quit)

        # ========== 窗口布局 =============
        frm_a1.grid(row=0, column=0)
        frm_a2.grid(row=1, column=0)
        frm_a3.grid(row=2, column=0)

        frm_b1.grid(row=0, column=1, columnspan=1)
        frm_b2.grid(row=1, column=1, columnspan=1)
        frm_b3.grid(row=2, column=1, columnspan=1)
        frm_b4.grid(row=3, column=1, columnspan=1, padx=1)

        # ========== 控件布局 =============
        widget_list_title.pack(fill=BOTH)
        widget_chat_side_title.pack(fill=BOTH)

        widget_chatted_content_global.pack(side=LEFT)
        widget_scroll_msg.pack(side=RIGHT, fill=Y)
        self.widget_editing_msg.pack(side=LEFT)
        widget_scroll_msg_edit.pack(side=RIGHT, fill=Y)

        self.widget_list_contact.pack(side=LEFT, fill=BOTH)
        widget_scro_contact.pack(side=RIGHT, fill=Y)

        widget_name_label.pack(side=TOP, fill=BOTH)
        widget_port_label.pack(side=BOTTOM, fill=BOTH)

        widget_btn_send.grid(row=0, column=0, padx=30)
        widget_btn_ancel.grid(row=0, column=1, padx=10)
        widget_btn_exit.grid(row=0, column=2, padx=30)

        # 创建线程去创建监听本地端口的线程
        self.create_server_thread()
        # 创建心跳包的线程
        self.create_heartbeat_thread()
        # 主事件循环
        self.chatting_window.mainloop()


class NewChatting(Chatting):
    """docstring for NewChatting"""

    def __init__(self, user_info_obj, server_info_obj,
                 server_connection_obj, chatting_peer_obj=None):
        super(NewChatting, self).__init__(user_info_obj, server_info_obj,
                                          server_connection_obj)
        self.chatting_peer_obj = chatting_peer_obj

        self.chatting_peer_name = chatting_peer_obj.peer_name
        self.chatting_peer_port = chatting_peer_obj.peer_port
        self.chatting_peer_ip = chatting_peer_obj.peer_ip


    def load_window(self):
        # ========== 创建窗口 =============
        self.chatting_window = Tk()
        self.chatting_window.title('P2P 聊天软件')  # 窗口名称
        self.chatting_window.geometry("580x500")
        # self.chatting_window.resizable(0, 0)  # 禁止调整窗口大小

        # ========== 创建frame容器 =============
        # 第一列
        frm_a1 = Frame(master=self.chatting_window,
                       width=180, height=30)
        frm_a2 = Frame(master=self.chatting_window,
                       width=180, height=400)
        frm_a3 = Frame(master=self.chatting_window,
                       width=180, height=150)

        # 第二列
        frm_b1 = Frame(master=self.chatting_window,
                       width=350, height=30)
        frm_b2 = Frame(master=self.chatting_window,
                       width=350, height=400)
        frm_b3 = Frame(master=self.chatting_window,
                       width=350, height=120)
        frm_b4 = Frame(master=self.chatting_window,
                       width=350, height=30)

        # ========== 定义各控件 =============
        # Label 控件
        widget_list_title = Label(master=frm_a1, text="联系人列表",
                                  font="Helvetica 12 bold", padx=30)

        self.var_chat_with = tk.StringVar()
        print("New chatting_peer_name: {}".format(self.chatting_peer_name))
        if self.chatting_peer_name is None:
            self.var_chat_with.set("Has not body chatting with you")
        else:
            self.var_chat_with.set("Chatting with: ".format(self.chatting_peer_name))
        # 初始化聊天对象
        widget_chat_side_title = Label(master=frm_b1,
                                       textvariable=self.var_chat_with,
                                       font="Helvetica 12 bold", padx=30)

        # 联系人列表
        # 滚动条 滚动条的宽度（如果是水平，则为y尺寸，如果为垂直，则为x尺寸）
        widget_scro_contact = Scrollbar(master=frm_a2, orient=VERTICAL,
                                        troughcolor="blue",
                                        width=22)

        # Listbox控件 height: 行数 width: 每个字节的大小
        # 连接listbox 到 vertical scrollbar
        self.widget_list_contact = Listbox(master=frm_a2, width=20, height=20,
                                           yscrollcommand=widget_scro_contact.set)

        # 鼠标双击
        self.widget_list_contact.bind('<Double-1>', self.chatting_with_peer)
        # scrollbar滚动时listbox同时滚动
        widget_scro_contact.config(command=self.widget_list_contact.yview)

        self.var_peer_name = tk.StringVar()
        self.var_peer_port = tk.StringVar()
        print("New user_name: {}".format(self.user_info_obj.user_name))
        print("New local_port: {}".format(self.user_info_obj.local_port))
        # self.var_peer_name.set("your name: {}".format(self.user_info_obj.user_name))
        # self.var_peer_port.set("your port: {}".format(self.user_info_obj.local_port))
        # 初始化聊天对象
        self.var_peer_name.set("your name: " + "Michael")
        self.var_peer_port.set("your port:" + "8082")
        widget_name_label = Label(master=frm_a3, textvariable=self.var_peer_name,
                                  font="Helvetica 12 bold",
                                  width=20, height=2)
        widget_port_label = Label(master=frm_a3, textvariable=self.var_peer_port,
                                  font="Helvetica 12 bold",
                                  width=20, height=1)

        # 对方发送过来的消息
        self.var_recv_msg = tk.StringVar()

        widget_scroll_msg = Scrollbar(master=frm_b2, orient=VERTICAL, troughcolor="blue",
                                      width=22)
        # text控件  height: 行数
        # 此处不绑定消息接收事件
        self.widget_chatted_content = Text(frm_b2, width=48, height=26,
                                           yscrollcommand=widget_scroll_msg.set)
        # 创建并配置标签tag属性
        self.widget_chatted_content.tag_config('timestamp_peer',  # 标签tag名称
                                               foreground='green')
        self.widget_chatted_content.tag_config('timestamp_self',  # 标签tag名称
                                               foreground='blue')
        widget_scroll_msg.config(command=self.widget_chatted_content.yview)

        # 消息编辑区
        widget_scroll_msg_edit = Scrollbar(master=frm_b3, orient=VERTICAL, troughcolor="blue",
                                           width=22)
        self.widget_editing_msg = Text(frm_b3, width=50, height=5,
                                       yscrollcommand=widget_scroll_msg_edit.set)
        # 事件绑定，定义快捷键
        self.widget_editing_msg.bind("<KeyPress-Return>", self.send_msg_event)
        widget_scroll_msg_edit.config(command=self.widget_editing_msg.yview)

        # Button 控件
        widget_btn_send = Button(frm_b4, text='发 送', width=8, height=1,
                                 font="Helvetica 9 bold",
                                 padx=2, command=self.send_msg_event)
        widget_btn_ancel = Button(frm_b4, text='取 消', width=8, height=1,
                                  font="Helvetica 9 bold",
                                  padx=2, command=self.cancel_edited_msg)
        widget_btn_exit = Button(frm_b4, text='退 出', width=8, height=1,
                                 font="Helvetica 9 bold",
                                 padx=2, command=self.chatting_window.quit)

        # ========== 窗口布局 =============
        frm_a1.grid(row=0, column=0)
        frm_a2.grid(row=1, column=0)
        frm_a3.grid(row=2, column=0)

        frm_b1.grid(row=0, column=1, columnspan=1)
        frm_b2.grid(row=1, column=1, columnspan=1)
        frm_b3.grid(row=2, column=1, columnspan=1)
        frm_b4.grid(row=3, column=1, columnspan=1, padx=1)

        # ========== 控件布局 =============
        widget_list_title.pack(fill=BOTH)
        widget_chat_side_title.pack(fill=BOTH)

        self.widget_chatted_content.pack(side=LEFT)
        widget_scroll_msg.pack(side=RIGHT, fill=Y)
        self.widget_editing_msg.pack(side=LEFT)
        widget_scroll_msg_edit.pack(side=RIGHT, fill=Y)

        self.widget_list_contact.pack(side=LEFT, fill=BOTH)
        widget_scro_contact.pack(side=RIGHT, fill=Y)

        widget_name_label.pack(side=TOP, fill=BOTH)
        widget_port_label.pack(side=BOTTOM, fill=BOTH)

        widget_btn_send.grid(row=0, column=0, padx=30)
        widget_btn_ancel.grid(row=0, column=1, padx=10)
        widget_btn_exit.grid(row=0, column=2, padx=30)

        # 创建心跳包的线程
        self.create_heartbeat_thread()
        # 置聊天对象
        self.set_chatting_peer(self.chatting_peer_name,
                               self.chatting_peer_ip,
                               self.chatting_peer_port)

        # 主事件循环
        self.chatting_window.mainloop()
