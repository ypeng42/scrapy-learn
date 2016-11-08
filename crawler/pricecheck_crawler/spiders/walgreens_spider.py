from scrapy.shell import inspect_response
import re
from time import strftime
from pricecheck_crawler.items import *
from pricecheck_crawler.lstData import *
from base_spider import BaseSpider
import requests
import json


class WalgreensSpider(BaseSpider):
    name = "walgreens"
    start_urls = ["http://www.walgreens.com"]
    allowed_domains = ["www.walgreens.com"]

    def parse(self, response):
        # walgreen uses a js script to load web page, send a POST request to get info instead of crawling
        brands_dict = lstData.get_brandlist()
        page_size = 60

        for category, brands in brands_dict.items():
            for brand in brands:
                search_term = brand

                # Is search word is only a brand like "Scotties",
                # Add category "Facial Tissues" to make it more specific
                if self.is_brand(brand):
                    search_term = brand + " " + category

                page = 0
                total_item_count = 100
                while page * page_size < total_item_count:
                    page += 1
                    url = 'http://www.walgreens.com/svc/products/search'
                    payload = {"p": str(page),  # page number
                            "s": str(page_size),  # page size
                            "sort": "relevance",
                            "view": "allView",
                            "geoTargetEnabled":'false',
                            "q": search_term,  # search query
                            "requestType": "search",
                            "deviceType": "desktop"}
                    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                            '(KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36',
                            'Origin': 'http://www.walgreens.com',
                            }

                    jsoncontent = requests.post(url, params=payload, headers=head).content

                    jsdict = json.loads(jsoncontent)

                    total_item_count = int(jsdict['summary']['productInfoCount'])

                    if 'products' in jsdict:
                        for info in jsdict['products']:
                            url = 'http://www.walgreens.com' + info['productInfo']['productURL']

                            product_name = info['productInfo']['productDisplayName']
                            if not self.is_targeted_product(product_name, brand):
                                continue

                            next_request = scrapy.Request(url, self.get_product_contents)
                            next_request.meta['json'] = info
                            next_request.meta['category'] = category
                            next_request.meta['search_term'] = brand

                            yield next_request

    def get_product_contents(self, response):
        #inspect_response(response, self)
        product = response.meta['json']['productInfo']
        category = response.meta['category']
        search_term = response.meta['search_term']

        img = product['imageUrl']
        url = response.url

        if 'messages' in product['priceInfo']:
            current_price = product['priceInfo']['messages']['message']
            normal_price = None
        else:
            if 'salePrice' in product['priceInfo']:
                normal_price = product['priceInfo']['regularPrice']
                current_price = product['priceInfo']['salePrice']
            else:
                current_price = product['priceInfo']['regularPrice']
                normal_price = None

        promotion = None
        if 'ruleMessage' in product['priceInfo']:
            promotion = product['priceInfo']['ruleMessage']['prefix']

        current_unit_price = None
        normal_unit_price = None
        if 'unitPrice' in product['priceInfo']:
            current_unit_price = product['priceInfo']['unitPrice'] + ' / ' + product['priceInfo']['unitPriceSize']

        retailer_id = self.get_json_info(product, 'prodId')
        if retailer_id:
            retailer_id = re.sub("prod", "", retailer_id)

        sku = self.get_json_info(product, 'skuId')
        if sku:
            sku = re.sub("sku", "", sku)

        upc = self.get_json_info(product, 'upc')

        product_name = product['productDisplayName']
        count, volume, pack, weight = self.get_product_metrics(product_name)

        # brand = None
        brand = self.get_brand(search_term)
        rating = None
        rating_count = None

        if 'reviewCount' in product:
            rating_count = product['reviewCount']
            rating = product['reviewHoverMessage'].split(" ")[0]

        breadcrumbs = response.xpath('//ul[contains(@class, "breadcrumb")]/li')
        if breadcrumbs:
            category_str = breadcrumbs[2].xpath('.//a/text()').extract()[0].strip()

            for breadcrumb in breadcrumbs[3:]:
                if breadcrumb:
                    category_str += "->" + breadcrumb.xpath('.//a/text()').extract()[0].strip()

            breadcrumbs = category_str
        else:
            breadcrumbs = None

        retailer = "Walgreens"
        page_status = response.status
        subscribe = None
        shipping = None

        yield self.create_item(product_name, retailer_id, upc, sku, url, current_price, current_unit_price,
                               normal_price, normal_unit_price, img, subscribe, promotion,
                               shipping, brand, retailer, page_status, rating, rating_count, breadcrumbs,
                               search_term, category, count, volume, pack, weight)
