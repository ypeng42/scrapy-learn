import re
from time import strftime
from pricecheck_crawler.items import *
from scrapy.shell import inspect_response
from pricecheck_crawler.lstData import *
import requests
import json
from base_spider import BaseSpider


class WalmartCategorySpider(BaseSpider):
    name = "walmart_cat"
    allowed_domains = ["www.walmart.com"]
    start_urls = ["http://www.walmart.com/All-Departments"]

    def parse(self, response):
        paths = response.xpath('//div[contains(@class, "all-depts-links-container")]//a[@class="all-depts-links-dept font-semibold"]')

        for path in paths:
            category_name = path.xpath("text()").extract()[0]
            url = response.urljoin(path.xpath('@href').extract()[0])

            request = scrapy.Request(url, callback=self.get_secondary_category)
            request.meta['category'] = category_name
            yield request

    def get_secondary_category(self, response):
        #inspect_response(response, self)
        parent = ""
        if "category" in response.meta:
            parent = response.meta['category']
        elif "new_category" in response.meta:
            parent = response.meta['new_category']

        paths = response.xpath('//div[contains(@class, "shop-by-category")]//li/a[contains(@class, "lhn-menu-toggle")]')
        if paths:
            for path in paths:
                category = path.xpath('.//span/text()').extract()[0]
                url = response.urljoin(path.xpath('@href').extract()[0])
                new_category = parent + "->" + category

                request = scrapy.Request(url, callback=self.get_secondary_category)
                request.meta["new_category"] = new_category
                yield request

        paths = response.xpath('//div[@class="expander expanded departments"]//li/a')
        if paths:
            for path in paths:
                category = path.xpath('text()').extract()[0]
                url = response.urljoin(path.xpath('@href').extract()[0])
                new_category = parent + "->" + category

                request = scrapy.Request(url, callback=self.get_secondary_category)
                request.meta["new_category"] = new_category
                yield request

        if "Pickup & delivery" in response.body:
            item = CategoryItem()
            item["category"] = parent
            yield item