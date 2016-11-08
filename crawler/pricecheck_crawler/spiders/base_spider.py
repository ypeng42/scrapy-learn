import re
from scrapy.shell import inspect_response
from time import strftime
from pricecheck_crawler.items import *
from pricecheck_crawler import *

class BaseSpider(scrapy.Spider):

    @staticmethod
    def make_requests(url, callback):
        requests = []
        brands_dict = lstData.get_brandlist()

        for category, brands in brands_dict.items():
            for brand in brands:

                search_term = brand

                # Is search word is only a brand like "Scotties",
                # Add category "Facial Tissues" to make it more specific
                if BaseSpider.is_brand(brand):
                    search_term = brand + " " + category

                requests.append(scrapy.Request(url + "+".join(str(s) for s in search_term.split(" ")),
                                     callback=callback,
                                     meta={'search_term' : brand, 'category' : category})
                                )
        return requests

    @staticmethod
    def is_targeted_product(product, search_term):
        if not product or not search_term:
            return False

        product = product.lower()
        brand_info = StringParser.get_brand_info(search_term)
        if brand_info.get("brand") not in product:
            return False

        if brand_info.get("meta"):
            for word in brand_info.get("meta").split(" "):
                if word not in product:
                    return False

        return True

    @staticmethod
    def get_brand(str):
        return StringParser.get_brand_info(str).get("brand")

    @staticmethod
    def is_brand(str):
        if not str:
            return False

        return StringParser.get_brand_info(str).get("meta") is None

    @staticmethod
    def get_json_info(json_obj, key):
        if key in json_obj:
            return json_obj[key]
        else:
            return None

    @staticmethod
    def clean_response(response, path):
        result = response.xpath(path).extract()
        if result and result[0].strip():
            return result[0]
        else:
            return None

    @staticmethod
    def get_product_metrics(product):
        return [StringParser.parse_count(product),
                StringParser.parse_volume(product),
                StringParser.parse_pack(product),
                StringParser.parse_weight(product)]

    @staticmethod
    def create_item(product, retailer_id, upc, sku, url, current_price, current_unit_price, normal_price, normal_unit_price,
                    img, subscribe, promotion, shipping, brand, retailer, page_status,
                    rating, rating_count, breadcrumbs, search_term, category,
                    count, volume, pack, weight):

        item = ProductInfoItem()
        item[ProductInfoItem.get_product()] = product

        item[ProductInfoItem.get_retailer_id()] = retailer_id
        item[ProductInfoItem.get_upc()] = upc
        item[ProductInfoItem.get_sku()] = sku

        item[ProductInfoItem.get_count()] = count
        item[ProductInfoItem.get_volume()] = volume
        item[ProductInfoItem.get_pack()] = pack
        item[ProductInfoItem.get_weight()] = weight

        item[ProductInfoItem.get_url()] = url
        item[ProductInfoItem.get_current_price()] = current_price
        item[ProductInfoItem.get_current_unit_price()] = current_unit_price
        item[ProductInfoItem.get_normal_price()] = normal_price
        item[ProductInfoItem.get_normal_unit_price()] = normal_unit_price
        item[ProductInfoItem.get_img_url()] = img
        item[ProductInfoItem.get_subscribe()] = subscribe
        item[ProductInfoItem.get_promotion()] = promotion
        item[ProductInfoItem.get_shipping()] = shipping
        item[ProductInfoItem.get_brand()] = brand
        item[ProductInfoItem.get_retailer()] = retailer
        item[ProductInfoItem.get_date_crawled()] = strftime("%Y/%m/%d")
        item[ProductInfoItem.get_page_status()] = page_status
        item[ProductInfoItem.get_rating()] = rating
        item[ProductInfoItem.get_rating_count()] = rating_count
        item[ProductInfoItem.get_breadcrumbs()] = breadcrumbs
        item[ProductInfoItem.get_search_term()] = search_term
        item[ProductInfoItem.get_category()] = category

        return item

