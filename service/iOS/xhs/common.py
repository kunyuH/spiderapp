import hashlib
import json
import re
import time
import traceback
# from ascript.android.system import R
# from android.content import Intent
# from android.net import Uri
from ascript.ios.node import Selector
# from ascript.ios.system import Clipboard
# from ascript.android import action

from ....utils.tools import run_sel, getNoteIdByUrl, getUrl, getLinkToNoteUrl, run_sel_s, generate_guid


def check_search(sort_type,filter_note_type,filter_note_time,filter_note_range):
    # 点击下拉筛选
    Selector().type("XCUIElementTypeButton").label("全部").click(0).find()
    # parent_index = 3
    # if (Selector().type("XCUIElementTypeStaticText").value("最新")
    #         .label("最新").name("最新").visible(True)
    #          .find()):
    #     parent_index = 1
    # 排序依据点击
    if sort_type != 'general':
        if sort_type == 'time_descending':  # 最新
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("最新")
             .label("最新")
             .name("最新")
             .visible(True)
             .click(0).find())
        elif sort_type == 'popularity_descending':  # 最多点赞
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("最多点赞")
             .label("最多点赞")
             .name("最多点赞")
             .visible(True)
             .click(0).find())
        elif sort_type == 'comment_descending':  # 最多评论
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("最多评论")
             .label("最多评论")
             .name("最多评论")
             .visible(True)
             .click(0).find())
        elif sort_type == 'collect_descending':  # 最多收藏
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("最多收藏")
             .label("最多收藏")
             .name("最多收藏")
             .visible(True)
             .click(0).find())
    # 笔记类型点击
    if filter_note_type != '不限':
        if filter_note_type == '视频':  # 视频
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("视频")
             .label("视频")
             .name("视频")
             .visible(True)
             .click(0).find())
        elif filter_note_type == '图文':  # 图文
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("图文")
             .label("图文")
             .name("图文")
             .visible(True)
             .click(0).find())
    # 发布时间点击
    if filter_note_time != '不限':
        if filter_note_time == '一天内':  # 一天内
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("一天内")
             .label("一天内")
             .name("一天内")
             .visible(True)
             .click(0).find())
        elif filter_note_time == '一周内':  # 一周内
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("一周内")
             .label("一周内")
             .name("一周内")
             .visible(True)
             .click(0).find())
        elif filter_note_time == '半年内':  # 半年内
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("半年内")
             .label("半年内")
             .name("半年内")
             .visible(True)
             .click(0).find())
    # 搜索范围点击
    if filter_note_range != '不限':
        if filter_note_range == '已看过':  # 已看过
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("已看过")
             .label("已看过")
             .name("已看过")
             .visible(True)
             .click(0).find())
        elif filter_note_range == '未看过':  # 未看过
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("未看过")
             .label("未看过")
             .name("未看过")
             .visible(True)
             .click(0).find())
        elif filter_note_range == '已关注':  # 已关注
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("已关注")
             .label("已关注")
             .name("已关注")
             .visible(True)
             .click(0).find())
    time.sleep(1)
    # 点击收起
    (Selector()
     .type("XCUIElementTypeStaticText")
     .value("收起")
     .label("收起")
     .name("收起")
     .visible(True)
     .click(0).find())
    # Selector(2).text("收起").type("TextView").parent(1).click().find()
