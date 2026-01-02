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

from ...utils.tools import run_sel, getNoteIdByUrl, getUrl, getLinkToNoteUrl, run_sel_s

def get_note_info(note_info=None,is_shop=False):
    """
    获取笔记详情  两种情况 1.笔记  2.视频
    :return:
    """
    t1 = time.time()
    # 确认详情页已经加载
    run_sel_s(lambda :Selector(2).desc("点赞.*").type("Button").find(),4)

    is_video = False
    note_info['类型'] = 'normal'
    # 确认是笔记 还是 视频
    if Selector(2).desc("暂停").type("ViewGroup").find():
        is_video = True
        note_info['类型'] = 'video'

    t2 = time.time()
    print(f"aa耗时：{t2 - t1}")
    # ================获取分享的笔记链接================
    if is_video:
        Selector(2).type("Button").desc("分享.*").click().find()
        # 也可能是下面这个
        Selector(2).type("ImageView").desc("分享.*").click().find()
    else:
        Selector(2).type("ImageView").id("com.xingin.xhs:id/moreOperateIV").click().find()
    time.sleep(0.2)
    run_sel_s(lambda: Selector(2).desc("复制链接").type("Button").child(1).click().find(), 4)
    t22 = time.time()
    print(f"aba耗时：{t22 - t2}")
    share_url_str = Clipboard.get()
    share_url = getUrl(share_url_str)
    t3 = time.time()
    print(f"ab耗时：{t3 - t22}")
    print('========点击复制后==========')
    print(share_url)
    if share_url is None:
        if is_video:
            Selector(2).type("Button").desc("分享.*").click().find()
        else:
            Selector(2).type("ImageView").drawingOrder(2).click().find()
        time.sleep(0.2)
        run_sel(lambda: Selector(2).desc("复制链接").type("Button").child(1).click().find(), 4, 0.3)
        share_url_str = Clipboard.get()
        share_url = getUrl(share_url_str)
    t4 = time.time()
    print(f"ac耗时：{t4 - t3}")
    if share_url is None:
        if is_video:
            Selector(2).type("Button").desc("分享.*").click().find()
        else:
            Selector(2).type("ImageView").drawingOrder(2).click().find()
        time.sleep(0.5)
        run_sel(lambda: Selector(2).desc("复制链接").type("Button").child(1).click().find(), 4, 0.3)
        share_url_str = Clipboard.get()
        share_url = getUrl(share_url_str)
    t5 = time.time()
    print(f"ad耗时：{t5 - t4}")
    print(share_url)
    if share_url is None:
        raise Exception('没有分享的链接')
    # 分享链接转实际链接
    url = share_url
    if 'xhslink' in share_url:
        url = getLinkToNoteUrl(option={
            'url': share_url
        })

    note_info['类型'] = 'video' if is_video else 'normal'
    note_info['笔记分享链接'] = share_url
    note_info['笔记ID'] = getNoteIdByUrl(url)
    note_info['笔记链接'] = url
    t6 = time.time()
    print(f"ae耗时：{t6 - t5}")
    try:
        # ===============获取作者昵称================
        if '用户名称' not in note_info:
            if is_video:
                note_info['用户名称'] = run_sel(lambda :Selector(2).path("/FrameLayout/RecyclerView/ViewGroup/LinearLayout/ViewGroup/Button").type("Button").desc("作者.*").find(),4,0.1).desc
            else:
                note_info['用户名称'] = run_sel(lambda :Selector(2).type("TextView").find(),4,0.1).text
        # ===============获取笔记标题================
        # ===============获取笔记内容================
        # ===============获取笔记发布时间================
        # ===============获取笔记发布地点================
        # ===============获取笔记点赞 收藏 评论 数================
        t7 = time.time()
        print(f"af耗时：{t7 - t6}")
        if is_video:
            note_info['内容'] = run_sel_s(lambda :Selector(2).id("com.xingin.xhs:id/noteContentText").find(),2).desc
            if '评论数' not in note_info:
                note_info['点赞数'] = run_sel_s(lambda: Selector(2).type("Button").desc('点赞.*').find(),
                                                2).desc.replace(' ', '').replace('点赞', '')
                note_info['收藏数'] = Selector(2).type("Button").desc('收藏.*').find().desc.replace(' ', '').replace(
                    '收藏', '')
                note_info['评论数'] = Selector(2).type("Button").desc('评论.*').find().desc.replace(' ', '').replace(
                    '评论', '')
                note_info['分享数'] = Selector(2).type("Button").desc('分享.*').find().desc.replace(' ', '').replace(
                    '分享', '')
        else:
            try:
                note_info['标题'] = Selector(2).type("TextView").drawingOrder(5).find().text
            except:
                note_info['标题'] = ''
            try:
                note_info['内容'] = Selector(2).type("TextView").drawingOrder(6).find().text
            except:
                note_info['内容'] = ''

            if '评论数' not in note_info:
                note_info['点赞数'] = run_sel_s(lambda: Selector(2).type("Button").desc('点赞.*').find(),
                                                2).desc.replace(' ', '').replace('点赞', '')
                note_info['收藏数'] = Selector(2).type("Button").desc('收藏.*').find().desc.replace(' ', '').replace(
                    '收藏', '')
                note_info['评论数'] = Selector(2).type("Button").desc('评论.*').find().desc.replace(' ', '').replace(
                    '评论', '')
        # ===============获取作者主页信息================
        t8 = time.time()
        print(f"ag耗时：{t8 - t7}")
        if is_shop:
            # 点击用户名称进入用户主页
            if is_video:
                Selector(2).id("com.xingin.xhs:id/0_resource_name_obfuscated").type("Button").clickable(
                    True).click().find()
            else:
                Selector(3).id("com.xingin.xhs:id/0_resource_name_obfuscated").type("LinearLayout").clickable(True).click().find()
            note_info = get_user_info(note_info)
            # ===============获取店铺信息================
            if is_shop and note_info['是否有店铺'] == '有':
                # 进入作者店铺内
                Selector(2).text("店铺").type("TextView").parent(1).click().find()
                note_info = get_shop_info(note_info)
                # 返回用户信息页
                print('===========返回用户信息页=====')
                Selector(2).type("ImageView").click().find()
                time.sleep(0.2)
                if is_shop_detail_page():
                    action.Key.back()
                    time.sleep(0.5)
                    if is_shop_detail_page():
                        action.Key.back()
                        time.sleep(0.5)
            # 返回笔记详情页
            print('===========返回笔记详情页=====')
            time.sleep(0.2)
            # Selector(2).desc("返回").type("ImageView").click().find()
            action.Key.back()
            time.sleep(0.2)
            # print(not is_note_detail_page())
            # if not is_note_detail_page():   # 不是笔记详情页 就再来一次
            #     action.Key.back()
            #     time.sleep(0.2)
            #     if is_user_detail_page():
            #         action.Key.back()
            #         time.sleep(0.2)
            # else:
            #     time.sleep(0.2)
            #     if not is_note_detail_page():   # 不是笔记详情页 就再来一次
            #         action.Key.back()
            #         time.sleep(0.2)
            #         if is_user_detail_page():
            #             action.Key.back()
            #             time.sleep(0.2)
            # exit()
    except Exception as e:
        print('异常 note ++++++++++++++++++++++++++')
        print(traceback.format_exc())

    return note_info

