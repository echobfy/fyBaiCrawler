# -*- encoding: utf-8 -*-

import os
import sys


reload(sys)
sys.setdefaultencoding('utf-8')

PWD = os.getcwd()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(PWD)))   # '/Users/bfy/Documents/python/fyBaiCrawler'
sys.path.append(BASE_DIR)

from sklearn.feature_extraction.text import TfidfVectorizer

from fyBaiCrawler.tools.mongo.read_field import ReadFieldFromMongo
from fyBaiCrawler.tools.jieba.tokenizer import JieBaTokenizer


class TFIDF(object):

    def __init__(self):
        self.vectorizer = TfidfVectorizer()

    def evaluate_tfidf(self, corpus):
        return self.vectorizer.fit_transform(corpus)


if __name__ == '__main__':
    tf_idf = TFIDF()
    jie_ba = JieBaTokenizer()
    mongo_client = ReadFieldFromMongo('mongodb://localhost:27017/itjuzi', 'company_list')

    corpus = []
    for field, value in mongo_client.read_from_mongo('com_registered_name'):
        value = value.strip()
        if value:
            tokens = ' '.join(jie_ba.tokenizer(value))
            corpus.append(tokens)

    weight = tf_idf.evaluate_tfidf(corpus)

    new_words = "惠州市德赛西威汽车电子股份有限公司"
    tokens = jie_ba.tokenizer(new_words)








