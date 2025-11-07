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

from .common import check_search, get_note_info, is_note_detail_page
from ..global_context import GCT
from ...utils.tools import parse_chinese_time, date_to_timestamp, timestamp_to_date, generate_guid, check_end, on, send, \
    out_info, run_sel, off, out_success, getNoteIdByUrl, getUrl, getLinkToNoteUrl, t_sleep, run_sel_s


def on_message_note(ws, option):
    """
    json_ = {
            "note_id": note_id,
            "op": op,       # 数据采集 or 点赞 or 收藏
        }
    """
    on()
    note_id = option.get('note_id')
    op = option.get('op')

    # 进入这个笔记内
    uri = Uri.parse(f"xhsdiscover://item/{note_id}")
    it = Intent(Intent.ACTION_VIEW, uri)
    it.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    R.context.startActivity(it)
    out_info(ws, f"正在打开笔记 {note_id}")

    # 等待进入笔记详情页
    run_sel(lambda: Selector(2).type("Button").desc("评论.*").find())

    # 进行点赞
    if op == 'like':
        new_like  = False
        # todo 确认是否已经点赞

        run_sel(lambda: Selector(2).type("Button").desc("点赞.*").find()).click()
        out_success(ws, f"点赞成功")

        send(ws, 'func_phone_xhs_note_like', {
            'data': {
                'new_like':new_like
            },
        })

    print('func_phone_xhs_note')
    pass






