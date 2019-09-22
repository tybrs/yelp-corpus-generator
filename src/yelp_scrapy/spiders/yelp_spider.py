from scrapy import Spider, Request
from scrapy_splash import SplashRequest
from yelp_scrapy.items import YelpItem
from re import findall
from time import sleep
from yaml import load
from random import randint
from collections import defaultdict

def print_progress(func):
    count = defaultdict(lambda:0)
    def helper(self, response):
        count[func.__name__] += 1
        meta = {k: response.meta[k] for k in response.meta
                if not k.startswith('download')}
        print('{:=^30}'.format(func.__name__))
        print('{:<20s}{:<1d}'.format('parser call index:',
                                     count[func.__name__]))
        print('{:<20s}{:<1s}'.format('url:', response.url))
        print('{:<20s}{:<1s}'.format('carried over data:', str(meta)))
        output = func(self, response)
        print('=' * 30)
        return output
    return helper

def get_urls(city):
    return ['https://www.yelp.com/search?find_desc='
            'Restaurants&find_loc={0}&'
            'sortby=review_count&start={1}'.format(city, x)
            for x in range(0, 960 + 1, 30)]


class YelpSpider(Spider):
    Spider.xpaths = load(open('yelp_scrapy/xpath.yml', 'r'))
    name = 'yelp_spider'
    allowed_urls = ['https://yelp.com']
    start_urls = ['https://www.yelp.com/search?find_desc='
                  'Restaurants&find_loc=New%20York%2C%20NY'
                  '&sortby=review_count']

    @print_progress
    def parse(self, response):
        nyc_urls = get_urls('New+York,+NY')
        chi_urls = get_urls('Chicago,+IL')
        la_urls = get_urls('Los+Angeles,+CA')
        orlando_urls = get_urls('Orlando,+FL')
        lv_urls = get_urls('Las+Vegas,+NV')

        all_urls = (nyc_urls + chi_urls + la_urls +
                    orlando_urls + lv_urls)

        for url in [nyc_urls[1]]:
            sleep(1)
            yield SplashRequest(url=url, callback=self.parse_search)

    @print_progress
    def parse_search(self, response):
        bizurls = response.xpath(
            self.xpaths['search_page']['biz_url']).extract()

        bizurls = ['https://yelp.com' + url for url in bizurls][2:]
        for url in bizurls:
            sleep(1)
            yield SplashRequest(url=url, callback=self.parse_biz_page)

    @print_progress
    def parse_biz_page(self, response):
        num_reviews_str = response.xpath(
            self.xpaths['reviews']['num_reviews_str']).extract_first()
        if num_reviews_str:
            num_reviews = int(findall(r'of (\d+)', num_reviews_str)[0])
            review_portion = int(20 * round(num_reviews * 2 / 20))
            reviews_range = [1] + list(
                range(20, num_reviews * 20, review_portion))
        else:
            reviews_range = [1]

        review_urls = [response.url + '&start={}'.format(i)
                       for i in reviews_range]

        business_name = response.xpath(
            self.xpaths['biz_page']['biz_h1']).extract_first()
        business_name = business_name.strip(' ').strip('\t')
        business_link = response.url
        business_state = response.xpath(
            '//span[@itemprop="addressRegion"]/text()').extract_first()
        business_city = response.xpath(
            '//span[@itemprop="addressLocality"]/text()').extract_first()
        business_zip = response.xpath(
            '//span[@itemprop="postalCode"]/text()').extract_first()
        business_star_rating = response.xpath(
            self.xpaths['biz_page']['business_star_rating']).extract_first()
        business_star_rating = response.xpath(
            self.xpaths['biz_page']['business_star_rating']).get()
        business_star_rating = float(findall(
            r'\d{1,1}\.?\d{0,2}',
            business_star_rating)[0])

        meta = {'business_name': business_name,
                'business_city': business_city,
                'business_state': business_state,
                'business_zip': business_zip,
                'business_link': business_link,
                'business_star_rating': business_star_rating}

        for url in review_urls[:1]:
            sleep(1)
            yield SplashRequest(url=url,
                          meta=meta,
                          callback=self.parse_reviews)

    @print_progress
    def parse_reviews(self, response):
        business_name = response.meta['business_name']
        business_city = response.meta['business_city']
        business_zip = response.meta['business_zip']
        business_state = response.meta['business_state']
        business_link = response.meta['business_link']
        business_star_rating = response.meta['business_star_rating']

        reviews = response.xpath(self.xpaths['reviews']['review_li'])

        for review in reviews:

            reviewer_location = review.xpath(
                self.xpaths['reviews']['reviewer_location']).extract_first()
            print(reviewer_location)
            input()
            #fix
            reviewer_id = review.xpath(
                './/@data-signup-object').extract_first()
            #fix
            review_date = review.xpath(
                './/span[@class="rating-qualifier"]'
                '/text()').extract_first()

            review_date = (review_date.strip(' ').strip('\t')
                           if review_date else None)
            #fix
            review_raiting = review.xpath(
                './/div[@class="biz-rating biz-rating-large'
                ' clearfix"]/div/div/@title').extract_first()

            # review_raiting = float(findall(
            #     r'\d{1,2}\.?\d{1,2}',
            #     review_raiting)[0])

            review_text = ''.join(review.xpath(
                self.xpaths['reviews']['review_text']).extract())

            review_text = review_text.replace('\xa0', '')

            #fix
            funny = review.xpath(
                './/a[@class="ybtn ybtn--small funny js-analytics-click"]'
                '/span[3]/text()').extract_first()

            funny = int(funny) if funny else None

            #fix
            useful = review.xpath(
                './/a[@class="ybtn ybtn--small useful js-analytics-click"]'
                '/span[3]/text()').extract_first()

            useful = int(useful) if useful else None
            #fix
            cool = review.xpath(
                './/a[@class="ybtn ybtn--small cool js-analytics-click"]'
                '/span[3]/text()').extract_first()

            cool = int(cool) if cool else None

            # if business_city + ', ' + business_state == reviewer_location:
            #     label = 'local'

            # elif reviewer_location and reviewer_location.split(' ')[-1] != business_state:
            #     label = 'remote'

            # else:
            #     continue

            item = YelpItem()

            item['business_name'] = business_name
            item['business_city'] = business_city
            item['business_state'] = business_state
            item['business_zip'] = business_zip
            item['business_url'] = business_link
            item['business_star_rating'] = business_star_rating

            # item['label'] = label
            item['reviewer_id'] = reviewer_id
            item['review_raiting'] = review_raiting
            item['reviewer_location'] = reviewer_location
            item['funny'] = funny
            item['useful'] = useful
            item['cool'] = cool
            item['review_text'] = review_text
            item['review_date'] = review_date
            yield item
