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

from ...utils.tools import parse_chinese_time, date_to_timestamp, timestamp_to_date, generate_guid, check_end, on


def out_info(ws, msg):
    ws.send(json.dumps({
        "type": "out_info",
        "msg": msg
    }))
def out_error(ws, msg):
    ws.send(json.dumps({
        "type": "out_error",
        "msg": msg
    }))
def out_success(ws, msg):
    ws.send(json.dumps({
        "type": "out_success",
        "msg": msg
    }))

def send(ws, type, data):
    ws.send(json.dumps({
        "type": type,
        "option": data
    }))


def run_sel(fun, re_time=10):
    num = 0
    while True:
        time.sleep(1)
        if num >= re_time:
            return None
        try:
            a = fun()
            if a:
                return a
        except Exception as e:
            return None
        num += 1
        time.sleep(0.5)

def ip_date_back(content):
    content = content.strip()

    # 时间正则：包含相对时间、YYYY-MM-DD、MM-DD
    time_pattern = (
        r"(刚刚|刚才|\d+分钟前|\d+小时前|\d+天前|今天|昨天|前天|"
        r"\d{4}-\d{2}-\d{2}|\d{2}-\d{2})"
    )

    # 完整正则，IP 属地可选
    pattern = re.compile(
        rf"{time_pattern}\s*([\u4e00-\u9fa5]+)?\s*回复"
    )

    match = pattern.search(content)
    if match:
        time_text = match.group(1)
        ip_text = match.group(2) if match.group(2) else None
    else:
        time_text = None
        ip_text = None

    # 去掉时间和属地后的“回复”，得到干净内容
    content_clean = pattern.sub("", content).strip()

    print(f"原始: {content}")
    print(f"时间: {time_text}, IP属地: {ip_text}")
    print(f"内容: {content_clean}")
    print("-" * 30)
    return time_text, ip_text, content_clean

def ip_date(content):
    content = content.strip()
    # 末尾是翻译 则去除
    if content.endswith("翻译"):
        content = content[:-2].strip()
    # 末尾是回复 则去除
    if content.endswith("回复"):
        content = content[:-2].strip()

    # 我的美食，还 有 昨日 12:50 北京
    # 我的美食，还 有 昨日 12:50
    # 我的美食，还 有 12:50 北京
    # 我的美食，还 有 12:50

    # 时间模式
    time_pattern = (
        r"(?:"
        r"(?:刚刚|刚才|今天|昨天|昨日|前天)(?:\s+\d{1,2}:\d{2})?"  # 相对时间 + 可选 HH:MM
        r"|\d+分钟前|\d+小时前|\d+天前"  # 数字时间
        r"|\d{1,2}:\d{2}"  # HH:MM
        r"|\d{2}-\d{2}"  # MM-DD
        r"|\d{4}-\d{2}-\d{2}"  # YYYY-MM-DD
        r")"
    )

    # 完整正则：评论 + 空格 + 时间 + 可选空格 + 可选IP(中文) + 结尾
    pattern = re.compile(rf"(.*?)\s+({time_pattern})(?:\s+([\u4e00-\u9fa5]+))?$")

    match = pattern.match(content)
    if match:
        comment = match.group(1).strip()
        time_text = match.group(2).strip()
        ip_text = match.group(3).strip() if match.group(3) else None
    else:
        # 如果末尾没有时间，则全部视为评论
        comment = content
        time_text = None
        ip_text = None

    print(f"原始: {content}")
    print(f"时间: {time_text}, IP属地: {ip_text}")
    print(f"内容: {comment}")
    print("-" * 30)
    return time_text, ip_text, comment

def content_filter(content_data,fiter_data):
    """
    # 数据过滤
    # 1. 首个时间不满足 则直接退出采集
    # 2. 时间过滤
    # 3. 关键词过滤 （排除关键词  符合关键词  ）
    # 4. 评论人昵称过滤
    # 5. 评论ip关键词
    # 6. 评论字数
    ## 7. 评论去重  这个做不了  不知道uid
    :param content:
    :return:
    """
    comment_search_keyword = fiter_data.get('comment_search_keyword')
    comment_not_search_keyword = fiter_data.get('comment_not_search_keyword')
    comment_not_user_name = fiter_data.get('comment_not_user_name')
    comment_ip_search = fiter_data.get('comment_ip_search')
    follow_time = fiter_data.get('follow_time','')
    comment_word_num = fiter_data.get('comment_word_num')

    content = content_data.get('content')
    nickname = content_data.get('user_info',{}).get('nickname')
    create_time = content_data.get('create_time')
    ip_location = content_data.get('ip_location')

    # 包含搜索关键词
    if(comment_search_keyword == '' or re.findall(comment_search_keyword, content)
        and (comment_ip_search == '' or re.findall(comment_ip_search, ip_location))
        # 评论时间要大于上次扫描时间 小于 本次扫描时间
        and (follow_time == '' or create_time >= follow_time)
        # 排除搜索关键词
        and (comment_not_search_keyword == '' or re.findall(comment_not_search_keyword, content) == [])
        # 评论人昵称屏蔽
        and (comment_not_user_name == '' or re.findall(comment_not_user_name, nickname) == [])
        and comment_word_num > len(content)):
        return content_data
    return None

