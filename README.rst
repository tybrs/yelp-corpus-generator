=============================================================================
Yelp Review Scraper: Using Scrapy with JavaScript integration through Splash
=============================================================================

This project contains a dockerized web scraping crawler designed to scrape restaurant reviews from Yelp.com from predefined cities.


Installation
============

## Dependencies

`docker pull scrapinghub/splash`

## Build docker image with scrape source files

``$ sudo docker build -t yelp_scrape .``

Configuration
=============


Usage
=====

``$ sudo docker run --rm  yelp_scrape``

## Output

`src/yelp_reveiws.csv`

TODO
========

* Use docker compose to create a second and third container for scrapy script and postgress contain
* Improve docstrings