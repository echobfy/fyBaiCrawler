# -*- coding: utf-8 -*-

import sys
import time
import multiprocessing

# @see https://www.zhihu.com/collection/131534722


def f(x):
    return x * x


cores = multiprocessing.cpu_count()

pool = multiprocessing.Pool(processes=cores)
xs = range(10)


cnt = 0
for a in pool.imap_unordered(f, xs):
    print  a
    cnt += 1