def get_user_info(note_info=None):
    """
    获取作者主页信息
    Selector(2).type("TextView").path("/FrameLayout/ViewGroup/LinearLayout/TextView").find()
    """
    # 获取用户名称
    note_info['用户名称'] = run_sel_s(lambda :Selector(2).type("TextView").find(),4).text
    note_info['用户小红书号'] = run_sel_s(lambda :Selector(2).type("TextView").text("小红书号：.*").find(),2).text.replace('小红书号：', '')
    try:
        note_info['用户IP属地'] = Selector(2).text("IP属地：.*").type("TextView").find().text.replace('IP属地：', '')
    except Exception as e:
        note_info['用户IP属地'] = ''
    try:
        note_info['用户简介'] = Selector(2).type("TextView").path(
            "/FrameLayout/ViewGroup/LinearLayout/TextView").find().text
    except Exception as e:
        note_info['用户简介'] = ''
    try:
        note_info['用户性别'] = Selector().path("/FrameLayout/ViewGroup/LinearLayout/LinearLayout/LinearLayout/LinearLayout").find().desc
    except Exception as e:
        note_info['用户性别'] = ''

    ffi = run_sel(lambda: Selector().path("/FrameLayout/ViewGroup/LinearLayout/Button/TextView").find_all(), 3, 0)
    # 用户关注
    follows = ffi[0].text if ffi is not None and len(ffi) > 0 else ''
    # 用户粉丝
    fans = ffi[2].text if ffi is not None and len(ffi) > 2 else ''
    # 用户获赞与收藏
    interaction = ffi[4].text if ffi is not None and len(ffi) > 4 else ''

    note_info['用户关注'] = follows
    note_info['用户粉丝'] = fans
    note_info['用户获赞与收藏'] = interaction
    # note_info['公开收藏笔记'] = Selector(2).type("TextView").find().text
    # note_info['收藏笔记数量'] = Selector(2).type("TextView").find().text
    # note_info['收藏专辑数量'] = Selector(2).type("TextView").find().text

    try:
        if Selector(2).text("店铺").type("TextView").find():
            note_info['是否有店铺'] = '有'
        else:
            note_info['是否有店铺'] = '无'
    except Exception as e:
        note_info['是否有店铺'] = '无'

    return note_info

