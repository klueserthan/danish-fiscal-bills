# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
from scrapy.exceptions import DropItem

class DanfinlawPipeline(object):
    def process_item(self, item, spider):
        return item

class StaffPipeline(object):
    def process_item(self, item, spider):
        def get_number(text):
            found_staff_section = False

            re_section = re.compile(r'\d+\.\s+Person')

            for line in text.splitlines():
                if found_staff_section:
                    if "Personale i alt" in line:
                        detailsline = line
                else:
                    if re_section.search(line):
                        found_staff_section = True

            try:
                # split line on many spaces, information is element - 4
                staffnumber = re.split(r'\s{2,}', detailsline)[-4]
                return int(staffnumber)

            except NameError:
                return -999
            except IndexError:
                return -999
        
        try:
            for agency in item['agencies']:
                agency['agency_staff'] = get_number(agency['agency_text'])
            return item                 
        except Exception as e:
            raise DropItem(e)
