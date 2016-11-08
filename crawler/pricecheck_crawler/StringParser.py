# -*- coding: UTF-8 -*-
import re

class StringParser:
    # Different ways to represent same unit
    same_unit_dict = {
        'roll': ['roll', 'large roll', 'big roll', 'giant roll',
                'huge roll', 'mega roll', 'regular roll', 'plus roll'],
        'oz': ['oz', 'ounce', 'fl oz', 'fl. oz']
    }

    @staticmethod
    def parse_price(price):
        if "Price Per Store" in price:
            return None
        if '-' in price:
            total = 0;
            for num in price.split("-"):
                total += float(num.strip())
            return str(total / 2)


    @staticmethod
    def get_brand_info(str):
        if not str:
            return None

        brand = re.search('[A-Z][a-z]*(\s[A-Z][a-z]*)*', str).group()
        meta = None
        if str != brand:
            meta = re.sub(brand, '', str).strip()

        return {'brand': brand.lower(), 'meta':meta}

    @staticmethod
    def clean_str(str):
        str = re.sub("(,|;|'|\$|®)", '', str)
        str = re.sub("\s+", ' ', str).strip()
        return str

    @staticmethod
    def parse_info(str, terms, need_unit):
        """
        Parse volume, pack, count or other info from a given product name
        :param str: ex. Easy Mac Original, 2.05 oz, 4 Count, 6 pk
        :param terms: ex. oz
        :return: ex. 2.05
        """

        if not str:
            return None

        str = StringParser.clean_str(str).lower()

        # Use standard way to represent unit
        if need_unit:
            for k, v in StringParser.same_unit_dict.iteritems():
                str = re.sub('|'.join(v), k, str)

        result = re.search('([.]*\d+[.\d]*)[\s]*(' + '|'.join(terms) + ')', str)

        if result:
            unit = re.sub('oz|ounce|fl oz|fl. oz', 'oz', result.group(2))

            return result.group(1) + (" " + unit if need_unit else "")
        else:
            return None


    @staticmethod
    def parse_count(str):
        """
        Parse count of a product name, ex. Kleenex tissue
        :param str: product name
        :return: count num
        """
        return StringParser.parse_info(str, ['count', 'ct', 'roll'] + StringParser.same_unit_dict.get('roll'), False)

    @staticmethod
    def parse_volume(str):
        """
        Parse volume of a product name, ex. coke, pepsi
        :param str: product name
        :return: count num
        """
        return StringParser.parse_info(str, ['l(?!b)', 'ml', 'gal'] +
                                       StringParser.same_unit_dict.get('oz'), True)

    @staticmethod
    def parse_pack(str):
        """
        Parse pack number of a product name, ex. coke, pepsi
        :param str: product name
        :return: pack num
        """
        if not str:
            return None

        result = re.search('(pack|packs|pk)\s*of\s*(\d+)', str)
        if result:
            return result.group(2)
        else:
            return StringParser.parse_info(str, ['pk', 'pack'], False)

    @staticmethod
    def parse_weight(str):
        """
        Parse weight info
        """
        return StringParser.parse_info(str, ['lb', 'kg', 'pound'], True)
