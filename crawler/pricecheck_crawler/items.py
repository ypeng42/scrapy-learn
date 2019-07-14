# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class CategoryItem(scrapy.Item):
    category = scrapy.Field()

class ProductInfoItem(scrapy.Item):
    # define the fields for your item here like:

    product_name = scrapy.Field()
    sku = scrapy.Field()
    upc = scrapy.Field()
    retailer_id = scrapy.Field()
    url = scrapy.Field()
    current_price = scrapy.Field()
    current_unit_price = scrapy.Field()
    normal_price = scrapy.Field()
    normal_unit_price = scrapy.Field()
    image_url = scrapy.Field()
    subscribe = scrapy.Field()
    promotion = scrapy.Field()
    shipping = scrapy.Field()
    brand = scrapy.Field()
    retailer = scrapy.Field()
    date_crawled = scrapy.Field()
    page_status = scrapy.Field()
    rating = scrapy.Field()
    rating_count = scrapy.Field()
    category = scrapy.Field()
    search_term = scrapy.Field()
    breadcrumbs = scrapy.Field()
    count_no = scrapy.Field()
    volume_no = scrapy.Field()
    pack_no = scrapy.Field()
    weight = scrapy.Field()

    @staticmethod
    def get_shipping():
        return "shipping"

    @staticmethod
    def get_promotion():
        return "promotion"

    @staticmethod
    def get_product():
        return "product_name"

    @staticmethod
    def get_retailer_id():
        return "retailer_id"

    @staticmethod
    def get_upc():
        return "upc"

    @staticmethod
    def get_sku():
        return "sku"

    @staticmethod
    def get_url():
        return "url"

    @staticmethod
    def get_current_price():
        return "current_price"

    @staticmethod
    def get_current_unit_price():
        return "current_unit_price"

    @staticmethod
    def get_normal_price():
        return "normal_price"

    @staticmethod
    def get_normal_unit_price():
        return "normal_unit_price"

    @staticmethod
    def get_img_url():
        return "image_url"

    @staticmethod
    def get_subscribe():
        return "subscribe"

    @staticmethod
    def get_brand():
        return "brand"

    @staticmethod
    def get_retailer():
        return "retailer"

    @staticmethod
    def get_date_crawled():
        return "date_crawled"

    @staticmethod
    def get_breadcrumbs():
        return "breadcrumbs"

    @staticmethod
    def get_category():
        return "category"

    @staticmethod
    def get_search_term():
        return "search_term"

    @staticmethod
    def get_rating():
        return "rating"

    @staticmethod
    def get_rating_count():
        return "rating_count"

    @staticmethod
    def get_page_status():
        return "page_status"

    @staticmethod
    def get_volume():
        return "volume_no"

    @staticmethod
    def get_count():
        return "count_no"

    @staticmethod
    def get_pack():
        return "pack_no"

    @staticmethod
    def get_weight():
        return "weight"