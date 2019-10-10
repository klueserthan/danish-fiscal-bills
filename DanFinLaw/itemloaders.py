# -*- coding: utf-8 -*-
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Identity
import re

# Define Functions
def get_ministry_name(self, text):
    name = re.sub(r'§\s\d+\s', '', text[0])
    name = re.sub(r'\[.*\]', '', name)
    if name is None:
        return "ERROR -- {}".format(text[0])
    else:
        return name.strip()

def get_agency_name(self, text):
    text = text[0].replace("¦", "").split("(")[0]
    try:
        return re.search(r'([A-Za-zæåø\s-])+', text)[0].strip()
    except TypeError:
        return "ERROR -- {}".format(text[0])

def agency_to_dict(self, agency):
    return dict(agency[0])

def ministry_to_dict(self, ministry):
    return dict(ministry[0])

def get_fy(self, fy):
    try:
        return int(re.search(r'\d+', fy[0])[0])
    except TypeError:
        return None

# Define Itemloaders
class MinistryLoader(ItemLoader):
    # ministry_name
    ministry_name_in = get_ministry_name
    ministry_name_out = TakeFirst()

    # fiscal_year
    fiscal_year_in = get_fy
    fiscal_year_out = TakeFirst()

    # agencies
    agencies_in = agency_to_dict
    agencies_out = Identity()


class AgencyLoader(ItemLoader):
    default_output_processor = TakeFirst()
    default_input_processor = Identity()

    # agency_name
    agency_name_in = get_agency_name
    
    # agency_text
    agency_text_out = Join(separator='\n')


class FinYearLoader(ItemLoader):
    # fiscal_year
    fiscal_year_in = get_fy
    fiscal_year_out = TakeFirst()

    # ministries
    ministries_in = ministry_to_dict
    ministries_out = Identity()