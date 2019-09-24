FROM python:3

WORKDIR /usr/src/yelp_scrape

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["./docker-entrypoint.sh"]