# Yelp Review Scraper with Scrapy/Splach

## Dependicies

## Python

`pip install -r requirements.txt` to install the following:

```
Scrapy==1.7.3
scrapy_splash==0.7.2
PyYAML==5.1.2
```

### Splash


`docker pull scrapinghub/splash`

`sudo docker run -p 8050:8050 scrapinghub/splash`

`cd src`

`scrapy crawl yelp_spider`

## Output

`src/yelp_reveiws.csv`

## TODO

* Compose single docker image.
* Improve docstrings