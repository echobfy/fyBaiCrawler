# -*- coding: utf-8 -*-

import logging
import multiprocessing


class ProcessesPoll(object):

    def __init__(self, cpu_count=0):
        self.cores = cpu_count if cpu_count else multiprocessing.cpu_count()
        logging.info(' ---> number of processes is {cores}.'.format(cores=self.cores))
        self.pool = multiprocessing.Pool(processes=self.cores)

    def get_process_number(self):
        return self.cores

    def map_tasks(self, target, tasks):
        logging.info(' ---> map {len_of_tasks} to {target_name}.'.
                     format(len_of_tasks=len(tasks), target_name=target.__name__))

