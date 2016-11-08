from scrapy.shell import inspect_response
import re
from pricecheck_crawler.items import *
from base_spider import BaseSpider

class SamsClubSpider(BaseSpider):
    name = "samsclub"

    start_urls = []
    allowed_domains = ["www.samsclub.com"]

    def start_requests(self):
        requests = self.make_requests('http://www.samsclub.com/sams/search/searchResults.jsp?searchTerm=', self.parse)
        for url_request in requests:
            yield url_request

    # Sam's Club's web page loads page dynamically as users scroll, to ease the crawling process, get all pages
    # from loader at once
    def parse(self, response):
        #inspect_response(response, self)
        item_count = response.xpath('//span[@class="gray6 fB"]/span/text()').extract()
        if item_count:
            item_count = item_count[0]
        else:
            item_count = 100

        key_term = response.url.split("?")[1].split("=")[1]

        loader_url = 'http://www.samsclub.com/sams/shop/common/ajaxSearchPageLazyLoad.jsp?' \
                     'sortKey=relevance&searchCategoryId=all&searchTerm={0}' \
                     '&noOfRecordsPerPage={1}' \
                     '&sortOrder=0&offset=1'.format(*(key_term, item_count))

        request = scrapy.Request(loader_url, callback=self.parse_loader)
        request.meta['category'] = response.meta['category']
        request.meta['search_term'] = response.meta['search_term']
        yield request

    def parse_loader(self, response):
        # inspect_response(response, self)

        for unit in response.xpath('//li[@class="item"]'):
            url = unit.xpath('.//a[@class="shelfProdImgHolder"]/@href').extract()
            url = response.urljoin(url[0])

            request = scrapy.Request(response.urljoin(url), callback=self.get_product_contents)
            request.meta['category'] = response.meta['category']
            request.meta['search_term'] = response.meta['search_term']
            yield request

    def get_product_contents(self, response):
        search_term = response.meta['search_term']
        category = response.meta['category']
        product = self.clean_response(response, '//span[@itemprop="name"]/text()')

        if not self.is_targeted_product(product, search_term):
            return

        rating = response.xpath('.//div[contains(@class, "bvSamsStars")]/@data-rating1').extract()
        if rating:
            rating_count = response.xpath('//span[@class="numOfReviews"]/text()').extract()
            rating_count = re.sub('[()]', '', rating_count[0])
            rating = rating[0]
        else:
            rating_count = None
            rating = None

        url = response.url
        img = self.clean_response(response, '//img[@itemprop="image"]/@src')

        retailer_id = None
        upc = None
        sku = self.clean_response(response, '//span[@itemprop="productID"]/text()')

        count, volume, pack, weight = self.get_product_metrics(product)

        # brand = self.clean_response(response, '//span[@itemprop="brand"]/span/text()')
        brand = self.get_brand(search_term)

        current_price = response.xpath('//span[@itemprop="price"]/text()').extract()
        if current_price:
            current_price = "$" + current_price[0]
        else:
            current_price = None

        current_unit_price = None
        normal_price = None
        normal_unit_price = None

        if response.xpath('//ul[@class="mapPrice"]/li/text()').extract():
            unit_price_string = response.xpath('//ul[@class="mapPrice"]/li/text()').extract()[0].strip()
            current_unit_price = re.sub('\xa0', ' ', unit_price_string)

        breadcrumbs = response.xpath('//div[@id="breadcrumb"]/span[not(@class="breadcrumbArrowImg")]')

        # check whether there is useful breadcrumb
        if len(breadcrumbs) > 2:
            category_str = breadcrumbs[1].xpath('./a/text()').extract()[0]
            for breadcrumb in breadcrumbs[2: -1]:
                if breadcrumb:
                    category_str += "->" + breadcrumb.xpath('./a/text()').extract()[0]
            breadcrumbs = category_str
        else:
            breadcrumbs = None

        subscribe = response.xpath('//div[@class="subscriptionDiv"]').extract()
        if subscribe:
            subscribe = "Subscribe Avaliable"
        else:
            subscribe = None

        retailer = "Sams Club"
        page_status = response.status
        promotion = None
        shipping = self.clean_response(response, '//div[@class="freeDelvryTxt"]/text()')

        yield self.create_item(product, retailer_id, upc, sku, url, current_price, current_unit_price,
                               normal_price, normal_unit_price, img, subscribe, promotion,
                               shipping, brand, retailer, page_status, rating, rating_count, breadcrumbs,
                               search_term, category, count, volume, pack, weight)
