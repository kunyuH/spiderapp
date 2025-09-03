import json
import threading

from websocket import WebSocketApp
import traceback
from ascript.android.ui import Dialog
from ascript.android import system

from ..utils.tools import is_json, send
from .global_context import GCT

class HooSock:

    func = None
    web_sock_key = 'Websocket'

    def __init__(self, url, app_uuid=None):
        self.url = url
        self.app_uuid = app_uuid

    def set_on_message(self, func):
        self.func = func
        return self

    def start(self):
        if GCT().get('Websocket') is None:

            def on_message(ws, message):
                print("=====：%s" % message)
                if message == '__ping__':
                    ws.send('__pong__')
                    print('__pong__')
                elif message == "__server_shutdown__":
                    print("服务端关闭了，客户端准备断开")
                    ws.close()
                    return
                else:
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