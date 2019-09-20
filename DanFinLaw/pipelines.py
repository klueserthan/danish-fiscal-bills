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
            lines = text.splitlines()
            for idx, line in enumerate(lines):
                if found_staff_section:
                    if "Personale i alt" in line:
                        staffnumber = lines[idx+1]
                else:
                    if re_section.search(line):
                        found_staff_section = True

            try:
                return int(staffnumber)

            except:
                return -999
        
        try:
            for agency in item['agencies']:
                agency['agency_staff'] = get_number(agency['agency_text'])
                del agency['agency_text']
            return item                 
        except Exception as e:
            raise DropItem(e)
