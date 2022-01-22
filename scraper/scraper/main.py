import os
import sys
import json
import logging

import redis
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner, Crawler
from spiders.job_offers_spider import JobOfferSpider2, JobOfferSpider1

sys.path.append("..")

from config import settings


JSON_PATHS = {
    "bdg" : os.path.join(settings.DATA_JSON_PATH, "bdg.json"),
    "nfj" : os.path.join(settings.DATA_JSON_PATH, "nfj.json"),
}

CSV_PATHS = {
    "bdg" : os.path.join(settings.DATA_CSV_PATH, "bdg.csv"),
    "nfj" : os.path.join(settings.DATA_CSV_PATH, "nfj.csv"),
}


def get_crawler_settings(feeds_filename: str) -> dict:
    try:
        crawler_settings = {
                "FEEDS" : {
                JSON_PATHS[feeds_filename]: {
                    "format": "json",
                    "indent": 4,
                    "overwrite": True,
                },
                CSV_PATHS[feeds_filename] : {
                    "format" : "csv",
                    "fields" : ["title", "company", "salary", "location"],
                    "overwrite": True,
                }  
            }    
        }
    except KeyError:
        print("feeds_filename not supported")
    else:
        return crawler_settings


def start_crawling(runner: CrawlerRunner) -> None:
    crawler_bdg = Crawler(JobOfferSpider1, get_crawler_settings("bdg"))
    crawler_nfj = Crawler(JobOfferSpider2, get_crawler_settings("nfj"))
    runner.crawl(crawler_bdg)
    runner.crawl(crawler_nfj)


def scrape() -> None:
    runner = CrawlerRunner()
    start_crawling(runner)
    runner.join()
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()


def save() -> None:
    redis_client = redis.Redis(host="localhost", port=6379)

    for website in settings.SCRAPED_URLS:
        try:
            with open(JSON_PATHS[website], "r") as f:
                redis_client.set(website, json.dumps(json.load(f)))
        except FileNotFoundError as exc:
            print(f"{exc.__class__.__name__}: No data for [{website}] website in {os.path.abspath(settings.DATA_JSON_PATH)}.")
        except KeyError as exc:
            print(f"{exc.__class__.__name__}: This website is currently not supported.")
        except Exception:
            print(f"An error occured during saving to Redis database.")


def main() -> None:
    try:
        option = sys.argv[1]
    except IndexError as exc:
        print(f"{exc.__class__.__name__}: Supply the program with needed command-line arguments!")
        sys.exit()

    if option == "scrape":
        scrape()
    elif option == "scrape-and-save":
        scrape()
        save()
    elif option == "save":
        save()
    else:
        print(f"{sys.argv}: invalid command-line argument! Suppored: scrape, scrape-and-save, save")


if __name__ == '__main__':
    logging.getLogger("scrapy").setLevel(logging.ERROR)
    main()