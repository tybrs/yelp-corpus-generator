#!/bin/sh
expect "Press Enter to start installation or ^C to abort" { send "\r" }
cd ./src
scrapy crawl yelp_spider  --set "JOBDIR=crawls/yelp_spider-seattle"
