import unittest
from pricecheck_crawler.StringParser import StringParser
from pricecheck_crawler.spiders.base_spider import BaseSpider

class TestStringParser(unittest.TestCase):
    def test_parse_info_one_space(self):
        name = 'Easy Mac Original, 2.05 oz, 4 Count, 6 pk'
        self.assertEqual('2.05', StringParser.parse_info(name, ['oz'], False))
        self.assertEqual('4', StringParser.parse_info(name, ['count', 'ct'], False))
        self.assertEqual('6', StringParser.parse_info(name, ['pack', 'pk'], False))

    def test_parse_info_multiple_space(self):
        name = 'Easy Mac Original, 2.05    oz, 4  CT, 6    pack'
        self.assertEqual('2.05', StringParser.parse_info(name, ['oz'], False))
        self.assertEqual('4', StringParser.parse_info(name, ['count', 'ct'], False))
        self.assertEqual('6', StringParser.parse_info(name, ['pack', 'pk'], False))

    def test_parse_info_no_space(self):
        name = 'Easy Mac Original, 2.05oz, 4Count, 6pk'
        self.assertEqual('2.05', StringParser.parse_info(name, ['oz'], False))
        self.assertEqual('4', StringParser.parse_info(name, ['count', 'ct'], False))
        self.assertEqual('6', StringParser.parse_info(name, ['pack', 'pk'], False))

    def test_parse_count(self):
        name = None
        self.assertEqual(None, StringParser.parse_count(name))

        name = 'Easy Mac Original, 2.05oz, 4Count, 6pk'
        self.assertEqual('4', StringParser.parse_count(name))

        name = 'Bounty Paper Towels with Dawn Detergent (8 large rolls)'
        self.assertEqual('8', StringParser.parse_count(name))

    def test_parse_volume(self):
        name = None
        self.assertEqual(None, StringParser.parse_volume(name))

        name = 'Easy Mac Original, 2.05oz, 4Count, 6pk'
        self.assertEqual('2.05 oz', StringParser.parse_volume(name))

        name = 'Easy Mac Original, 2.05 ounce, 4Count, 6pk'
        self.assertEqual('2.05 oz', StringParser.parse_volume(name))

        name = 'Easy Mac Original, 2.05 gallon, 4Count, 6pk'
        self.assertEqual('2.05 gal', StringParser.parse_volume(name))

        # volum less than 1
        name = 'Easy Mac Original, .05 gallon, 4Count, 6pk'
        self.assertEqual('.05 gal', StringParser.parse_volume(name))

        # lbs should not be recognized as l
        name = 'Easy Mac Original, 2.05 lbs, 3.06 l'
        self.assertEqual('3.06 l', StringParser.parse_volume(name))

        name = "Newman'S Own Organics Organic Chocolate Bars Milk Chocolate 3.25 OZ, 12CT"
        self.assertEqual('3.25 oz', StringParser.parse_volume(name))
        self.assertEqual(None, StringParser.parse_pack(name))

    def test_parse_pack(self):
        name = None
        self.assertEqual(None, StringParser.parse_pack(name))

        name = 'Easy Mac Original, 6pk'
        self.assertEqual('6', StringParser.parse_pack(name))

        name = 'Easy Mac Original, 6 packs'
        self.assertEqual('6', StringParser.parse_pack(name))

        name = 'Easy Mac Original, pack of 6'
        self.assertEqual('6', StringParser.parse_pack(name))

    def test_parse_weight(self):
        name = 'Easy Mac Original, 2.05lbs'
        self.assertEqual('2.05 lb', StringParser.parse_weight(name))

    def test_clean_str(self):
        str = "$123  ,,,,  'abc"
        self.assertEqual('123 abc', StringParser.clean_str(str))

    def test_get_brand_info(self):
        str = 'Ziploc sandwich bags'
        self.assertEqual('sandwich bags', StringParser.get_brand_info(str).get('meta'))
        self.assertEqual('ziploc', StringParser.get_brand_info(str).get('brand'))

        str = 'Ziploc'
        self.assertEqual(None, StringParser.get_brand_info(str).get('meta'))
        self.assertEqual('ziploc', StringParser.get_brand_info(str).get('brand'))

        str = 'Ziploc Zip sandwich bags'
        self.assertEqual('sandwich bags', StringParser.get_brand_info(str).get('meta'))
        self.assertEqual('ziploc zip', StringParser.get_brand_info(str).get('brand'))

    def test_is_targeted_product(self):

        search_term = "Ziploc sandwich bags"
        product = "Ziploc Sandwich Storage Bags 90 count"
        self.assertEqual(True, BaseSpider.is_targeted_product(product, search_term))

        product = "Ziploc Freezer Bags Gallon 50 count"
        self.assertEqual(False, BaseSpider.is_targeted_product(product, search_term))

        search_term = "Ziploc"
        product = "Ziploc Sandwich Bags 90 count"
        self.assertEqual(True, BaseSpider.is_targeted_product(product, search_term))

        search_term = "Ziploc"
        product = "Ziploc Sandwich Bags 90 count"
        self.assertEqual(True, BaseSpider.is_targeted_product(product, search_term))

        search_term = "Puffs plus lotion"
        product = "Ziploc Sandwich Bags 90 count"
        self.assertEqual(False, BaseSpider.is_targeted_product(product, search_term))

    def test_is_brand(self):
        search_term = "Kleenex"
        self.assertEqual(True, BaseSpider.is_brand(search_term))

        search_term = "Kleenex tissue"
        self.assertEqual(False, BaseSpider.is_brand(search_term))

    def test_parse_price(self):
        price = '10 - 20'
        self.assertEqual('15.0', StringParser.parse_price(price))

        price = 'Price Per Store'
        self.assertEqual(None, StringParser.parse_price(price))

if __name__ == '__main__':
    unittest.main()