# Yelp Review Scraper: Using Scrapy with JavaScript integration through Splash

Yelp Review Scraper is a multi-container docker application designed to scrape restaurant reviews from Yelp.com from predefined cities.

## Installation

### Dependencies

#### Docker and Docker Compose

**Arch Linux**

`$ sudo pacman -S docker docker-compose`

**Other Distros**

For other distributions, follow the instructions [here](https://docs.docker.com/install/linux/docker-ce/) to add repository necessary to install `docker`.

If your perfered package manager does not have a repository for `docker-compose`, the appropriate binary can be added to your local binary directory with the following command.

```$ sudo curl -L "https://github.com/docker/compose/releases/download/1.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose```

### Build docker image with scrapy source files

``$ sudo docker-compose build``

## Configuration

## Usage

Start network and begin scrapping with the following command.
``$ sudo docker-compose up -d``

**TODO**

* Improve documentation and docstrings.
* Add database cursor to item processing pipline.