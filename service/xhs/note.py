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
            # 第二次迭代开始 就是能取到则 取 不能取到就跳过  用于加快速度
            re_time = 5
            if idx > 1:
                re_time = 1
            # 获取笔记标题
            note_title = run_sel_s(lambda :note.find(Selector(3).type('TextView').drawingOrder(13)).text, re_time)
            if note_title is None:
                continue
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
            note_info = get_note_info(note_info)
            print('======note_info=====')
            # print(note_info)
            note_id = note_info.get('笔记ID')
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
                    '笔记分享链接': note_info.get('笔记分享链接')
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

            # 返回
            print('===========返回=====')
            time.sleep(0.2)
            if note_info.get('类型') == 'video':
                Selector(2).desc("返回").type("ImageView").click().find()
            else:
                Selector(2).type("ImageView").click().find()
            time.sleep(0.2)
            if is_note_detail_page():
                action.Key.back()
                time.sleep(0.2)
                if is_note_detail_page():
                    action.Key.back()
                    time.sleep(0.2)


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

def get_note_info(note_info=None):
    """
    获取笔记详情  两种情况 1.笔记  2.视频
    :return:
    """
    # 确认详情页已经加载
    run_sel(lambda :Selector(2).desc("点赞.*").type("Button").find(),4,0.1)

    is_video = False
    # 确认是笔记 还是 视频
    if Selector(2).desc("暂停").type("ViewGroup").find():
        is_video = True

    # ================获取分享的笔记链接================
    if is_video:
        Selector(2).type("Button").desc("分享.*").click().find()
    else:
        Selector(2).type("ImageView").drawingOrder(2).click().find()
    run_sel(lambda: Selector(2).desc("复制链接").type("Button").child(1).click().find(), 4, 0.3)
    share_url_str = Clipboard.get()
    share_url = getUrl(share_url_str)
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

    print(share_url)
    if share_url is None:
        exit()
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
        if is_video:
            note_info['内容'] = run_sel_s(lambda :Selector(2).id("com.xingin.xhs:id/noteContentText").find(),2).desc
            if '评论数' not in note_info:
                a = run_sel_s(lambda: Selector(2).type("LinearLayout").drawingOrder(3).child().find_all(), 2)
                note_info['点赞数'] = a[0].desc.replace(' ', '').replace('点赞', '')
                note_info['评论数'] = a[1].desc.replace(' ', '').replace('评论', '')
                note_info['收藏数'] = a[2].desc.replace(' ', '').replace('收藏', '')
        else:
            note_info['标题'] = run_sel_s(lambda :Selector(2).path("/FrameLayout/TextView").drawingOrder(5).find(),2).text
            note_info['内容'] = run_sel_s(lambda :Selector(2).path("/FrameLayout/TextView").drawingOrder(6).find(),2).text

            if '评论数' not in note_info:
                a = run_sel_s(lambda: Selector(2).type("Button").find_all(), 2)

                note_info['点赞数'] = a[0].desc.replace(' ', '').replace('点赞', '')
                note_info['收藏数'] = a[1].desc.replace(' ', '').replace('收藏', '')
                note_info['评论数'] = a[2].desc.replace(' ', '').replace('评论', '')

    except Exception as e:
        print('异常 note ++++++++++++++++++++++++++')
        print(traceback.format_exc())

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
        if Selector(2).text("关注").type("TextView").find():
            if Selector(2).text("作者").type("TextView").find():
                return True
        if Selector(2).desc("作者.*").type("Button").find():
            if Selector(2).text("关注").type("Button").find():
                return True

        return False
    except:
        return False




