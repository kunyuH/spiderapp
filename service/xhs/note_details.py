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

from ...utils.tools import out_error
from .common import check_search, get_note_info, is_note_detail_page
from ..global_context import GCT
from ...utils.tools import parse_chinese_time, date_to_timestamp, timestamp_to_date, generate_guid, check_end, on, send, \
    out_info, run_sel, off, out_success, getNoteIdByUrl, getUrl, getLinkToNoteUrl, t_sleep, run_sel_s, out_warning


def on_message_note_details(ws, option):
    """
    json_ = {
            "note_id": note_id,
            "note_url": note_url,
            "op": op,       # 数据采集 or 点赞 or 收藏
        }
    """
    on()
    op = option.get('op')
    if option.get('note_id'):
        note_id = option.get('note_id')
    else:
        note_url = option.get('note_url')
        # 判断是否分享过来的链接
        if 'xhslink' in note_url:
            note_url = getLinkToNoteUrl(option={
                'url': note_url
            })
        note_id = getNoteIdByUrl(note_url)
    try:
        # 进入这个笔记内
        uri = Uri.parse(f"xhsdiscover://item/{note_id}")
        it = Intent(Intent.ACTION_VIEW, uri)
        it.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        R.context.startActivity(it)
        out_info(ws, f"正在打开笔记 {note_id}")
    except Exception as e:
        traceback.print_exc()
        out_error(ws, f"进入这个笔记内 失败 {note_id}")
        send(ws, 'func_phone_xhs_note_like', {
            'data': {},
        })

    # 等待进入笔记详情页
    run_sel(lambda: Selector(2).type("Button").desc("评论.*").find())
    print("======================"+op)
    # 分隔字符串
    ops = op.split('&')
    send_type = None
    send_data = {}
    # 进行点赞
    if 'like' in ops:
        # 确认是否已经点赞
        if run_sel(lambda: Selector(2).type("Button").desc("已点赞.*").find(),re_time=0.1):
            new_like = False
            # out_warning(ws, f"已经点过赞了")
        else:
            new_like = True
            run_sel(lambda: Selector(2).type("Button").desc("点赞.*").find()).click()
            # out_success(ws, f"点赞成功")

        send_type = 'func_phone_xhs_note_like'
        send_data['new_like'] = new_like

    if 'collect' in ops:      # 进行收藏
        # 确认是否已经收藏
        if run_sel(lambda: Selector(2).type("Button").desc("已收藏.*").find(), re_time=0.1):
            new_collect = False
            # out_warning(ws, f"已经收藏过了")
        else:
            new_collect = True
            run_sel(lambda: Selector(2).type("Button").desc("收藏.*").find()).click()
            # out_success(ws, f"收藏成功")

        send_type = 'func_phone_xhs_note_like'
        send_data['new_collect'] = new_collect

    if op == 'detail':
        note_info = {
            '标题': '',
            '封面图': '',
            '用户主页链接': '',
            '用户ID': '',
            '发布时间': '',
            '点赞数': '',
        }
        # 获取笔记
        note_info = get_note_info(note_info, False)
        gather_note = {
            '来源': note_info.get('来源'),
            '标题': note_info.get('标题'),
            '内容': note_info.get('内容'),
            '用户名称': note_info.get('用户名称'),
            '发布时间': note_info.get('发布时间'),
            '点赞数': note_info.get('点赞数'),
            '收藏数': note_info.get('收藏数'),
            '评论数': note_info.get('评论数'),
            '分享数': note_info.get('分享数'),
            '类型': note_info.get('类型'),

            '笔记ID': note_info.get('笔记ID'),
            '笔记链接': note_info.get('笔记链接'),
            '笔记分享链接': note_info.get('笔记分享链接'),

            '用户小红书号': note_info.get('用户小红书号'),
            '用户IP属地': note_info.get('用户IP属地'),
            '用户简介': note_info.get('用户简介'),
            '用户性别': note_info.get('用户性别'),
            '用户关注': note_info.get('用户关注'),
            '用户粉丝': note_info.get('用户粉丝'),
            '用户获赞与收藏': note_info.get('用户获赞与收藏'),
            '是否有店铺': note_info.get('是否有店铺'),
            '店铺名称': note_info.get('店铺名称'),
            '店铺星级': note_info.get('店铺星级'),
            '店铺已售': note_info.get('店铺已售'),
            '店铺粉丝': note_info.get('店铺粉丝'),
        }
        send_type = 'func_phone_xhs_note_like'
        send_data = gather_note

    if send_type:
        send(ws, send_type, {
            'data': send_data,
        })

    print('func_phone_xhs_note')
    pass






