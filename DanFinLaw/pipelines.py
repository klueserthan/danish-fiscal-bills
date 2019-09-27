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
        def get_number_first(text):
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
 

        def get_number_second(text, fy):
            # Condition_id
            process_id = 1

            for line in text.splitlines():
                # Get section
                if process_id == 1:
                    if line.strip().startswith("Personaleoplysni"):
                        process_id += 1

                # Get years
                elif process_id == 2:
                    if re.search(r'\d{4}', line):
                        staff_years = re.findall(r'\d{4}', line)
                        process_id += 1

                # Get staff
                elif process_id == 3:
                    if re.search(r'I alt \.+', line):
                        staff_numbers = re.findall(r'\d+', line.replace(".", ""))
                        break

            # Output correct number
            try:
                if len(staff_years) == len(staff_numbers):
                    return int(staff_numbers[staff_years.index(str(fy))])
                else:
                    return -999

            except Exception:
                return -999

        try:
            for agency in item['agencies']:
                agency_staff = get_number_first(agency['agency_text'])
                if agency_staff == -999:
                    agency['agency_staff'] = get_number_second(agency['agency_text'], item.get('fiscal_year'))
                else:
                    agency['agency_staff'] = agency_staff
                
                del agency['agency_text']
            return item                 
        
        except Exception as e:
            for agency in item['agencies']:
                del agency['agency_text']
            raise DropItem(e)
