from scrapy import Spider
from scrapy_splash import SplashRequest
from yelp_scrapy.items import UserItem, BizItem
from re import findall
from yaml import load, SafeLoader
from collections import defaultdict
from scrape_utils import print_progress, get_urls
# from time import sleep


class YelpSpider(Spider):
    """Scrapy Spider subclass designed to crawl all businesses
    on Yelp search page for resturant reviews.
    """

    Spider.xpaths = load(open('yelp_scrapy/xpath.yml', 'r'),
                         Loader=SafeLoader)
    name = 'yelp_spider'

    allowed_urls = ['https://yelp.com']
    start_urls = ['https://www.yelp.com/search?find_desc='
                  'Restaurants&find_loc=New%20York%2C%20NY'
                  '&sortby=review_count']

    @print_progress
    def parse(self, response):
        """Root parse function for spider to colllect all urls
        to vbe parsed
        """
        nyc_urls = get_urls('New+York,+NY')
        chi_urls = get_urls('Chicago,+IL')
        la_urls = get_urls('Los+Angeles,+CA')
        orlando_urls = get_urls('Orlando,+FL')
        lv_urls = get_urls('Las+Vegas,+NV')

        all_urls = (nyc_urls + chi_urls + la_urls +
                    orlando_urls + lv_urls)

        for url in [nyc_urls[0]]:
            # sleep(1)
            yield SplashRequest(url=url, callback=self.parse_search)

    @print_progress
    def parse_search(self, response):
        bizurls = response.xpath(
            self.xpaths['search_page']['biz_url']).extract()

        bizurls = ['https://yelp.com' + url for url in bizurls
                   if not url.startswith('https://')][2:]

        for url in bizurls:
            # sleep(1)
            yield SplashRequest(url=url, callback=self.parse_biz_page)

    @print_progress
    def parse_biz_page(self, response):
        num_reviews_str = response.xpath(
            self.xpaths['reviews']['num_reviews_str']).extract_first()

        # make into function
        if num_reviews_str:
            num_reviews = int(findall(r'of (\d+)', num_reviews_str)[0])
            review_portion = int(20 * round(num_reviews * 2 / 20))
            reviews_range = [1] + list(
                range(20, num_reviews * 20, review_portion))
        else:
            reviews_range = [1]

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

        item = BizItem()
        item['business_name'] = business_name
        item['business_city'] = business_city
        item['business_state'] = business_state
        item['business_zip'] = business_zip
        item['business_url'] = business_link
        item['business_star_rating'] = business_star_rating

        yield item

        review_urls = [response.url + '&start={}'.format(i)
                       for i in reviews_range]

        for url in review_urls[:1]:
            # sleep(1)
            yield SplashRequest(url=url,
                                meta={'business_city': business_city,
                                      'business_state': business_state},
                                callback=self.parse_reviews)

    @print_progress
    def parse_reviews(self, response):

        business_city = response.meta['business_city']
        business_state = response.meta['business_state']
        reviews = response.xpath(self.xpaths['reviews']['review_li'])

        # make into function
        for review in reviews:

            reviewer_location = review.xpath(
                self.xpaths['reviews']['reviewer_location']).extract_first()

            user_url = review.xpath(
                self.xpaths['reviews']['user_url']).extract_first()

            review_date = review.xpath(
                self.xpaths['reviews']['date']).extract_first()

            review_date = (review_date.strip(' ').strip('\t')
                           if review_date else None)

            review_raiting = review.xpath(
                self.xpaths['reviews']['raiting']).extract_first()

            review_raiting = findall(r'\d{1,2}\.?\d{1,2}',
                                     review_raiting)

            review_raiting = (float(review_raiting[0])
                              if review_raiting else None)

            review_text = ''.join(review.xpath(
                self.xpaths['reviews']['review_text']).extract())

            review_text = review_text.replace('\xa0', '')

            feedback = review.xpath(
                self.xpaths['reviews']['review_text']).extract()

            # make into function
            business_loc = business_city + ', ' + business_state
            reviewer_state = reviewer_location.split(' ')[-1]

            if business_loc == reviewer_location:
                label = 'local'

            elif reviewer_location and reviewer_state != business_state:
                label = 'remote'
            else:
                label = None

            item = UserItem()
            item['label'] = label
            item['user_url'] = user_url
            item['review_raiting'] = review_raiting
            item['reviewer_location'] = reviewer_location
            item['review_text'] = review_text
            item['review_date'] = review_date
            item['feedback'] = feedback

            yield item
