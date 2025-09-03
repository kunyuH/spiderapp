import json
import re
import time
import traceback
import requests
from ascript.android.system import R
from android.content import Intent
from android.net import Uri
from ascript.android.node import Selector
from ascript.android.system import Clipboard
from ascript.android import action
from ascript.android.system import Device

from ..global_context import GCT
from ...utils.tools import parse_chinese_time, date_to_timestamp, timestamp_to_date, generate_guid, check_end, on, send, \
    out_info, run_sel


def on_message_note(ws, option):
    print(option)
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
    keyword = option.get('keyword')
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

        # 存放全部采集到的笔记数据  用于确认页面上的笔记是否采集过了
        GCT().set('all_note', [])

    # 存放本次采集到的笔记数据
    gather_note = []
    all_note = GCT().get('all_note')
    while check_end():
        # 获取笔记数据
        notes = Selector(2).path("/FrameLayout/LinearLayout/ViewPager/RecyclerView/FrameLayout/TextView").parent(1).find_all()
        for note in notes:
            # 获取笔记标题
            note_title = note.find(Selector(2).type('TextView')).text
            print(note_title)
            # 点击笔记
            note.find(Selector().click())
            # 获取笔记详情  两种情况 1.笔记  2.视频
            # 获取笔记
            note_info = get_note_info()
            note_id = note_info.get('note_id')
            if note_id is not None:
                if note_id not in all_note:
                    all_note.append(note_id)
                    gather_note.append(note_id)
            # 返回
            action.Key.back()

        # 往下滑动
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


    gather_comment = []
    print(page, page_size, sort_type, filter_note_type, filter_note_time, filter_note_range)


    pass

def get_note_info():
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
    run_sel(lambda: Selector(2).desc("复制链接").type("Button").child(1).click().find(), 4, 0.1)
    share_url = Clipboard.get()
    share_url = re.findall(r'https?://[^\s]+', share_url)
    share_url = share_url[0] if share_url else None
    # 分享链接转实际链接
    url = getLinkToNoteUrl(option={
        'url': share_url
    })
    try:
        # ===============获取作者昵称================
        author_name = Selector(2).path("/FrameLayout/RelativeLayout/LinearLayout/TextView").type("TextView").find().text
        # ===============获取笔记内容================
        # ===============获取笔记发布时间================
        # ===============获取笔记发布地点================
        # ===============获取笔记点赞 收藏 评论 数================
    except Exception as e:
        print('异常 note ++++++++++++++++++++++++++')
        print(traceback.format_exc())
    return {
        'share_url': share_url,
        'note_id': getNoteIdByUrl(url),
        'url': url
    }

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


def getLinkToNoteUrl(option=None):
    # 参数组装
    if option is None:
        option = {}
    url = option['url'] if 'url' in option else ''

    res = requests.get(url, allow_redirects=False)  # 不跟随跳转# 默认是 True
    if res.is_redirect or res.status_code in (301, 302, 303, 307, 308):
        redirect_url = res.headers.get('Location')
        return redirect_url

    if 'discovery/item' in res.url:
        return res.url

    if res.history:
        for history in res.history:
            if history.status_code == 302:
                return history.url
    return ''

def getNoteIdByUrl(url):
    """
    从笔记链接中获取笔记ID
    :param url:
    :return:
    """
    return str(url).split("/")[-1].split("?")[0]