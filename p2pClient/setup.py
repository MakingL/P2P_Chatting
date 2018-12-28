# -*- coding: utf-8 -*-
# @Time    : 2018/11/13 9:03
# @Author  : MLee
# @File    : setup.py

from distutils.core import setup
import py2exe

setup(console=['client.py'],
      zipfile=None,
      options={'py2exe': {
          "bundle_files": 1,
          "dll_excludes": ["MSVCP90.dll", "w9xpopen.exe"]
      }
      }
      )
