import psycopg2

class YelpScrapyPipeline(object):

    def __init__(self):
        self.host = 'postgres'
        self.user = ''
        self.passwd = ''
        self.db = ''

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
        query = """INSERT INTO table (field, field)
                VALUES (%s, %s)"""

        values = (item['field1'], item['field2'], item['field3'],
                  item['field4'], item['field5'], item['field6'],
                  item['field7'], item['field8'])

        self.cur.execute(query, values)
        self.conn.commit()
        return item
