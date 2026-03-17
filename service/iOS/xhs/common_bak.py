import time
import traceback
from ascript.ios.node import Selector
from ascript.ios import system
from ascript.ios import action
import xml.etree.ElementTree as ET

from ...hoo_xml import find
from ....utils.tools import run_sel, run_sel_s, generate_guid

def get_user_info(note_info=None):
    """
    获取作者主页信息
    """
    user_all_obj_str = 'Selector().type("XCUIElementTypeCollectionView").enabled(True).visible(True).accessible(False).index(1)'
    user_info_obj_str = user_all_obj_str + '.child().type("XCUIElementTypeCell").index(2).child().type("XCUIElementTypeOther").index(0).child().type("XCUIElementTypeOther").index(2)'

    # 获取用户名称
    note_info['用户名称'] = run_sel_s(
        lambda: eval(user_info_obj_str).child().type("XCUIElementTypeOther").index(0).child().type(
            "XCUIElementTypeButton").find(), 4).name

    xml_info = Selector.xml()
    tree = ET.fromstring(xml_info)

    try:
        # note_info['用户小红书号'] = run_sel_s(lambda :eval(user_info_obj_str).child().type("XCUIElementTypeOther").index(1).child().type("XCUIElementTypeStaticText").find(),2).value.replace('小红书号：', '')
        note_info['用户小红书号'] = \
        find(tree, user_info_obj_str + '.child().type("XCUIElementTypeStaticText")')[
            'value'].replace('小红书号：', '')
    except Exception as e:
        try:
            # note_info['用户小红书号'] = eval(user_info_obj_str).child().type("XCUIElementTypeOther").index(1).child().type("XCUIElementTypeStaticText").find().value.replace('小红书号：', '')
            note_info['用户小红书号'] = find(tree,user_info_obj_str + '.child().type("XCUIElementTypeOther").index(1).child().type("XCUIElementTypeStaticText")')[
                'value'].replace('小红书号：', '')
        except Exception as e:
            note_info['用户小红书号'] = ''

    try:
        # note_info['用户IP属地'] = eval(user_info_obj_str).child().type("XCUIElementTypeButton").index(3).find().name.replace('IP属地：', '').replace('IP：', '')
        note_info['用户IP属地'] = find(tree, user_info_obj_str + '.child().type("XCUIElementTypeButton").index(3)')['name'].replace('IP属地：',
                                                                                                           '').replace(
            'IP：', '')
    except Exception as e:
        note_info['用户IP属地'] = ''

    try:
        # note_info['用户简介'] = eval(user_all_obj_str).child().type("XCUIElementTypeCell").index(4).child().type("XCUIElementTypeOther").index(0).child().type("XCUIElementTypeButton").index(0).find().name
        note_info['用户简介'] = find(tree, user_info_obj_str + '.child().type("XCUIElementTypeCell").index(4).child().type("XCUIElementTypeOther").index(0).child().type("XCUIElementTypeButton").index(0)')['name']
    except Exception as e:
        note_info['用户简介'] = ''
    note_info['用户性别'] = ''

    # 用户关注
    try:
        # follows = Selector().value("关注").type("XCUIElementTypeStaticText").enabled(True).visible(True).accessible(True).index(1).brother().type("XCUIElementTypeStaticText").index(0).find().value
        follows = find(tree,'Selector().value("关注").type("XCUIElementTypeStaticText").enabled(True).visible(True).accessible(True).index(1).brother().type("XCUIElementTypeStaticText").index(0)')['value']
    except Exception as e:
        follows = ''
    # 用户粉丝
    try:
        # fans = Selector().value("粉丝").type("XCUIElementTypeStaticText").enabled(True).visible(True).accessible(True).index(1).brother().type("XCUIElementTypeStaticText").index(0).find().value
        fans = find(tree,
                    'Selector().value("粉丝").type("XCUIElementTypeStaticText").enabled(True).visible(True).accessible(True).index(1).brother().type("XCUIElementTypeStaticText").index(0)')[
            'name']
    except Exception as e:
        fans = ''
    # 用户获赞与收藏
    try:
        # interaction = Selector().value("获赞与收藏").type("XCUIElementTypeStaticText").enabled(True).visible(True).accessible(True).index(1).brother().type("XCUIElementTypeStaticText").index(0).find().value
        interaction = find(tree,
                           'Selector().value("获赞与收藏").type("XCUIElementTypeStaticText").enabled(True).visible(True).accessible(True).index(1).brother().type("XCUIElementTypeStaticText").index(0)')[
            'value']
    except Exception as e:
        interaction = ''

    note_info['用户关注'] = follows
    note_info['用户粉丝'] = fans
    note_info['用户获赞与收藏'] = interaction

    try:
        # if Selector().name("店铺").label("店铺").value("店铺").type("XCUIElementTypeStaticText").enabled(True).visible(True).accessible(True).find():
        if find(tree,
                'Selector().name("店铺").label("店铺").value("店铺").type("XCUIElementTypeStaticText").enabled(True).visible(True).accessible(True)')[
            'value']:
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
    shop_info_obj_str = ('Selector().type("XCUIElementTypeCollectionView").enabled(True).visible(True).accessible(False).index(2)'
                         '.child().type("XCUIElementTypeCell").index(0)'
                         '.child().type("XCUIElementTypeOther").index(0)'
                         '.child().type("XCUIElementTypeOther").index(0)'
                         '.child().type("XCUIElementTypeOther").index(0)'
                         '.child().type("XCUIElementTypeOther").index(0)'
                         '.child().type("XCUIElementTypeOther").index(0)'
                         '.child().type("XCUIElementTypeOther").index(1)')

    note_info['店铺名称'] = run_sel(lambda :eval(shop_info_obj_str).child().type("XCUIElementTypeOther").index(0).child().type("XCUIElementTypeButton").index(0).find(),4,0.5).name

    xml_info = Selector.xml()
    tree = ET.fromstring(xml_info)

    # note_info['店铺星级'] = (eval(shop_info_obj_str).child().type("XCUIElementTypeOther").index(1)
    #                          .child().type("XCUIElementTypeOther").index(0)
    #                          .child().type("XCUIElementTypeOther")
    #                          .child().type("XCUIElementTypeOther")
    #                          .child().type("XCUIElementTypeOther")
    #                          .child().type("XCUIElementTypeOther")
    #                          .child().type("XCUIElementTypeOther")
    #                          .child().type("XCUIElementTypeStaticText")
    #                          .find().value)

    note_info['店铺星级'] = find(tree,shop_info_obj_str+'.child().type("XCUIElementTypeOther").index(1)'
                                                        '.child().type("XCUIElementTypeOther").index(0)'
                                                        '.child().type("XCUIElementTypeOther")'
                                                         '.child().type("XCUIElementTypeOther")'
                                                         '.child().type("XCUIElementTypeOther")'
                                                         '.child().type("XCUIElementTypeOther")'
                                                         '.child().type("XCUIElementTypeOther")'
                                                         '.child().type("XCUIElementTypeStaticText")')['value']

    # note_info['店铺已售'] = (eval(shop_info_obj_str).child().type("XCUIElementTypeOther").index(1)
    #                          .child().type("XCUIElementTypeOther").index(1)
    #                          .child().type("XCUIElementTypeOther")
    #                          .child().type("XCUIElementTypeOther")
    #                          .child().type("XCUIElementTypeOther")
    #                          .child().type("XCUIElementTypeOther")
    #                          .child().type("XCUIElementTypeOther")
    #                          .child().type("XCUIElementTypeStaticText")
    #                          .find().value).replace('已售', '')
    note_info['店铺已售'] = find(tree,shop_info_obj_str+'.child().type("XCUIElementTypeOther").index(1)'
                                                        '.child().type("XCUIElementTypeOther").index(1)'
                                                        '.child().type("XCUIElementTypeOther")'
                                                         '.child().type("XCUIElementTypeOther")'
                                                         '.child().type("XCUIElementTypeOther")'
                                                         '.child().type("XCUIElementTypeOther")'
                                                         '.child().type("XCUIElementTypeOther")'
                                                         '.child().type("XCUIElementTypeStaticText")')['value'].replace('已售', '')

    # note_info['店铺粉丝'] = (eval(shop_info_obj_str).child().type("XCUIElementTypeOther").index(2)
    #                          .child().type("XCUIElementTypeOther")
    #                          .child().type("XCUIElementTypeOther")
    #                          .child().type("XCUIElementTypeOther")
    #                          .child().type("XCUIElementTypeOther")
    #                          .child().type("XCUIElementTypeOther")
    #                          .child().type("XCUIElementTypeStaticText")
    #                          .find().value).replace('粉丝', '')
    note_info['店铺粉丝'] = find(tree, shop_info_obj_str + '.child().type("XCUIElementTypeOther").index(2)'
                                                           '.child().type("XCUIElementTypeOther")'
                                                           '.child().type("XCUIElementTypeOther")'
                                                           '.child().type("XCUIElementTypeOther")'
                                                           '.child().type("XCUIElementTypeOther")'
                                                           '.child().type("XCUIElementTypeOther")'
                                                           '.child().type("XCUIElementTypeStaticText")')['value'].replace('粉丝', '')
    return note_info

