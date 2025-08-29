import traceback

from ascript.android.system import R
from ascript.android.ui import WebWindow
import json
from ascript.android.system import Device

from ..service.hoo_sock import HooSock
from ..utils.tools import off
from ..service.xhs.common import on_message_content

def run():
    try:
        formw = WebWindow(R.ui("form.html"), tunnel)
        formw.height("70vh")
        formw.show()
    except Exception as e:
        print(e)
        traceback.print_exc()

def tunnel(k,v):
    try:
        print(k,v)
        if k =="close":
            print(v) # 用户点X关闭了窗口
        elif k =="submit":
            print(v) # 用户点击确定并回传了数据
            resobj = json.loads(v)
            print(resobj)

            def on_message(ws, type, id, option):
                if type == 'xhs_gather_comment':
                    on_message_content(ws, id, option)
                elif type == 'end':
                    off()
                    print('===============================================')
                pass

            # HooSock("ws://192.168.0.101:10102").set_on_message(on_message).start()
            HooSock(f"ws://{resobj.get('ip')}").set_on_message(on_message).start()
    except Exception as e:
        print(e)
        traceback.print_exc()
