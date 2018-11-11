# _*_ coding:utf-8 _*_
# Filename:ClientUI.py
# Python在线聊天客户端
import threading
import tkinter
# import tkFont
import socket
# import thread
import time
import sys


class ClientUI:
    title = 'P2P 聊天软件 客户端'
    local = '127.0.0.1'
    port = 8808
    global clientSock
    flag = False

    # 初始化类的相关属性，类似于Java的构造方法
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title(self.title)

        # 窗口面板,用4个面板布局
        self.frame = [tkinter.Frame(), tkinter.Frame(), tkinter.Frame(), tkinter.Frame()]

        # 显示消息Text右边的滚动条
        self.chatTextScrollBar = tkinter.Scrollbar(self.frame[0])
        self.chatTextScrollBar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # 显示消息Text，并绑定上面的滚动条
        ft = ('Fixdsys', 11)
        self.chatText = tkinter.Listbox(self.frame[0], width=70, height=18, font=ft)
        self.chatText['yscrollcommand'] = self.chatTextScrollBar.set
        self.chatText.pack(expand=1, fill=tkinter.BOTH)
        self.chatTextScrollBar['command'] = self.chatText.yview()
        self.frame[0].pack(expand=1, fill=tkinter.BOTH)

        # 标签，分开消息显示Text和消息输入Text
        label = tkinter.Label(self.frame[1], height=2)
        label.pack(fill=tkinter.BOTH)
        self.frame[1].pack(expand=1, fill=tkinter.BOTH)

        # 输入消息Text的滚动条
        self.inputTextScrollBar = tkinter.Scrollbar(self.frame[2])
        self.inputTextScrollBar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # 输入消息Text，并与滚动条绑定
        ft = ('Fixdsys', 11)
        self.inputText = tkinter.Text(self.frame[2], width=70, height=8, font=ft)
        self.inputText['yscrollcommand'] = self.inputTextScrollBar.set
        self.inputText.pack(expand=1, fill=tkinter.BOTH)
        self.inputTextScrollBar['command'] = self.chatText.yview()
        self.frame[2].pack(expand=1, fill=tkinter.BOTH)

        # 发送消息按钮
        self.sendButton = tkinter.Button(self.frame[3], text=' 发 送 ', width=10, command=self.sendMessage)
        self.sendButton.pack(expand=1, side=tkinter.BOTTOM and tkinter.RIGHT, padx=15, pady=8)

        # 关闭按钮
        self.closeButton = tkinter.Button(self.frame[3], text=' 关 闭 ', width=10, command=self.close)
        self.closeButton.pack(expand=1, side=tkinter.RIGHT, padx=15, pady=8)
        self.frame[3].pack(expand=1, fill=tkinter.BOTH)

        # 接收消息

    def receiveMessage(self):
        try:
            # 建立Socket连接
            self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clientSock.connect((self.local, self.port))
            self.flag = True
        except:
            self.flag = False
            self.chatText.insert(tkinter.END, '您还未与服务器端建立连接，请检查服务器端是否已经启动')
            return

        self.buffer = 1024
        self.clientSock.send('Y')
        while True:
            try:
                if self.flag == True:
                    # 连接建立，接收服务器端消息
                    self.serverMsg = self.clientSock.recv(self.buffer)
                    if self.serverMsg == 'Y':
                        self.chatText.insert(tkinter.END, '客户端已经与服务器端建立连接......')
                    elif self.serverMsg == 'N':
                        self.chatText.insert(tkinter.END, '客户端与服务器端建立连接失败......')
                    elif not self.serverMsg:
                        continue
                    else:
                        theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        self.chatText.insert(tkinter.END, '服务器端 ' + theTime + ' 说：\n')
                        self.chatText.insert(tkinter.END, '  ' + self.serverMsg)
                else:
                    break
            except Exception as e:
                self.clientSock.close()
                raise e

    # 发送消息
    def sendMessage(self):
        # 得到用户在Text中输入的消息
        message = self.inputText.get('1.0', tkinter.END)
        # 格式化当前的时间
        theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.chatText.insert(tkinter.END, '客户端器 ' + theTime + ' 说：\n')
        self.chatText.insert(tkinter.END, '  ' + message + '\n')
        if self.flag == True:
            # 将消息发送到服务器端
            self.clientSock.send(message);
        else:
            # Socket连接没有建立，提示用户
            self.chatText.insert(tkinter.END, '您还未与服务器端建立连接，服务器端无法收到您的消息\n')
            # 清空用户在Text中输入的消息
        self.inputText.delete(0.0, message.__len__() - 1.0)

        # 关闭消息窗口并退出

    def close(self):
        sys.exit()

        # 启动线程接收服务器端的消息

    def startNewThread(self):
        # 启动一个新线程来接收服务器端的消息
        # thread.start_new_thread(function,args[,kwargs])函数原型，
        # 其中function参数是将要调用的线程函数，args是传递给线程函数的参数，它必须是个元组类型，而kwargs是可选的参数
        # receiveMessage函数不需要参数，就传一个空元组
        threading.Thread(target=self.receiveMessage,
                         args=()).start()
        # threading.start_new_thread(self.receiveMessage, ())


def main():
    client = ClientUI()
    client.startNewThread()
    client.root.mainloop()


if __name__ == '__main__':
    main()
