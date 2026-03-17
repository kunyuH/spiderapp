import sys
from .test.test import test_run

# test_run()
# exit()

from .service.global_context import GCT

# 重置 GCT 单例（解决重启后缓存未释放问题）
GCT.reset_instance()
# 清理缓存
print(GCT().keys())
print('已经清空')



if sys.platform == "android":
    from .controllers.android import form
    form.run()
elif sys.platform == "ios":
    from .controllers.iOS import form_iOS
    form_iOS.run()
else:
    print("其他平台")