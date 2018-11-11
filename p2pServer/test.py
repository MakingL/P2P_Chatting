# -*- coding: utf-8 -*-
# @Time    : 2018/11/10 19:45
# @Author  : MLee
# @File    : test.py

import threading
# -*- coding: UTF-8 -*-
from tkinter import *  # 引入模块

x = ""  # 储存命令行传来的字符
running = True  # 判断tkinter界面是否还在运行


def getinput():
    # 这个线程用以监听命令行输入,并发送event给tkinter
    global x, running
    while running:
        x = input()
        if running:
            lb.event_generate("<<get>>")
        else:
            return


def callback(event):  # 吧命令行的输入放入listbox中
    global x
    lb.insert(0, x)
    print("put %s in lb, ok!" % x)


def close():  # 关闭窗口
    global running, top
    running = False
    top.destroy()  # 绑定了WM_DELETE_WINDOW后需要手动关闭,否则窗口会一直存在


top = Tk()  # 主窗口
top.geometry('200x400')  # 设置了主窗口的初始大小600x400
lb = Listbox(top)  # 设置标签字体的初始大小
lb.insert(0, "Hello")
lb.pack(fill=Y, expand=1)
lb.bind('<<get>>', callback)  # 自定义的event 需要<<something>>的形式
top.protocol("WM_DELETE_WINDOW", close)  # 关闭窗口时改变running的值

y = threading.Thread(target=getinput)

y.start()
lb.mainloop()
