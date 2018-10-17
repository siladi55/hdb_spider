# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
import datetime
import csv


class HdbPipeline(object):

    def __init__(self):
        today = str(datetime.datetime.today())[:10]
        timestamp = str(int(time.time()))
        filename = 'recent_exhibition_{}_{}.csv'.format(today, timestamp)
        self.file = open(filename, 'a', encoding='utf-8', newline='')
        self.writer = csv.writer(self.file, dialect='excel')
        self.writer.writerow([
            '举办日期', '主题', 'URL', '主办方', '举办地址', '门票费用（元）', '参会人数'
        ])

    def process_item(self, item, spider):
        ls = [item['hostime'],
              item['subject'],
              item['url'],
              item['organizer'],
              item['addr'],
              item['price'],
              item['join']]
        self.writer.writerow(ls)
        return item

    def close_spider(self, spider):
        self.file.close()