def is_shop_detail_page():
    try:
        if Selector().xpath("//*[starts-with(@name, '已售')]").find():
            return True
        return False
    except:
        return False

def back():
    action.touch_and_slide(422,1707,2087,1720,500,600,500)

def get_note_info(note_info=None,is_shop=False,is_get_url=True):
    """
    获取笔记详情  两种情况 1.笔记  2.视频
    :return:
    """
    t1 = time.time()
    # 确认详情页已经加载
    run_sel_s(lambda: Selector().label("点赞").type("XCUIElementTypeButton").enabled(True).visible(True).accessible(
        True).find(), 4)

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
                note_info['用户名称'] = run_sel(
                    lambda: Selector().type("XCUIElementTypeStaticText").enabled(True).visible(True).accessible(
                        True).index(0).find(), 4, 0.1).value
            else:
                note_info['用户名称'] = run_sel(
                    lambda: Selector().type("XCUIElementTypeStaticText").enabled(True).visible(True).accessible(
                        True).index(0).find(), 4, 0.1).value
        # ===============获取笔记标题================
        # ===============获取笔记内容================
        # ===============获取笔记发布时间================
        # ===============获取笔记发布地点================
        # ===============获取笔记点赞 收藏 评论 数================
        t7 = time.time()
        print(f"af耗时：{t7 - t6}")
        if is_video:
            note_info['内容'] = ''

            interaction_obj_str = 'Selector().label("说点什么...").type("XCUIElementTypeButton").enabled(True).visible(True).accessible(True).parent(1).brother()'
            if '评论数' not in note_info:
                like = run_sel_s(lambda: eval(interaction_obj_str).type("XCUIElementTypeOther").index(1).child().type("XCUIElementTypeButton").find(),
                                 2).name.replace(' ', '').replace('点赞', '')
                if like:
                    note_info['点赞数'] = like.replace(' ', '').replace('点赞', '')
                else:
                    note_info['点赞数'] = ''
                note_info['收藏数'] = eval(interaction_obj_str).type("XCUIElementTypeOther").index(2).child().type(
                    "XCUIElementTypeButton").find().name.replace(' ', '').replace('收藏', '')

                note_info['评论数'] = eval(interaction_obj_str).type("XCUIElementTypeOther").index(3).child().type(
                    "XCUIElementTypeButton").find().name.replace(' ', '').replace('评论', '').replace('抢首评', '')

                note_info['分享数'] = ''
        else:
            try:
                note_info['内容'] = Selector().name("笔记正文").type("XCUIElementTypeOther").enabled(True).visible(
                    True).accessible(False).find().value
            except:
                try:
                    note_info['内容'] = Selector().name("笔记正文").type("XCUIElementTypeOther").enabled(True).visible(
                        True).accessible(False).find().value
                except:
                    note_info['内容'] = ''
            interaction_obj_str = 'Selector().label("评论输入框").enabled(True).visible(True).accessible(False).brother().type("XCUIElementTypeOther")'

            if '评论数' not in note_info:
                note_info['点赞数'] = run_sel_s(
                    lambda: Selector().label("点赞").type("XCUIElementTypeButton").enabled(True).visible(
                        True).accessible(True).find(),
                    2).value.replace(' ', '').replace('点赞', '')
                note_info['收藏数'] = Selector().label("收藏").type("XCUIElementTypeButton").enabled(True).visible(
                    True).accessible(True).find().value.replace(' ', '').replace(
                    '收藏', '')
                note_info['评论数'] = Selector().label("评论").type("XCUIElementTypeButton").enabled(True).visible(
                    True).accessible(True).find().value.replace(' ', '').replace(
                    '评论', '')
        # ===============获取作者主页信息================
        t8 = time.time()
        print(f"ag耗时：{t8 - t7}")
        if is_shop:
            # 点击用户名称进入用户主页
            if is_video:
                Selector().type("XCUIElementTypeStaticText").enabled(True).visible(True).accessible(True).index(
                    0).find().click()
            else:
                Selector().type("XCUIElementTypeStaticText").enabled(True).visible(True).accessible(True).index(
                    0).find().click()
            note_info = get_user_info(note_info)

            # ===============获取店铺信息================
            if is_shop and note_info['是否有店铺'] == '有':
                # 进入作者店铺内
                Selector().name("店铺").label("店铺").value("店铺").type("XCUIElementTypeStaticText").enabled(
                    True).visible(True).accessible(True).find().click()
                time.sleep(1)
                note_info = get_shop_info(note_info)
                # 返回用户信息页
                print('===========返回用户信息页=====')
                back()
                time.sleep(0.2)
                if is_shop_detail_page():
                    back()
                    time.sleep(0.5)
                    if is_shop_detail_page():
                        back()
                        time.sleep(0.5)
            # 返回笔记详情页
            print('===========返回笔记详情页=====')
            time.sleep(0.2)
            # Selector(2).desc("返回").type("ImageView").click().find()
            back()
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


