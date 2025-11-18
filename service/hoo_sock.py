import json
import threading
import time
from urllib.parse import urlparse

import socket
from websocket import WebSocketApp
import traceback
from ascript.android.ui import Dialog
from ascript.android import system

from ..utils.tools import is_json, send
from .global_context import GCT

class HooSock:

    func = None
    web_sock_key = 'Websocket'

    def __init__(self, url, app_uuid=None, reconnect_interval=2, max_reconnect=10):
        self.url = url
        self.app_uuid = app_uuid

        self.reconnect_interval = reconnect_interval    # 重连间隔时间
        self.max_reconnect = max_reconnect  # 最大重连次数
        self.reconnect_count = 0  # 当前重连次数

        self.connected = False  # 是否已连接
        self.manual_stop = False  # 用于手动关闭，不触发重连

        # self.run_source = True  # ⭐ 区分手动连接

        # 是否首次成功
        # reconnect_count = 0 时就成功了
        # self.is_first_connect = True

    def set_on_message(self, func):
        self.func = func
        return self
    # =============================
    # 主入口函数: 启动 WebSocket
    # =============================
    def start(self):

        # 避免重复启动
        if GCT().get(self.web_sock_key) is not None:
            print("WebSocket 已在运行，无需重复启动")
            return
        print('连接中')
        # 启动独立线程连接
        threading.Thread(target=self._run_forever, daemon=True).start()

    # =================================================
    # 核心：自动重连循环
    # =================================================
    def _run_forever(self):
        while not self.manual_stop:

            if self.reconnect_count >= self.max_reconnect:
                print("已达到最大重连次数，停止重连")
                Dialog.confirm("连接已断开！", None, "确认")
                system.exit()
                break

            print(f"尝试连接 WebSocket 1: {self.url}")
            ws = WebSocketApp(
                self.url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            print(f"尝试连接 WebSocket 2: {self.url}")
            # 放入全局缓存
            GCT().set(self.web_sock_key, ws)
            try:
                ws.run_forever()  # 此时 run_forever 不会再卡住
            except Exception as e:
                print("WebSocket 运行异常:", e)

            # 运行到这里说明连接已断开
            self.connected = False
            GCT().set(self.web_sock_key, None)

            if self.manual_stop:
                Dialog.confirm("连接已关闭！", None, "确认")
                system.exit()  # 直接退出程序，不再重连
                break

            # # 手动连接的 出错后 不再自动连了 直接退出
            # print(f'self.is_first_connect:{self.is_first_connect}')
            # if self.is_first_connect:
            #     Dialog.confirm("连接失败！", None, "确认")
            #     system.exit()  # 直接退出程序，不再重连
            #     break

            # 增加重连次数
            self.reconnect_count += 1

            print(f"连接断开，{self.reconnect_interval} 秒后重试...")
            Dialog.toast(f"连接已断开，第{self.reconnect_count}次重连...", dur=2000)

            time.sleep(self.reconnect_interval)

    # =================================================
    # 事件处理：open / message / error / close
    # =================================================
    def _on_open(self, ws):
        print("####### on_open #######")
        self.connected = True

        # ⭐⭐⭐ 连上后立刻重置重连次数 ⭐⭐⭐
        self.reconnect_count = 0

        Dialog.toast("已连接", dur=2000, gravity=1 | 16, x=0, y=200)

        # 发送 UUID
        send(ws=ws, type='change_uuid', option={
            "app_uuid": self.app_uuid
        })

    def _on_message(self, ws, message):
        # 心跳包
        if message == '__ping__':
            ws.send('__pong__')
            return

        if message == "__server_shutdown__":
            print("服务端关闭，客户端准备断开")
            self.stop()
            return

        print("=====：%s" % message)
        try:
            if is_json(message):
                msg = json.loads(message)
                threading.Thread(
                    target=self.func,
                    args=(ws, msg.get('type'), msg.get('option')),
                    daemon=True
                ).start()
        except Exception as e:
            print(e)
            traceback.print_exc()

    def _on_error(self, ws, error):
        print("####### on_error #######")
        print("error:", error)
        traceback.print_exc()
        # 不 exit，交给自动重连
        Dialog.toast("连接异常，尝试重连...", dur=2000)
        self.connected = False
        # self.is_first_connect = False

    def _on_close(self, ws, status, msg):
        print("####### on_close #######")
        print("close_status_code:", status)
        print("close_msg:", msg)
        # 不 exit，自动重连
        Dialog.toast("连接断开...", dur=2000)
        self.connected = False
        # self.is_first_connect = False
        # Dialog.confirm("连接已关闭！", None, "确认")
        # system.exit()  # 直接退出程序，不再重连

    # =================================================
    # 手动关闭连接
    # =================================================
    def stop(self):
        """手动停止 WebSocket，不再自动重连"""
        self.manual_stop = True
        ws = GCT().get(self.web_sock_key)
        if ws:
            ws.close()
        GCT().set(self.web_sock_key, None)
        print("WebSocket 已手动关闭")

    def start_z(self):
        if GCT().get('Websocket') is None:

            def on_message(ws, message):
                if message == '__ping__':
                    ws.send('__pong__')
                    # print('__pong__')
                elif message == "__server_shutdown__":
                    print("服务端关闭了，客户端准备断开")
                    ws.close()
                    return
                else:
                    print("=====：%s" % message)
                    try:
                        # print("####### on_message #######")
                        # print("message：%s" % message)
                        if is_json(message):
                            msg = json.loads(message)
                            # 客户端id
                            # client_id = msg.get('id')
                            # 把耗时逻辑放到子线程执行
                            threading.Thread(
                                target=self.func,
                                args=(ws, msg.get('type'), msg.get('option')),
                                daemon=True
                            ).start()

                    except Exception as e:
                        print(e)
                        traceback.print_exc()
                pass

            def on_error(ws, error):
                print("####### on_error #######")
                print("error：%s" % error)
                traceback.print_exc()
                # Dialog.toast("连接异常", dur=3000, gravity=1 | 16, x=0, y=200, bg_color=None, color=None, font_size=0)
                Dialog.confirm("连接已断开！", None, "确认")
                system.exit()

            def on_close(ws,close_status_code, close_msg):
                print("####### on_close #######")
                print("close_status_code:", close_status_code)
                print("close_msg:", close_msg)
                Dialog.confirm("连接已断开！", None, "确认")
                system.exit()

            def on_open(ws):
                print("####### on_open #######")
                Dialog.toast("已连接", dur=3000, gravity=1 | 16, x=0, y=200, bg_color=None, color=None, font_size=0)
                send(ws=ws,type='change_uuid',option={
                    "app_uuid": self.app_uuid
                })

            def server_thread():
                # url = "ws://192.168.0.101:10102"
                # url = self.url
                print(self.url)

                ws = WebSocketApp(self.url,
                                  on_open=on_open,
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close
                )
                GCT().set(self.web_sock_key, ws)
                ws.run_forever()  # 不传 timeout

            threading.Thread(target=server_thread, daemon=True).start()