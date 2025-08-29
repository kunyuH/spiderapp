import threading

"""
全局唯一
多线程唯一
上下文管理
"""


class GCT:
    _instance = None
    _lock = threading.Lock()  # 用于线程安全

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls, *args, **kwargs)
                cls._instance._data = {}  # 初始化状态数据存储
        return cls._instance

    def set(self, key, value):
        with self._lock:
            self._data[key] = value

    def get(self, key, default=None):
        with self._lock:
            return self._data.get(key, default)

    def keys(self):
        with self._lock:
            return self._data.keys()

    def remove(self, key):
        with self._lock:
            if key in self._data:
                del self._data[key]

    def clear(self):
        with self._lock:
            self._data.clear()

    def __repr__(self):
        with self._lock:
            return f"GCT({self._data})"
