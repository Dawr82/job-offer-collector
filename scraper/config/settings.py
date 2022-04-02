import os
import sys
from pathlib import Path

from decouple import AutoConfig

# CONFIG_PATH should be file system location
# that contains configuration files (either .env or .ini)

# If you don't specify all needed variables there
# it's going to use default values which might be inappropriate
# (like root as database user)

config_path = os.getenv("CONFIG_PATH")

if config_path is None:
    config_path_error = """
    CONFIG_PATH environment variable is not set.
    Set it to the location of directory that contains configuration files.
    """
    print(config_path_error)
    sys.exit(-1)

config = AutoConfig(search_path=config_path)

# Data directories can't be adjusted currently.
DATA_DIRECTORY = Path().parent.parent.joinpath("data")
DATA_JSON_PATH = config("DATA_JSON_PATH", default=DATA_DIRECTORY.joinpath("json"))
DATA_CSV_PATH = config("DATA_CSV_PATH", default=DATA_DIRECTORY.joinpath("csv"))

# Max pages to process (if website lists offers using pagination)
MAX_PAGES = config("MAX_PAGES", default=3, cast=int)

# Redis connection
REDIS_DB_HOSTNAME = config("REDIS_DB_HOSTNAME", default="redis")
REDIS_DB_PORT = config("REDIS_DB_PORT", default="6379", cast=int)

# REST API connection
API_SERVER_HOSTANAME = config("API_SERVER_HOSTNAME", default="flask-api")

# MongoDB connection
MONGO_DB_HOSTNAME = config("MONGO_DB_HOSTNAME", default="localhost")
MONGO_DB_USER = config("MONGO_INITDB_ROOT_USERNAME", default="root")
MONGO_DB_PASSWORD = config("MONGO_INITDB_ROOT_PASSWORD", default="root")
MONGO_DB_PORT = config("MONGO_DB_PORT", default="27017", cast=int)
MONGO_DB_JOB_OFFER_DATABASE = config("MONGO_DB_JOB_OFFER_DATABASE", default="scraper")
MONGO_DB_CONNECTION_STRING = f"mongodb://{MONGO_DB_USER}:{MONGO_DB_PASSWORD}@{MONGO_DB_HOSTNAME}:{MONGO_DB_PORT}/{MONGO_DB_JOB_OFFER_DATABASE}?authSource=admin&retryWrites=true&w=majority"

# Log file location can't be adjusted currently
CRAWLER_LOG_FILE = config(
    "CRAWLER_LOG_FILE", default=Path().parent.parent.joinpath("log/crawler_logs.log")
)
CRAWLER_LOG_MODE = "a+"
CRAWLER_LOG_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
