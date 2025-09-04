import json
import re
import time
import uuid
from datetime import datetime, timedelta
import requests

from ..service.global_context import GCT


def timestamp_to_date(timestamp, fmt='%Y-%m-%d %H:%M:%S'):
    # 如果是10位
    if len(str(timestamp)) == 13:
        timestamp = timestamp / 1000
    # 将10位时间戳转换为datetime对象
    dt = datetime.fromtimestamp(timestamp)
    # 格式化日期
    date = dt.strftime(fmt)
    return date

def date_to_timestamp(time_str):
    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return int(dt.timestamp())*1000

def generate_guid():
    return str(uuid.uuid4())

def is_json(s):
    if not isinstance(s, str):
        return False
    try:
        obj = json.loads(s)
        return isinstance(obj, (dict, list))  # 确保是对象或数组
    except json.JSONDecodeError:
        return False

def parse_chinese_time(text):
    now = datetime.now()

    if match := re.match(r"(\d+)分钟前", text):
        minutes = int(match.group(1))
        dt = now - timedelta(minutes=minutes)
    elif text.startswith("刚刚"):
        dt = now
    elif match := re.match(r"(\d+)小时前", text):
        hours = int(match.group(1))
        dt = now - timedelta(hours=hours)
    elif match := re.match(r"(\d+)天前", text):
        days = int(match.group(1))
        dt = now - timedelta(days=days)
    elif text.startswith("昨天"):
        time_part = text.replace("昨天", "").strip()
        if time_part:
            try:
                time_obj = datetime.strptime(time_part, "%H:%M")
                dt = datetime(now.year, now.month, now.day, time_obj.hour, time_obj.minute) - timedelta(days=1)
            except:
                dt = now - timedelta(days=1)
        else:
            dt = now - timedelta(days=1)
    elif re.match(r"^\d{2}:\d{2}$", text):  # HH:MM 格式，当天时间
        time_obj = datetime.strptime(text, "%H:%M")
        dt = datetime(now.year, now.month, now.day,
                      time_obj.hour, time_obj.minute)
    elif re.match(r"\d{2}-\d{2}$", text):  # MM-DD
        dt = datetime.strptime(f"{now.year}-{text}", "%Y-%m-%d")
    elif re.match(r"\d{4}-\d{2}-\d{2}", text):  # YYYY-MM-DD
        dt = datetime.strptime(text, "%Y-%m-%d")
    else:
        return None  # 不识别的格式

    return dt.strftime("%Y-%m-%d %H:%M:%S")

is_end_key = 'sys_is_end_key'
def off():
    GCT().remove(is_end_key)

def on():
    GCT().set(is_end_key, True)

def check_end():
    if GCT().get(is_end_key) is None:
        return False
    return GCT().get(is_end_key)

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

def send(ws, type, option):
    ws.send(json.dumps({
        "type": type,
        "option": option
    }))

def run_sel(fun, re_time=10, sleep=0.8):
    num = 0
    while True:
        time.sleep(sleep)
        if num >= re_time:
            return None
        try:
            a = fun()
            if a:
                return a
        except Exception as e:
            pass
        num += 1
        time.sleep(0.5)

def getLinkToNoteUrl(option=None):
    # 参数组装
    if option is None:
        option = {}
    url = option['url'] if 'url' in option else ''

    res = requests.get(url, allow_redirects=False)  # 不跟随跳转# 默认是 True
    if res.is_redirect or res.status_code in (301, 302, 303, 307, 308):
        redirect_url = res.headers.get('Location')
        return redirect_url

    if 'discovery/item' in res.url or 'user/profile' in res.url:
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

def getUrl(str):
    strs = re.findall(r'https?://[^\s]+', str)
    return strs[0] if strs else None