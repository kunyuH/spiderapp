import re
from datetime import timedelta, datetime


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
    # 好心疼这些土地啊， 11小时前 江苏

    # 时间模式
    time_pattern = (
         r"(?:"
        r"(?:刚刚|刚才|今天|昨天|昨日|前天)(?:\s+\d{1,2}:\d{2})?"  # 相对时间 + 可选 HH:MM
        r"|\d+分钟前|\d+小时前|\d+天前"                               # 数字时间
        r"|\d{1,2}:\d{2}"                                           # HH:MM
        r"|\d{2}-\d{2}"                                             # MM-DD
        r"|\d{4}-\d{2}-\d{2}"                                       # YYYY-MM-DD
        r")"
    )

    # 完整正则：评论 + 空格 + 时间 + 可选空格 + 可选IP(中文) + 结尾
    # pattern = re.compile(rf"(.*?)\s+({time_pattern})(?:\s+([\u4e00-\u9fa5]+))?$")
    # pattern = re.compile(rf"^(.*?)(?:\s+({time_pattern})(?:\s+([\u4e00-\u9fa5]+))?)?$")
    pattern = re.compile(rf"^(.*?)(?:\s*({time_pattern})(?:\s+([\u4e00-\u9fa5]+))?)?$")

    # pattern = re.compile(rf"^(.*?)(?:\s+({time_pattern})(?:\s+([\u4e00-\u9fa5]+))?)?$")

    match = pattern.match(content)
    # 如果只分出来两个 则
    if match:
        comment = match.group(1).strip() or None
        time_text = match.group(2).strip() if match.group(2) else None
        ip_text = match.group(3).strip() if match.group(3) else None
    else:
        # 如果末尾没有时间，则全部视为评论
        comment = content
        time_text = None
        ip_text = None

    # print(f"原始: {content}")
    # print(f"时间: {time_text}, IP属地: {ip_text}")
    # print(f"内容: {comment}")
    # print("-" * 30)
    return time_text, ip_text, comment

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

cc = [
    # "我的美食，还 有 昨日 12:50 北京",
    # "我的美食，还 有 昨日 12:50",
    # "我的美食，还 有 昨日 23:50 北京",
    # "我的美食，还 有 昨日 22:50",
    # "我的美食，还 有 12:50 北京",
    # "我的美食，还 有 12:50",
    # "好心疼这些土地啊， 11小时前 江苏",
    # "好心疼这些土地啊， 11小时前",
    # "好心疼这些土地啊， 1分钟前 江苏",
    # "好心疼这些土地啊， 1分钟前",
    # "好心疼这些土地啊， 刚刚 江苏",
    # "好心疼这些土地啊， 刚刚",
    # "好心疼这些土地啊， 05-24",
    "好心疼这些土地啊， 05-24 江苏",
    "好心疼这些土地啊， 2025-05-24 江苏",
    "好心疼这些土地啊， 2023-05-24",
    "28分钟前 浙江",
]

for c in cc:
    a,b,v = ip_date(c)
    print(c)
    print(a)
    print(b)
    print(v)
    print(parse_chinese_time(a))
    print('=================')