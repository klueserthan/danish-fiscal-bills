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
            found_staff_section = False
            found_staff_years = False

            re_section = re.compile(r'\d+\.\s+Person')
            re_years = re.compile(r'\d{4}')
            lines = text.splitlines()

            for idx, line in enumerate(lines):
                # Get data
                if found_staff_section:
                    if line.strip().startswith("I alt"):
                        staff_numbers = re.findall(r'\d+', lines[idx+1])
                        break
                
                # Get years
                elif found_staff_section and found_staff_years is False:
                    if re_years.match(line.strip()):
                        staff_years = re.findall(r'\d{4}', line)
                        found_staff_years = True

                else:
                    if re_section.search(line):
                        found_staff_section = True

            # Merge years and staff numbers
            try:
                if len(staff_years) == len(staff_numbers):
                    staff_dict = [
                                {'fiscal_year': int(fy), 'staff_number': int(sn)}
                                for fy, sn in zip(staff_years, staff_numbers)
                            ]

                    for item in staff_dict:
                        if item['fiscal_year'] == fy:
                            return item['staff_number']

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
            raise DropItem(e)
