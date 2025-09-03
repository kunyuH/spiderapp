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

from ...utils.tools import parse_chinese_time, date_to_timestamp, timestamp_to_date, generate_guid, check_end, on, send, \
    out_info


def on_message_note(ws, option):
    print(option)
    on()
    note_id = option.get('note_id')
    maxPage = option.get('maxPage')
    follow_time = option.get('follow_time')  # 评论时间 限制
    comment_search_keyword = option.get('comment_search_keyword')  # 评论关键词
    comment_not_search_keyword = option.get('comment_not_search_keyword')  # 评论搜索排除关键字
    comment_not_user_name = option.get('comment_not_user_name')  # 评论人昵称排除关键字
    comment_ip_search = option.get('comment_ip_search')  # 评论ip搜索关键字
    comment_word_num = option.get('comment_word_num')  # 评论字数小于

    max_num = maxPage * 10
    # Selector.cache(False)
    # 进入这个笔记内
    uri = Uri.parse(f"xhsdiscover://item/{note_id}")
    it = Intent(Intent.ACTION_VIEW, uri)
    it.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    R.context.startActivity(it)
    out_info(ws, f"正在打开笔记 {note_id}")

    gather_comment = []


    pass