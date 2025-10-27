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

from ..global_context import GCT
from ...utils.tools import parse_chinese_time, date_to_timestamp, timestamp_to_date, generate_guid, check_end, on, send, \
    out_info, run_sel, off, out_success, getNoteIdByUrl, getUrl, getLinkToNoteUrl, t_sleep, run_sel_s


def on_message_note(ws, option):
    # print(option)
    """
    json_ = {
            "keyword": keyword,
            "is_shop": is_shop,
            "page": gct.get('page'),
            "page_size": 10,
            "search_id": get_search_id(),
            "sort": "general",
            "note_type": 0,
            "ext_flags": [],
            "image_formats": ["jpg", "webp", "avif"],
            "filters": [
                {"tags": [sort_type], "type": "sort_type"},# 排序依据
                {"tags": [filter_note_type], "type": "filter_note_type"},           # 笔记类型
                {"tags": [filter_note_time], "type": "filter_note_time"},           # 发布时间
                {"tags": [filter_note_range], "type": "filter_note_range"},          # 搜索范围
                {"tags": ["不限"], "type": "filter_pos_distance"},        # 位置距离 不做更改 需要用户授权获取当前位置信息
            ]
        }
    """
    on()
    frequency = option.get('frequency')
    is_shop = option.get('is_shop')
    keyword = option.get('keyword')
    max_num = option.get('max_num')
    page = option.get('page')
    page_size = option.get('page_size')
    sort_type = option.get('filters')[0].get('tags')[0]         # 排序依据
    filter_note_type = option.get('filters')[1].get('tags')[0]  # 笔记类型
    filter_note_time = option.get('filters')[2].get('tags')[0]  # 发布时间
    filter_note_range = option.get('filters')[3].get('tags')[0] # 搜索范围

    # 采集第一页才需要 进入笔记搜索页 以及 点击筛选项
    if page == 1:
        # 进入这个笔记内
        uri = Uri.parse(f"xhsdiscover://search/result?keyword={keyword}")
        it = Intent(Intent.ACTION_VIEW, uri)
        it.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        R.context.startActivity(it)
        out_info(ws, f"正在搜索关键词： {keyword}")

        # 等待搜索结果加载完成
        run_sel(lambda :Selector(2).type("ActionBar\$Tab").find(),4,0.1)

        # 需添加筛选项情况
        # 存在某个非默认的  不是综合 不是不限
        if sort_type != 'general' or filter_note_type != '不限' or filter_note_time != '不限' or filter_note_range != '不限':
            check_search(sort_type, filter_note_type, filter_note_time, filter_note_range)
            time.sleep(2)

        # 存放全部采集到的笔记唯一标识  用于确认搜索页面上的笔记是否采集过了 标题加昵称来确认
        GCT().set('data_keys', [])
        # 存放全部采集到的笔记数据  用于确认页面上的笔记是否采集过了
        GCT().set('all_note', [])
    else:
        # 非第一页 开始暂停
        t_sleep(frequency)
    # 存放本次采集到的笔记数据
    gather_note = []
    data_keys = GCT().get('data_keys')
    all_note = GCT().get('all_note')

    g_num = 0
    old = 0
    is_end = False # 是否采集完了  要把这个数据推送给客户端
    is_jump = False
    while check_end():
        # 获取笔记数据
        # notes = Selector(2).path("/FrameLayout/LinearLayout/ViewPager/RecyclerView/FrameLayout/TextView").parent(1).find_all()
        notes = Selector(3).type("FrameLayout").clickable(True).find_all()
        if notes is None:
            notes = []
        for idx, note in enumerate(notes, start=1):  # start=1 表示从 1 开始计数

            print('=====笔记项=======')
            t1 = time.time()

            # 第二次迭代开始 就是能取到则 取 不能取到就跳过  用于加快速度
            re_time = 3
            if idx > 1:
                re_time = 0.2
            # 获取笔记标题
            # note_title = run_sel_s(lambda :note.find(Selector(3).type('TextView').drawingOrder(13)).text, re_time)
            note_title = run_sel_s(lambda :note.find(Selector(3).path("/RelativeLayout/TextView")).text, re_time)
            if note_title is None:
                continue

            t2 = time.time()
            print(f"耗时：{t2-t1}")
            # 用户昵称
            author_name = run_sel_s(lambda :note.find(Selector(2).type('TextView').drawingOrder(1)).text, re_time)
            if note_title is None:
                continue
            # 发布时间
            push_time = run_sel_s(lambda :note.find(Selector(2).type('TextView').drawingOrder(2)).text, re_time)
            if push_time is None or author_name is None:
                continue
            push_time = parse_chinese_time(push_time)
            # 点赞数
            like_num = run_sel_s(lambda :note.find(Selector(2).type('TextView').drawingOrder(3)).text, re_time)
            if like_num:
                like_num = like_num.replace('赞', '0')

            # print(f"{author_name}=={push_time}=={like_num}=={note_title}")
            # if like_num is None:
            #     exit()

            data_key = hashlib.md5(f"{note_title}{author_name}".encode('utf-8')).hexdigest()
            # print(data_key)
            # true 已经抓过了 不再抓取
            if data_key in data_keys:
                continue

            note_info = {
                '来源': keyword,
                '标题': note_title,
                '封面图': '',
                '用户名称': author_name,
                '用户主页链接': '',
                '用户ID': '',
                '发布时间': push_time,
                '点赞数': like_num,
            }

            data_keys.append(data_key)

            # """
            # 每50 取一个
            # """
            # print(len(data_keys))
            # if (len(data_keys)-1) % 10 != 0:
            #     continue

            # 点击笔记
            note.find(Selector().click())
            time.sleep(0.5)
            # 获取笔记详情  两种情况 1.笔记  2.视频
            # 获取笔记
            t1 = time.time()
            note_info = get_note_info(note_info,is_shop)
            print('======note_info=====')
            # print(note_info)

            note_id = note_info.get('笔记ID')
            t2 = time.time()
            print(f"a耗时：{t2 - t1}")
            # print(note_id)
            # print(all_note)
            # print(note_id not in all_note)
            if note_id is not None and note_id not in all_note:
                all_note.append(note_id)
                gather_note.append({
                    '来源': note_info.get('来源'),
                    '标题': note_info.get('标题'),
                    '内容': note_info.get('内容'),
                    '用户名称': note_info.get('用户名称'),
                    '发布时间': note_info.get('发布时间'),
                    '点赞数': note_info.get('点赞数'),
                    '收藏数': note_info.get('收藏数'),
                    '评论数': note_info.get('评论数'),

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
                })
                # 采集了多少条
                gr_total = (page-1)*page_size + len(gather_note)

                out_success(ws, f'{gr_total}. {note_title}')

                # 判断是否足够一页数据了
                if len(gather_note) >= page_size:
                    out_info(ws, f'第{page}页采集完， 采集到 {len(gather_note)} 条笔记')
                    is_jump = True
                # 已经取够数量的笔记了
                if gr_total >= max_num:
                    out_info(ws, f'已经采集到 {gr_total} 条笔记， 【{keyword}】采集完成')
                    is_jump = True
                    is_end = True
            t3 = time.time()
            print(f"b耗时：{t3 - t2}")
            # 返回
            print('===========返回关键词搜索列表页=====')
            time.sleep(0.2)
            # if note_info.get('类型') == 'video':
            #     Selector(2).desc("返回").type("ImageView").click().find()
            # else:
            #     Selector(2).type("ImageView").click().find()
            action.Key.back()
            time.sleep(0.2)
            t4 = time.time()
            print(f"c耗时：{t4 - t3}")
            if is_note_detail_page():
                t5 = time.time()
                print(f"d耗时：{t5 - t4}")
                action.Key.back()
                time.sleep(0.5)
                if is_note_detail_page():
                    t6 = time.time()
                    print(f"e耗时：{t6 - t5}")
                    action.Key.back()
                    time.sleep(0.5)


            t7 = time.time()
            print(f"f耗时：{t7 - t4}")
            if is_jump:
                off()
                break

        GCT().set('data_keys', data_keys)
        GCT().set('all_note', all_note)
        # 往下滑动
        print('======滑动======')
        # 滑动
        display = Device.display()
        width = display.widthPixels
        height = display.heightPixels

        # 从屏幕中间向下滑动（向下滚动页面）
        # 注意：向下滑动，终点y比起点y大
        action.slide(
            x=width // 2,
            y=int(height * 0.8),  # 从屏幕下方开始
            x1=width // 2,
            y1=int(height * 0.2),  # 到屏幕上方
            dur=500  # 持续时间 ms
        )

        time.sleep(0.2)
        # exit()

        if g_num >= 3:
            break
        if len(gather_note) > old:
            g_num = 0
        else:
            g_num += 1

        old = len(gather_note)

    send(ws, 'func_phone_xhs_note_data', {
        'data': gather_note,
        'is_end': is_end
    })
    print('func_phone_xhs_note_data')
    pass

