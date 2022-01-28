import os
import sys
import json
import logging
from typing import Union

import redis
import pymongo
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner, Crawler
from spiders.job_offers_spider import NFJJobOfferSpider, BDGJobOfferSpider

sys.path.append("..")

from config import settings, sns


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
    crawler_bdg = Crawler(BDGJobOfferSpider, get_crawler_settings("bdg"))
    crawler_nfj = Crawler(NFJJobOfferSpider, get_crawler_settings("nfj"))
    runner.crawl(crawler_bdg)
    runner.crawl(crawler_nfj)


def scrape() -> None:
    runner = CrawlerRunner()
    start_crawling(runner)
    runner.join()
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()


def save(db_client: Union[redis.Redis, pymongo.MongoClient]) -> None:
    for website in sns.SCRAPED_URLS:
        try:
            with open(JSON_PATHS[website], "r") as f:
                if isinstance(db_client, redis.Redis):
                    save_to_redis(db_client, website, json.dumps(json.load(f)))
                elif isinstance(db_client, pymongo.MongoClient):
                    save_to_mongo(db_client, website, json.load(f))
                else:
                    raise TypeError(f"This database client ({db_client.__class__.__name__}) is not supported.")
        except FileNotFoundError as exc:
            print(f"{exc.__class__.__name__}: No data for [{website}] website in {os.path.abspath(settings.DATA_JSON_PATH)}.")
        except KeyError as exc:
            print(f"{exc.__class__.__name__}: This website is currently not supported.")
        except Exception as exc:
            print(exc)
            print(f"{exc.__class__.__name__}: An error occured during saving to the database.")


def save_to_redis(redis_client: redis.Redis, key: str, value: str) -> None:
    redis_client.set(key, value)


def save_to_mongo(mongo_client: pymongo.MongoClient, collection_name: str, data: list) -> None:
    db = mongo_client[settings.MONGO_DB_JOB_OFFER_DATABASE]
    print(f"Saving data to collection: {collection_name}")
    collection = db[collection_name]
    saved_count = 0
    for offer in data:
        if collection.find_one(offer) is None:
            collection.insert_one(offer)
            saved_count += 1
    print(f"Saved {saved_count} documents in collection {collection_name}")


def help_panel() -> None:
    print("\nUsage: python main.py [OPTION]\n\n")
    print("Available options: \
        \n\thelp               get help regarding usage of this program \
        \n\tscrape             scrape website and output the data to .json file \
        \n\tsave               save .json data (if exists) to redis database \
        \n\tscrape-and-save    scrape and then save the data to redis database (combined scrape and save options) \
        \n")


def main() -> None:
    try:
        option = sys.argv[1]
    except IndexError as exc:
        print(f"{exc.__class__.__name__}: Supply the program with needed command-line arguments!")
        help_panel()
        sys.exit()

    if option == "help":
        help_panel()
    elif option == "scrape":
        scrape()
    elif option == "scrape-and-save":
        scrape()
        save_to_redis()
    elif option == "save":
        try:
            save_option = sys.argv[2]
        except IndexError as exc:
            print(f"{exc.__class__.__name__}: Specify option for saving: mongo or redis")
        else:
            if save_option == "mongo":
                save(pymongo.MongoClient(settings.MONGO_DB_CONNECTION_STRING))
            elif save_option == "redis":
                save(redis.Redis(settings.REDIS_DB_HOSTNAME, settings.REDIS_DB_PORT, 0))
            else:
                print("Unsupported option for save command! (choose mongo or redis)")
    else:
        print(f"{sys.argv[1]}: invalid command-line argument! Suppored: help, scrape, scrape-and-save, save")


if __name__ == '__main__':
    logging.getLogger("scrapy").setLevel(logging.ERROR)
    main()