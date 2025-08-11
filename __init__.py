#展示一个简单的Html页面
from ascript.android.ui import WebWindow
from ascript.android.system import R

def tunnel(k,v):
    print(k)
    print(v)

# 构建一个WebWindow 显示‘/res/ui/a.html’ 通信通道为tunnel 函数
w = WebWindow(R.ui('index.html'),tunnel)
w.show()