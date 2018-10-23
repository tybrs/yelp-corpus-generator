from scrapy import Spider, Request
from yelp_scrapy.items import YelpItem
from re import findall

class YelpSpider(Spider):
    name = 'yelp_spider'
    allowed_urls = ['https://yelp.com']
    start_urls = ['https://www.yelp.com/search?find_loc=New+York,+NY&start=0&sortby=review_count']
    nyc_urls = ["https://www.yelp.com/search?find_loc=New+York,+NY&start={}&sortby=review_count".format(x) for x in range(10, 1000, 10)]


    def parse(self, response):
        biznames = response.xpath('//a[@class="biz-name js-analytics-click"]/span/text()').extract()
        bizurls = response.xpath('//a[@class="biz-name js-analytics-click"]/@href').extract()
        bizurls = ['https://yelp.com'+ url for url in bizurls]
        for url in bizurls[:1]:
            yield Request(url=url, callback=self.parse_biz_page)

    def parse_biz_page(self, response):
        num_reviews_str = response.xpath('//div[@class="page-of-pages arrange_unit arrange_unit--fill"]/text()').extract_first()

        num_reviews = int(findall('of (\d+)', num_reviews_str)[0])
        review_urls = [response.url + '?start={}'.format(i) for i in range(0, num_reviews * 20, 20)]

        business_name = response.xpath('//div[@class="biz-page-header-left claim-status"]//h1/text()').extract_first()
        business_name = findall('\s+(.*)\s+', business_name)[0]
        business_location = ""
        business_star_rating = ""
        business_link = response.url

        # item = YelpItem()
        # item['business_name'] = business_name
        # item['business_link'] = business_link

#         address = 
#         price = 
#         cuisine = 

# #       Business page Fields
#         business_link = 
        
#         liked_by_vegetarians = 
#         takes_reservations = 
#         delivery = 
#         take_out = 
#         accepts_credit_cards = 
#         accepts_apple_pay = 
#         accepts_google_pay = 
#         good_for_lunch = 
#         parking_garage = 
#         bike_parking = 
#         good_for_kids = 
#         good_for_groups = 
#         attire_casual = 
#         ambience = 
#         noise_level = 
#         alcohol_full_bar = 
#         outdoor_seating = 
#         wi_fi = 
#         has_tv = 
#         dogs_allowed = 
#         drive_thru = 
#         caters = 

        for url in review_urls[:1]:
            yield Request(url=url, callback=self.parse_reviews)

    def parse_reviews(self, response):
        reviews_rc1 = '//ul[@class="ylist ylist-bordered reviews]//li/'
        reviews_rc2 = response.xpath('//div[@class="review review--with-sidebar"]')

        for review in reviews_rc2:
            reviewer_location = review.xpath('.//li[@class="user-location responsive-hidden-small"]/b/text()').extract_first()
            review_text = review.xpath('.//div[@class="review-content"]/p/text()').extract_first()

            item = YelpItem()
            item['review_text'] = review_text
            item['reviewer_location'] = reviewer_location
            yield item
