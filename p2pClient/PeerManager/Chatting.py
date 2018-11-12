# -*- coding: utf-8 -*-
# @Time    : 2018/11/10 17:00
# @Author  : MLee
# @File    : Chatting.py
import threading
import time
import tkinter as tk
from queue import Queue
from tkinter import *
from tkinter import messagebox

from PeerManager.ServerConnection import ServerConnection


class Chatting(object):
    """docstring for Chatting"""

    def __init__(self, user_info_obj, server_info_obj,
                 server_connection_obj, window_manager,
                 chatting_peer_name=None):

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

        self.widget_name_label = None
        self.widget_port_label = None
        self.widget_scro_contact = None
        self.widget_scroll_msg = None
        self.widget_scroll_msg_edit = None

        self.widget_list_contact = None
        self.widget_chatted_content = None
        self.widget_editing_msg = None

        # 正在聊天的对象信息
        self.chatting_peer_name = chatting_peer_name
        self.chatting_peer_port = None
        self.chatting_peer_ip = None

        self.chatting_connection = None

        # 当前活跃的节点信息
        self.active_peer_node_info = dict()

        self.message_queue = Queue()
        self.window_manager = window_manager
        # 界面窗口操作锁
        self._window_load_lock = threading.Lock()

    def refresh_contact_list_info(self, peer_list_info):
        active_peer_name_set = set()
        self.active_peer_node_info.clear()
        for peer_node in peer_list_info:
            # 此处的 peer list 要除去自己
            if peer_node["name"] == self.user_info_obj.user_name:
                continue

            # 将收到的节点添加到集合
            active_peer_name_set.add(peer_node["name"])
            node_info = (peer_node["ip"], peer_node["port"])

            self.active_peer_node_info[peer_node["name"]] = node_info

        self.update_peer_list(active_peer_name_set)

    def update_peer_list(self, active_peer_name_set):
        with self._window_load_lock:
            if self.widget_list_contact is None:
                return False

            self.widget_list_contact.delete(first=0, last=END)
            for active_peer_name in active_peer_name_set:
                self.widget_list_contact.insert(END, "  {}".format(active_peer_name))

    def set_info(self, user_info_obj, server_info_obj,
                 server_connection_obj, chatting_peer_name):
        self.user_info_obj = user_info_obj
        self.server_info_obj = server_info_obj
        self.server_connection_obj = server_connection_obj
        self.chatting_peer_name = chatting_peer_name

        with self._window_load_lock:
            self.var_peer_name.set("your name: {}".format(self.user_info_obj.user_name))
            self.var_peer_port.set("your port: {}".format(self.user_info_obj.local_port))

        peer_info = self.active_peer_node_info[chatting_peer_name]
        peer_ip, peer_port = peer_info
        self.set_chatting_peer(chatting_peer_name, peer_ip, peer_port)

    def put_message(self, message):
        """
        添加消息
        :param message:
        :return:
        """
        # 将消息添加到自己的消息队列中
        self.message_queue.put(message)

        with self._window_load_lock:
            # 产生获得消息事件
            self.widget_chatted_content.event_generate("<<get_message>>")

    def create_chatting_thread(self):
        """
        创建线程加载聊天界面
        :return:
        """
        chatting_window_thread = threading.Thread(target=self.load_window,
                                                  args=())
        chatting_window_thread.start()

    def set_chatting_peer(self, peer_name, peer_ip, peer_port):
        """
        设置当前聊天对象
        :param peer_name: 聊天对象名字
        :param peer_ip: 聊天对象 IP
        :param peer_port: 聊天对象端口
        :return:
        """
        self.chatting_peer_name = peer_name
        self.chatting_peer_port = peer_port
        self.chatting_peer_ip = peer_ip

        # 聊天对象
        with self._window_load_lock:
            self.var_chat_with.set("Chat with: {}".format(peer_name))
        # 建立与聊天对象的连接
        self.chatting_connection = ServerConnection(peer_ip, peer_port)
        self.chatting_connection.connect_server()

    def has_chatting_peer(self):
        """
        当前窗口是否有对象
        :return:
        """
        if self.chatting_peer_name is None or \
                self.chatting_peer_ip is None or \
                self.chatting_peer_port is None:
            return False
        else:
            return True

    def chatting_with_peer(self, event):
        """
        产生与节点聊天的事件 --- 主动发起
        :param event: 事件对象
        :return:
        """
        curse_index = self.widget_list_contact.curselection()
        if curse_index == 0:
            # 获取光标位置的信息失败
            return False

        # 光标所在列的值
        value = self.widget_list_contact.get(curse_index)
        value = value.strip("\n ")
        tk.messagebox.showinfo(title="chatting with peer",
                               message="chatting with: {}".format(value))

        if self.chatting_peer_name is None:
            peer_info = self.active_peer_node_info[value]
            peer_ip, peer_port = peer_info
            self.set_chatting_peer(value, peer_ip, peer_port)
            self.window_manager.set_window_connection(self, value)
        else:

            active_peer_list = list()
            for name, info in self.active_peer_node_info.items():
                ip, port = info
                active_peer_list.append({"name": name, "ip": ip, "port": port})
            self.window_manager.create_new_chatting_window(self.user_info_obj,
                                                           self.server_info_obj,
                                                           self.server_connection_obj,
                                                           self.window_manager,
                                                           value,
                                                           active_peer_list)

    def send_message_to_peer(self, message):  # 发送消息
        if self.chatting_connection is None:
            if self.chatting_peer_name is not None:
                # 建立连接
                peer_info = self.active_peer_node_info[self.chatting_peer_name]
                peer_ip, peer_port = peer_info
                self.set_chatting_peer(self.chatting_peer_name, peer_ip, peer_port)

                # 发送消息
                self.chatting_connection.send_chatting_message(message,
                                                               self.peer_name)
                return True
            else:
                return False
        else:
            self.chatting_connection.send_chatting_message(message,
                                                           self.peer_name)
            return True

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
        while not self.message_queue.empty():
            message_info = self.message_queue.get()
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
                    # 收到的消息不是正在聊天的对象

                if is_chatting_peer_message is True:
                    data = message_info["data"]
                    peer_info = "{} :  {}\n".format(sender_name,
                                                    time.strftime("%Y-%m-%d %H:%M:%S",
                                                                  time.localtime()))
                    # 插入到tag: timestamp 位置
                    self.widget_chatted_content.insert(END, peer_info, 'timestamp_peer')
                    data = "{}\n".format(data)
                    self.widget_chatted_content.insert(END, data)

    def load_window(self):
        # 窗口加载锁
        self._window_load_lock.acquire()

        # ========== 创建窗口 =============
        self.chatting_window = Tk()
        self.chatting_window.title('P2P 聊天软件')  # 窗口名称
        self.chatting_window.geometry("580x500")
        self.chatting_window.resizable(0, 0)  # 禁止调整窗口大小

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

        self.var_peer_name = tk.StringVar()
        self.var_peer_port = tk.StringVar()
        self.var_peer_name.set("your name: {}".format(self.peer_name))
        self.var_peer_port.set("your port: {}".format(self.peer_port))

        # 初始化节点信息
        self.widget_name_label = Label(master=frm_a3, textvariable=self.var_peer_name,
                                       font="Helvetica 12 bold",
                                       width=20, height=2)
        self.widget_port_label = Label(master=frm_a3, textvariable=self.var_peer_port,
                                       font="Helvetica 12 bold",
                                       width=20, height=1)

        # 联系人列表
        # 滚动条 滚动条的宽度（如果是水平，则为y尺寸，如果为垂直，则为x尺寸）
        self.widget_scro_contact = Scrollbar(master=frm_a2, orient=VERTICAL,
                                             troughcolor="blue",
                                             width=22)

        # Listbox控件 height: 行数 width: 每个字节的大小
        # 连接listbox 到 vertical scrollbar
        self.widget_list_contact = Listbox(master=frm_a2, width=20, height=20,
                                           yscrollcommand=self.widget_scro_contact.set)

        # 鼠标双击
        self.widget_list_contact.bind('<Double-1>', self.chatting_with_peer)
        # scrollbar滚动时listbox同时滚动
        self.widget_scro_contact.config(command=self.widget_list_contact.yview)

        # 对方发送过来的消息
        self.var_recv_msg = tk.StringVar()

        self.widget_scroll_msg = Scrollbar(master=frm_b2, orient=VERTICAL, troughcolor="blue",
                                           width=22)
        # text控件  height: 行数
        self.widget_chatted_content = Text(frm_b2, width=48, height=26,
                                           yscrollcommand=self.widget_scroll_msg.set)
        # 创建并配置标签tag属性
        self.widget_chatted_content.tag_config('timestamp_peer',  # 标签tag名称
                                               foreground='green')
        self.widget_chatted_content.tag_config('timestamp_self',  # 标签tag名称
                                               foreground='blue')
        self.widget_scroll_msg.config(command=self.widget_chatted_content.yview)
        self.widget_chatted_content.bind('<<get_message>>', self.receive_msg_event)

        # 消息编辑区
        self.widget_scroll_msg_edit = Scrollbar(master=frm_b3, orient=VERTICAL, troughcolor="blue",
                                                width=22)
        self.widget_editing_msg = Text(frm_b3, width=50, height=5,
                                       yscrollcommand=self.widget_scroll_msg_edit.set)
        # 事件绑定，定义快捷键
        self.widget_editing_msg.bind("<KeyPress-Return>", self.send_msg_event)
        self.widget_scroll_msg_edit.config(command=self.widget_editing_msg.yview)

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
        self.widget_scroll_msg.pack(side=RIGHT, fill=Y)
        self.widget_editing_msg.pack(side=LEFT)
        self.widget_scroll_msg_edit.pack(side=RIGHT, fill=Y)

        self.widget_list_contact.pack(side=LEFT, fill=BOTH)
        self.widget_scro_contact.pack(side=RIGHT, fill=Y)

        self.widget_name_label.pack(side=TOP, fill=BOTH)
        self.widget_port_label.pack(side=BOTTOM, fill=BOTH)

        widget_btn_send.grid(row=0, column=0, padx=30)
        widget_btn_ancel.grid(row=0, column=1, padx=10)
        widget_btn_exit.grid(row=0, column=2, padx=30)

        # 窗口加载完成，释放锁
        self._window_load_lock.release()

        # 主事件循环
        self.chatting_window.mainloop()
