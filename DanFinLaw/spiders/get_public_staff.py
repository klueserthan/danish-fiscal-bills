# -*- coding: utf-8 -*-
import scrapy
from DanFinLaw.items import FinYear, Ministry, Agency
from DanFinLaw.itemloaders import MinistryLoader, AgencyLoader #, FinYearLoader
import re
import sys


class GetPublicStaffSpider(scrapy.Spider):
    name = 'get_public_staff'
    #allowed_domains = ['http://www.oes-cs.dk/bevillingslove/']
    start_urls = ['http://www.oes-cs.dk/bevillingslove/']

    # def start_requests(self):
    #     yield scrapy.Request(url='http://www.oes-cs.dk/bevillingslove/', callback=self.parse)

    def parse(self, response):
        for finanslov_int_url in response.xpath('body/form/table//a[starts-with(text(), "Finanslov for")]/@href').getall()[1:3]:
            yield response.follow(finanslov_int_url, callback=self.parse_finanslov_int)

    def parse_finanslov_int(self, response):
        # Heading
        #finyear_loader = FinYearLoader(item=FinYear(), response=response)
        #finyear_loader.add_css('fiscal_year', 'h1::text')
        fiscal_year = response.css('h1::text').get()

        # Get link to final law plus start at first element
        request = scrapy.Request(
            url=response.urljoin(response.xpath('.//pre/a[@href]/@href').getall()[-1] + "&topic=2"),
            callback=self.parse_finanslov_section
        )

        #request.meta['finyear_loader'] = finyear_loader
        request.meta['ministry_loader'] = None
        request.meta['fiscal_year'] = fiscal_year
        yield request
  

    def parse_finanslov_section(self, response):
        section_title = response.xpath('body/h1/text()|body/h2/text()|body/h3/text()|body/h4/text()').get()
        section_title = "" if section_title is None else section_title
        # finyear_loader = response.meta['finyear_loader']
        # ministry_loader = response.meta['ministry_loader']
        fiscal_year = response.meta['fiscal_year']
        ministry_loader = response.meta['ministry_loader']
        
        # Add new ministry
        if re.match(r'§\s\d+', section_title):
            # yield existing ministry and start new one
            if "inisteriet" in section_title and ministry_loader is not None:
                # load ministry and yield
                ministry = ministry_loader.load_item()
                yield ministry

                # New ministry loader
                ministry_loader = MinistryLoader(item=Ministry(), response=response)
                ministry_loader.add_value('ministry_name', section_title)
                ministry_loader.add_value('fiscal_year', fiscal_year)

            elif "inisteriet" in section_title and ministry_loader is None:
                # New ministry loader
                ministry_loader = MinistryLoader(item=Ministry(), response=response)
                ministry_loader.add_value('ministry_name', section_title)
                ministry_loader.add_value('fiscal_year', fiscal_year)
            
            elif ministry_loader is not None:
                # yield ministry and delete loader
                ministry = ministry_loader.load_item()
                yield ministry
                ministry_loader = None


        # Add new agency
        else:
            if response.xpath('//i[contains(text(), "Personale")]').get() is not None and ministry_loader is not None:
                agency_loader = AgencyLoader(item=Agency(), response=response)
                agency_loader.add_value('agency_name', section_title)
                agency_loader.add_value('agency_url', response.url)
                agency_loader.add_xpath('agency_text', 'body/pre/text()|body/pre/i/text()|body/pre/b/text()')

                # load agency and add it to ministry
                agency = agency_loader.load_item()
                ministry_loader.add_value('agencies', agency)

        # Follow link or yield complete FY
        followlink = None
        arrowlist = response.xpath('//table[1]/tr[@align="center" and @valign="middle"]/td')
        for idx, row in enumerate(arrowlist):
            if row.xpath('img[@src="/images/right.gif"]').get() is not None:
                followlink = arrowlist[idx+1].xpath('a/@href').get()

        # # yield final fiscal year
        # if followlink is None:
        #     fy = finyear_loader.load_item()
        #     yield fy
            
        # move on to next section
        if followlink is not None:
            request = scrapy.Request(url=response.urljoin(followlink), callback=self.parse_finanslov_section)
            # request.meta['finyear_loader'] = finyear_loader
            request.meta['ministry_loader'] = ministry_loader
            request.meta['fiscal_year'] = fiscal_year
            yield request
            
