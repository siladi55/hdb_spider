# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HdbItem(scrapy.Item):
    # define the fields for your item here like:
    hostime = scrapy.Field()
    subject = scrapy.Field()
    url = scrapy.Field()
    organizer = scrapy.Field()
    addr = scrapy.Field()
    price = scrapy.Field()
    join = scrapy.Field()
