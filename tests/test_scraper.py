import requests
from scrapy.http import Request, TextResponse
from yaml import load, SafeLoader


def test_xpaths():
    """Unit test to make sure all xpaths in src/yelp_scrapy/xpath.yml
    retrieve a non-empty output for predefined test urls.
    """
    config = load(open('scrapy/src/yelp_scrapy/xpath.yml', 'r'),
                  Loader=SafeLoader)

    for page in config:
        page_dict = config[page]
        url = 'http://localhost:8050/render.html?url='
        url += page_dict['test_url']

        page_xpaths = {k: v for k, v in page_dict.items()
                       if k != 'test_url'}

        req = Request(url=url)
        resp = requests.get(url)

        response = TextResponse(url=url, request=req,
                                body=resp.text, encoding='utf-8')

        for key, xpath in page_xpaths.items():
            extraction = response.xpath(xpath).extract()
            assert extraction, f"xpath for {key} failed"

if __name__ == '__main__':
    test_xpaths()
