# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FinYear(scrapy.Item):
    # define the fields for your item here like:
    fiscal_year = scrapy.Field()
    ministries = scrapy.Field()

class Ministry(scrapy.Item):
    ministry_name = scrapy.Field()
    agencies = scrapy.Field()

class Agency(scrapy.Item):
    agency_name = scrapy.Field()
    agency_url = scrapy.Field()
    agency_text = scrapy.Field()
