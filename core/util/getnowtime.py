import time


def get_now_str():
    nowtime = time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
    return nowtime