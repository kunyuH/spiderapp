import hashlib
import json
import re
import time
import traceback
from typing import Dict

from ascript.android.system import R
from android.content import Intent
from android.net import Uri
from ascript.android.node import Selector
from ascript.android.system import Clipboard
from ascript.android import action
from ascript.android.system import Device

from ..global_context import GCT
from ...utils.tools import parse_chinese_time, date_to_timestamp, timestamp_to_date, generate_guid, check_end, on, send, \
    out_info, run_sel, off, out_success, getNoteIdByUrl, getUrl, getLinkToNoteUrl, t_sleep, run_sel_s,out_error


def on_message_op(ws, option):
    # print(option)
    on()
    frequency = option.get('frequency')
    keyword = option.get('keyword')
    item_num = option.get('item_num')
    page = option.get('page')
    page_size = option.get('page_size')

    # 采集第一页才需要 进入搜索页 以及 点击筛选项
    if page == 1:
        # 进入这个关键词内
        uri = Uri.parse(f"snssdk1128://search?keyword={keyword}")
        it = Intent(Intent.ACTION_VIEW, uri)
        it.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        R.context.startActivity(it)

        # 然后点击用户 进行用户搜索
        run_sel_s(lambda :Selector(2).text("用户").type("Button").id("android:id/text1").parent(1).click().find(),2)
        out_info(ws, f"正在使用用户搜索；关键词： {keyword}")
        # 再点一下 防止漏点
        run_sel_s(lambda: Selector(2).text("用户").type("Button").id("android:id/text1").parent(1).click().find(), 2)

        # 等待搜索结果加载完成
        run_sel_s(lambda :Selector(2).path("/FrameLayout/FrameLayout/ViewPager/RecyclerView/FrameLayout/FrameLayout").find(),4)

        # 存放全部采集到的用户唯一标识  用于确认搜索页面上的用户是否采集过了 抖音号来确认
        GCT().set('data_keys', [])
    else:
        # 非第一页 开始暂停
        t_sleep(frequency)
    # 存放本次采集到的用户数据
    gather_user = []
    data_keys = GCT().get('data_keys')

    g_num = 0
    old = 0
    is_end = False # 是否采集完了  要把这个数据推送给客户端
    is_jump = False
    while check_end():

        # 点一下用户，防止退到综合
        run_sel_s(lambda: Selector(2).text("用户").type("Button").id("android:id/text1").parent(1).click().find(), 2)

        # 获取用户数据
        # notes = Selector(2).path("/FrameLayout/LinearLayout/ViewPager/RecyclerView/FrameLayout/TextView").parent(1).find_all()
        users = Selector(2).path("/FrameLayout/FrameLayout/ViewPager/RecyclerView/FrameLayout/FrameLayout/UIView").text("关注按钮").parent(1).find_all()
        if users is None:
            users = []
        for idx, user in enumerate(users, start=1):  # start=1 表示从 1 开始计数
            if not check_end():
                break

            print('=====用户项=======')

            t1 = time.time()

            # 第二次迭代开始 就是能取到则 取 不能取到就跳过  用于加快速度
            re_time = 3
            if idx > 1:
                re_time = 0.5
            # 获取用户信息 （包含标题，粉丝，主体）
            # text_str = run_sel_s(lambda :user.find(Selector(2).type('LynxFlattenUI').clickable(False)).text, re_time)
            text_str = run_sel_s(lambda :user.find(Selector(2).text("粉丝: .*")).text, re_time)
            print(text_str)
            if text_str is None:
                if is_user_page():
                    # 在用户详情页  则 返回一下
                    action.Key.back()
                    time.sleep(1)
                continue
            # 标点符号兼容 有的系统是英文标点符号
            text_str = text_str.replace('，', ',')
            # 按照逗号分割
            text_strs = text_str.split(',')
            user_name = text_strs[0]
            user_fans = text_strs[1].replace('粉丝:', '')
            user_main = text_strs[2].replace(' 按钮','')    # 账号公司 或 抖音号
            t2 = time.time()
            print(f"a耗时：{t2-t1}")

            data_key = hashlib.md5(f"{user_name}{user_main}".encode('utf-8')).hexdigest()
            print(f"{user_name}-{user_main}")
            print(data_key in data_keys)
            # true 已经抓过了 不再抓取
            if data_key in data_keys:
                continue

            user_info = {
                '来源': keyword,
                '昵称': user_name,
                '粉丝量': user_fans,
                '账号': user_main,
            }

            # 点击用户 [根据定位 点击  元素点击不生效]
            time.sleep(0.2)
            item_rect = user.rect
            action.Touch.down(item_rect.right/2, item_rect.top+50, 20)
            time.sleep(0.2)
            action.Touch.up(item_rect.right/2, item_rect.top+50,  20)
            time.sleep(0.5)
            # 确认是否在用户页
            if not is_user_page():
                continue

            data_keys.append(data_key)
            t3 = time.time()
            print(f"b耗时：{t3 - t2}")
            # 获取用户详情
            print('==开始采集用户信息==')
            user_info = {**user_info,**get_user_info()}
            print('======user_info=====')
            t4 = time.time()
            print(f"c耗时：{t4 - t3}")

            gather_user.append(user_info)
            # 采集了多少条
            gr_total = (page-1)*page_size + len(gather_user)

            out_success(ws, f'{gr_total}. {user_name}')

            # 判断是否足够一页数据了
            if len(gather_user) >= page_size:
                out_info(ws, f'第{page}页采集完， 采集到 {len(gather_user)} 个用户')
                is_jump = True
            # 已经取够数量的用户了
            if gr_total >= item_num:
                out_info(ws, f'已经采集到 {gr_total} 个用户， 【{keyword}】采集完成')
                is_jump = True
                is_end = True

            # 返回
            print('===========返回关键词搜索列表页=====')
            time.sleep(0.4)
            if not is_user_page():
                if is_user_phone_page():
                    action.Key.back()
                    time.sleep(0.2)

            if not is_user_page():
                out_error(ws,f'返回关键词搜索列表页失败,跳过【{keyword}】采集')
                off()
                is_end = True
                break
            action.Key.back()

            if is_jump:
                off()
                break
        time.sleep(0.3)
        GCT().set('data_keys', data_keys)
        # 往下滑动
        print('======滑动======')
        if is_user_page():
            action.Key.back()
            time.sleep(1)
        if is_user_page():
            action.Key.back()
            time.sleep(1)

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

        if g_num >= 3:
            break
        if len(gather_user) > old:
            g_num = 0
        else:
            g_num += 1

        old = len(gather_user)

    if len(gather_user) == 0:
        is_end = True

    send(ws, 'dy_yy_phone_gather_by_phone_device_data', {
        'data': gather_user,
        'is_end': is_end
    })
    print('dy_yy_phone_gather_by_phone_device_data')
    pass

