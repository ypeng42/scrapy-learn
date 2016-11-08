from pricecheck_crawler.spiders.target_spider import TargetSpider
from pricecheck_crawler.spiders.dollargeneral_spider import DollarGeneralSpider
from pricecheck_crawler.spiders.cvs_spider import CvsSpider
from pricecheck_crawler.spiders.samsclub_spider import SamsClubSpider
from pricecheck_crawler.spiders.walgreens_spider import WalgreensSpider
from pricecheck_crawler.spiders.walmart_spider import WalmartSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())
process.crawl(CvsSpider)
process.crawl(TargetSpider)
process.crawl(DollarGeneralSpider)
process.crawl(SamsClubSpider)
process.crawl(WalgreensSpider)
process.crawl(WalmartSpider)
process.start()