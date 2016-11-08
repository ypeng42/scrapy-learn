import csv
import re
import settings
import psycopg2
import psycopg2.extras
from pricecheck_crawler.spiders.base_spider import BaseSpider

conn = psycopg2.connect("dbname=" + settings.DB_NAME +
                        " user=" + settings.DB_USER +
                        " host=" + settings.DB_HOST +
                        " password=" + settings.DB_PASSWORD)

cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

with open('../brands.csv', 'rb') as csvfile:
    output = csv.reader(csvfile, delimiter = ',')

    next(output) # Skip the first row (title)

    # Loop through every category
    for row in output:
        category = row[0]

        for token in row[1:]:
            if "Private Label" not in token and token.strip():
                search_term = re.sub(r" \(key\)", '', token)
                is_brand = BaseSpider.is_brand(search_term)

                query = """INSERT INTO brandlist (%s) VALUES (%s)"""
                fields = u','.join(["search_term", "category", "is_brand"])
                values = [search_term, category, is_brand]
                qm = u','.join([u'%s'] * len(values))
                sql = query % (fields, qm)

                cur.execute(sql, values)
                conn.commit()


