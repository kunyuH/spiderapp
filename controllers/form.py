import traceback

from ascript.android.system import R
from ascript.android.ui import WebWindow
import json
from ascript.android.ui import FloatWindow
from ascript.android.ui import Dialog
from ascript.android.system import Device

from ..service.global_context import GCT
from ..service.xhs.note import on_message_note
from ..service.hoo_sock import HooSock
from ..utils.tools import off
from ..service.xhs.common import on_message_content

def run():
    try:
        def show_name():
            Dialog.confirm(f"名称：{GCT().get('app_uuid')}", None, "确认")

        # 点击显示名称
        FloatWindow.add_menu("名称", R.img("P.png"), show_name)

        formw = WebWindow(R.ui("form.html"), tunnel)
        formw.height("70vh")
        formw.show()

        # 调用 javascript 中的 函数 fun1 ,并传入参数 "自在老师",2
        formw.call('fun1("自在老师",2)')

    except Exception as e:
        print(e)
        traceback.print_exc()

def tunnel(k,v=None):
    try:
        print(k,v)
        if k =="close":
            print(v) # 用户点X关闭了窗口
        elif k =="set_app_uuid":
            GCT().set('app_uuid',v)
        elif k =="submit":
            print(v) # 用户点击确定并回传了数据
            resobj = json.loads(v)
            print(resobj)
            app_uuid = resobj.get('app_uuid')

            def on_message(ws, type, id, option):
                if type == 'xhs_gather_note':
                    on_message_note(ws, id, option)
                if type == 'xhs_gather_comment':
                    on_message_content(ws, id, option)
                elif type == 'end':
                    off()
                    print('===============================================')
                pass
            HooSock(f"ws://{resobj.get('ip')}",app_uuid).set_on_message(on_message).start()
    except Exception as e:
        print(e)
        traceback.print_exc()
