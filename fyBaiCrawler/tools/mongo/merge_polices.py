# -*- encoding: utf-8 -*-

import os
import re
import sys
import logging
import tldextract

reload(sys)
sys.setdefaultencoding('utf-8')

PWD = os.getcwd()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(PWD)))   # '/Users/bfy/Documents/python/fyBaiCrawler'
sys.path.append(BASE_DIR)


class MergePolicy(object):
    def merge(self, merged_doc, doc_coll):
        raise NotImplemented


class AttributeMergePolicy(MergePolicy):

    def _extract_domain(self, url):
        return tldextract.extract(url).domain

    def _compare_com_url(self, url1, url2):
        domain1 = self._extract_domain(url1)
        domain2 = self._extract_domain(url2)
        if domain1 == domain2:
            return True
        return False

    def _compare_com_name(self, name, doc):
        if (doc.get('com_name') and name == doc['com_name']) \
                or (doc.get('com_registered_name') and name == doc['com_registered_name']) \
                    or (doc.get('com_sec_name') and name == doc['com_sec_name']):
            return True
        return False

    def merge(self, merged_doc, doc_coll):
        flag = False
        for doc in doc_coll:
            if merged_doc.get('com_name'):
                if self._compare_com_name(merged_doc['com_name'], doc):
                    doc['com_apps_apk'].append(merged_doc)
                    logging.info(' --> They have the same com_name, merging {com_name}'.format(com_name=merged_doc['com_name']))
                    flag = True
                    break
            if merged_doc.get('name'):
                if self._compare_com_name(merged_doc['name'], doc):
                    doc['com_apps_apk'].append(merged_doc)
                    logging.info(' --> They have the same app_name, merging {app_name}'.format(app_name=merged_doc['name']))
                    flag = True
                    break
            if merged_doc.get('com_url') and doc.get('com_url'):
                merged_doc_com_url = merged_doc.get('com_url')
                com_url = doc['com_url']
                if self._compare_com_url(merged_doc_com_url, com_url):
                    doc['com_apps_apk'].append(merged_doc)
                    logging.info(' ---> They have the same domain, which found in com_url {com_url}'.format(com_url=merged_doc_com_url))
                    flag = True
                    break
            if merged_doc.get('wandoujia_link') and doc.get('com_url'):
                link = merged_doc.get('wandoujia_link')
                match = re.search('.*apps/(.*)', link)
                if match:
                    lst = match.group(1).split('.')
                    lst.reverse()
                    if self._compare_com_url('.'.join(lst), doc['com_url']):
                        doc['com_apps_apk'].append(merged_doc)
                        logging.info(' ---> They have the same domain, which found in wandoujia_link {link}'.format(link=link))
                        flag = True
                        break

        if flag is False:
            logging.warning(' !!!!!! -----> Oh shit, no company find for this app {app_name}'
                            .format(app_name=merged_doc.get('name')))
        return flag


