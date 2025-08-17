#展示一个简单的Html页面
from ascript.android.node import Selector


from ascript.android.ui import WebWindow
from ascript.android.system import R

from .utils.tools import off
# from flask import Flask, request, jsonify
# from threading import Thread

from .service.xhs.common import on_message_content, ip_date
from .service.hoo_sock import HooSock

"""
xhsdiscover://item/123456
"""
def tunnel(k,v):
    print(k)
    print(v)

# 构建一个WebWindow 显示‘/res/ui/a.html’ 通信通道为tunnel 函数
w = WebWindow(R.ui('index.html'),tunnel)
w.show()

def on_message(ws,type,id,option):
    print(1111111)
    print(type)
    if type == 'xhs_gather_comment':
        on_message_content(ws,id,option)
    elif type == 'end':
        off()
        print('===============================================')
    pass

# HooSock("ws://192.168.0.101:10102").set_on_message(on_message).start()
HooSock("ws://192.168.1.70:10102").set_on_message(on_message).start()
