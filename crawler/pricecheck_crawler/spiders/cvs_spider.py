import scrapy
from scrapy.shell import inspect_response
import re
from time import strftime
from pricecheck_crawler.items import *
from pricecheck_crawler.lstData import *
from base_spider import BaseSpider
import json
import requests
from pricecheck_crawler.StringParser import StringParser


class CvsSpider(BaseSpider):
    name = "cvs"
    brands_dict = lstData.get_brandlist()

    start_urls = ["http://www.cvs.com"]
    allowed_domains = ["www.cvs.com"]

    def parse(self, response):

        # CVS uses a api to get product page info, do a GET request to get this info
        # Hack the value of apiKey and apiSecret, trying to find a more stable way to
        # do it

        brands_dict = lstData.get_brandlist()
        item_per_page = 20
        url = 'https://www.cvs.com/retail/frontstore/OnlineShopService'

        for category, brands in brands_dict.items():
            for brand in brands:
                search_term = brand

                # Is search word is only a brand like "Scotties",
                # Add category "Facial Tissues" to make it more specific
                if self.is_brand(brand):
                    search_term = brand + " " + category

                page = 1
                total_page = 1
                while page <= total_page:
                    payload = { "apiKey": "c9c4a7d0-0a3c-4e88-ae30-ab24d2064e43",
                                "apiSecret": "4bcd4484-c9f5-4479-a5ac-9e8e2c8ad4b0",
                                "appName": "CVS_WEB",
                                "channelName": "WEB",
                                "contentZone": "resultListZone",

                                "deviceToken": "7780",
                                'deviceType':'DESKTOP',
                                'lineOfBusiness':'RETAIL',
                                'navNum': item_per_page,
                                'pageNum': page,
                                'operationName':'getProductResultList',
                                'referer': 'http://www.cvs.com/search/N-0?pt=product&searchTerm=' + "+".join(str(s) for s in search_term.split(" ")),

                                'serviceCORS':'False',
                                'serviceName': 'OnlineShopService',
                                'sortBy': 'relevance',
                                'version': '1.0'
                               }
                    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
                            'Origin': 'http://www.cvs.com',
                            'Referer': 'http://www.cvs.com/search/N-0?pt=product&searchTerm=' + "+".join(str(s) for s in search_term.split(" "))
                            }

                    page += 1
                    jsoncontent = requests.get(url, params=payload, headers=head).content
                    jsdict = json.loads(jsoncontent)

                    if 'response' not in jsdict:
                        continue

                    jsresponse = jsdict['response']

                    if 'details' not in jsresponse:
                        continue

                    if 'pages' not in jsresponse['details']:
                        continue

                    total_page = jsresponse['details']['pages']

                    if 'skuGroupList' not in jsresponse:
                        continue

                    # Get the url and sku, other info can be get from subsequent call
                    # Not all info is included in this call
                    for item_group in jsresponse['skuGroupList']:
                        for item in item_group['skuGroupDetails']['skuDetails']:
                            if 'detailsLink' in item:
                                product_url = "https://www.cvs.com" + item['detailsLink']

                                product_name = item['displayName']
                                if not self.is_targeted_product(product_name, brand):
                                    continue

                                next_request = scrapy.Request(product_url, self.get_product_contents)
                                next_request.meta['category'] = category
                                next_request.meta['search_term'] = brand
                                next_request.meta['skuId'] = self.get_json_info(item, 'skuId')

                                yield next_request


    def get_product_contents(self, response):
        # inspect_response(response, self)

        skuId = response.meta['skuId']
        url = 'https://www.cvs.com/retail/frontstore/productDetails'
        payload = { "apiKey": "c9c4a7d0-0a3c-4e88-ae30-ab24d2064e43",
                    "apiSecret": "4bcd4484-c9f5-4479-a5ac-9e8e2c8ad4b0",
                    "appName": "CVS_WEB",
                    "channelName": "WEB",
                    "code": skuId,
                    "codeType": "sku",
                    "deviceToken": "2695",
                    'deviceType':'DESKTOP',
                    'lineOfBusiness':'RETAIL',
                    'operationName':'getSkuDetails',
                    'serviceCORS':'True',
                    'serviceName': 'productDetails',
                    'version': '1.0'
                    }
        head = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36',
                'Origin': 'http://www.cvs.com',
                }

        jsoncontent = requests.get(url, params=payload, headers=head).content
        jsdict = json.loads(jsoncontent)

        info = jsdict['response'][u'getSkuDetails'][0]['skuDetails'][0]
        breadcrumb = info['breadCrumb']
        details = info['detail']

        product = self.get_json_info(details, 'displayName')
        category = response.meta['category']
        search_term = response.meta['search_term']

        # brand = self.get_json_info(details, 'brandName')
        brand = self.get_brand(search_term)

        img = "www.cvs.com" + details['brandImageUrl']
        rating = self.get_json_info(details, 'productRating')
        rating_count = self.get_json_info(details, 'productReviewCount')

        count, volume, pack, weight = self.get_product_metrics(product)

        weight = self.get_json_info(details, 'weight')

        breadcrumb_str = breadcrumb[0]['label']
        for bread in breadcrumb[1:]:
            breadcrumb_str = breadcrumb_str + "->" + bread['label']

        page_status = response.status
        retailer = "CVS"

        ################################ Get Promotion Info ########################################
        payload['operationName'] = 'getSkuPricePromotions'
        jsoncontent = requests.get(url, params=payload, headers=head).content
        jsdict = json.loads(jsoncontent)

        details = jsdict[u'response'][u'getSkuPricePromotions'][0][u'skuDetails'][0]
        priceInfo = details[u'priceInfo']

        normal_unit_price = self.get_json_info(priceInfo, 'uomListPrice')
        normal_price = self.get_json_info(priceInfo, 'listPrice')

        if priceInfo['salePrice']:
            current_unit_price = priceInfo['uomSalePrice']
            current_price = priceInfo['salePrice']
        else:
            current_price = normal_price
            current_unit_price = normal_unit_price

        if not normal_unit_price:
            normal_unit_price = None
            current_unit_price = None

        retailer_id = None
        upc = None
        subscribe = None
        shipping = None

        spin_price = details[u'spinPricing']
        promotion = spin_price[u'promoType']
        if promotion == "noPromo":
            promotion = None
        elif promotion == "xForAmount":
            promotion = "Price Discount"
        elif promotion == "bogoPercentOff":
            promotion = "Buy " + spin_price['buyAmount'] + " Get " \
                        + spin_price['getAmount'] + " " + spin_price['savePercent'] + " Off"
        elif promotion == "bogoFree":
            promotion = "Buy " + spin_price['buyAmount'] + " Get " \
                        + spin_price['getAmount'] + " Free"

        yield self.create_item(product, retailer_id, upc, skuId, response.url, current_price, current_unit_price,
                               normal_price, normal_unit_price, img, subscribe, promotion,
                               shipping, brand, retailer, page_status, rating, rating_count, breadcrumb_str,
                               search_term, category, count, volume, pack, weight)
