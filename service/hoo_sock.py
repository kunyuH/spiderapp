import json
import threading
import time
from urllib.parse import urlparse

import socket
from websocket import WebSocketApp
import traceback
from ascript.android.ui import Dialog

from utils.tools import system_exit
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
                system_exit()
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
                system_exit()  # 直接退出程序，不再重连
                break

            # # 手动连接的 出错后 不再自动连了 直接退出
            # print(f'self.is_first_connect:{self.is_first_connect}')
            # if self.is_first_connect:
            #     Dialog.confirm("连接失败！", None, "确认")
            #     system_exit()  # 直接退出程序，不再重连
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

        # 启动心跳检测
        # 每隔一段时间ping服务器
        self._start_heartbeat(ws)

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

        try:
            if is_json(message):
                msg = json.loads(message)
                if msg.get("type") == "__pong__":
                    rtt = int(time.time() * 1000) - msg.get("ts")
                    print(f"📡 WebSocket RTT: {rtt} ms")
                    # Dialog.toast(f"{rtt} ms", dur=5000)
                    # Dialog.toast(f"{rtt}ms", 6000, 5 | 48, 0, 0, "#AD93FF", "#F8C03E")
                    self._record_rtt(rtt)
                    return
                else:
                    print("=====：%s" % message)
                    threading.Thread(
                        target=self.func,
                        args=(ws, msg.get('type'), msg.get('option')),
                        daemon=True
                    ).start()
        except Exception as e:
            print(e)
            traceback.print_exc()

    def _start_heartbeat(self, ws):
        def loop():
            while self.connected and not self.manual_stop:
                try:
                    ts = int(time.time() * 1000)
                    ws.send(json.dumps({
                        "type": "__ping__",
                        "ts": ts
                    }))
                except Exception as e:
                    print("心跳发送失败:", e)
                    break
                time.sleep(5)  # 5 秒一次

        threading.Thread(target=loop, daemon=True).start()

    def _record_rtt(self, rtt):
        if rtt < 200:
            level = "GOOD"
        elif rtt < 800:
            level = "WARN"
        else:
            level = "BAD"

        print(f"网络质量: {level}")

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
        # system_exit()  # 直接退出程序，不再重连

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
