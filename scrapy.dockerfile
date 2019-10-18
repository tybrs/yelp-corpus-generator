FROM python:3.6-alpine

WORKDIR /usr/src/yelp_scrape

COPY ./scrapy .

RUN apk update
RUN apk add --no-cache \
    gcc \
    linux-headers \
    postgresql-dev \
    musl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    openssl-dev \
    python3-dev \
    python3

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["./docker-entrypoint.sh"]
