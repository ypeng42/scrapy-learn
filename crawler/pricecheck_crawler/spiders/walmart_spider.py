from scrapy.shell import inspect_response
import logging
from pricecheck_crawler.items import *
from pricecheck_crawler.lstData import *
from base_spider import BaseSpider


class WalmartSpider(BaseSpider):
    name = "walmart"

    allowed_domains = ["www.walmart.com"]
    start_urls = []

    def start_requests(self):
        requests = self.make_requests('http://www.walmart.com/search/?query=', self.parse)
        for url_request in requests:
            yield url_request

    def parse(self, response):
        # inspect_response(response, self)
        for url in response.xpath('//a[@class="js-product-title"]'):
            url = response.urljoin(url.xpath('@href').extract()[0])

            request = scrapy.Request(url, callback=self.get_product_contents)
            request.meta['category'] = response.meta['category']
            request.meta['search_term'] = response.meta['search_term']

            yield request

        next_page = response.xpath('//a[@class="paginator-btn paginator-btn-next"]/@href').extract()

        if next_page:
            next_url = response.urljoin(next_page[0])
            page_num = re.search(r'page=\d', next_url, re.M|re.I)

            if page_num:
                page_num = int(page_num.group().split("=")[1])

                if page_num < 3:
                    yield scrapy.Request(next_url, callback=self.parse,
                        meta={'search_term' : response.meta['search_term'], 'category' : response.meta['category']})

    def get_product_contents(self, response):
        #inspect_response(response, self)

        search_term = response.meta['search_term']
        category = response.meta['category']
        product = self.clean_response(response, '//h1[@itemprop="name"]/span/text()')
        if not self.is_targeted_product(product, search_term):
            return

        retailer_id = self.clean_response(response, '//meta[@itemprop="productID"]/@content')
        upc = self.clean_response(response, '//meta[@property="og:upc"]/@content')
        sku = None

        url = response.url
        img = self.clean_response(response, '//img[@itemprop="image"]/@src')

        count, volume, pack, weight = self.get_product_metrics(product)

        current_price = self.clean_response(response, 'string(.//div[@itemprop="price"])')
        current_unit_price = self.clean_response(response, 'string(.//div[@class="price-info"])')

        shipping = response.xpath('string(//div[contains(@class, "price-fulfillment")])').extract()
        if shipping[0].strip():
            shipping = ' '.join(shipping[0].split())
        else:
            shipping = None

        normal_unit_price = None
        normal_price = response.xpath('string(//div[@class="price-comparison"])').extract()

        if normal_price[0].strip():
            normal_price = normal_price[0].split("Save")[0].split(" ")
            normal_price = ''.join([x for x in normal_price if '$' in x])
        else:
            normal_price = None

        page_status = response.status

        breadcrumbs = response.xpath('//ol[contains(@class, "breadcrumb-list-mini")]/nav/li')
        if breadcrumbs:
            breadcrumb_str = breadcrumbs[0].xpath('string()').extract()[0]
            for breadcrumb in breadcrumbs[1:]:
                breadcrumb_str += "->" + breadcrumb.xpath('string()').extract()[0].strip()
        else:
            breadcrumb_str = None

        promotion = None
        subscribe = None

        rating_count = response.xpath('//span[@itemprop="ratingCount"]/text()').extract()
        if rating_count:
            rating = response.xpath('string(//span[@itemprop="ratingValue"])').extract()[0].split(" ")[0]
            rating_count = rating_count[0]
        else:
            rating = None
            rating_count = None

        # brand = self.clean_response(response, '//span[@itemprop="brand"]/text()')
        brand = self.get_brand(search_term)

        retailer = "Walmart"

        yield self.create_item(product, retailer_id, upc, sku, url, current_price, current_unit_price,
                               normal_price, normal_unit_price, img, subscribe, promotion,
                               shipping, brand, retailer, page_status, rating, rating_count, breadcrumb_str,
                               search_term, category, count, volume, pack, weight)
