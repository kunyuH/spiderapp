import time
from builtins import print, enumerate

from ascript.ios.node import Selector
from ascript.ios import system

from ..utils.tools import run_sel_s, generate_guid

re_time = 0.2
def test_run():
    user_id = '555cbb41e4b1cf4b1e86b4f8'
    system.scheme_start(f"xhsdiscover://user/{user_id}")
    exit()

    note_info = {}
    is_get_url = False

    # 确认详情页已经加载
    run_sel_s(lambda :Selector().label("点赞").type("XCUIElementTypeButton").enabled(True).visible(True).accessible(True).find(),4)

    is_video = True
    note_info['类型'] = 'video'
    # 确认是笔记 还是 视频
    if Selector().name("笔记正文").type("XCUIElementTypeOther").find():
        is_video = False
        note_info['类型'] = 'normal'
    if is_get_url:
        # ================获取分享的笔记链接================
        if is_video:
            Selector(2).type("Button").desc("分享.*").click().find()
            # 也可能是下面这个
            Selector(2).type("ImageView").desc("分享.*").click().find()
        else:
            Selector().type("XCUIElementTypeButton").index(3).find().click()

        exit()
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

        note_info['笔记分享链接'] = share_url
        note_info['笔记ID'] = getNoteIdByUrl(url)
        note_info['笔记链接'] = url
    else:
        note_info['笔记ID'] = generate_guid()
        t5 = time.time()
# def test_run():
#     notes_obj_str = 'Selector().type("XCUIElementTypeCollectionView").index(1).child().type("XCUIElementTypeCell").visible(True)'
#
#     notes = eval(notes_obj_str).find_all()
#     print(f"总数{len(notes)}")
#     for i, note in enumerate(notes):
#         print(f"第{i+2}个")
#         print('=============')
#
#         note_obj_str = notes_obj_str + f".index({i+2})" + '.child().type("XCUIElementTypeOther").child().type("XCUIElementTypeOther").child()'
#
#         # note_title = notes_obj.index(i+2).child().type("XCUIElementTypeOther").child().type("XCUIElementTypeOther").child().type("XCUIElementTypeOther").index(2).child().type("XCUIElementTypeStaticText").find()
#         note_title_obj = eval(note_obj_str).type("XCUIElementTypeOther").index(2).child().type("XCUIElementTypeStaticText").find()
#         note_title = note_title_obj.value
#         print(note_title)
#
#         author_name_obj = eval(note_obj_str).type("XCUIElementTypeOther").index(3).child().type('XCUIElementTypeStaticText').index(1).find()
#         author_name = author_name_obj.value
#         print(author_name)
#
#         push_time_obj = eval(note_obj_str).type("XCUIElementTypeOther").index(3).child().type('XCUIElementTypeStaticText').index(3).find()
#         push_time = push_time_obj.value
#         print(push_time)
#
#         like_num_obj = eval(note_obj_str).type("XCUIElementTypeOther").index(3).child().type('XCUIElementTypeButton').child().type('XCUIElementTypeStaticText').find()
#         like_num = like_num_obj.value
#         print(like_num)
#
#         # 点击
#         eval(note_obj_str).type("XCUIElementTypeOther").find().click()
#         exit()