def get_note_info(note_info=None,is_shop=False):
    """
    获取笔记详情  两种情况 1.笔记  2.视频
    :return:
    """
    t1 = time.time()
    # 确认详情页已经加载
    run_sel_s(lambda :Selector(2).desc("点赞.*").type("Button").find(),4)

    is_video = False
    # 确认是笔记 还是 视频
    if Selector(2).desc("暂停").type("ViewGroup").find():
        is_video = True

    t2 = time.time()
    print(f"aa耗时：{t2 - t1}")
    # ================获取分享的笔记链接================
    if is_video:
        Selector(2).type("Button").desc("分享.*").click().find()
    else:
        Selector(2).type("ImageView").drawingOrder(2).click().find()
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
        run_sel(lambda: Selector(2).desc("复制链接").type("Button").child(1).click().find(), 4, 0.3)
        share_url_str = Clipboard.get()
        share_url = getUrl(share_url_str)
    t4 = time.time()
    print(f"ac耗时：{t4 - t3}")
    if share_url is None:
        time.sleep(1)
        if is_video:
            Selector(2).type("Button").desc("分享.*").click().find()
        else:
            Selector(2).type("ImageView").drawingOrder(2).click().find()
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
    note_info['笔记分享链接'] = share_url
    note_info['笔记ID'] = getNoteIdByUrl(url)
    note_info['笔记链接'] = url

    note_info['类型'] = 'video' if is_video else 'normal'
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
            Selector(2).type("TextView").text("最新").parent(1).click().find()
        elif sort_type == 'popularity_descending':  # 最多点赞
            Selector(2).type("TextView").text("最多点赞").parent(1).click().find()
        elif sort_type == 'comment_descending':  # 最多评论
            Selector(2).type("TextView").text("最多评论").parent(1).click().find()
        elif sort_type == 'collect_descending':  # 最多收藏
            Selector(2).type("TextView").text("最多收藏").parent(1).click().find()
    # 笔记类型点击
    if filter_note_type != '不限':
        if filter_note_type == '视频':  # 视频
            Selector(2).type("TextView").text("视频").parent(1).click().find()
        elif filter_note_type == '图文':  # 图文
            Selector(2).type("TextView").text("图文").parent(1).click().find()
    # 发布时间点击
    if filter_note_time != '不限':
        if filter_note_time == '一天内':  # 一天内
            Selector(2).type("TextView").text("一天内").parent(1).click().find()
        elif filter_note_time == '一周内':  # 一周内
            Selector(2).type("TextView").text("一周内").parent(1).click().find()
        elif filter_note_time == '半年内':  # 半年内
            Selector(2).type("TextView").text("半年内").parent(1).click().find()
    # 搜索范围点击
    if filter_note_range != '不限':
        if filter_note_range == '已看过':  # 已看过
            Selector(2).type("TextView").text("已看过").parent(1).click().find()
        elif filter_note_range == '未看过':  # 未看过
            Selector(2).type("TextView").text("未看过").parent(1).click().find()
        elif filter_note_range == '已关注':  # 已关注
            Selector(2).type("TextView").text("已关注").parent(1).click().find()

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