def check_search(sort_type,filter_note_type,filter_note_time,filter_note_range):
    # 点击下拉筛选
    Selector().type("XCUIElementTypeButton").label("全部").click(0).find()
    # parent_index = 3
    # if (Selector().type("XCUIElementTypeStaticText").value("最新")
    #         .label("最新").name("最新").visible(True)
    #          .find()):
    #     parent_index = 1
    # 排序依据点击
    if sort_type != 'general':
        if sort_type == 'time_descending':  # 最新
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("最新")
             .label("最新")
             .name("最新")
             .visible(True)
             .click(0).find())
        elif sort_type == 'popularity_descending':  # 最多点赞
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("最多点赞")
             .label("最多点赞")
             .name("最多点赞")
             .visible(True)
             .click(0).find())
        elif sort_type == 'comment_descending':  # 最多评论
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("最多评论")
             .label("最多评论")
             .name("最多评论")
             .visible(True)
             .click(0).find())
        elif sort_type == 'collect_descending':  # 最多收藏
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("最多收藏")
             .label("最多收藏")
             .name("最多收藏")
             .visible(True)
             .click(0).find())
    # 笔记类型点击
    if filter_note_type != '不限':
        if filter_note_type == '视频':  # 视频
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("视频")
             .label("视频")
             .name("视频")
             .visible(True)
             .click(0).find())
        elif filter_note_type == '图文':  # 图文
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("图文")
             .label("图文")
             .name("图文")
             .visible(True)
             .click(0).find())
    # 发布时间点击
    if filter_note_time != '不限':
        if filter_note_time == '一天内':  # 一天内
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("一天内")
             .label("一天内")
             .name("一天内")
             .visible(True)
             .click(0).find())
        elif filter_note_time == '一周内':  # 一周内
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("一周内")
             .label("一周内")
             .name("一周内")
             .visible(True)
             .click(0).find())
        elif filter_note_time == '半年内':  # 半年内
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("半年内")
             .label("半年内")
             .name("半年内")
             .visible(True)
             .click(0).find())
    # 搜索范围点击
    if filter_note_range != '不限':
        if filter_note_range == '已看过':  # 已看过
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("已看过")
             .label("已看过")
             .name("已看过")
             .visible(True)
             .click(0).find())
        elif filter_note_range == '未看过':  # 未看过
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("未看过")
             .label("未看过")
             .name("未看过")
             .visible(True)
             .click(0).find())
        elif filter_note_range == '已关注':  # 已关注
            (Selector()
             .type("XCUIElementTypeStaticText")
             .value("已关注")
             .label("已关注")
             .name("已关注")
             .visible(True)
             .click(0).find())
    time.sleep(0.5)
    # 点击收起
    (Selector()
     .type("XCUIElementTypeStaticText")
     .value("收起")
     .label("收起")
     .name("收起")
     .visible(True)
     .click(0).find())
