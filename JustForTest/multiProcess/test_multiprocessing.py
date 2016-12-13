# -*- coding: utf-8 -*-

import sys
import time
import multiprocessing

# @see https://www.zhihu.com/collection/131534722


def f(x):
    return x * x


cores = multiprocessing.cpu_count()
print cores

pool = multiprocessing.Pool(processes=cores)
xs = range(5)


cnt = 0
for _ in pool.imap_unordered(f, xs):
    sys.stdout.write('done %d/%d\r' % (cnt, len(xs)))
    sys.stdout.flush()
    time.sleep(2)
    cnt += 1

