import ctypes
import win32process


# 获取当前线程的句柄
def get_current_thread():
    return ctypes.windll.kernel32.GetCurrentThread()


# 设置线程优先级
def set_thread_priority_to_high():
    win32process.SetThreadPriority(
        get_current_thread(), win32process.THREAD_PRIORITY_HIGHEST
    )
