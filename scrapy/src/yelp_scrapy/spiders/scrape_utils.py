def print_progress(func):
    count = defaultdict(lambda: 0)

    def helper(self, response):
        count[func.__name__] += 1
        # meta = {k: response.meta[k] for k in response.meta
        #         if not k.startswith('download')}
        print('{:=^30}'.format(func.__name__))
        print('{:<20s}{:<1d}'.format('parser call index:',
                                     count[func.__name__]))
        print('{:<20s}{:<1s}'.format('url:', response.url))
        output = func(self, response)
        print('=' * 30)
        return output
    return helper


def get_urls(city):
    return ['https://www.yelp.com/search?find_desc='
            'Restaurants&find_loc={0}&'
            'sortby=review_count&start={1}'.format(city, x)
            for x in range(0, 960 + 1, 30)]