import psycopg2

class YelpScrapyPipeline(object):

    def __init__(self):
        self.host = 'postgres'
        self.user = 'postgres'
        self.passwd = 'postgres'
        self.db = 'yelp_reviews'

    def open_spider(self, spider):
        self.conn = psycopg2.connect(host=self.host,
                                     user=self.user,
                                     password=self.passwd,
                                     dbname=self.db)

        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        query = """INSERT INTO biz (name, city, zipcode,
                                    state, link, star_raiting)
                VALUES (%s, %s, %s, %s, %s, %s)"""

        values = (item['business_name'], item['business_city'],
                  item['business_zip'], item['business_state'],
                  item['business_url'], item['business_star_rating'])

        self.cursor.execute(query, values)
        self.conn.commit()

        query = """INSERT INTO reviewers (user_url, star_raiting, location,
                                          review_text, review_date)
        VALUES (%s, %s, %s, %s, %s)"""

        values = (item['user_url'], item['review_raiting'],
                  item['reviewer_location'], item['review_text'],
                  item['review_date'])

        self.cursor.execute(query, values)

        self.conn.commit()
        return item
