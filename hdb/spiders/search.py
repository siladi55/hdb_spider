# -*- coding: utf-8 -*-
import re
import json
import scrapy
from scrapy.http.request import Request
from hdb import settings
from urllib.parse import urlencode
from hdb.items import HdbItem


class SearchSpider(scrapy.Spider):
    name = 'search'
    allowed_domains = ['hdb.com']

    def __init__(self):
        super(SearchSpider, self).__init__()
        self.base_url = ''

    def start_requests(self):
        url = 'http://www.hdb.com/info_search'
        for kw in settings.KEYWORDS:
            values = urlencode({'word': kw, 'area_code': settings.CITY, 'page_num': 1})
            self.base_url = url + '?' + values
            yield Request(self.base_url, callback=self.parse)

    def parse(self, response):
        ulist = response.xpath('//*[contains(@class, "find_main_ul")]//li//*[contains(@class, "find_main_div")]')
        for div in ulist:
            item = HdbItem()
            url = div.xpath('.//h3//a/@href').extract()[0].strip()
            item['url'] = url
            finished = div.xpath('string(.//*[contains(@class,"find_main_time")])').extract()[0].strip()
            print(type(finished), finished)
            if '已结束' != finished:
                print('OK!=OK')
                yield Request(url, meta={'item': item}, callback=self.parse_detail)

        for i in range(2, 11):
            print(self.base_url[:-1]+str(i))
            yield Request(self.base_url[:-1]+str(i), callback=self.parse)

    def parse_detail(self, response):
        item = response.meta['item']
        item['subject'] = response.xpath('string(//h1[@id="dt_title"])').extract()[0].strip()
        item['addr'] = response.xpath('string(//*[contains(@class,"detail_attr_blue")])').extract()[0].strip()
        shopid = re.search('/(\w{4,7}).html', item['url']).group(1)
        url = 'http://api.hdb.com/ajax/api:4009?queryType=0&infoId36={}&infoType=party'.format(shopid)
        yield Request(url, meta={'shopid': shopid, 'item':item}, callback=self.parse_ajax0)

    def parse_ajax0(self, response):
        shopid, item = response.meta['shopid'], response.meta['item']
        res = json.loads(response.text, encoding='utf-8')
        item['organizer'] = res['result']['shopName']
        url = 'http://api.hdb.com/ajax/api:110?infoId36={}&type=1'.format(shopid)
        yield Request(url, meta={'shopid': shopid, 'item': item}, callback=self.parse_ajax1)

    def parse_ajax1(self, response):
        shopid, item = response.meta['shopid'], response.meta['item']
        res = json.loads(response.text, encoding='utf-8')
        frequencyId = res['result']['frequencyList'][0]['frequencyId']
        item['hostime'] = res['result']['dateStr']
        url = 'http://api.hdb.com/ajax/api:100?infoId36={}&infoType=party&frequencyId={}'.format(shopid, frequencyId)
        yield Request(url, meta={'shopid': shopid, 'item': item}, callback=self.parse_ajax2)

    def parse_ajax2(self, response):
        shopid, item = [response.meta[x] for x in ('shopid', 'item')]
        res =  json.loads(response.text, encoding='utf-8')
        price_box = []
        for payitem in res['result']['payItemList']:
            price = float(payitem['price']) if '.' in payitem['price'] else int(payitem['price'])
            price_box.append(price)
        if len(price_box):
            mi, ma = min(price_box), max(price_box)
            item['price'] = mi if mi == ma else str(mi) + ' ~ ' + str(ma)
        else:
            item['price'] = '0.00'
        url = 'http://api.hdb.com/ajax/api:51?info_type=party&info_id={}'.format(shopid)
        yield Request(url, meta={'item': item}, callback=self.parse_ajax3)

    def parse_ajax3(self, response):
        item = response.meta['item']
        res = json.loads(response.text, encoding='utf-8')
        item['join'] = res['result']['join']
        yield item

