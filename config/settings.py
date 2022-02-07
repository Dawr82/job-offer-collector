import os
from decouple import AutoConfig

config = AutoConfig(search_path="..")

# data directories locations
DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATA_JSON_PATH = os.path.join(DATA_DIRECTORY, "json")
DATA_CSV_PATH = os.path.join(DATA_DIRECTORY, "csv")


# max pages to process (if website lists offers using pagination)
MAX_PAGES = 1


# Redis connection
REDIS_DB_HOSTNAME = config("REDIS_DB_HOSTNAME", default="redis-db")
REDIS_DB_PORT = config("REDIS_DB_PORT", default="6379")


# REST API connection
API_SERVER_HOSTANAME = config("API_SERVER_HOSTNAME", default="flask-api")


# MongoDB connection
MONGO_DB_HOSTNAME = config("MONGO_DB_HOSTNAME", default="localhost")
MONGO_DB_USER = config("MONGO_INITDB_ROOT_USERNAME", default="root")
MONGO_DB_PASSWORD = config("MONGO_INITDB_ROOT_PASSWORD", default="root")
MONGO_DB_PORT = config("MONGO_DB_PORT", default="27017")
MONGO_DB_JOB_OFFER_DATABASE = config("MONGO_DB_JOB_OFFER_DATABASE", default="scraper")
MONGO_DB_CONNECTION_STRING = f"mongodb://{MONGO_DB_USER}:{MONGO_DB_PASSWORD}@{MONGO_DB_HOSTNAME}:{MONGO_DB_PORT}/{MONGO_DB_JOB_OFFER_DATABASE}?authSource=admin&retryWrites=true&w=majority"


# logging
CRAWLER_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs/crawler_logs.log")
CRAWLER_LOG_MODE = "a+"
CRAWLER_LOG_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"