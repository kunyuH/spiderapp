import time
import traceback
from builtins import print, enumerate

from ascript.ios.node import Selector
from ascript.ios import system

from ..utils.tools import run_sel_s, generate_guid, run_sel

re_time = 0.2
def test_run():

    note_info = {}
    is_get_url = False
    is_shop = True

    # 确认详情页已经加载
    run_sel_s(lambda :Selector().label("点赞").type("XCUIElementTypeButton").enabled(True).visible(True).accessible(True).find(),4)

    is_video = True
    note_info['类型'] = 'video'
    # 确认是笔记 还是 视频
    if Selector().name("笔记正文").type("XCUIElementTypeOther").find():
        is_video = False
        note_info['类型'] = 'normal'
    if is_get_url:
        t5 = time.time()
        pass
    else:
        note_info['笔记ID'] = generate_guid()
        t5 = time.time()

    note_info['类型'] = 'video' if is_video else 'normal'
    t6 = time.time()
    print(f"ae耗时：{t6 - t5}")

    try:
        # ===============获取作者昵称================
        if '用户名称' not in note_info:
            if is_video:
                note_info['用户名称'] = run_sel(lambda :Selector().type("XCUIElementTypeStaticText").enabled(True).visible(True).accessible(True).index(0).find(),4,0.1).value
            else:
                note_info['用户名称'] = run_sel(lambda :Selector().type("XCUIElementTypeStaticText").enabled(True).visible(True).accessible(True).index(0).find(),4,0.1).value
        # ===============获取笔记标题================
        # ===============获取笔记内容================
        # ===============获取笔记发布时间================
        # ===============获取笔记发布地点================
        # ===============获取笔记点赞 收藏 评论 数================
        t7 = time.time()
        print(f"af耗时：{t7 - t6}")
        if is_video:
            note_info['内容'] = ''

            interaction_obj_str = 'Selector().label("说点什么...").type("XCUIElementTypeButton").enabled(True).visible(True).accessible(True).parent(1).brother(1)'
            if '评论数' not in note_info:
                print(run_sel_s(lambda: eval(interaction_obj_str).type("XCUIElementTypeOther").index(1).child().type("XCUIElementTypeButton").find(),
                                                2).value)
                print('zzz')
                exit()
                like = run_sel_s(lambda: eval(interaction_obj_str).type("XCUIElementTypeOther").index(1).child().type("XCUIElementTypeButton").find(),
                                                2).value.replace(' ', '').replace('点赞', '')
                if like:
                    note_info['点赞数'] = like.desc.replace(' ', '').replace('点赞', '')
                else:
                    note_info['点赞数'] = ''
                note_info['收藏数'] = eval(interaction_obj_str).type("XCUIElementTypeOther").index(2).child().type("XCUIElementTypeButton").find().value.replace(' ', '').replace('收藏', '')

                note_info['评论数'] = eval(interaction_obj_str).type("XCUIElementTypeOther").index(3).child().type("XCUIElementTypeButton").find().value.replace(' ', '').replace('评论', '').replace('抢首评', '')

                note_info['分享数'] = ''
        else:
            try:
                note_info['内容'] = Selector().name("笔记正文").type("XCUIElementTypeOther").enabled(True).visible(True).accessible(False).find().value
            except:
                try:
                    note_info['内容'] = Selector().name("笔记正文").type("XCUIElementTypeOther").enabled(True).visible(True).accessible(False).find().value
                except:
                    note_info['内容'] = ''
            interaction_obj_str = 'Selector().label("评论输入框").enabled(True).visible(True).accessible(False).brother().type("XCUIElementTypeOther")'

            if '评论数' not in note_info:
                note_info['点赞数'] = run_sel_s(lambda: Selector().label("点赞").type("XCUIElementTypeButton").enabled(True).visible(True).accessible(True).find(),
                                                2).value.replace(' ', '').replace('点赞', '')
                note_info['收藏数'] = Selector().label("收藏").type("XCUIElementTypeButton").enabled(True).visible(True).accessible(True).find().value.replace(' ', '').replace(
                    '收藏', '')
                note_info['评论数'] = Selector().label("评论").type("XCUIElementTypeButton").enabled(True).visible(True).accessible(True).find().value.replace(' ', '').replace(
                    '评论', '')
        # ===============获取作者主页信息================
        print(note_info)
        exit()
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
                Selector(2).text("店铺").type("TextView").parent(1).clickable(True).click().find()
                time.sleep(1)
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