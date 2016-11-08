# -*- coding: UTF-8 -*-

import csv
import sys
import re
from time import strftime
from pricecheck_crawler.items import *
import psycopg2
import psycopg2.extras
import logging
import settings
from pricecheck_crawler.StringParser import StringParser

class WriteToDatabasePipeline(object):

    def __init__(self):
        conn = psycopg2.connect("dbname=" + settings.DB_NAME +
                                " user=" + settings.DB_USER +
                                " host=" + settings.DB_HOST +
                                " password=" + settings.DB_PASSWORD)

        self.cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        self.conn = conn

    def process_item(self, item, spider):
        product = item[ProductInfoItem.get_product()]
        retailer = item[ProductInfoItem.get_retailer()]

        query = """SELECT * FROM product_info WHERE product_name = %s AND retailer = %s"""
        self.cur.execute(query, (product, retailer))

        rows = self.cur.fetchall()
        if not rows:
            self.insert_data_info(item)
            self.insert_data_price_info(item)
        elif len(rows) == 1:
            date_crawled = strftime("%Y/%m/%d")
            query = """UPDATE product_info SET date_crawled = %s WHERE product_name = %s AND retailer = %s"""

            self.cur.execute(query, (date_crawled, product, retailer))
            self.conn.commit()

            self.insert_data_price_info(item)
            # promotion = item[ProductInfoItem.get_promotion()]
            # shipping = item[ProductInfoItem.get_shipping()]
            # if promotion != rows[0]['promotion'] or shipping != rows[0]['shipping']:
            #     self.insert_data_price_info(item)
            #     query = """UPDATE product_info SET promotion = %s, shipping = %s WHERE product_name = %s AND retailer = %s"""
            #
            #     self.cur.execute(query, (promotion, shipping, product, retailer))
            #     self.conn.commit()
        else:
            logging.error("Duplicate Occurs")

        return item

    def insert_data_price_info(self, item):
        insert = """INSERT INTO product_price_info (%s) VALUES ( %s )"""

        fields = [ProductInfoItem.get_product(),
             ProductInfoItem.get_current_price(),
             ProductInfoItem.get_promotion(),
             ProductInfoItem.get_subscribe(),
             ProductInfoItem.get_shipping(),
             ProductInfoItem.get_search_term(),
             ProductInfoItem.get_retailer(),
             ProductInfoItem.get_date_crawled(),
             ]

        self.insert_data_helper(item, fields, insert)

    def insert_data_info(self, item):
        # keys = item.fields.keys()
        # fields = u','.join(keys)
        # qm = u','.join([u'%s'] * len(keys))
        # sql = insert % (fields, qm)
        # data = (item[k] for k in keys)
        # logging.warning(sql)
        # logging.warning(' '.join([x for x in data]))

        insert = """INSERT INTO product_info (%s) VALUES ( %s )"""

        fields = [ProductInfoItem.get_product(),
             ProductInfoItem.get_retailer_id(),
             ProductInfoItem.get_sku(),
             ProductInfoItem.get_upc(),
             ProductInfoItem.get_rating(),
             ProductInfoItem.get_rating_count(),
             ProductInfoItem.get_brand(),
             ProductInfoItem.get_current_price(),
             ProductInfoItem.get_breadcrumbs(),
             ProductInfoItem.get_retailer(),
             ProductInfoItem.get_img_url(),
             ProductInfoItem.get_date_crawled(),
             ProductInfoItem.get_page_status(),
             ProductInfoItem.get_url(),
             ProductInfoItem.get_count(),
             ProductInfoItem.get_volume(),
             ProductInfoItem.get_pack(),
             ProductInfoItem.get_weight(),
             ProductInfoItem.get_search_term(),
             ProductInfoItem.get_category()]

        self.insert_data_helper(item, fields, insert)

    def insert_data_helper(self, item, fields, query):
        fieldstr = u','.join(fields)
        data = []
        for field in fields:
            if item[field] == "N/A":
                data.append(None)
            else:
                data.append(item[field])

        qm = u','.join([u'%s'] * len(fields))
        sql = query % (fieldstr, qm)

        self.cur.execute(sql, data)
        self.conn.commit()


class FieldCleanerPipeline(object):
    def process_item(self, item, spider):
        for key in item.fields.iterkeys():
            if isinstance(item[key], str) or isinstance(item[key], unicode):
                item[key] = StringParser.clean_str(item[key])
                if not item[key]:
                    item[key] = None

                if key == "current_price":
                    item[key] = StringParser.parse_price(item[key])

        return item


class CSVWriterPipeline(object):
    def __init__(self):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.file_name = "output.csv"
        self.f = open(self.file_name, "a")
        self.writer = csv.writer(self.f)
        self.writer.writerow(['Product', 'Product ID', 'Rating', 'Rating Count', 'Brand', 'Current Price',
                              'Current Unit Price', 'Normal Price', 'Normal Unit Price', 'Breadcrumbs',
                              'Retailer', 'Promotion', 'Shipping', 'Subscribe',
                              'Image URL', 'Date_Crawled', 'Page Status', 'URL'])

    def process_item(self, item, spider):
        self.f = open(self.file_name, "a")
        self.writer = csv.writer(self.f)
        self.writer.writerow([
            item[ProductInfoItem.get_product()],
            item[ProductInfoItem.get_productID()],
            item[ProductInfoItem.get_rating()],
            item[ProductInfoItem.get_rating_count()],
            item[ProductInfoItem.get_brand()],
            item[ProductInfoItem.get_current_price()],
            item[ProductInfoItem.get_current_unit_price()],
            item[ProductInfoItem.get_normal_price()],
            item[ProductInfoItem.get_normal_unit_price()],
            item[ProductInfoItem.get_breadcrumbs()],
            item[ProductInfoItem.get_retailer()],
            item[ProductInfoItem.get_promotion()],
            item[ProductInfoItem.get_shipping()],
            item[ProductInfoItem.get_subscribe()],
            item[ProductInfoItem.get_img_url()],
            item[ProductInfoItem.get_date_crawled()],
            item[ProductInfoItem.get_page_status()],
            item[ProductInfoItem.get_url()]])

        self.f.close()
        return item