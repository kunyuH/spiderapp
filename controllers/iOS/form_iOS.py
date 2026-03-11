import sys
import time
import traceback
import json

from ascript.ios.system import R
from ascript.ios.ui import WebWindow

from ...utils.tools import off
from ...utils.ui_helper import UIHelper
from ...service.global_context import GCT

from ...service.iOS.xhs.note import on_message_note
# from ...service.xhs.user_details import on_message_user_details
# from ...service.xhs.note_details import on_message_note_details
# from ...service.dy.phone_gather import on_message_op
# from ...service.xhs.dm import on_message_dm
# from ...service.xhs.comment import on_message_content

def run():
    try:
        # 初始化 iOS UI Helper
        UIHelper.init_ios()

        # 创建独立的 alert window（隐藏，用于弹窗）
        alert_win = WebWindow(R.ui("alert.html"), alert_tunnel)
        UIHelper.set_alert_window(alert_win)
        alert_win.show()
        time.sleep(0.3)  # 等待 alert window 初始化

        form = WebWindow(R.ui("form.html"), tunnel)
        form.show()
        time.sleep(0.5)
        # 调用 javascript 中的 函数
        form.call(f'init_platform("{sys.platform}")')

    except Exception as e:
        print(e)
        traceback.print_exc()

def alert_tunnel(k, v=None):
    """alert window 的回调通道（一般不使用）"""
    if k == 'alert_ready':
        print("Alert window 已就绪")

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

            def on_message(ws, type, option):
                if type == 'xhs_gather_note':                     # 关键词采集笔记
                    on_message_note(ws, option)
                # if type == 'xhs_gather_comment':                  # 帖子id 采集评论
                #     on_message_content(ws, option)
                # if type == 'xhs_gather_note_details':             # 帖子id 采集详情 or 点赞 or 收藏 or 评论
                #     on_message_note_details(ws, option)
                # if type == 'xhs_gather_user_details':             # 用户id 采集用户信息 or 关注
                #     on_message_user_details(ws, option)
                # if type == 'xhs_dm_comment':                      # 帖子user id 私信
                #     on_message_dm(ws, option)
                # if type == 'dy_yy_phone_gather_by_phone_device':  # 定制-快手运营-店铺手机号采集
                #     on_message_op(ws, option)
                if type == 'end':
                    off()
                    print('===============================================')
                pass

            from ...service.hoo_sock import HooSock
            HooSock(f"ws://{resobj.get('ip')}:{resobj.get('port')}",app_uuid).set_on_message(on_message).start()
    except Exception as e:
        print(e)
        traceback.print_exc()
