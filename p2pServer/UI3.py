# -*- coding: utf-8 -*-
# @Time    : 2018/11/9 8:36
# @Author  : MLee
# @File    : UI3.py

import time
import tkinter as tk
from tkinter import *
from tkinter import messagebox


def main():
    # ========== 回调函数定义 =============
    def sendMsg():  # 发送消息
        str_msg = 'you:' + time.strftime("%Y-%m-%d %H:%M:%S",
                                               time.localtime()) + '\n '
        widget_chatted_content.insert(END, str_msg, 'timestamp')  # 插入到tag位置
        widget_chatted_content.insert(END, widget_editing_msg.get('0.0', END))
        widget_editing_msg.delete('0.0', END)

    def cancelMsg():  # 取消消息
        widget_editing_msg.delete('0.0', END)

    def sendMsgEvent(event):  # 发送消息事件
        if event.keysym == "Return":  # 按回车键可发送
            sendMsg()

    def chatting_with(e):
        print(e)
        tk.messagebox.showwarning(title="chatting with",
                                  message="chatting with")
        print("chatting with")

    # ========== 创建窗口 =============
    window = Tk()
    window.title('P2P 聊天软件')  # 窗口名称
    window.geometry("580x500")
    # window.resizable(0, 0)  # 禁止调整窗口大小

    # ========== 创建frame容器 =============
    # 第一列
    frm_a1 = Frame(width=180, height=30)
    frm_a2 = Frame(width=180, height=400)
    frm_a3 = Frame(width=180, height=150)

    # 第二列
    frm_b1 = Frame(width=350, height=30)
    frm_b2 = Frame(width=350, height=400)
    frm_b3 = Frame(width=350, height=120)
    frm_b4 = Frame(width=350, height=30)

    # ========== 定义各控件 =============
    # Label 控件
    widget_list_title = Label(frm_a1, text="联系人列表", font="Helvetica 12 bold", padx=30)

    var_chat_with = tk.StringVar()
    # 初始化聊天对象
    var_chat_with.set("Chatting with: " + "Mike")
    widget_chat_side_title = Label(frm_b1, textvariable=var_chat_with,
                                   font="Helvetica 12 bold", padx=30)

    # 联系人列表
    # 滚动条 滚动条的宽度（如果是水平，则为y尺寸，如果为垂直，则为x尺寸）。 默认值为16。
    widget_scro_contact = Scrollbar(frm_a2, orient=VERTICAL, troughcolor="blue",
                                    width=22)

    # 列表
    # Listbox控件 height: 行数 width: 每个字节的大小
    widget_list_contact = Listbox(frm_a2, width=20, height=20,
                                  yscrollcommand=widget_scro_contact.set)
    # 连接listbox 到 vertical scrollbar

    widget_list_contact.bind('<Double-1>', chatting_with)
    registered_contact_list = ['曹操', '刘备', '孙权', '关羽', '张飞', '赵云', '马超', '黄忠', '张郃', '姜维',
                               '夏侯惇', '魏延', '张辽', '周瑜',
                               '贾诩', '典韦', '吕布',
                               '袁绍', '袁术', '貂蝉', '董卓', '华佗', '诸葛亮', '郭嘉', '孙策', '孙坚', '太史慈',
                               '鲁肃', '黄盖', '程普', '程昱',
                               '司马懿', '曹丕', '曹植',
                               '曹睿']
    for line in registered_contact_list:
        widget_list_contact.insert(END, " 联系人 ------" + str(line))
    # scrollbar滚动时listbox同时滚动
    widget_scro_contact.config(command=widget_list_contact.yview)

    var_your_name = tk.StringVar()
    var_your_port = tk.StringVar()
    # 初始化聊天对象
    var_your_name.set("your name: " + "Michael")
    var_your_port.set("your port:" + "8082")
    weidget_name_label = Label(frm_a3, textvariable=var_your_name, font="Helvetica 12 bold",
                               width=20, height=2)
    weidget_port_label = Label(frm_a3, textvariable=var_your_port, font="Helvetica 12 bold",
                               width=20, height=1)

    # 对方发送过来的消息
    var_recv_msg = tk.StringVar()

    widget_scroll_msg = Scrollbar(frm_b2, orient=VERTICAL, troughcolor="blue",
                                  width=22)
    # text控件  height: 行数
    widget_chatted_content = Text(frm_b2, width=48, height=26,
                                  yscrollcommand=widget_scroll_msg.set)
    # 创建并配置标签tag属性
    widget_chatted_content.tag_config('timestamp',  # 标签tag名称
                                      foreground='#008C00')  # 标签tag前景色，背景色为默认白色
    widget_scroll_msg.config(command=widget_chatted_content.yview)

    # 消息编辑区
    widget_scroll_msg_edit = Scrollbar(frm_b3, orient=VERTICAL, troughcolor="blue",
                                       width=22)
    widget_editing_msg = Text(frm_b3, width=50, height=5,
                              yscrollcommand=widget_scroll_msg_edit.set)
    widget_editing_msg.bind("<KeyPress-Return>", sendMsgEvent)  # 事件绑定，定义快捷键
    widget_scroll_msg_edit.config(command=widget_editing_msg.yview)

    # Button 控件
    widget_btn_send = Button(frm_b4, text='发 送', width=8, height=1,
                             font="Helvetica 9 bold",
                             padx=2, command=sendMsg)
    widget_btn_ancel = Button(frm_b4, text='取 消', width=8, height=1,
                              font="Helvetica 9 bold",
                              padx=2, command=cancelMsg)
    widget_btn_exit = Button(frm_b4, text='退 出', width=8, height=1,
                             font="Helvetica 9 bold",
                             padx=2, command=window.quit)

    # ========== 窗口布局 =============
    frm_a1.grid(row=0, column=0)
    frm_a2.grid(row=1, column=0)
    frm_a3.grid(row=2, column=0)

    frm_b1.grid(row=0, column=1, columnspan=1, rowspan=1)
    frm_b2.grid(row=1, column=1, columnspan=1)
    frm_b3.grid(row=2, column=1, columnspan=1)
    frm_b4.grid(row=3, column=1, columnspan=1, padx=1)

    # ========== 窗口布局 =============
    # 固定大小
    # frm_a1.grid_propagate(0)
    # frm_a2.grid_propagate(0)
    # frm_a3.grid_propagate(0)
    #
    # frm_b1.grid_propagate(0)
    # frm_b2.grid_propagate(0)
    # frm_b3.grid_propagate(0)
    # frm_b4.grid_propagate(0)

    # ========== 控件布局 =============
    widget_list_title.pack(fill=BOTH)
    widget_chat_side_title.pack(fill=BOTH)

    widget_chatted_content.pack(side=LEFT)
    widget_scroll_msg.pack(side=RIGHT, fill=Y)
    widget_editing_msg.pack(side=LEFT)
    widget_scroll_msg_edit.pack(side=RIGHT, fill=Y)

    widget_list_contact.pack(side=LEFT, fill=BOTH)
    widget_scro_contact.pack(side=RIGHT, fill=Y)

    weidget_name_label.pack(side=TOP, fill=BOTH)
    weidget_port_label.pack(side=BOTTOM, fill=BOTH)

    widget_btn_send.grid(row=0, column=0, padx=30)
    widget_btn_ancel.grid(row=0, column=1, padx=10)
    widget_btn_exit.grid(row=0, column=2, padx=30)

    # 主事件循环
    window.mainloop()


if __name__ == '__main__':
    main()
