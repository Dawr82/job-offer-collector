import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Union

import redis
import pymongo
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner, Crawler

from spiders.job_offers_spider import NFJJobOfferSpider, BDGJobOfferSpider
from config import settings, sns


JSON_PATHS = {
    "bdg": Path(settings.DATA_JSON_PATH).joinpath("bdg.json"),
    "nfj": Path(settings.DATA_JSON_PATH).joinpath("nfj.json"),
}

CSV_PATHS = {
    "bdg": Path(settings.DATA_CSV_PATH).joinpath("bdg.csv"),
    "nfj": Path(settings.DATA_CSV_PATH).joinpath("nfj.csv"),
}


def get_crawler_settings(feeds_filename):
    try:
        crawler_settings = {
            "FEEDS": {
                JSON_PATHS[feeds_filename]: {
                    "format": "json",
                    "indent": 4,
                    "overwrite": True,
                },
                CSV_PATHS[feeds_filename]: {
                    "format": "csv",
                    "fields": ["title", "company", "salary", "location"],
                    "overwrite": True,
                },
            }
        }
    except KeyError:
        print("feeds_filename not supported")
    else:
        return crawler_settings


def start_crawling(runner):
    crawler_nfj = Crawler(NFJJobOfferSpider, get_crawler_settings("nfj"))
    crawler_bdg = Crawler(BDGJobOfferSpider, get_crawler_settings("bdg"))
    runner.crawl(crawler_bdg)
    runner.crawl(crawler_nfj)


def scrape():
    runner = CrawlerRunner()
    start_crawling(runner)
    runner.join()
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()


def save(db_client):
    for website in sns.SCRAPED_URLS:
        try:
            with open(JSON_PATHS[website], "r") as f:
                if isinstance(db_client, redis.Redis):
                    save_to_redis(db_client, website, json.dumps(json.load(f)))
                elif isinstance(db_client, pymongo.MongoClient):
                    save_to_mongo(db_client, website, json.load(f))
                else:
                    raise TypeError(
                        f"This database client ({db_client.__class__.__name__}) is not supported."
                    )
        except FileNotFoundError as exc:
            print(
                f"{exc.__class__.__name__}: No data for [{website}] website in {os.path.abspath(settings.DATA_JSON_PATH)}."
            )
        except KeyError as exc:
            print(f"{exc.__class__.__name__}: This website is currently not supported.")
        except Exception as exc:
            print(
                f"{exc.__class__.__name__}: An error occured during saving to the database."
            )


def save_to_redis(redis_client, key, value):
    redis_client.set(key, value)


def save_to_mongo(mongo_client, collection_name, data):
    db = mongo_client[settings.MONGO_DB_JOB_OFFER_DATABASE]
    print(f"Saving data to collection: {collection_name}")
    collection = db[collection_name]
    saved_count = 0
    for offer in data:
        filter = {"offer_id": offer.get("offer_id")}
        update = {"$setOnInsert": {"insertionDate": datetime.now()}, "$set": offer}
        result = collection.update_one(filter=filter, update=update, upsert=True)
        if result.upserted_id is not None:
            saved_count += 1
    print(f"Saved {saved_count} documents in collection {collection_name}")


def drop_from_redis(redis_client):
    for key in JSON_PATHS.keys():
        if redis_client.delete(key):
            print(f"Removed key {key} from redis cache.")
        else:
            print(f"Couldn't remove key {key} from redis cache.")


def help_panel():
    print("\nUsage: python main.py [OPTION]\n\n")
    print(
        "Available options: \
        \n\thelp               get help regarding usage of this program \
        \n\tscrape             scrape website and output the data to .json file \
        \n\tsave               save .json data (if exists) to redis/mongo database \
        \n\textract            scrape and then save the data to redis/mongo database (combined scrape and save options) \
        \n"
    )


def main():
    try:
        option = sys.argv[1]
    except IndexError as exc:
        print(
            f"{exc.__class__.__name__}: Supply the program with needed command-line arguments!"
        )
        help_panel()
        sys.exit()

    def save_helper(save_option):
        redis_client = redis.Redis(host="localhost", port=6379, db=0)
        mongo_client = pymongo.MongoClient(settings.MONGO_DB_CONNECTION_STRING)
        if save_option == "mongo":
            save(mongo_client)
            drop_from_redis(redis_client)
        elif save_option == "redis":
            save(redis_client)
        else:
            print("Unsupported option for save command! (choose mongo or redis)")

    if option == "help":
        help_panel()
    elif option == "scrape":
        scrape()
    elif option in ("extract", "save"):
        try:
            save_option = sys.argv[2]
        except IndexError as exc:
            print(f"Specify option for saving: mongo or redis")
        else:
            if option == "extract":
                scrape()
            save_helper(save_option)
    else:
        print(
            f"{sys.argv[1]}: invalid command-line argument! Supported: help, scrape, extract, save"
        )


if __name__ == "__main__":
    logging.getLogger("scrapy").setLevel(logging.ERROR)
    main()
