import re
from datetime import datetime, timedelta
from venv import create
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


def date_to_timestamp(time_str):
    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return int(dt.timestamp())*1000

create_time = '18:09'
a = parse_chinese_time(create_time)
pass