def get_user_info()->Dict:
    """
    获取作者主页信息
    Selector(2).type("TextView").path("/FrameLayout/ViewGroup/LinearLayout/TextView").find()
    """
    user_info = {}
    try:
        # 获取用户名称
        # 获取用户账号主体
        # 获赞
        user_info['获赞'] = run_sel_s(lambda :Selector(2).id("com.ss.android.ugc.aweme:id/ddp").find(),2).text.strip()
        if user_info['获赞'] == '':
            time.sleep(0.1)
            user_info['获赞'] = run_sel_s(lambda: Selector(2).id("com.ss.android.ugc.aweme:id/ddp").find(), 2).text.strip()
        if user_info['获赞'] == '':
            time.sleep(0.1)
            user_info['获赞'] = run_sel_s(lambda: Selector(2).id("com.ss.android.ugc.aweme:id/ddp").find(), 2).text.strip()
        if user_info['获赞'] == '':
            time.sleep(0.2)
            user_info['获赞'] = run_sel_s(lambda: Selector(2).id("com.ss.android.ugc.aweme:id/ddp").find(), 2).text.strip()
        # 关注
        user_info['关注'] = Selector(2).id("com.ss.android.ugc.aweme:id/e-t").find().text
        # 粉丝
        user_info['粉丝'] = Selector(2).id("com.ss.android.ugc.aweme:id/e-k").find().text
    except:
        user_info['获赞'] = ''
        user_info['关注'] = ''
        user_info['粉丝'] = ''
    # 简介
    try:
        user_info['简介'] = Selector(2).path("/FrameLayout/LinearLayout/TextView").find().text

        # 规则：
        # - 先找 "："
        """
        ： → 匹配中文冒号后面的内容
        [a-zA-Z] → 以字母开头（不能是数字、@ 或其他符号）
        [a-zA-Z0-9_-]{5,19} → 后面 5到19 个字符，允许字母、数字、下划线、短横线
        整体保证不会把 🎵號=💚 这种带中文或特殊符号的东西抓出来
        """
        pattern = re.compile(r'：([a-zA-Z][-_a-zA-Z0-9]{5,19})')

        match = pattern.search(user_info['简介'])
        if match:
            user_info['其他联系方式'] = match.group(1).strip()
        else:
            user_info['其他联系方式'] = ''
    except:
        user_info['简介'] = ''
        user_info['其他联系方式'] = ''

    # ip
    try:
        user_info['IP'] = Selector(2).desc("IP.*").find().desc.replace('IP', '').replace('属地', '').replace('：', '')
    except:
        try:
            user_info['IP'] = Selector(2).text("IP.*").find().text.replace('IP', '').replace('属地', '').replace('：',                                                                                              '')
        except:
            user_info['IP'] = ''
    # 性别
    try:
        user_info['性别'] = Selector(2).text("女·").find().text.split('·')[0]
    except:
        try:
            user_info['性别'] = Selector(2).text("女").maxTextLength(1).find().text
        except:
            try:
                user_info['性别'] = Selector(2).text("男·").find().text.split('·')[0]
            except:
                try:
                    user_info['性别'] = Selector(2).text("男").maxTextLength(1).find().text
                except:
                    user_info['性别'] = ''

    # 电话
    if Selector(2).text("\[label\] 联系.*").type("TextView").parent(1).find():
        # 点击
        Selector(2).text("\[label\] 联系.*").type("TextView").parent(1).click().find()
        try:
            user_info["手机号"] = run_sel_s(lambda :Selector(2).text("呼叫 .*").find(),2).text.replace('呼叫 ', '')
            time.sleep(0.2)
            action.Key.back()
        except:
            user_info["手机号"] = ""
    elif Selector(2).text("\[label\] 官方电话").type("TextView").parent(1).find():
        # 点击
        Selector(2).text("\[label\] 官方电话").type("TextView").parent(1).click().find()
        try:
            user_info["手机号"] = run_sel_s(lambda: Selector(2).text("呼叫 .*").find(), 2).text.replace('呼叫 ', '')
            time.sleep(0.2)
            action.Key.back()
        except:
            user_info["手机号"] = ""
    else:
        user_info["手机号"] = ""

    return user_info

def is_keyword_user_page():
    try:
        if Selector(2).type("Button").text("用户").find():
            return True
        return False
    except:
        return False

def is_user_page():
    """
    判断是否是用户主页
    """
    if Selector(2).desc("用户头像").find():
        return True
    return False

def is_user_phone_page():
    """
    判断是否是用户手机号页面
    """
    if Selector(2).text("呼叫 .*").find():
        return True
    return False

