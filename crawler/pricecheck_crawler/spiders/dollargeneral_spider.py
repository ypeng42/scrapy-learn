from scrapy.shell import inspect_response
from pricecheck_crawler.items import *
from base_spider import BaseSpider


class DollarGeneralSpider(BaseSpider):
    name = "dollargeneral"

    start_urls = []
    allowed_domains = ["dollargeneral.com"]

    def start_requests(self):
        requests = self.make_requests('http://www.dollargeneral.com/search/index.jsp?kw=', self.parse)
        for url_request in requests:
            yield url_request

    def parse(self, response):
        #inspect_response(response, self)

        for unit in response.xpath('//section[@class="productInfo"]'):
            url = unit.xpath('.//div[@class="nameURL"]/a/@href').extract()[0]

            request = scrapy.Request(response.urljoin(url), callback=self.get_product_contents)
            request.meta['category'] = response.meta['category']
            request.meta['search_term'] = response.meta['search_term']
            yield request

        next_page = response.xpath('//li[@class="next img"]/a/@href').extract()
        if next_page:
            next_url = response.urljoin(next_page[0])
            yield scrapy.Request(next_url, callback=self.parse,
                    meta={'search_term' : response.meta['search_term'], 'category' : response.meta['category']})

    def get_product_contents(self, response):
        #inspect_response(response, self)
        url = response.url
        product = self.clean_response(response, '//h1[@class="prodTitle"]/text()')
        search_term = response.meta['search_term']
        category = response.meta['category']

        if not self.is_targeted_product(product, search_term):
            return

        img = self.clean_response(response, '//div[@id="mainImage"]/img/@src')

        retailer_id = response.url.split('?')[1].split('=')[1]
        upc = None
        sku = None

        count, volume, pack, weight = self.get_product_metrics(product)

        current_price = self.clean_response(response, '//div[@id="config"]//div[contains(@class, "prdPrice")]/strong/text()')

        current_unit_price = None
        normal_unit_price = None

        normal_price = response.xpath('//div[@id="config"]//div[contains(@class, "prdPrice")]/span/text()').extract()
        if normal_price:
            normal_price = normal_price[0].split(" ")[-1].strip(")")
        else:
            normal_price = None

        breadcrumbs = response.xpath('//section[@id="breadcrumbs"]//li[not(contains(@class, "first"))]')
        if len(breadcrumbs) > 1:
            category_str = breadcrumbs[0].xpath('.//a/text()').extract()[0].strip()
            for breadcrumb in breadcrumbs[1:]:
                if breadcrumb:
                    category_str += "->" + breadcrumb.xpath('.//a/text()').extract()[0].strip()

            breadcrumbs = category_str
        else:
            breadcrumbs = None

        subscribe = None
        promotion = self.clean_response(response, '//p[@class="promo"]/text()')

        shipping = None

        # Dollar General doesn't have product rating
        rating = None
        rating_count = None
        brand = self.get_brand(search_term)
        retailer = "Dollar General"
        page_status = response.status

        yield self.create_item(product, retailer_id, upc, sku, url, current_price, current_unit_price,
                               normal_price, normal_unit_price, img, subscribe, promotion,
                               shipping, brand, retailer, page_status, rating, rating_count, breadcrumbs,
                               search_term, category, count, volume, pack, weight)