def get_shop_info(note_info=None):
    """
    获取店铺信息
    """
    note_info['店铺名称'] = run_sel(lambda :Selector(2).type("TextView").path("/FrameLayout/ViewGroup/RecyclerView/FrameLayout/TextView").find(),4,0.5).text
    note_info['店铺星级'] = Selector(2).type("TextView").path("/FrameLayout/ViewGroup/RecyclerView/FrameLayout/LinearLayout/TextView").find().text
    note_info['店铺已售'] = Selector(2).text("已售.*").type("TextView").find().text.replace('已售', '')
    note_info['店铺粉丝'] = Selector(2).text("粉丝.*").type("TextView").find().text.replace('粉丝', '')
    return note_info

def check_search(sort_type,filter_note_type,filter_note_time,filter_note_range):
    # 点击下拉筛选
    Selector(2).type("ActionBar\$Tab").click().find()
    # 排序依据点击
    if sort_type != 'general':
        if sort_type == 'time_descending':  # 最新
            (Selector(2).type("TextView").text("最新")
             .parent(1)
             .path(".*/FrameLayout/ViewGroup/.*")
             # .parent(3)
             .click().find())
        elif sort_type == 'popularity_descending':  # 最多点赞
            (Selector(2).type("TextView").text("最多点赞")
             .parent(1)
             .path(".*/FrameLayout/ViewGroup/.*")
             # .parent(3)
             .click().find())
        elif sort_type == 'comment_descending':  # 最多评论
            (Selector(2).type("TextView").text("最多评论")
             .parent(1)
             .path(".*/FrameLayout/ViewGroup/.*")
             # .parent(3)
             .click().find())
        elif sort_type == 'collect_descending':  # 最多收藏
            (Selector(2).type("TextView").text("最多收藏")
             .path(".*/FrameLayout/ViewGroup/.*")
             # .parent(3)
             .parent(1)
             .click().find())
    # 笔记类型点击
    if filter_note_type != '不限':
        if filter_note_type == '视频':  # 视频
            (Selector(2).type("TextView").text("视频")
             .path(".*/FrameLayout/ViewGroup/.*")
             # .parent(3)
             .parent(1)
             .click().find())
        elif filter_note_type == '图文':  # 图文
            (Selector(2).type("TextView").text("图文")
             .path(".*/FrameLayout/ViewGroup/.*")
             # .parent(3)
             .parent(1)
             .click().find())
    # 发布时间点击
    if filter_note_time != '不限':
        if filter_note_time == '一天内':  # 一天内
            (Selector(2).type("TextView").text("一天内")
             .path(".*/FrameLayout/ViewGroup/.*")
             # .parent(3)
             .parent(1)
             .click().find())
        elif filter_note_time == '一周内':  # 一周内
            (Selector(2).type("TextView").text("一周内")
             .path(".*/FrameLayout/ViewGroup/.*")
             # .parent(3)
             .parent(1)
             .click().find())
        elif filter_note_time == '半年内':  # 半年内
            (Selector(2).type("TextView").text("半年内")
             .path(".*/FrameLayout/ViewGroup/.*")
             # .parent(3)
             .parent(1)
             .click().find())
    # 搜索范围点击
    if filter_note_range != '不限':
        if filter_note_range == '已看过':  # 已看过
            (Selector(2).type("TextView").text("已看过")
             .path(".*/FrameLayout/ViewGroup/.*")
             # .parent(3)
             .parent(1)
             .click().find())
        elif filter_note_range == '未看过':  # 未看过
            (Selector(2).type("TextView").text("未看过")
             .path(".*/FrameLayout/ViewGroup/.*")
             # .parent(3)
             .parent(1)
             .click().find())
        elif filter_note_range == '已关注':  # 已关注
            (Selector(2).type("TextView").text("已关注")
             .path(".*/FrameLayout/ViewGroup/.*")
             # .parent(3)
             .parent(1)
             .click().find())

    # 点击收起
    Selector(2).text("收起").type("TextView").parent(1).click().find()

def is_note_detail_page():
    try:
        if Selector(2).desc("点赞.*").type("Button").find():
            if Selector(2).desc("收藏.*").type("Button").find():
                if Selector(2).desc("评论.*").type("Button").find():
                    return True
        return False
    except:
        return False

def is_user_detail_page():
    try:
        if Selector(2).text("小红书号：.*").type("TextView").find():
            if Selector(2).text("私信").type("TextView").find():
                time.sleep(0.5)
                if Selector(2).text("小红书号：.*").type("TextView").find():
                    if Selector(2).text("私信").type("TextView").find():
                        return True
        return False
    except:
        return False

def is_shop_detail_page():
    try:
        if Selector(2).text("销量").type("TextView").find() and Selector(2).text("价格").type("TextView").find():
            return True
        return False
    except:
        return False