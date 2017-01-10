# -*- encoding: utf-8 -*-

import jieba


class JieBaTokenizer(object):

    def __init__(self):
        jieba.load_userdict('/Users/fybai/fyBai-Files/PycharmProjects/fyBaiCrawler/fyBaiCrawler/tools/jieba/dict.txt') # 加载自定义公司名称

    def tokenizer(self, words):
        return list(jieba.cut(words, cut_all=True))
