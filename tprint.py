import datetime
import string
# import time
from random import *

fake_date = None


class Dict2Obj(object):
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, (list, tuple)):
                setattr(self, key, [Dict2Obj(x) if isinstance(x, dict) else x for x in value])
            else:
                setattr(self, key, Dict2Obj(value) if isinstance(value, dict) else value)


class TPrint:
    trace_on = None

    def __init__(self, to: True | False) -> None:
        self.trace_on = to

    def print(self, *args, **kwargs):
        if self.trace_on:
            print(*args, **kwargs)


def generate_password(length: int):
    char_set = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    cs_len = len(char_set)
    res = ''
    for _ in range(length):
        res += char_set[randrange(cs_len)]
    return res


def date2str(dt):
    return datetime.datetime.strftime(dt, "%Y-%m-%d %H:%M:%S")


def str2date(dt_str):
    return datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")


def now():
    if fake_date is None:
        return datetime.datetime.now()
    else:
        return fake_date


def date2str_full(dt):
    return datetime.datetime.strftime(dt, "%Y_%m_%d__%H_%M_%S_%f")


def timedelta(*args, **kwargs):
    return datetime.timedelta(*args, **kwargs)


def before(**kwargs):
    return now() - timedelta(**kwargs)


# Accept a list of strings, glue them together to the list of chunks,
# where each is as long as posible, but not longer than clip_length
# Append prefix and postfix to each chunk
def clip(rows: list, clip_length: int, prefix: str = '', postfix: str = None, ignore_new_lines=False):
    res = []
    current = prefix + rows[0]
    for row in rows[1:]:
        if len(current + row + postfix) > clip_length:
            res.append(current + postfix)
            current = prefix + row
        else:
            current += '\n' + row
    if current != prefix:
        res.append(current + postfix)
    return res


if __name__ == '__main__':

    # print(*clip(['abc\n', 'badfa\n', 'Gulmon\n'], 17, '<pre>', '</pre>'), sep='\n')
    print(clip(['abc', 'badfa', 'Gulmondur Gulmandury'], 25, '<pre>', '</pre>'))
    char_set = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    if ' ' in char_set:
        print('Oops!')
    else:
        print('OK!')
    # fake_date = now()
    # print(now())
    # time.sleep(10)
    # print(now())
    #
    # fake_date = None
    # print(now())
    # time.sleep(10)
    # print(now())

    # print(before(days=2))
    # print(string.punctuation)

    # trace_on = True
    # missions = []

    # def pr_trace(f):
    #     def wrapper(*args, **kwargs):
    #         f(*args, **kwargs)

    #     return wrapper

    # t = TPrint(True)
    # t = TPrint(False)
    # t.print("Hello")
    # trace_on = False
    # tprint("Hello")
