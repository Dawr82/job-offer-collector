import os
import sys

import scrapy
from scrapy.crawler import CrawlerProcess

from spiders.job_offers_spider import JobOfferSpider1

sys.path.append("..")

from config import settings


process_settings = {
    "FEEDS" : {
        os.path.join(settings.DATA_DIRECTORY, "data.json") : {
            "format": "json",
            "indent": 4,
            "overwrite": True,
        },
        os.path.join(settings.DATA_DIRECTORY, "data.csv") : {
            "format" : "csv",
            "fields" : ["title", "company", "salary", "location"],
            "overwrite": True,
        }
    }
}


if __name__ == '__main__':
    process = CrawlerProcess(settings=process_settings)
    process.crawl(JobOfferSpider1)
    process.start()

    # .json file is available now

    import redis
    import json

    redis_client = redis.Redis(host="localhost", port=6379)

    with open(settings.DATA_JSON_PATH, "r") as f:
        redis_client.set("bdg", json.dumps(json.load(f)))