def on_message_content(ws , id, option):
    # print(option)
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

    # 获取笔记评论量
    # 有评论  则 点击评论  点击按最新
    content_button = run_sel(lambda :Selector(2).type("Button").desc("评论.*").find())
    if content_button:
        # 去除所有空格
        content_num = content_button.desc.replace(" ", "").replace("评论", "")
        # true 没有评论
        if content_num == '' or content_num == '0' or content_num == 0:
            out_info(ws, f"笔记 【{note_id}】 没有评论")
        else:
            out_info(ws, f"笔记 【{note_id}】 评论量：{content_num}")

            # 点击评论
            run_sel(lambda :content_button.find(Selector(2).click()))

            # 点击按最新
            run_sel(lambda :Selector(2).text(".*条评论").type("TextView").click().find())
            run_sel(lambda: Selector(2).text("按最新").type("TextView").parent(1).click().find())
            time.sleep(0.5)

            is_jump = False
            num = 0
            data_keys = []
            g_num = 0
            old = 0
            time_check_num = 0

            while check_end():
                # 获取评论项
                items = run_sel(lambda: Selector(2).type("RecyclerView").child().type("LinearLayout").find_all())
                if items:
                    for item in items:
                        if not item:
                            continue
                        num += 1
                        if num > max_num:
                            out_info(ws, f"笔记 【{note_id}】 评论已经提取 {max_num} 条")
                            is_jump = True
                            break
                        if not check_end():
                            is_jump = True
                            break
                        try:
                            usre_name_obj = item.find(Selector().child().type('TextView').drawingOrder(2))
                            if not usre_name_obj:
                                continue
                            usre_name = usre_name_obj.text

                            content = item.find(Selector().child().type('TextView').drawingOrder(4)).text

                            try:
                                like = item.find(Selector().child().type('LinearLayout').child().type("TextView")).text
                            except:
                                like = 0
                            # 提取时间 ip
                            create_time,ip_location,content = ip_date(content)
                            # ture 如果时间 ip 都没有
                            if create_time is None and ip_location is None:
                                date_ip = item.find(Selector().child().type('RelativeLayout').child().type("TextView")).text
                                # true 如果末尾是翻译 则去除
                                if date_ip.endswith('翻译'):
                                    date_ip = date_ip.replace('翻译', '').strip()
                                create_time, ip_location, _ = ip_date(date_ip)

                            usre_name = usre_name if usre_name else ''
                            content = content if content else ''
                            like = like if like else 0
                            create_time = int(date_to_timestamp(parse_chinese_time(create_time))) if create_time else ''
                            ip_location = ip_location if ip_location else ''

                            # 先判断时间 只要有一个不合适的 就退出
                            # 必须校验3（包含）个以上 因为有置顶的 包括置顶的一个子评论
                            if create_time is None or create_time == '' or create_time < follow_time:
                                time_check_num += 1
                                out_info(ws,
                                         f'{timestamp_to_date(create_time)}----{timestamp_to_date(follow_time)}----{time_check_num}')
                                if time_check_num > 2:
                                    out_info(ws, f"笔记 【{note_id}】 评论已经采集完")
                                    is_jump = True
                                    break
                                continue

                            data_key = f"{usre_name}{content}"
                            # true 已经抓过了 不再抓取
                            if data_key in data_keys:
                                continue

                            out_success(ws,
                                        f"{num}. 【{timestamp_to_date(create_time)}】 【{usre_name}】 评论：{content} 点赞：{like} IP属地：{ip_location}")

                            content_data = {
                                # 'usre_name':usre_name,
                                'id':generate_guid(),
                                'content':content,
                                'like_count':like,
                                'create_time':create_time,
                                'ip_location':ip_location,
                                'user_info':{
                                    'nickname':usre_name
                                },
                                'show_tags':[]
                            }


                            content_data = content_filter(content_data,{
                                # 'follow_time': follow_time,                               # 评论时间 限制
                                'comment_search_keyword': comment_search_keyword,           # 评论关键词
                                'comment_not_search_keyword': comment_not_search_keyword,   # 评论搜索排除关键字
                                'comment_not_user_name': comment_not_user_name,             # 评论人昵称排除关键字
                                'comment_ip_search': comment_ip_search,                     # 评论ip搜索关键字
                                'comment_word_num': comment_word_num,                       # 评论字数小于
                            })

                            if content_data is not None:
                                # 获取uid （点击用户名称 进入主页 把链接复制出来 截取里面的uid）
                                item.find(Selector(2).child().type('TextView').drawingOrder(2).click())
                                run_sel(lambda :Selector(2).type("ImageView").desc("更多").click().find())
                                run_sel(lambda :Selector(2).desc("复制链接").type("Button").child().type("ViewGroup").click().find())
                                # exit()
                                user_url = Clipboard.get()
                                content_data['user_info']['user_id'] = user_url.split('?')[0].split('/')[-1]

                                # 留存数据
                                # send(ws, 'content_data', content_data)
                                gather_comment.append(content_data)
                                data_keys.append(data_key)

                                # 返回
                                run_sel(lambda :Selector(2).type("ImageView").desc("返回").click().find())
                                print('44444444444444')
                        except Exception as e:
                            print('异常++++++++++++++++++++++++++')
                            # err_msg = traceback.format_exc()   # 获取完整堆栈字符串
                            # out_error(ws, f"笔记 【{note_id}】 评论采集异常 {err_msg}")

                if is_jump:
                    break
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
                time.sleep(0.3)

                if g_num >= 3:
                    break

                if len(gather_comment) > old:
                    g_num = 0
                else:
                    g_num += 1

                old = len(gather_comment)
                print('55555555555555555')

    send(ws, 'func_phone_xhs_content_data', gather_comment)
    print('func_phone_xhs_content_data')
    print(gather_comment)
    
    print(note_id+'zzzz')
    pass