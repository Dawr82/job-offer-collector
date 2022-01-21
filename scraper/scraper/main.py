import os

import scrapy

from .spiders.job_offers_spider import JobOfferSpider1
from .spiders import config


settings = {
    "FEEDS" : {
        os.path.join(config.DATA_DIRECTORY, "data.json") : {
            "format": "json",
            "indent": 4,
        },
        os.path.join(config.DATA_DIRECTORY, "data.csv") : {
            "format" : "csv",
            "fields" : ["title", "company", "salary", "location"],
        }
    }
}


if __name__ == '__main__':
    process = scrapy.CrawlerProcess(settings=settings)
    process.crawl(JobOfferSpider1)
    process.start()

