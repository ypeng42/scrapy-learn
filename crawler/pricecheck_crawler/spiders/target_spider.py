from pricecheck_crawler.items import *
from scrapy.shell import inspect_response
import requests
import json
from base_spider import BaseSpider

class TargetSpider(BaseSpider):

    name = "target"

    allowed_domains = ["www.target.com"]
    start_urls = []

    def start_requests(self):
        requests = self.make_requests('http://www.target.com/s?searchTerm=', self.parse)
        for url_request in requests:
            yield url_request

    def parse(self, response):
        #inspect_response(response, self)
        for sel in response.xpath('//li[@class="tile standard"]'):
            url = self.clean_response(sel, './/a[@class="productClick productTitle"]/@href')
            brand = self.clean_response(sel, './/p/a[@class="productBrand"]/text()')
            promotion = self.clean_response(sel, './/li[@class="promotion"]/@title')

            request = scrapy.Request(url, callback=self.get_product_contents)
            request.meta['brand'] = brand
            request.meta['promotion'] = promotion
            request.meta['category'] = response.meta['category']
            request.meta['search_term'] = response.meta['search_term']

            yield request

        next_page = response.xpath('//a[@title="view next page"]/@href').extract()

        if next_page:
            next_url = response.urljoin(next_page[0])
            yield scrapy.Request(next_url, callback=self.parse,
                    meta={'search_term' : response.meta['search_term'], 'category' : response.meta['category']})

    def get_product_contents(self, response):
        #inspect_response(response, self)
        url = response.url

        search_term = response.meta['search_term']
        category = response.meta['category']
        product = self.clean_response(response, '//span[@itemprop="name"]/text()')

        if not self.is_targeted_product(product, search_term):
            return

        retailer_id = self.clean_response(response, '//meta[@itemprop="productID"]/@content')
        sku = None
        upc = None

        img = self.clean_response(response, '//img[@itemprop="image"]/@src')

        count, volume, pack, weight = self.get_product_metrics(product)

        current_price = self.clean_response(response, '//div[@id="price_main"]//span[@itemprop="price"]/text()')
        current_unit_price = None

        shipping = self.clean_response(response, '//p[@class="freeShippingPromo"]/span/text()')

        promotion = response.meta['promotion']

        normal_unit_price = None
        normal_price = response.xpath('//span[@id="regPriceDisplay"]/text()').extract()
        if normal_price:
            for i in normal_price:
                if "$" in i:
                    normal_price = i.strip()
        else:
            normal_price = None

        page_status = response.status

        breadcrumbs = response.xpath('//div[@id="breadcrumbs"]/span[not(@class)]')
        if breadcrumbs[1]:
            category_str = breadcrumbs[1].xpath('.//a/text()').extract()[0].strip()
            for breadcrumb in breadcrumbs[2:]:
                if breadcrumb:
                    category_str += "->" + breadcrumb.xpath('.//a/text()').extract()[0].strip()
            breadcrumbs = category_str
        else:
            breadcrumbs = None

        subscribe = self.clean_response(response, '//span[@class="subPercent"]/text()')

        # brand = response.meta['brand']
        brand = self.get_brand(search_term)

        retailer = "Target"

        head = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36',
                'Origin': 'http://www.target.com',
                'Referer': response.url}
        rating_url = 'http://tws.target.com/productservice/services/reviews/v1/reviewstats/' + retailer_id
        jsoncontent = requests.get(rating_url, headers=head).content
        jsdict = json.loads(jsoncontent)

        if jsdict['result']:
            coreStat = jsdict['result'][retailer_id]['coreStats']
            rating = "{0:.1f}".format(coreStat['AverageOverallRating'])
            rating_count = coreStat['TotalReviewCount']
        else:
            rating = None
            rating_count = None

        yield self.create_item(product, retailer_id, upc, sku, url, current_price, current_unit_price,
                               normal_price, normal_unit_price, img, subscribe, promotion,
                               shipping, brand, retailer, page_status, rating, rating_count, breadcrumbs,
                               search_term, category, count, volume, pack, weight)
