from scrapy import Spider, Request
from yelp_scrapy.items import YelpItem
from re import findall
from time import sleep
#from random import randint


def get_urls(city):
    return ['https://www.yelp.com/search?find_desc='
            'Restaurants&find_loc={0}&'
            'sortby=review_count&start={1}'.format(city, x)
            for x in range(0, 960 + 1, 30)]


class YelpSpider(Spider):
    name = 'yelp_spider'
    allowed_urls = ['https://yelp.com']
    start_urls = [
        'https://www.yelp.com/search?find_desc='
        'Restaurants&find_loc=New%20York%2C%20NY&sortby=review_count']

    def parse(self, response):

        nyc_urls = get_urls('New+York,+NY')
        chi_urls = get_urls('Chicago,+IL')
        la_urls = get_urls('Los+Angeles,+CA')
        orlando_urls = get_urls('Orlando,+FL')
        lv_urls = ('Las+Vegas,+NV')

        all_urls = (nyc_urls + chi_urls + la_urls +
                    orlando_urls + lv_urls)

        for url in all_urls:
            sleep(1)
            yield Request(url=url, callback=self.parse_search)

    def parse_search(self, response):
        print("=search=" * 30)
        bizurls = response.xpath(
            '//a[@class="biz-name js-analytics-click"]/@href').extract()
        bizurls = ['https://yelp.com' + url for url in bizurls][1:]
        print(bizurls)
        for url in bizurls:
            sleep(1)
            yield Request(url=url, callback=self.parse_biz_page)

    def parse_biz_page(self, response):
        print(r"%biz%" * 30)
        num_reviews_str = response.xpath(
            '//div[@class="page-of-pages '
            'arrange_unit arrange_unit--fill"]/text()').extract_first()

        if num_reviews_str:
            num_reviews = int(findall('of (\d+)', num_reviews_str)[0])
            review_portion = int(20 * round(num_reviews * 2 / 20))
            reviews_range = [1] + list(
                range(20, num_reviews * 20, review_portion))
        else:
            reviews_range = [1]

        review_urls = [
            response.url + '?start={}'.format(i)
            for i in reviews_range]

        business_name = response.xpath(
            '//div[@class="biz-page-header-left claim-status"]'
            '//h1/text()').extract_first()
        business_name = findall('\s+(.*)\s+', business_name)[0]
        business_link = response.url
        business_state = response.xpath(
            '//span[@itemprop="addressRegion"]/text()').extract_first()
        business_city = response.xpath(
            '//span[@itemprop="addressLocality"]/text()').extract_first()
        business_zip = response.xpath(
            '//span[@itemprop="postalCode"]/text()').extract_first()
        business_star_rating = response.xpath(
            '//div[@class="biz-rating biz-rating-very-large '
            'clearfix"]/div/@title').extract_first()
        business_star_rating = float(findall(
            '\d{1,2}\.?\d{1,2}',
            business_star_rating)[0])

        for url in review_urls[:1]:
            sleep(1)
            yield Request(url=url,
                          meta={'business_name': business_name,
                                'business_city': business_city,
                                'business_state': business_state,
                                'business_zip': business_zip,
                                'business_link': business_link,
                                'business_star_rating': business_star_rating},
                          callback=self.parse_reviews)

    def parse_reviews(self, response):
        print("*reviews*" * 30)
        business_name = response.meta['business_name']
        business_city = response.meta['business_city']
        business_zip = response.meta['business_zip']
        business_state = response.meta['business_state']
        business_link = response.meta['business_link']
        business_star_rating = response.meta['business_star_rating']

        reviews = response.xpath('//div[@class="review review--with-sidebar"]')

        for review in reviews:

            reviewer_location = review.xpath(
                './/li[@class="user-location responsive-hidden-small"]'
                '/b/text()').extract_first()

            reviewer_id = review.xpath(
                './/@data-signup-object').extract_first()

            review_date = review.xpath(
                './/span[@class="rating-qualifier"]'
                '/text()').extract_first()

            review_date = findall('\s+(.*)\s+', review_date)[0]

            review_raiting = review.xpath(
                './/div[@class="biz-rating biz-rating-large'
                ' clearfix"]/div/div/@title').extract_first()

            review_raiting = float(findall(
                '\d{1,2}\.?\d{1,2}',
                review_raiting)[0])

            review_text = ''.join(review.xpath(
                './/div[@class="review-content"]/p//text()').extract())

            review_text = review_text.replace('\xa0', '')

            funny = review.xpath(
                './/a[@class="ybtn ybtn--small funny js-analytics-click"]'
                '/span[3]/text()').extract_first()

            if funny:
                funny = int(funny)

            useful = review.xpath(
                './/a[@class="ybtn ybtn--small useful js-analytics-click"]'
                '/span[3]/text()').extract_first()

            if useful:
                useful = int(useful)

            cool = review.xpath(
                './/a[@class="ybtn ybtn--small cool js-analytics-click"]'
                '/span[3]/text()').extract_first()

            if cool:
                cool = int(cool)

            if business_city + ', ' + business_state == reviewer_location:
                label = 'local'

            elif reviewer_location.split(' ')[-1] != business_state:
                label = 'remote'

            else:
                continue

            item = YelpItem()

            item['business_name'] = business_name
            item['business_city'] = business_city
            item['business_state'] = business_state
            item['business_zip'] = business_zip
            item['business_url'] = business_link
            item['business_star_rating'] = business_star_rating

            item['label'] = label
            item['reviewer_id'] = reviewer_id
            item['review_raiting'] = review_raiting
            item['reviewer_location'] = reviewer_location
            item['funny'] = funny
            item['useful'] = useful
            item['cool'] = cool
            item['review_text'] = review_text
            item['review_date'] = review_date

            yield item
