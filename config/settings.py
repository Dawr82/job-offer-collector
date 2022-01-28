import os
from decouple import AutoConfig


DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATA_JSON_PATH = os.path.join(DATA_DIRECTORY, "json")
DATA_CSV_PATH = os.path.join(DATA_DIRECTORY, "csv")

MAX_REQUESTS = 1

config = AutoConfig(search_path="..")
REDIS_DB_HOSTNAME = config("REDIS_DB_HOSTANAME", default="redis-db")
API_SERVER_HOSTANAME = config("API_SERVER_HOSTNAME", default="flask-api")

