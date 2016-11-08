import csv
import re
import settings

class lstData:

    @staticmethod
    def get_brandlist():
        # brand = {
        #     # 'paper towel': [u'Bounty', u'Brawny', u'Sparkle'],
        #     # 'diaper': [u'Huggies', u'Pampers', u'Luvs']
        #     'Facial Tissues': [u'Scotties']
        # }

        brand = {}
        with open('./brands.csv', 'rb') as csvfile:
            output = csv.reader(csvfile, delimiter = ',')

            next(output) # Skip the first row (title)

            for row in output:
                category = row[0]
                brandlist = []

                for token in row[1:]:
                    if "Private Label" not in token and token.strip():
                        brandlist.append(re.sub(r" \(key\)", '', token))
                brand[category] = brandlist

        return brand