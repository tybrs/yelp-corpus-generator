from yelp_scrapy.items import UserItem, BizItem
from .db_utils import PgsqlHandler


class YelpScrapyPipeline(object):
    """Scrapy Pipline for initializing PostgreSQL database
    and saving UserItem and BizItem to respective tables
    with database API.
    """

    def __init__(self):
        self.host = 'postgres'
        self.user = 'postgres'
        self.passwd = 'postgres'
        self.db = 'yelp_reviews'
        self.port = 5432

    def open_spider(self, spider):
        """Initialize database connection and cursor
        """
        self.db_h = PgsqlHandler()
        self.conn = self.db_h.conn
        self.cursor = self.db_h.cursor

    def close_spider(self, spider):
        """Close database API conection
        """
        self.cursor.close()
        self.conn.close()

    def save_biz(self, item):
        """Execute query to save BizItem to biz table 
        """
        query = """INSERT INTO biz (name, city, zipcode,
                                    state, link, star_raiting)
                VALUES (%s, %s, %s, %s, %s, %s)"""

        values = (item['business_name'], item['business_city'],
                  item['business_zip'], item['business_state'],
                  item['business_url'], item['business_star_rating'])

        self.cursor.execute(query, values)
        return item

    def save_user(self, item):
        """Execute query to save UserItem to reviewers table
        """
        biz_id = self.db_h.get_biz_seq_id()

        query = """INSERT INTO reviewers (id, user_url, star_raiting, location,
                                          review_text, review_date, link,
                                          label, feedback)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        values = (biz_id, item['user_url'], item['review_raiting'],
                  item['reviewer_location'], item['review_text'],
                  item['review_date'], item['link'], item['label'],
                  item['feedback'])

        self.cursor.execute(query, values)
        return item

    def process_item(self, item, spider):
        """Exectute query for the correct item type.
        """

        if isinstance(item, BizItem):
            self.save_biz(item)

        if isinstance(item, UserItem):
            self.save_user(item)
