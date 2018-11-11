# -*- coding: utf-8 -*-
# @Time    : 2018/11/10 13:15
# @Author  : MLee
# @File    : UserInfo.py


class UserInfo(object):
    """docstring for UserInfo"""

    def __init__(self, user_name=None, user_password=None,
                 local_port=None):
        self.user_name = user_name
        self.user_password = user_password
        self.local_port = local_port

    def set_user_info(self, user_name, user_password, local_port=None):
        self.user_name = user_name
        self.user_password = user_password
        if local_port is not None:
            self.local_port = local_port

    def set_user_name(self, user_name):
        self.user_name = user_name

    def set_user_password(self, user_password):
        self.user_password = user_password

    def set_local_port(self, local_port):
        self.local_port = local_port

    def is_set_user_info(self):
        if self.user_name is None or self.user_password is None\
                or self.local_port is None:
            return False
        else:
            return True

