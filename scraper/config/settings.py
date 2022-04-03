import os
from pathlib import Path


# Data directories can't be adjusted currently.
DATA_DIRECTORY = Path().parent.parent.joinpath("data")
DATA_JSON_PATH = os.getenv("DATA_JSON_PATH", default=DATA_DIRECTORY.joinpath("json"))
DATA_CSV_PATH = os.getenv("DATA_CSV_PATH", default=DATA_DIRECTORY.joinpath("csv"))

# Max pages to process (if website lists offers using pagination)
MAX_PAGES = int(os.getenv("MAX_PAGES", default=3))

# Redis connection
REDIS_DB_HOSTNAME = os.getenv("REDIS_DB_HOSTNAME", default="redis")
REDIS_DB_PORT = int(os.getenv("REDIS_DB_PORT", default="6379"))

# REST API connection
API_SERVER_HOSTANAME = os.getenv("API_SERVER_HOSTNAME", default="flask-api")

# MongoDB connection
MONGO_DB_HOSTNAME = os.getenv("MONGO_DB_HOSTNAME", default="localhost")
MONGO_DB_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", default="root")
MONGO_DB_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD", default="root")
MONGO_DB_PORT = int(os.getenv("MONGO_DB_PORT", default="27017"))
MONGO_DB_JOB_OFFER_DATABASE = os.getenv("MONGO_DB_JOB_OFFER_DATABASE", default="scraper")
MONGO_DB_CONNECTION_STRING = f"mongodb://{MONGO_DB_USER}:{MONGO_DB_PASSWORD}@{MONGO_DB_HOSTNAME}:{MONGO_DB_PORT}/{MONGO_DB_JOB_OFFER_DATABASE}?authSource=admin&retryWrites=true&w=majority"

# Log file location can't be adjusted currently
CRAWLER_LOG_FILE = os.getenv(
    "CRAWLER_LOG_FILE", default=Path().parent.parent.joinpath("log/crawler_logs.log")
)
CRAWLER_LOG_MODE = "a+"
CRAWLER_LOG_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
