"""
跨平台 UI 弹窗工具
- Android 端调用原生 Dialog
- iOS 端使用独立的 WebWindow 弹窗（不依赖 form.html）
"""
import sys
import os


class UIHelper:
    _web_window = None      # form WebWindow 引用（iOS 用，可能会关闭）
    _alert_window = None    # 独立的弹窗 WebWindow（iOS 用，常驻）
    _is_ios = False         # 是否 iOS 环境
    _is_android = False     # 是否 Android 环境

    @classmethod
    def init_android(cls):
        """Android 环境初始化"""
        cls._is_android = True
        cls._is_ios = False

    @classmethod
    def init_ios(cls, win=None):
        """
        iOS 环境初始化
        :param win: WebWindow 实例（可选，用于兼容旧的调用方式）
        """
        cls._is_ios = True
        cls._is_android = False
        if win:
            cls._web_window = win

    @classmethod
    def set_web_window(cls, win):
        """设置 form WebWindow 引用（可选，用于兼容旧的调用方式）"""
        cls._web_window = win

    @classmethod
    def set_alert_window(cls, win):
        """设置独立的弹窗 WebWindow（必须在 iOS 端初始化后创建）"""
        cls._alert_window = win

    @classmethod
    def _ios_call_js(cls, js_code):
        """
        iOS 端调用 JavaScript
        优先使用独立的 alert_window，如果不存在则尝试 web_window
        """
        if cls._alert_window:
            try:
                cls._alert_window.call(js_code)
                return
            except:
                pass
        if cls._web_window:
            try:
                cls._web_window.call(js_code)
                return
            except:
                pass
        # 都没有就打印日志
        print(f"[iOS JS] {js_code}")

    @classmethod
    def _ios_alert(cls, message, title=None):
        """iOS 原生 alert（使用 JavaScript 系统级弹窗）"""
        # 使用 JavaScript 原生 alert/confirm，这是系统级的
        msg = message.replace("'", "\\'")
        if title:
            title_str = title.replace("'", "\\'")
            js = f"alert('{title_str}\\n{msg}')"
        else:
            js = f"alert('{msg}')"
        cls._ios_call_js(js)

    @classmethod
    def confirm(cls, message, title=None, btn_text="确认"):
        """
        显示确认对话框
        :param message: 消息内容
        :param title: 标题（可选）
        :param btn_text: 按钮文字（iOS 不支持自定义，固定为 确认/取消）
        """
        if cls._is_ios:
            # iOS: 使用 JavaScript 原生 confirm（系统级弹窗）
            msg = message.replace("'", "\\'")
            if title:
                title_str = title.replace("'", "\\'")
                js = f"var r=confirm('{title_str}\\n{msg}');"
            else:
                js = f"var r=confirm('{msg}');"
            cls._ios_call_js(js)
        elif cls._is_android:
            # Android: 原生 Dialog
            from ascript.android.ui import Dialog
            Dialog.confirm(message, title, btn_text)
        else:
            # 其他环境（如 PC 测试）
            print(f"[CONFIRM] {title or '提示'}: {message}")

    @classmethod
    def toast(cls, message, dur=2000, gravity=None, x=None, y=None):
        """
        显示提示消息
        :param message: 消息内容
        :param dur: 持续时间（毫秒）（iOS 不支持，忽略）
        :param gravity: 位置（Android 专用）
        :param x: x 坐标（Android 专用）
        :param y: y 坐标（Android 专用）
        """
        if cls._is_ios:
            # iOS: 使用 JavaScript 原生 alert（系统级弹窗）
            # 注意：iOS 没有 Toast，只能用 alert 替代
            msg = message.replace("'", "\\'")
            js = f"alert('{msg}')"
            cls._ios_call_js(js)
        elif cls._is_android:
            # Android: 原生 Dialog
            from ascript.android.ui import Dialog
            kwargs = {'dur': dur}
            if gravity is not None:
                kwargs['gravity'] = gravity
            if x is not None:
                kwargs['x'] = x
            if y is not None:
                kwargs['y'] = y
            Dialog.toast(message, **kwargs)
        else:
            # 其他环境（如 PC 测试）
            print(f"[TOAST] {message}")
