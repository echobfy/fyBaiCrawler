# -*- coding: utf-8 -*-

from sys import platform as _platform


def get_platform_command(lst):
    """
    :param lst: lst[0] -> linux, lst[1] -> darwin, lst[2] -> win32
    :return:
    """
    if _platform == "linux" or _platform == "linux2":
        return lst[0]
    elif _platform == "darwin":
        return lst[1]
    elif _platform == "win32":
        return lst[2]


if __name__ == '__main__':
    print get_platform_command(['linux', 'macos', 'win32'])

