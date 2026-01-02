import hashlib
import json
import re
import time
import traceback
from ascript.android.system import R
from android.content import Intent
from android.net import Uri
from ascript.android.node import Selector
from ascript.android.system import Clipboard
from ascript.android import action
from ascript.android.system import Device

from ...utils.tools import out_error, getUserIdByUrl
from .common import check_search, get_note_info, is_note_detail_page
from ..global_context import GCT
from ...utils.tools import parse_chinese_time, date_to_timestamp, timestamp_to_date, generate_guid, check_end, on, send, \
    out_info, run_sel, off, out_success, getNoteIdByUrl, getUrl, getLinkToNoteUrl, t_sleep, run_sel_s, out_warning


def on_message_user_details(ws, option):
    """
        # 发送命令
        web_sock.send_message(client, json.dumps({
            'type': 'xhs_gather_user_details',
            'id': client_id,
            'option': {
                'user_id': user_id,
                'user_url': user_url,
                # 操作  follow
                'op': op,
            }
        }))
    """
    on()
    op = option.get('op')
    if option.get('user_id'):
        user_id = option.get('user_id')
    else:
        user_url = option.get('user_url')
        user_id = getUserIdByUrl(user_url)
    try:
        # 进入这个用户主页内//user/user_id
        uri = Uri.parse(f"xhsdiscover://user/{user_id}")
        it = Intent(Intent.ACTION_VIEW, uri)
        it.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        R.context.startActivity(it)
        out_info(ws, f"正在进入用户主页 {user_id}")
    except Exception as e:
        traceback.print_exc()
        out_error(ws, f"进入这个用户主页 失败 {user_id}")
        send(ws, 'func_phone_xhs_user_follow', {
            'data': {},
        })

    # 等待进入用户主页
    run_sel(lambda: Selector(2).type("TextView").text("私信.*").find())
    print("======================"+op)
    # 分隔字符串
    ops = op.split('&')
    send_type = None
    send_data = {}
    # 进行关注
    if 'follow' in ops:
        # 确认是否已经点赞
        if run_sel(lambda: Selector(2).type("Button").text("已关注.*").find(),re_time=0.1):
            new_follow = False
            # out_warning(ws, f"已经关注过了")
        else:
            new_follow = True
            run_sel(lambda: Selector(2).type("Button").text("关注.*").find()).click()
            # out_success(ws, f"关注成功")

        send_type = 'func_phone_xhs_user_follow'
        send_data['new_follow'] = new_follow

    if send_type:
        send(ws, send_type, {
            'data': send_data,
        })

    print('func_phone_xhs_user')
    pass






