# -*- coding: utf-8 -*-
# @Time    : 2018/11/10 13:30
# @Author  : MLee
# @File    : LoginAndSignUp.py
import random
import tkinter as tk
from tkinter import messagebox


class LoginAndSignUp(object):
    """docstring for LoginAndSignUp"""

    def __init__(self, user_info_obj, server_info_obj, server_connection_obj):
        self.user_info_obj = user_info_obj
        self.server_info_obj = server_info_obj
        self.server_connection_obj = server_connection_obj

        # 登录界面信息
        self.login_window = None
        self.var_usr_name = None
        self.widget_entry_usr_name = None
        self.widget_entry_usr_pwd = None
        self.var_usr_pwd = None
        self.var_server_ip = None
        self.widget_entry_server_ip = None
        self.var_server_port = None
        self.widget_entry_server_port = None
        self.var_local_port = None
        self.widget_entry_local_port = None
        self.welcome_image = "./image/welcome.gif"

        # 注册界面信息
        self.sign_up_window = None
        self.var_new_usr_name = None
        self.widget_new_name_entry = None
        self.var_new_pwd = None
        self.widget_new_usr_pwd_entry = None
        self.widget_new_pwd_confirm_entry = None

    def load_window(self):
        """
        加载登录界面,进入主循环
        :return:
        """

        self.login_window = tk.Tk()
        self.login_window.title('Login and Sign up')
        self.login_window.geometry('450x320')

        frm_1 = tk.Frame(master=self.login_window,
                         width=450, height=140)
        frm_2 = tk.Frame(master=self.login_window,
                         width=430, height=80)
        frm_3 = tk.Frame(master=self.login_window,
                         width=430, height=30)

        frm_1.grid(row=0, column=0)
        frm_2.grid(row=1, column=0)
        frm_3.grid(row=2, column=0, pady=15)

        # welcome image
        canvas = tk.Canvas(frm_1, width=450, height=140)
        image_file = tk.PhotoImage(file=self.welcome_image)
        image = canvas.create_image(0, 0, anchor="nw", image=image_file)
        canvas.pack()

        # user information
        # 提示框
        widget_user_name_label = tk.Label(frm_2, text='User name: ',
                                          font="Helvetica 9 bold")
        widget_user_passwd_label = tk.Label(frm_2, text='Password: ',
                                            font="Helvetica 9 bold")

        # 用户名 密码 输入框
        self.var_usr_name = tk.StringVar()
        self.var_usr_name.set('Example')
        self.widget_entry_usr_name = tk.Entry(frm_2,
                                              textvariable=self.var_usr_name)
        self.var_usr_pwd = tk.StringVar()
        self.widget_entry_usr_pwd = tk.Entry(frm_2,
                                             textvariable=self.var_usr_pwd,
                                             show='*')

        widget_user_name_label.grid(row=0, column=0)
        self.widget_entry_usr_name.grid(row=0, column=1)
        widget_user_passwd_label.grid(row=1, column=0)
        self.widget_entry_usr_pwd.grid(row=1, column=1)

        # 服务器信息
        widget_server_ip_label = tk.Label(frm_2, text='Server IP: ',
                                          font="Helvetica 9 bold")
        widget_server_port_label = tk.Label(frm_2, text='Server port: ',
                                            font="Helvetica 9 bold")

        # 服务器 IP 端口号
        self.var_server_ip = tk.StringVar()
        self.var_server_ip.set('127.0.0.1')
        self.widget_entry_server_ip = tk.Entry(frm_2,
                                               textvariable=self.var_server_ip)
        self.var_server_port = tk.StringVar()
        # 设置服务器端口号默认值
        self.var_server_port.set(45354)
        self.widget_entry_server_port = tk.Entry(frm_2,
                                                 textvariable=self.var_server_port)

        widget_server_ip_label.grid(row=2, column=0)
        self.widget_entry_server_ip.grid(row=2, column=1)
        widget_server_port_label.grid(row=3, column=0)
        self.widget_entry_server_port.grid(row=3, column=1)

        # 本地监听的 端口号
        widget_local_port_label = tk.Label(frm_2, text='Local listening port: ',
                                           font="Helvetica 9 bold")

        # 本地监听的 端口号
        self.var_local_port = tk.StringVar()
        random_num = random.randint(0, 1024)
        random_port_num = 50000 + random_num
        self.var_local_port.set(random_port_num)
        self.widget_entry_local_port = tk.Entry(frm_2,
                                                textvariable=self.var_local_port)
        widget_local_port_label.grid(row=4, column=0)
        self.widget_entry_local_port.grid(row=4, column=1)

        # login and sign up button
        widget_btn_login = tk.Button(frm_3, text='Login', command=self.usr_login,
                                     width=8, height=1,
                                     font="Helvetica 9 bold")
        widget_btn_sign_up = tk.Button(frm_3, text='Sign up', command=self.usr_sign_up,
                                       width=8, height=1,
                                       font="Helvetica 9 bold")
        widget_btn_exit = tk.Button(frm_3, text='Exit', command=self.login_window.quit,
                                    width=8, height=1,
                                    font="Helvetica 9 bold")
        widget_btn_login.grid(row=0, column=0, padx=10)
        widget_btn_sign_up.grid(row=0, column=1, padx=10)
        widget_btn_exit.grid(row=0, column=2, padx=10)

        self.login_window.mainloop()

    def get_server_info(self):
        server_ip = self.var_server_ip.get()
        server_port = self.var_server_port.get()

        if server_ip is None or len(server_ip) == 0:
            tk.messagebox.showwarning(title="Server ip is empty",
                                      message="Server ip is empty, please input server ip")
            return False
        if server_port is None or len(server_port) == 0:
            tk.messagebox.showwarning(title="Server port is empty",
                                      message="Server port is empty, please input server port")
            return False

        server_port = int(server_port)

        return server_ip, server_port

    def get_local_host(self):
        local_port = self.var_local_port.get()

        if local_port is None or len(local_port) == 0:
            tk.messagebox.showwarning(title="Local port is empty",
                                      message="Local port that local host listening is empty,"
                                              " please input local port")
            return False

        local_port = int(local_port)
        return local_port

    def usr_login(self):
        usr_name = self.var_usr_name.get()
        usr_pwd = self.var_usr_pwd.get()

        if usr_name is None or len(usr_name) == 0:
            tk.messagebox.showwarning(title="User name is empty",
                                      message="User name is empty, please input user name")
            return False
        if usr_pwd is None or len(usr_pwd) == 0:
            tk.messagebox.showwarning(title="Password is empty",
                                      message="Password is empty, please input password")
            return False

        # 发起登录请求
        # 从界面上获取服务器信息
        server_ip, server_port = self.get_server_info()
        local_port = self.get_local_host()

        # 设置服务器信息
        self.server_info_obj.set_server_info(server_ip, server_port)

        # 设置连接对象中的服务器信息
        self.server_connection_obj.set_server_info(server_ip, server_port)

        # 发起请求
        feedback = self.server_connection_obj.login_peer(usr_name, usr_pwd)
        if feedback["status"] is True:
            # 登录成功
            tk.messagebox.showinfo(title='Login success',
                                   message="Login success! Let's start chatting")
            # 设置用户信息 保存已经登录的用户信息
            self.user_info_obj.set_user_info(usr_name, usr_pwd, local_port)
            # 关闭注册登录界面
            self.login_window.destroy()
        else:
            if feedback["code"] == "402":
                # 用户密码不正确
                tk.messagebox.showwarning(title="Login failed",
                                          message='Your password is wrong, try again.')
            elif feedback["code"] == "404":
                # 用户名不存在
                is_sign_up = tk.messagebox.askyesno(title="User name unregistered",
                                                    message="You have not signed up yet. Sign up now?")
                if is_sign_up:
                    self.usr_sign_up()
            else:
                # 未知错误
                tk.messagebox.showwarning(title="Unknown error",
                                          message='Unknown error!')

    def usr_sign_up(self):
        # 注册界面加载
        self.sign_up_window = tk.Toplevel(self.login_window)
        self.sign_up_window.geometry('330x180')
        self.sign_up_window.title('Sign up')

        sign_up_frm1 = tk.Frame(master=self.sign_up_window, width=200, height=80)
        sign_up_frm2 = tk.Frame(master=self.sign_up_window, width=200, height=50)

        sign_up_frm1.grid(row=0, column=0, pady=30, padx=30)
        sign_up_frm2.grid(row=1, column=0, pady=0, padx=30)

        self.var_new_usr_name = tk.StringVar()
        self.var_new_usr_name.set('UserName')
        widget_new_name_label = tk.Label(sign_up_frm1, text='User name: ')
        self.widget_new_name_entry = tk.Entry(sign_up_frm1,
                                              textvariable=self.var_new_usr_name)

        self.var_new_pwd = tk.StringVar()
        widget_password_label = tk.Label(sign_up_frm1, text='Password: ')
        self.widget_new_usr_pwd_entry = tk.Entry(sign_up_frm1,
                                                 textvariable=self.var_new_pwd, show='*')

        new_pwd_confirm = tk.StringVar()
        widget_confirm_password_label = tk.Label(sign_up_frm1, text='Confirm password: ')
        self.widget_new_pwd_confirm_entry = tk.Entry(sign_up_frm1,
                                                     textvariable=new_pwd_confirm, show='*')

        widget_new_name_label.grid(row=0, column=0)
        self.widget_new_name_entry.grid(row=0, column=1)
        widget_password_label.grid(row=1, column=0)
        self.widget_new_usr_pwd_entry.grid(row=1, column=1)
        widget_confirm_password_label.grid(row=2, column=0)
        self.widget_new_pwd_confirm_entry.grid(row=2, column=1)

        sign_up_btn = tk.Button(sign_up_frm2, text='Sign up',
                                command=self.sign_up_to_server)
        cancel_sign_up_btn = tk.Button(sign_up_frm2, text='Cancel',
                                       command=self.cancel_sign_up)

        sign_up_btn.grid(row=0, column=0, padx=30)
        cancel_sign_up_btn.grid(row=0, column=1, padx=30)

    def sign_up_to_server(self):
        new_name = self.widget_new_name_entry.get()
        new_password = self.widget_new_usr_pwd_entry.get()
        new_confirm_pwd = self.widget_new_pwd_confirm_entry.get()

        # 验证数据有效性
        if new_name is None or len(new_name) == 0:
            tk.messagebox.showwarning(title="User name is empty",
                                      message="User name is empty, please input user name")
            return False
        if new_password is None or len(new_password) == 0:
            tk.messagebox.showwarning(title="Password is empty",
                                      message="Password is empty, please input password")
            return False
        if new_confirm_pwd is None or len(new_confirm_pwd) == 0:
            tk.messagebox.showwarning(title="Password is empty",
                                      message="Password is empty, please input password again")
            return False

        if new_password != new_confirm_pwd:
            tk.messagebox.showerror(title="Password is not same",
                                    message='Password and confirm password must be the same!')
            return False

        # 从界面上获取服务器信息
        server_ip, server_port = self.get_server_info()

        # 设置服务器信息
        self.server_info_obj.set_server_info(server_ip, server_port)

        # 设置连接对象中的服务器信息
        self.server_connection_obj.set_server_info(server_ip, server_port)

        feedback = self.server_connection_obj.register_peer(new_name, new_password)
        if feedback is True:
            # 注册成功
            tk.messagebox.showinfo(title="Register successfully",
                                   message='You have successfully signed up! Please login')
            self.sign_up_window.destroy()
        else:
            # 注册失败
            tk.messagebox.showerror(title="User name has been registered",
                                    message='The user name has already been signed up!')

    def cancel_sign_up(self):
        self.sign_up_window.destroy()


if __name__ == '__main__':
    from PeerManager.ServerConnection import ServerConnection
    from PeerManager.ServerInfo import ServerInfo
    from PeerManager.UserInfo import UserInfo

    user_info = UserInfo()
    server_info = ServerInfo()
    server_connection = ServerConnection()
    login_obj = LoginAndSignUp(user_info, server_info, server_connection)

    login_obj.load_window()

    if user_info.is_set_user_info() and server_info.is_set_server_info():
        print("OK")
    else:
        print("False")



