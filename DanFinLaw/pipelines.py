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
        def get_number_second(text, fy):
            # Condition_id
            process_id = 1

            for line in text.splitlines():
                # Get section
                if process_id == 1:
                    if re.search(r'Personaleoplysni|\.\sPerson', line.strip()):
                        process_id += 1

                # Get years
                elif process_id == 2:
                    if re.search(r'\d{4}', line):
                        staff_years = re.findall(r'\d{4}', line)
                        process_id += 1

                # Get staff
                elif process_id == 3:
                    #if re.search(r'I alt \.+', line):
                    line = line.replace(".", "").strip()
                    if re.search(r'\s\d+\s', line):
                        staff_numbers = re.findall(r'(?<=\s)\d+|-', line.replace(".", "").strip())
                        break

            # Output correct number
            try:
                if len(staff_years) == len(staff_numbers):
                    return int(staff_numbers[staff_years.index(str(fy))])
                else:
                    return -999

            except Exception:
                return -999


        def get_number_2008(text, fy=2008):
            # Condition_id
            process_id = 1

            for line in text.splitlines():
                # Get section
                if process_id == 1:
                    if re.search(r'Personaleoplysni|\.\sPerson', line.strip()):
                        process_id += 1

                # Get years
                elif process_id == 2:
                    if str(fy) in line:
                        process_id += 1

                # Get staff
                elif process_id == 3:
                    line = line.replace(".", "").strip()
                    if re.match(r'(?<!.)\d+(?!.)', line):
                        try:
                            return int(line)
                        except ValueError:
                            return -999
        
        try:
            for agency in item['agencies']:
                if item.get('fiscal_year') < 2008:
                    agency['agency_staff'] = get_number_second(
                        agency['agency_text'],
                        item.get('fiscal_year')
                    )
                else:
                    agency["agency_staff"] = get_number_2008(agency["agency_text"])
                
                del agency['agency_text']
            return item                 
        
        except Exception as e:
            for agency in item['agencies']:
                del agency['agency_text']
            raise DropItem(e)
