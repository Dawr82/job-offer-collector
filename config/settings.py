import os
from decouple import AutoConfig


DATA_DIRECTORY = os.path.join(os.path.dirname(__file__), "data")
DATA_JSON_PATH = os.path.join(DATA_DIRECTORY, "data.json")
DATA_CSV_PATH = os.path.join(DATA_DIRECTORY, "data.csv")

SCRAPED_URLS = {
    "bdg" : r"https://bulldogjob.pl/companies/jobs",
    "nfj" : r"https://nofluffjobs.com/pl/praca-it/backend?criteria=category%3Dfrontend,fullstack, \
        mobile,testing,devops,embedded,security,gaming,artificial-intelligence,big-data,support, \
        it-administrator,agile,product-management,project-manager,business-intelligence, \
        business-analyst,ux,sales,marketing,backoffice,hr,other&page=1",
}

MAX_REQUESTS = 10

config = AutoConfig(search_path="..")
REDIS_DB_HOSTNAME = config("REDIS_DB_HOSTANAME", default="redis-db")
API_SERVER_HOSTANAME = config("API_SERVER_HOSTNAME", default="flask-api")

