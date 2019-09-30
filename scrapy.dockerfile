FROM python:3

WORKDIR /usr/src/yelp_scrape

COPY ./scrapy .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["./docker-entrypoint.sh"]
