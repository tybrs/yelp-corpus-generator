FROM scrapinghub/splash as base

WORKDIR /usr/src/yelp_scrape

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


ENTRYPOINT ["/usr/src/yelp_scrape/docker-entrypoint.sh"]